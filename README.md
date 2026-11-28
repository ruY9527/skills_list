# My Research Skills

> 个人研究技能库 —— 沉淀、复用与持续迭代我在 **Agent + HSI-MSI 图像融合** 科研中打磨的 Agent Skills。

这里存放我自己在研究与工程中实际使用的 skills。科研 Skill 采用 `skills/<category>/<skill-id>/` 二级分类结构，每个 Skill 仍是自包含目录：核心指令、使用手册、可执行脚本、参考知识、输出样例与展示元数据放在一起，便于扁平安装到 Codex / Claude / 其他支持 `SKILL.md` 的 Agent 运行时，也便于跨项目共享与版本追溯。所有 Skill 的 `name` 与目录名保持纯英文小写连字符规范，并在 `SKILL.md` 的 `description` 开头统一标注 **【中文别名】** 便于速查与中文触发。

## 在线交互网站

**线上地址（完成 GitHub Pages 部署后）：[https://ruY9527.github.io/skills_list/](https://ruY9527.github.io/skills_list/)**

仓库的 `docs/` 目录提供一套可随分类扩展的交互式介绍网站，包含专题工作流接力、分类筛选、场景快选、Skill 搜索、完整详情、双系统安装命令、声明式 Prompt 生成器与折叠 FAQ。网站支持浅色 / 深色主题和 `#skill=<skill-name>` 详情直达；只有 `hasWorkflow: true` 的分类会进入专题流程，独立 Skill 保留目录入口。内容分发 Skill 仍通过本 README 与其 `USER_USE.md` 查看。

- **本地预览**：直接用浏览器打开 [`docs/index.html`](./docs/index.html)，无需 npm 或构建服务；数据通过相对 `script` 标签加载，支持 `file://`。
- **更新网站数据**：在仓库根目录运行 `python scripts/build_site_data.py`，从分类目录、`SKILL.md`、`category.json` 与 `skill.meta.json` 重新生成 `docs/data/skills_data.js`；提交前用 `python scripts/build_site_data.py --check` 校验数据未漂移。
- **部署 GitHub Pages**：推送 `docs/` 后，在仓库 **Settings → Pages** 中选择 **Deploy from a branch**，将分支设为 `main`、目录设为 `/docs` 并保存。
- **技术形态**：原生 HTML5 + CSS3 + Vanilla ES6 JS；数据构建器只用 Python 3 标准库，无外部 CDN 强依赖，站内静态资源均使用相对路径，适配 `/skills_list/` 子路径。

---

## 当前收录（7 个 Skill：6 个科研闭环 + 1 个图文草稿自动化）

| 阶段 / 分类 | Skill | 中文别名 | 简介 | 手册 | 状态 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0. 上游雷达** | [`cross-domain-paper-radar-codex`](./skills/hsi-msi-fusion/cross-domain-paper-radar-codex) | **【9大顶会跨域论文雷达】** | 借鉴 `M0rtzz/paper-notes` 分类体系，从 9 大顶会顶刊近 2 年论文中按 7 大高共鸣扩展领域（`D1–D7`）定向巡检、与本地台账联动去重、25 分量表快筛 Top 5–10 候选并生成下游深挖指令 | [USER_USE](./skills/hsi-msi-fusion/cross-domain-paper-radar-codex/USER_USE.md) | 可用 |
| **1. 跨域选题** | [`hsi-msi-idea-scout-codex`](./skills/hsi-msi-fusion/hsi-msi-idea-scout-codex) | **【单篇跨域选题与查新】** | 单篇论文跨域迁移分析：把自然/医学等顶会顶刊论文的失效机理，经 OpenAlex + arXiv 双通道查新、隐性前提审计与物理适配，转化为 Track A（HSI-MSI）与 Track B（Agent+HSI-MSI）研究蓝图 | [USER_USE](./skills/hsi-msi-fusion/hsi-msi-idea-scout-codex/USER_USE.md) | 可用 |
| **2. 精读沉淀** | [`hsi-agent-paper-reader-codex`](./skills/hsi-msi-fusion/hsi-agent-paper-reader-codex) | **【论文精读与台账】** | 对 HSI-MSI 融合 / Vision Agent / Agent+HSI-MSI 论文按统一 Schema 结构化精读，提取退化假设、Agent 闭环与局限性，并持久化写入本地文献台账（CSV + Markdown） | [USER_USE](./skills/hsi-msi-fusion/hsi-agent-paper-reader-codex/USER_USE.md) | 可用 |
| **3. 代码解剖** | [`hsi-repo-surgeon-codex`](./skills/hsi-msi-fusion/hsi-repo-surgeon-codex) | **【代码解剖与Tool封装】** | AST 自动扫描 PyTorch 开源仓库，输出端到端张量维度流转表、公式-代码行号对照、128+ 波段显存与光谱兼容性审计，并将现有求解器封装为标准 Agent Tool | [USER_USE](./skills/hsi-msi-fusion/hsi-repo-surgeon-codex/USER_USE.md) | 可用 |
| **4. 实验诊断** | [`hsi-exp-diagnostician-codex`](./skills/hsi-msi-fusion/hsi-exp-diagnostician-codex) | **【实验诊断与论文出图】** | 计算 PSNR / SAM / ERGAS / CC 及最差波段与最差像元光谱曲线，诊断空间-光谱权衡与 Agent 反思发散原因，自动输出出版级 SVG 诊断图 | [USER_USE](./skills/hsi-msi-fusion/hsi-exp-diagnostician-codex/USER_USE.md) | 可用 |
| **5. 审稿攻防** | [`hsi-agent-reviewer-codex`](./skills/hsi-msi-fusion/hsi-agent-reviewer-codex) | **【三视角审稿与Rebuttal】** | 投稿前模拟 **遥感物理逆问题 / CV 顶会方法论 / Agent 系统效率** 三位严苛审稿人，按 P0/P1/P2 排查拒稿风险与缺失消融，并辅助起草实证型 Rebuttal | [USER_USE](./skills/hsi-msi-fusion/hsi-agent-reviewer-codex/USER_USE.md) | 可用 |
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
├── README.md
├── .gitignore
├── scripts/
│   ├── build_site_data.py                 # 标准库数据构建、强校验、无 meta 兜底与 --check
│   ├── install_skills.ps1                 # Windows 扁平安装：All / Category / Skill / Target / List
│   └── install_skills.sh                  # macOS / Linux 对等安装入口
├── skills/
│   └── hsi-msi-fusion/                    # 科研专题分类（hasWorkflow: true）
│       ├── category.json                  # 分类名称、排序与专题流程开关
│       ├── cross-domain-paper-radar-codex/
│       │   ├── SKILL.md / USER_USE.md / skill.meta.json
│       │   ├── scripts/                   # radar_scan / download_papers / export_shortlist
│       │   ├── references/                # venue、D1–D7、评分量表与反模式
│       │   └── examples/sample_radar_brief.md
│       ├── hsi-msi-idea-scout-codex/
│       │   ├── SKILL.md / USER_USE.md / skill.meta.json
│       │   ├── scripts/                   # check_hsi_gap / fetch_top_venues
│       │   ├── references/                # 查新、迁移桥接、baseline 与校准手册
│       │   └── examples/sample_idea_report.md
│       ├── hsi-agent-paper-reader-codex/
│       │   ├── SKILL.md / USER_USE.md / skill.meta.json
│       │   ├── scripts/append_ledger.py
│       │   ├── references/extraction_schema.md
│       │   └── examples/sample_paper_note.md
│       ├── hsi-repo-surgeon-codex/
│       │   ├── SKILL.md / USER_USE.md / skill.meta.json
│       │   ├── scripts/scan_repo_structure.py
│       │   └── references/                # Agent Tool 合约与张量审计清单
│       ├── hsi-exp-diagnostician-codex/
│       │   ├── SKILL.md / USER_USE.md / skill.meta.json
│       │   ├── scripts/compute_hsi_metrics.py
│       │   └── references/metric_interpretation_guide.md
│       └── hsi-agent-reviewer-codex/
│           ├── SKILL.md / USER_USE.md / skill.meta.json
│           └── references/                # 三视角审稿人与 Rebuttal 手册
├── docs/                                  # GitHub Pages 静态门户
│   ├── .nojekyll
│   ├── index.html
│   ├── assets/style.css                   # 双主题、分类筛选与响应式设计系统
│   ├── assets/app.js                      # 多工作流、详情、复制与通用模板渲染
│   └── data/skills_data.js                # 自动生成；请勿手工编辑
└── xhs-douyin-draft-publisher/            # 独立内容分发 Skill，不纳入科研分类与 -All
    ├── SKILL.md / USER_USE.md
    ├── scripts/                           # win32_ui / publish_draft
    └── references/                        # 双平台文案与草稿流程
```

---

## 快速开始

### 1. 一键扁平安装科研 Skills 到 Codex（全局，推荐）

安装脚本扫描 `skills/*/*/SKILL.md`，将 Skill 复制到目标目录第一层，目标仍为 `~/.codex/skills/<skill-id>/`；同目录刷新安装，自动排除 `__pycache__/` 与 `*.pyc`。以下命令均在 `skills_list/` 仓库根目录执行。

**Windows (PowerShell)：**

```powershell
.\scripts\install_skills.ps1 -List
.\scripts\install_skills.ps1 -All
# 也可按分类、单 Skill 或自定义目标安装：
.\scripts\install_skills.ps1 -Category hsi-msi-fusion
.\scripts\install_skills.ps1 -Skill hsi-msi-idea-scout-codex -Target "$HOME\.codex\skills"
```

**macOS / Linux：**

```bash
./scripts/install_skills.sh --list
./scripts/install_skills.sh --all
# 也可按分类、单 Skill 或自定义目标安装：
./scripts/install_skills.sh --category hsi-msi-fusion
./scripts/install_skills.sh --skill hsi-msi-idea-scout-codex --target "$HOME/.codex/skills"
```

复制完成后重启 Codex 即可自动扫描加载。`-All` / `--all` 覆盖 `skills/` 下全部 6 个科研 Skill；根目录的 `xhs-douyin-draft-publisher` 是独立内容分发 Skill，继续按其 `USER_USE.md` 安装。项目级安装可将 `-Target` / `--target` 指向当前项目的 `.agents/skills/`。

### 2. 首次配置（推荐）

填写 `skills/hsi-msi-fusion/hsi-msi-idea-scout-codex/references/my_baseline_profile.md`，写入你的主力 baseline、显卡显存、常用数据集与目标投稿会议，后续迁移蓝图会自动对齐这些约束。

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

新增一个 Skill 时遵循统一约定：

- 在 `skills/<category>/<skill-id>/` 下创建目录；分类与 Skill 目录名都使用 `^[a-z0-9-]+$`，Skill 的 frontmatter `name` 必须与目录名一致，跨分类不可重名。中文别名统一写在 `description` 开头（`【...】`）。
- 在分类目录维护 `category.json`（`id`、`name`、`hasWorkflow`、`order`）。只有明确具备上下游接力的专题才开启 `hasWorkflow`，独立 Skill 不强行进入流程。
- `SKILL.md` 必带 YAML frontmatter（`name`、`description`），`description` 写清触发条件；核心指令放 `SKILL.md`，大体积资料放 `references/`，可执行脚本放 `scripts/`，安装与用法放 `USER_USE.md`。
- 展示文案放 `skill.meta.json`，包含 What / Why / Phases / Preview / `promptFields` / 纯字符串 `promptTemplate`。占位符使用 `{{key}}`，不要在 JSON 中写 JS 函数。
- 暂未提供 `skill.meta.json` 时，构建器会从 `SKILL.md` 提取名称、中文别名和描述，扫描真实文件并生成基础卡片与 Prompt；这用于兜底，不替代高质量文案。
- 脚本路径相对 Skill 目录解析；`__pycache__/`、`*.pyc` 等生成物不入库，也不会被安装脚本复制。
- 变更后运行 `python scripts/build_site_data.py` 更新网站数据，再运行 `python scripts/build_site_data.py --check`。`docs/data/skills_data.js` 是生成物，禁止手工编辑。
- 在本文件「当前收录」表格登记新 Skill，并同步其 `USER_USE.md` 的仓库路径和扁平安装命令。

提交前自检：构建与 `--check` 通过、脚本可运行、文档链接有效、无敏感路径与凭证明文。核心检索/台账脚本零外部 Python 依赖；指标出图脚本按需使用 `numpy` / `matplotlib`。

---

## 说明

本仓库为个人研究用途，内容随研究进展持续演进；不同的 skill 可能面向不同的 Agent 运行时，以各自 `USER_USE.md` 中的说明为准。
