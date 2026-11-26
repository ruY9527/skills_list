# My Research Skills

> 个人研究技能库 —— 沉淀、复用与持续迭代我在 **Agent + HSI-MSI 图像融合** 科研中打磨的 Agent Skills。

这里存放我自己在研究与工程中实际使用的 skills。每个 skill 是一个自包含目录：核心指令、使用手册、可执行脚本、参考知识与输出样例放在一起，便于安装到 Codex / Claude / 其他支持 `SKILL.md` 的 Agent 运行时，也便于跨项目共享与版本追溯。

---

## 当前收录（5 个 Skill 构成完整科研闭环）

| 科研阶段 | Skill | 简介 | 手册 | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **1. 精读沉淀** | [`hsi-agent-paper-reader_codex`](./hsi-agent-paper-reader_codex) | 对 HSI-MSI 融合 / Vision Agent / Agent+HSI-MSI 论文按统一 Schema 结构化精读，提取退化假设、Agent 闭环与局限性，并持久化写入本地文献台账（CSV + Markdown） | [USER_USE](./hsi-agent-paper-reader_codex/USER_USE.md) | 可用 |
| **2. 跨域选题** | [`hsi-msi-idea-scout_codex`](./hsi-msi-idea-scout_codex) | 单篇论文跨域迁移分析：把自然图像 / 医学图像 9 大顶会顶刊近 2 年论文的失效机理，经 OpenAlex + arXiv 双通道查新与物理适配，转化为 HSI-MSI（Track A）与 Agent + HSI-MSI（Track B）的可执行研究蓝图 | [USER_USE](./hsi-msi-idea-scout_codex/USER_USE.md) | 可用 |
| **3. 代码解剖** | [`hsi-repo-surgeon_codex`](./hsi-repo-surgeon_codex) | AST 自动扫描 PyTorch 开源仓库，输出端到端张量维度流转表、公式-代码行号对照、128+ 波段显存与光谱兼容性审计，并将现有求解器封装为标准 Agent Tool | [USER_USE](./hsi-repo-surgeon_codex/USER_USE.md) | 可用 |
| **4. 实验诊断** | [`hsi-exp-diagnostician_codex`](./hsi-exp-diagnostician_codex) | 计算 PSNR / SAM / ERGAS / CC 及最差波段与最差像元光谱曲线，诊断空间-光谱权衡与 Agent 反思发散原因，自动输出出版级 SVG 诊断图 | [USER_USE](./hsi-exp-diagnostician_codex/USER_USE.md) | 可用 |
| **5. 审稿攻防** | [`hsi-agent-reviewer_codex`](./hsi-agent-reviewer_codex) | 投稿前模拟 **遥感物理逆问题 / CV 顶会方法论 / Agent 系统效率** 三位严苛审稿人，按 P0/P1/P2 排查拒稿风险与缺失消融，并辅助起草实证型 Rebuttal | [USER_USE](./hsi-agent-reviewer_codex/USER_USE.md) | 可用 |

### 推荐科研闭环串联方式

1. **调研与选题期**：用 `hsi-agent-paper-reader_codex` 持续沉淀领域文献台账 + 用 `hsi-msi-idea-scout_codex` 挖掘跨领域 Tier 1/2 创新点。
2. **复现与实验期**：用 `hsi-repo-surgeon_codex` 拆改开源代码或封装 Agent Tools + 用 `hsi-exp-diagnostician_codex` 定位 SAM 漂移、最差波段和 Agent 轨迹问题并出图。
3. **成文与投稿期**：用 `hsi-agent-reviewer_codex` 在投稿前做三视角压力测试，提前补齐关键消融实验。

---

## 目录结构

```text
skills_list/
├── README.md                              # 本文件：技能库总览
├── .gitignore                             # 排除 Python 缓存等生成物
├── hsi-agent-paper-reader_codex/          # 1. 结构化精读 + 文献台账
│   ├── SKILL.md
│   ├── USER_USE.md
│   ├── scripts/append_ledger.py           # 追加/去重/检索 CSV + Markdown 台账
│   ├── references/extraction_schema.md
│   └── examples/sample_paper_note.md
├── hsi-msi-idea-scout_codex/              # 2. 单篇跨域迁移 + 双通道查新
│   ├── SKILL.md
│   ├── USER_USE.md
│   ├── scripts/
│   │   ├── check_hsi_gap.py               # OpenAlex + arXiv 双通道反向查新
│   │   └── fetch_top_venues.py            # DBLP + OpenAlex 9 大顶会顶刊检索
│   ├── references/
│   │   ├── venue_taxonomy.md
│   │   ├── hsi_msi_pain_points.md
│   │   ├── transfer_bridge_map.md
│   │   ├── my_baseline_profile.md         # [建议填写] 个人 baseline / 显存 / 数据集
│   │   ├── anti_patterns.md
│   │   └── calibration_playbook.md
│   └── examples/sample_idea_report.md
├── hsi-repo-surgeon_codex/                # 3. 开源仓库解剖 + Agent Tool 封装
│   ├── SKILL.md
│   ├── USER_USE.md
│   ├── scripts/scan_repo_structure.py     # AST 扫描 nn.Module 与 forward 入口
│   └── references/
│       ├── agent_tool_contract.md
│       └── tensor_audit_checklist.md
├── hsi-exp-diagnostician_codex/           # 4. 物理指标诊断 + SVG 出图
│   ├── SKILL.md
│   ├── USER_USE.md
│   ├── scripts/compute_hsi_metrics.py     # PSNR/SAM/ERGAS/CC + 诊断 SVG
│   └── references/metric_interpretation_guide.md
└── hsi-agent-reviewer_codex/              # 5. 三视角严苛审稿人模拟 + Rebuttal
    ├── SKILL.md
    ├── USER_USE.md
    └── references/
        ├── reviewer_personas.md
        └── rebuttal_playbook.md
```

---

## 快速开始

### 1. 一键安装全部 Skills 到 Codex（全局，推荐）

**Windows (PowerShell，在 `skills_list/` 目录下执行)：**

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Get-ChildItem -Directory -Filter "*_codex" | ForEach-Object {
    Copy-Item -Recurse -Force $_.FullName (Join-Path "$HOME\.codex\skills" $_.Name)
}
```

**macOS / Linux：**

```bash
mkdir -p ~/.codex/skills
cp -r *_codex ~/.codex/skills/
```

复制完成后重启 Codex 即可自动扫描加载。如果只需安装单个 skill 或项目级安装（`.agents/skills/`），请查看各自目录下的 `USER_USE.md`。

### 2. 首次配置（推荐）

填写 `hsi-msi-idea-scout_codex/references/my_baseline_profile.md`，写入你的主力 baseline、显卡显存、常用数据集与目标投稿会议，后续迁移蓝图会自动对齐这些约束。

### 3. 调用示例

在 Codex 对话中通过 `$<skill_name>` 显式触发，例如：

```text
使用 $hsi-agent-paper-reader_codex 精读论文 D:\papers\xxx.pdf 并入库 ./literature_ledger。
使用 $hsi-msi-idea-scout_codex 分析论文 D:\papers\yyy_cvpr2025.pdf 并运行双通道查新。
使用 $hsi-repo-surgeon_codex 解剖仓库 D:\code\fusion_repo 并封装为 BaseHSIAgentTool。
使用 $hsi-exp-diagnostician_codex 诊断 gt.npy 与 pred.npy 并生成 SVG 误差图。
使用 $hsi-agent-reviewer_codex 对论文初稿 D:\paper\draft.tex 进行三视角审稿。
```

---

## 新增 / 维护 skill

新增一个 skill 时遵循统一约定：

- 一个 skill 一个顶层目录，目录名与 `SKILL.md` frontmatter 中的 `name` 一致。
- `SKILL.md` 必带 YAML frontmatter（`name`、`description`），`description` 写清触发条件。
- 核心指令放 `SKILL.md`；大体积参考资料放 `references/` 按需加载；可执行脚本放 `scripts/`。
- 给人看的安装与用法单独放 `USER_USE.md`。
- 脚本路径一律相对 skill 目录解析，不依赖调用方当前工作目录。
- 生成物（`__pycache__/`、`*.pyc` 等）由 `.gitignore` 排除，不入库。
- 在本文件「当前收录」表格中登记新 skill。

提交前自检：脚本可运行、文档链接有效、无敏感路径与凭证明文。

---

## 说明

本仓库为个人研究用途，内容随研究进展持续演进；不同的 skill 可能面向不同的 Agent 运行时，以各自 `USER_USE.md` 中的说明为准。
