#!/usr/bin/env python3
"""Export a radar candidate JSON file into a clean Markdown triage table.

Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def esc(val: Any) -> str:
    return str(val or "").replace("|", "\\|").replace("\n", " ").strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export radar_scan.py JSON output to a compact Markdown table.")
    parser.add_argument("--input", required=True, help="Path to radar_candidates.json")
    parser.add_argument("--top", type=int, default=15, help="Number of top candidates to export (default: 15).")
    parser.add_argument("--only-with-abstract", action="store_true", help="Exclude entries missing verified abstracts.")
    parser.add_argument("--output", required=True, help="Output Markdown file path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    papers = data.get("papers", []) if isinstance(data, dict) else data
    if args.only_with_abstract:
        papers = [p for p in papers if p.get("abstract_verified")]

    selected = papers[: args.top]
    window = data.get("rolling_window", {}) if isinstance(data, dict) else {}
    domains = data.get("scanned_domains", []) if isinstance(data, dict) else []

    lines = [
        "# Radar Candidate Triage Table",
        "",
        f"- **Generated At**: {data.get('generated_at', '') if isinstance(data, dict) else ''}",
        f"- **Window**: {window.get('from_date', '')} to {window.get('to_date', '')}",
        f"- **Domains**: {', '.join(domains) if domains else 'Custom'}",
        f"- **Exported**: {len(selected)} / {len(papers)} candidates",
        "",
        "| # | Venue & Year | Domain | Hint Score | Abstract? | Title | Link |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for idx, p in enumerate(selected, 1):
        url = esc(p.get("url", ""))
        link_cell = f"[Link]({url})" if url.startswith("http") else "N/A"
        has_abs = "Yes" if p.get("abstract_verified") else "Missing"
        lines.append(
            f"| {idx} | {esc(p.get('venue'))} {esc(p.get('publication_year'))} "
            f"| {esc(p.get('domain_tag'))} | {esc(p.get('triage_hint_score'))} "
            f"| {has_abs} | **{esc(p.get('title'))}** | {link_cell} |"
        )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Exported {len(selected)} candidates to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
