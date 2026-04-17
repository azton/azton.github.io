"""Refresh the My Work page data file.

Queries arXiv and Semantic Scholar for the author, merges/dedups across
sources, and writes a consolidated JSON blob that the static site renders
client-side.

Usage:
    python tools/works/update.py

Run it from the site repo root (or anywhere — paths resolve relative to this
file). Commit the updated `assets/data/works.json` + any `overrides.yml`
changes and push.

Designed to be extensible: a `fetch_*` function per source produces records
in a shared normalized shape, then a single merge pass dedups across sources
by arXiv id → DOI → normalized title. Add bioRxiv later by writing
`fetch_biorxiv` that returns the same record shape.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import yaml

THIS = Path(__file__).resolve()
ROOT = THIS.parent.parent.parent
OVERRIDES = THIS.parent / "overrides.yml"
OUT = ROOT / "assets" / "data" / "works.json"

ARXIV_ENDPOINT = "http://export.arxiv.org/api/query"
ARXIV_AUTHOR_QUERY = 'au:"Azton Wells"'
ARXIV_PAGE_SIZE = 100

S2_ENDPOINT = "https://api.semanticscholar.org/graph/v1"
S2_PAPER_FIELDS = "title,abstract,authors,year,publicationDate,venue,externalIds,openAccessPdf,url"
S2_PAGE_SIZE = 100
S2_REQUEST_DELAY_S = 1.2  # public tier: ~100 req / 5 min

# Strings that count as an unambiguous match for this author.
EXACT_NAME_FORMS = {
    "azton wells",
    "azton i wells",
    "azton i. wells",
    "azton i.wells",
}

NS = {
    "a": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}


# ---------- arxiv fetch ----------

def fetch_arxiv(query: str = ARXIV_AUTHOR_QUERY, page_size: int = ARXIV_PAGE_SIZE) -> list[dict]:
    """Fetch arXiv entries page-by-page until exhausted. Returns raw parsed records."""
    out: list[dict] = []
    start = 0
    while True:
        params = urllib.parse.urlencode({
            "search_query": query,
            "start": start,
            "max_results": page_size,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        })
        url = f"{ARXIV_ENDPOINT}?{params}"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                body = r.read()
        except Exception as e:
            print(f"  [warn] arXiv fetch failed @ start={start}: {e}", file=sys.stderr)
            break

        root = ET.fromstring(body)
        entries = root.findall("a:entry", NS)
        if not entries:
            break
        for e in entries:
            rec = _parse_arxiv_entry(e)
            if rec:
                out.append(rec)
        if len(entries) < page_size:
            break
        start += page_size
        time.sleep(3)  # arXiv asks for ~3s between queries.
    return out


def _parse_arxiv_entry(e: ET.Element) -> dict | None:
    def text(tag: str, root: ET.Element = e) -> str:
        el = root.find(f"a:{tag}", NS)
        return (el.text or "").strip() if el is not None and el.text else ""

    raw_id = text("id")  # e.g. http://arxiv.org/abs/2510.07684v1
    if not raw_id:
        return None
    short_id = raw_id.rsplit("/", 1)[-1]
    bare_id = short_id.split("v")[0]

    authors: list[dict] = []
    for a in e.findall("a:author", NS):
        name_el = a.find("a:name", NS)
        aff_el = a.find("arxiv:affiliation", NS)
        if name_el is None or not (name_el.text or "").strip():
            continue
        authors.append({
            "name": (name_el.text or "").strip(),
            "affiliation": (aff_el.text or "").strip() if aff_el is not None else None,
        })

    categories = [c.get("term") for c in e.findall("a:category", NS) if c.get("term")]
    primary_el = e.find("arxiv:primary_category", NS)
    primary = primary_el.get("term") if primary_el is not None else (categories[0] if categories else None)

    doi_el = e.find("arxiv:doi", NS)
    comment_el = e.find("arxiv:comment", NS)

    pdf_url = None
    for link in e.findall("a:link", NS):
        if link.get("title") == "pdf" or link.get("type") == "application/pdf":
            pdf_url = link.get("href")
            break

    return {
        "id": f"arxiv:{bare_id}",
        "arxiv_id": bare_id,
        "arxiv_version": short_id,
        "title": _collapse_ws(text("title")),
        "abstract": _collapse_ws(text("summary")),
        "authors": authors,
        "published": text("published"),
        "updated": text("updated"),
        "primary_category": primary,
        "categories": categories,
        "url": f"https://arxiv.org/abs/{bare_id}",
        "pdf_url": pdf_url or f"https://arxiv.org/pdf/{bare_id}",
        "doi": (doi_el.text or "").strip() if doi_el is not None and doi_el.text else None,
        "comment": (comment_el.text or "").strip() if comment_el is not None and comment_el.text else None,
        "venue": None,
        "author_ids_s2": [],
        "source": "arxiv",
    }


# ---------- semantic scholar fetch ----------

def fetch_semanticscholar(author_ids: list[str]) -> list[dict]:
    """Fetch papers for each pinned S2 author ID. Returns normalized records."""
    out: list[dict] = []
    seen_paper_ids: set[str] = set()
    for aid in author_ids:
        url = f"{S2_ENDPOINT}/author/{aid}/papers?fields={urllib.parse.quote(S2_PAPER_FIELDS)}&limit={S2_PAGE_SIZE}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "azton.github.io/works-updater"})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
        except Exception as e:
            print(f"  [warn] Semantic Scholar fetch failed for author {aid}: {e}", file=sys.stderr)
            time.sleep(S2_REQUEST_DELAY_S)
            continue

        try:
            payload = json.loads(body)
        except Exception as e:
            print(f"  [warn] Semantic Scholar JSON parse failed for author {aid}: {e}", file=sys.stderr)
            time.sleep(S2_REQUEST_DELAY_S)
            continue

        for p in payload.get("data") or []:
            pid = p.get("paperId")
            if not pid or pid in seen_paper_ids:
                continue
            seen_paper_ids.add(pid)
            rec = _parse_s2_paper(p)
            if rec:
                out.append(rec)
        time.sleep(S2_REQUEST_DELAY_S)
    return out


def _parse_s2_paper(p: dict) -> dict | None:
    pid = p.get("paperId")
    title = _collapse_ws(p.get("title") or "")
    if not pid or not title:
        return None

    ext = p.get("externalIds") or {}
    arxiv_id = ext.get("ArXiv")
    doi = ext.get("DOI")
    # S2 often synthesizes a DOI of the form 10.48550/arXiv.<id> for arxiv-only
    # preprints. That DOI adds no information over the arxiv id and clutters
    # the UI, so drop it.
    if doi and doi.lower().startswith("10.48550/arxiv."):
        doi = None

    pub = p.get("publicationDate")
    if not pub and p.get("year"):
        pub = f"{p['year']}-01-01"
    pub_iso = f"{pub}T00:00:00Z" if pub and "T" not in pub else (pub or "")

    oa = p.get("openAccessPdf") or {}
    pdf_url = oa.get("url") if isinstance(oa, dict) else None

    if arxiv_id:
        url = f"https://arxiv.org/abs/{arxiv_id}"
        rid = f"arxiv:{arxiv_id}"
        if not pdf_url:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    elif doi:
        url = f"https://doi.org/{doi}"
        rid = f"doi:{doi.lower()}"
    else:
        url = p.get("url") or f"https://www.semanticscholar.org/paper/{pid}"
        rid = f"s2:{pid}"

    authors = []
    s2_author_ids: list[str] = []
    for a in p.get("authors") or []:
        name = (a.get("name") or "").strip()
        if name:
            authors.append({"name": name, "affiliation": None})
        if a.get("authorId"):
            s2_author_ids.append(str(a["authorId"]))

    return {
        "id": rid,
        "arxiv_id": arxiv_id,
        "arxiv_version": None,
        "title": title,
        "abstract": _collapse_ws(p.get("abstract") or ""),
        "authors": authors,
        "published": pub_iso,
        "updated": pub_iso,
        "primary_category": None,
        "categories": [],
        "url": url,
        "pdf_url": pdf_url,
        "doi": doi,
        "comment": None,
        "venue": (p.get("venue") or None) or None,
        "author_ids_s2": s2_author_ids,
        "s2_paper_id": pid,
        "source": "semanticscholar",
    }


def _collapse_ws(s: str) -> str:
    return " ".join(s.split())


# ---------- merge / dedup ----------

_TITLE_NORM_RX = re.compile(r"[^a-z0-9]+")


def _norm_title(t: str) -> str:
    return _TITLE_NORM_RX.sub("", (t or "").lower())


def _dedup_key(rec: dict) -> str:
    if rec.get("arxiv_id"):
        return f"arxiv:{rec['arxiv_id']}"
    if rec.get("doi"):
        return f"doi:{rec['doi'].lower()}"
    return f"title:{_norm_title(rec.get('title', ''))}"


def merge_records(*source_lists: list[dict]) -> list[dict]:
    """Merge records from multiple sources. Earlier sources win on core fields."""
    merged: dict[str, dict] = {}
    for src_list in source_lists:
        for rec in src_list:
            key = _dedup_key(rec)
            if key in merged:
                _fill_from(merged[key], rec)
            else:
                merged[key] = dict(rec)
                merged[key]["sources"] = [rec.get("source", "?")]
    return list(merged.values())


def _fill_from(dst: dict, src: dict) -> None:
    """Fill missing fields on dst with values from src. Also merges list-like metadata."""
    for k in ("doi", "venue", "comment", "pdf_url", "abstract", "published", "updated"):
        if not dst.get(k) and src.get(k):
            dst[k] = src[k]
    extra_s2 = src.get("author_ids_s2") or []
    if extra_s2:
        existing = dst.get("author_ids_s2") or []
        dst["author_ids_s2"] = sorted(set(existing) | set(extra_s2))
    if src.get("s2_paper_id") and not dst.get("s2_paper_id"):
        dst["s2_paper_id"] = src["s2_paper_id"]
    src_name = src.get("source")
    if src_name and src_name not in (dst.get("sources") or []):
        dst.setdefault("sources", []).append(src_name)


# ---------- disambiguation ----------

def classify(rec: dict, overrides: dict, pinned_s2_ids: set[str]) -> tuple[str, str]:
    """Return (status, reason). status ∈ {included, excluded, needs_review}."""
    candidate_keys = _override_keys(rec)
    exclude = set(str(x) for x in (overrides.get("exclude") or []))
    include = set(str(x) for x in (overrides.get("include") or []))
    if candidate_keys & exclude:
        return "excluded", "manual exclude"
    if candidate_keys & include:
        return "included", "manual include"

    # S2 pinned author ID match — the user vetted these IDs, so any paper S2
    # ties to them is trusted. This is how we pick up non-arxiv publications.
    rec_s2_ids = set(rec.get("author_ids_s2") or [])
    if rec_s2_ids & pinned_s2_ids:
        return "included", "pinned S2 author id"

    # Exact name-form match on any source's author list.
    for a in rec.get("authors") or []:
        name = (a.get("name") or "").lower().replace(".", "")
        key = " ".join(name.split())
        if key in EXACT_NAME_FORMS:
            return "included", "exact name match"

    return "needs_review", "no unambiguous match"


def _override_keys(rec: dict) -> set[str]:
    """Every string that could match an include/exclude entry for this record."""
    keys: set[str] = set()
    if rec.get("id"):
        keys.add(rec["id"])
    if rec.get("arxiv_id"):
        keys.add(rec["arxiv_id"])
        keys.add(f"arxiv:{rec['arxiv_id']}")
    if rec.get("doi"):
        keys.add(f"doi:{rec['doi'].lower()}")
    if rec.get("s2_paper_id"):
        keys.add(f"s2:{rec['s2_paper_id']}")
    return keys


def load_overrides() -> dict:
    if not OVERRIDES.exists():
        return {"include": [], "exclude": [], "semantic_scholar": {"author_ids": []}}
    raw = yaml.safe_load(OVERRIDES.read_text(encoding="utf-8")) or {}
    s2_cfg = raw.get("semantic_scholar") or {}
    return {
        "include": [str(x) for x in (raw.get("include") or [])],
        "exclude": [str(x) for x in (raw.get("exclude") or [])],
        "semantic_scholar": {
            "author_ids": [str(x) for x in (s2_cfg.get("author_ids") or [])],
        },
    }


# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Don't write; just print summary.")
    ap.add_argument("--query", default=ARXIV_AUTHOR_QUERY)
    ap.add_argument("--skip-s2", action="store_true", help="Skip Semantic Scholar fetch.")
    ap.add_argument("--skip-arxiv", action="store_true", help="Skip arXiv fetch.")
    args = ap.parse_args()

    print(f"[update] loading overrides from {OVERRIDES}")
    overrides = load_overrides()
    print(f"  include: {overrides['include'] or '(none)'}")
    print(f"  exclude: {overrides['exclude'] or '(none)'}")
    pinned_s2_ids = set(overrides["semantic_scholar"]["author_ids"])
    print(f"  pinned S2 author ids: {sorted(pinned_s2_ids) or '(none)'}")

    sources_queried: list[str] = []
    arxiv_recs: list[dict] = []
    s2_recs: list[dict] = []

    if not args.skip_arxiv:
        print(f"[update] querying arXiv: {args.query}")
        arxiv_recs = fetch_arxiv(args.query)
        print(f"  {len(arxiv_recs)} raw arXiv entries")
        sources_queried.append("arxiv")

    if not args.skip_s2 and pinned_s2_ids:
        print(f"[update] querying Semantic Scholar for {len(pinned_s2_ids)} author ids")
        s2_recs = fetch_semanticscholar(sorted(pinned_s2_ids))
        print(f"  {len(s2_recs)} raw S2 entries")
        sources_queried.append("semanticscholar")

    # arXiv first so it wins on field collisions (richer categories, versioning).
    merged = merge_records(arxiv_recs, s2_recs)
    print(f"[update] merged → {len(merged)} unique records (from {len(arxiv_recs)} arXiv + {len(s2_recs)} S2)")

    for rec in merged:
        status, reason = classify(rec, overrides, pinned_s2_ids)
        rec["status"] = status
        rec["status_reason"] = reason

    merged.sort(key=lambda r: r.get("published", ""), reverse=True)

    counts = {"included": 0, "excluded": 0, "needs_review": 0}
    for r in merged:
        counts[r["status"]] += 1

    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sources_queried": sources_queried,
        "query": args.query,
        "counts": counts,
        "entries": merged,
    }

    print(f"[update] included={counts['included']} excluded={counts['excluded']} needs_review={counts['needs_review']}")
    if counts["needs_review"]:
        print("  Papers that need review (add to overrides.yml → include or exclude):")
        for r in merged:
            if r["status"] == "needs_review":
                first_author = r["authors"][0]["name"] if r["authors"] else "?"
                ident = r.get("arxiv_id") or r.get("doi") or r.get("id")
                print(f"    {ident} — {r['title'][:70]} (lead: {first_author})")

    if args.dry_run:
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[update] wrote → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
