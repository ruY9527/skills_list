#!/usr/bin/env python3
"""Dual-engine 9-venue cross-domain paper radar scanner (DBLP + OpenAlex).

Features:
  - Built-in 7 expanded high-resonance domain presets (D1-D7) inspired by M0rtzz/paper-notes.
  - Strict 9-venue whitelist via exact DBLP streams (IJCV, TIP, CVPR, NeurIPS, AAAI,
    ICLR, ICCV, ECCV, TPAMI) + OpenAlex abstract/citation enrichment.
  - Automatic deduplication against local literature_ledger/ledger.csv (--exclude-ledger).
  - Optional merge with external JSON exports from OpenReview / CVF / papernotes.org (--extra-json).

Uses only the Python standard library (zero pip dependencies).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DBLP_API_URL = "https://dblp.org/search/publ/api"
OPENALEX_WORKS_URL = "https://api.openalex.org/works"

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

DOMAIN_PRESETS: dict[str, dict[str, Any]] = {
    "D1": {
        "name": "Natural Image Low-Level Vision & Inverse Problems",
        "track": "Track A",
        "queries": [
            "all-in-one image restoration",
            "blind super-resolution",
            "infrared visible image fusion",
            "inverse problem image restoration",
        ],
    },
    "D2": {
        "name": "Medical Image Fusion, Registration & Physics Reconstruction",
        "track": "Track A & B",
        "queries": [
            "medical image fusion",
            "deformable registration multimodal fusion",
            "physics-informed MRI reconstruction",
            "sparse-view CT reconstruction",
        ],
    },
    "D3": {
        "name": "Generative Priors & Few-Step Sampling (Diffusion / Flow)",
        "track": "Track A",
        "queries": [
            "flow matching inverse problem",
            "rectified flow image restoration",
            "diffusion posterior sampling inverse",
            "zero-shot diffusion restoration",
        ],
    },
    "D4": {
        "name": "Vision Agents, Tool-Use & Multi-Step Self-Reflection",
        "track": "Track B",
        "queries": [
            "agentic image restoration",
            "vision agent tool use",
            "self-correcting vision agent",
            "test-time scaling visual reasoning",
        ],
    },
    "D5": {
        "name": "Efficient Long-Range Representation, Continuous Fields & Frequency",
        "track": "Track A",
        "queries": [
            "vision mamba image restoration",
            "implicit neural representation super-resolution",
            "arbitrary-scale super-resolution",
            "frequency decomposition image restoration",
        ],
    },
    "D6": {
        "name": "Test-Time Adaptation, Zero-Shot Generalization & Uncertainty",
        "track": "Track A & B",
        "queries": [
            "test-time adaptation image restoration",
            "test-time training vision",
            "zero-shot blind image restoration",
            "uncertainty quantification image reconstruction",
        ],
    },
    "D7": {
        "name": "Scientific Computational Imaging & Multi-Sensor Physical Fusion",
        "track": "Track A",
        "queries": [
            "computational imaging inverse problem",
            "snapshot compressive imaging reconstruction",
            "physics-informed neural network imaging",
            "event camera image fusion",
        ],
    },
}

EXCLUDE_VENUE_SUBSTRINGS = ["workshop", "findings of", "arxiv", "biorxiv", "medrxiv", "ssrn", "companion"]
SURVEY_TITLE_PATTERNS = [r"\bsurvey\b", r"\breview\b", r"\boverview\b", r"\bbenchmark(?:ing)?\b", r"\bdataset\b", r"\btaxonomy\b"]
PIONEER_SIGNALS = [
    r"\bfirst\b", r"\bpioneer(?:ing)?\b", r"\boverlook(?:ed|ing)?\b", r"\brethink(?:ing)?\b",
    r"\brevisit(?:ing)?\b", r"\bneglect(?:ed|ing)?\b", r"\bnovel paradigm\b", r"\bzero-shot\b",
    r"\bagentic\b", r"\bself-correct", r"\btest-time\b", r"\bflow matching\b", r"\brectified flow\b",
]


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def is_survey_like(title: str) -> bool:
    low = title.lower()
    return any(re.search(pat, low) for pat in SURVEY_TITLE_PATTERNS)


def http_get_json(url: str, timeout: int = 25) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "cross-domain-paper-radar-codex/1.0 (Academic Radar Skill)",
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


def load_ledger_titles(csv_path: str | None) -> set[str]:
    if not csv_path or not os.path.exists(csv_path):
        return set()
    titles: set[str] = set()
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            t = row.get("title", "").strip()
            if t:
                titles.add(normalize_title(t))
    return titles


def compute_triage_hint(title: str, abstract: str, cited_by: int, year: int | None) -> tuple[float, list[str]]:
    text = f"{title} {abstract}".lower()
    matched: list[str] = []
    for pat in PIONEER_SIGNALS:
        if re.search(pat, text):
            matched.append(re.sub(r"\\b|\(\?:[^)]*\)|\?", "", pat))
    kw_score = min(len(matched), 3) * 1.2
    years_old = max(0.5, (dt.date.today().year - (year or dt.date.today().year)) + 0.5)
    cite_score = min(cited_by / years_old, 60.0) * 0.08
    return round(kw_score + cite_score, 2), matched


def infer_direct_pdf_url(url: str) -> str:
    """Derive a legal public PDF URL for standard open-access repositories."""
    if not url:
        return ""
    u = url.strip()
    if u.lower().endswith(".pdf"):
        return u
    # OpenReview forum -> direct PDF
    if "openreview.net/forum?id=" in u:
        return u.replace("openreview.net/forum?id=", "openreview.net/pdf?id=")
    # arXiv abs -> direct PDF
    m_arxiv = re.search(r"arxiv\.org/abs/([^\s?#]+)", u)
    if m_arxiv:
        return f"https://arxiv.org/pdf/{m_arxiv.group(1)}.pdf"
    # CVF Open Access html -> PDF
    if "openaccess.thecvf.com/content/" in u and "/html/" in u and u.endswith("_paper.html"):
        return u.replace("/html/", "/papers/").replace("_paper.html", "_paper.pdf")
    return ""


def fetch_dblp_stream(
    query: str,
    domain_tag: str,
    venue: str,
    min_year: int,
    max_hits: int,
    include_surveys: bool,
) -> list[dict[str, Any]]:
    stream = DBLP_STREAMS[venue]
    params = {"q": f"{query} stream:{stream}:", "h": max_hits, "format": "json"}
    url = f"{DBLP_API_URL}?{urllib.parse.urlencode(params)}"
    data = http_get_json(url)
    hits = (((data.get("result") or {}).get("hits") or {}).get("hit")) or []

    results: list[dict[str, Any]] = []
    for h in hits:
        info = h.get("info") or {}
        title = str(info.get("title") or "").strip().rstrip(".")
        if not title or (not include_surveys and is_survey_like(title)):
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
                "domain_tag": domain_tag,
                "matched_query": query,
                "title": title,
                "authors": [a for a in authors if a],
                "venue": venue,
                "raw_venue": raw_venue,
                "publication_year": year,
                "publication_date": str(year),
                "cited_by_count": 0,
                "doi": f"https://doi.org/{doi}" if doi and not doi.startswith("http") else doi,
                "url": paper_url,
                "pdf_url": infer_direct_pdf_url(paper_url),
                "is_oa": bool(infer_direct_pdf_url(paper_url)),
                "oa_status": "open" if infer_direct_pdf_url(paper_url) else "unknown",
                "abstract": "",
                "abstract_verified": False,
            }
        )
    return results


def extract_openalex_pdf(work: dict[str, Any]) -> tuple[str, bool, str]:
    oa = work.get("open_access") or {}
    is_oa = bool(oa.get("is_oa"))
    oa_status = str(oa.get("oa_status") or ("open" if is_oa else "closed"))

    candidates: list[str] = []
    best_oa = work.get("best_oa_location") or {}
    if isinstance(best_oa, dict):
        if best_oa.get("pdf_url"):
            candidates.append(str(best_oa["pdf_url"]))
        if best_oa.get("landing_page_url"):
            inferred = infer_direct_pdf_url(str(best_oa["landing_page_url"]))
            if inferred:
                candidates.append(inferred)

    primary = work.get("primary_location") or {}
    if isinstance(primary, dict) and primary.get("pdf_url"):
        candidates.append(str(primary["pdf_url"]))

    if oa.get("oa_url"):
        oa_u = str(oa["oa_url"])
        inferred = infer_direct_pdf_url(oa_u)
        candidates.append(inferred or oa_u)

    for loc in work.get("locations") or []:
        if isinstance(loc, dict):
            if loc.get("pdf_url"):
                candidates.append(str(loc["pdf_url"]))
            elif loc.get("landing_page_url"):
                inferred = infer_direct_pdf_url(str(loc["landing_page_url"]))
                if inferred:
                    candidates.append(inferred)

    for c in candidates:
        if c and c.startswith("http"):
            return c, True, oa_status
    return "", is_oa, oa_status


def enrich_with_openalex(paper: dict[str, Any], mailto: str | None) -> None:
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
            pdf_url, is_oa, oa_status = extract_openalex_pdf(w)
            if pdf_url and not paper.get("pdf_url"):
                paper["pdf_url"] = pdf_url
            paper["is_oa"] = bool(paper.get("pdf_url")) or is_oa
            paper["oa_status"] = oa_status
            return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan rolling 24-month papers from the 9 target venues across 7 expanded domains (D1-D7)."
    )
    parser.add_argument("--list-domains", action="store_true", help="Print the 7 built-in domain presets (D1-D7) and exit.")
    parser.add_argument("--domains", default="", help="Comma-separated domain IDs to scan, e.g. 'D2,D4' (recommended: 1-2 per run).")
    parser.add_argument("--queries", default="", help="Optional comma-separated custom queries in addition to or instead of --domains.")
    parser.add_argument("--venues", default="IJCV,TIP,CVPR,NeurIPS,AAAI,ICLR,ICCV,ECCV,TPAMI", help="Comma-separated subset of the 9 allowed venues.")
    parser.add_argument("--months", type=int, default=24, help="Rolling lookback window in months (default: 24).")
    parser.add_argument("--max-per-venue", type=int, default=8, help="Max papers retained per venue (default: 8).")
    parser.add_argument("--enrich-top", type=int, default=35, help="Enrich up to N papers with OpenAlex abstracts/citations (default: 35).")
    parser.add_argument("--exclude-ledger", default=None, help="Optional path to literature_ledger/ledger.csv to skip already-read papers.")
    parser.add_argument("--extra-json", default=None, help="Optional external JSON list of papers (e.g. from OpenReview/CVF/papernotes.org) to merge.")
    parser.add_argument("--include-surveys", action="store_true", help="Include survey/review/benchmark papers.")
    parser.add_argument("--mailto", default=None, help="Optional email for OpenAlex polite pool.")
    parser.add_argument("--output", default=None, help="Optional output JSON file path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list_domains:
        print("Built-in 7 High-Resonance Expanded Domains (D1-D7):")
        for dom_id, info in DOMAIN_PRESETS.items():
            print(f"  {dom_id} [{info['track']}] {info['name']}")
            print(f"     Queries: {', '.join(info['queries'])}")
        return 0

    domain_ids = [d.strip().upper() for d in args.domains.split(",") if d.strip()]
    invalid_doms = set(domain_ids) - set(DOMAIN_PRESETS.keys())
    if invalid_doms:
        print(f"Error: Unknown domains {sorted(invalid_doms)}. Valid: {sorted(DOMAIN_PRESETS.keys())}", file=sys.stderr)
        return 2

    query_pairs: list[tuple[str, str]] = []
    for d in domain_ids:
        for q in DOMAIN_PRESETS[d]["queries"]:
            query_pairs.append((d, q))
    for q in [x.strip() for x in args.queries.split(",") if x.strip()]:
        query_pairs.append(("CUSTOM", q))

    if not query_pairs and not args.extra_json:
        print("Error: Provide --domains (e.g. 'D2,D4'), --queries, or --extra-json. Use --list-domains to inspect presets.", file=sys.stderr)
        return 2

    requested_venues = [v.strip() for v in args.venues.split(",") if v.strip()]
    invalid_venues = set(requested_venues) - set(DBLP_STREAMS.keys())
    if invalid_venues:
        print(f"Error: Unsupported venues {sorted(invalid_venues)}. Allowed: {sorted(DBLP_STREAMS.keys())}", file=sys.stderr)
        return 2

    today = dt.date.today()
    from_date_obj = today - dt.timedelta(days=args.months * 30)
    min_year = from_date_obj.year
    ledger_titles = load_ledger_titles(args.exclude_ledger)
    skipped_ledger = 0

    dedup: dict[str, dict[str, Any]] = {}
    network_errors: list[str] = []

    for dom_tag, q in query_pairs:
        for venue in requested_venues:
            try:
                batch = fetch_dblp_stream(
                    query=q,
                    domain_tag=dom_tag,
                    venue=venue,
                    min_year=min_year,
                    max_hits=max(12, args.max_per_venue * 2),
                    include_surveys=args.include_surveys,
                )
                for item in batch:
                    key = normalize_title(item["title"])
                    if key in ledger_titles:
                        skipped_ledger += 1
                        continue
                    if key not in dedup:
                        dedup[key] = item
            except urllib.error.URLError as exc:
                network_errors.append(f"DBLP({venue}, '{q}'): {exc}")
            time.sleep(0.18)

    # Merge optional external JSON (OpenReview / CVF / papernotes.org export)
    if args.extra_json and os.path.exists(args.extra_json):
        with open(args.extra_json, "r", encoding="utf-8") as f:
            raw_extra = json.load(f)
        extra_list = raw_extra.get("papers", raw_extra) if isinstance(raw_extra, dict) else raw_extra
        if isinstance(extra_list, list):
            for rec in extra_list:
                if not isinstance(rec, dict) or not rec.get("title"):
                    continue
                key = normalize_title(str(rec["title"]))
                if key in ledger_titles:
                    skipped_ledger += 1
                    continue
                if key not in dedup:
                    rec.setdefault("source_engine", "extra_json")
                    rec.setdefault("domain_tag", domain_ids[0] if domain_ids else "EXTRA")
                    rec.setdefault("abstract", "")
                    rec["abstract_verified"] = bool(rec.get("abstract"))
                    dedup[key] = rec

    if not dedup and network_errors:
        print(
            "Network unreachable while scanning DBLP. Do not invent papers; allow network access or supply --extra-json.\n"
            + "\n".join(network_errors[:5]),
            file=sys.stderr,
        )
        return 1

    # Enrich top recent papers with OpenAlex abstracts & citation counts
    needs_enrich = [p for p in dedup.values() if not p.get("abstract")]
    needs_enrich.sort(key=lambda x: int(x.get("publication_year") or 0), reverse=True)
    for paper in needs_enrich[: args.enrich_top]:
        enrich_with_openalex(paper, args.mailto)
        time.sleep(0.15)

    for paper in dedup.values():
        score, signals = compute_triage_hint(
            str(paper.get("title", "")),
            str(paper.get("abstract", "")),
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
            int(x.get("publication_year") or 0),
            int(x.get("cited_by_count") or 0),
        ),
        reverse=True,
    )

    venue_counts: dict[str, int] = {}
    filtered: list[dict[str, Any]] = []
    for item in sorted_all:
        v = str(item.get("venue", "OTHER"))
        if venue_counts.get(v, 0) < args.max_per_venue:
            venue_counts[v] = venue_counts.get(v, 0) + 1
            filtered.append(item)

    payload = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "rolling_window": {"from_date": from_date_obj.isoformat(), "to_date": today.isoformat(), "months": args.months},
        "scanned_domains": domain_ids,
        "allowed_venues": sorted(requested_venues),
        "skipped_already_in_ledger": skipped_ledger,
        "total_matched": len(filtered),
        "verified_abstract_count": sum(1 for p in filtered if p.get("abstract_verified")),
        "venue_breakdown": venue_counts,
        "network_warnings": network_errors[:5],
        "papers": filtered,
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(filtered)} radar candidates ({payload['verified_abstract_count']} with abstracts) to {args.output}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    print(
        f"[Radar Summary] Domains={domain_ids or ['CUSTOM']} | Matched={len(filtered)} | "
        f"WithAbstract={payload['verified_abstract_count']} | SkippedLedger={skipped_ledger}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
