# -*- coding: utf-8 -*-
"""
Unified Xiaohongshu & Douyin image-post draft saver (Windows Win32 UI).

SAFETY: This script ONLY clicks '暂存离开' (Save Draft). It NEVER clicks '发布'.

Examples:
    python publish_draft.py --list-windows
    python publish_draft.py --platform xhs --screenshot cal_xhs.png
    python publish_draft.py --crop cal_xhs.png --box 720,130,1560,420 --out zoom.png
    python publish_draft.py --platform xhs --config job.json --shot-dir ./shots_xhs
    python publish_draft.py --platform douyin --config job.json --from title
"""
import argparse
import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import win32_ui as ui  # noqa: E402

DEFAULTS = {
    "xhs": {
        "url": "https://creator.xiaohongshu.com/publish/publish?target=image",
        "window_keywords": ["创作", "creator"],
        "t_nav": 7.0,
        "t_upload": 15.0,
        "t_focus": 1.3,
        "t_paste": 1.8,
        "t_tag": 1.4,
        "t_save": 4.0,
        "coords": {
            "upload": [790, 500],
            "title": [900, 405],
            "body": [900, 448],
            "tags_anchor": [900, 500],
            "save": [1066, 1342],
        },
    },
    "douyin": {
        "url": "https://creator.douyin.com/creator-micro/content/post/image",
        "window_keywords": ["抖音"],
        "t_nav": 8.0,
        "t_upload": 16.0,
        "t_focus": 1.5,
        "t_paste": 2.0,
        "t_tag": 1.5,
        "t_save": 6.0,
        "coords": {
            "upload": [1758, 480],
            "title": [1100, 320],
            "body": [1180, 400],
            "tags_anchor": [1180, 400],
            "blank_scroll": [700, 1200],
            "save": [1101, 1300],
        },
    },
}

STEPS = ["nav", "upload", "title", "body", "tags", "save"]


def find_target_window(keywords):
    for hwnd, title, rect in ui.list_chrome_windows():
        low = title.lower()
        if any(k.lower() in low for k in keywords):
            return hwnd, title, rect
    raise RuntimeError(
        f"No visible Chrome window matched keywords {keywords!r}. "
        "Open and sign in to the creator tab in Chrome first."
    )


def ensure_fg(hwnd):
    if not ui.force_foreground(hwnd):
        raise RuntimeError(f"Failed to bring Chrome window {hwnd} to foreground.")


def paste_into_box(hwnd, pos, text, shot_path, t_focus, t_paste):
    # Focus BEFORE clicking editor; never call force_foreground after clicking contenteditable.
    ensure_fg(hwnd)
    ui.set_clipboard_text(text)
    time.sleep(0.35)
    ui.move(*pos)
    time.sleep(0.25)
    ui.click(*pos, wait=t_focus)
    ui.hotkey("ctrl", "v")
    time.sleep(t_paste)
    ui.screenshot(shot_path)


def run_job(platform, cfg, start_step="nav", no_nav=False, shot_dir="./shots"):
    defaults = DEFAULTS[platform]
    url = cfg.get("url", defaults["url"])
    keywords = (
        [cfg["window_keyword"]]
        if cfg.get("window_keyword")
        else cfg.get("window_keywords", defaults["window_keywords"])
    )
    coords = dict(defaults["coords"])
    coords.update(cfg.get("coords", {}))

    images = cfg.get("images", [])
    title = cfg.get("title", "")
    body = cfg.get("body", "")
    tags = cfg.get("tags", [])

    if len(title) > 20:
        print(f"[WARN] Title length is {len(title)} > 20 chars; platform may truncate it.")
    if len(body) > 960:
        print(f"[WARN] Body length is {len(body)} chars; leave room for tags within 1000-char cap.")

    hwnd, win_title, rect = find_target_window(keywords)
    print(f"[WINDOW] hwnd={hwnd} rect={rect} title={win_title!r}")
    os.makedirs(shot_dir, exist_ok=True)
    prefix = "xhs" if platform == "xhs" else "dy"

    def shot(tag):
        p = os.path.join(shot_dir, f"_{prefix}_{tag}.png")
        ui.screenshot(p)
        print(f"  saved screenshot: {p}", flush=True)
        return p

    begin = 1 if (no_nav and start_step == "nav") else STEPS.index(start_step)

    try:
        for step in STEPS[begin:]:
            if step == "nav":
                print("[1/6 nav]")
                ensure_fg(hwnd)
                ui.hotkey("ctrl", "l")
                time.sleep(0.4)
                ui.set_clipboard_text(url)
                time.sleep(0.3)
                ui.hotkey("ctrl", "v")
                time.sleep(0.3)
                ui.press("enter")
                time.sleep(defaults["t_nav"])
                ensure_fg(hwnd)
                shot("01_nav")

            elif step == "upload":
                print("[2/6 upload]")
                if not images:
                    raise ValueError("Config 'images' list is empty.")
                ui.cancel_file_dialog()
                ensure_fg(hwnd)
                ui.move(*coords["upload"])
                time.sleep(0.25)
                ui.click(*coords["upload"], wait=2.0)
                ui.submit_files_to_dialog(images, timeout=10.0)
                time.sleep(defaults["t_upload"])
                ensure_fg(hwnd)
                shot("02_uploaded")

            elif step == "title":
                print("[3/6 title]")
                paste_into_box(
                    hwnd,
                    coords["title"],
                    title,
                    os.path.join(shot_dir, f"_{prefix}_03_title.png"),
                    defaults["t_focus"],
                    defaults["t_paste"],
                )

            elif step == "body":
                print("[4/6 body]")
                paste_into_box(
                    hwnd,
                    coords["body"],
                    body,
                    os.path.join(shot_dir, f"_{prefix}_04_body.png"),
                    defaults["t_focus"],
                    3.0,
                )
                if platform == "xhs":
                    ui.hotkey("ctrl", "home")
                    time.sleep(1.0)
                    shot("04b_body_top")

            elif step == "tags":
                print("[5/6 tags]")
                if tags:
                    ensure_fg(hwnd)
                    ui.move(*coords["tags_anchor"])
                    time.sleep(0.25)
                    ui.click(*coords["tags_anchor"], wait=1.2)
                    ui.hotkey("ctrl", "end")
                    time.sleep(1.0)
                    ui.press("enter")
                    time.sleep(0.4)
                    for tag in tags:
                        clean = tag.lstrip("#")
                        ui.set_clipboard_text("#" + clean)
                        time.sleep(0.4)
                        ui.hotkey("ctrl", "v")
                        time.sleep(defaults["t_tag"])
                        ui.press("enter")
                        time.sleep(0.85)
                        print(f"  tag: #{clean}", flush=True)
                shot("05_tags")

            elif step == "save":
                print("[6/6 save draft — NEVER clicking Publish]")
                ensure_fg(hwnd)
                if platform == "douyin":
                    blank = coords.get("blank_scroll", [700, 1200])
                    ui.click(*blank, wait=0.9)
                    ui.press("end")
                    time.sleep(1.0)
                    ui.press("end")
                    time.sleep(1.5)
                    shot("06_bottom")
                ui.move(*coords["save"])
                time.sleep(0.3)
                ui.click(*coords["save"], wait=defaults["t_save"])
                time.sleep(1.5)
                shot("07_saved")
                if platform == "xhs":
                    print("  Verify: top green '保存成功' toast + draft count +1.")
                else:
                    print("  Verify: redirected back to upload page with '你还有上次未发布的图文'.")
    finally:
        ui.release_all()
        ui.cancel_file_dialog()


def main():
    ap = argparse.ArgumentParser(description="Xiaohongshu & Douyin Win32 draft saver")
    ap.add_argument("--list-windows", action="store_true", help="List visible Chrome windows")
    ap.add_argument("--platform", choices=["xhs", "douyin"], help="Target platform")
    ap.add_argument("--screenshot", help="Focus target platform window and save calibration screenshot")
    ap.add_argument("--crop", help="Source image path to crop-zoom for coordinate calibration")
    ap.add_argument("--box", help="Crop box x1,y1,x2,y2 (used with --crop)")
    ap.add_argument("--out", help="Output path for --crop")
    ap.add_argument("--scale", type=int, default=2, help="Upscale factor for --crop")
    ap.add_argument("--config", help="Path to JSON job config")
    ap.add_argument("--from", dest="start", default="nav", choices=STEPS, help="Start step")
    ap.add_argument("--no-nav", action="store_true", help="Skip navigation step")
    ap.add_argument("--shot-dir", default="./shots", help="Directory for verification screenshots")
    args = ap.parse_args()

    if args.list_windows:
        for hwnd, title, rect in ui.list_chrome_windows():
            print(f"{hwnd}\t{rect}\t{title}")
        return

    if args.crop:
        if not args.box or not args.out:
            ap.error("--crop requires --box x1,y1,x2,y2 and --out PATH")
        box = [int(v.strip()) for v in args.box.split(",")]
        ui.crop_zoom(args.crop, box, args.out, scale=args.scale)
        print(f"Saved crop-zoom to {args.out}")
        return

    if args.screenshot:
        if not args.platform:
            ap.error("--screenshot requires --platform xhs|douyin")
        hwnd, title, rect = find_target_window(DEFAULTS[args.platform]["window_keywords"])
        ensure_fg(hwnd)
        time.sleep(0.5)
        ui.screenshot(args.screenshot)
        print(f"Saved screenshot of {hwnd} ({title}) to {args.screenshot}")
        return

    if not args.platform or not args.config:
        ap.error("Provide --platform and --config (or use --list-windows / --screenshot / --crop).")

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    run_job(
        args.platform,
        cfg,
        start_step=args.start,
        no_nav=args.no_nav,
        shot_dir=args.shot_dir,
    )


if __name__ == "__main__":
    main()
