# Target Venue Taxonomy & Rolling Window Rules

This skill strictly restricts source papers to **9 top-tier computer vision, machine learning, and image processing venues** published or accepted within the **rolling 24-month window** relative to the current date.

## Strict 9-Venue Whitelist

| Short Name | Full Official Name | Type | Typical OpenAlex / DBLP / S2 Aliases |
| :--- | :--- | :--- | :--- |
| **CVPR** | IEEE/CVF Conference on Computer Vision and Pattern Recognition | Conference | `CVPR`, `Computer Vision and Pattern Recognition` |
| **ICCV** | IEEE/CVF International Conference on Computer Vision | Conference | `ICCV`, `International Conference on Computer Vision` |
| **ECCV** | European Conference on Computer Vision | Conference | `ECCV`, `European Conference on Computer Vision` |
| **NeurIPS** | Advances in Neural Information Processing Systems | Conference | `NeurIPS`, `Neural Information Processing Systems` |
| **ICLR** | International Conference on Learning Representations | Conference | `ICLR`, `International Conference on Learning Representations` |
| **AAAI** | AAAI Conference on Artificial Intelligence | Conference | `AAAI`, `AAAI Conference on Artificial Intelligence` |
| **TPAMI** | IEEE Transactions on Pattern Analysis and Machine Intelligence | Journal | `IEEE Transactions on Pattern Analysis and Machine Intelligence`, `TPAMI`, `PAMI` |
| **IJCV** | International Journal of Computer Vision | Journal | `International Journal of Computer Vision`, `IJCV` |
| **TIP** | IEEE Transactions on Image Processing | Journal | `IEEE Transactions on Image Processing`, `TIP` |

## Rolling 2-Year Window Calculation

- Anchor to the current system date (`YYYY-MM-DD`).
- Include papers whose publication date or official acceptance year falls within `[today - 24 months, today]`.
- Note on biennial conferences:
  - **ICCV** is held in odd years (e.g., 2025).
  - **ECCV** is held in even years (e.g., 2024, 2026).
  - Together, any rolling 24-month window covers at least one ICCV and one ECCV edition.

## Source Domain Filtering Keywords

### Natural Image Sub-Domains (High Transfer Value)
- Low-level vision & inverse problems: `image restoration`, `super-resolution`, `deblurring`, `denoising`, `all-in-one restoration`, `blind restoration`, `image fusion`, `infrared visible fusion`, `multi-exposure fusion`, `multi-focus fusion`.
- Generative & representation priors: `diffusion inverse problem`, `flow matching`, `rectified flow`, `state space model`, `mamba vision`, `implicit neural representation`, `gaussian splatting 2d`, `test-time adaptation`.
- Agentic vision: `agentic image restoration`, `vision agent`, `multimodal agent`, `tool-using vision`, `self-correcting vision`, `reasoning restoration`.

### Medical Image Sub-Domains (High Transfer Value)
- Multimodal & high-dimensional reconstruction: `medical image fusion`, `MRI reconstruction`, `CT reconstruction`, `PET-MRI fusion`, `multimodal registration`, `3D volumetric`, `physics-informed reconstruction`, `uncertainty quantification`, `zero-shot medical reconstruction`, `foundation model medical imaging`.

## Verification Rules for Venue Membership

1. A pure `arXiv` preprint **without** confirmed acceptance to one of the 9 venues does **not** qualify as a primary source paper.
2. If OpenAlex lists an arXiv version alongside a published venue version, verify the venue string or comment field (e.g., `Accepted at CVPR 2025`, `Published in IEEE TIP 2025`) before admitting it.
3. Prefer papers with verifiable identifiers: DOI, OpenAlex ID, Semantic Scholar ID, OpenReview URL, CVF Open Access URL, or IEEE Xplore URL.
