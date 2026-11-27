# 5-Dimension / 25-Point Radar Triage Rubric

Score every candidate paper **only after reading its actual retrieved abstract** (never from titles alone). A paper must score **$\ge 18 / 25$** to enter the final Top 5–10 shortlist.

| Dimension | 0–1 (Weak / Drop) | 2–3 (Moderate) | 4–5 (Strong / Priority) |
| :--- | :--- | :--- | :--- |
| **1. Pioneering / Overlooked Flaw Signal** | Incremental tweaking of an existing backbone or buzzword-heavy title with no real insight. | Clean engineering improvement or solid combination of known ideas. | Explicitly uncovers an overlooked mathematical/physical failure mode or introduces a genuinely first-of-its-kind mechanism. |
| **2. Physical / Algorithmic Isomorphism** | Tightly coupled to RGB semantics (e.g., face/text/class labels) with weak link to HSI-MSI. | General visual architecture that could be adapted with moderate engineering. | Deep structural isomorphism with HSI-MSI physics ($\mathbf{Y}=\mathbf{X}\mathbf{B}\mathbf{D}, \mathbf{Z}=\mathbf{R}\mathbf{X}$, $C \gg 3$ spectra) or Agent closed-loop control. |
| **3. Cross-Domain Information Advantage** | Already heavily crowded in HSI-MSI/pansharpening (e.g., vanilla Attention/Swin/DDPM). | Broad family exists in HSI-MSI, but a clear sub-problem remains open. | High information asymmetry (e.g., Medical M1–M3, Scientific Imaging D7, Physics-Probe Agent D4) rarely touched by remote-sensing fusion yet. |
| **4. Verifiability & Reproducibility** | Missing abstract, vague claims, or prohibitive compute (e.g., requires 8x80GB cluster). | Clear abstract and plausible adaptation, though code is not yet confirmed. | Verified abstract + clear mathematical/algorithmic core + feasible on 1x24GB–48GB GPU (bonus if official code link exists). |
| **5. Recency & Venue Impact** | Older edge of the 24-month window with low signal. | Solid recent publication in one of the 9 venues. | Published within the last 12 months in the 9 venues with strong citation velocity or Oral/Spotlight/Highlight signal. |

## Action Priority Tiers
- **`P0 (Immediate Deep-Dive)`**: Total score $\ge 21/25$ — Immediately download PDF/code and feed into `$hsi-msi-idea-scout-codex`.
- **`P1 (Watchlist)`**: Total score $18\text{–}20/25$ — Worth keeping in backlog or skimming if P0 hits a snag.
- **`Drop (< 18)`**: Exclude from final shortlist (optionally count in retrieval stats).
