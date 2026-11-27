---
name: xhs-douyin-draft-publisher
description: >-
  【小红书与抖音图文草稿自动化】Use this skill when the user wants to generate or adapt
  social media promotional copywriting and images (from provided keywords, a project repo,
  or existing local images) and save them as drafts into already logged-in Xiaohongshu
  (小红书创作服务平台) and/or Douyin (抖音创作者服务平台) Chrome tabs on Windows without
  extracting cookies/tokens and without clicking Publish.
---

# Xiaohongshu & Douyin Draft Publisher

Automate the full workflow from **keywords / project / local images → grounded copywriting & tags → Windows Win32 UI draft saving** on already logged-in Xiaohongshu (`creator.xiaohongshu.com`) and Douyin (`creator.douyin.com`) Chrome tabs.

## Hard Guardrails (Never Violate)

1. **Draft-Only (`暂存离开`) — NEVER click `发布`:** Save to the draft box and stop so the user can review and publish manually.
2. **Operate the Logged-In Chrome Tab Directly:** Never attempt `--remote-debugging-port`, Chrome profile cloning, or reading/copying `Cookies` SQLite files (all fail on modern Chrome due to Chrome 136+ policy, DPAPI device-bound encryption, and exclusive file locks).
3. **Calibrate Coordinates Before Clicking:** Reference coordinates are for 2560×1440 (DPI 96, maximized). Always take a screenshot and crop-zoom to confirm element positions before running upload/fill/save.
4. **Verify Every Step with Screenshots:** Never assume a click or paste succeeded. Check each step's screenshot against its verification criterion.
5. **Ground Copy in Real Facts:** When given local images or a repo, inspect every image/metric first. Never invent features or numbers.

## Progressive Disclosure Map

- Copywriting structure, title formulas, hashtag strategy, compliance & OCR fallback: [references/copywriting_guide.md](./references/copywriting_guide.md)
- Xiaohongshu exact steps, coordinates, traps & troubleshooting: [references/xiaohongshu_flow.md](./references/xiaohongshu_flow.md)
- Douyin exact steps, 6 diffs vs Xiaohongshu, traps & troubleshooting: [references/douyin_flow.md](./references/douyin_flow.md)
- Reusable Win32 UI automation primitives (DPI, window discovery, foreground, clipboard/CF_HDROP, `#32770` file dialog, crop-zoom): [scripts/win32_ui.py](./scripts/win32_ui.py)
- Unified CLI draft saver (`xhs` / `douyin`, JSON config driven): [scripts/publish_draft.py](./scripts/publish_draft.py)

---

## Standard 4-Phase Workflow

### Phase 1: Material Inspection & Content Preparation
1. **If the user provides local images:**
   - Read every image carefully (use native vision if available; if unavailable, run `rapidocr_onnxruntime` and write UTF-8 text output — see [references/copywriting_guide.md](./references/copywriting_guide.md)).
   - Confirm image file paths and display order (`01 → 0N`).
2. **If the user provides keywords or a project repo:**
   - Inspect actual source code, UI, and verified test/benchmark metrics.
   - If promotional cards need to be generated, render vertical **3:4 (1080×1440)** PNGs with Microsoft YaHei (`微软雅黑`), text-measured card heights, no mid-word English line breaks, and no leading Chinese punctuation.
3. **Draft platform-adapted copy** following [references/copywriting_guide.md](./references/copywriting_guide.md):
   - **Title:** ≤20 chars (XHS target ≤18 chars; Douyin target 12–16 chars, shorter & more colloquial, no decorative `《》` / `—`).
   - **Body + Tags:** Total ≤1000 chars on both platforms → keep body ≤950 chars + 4 high-signal tags (~32–50 chars).
   - Save the finalized copy locally (e.g., `小红书推广文案.md` / `抖音推广文案.md`) for user review.

### Phase 2: Window Discovery & Coordinate Calibration
Always resolve script paths relative to `<SKILL_DIR>`:

1. List visible Chrome windows to verify the logged-in target tab is open:
   ```powershell
   python <SKILL_DIR>/scripts/publish_draft.py --list-windows
   ```
   If the target creator tab is not open or not logged in, stop and ask the user to log in first.
2. Navigate (if needed) and take a calibration screenshot:
   ```powershell
   python <SKILL_DIR>/scripts/publish_draft.py --platform xhs --screenshot cal_xhs.png
   ```
3. Crop-zoom the target area (upload button, title/body inputs, or bottom save bar) to verify exact `(x, y)` coordinates before executing:
   ```powershell
   python <SKILL_DIR>/scripts/publish_draft.py --crop cal_xhs.png --box 720,130,1560,420 --out zoom.png
   ```

### Phase 3: Execute Draft Creation (via JSON Job Config)
Create a temporary JSON config file (e.g., `draft_job.json`) with the verified coordinates, image paths, title, body, and tags:

```json
{
  "window_keyword": "创作",
  "images": ["E:\\path\\to\\01.png", "E:\\path\\to\\02.png"],
  "title": "标题（<=20字）",
  "body": "正文内容（<=950字）",
  "tags": ["标签1", "标签2", "标签3", "标签4"],
  "coords": {
    "upload": [790, 500],
    "title": [900, 405],
    "body": [900, 448],
    "tags_anchor": [900, 500],
    "save": [1066, 1342]
  }
}
```

Run the unified script (supports `--no-nav` and `--from nav|upload|title|body|tags|save` for step-by-step recovery):

```powershell
# Xiaohongshu
python <SKILL_DIR>/scripts/publish_draft.py --platform xhs --config draft_job.json --shot-dir ./shots_xhs

# Douyin
python <SKILL_DIR>/scripts/publish_draft.py --platform douyin --config draft_job.json --shot-dir ./shots_dy
```

Read the platform-specific reference before running:
- **Xiaohongshu:** [references/xiaohongshu_flow.md](./references/xiaohongshu_flow.md) (watch out for `y≈274` thumbnail trap; strictly fill Title → Body; `Ctrl+Home` to verify top of body).
- **Douyin:** [references/douyin_flow.md](./references/douyin_flow.md) (must navigate to `/creator-micro/content/post/image`, NOT `/upload`; watch out for `y≈210` `快速填写` trap; NEVER use `Ctrl+A`; press `End` twice before clicking `暂存离开`).

### Phase 4: Verification & Handoff
Inspect the generated step screenshots and confirm all checklist items before reporting completion:
- [ ] All images uploaded and visible in thumbnail bar (`n/18` on XHS; `已添加 N 张图片` on Douyin).
- [ ] Title filled accurately with valid counter (`n/20`) and no accidental paste into body.
- [ ] Body complete from paragraph 1 (verified via `Ctrl+Home` on XHS) + tags appended cleanly at the end (`n/1000`).
- [ ] Draft saved:
  - **Xiaohongshu:** Top green `保存成功` toast + draft box count incremented.
  - **Douyin:** Redirected back to upload page showing `你还有上次未发布的图文，是否继续编辑？` (Douyin has no green toast).
- [ ] **`发布` was NEVER clicked.** Report the saved draft summary and local copy file path to the user for manual review.
