# Single-Paper Cross-Domain Transfer Report (Format Template)

> **Note**: This file is the output format anchor for `hsi-msi-idea-scout_codex`. Replace all bracketed placeholders with **verified details from the user-provided paper** and **verified reverse gap-check results** from `scripts/check_hsi_gap.py`. Never fabricate citations or unread equations.

---

## 1. Source Paper Qualification & Evidence Depth

- **Paper Title**: `<Exact Title of User-Provided Paper>`
- **Authors & Year**: `<First Author et al., YYYY>`
- **Venue & Eligibility Check**: `<e.g., CVPR 2025 — PASS (in 9-venue whitelist & within rolling 24-month window)>` *(or explicitly flag if preprint / outside 9 venues / >24 months)*
- **Source Domain**: `<Natural Image / Medical Image>`
- **Verifiable Source**: `<PDF path / DOI / arXiv URL / GitHub repo>`
- **Evidence Depth Tag**: `[Full-Text Verified]` or `[Abstract-Level Triage]`
- **Target Tracks**: `Track A (HSI-MSI Fusion)` / `Track B (Agent + HSI-MSI Fusion)`
- **Pioneering / First-of-Its-Kind Assessment**: `<2–3 sentences explaining what makes this paper genuinely pioneering or what overlooked flaw it exposes.>`

---

## 2. Atomic Sub-Points & Reverse Gap-Check Matrix

| ID | Extracted Innovation / Overlooked Flaw (from Source Paper) | Target Track | HSI-MSI Pain Point | Gap Tier | Closest Existing HSI-MSI Work (OpenAlex + arXiv) | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| P1 | `<Sub-mechanism / overlooked flaw #1>` | Track A | `A1 + A2` | **Tier 1** | None matching core mechanism (`queries: ...`) | **Keep (Primary)** |
| P2 | `<Sub-mechanism / overlooked flaw #2>` | Track B | `B2 + B4` | **Tier 2** | `<Closest paper, Year, Venue — explain what it still misses>` | **Keep (Differentiated)** |
| P3 | `<Sub-mechanism #3>` | Track A | `A3` | **Tier 3** | `<Multiple existing HSI-MSI papers>` | **Drop (Saturated)** |

---

## 3. Implicit-Assumption Audit (What Breaks in HSI-MSI?)

1. **Assumption #1 (`<e.g., 3-channel RGB / isotropic 3D voxel>`)**: `<Why it breaks for C=31..224 non-uniform spectral bands and SAM preservation.>`
2. **Assumption #2 (`<e.g., Known degradation / pre-aligned input>`)**: `<Why it breaks under blind PSF/SRF or spatial misregistration in real HSI-MSI.>`
3. **Assumption #3 (`<e.g., RGB VLM perceptual critic>`)**: `<Why RGB-only critics miss spectral distortion in Track B Agent loops.>`

---

## 4. Actionable Cross-Domain Transfer Blueprints (Tier 1 & Tier 2 Only)

### Blueprint P1: `<Concise HSI-MSI Proposal Title>` (`Track A: HSI-MSI Fusion`)
- **Evidence Depth**: `[Full-Text Verified]` / `[Abstract-Level Triage]`
- **Source Anchor**: `<Exact section, equation number, or module/class name in the source paper>`
- **Medical Goldmine Tag** *(if applicable)*: `<M1 Registration+Fusion / M2 Operator Mismatch / M3 Uncertainty & Hallucination / N/A>`
- **Gap-Check Evidence**:
  - **Gap Tier**: `Tier 1` / `Tier 2`
  - **Queries & Synonyms Run**: `<Exact --concept and --synonyms passed to check_hsi_gap.py>`
  - **Differentiation vs. Closest HSI-MSI Work**: `<Concrete delta>`
- **Motivation Diagnostic Experiment (Prove the Flaw Exists in HSI-MSI First)**:
  - `<10–20 line quantitative diagnostic setup on CAVE/Chikusei exposing the overlooked failure mode in existing baselines (e.g., plot/metric to generate before introducing the new module).>`
- **Physics-Aware Adaptation for HSI-MSI**:
  - **Why Naive Copy Fails**: `<Exact failure mode on C-band HSI tensors or SAM>`
  - **Proposed Modification**: `<Tensor shape transformation, spectral-subspace handling, and coupling with Y=XBD & Z=RX>`
  - **Baseline Integration & Memory Fit** *(aligned with `my_baseline_profile.md`)*: `<Exact insertion slot in user's baseline + estimated VRAM/runtime impact>`
- **MVP Experiment & Reviewer Defense**:
  - **Datasets & Metrics**: `<CAVE, Chikusei, PaviaU, WorldView-3; PSNR, SAM, ERGAS, Q2n>`
  - **Critical Ablation**: `<Single ablation isolating P1's contribution>`
  - **Likely Reviewer Objections & Mitigations**:
    1. `<Objection 1>` -> `<Concrete mitigation>`
    2. `<Objection 2>` -> `<Concrete mitigation>`
  - **Ratings**: Novelty `★★★★★` | Feasibility `★★★★☆`

---

### Blueprint P2: `<Concise Agent+HSI-MSI Proposal Title>` (`Track B: Agent + HSI-MSI Fusion`)
- **Evidence Depth**: `[Full-Text Verified]` / `[Abstract-Level Triage]`
- **Source Anchor**: `<Exact section/algorithm in the source paper>`
- **Gap-Check Evidence**:
  - **Gap Tier**: `Tier 1` / `Tier 2`
  - **Queries & Synonyms Run**: `<...>`
  - **Differentiation vs. Closest HSI-MSI Work**: `<...>`
- **Motivation Diagnostic Experiment (Prove Static Pipelines Fail First)**:
  - `<Quantitative stress test showing where fixed networks/routers collapse under compound degradation or spectral drift.>`
- **Agent Loop Adaptation for HSI-MSI**:
  - **Observation State (Non-RGB Physical Probes)**: `<Spatial/spectral re-projection residuals, PSF/SRF mismatch, local SAM proxy / uncertainty map>`
  - **Action Space**: `<Alignment tool, PSF/SRF updater, unfolding solver switch, band-specific refiner>`
  - **Reflection & Stopping Criterion**: `<Monotonic physical residual reduction within <=3–4 turns>`
- **Mandatory 3-Question Reviewer Defense (Track B)**:
  1. **Why Agent over MoE/Router?**: `<Explain compound unseen degradation + multi-step rollback that static routers cannot execute.>`
  2. **How does it see 100+ spectral bands beyond RGB?**: `<Name the exact deterministic spectral/physical probe tools feeding structured diagnostics to the agent.>`
  3. **How is compute/latency bounded on large remote-sensing tiles?**: `<Macro tile-level planning (<=3 turns) + micro differentiable execution; estimated token/latency overhead.>`
- **MVP Experiment & Reviewer Defense**:
  - **Datasets & Metrics**: `<Reduced-res CAVE/Chikusei + full-res WorldView-3/GaoFen-2; PSNR, SAM, QNR, turns/latency>`
  - **Critical Ablation**: `<Fixed pipeline vs. open-loop router vs. physics-probe closed-loop agent>`
  - **Likely Reviewer Objections & Mitigations**:
    1. `<Latency / compute overhead>` -> `<Tile-level coarse planning + lightweight numeric probes>`
    2. `<Non-determinism>` -> `<Structured JSON tool schema + deterministic physical fallback>`
  - **Ratings**: Novelty `★★★★★` | Feasibility `★★★☆☆`

---

## 5. Recommended Research Action Plan

| Priority | Blueprint | Track | Gap Tier | Novelty | Impl. Effort | Recommended Target Venue |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `P1` | Track A | Tier 1 | High | Medium | CVPR / TIP / TPAMI |
| 2 | `P2` | Track B | Tier 2 | Very High | Medium-High | NeurIPS / CVPR / ICLR |
