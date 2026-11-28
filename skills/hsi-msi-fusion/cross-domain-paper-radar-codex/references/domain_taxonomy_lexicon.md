# 7 High-Resonance Expanded Domains & Query Lexicon

Adapted from multi-domain AI paper taxonomies (inspired by `M0rtzz/paper-notes` covering CV, VLM, Agent, Diffusion, Medical AI, Reasoning, and Scientific ML), distilled into **7 expanded domains (`D1–D7`)** with maximum structural resonance for **HSI-MSI Image Fusion (Track A)** and **Agent + HSI-MSI Image Fusion (Track B)**.

---

## D1: Natural Image Low-Level Vision & Inverse Problems
- **Target Track**: Track A
- **Curated Query Clusters**:
  - `all-in-one image restoration`
  - `blind super-resolution`
  - `infrared visible image fusion`
  - `image fusion degradation modeling`
  - `inverse problem image restoration`
- **HSI-MSI Resonance**: Blind PSF/noise conditioning, cross-modality complementary feature fusion, high-frequency spatial detail injection.

## D2: Medical Image Fusion, Registration & Physics Reconstruction
- **Target Track**: Track A & Track B (High-Value Goldmines M1/M2/M3)
- **Curated Query Clusters**:
  - `medical image fusion`
  - `deformable registration multimodal fusion`
  - `physics-informed MRI reconstruction`
  - `sparse-view CT reconstruction`
  - `3D volumetric medical reconstruction`
- **HSI-MSI Resonance**: Functional-structural fusion (MRI-PET $\leftrightarrow$ HSI-MSI), non-rigid spatial alignment (M1), forward-operator mismatch (M2), anisotropic high-D volumetric modeling.

## D3: Generative Priors & Few-Step Sampling (Diffusion / Flow / Consistency)
- **Target Track**: Track A
- **Curated Query Clusters**:
  - `flow matching inverse problem`
  - `rectified flow image restoration`
  - `diffusion posterior sampling inverse`
  - `zero-shot diffusion restoration`
  - `bridge diffusion image restoration`
- **HSI-MSI Resonance**: 1–4 step generative fusion transporting upsampled LR-HSI toward HR-HSI with measurement-space projection to prevent spectral hallucination.

## D4: Vision Agents, Tool-Use & Multi-Step Self-Reflection
- **Target Track**: **Track B Core**
- **Curated Query Clusters**:
  - `agentic image restoration`
  - `vision agent tool use`
  - `multimodal agent visual reasoning`
  - `self-correcting vision agent`
  - `test-time scaling visual reasoning`
- **HSI-MSI Resonance**: Degradation diagnosis, specialist solver/unfolding routing, non-RGB physical-probe reflection, and monotonic rollback under compound unknown degradations.

## D5: Efficient Long-Range Representation, Continuous Fields & Frequency Operators
- **Target Track**: Track A
- **Curated Query Clusters**:
  - `vision mamba image restoration`
  - `state space model super-resolution`
  - `implicit neural representation super-resolution`
  - `arbitrary-scale super-resolution`
  - `frequency decomposition image restoration`
- **HSI-MSI Resonance**: $O(N)$ modeling across 100–224 spectral bands without OOM, continuous arbitrary-scale / arbitrary-wavelength cross-sensor fusion, dual spatial-spectral frequency decoupling.

## D6: Test-Time Adaptation, Zero-Shot Generalization & Uncertainty Quantification
- **Target Track**: Track A & Track B
- **Curated Query Clusters**:
  - `test-time adaptation image restoration`
  - `test-time training vision`
  - `zero-shot blind image restoration`
  - `uncertainty quantification image reconstruction`
  - `hallucination detection medical imaging`
- **HSI-MSI Resonance**: Closing the Wald's protocol vs. full-resolution gap without GT; pixel/band-wise uncertainty triggering stricter physical projection or Agent reflection.

## D7: Scientific Computational Imaging & Multi-Sensor Physical Fusion
- **Target Track**: Track A (High Information-Advantage Frontier)
- **Curated Query Clusters**:
  - `computational imaging inverse problem`
  - `snapshot compressive imaging reconstruction`
  - `physics-informed neural network imaging`
  - `event camera image fusion`
  - `multi-sensor alignment fusion`
- **HSI-MSI Resonance**: Directly shares physical forward-model unfolding, coded/spectral sensing constraints, and asymmetric multi-sensor fusion with HSI-MSI, while remaining far less crowded than RGB restoration.
