"""Refresh the Conferences page data file.

Pulls upcoming astrophysics/cosmology conferences from the INSPIRE-HEP API,
merges with the hand-maintained `curated.yml`, and writes one consolidated
JSON file that the static site renders client-side.

Usage:
    python tools/conferences/update.py

Run it from the site repo root (or anywhere — it resolves paths relative to
this file). Commit the updated `assets/data/conferences.json` and push.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import requests
import yaml

THIS = Path(__file__).resolve()
ROOT = THIS.parent.parent.parent
CURATED = THIS.parent / "curated.yml"
OUT = ROOT / "assets" / "data" / "conferences.json"

INSPIRE_URL = "https://inspirehep.net/api/conferences"
INSPIRE_CATEGORIES = ["Astrophysics", "Gravitation and Cosmology"]
PAGE_SIZE = 50
MAX_PAGES = 6  # cap so we don't over-pull; ~300 entries per category is plenty

# huggingface/ai-deadlines: per-venue YAML files in the repo's
# src/data/conferences/ directory. We pick a whitelist of venues relevant to
# the site owner's ML/AI-for-science work. Each YAML carries multiple year
# entries; we pick the one with the most future-facing deadline.
AI_DEADLINES_RAW = "https://raw.githubusercontent.com/huggingface/ai-deadlines/main/src/data/conferences"
AI_DEADLINES_WHITELIST = [
    # Top-tier general ML / AI
    "neurips", "icml", "iclr", "aaai", "ijcai", "uai", "aistats",
    # NLP / LLM-relevant
    "acl", "emnlp", "naacl", "colm", "conll",
    # Data mining / retrieval (relevant for RAG-style work)
    "kdd", "cikm", "sigir", "ecir", "wsdm",
]

# Keyword filter for INSPIRE entries. Tuned to the site owner's work:
# cosmological simulations of first galaxies + ML/HPC for astro. See
# CLAUDE.md "Conferences" section for the rationale and how to tune.

POS_KEYWORDS = [
    # Astrophysics / cosmology anchors
    "astrophys", "astronom", "astroparticle",
    "cosmol",
    "galaxy", "galaxies", "galactic",
    "reioniz",
    "primordial", "pop iii", "pop. iii", "pop-iii", "population iii",
    "dark matter", "dark energy",
    "n-body",
    "hydrodynam",
    "first stars", "first galaxies", "first star", "first galaxy",
    "intergalactic", "interstellar", "igm",
    "supernova", "supernovae",
    "cmb", "cosmic microwave",
    "large-scale structure", "large scale structure",
    "baryon acoustic", "bao",
    "gravitational wave",
    "observational", "telescope", "observatory",
    "spectroscop", "photometr",
    "redshift",
    "halo", "halos", "haloes",
    "star formation", "star-forming",
    "stellar population",
    "lensing",
    "radio astronomy",
    "x-ray", "gamma-ray",
    "inflation", "inflationary",
    "simulation",
    "21 cm", "21cm",
    "weak lensing", "strong lensing",
    "lsst", "vera rubin", "rubin observatory", "euclid", "ska", "desi",
    # ML / AI / HPC anchors
    "machine learning", "deep learning", "neural network", "neural net",
    "transformer", "attention",
    "language model", "llm", "large language",
    "foundation model",
    "surrogate", "emulator",
    "generative model", "diffusion model",
    "artificial intelligence", "ai for science", "ai4science", "ai for physics",
    "ml4ps", "ml4astro", "sciml", "ai4mat",
    "high-performance computing", "high performance computing", "hpc",
    "supercomputing", "supercomputer", "exascale",
    "gpu", "accelerator",
    "big data",
]

# Strong signals this is not in scope. Each hit subtracts 2 from the score.
# "Cosmic string" is kept (astro) by matching only the full "string theor..."
# or similar formal-theory strings, not "string" alone.
NEG_KEYWORDS = [
    "de sitter", "anti-de sitter", "ads/cft", "ads-cft",
    "holograph",
    "string theor", "string phenomenolog", "string land",
    "strings 20", "strings &", "strings and cosmolog",  # "Strings 2026" annual + "Strings & Cosmology"
    "from amplitudes",  # scattering amplitudes formalism conferences
    "supersymmet", "susy",
    "lattice qcd", "lattice gauge", "lattice field theor",
    "gauge theor", "yang-mills", "yang mills",
    "scattering amplitud", "conformal field",
    "quark-gluon", "qgp",
    "heavy ion", "heavy-ion", "rhic",
    "nuclear physics", "nuclear structure", "nuclear theor", "nuclear reaction",
    "subnuclear",  # particle/HEP school keyword
    "collider phys", "lhc phys", "hep-ex",
    "parton",
    "hadron collider",
    "chiral perturb", "chiral sigma",
    # Theoretical cosmology / formal-theory traps
    "wormhole", "complex saddle",
    "quantum gravity",
    "fundamental physics",  # often signals formal-theory (e.g. "Cosmological Frontiers in Fundamental Physics")
    "particles, strings",   # PASCOS-style string-heavy venues
]

MIN_RELEVANCE_SCORE = 1

# Venue allowlist for INSPIRE entries. Most INSPIRE-listed workshops are
# hosted at random universities; the site owner doesn't travel to small
# venues, so filter to:
#  - US cities containing a top-~50 research university or major astro
#    national lab (national labs are listed by their host town, e.g.
#    "Argonne", "Greenbelt").
#  - A short allowlist of international cities at major astro/physics
#    institutions where the trip would be plausible.
# Match is case-insensitive substring on the location string ("city, country").
# Entries with NO location string (virtual/online/unknown) are kept by
# default — they cost nothing to attend.

US_VENUE_CITIES = {
    # New England
    "boston", "cambridge", "new haven", "providence", "hanover", "amherst",
    # NY metro + nearby Ivies / labs
    "new york", "ithaca", "stony brook", "upton",
    # Mid-Atlantic
    "princeton", "philadelphia", "baltimore", "college park", "greenbelt",
    "charlottesville", "blacksburg",
    # Southeast
    "durham", "chapel hill", "atlanta", "nashville", "gainesville",
    # Midwest
    "pittsburgh", "columbus", "cleveland", "ann arbor", "east lansing",
    "evanston", "chicago", "argonne", "lemont", "batavia",
    "urbana", "champaign", "madison", "minneapolis",
    "st louis", "saint louis", "south bend", "notre dame",
    "bloomington", "west lafayette", "rochester",
    # Plains / Mountain
    "boulder", "denver", "salt lake city", "lincoln", "aspen", "los alamos",
    # Southwest
    "tucson", "tempe", "phoenix", "albuquerque",
    # Texas
    "austin", "college station", "houston", "dallas",
    # West Coast
    "berkeley", "oakland", "stanford", "palo alto", "menlo park",
    "san francisco", "santa cruz", "santa barbara",
    "los angeles", "pasadena", "irvine", "riverside",
    "san diego", "la jolla", "davis",
    "seattle", "eugene", "portland",
    # Hawaii (astronomy)
    "honolulu", "hilo",
}

INTL_VENUE_CITIES = {
    # UK
    "oxford", "london", "edinburgh", "manchester",
    # Continental Europe
    "zurich", "lausanne", "geneva",
    "munich", "garching", "heidelberg", "potsdam",
    "paris", "saclay",
    "leiden", "amsterdam",
    "copenhagen", "stockholm",
    # Asia
    "tokyo", "kyoto", "beijing", "shanghai", "seoul",
    # Oceania
    "canberra", "sydney", "melbourne",
    # Canada
    "toronto", "vancouver", "montreal", "waterloo",
}

# "cambridge" is shared between Cambridge MA (USA) and Cambridge UK; both
# qualify, so it's only listed under US_VENUE_CITIES — the country check
# routes correctly.


def today() -> date:
    return datetime.now(timezone.utc).date()


def fetch_inspire(category: str) -> list[dict]:
    """Fetch conferences from INSPIRE matching a single category, future events only."""
    cutoff = today().isoformat()
    q = f'inspire_categories.term:"{category}" AND opening_date:[{cutoff} TO *]'
    results: list[dict] = []
    for page in range(1, MAX_PAGES + 1):
        params = {
            "q": q,
            "size": PAGE_SIZE,
            "page": page,
            "sort": "dateasc",
            "fields": (
                "titles,cnum,opening_date,closing_date,addresses,"
                "inspire_categories,series,urls,acronyms"
            ),
        }
        try:
            r = requests.get(INSPIRE_URL, params=params, timeout=30)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"  [warn] INSPIRE fetch failed for {category!r}: {e}", file=sys.stderr)
            break
        data = r.json()
        hits = (data.get("hits") or {}).get("hits") or []
        if not hits:
            break
        results.extend(hits)
        if len(hits) < PAGE_SIZE:
            break
    return results


def relevance_score(text: str) -> int:
    """Score an entry by keyword hits. Require >=1 positive match; strong negatives subtract."""
    t = (text or "").lower()
    pos = sum(1 for kw in POS_KEYWORDS if kw in t)
    if pos == 0:
        return 0
    neg = sum(1 for kw in NEG_KEYWORDS if kw in t)
    return pos - 2 * neg


def passes_venue_filter(location: str) -> bool:
    """True if the entry's host location is in our travel allowlist.
    Empty/unknown locations pass (commonly virtual)."""
    if not location:
        return True
    loc = location.lower()
    is_us = "usa" in loc or "united states" in loc
    cities = US_VENUE_CITIES if is_us else INTL_VENUE_CITIES
    return any(city in loc for city in cities)


def parse_inspire_hit(hit: dict) -> dict | None:
    meta = hit.get("metadata", {}) or {}
    titles = meta.get("titles") or []
    if not titles:
        return None
    title = (titles[0].get("title") or "").strip()
    if not title:
        return None
    opening = meta.get("opening_date")
    closing = meta.get("closing_date") or opening
    if not opening:
        return None

    subtitle = (titles[0].get("subtitle") or "").strip()
    if relevance_score(title + " " + subtitle) < MIN_RELEVANCE_SCORE:
        return None

    addrs = meta.get("addresses") or []
    location = ""
    if addrs:
        a = addrs[0]
        parts = []
        cities = a.get("cities") or []
        if cities:
            parts.append(cities[0])
        country = a.get("country") or a.get("country_code")
        if country:
            parts.append(country)
        location = ", ".join(parts)

    if not passes_venue_filter(location):
        return None

    cats = [c.get("term") for c in (meta.get("inspire_categories") or []) if c.get("term")]
    tags = ["conference"]
    if "Astrophysics" in cats:
        tags.append("astro")
    if "Gravitation and Cosmology" in cats:
        tags.append("cosmo")

    urls = meta.get("urls") or []
    url = urls[0].get("value") if urls and urls[0].get("value") else f"https://inspirehep.net/conferences/{hit.get('id')}"

    series = (meta.get("series") or [{}])[0].get("name")
    acronyms = meta.get("acronyms") or []
    short = acronyms[0] if acronyms else series

    return {
        "id": f"inspire-{hit.get('id')}",
        "name": short or title[:60],
        "full_name": title,
        "url": url,
        "location": location,
        "submission_deadline": None,
        "deadline_note": None,
        "start": opening,
        "end": closing,
        "tags": sorted(set(tags)),
        "source": "inspire-hep",
        "approximate": False,
    }


# ---------- ai-deadlines fetch ----------

def _coerce_date(v) -> str | None:
    """YAML safe_load turns bare `YYYY-MM-DD` into a datetime.date; coerce to ISO string."""
    if v is None:
        return None
    if isinstance(v, (date, datetime)):
        return v.isoformat()[:10]
    if isinstance(v, str):
        return v[:10] if v else None
    return None


def fetch_ai_deadlines(whitelist: list[str] = AI_DEADLINES_WHITELIST) -> list[dict]:
    """Fetch per-venue YAML from huggingface/ai-deadlines and pick the most
    upcoming entry per venue. Returns normalized records."""
    today_iso = today().isoformat()
    out: list[dict] = []
    for slug in whitelist:
        url = f"{AI_DEADLINES_RAW}/{slug}.yml"
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 404:
                continue  # venue removed upstream
            r.raise_for_status()
            entries = yaml.safe_load(r.text) or []
        except Exception as e:
            print(f"  [warn] ai-deadlines fetch failed for {slug}: {e}", file=sys.stderr)
            continue
        if not isinstance(entries, list):
            continue
        best = _pick_ai_deadlines_entry(entries, today_iso)
        if best is None:
            continue
        rec = _parse_ai_deadlines_entry(best)
        if rec:
            out.append(rec)
    return out


def _pick_ai_deadlines_entry(entries: list[dict], today_iso: str) -> dict | None:
    """Pick the entry with the most future-facing deadline. Prefer upcoming
    paper/abstract CFP; fall back to upcoming event; skip fully-past venues.
    Ties are broken by year (latest wins)."""
    best = None
    best_key: tuple = (0, 0)  # (base, year); base 0 means not-in-scope
    for e in entries:
        if not isinstance(e, dict):
            continue
        paper_future = False
        for d in e.get("deadlines") or []:
            if not isinstance(d, dict):
                continue
            if d.get("type") in ("paper", "abstract"):
                date_str = str(d.get("date", ""))[:10]
                if date_str and date_str >= today_iso:
                    paper_future = True
                    break
        end_raw = e.get("end") or e.get("start") or ""
        end_str = str(end_raw)[:10] if end_raw else ""
        event_future = bool(end_str) and end_str >= today_iso
        if paper_future:
            base = 2
        elif event_future:
            base = 1
        else:
            continue  # strictly past — skip
        key = (base, e.get("year") or 0)
        if key > best_key:
            best = e
            best_key = key
    return best


def _parse_ai_deadlines_entry(e: dict) -> dict | None:
    today_iso = today().isoformat()
    deadlines = e.get("deadlines") or []
    paper_dl = None
    abstract_dl = None
    for d in deadlines:
        if not isinstance(d, dict):
            continue
        if d.get("type") == "paper":
            paper_dl = d
        elif d.get("type") == "abstract" and abstract_dl is None:
            abstract_dl = d
    # Only keep a deadline if it's actually upcoming — past deadlines would
    # otherwise rank the entry at the top of the page as stale "red" cards.
    primary = None
    for candidate in (paper_dl, abstract_dl):
        if candidate is None:
            continue
        cand_iso = str(candidate.get("date", ""))[:10]
        if cand_iso and cand_iso >= today_iso:
            primary = candidate
            break

    dl_date = None
    dl_note = None
    if primary:
        dl_date = str(primary.get("date", ""))[:10]
        dl_label = primary.get("label") or primary.get("type") or "submission"
        tz = primary.get("timezone") or ""
        dl_note = f"{dl_label}" + (f" ({tz})" if tz else "")
        if paper_dl and abstract_dl and paper_dl is primary:
            abs_iso = str(abstract_dl.get("date", ""))[:10]
            if abs_iso and abs_iso >= today_iso:
                dl_note += f"; abstract due {abs_iso}"

    city = e.get("city") or ""
    country = e.get("country") or ""
    location = ", ".join(p for p in [city, country] if p) or None

    year = e.get("year")
    title = (e.get("title") or "").strip()
    name = f"{title} {year}".strip() if title and year else (title or str(e.get("id") or "ai-deadlines"))

    start = _coerce_date(e.get("start"))
    end = _coerce_date(e.get("end"))

    upstream_tags = [t for t in (e.get("tags") or []) if isinstance(t, str)]
    tags = sorted(set(["ml", "conference"] + upstream_tags))

    return {
        "id": f"ai-deadlines:{e.get('id', name.lower().replace(' ', '-'))}",
        "name": name,
        "full_name": e.get("full_name"),
        "url": e.get("link"),
        "location": location,
        "submission_deadline": dl_date,
        "deadline_note": dl_note,
        "start": start,
        "end": end,
        "tags": tags,
        "source": "ai-deadlines",
        "approximate": False,
    }


# ---------- curated ----------

def load_curated() -> list[dict]:
    if not CURATED.exists():
        return []
    raw = yaml.safe_load(CURATED.read_text(encoding="utf-8")) or {}
    entries = raw.get("entries") or []
    normalized = []
    for e in entries:
        if not isinstance(e, dict) or not e.get("id") or not e.get("name"):
            continue
        normalized.append({
            "id": e["id"],
            "name": e["name"],
            "full_name": e.get("full_name"),
            "url": e.get("url"),
            "parent": e.get("parent"),
            "location": e.get("location"),
            "submission_deadline": e.get("submission_deadline"),
            "deadline_note": e.get("deadline_note"),
            "notification": e.get("notification"),
            "start": e.get("start"),
            "end": e.get("end"),
            "tags": sorted(set(e.get("tags") or [])),
            "notes": e.get("notes"),
            "approximate": bool(e.get("approximate", False)),
            "source": "curated",
        })
    return normalized


def merge(curated: list[dict], *others: list[dict]) -> list[dict]:
    """Curated wins on id collision; remaining sources are appended in order,
    each losing to anything already present (first source wins for a given id)."""
    by_id: dict[str, dict] = {e["id"]: e for e in curated}
    for src in others:
        for e in src:
            by_id.setdefault(e["id"], e)
    return list(by_id.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-inspire", action="store_true", help="Skip the INSPIRE-HEP pull")
    ap.add_argument("--no-ai-deadlines", action="store_true", help="Skip the ai-deadlines pull")
    args = ap.parse_args()

    print(f"[update] loading curated from {CURATED}")
    curated = load_curated()
    print(f"  {len(curated)} curated entries")

    inspire_hits: list[dict] = []
    if not args.no_inspire:
        for cat in INSPIRE_CATEGORIES:
            print(f"[update] fetching INSPIRE-HEP category {cat!r}")
            hits = fetch_inspire(cat)
            print(f"  {len(hits)} raw hits")
            inspire_hits.extend(hits)

    parsed = [p for p in (parse_inspire_hit(h) for h in inspire_hits) if p]
    dropped = len(inspire_hits) - len(parsed)
    print(f"[update] {len(parsed)} INSPIRE entries after relevance filter ({dropped} dropped)")

    # Secondary dedupe: INSPIRE sometimes has multiple records for the same
    # physical conference (e.g. series + instance). Collapse on (title, start).
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for p in parsed:
        key = ((p.get("full_name") or p.get("name") or "").strip().lower(), p.get("start") or "")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(p)
    if len(deduped) != len(parsed):
        print(f"[update] deduped {len(parsed) - len(deduped)} title-collision entries")
    parsed = deduped

    ai_entries: list[dict] = []
    if not args.no_ai_deadlines:
        print(f"[update] fetching huggingface/ai-deadlines ({len(AI_DEADLINES_WHITELIST)} venues)")
        ai_entries = fetch_ai_deadlines()
        print(f"  {len(ai_entries)} venues with upcoming deadline or event")

    merged = merge(curated, ai_entries, parsed)
    merged.sort(key=_sort_key)

    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "today": today().isoformat(),
        "categories_queried": INSPIRE_CATEGORIES,
        "entries": merged,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[update] wrote {len(merged)} entries → {OUT}")
    return 0


def _sort_key(e: dict):
    """Entries with a deadline sort first (by deadline asc).
    Then entries with a start date (by start asc). Then the rest."""
    d = e.get("submission_deadline")
    s = e.get("start")
    if d:
        return (0, d)
    if s:
        return (1, s)
    return (2, e.get("name", "").lower())


if __name__ == "__main__":
    raise SystemExit(main())
