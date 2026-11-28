---
name: hsi-agent-paper-reader-codex
description: >-
  【论文精读与台账】Use this skill when the user wants to perform structured deep reading of an HSI-MSI image
  fusion paper, a Vision Agent / Agentic Restoration paper, or an Agent+HSI-MSI paper, extract
  standardized technical fields (degradation model, spectral handling, agent state/action/tools,
  datasets, metrics, limitations), and persistently log the paper into a local literature ledger
  (CSV + Markdown) for fast Related Work writing and baseline comparison.
---

# HSI-MSI & Vision Agent Paper Reader (Codex)

This skill turns Codex into a disciplined research note-taker for graduate students working on **Agent + HSI-MSI image fusion**. Instead of writing ad-hoc summaries that are forgotten two weeks later, every paper is dissected into a strict schema and appended to a persistent local **Literature Ledger**.

## Progressive Disclosure Map

- Standardized extraction fields & limitation audit rules: [references/extraction_schema.md](./references/extraction_schema.md)
- Output note format anchor: [examples/sample_paper_note.md](./examples/sample_paper_note.md)
- Deterministic ledger manager (append, deduplicate, search, export Markdown): [scripts/append_ledger.py](./scripts/append_ledger.py)

## Codex Execution Notes

1. Always resolve script paths relative to `<SKILL_DIR>`: invoke `<SKILL_DIR>/scripts/append_ledger.py`.
2. Label every reading note with **`[Full-Text Verified]`** (full PDF/Markdown/LaTeX/code read) or **`[Abstract-Level Triage]`** (only title/abstract available). Never fabricate metrics, datasets, or architectural details not present in the source.
3. Default ledger directory: `./literature_ledger/` inside the user's current workspace (unless the user specifies another path).

---

## Mandatory 4-Phase Reading Workflow

### Phase 0: Classify Paper Category & Evidence Depth
Read the provided paper (PDF, text, Markdown, or URL content) and classify it into one of three categories:
- **`HSI-MSI`**: Hyperspectral-multispectral image fusion, pansharpening, spectral super-resolution.
- **`Vision-Agent`**: Agentic image restoration, tool-use vision agents, multimodal planning/reflection.
- **`Agent+HSI-MSI`**: Direct intersection of agentic workflows and hyperspectral/remote-sensing fusion.

### Phase 1: Structured Field Extraction
Read [references/extraction_schema.md](./references/extraction_schema.md) and extract all applicable fields verbatim from the source:
- **Bibliographic Core**: Title, First Author et al., Year, Venue, Code URL (or `N/A`).
- **For `HSI-MSI` / `Agent+HSI-MSI`**:
  - Degradation assumption: Known vs. Blind PSF ($\mathbf{B}$) / SRF ($\mathbf{R}$), aligned vs. misregistered.
  - Spectral handling: Band dimension strategy (subspace/PCA, 3D conv, spectral attention, Mamba, INR, etc.).
  - Paradigm: Deep Unfolding / Transformer / Diffusion / Flow / CNN / Hybrid.
  - Training & Eval Protocol: Wald's reduced-resolution vs. full-resolution unsupervised/TTA.
  - Datasets & Scales: e.g., CAVE ($\times 8$), Chikusei ($\times 8$), PaviaU, WorldView-3.
  - Key Metrics Reported: PSNR, SAM, ERGAS, SSIM, Q2n / QNR (only record exact numbers read from the paper).
- **For `Vision-Agent` / `Agent+HSI-MSI`**:
  - Observation State: What signals the agent observes (RGB VLM, degradation estimator, numeric residuals, spectral probes).
  - Action / Tool Space: Which specialist models or operators the agent invokes.
  - Planning & Reflection Loop: Single-turn router vs. multi-step reflection/rollback, max turns, latency/cost.

### Phase 2: Critical Limitation & Reusable-Asset Extraction
Never end a note with "great paper." Always extract:
1. **Fatal / Hidden Assumptions**: What breaks in real-world full-resolution or cross-sensor HSI-MSI?
2. **Comparison Value**: Should this paper be a **Baseline to beat**, a **Tool to wrap for our Agent**, or a **Related Work citation**?
3. **One-Sentence Related-Work Blurb**: A concise, objective 1–2 sentence academic summary ready to paste into a Related Work section.

### Phase 3: Persist to Literature Ledger & Deliver Note
1. Present the structured reading card following [examples/sample_paper_note.md](./examples/sample_paper_note.md).
2. Run `scripts/append_ledger.py` to append/update the paper in `literature_ledger/ledger.csv` and regenerate `literature_ledger/ledger.md`:

```bash
python <SKILL_DIR>/scripts/append_ledger.py \
  --ledger-dir ./literature_ledger \
  --title "<Exact Paper Title>" \
  --authors "<First Author et al.>" \
  --year 2025 \
  --venue "CVPR" \
  --category "HSI-MSI" \
  --degradation "Blind PSF/SRF" \
  --paradigm "Deep Unfolding + Flow" \
  --agent-loop "N/A" \
  --datasets "CAVE, Chikusei, WorldView-3" \
  --metrics "PSNR/SAM/ERGAS" \
  --limitation "<Core flaw or assumption>" \
  --role "Baseline" \
  --code-url "<GitHub URL or N/A>" \
  --evidence-depth "Full-Text Verified"
```
