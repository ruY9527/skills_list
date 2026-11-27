# Radar Anti-Patterns & Quality Red Lines

Audit every radar brief against these 5 red lines in **Phase 4**:

1. **Zero Citation Hallucination**: Every shortlisted paper must originate directly from `scripts/radar_scan.py` output (or user-provided `--extra-json`) with a real DOI / landing URL / DBLP record. Never invent or fill gaps from memory.
2. **Strict 9-Venue & 24-Month Enforcement**: Never smuggle unrefereed arXiv preprints, workshops, MDPI/Sensors papers, or >24-month-old papers into the radar shortlist.
3. **No Title-Only Scoring**: Never assign a `P0` priority or write a "5-minute summary" for a paper whose abstract is empty (`abstract_verified: false`). If a promising DBLP hit lacks an abstract, flag it as `[Abstract Missing — Fetch PDF Before Scoring]` and place it in a separate "Needs Manual Fetch" appendix.
4. **No Full-Spectrum Overload**: Never blindly sweep all 7 domains (`D1–D7`) in one single pass unless the user explicitly demands a broad annual census; focused 1–2 domain sweeps yield far higher precision.
5. **No False "Unexplored" Guarantees at Radar Stage**: This radar skill identifies *high-potential cross-domain candidates*—it does **not** replace `hsi-msi-idea-scout-codex`'s per-point `check_hsi_gap.py` reverse gap check. Always hand off `P0` candidates to `$hsi-msi-idea-scout-codex` for formal Tier 1/2/3 verification.
