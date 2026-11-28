# `hsi-repo-surgeon-codex` 使用手册

用于快速解剖 PyTorch 开源视觉/融合代码仓库：定位核心 `nn.Module` 与 `forward` 链路、输出张量维度流转表、审计显存与高光谱兼容性，并将现有模型封装为标准 **Agent Tool**。

## 1. 安装到 Codex

仓库源路径：`skills/hsi-msi-fusion/hsi-repo-surgeon-codex/`。在 `skills_list/` 仓库根目录执行对应命令，脚本会扁平安装到 `~/.codex/skills/hsi-repo-surgeon-codex/`。

**Windows (PowerShell)：**
```powershell
.\scripts\install_skills.ps1 -Skill hsi-repo-surgeon-codex
```

**macOS / Linux：**
```bash
./scripts/install_skills.sh --skill hsi-repo-surgeon-codex
```

## 2. 常用调用方式

### 场景 1：解剖开源仓库并输出张量维度流转表
```text
使用 $hsi-repo-surgeon-codex 解剖仓库 D:\code\some_fusion_repo，
定位核心模型文件，输出从输入 (LR_HSI, HR_MSI) 到输出的张量维度变化表，并检查在 128 波段下的显存风险。
```

### 场景 2：把开源融合模型封装成 Agent Tool
```text
使用 $hsi-repo-surgeon-codex 将 D:\code\some_fusion_repo 中的核心推理模型，
按照 agent_tool_contract.md 封装为标准的 BaseHSIAgentTool Python 类（返回融合结果与空间/光谱物理残差）。
```

## 3. 手动运行仓库扫描脚本

```powershell
D:\software_env\anaconda3\python.exe "$HOME\.codex\skills\hsi-repo-surgeon-codex\scripts\scan_repo_structure.py" `
  --repo "D:\code\some_fusion_repo" --output repo_map.json
```
