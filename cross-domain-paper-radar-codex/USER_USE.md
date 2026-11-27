# `cross-domain-paper-radar-codex` 使用手册（【9大顶会跨域论文雷达】）

本 Skill 是科研闭环的 **第 0 环（上游发现雷达）**，用于在 **IJCV, TIP, CVPR, NeurIPS, AAAI, ICLR, ICCV, ECCV, TPAMI** 最近 2 年的论文中，按 7 大高共鸣扩展领域（`D1–D7`）定向巡检、去重打分，筛出最值得精读的 Top 5–10 篇候选论文，并一键生成喂给 `$hsi-msi-idea-scout-codex` 的深挖指令。

---

## 1. 安装到 Codex

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force ".\cross-domain-paper-radar-codex" "$HOME\.codex\skills\cross-domain-paper-radar-codex"
```

---

## 2. 7 大扩展领域速查表（建议每次只扫 1–2 个）

| 编号 | 领域名称 | 适合你的轨道 |
| :--- | :--- | :--- |
| `D1` | 自然图像底层视觉与逆问题（复原/盲超分/多源融合） | Track A |
| `D2` | 医学图像融合、配准与物理重建（CT-MRI/算子失配/3D体数据） | Track A & B |
| `D3` | 生成式先验与极速采样（Flow Matching/Rectified Flow/扩散逆问题） | Track A |
| `D4` | 视觉智能体、工具调用与多步反思（Agentic Vision/Self-Correction） | **Track B 核心** |
| `D5` | 高效长程表征、连续场与频域算子（Mamba/INR/小波频域） | Track A |
| `D6` | 测试期自适应、零样本与不确定性（TTT/TTA/幻觉抑制） | Track A & B |
| `D7` | 科学计算成像与多传感器物理融合（CASSI/PINN/Event/RGB-T） | Track A（高信息差） |

---

## 3. 在 Codex 中的常用调用 Prompt

### 场景 1：按周分领域巡检（最推荐，高信噪比）
```text
使用 $cross-domain-paper-radar-codex，从 9 大顶会顶刊近 24 个月中巡检 D2（医学图像融合与物理重建）和 D4（视觉智能体与多步反思）两个领域。
如果当前目录存在 ./literature_ledger/ledger.csv 请自动去重跳过已读论文。
按 25 分量表筛出 Top 8 篇高价值论文，生成“5分钟洞察”雷达简报保存为 radar_brief_D2_D4.md，并在文末为前 2 篇 P0 论文附带可直接喂给 $hsi-msi-idea-scout-codex 的深挖 Prompt。
```

### 场景 2：专项挖掘高信息差冷门金矿（D6 + D7）
```text
使用 $cross-domain-paper-radar-codex 巡检 D6（测试期自适应与不确定性）和 D7（科学计算成像与多传感器融合），
重点寻找能解决 HSI-MSI 全分辨率无 GT 泛化或未知 PSF/SRF 退化的首创论文，保存简报为 radar_brief_D6_D7.md。
```

---

## 4. 手动运行巡检脚本（支持提前离线缓存）

```powershell
# 查看内置 7 大领域及对应检索词簇
D:\software_env\anaconda3\python.exe "$HOME\.codex\skills\cross-domain-paper-radar-codex\scripts\radar_scan.py" --list-domains

# 定向扫描 D2 + D4 近 24 个月 9 大顶会顶刊论文并自动排除已读台账
D:\software_env\anaconda3\python.exe "$HOME\.codex\skills\cross-domain-paper-radar-codex\scripts\radar_scan.py" `
  --domains "D2,D4" `
  --months 24 `
  --max-per-venue 8 `
  --exclude-ledger ./literature_ledger/ledger.csv `
  --output radar_candidates.json
```

> **提示**：对于最近 1–2 个月刚放榜、DBLP 尚未收录的极少数顶会论文，你也可以把从 OpenReview / CVF / `papernotes.org` 导出的 JSON 通过 `--extra-json` 合并进来一起打分筛选。
