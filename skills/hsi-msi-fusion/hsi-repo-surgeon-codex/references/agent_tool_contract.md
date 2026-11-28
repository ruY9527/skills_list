# Standardized HSI-MSI Agent Tool Contract

When wrapping any open-source fusion solver, registration aligner, denoiser, or PSF/SRF estimator for **Track B (Agent + HSI-MSI Image Fusion)**, enforce this uniform interface so the Agent Planner can orchestrate heterogeneous models cleanly.

## 1. Unified Python Interface

```python
from dataclasses import dataclass, field
from typing import Any
import numpy as np

@dataclass
class ToolResult:
    hr_hsi: np.ndarray              # [H, W, C], float32 in [0, 1]
    spatial_residual: float         # ||H(hr_hsi) - lr_hsi||_F / ||lr_hsi||_F
    spectral_residual: float        # ||R(hr_hsi) - hr_msi||_F / ||hr_msi||_F
    elapsed_sec: float              # Wall-clock latency for budget tracking
    status: str = "ok"              # "ok" | "oom_fallback" | "error"
    diagnostics: dict[str, Any] = field(default_factory=dict)

class BaseHSIAgentTool:
    name: str                       # Unique tool identifier, e.g. "blind_unfolding_solver"
    capability: str                 # One-line description for the Agent planner
    supported_scales: tuple[int, ...] = (4, 8, 16)

    def run(
        self,
        lr_hsi: np.ndarray,         # [h, w, C], float32
        hr_msi: np.ndarray,         # [H, W, c], float32
        psf: np.ndarray | None = None,
        srf: np.ndarray | None = None,
        params: dict[str, Any] | None = None,
    ) -> ToolResult:
        raise NotImplementedError
```

## 2. Mandatory Engineering Rules for Agent Tools
1. **Deterministic Physical Feedback**: Every tool MUST return `spatial_residual` and `spectral_residual` (or alignment score / PSF error) so the Agent reflects on quantitative physics rather than RGB previews.
2. **VRAM Hygiene**: Wrap inference in `with torch.no_grad():` and release intermediate tensors (`torch.cuda.empty_cache()` on exception) so multi-tool chains do not OOM on 24GB GPUs.
3. **Tile-Safe Fallback**: For large remote-sensing tiles ($> 512 \times 512$), support overlapping patch tiling (`tile_size`, `overlap`) instead of crashing with OOM.
4. **No Silent NaN/Inf**: Explicitly check `np.isfinite(hr_hsi).all()` and clamp or return `status="error"` if divergence occurs, enabling the Agent to roll back.
