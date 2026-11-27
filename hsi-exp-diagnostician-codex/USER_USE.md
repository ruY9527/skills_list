# `hsi-exp-diagnostician-codex` 使用手册

用于对 **HSI-MSI 图像融合** 与 **Agent + HSI-MSI 融合** 的实验结果做物理/光谱诊断、失败案例归因与出版级矢量图（SVG）生成。

## 1. 安装到 Codex

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force ".\hsi-exp-diagnostician-codex" "$HOME\.codex\skills\hsi-exp-diagnostician-codex"
```

## 2. 常用调用方式

### 场景 1：分析重建结果 `.npy` / `.mat` 并自动出诊断图
```text
使用 $hsi-exp-diagnostician-codex 诊断实验结果：
GT 路径为 D:\exp\cave_gt.npy，预测路径为 D:\exp\ours_pred.npy，倍率 scale=8。
计算 PSNR/SAM/ERGAS/CC，找出最差的 5 个波段和最差 SAM 像元，把诊断 SVG 图输出到 ./diag_figs，并告诉我为什么 SAM 偏高。
```

### 场景 2：分析 Agent 多轮执行日志
```text
使用 $hsi-exp-diagnostician-codex 分析这份 Agent 执行日志 D:\exp\agent_trace.json，
排查为什么第 2 轮反思后残差反而上升，并给出改进后的停止与回滚策略。
```

## 3. 手动运行指标脚本

```powershell
D:\software_env\anaconda3\python.exe "$HOME\.codex\skills\hsi-exp-diagnostician-codex\scripts\compute_hsi_metrics.py" `
  --gt gt.npy --pred pred.npy --scale 8 --plot-dir ./diag_figs --output metrics.json
```
