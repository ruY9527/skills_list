---
name: hsi-msi-idea-scout-codex
description: >-
  【单篇跨域选题与查新】Use this skill when the user provides a single paper (PDF, arXiv/URL, title, text, or
  official code repo) from natural image or medical image domains—ideally a pioneering or
  first-of-its-kind paper/module from the last 2 years of IJCV, TIP, CVPR, NeurIPS, AAAI,
  ICLR, ICCV, ECCV, or TPAMI—and wants to dissect its core innovations or overlooked flaws,
  verify whether they are unexplored in HSI-MSI image fusion or Agent + HSI-MSI image fusion,
  and produce a concrete, physics-aware cross-domain transfer blueprint.
---

# Single-Paper Cross-Domain Transfer to HSI-MSI Fusion (Codex)

This skill turns Codex into a rigorous, evidence-backed research analyst that takes **one user-provided paper** from natural image or medical image domains and systematically transfers its pioneering mechanisms or overlooked insights into **HSI-MSI image fusion (Track A)** and/or **Agent + HSI-MSI image fusion (Track B)**.

It enforces **venue/recency verification, implicit-assumption auditing, dual-channel reverse gap checking, physics-aware adaptation, and strict anti-hallucination red lines**.

## Progressive Disclosure Map

Read reference files on demand rather than loading everything upfront:

- 9-venue whitelist, aliases & rolling 2-year verification rules: [references/venue_taxonomy.md](./references/venue_taxonomy.md)
- HSI-MSI & Agent+HSI-MSI core pain points: [references/hsi_msi_pain_points.md](./references/hsi_msi_pain_points.md)
- Natural/Medical-to-HSI-MSI mechanism transfer map (incl. 3 high-priority Medical Goldmines): [references/transfer_bridge_map.md](./references/transfer_bridge_map.md)
- Personal baseline, GPU budget & target venue profile (read in Phase 0/4 if populated): [references/my_baseline_profile.md](./references/my_baseline_profile.md)
- 7 hard academic red lines & anti-patterns audit: [references/anti_patterns.md](./references/anti_patterns.md)
- Skill calibration & continuous evolution playbook: [references/calibration_playbook.md](./references/calibration_playbook.md)
- Single-paper transfer report format anchor: [examples/sample_idea_report.md](./examples/sample_idea_report.md)

Executable deterministic helpers (always resolve paths relative to this skill directory `<SKILL_DIR>`):

- **Core (Mandatory in Phase 3)**: Dual-channel reverse gap-check (OpenAlex + arXiv preprints with synonym expansion): [scripts/check_hsi_gap.py](./scripts/check_hsi_gap.py)
- **Optional (Phase 0 metadata check / peer lookup)**: Verify 9-venue membership or fetch related papers from the 9 venues: [scripts/fetch_top_venues.py](./scripts/fetch_top_venues.py)

## Codex Execution Notes

1. **Resolve script paths relative to `<SKILL_DIR>`**: Invoke `<SKILL_DIR>/scripts/check_hsi_gap.py` (never assume `scripts/` is in the user's current working directory).
2. **Sandbox / Offline handling**: If Codex disables outbound network so `check_hsi_gap.py` cannot reach OpenAlex/arXiv, **stop and tell the user** to allow network access or provide local HSI-MSI literature notes. Never claim "unexplored in HSI-MSI (Tier 1)" without verified gap-check evidence.
3. **Evidence depth honesty**: Label the analysis explicitly as **`[Full-Text Verified]`** (when the user provides full PDF/Markdown/LaTeX/code) or **`[Abstract-Level Triage]`** (when only title/abstract is available). Never fabricate equations, layer counts, or loss terms not present in the provided source.

---

## Mandatory 6-Phase Single-Paper Workflow

Execute every phase in order. Do not skip Phase 2 (implicit-assumption audit), Phase 3 (per-point reverse gap check), or Phase 5 (anti-pattern audit).

### Phase 0: Paper Intake, Venue/Recency Check & Track Contract

1. **Ingest the user's paper**: Read the provided PDF, Markdown, text excerpt, arXiv/URL content, or code repository.
2. **Verify against the 9-venue & rolling 2-year criteria** (see [references/venue_taxonomy.md](./references/venue_taxonomy.md)):
   - Target 9 venues: `IJCV, TIP, CVPR, NeurIPS, AAAI, ICLR, ICCV, ECCV, TPAMI`.
   - Target recency: rolling **24 months** from today's date.
   - Source domain: **Natural Image** or **Medical Image**.
   - *Strict honesty rule*: If the provided paper is outside the 9 venues, older than 24 months, or still an unrefereed arXiv preprint, **flag this explicitly in the header** rather than mislabeling it, then proceed with the transfer analysis.
3. **Check Personal Baseline Profile**: Read [references/my_baseline_profile.md](./references/my_baseline_profile.md). If the user has filled in their baseline repo, GPU memory limit, datasets, or target venue, lock all Phase 4 blueprints to those exact constraints; otherwise use standard defaults and note that the profile can be customized.
4. **Lock Target Track** (default to **Dual Track** unless the user specifies one):
   - **Track A**: HSI-MSI Image Fusion
   - **Track B**: Agent + HSI-MSI Image Fusion

### Phase 1: Deep Dissection — Prioritize Failure Mechanisms Over Raw Modules

Do **not** write a generic paper summary, and do **not** treat the paper merely as a "module to swap in." Dissect the paper into **2–4 atomic, transferable sub-points**, explicitly prioritizing:

1. **Overlooked failure mechanism (highest value)**: The exact underlying failure mode, mathematical bias, or blind spot exposed by this paper in natural/medical imaging—this is what elevates a paper from "module stitching" to a top-venue discovery.
2. **First-of-its-kind / pioneering core**: The minimal mathematical operator, prior, training/inference rule, loss structure, or agentic loop stripped of its original RGB/MRI/CT dataset shell.
3. **Verified source anchors**: Exact section/equation/module names from the provided text or code (do not invent any that were not read).

### Phase 2: Implicit-Assumption Audit & HSI-MSI Resonance Mapping

Read [references/hsi_msi_pain_points.md](./references/hsi_msi_pain_points.md) and [references/transfer_bridge_map.md](./references/transfer_bridge_map.md). When the source paper is from **Medical Imaging**, explicitly check whether it touches the **3 High-Priority Medical-to-HSI Goldmines** (`M1` Joint Deformable Registration & Fusion, `M2` Forward-Operator Mismatch / Blind Reconstruction, `M3` Pixel-Wise Uncertainty & Hallucination Control).

Before designing any transfer, audit every hidden assumption in the source paper that **breaks** in HSI-MSI fusion:

- **Channel dimensionality**: RGB ($3$) or 3D medical volume $\rightarrow$ HSI ($C = 31\text{–}224$ strongly correlated spectral bands).
- **Physical observation model**: HSI-MSI obeys explicit spatial ($\mathbf{Y} = \mathbf{X}\mathbf{B}\mathbf{D} + \mathbf{N}_h$) and spectral ($\mathbf{Z} = \mathbf{R}\mathbf{X} + \mathbf{N}_m$) degradation constraints.
- **Evaluation fidelity**: Perceptual sharpness (PSNR/LPIPS) vs. **spectral fidelity (SAM)** and full-resolution Wald's protocol mismatch (no full-resolution GT).
- **For Track B (Agent)**: Standard VLM critics only inspect 3-channel RGB and cannot perceive spectral distortion; agent perception must be grounded in quantitative physical/spectral probes.

Map each atomic sub-point from Phase 1 to the exact HSI-MSI pain point(s) (`A1–A5`, `B1–B5`) it can unlock.

### Phase 3: Per-Point Reverse Gap Check in HSI-MSI Literature

For **every** atomic sub-point extracted in Phase 1, run `scripts/check_hsi_gap.py` with **at least 2 synonym / parent mechanism phrases** (`--synonyms`) across both published venues (OpenAlex) and recent preprints (arXiv):

```bash
python <SKILL_DIR>/scripts/check_hsi_gap.py \
  --concept "<atomic mechanism from this paper>" \
  --synonyms "<synonym 1>,<synonym 2>" \
  --years 3 \
  --output gap_check_point1.json
```

Assign each sub-point an objective **Gap Tier**:

- **Tier 1 (True White Space)**: 0 directly comparable works found in HSI-MSI / pansharpening / spectral super-resolution (including recent arXiv preprints).
- **Tier 2 (Shallow Adoption / Specific Blind Spot)**: Broad family exists in HSI-MSI, **but** the specific overlooked flaw or sub-mechanism from this paper has not been solved.
- **Tier 3 (Saturated — Drop from Blueprint)**: Already widely migrated to HSI-MSI. Record it in the summary table as excluded and do **not** inflate it into a novelty claim.

### Phase 4: Concrete Transfer Blueprint (HSI-MSI & Agent+HSI-MSI)

For every **Tier 1** and **Tier 2** sub-point, produce an actionable adaptation blueprint aligned with [references/my_baseline_profile.md](./references/my_baseline_profile.md) (if populated):

- **Mandatory Motivation Diagnostic Experiment (Both Tracks)**:
  - Before proposing the module/agent fix, design a **10–20 line quantitative diagnostic experiment** on HSI-MSI data (e.g., CAVE/Chikusei) that exposes the exact overlooked failure mode in existing HSI-MSI SOTA baselines (e.g., spectral-angle drift vs. spatial gradient conflict, registration error sensitivity, or blind-PSF collapse).
- **For Track A (HSI-MSI Fusion)**:
  - Exact tensor-shape / spectral-subspace adaptation from source module to $(B, C, H, W)$ within the user's GPU memory budget without OOM or SAM collapse.
  - How the mechanism couples with $\mathbf{Y} = \mathbf{X}\mathbf{B}\mathbf{D}$ and $\mathbf{Z} = \mathbf{R}\mathbf{X}$ (including blind PSF/SRF or misregistration if relevant).
  - Why naive drop-in copying fails, and what exact modification fixes it.
  - Exact insertion slot in the user's baseline (if `my_baseline_profile.md` or source code was provided).
- **For Track B (Agent + HSI-MSI Fusion)**:
  - **Observation State**: Non-RGB deterministic physical/spectral probes (re-projection residuals, blur/SRF mismatch score, local SAM proxy / uncertainty map).
  - **Action Space**: Specialist fusion solvers, alignment tools, unfolding steps, or band-specific refiners.
  - **Reflection & Stopping Rule**: Monotonic physical-consistency gain under a strict turn/latency budget (e.g., $\le 3\text{–}4$ turns).
  - **Mandatory 3-Question Reviewer Defense**:
    1. *Why Agent over a lightweight MoE/Router?* (Long-tail compound degradation + non-fixed-step test-time rollback/reflection.)
    2. *How does the Agent perceive 100+ spectral bands beyond 3-channel RGB?* (Explicit physical/spectral probe tools translating high-D distortion into structured feedback.)
    3. *How is compute/latency bounded on large remote-sensing tiles?* (Macro scene/tile-level sparse planning + micro differentiable execution, with turn/token/latency budget.)
- **Minimum Viable Experiment (MVP)**:
  - Datasets (preferring those in `my_baseline_profile.md`, defaulting to CAVE, Harvard, Chikusei, PaviaU, WorldView-3 / GaoFen-2).
  - Critical ablation isolating the transferred mechanism's true contribution.
  - Metrics: PSNR, SAM, ERGAS, SSIM, Q2n / QNR (plus turn count, token cost & latency for Track B).

### Phase 5: 7-Red-Line Anti-Patterns Audit & Report Delivery

Read [references/anti_patterns.md](./references/anti_patterns.md) and audit the entire output against all **7 red lines** (including Red Line 3 diagnostic motivation, Red Line 5 Track B 3-question defense, and Red Line 7 no abstract-only technical fabrication). Fix or remove any sub-point that fails.

### Continuous Calibration (Post-Session Evolution)

After running this skill on a real paper, follow [references/calibration_playbook.md](./references/calibration_playbook.md) to promote a verified high-bar report into `examples/sample_idea_report.md` and feed newly discovered pitfalls or analogies back into `references/`.

---

## Final Output Format Contract

Follow [examples/sample_idea_report.md](./examples/sample_idea_report.md). Output directly in chat or save to a Markdown file when requested:

1. **Source Paper Qualification & Evidence Depth Header** (Title, Venue/Year check against the 9 venues & 24-month rule, Source Domain, Pioneering assessment, `[Full-Text Verified]` vs. `[Abstract-Level Triage]`).
2. **Atomic Sub-Points & Reverse Gap-Check Matrix** (Table mapping every extracted innovation/overlooked flaw $\rightarrow$ HSI-MSI Pain Point $\rightarrow$ Gap Tier `Tier 1/2/3` $\rightarrow$ Closest existing HSI-MSI work).
3. **Implicit-Assumption Audit** (What breaks when moving from the source paper's domain to HSI-MSI).
4. **Actionable Transfer Blueprints** (Detailed Track A and/or Track B adaptation cards for Tier 1 & Tier 2 points only, each with MVP experiment + top 1–2 reviewer objections and mitigations).
5. **Recommended Research Action Plan** (Which 1–2 sub-points to implement first, ranked by novelty, feasibility, and target venue ceiling).
