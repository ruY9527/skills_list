# Cross-Domain Transfer Bridge Map

Use this table in **Phase 2** to translate mechanisms from **Natural Image** and **Medical Image** papers into concrete **HSI-MSI** or **Agent + HSI-MSI** hypotheses.

## 1. Natural Image Mechanisms -> HSI-MSI / Agent+HSI-MSI

| Source Domain Concept | Core Transferable Mechanism | HSI-MSI / Agent+HSI-MSI Mapping | Key Adaptation Pitfall to Solve |
| :--- | :--- | :--- | :--- |
| **All-in-One / Prompt-Guided Restoration** | Dynamic degradation representation conditioning network weights or routing | Blind PSF/SRF + noise + misregistration unified fusion across sensors | RGB degradation prompts ignore spectral response mismatch; need physics-parameterized SRF/PSF prompts |
| **Rectified Flow / Flow Matching / Few-Step Consistency** | Straight ODE transport from degraded state to clean manifold in 1–4 steps | Fast generative HSI-MSI fusion directly transporting subspace/upsampled LR-HSI toward HR-HSI | Must enforce data-fidelity projection ($\mathbf{Y}, \mathbf{Z}$) along ODE steps to prevent spectral hallucination |
| **Frequency / Wavelet / Fourier Decomposition** | Decoupling low-frequency global structure from high-frequency detail | Separating low-freq spectral fidelity (from LR-HSI) and high-freq spatial detail (from HR-MSI) in dual spectral-spatial frequency domains | 2D spatial FFT alone misses 1D spectral-axis frequency anomalies |
| **Test-Time Training (TTT) / Test-Time Scaling** | Adapting model state or searching inference trajectories per test sample | Full-resolution zero-shot HSI-MSI adaptation using re-projection loss ($\mathbf{Y}, \mathbf{Z}$) without GT | Risk of overfitting to noise in $\mathbf{Y}$ or wrong PSF estimate; needs early-stopping / regularization |
| **Vision State Space (Mamba) / Linear Attention** | $O(N)$ long-range sequence modeling with selective gating | Joint spatial-spectral scanning across long band sequences ($C > 100$) + large spatial tiles | Scan order bias across non-adjacent spectral bands; need spectral-correlation-aware scanning |
| **Agentic Image Restoration / Tool-Use Vision Agents** | Plan -> Act (call specialist models) -> Observe -> Reflect closed loop | Degradation-aware fusion agent orchestrating registration, PSF/SRF estimation, unfolding, and spectral refinement | Standard VLM critics only read RGB; must inject quantitative spectral/physical diagnostic tools into agent observation |
| **Implicit Neural Representation (INR) / Continuous Fields** | Continuous coordinate-to-signal mapping for arbitrary resolution | Arbitrary-scale spatial AND arbitrary-wavelength continuous spectral fusion (cross-sensor SRF invariance) | High MLP query cost for $H \times W \times C$; needs subspace or factorized coordinate representation |

## 2. Medical Image Mechanisms -> HSI-MSI / Agent+HSI-MSI

### High-Priority Medical-to-HSI Goldmines (Raise Sensitivity When Reading Medical Papers)

Beyond standard `MRI-PET` fusion, pay special attention to **3 under-explored medical imaging themes** that share deep mathematical isomorphism with HSI-MSI fusion yet face far less competition than natural-image transfers:

1. **Goldmine M1 — Joint Deformable Registration & Fusion** (`CT-MRI alignment`, `non-rigid multimodal fusion`, `motion-compensated fusion`):
   - *HSI-MSI resonance*: Real remote-sensing LR-HSI and HR-MSI suffer from sub-pixel/parallax geometric misregistration, whereas ~95% of HSI-MSI papers assume ideal alignment.
   - *Key adaptation*: Enforce **band-consistent spatial warping** so spectral vectors are not mixed across object boundaries.
2. **Goldmine M2 — Forward-Operator Mismatch & Blind Reconstruction** (`MRI motion artifact`, `sparse-view CT operator mismatch`, `unknown coil sensitivity`, `blind physics-informed reconstruction`):
   - *HSI-MSI resonance*: Mathematically isomorphic to **spatially varying PSF** ($\mathbf{B}$) and **cross-sensor SRF drift** ($\mathbf{R}$) in blind HSI-MSI fusion.
   - *Key adaptation*: Marginalize or co-estimate $(\mathbf{B}, \mathbf{R})$ jointly with the latent HR-HSI subspace.
3. **Goldmine M3 — Pixel-Wise Uncertainty Quantification & Hallucination Control** (`epistemic uncertainty MRI`, `conformal/calibrated medical reconstruction`, `hallucination-free generative imaging`):
   - *HSI-MSI resonance*: Medical imaging forbids hallucinating lesions; hyperspectral remote sensing forbids hallucinating material absorption valleys (SAM collapse).
   - *Key adaptation*: Use band-aggregated uncertainty maps either as adaptive weights for data-consistency projection (Track A) or as **reflection triggers** for an Agent to switch to stricter physical solvers (Track B).

| Source Domain Concept | Core Transferable Mechanism | HSI-MSI / Agent+HSI-MSI Mapping | Key Adaptation Pitfall to Solve |
| :--- | :--- | :--- | :--- |
| **Multimodal Medical Fusion (MRI-PET / CT-MRI)** | Preserving functional intensity (PET/SPECT) while injecting structural edges (MRI/CT) | Exact structural analogy to HSI-MSI: preserving functional spectral curves (LR-HSI) while injecting spatial edges (HR-MSI) | PET has 1–3 channels whereas HSI has 31–224 strongly correlated bands; intensity preservation must generalize to spectral angle (SAM) |
| **Joint Registration & Fusion (Deformable Alignment)** | Handling non-rigid misalignment between modalities during fusion rather than assuming pre-alignment | Unaligned / misregistered real-world HSI-MSI fusion (different viewing angles, sensor parallax) | Spatial warping must be band-consistent so it does not mix spectra across object boundaries |
| **Physics-Informed MRI/CT Reconstruction (k-space / Radon Consistency)** | Alternating learned prior with exact measurement-space data consistency (DC) | Alternating learned spatial-spectral prior with exact PSF/SRF data consistency layers in HSI-MSI | In MRI the sampling mask is known; in blind HSI-MSI, PSF/SRF must be co-estimated or marginalized |
| **3D Volumetric / Slice-Consistent Modeling** | Exploiting inter-slice continuity in 3D volumes while keeping compute tractable | Treating the spectral axis as the 3rd dimension with non-uniform band spacing and spectral absorption structure | Unlike isotropic 3D medical voxels, HSI spatial and spectral axes are physically asymmetric |
| **Uncertainty Quantification & Hallucination Detection** | Pixel-wise epistemic/aleatoric uncertainty maps flagging unreliable reconstructions | Uncertainty-guided HSI-MSI fusion or Agent reflection trigger (routing high-uncertainty pixels/bands to stricter physical solvers) | Need band-aware uncertainty aggregation rather than scalar intensity variance |
| **Clinical / Radiology Diagnostic Agents** | Multi-specialist agent debate / verification grounded in quantitative measurements | Multi-agent HSI-MSI workflow: Degradation Estimator + Fusion Planner + Spectral Physicist Verifier | Keep agent turns sparse (2–4 rounds) to remain practical for batch remote-sensing tiles |
