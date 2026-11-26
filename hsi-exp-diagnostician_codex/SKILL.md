---
name: hsi-exp-diagnostician_codex
description: >-
  Use this skill when the user wants to audit HSI-MSI image fusion or Agent+HSI-MSI experiment
  results, compute physical/spectral metrics (PSNR, SAM, ERGAS, CC, band-wise error), diagnose
  why PSNR improves while SAM degrades or why an Agent reflection loop diverges, and generate
  publication-grade diagnostic plots (spatial error heatmaps, pixel spectral curves, agent
  residual convergence curves).
---

# HSI-MSI Experiment Diagnostician & Visualizer (Codex)

This skill helps graduate students move beyond looking only at average PSNR. It audits **spatial-spectral trade-offs**, pinpoints **spectral absorption distortion**, evaluates **Agent multi-step convergence/cost**, and generates publication-ready diagnostic figures (SVG/PDF/PNG).

## Progressive Disclosure Map

- Metric anomaly & failure-mode diagnostic matrix: [references/metric_interpretation_guide.md](./references/metric_interpretation_guide.md)
- Deterministic metric & diagnostic plotting script: [scripts/compute_hsi_metrics.py](./scripts/compute_hsi_metrics.py)

## Codex Execution Notes

1. Resolve `<SKILL_DIR>/scripts/compute_hsi_metrics.py` relative to this skill directory.
2. Never fabricate metric tables or improvement deltas—compute them directly from user-provided `.npy` / `.mat` arrays, logs, or CSV files.
3. For publication figures, prefer vector output (`.svg` or `.pdf`) with clean labels, colorblind-safe colormaps, and non-overlapping legends.

---

## Mandatory 4-Phase Diagnostic Workflow

### Phase 0: Intake Experimental Artifacts
Accept any of the following from the user:
- Ground-truth & reconstructed HSI arrays (`.npy` or `.mat`, shape `[H, W, C]` or `[C, H, W]`).
- Training/evaluation logs or CSV metric tables across baselines and ablations.
- Agent execution traces (JSON logs recording turn-by-turn tool calls, spatial/spectral residuals, latency).

### Phase 1: Deterministic Metric Computation & Band/Spatial Breakdown
When arrays are available, run `scripts/compute_hsi_metrics.py` to compute:
- **Global metrics**: PSNR (dB), SAM (degrees), ERGAS (at given scale ratio), Mean Spectral Correlation Coefficient (CC).
- **Per-band error profile**: Identify which wavelength indices suffer worst RMSE/PSNR (e.g., edge bands or absorption valleys).
- **Spatial error hotspots**: Top-K worst-SAM pixels and spatial error percentiles (p50 / p95 / p99).

```bash
python <SKILL_DIR>/scripts/compute_hsi_metrics.py \
  --gt path/to/gt.npy \
  --pred path/to/pred.npy \
  --scale 8 \
  --plot-dir ./diag_figs \
  --output metrics_report.json
```

### Phase 2: Root-Cause Diagnosis (Spatial vs. Spectral vs. Agent Loop)
Read [references/metric_interpretation_guide.md](./references/metric_interpretation_guide.md) and map observed anomalies to concrete causes:
- **PSNR up, SAM worse** -> MSI spatial detail over-injection / missing spectral angle constraint / `InstanceNorm` distorting band ratios.
- **High ERGAS on specific bands** -> Unbalanced band scaling, poor SRF estimation, or noisy boundary bands.
- **Agent residual oscillates or worsens after Turn 2** -> No monotonic rollback guard, noisy physical probe, or mismatched tool ordering.

### Phase 3: Actionable Fix Plan & Publication-Ready Visuals
Deliver:
1. **Diagnostic Summary Table** (Baseline vs. Ours across PSNR, SAM, ERGAS, worst-5-band PSNR, and Agent turn/latency overhead).
2. **Top 3 Prioritized Engineering Fixes** (loss weight, normalization, PSF/SRF consistency, or Agent stopping rule).
3. **Diagnostic Figures** (saved to `--plot-dir` if arrays/traces were provided): spatial error heatmap, worst-pixel spectral curve comparison, and band-wise PSNR curve.
