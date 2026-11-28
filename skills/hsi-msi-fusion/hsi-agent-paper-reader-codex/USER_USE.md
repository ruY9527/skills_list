# `hsi-agent-paper-reader-codex` 使用手册

用于对 **HSI-MSI 图像融合**、**Vision Agent** 及 **Agent + HSI-MSI** 论文进行统一结构化精读，并自动沉淀为本地可检索的 **文献台账（`ledger.csv` + `ledger.md`）**。

## 1. 安装到 Codex

仓库源路径：`skills/hsi-msi-fusion/hsi-agent-paper-reader-codex/`。在 `skills_list/` 仓库根目录执行对应命令，脚本会扁平安装到 `~/.codex/skills/hsi-agent-paper-reader-codex/`。

**Windows (PowerShell)：**
```powershell
.\scripts\install_skills.ps1 -Skill hsi-agent-paper-reader-codex
```

**macOS / Linux：**
```bash
./scripts/install_skills.sh --skill hsi-agent-paper-reader-codex
```

## 2. 常用调用方式

### 场景 1：精读单篇论文并自动入库文献台账
```text
使用 $hsi-agent-paper-reader-codex 精读本地论文 D:\papers\xxx.pdf，
按规范提取退化假设、光谱策略、Agent 闭环、指标与局限性，并追加写入 ./literature_ledger。
```

### 场景 2：检索已读文献台账（写 Related Work / 选 Baseline）
```powershell
D:\software_env\anaconda3\python.exe "$HOME\.codex\skills\hsi-agent-paper-reader-codex\scripts\append_ledger.py" `
  --ledger-dir ./literature_ledger --search "blind"
```
