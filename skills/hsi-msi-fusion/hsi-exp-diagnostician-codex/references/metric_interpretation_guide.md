# HSI-MSI & Agent Metric Interpretation Guide

Use this diagnostic matrix in **Phase 2** to translate metric anomalies into concrete engineering fixes.

## 1. HSI-MSI Quantitative Anomaly Matrix

| Observed Symptom | Likely Physical / Algorithmic Root Cause | Recommended Fix |
| :--- | :--- | :--- |
| **PSNR increases, SAM degrades** | Spatial edges from HR-MSI dominate the loss, distorting relative inter-band spectral ratios; or per-channel normalization (`InstanceNorm`) breaks band scaling. | Add explicit SAM / cosine spectral loss; enforce spectral re-projection $\|\mathbf{R}\hat{\mathbf{X}}-\mathbf{Z}\|_1$; replace `InstanceNorm` with `LayerNorm` / residual-to-upsampled-LR-HSI. |
| **PSNR good, ERGAS unusually high** | Large relative error on low-intensity bands (e.g., water-absorption or UV/NIR edge bands), since ERGAS normalizes RMSE by band mean. | Inspect per-band RMSE curve; apply band-balanced relative loss or clip/regularize near-zero noisy bands. |
| **Sharp edges in reduced-res (Wald), blurry or haloed in full-res** | Domain shift between synthetic Gaussian PSF/SRF and real sensor PSF/SRF, or LR-HSI/HR-MSI sub-pixel misregistration. | Add blind PSF/SRF estimation or Test-Time Adaptation (TTA) minimizing real re-projection residuals; check deformable alignment. |
| **Checkerboard or periodic artifacts** | Transposed conv / `PixelShuffle` mismatch or window-attention boundary shift. | Switch to bilinear/bicubic upsampling + conv refinement, or add shifted-window / overlapping tile blending. |
| **Worst-SAM pixels cluster along object boundaries** | Spatial-spectral mixing across material edges due to misalignment or overly wide blur kernel. | Add edge-aware / gradient-guided weighting or joint registration before fusion. |

## 2. Agent + HSI-MSI Loop Anomaly Matrix

| Observed Symptom | Likely Root Cause | Recommended Fix |
| :--- | :--- | :--- |
| **Residual drops at Turn 1, spikes at Turn 2** | Agent invokes an incompatible refiner or over-iterates without rollback verification. | Enforce deterministic **monotonic residual guard**: keep best-so-far state and roll back if physical residual increases. |
| **Agent always picks the same tool** | Observation state lacks discriminative physical cues (e.g., only passing RGB preview or coarse scalar PSNR). | Inject structured physical probes: `(spatial_res, spectral_res, blur_score, alignment_corr, band_uncertainty)`. |
| **Latency / token cost too high** | Per-patch or pixel-level LLM calls. | Restrict Agent to macro tile/scene-level planning ($\le 3$ turns) and delegate pixel execution to lightweight PyTorch tools. |
