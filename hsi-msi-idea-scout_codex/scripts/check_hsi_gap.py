#!/usr/bin/env python3
"""Reverse gap-check a candidate mechanism against HSI-MSI image fusion literature.

Dual-channel verification:
  1. OpenAlex (published remote sensing & vision journals/conferences, e.g., TGRS, TIP, CVPR).
  2. arXiv Atom API (latest preprints from the past 6-12 months to catch brand-new
     HSI-MSI work not yet indexed by OpenAlex and prevent false 'Tier 1' claims).

Supports --synonyms so renamed variants of the same mechanism are checked together.
Uses only the Python standard library.
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
import xml.etree.ElementTree as ET
from typing import Any

OPENALEX_WORKS_URL = "https://api.openalex.org/works"
ARXIV_API_URL = "http://export.arxiv.org/api/query"

HSI_ANCHOR_QUERIES = [
    "hyperspectral multispectral image fusion",
    "HSI MSI fusion",
    "hyperspectral pansharpening",
    "hyperspectral image super-resolution",
    "RGB-guided hyperspectral",
    "spectral-spatial fusion hyperspectral",
]

HSI_RELEVANCE_TERMS = [
    "hyperspectral",
    "hsi-msi",
    "hsi and msi",
    "multispectral",
    "pansharpening",
    "hyper-sharpening",
    "spectral super-resolution",
    "spectral-spatial fusion",
]

STOPWORDS = {
    "the", "and", "for", "with", "from", "image", "model", "based",
    "using", "of", "in", "to", "via", "new", "novel", "method",
}


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


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


def http_get_text(url: str, accept: str = "application/json", timeout: int = 25) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hsi-msi-idea-scout_codex/1.1 (Gap Check Script)",
            "Accept": accept,
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def is_hsi_relevant(title: str, abstract: str) -> bool:
    text = f"{title} {abstract}".lower()
    return any(t in text for t in HSI_RELEVANCE_TERMS)


def best_concept_match(phrases: list[str], title: str, abstract: str) -> tuple[int, int, str]:
    """Return (best_hit_tokens, total_tokens_for_that_phrase, matched_phrase)."""
    text = f"{title} {abstract}".lower()
    best = (0, 1, "")
    for phrase in phrases:
        tokens = [t.lower() for t in re.split(r"[\s\-/]+", phrase) if len(t) >= 3 and t.lower() not in STOPWORDS]
        if not tokens:
            continue
        hits = sum(1 for t in tokens if t in text)
        if hits / len(tokens) > best[0] / best[1] or (hits / len(tokens) == best[0] / best[1] and hits > best[0]):
            best = (hits, len(tokens), phrase)
    return best


def query_arxiv(concept_phrases: list[str], from_year: int) -> list[dict[str, Any]]:
    """Check recent arXiv preprints to catch brand-new HSI-MSI work before journal indexing."""
    results: list[dict[str, Any]] = []
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    for phrase in concept_phrases[:3]:
        clean = phrase.replace('"', "").strip()
        q = f'all:"{clean}" AND (all:hyperspectral OR all:pansharpening OR all:"HSI-MSI")'
        params = {
            "search_query": q,
            "start": 0,
            "max_results": 15,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
        xml_text = http_get_text(url, accept="application/atom+xml")
        root = ET.fromstring(xml_text)

        for entry in root.findall("atom:entry", ns):
            title = " ".join((entry.findtext("atom:title", "", ns) or "").split())
            abstract = " ".join((entry.findtext("atom:summary", "", ns) or "").split())
            published = entry.findtext("atom:published", "", ns) or ""
            pub_year = int(published[:4]) if len(published) >= 4 and published[:4].isdigit() else 0
            if pub_year < from_year:
                continue
            if not is_hsi_relevant(title, abstract):
                continue

            hits, total, matched_p = best_concept_match(concept_phrases, title, abstract)
            if hits == 0:
                continue
            entry_id = entry.findtext("atom:id", "", ns) or ""
            results.append(
                {
                    "source_channel": "arxiv_preprint",
                    "title": title,
                    "publication_year": pub_year,
                    "publication_date": published[:10],
                    "venue": "arXiv (preprint)",
                    "cited_by_count": 0,
                    "doi": "",
                    "url": entry_id,
                    "matched_phrase": matched_p,
                    "concept_token_hits": hits,
                    "concept_token_total": total,
                    "abstract_snippet": abstract[:400],
                }
            )
        time.sleep(0.35)
    return results


def suggest_gap_tier(strong_hits: int, moderate_hits: int, arxiv_strong: int) -> tuple[str, str]:
    if strong_hits == 0 and moderate_hits <= 1:
        return (
            "Tier 1 (Potential White Space)",
            "No directly comparable published or arXiv HSI-MSI papers matched all core concept/synonym terms. Still inspect top hits manually.",
        )
    if strong_hits <= 3:
        extra = f" (including {arxiv_strong} recent arXiv preprint(s))" if arxiv_strong else ""
        return (
            "Tier 2 (Shallow Adoption / Specific Blind Spot)",
            f"A small number of related HSI-MSI works exist{extra}. Verify whether they missed the source paper's key overlooked flaw or mechanism.",
        )
    return (
        "Tier 3 (Likely Saturated)",
        "Multiple HSI-MSI papers already cover this concept or its synonyms. Drop unless isolating a genuinely unaddressed sub-problem.",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dual-channel (OpenAlex + arXiv) reverse gap-check in HSI-MSI image fusion literature."
    )
    parser.add_argument(
        "--concept",
        required=True,
        help="Primary mechanism or module phrase, e.g. 'rectified flow inverse problem'",
    )
    parser.add_argument(
        "--synonyms",
        default="",
        help="Comma-separated synonym/parent phrases to prevent false Tier 1 claims, e.g. 'flow matching,ODE transport'",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=3,
        help="Lookback window in years for HSI-MSI gap check (default: 3).",
    )
    parser.add_argument(
        "--skip-arxiv",
        action="store_true",
        help="Skip arXiv preprint channel and query OpenAlex only.",
    )
    parser.add_argument(
        "--extra-terms",
        default="",
        help="Optional comma-separated extra HSI anchor queries.",
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
    today = dt.date.today()
    from_date_obj = today - dt.timedelta(days=args.years * 365)
    from_date = from_date_obj.isoformat()
    from_year = from_date_obj.year

    concept_phrases = [args.concept.strip()]
    if args.synonyms.strip():
        concept_phrases.extend([s.strip() for s in args.synonyms.split(",") if s.strip()])

    anchors = list(HSI_ANCHOR_QUERIES)
    if args.extra_terms.strip():
        anchors.extend([t.strip() for t in args.extra_terms.split(",") if t.strip()])

    dedup: dict[str, dict[str, Any]] = {}
    queries_run: list[str] = []
    warnings: list[str] = []

    # Channel 1: OpenAlex
    for phrase in concept_phrases:
        for anchor in anchors[:4]:
            q = f"{phrase} {anchor}"
            queries_run.append(f"openalex: {q}")
            params: dict[str, Any] = {
                "search": q,
                "filter": f"from_publication_date:{from_date}",
                "sort": "relevance_score:desc",
                "per-page": 20,
                "page": 1,
            }
            if args.mailto:
                params["mailto"] = args.mailto
            url = f"{OPENALEX_WORKS_URL}?{urllib.parse.urlencode(params)}"
            try:
                data = json.loads(http_get_text(url))
            except urllib.error.URLError as exc:
                warnings.append(f"OpenAlex error for '{q}': {exc}")
                continue

            for w in data.get("results") or []:
                title = (w.get("display_name") or "").strip()
                abstract = reconstruct_abstract(w.get("abstract_inverted_index"))
                if not title or not is_hsi_relevant(title, abstract):
                    continue
                hits, total, matched_p = best_concept_match(concept_phrases, title, abstract)
                if hits == 0:
                    continue

                primary_loc = w.get("primary_location") or {}
                src = (primary_loc.get("source") or {}) if isinstance(primary_loc, dict) else {}
                venue_name = src.get("display_name") or "Unknown"
                landing = primary_loc.get("landing_page_url") if isinstance(primary_loc, dict) else ""

                key = normalize_title(title)
                rec = {
                    "source_channel": "openalex",
                    "openalex_id": w.get("id", ""),
                    "title": title,
                    "publication_year": w.get("publication_year"),
                    "publication_date": w.get("publication_date", ""),
                    "venue": venue_name,
                    "cited_by_count": int(w.get("cited_by_count") or 0),
                    "doi": w.get("doi") or "",
                    "url": landing or w.get("doi") or w.get("id", ""),
                    "matched_phrase": matched_p,
                    "concept_token_hits": hits,
                    "concept_token_total": total,
                    "abstract_snippet": abstract[:400],
                }
                if key not in dedup or (rec["concept_token_hits"] / rec["concept_token_total"]) > (
                    dedup[key]["concept_token_hits"] / dedup[key]["concept_token_total"]
                ):
                    dedup[key] = rec
            time.sleep(0.18)

    # Channel 2: arXiv latest preprints
    if not args.skip_arxiv:
        try:
            queries_run.append(f"arxiv: {concept_phrases[:3]} + HSI/pansharpening")
            arxiv_hits = query_arxiv(concept_phrases, from_year=from_year)
            for rec in arxiv_hits:
                key = normalize_title(rec["title"])
                if key not in dedup:
                    dedup[key] = rec
        except Exception as exc:
            warnings.append(f"arXiv channel warning: {exc}")

    if not dedup and len(warnings) >= len(concept_phrases) * 2:
        print(
            "Network error across gap-check channels. Do not claim Tier 1 white space without verified results.\n"
            + "\n".join(warnings[:5]),
            file=sys.stderr,
        )
        return 1

    hits = sorted(
        dedup.values(),
        key=lambda x: (
            x["concept_token_hits"] / max(1, x["concept_token_total"]),
            x["concept_token_hits"],
            x.get("publication_year") or 0,
            x.get("cited_by_count") or 0,
        ),
        reverse=True,
    )

    strong_hits = sum(1 for h in hits if h["concept_token_hits"] >= h["concept_token_total"])
    arxiv_strong = sum(
        1
        for h in hits
        if h["concept_token_hits"] >= h["concept_token_total"] and h["source_channel"] == "arxiv_preprint"
    )
    moderate_hits = sum(1 for h in hits if 0 < h["concept_token_hits"] < h["concept_token_total"])
    tier, rationale = suggest_gap_tier(strong_hits, moderate_hits, arxiv_strong)

    payload = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "concept": args.concept,
        "synonyms": concept_phrases[1:],
        "lookback_from": from_date,
        "queries_run": queries_run,
        "strong_match_count": strong_hits,
        "arxiv_strong_match_count": arxiv_strong,
        "moderate_match_count": moderate_hits,
        "suggested_gap_tier": tier,
        "rationale": rationale,
        "warnings": warnings[:5],
        "closest_hsi_papers": hits[:15],
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"Saved dual-channel HSI-MSI gap check ({tier}) to {args.output}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    print(
        f"[Gap Check] Concept='{args.concept}' | Strong={strong_hits} (arXiv={arxiv_strong}), "
        f"Moderate={moderate_hits} -> {tier}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
