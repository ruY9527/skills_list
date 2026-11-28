# Anti-Patterns & Academic Audit Checklist

Run this audit in **Phase 5** before finalizing any report. Any candidate idea that violates a red line must be revised with real evidence or removed.

## Red Line 1: Zero Citation Hallucination
- **Forbidden**: Inventing paper titles, guessing authors/venues, citing a paper from memory without a verified URL/DOI/ID returned by `scripts/fetch_top_venues.py` or verified academic search, or claiming a paper is an "Oral/Spotlight" without evidence.
- **Required**: Every source paper must carry a real identifier (DOI, OpenAlex ID, arXiv ID with confirmed venue acceptance, CVF/OpenReview/IEEE URL).

## Red Line 2: Strict Venue & Rolling 24-Month Compliance
- **Forbidden**: Passing off 2022–2023 papers as "recent 2 years", or smuggling unrefereed arXiv preprints / non-target venues into the 9-venue list (`IJCV, TIP, CVPR, NeurIPS, AAAI, ICLR, ICCV, ECCV, TPAMI`).
- **Required**: Explicitly state the publication/acceptance year and exact venue for every source paper.

## Red Line 3: No "A + B Stitching" (Superficial Module Swapping Without Diagnostic Motivation)
- **Forbidden**: Proposals that merely say "replace Conv/Transformer in an HSI-MSI network with Module X from CVPR 2025 to improve performance," without proving that HSI-MSI actually suffers from the source paper's failure mode.
- **Required**: Articulate (a) **what overlooked failure mechanism** in HSI-MSI this solves, (b) a **Motivation Diagnostic Experiment** that can empirically expose that flaw on HSI-MSI data before proposing the fix, (c) **what fails if naively copied** from RGB/medical to $C$-band HSI-MSI, and (d) **the exact physics-aware adaptation** required.

## Red Line 4: No Unverified "Nobody Has Done This" Claims
- **Forbidden**: Asserting "no one in HSI-MSI has explored X" without running `scripts/check_hsi_gap.py` (or equivalent systematic literature search).
- **Required**: Report the exact reverse-search queries, the closest existing HSI-MSI papers found (if any), and an honest `Tier 1` vs `Tier 2` verdict.

## Red Line 5: No Empty LLM-Wrapper "Agent" Proposals (Must Pass the 3 Reviewer Questions)
- **Forbidden**: Calling a pipeline "Agent + HSI-MSI" when it is merely an LLM chatbot calling a single fusion script, inspecting RGB pseudo-color previews, or failing to justify why a lightweight MoE/Router cannot replace it.
- **Required**: Every Track B proposal must explicitly pass all 3 mandatory reviewer questions: (1) **Necessity over MoE/Router** (long-tail compound degradation + non-fixed-step test-time rollback/reflection), (2) **Non-RGB Spectral Perception** (deterministic physical/spectral probe tools rather than RGB-only VLM eyes), and (3) **Bounded Compute/Latency** (macro tile-level sparse planning in $\le 3\text{–}4$ turns + micro differentiable execution).

## Red Line 6: No Overstatement (Mandatory Reviewer Critique)
- **Forbidden**: Presenting an idea as flawless or guaranteeing SOTA gains.
- **Required**: Every idea card must include **1–2 realistic reviewer objections** (e.g., compute overhead on 200-band HSIs, sensitivity to unknown SRF, Wald's protocol vs. full-resolution gap, agent inference latency) paired with concrete engineering/experimental mitigations.

## Red Line 7: No Abstract-Only Technical Fabrication
- **Forbidden**: Reading only a paper's title and abstract, then inventing detailed internal equations, layer counts, loss weights, or claiming the source paper uses a specific architecture not explicitly stated in the retrieved text.
- **Required**: Tag every proposal with `[Abstract-Level Triage]` (explicitly stating which design details are proposed adaptations vs. verified source mechanisms) until the full PDF/arXiv source or official code has been inspected (`[Full-Text Verified]`).
