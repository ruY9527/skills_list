# My Research Skills

> 个人研究技能库 —— 沉淀、复用与持续迭代我在 **Agent + HSI-MSI 图像融合** 科研中打磨的 Agent Skills。

这里存放我自己在研究与工程中实际使用的 skills。每个 skill 是一个自包含目录：核心指令、使用手册、可执行脚本、参考知识与输出样例放在一起，便于安装到 Codex / Claude / 其他支持 `SKILL.md` 的 Agent 运行时，也便于跨项目共享与版本追溯。所有 skill 的 `name` 与目录名保持纯英文规范，并在 `SKILL.md` 的 `description` 开头统一标注 **【中文别名】** 便于速查与中文触发。

---

## 当前收录（7 个 Skill：6 个科研闭环 + 1 个图文草稿自动化）

| 阶段 / 分类 | Skill | 中文别名 | 简介 | 手册 | 状态 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0. 上游雷达** | [`cross-domain-paper-radar-codex`](./cross-domain-paper-radar-codex) | **【9大顶会跨域论文雷达】** | 借鉴 `M0rtzz/paper-notes` 分类体系，从 9 大顶会顶刊近 2 年论文中按 7 大高共鸣扩展领域（`D1–D7`）定向巡检、与本地台账联动去重、25 分量表快筛 Top 5–10 候选并生成下游深挖指令 | [USER_USE](./cross-domain-paper-radar-codex/USER_USE.md) | 可用 |
| **1. 跨域选题** | [`hsi-msi-idea-scout-codex`](./hsi-msi-idea-scout-codex) | **【单篇跨域选题与查新】** | 单篇论文跨域迁移分析：把自然/医学等顶会顶刊论文的失效机理，经 OpenAlex + arXiv 双通道查新、隐性前提审计与物理适配，转化为 Track A（HSI-MSI）与 Track B（Agent+HSI-MSI）研究蓝图 | [USER_USE](./hsi-msi-idea-scout-codex/USER_USE.md) | 可用 |
| **2. 精读沉淀** | [`hsi-agent-paper-reader-codex`](./hsi-agent-paper-reader-codex) | **【论文精读与台账】** | 对 HSI-MSI 融合 / Vision Agent / Agent+HSI-MSI 论文按统一 Schema 结构化精读，提取退化假设、Agent 闭环与局限性，并持久化写入本地文献台账（CSV + Markdown） | [USER_USE](./hsi-agent-paper-reader-codex/USER_USE.md) | 可用 |
| **3. 代码解剖** | [`hsi-repo-surgeon-codex`](./hsi-repo-surgeon-codex) | **【代码解剖与Tool封装】** | AST 自动扫描 PyTorch 开源仓库，输出端到端张量维度流转表、公式-代码行号对照、128+ 波段显存与光谱兼容性审计，并将现有求解器封装为标准 Agent Tool | [USER_USE](./hsi-repo-surgeon-codex/USER_USE.md) | 可用 |
| **4. 实验诊断** | [`hsi-exp-diagnostician-codex`](./hsi-exp-diagnostician-codex) | **【实验诊断与论文出图】** | 计算 PSNR / SAM / ERGAS / CC 及最差波段与最差像元光谱曲线，诊断空间-光谱权衡与 Agent 反思发散原因，自动输出出版级 SVG 诊断图 | [USER_USE](./hsi-exp-diagnostician-codex/USER_USE.md) | 可用 |
| **5. 审稿攻防** | [`hsi-agent-reviewer-codex`](./hsi-agent-reviewer-codex) | **【三视角审稿与Rebuttal】** | 投稿前模拟 **遥感物理逆问题 / CV 顶会方法论 / Agent 系统效率** 三位严苛审稿人，按 P0/P1/P2 排查拒稿风险与缺失消融，并辅助起草实证型 Rebuttal | [USER_USE](./hsi-agent-reviewer-codex/USER_USE.md) | 可用 |
| **内容分发** | [`xhs-douyin-draft-publisher`](./xhs-douyin-draft-publisher) | **【小红书与抖音图文草稿自动化】** | 根据关键词、项目仓库或本地图片生成/适配双平台标题、正文与标签，通过 Windows 原生 Win32 UI 自动化直接写入已登录的小红书 / 抖音 Chrome 标签页草稿箱（不碰 Cookie/Token，永不点击发布） | [USER_USE](./xhs-douyin-draft-publisher/USER_USE.md) | 可用 |

### 推荐科研闭环串联方式

```text
[0] cross-domain-paper-radar-codex (9大顶会 × 7大扩展领域宽口径巡检 + 台账去重)
         │  筛出 Top 5–10 篇 P0/P1 候选
         ▼
[1] hsi-msi-idea-scout-codex       (单篇深挖 + 隐性前提审计 + 双通道查新 + 改造蓝图)
         │  同步沉淀精读记录
         ▼
[2] hsi-agent-paper-reader-codex   (结构化精读 + 持久化 literature_ledger 台账)
         │  选定开源代码落地
         ▼
[3] hsi-repo-surgeon-codex         (PyTorch仓库解剖 + 张量流转表 + Agent Tool 封装)
         │  跑实验调参出图
         ▼
[4] hsi-exp-diagnostician-codex    (PSNR/SAM/ERGAS/最差波段诊断 + 出版级 SVG 出图)
         │  投稿前压力测试
         ▼
[5] hsi-agent-reviewer-codex       (遥感物理 / CV方法论 / Agent效率 三视角严苛审稿)
```

---

## 目录结构

```text
skills_list/
├── README.md                              # 本文件：技能库总览
├── .gitignore                             # 排除 Python 缓存等生成物
├── cross-domain-paper-radar-codex/        # 0. 【9大顶会跨域论文雷达】
│   ├── SKILL.md
│   ├── USER_USE.md
│   ├── scripts/
│   │   ├── radar_scan.py                  # DBLP 9大精确流 + OpenAlex补全 + 7大领域预设 + 台账去重
│   │   └── export_shortlist.py            # 导出 Markdown 雷达简报
│   ├── references/
│   │   ├── venue_whitelist.md
│   │   ├── domain_taxonomy_lexicon.md     # D1–D7 扩展领域与英文词簇
│   │   ├── scoring_rubric.md              # 5维25分量化量表
│   │   └── anti_patterns.md
│   └── examples/sample_radar_brief.md
├── hsi-msi-idea-scout-codex/              # 1. 【单篇跨域选题与查新】
│   ├── SKILL.md
│   ├── USER_USE.md
│   ├── scripts/
│   │   ├── check_hsi_gap.py               # OpenAlex + arXiv 双通道反向查新
│   │   └── fetch_top_venues.py            # DBLP + OpenAlex 9 大顶会顶刊辅助检索
│   ├── references/
│   │   ├── venue_taxonomy.md
│   │   ├── hsi_msi_pain_points.md
│   │   ├── transfer_bridge_map.md
│   │   ├── my_baseline_profile.md         # [建议填写] 个人 baseline / 显存 / 数据集
│   │   ├── anti_patterns.md
│   │   └── calibration_playbook.md
│   └── examples/sample_idea_report.md
├── hsi-agent-paper-reader-codex/          # 2. 【论文精读与台账】
│   ├── SKILL.md
│   ├── USER_USE.md
│   ├── scripts/append_ledger.py           # 追加/去重/检索 CSV + Markdown 台账
│   ├── references/extraction_schema.md
│   └── examples/sample_paper_note.md
├── hsi-repo-surgeon-codex/                # 3. 【代码解剖与Tool封装】
│   ├── SKILL.md
│   ├── USER_USE.md
│   ├── scripts/scan_repo_structure.py     # AST 扫描 nn.Module 与 forward 入口
│   └── references/
│       ├── agent_tool_contract.md
│       └── tensor_audit_checklist.md
├── hsi-exp-diagnostician-codex/           # 4. 【实验诊断与论文出图】
│   ├── SKILL.md
│   ├── USER_USE.md
│   ├── scripts/compute_hsi_metrics.py     # PSNR/SAM/ERGAS/CC + 诊断 SVG
│   └── references/metric_interpretation_guide.md
├── hsi-agent-reviewer-codex/              # 5. 【三视角审稿与Rebuttal】
│   ├── SKILL.md
│   ├── USER_USE.md
│   └── references/
│       ├── reviewer_personas.md
│       └── rebuttal_playbook.md
└── xhs-douyin-draft-publisher/            # 内容分发：【小红书与抖音图文草稿自动化】
    ├── SKILL.md
    ├── USER_USE.md
    ├── scripts/
    │   ├── win32_ui.py                    # Win32 底层（DPI/窗口/强前台/剪贴板/文件框/裁剪标定）
    │   └── publish_draft.py               # 小红书 & 抖音统一草稿保存 CLI（永不点发布）
    └── references/
        ├── copywriting_guide.md           # 读图OCR/3:4制图/标题公式/正文/标签与合规规范
        ├── xiaohongshu_flow.md            # 小红书坐标、缩略图陷阱与验收清单
        └── douyin_flow.md                 # 抖音与小红书6处差异、干扰元素与验收清单
```

---

## 快速开始

### 1. 一键安装全部 Skills 到 Codex（全局，推荐）

**Windows (PowerShell，在 `skills_list/` 目录下执行)：**

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Get-ChildItem -Directory | Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } | ForEach-Object {
    Copy-Item -Recurse -Force $_.FullName (Join-Path "$HOME\.codex\skills" $_.Name)
}
```

**macOS / Linux：**

```bash
mkdir -p ~/.codex/skills
for d in */; do [ -f "$d/SKILL.md" ] && cp -r "$d" ~/.codex/skills/; done
```

复制完成后重启 Codex 即可自动扫描加载。如果只需安装单个 skill 或项目级安装（`.agents/skills/`），请查看各自目录下的 `USER_USE.md`。

### 2. 首次配置（推荐）

填写 `hsi-msi-idea-scout-codex/references/my_baseline_profile.md`，写入你的主力 baseline、显卡显存、常用数据集与目标投稿会议，后续迁移蓝图会自动对齐这些约束。

### 3. 调用示例

在 Codex 对话中通过 `$<skill_name>`（或中文别名）显式触发，例如：

```text
使用 $cross-domain-paper-radar-codex 巡检 9 大顶会近 24 个月的 D2（医学）和 D4（视觉智能体）论文并输出雷达简报。
使用 $hsi-msi-idea-scout-codex 分析论文 D:\papers\yyy_cvpr2025.pdf 并运行双通道查新。
使用 $hsi-agent-paper-reader-codex 精读论文 D:\papers\xxx.pdf 并入库 ./literature_ledger。
使用 $hsi-repo-surgeon-codex 解剖仓库 D:\code\fusion_repo 并封装为 BaseHSIAgentTool。
使用 $hsi-exp-diagnostician-codex 诊断 gt.npy 与 pred.npy 并生成 SVG 误差图。
使用 $hsi-agent-reviewer-codex 对论文初稿 D:\paper\draft.tex 进行三视角审稿。
使用 $xhs-douyin-draft-publisher 读取本地图片并生成适配小红书与抖音的文案，保存到已登录的草稿箱（不要发布）。
```

---

## 新增 / 维护 skill

新增一个 skill 时遵循统一约定：

- 一个 skill 一个顶层目录，目录名与 `SKILL.md` frontmatter 中的 `name` 一致（纯英文小写），中文别名统一写在 `description` 开头（`【...】`）。
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
