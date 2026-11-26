#!/usr/bin/env python3
"""Fetch rolling 24-month papers from the 9 target venues using DBLP + OpenAlex.

Target venues (strict whitelist):
  IJCV, TIP, CVPR, NeurIPS, AAAI, ICLR, ICCV, ECCV, TPAMI

Why dual-engine (DBLP + OpenAlex)?
  - DBLP indexes the 9 CS/CV/ML venues rapidly with exact stream IDs (zero venue
    pollution, no wasting page quota on unrelated journals or unrefereed arXiv).
  - OpenAlex enriches matched papers with abstracts, citation counts, and DOIs,
    and serves as a fallback/supplement for journal articles.

Uses only the Python standard library (zero pip dependencies).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DBLP_API_URL = "https://dblp.org/search/publ/api"
OPENALEX_WORKS_URL = "https://api.openalex.org/works"

# Exact DBLP stream prefixes for the 9 target venues
DBLP_STREAMS: dict[str, str] = {
    "CVPR": "streams/conf/cvpr",
    "ICCV": "streams/conf/iccv",
    "ECCV": "streams/conf/eccv",
    "NeurIPS": "streams/conf/nips",
    "ICLR": "streams/conf/iclr",
    "AAAI": "streams/conf/aaai",
    "TPAMI": "streams/journals/pami",
    "IJCV": "streams/journals/ijcv",
    "TIP": "streams/journals/tip",
}

VENUE_PATTERNS: dict[str, list[str]] = {
    "CVPR": [r"computer vision and pattern recognition", r"\bcvpr\b"],
    "ICCV": [r"international conference on computer vision", r"\biccv\b"],
    "ECCV": [r"european conference on computer vision", r"\beccv\b"],
    "NeurIPS": [r"neural information processing systems", r"\bneurips\b", r"\bnips\b"],
    "ICLR": [r"international conference on learning representations", r"\biclr\b"],
    "AAAI": [r"aaai conference on artificial intelligence", r"proceedings of the aaai", r"\baaai\b"],
    "TPAMI": [r"transactions on pattern analysis and machine intelligence", r"\btpami\b"],
    "IJCV": [r"international journal of computer vision", r"\bijcv\b"],
    "TIP": [r"ieee transactions on image processing", r"transactions on image processing"],
}

EXCLUDE_VENUE_SUBSTRINGS = [
    "workshop",
    "findings of",
    "arxiv",
    "biorxiv",
    "medrxiv",
    "ssrn",
    "companion",
]

SURVEY_TITLE_PATTERNS = [
    r"\bsurvey\b",
    r"\breview\b",
    r"\boverview\b",
    r"\bbenchmark(?:ing)?\b",
    r"\bdataset\b",
    r"\btaxonomy\b",
]

PIONEER_SIGNALS = [
    r"\bfirst\b",
    r"\bpioneer(?:ing)?\b",
    r"\boverlook(?:ed|ing)?\b",
    r"\brethink(?:ing)?\b",
    r"\brevisit(?:ing)?\b",
    r"\bneglect(?:ed|ing)?\b",
    r"\bnovel paradigm\b",
    r"\bnew paradigm\b",
    r"\bzero-shot\b",
    r"\bagentic\b",
    r"\bself-correct",
    r"\btest-time\b",
    r"\bflow matching\b",
    r"\brectified flow\b",
]


def http_get_json(url: str, timeout: int = 25) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hsi-msi-idea-scout_codex/1.1 (Academic Research Skill)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str:
    if not inverted_index:
        return ""
    max_pos = 0
    for positions in inverted_index.values():
        if positions:
            max_pos = max(max_pos, max(positions))
    words = [""] * (max_pos + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            if 0 <= pos <= max_pos:
                words[pos] = word
    return " ".join(w for w in words if w).strip()


def is_survey_like(title: str) -> bool:
    low = title.lower()
    return any(re.search(pat, low) for pat in SURVEY_TITLE_PATTERNS)


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def compute_triage_hint(title: str, abstract: str, cited_by: int, year: int | None) -> tuple[float, list[str]]:
    """Heuristic triage hint only — never a substitute for reading the abstract/paper."""
    text = f"{title} {abstract}".lower()
    matched: list[str] = []
    for pat in PIONEER_SIGNALS:
        if re.search(pat, text):
            clean = re.sub(r"\\b|\(\?:[^)]*\)|\?", "", pat)
            matched.append(clean)

    # Cap keyword bonus so buzzword-heavy papers cannot dominate purely on adjectives
    keyword_part = min(len(matched), 3) * 1.2
    years_old = max(0.5, (dt.date.today().year - (year or dt.date.today().year)) + 0.5)
    cite_part = min(cited_by / years_old, 60.0) * 0.08
    return round(keyword_part + cite_part, 2), matched


def fetch_dblp_for_venue(
    query: str,
    venue: str,
    min_year: int,
    max_hits: int,
    include_surveys: bool,
) -> list[dict[str, Any]]:
    stream = DBLP_STREAMS[venue]
    dblp_q = f"{query} stream:{stream}:"
    params = {"q": dblp_q, "h": max_hits, "format": "json"}
    url = f"{DBLP_API_URL}?{urllib.parse.urlencode(params)}"
    data = http_get_json(url)
    hits = (((data.get("result") or {}).get("hits") or {}).get("hit")) or []

    results: list[dict[str, Any]] = []
    for h in hits:
        info = h.get("info") or {}
        title = str(info.get("title") or "").strip().rstrip(".")
        if not title:
            continue
        if not include_surveys and is_survey_like(title):
            continue

        raw_venue = str(info.get("venue") or venue)
        if any(bad in raw_venue.lower() for bad in EXCLUDE_VENUE_SUBSTRINGS):
            continue

        try:
            year = int(info.get("year") or 0)
        except ValueError:
            year = 0
        if year < min_year:
            continue

        authors_field = (info.get("authors") or {}).get("author")
        authors: list[str] = []
        if isinstance(authors_field, list):
            for a in authors_field[:5]:
                authors.append(a.get("text", "") if isinstance(a, dict) else str(a))
        elif isinstance(authors_field, dict):
            authors.append(authors_field.get("text", ""))
        elif isinstance(authors_field, str):
            authors.append(authors_field)

        doi = str(info.get("doi") or "")
        ee = info.get("ee") or ""
        if isinstance(ee, list):
            ee = ee[0] if ee else ""
        paper_url = str(ee) or (f"https://doi.org/{doi}" if doi else str(info.get("url") or ""))

        results.append(
            {
                "source_engine": "dblp",
                "title": title,
                "authors": [a for a in authors if a],
                "venue": venue,
                "raw_venue": raw_venue,
                "publication_year": year,
                "publication_date": str(year),
                "cited_by_count": 0,
                "doi": f"https://doi.org/{doi}" if doi and not doi.startswith("http") else doi,
                "url": paper_url,
                "matched_query": query,
                "abstract": "",
                "abstract_verified": False,
            }
        )
    return results


def enrich_with_openalex(paper: dict[str, Any], mailto: str | None) -> None:
    """Enrich a DBLP paper with abstract and citation count from OpenAlex."""
    params: dict[str, Any] = {"per-page": 3}
    if mailto:
        params["mailto"] = mailto

    doi = paper.get("doi") or ""
    if doi:
        params["filter"] = f"doi:{doi}"
    else:
        params["search"] = paper["title"]

    url = f"{OPENALEX_WORKS_URL}?{urllib.parse.urlencode(params)}"
    try:
        data = http_get_json(url, timeout=15)
    except Exception:
        return

    norm_target = normalize_title(paper["title"])
    for w in data.get("results") or []:
        w_title = normalize_title(str(w.get("display_name") or ""))
        if doi or w_title == norm_target or (len(norm_target) > 20 and norm_target in w_title):
            abstract = reconstruct_abstract(w.get("abstract_inverted_index"))
            if abstract:
                paper["abstract"] = abstract[:1800]
                paper["abstract_verified"] = True
            paper["cited_by_count"] = int(w.get("cited_by_count") or 0)
            if w.get("publication_date"):
                paper["publication_date"] = w["publication_date"]
            if w.get("id"):
                paper["openalex_id"] = w["id"]
            return


def match_openalex_venue(work: dict[str, Any], allowed_venues: set[str]) -> tuple[str | None, str]:
    candidate_sources: list[str] = []
    primary = work.get("primary_location") or {}
    if isinstance(primary, dict):
        src = primary.get("source") or {}
        if isinstance(src, dict) and src.get("display_name"):
            candidate_sources.append(str(src["display_name"]))
    for loc in work.get("locations") or []:
        if isinstance(loc, dict):
            src = loc.get("source") or {}
            if isinstance(src, dict) and src.get("display_name"):
                name = str(src["display_name"])
                if name not in candidate_sources:
                    candidate_sources.append(name)

    for raw_name in candidate_sources:
        low = raw_name.lower()
        if any(bad in low for bad in EXCLUDE_VENUE_SUBSTRINGS):
            continue
        for venue_key in allowed_venues:
            for pat in VENUE_PATTERNS[venue_key]:
                if re.search(pat, low):
                    return venue_key, raw_name
    return None, ""


def fetch_openalex_supplement(
    query: str,
    from_date: str,
    allowed_venues: set[str],
    include_surveys: bool,
    mailto: str | None,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "search": query,
        "filter": f"from_publication_date:{from_date}",
        "sort": "relevance_score:desc",
        "per-page": 50,
        "page": 1,
    }
    if mailto:
        params["mailto"] = mailto

    url = f"{OPENALEX_WORKS_URL}?{urllib.parse.urlencode(params)}"
    data = http_get_json(url)
    results: list[dict[str, Any]] = []
    for w in data.get("results") or []:
        venue_key, raw_venue = match_openalex_venue(w, allowed_venues)
        if not venue_key:
            continue
        title = (w.get("display_name") or "").strip()
        if not title or (not include_surveys and is_survey_like(title)):
            continue
        abstract = reconstruct_abstract(w.get("abstract_inverted_index"))
        authors = [
            a["author"]["display_name"]
            for a in (w.get("authorships") or [])[:5]
            if isinstance(a.get("author"), dict) and a["author"].get("display_name")
        ]
        doi = w.get("doi") or ""
        primary_loc = w.get("primary_location") or {}
        landing = primary_loc.get("landing_page_url") if isinstance(primary_loc, dict) else ""
        results.append(
            {
                "source_engine": "openalex",
                "openalex_id": w.get("id", ""),
                "title": title,
                "authors": authors,
                "venue": venue_key,
                "raw_venue": raw_venue,
                "publication_year": w.get("publication_year"),
                "publication_date": w.get("publication_date") or str(w.get("publication_year") or ""),
                "cited_by_count": int(w.get("cited_by_count") or 0),
                "doi": doi,
                "url": landing or doi or w.get("id", ""),
                "matched_query": query,
                "abstract": abstract[:1800],
                "abstract_verified": bool(abstract),
            }
        )
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch rolling 24-month papers from the 9 target venues (DBLP + OpenAlex)."
    )
    parser.add_argument(
        "--queries",
        required=True,
        help="Comma-separated focused queries, e.g. 'image restoration,medical image fusion,agentic restoration'",
    )
    parser.add_argument(
        "--venues",
        default="IJCV,TIP,CVPR,NeurIPS,AAAI,ICLR,ICCV,ECCV,TPAMI",
        help="Comma-separated subset of the 9 allowed venues.",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=24,
        help="Rolling lookback window in months (default: 24).",
    )
    parser.add_argument(
        "--source",
        choices=["both", "dblp", "openalex"],
        default="both",
        help="Retrieval backend: 'both' (DBLP venue-exact + OpenAlex enrichment, recommended), 'dblp', or 'openalex'.",
    )
    parser.add_argument(
        "--max-per-venue",
        type=int,
        default=12,
        help="Maximum papers to retain per venue in final output (default: 12).",
    )
    parser.add_argument(
        "--enrich-top",
        type=int,
        default=30,
        help="Enrich up to N DBLP papers with OpenAlex abstracts/citations (default: 30).",
    )
    parser.add_argument(
        "--include-surveys",
        action="store_true",
        help="Keep survey/review/benchmark papers (excluded by default).",
    )
    parser.add_argument(
        "--mailto",
        default=None,
        help="Optional email for OpenAlex polite pool.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON file path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    requested_venues = [v.strip() for v in args.venues.split(",") if v.strip()]
    invalid = set(requested_venues) - set(DBLP_STREAMS.keys())
    if invalid:
        print(f"Error: Unsupported venues requested: {sorted(invalid)}", file=sys.stderr)
        print(f"Allowed venues: {sorted(DBLP_STREAMS.keys())}", file=sys.stderr)
        return 2

    today = dt.date.today()
    from_date_obj = today - dt.timedelta(days=args.months * 30)
    from_date = from_date_obj.isoformat()
    min_year = from_date_obj.year
    queries = [q.strip() for q in args.queries.split(",") if q.strip()]

    dedup: dict[str, dict[str, Any]] = {}
    network_errors: list[str] = []

    if args.source in ("both", "dblp"):
        for q in queries:
            for venue in requested_venues:
                try:
                    batch = fetch_dblp_for_venue(
                        query=q,
                        venue=venue,
                        min_year=min_year,
                        max_hits=max(15, args.max_per_venue * 2),
                        include_surveys=args.include_surveys,
                    )
                    for item in batch:
                        key = normalize_title(item["title"])
                        if key not in dedup:
                            dedup[key] = item
                except urllib.error.URLError as exc:
                    network_errors.append(f"DBLP({venue}, '{q}'): {exc}")
                time.sleep(0.2)

    if args.source in ("both", "openalex"):
        allowed_set = set(requested_venues)
        for q in queries:
            try:
                batch = fetch_openalex_supplement(
                    query=q,
                    from_date=from_date,
                    allowed_venues=allowed_set,
                    include_surveys=args.include_surveys,
                    mailto=args.mailto,
                )
                for item in batch:
                    key = normalize_title(item["title"])
                    if key not in dedup or (not dedup[key].get("abstract") and item.get("abstract")):
                        dedup[key] = item
            except urllib.error.URLError as exc:
                network_errors.append(f"OpenAlex('{q}'): {exc}")
            time.sleep(0.2)

    if not dedup and network_errors:
        print(
            "Network blocked or unreachable across retrieval backends. "
            "Do not fabricate papers; enable network access or supply local metadata.\n"
            + "\n".join(network_errors[:5]),
            file=sys.stderr,
        )
        return 1

    # Enrich DBLP entries lacking abstracts via OpenAlex
    if args.source == "both" and args.enrich_top > 0:
        needs_enrich = [p for p in dedup.values() if not p.get("abstract")]
        needs_enrich.sort(key=lambda x: x.get("publication_year") or 0, reverse=True)
        for paper in needs_enrich[: args.enrich_top]:
            enrich_with_openalex(paper, args.mailto)
            time.sleep(0.15)

    for paper in dedup.values():
        score, signals = compute_triage_hint(
            paper["title"],
            paper.get("abstract", ""),
            int(paper.get("cited_by_count") or 0),
            paper.get("publication_year"),
        )
        paper["triage_hint_score"] = score
        paper["triage_signals"] = signals

    sorted_all = sorted(
        dedup.values(),
        key=lambda x: (
            bool(x.get("abstract")),
            x.get("triage_hint_score", 0.0),
            x.get("publication_year") or 0,
            x.get("cited_by_count") or 0,
        ),
        reverse=True,
    )

    venue_counts: dict[str, int] = {}
    filtered: list[dict[str, Any]] = []
    for item in sorted_all:
        v = item["venue"]
        if venue_counts.get(v, 0) < args.max_per_venue:
            venue_counts[v] = venue_counts.get(v, 0) + 1
            filtered.append(item)

    payload = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "source_mode": args.source,
        "rolling_window": {"from_date": from_date, "to_date": today.isoformat(), "months": args.months},
        "allowed_venues": sorted(requested_venues),
        "queries": queries,
        "total_matched": len(filtered),
        "venue_breakdown": venue_counts,
        "network_warnings": network_errors[:5],
        "papers": filtered,
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(filtered)} verified venue papers to {args.output}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    print(
        f"[Summary] Mode={args.source} | Window={from_date}..{today.isoformat()} | "
        f"Total={len(filtered)} | Breakdown={venue_counts}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
