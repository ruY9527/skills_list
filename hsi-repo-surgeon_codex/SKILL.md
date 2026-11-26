---
name: hsi-repo-surgeon_codex
description: >-
  Use this skill when the user wants to dissect an open-source PyTorch computer vision or
  HSI-MSI fusion repository, trace tensor shapes through the forward pass, map paper equations
  to exact code lines, audit GPU memory and spectral-dimension compatibility, or wrap an
  existing fusion/registration/PSF-estimation model into a standardized Agent Tool.
---

# HSI-MSI Repo Surgeon & Agent Tool Wrapper (Codex)

This skill helps graduate students turn complex open-source research repos into **clear tensor-flow maps**, **drop-in baseline modules**, or **standardized callable tools for an HSI-MSI Fusion Agent**.

## Progressive Disclosure Map

- Standard Agent Tool interface contract for HSI-MSI solvers: [references/agent_tool_contract.md](./references/agent_tool_contract.md)
- Tensor shape, VRAM & spectral-dimension audit checklist: [references/tensor_audit_checklist.md](./references/tensor_audit_checklist.md)
- Fast AST-based PyTorch repository scanner (`nn.Module` & `forward` locator): [scripts/scan_repo_structure.py](./scripts/scan_repo_structure.py)

## Codex Execution Notes

1. Always resolve `<SKILL_DIR>/scripts/scan_repo_structure.py` relative to this skill directory.
2. Never guess class names, line numbers, or tensor shapes—read the actual files returned by the scanner before writing the report or wrapper code.

---

## Mandatory 4-Phase Repo Dissection Workflow

### Phase 0: Automated Repo Inventory
Run `scripts/scan_repo_structure.py` on the target repository directory to locate all `nn.Module` classes, `forward` signatures, loss definitions, and entry-point scripts without wasting context reading boilerplate files:

```bash
python <SKILL_DIR>/scripts/scan_repo_structure.py \
  --repo "<path_to_repo>" \
  --output repo_map.json
```

### Phase 1: Core Forward Trace & Equation-to-Code Mapping
Inspect the core model files identified in Phase 0 and produce:
1. **End-to-End Tensor Shape Table**: Trace exact shapes from input `(LR_HSI: [B, C, h, w], HR_MSI: [B, c, H, W])` (or RGB `[B, 3, H, W]`) through every major stage to output `[B, C, H, W]`.
2. **Paper-to-Code Anchor Map**: Map each key paper module/equation to exact `file.py:line_start-line_end` and `ClassName.method`.

### Phase 2: HSI-MSI Compatibility & VRAM Audit
Read [references/tensor_audit_checklist.md](./references/tensor_audit_checklist.md) and check:
- Hardcoded `in_channels=3` or `out_channels=3` assumptions.
- Quadratic $O((HW)^2)$ or $O((HWC)^2)$ attention/3D-conv bottlenecks that will OOM on $C=128\text{–}224$ bands.
- Hardcoded scale factors ($\times 4 / \times 8$) or fixed spatial patch sizes.
- Missing physical data-consistency hooks ($\mathbf{Y}=\mathbf{X}\mathbf{B}\mathbf{D}, \mathbf{Z}=\mathbf{R}\mathbf{X}$).

### Phase 3: Integration or Agent-Tool Wrapping Blueprint
Deliver one of two concrete artifacts depending on the user's goal:
- **Goal A (Module Extraction into Baseline)**: Minimal self-contained PyTorch module snippet + exact tensor adapter (`C -> d -> C`) + dependency/VRAM delta.
- **Goal B (Wrap as HSI-MSI Agent Tool)**: Read [references/agent_tool_contract.md](./references/agent_tool_contract.md) and generate a clean wrapper class exposing `run(lr_hsi, hr_msi, meta) -> ToolResult` (including fused tensor, spatial/spectral re-projection residuals, runtime, and GPU memory cleanup).
