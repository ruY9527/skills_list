# Cross-Domain Top-Venue Paper Radar Brief (Format Template)

> **Note**: Replace all bracketed placeholders with **verified papers** returned by `scripts/radar_scan.py`. Never invent citations or score papers with missing abstracts as `P0`.

---

## 1. Radar Mission Summary

- **Sweep Date**: `<YYYY-MM-DD>`
- **Rolling 24-Month Window**: `<YYYY-MM>` to `<YYYY-MM>`
- **Scanned Domains**: `<e.g., D2 (Medical Fusion/Physics) + D4 (Vision Agents)>`
- **Target Venues (Strict 9)**: `IJCV, TIP, CVPR, NeurIPS, AAAI, ICLR, ICCV, ECCV, TPAMI`
- **Ledger Deduplication**: `<Skipped N already-read papers from ./literature_ledger/ledger.csv>`
- **Funnel Stats**: Raw venue hits `<X>` -> Verified-abstract candidates `<Y>` -> Final Shortlist (`>= 18/25`) `<K>`

---

## 2. Top Shortlisted Candidates ("5-Minute Core Insight" Cards)

### [#1] `<Exact Verified Paper Title>` — `P0 (Immediate Deep-Dive)`
- **Metadata**: `<First Author et al.>` | **`<Venue YYYY>`** | Domain: `<D2 / D4>` | Score: **`<23/25>`** (`Pioneering 5 + Iso 5 + InfoGap 5 + Repro 4 + Recency 4`)
- **Links & Download**: Landing: `<DOI / CVF / OpenReview URL>` | **PDF**: `<Direct OA PDF URL or 'Institutional Access Required'>` (`<oa_status>`) | Code: `<GitHub URL or Not Listed>`
- **5-Minute Core Summary**:
  1. **Overlooked Problem**: `<What exact flaw in natural/medical/agent vision did it expose?>`
  2. **Core Mechanism**: `<The transferable mathematical operator, prior, or agentic loop.>`
  3. **Key Takeaway**: `<Main verified result from the abstract.>`
- **Transfer Hook for Your Research**:
  - **Target Track**: `Track A (HSI-MSI Fusion)` / `Track B (Agent + HSI-MSI Fusion)`
  - **Concrete Resonance**: `<1–2 crisp sentences explaining why this could unlock a major HSI-MSI pain point (e.g., blind PSF/SRF, non-rigid registration, or physics-probe Agent reflection).>`

---

### [#2] `<Exact Verified Paper Title>` — `P1 (Watchlist)`
- **Metadata**: `<...>` | **`<Venue YYYY>`** | Domain: `<D6>` | Score: **`<19/25>`**
- **Verifiable Link**: `<...>`
- **5-Minute Core Summary**: `<3 crisp sentences>`
- **Transfer Hook for Your Research**: `<1–2 sentences>`

---

## 3. Quick Comparison Matrix

| Rank | Priority | Venue & Year | Domain | Track | Score (/25) | Title | Link |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `P0` | `<CVPR 2025>` | `D2` | Track A | 23 | `<Title #1>` | [Link](<URL>) |
| 2 | `P1` | `<ICLR 2026>` | `D4` | Track B | 19 | `<Title #2>` | [Link](<URL>) |

---

## 4. One-Click Handoff Prompts for `$hsi-msi-idea-scout-codex`

After downloading the PDF (and optional repo) for the top `P0` paper(s), paste this directly into Codex:

```text
请严格启用 `$hsi-msi-idea-scout-codex` 对我从雷达简报中选出的 P0 论文进行单篇深度跨领域迁移分析：
- 论文标题与出处：<Title #1> (<Venue YYYY>)
- 本地 PDF 路径：<下载后填入本地路径>
- 目标轨道：<Track A / Track B / 双轨>
- 请按完整 6 阶段流程执行，对拆解出的每个子创新点运行 scripts/check_hsi_gap.py（含同义词扩展）做 Tier 1/2/3 反向查新，输出动机诊断小实验与改造蓝图，保存为 transfer_report_1.md。
```

## 5. Appendix: Promising DBLP Hits Missing Abstracts (Needs Manual Check)
- `<Title>` (`<Venue YYYY>`) — [Link](<URL>) *(Abstract not indexed in OpenAlex yet; inspect manually if title looks highly relevant.)*
