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


def merge(curated: list[dict], inspire: list[dict]) -> list[dict]:
    """Curated entries win on id collision; otherwise concat."""
    by_id: dict[str, dict] = {e["id"]: e for e in curated}
    for e in inspire:
        by_id.setdefault(e["id"], e)
    return list(by_id.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-inspire", action="store_true", help="Skip the INSPIRE-HEP pull")
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
    print(f"[update] {len(parsed)} INSPIRE entries after parse/filter")

    merged = merge(curated, parsed)
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
