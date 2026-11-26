#!/usr/bin/env python3
"""Maintain a persistent CSV + Markdown literature ledger for HSI-MSI & Agent papers.

Supports:
  - Appending/updating papers with automatic title-based deduplication.
  - Regenerating a clean Markdown summary table (`ledger.md`).
  - Searching existing ledger entries (`--search`).

Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import sys

FIELDNAMES = [
    "added_date",
    "year",
    "venue",
    "category",
    "title",
    "authors",
    "degradation",
    "paradigm",
    "agent_loop",
    "datasets",
    "metrics",
    "limitation",
    "role",
    "evidence_depth",
    "code_url",
]


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def load_rows(csv_path: str) -> list[dict[str, str]]:
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def save_csv(csv_path: str, rows: list[dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDNAMES})


def escape_md(val: str) -> str:
    return (val or "").replace("|", "\\|").replace("\n", " ").strip()


def save_markdown(md_path: str, rows: list[dict[str, str]]) -> None:
    sorted_rows = sorted(rows, key=lambda r: (r.get("year", ""), r.get("added_date", "")), reverse=True)
    lines = [
        "# HSI-MSI & Vision Agent Literature Ledger",
        "",
        f"- **Total Papers Logged**: {len(sorted_rows)}",
        f"- **Last Updated**: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Year | Venue | Cat. | Title | Degradation | Paradigm / Agent Loop | Datasets | Core Limitation | Role | Depth | Code |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in sorted_rows:
        method = escape_md(r.get("paradigm", ""))
        agent = escape_md(r.get("agent_loop", ""))
        if agent and agent.upper() != "N/A":
            method = f"{method} / Agent: {agent}" if method else f"Agent: {agent}"
        code = escape_md(r.get("code_url", "N/A"))
        code_cell = f"[Link]({code})" if code.startswith("http") else code
        lines.append(
            f"| {escape_md(r.get('year', ''))} "
            f"| {escape_md(r.get('venue', ''))} "
            f"| {escape_md(r.get('category', ''))} "
            f"| **{escape_md(r.get('title', ''))}** ({escape_md(r.get('authors', ''))}) "
            f"| {escape_md(r.get('degradation', ''))} "
            f"| {method} "
            f"| {escape_md(r.get('datasets', ''))} "
            f"| {escape_md(r.get('limitation', ''))} "
            f"| {escape_md(r.get('role', ''))} "
            f"| {escape_md(r.get('evidence_depth', ''))} "
            f"| {code_cell} |"
        )
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append/update or search the local HSI-MSI literature ledger.")
    parser.add_argument("--ledger-dir", default="./literature_ledger", help="Directory for ledger.csv and ledger.md")
    parser.add_argument("--search", default=None, help="Search existing ledger entries by keyword (read-only mode).")
    parser.add_argument("--title", default="")
    parser.add_argument("--authors", default="")
    parser.add_argument("--year", default="")
    parser.add_argument("--venue", default="")
    parser.add_argument("--category", default="HSI-MSI", choices=["HSI-MSI", "Vision-Agent", "Agent+HSI-MSI"])
    parser.add_argument("--degradation", default="N/A")
    parser.add_argument("--paradigm", default="N/A")
    parser.add_argument("--agent-loop", default="N/A")
    parser.add_argument("--datasets", default="N/A")
    parser.add_argument("--metrics", default="N/A")
    parser.add_argument("--limitation", default="")
    parser.add_argument("--role", default="Related Work Only")
    parser.add_argument("--evidence-depth", default="Full-Text Verified")
    parser.add_argument("--code-url", default="N/A")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_path = os.path.join(args.ledger_dir, "ledger.csv")
    md_path = os.path.join(args.ledger_dir, "ledger.md")
    rows = load_rows(csv_path)

    if args.search is not None:
        q = args.search.lower().strip()
        matched = [r for r in rows if q in " ".join(r.values()).lower()]
        print(f"Found {len(matched)} matching paper(s) in {csv_path}:")
        for r in matched:
            print(f"- [{r.get('year')} {r.get('venue')} | {r.get('category')}] {r.get('title')} — Role: {r.get('role')} | Limit: {r.get('limitation')}")
        return 0

    if not args.title.strip():
        print("Error: --title is required when adding/updating a paper.", file=sys.stderr)
        return 2

    new_row = {
        "added_date": dt.date.today().isoformat(),
        "year": str(args.year).strip(),
        "venue": args.venue.strip(),
        "category": args.category,
        "title": args.title.strip(),
        "authors": args.authors.strip(),
        "degradation": args.degradation.strip(),
        "paradigm": args.paradigm.strip(),
        "agent_loop": args.agent_loop.strip(),
        "datasets": args.datasets.strip(),
        "metrics": args.metrics.strip(),
        "limitation": args.limitation.strip(),
        "role": args.role.strip(),
        "evidence_depth": args.evidence_depth.strip(),
        "code_url": args.code_url.strip(),
    }

    norm = normalize_title(new_row["title"])
    updated = False
    for idx, existing in enumerate(rows):
        if normalize_title(existing.get("title", "")) == norm:
            rows[idx] = new_row
            updated = True
            break
    if not updated:
        rows.append(new_row)

    save_csv(csv_path, rows)
    save_markdown(md_path, rows)
    action = "Updated" if updated else "Appended"
    print(f"{action} paper in {csv_path} and regenerated {md_path} (total: {len(rows)} papers).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
