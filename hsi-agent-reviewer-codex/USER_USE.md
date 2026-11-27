# `hsi-agent-reviewer-codex` 使用手册

投稿前模拟 **遥感物理专家 / CV 顶会方法论 / Agent 系统效率** 三位严苛审稿人，提前暴露致命漏洞并准备 Rebuttal。

## 1. 安装到 Codex

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force ".\hsi-agent-reviewer-codex" "$HOME\.codex\skills\hsi-agent-reviewer-codex"
```

## 2. 常用调用方式

### 场景 1：投稿前全稿压力测试
```text
使用 $hsi-agent-reviewer-codex 对我的论文初稿 D:\paper\draft.tex（目标投 CVPR / IEEE TIP）进行三视角严苛审稿，
重点列出 P0 拒稿风险项和投稿前必须补做的消融实验清单。
```

### 场景 2：起草审稿回复信（Rebuttal）
```text
使用 $hsi-agent-reviewer-codex，结合审稿意见（贴在下面）和我的补充实验结果，
起草客观、克制、逐点回应的 Rebuttal。
```
