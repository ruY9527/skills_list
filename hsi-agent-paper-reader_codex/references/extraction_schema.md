# Standardized Paper Extraction Schema

Use this schema in **Phase 1** to ensure every paper in the literature ledger is directly comparable when writing Related Work or selecting baselines.

## 1. Universal Fields (All Categories)
- `title`: Exact paper title.
- `authors`: `First Author et al.`
- `year`: 4-digit publication/acceptance year.
- `venue`: Conference/Journal short name (e.g., `CVPR`, `TIP`, `TGRS`, `TPAMI`, `ICLR`, `arXiv`).
- `category`: `HSI-MSI` | `Vision-Agent` | `Agent+HSI-MSI`.
- `evidence_depth`: `Full-Text Verified` | `Abstract-Level Triage`.
- `code_url`: Official repository URL or `N/A`.
- `role`: `Baseline` (must compare experimentally) | `Agent Tool Candidate` (can be wrapped as a solver) | `Inspiration` (method idea) | `Related Work Only`.

## 2. HSI-MSI Specific Fields
- **Degradation Model**:
  - `Known-Uniform`: Assumes fixed Gaussian PSF & known SRF.
  - `Blind-PSF/SRF`: Estimates or adapts to unknown PSF and/or SRF.
  - `Misregistered`: Explicitly handles spatial misalignment between LR-HSI and HR-MSI.
- **Spectral Handling**: How $C=31\text{–}224$ bands are processed (e.g., spectral subspace projection, group-wise 3D conv, spectral-spatial attention, band-wise Mamba).
- **Loss / Physics Consistency**: e.g., $L_1$, SAM loss, spatial/spectral re-projection loss ($\|\hat{\mathbf{X}}\mathbf{B}\mathbf{D}-\mathbf{Y}\|$, $\|\mathbf{R}\hat{\mathbf{X}}-\mathbf{Z}\|$).
- **Evaluation Protocol**: Reduced-resolution (Wald's protocol) and/or Full-resolution (no-reference QNR / $D_\lambda$ / $D_s$).

## 3. Vision-Agent Specific Fields
- **State / Perception**: RGB VLM visual inspection, degradation classifier, numeric quality metrics, or physical residual probes.
- **Action / Tool Space**: List of callable tools (restorers, aligners, denoisers, parameter tuners).
- **Control Policy**: Fixed pipeline vs. single-step LLM router vs. multi-turn Plan-Act-Observe-Reflect with rollback.
- **Efficiency**: Number of LLM/VLM calls per image, inference latency, backbone LLM size.

## 4. Mandatory Limitation Checklist (Check at Least 2)
- Does it fail when the sensor SRF or scale factor changes at test time?
- Does it silently assume pixel-perfect LR-HSI / HR-MSI registration?
- Does it boost PSNR at the expense of SAM (spectral distortion)?
- For Agents: Is the critic RGB-only (blind to spectral distortion), or is per-image latency prohibitive for large remote-sensing tiles?
