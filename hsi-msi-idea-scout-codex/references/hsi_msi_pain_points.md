# HSI-MSI Image Fusion & Agent+HSI-MSI Pain Point Atlas

Use this atlas in **Phase 2** and **Phase 4** to ensure every transferred idea addresses a real, high-impact scientific bottleneck rather than a superficial architectural tweak.

---

## Physical Observation Model (Reference Anchor)

Let the target High-Resolution Hyperspectral Image (HR-HSI) be $\mathbf{X} \in \mathbb{R}^{C \times HW}$ (where $C$ is typically $31\text{–}224$ spectral bands):

1. **Low-Resolution HSI (LR-HSI)**:
   $$\mathbf{Y} = \mathbf{X}\mathbf{B}\mathbf{D} + \mathbf{N}_h \in \mathbb{R}^{C \times hw}$$
   where $\mathbf{B}$ is the spatial point spread function (PSF / blur kernel) and $\mathbf{D}$ is spatial downsampling (often $\times 4, \times 8, \times 16, \times 32$).
2. **High-Resolution MSI (HR-MSI)**:
   $$\mathbf{Z} = \mathbf{R}\mathbf{X} + \mathbf{N}_m \in \mathbb{R}^{c \times HW}$$
   where $\mathbf{R} \in \mathbb{R}^{c \times C}$ ($c \ll C$, e.g., $c=3, 4, 8$) is the spectral response function (SRF).

---

## Track A: Core Pain Points in HSI-MSI Image Fusion

### A1. Blind & Non-Uniform Degradation (Unknown PSF / SRF / Misregistration)
- Most supervised networks assume known, fixed, spatially uniform Gaussian PSF and fixed SRF.
- In real remote sensing / multi-camera setups, PSF varies spatially, SRF shifts across sensors, and LR-HSI and HR-MSI suffer from sub-pixel or non-rigid **spatial misregistration**.

### A2. Extreme Spatial-Spectral Trade-Off & Spectral Distortion (SAM Collapse)
- Boosting high-frequency spatial sharpness (PSNR/SSIM) often injects MSI-dominated textures that corrupt subtle spectral absorption valleys, degrading **SAM** (Spectral Angle Mapper) and downstream material unmixing/classification.
- Existing 2D spatial modules treat $C$ channels as generic feature maps and ignore **inter-band physical continuity and low-rank spectral subspaces**.

### A3. High-Dimensional Compute & Memory Bottleneck
- Applying 3D attention, full diffusion trajectories, or large vision transformers directly to $H \times W \times 200$ tensors causes prohibitive memory/latency overhead.
- Conversely, compressing bands naively via PCA or 1x1 conv loses rare/small-target spectral signatures.

### A4. Zero-Shot Cross-Sensor & Cross-Scale Generalization
- Models trained on CAVE ($\times 8$, 31 bands) collapse on Chikusei (128 bands), WorldView-3 (8-band MSI), or unseen scale ratios ($\times 16$, $\times 32$, arbitrary non-integer scales).
- Paired real HR-HSI ground truth is fundamentally unavailable at full resolution (Wald's protocol mismatch between reduced-resolution training and full-resolution inference).

### A5. Generative Hallucination vs. Physical Consistency
- Diffusion / flow models produce visually crisp textures but hallucinate physically impossible spectral curves that violate $\mathbf{Y} = \mathbf{X}\mathbf{B}\mathbf{D}$ and $\mathbf{Z} = \mathbf{R}\mathbf{X}$.

---

## Track B: Core Pain Points in Agent + HSI-MSI Image Fusion

### B1. Static Pipelines vs. Scene- & Degradation-Adaptive Decision Making
- Real HSI-MSI pairs vary drastically in noise level, cloud/haze contamination, misregistration severity, scale factor, and scene heterogeneity (urban edges vs. smooth vegetation).
- A single fixed feed-forward network cannot adapt its restoration strategy per scene or per local region.

### B2. Lack of Closed-Loop Spectral-Spatial Self-Diagnosis & Reflection
- Existing vision agents mainly judge RGB perceptual quality (using VLMs on 3-channel images), which **cannot see spectral distortion** across 100+ bands.
- An HSI-MSI agent needs **non-RGB physical/spectral probes** (e.g., re-projection residual $\|\hat{\mathbf{X}}\mathbf{B}\mathbf{D} - \mathbf{Y}\|$, $\|\mathbf{R}\hat{\mathbf{X}} - \mathbf{Z}\|$, local spectral smoothness, SAM proxy maps, registration correlation maps) to diagnose *what* failed and *where*.

### B3. Dynamic Tool / Solver / Unfolding Orchestration
- Combining classical physical priors (coupled tensor/matrix factorization, subspace projection), deep unfolding blocks, registration aligners, and generative refiners requires intelligent routing: choosing **which tool, in what order, and with what hyperparameters** under a compute budget.

### B4. Test-Time Adaptation (TTA) & Full-Resolution Self-Supervised Alignment
- At full resolution (no GT), an agent can iteratively run self-supervised adaptation, verify physical consistency after each step, detect overfitting or spectral drift, and roll back or switch solvers.

### B5. Latency, Token Cost & Determinism
- Naive LLM-in-the-loop per-pixel or per-patch calls are too slow and expensive.
- Practical Agent + HSI-MSI designs must separate **lightweight symbolic/metric perception** from **sparse high-level planning** (e.g., coarse scene diagnosis + few-step tool execution).
