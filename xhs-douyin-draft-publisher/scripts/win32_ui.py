# -*- coding: utf-8 -*-
"""
Self-contained Win32 UI automation primitives for Windows Chrome tabs.

Includes:
- PER_MONITOR_AWARE DPI initialization (mandatory before any coordinates)
- Visible Chrome window discovery
- Foreground forcing (topmost jitter + AttachThreadInput)
- Keyboard / mouse synthesis + Unicode fallback typing
- Clipboard text (CF_UNICODETEXT) & file drop (CF_HDROP)
- Native Windows #32770 File Open dialog automation (WM_SETTEXT + BM_CLICK)
- Fullscreen screenshot & crop-zoom helper for coordinate calibration
"""
import ctypes
import os
import time
from ctypes import wintypes

# Step 0: Enable per-monitor DPI awareness before any Win32 coordinate calls.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# Win32 signatures (SendMessageW 4th arg MUST be c_void_p to pass string buffers safely)
user32.FindWindowW.restype = wintypes.HWND
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.SendMessageW.restype = ctypes.c_ssize_t
user32.SendMessageW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    ctypes.c_void_p,
]
user32.GetForegroundWindow.restype = wintypes.HWND
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.BringWindowToTop.argtypes = [wintypes.HWND]
user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowThreadProcessId.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.DWORD),
]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]

user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.restype = wintypes.BOOL
user32.CloseClipboard.restype = wintypes.BOOL
user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
user32.SetClipboardData.restype = wintypes.HANDLE
user32.GetClipboardData.argtypes = [wintypes.UINT]
user32.GetClipboardData.restype = wintypes.HANDLE
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.restype = wintypes.BOOL

SW_MAXIMIZE = 3
SW_RESTORE = 9
HWND_TOPMOST = wintypes.HWND(-1)
HWND_NOTOPMOST = wintypes.HWND(-2)
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040

WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
BM_CLICK = 0x00F5

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

CF_UNICODETEXT = 13
CF_HDROP = 15
GMEM_MOVEABLE = 0x0002

VK = {
    "ctrl": 0x11, "shift": 0x10, "alt": 0x12, "enter": 0x0D, "esc": 0x1B,
    "tab": 0x09, "space": 0x20, "back": 0x08, "delete": 0x2E,
    "home": 0x24, "end": 0x23, "left": 0x25, "right": 0x27, "up": 0x26, "down": 0x28,
    "a": 0x41, "c": 0x43, "v": 0x56, "x": 0x58, "z": 0x5A, "f": 0x46, "l": 0x4C,
    "t": 0x54, "w": 0x57, "n": 0x4E, "r": 0x52, "p": 0x50,
    "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
    "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
    "f5": 0x74, "f6": 0x75, "f12": 0x7B,
}
_pressed = set()


class DROPFILES(ctypes.Structure):
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
        ("fNC", wintypes.BOOL),
        ("fWide", wintypes.BOOL),
    ]


# ---------------- Window Management ----------------
def list_chrome_windows():
    """Return [(hwnd, title, (left, top, right, bottom)), ...] for visible Chrome windows."""
    out = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls, 256)
        if cls.value != "Chrome_WidgetWin_1":
            return True
        r = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(r))
        if r.right - r.left < 400 or r.bottom - r.top < 300:
            return True
        title = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, title, 512)
        out.append((hwnd, title.value, (r.left, r.top, r.right, r.bottom)))
        return True

    user32.EnumWindows(cb, 0)
    return out


def maximize(hwnd):
    user32.ShowWindow(hwnd, SW_MAXIMIZE)
    time.sleep(0.3)


def force_foreground(hwnd, tries=15):
    """Bring target window to foreground; do NOT call after clicking inside a contenteditable box."""
    cur = kernel32.GetCurrentThreadId()
    for _ in range(tries):
        if user32.GetForegroundWindow() == hwnd:
            return True
        user32.SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW,
        )
        user32.SetWindowPos(
            hwnd, HWND_NOTOPMOST, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW,
        )
        fg = user32.GetForegroundWindow()
        ft = user32.GetWindowThreadProcessId(fg, None) if fg else 0
        tt = user32.GetWindowThreadProcessId(hwnd, None)
        attached = []
        for tid in (ft, tt):
            if tid and tid != cur and tid not in attached:
                user32.AttachThreadInput(cur, tid, True)
                attached.append(tid)
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
        for tid in attached:
            user32.AttachThreadInput(cur, tid, False)
        time.sleep(0.25)
    return user32.GetForegroundWindow() == hwnd


# ---------------- Keyboard & Mouse ----------------
def down(key):
    vk = VK[key.lower()] if isinstance(key, str) else key
    if vk not in _pressed:
        user32.keybd_event(vk, 0, 0, 0)
        _pressed.add(vk)
    time.sleep(0.02)


def up(key):
    vk = VK[key.lower()] if isinstance(key, str) else key
    if vk in _pressed:
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        _pressed.discard(vk)
    time.sleep(0.02)


def release_all():
    for vk in list(_pressed):
        try:
            user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        except Exception:
            pass
    _pressed.clear()


def press(key, times=1, interval=0.06):
    for _ in range(times):
        down(key)
        up(key)
        time.sleep(interval)


def hotkey(*keys):
    for k in keys:
        down(k)
    time.sleep(0.05)
    for k in reversed(keys):
        up(k)
    time.sleep(0.12)


def type_unicode_text(text, delay=0.008):
    """Fallback character-by-character Unicode input when clipboard is unavailable."""
    for ch in text:
        code = ord(ch)
        user32.keybd_event(0, code, KEYEVENTF_UNICODE, 0)
        time.sleep(delay)
        user32.keybd_event(0, code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0)
        time.sleep(delay)


def move(x, y):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.05)


def click(x=None, y=None, wait=0.35):
    if x is not None:
        move(x, y)
        time.sleep(0.12)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.06)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(wait)


# ---------------- Clipboard ----------------
def _open_clipboard(retries=25):
    for _ in range(retries):
        if user32.OpenClipboard(None):
            return True
        time.sleep(0.1)
    return False


def set_clipboard_text(text):
    if not _open_clipboard():
        raise RuntimeError("OpenClipboard failed")
    try:
        user32.EmptyClipboard()
        buf = ctypes.create_unicode_buffer(text)
        size = ctypes.sizeof(buf)
        h = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
        p = kernel32.GlobalLock(h)
        ctypes.memmove(p, buf, size)
        kernel32.GlobalUnlock(h)
        user32.SetClipboardData(CF_UNICODETEXT, h)
    finally:
        user32.CloseClipboard()


def set_clipboard_files(paths):
    """Put file paths into clipboard as CF_HDROP (equivalent to Explorer Ctrl+C)."""
    abs_paths = [os.path.abspath(p) for p in paths]
    for p in abs_paths:
        if not os.path.isfile(p):
            raise FileNotFoundError(p)

    path_bytes = b"".join(p.encode("utf-16-le") + b"\x00\x00" for p in abs_paths) + b"\x00\x00"
    hdr = DROPFILES(pFiles=20, pt_x=0, pt_y=0, fNC=False, fWide=True)
    blob = bytes(hdr) + path_bytes
    if len(blob) % 4:
        blob += b"\x00" * (4 - len(blob) % 4)

    if not _open_clipboard():
        raise RuntimeError("OpenClipboard failed")
    try:
        user32.EmptyClipboard()
        h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(blob))
        p = kernel32.GlobalLock(h)
        ctypes.memmove(p, blob, len(blob))
        kernel32.GlobalUnlock(h)
        if not user32.SetClipboardData(CF_HDROP, h):
            raise RuntimeError("SetClipboardData(CF_HDROP) failed")
    finally:
        user32.CloseClipboard()
    return abs_paths


# ---------------- Native #32770 File Open Dialog ----------------
def enum_children(dlg, klass):
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(h, _):
        b = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(h, b, 64)
        if b.value == klass:
            found.append(h)
        return True

    user32.EnumChildWindows(dlg, cb, 0)
    return found


def get_win_text(hwnd, cap=8192):
    buf = ctypes.create_unicode_buffer(cap)
    user32.SendMessageW(hwnd, WM_GETTEXT, cap, ctypes.cast(buf, ctypes.c_void_p))
    return buf.value


def set_win_text(hwnd, text):
    buf = ctypes.create_unicode_buffer(text, len(text) + 1)
    user32.SendMessageW(hwnd, WM_SETTEXT, 0, ctypes.cast(buf, ctypes.c_void_p))


def find_file_dialog():
    return user32.FindWindowW("#32770", "打开") or user32.FindWindowW("#32770", None)


def cancel_file_dialog():
    dlg = find_file_dialog()
    if not dlg:
        return False
    for b in enum_children(dlg, "Button"):
        if "取消" in get_win_text(b, 64):
            user32.SendMessageW(b, BM_CLICK, 0, None)
            time.sleep(1.0)
            return True
    return False


def submit_files_to_dialog(paths, timeout=10.0):
    """Fill native Windows #32770 Open dialog with multi-file paths and click Open."""
    abs_paths = [os.path.abspath(p) for p in paths]
    for p in abs_paths:
        if not os.path.isfile(p):
            raise FileNotFoundError(p)

    dlg = None
    deadline = time.time() + timeout
    while time.time() < deadline:
        dlg = find_file_dialog()
        if dlg:
            break
        time.sleep(0.5)
    if not dlg:
        raise RuntimeError("Windows #32770 file dialog did not appear; check upload coordinate.")

    edits = enum_children(dlg, "Edit")
    if not edits:
        raise RuntimeError("Could not find Edit control in file dialog.")

    joined = " ".join(f'"{p}"' for p in abs_paths)
    set_win_text(edits[0], joined)
    time.sleep(0.6)
    last_name = os.path.basename(abs_paths[-1])
    if last_name not in get_win_text(edits[0]):
        raise RuntimeError(f"WM_SETTEXT verification failed: {last_name!r} not in Edit box.")

    for b in enum_children(dlg, "Button"):
        if "打开" in get_win_text(b, 64):
            user32.SendMessageW(b, BM_CLICK, 0, None)
            return dlg
    raise RuntimeError("Could not find '打开' button in file dialog.")


# ---------------- Screenshots & Calibration ----------------
def screenshot(path):
    from PIL import ImageGrab
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    img = ImageGrab.grab()
    img.save(path)
    return path


def crop_zoom(src_path, box, out_path, scale=2):
    from PIL import Image
    x1, y1, x2, y2 = box
    img = Image.open(src_path).crop((x1, y1, x2, y2))
    img = img.resize((img.width * scale, img.height * scale))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    img.save(out_path)
    return out_path
