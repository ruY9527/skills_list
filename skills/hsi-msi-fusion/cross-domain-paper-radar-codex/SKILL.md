---
name: cross-domain-paper-radar-codex
description: >-
  【9大顶会跨域论文雷达】Use this skill when the user wants to proactively scan and discover
  high-value pioneering papers from the last 2 years of 9 top venues (IJCV, TIP, CVPR,
  NeurIPS, AAAI, ICLR, ICCV, ECCV, TPAMI) across 7 high-resonance expanded domains (natural
  image restoration/fusion, medical imaging, generative priors, vision agents, efficient
  representation/Mamba/INR, test-time adaptation/uncertainty, and computational/scientific
  imaging) to build a scored Top 5-10 reading shortlist that feeds directly into
  hsi-msi-idea-scout-codex for HSI-MSI and Agent+HSI-MSI image fusion.
---

# Cross-Domain Top-Venue Paper Radar (Codex) — 【9大顶会跨域论文雷达】

This skill acts as **Stage 0 (Upstream Discovery Radar)** in the graduate research suite for **Agent + HSI-MSI image fusion**. Inspired by multi-domain AI paper note taxonomies (`M0rtzz/paper-notes`) and 5-minute core-insight triage, it scans the rolling 24-month window of the **9 target venues** across **7 expanded high-resonance domains**, filters out surveys and already-read papers, scores candidates on a 25-point rubric, and hands off the best 1–2 hits directly to `hsi-msi-idea-scout-codex`.

## Progressive Disclosure Map

- 9-venue whitelist, DBLP stream IDs & rolling 24-month rules: [references/venue_whitelist.md](./references/venue_whitelist.md)
- 7 expanded domains (`D1–D7`) & curated English query lexicon: [references/domain_taxonomy_lexicon.md](./references/domain_taxonomy_lexicon.md)
- 5-dimension / 25-point pioneering & transferability rubric: [references/scoring_rubric.md](./references/scoring_rubric.md)
- Radar-specific anti-patterns & audit red lines: [references/anti_patterns.md](./references/anti_patterns.md)
- "5-minute core insight" radar brief format anchor: [examples/sample_radar_brief.md](./examples/sample_radar_brief.md)

Executable deterministic helpers (always resolve paths relative to `<SKILL_DIR>`):

- Dual-engine 9-venue radar scanner (DBLP exact streams + OpenAlex enrichment + OA PDF URL extraction + ledger deduplication): [scripts/radar_scan.py](./scripts/radar_scan.py)
- Legal Open-Access PDF batch downloader (validates `%PDF` header, skips paywalls cleanly): [scripts/download_papers.py](./scripts/download_papers.py)
- Shortlist Markdown/JSON exporter: [scripts/export_shortlist.py](./scripts/export_shortlist.py)

## Codex Execution Notes

1. Always resolve `<SKILL_DIR>/scripts/radar_scan.py` and `<SKILL_DIR>/scripts/export_shortlist.py` relative to this skill directory.
2. **Focus each sweep on 1–2 domains** (e.g., `D2,D7` or `D4,D6`) rather than sweeping all 7 domains at once, to preserve high signal-to-noise ratio and stay within context/API budgets.
3. **Offline / sandbox rule**: If outbound network is blocked and `radar_scan.py` cannot reach DBLP/OpenAlex, stop and ask the user to allow network access or provide an `--extra-json` export from OpenReview / CVF / `papernotes.org`. Never invent papers from memory.

---

## Mandatory 5-Phase Radar Workflow

### Phase 0: Lock the Radar Mission Contract
1. Select **1–2 target domains** from `D1–D7` in [references/domain_taxonomy_lexicon.md](./references/domain_taxonomy_lexicon.md) based on the user's request (if unspecified, recommend a focused pair such as `D2 + D4` or `D1 + D6`).
2. Lock **target venues** (default: all 9 venues in [references/venue_whitelist.md](./references/venue_whitelist.md)) and **rolling lookback window** (default: `24` months).
3. Lock **target track** (`Track A: HSI-MSI Fusion`, `Track B: Agent + HSI-MSI Fusion`, or `Dual Track`).
4. Check if `./literature_ledger/ledger.csv` exists in the workspace so `radar_scan.py` automatically skips papers already read via `hsi-agent-paper-reader-codex`.

### Phase 1: Deterministic 9-Venue Retrieval & Deduplication
Run `scripts/radar_scan.py` using domain presets (`--domains`) and/or custom queries (`--queries`):

```bash
python <SKILL_DIR>/scripts/radar_scan.py \
  --domains "D2,D4" \
  --months 24 \
  --max-per-venue 8 \
  --exclude-ledger ./literature_ledger/ledger.csv \
  --output radar_candidates.json
```

If the user also supplied a local export from OpenReview / CVF / `papernotes.org`, merge it via `--extra-json path/to/extra.json`.

### Phase 2: "5-Minute Triage" Scoring (25-Point Rubric)
Read [references/scoring_rubric.md](./references/scoring_rubric.md). Inspect the **actual retrieved abstracts** (never score from titles alone) and score each strong candidate on 5 dimensions (0–5 each, max 25):
1. **Pioneering / Overlooked Flaw Signal** (0–5)
2. **Physical / Algorithmic Isomorphism with HSI-MSI or Agent Loop** (0–5)
3. **Cross-Domain Information Advantage** (0–5)
4. **Verifiability & Reproducibility** (0–5)
5. **Recency & Venue Impact** (0–5)

Keep only the **Top 5–10 papers** scoring **$\ge 18/25$** (or clearly note if fewer pass the bar).

### Phase 3: Generate "5-Minute Core Insight" Radar Brief & Download Info
Follow [examples/sample_radar_brief.md](./examples/sample_radar_brief.md). For each shortlisted paper, write a crisp, high-density card:
- Exact verified metadata (title, authors, venue & year strictly within the 9 venues & 24 months, domain tag `D1–D7`, 25-point score breakdown, DOI/URL, **OA PDF download URL & OA status**, and code link if present).
- **5-Minute Core Summary (3 crisp sentences)**: overlooked problem + core mechanism + verified takeaway.
- **Why It Helps Your Research (Track A / Track B)**: exact HSI-MSI or Agent+HSI-MSI hook.
- **Action Priority**: `P0 (Deep-Dive Immediately)` / `P1 (Watchlist)` / `P2 (Related Work)`.

If the user asks to download the `P0` PDFs (or if network is enabled), run `scripts/download_papers.py` to fetch legal Open-Access PDFs directly into `./downloaded_papers/` (never bypass paywalls; flag closed-access IEEE/Springer papers for institutional download):

```bash
python <SKILL_DIR>/scripts/download_papers.py \
  --input radar_candidates.json \
  --indices "1,2" \
  --output-dir ./downloaded_papers
```

Optionally run `scripts/export_shortlist.py` to persist a clean Markdown/JSON shortlist artifact.

### Phase 4: Anti-Patterns Audit & Handoff to `hsi-msi-idea-scout-codex`
1. Audit the entire brief against [references/anti_patterns.md](./references/anti_patterns.md) (zero fabricated citations, zero unrefereed arXiv masquerading as top venues, zero survey leakage, no title-only scoring).
2. At the bottom of the brief, **generate 1–2 ready-to-copy `$hsi-msi-idea-scout-codex` prompts** pre-filled with the top `P0` paper(s) so the user can transition seamlessly into full-text single-paper deep dive.
