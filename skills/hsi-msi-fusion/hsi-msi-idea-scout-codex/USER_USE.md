# `hsi-msi-idea-scout-codex` 使用手册

本手册用于指导你在 **Codex** 中安装、配置、日常调用与持续迭代 `hsi-msi-idea-scout-codex` 技能包。

---

## 一、这个 Skill 是做什么的？

当你阅读了一篇**自然图像**或**医学图像**领域的单篇前沿论文（理想来源为 **IJCV, TIP, CVPR, NeurIPS, AAAI, ICLR, ICCV, ECCV, TPAMI** 最近 2 年的首创/首发论文或原创模块），把这篇论文（PDF、文本、arXiv 链接或开源代码）交给 Codex 后，该 Skill 会强制 Codex 按严格科研流程执行：

1. **资格与证据深度核验**：检查是否符合 9 大顶会顶刊及近 2 年窗口，明确标注 `[Full-Text Verified]` 或 `[Abstract-Level Triage]`。
2. **失效机理与首创点解构**：拆出 2–4 个原子级创新点 / 原创模块 / 被前人忽略的底层问题。
3. **隐性前提审计**：挖出原论文在 RGB / 医学图像中成立、但在高光谱（$C = 31\text{–}224$ 通道、未知 PSF/SRF、SAM 约束）中会失效的假设。
4. **双通道反向查新（Gap Check）**：自动调用 OpenAlex（已发表文献）+ arXiv（最新预印本）+ 同义词扩展，客观判定每个点在 HSI-MSI 领域是 **Tier 1（真正空白）**、**Tier 2（存在盲区）** 还是 **Tier 3（已饱和淘汰）**。
5. **精准改造蓝图**：面向 **Track A（HSI-MSI 图像融合）** 与/或 **Track B（Agent + HSI-MSI 图像融合）**，给出动机诊断小实验、物理退化观测方程适配（或 Agent 非 RGB 物理探针闭环与审稿人三连问防御）、MVP 实验与审稿人攻防。
6. **7 条反模式自检**：杜绝文献幻觉、杜绝 A+B 缝合、杜绝基于摘要编造未读公式。

---

## 二、目录结构速览

```text
hsi-msi-idea-scout-codex/
├── SKILL.md                          # [自动加载] Codex 核心指令与 6 阶段工作流
├── USER_USE.md                       # [给人看的] 本使用手册
├── skill.meta.json                   # [网站数据] 高质量文案与声明式 Prompt 模板
├── scripts/
│   ├── check_hsi_gap.py              # [核心脚本] OpenAlex + arXiv 双通道反向查新（零外部依赖）
│   └── fetch_top_venues.py           # [辅助脚本] DBLP + OpenAlex 9 大顶会顶刊近 2 年论文检索
├── references/
│   ├── my_baseline_profile.md        # [建议你填写] 你的 Baseline、显卡显存、数据集与目标会议
│   ├── venue_taxonomy.md             # 9 大顶会顶刊白名单与近 24 个月规则
│   ├── hsi_msi_pain_points.md        # HSI-MSI 与 Agent+HSI-MSI 核心痛点图谱（A1–A5, B1–B5）
│   ├── transfer_bridge_map.md        # 跨领域映射词典（含医学图像 M1/M2/M3 三大高优金矿）
│   ├── anti_patterns.md              # 7 条硬性学术审计红线
│   └── calibration_playbook.md       # 技能校准与持续进化指南
└── examples/
    └── sample_idea_report.md         # 标准输出报告格式锚点（后续可替换为你的真实黄金样例）
```

---

## 三、安装到 Codex（二选一）

仓库源路径：`skills/hsi-msi-fusion/hsi-msi-idea-scout-codex/`。以下命令均在 `skills_list/` 仓库根目录执行，安装脚本自动排除 `__pycache__/` 与 `*.pyc`。

### 方式 A：全局安装（推荐，本机所有项目均可直接调用）

**Windows (PowerShell)：**
```powershell
.\scripts\install_skills.ps1 -Skill hsi-msi-idea-scout-codex
```

**macOS / Linux：**
```bash
./scripts/install_skills.sh --skill hsi-msi-idea-scout-codex
```

默认扁平安装到 `~/.codex/skills/hsi-msi-idea-scout-codex/`，不会保留仓库的分类层级。

### 方式 B：项目级安装（仅当前项目生效，可随 Git 共享）

**Windows (PowerShell)：**
```powershell
.\scripts\install_skills.ps1 -Skill hsi-msi-idea-scout-codex -Target ".agents\skills"
```

**macOS / Linux：**
```bash
./scripts/install_skills.sh --skill hsi-msi-idea-scout-codex --target ".agents/skills"
```

> **生效提示**：复制完成后，重启一次 Codex（CLI 或 IDE 插件）即可自动扫描加载该 Skill。

---

## 四、首次使用前推荐配置（1 分钟）

打开 `references/my_baseline_profile.md`，填入你的真实科研配置。例如：

```markdown
- Baseline Name / Repo Path: MoG-DCN (E:\thesis-code\MoG-DCN)
- GPU Hardware: 1x RTX 4090 (24GB)
- Reduced-Resolution Datasets: CAVE (31 bands), Chikusei (128 bands), PaviaU (103 bands)
- Full-Resolution / Real Datasets: WorldView-3, GaoFen-2
- Primary Target Venues: CVPR / IEEE TIP / IEEE TGRS
```

填完后，Codex 在 Phase 4 生成的改造方案会直接对齐你的 **Baseline 插槽位置、24GB 显存预算、目标数据集与投稿档位**，而不是给空泛的通用建议。

---

## 五、在 Codex 中的 4 种核心使用场景（可直接复制 Prompt）

在 Codex 对话中，最稳妥的方式是通过 **`$hsi-msi-idea-scout-codex`** 显式触发。

### 场景 1：单篇本地 PDF 论文双轨深度拆解（最常用）
```text
使用 $hsi-msi-idea-scout-codex 分析本地论文 D:\papers\xxx_cvpr2025.pdf。
请同时评估迁移到 Track A（HSI-MSI 图像融合）和 Track B（Agent + HSI-MSI 图像融合）的潜力，
对拆解出的每个子创新点运行双通道反向查新，最后将完整报告保存为 transfer_report.md。
```

### 场景 2：论文 + 官方开源代码联合分析（产出代码级改造蓝图）
```text
使用 $hsi-msi-idea-scout-codex 结合论文 D:\papers\xxx.pdf 与官方源码目录 D:\code\xxx_repo，
按 [Full-Text Verified] 深度拆解核心模块，完成 HSI-MSI 反向查新，
并结合我的 my_baseline_profile.md 给出具体的代码修改点、显存评估与动机诊断实验。
```

### 场景 3：专攻 Track B（Agent + HSI-MSI 图像融合）
```text
使用 $hsi-msi-idea-scout-codex，仅聚焦 Track B（Agent + HSI-MSI 图像融合），
深度分析论文 D:\papers\xxx_iclr2026.pdf。
重点提炼其决策/反思机制，严格回答审稿人三连问（为何优于 MoE、如何用非 RGB 物理探针感知光谱、大图延迟控制）。
```

### 场景 4：只有标题 / 摘要 / arXiv 链接时的快速初筛
```text
使用 $hsi-msi-idea-scout-codex 快速初筛这篇论文（标题与摘要贴在下面），
按 [Abstract-Level Triage] 深度判断它有哪些点在 HSI-MSI 融合领域是 Tier 1/Tier 2 空白，
帮我决定值不值得下载全文精读。
```

---

## 六、辅助脚本手动运行指南

两个脚本均仅使用 Python 3 标准库，**无需额外 `pip install`**。如果你处于离线沙箱，或想提前批量查新/检索，可以在终端手动运行：

> **Windows 提示**：如果直接输入 `python` 报错（微软商店别名冲突），请替换为你本机的真实 Python 路径，例如 `D:\software_env\anaconda3\python.exe`。

### 1. 手动运行双通道反向查新（`check_hsi_gap.py`）
```powershell
D:\software_env\anaconda3\python.exe "$HOME\.codex\skills\hsi-msi-idea-scout-codex\scripts\check_hsi_gap.py" `
  --concept "rectified flow inverse problem" `
  --synonyms "flow matching,ODE transport,consistency model" `
  --years 3 `
  --output gap_check.json
```
* `--concept`（必填）：你要查新的核心机制短语。
* `--synonyms`（强烈建议填）：逗号分隔的同义/上位机制词，防止因为“换了名字”误判为 Tier 1 空白。
* `--skip-arxiv`（可选）：只查 OpenAlex，跳过 arXiv 预印本通道。

### 2. 手动按 9 大顶会顶刊拉取近 2 年候选论文（`fetch_top_venues.py`）
```powershell
D:\software_env\anaconda3\python.exe "$HOME\.codex\skills\hsi-msi-idea-scout-codex\scripts\fetch_top_venues.py" `
  --queries "blind image restoration,medical image fusion,agentic image restoration" `
  --months 24 `
  --source both `
  --max-per-venue 10 `
  --output candidates.json
```
* `--venues`（可选）：默认全覆盖 9 大顶会顶刊，可缩小子集如 `--venues "CVPR,NeurIPS,ICLR,TPAMI"`。
* `--include-surveys`（可选）：默认过滤综述/基准类论文，加此参数可保留。

---

## 七、如何读懂输出报告里的关键标签

| 标签 | 含义与行动建议 |
| :--- | :--- |
| **`Tier 1`** | **真正空白**：OpenAlex 与近 3 年 arXiv 均未查到同类 HSI-MSI 工作，优先作为核心创新点立项。 |
| **`Tier 2`** | **浅层借用 / 存在盲区**：大方向有人做过，但原论文指出的具体失效机理或关键子模块在 HSI-MSI 没人解决；写作时需重点突出与最近工作的差异。 |
| **`Tier 3`** | **已饱和**：已被广泛迁移至 HSI-MSI，直接剔除，避免浪费实验时间。 |
| **`[Full-Text Verified]`** | 基于原文全文/源码核验的可靠方案，可直接进入写代码与动机诊断实验阶段。 |
| **`[Abstract-Level Triage]`** | 仅基于标题/摘要的初筛提案，下一步应下载 PDF/代码精读后再确认具体公式。 |
| **`M1 / M2 / M3`** | 命中医学图像三大高优金矿（`M1` 非刚性配准+融合、`M2` 前向算子失配/盲重建、`M3` 不确定性量化与幻觉抑制），通常具备更高的跨领域差异化价值。 |

---

## 八、如何让这个 Skill 越用越强（持续迭代）

每当你用真实论文跑完 1–2 次深度分析后，可以按 `references/calibration_playbook.md` 做 3 件小事：

1. **升级黄金样例**：挑出你最满意的一份 `[Full-Text Verified]` 真实报告，替换掉 `examples/sample_idea_report.md` 中的占位符模板，Codex 后续输出质量会显著跃升。
2. **反哺红线与词典**：遇到新的实验踩坑（如某模块在 128 波段显存爆炸或 SAM 恶化）记入 `references/anti_patterns.md`；发现新的高质量映射记入 `references/transfer_bridge_map.md`。
3. **定期同步**：如果你在项目 `skills_list/` 下修改了 Skill，重新执行第三节的 `install_skills.ps1` 或 `install_skills.sh` 即可刷新扁平安装目录。

---

## 九、常见问题排查（FAQ）

* **Q1：在 Codex 里发了论文，但没有触发这个 Skill？**
  * 确认已复制到 `~/.codex/skills/hsi-msi-idea-scout-codex/`（或 `.agents/skills/`）且重启了 Codex；对话开头显式加上 `$hsi-msi-idea-scout-codex` 即可强制触发。
* **Q2：Phase 3 查新脚本提示网络错误（Network error）？**
  * Codex 默认沙箱可能关闭了外网。请在运行脚本时批准网络权限，或按第六节在本地终端手动运行 `check_hsi_gap.py` 生成 JSON 后发给 Codex。Skill 会严格遵守红线，绝不会在断网时凭记忆编造“没人做过”。
* **Q3：如果我提供的论文不是这 9 大顶会顶刊，或者超过了 2 年，还能用吗？**
  * 可以用。Phase 0 会在报告头部**显式标注超出 9 大顶会或超过 24 个月窗口的提示**，不会静默放行或篡改出处，随后仍会完整执行拆解、反向查新与迁移蓝图分析。
