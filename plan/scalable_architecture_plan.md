# `skills_list` 路线 A：可扩展多分类仓库与自动化门户架构重构方案

> **目标**：将 `ruY9527/skills_list` 从“6 个固定 Skill 平铺 + 手写前端数据”升级为**可平滑扩展至 50+ 跨领域 Skills 的二级分类仓库 + 自动化站点数据构建 + 一键扁平化 Codex 安装 + 动态分类门户网站**。<br>
> **核心工程原则**：**源码按分类文件夹组织（人读清爽）+ 安装到 Codex 时自动拍平（100% 兼容 Codex 一级目录扫描）+ 单一数据源自动构建网站（新增 Skill 零手改前端）**。

---

## 一、核心痛点与重构目标

当前架构在 6 个同主题 Skill 时运行良好，但扩展到 15–50+ 跨领域 Skill 时存在 4 个瓶颈：
1. **闭环图强绑定**：`docs/assets/app.js` 将全部 Skill 线性放入 `Stage 0–5` 流程图，加入非闭环独立工具 Skill 后会破坏布局。
2. **缺少分类筛选**：Skills 增多后仅靠搜索框难以按领域浏览。
3. **数据维护割裂**：所有展示文案与 6 个 `buildPrompt()` 函数硬编码在 41KB 的 `docs/data/skills_data.js` 中，新增或修改 Skill 时极易脱节。
4. **Codex 嵌套目录兼容性**：Codex 扫描 `~/.codex/skills/` 仅识别第一层子目录（`~/.codex/skills/<skill-name>/SKILL.md`），因此仓库按分类分文件夹后，必须配套扁平化安装脚本。

---

## 二、目标仓库目录架构

```text
skills_list/
├── skills/                                      # 【所有 Skills 统一收纳区】
│   └── hsi-msi-fusion/                          # 分类 1：Agent + HSI-MSI 图像融合
│       ├── category.json                        # 分类元数据（名称、简介、是否含专题闭环）
│       ├── cross-domain-paper-radar-codex/
│       │   ├── SKILL.md                         # Codex 专用指令（保持精简）
│       │   ├── USER_USE.md                      # 人工使用手册
│       │   ├── skill.meta.json                  # [可选] 网站富展示与 Prompt 表单声明
│       │   ├── scripts/
│       │   ├── references/
│       │   └── examples/
│       ├── hsi-msi-idea-scout-codex/            # (+ skill.meta.json)
│       ├── hsi-agent-paper-reader-codex/        # (+ skill.meta.json)
│       ├── hsi-repo-surgeon-codex/              # (+ skill.meta.json)
│       ├── hsi-exp-diagnostician-codex/         # (+ skill.meta.json)
│       └── hsi-agent-reviewer-codex/            # (+ skill.meta.json)
│   # 未来新增分类直接新建目录即可（例如 paper-writing-figures/、research-productivity/、dev-automation/），
│   # 本次重构不创建空壳假分类，保持仓库 100% 真实有效。
├── scripts/
│   ├── build_site_data.py                       # 【核心构建脚本】扫描 skills/*/*/ -> 生成 docs/data/skills_data.js
│   ├── install_skills.ps1                       # Windows 一键扁平化安装（支持 -All / -Category / -Skill / -List / -Target）
│   └── install_skills.sh                        # macOS / Linux 一键扁平化安装（支持 --all / --category / --skill / --list / --target）
├── docs/                                        # GitHub Pages 静态站点（支持 N 分类 × M Skills）
│   ├── .nojekyll
│   ├── index.html
│   ├── assets/
│   │   ├── style.css
│   │   └── app.js
│   └── data/
│       └── skills_data.js                       # 由 scripts/build_site_data.py 自动生成（禁止手改）
├── plan/
│   ├── github_pages_site_plan.md
│   └── scalable_architecture_plan.md
├── .gitignore
└── README.md
```

---

## 三、元数据 Schema 规范（纯数据驱动，零手写 JS 函数）

### 1. 分类元数据：`skills/<category-id>/category.json`
```json
{
  "id": "hsi-msi-fusion",
  "name": "Agent + HSI-MSI 图像融合",
  "shortName": "HSI-MSI 科研闭环",
  "description": "面向高光谱-多光谱图像融合与 Agent 融合研究生的 6 环全周期 Codex 技能套件。",
  "order": 1,
  "accent": "indigo",
  "hasWorkflow": true,
  "workflowTitle": "HSI-MSI 6 环科研闭环",
  "workflowSubtitle": "从顶会发现、跨域选题、精读台账到代码解剖、实验诊断与三视角审稿的完整接力。"
}
```
* 兜底规则：若未来新建分类目录时未写 `category.json`，`build_site_data.py` 自动用目录名作为 `id` 和 `name`，`hasWorkflow: false`，`order: 99`。

### 2. Skill 富展示元数据：`skills/<category-id>/<skill-id>/skill.meta.json`（可选）
把原 `docs/data/skills_data.js` 中 6 个 Skill 现有的高质量中文文案、痛点对比、阶段流程、产出预览与 Prompt 表单拆回各自的 `skill.meta.json`，并将原先的 JS `buildPrompt(values)` 函数升级为**声明式 `promptTemplate` 模板字符串**（例如 `使用 $cross-domain-paper-radar-codex 巡检 {{domains}}（近 {{months}} 个月）...`），由 `app.js` 统一渲染：

```json
{
  "alias": "9大顶会跨域论文雷达",
  "stage": 0,
  "stageName": "上游雷达",
  "icon": "radar",
  "tagline": "...",
  "description": "...",
  "audience": "...",
  "tags": ["9大顶会", "7大扩展领域", "OA PDF下载"],
  "action": "...",
  "inputArtifact": "...",
  "outputArtifact": "...",
  "handoffLabel": "...",
  "inputs": ["..."],
  "outputs": ["..."],
  "why": [
    { "pain": "...", "benefit": "..." }
  ],
  "phases": [
    { "name": "Phase 0", "title": "...", "text": "..." }
  ],
  "fileDescriptions": {
    "SKILL.md": "核心指令与 5 阶段雷达巡检 SOP",
    "scripts/radar_scan.py": "DBLP 9 大精确流 + OpenAlex 补全 + 台账去重"
  },
  "promptFields": [
    { "key": "domains", "label": "扫描领域（1–2个）", "type": "checkboxes", "min": 1, "max": 2, "default": ["D2", "D4"], "options": [...] }
  ],
  "promptTemplate": "请严格启用 `$cross-domain-paper-radar-codex` ... 扫描领域：{{domains}} ...",
  "preview": { "title": "...", "headers": [...], "rows": [[...]], "note": "..." },
  "next": "hsi-msi-idea-scout-codex",
  "nextText": "..."
}
```

### 3. 零 `skill.meta.json` 自动兜底机制（极简扩展的关键）
未来新增一个 Skill 时，即使**只写了 `SKILL.md`**、完全没写 `skill.meta.json`，`scripts/build_site_data.py` 也能自动完成：
1. 解析 `SKILL.md` 顶部的 YAML frontmatter：提取 `name` 和 `description`；
2. 若 `description` 开头包含 `【...】`，自动提取为 `alias`（中文别名）；
3. 自动遍历该 Skill 目录下的 `SKILL.md`、`USER_USE.md`、`scripts/*.py`、`references/*.md`、`examples/*.md` 生成真实 `files` 清单与 GitHub `/blob/main/skills/<category>/<skill-id>/...` 直链；
4. 自动生成默认安装命令（调用 `install_skills.ps1 -Skill <id>` 与 `install_skills.sh --skill <id>`）以及通用基础 `promptFields` + `promptTemplate`；
5. 自动归入其所在文件夹的分类下展示，**无需修改任何一行前端代码**！

---

## 四、三大自动化脚本规格

### 1. `scripts/build_site_data.py`（纯 Python 3 标准库，零外部依赖）
* **核心职责**：
  1. 扫描 `skills/*/*/SKILL.md`；
  2. **严格校验（失败直接返回非零退出码）**：
     * 目录名必须匹配 `^[a-z0-9-]+$`，禁止下划线 `_`；
     * `SKILL.md` 无 UTF-8 BOM，frontmatter 中 `name` 必须与目录名完全一致；
     * 全仓库跨分类禁止出现重名 Skill（防止扁平安装到 `~/.codex/skills/` 时互相覆盖！）；
     * 所有 `files` 路径真实存在；
  3. 合并 `category.json`、`skill.meta.json`（若存在）、`SKILL.md` 元数据与全局站点配置（场景向导、FAQ、全局安装命令、联网配置），生成带自动生成头注释的 `docs/data/skills_data.js`（挂载 `window.CATEGORIES_DATA`、`window.SKILLS_DATA`、`window.SITE_DATA`）；
  4. 支持 `--check` 参数：仅校验规范与数据同步状态，不写文件。

### 2. `scripts/install_skills.ps1`（Windows PowerShell 扁平化安装）
* **参数**：
  * `-All`：扁平化安装 `skills/*/*/` 下全部合法 Skill；
  * `-Category <cat1,cat2>`：仅安装指定分类下的 Skill；
  * `-Skill <id1,id2>`：仅安装指定名称的 Skill；
  * `-Target <path>`：安装目标目录，默认 `"$HOME\.codex\skills"`（可改为 `".\.agents\skills"` 做项目级安装）；
  * `-List`：打印所有分类与包含的 Skill 列表。
* **工程细节**：
  * 复制时自动排除 `__pycache__`、`*.pyc`（不污染目标目录）；
  * 自动清理旧的同名前缀 `*_codex` 残留；
  * 安装结束后打印清晰汇总（已安装数量、目标目录、提示重启 Codex）。

### 3. `scripts/install_skills.sh`（macOS / Linux 扁平化安装）
* 与 PowerShell 版保持完全等价的 CLI 参数：`--all`、`--category <cat>`、`--skill <id>`、`--target <dir>`（默认 `$HOME/.codex/skills`）、`--list`。

---

## 五、前端网站（`docs/`）可扩展升级规范

在完整保留现有高颜值 UI、深浅双主题、`Ctrl K` 搜索、`<dialog>` 详情抽屉与零外部 CDN 优点的基础上，完成 **6 项关键升级**：

1. **动态全局统计（消除硬编码）**：
   * Hero 区的 `Skills 总数`、`分类总数`、`真实 Python 脚本总数` 全部由 `app.js` 从 `window.SKILLS_DATA` / `window.CATEGORIES_DATA` 动态计算渲染；
   * 同步修正之前验收发现的 2 处细节：
     * 不再笼统写 `0 PY DEPS / 仅用 Python 3 标准库`，改为严谨表述（如动态显示脚本总数 + 说明「核心检索/台账脚本零外部依赖，指标出图脚本按需使用 numpy/matplotlib」）；
     * 联网配置路径由硬编码 `C:\Users\Administrator\.codex\config.toml` 改为通用 `%USERPROFILE%\.codex\config.toml`（macOS/Linux：`~/.codex/config.toml`）。
2. **专题工作流解耦（Featured Workflows）**：
   * Pipeline 区块只渲染 `hasWorkflow === true` 的分类，并按 `stage` 升序排列；
   * 当存在多个带工作流的分类时，自动在 Pipeline 顶部显示工作流切换 Tabs；当前仅有 1 个工作流（`hsi-msi-fusion`）时保持简洁无冗余 Tab；
   * 不属于工作流的独立 Skill 不强行塞入流程图，只在分类目录中展示。
3. **分类筛选胶囊栏（Category Filter Pills）**：
   * 在 Skills 目录区顶部动态渲染 `全部 (N)` + 每个分类的胶囊按钮（带该分类 Skill 计数）；
   * 分类筛选与搜索框关键词实时**叠加生效**，且支持一键清空。
4. **声明式 `promptTemplate` 渲染器**：
   * `app.js` 统一解析 `skill.promptTemplate` 中的 `{{key}}` 占位符（`checkboxes` 自动按 `, ` 拼接，空文本字段自动回退到 `placeholder` 或默认值），彻底移除 `skills_data.js` 里的硬编码 JS 函数。
5. **详情页源码链接与分类徽章**：
   * 所有 GitHub 源码链接基于 `skill.repoPath`（即 `skills/<category>/<skill-id>`）自动拼接，确保迁移到二级目录后 100% 指向真实文件；
   * 卡片与详情页同时展示所属分类标签；对于没有 `next` 下游接力的独立 Skill，优雅隐藏“下游接力”板块或改为“返回所属分类”。
6. **全局安装区与单 Skill 安装区升级**：
   * 全局安装区展示 `.\scripts\install_skills.ps1 -All`（及按分类 `-Category hsi-msi-fusion`）与 `./scripts/install_skills.sh --all`；
   * 每个 Skill 详情页的“① 安装本 Skill”展示 `.\scripts\install_skills.ps1 -Skill <id>` 与 `./scripts/install_skills.sh --skill <id>`。

---

## 六、验收标准（交付前必须 100% 通过）

1. **目录迁移干净**：仓库根目录不再有散落的 `*-codex` 目录，6 个 Skill 全部位于 `skills/hsi-msi-fusion/<skill-id>/`，且 `git status` 清晰反映重命名迁移。
2. **自动化构建跑通**：运行 `python scripts/build_site_data.py` 退出码 `0`，自动生成的 `docs/data/skills_data.js` 通过 `node --check`，且 `python scripts/build_site_data.py --check` 通过。
3. **全链路文件核验**：生成的 `skills_data.js` 中 6 个 Skill 的所有 `files` 路径（基于 `skills/hsi-msi-fusion/...`）100% 真实存在，**0 断链**，**0 `_codex` 残留**，**0 根绝对路径 `/assets/`**。
4. **Prompt 模板引擎验证**：在 Node 中用 `app.js` 同等逻辑测试 6 个 Skill 的 `promptTemplate` 渲染，确认无未替换的 `{{...}}` 残留。
5. **扁平安装脚本验证**：运行 `.\scripts\install_skills.ps1 -List` 正常列出分类与 6 个 Skill；用 `-Target <临时测试目录> -All` 实测扁平化安装成功（目标目录第一层直接是 6 个 `<skill-id>/SKILL.md`，且不含 `__pycache__`），测试后删除临时目录。
6. **文档同步**：根目录 `README.md` 与各 Skill 的 `USER_USE.md` 均已更新为新的 `skills/<category>/` 结构与一键安装脚本用法；`docs/index.html` 已修复 `C:\Users\Administrator` 硬编码与 `0 PY DEPS` 绝对化表述。
7. **禁止擅自 `git push`**：完成所有修改与自检后，汇报变更清单与验证结果，等待用户确认后再提交推送。
