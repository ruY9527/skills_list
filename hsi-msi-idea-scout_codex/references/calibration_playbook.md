# Skill Calibration & Continuous Evolution Playbook

A skill starts at ~60% quality on day one and reaches 90%+ through closed-loop calibration on real papers. Run these 3 lightweight calibration steps whenever you refine `hsi-msi-idea-scout_codex`.

---

## Step 1: Stress-Test Gap Detection with a Known Saturated Paper (Tier-3 Sanity Check)
Pick 1 well-known mechanism that you **already know** has been widely migrated to HSI-MSI fusion (e.g., standard DDPM diffusion, vanilla Swin Transformer, or basic Mamba scanning):
1. Run `scripts/check_hsi_gap.py --concept "<mechanism>" --synonyms "<synonym1>,<synonym2>"`.
2. **Pass condition**: The script must classify it as `Tier 3 (Likely Saturated)` and surface real HSI-MSI papers.
3. **If it mistakenly reports Tier 1**: Add the missing HSI-MSI terminology to `HSI_ANCHOR_QUERIES` in `scripts/check_hsi_gap.py` or broaden your `--synonyms` habit.

## Step 2: Upgrade `examples/sample_idea_report.md` into a Real Golden Example
1. Run the full 6-phase workflow on **1 real pioneering paper** (natural or medical image) that you personally inspect and approve.
2. Polish the resulting `[Full-Text Verified]` report until it matches your exact standard for novelty rigor, mathematical clarity, and reviewer defense.
3. Replace the placeholder template in `examples/sample_idea_report.md` with that real golden report (or save it alongside as `examples/golden_example_1.md` and link it in `SKILL.md`).
   - *Why it matters*: One high-bar real example anchors Codex's output depth far more effectively than dozens of abstract rules.

## Step 3: Post-Run Feedback Loop (Capture New Failure Modes)
After each real single-paper analysis session, spend 2 minutes asking:
- **Did Codex hallucinate or over-extrapolate?** -> Add a specific rule to `references/anti_patterns.md`.
- **Did we discover a high-value cross-domain analogy?** -> Append a row to `references/transfer_bridge_map.md`.
- **Did a newly tried module fail on 128-band HSI (OOM or SAM collapse)?** -> Record the empirical pitfall in `references/hsi_msi_pain_points.md` or `references/my_baseline_profile.md`.
