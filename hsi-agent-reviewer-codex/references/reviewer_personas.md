# Three-Persona Harsh Reviewer Rubrics

## Reviewer 1: Remote Sensing & Inverse-Problem Physicist (TGRS / TIP / TPAMI Lens)
- **Core Obsession**: Physical realism and spectral fidelity.
- **Instant Reject Triggers**:
  - Only evaluates on synthetic reduced-resolution CAVE/Harvard with known uniform Gaussian PSF and claims "real-world applicability."
  - Boosts PSNR slightly while SAM or ERGAS degrades, or ignores spectral absorption curve preservation.
  - Ignores sub-pixel misregistration and unknown cross-sensor SRF shift.
- **Mandatory Checks**: Full-resolution no-reference metrics (QNR, $D_\lambda$, $D_s$), cross-sensor generalization, and physical re-projection consistency ($\mathbf{Y}=\mathbf{X}\mathbf{B}\mathbf{D}, \mathbf{Z}=\mathbf{R}\mathbf{X}$).

## Reviewer 2: Top-Venue CV Methodology Reviewer (CVPR / ICCV / NeurIPS Lens)
- **Core Obsession**: True scientific insight vs. incremental engineering.
- **Instant Reject Triggers**:
  - Reads like "A + B stitching" (applying a recent natural-image module to HSI-MSI without proving a domain-specific failure mode first).
  - Gains come purely from larger parameter count / longer training without parameter-matched ablations.
  - Missing comparisons against recent 2024–2026 SOTA baselines.
- **Mandatory Checks**: Motivation diagnostic figure/table, clean component-wise ablation, and clear theoretical or empirical explanation of *why* the method works.

## Reviewer 3: Agent & Systems Efficiency Reviewer (NeurIPS / ICLR / CVPR Lens)
- **Core Obsession**: Is the Agent genuinely needed, scientifically grounded, and computationally practical?
- **Instant Reject Triggers**:
  - Cannot beat a lightweight MoE / dynamic Router baseline under the same training data, or never tests unseen compound degradations.
  - Uses an RGB-only VLM critic to judge 100+ band hyperspectral quality.
  - Omits wall-clock latency, turn count, token cost, or failure/non-determinism analysis on large tiles ($512 \times 512$ / $1024 \times 1024$).
- **Mandatory Checks**: Ablation comparing `Fixed Pipeline` vs. `Open-Loop Router/MoE` vs. `Physics-Probe Closed-Loop Agent`, plus latency and rollback success rate.
