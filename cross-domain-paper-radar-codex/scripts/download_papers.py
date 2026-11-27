#!/usr/bin/env python3
"""Download legal Open-Access PDFs from radar_scan.py output or a direct URL.

Only downloads publicly accessible open-access PDFs (e.g., CVF Open Access,
OpenReview, arXiv, or OpenAlex verified OA PDF URLs). Validates the '%PDF'
magic header so HTML login/paywall pages are never saved as corrupted PDFs.

Uses only the Python standard library (zero pip dependencies).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Any


def safe_filename(year: Any, venue: str, title: str) -> str:
    clean_title = re.sub(r"[^a-zA-Z0-9]+", "_", title).strip("_")[:65]
    clean_venue = re.sub(r"[^a-zA-Z0-9]+", "", str(venue or "Venue"))
    yr = str(year or "YYYY")
    return f"{yr}_{clean_venue}_{clean_title}.pdf"


def download_single_pdf(pdf_url: str, dest_path: str, timeout: int = 35) -> tuple[bool, str]:
    req = urllib.request.Request(
        pdf_url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; cross-domain-paper-radar-codex/1.1; Academic OA Downloader)",
            "Accept": "application/pdf,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}: {exc.reason}"
    except urllib.error.URLError as exc:
        return False, f"Network error: {exc.reason}"
    except Exception as exc:
        return False, str(exc)

    if not data.startswith(b"%PDF"):
        return False, "Response is not a valid PDF (likely an HTML landing or paywall page)."

    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)
    size_kb = round(len(data) / 1024.0, 1)
    return True, f"Saved ({size_kb} KB)"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download legal Open-Access PDFs from radar_candidates.json or a single PDF URL."
    )
    parser.add_argument("--input", default=None, help="Path to radar_candidates.json produced by radar_scan.py.")
    parser.add_argument("--indices", default="", help="1-based comma-separated paper indices to download, e.g. '1,2,3'.")
    parser.add_argument("--top", type=int, default=5, help="Download top N papers with pdf_url when --indices is not set (default: 5).")
    parser.add_argument("--url", default=None, help="Direct single OA PDF URL (alternative to --input).")
    parser.add_argument("--title", default="paper", help="Title for filename when using --url.")
    parser.add_argument("--output-dir", default="./downloaded_papers", help="Target directory for downloaded PDFs.")
    parser.add_argument("--manifest", default=None, help="Optional JSON path to save download status manifest.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    targets: list[dict[str, Any]] = []
    if args.url:
        targets.append({"title": args.title, "venue": "OA", "publication_year": "", "pdf_url": args.url, "url": args.url})
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            raw = json.load(f)
        papers = raw.get("papers", raw) if isinstance(raw, dict) else raw
        if args.indices.strip():
            wanted = [int(x.strip()) for x in args.indices.split(",") if x.strip().isdigit()]
            for idx in wanted:
                if 1 <= idx <= len(papers):
                    targets.append(papers[idx - 1])
        else:
            targets = papers[: args.top]
    else:
        print("Error: Provide either --input radar_candidates.json or --url <pdf_url>.", file=sys.stderr)
        return 2

    results: list[dict[str, Any]] = []
    ok_count = 0
    for item in targets:
        title = str(item.get("title") or "untitled")
        venue = str(item.get("venue") or "Venue")
        year = item.get("publication_year") or ""
        pdf_url = str(item.get("pdf_url") or "").strip()
        landing = str(item.get("url") or item.get("doi") or "")

        if not pdf_url:
            rec = {
                "title": title,
                "status": "no_oa_pdf",
                "message": "No public OA PDF URL found; use institutional access via landing URL.",
                "landing_url": landing,
                "local_path": "",
            }
            results.append(rec)
            print(f"[SKIP - No OA PDF] {title} -> {landing}")
            continue

        fname = safe_filename(year, venue, title)
        dest = os.path.abspath(os.path.join(args.output_dir, fname))
        ok, msg = download_single_pdf(pdf_url, dest)
        if ok:
            ok_count += 1
            print(f"[OK] {dest} ({msg})")
            results.append({"title": title, "status": "downloaded", "message": msg, "pdf_url": pdf_url, "local_path": dest})
        else:
            print(f"[FAIL] {title} ({msg}) -> Landing: {landing}")
            results.append({"title": title, "status": "failed", "message": msg, "pdf_url": pdf_url, "landing_url": landing, "local_path": ""})
        time.sleep(0.3)

    if args.manifest:
        with open(args.manifest, "w", encoding="utf-8") as f:
            json.dump({"downloaded_count": ok_count, "total_attempted": len(targets), "items": results}, f, ensure_ascii=False, indent=2)

    print(f"[Done] Downloaded {ok_count}/{len(targets)} OA PDF(s) into {os.path.abspath(args.output_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
