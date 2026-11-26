# My Research Skills

> 个人研究技能库 —— 沉淀、复用与持续迭代我在科研中打磨的 Agent Skills。

这里存放我自己在研究与工程中实际使用的 skills。每个 skill 是一个自包含目录：核心指令、使用手册、可执行脚本、参考知识与输出样例放在一起，便于安装到 Codex / Claude / 其他支持 SKILL.md 的 Agent 运行时，也便于跨项目共享与版本追溯。

---

## 当前收录

| Skill | 简介 | 状态 |
| --- | --- | --- |
| [`hsi-msi-idea-scout_codex`](./hsi-msi-idea-scout_codex) | 单篇论文跨域迁移分析：把自然图像 / 医学图像顶会顶刊论文的创新机理，经反向查新与物理适配，转化为 HSI-MSI 图像融合（Track A）与 Agent + HSI-MSI 融合（Track B）的可执行研究蓝图 | 可用 |

### `hsi-msi-idea-scout_codex`

给定一篇自然图像或医学图像领域的单篇前沿论文（PDF / arXiv / 标题 / 正文 / 官方代码），该 skill 强制 Agent 按严格的 6 阶段科研流程执行：

1. **资格与证据深度核验** —— 9 大顶会顶刊 + 近 24 个月窗口，标注 `[Full-Text Verified]` 或 `[Abstract-Level Triage]`。
2. **失效机理与首创点解构** —— 优先拆出被忽略的失效机理，而非泛泛的模块摘要。
3. **隐性前提审计** —— 找出在 RGB / 医学图像成立、但在高光谱（31–224 波段、未知 PSF/SRF、SAM 约束）下失效的假设。
4. **双通道反向查新** —— OpenAlex（已发表）+ arXiv（预印本）+ 同义词扩展，对每个原子创新点判定 Gap Tier（Tier 1 空白 / Tier 2 盲区 / Tier 3 饱和淘汰）。
5. **精准改造蓝图** —— 面向 Track A / Track B 的动机诊断实验、物理退化观测方程适配、Agent 非 RGB 物理探针闭环、审稿人三连问防御与 MVP 实验。
6. **反模式自检** —— 杜绝文献幻觉、模块缝合与基于摘要编造公式。

详细安装与用法见 [`hsi-msi-idea-scout_codex/USER_USE.md`](./hsi-msi-idea-scout_codex/USER_USE.md)。

---

## 目录结构

```text
skills_list/
├── README.md                          # 本文件：技能库总览
├── .gitignore                         # 排除 Python 缓存等生成物
└── hsi-msi-idea-scout_codex/           # 单个 skill = 一个自包含目录
    ├── SKILL.md                       # [Agent 自动加载] 核心指令与工作流
    ├── USER_USE.md                    # [人读] 安装 / 配置 / 调用手册
    ├── scripts/
    │   ├── check_hsi_gap.py           # 核心：OpenAlex + arXiv 双通道反向查新（零外部依赖）
    │   └── fetch_top_venues.py        # 辅助：DBLP + OpenAlex 顶会顶刊论文检索
    ├── references/
    │   ├── venue_taxonomy.md          # 9 大顶会顶刊白名单与近 24 个月规则
    │   ├── hsi_msi_pain_points.md     # HSI-MSI / Agent+HSI-MSI 痛点图谱（A1–A5, B1–B5）
    │   ├── transfer_bridge_map.md     # 跨域映射词典（含医学图像 M1/M2/M3 金矿）
    │   ├── my_baseline_profile.md     # [建议填写] 个人 baseline / 显存 / 数据集 / 目标会议
    │   ├── anti_patterns.md           # 7 条硬性学术审计红线
    │   └── calibration_playbook.md    # 技能校准与持续进化指南
    └── examples/
        └── sample_idea_report.md      # 标准输出报告格式锚点
```

---

## 快速开始

**1. 安装 skill（全局，以 Codex 为例）**

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force ".\hsi-msi-idea-scout_codex" "$HOME\.codex\skills\hsi-msi-idea-scout_codex"
```

macOS / Linux：

```bash
mkdir -p ~/.codex/skills
cp -r hsi-msi-idea-scout_codex ~/.codex/skills/
```

复制后重启 Agent 即可自动扫描加载。项目级安装（随 Git 共享）等方式见各 skill 的 `USER_USE.md`。

**2. 首次配置（推荐）**

填写 `hsi-msi-idea-scout_codex/references/my_baseline_profile.md`，写入你的 baseline、显存、数据集与目标会议，生成方案会自动对齐这些约束。

**3. 调用**

在 Agent 对话中显式触发，例如：

```text
使用 $hsi-msi-idea-scout_codex 分析本地论文 D:\papers\xxx_cvpr2025.pdf，
对拆解出的每个子创新点运行双通道反向查新，最后保存为 transfer_report.md。
```

更多场景化 Prompt 模板见 [`USER_USE.md`](./hsi-msi-idea-scout_codex/USER_USE.md)。

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
