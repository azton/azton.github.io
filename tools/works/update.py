"""Refresh the My Work page data file.

Queries arXiv for the author and writes a consolidated JSON blob that the
static site renders client-side.

Usage:
    python tools/works/update.py

Run it from the site repo root (or anywhere — paths resolve relative to this
file). Commit the updated `assets/data/works.json` + any `overrides.yml`
changes and push.

Designed to be extensible: a `fetch_*` function per source feeds a single
parse/normalize pipeline. Add bioRxiv later by writing `fetch_biorxiv` with
the same record shape.
"""
from __future__ import annotations

import argparse
import json
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
        "source": "arxiv",
    }


def _collapse_ws(s: str) -> str:
    return " ".join(s.split())


# ---------- disambiguation ----------

def classify(rec: dict, overrides: dict) -> tuple[str, str]:
    """Return (status, reason). status ∈ {included, excluded, needs_review}."""
    bare = rec.get("arxiv_id", "")
    if bare in overrides.get("exclude", []):
        return "excluded", "manual exclude"
    if bare in overrides.get("include", []):
        return "included", "manual include"

    names = [a["name"].lower().replace(".", "") for a in rec.get("authors", [])]
    for n in names:
        tokens = n.split()
        # Strict: exact "azton wells" or "azton i wells" (case-insensitive,
        # punctuation-tolerant). Anything else routes to review.
        key = " ".join(tokens)
        if key in EXACT_NAME_FORMS:
            return "included", "exact name match"
    return "needs_review", "no unambiguous name form matched"


def load_overrides() -> dict:
    if not OVERRIDES.exists():
        return {"include": [], "exclude": []}
    raw = yaml.safe_load(OVERRIDES.read_text(encoding="utf-8")) or {}
    return {
        "include": [str(x) for x in (raw.get("include") or [])],
        "exclude": [str(x) for x in (raw.get("exclude") or [])],
    }


# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Don't write; just print summary.")
    ap.add_argument("--query", default=ARXIV_AUTHOR_QUERY)
    args = ap.parse_args()

    print(f"[update] loading overrides from {OVERRIDES}")
    overrides = load_overrides()
    print(f"  include: {overrides['include'] or '(none)'}")
    print(f"  exclude: {overrides['exclude'] or '(none)'}")

    print(f"[update] querying arXiv: {args.query}")
    raw = fetch_arxiv(args.query)
    print(f"  {len(raw)} raw arXiv entries")

    for rec in raw:
        status, reason = classify(rec, overrides)
        rec["status"] = status
        rec["status_reason"] = reason

    raw.sort(key=lambda r: r.get("published", ""), reverse=True)

    counts = {"included": 0, "excluded": 0, "needs_review": 0}
    for r in raw:
        counts[r["status"]] += 1

    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sources_queried": ["arxiv"],
        "query": args.query,
        "counts": counts,
        "entries": raw,
    }

    print(f"[update] included={counts['included']} excluded={counts['excluded']} needs_review={counts['needs_review']}")
    if counts["needs_review"]:
        print("  Papers that need review (add to overrides.yml → include or exclude):")
        for r in raw:
            if r["status"] == "needs_review":
                first_author = r["authors"][0]["name"] if r["authors"] else "?"
                print(f"    {r['arxiv_id']} — {r['title'][:70]} (lead: {first_author})")

    if args.dry_run:
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[update] wrote → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
