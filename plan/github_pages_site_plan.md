# `skills_list` GitHub Pages 在线门户网站详细设计方案

> **目标部署地址**：`https://ruY9527.github.io/skills_list/`<br>
> **部署模式**：GitHub Pages（Branch: `main` / Folder: `/docs`）<br>
> **适用仓库**：`ruY9527/skills_list`（面向 **Agent + HSI-MSI 图像融合** 研究生的 6 环 Codex Skills 全周期科研套件）

---

## 一、项目目标与定位

为 `skills_list` 仓库构建一个**高审美、零构建依赖、带交互式实用工具**的在线门户网站，让访问者（作者本人、导师、同门、开源社区研究者）能够：

1. **一眼看懂全局**：通过交互式 **6 环科研闭环图**，理解 6 个 Skill 如何从上游顶会发现一路串联到实验诊断与投稿前审稿。
2. **深度了解每个 Skill**：针对每一个 Skill，清晰回答 **What（做什么）**、**Why（为什么要用 / 相比普通问 AI 的痛点对比）**、**Architecture（内部阶段与脚本组成）**、**How to Use（怎么安装与怎么写 Prompt）**、**Expected Output（产出样例）** 与 **Next Step（下游接力）**。
3. **即拿即用**：提供**场景快选向导**、**交互式 Prompt 生成器（表单填参 → 实时拼接 → 一键复制）**、以及 **Windows PowerShell / macOS & Linux 一键安装命令切换器**。

---

## 二、真实源文件基线（实施前必须读取，严禁编造）

网站中涉及的所有 Skill 名称、中文别名、脚本名、参数、参考知识库文件名，**必须严格对齐仓库内真实文件**（禁止出现已废弃的 `_codex` 下划线命名，全部使用规范的 `-codex`）：

| 阶段 | 目录与 `name` | 中文别名 | 核心文档与脚本（相对仓库根） |
| :--- | :--- | :--- | :--- |
| **0. 上游雷达** | `cross-domain-paper-radar-codex` | 【9大顶会跨域论文雷达】 | `SKILL.md`, `USER_USE.md`, `scripts/radar_scan.py`, `scripts/download_papers.py`, `scripts/export_shortlist.py`, `references/{venue_whitelist,domain_taxonomy_lexicon,scoring_rubric,anti_patterns}.md` |
| **1. 跨域选题** | `hsi-msi-idea-scout-codex` | 【单篇跨域选题与查新】 | `SKILL.md`, `USER_USE.md`, `scripts/check_hsi_gap.py`, `scripts/fetch_top_venues.py`, `references/{venue_taxonomy,hsi_msi_pain_points,transfer_bridge_map,my_baseline_profile,anti_patterns,calibration_playbook}.md` |
| **2. 精读沉淀** | `hsi-agent-paper-reader-codex` | 【论文精读与台账】 | `SKILL.md`, `USER_USE.md`, `scripts/append_ledger.py`, `references/extraction_schema.md`, `examples/sample_paper_note.md` |
| **3. 代码解剖** | `hsi-repo-surgeon-codex` | 【代码解剖与Tool封装】 | `SKILL.md`, `USER_USE.md`, `scripts/scan_repo_structure.py`, `references/{agent_tool_contract,tensor_audit_checklist}.md` |
| **4. 实验诊断** | `hsi-exp-diagnostician-codex` | 【实验诊断与论文出图】 | `SKILL.md`, `USER_USE.md`, `scripts/compute_hsi_metrics.py`, `references/metric_interpretation_guide.md` |
| **5. 审稿攻防** | `hsi-agent-reviewer-codex` | 【三视角审稿与Rebuttal】 | `SKILL.md`, `USER_USE.md`, `references/{reviewer_personas,rebuttal_playbook}.md` |

GitHub 源码直达链接基地址：`https://github.com/ruY9527/skills_list/tree/main/<skill-dir>`（文件直链用 `/blob/main/...`）。

---

## 三、技术架构与目录规范

### 1. 技术选型约束
* **纯静态原生前端**：HTML5 + CSS3（CSS Variables 驱动双主题）+ Vanilla ES6 JavaScript。
* **零构建依赖**：不引入 `node_modules`、Webpack、Vite、React 构建链，确保 GitHub Pages 开启 `/docs` 后 10 秒直接上线，且保持 Python/Markdown 科研仓库的极度洁净。
* **本地双击 + 线上双兼容（重要工程细节）**：
  * 将结构化数据写入 `docs/data/skills_data.js`（挂载 `window.SKILLS_DATA = [...]`），而不是仅靠 `fetch('data/skills.json')`，这样无论是直接本地双击 `docs/index.html`（`file://` 协议）还是部署在 `https://ruY9527.github.io/skills_list/`，都不会触发浏览器 CORS 报错！
* **零外部 CDN 强依赖**：字体使用现代系统字体栈（`Inter, -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif` + `JetBrains Mono, Consolas, monospace`），图标使用内联轻量 SVG，确保国内/离线环境毫秒级加载、永不裂图。

### 2. 目标目录结构

```text
skills_list/
├── docs/
│   ├── index.html              # 主页面（语义化 HTML5 + OpenGraph 元信息）
│   ├── .nojekyll               # 禁用 Jekyll 处理，防止静态资源路径问题
│   ├── assets/
│   │   ├── style.css           # 深浅双主题设计系统、组件样式、响应式布局
│   │   └── app.js              # 闭环交互、场景快选、详情抽屉/视图、Prompt生成器、一键复制、搜索过滤
│   └── data/
│       └── skills_data.js      # 6个Skill的完整结构化数据 + 场景向导数据 + FAQ数据
└── plan/
    └── github_pages_site_plan.md
```

---

## 四、页面信息架构与功能详设

### 模块 1：顶部粘性导航栏（Sticky Header）
* 左侧品牌标识：`HSI-MSI × Agent Skills`（附带微缩光谱条 SVG Logo）。
* 中间锚点导航：`6环闭环` / `场景快选` / `全部 Skills (6)` / `快速安装` / `避坑 FAQ`。
* 右侧操作区：
  * 即时关键词搜索框（支持按英文名、中文别名、功能词如 `SAM` / `查新` / `PDF` / `审稿` 实时过滤 Skill 卡片）；
  * **浅色 / 深色主题切换按钮**（写入 `localStorage`，首次访问默认清爽学术浅色主题）；
  * GitHub 仓库外链按钮（`https://github.com/ruY9527/skills_list`）。

### 模块 2：Hero 首屏区
* 醒目主标题与副标题：清晰阐明这是专为 **Agent + HSI-MSI 图像融合** 研究打造的 6 环 Codex 科研技能套件。
* 4 枚核心数据徽章：`6 个全周期 Skill` · `9 大顶会顶刊覆盖` · `7 大扩展领域 (D1–D7)` · `零外部依赖 Python 脚本`。
* 主 CTA 按钮：`探索 6 环科研闭环`（平滑滚动）、`一键安装全部 Skills`（跳转到安装区并高亮）。

### 模块 3：交互式 6 环科研闭环图（Interactive Pipeline）
* 横向 6 节点步骤流（移动端自动切换为纵向时间轴），节点之间带方向箭头与数据流转标签：
  * `[0] 雷达发现` —(Top 5–10 候选 & OA PDF)→ `[1] 单篇跨域选题` —(Tier 1/2 改造蓝图)→ `[2] 精读台账` —(`ledger.csv` 联动去重)→ `[3] 代码解剖` —(张量表 & Agent Tool)→ `[4] 实验诊断` —(指标 & SVG 诊断图)→ `[5] 三视角审稿`
* **交互行为**：
  * 点击任意节点，在流程图下方立即更新“当前节点摘要条”（输入产物、核心动作、输出产物、一键打开完整详情按钮）；
  * 高亮当前节点与下游接力节点。

### 模块 4：“我现在卡在哪？”场景快选向导（Scenario Picker）
* 6 张高频研究生痛点场景卡片：
  1. *“不知道这周该看哪些自然/医学顶会新论文”* → 推荐 `[0] cross-domain-paper-radar-codex`
  2. *“手头有篇 CVPR/NeurIPS 好论文，想知道能不能迁移到 HSI-MSI 且没人做过”* → 推荐 `[1] hsi-msi-idea-scout-codex`
  3. *“读了几十篇论文总忘，想建一份长期可检索的文献台账”* → 推荐 `[2] hsi-agent-paper-reader-codex`
  4. *“开源代码几千行看不懂，或想把融合模型封装成 Agent Tool”* → 推荐 `[3] hsi-repo-surgeon-codex`
  5. *“PSNR 涨了但 SAM 变差了，或 Agent 反思越修越崩”* → 推荐 `[4] hsi-exp-diagnostician-codex`
  6. *“论文快投稿了，想提前被遥感/CV/Agent 三类审稿人狠狠挑刺”* → 推荐 `[5] hsi-agent-reviewer-codex`
* **交互行为**：点击任意场景卡片，自动打开对应 Skill 的详情视图并定位到它的 **交互式 Prompt 生成器**。

### 模块 5：6 个 Skill 卡片矩阵与深度详情视图（核心主体）
* **概览卡片**（3 列网格，平板 2 列，手机 1 列）：
  * 阶段徽章（`Stage 0` ~ `Stage 5`）、中文别名、英文 `name`（等宽字体）、一句话定位、3 个能力标签、脚本数量徽章、`查看详情 & 生成 Prompt` 按钮。
* **完整详情视图（模态抽屉或展开面板，支持 URL Hash 如 `#skill=hsi-msi-idea-scout-codex` 分享直达）**，严格包含 **6 大标准板块**：
  1. **① 是什么（What）**：精准定位、适用对象、核心输入与输出产物。
  2. **② 为什么要用它（Why — 痛点对比表）**：双列对比表格（左侧「普通问 AI / 纯人工的痛点」 vs 右侧「使用本 Skill 后的确定性收益」），至少 3 条硬核对比。
  3. **③ 内部工作流与文件组成（Architecture）**：
     * 展示 Phase 0 → Phase N 的步骤条；
     * 列出该 Skill 的 `scripts/` 与 `references/` 文件清单，每个文件附带一句话职责说明与 GitHub 源码直链。
  4. **④ 怎么用（How to Use — 交互式实操）**：
     * **安装命令块**：支持一键切换 `Windows PowerShell` / `macOS & Linux`，一键复制；
     * **交互式 Prompt 生成器**：为每个 Skill 提供 2–3 个可调参数控件（例如雷达的领域勾选 `D1–D7`、单篇选题的 PDF 路径/轨道切换、实验诊断的 `gt.npy`/`pred.npy`/倍率输入、审稿的目标会议选择），实时拼出完整 Prompt 并支持 **一键复制**。
  5. **⑤ 预期产出预览（Output Preview）**：展示精简但真实的报告片段/表格样例（例如 25 分打分卡、Tier 1/2/3 查新矩阵、SVG 诊断图清单、P0/P1/P2 审稿结论）。
  6. **⑥ 下游接力（Next Step）**：明确说明下一步把产出交给哪个 Skill，并提供一键跳转按钮。

### 模块 6：全局安装、Codex 联网配置与避坑 FAQ
* **一键全量安装块**（Windows PowerShell / macOS & Linux 切换 + 复制按钮）。
* **必看 Codex 联网配置卡片**：明确展示 `C:\Users\Administrator\.codex\config.toml` 中开启 `[sandbox_workspace_write] network_access = true` 的配置块（解决 DNS 报错 `<urlopen error [Errno 11001] getaddrinfo failed>`），以及离线本地先跑脚本再喂 JSON 的备用方案。
* **个人基线档案定制提示**：指导填写 `hsi-msi-idea-scout-codex/references/my_baseline_profile.md`。
* **折叠式 FAQ**（至少 4 条：为什么目录名用 `-codex` 不用 `_codex`、Windows Python 别名冲突怎么办、如何更新同步 Skill、付费墙论文怎么处理）。

---

## 五、视觉与交互美学规范

* **设计语言**：Academic Precision × Modern Developer Docs（干净、克制、高信息密度但不拥挤）。
* **色板系统（CSS Variables）**：
  * 浅色模式（默认）：页面背景 `#F8FAFC`，卡片背景 `#FFFFFF`，边框 `#E2E8F0`，主文字 `#0F172A`，次文字 `#475569`。
  * 深色模式：页面背景 `#0B1120`，卡片背景 `#111827`，边框 `#1E293B`，主文字 `#F1F5F9`，次文字 `#94A3B8`。
  * 品牌强调色：光谱靛蓝 `#4F46E5`（主按钮/高亮）、遥感青 `#06B6D4`（副强调/流程连线）、琥珀金 `#F59E0B`（`P0` / `Tier 1` / 金矿标签）、翠绿 `#10B981`（已复制/验证通过状态）。
* **交互反馈**：
  * 所有代码块与生成的 Prompt 均带右上角 `复制` 按钮，点击后变为 `已复制 ✓` 保持 1.8 秒；
  * 详情面板支持 `ESC` 键关闭与点击遮罩关闭；
  * 完整适配 `>=1200px`（桌面）、`768–1199px`（平板）、`<768px`（手机）。

---

## 六、验收标准（交付前必须逐条自检）

1. **真实性 100%**：所有 6 个 Skill 的名称、中文别名、脚本名、参数、参考文件名与仓库实际文件完全一致，**零 `_codex` 残留**。
2. **双模式零报错**：无论是本地直接打开 `docs/index.html` 还是通过 `python -m http.server` 访问，浏览器控制台 **0 Error**，无 CORS 报错。
3. **核心交互完整可用**：6 环闭环图点击联动、场景快选跳转、搜索实时过滤、深浅主题切换持久化、6 个 Skill 详情视图、交互式 Prompt 生成器实时拼接与一键复制、PowerShell/Bash 切换全部工作正常。
4. **视觉与排版精致**：无文字溢出、无遮挡、无破损链接，深色与浅色模式下文字对比度均清晰易读。
5. **部署就绪**：包含 `docs/.nojekyll`，所有内部资源引用均为相对路径（如 `./assets/style.css`），完美兼容 `https://ruY9527.github.io/skills_list/` 子路径部署（**严禁使用 `/assets/...` 根绝对路径导致子路径 404**）。

---

## 七、GitHub Pages 上线步骤

1. 将 `docs/` 提交并推送到 `ruY9527/skills_list` 的 `main` 分支。
2. 在 GitHub 仓库打开 `Settings → Pages → Build and deployment`：
   * `Source`: `Deploy from a branch`
   * `Branch`: `main` / Folder: `/docs` → 点击 `Save`
3. 等待约 1 分钟，访问 `https://ruY9527.github.io/skills_list/` 即可上线。
