---
name: hsi-agent-reviewer_codex
description: >-
  Use this skill when the user wants a rigorous pre-submission peer-review simulation or
  rebuttal preparation for a paper, method draft, or research proposal on HSI-MSI image fusion
  or Agent + HSI-MSI image fusion. Simulates 3 strict specialist reviewers (Remote Sensing
  Physics, Top-Venue CV Methodology, and Agent Systems Efficiency) to uncover fatal flaws
  and missing ablations before submission.
---

# HSI-MSI & Agent Triple-Reviewer Simulator (Codex)

Cross-disciplinary **Agent + HSI-MSI** papers frequently get caught between two communities: CV reviewers critique incremental novelty, remote-sensing reviewers critique physical assumptions and full-resolution validation, and systems/agent reviewers critique LLM necessity and latency.

This skill simulates **3 strict specialist reviewers** before you submit (or during rebuttal) so you catch fatal weaknesses early.

## Progressive Disclosure Map

- 3 specialist reviewer personas, rubrics & rejection triggers: [references/reviewer_personas.md](./references/reviewer_personas.md)
- Evidence-based rebuttal & anti-overstatement playbook: [references/rebuttal_playbook.md](./references/rebuttal_playbook.md)

---

## Mandatory 4-Phase Review Workflow

### Phase 0: Lock Submission Target & Draft Scope
Read the user's manuscript draft, method section, experiment tables, or rebuttal letters. Confirm target venue (e.g., `CVPR`, `NeurIPS`, `TIP`, `TPAMI`, `TGRS`) and whether the mode is **Pre-Submission Stress Test** or **Rebuttal Drafting**.

### Phase 1: Independent 3-Persona Harsh Review
Read [references/reviewer_personas.md](./references/reviewer_personas.md) and write **3 separate, non-overlapping reviews** (each with Summary, Major Weaknesses, Minor Issues, Missing Experiments, and Rating):
1. **Reviewer 1 — Remote Sensing & Inverse-Problem Physicist**: Audits PSF/SRF assumptions, spectral fidelity (SAM/ERGAS), misregistration, and Wald's protocol vs. real full-resolution (WorldView/GaoFen/PRISMA) generalization.
2. **Reviewer 2 — Top-Venue CV Methodology Reviewer**: Audits novelty vs. A+B stitching, motivation diagnostic evidence, fairness of baseline comparisons, and ablation completeness.
3. **Reviewer 3 — Agent & Systems Efficiency Reviewer**: Enforces the **3 mandatory Agent questions** (necessity over MoE/Router, non-RGB spectral perception, and tile-level latency/token/determinism budget).

### Phase 2: Meta-Review & Fatal-Flaw Triage
Synthesize a Meta-Review ranking all issues into:
- **P0 (Reject-Risk Blockers)**: Must be fixed with new experiments or method revisions before submission.
- **P1 (Borderline Swing Points)**: High-ROI ablations or clarifications that flip Borderline to Accept.
- **P2 (Polish / Presentation)**: Notation, figure clarity, and claim toning.

### Phase 3: Concrete Action Plan (or Point-by-Point Rebuttal)
Read [references/rebuttal_playbook.md](./references/rebuttal_playbook.md) and deliver:
- **Pre-Submission Mode**: A prioritized 1–2 week experiment & revision checklist with exact tables/figures to add.
- **Rebuttal Mode**: Concise, polite, strictly evidence-backed point-by-point responses (never promising unrun experiments as completed, never overstating claims).
