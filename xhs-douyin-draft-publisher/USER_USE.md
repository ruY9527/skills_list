# `xhs-douyin-draft-publisher` 使用手册

> **【小红书与抖音图文草稿自动化】** —— 根据你提供的关键词、开源项目或本地图片，自动提炼/改写适配平台的标题、正文与标签，并通过 Windows 原生 Win32 UI 自动化直接写入你已登录的 Chrome 小红书 / 抖音标签页草稿箱（**仅点「暂存离开」，永不点「发布」**）。

---

## 1. 前置条件（手动完成一次即可）

1. **Windows 环境 + Python 3**（需安装 `Pillow`：`pip install pillow`；若需离线 OCR 读图，可安装 `rapidocr-onnxruntime`）。
2. 在**本机 Chrome** 中已登录：
   - 小红书创作服务平台：`https://creator.xiaohongshu.com/publish/publish?target=image`
   - 抖音创作者服务平台：`https://creator.douyin.com/creator-micro/content/post/image`
3. 建议将目标 Chrome 窗口**最大化**（或单独用 `--app=URL` 打开），避免同窗口其他标签抢焦点。

---

## 2. 安装方式

### Antigravity（当前工作区已自动生效）
本 Skill 位于 `.agents/skills/xhs-douyin-draft-publisher/`，Antigravity 会在当前工作区自动发现并按需加载。

### 复制到 Codex 全局目录（可选）
```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force ".\.agents\skills\xhs-douyin-draft-publisher" "$HOME\.codex\skills\xhs-douyin-draft-publisher"
```

---

## 3. 常用调用示例

### 场景 1：根据本地已有图片写文案并存双平台草稿
```text
使用 xhs-douyin-draft-publisher，读取 E:\path\to\images 下的 4 张图片，
先识别图片内容，分别编写适配小红书和抖音的标题、正文与标签，
然后存到我旁边已登录的小红书和抖音草稿箱，不要发布。
```

### 场景 2：根据项目或关键词生成推广文案并存小红书草稿
```text
使用 xhs-douyin-draft-publisher，围绕关键词「XXX」和项目目录 E:\path\to\repo，
生成推广文案与标签，并保存到我已登录的小红书草稿箱，审核后由我自己发布。
```

### 场景 3：手动调用自动化脚本（断点续跑）
```powershell
# 查看当前 Chrome 窗口
python .\.agents\skills\xhs-douyin-draft-publisher\scripts\publish_draft.py --list-windows

# 从填写标题步骤继续（例如图片已上传）
python .\.agents\skills\xhs-douyin-draft-publisher\scripts\publish_draft.py `
  --platform xhs --config .\draft_job.json --from title
```

---

## 4. 安全边界

- **绝不读取或复制 Chrome Cookie / Token**，不开远程调试端口，只操作屏幕上已登录的窗口。
- **绝不点击「发布」按钮**，脚本中不提供发布动作，终点固定为「暂存离开」并截图验收。
