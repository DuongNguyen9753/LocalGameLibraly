#!/usr/bin/env python3
"""
Local Game Library – Modern Steam-style game manager for Windows 11
With Collections support.
"""

import os
import sys
import json
import subprocess
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from datetime import datetime
import ctypes
import shutil
import time
import shlex
import base64
import urllib.request
import urllib.parse
import urllib.error
import threading
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional system-tray support (pip install pystray)
HAS_PYSTRAY = False
try:
    import pystray
    from PIL import Image as PILImage, ImageDraw as PILImageDraw
    HAS_PYSTRAY = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Paths & data
# ---------------------------------------------------------------------------

def get_app_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".local" / "share"
    path = base / "LocalGameLibrary"
    path.mkdir(parents=True, exist_ok=True)
    return path



# Default window/EXE icon (blue play button) — used if app.ico is missing
DEFAULT_ICO_B64 = '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'
DEFAULT_PNG_B64 = 'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABcUlEQVR4nO2bQZaCMBBEy3keQY8wXkyPpRfTI4x30FVvEAhg0lWd6b9EIKlPhWwQSJLkP7PbctHv+e9VeyI1eNyOq/OsukA1+JA1IhadGCX4kCUifkonRA0PLJv7rIDI4Y1ShkkBPYQ35rIUl0DvjAro6ekbU5myAcMDPT59YyxbNoA9ATYpoPUA9+uh9RBf4dIAZQluS+B+PUiKcH8HqEmgvASV2kDdBRQk0LdBdhvoAgyWBBkBAKcNUgIMTwmSAgC/NsgKMFpLkBcAtG1DCAFGCwmhBAD12xBOgFFLwr7KXZw5XZ7V7hWuATXDA4EaUDu4EaIBrcID4g1oGdyQbYBHeECwAV7BDRkB3sENiSXACg+QG8AMbtAaoBAeIDRAJbjh2gC18IBTAxSDG80boBweENkGmaQA9gTYfAjY8sl5FMayZQPGDvbYgqlM2YCpH3pqwVyW2Qb0IKGUobgEIktYMvf809SWAVRFRG5rkiQc3liUdcxMt1GNAAAAAElFTkSuQmCC'

LIBRARY_FILE = get_app_data_dir() / "library.json"
COVERS_DIR = get_app_data_dir() / "covers"
COVERS_DIR.mkdir(exist_ok=True)


def purge_ra_image_caches():
    """Permanently delete temporary RA badge/icon download folders."""
    base = get_app_data_dir()
    for name in ("ra_badges", "ra_icons"):
        folder = base / name
        if not folder.exists():
            continue
        try:
            shutil.rmtree(folder, ignore_errors=True)
        except Exception:
            pass


def fetch_image_bytes(url: str, timeout: int = 12) -> bytes | None:
    """Download image bytes for one-time use (no disk cache)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "LocalGameLibrary/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        return data if data and len(data) > 50 else None
    except Exception:
        return None


def load_data() -> dict:
    """Load games + collections + RA settings. Migrates old formats."""
    default = {
        "games": [],
        "collections": [],
        "ra": {"username": "", "api_key": ""},
        "settings": {"start_with_windows": False, "collapsed_collections": []},
    }
    if not LIBRARY_FILE.exists():
        return default
    try:
        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for g in data:
                g.setdefault("collections", [])
                g.setdefault("launch_options", "")
                g.setdefault("ra_game_id", None)
                g.setdefault("ra_display_set_id", None)
                g.setdefault("cover_mode", "fill")
                g.setdefault("system", "")
                g.setdefault("playtime_seconds", 0)
                g.setdefault("last_played", None)
            return {
                "games": data,
                "collections": [],
                "ra": {"username": "", "api_key": ""},
                "settings": {"start_with_windows": False, "collapsed_collections": []},
            }
        data.setdefault("games", [])
        data.setdefault("collections", [])
        data.setdefault("ra", {"username": "", "api_key": ""})
        data.setdefault("settings", {"start_with_windows": False, "collapsed_collections": []})
        data["settings"].setdefault("start_with_windows", False)
        data["settings"].setdefault("collapsed_collections", [])
        for g in data["games"]:
            g.setdefault("collections", [])
            g.setdefault("launch_options", "")
            g.setdefault("ra_game_id", None)
            g.setdefault("ra_display_set_id", None)
            g.setdefault("cover_mode", "fill")
            g.setdefault("system", "")
            g.setdefault("playtime_seconds", 0)
            g.setdefault("last_played", None)
        for i, c in enumerate(data["collections"]):
            c.setdefault("parent_id", None)
            if "sort_order" not in c:
                c["sort_order"] = i
        return data
    except Exception:
        return default


STARTUP_REG_NAME = "LocalGameLibrary"


def get_app_launch_command(extra_args: str = "") -> str:
    """Command line used for Windows startup / shortcuts."""
    extra = f" {extra_args.strip()}" if extra_args.strip() else ""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"{extra}'
    script = str(Path(__file__).resolve())
    return f'"{sys.executable}" "{script}"{extra}'


def is_start_with_windows_enabled() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
        ) as key:
            val, _ = winreg.QueryValueEx(key, STARTUP_REG_NAME)
            return bool(val)
    except Exception:
        return False


def set_start_with_windows(enabled: bool) -> tuple[bool, str]:
    """
    Enable/disable Start with Windows.
    Startup entry always includes --tray so the app opens in the system tray.
    """
    if sys.platform != "win32":
        return False, "Start with Windows is only available on Windows."
    try:
        import winreg
        path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        if enabled:
            cmd = get_app_launch_command("--tray")
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, STARTUP_REG_NAME, 0, winreg.REG_SZ, cmd)
            return True, "Will start with Windows in system tray."
        else:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, STARTUP_REG_NAME)
            except FileNotFoundError:
                pass
            return True, "Removed from Windows startup."
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# RetroAchievements API
# ---------------------------------------------------------------------------

RA_API_BASE = "https://retroachievements.org/API"
RA_MEDIA = "https://media.retroachievements.org"


class RAClient:
    def __init__(self, username: str, api_key: str):
        self.username = username.strip()
        self.api_key = api_key.strip()

    def _get(self, endpoint: str, params: dict) -> dict | list | None:
        params = {**params, "y": self.api_key}
        qs = urllib.parse.urlencode(params)
        url = f"{RA_API_BASE}/{endpoint}?{qs}"
        req = urllib.request.Request(url, headers={"User-Agent": "LocalGameLibrary/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                if not raw or raw in ("{}", "[]", "null"):
                    return None
                return json.loads(raw)
        except Exception as e:
            raise RuntimeError(str(e)) from e

    def validate(self) -> dict:
        """Validate credentials via user profile. Returns profile or raises."""
        data = self._get("API_GetUserProfile.php", {"u": self.username})
        if not data or not data.get("User"):
            raise RuntimeError("Invalid username or API key")
        return data

    def get_game_progress(self, game_id: int) -> dict:
        data = self._get("API_GetGameInfoAndUserProgress.php", {
            "g": game_id,
            "u": self.username,
        })
        if not data:
            raise RuntimeError("Game not found or API error")
        return data

    def get_game(self, game_id: int) -> dict:
        data = self._get("API_GetGame.php", {"i": game_id})
        if not data:
            raise RuntimeError("Game not found")
        return data

    def find_subsets(self, parent_game_id: int) -> list[dict]:
        """
        Find RA subset sets linked to a parent game.
        Returns [{id, title, console}, ...] excluding the parent itself.
        """
        import re
        parent_id = int(parent_game_id)
        try:
            info = self.get_game_progress(parent_id)
        except Exception:
            try:
                info = self.get_game(parent_id)
            except Exception:
                return []

        title = info.get("Title") or info.get("GameTitle") or info.get("title") or ""
        console_id = info.get("ConsoleID") or info.get("consoleId")
        if not title or console_id is None:
            return []

        # If this ID is already a subset, resolve to the parent when possible
        parent_of = info.get("ParentGameID") or info.get("parentGameId")
        if parent_of:
            try:
                parent_of = int(parent_of)
                if parent_of and parent_of != parent_id:
                    return self.find_subsets(parent_of)
            except Exception:
                pass

        base = re.sub(r"\s*\[Subset[^\]]*\]\s*", "", title, flags=re.I).strip()
        base_l = base.lower()
        if not base_l:
            return []

        try:
            catalog = self.get_game_list(int(console_id))
        except Exception:
            return []

        subsets = []
        seen = {parent_id}
        for g in catalog:
            gid = g.get("id")
            t = g.get("title") or ""
            if gid is None or not t:
                continue
            gid = int(gid)
            if gid in seen:
                continue
            if "[subset" not in t.lower():
                continue
            t_base = re.sub(r"\s*\[Subset[^\]]*\]\s*", "", t, flags=re.I).strip()
            # Same base game name
            if t_base.lower() != base_l and not t.lower().startswith(base_l):
                continue
            seen.add(gid)
            # Prefer short subset label for tabs
            m = re.search(r"\[Subset\s*[-–—]?\s*([^\]]+)\]", t, flags=re.I)
            label = m.group(1).strip() if m else t
            subsets.append({
                "id": gid,
                "title": t,
                "label": label,
                "console": g.get("console") or "",
            })
        subsets.sort(key=lambda x: x.get("label", "").lower())
        return subsets

    def get_consoles(self) -> list[dict]:
        data = self._get("API_GetConsoleIDs.php", {})
        if not data:
            return []
        out = []
        for item in data:
            cid = item.get("ID") or item.get("id")
            name = item.get("Name") or item.get("name") or str(cid)
            if cid is not None:
                out.append({"id": int(cid), "name": str(name)})
        out.sort(key=lambda x: x["name"].lower())
        return out

    def get_game_list(self, console_id: int) -> list[dict]:
        cache_dir = get_app_data_dir() / "ra_cache"
        cache_dir.mkdir(exist_ok=True)
        cache_file = cache_dir / f"console_{console_id}.json"
        if cache_file.exists():
            age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if age < 7 * 24 * 3600:
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        data = self._get("API_GetGameList.php", {"i": console_id, "f": 1})
        if not data:
            return []
        results = []
        for g in data:
            gid = g.get("ID") or g.get("id")
            title = g.get("Title") or g.get("title") or ""
            console = g.get("ConsoleName") or g.get("consoleName") or ""
            icon = g.get("ImageIcon") or g.get("imageIcon") or ""
            if gid is None or not title:
                continue
            results.append({
                "id": int(gid),
                "title": title,
                "console": console,
                "icon": icon,
            })
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(results, f)
        except Exception:
            pass
        return results

    def search_user_games(self, query: str, limit: int = 30) -> list[dict]:
        q = query.strip().lower()
        results = []
        seen = set()
        try:
            recent = self._get("API_GetUserRecentlyPlayedGames.php", {
                "u": self.username, "c": 50,
            }) or []
            for g in recent:
                gid = g.get("GameID") or g.get("gameId") or g.get("ID")
                title = g.get("Title") or g.get("title") or ""
                console = g.get("ConsoleName") or g.get("consoleName") or ""
                if gid is None:
                    continue
                if q and q not in title.lower():
                    continue
                gid = int(gid)
                if gid in seen:
                    continue
                seen.add(gid)
                results.append({"id": gid, "title": title, "console": console})
        except Exception:
            pass
        try:
            prog = self._get("API_GetUserCompletionProgress.php", {
                "u": self.username, "c": 100,
            }) or {}
            results_list = prog if isinstance(prog, list) else (
                prog.get("Results") or prog.get("results") or []
            )
            for g in results_list:
                gid = g.get("GameID") or g.get("gameId") or g.get("ID") or g.get("id")
                title = g.get("Title") or g.get("title") or ""
                console = g.get("ConsoleName") or g.get("consoleName") or ""
                if gid is None:
                    continue
                if q and q not in title.lower():
                    continue
                gid = int(gid)
                if gid in seen:
                    continue
                seen.add(gid)
                results.append({"id": gid, "title": title, "console": console})
                if len(results) >= limit:
                    break
        except Exception:
            pass
        return results[:limit]

    # Popular consoles to search when no system is selected
    POPULAR_CONSOLES = [
        12,  # PlayStation
        21,  # PlayStation 2
        3,   # SNES
        7,   # NES
        6,   # GBA
        4,   # GB
        5,   # GBC
        1,   # Mega Drive
        2,   # N64
        11,  # Master System
        8,   # PC Engine
        15,  # Game Gear
        27,  # Arcade
        28,  # Virtual Boy
        18,  # Nintendo DS
        13,  # Atari Lynx
    ]

    def search_games(self, query: str, console_id: int | None = None, limit: int = 40) -> list[dict]:
        q = query.strip().lower()
        if len(q) < 2:
            return []
        results = []
        seen = set()

        for r in self.search_user_games(query, limit=limit):
            if r["id"] not in seen:
                seen.add(r["id"])
                results.append(r)

        consoles = [int(console_id)] if console_id is not None else list(self.POPULAR_CONSOLES)

        def search_console(cid):
            found = []
            try:
                catalog = self.get_game_list(cid)
                for g in catalog:
                    if q not in g.get("title", "").lower():
                        continue
                    found.append(g)
            except Exception:
                pass
            return found

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(search_console, cid): cid for cid in consoles}
            for fut in as_completed(futures):
                for g in fut.result():
                    gid = g["id"]
                    if gid in seen:
                        continue
                    seen.add(gid)
                    results.append(g)
                    if len(results) >= limit:
                        break
                if len(results) >= limit:
                    break

        # Prefer non-hack titles first
        def sort_key(item):
            t = item.get("title", "")
            hack = 1 if t.startswith("~") else 0
            return (hack, t.lower())
        results.sort(key=sort_key)
        return results[:limit]


def save_data(data: dict):
    with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Optional Pillow
# ---------------------------------------------------------------------------

HAS_PIL = False
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    pass


def photo_from_bytes(data: bytes, size: int | None = None):
    """
    Build a Tk PhotoImage from raw bytes without keeping a permanent cache file.
    Uses Pillow when available; otherwise a short-lived temp file that is deleted.
    """
    if not data:
        return None
    if HAS_PIL:
        from io import BytesIO
        pil = Image.open(BytesIO(data)).convert("RGBA")
        if size:
            pil = pil.resize((size, size), Image.LANCZOS)
        return ImageTk.PhotoImage(pil)

    import tempfile
    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.write(data)
        tmp.close()
        photo = tk.PhotoImage(file=tmp.name)
        if size:
            while photo.width() > size or photo.height() > size:
                photo = photo.subsample(2, 2)
        return photo
    except Exception:
        return None
    finally:
        if tmp is not None:
            try:
                Path(tmp.name).unlink(missing_ok=True)
            except Exception:
                pass


def prepare_cover_image(path: str | Path, target_w: int, target_h: int,
                        mode: str = "fill"):
    """
    Load and resize a cover image according to mode.
    Returns a PhotoImage (PIL-backed when available) or None on failure.

    Modes:
      - fill:    scale to cover the area, center-crop (no letterbox)
      - fit:     scale to fit entirely inside, letterbox with dark bg
      - stretch: force exact size (may distort)
    """
    path = Path(path)
    if not path.exists():
        return None
    mode = (mode or "fill").lower()
    if mode not in ("fill", "fit", "stretch"):
        mode = "fill"

    if not HAS_PIL:
        try:
            img = tk.PhotoImage(file=str(path))
            while img.width() > target_w * 2 or img.height() > target_h * 2:
                img = img.subsample(2, 2)
            return img
        except Exception:
            return None

    try:
        # Open via binary handle — more reliable with non-ASCII Windows paths
        with open(path, "rb") as fh:
            src = Image.open(fh).convert("RGB")
            # Fully load while file handle is open
            src.load()
        sw, sh = src.size
        if sw < 1 or sh < 1:
            return None

        if mode == "stretch":
            out = src.resize((target_w, target_h), Image.LANCZOS)
        elif mode == "fit":
            scale = min(target_w / sw, target_h / sh)
            nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
            resized = src.resize((nw, nh), Image.LANCZOS)
            out = Image.new("RGB", (target_w, target_h), (26, 35, 50))  # SURFACE2-ish
            out.paste(resized, ((target_w - nw) // 2, (target_h - nh) // 2))
        else:  # fill — cover + center crop
            scale = max(target_w / sw, target_h / sh)
            nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
            resized = src.resize((nw, nh), Image.LANCZOS)
            left = max(0, (nw - target_w) // 2)
            top = max(0, (nh - target_h) // 2)
            out = resized.crop((left, top, left + target_w, top + target_h))
            # Guard against off-by-one size from rounding
            if out.size != (target_w, target_h):
                out = out.resize((target_w, target_h), Image.LANCZOS)

        return ImageTk.PhotoImage(out)
    except Exception:
        return None


# Short labels for system badge on covers
SYSTEM_SHORT = {
    "playstation": "PS1",
    "playstation 2": "PS2",
    "playstation portable": "PSP",
    "playstation vita": "Vita",
    "nintendo 64": "N64",
    "nintendo entertainment system": "NES",
    "super nintendo entertainment system": "SNES",
    "snes": "SNES",
    "game boy": "GB",
    "game boy color": "GBC",
    "game boy advance": "GBA",
    "nintendo ds": "NDS",
    "nintendo 3ds": "3DS",
    "nintendo gamecube": "GCN",
    "wii": "Wii",
    "wii u": "Wii U",
    "mega drive": "MD",
    "genesis": "MD",
    "master system": "SMS",
    "game gear": "GG",
    "sega cd": "Sega CD",
    "sega saturn": "Saturn",
    "dreamcast": "DC",
    "pc engine": "PCE",
    "turbografx-16": "TG16",
    "neo geo": "Neo Geo",
    "arcade": "Arcade",
    "atari 2600": "2600",
    "atari lynx": "Lynx",
    "virtual boy": "VB",
    "wonderswan": "WS",
    "wonderswan color": "WSC",
    "msx": "MSX",
    "pc-8000/8800": "PC-88",
    "pc-9800": "PC-98",
    "xbox": "Xbox",
    "xbox 360": "X360",
    "steam": "PC",
    "windows": "PC",
    "pc": "PC",
}


def short_system_name(name: str) -> str:
    """Compact label for the cover badge."""
    if not name:
        return ""
    key = name.strip().lower()
    if key in SYSTEM_SHORT:
        return SYSTEM_SHORT[key]
    # Already short
    if len(name) <= 10:
        return name
    return name[:9] + "…"


def format_playtime(seconds) -> str:
    """Human-readable playtime."""
    try:
        seconds = int(seconds or 0)
    except (TypeError, ValueError):
        seconds = 0
    if seconds <= 0:
        return "0m"
    minutes = seconds // 60
    hours, minutes = divmod(minutes, 60)
    if hours and minutes:
        return f"{hours}h {minutes}m"
    if hours:
        return f"{hours}h"
    return f"{minutes}m"


def format_last_played(iso) -> str:
    """Human-readable last played timestamp."""
    if not iso:
        return "Never"
    try:
        dt = datetime.fromisoformat(str(iso))
    except Exception:
        return "—"
    now = datetime.now()
    delta = now - dt
    days = delta.days
    if days < 0:
        return dt.strftime("%Y-%m-%d")
    if days == 0:
        return f"Today {dt.strftime('%H:%M')}"
    if days == 1:
        return "Yesterday"
    if days < 7:
        return f"{days}d ago"
    if days < 30:
        weeks = days // 7
        return f"{weeks}w ago"
    return dt.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

class Theme:
    BG           = "#0f1419"
    SURFACE      = "#1a2332"
    SURFACE2     = "#243044"
    BORDER       = "#2d3a4f"
    ACCENT       = "#3b82f6"
    ACCENT_HOV   = "#60a5fa"
    ACCENT_DIM   = "#1e3a5f"
    TEXT         = "#e8eef7"
    TEXT_MUTED   = "#8b9bb4"
    SUCCESS      = "#22c55e"
    DANGER       = "#ef4444"
    SIDEBAR      = "#121a24"
    SIDEBAR_HOV  = "#1c2838"
    SIDEBAR_SEL  = "#1e3a5f"
    SCROLL_THUMB = "#3d4f6a"
    SCROLL_THUMB_HOV = "#5a6f8f"
    SCROLL_TROUGH = "#141b24"
    GLOW_SOFT    = "#1e3a5f"
    GLOW_MID     = "#2563eb"
    GLOW_CORE    = "#60a5fa"


def themed_input(parent, title: str, prompt: str, initial: str = "",
                 width: int = 440, height: int = 220) -> str | None:
    """Modern dark-themed single-line input dialog. Returns text or None if cancelled."""
    result = {"value": None}

    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry(f"{width}x{height}")
    win.minsize(360, 180)
    win.configure(bg=Theme.SURFACE)
    win.transient(parent)
    win.grab_set()
    win.resizable(False, False)

    # Center over parent
    try:
        parent.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        win.geometry(f"+{max(0, px)}+{max(0, py)}")
    except Exception:
        pass

    body = tk.Frame(win, bg=Theme.SURFACE)
    body.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

    tk.Label(body, text=title, font=("Segoe UI", 13, "bold"),
             bg=Theme.SURFACE, fg=Theme.TEXT).pack(anchor="w")
    tk.Label(body, text=prompt, font=("Segoe UI", 9),
             bg=Theme.SURFACE, fg=Theme.TEXT_MUTED, justify="left",
             wraplength=width - 60).pack(anchor="w", pady=(6, 12))

    entry_wrap = tk.Frame(body, bg=Theme.SURFACE2, highlightthickness=1,
                          highlightbackground=Theme.BORDER)
    entry_wrap.pack(fill=tk.X)
    var = tk.StringVar(value=initial)
    entry = tk.Entry(entry_wrap, textvariable=var, bg=Theme.SURFACE2, fg=Theme.TEXT,
                     insertbackground=Theme.TEXT, relief="flat", font=("Segoe UI", 11))
    entry.pack(fill=tk.X, ipady=10, padx=10)
    entry.bind("<FocusIn>", lambda e: entry_wrap.configure(highlightbackground=Theme.ACCENT))
    entry.bind("<FocusOut>", lambda e: entry_wrap.configure(highlightbackground=Theme.BORDER))

    btn_row = tk.Frame(body, bg=Theme.SURFACE)
    btn_row.pack(fill=tk.X, pady=(18, 0))

    def ok(_e=None):
        result["value"] = var.get()
        win.destroy()

    def cancel(_e=None):
        result["value"] = None
        win.destroy()

    ok_btn = tk.Button(btn_row, text="OK", font=("Segoe UI", 10, "bold"),
                       bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
                       width=10, pady=7, command=ok,
                       activebackground=Theme.ACCENT_HOV, activeforeground="white")
    ok_btn.pack(side=tk.RIGHT)
    cancel_btn = tk.Button(btn_row, text="Cancel", font=("Segoe UI", 10),
                           bg=Theme.SURFACE2, fg=Theme.TEXT, relief="flat", cursor="hand2",
                           width=10, pady=7, command=cancel,
                           activebackground=Theme.BORDER, activeforeground=Theme.TEXT)
    cancel_btn.pack(side=tk.RIGHT, padx=(0, 8))

    win.bind("<Return>", ok)
    win.bind("<Escape>", cancel)
    entry.focus_set()
    entry.select_range(0, tk.END)
    win.wait_window()
    return result["value"]


def themed_confirm(parent, title: str, message: str) -> bool:
    """Modern dark yes/no dialog."""
    result = {"ok": False}
    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry("420x200")
    win.configure(bg=Theme.SURFACE)
    win.transient(parent)
    win.grab_set()
    win.resizable(False, False)
    try:
        parent.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() - 420) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - 200) // 2
        win.geometry(f"+{max(0, px)}+{max(0, py)}")
    except Exception:
        pass

    body = tk.Frame(win, bg=Theme.SURFACE)
    body.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)
    tk.Label(body, text=title, font=("Segoe UI", 13, "bold"),
             bg=Theme.SURFACE, fg=Theme.TEXT).pack(anchor="w")
    tk.Label(body, text=message, font=("Segoe UI", 10),
             bg=Theme.SURFACE, fg=Theme.TEXT_MUTED, justify="left",
             wraplength=360).pack(anchor="w", pady=(10, 16))

    btn_row = tk.Frame(body, bg=Theme.SURFACE)
    btn_row.pack(fill=tk.X)

    def yes():
        result["ok"] = True
        win.destroy()

    def no():
        result["ok"] = False
        win.destroy()

    tk.Button(btn_row, text="Yes", font=("Segoe UI", 10, "bold"),
              bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
              width=10, pady=7, command=yes).pack(side=tk.RIGHT)
    tk.Button(btn_row, text="No", font=("Segoe UI", 10),
              bg=Theme.SURFACE2, fg=Theme.TEXT, relief="flat", cursor="hand2",
              width=10, pady=7, command=no).pack(side=tk.RIGHT, padx=(0, 8))
    win.bind("<Escape>", lambda e: no())
    win.wait_window()
    return result["ok"]


# ---------------------------------------------------------------------------
# Modern scrollbar
# ---------------------------------------------------------------------------

class ModernScrollbar(tk.Canvas):
    def __init__(self, parent, command=None, **kwargs):
        super().__init__(parent, width=10, bg=Theme.SCROLL_TROUGH,
                         highlightthickness=0, bd=0, **kwargs)
        self.command = command
        self._start = 0.0
        self._end = 1.0
        self._dragging = False
        self._drag_start_y = 0
        self._drag_start_pos = 0.0
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", lambda e: self._draw(hover=True))
        self.bind("<Leave>", lambda e: self._draw(hover=False))
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, start, end):
        self._start = float(start)
        self._end = float(end)
        self._draw()

    def _draw(self, hover=False):
        self.delete("all")
        h = self.winfo_height()
        w = self.winfo_width()
        if h <= 1:
            return
        if self._start <= 0.001 and self._end >= 0.999:
            return
        thumb_h = max(30, (self._end - self._start) * h)
        thumb_y = self._start * h
        color = Theme.SCROLL_THUMB_HOV if hover or self._dragging else Theme.SCROLL_THUMB
        r = 4
        self.create_rectangle(2, thumb_y + r, w - 2, thumb_y + thumb_h - r, fill=color, outline="")
        self.create_oval(2, thumb_y, w - 2, thumb_y + 2 * r, fill=color, outline="")
        self.create_oval(2, thumb_y + thumb_h - 2 * r, w - 2, thumb_y + thumb_h, fill=color, outline="")

    def _on_click(self, event):
        h = self.winfo_height()
        thumb_h = max(30, (self._end - self._start) * h)
        thumb_y = self._start * h
        if thumb_y <= event.y <= thumb_y + thumb_h:
            self._dragging = True
            self._drag_start_y = event.y
            self._drag_start_pos = self._start
        else:
            if self.command:
                self.command("moveto", event.y / h)
        self._draw(hover=True)

    def _on_drag(self, event):
        if not self._dragging:
            return
        h = self.winfo_height()
        delta = (event.y - self._drag_start_y) / h
        new_pos = max(0.0, min(1.0 - (self._end - self._start), self._drag_start_pos + delta))
        if self.command:
            self.command("moveto", new_pos)

    def _on_release(self, event):
        self._dragging = False
        self._draw()


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------

class LocalGameLibrary(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Local Game Library")
        self.geometry("1280x760")
        self.minsize(1000, 620)
        self.configure(bg=Theme.BG)

        if sys.platform == "win32":
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass

        # Detect tray boot early (before maximize flash)
        _tray_boot = any(
            a in ("--tray", "--startup", "/tray", "/startup")
            for a in sys.argv[1:]
        )
        if not _tray_boot:
            try:
                self.state("zoomed")  # Windows / some Linux
            except Exception:
                try:
                    self.attributes("-zoomed", True)  # other Linux
                except Exception:
                    pass

        self.data = load_data()
        self.games = self.data["games"]
        self.collections = self.data["collections"]
        for i, c in enumerate(self.collections):
            if "sort_order" not in c:
                c["sort_order"] = i
        self._col_drag = None  # sidebar drag-reorder state
        self.ra = self.data.get("ra", {"username": "", "api_key": ""})
        self.settings = self.data.setdefault("settings", {"start_with_windows": False})
        self.current_collection = None  # None = All Games
        self.filtered_games = self.games.copy()
        self.card_images = {}
        self._sidebar_btns = {}
        self._ra_badge_images = {}
        # Active play sessions: game_id -> {pid, start, game}
        self._play_sessions: dict = {}
        self._icon_path = None
        self._icon_photo = None
        self._tray_icon = None
        self._tray_thread = None
        self._really_quit = False
        # --tray / --startup → start hidden in system tray
        self._start_in_tray = any(
            a in ("--tray", "--startup", "/tray", "/startup")
            for a in sys.argv[1:]
        )

        self._setup_styles()
        self._build_ui()
        self.refresh_sidebar()
        self._last_cols = None
        self._reflow_after = None
        # Drop any leftover RA badge/icon disk caches (download only when used)
        purge_ra_image_caches()
        # Icon must be applied after the HWND exists (Windows)
        self.after(10, self._set_app_icon)
        self.after(300, self._set_app_icon)  # again after maximize settles
        # Defer first layout until the window is sized (esp. maximized)
        self.after(50, self._initial_layout)
        self.after(15000, self._poll_play_sessions)
        self.protocol("WM_DELETE_WINDOW", self._on_app_close)
        if self._start_in_tray:
            # Hide immediately, then park in the tray once UI is ready
            try:
                self.withdraw()
            except Exception:
                pass
            self.after(80, self._boot_to_tray)

    def _app_dir(self) -> Path:
        """Folder containing the script, or the frozen EXE."""
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parent

    def _resolve_icon_path(self) -> Path | None:
        """Find app.ico next to the app, or extract the embedded default."""
        candidates = []
        try:
            # Prefer real app.ico beside the script / EXE (user can replace this file)
            candidates.append(self._app_dir() / "app.ico")
        except Exception:
            pass
        try:
            candidates.append(Path.cwd() / "app.ico")
        except Exception:
            pass
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "app.ico")
        try:
            candidates.append(get_app_data_dir() / "app.ico")
        except Exception:
            pass

        for p in candidates:
            try:
                if p and p.is_file() and p.stat().st_size > 100:
                    return p.resolve()
            except Exception:
                pass

        # No app.ico found — write embedded default beside the script, then app data
        raw = None
        try:
            raw = base64.b64decode(DEFAULT_ICO_B64)
        except Exception:
            raw = None
        if not raw or len(raw) < 100:
            return None

        for dest in (self._app_dir() / "app.ico", get_app_data_dir() / "app.ico"):
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
                if dest.is_file() and dest.stat().st_size > 100:
                    return dest.resolve()
            except Exception:
                continue
        return None

    def _set_app_icon_winapi(self, icon_path: Path) -> bool:
        """Force window icon via Win32 WM_SETICON (most reliable on Windows)."""
        if sys.platform != "win32":
            return False
        try:
            user32 = ctypes.windll.user32
            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x0010
            LR_DEFAULTSIZE = 0x0040
            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1

            path = str(icon_path.resolve())
            # Load large + small icons
            hicon_big = user32.LoadImageW(
                None, path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE
            )
            hicon_small = user32.LoadImageW(
                None, path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE
            )
            if not hicon_big and not hicon_small:
                # Let system pick size
                hicon_big = user32.LoadImageW(
                    None, path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE
                )
            if not hicon_big and not hicon_small:
                return False

            # Tk child HWND → real top-level frame
            hwnd = self.winfo_id()
            parent = user32.GetParent(hwnd)
            if parent:
                hwnd = parent

            if hicon_big:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
            if hicon_small:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
            elif hicon_big:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_big)
            return True
        except Exception:
            return False

    def _set_app_icon(self):
        """Set window / taskbar icon from app.ico (Tk + Win32)."""
        icon_path = self._resolve_icon_path()
        self._icon_path = icon_path
        if icon_path is None:
            return

        ico = str(icon_path)

        # 1) Classic Tk .ico methods
        try:
            self.iconbitmap(default=ico)
        except Exception:
            try:
                self.iconbitmap(ico)
            except Exception:
                pass

        # 2) iconphoto — convert .ico via Pillow when available (sharper on some setups)
        try:
            if HAS_PIL:
                from PIL import Image as _PILImage, ImageTk as _ImageTk
                pil = _PILImage.open(ico)
                # Prefer largest frame in multi-size ICO
                try:
                    best = 0
                    best_area = 0
                    i = 0
                    while True:
                        pil.seek(i)
                        area = pil.size[0] * pil.size[1]
                        if area > best_area:
                            best_area = area
                            best = i
                        i += 1
                except EOFError:
                    pass
                pil.seek(best)
                frame = pil.convert("RGBA")
                # Reasonable size for title bar / taskbar
                if max(frame.size) > 64:
                    frame.thumbnail((64, 64), _PILImage.LANCZOS)
                img = _ImageTk.PhotoImage(frame)
                self.iconphoto(True, img)
                self._icon_photo = img
            else:
                # Fallback PNG only if we cannot read the ico
                png_path = get_app_data_dir() / "app_icon.png"
                if not png_path.is_file():
                    png_path.write_bytes(base64.b64decode(DEFAULT_PNG_B64))
                img = tk.PhotoImage(file=str(png_path))
                self.iconphoto(True, img)
                self._icon_photo = img
        except Exception:
            pass

        # 3) Win32 API — most reliable for title-bar + taskbar on Windows
        self._set_app_icon_winapi(icon_path)

    def _initial_layout(self):
        try:
            self.update_idletasks()
        except Exception:
            pass
        self.refresh_library()

    def _grid_columns(self, width: int | None = None) -> int:
        """How many game cards fit in a row for the current canvas width."""
        if width is None:
            try:
                width = self.canvas.winfo_width()
            except Exception:
                width = 0
        # Card is ~200px + padding ≈ 220px per column
        if not width or width < 50:
            return 4
        return max(1, min(8, int(width) // 220))

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=Theme.BG, foreground=Theme.TEXT, font=("Segoe UI", 10))
        style.configure("TFrame", background=Theme.BG)
        style.configure("TLabel", background=Theme.BG, foreground=Theme.TEXT)

    def _save(self):
        self.data["games"] = self.games
        self.data["collections"] = self.collections
        self.data["ra"] = self.ra
        self.data["settings"] = self.settings
        save_data(self.data)

    def _boot_to_tray(self):
        """Used when launched with --tray (Windows startup)."""
        try:
            self.withdraw()
        except Exception:
            pass
        if not HAS_PYSTRAY:
            # No tray support — show window instead of being invisible forever
            try:
                self.deiconify()
            except Exception:
                pass
            return
        self._ensure_tray()
        try:
            self.status_var.set("Started in system tray")
        except Exception:
            pass

    def _ra_client(self) -> RAClient | None:
        u = (self.ra.get("username") or "").strip()
        k = (self.ra.get("api_key") or "").strip()
        if not u or not k:
            return None
        return RAClient(u, k)

    # ------------------------------------------------------------------
    def _build_ui(self):
        # ===== HEADER =====
        header = tk.Frame(self, bg=Theme.SURFACE, height=64)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_inner = tk.Frame(header, bg=Theme.SURFACE)
        header_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        title_frame = tk.Frame(header_inner, bg=Theme.SURFACE)
        title_frame.pack(side=tk.LEFT)
        tk.Label(title_frame, text="◈", font=("Segoe UI", 20),
                 bg=Theme.SURFACE, fg=Theme.ACCENT).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(title_frame, text="Local Game Library",
                 font=("Segoe UI", 15, "bold"),
                 bg=Theme.SURFACE, fg=Theme.TEXT).pack(side=tk.LEFT)

        controls = tk.Frame(header_inner, bg=Theme.SURFACE)
        controls.pack(side=tk.RIGHT)

        # Search
        search_wrap = tk.Frame(controls, bg=Theme.SURFACE2, highlightthickness=1,
                               highlightbackground=Theme.BORDER)
        search_wrap.pack(side=tk.LEFT, padx=(0, 12))
        tk.Label(search_wrap, text="  🔍", bg=Theme.SURFACE2,
                 fg=Theme.TEXT_MUTED, font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.apply_filter())
        search_entry = tk.Entry(
            search_wrap, textvariable=self.search_var,
            bg=Theme.SURFACE2, fg=Theme.TEXT, insertbackground=Theme.TEXT,
            relief="flat", font=("Segoe UI", 11), width=24
        )
        search_entry.pack(side=tk.LEFT, ipady=7, padx=(0, 10))
        search_entry.bind("<FocusIn>", lambda e: search_wrap.configure(highlightbackground=Theme.ACCENT))
        search_entry.bind("<FocusOut>", lambda e: search_wrap.configure(highlightbackground=Theme.BORDER))

        # Settings (startup / tray)
        self.settings_btn = tk.Button(
            controls, text="  ⚙  ",
            font=("Segoe UI", 10, "bold"),
            bg=Theme.SURFACE2, fg=Theme.TEXT,
            activebackground=Theme.BORDER, activeforeground=Theme.TEXT,
            relief="flat", cursor="hand2", padx=6, pady=5,
            command=self.show_app_settings
        )
        self.settings_btn.pack(side=tk.LEFT, padx=(0, 8))

        # RA Login — purple button, top bar (left of Add Game)
        self.ra_btn = tk.Button(
            controls, text="  🏆  RA Login  ",
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed", fg="white",
            activebackground="#8b5cf6", activeforeground="white",
            relief="flat", cursor="hand2", padx=6, pady=5,
            command=self.show_ra_settings
        )
        self.ra_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._update_ra_btn()

        # Add Game
        self.add_btn = tk.Button(
            controls, text="  ＋  Add Game  ",
            font=("Segoe UI", 10, "bold"),
            bg=Theme.ACCENT, fg="white",
            activebackground=Theme.ACCENT_HOV, activeforeground="white",
            relief="flat", cursor="hand2", padx=4, pady=5,
            command=self.add_game
        )
        self.add_btn.pack(side=tk.LEFT)
        self.add_btn.bind("<Enter>", lambda e: self.add_btn.configure(bg=Theme.ACCENT_HOV))
        self.add_btn.bind("<Leave>", lambda e: self.add_btn.configure(bg=Theme.ACCENT))

        # ===== BODY: sidebar + content =====
        body = tk.Frame(self, bg=Theme.BG)
        body.pack(fill=tk.BOTH, expand=True)

        # --- Sidebar ---
        sidebar = tk.Frame(body, bg=Theme.SIDEBAR, width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Sidebar header
        sb_head = tk.Frame(sidebar, bg=Theme.SIDEBAR)
        sb_head.pack(fill=tk.X, padx=14, pady=(16, 8))
        tk.Label(sb_head, text="COLLECTIONS", font=("Segoe UI", 9, "bold"),
                 bg=Theme.SIDEBAR, fg=Theme.TEXT_MUTED).pack(side=tk.LEFT)
        new_col_btn = tk.Label(
            sb_head, text="＋", font=("Segoe UI", 14, "bold"),
            bg=Theme.SIDEBAR, fg=Theme.ACCENT, cursor="hand2"
        )
        new_col_btn.pack(side=tk.RIGHT)
        new_col_btn.bind("<Button-1>", lambda e: self.create_collection())
        new_col_btn.bind("<Enter>", lambda e: new_col_btn.configure(fg=Theme.ACCENT_HOV))
        new_col_btn.bind("<Leave>", lambda e: new_col_btn.configure(fg=Theme.ACCENT))

        # Scrollable sidebar list
        self.sidebar_canvas = tk.Canvas(sidebar, bg=Theme.SIDEBAR, highlightthickness=0)
        self.sidebar_frame = tk.Frame(self.sidebar_canvas, bg=Theme.SIDEBAR)
        self.sidebar_canvas.create_window((0, 0), window=self.sidebar_frame, anchor="nw", tags="sb")
        self.sidebar_frame.bind("<Configure>", lambda e: (
            self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all")),
            self.sidebar_canvas.itemconfig("sb", width=self.sidebar_canvas.winfo_width())
        ))
        self.sidebar_canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 8))
        self.sidebar_canvas.bind("<Configure>", lambda e: self.sidebar_canvas.itemconfig("sb", width=e.width))

        # --- Main content ---
        content = tk.Frame(body, bg=Theme.BG)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Collection title bar
        self.coll_title_var = tk.StringVar(value="All Games")
        title_bar = tk.Frame(content, bg=Theme.BG)
        title_bar.pack(fill=tk.X, padx=20, pady=(14, 4))
        tk.Label(title_bar, textvariable=self.coll_title_var,
                 font=("Segoe UI", 14, "bold"),
                 bg=Theme.BG, fg=Theme.TEXT).pack(side=tk.LEFT)

        # Games grid
        grid_wrap = tk.Frame(content, bg=Theme.BG)
        grid_wrap.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(grid_wrap, bg=Theme.BG, highlightthickness=0)
        self.scrollbar = ModernScrollbar(grid_wrap, command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg=Theme.BG)

        self.scrollable.bind("<Configure>", lambda e: self._update_scrollregion())
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0), pady=(0, 8))
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 8), padx=(4, 8))

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Status bar
        status_bar = tk.Frame(self, bg=Theme.SURFACE, height=34)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(status_bar, textvariable=self.status_var, bg=Theme.SURFACE,
                 fg=Theme.TEXT_MUTED, font=("Segoe UI", 9), anchor="w").pack(side=tk.LEFT, padx=16, pady=6)
        self.count_var = tk.StringVar(value="")
        tk.Label(status_bar, textvariable=self.count_var, bg=Theme.SURFACE,
                 fg=Theme.TEXT_MUTED, font=("Segoe UI", 9), anchor="e").pack(side=tk.RIGHT, padx=16, pady=6)

    # ------------------------------------------------------------------
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._update_scrollregion()
        # Reflow cards when the number of columns changes (resize / maximize)
        cols = self._grid_columns(event.width)
        if self._last_cols is not None and cols != self._last_cols:
            if self._reflow_after is not None:
                try:
                    self.after_cancel(self._reflow_after)
                except Exception:
                    pass
            self._reflow_after = self.after(80, self.refresh_library)
        self._last_cols = cols

    def _update_scrollregion(self):
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            content_height = bbox[3] - bbox[1]
            canvas_height = self.canvas.winfo_height()
            if content_height <= canvas_height:
                self.canvas.configure(scrollregion=(0, 0, bbox[2], canvas_height))
                self.canvas.yview_moveto(0)
            else:
                self.canvas.configure(scrollregion=bbox)

    def _on_mousewheel(self, event):
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        if bbox[3] - bbox[1] <= self.canvas.winfo_height():
            return
        current = self.canvas.yview()
        delta = int(-1 * (event.delta / 120))
        if delta < 0 and current[0] <= 0.0:
            return
        if delta > 0 and current[1] >= 1.0:
            return
        self.canvas.yview_scroll(delta, "units")

    # ------------------------------------------------------------------
    # Sidebar / Collections
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Collection tree helpers
    # ------------------------------------------------------------------
    def _col_by_id(self, col_id) -> dict | None:
        return next((c for c in self.collections if c["id"] == col_id), None)

    def _norm_parent(self, parent_id):
        """Treat None / missing / empty as root parent."""
        if parent_id is None or parent_id == "":
            return None
        return parent_id

    def _col_children(self, parent_id) -> list[dict]:
        parent_id = self._norm_parent(parent_id)
        kids = [
            c for c in self.collections
            if self._norm_parent(c.get("parent_id")) == parent_id
        ]
        kids.sort(key=lambda c: (
            c.get("sort_order", 10**9),
            (c.get("name") or "").lower(),
        ))
        return kids

    def _normalize_sibling_order(self, parent_id=None):
        """Rewrite sort_order to 0..n-1 for siblings under parent_id."""
        kids = self._col_children(parent_id)
        for i, c in enumerate(kids):
            c["sort_order"] = i

    def move_collection(self, col_id, direction: int):
        """Move a collection among its siblings. direction -1 = up, +1 = down."""
        col = self._col_by_id(col_id)
        if not col:
            return
        parent_id = self._norm_parent(col.get("parent_id"))
        self._normalize_sibling_order(parent_id)
        siblings = self._col_children(parent_id)
        ids = [c["id"] for c in siblings]
        try:
            idx = ids.index(col_id)
        except ValueError:
            return
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(siblings):
            return
        siblings[idx], siblings[new_idx] = siblings[new_idx], siblings[idx]
        for i, c in enumerate(siblings):
            c["sort_order"] = i
        self._save()
        self.refresh_sidebar()
        self.status_var.set(
            f'Moved “{col.get("name", "collection")}” {"up" if direction < 0 else "down"}'
        )

    def _col_descendants(self, col_id) -> list[str]:
        """All descendant collection ids (not including col_id itself)."""
        out = []
        stack = [col_id]
        seen = {col_id}
        while stack:
            pid = stack.pop()
            for c in self.collections:
                if self._norm_parent(c.get("parent_id")) == pid and c["id"] not in seen:
                    out.append(c["id"])
                    seen.add(c["id"])
                    stack.append(c["id"])
        return out

    def _col_and_descendants(self, col_id) -> set[str]:
        return {col_id, *self._col_descendants(col_id)}

    def _col_depth(self, col_id) -> int:
        depth = 0
        seen = set()
        cur = self._col_by_id(col_id)
        while cur and cur.get("parent_id"):
            pid = cur["parent_id"]
            if pid in seen:
                break
            seen.add(pid)
            depth += 1
            cur = self._col_by_id(pid)
        return depth

    def _col_game_count(self, col_id, include_children: bool = True) -> int:
        ids = self._col_and_descendants(col_id) if include_children else {col_id}
        return sum(
            1 for g in self.games
            if any(cid in g.get("collections", []) for cid in ids)
        )

    def _iter_collection_tree(self, parent_id=None, depth=0, respect_collapsed=True):
        """Yield (col, depth) in depth-first order. Skips children of collapsed parents."""
        if not hasattr(self, "_collapsed_collections"):
            self._collapsed_collections = set(
                self.settings.get("collapsed_collections") or []
            )
        for col in self._col_children(parent_id):
            yield col, depth
            if respect_collapsed and col["id"] in self._collapsed_collections:
                continue
            yield from self._iter_collection_tree(col["id"], depth + 1, respect_collapsed)

    def toggle_collection_expand(self, col_id):
        """Expand/collapse children under a parent collection."""
        if not hasattr(self, "_collapsed_collections"):
            self._collapsed_collections = set(
                self.settings.get("collapsed_collections") or []
            )
        if col_id in self._collapsed_collections:
            self._collapsed_collections.discard(col_id)
        else:
            self._collapsed_collections.add(col_id)
        self.settings["collapsed_collections"] = sorted(self._collapsed_collections)
        self._save()
        self.refresh_sidebar()

    def refresh_sidebar(self):
        for w in self.sidebar_frame.winfo_children():
            w.destroy()
        self._sidebar_btns.clear()
        self._col_drag = None
        if not hasattr(self, "_collapsed_collections"):
            self._collapsed_collections = set(
                self.settings.get("collapsed_collections") or []
            )

        # All Games
        self._add_sidebar_item(None, "🎮  All Games", len(self.games), depth=0)

        # Favorites (virtual – games tagged with "favorites")
        fav_count = sum(1 for g in self.games if "favorites" in g.get("collections", []))
        self._add_sidebar_item("favorites", "★  Favorites", fav_count, depth=0)

        # Divider
        div = tk.Frame(self.sidebar_frame, bg=Theme.BORDER, height=1)
        div.pack(fill=tk.X, padx=10, pady=8)

        # Custom collections (tree) — parents can expand/collapse children
        any_col = False
        for col, depth in self._iter_collection_tree(None, 0, respect_collapsed=True):
            any_col = True
            count = self._col_game_count(col["id"], include_children=True)
            has_kids = bool(self._col_children(col["id"]))
            expanded = col["id"] not in self._collapsed_collections
            if has_kids:
                icon = "📂" if expanded else "📁"
            else:
                icon = "📄"
            self._add_sidebar_item(
                col["id"], f"{icon}  {col['name']}", count,
                custom=True, depth=depth, has_children=has_kids, expanded=expanded,
            )

        if not any_col:
            hint = tk.Label(
                self.sidebar_frame,
                text="Create a collection\nwith the ＋ button\n\nRight-click a collection\nto add a sub-collection",
                bg=Theme.SIDEBAR, fg=Theme.TEXT_MUTED,
                font=("Segoe UI", 9), justify="center"
            )
            hint.pack(pady=12)

    def _add_sidebar_item(self, col_id, label, count, custom=False, depth=0,
                          has_children=False, expanded=True):
        selected = self.current_collection == col_id
        bg = Theme.SIDEBAR_SEL if selected else Theme.SIDEBAR
        fg = Theme.ACCENT_HOV if selected else Theme.TEXT

        row = tk.Frame(self.sidebar_frame, bg=bg, cursor="hand2")
        left_pad = 4 + depth * 12
        row.pack(fill=tk.X, padx=(left_pad, 4), pady=1)
        row._col_id = col_id  # used by drag-and-drop hit testing
        row._custom_col = bool(custom)

        extra_widgets = []

        # Expand / collapse toggle for parents — visible only on hover
        toggle = None
        chevron_text = "▼" if expanded else "▶"
        if custom and has_children:
            toggle = tk.Label(
                row, text="", font=("Segoe UI", 8),
                bg=bg, fg=Theme.TEXT_MUTED, cursor="hand2", width=2,
            )
            toggle.pack(side=tk.LEFT, padx=(2, 0))
            extra_widgets.append(toggle)

            def on_toggle(e=None, cid=col_id):
                self.toggle_collection_expand(cid)
                return "break"

            toggle.bind("<Button-1>", on_toggle)
        elif custom:
            spacer = tk.Label(row, text=" ", font=("Segoe UI", 8), bg=bg, width=2)
            spacer.pack(side=tk.LEFT, padx=(2, 0))
            extra_widgets.append(spacer)

        # Reorder ▲ ▼ — also only on hover
        up_btn = down_btn = move_fr = None
        can_up = can_down = False
        if custom:
            col_ref = self._col_by_id(col_id)
            parent_id = self._norm_parent(col_ref.get("parent_id")) if col_ref else None
            siblings = self._col_children(parent_id)
            ids = [c["id"] for c in siblings]
            idx = ids.index(col_id) if col_id in ids else -1
            can_up = idx > 0
            can_down = 0 <= idx < len(ids) - 1

            move_fr = tk.Frame(row, bg=bg)
            move_fr.pack(side=tk.RIGHT, padx=(0, 2))
            up_btn = tk.Label(
                move_fr, text="", font=("Segoe UI", 9, "bold"),
                bg=bg, fg="#60a5fa" if can_up else "#3d4f6a",
                cursor="hand2" if can_up else "arrow", padx=4,
            )
            up_btn.pack(side=tk.TOP)
            down_btn = tk.Label(
                move_fr, text="", font=("Segoe UI", 9, "bold"),
                bg=bg, fg="#60a5fa" if can_down else "#3d4f6a",
                cursor="hand2" if can_down else "arrow", padx=4,
            )
            down_btn.pack(side=tk.TOP)
            extra_widgets.extend([move_fr, up_btn, down_btn])
            if can_up:
                up_btn.bind("<Button-1>", lambda e, cid=col_id: self.move_collection(cid, -1))
            if can_down:
                down_btn.bind("<Button-1>", lambda e, cid=col_id: self.move_collection(cid, 1))

        cnt = tk.Label(row, text=str(count), bg=bg, fg=Theme.TEXT_MUTED,
                       font=("Segoe UI", 9))
        cnt.pack(side=tk.RIGHT, padx=(0, 6))

        lbl = tk.Label(row, text=label, bg=bg, fg=fg,
                       font=("Segoe UI", 10), anchor="w")
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 4), pady=7)

        def select(_e=None):
            self.current_collection = col_id
            if col_id is None:
                self.coll_title_var.set("All Games")
            elif col_id == "favorites":
                self.coll_title_var.set("Favorites")
            else:
                name = next((c["name"] for c in self.collections if c["id"] == col_id), "Collection")
                n_subs = len(self._col_descendants(col_id))
                if n_subs:
                    self.coll_title_var.set(
                        f"{name}  ·  +{n_subs} sub-collection{'s' if n_subs != 1 else ''}"
                    )
                else:
                    self.coll_title_var.set(name)
            self.refresh_sidebar()
            self.apply_filter()

        hover_targets = [row, lbl, cnt, *extra_widgets]
        base_bg = Theme.SIDEBAR_SEL if selected else Theme.SIDEBAR

        def show_arrows(visible: bool):
            if toggle is not None:
                try:
                    toggle.configure(text=chevron_text if visible else "")
                except Exception:
                    pass
            if up_btn is not None:
                try:
                    up_btn.configure(text="▲" if visible else "")
                except Exception:
                    pass
            if down_btn is not None:
                try:
                    down_btn.configure(text="▼" if visible else "")
                except Exception:
                    pass

        def on_enter(_):
            if self._col_drag:
                return
            show_arrows(True)
            if not selected:
                for w in hover_targets:
                    try:
                        w.configure(bg=Theme.SIDEBAR_HOV)
                    except Exception:
                        pass

        def on_leave(e):
            if self._col_drag:
                return
            # Don't hide if pointer moved onto a child widget of this row
            try:
                x, y = self.winfo_pointerxy()
                over = self.winfo_containing(x, y)
                if over is not None:
                    w = over
                    while w is not None:
                        if w == row:
                            return
                        w = w.master if hasattr(w, "master") else None
            except Exception:
                pass
            show_arrows(False)
            if not selected:
                for w in hover_targets:
                    try:
                        w.configure(bg=base_bg)
                    except Exception:
                        pass

        for w in (row, lbl, cnt):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
        for w in extra_widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        # Click to select (non-custom) or press-drag to reorder (custom)
        if custom:
            def on_press(e, cid=col_id):
                col_ref = self._col_by_id(cid)
                parent_id = self._norm_parent(col_ref.get("parent_id")) if col_ref else None
                self._col_drag = {
                    "id": cid,
                    "parent_id": parent_id,
                    "start_y": e.y_root,
                    "start_x": e.x_root,
                    "dragging": False,
                    "row": row,
                }

            def on_motion(e):
                drag = self._col_drag
                if not drag or drag.get("id") != col_id:
                    return
                if abs(e.y_root - drag["start_y"]) > 6 or abs(e.x_root - drag["start_x"]) > 6:
                    drag["dragging"] = True
                    try:
                        self.configure(cursor="fleur")
                        row.configure(bg=Theme.ACCENT_DIM)
                        lbl.configure(bg=Theme.ACCENT_DIM)
                        cnt.configure(bg=Theme.ACCENT_DIM)
                    except Exception:
                        pass
                    # Highlight drop target sibling under pointer
                    self._highlight_col_drop_target(e.x_root, e.y_root, drag)

            def on_release(e, cid=col_id):
                drag = self._col_drag
                self._col_drag = None
                try:
                    self.configure(cursor="")
                except Exception:
                    pass
                if not drag or drag.get("id") != cid:
                    select()
                    return
                if not drag.get("dragging"):
                    select()
                    return
                target_id = self._col_at_point(e.x_root, e.y_root)
                if target_id and target_id != cid:
                    self._reorder_collection_before(cid, target_id)
                else:
                    self.refresh_sidebar()

            for w in (row, lbl, cnt):
                w.bind("<ButtonPress-1>", on_press)
                w.bind("<B1-Motion>", on_motion)
                w.bind("<ButtonRelease-1>", on_release)
        else:
            for w in (row, lbl, cnt):
                w.bind("<Button-1>", select)

        # Right-click menu on custom collections
        if custom:
            def ctx(e, cid=col_id):
                menu = tk.Menu(self, tearoff=0, bg=Theme.SURFACE2, fg=Theme.TEXT,
                               activebackground=Theme.ACCENT, activeforeground="white",
                               relief="flat", font=("Segoe UI", 10))
                L = self._menu_label
                menu.add_command(
                    label=L("📁", "New sub-collection"),
                    command=lambda: self.create_collection(parent_id=cid),
                )
                if self._col_children(cid):
                    is_collapsed = cid in getattr(self, "_collapsed_collections", set())
                    menu.add_command(
                        label=L("▶", "Expand") if is_collapsed else L("▼", "Collapse"),
                        command=lambda: self.toggle_collection_expand(cid),
                    )
                menu.add_separator()
                col2 = self._col_by_id(cid)
                parent_id2 = self._norm_parent(col2.get("parent_id")) if col2 else None
                siblings2 = self._col_children(parent_id2)
                ids2 = [c["id"] for c in siblings2]
                idx2 = ids2.index(cid) if cid in ids2 else -1
                can_up2 = idx2 > 0
                can_down2 = 0 <= idx2 < len(ids2) - 1
                menu.add_command(
                    label="  Move Up",
                    command=lambda: self.move_collection(cid, -1),
                    state="normal" if can_up2 else "disabled",
                )
                menu.add_command(
                    label="  Move Down",
                    command=lambda: self.move_collection(cid, 1),
                    state="normal" if can_down2 else "disabled",
                )
                menu.add_separator()
                menu.add_command(label=L("✏", "Rename"),
                                 command=lambda: self.rename_collection(cid))
                menu.add_command(label=L("🗑", "Delete"),
                                 command=lambda: self.delete_collection(cid))
                try:
                    menu.tk_popup(e.x_root, e.y_root)
                finally:
                    menu.grab_release()

            for w in (row, lbl, cnt, *extra_widgets):
                w.bind("<Button-3>", ctx)

        self._sidebar_btns[col_id] = row

    def _col_at_point(self, x_root, y_root):
        """Return custom collection id under screen point, if any."""
        try:
            w = self.winfo_containing(x_root, y_root)
        except Exception:
            return None
        while w is not None:
            try:
                if getattr(w, "_custom_col", False) and getattr(w, "_col_id", None):
                    return w._col_id
            except Exception:
                pass
            try:
                w = w.master
            except Exception:
                break
        return None

    def _highlight_col_drop_target(self, x_root, y_root, drag):
        target_id = self._col_at_point(x_root, y_root)
        for cid, row in list(self._sidebar_btns.items()):
            if not getattr(row, "_custom_col", False):
                continue
            try:
                if cid == drag["id"]:
                    continue
                col = self._col_by_id(cid)
                same_parent = (
                    col
                    and self._norm_parent(col.get("parent_id")) == drag.get("parent_id")
                )
                if target_id == cid and same_parent:
                    row.configure(bg=Theme.ACCENT)
                elif self.current_collection == cid:
                    row.configure(bg=Theme.SIDEBAR_SEL)
                else:
                    row.configure(bg=Theme.SIDEBAR)
            except Exception:
                pass

    def _reorder_collection_before(self, drag_id, target_id):
        """Place drag_id in the sibling list at the position of target_id."""
        drag_col = self._col_by_id(drag_id)
        target_col = self._col_by_id(target_id)
        if not drag_col or not target_col:
            self.refresh_sidebar()
            return
        parent_id = self._norm_parent(drag_col.get("parent_id"))
        if self._norm_parent(target_col.get("parent_id")) != parent_id:
            # Only reorder among the same parent
            self.refresh_sidebar()
            self.status_var.set("Can only reorder within the same level")
            return
        self._normalize_sibling_order(parent_id)
        siblings = self._col_children(parent_id)
        ids = [c["id"] for c in siblings]
        if drag_id not in ids or target_id not in ids:
            self.refresh_sidebar()
            return
        ids.remove(drag_id)
        insert_at = ids.index(target_id)
        ids.insert(insert_at, drag_id)
        by_id = {c["id"]: c for c in siblings}
        for i, cid in enumerate(ids):
            by_id[cid]["sort_order"] = i
        self._save()
        self.refresh_sidebar()
        name = drag_col.get("name", "collection")
        self.status_var.set(f'Reordered “{name}”')

    def create_collection(self, parent_id=None):
        if parent_id:
            parent = self._col_by_id(parent_id)
            parent_name = parent["name"] if parent else "collection"
            name = themed_input(
                self,
                "New Sub-collection",
                f"Name for sub-collection under “{parent_name}”:",
                initial="",
            )
        else:
            name = themed_input(self, "New Collection", "Enter a name for this collection:", initial="")
        if not name or not name.strip():
            return
        name = name.strip()
        # Limit nesting depth
        if parent_id and self._col_depth(parent_id) >= 4:
            messagebox.showinfo(
                "Too deep",
                "Maximum collection depth is 5 levels.",
            )
            return
        siblings = self._col_children(parent_id)
        next_order = max((c.get("sort_order", 0) for c in siblings), default=-1) + 1
        col = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "name": name,
            "parent_id": parent_id,
            "sort_order": next_order,
        }
        self.collections.append(col)
        self._save()
        self.refresh_sidebar()
        kind = "Sub-collection" if parent_id else "Collection"
        self.status_var.set(f'{kind} “{name}” created')

    def rename_collection(self, col_id):
        col = self._col_by_id(col_id)
        if not col:
            return
        new_name = themed_input(self, "Rename Collection", "New collection name:",
                                initial=col["name"])
        if new_name and new_name.strip():
            col["name"] = new_name.strip()
            self._save()
            if self.current_collection == col_id:
                self.coll_title_var.set(col["name"])
            self.refresh_sidebar()
            self.status_var.set("Collection renamed")

    def delete_collection(self, col_id):
        col = self._col_by_id(col_id)
        if not col:
            return
        descendants = self._col_descendants(col_id)
        extra = f"\n\nAlso deletes {len(descendants)} sub-collection(s)." if descendants else ""
        if not themed_confirm(
            self,
            "Delete Collection",
            f'Delete “{col["name"]}”?{extra}\n\nGames will not be deleted.',
        ):
            return
        remove_ids = {col_id, *descendants}
        self.collections = [c for c in self.collections if c["id"] not in remove_ids]
        for g in self.games:
            cols = g.get("collections", [])
            if any(cid in remove_ids for cid in cols):
                g["collections"] = [c for c in cols if c not in remove_ids]
        if self.current_collection in remove_ids:
            self.current_collection = None
            self.coll_title_var.set("All Games")
        self._save()
        self.refresh_sidebar()
        self.apply_filter()
        self.status_var.set(f'Collection “{col["name"]}” deleted')

    # ------------------------------------------------------------------
    def apply_filter(self):
        query = self.search_var.get().strip().lower()
        games = list(self.games)

        # Filter by collection — parent shows its games + all sub-collection games
        if self.current_collection == "favorites":
            games = [g for g in games if "favorites" in g.get("collections", [])]
        elif self.current_collection is not None:
            ids = self._col_and_descendants(self.current_collection)
            games = [
                g for g in games
                if any(cid in (g.get("collections") or []) for cid in ids)
            ]

        # Search
        if query:
            games = [g for g in games if query in (g.get("name") or "").lower()]

        self.filtered_games = games
        self.refresh_library()

    def _library_sections(self) -> list[tuple[str | None, list[dict]]]:
        """
        Group filtered games into sections for display.
        When viewing a parent collection that has sub-collections, return
        (section_title, games) pairs so the UI can show headers + games under each.
        Otherwise a single flat section with no title.
        """
        games = self.filtered_games
        cid = self.current_collection
        if not games or cid is None or cid == "favorites":
            return [(None, games)]

        # Direct + nested sub-collections under the current collection
        subs = list(self._iter_collection_tree(cid, 0))
        if not subs:
            return [(None, games)]

        sub_ids = {c["id"] for c, _ in subs}
        parent_col = self._col_by_id(cid)
        parent_name = (parent_col.get("name") if parent_col else None) or "Collection"

        sections: list[tuple[str | None, list[dict]]] = []

        # Games only in the parent (not in any sub-collection)
        parent_only = [
            g for g in games
            if cid in (g.get("collections") or [])
            and not sub_ids.intersection(g.get("collections") or [])
        ]
        if parent_only:
            sections.append((parent_name, parent_only))

        # Each sub-collection as its own section
        for col, depth in subs:
            section_games = [
                g for g in games
                if col["id"] in (g.get("collections") or [])
            ]
            if section_games:
                # Indent deeper levels slightly in the title
                prefix = "› " * depth if depth else ""
                sections.append((f"{prefix}{col['name']}", section_games))

        # Anything left (shouldn't happen often)
        shown = {g["id"] for _, gs in sections for g in gs}
        rest = [g for g in games if g["id"] not in shown]
        if rest:
            sections.append(("Other", rest))

        return sections if sections else [(None, games)]

    def refresh_library(self):
        # Cancel any running marquees before destroying cards
        for stop_fn in getattr(self, "_active_marquees", []):
            try:
                stop_fn()
            except Exception:
                pass
        self._active_marquees = []

        for widget in self.scrollable.winfo_children():
            widget.destroy()
        self.card_images.clear()

        if not self.filtered_games:
            self._show_empty_state()
            self.count_var.set("")
            self.after(10, self._update_scrollregion)
            return

        cols = self._grid_columns()
        self._last_cols = cols

        sections = self._library_sections()
        for title, section_games in sections:
            if title:
                header = tk.Frame(self.scrollable, bg=Theme.BG)
                header.pack(fill=tk.X, padx=14, pady=(16, 4))
                tk.Label(
                    header, text=title,
                    font=("Segoe UI", 12, "bold"),
                    bg=Theme.BG, fg=Theme.TEXT,
                ).pack(side=tk.LEFT)
                tk.Label(
                    header,
                    text=f"  {len(section_games)}",
                    font=("Segoe UI", 10),
                    bg=Theme.BG, fg=Theme.TEXT_MUTED,
                ).pack(side=tk.LEFT)
                # Thin underline
                line = tk.Frame(self.scrollable, bg=Theme.BORDER, height=1)
                line.pack(fill=tk.X, padx=14, pady=(0, 6))

            grid = tk.Frame(self.scrollable, bg=Theme.BG)
            grid.pack(fill=tk.X, anchor="nw")
            for i, game in enumerate(section_games):
                row, col = divmod(i, cols)
                self._create_game_card(game, row, col, parent=grid)

        n = len(self.filtered_games)
        self.count_var.set(f"{n} game{'s' if n != 1 else ''}")
        self.status_var.set("Ready")
        self.after(10, self._update_scrollregion)

    def _show_empty_state(self):
        empty = tk.Frame(self.scrollable, bg=Theme.BG)
        empty.pack(expand=True, fill=tk.BOTH, pady=80)
        tk.Label(empty, text="🎮", font=("Segoe UI", 42),
                 bg=Theme.BG, fg=Theme.TEXT_MUTED).pack()
        if self.current_collection:
            msg = "No games in this collection"
            sub = "Right-click a game → Add to collection"
        else:
            msg = "No games yet"
            sub = "Click “Add Game” to start building your library"
        tk.Label(empty, text=msg, font=("Segoe UI", 16, "bold"),
                 bg=Theme.BG, fg=Theme.TEXT).pack(pady=(10, 4))
        tk.Label(empty, text=sub, font=("Segoe UI", 10),
                 bg=Theme.BG, fg=Theme.TEXT_MUTED).pack()

    # ------------------------------------------------------------------
    def _create_game_card(self, game: dict, row: int, col: int, parent=None):
        # Square cover
        cover_w, cover_h = 200, 200
        info_h = 92  # name (1 line + marquee) + playtime/last played + buttons
        border_pad = 6  # glow layers
        card_w = cover_w + border_pad
        card_h = cover_h + info_h + border_pad

        host = parent if parent is not None else self.scrollable
        card = tk.Frame(host, bg=Theme.BG, highlightthickness=0, bd=0,
                        width=card_w, height=card_h)
        card.grid(row=row, column=col, padx=10, pady=12, sticky="n")
        card.grid_propagate(False)

        glow_outer = tk.Frame(card, bg=Theme.BG, padx=1, pady=1)
        glow_outer.pack(fill=tk.BOTH, expand=True)
        glow_mid = tk.Frame(glow_outer, bg=Theme.BG, padx=1, pady=1)
        glow_mid.pack(fill=tk.BOTH, expand=True)
        border = tk.Frame(glow_mid, bg=Theme.BORDER, padx=1, pady=1)
        border.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(border, bg=Theme.SURFACE)
        inner.pack(fill=tk.BOTH, expand=True)

        cover_frame = tk.Frame(inner, bg=Theme.SURFACE2, width=cover_w, height=cover_h,
                               cursor="hand2")
        cover_frame.pack(fill=tk.BOTH, expand=True)
        cover_frame.pack_propagate(False)
        # Click cover to customize
        cover_frame.bind("<Button-1>", lambda e, g=game: self.customize_cover(g))

        cover_path = game.get("cover")
        cover_mode = game.get("cover_mode") or "fill"
        img = None
        if cover_path and Path(cover_path).exists():
            img = prepare_cover_image(cover_path, cover_w, cover_h, cover_mode)

        if img:
            self.card_images[game["id"]] = img
            # Place at exact size (do NOT stretch with relwidth/relheight — that
            # would undo Fill/Fit/Stretch processing)
            cover_lbl = tk.Label(cover_frame, image=img, bg=Theme.SURFACE2, bd=0, cursor="hand2")
            cover_lbl.place(relx=0.5, rely=0.5, anchor="center")
            cover_lbl.bind("<Button-1>", lambda e, g=game: self.customize_cover(g))
            placeholder_bg = Theme.SURFACE2
        else:
            letter = (game.get("name") or "?")[0].upper()
            palette = ["#3b82f6", "#8b5cf6", "#ec4899", "#14b8a6", "#f59e0b", "#ef4444"]
            c1 = palette[hash(game["id"]) % len(palette)]
            placeholder_bg = c1
            cover_lbl = tk.Label(cover_frame, text=letter, font=("Segoe UI", 56, "bold"),
                                 bg=c1, fg="white", cursor="hand2")
            cover_lbl.place(relx=0, rely=0, relwidth=1, relheight=1)
            cover_lbl.bind("<Button-1>", lambda e, g=game: self.customize_cover(g))

        # Star if favorited (top-left)
        if "favorites" in game.get("collections", []):
            star = tk.Label(cover_frame, text="★", font=("Segoe UI", 12),
                            bg=placeholder_bg, fg="#fbbf24")
            star.place(relx=0.0, rely=0.0, anchor="nw", x=6, y=4)

        # System badge (top-right)
        system_name = (game.get("system") or "").strip()
        if system_name:
            sys_txt = short_system_name(system_name)
            sys_lbl = tk.Label(
                cover_frame, text=sys_txt,
                font=("Segoe UI", 8, "bold"),
                bg="#0f172a", fg="#93c5fd",
                padx=5, pady=1,
            )
            sys_lbl.place(relx=1.0, rely=0.0, anchor="ne", x=-6, y=5)

        # RA achievement progress overlay on cover
        # In progress → white count
        # Complete (all softcore) → green + tick
        # Mastered (all hardcore) → gold + cup
        prog = game.get("ra_progress")
        if game.get("ra_game_id") and prog and prog.get("total"):
            awarded = int(prog.get("awarded") or 0)
            total = int(prog.get("total") or 0)
            awarded_hc = int(prog.get("awarded_hc") or 0)
            completed = total > 0 and awarded >= total
            mastered = total > 0 and awarded_hc >= total

            count_txt = f"{awarded}/{total}"
            if mastered:
                fg = "#fbbf24"          # gold
                mark = "🏆"
                mark_font = ("Segoe UI Emoji", 10)
            elif completed:
                fg = "#4ade80"          # green
                mark = "✓"
                mark_font = ("Segoe UI", 10, "bold")
            else:
                fg = "#f8fafc"          # white
                mark = ""
                mark_font = ("Segoe UI", 9, "bold")

            prog_fr = tk.Frame(cover_frame, bg="#0f172a")
            prog_fr.place(relx=0.0, rely=1.0, anchor="sw", x=6, y=-6)
            tk.Label(
                prog_fr, text=count_txt,
                font=("Segoe UI", 9, "bold"),
                bg="#0f172a", fg=fg,
            ).pack(side=tk.LEFT, padx=(6, 2 if mark else 6), pady=2)
            if mark:
                tk.Label(
                    prog_fr, text=mark,
                    font=mark_font,
                    bg="#0f172a", fg=fg,
                ).pack(side=tk.LEFT, padx=(0, 6), pady=2)
        elif game.get("ra_game_id"):
            # Linked but no progress cached yet — small RA mark
            ra_mark = tk.Label(
                cover_frame, text="RA",
                font=("Segoe UI", 8, "bold"),
                bg="#7c3aed", fg="white",
                padx=4, pady=1
            )
            ra_mark.place(relx=0.0, rely=1.0, anchor="sw", x=6, y=-6)

        info = tk.Frame(inner, bg=Theme.SURFACE, height=info_h)
        info.pack(fill=tk.X, side=tk.BOTTOM)
        info.pack_propagate(False)
        info_inner = tk.Frame(info, bg=Theme.SURFACE)
        info_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6, 6))

        full_name = game.get("name", "Unknown")
        # Single line — show what fits; long titles scroll on hover (marquee)
        name_lbl = tk.Label(
            info_inner,
            text=full_name,
            bg=Theme.SURFACE,
            fg=Theme.TEXT,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        name_lbl.pack(fill=tk.X)

        # Playtime + last played under the name
        pt = format_playtime(game.get("playtime_seconds", 0))
        lp = format_last_played(game.get("last_played"))
        meta_txt = f"{pt}  ·  {lp}"
        meta_lbl = tk.Label(
            info_inner, text=meta_txt, bg=Theme.SURFACE, fg=Theme.TEXT_MUTED,
            font=("Segoe UI", 8), anchor="w",
        )
        meta_lbl.pack(fill=tk.X)

        # Marquee: fill available width, then scroll full name left ↔ right on hover
        marquee = {
            "after_id": None,
            "pos": 0.0,
            "direction": 1,  # 1 = scroll left (show later chars), -1 = back
            "running": False,
            "pause": 0,
            "visible": len(full_name),
            "idle_text": full_name,
        }

        def _label_alive() -> bool:
            try:
                return bool(name_lbl.winfo_exists())
            except Exception:
                return False

        def _measure_visible() -> int:
            """How many characters fit in the label width."""
            try:
                name_lbl.update_idletasks()
                w = max(1, name_lbl.winfo_width())
                # Approximate average char width for Segoe UI 10 bold
                # Prefer actual font measure when available
                try:
                    f = tkfont.Font(font=name_lbl.cget("font"))
                    # binary search max chars that fit
                    lo, hi = 1, len(full_name)
                    best = hi
                    while lo <= hi:
                        mid = (lo + hi) // 2
                        if f.measure(full_name[:mid]) <= w - 2:
                            best = mid
                            lo = mid + 1
                        else:
                            hi = mid - 1
                    return max(1, best)
                except Exception:
                    return max(1, int(w / 7.2))
            except Exception:
                return 20

        def _set_idle_text():
            """Show start of title, ellipsis only if truncated."""
            vis = marquee["visible"]
            if len(full_name) <= vis:
                marquee["idle_text"] = full_name
            else:
                # leave room for ellipsis
                cut = max(1, vis - 1)
                marquee["idle_text"] = full_name[:cut] + "…"
            try:
                name_lbl.configure(text=marquee["idle_text"])
            except tk.TclError:
                pass

        def marquee_step():
            if not marquee["running"] or not _label_alive():
                marquee["running"] = False
                marquee["after_id"] = None
                return
            try:
                vis = marquee["visible"]
                if len(full_name) <= vis:
                    name_lbl.configure(text=full_name)
                    marquee["running"] = False
                    return
                if marquee["pause"] > 0:
                    marquee["pause"] -= 1
                    marquee["after_id"] = self.after(30, marquee_step)
                    return
                max_offset = float(len(full_name) - vis)
                marquee["pos"] += marquee["direction"] * 0.4
                if marquee["pos"] >= max_offset:
                    marquee["pos"] = max_offset
                    marquee["direction"] = -1
                    marquee["pause"] = 18  # pause at end
                elif marquee["pos"] <= 0:
                    marquee["pos"] = 0.0
                    marquee["direction"] = 1
                    marquee["pause"] = 18  # pause at start
                start = int(marquee["pos"])
                name_lbl.configure(text=full_name[start: start + vis])
                marquee["after_id"] = self.after(28, marquee_step)
            except tk.TclError:
                marquee["running"] = False
                marquee["after_id"] = None

        def start_marquee():
            if marquee["running"] or not _label_alive():
                return
            vis = _measure_visible()
            marquee["visible"] = vis
            if len(full_name) <= vis:
                return  # fits fully — no scroll needed
            marquee["running"] = True
            marquee["pos"] = 0.0
            marquee["direction"] = 1
            marquee["pause"] = 12  # brief pause before scrolling
            try:
                name_lbl.configure(text=full_name[:vis])
            except tk.TclError:
                marquee["running"] = False
                return
            marquee_step()

        def stop_marquee():
            marquee["running"] = False
            if marquee["after_id"] is not None:
                try:
                    self.after_cancel(marquee["after_id"])
                except Exception:
                    pass
                marquee["after_id"] = None
            if _label_alive():
                _set_idle_text()

        # Track so refresh can cancel pending marquees
        if not hasattr(self, "_active_marquees"):
            self._active_marquees = []
        self._active_marquees.append(stop_marquee)

        # Set initial truncated text once width is known
        def _init_idle():
            if _label_alive():
                marquee["visible"] = _measure_visible()
                _set_idle_text()
        self.after(30, _init_idle)

        btn_row = tk.Frame(info_inner, bg=Theme.SURFACE, height=28)
        btn_row.pack(fill=tk.X, pady=(6, 0))
        btn_row.pack_propagate(False)

        play_btn = tk.Label(btn_row, text="▶  Play", font=("Segoe UI", 9, "bold"),
                            bg=Theme.ACCENT, fg="white", cursor="hand2", padx=10, pady=4)
        play_btn.pack(side=tk.LEFT)
        play_btn.bind("<Button-1>", lambda e, g=game: self.launch_game(g))
        play_btn.bind("<Enter>", lambda e: play_btn.configure(bg=Theme.ACCENT_HOV))
        play_btn.bind("<Leave>", lambda e: play_btn.configure(bg=Theme.ACCENT))

        more_btn = tk.Label(btn_row, text="⋯", font=("Segoe UI", 11, "bold"),
                            bg=Theme.SURFACE2, fg=Theme.TEXT, cursor="hand2", padx=10, pady=3)
        more_btn.pack(side=tk.RIGHT)
        more_btn.bind("<Button-1>", lambda e, g=game: self.show_context_menu(g))
        more_btn.bind("<Enter>", lambda e: more_btn.configure(bg=Theme.BORDER))
        more_btn.bind("<Leave>", lambda e: more_btn.configure(bg=Theme.SURFACE2))

        def on_enter(_):
            glow_outer.configure(bg=Theme.GLOW_SOFT)
            glow_mid.configure(bg=Theme.GLOW_MID)
            border.configure(bg=Theme.GLOW_CORE)
            start_marquee()

        def on_leave(e):
            x, y = self.winfo_pointerxy()
            widget = self.winfo_containing(x, y)
            if widget is not None:
                w = widget
                while w is not None:
                    if w == card:
                        return
                    w = w.master if hasattr(w, "master") else None
            glow_outer.configure(bg=Theme.BG)
            glow_mid.configure(bg=Theme.BG)
            border.configure(bg=Theme.BORDER)
            stop_marquee()

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    # ------------------------------------------------------------------
    @staticmethod
    def _resolve_shortcut(path: Path) -> tuple[str, str, str]:
        """
        If path is a .lnk shortcut, return (target, arguments, working_dir).
        Otherwise return (path, "", parent).
        """
        path = Path(path)
        if path.suffix.lower() != ".lnk" or sys.platform != "win32":
            return str(path), "", str(path.parent)

        # PowerShell COM is the most reliable way without extra packages
        ps = (
            "$ErrorActionPreference='Stop'; "
            f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{str(path).replace(chr(39), chr(39)+chr(39))}'); "
            "$o=[ordered]@{Target=$s.TargetPath; Args=$s.Arguments; Dir=$s.WorkingDirectory}; "
            "$o | ConvertTo-Json -Compress"
        )
        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps],
                capture_output=True, text=True, timeout=15,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if proc.returncode == 0 and proc.stdout.strip():
                data = json.loads(proc.stdout.strip())
                target = (data.get("Target") or "").strip() or str(path)
                args = (data.get("Args") or "").strip()
                cwd = (data.get("Dir") or "").strip() or str(Path(target).parent)
                return target, args, cwd
        except Exception:
            pass
        return str(path), "", str(path.parent)

    def add_game(self):
        chosen = filedialog.askopenfilename(
            title="Select the game executable or shortcut",
            filetypes=[
                ("Games", "*.exe *.lnk"),
                ("Executable", "*.exe"),
                ("Shortcut", "*.lnk"),
                ("All files", "*.*"),
            ]
        )
        if not chosen:
            return

        chosen_path = Path(chosen)
        target, launch_args, _cwd = self._resolve_shortcut(chosen_path)
        exe_path = Path(target)

        # Default name from shortcut name, else exe stem
        default_name = chosen_path.stem if chosen_path.suffix.lower() == ".lnk" else exe_path.stem
        name = themed_input(self, "Game Name", "Enter a name for this game:",
                            initial=default_name)
        if not name or not name.strip():
            return
        name = name.strip()

        # If shortcut had args, show them so user can confirm/edit
        if launch_args:
            edited = themed_input(
                self,
                "Launch Options",
                "Launch options found in the shortcut.\nEdit if needed, or leave as-is:",
                initial=launch_args,
                width=480,
                height=230,
            )
            if edited is not None:
                launch_args = edited.strip()

        cover = None
        cover_mode = "fill"
        if themed_confirm(self, "Cover Image", "Add a cover image?\n(PNG or JPG recommended)"):
            cover_file = filedialog.askopenfilename(
                title="Select cover image",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"), ("All files", "*.*")]
            )
            if cover_file:
                ext = Path(cover_file).suffix.lower()
                dest = COVERS_DIR / f"{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                try:
                    shutil.copy2(cover_file, dest)
                    cover = str(dest)
                except Exception as e:
                    messagebox.showwarning("Cover", f"Could not copy cover:\n{e}")

        game = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "name": name,
            "path": str(exe_path),
            "cover": cover,
            "cover_mode": cover_mode,
            "launch_options": launch_args,
            "collections": [],
            "ra_game_id": None,
            "ra_display_set_id": None,
            "system": "",
            "playtime_seconds": 0,
            "added": datetime.now().isoformat(timespec="seconds"),
            "last_played": None
        }
        self.games.append(game)
        self._save()
        self.refresh_sidebar()
        self.apply_filter()
        msg = f'Added “{name}”'
        if launch_args:
            msg += " (launch options from shortcut)"
        self.status_var.set(msg)

    def _pid_alive(self, pid: int) -> bool:
        if not pid or pid <= 0:
            return False
        if sys.platform == "win32":
            # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                return True
            return False
        try:
            os.kill(int(pid), 0)
            return True
        except Exception:
            return False

    def _start_play_session(self, game: dict, pid: int | None):
        """Begin tracking playtime for a launched game."""
        # Flush any previous session for this game first
        gid = game.get("id")
        if gid in self._play_sessions:
            self._end_play_session(gid)
        self._play_sessions[gid] = {
            "pid": pid,
            "start": time.time(),
            "game": game,
        }

    def _end_play_session(self, gid: str):
        sess = self._play_sessions.pop(gid, None)
        if not sess:
            return
        elapsed = max(0, int(time.time() - sess["start"]))
        game = sess.get("game")
        if game is not None and elapsed > 0:
            game["playtime_seconds"] = int(game.get("playtime_seconds") or 0) + elapsed

    def _poll_play_sessions(self):
        """Accumulate playtime for running games; drop finished sessions."""
        now = time.time()
        changed = False
        finished = []
        for gid, sess in list(self._play_sessions.items()):
            pid = sess.get("pid")
            game = sess.get("game")
            if game is None:
                finished.append(gid)
                continue
            # If we have a PID, stop when process exits; otherwise keep
            # accumulating while the launcher is open (best-effort).
            alive = self._pid_alive(pid) if pid else True
            elapsed = max(0, int(now - sess["start"]))
            if elapsed > 0:
                game["playtime_seconds"] = int(game.get("playtime_seconds") or 0) + elapsed
                sess["start"] = now
                changed = True
            if pid and not alive:
                finished.append(gid)
        for gid in finished:
            self._play_sessions.pop(gid, None)
            changed = True
        if changed:
            self._save()
        try:
            self.after(15000, self._poll_play_sessions)
        except Exception:
            pass

    def _on_app_close(self):
        """Close button → minimize to system tray (or quit if tray unavailable)."""
        if self._really_quit or not HAS_PYSTRAY:
            self._quit_app()
            return
        # Hide to tray
        self.withdraw()
        self._ensure_tray()
        try:
            self.status_var.set("Running in system tray — right-click icon to Exit")
        except Exception:
            pass

    def _quit_app(self):
        """Truly exit: stop tray, flush playtime, destroy window."""
        self._really_quit = True
        for gid in list(self._play_sessions.keys()):
            try:
                self._end_play_session(gid)
            except Exception:
                pass
        try:
            self._save()
        except Exception:
            pass
        self._stop_tray()
        # Never keep RA badge/icon downloads on disk
        try:
            purge_ra_image_caches()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
        # Ensure process ends even if something is stuck
        try:
            self.after(200, lambda: sys.exit(0))
        except Exception:
            sys.exit(0)

    def _make_tray_image(self):
        """Tray icon from app.ico, with a drawn fallback."""
        size = 64
        # Prefer the same app.ico used for the window / taskbar
        try:
            icon_path = getattr(self, "_icon_path", None) or self._resolve_icon_path()
            if icon_path and Path(icon_path).is_file():
                pil = PILImage.open(str(icon_path))
                # Multi-size ICO: pick the frame closest to 64px
                best = 0
                best_score = 10**9
                i = 0
                try:
                    while True:
                        pil.seek(i)
                        w, h = pil.size
                        score = abs(max(w, h) - size)
                        if score < best_score:
                            best_score = score
                            best = i
                        i += 1
                except EOFError:
                    pass
                pil.seek(best)
                frame = pil.convert("RGBA")
                if frame.size != (size, size):
                    frame = frame.resize((size, size), PILImage.LANCZOS)
                return frame
        except Exception:
            pass

        # Fallback: blue rounded square with play triangle
        img = PILImage.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = PILImageDraw.Draw(img)
        margin = 4
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=14,
            fill=(59, 130, 246, 255),
        )
        tri = [(24, 18), (24, 46), (48, 32)]
        draw.polygon(tri, fill=(255, 255, 255, 255))
        return img

    def _ensure_tray(self):
        if not HAS_PYSTRAY:
            return
        if self._tray_icon is not None:
            return

        def on_show(icon=None, item=None):
            self.after(0, self._restore_from_tray)

        def on_exit(icon=None, item=None):
            self.after(0, self._quit_app)

        menu = pystray.Menu(
            pystray.MenuItem("Show Local Game Library", on_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", on_exit),
        )
        try:
            image = self._make_tray_image()
        except Exception:
            # Fallback solid color
            image = PILImage.new("RGBA", (64, 64), (59, 130, 246, 255))

        self._tray_icon = pystray.Icon(
            "LocalGameLibrary",
            image,
            "Local Game Library",
            menu,
        )

        def run_tray():
            try:
                self._tray_icon.run()
            except Exception:
                pass

        self._tray_thread = threading.Thread(target=run_tray, daemon=True)
        self._tray_thread.start()

    def _restore_from_tray(self):
        """Bring the main window back (from tray or background)."""
        try:
            self.deiconify()
        except Exception:
            pass
        try:
            self.state("zoomed")
        except Exception:
            try:
                self.attributes("-zoomed", True)
            except Exception:
                pass
        try:
            self.lift()
            self.attributes("-topmost", True)
            self.after(150, lambda: self.attributes("-topmost", False))
            self.focus_force()
        except Exception:
            try:
                self.lift()
                self.focus_force()
            except Exception:
                pass
        # Windows: force foreground
        if sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32
                hwnd = self.winfo_id()
                parent = user32.GetParent(hwnd)
                if parent:
                    hwnd = parent
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                user32.SetForegroundWindow(hwnd)
            except Exception:
                pass
        try:
            self.status_var.set("Welcome back")
        except Exception:
            pass

    def _stop_tray(self):
        icon = self._tray_icon
        self._tray_icon = None
        if icon is not None:
            try:
                icon.stop()
            except Exception:
                pass

    def launch_game(self, game: dict, as_admin: bool = False):
        path = Path(game["path"])
        if not path.exists():
            messagebox.showerror("File not found",
                                 f'The executable no longer exists:\n{path}')
            return
        try:
            args = game.get("launch_options", "").strip()
            cwd = str(path.parent)
            exe = str(path)
            pid = None
            if sys.platform == "win32":
                if as_admin:
                    ret = ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", exe, args if args else None, cwd, 1)
                    if ret <= 32:
                        raise RuntimeError(f"ShellExecute failed ({ret})")
                    # ShellExecute does not return a PID we can track
                else:
                    # Prefer list form so we get a real process PID
                    try:
                        cmd = [exe] + (shlex.split(args, posix=False) if args else [])
                    except Exception:
                        cmd = [exe]
                    CREATE_NEW_PROCESS_GROUP = 0x00000200
                    DETACHED_PROCESS = 0x00000008
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = 1
                    proc = subprocess.Popen(
                        cmd, cwd=cwd, shell=False, startupinfo=startupinfo,
                        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                        close_fds=True,
                    )
                    pid = proc.pid
            else:
                cmd = [exe] + (args.split() if args else [])
                proc = subprocess.Popen(cmd, cwd=cwd, start_new_session=True)
                pid = proc.pid
            game["last_played"] = datetime.now().isoformat(timespec="seconds")
            self._start_play_session(game, pid)
            self._save()
            self.refresh_library()
            self.status_var.set(f'Launching “{game["name"]}”…')
        except Exception as e:
            messagebox.showerror("Launch failed",
                                 f'Could not start “{game["name"]}”:\n\n{e}')

    def set_launch_options(self, game: dict):
        current = game.get("launch_options", "")
        new_opts = themed_input(
            self,
            "Launch Options",
            f"Command-line arguments for “{game.get('name', 'this game')}”\n"
            "Example:  -windowed -novid",
            initial=current,
            width=460,
            height=230,
        )
        if new_opts is not None:
            game["launch_options"] = new_opts.strip()
            self._save()
            self.status_var.set("Launch options updated")

    def toggle_favorite(self, game: dict):
        cols = game.setdefault("collections", [])
        if "favorites" in cols:
            cols.remove("favorites")
            self.status_var.set(f'Removed “{game["name"]}” from Favorites')
        else:
            cols.append("favorites")
            self.status_var.set(f'Added “{game["name"]}” to Favorites')
        self._save()
        self.refresh_sidebar()
        self.apply_filter()

    def add_to_collection(self, game: dict, col_id: str):
        cols = game.setdefault("collections", [])
        if col_id not in cols:
            cols.append(col_id)
            self._save()
            self.refresh_sidebar()
            self.apply_filter()
            name = next((c["name"] for c in self.collections if c["id"] == col_id), col_id)
            self.status_var.set(f'Added to “{name}”')

    def remove_from_collection(self, game: dict, col_id: str):
        cols = game.setdefault("collections", [])
        if col_id in cols:
            cols.remove(col_id)
            self._save()
            self.refresh_sidebar()
            self.apply_filter()
            self.status_var.set("Removed from collection")

    def _update_ra_btn(self):
        if self._ra_client():
            self.ra_btn.configure(bg="#059669", fg="white", text="  🏆  RA Connected  ")
        else:
            self.ra_btn.configure(bg="#7c3aed", fg="white", text="  🏆  RA Login  ")

    def show_app_settings(self):
        """App settings: Start with Windows (opens in system tray)."""
        win = tk.Toplevel(self)
        win.title("Settings")
        win.geometry("460x280")
        win.minsize(400, 240)
        win.configure(bg=Theme.SURFACE)
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)
        try:
            self.update_idletasks()
            px = self.winfo_rootx() + (self.winfo_width() - 460) // 2
            py = self.winfo_rooty() + (self.winfo_height() - 280) // 2
            win.geometry(f"+{max(0, px)}+{max(0, py)}")
        except Exception:
            pass

        body = tk.Frame(win, bg=Theme.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        tk.Label(body, text="Settings", font=("Segoe UI", 14, "bold"),
                 bg=Theme.SURFACE, fg=Theme.TEXT).pack(anchor="w")
        tk.Label(
            body,
            text="Startup and system tray options",
            font=("Segoe UI", 9),
            bg=Theme.SURFACE,
            fg=Theme.TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 16))

        # Sync checkbox with actual registry (source of truth on Windows)
        current = is_start_with_windows_enabled() if sys.platform == "win32" else bool(
            self.settings.get("start_with_windows")
        )
        self.settings["start_with_windows"] = bool(current)

        startup_var = tk.BooleanVar(value=current)
        row = tk.Frame(body, bg=Theme.SURFACE2, highlightthickness=1,
                       highlightbackground=Theme.BORDER)
        row.pack(fill=tk.X, pady=(0, 8))
        inner = tk.Frame(row, bg=Theme.SURFACE2)
        inner.pack(fill=tk.X, padx=12, pady=12)

        cb = tk.Checkbutton(
            inner,
            text="Start with Windows",
            variable=startup_var,
            bg=Theme.SURFACE2,
            fg=Theme.TEXT,
            selectcolor=Theme.SURFACE,
            activebackground=Theme.SURFACE2,
            activeforeground=Theme.TEXT,
            font=("Segoe UI", 11, "bold"),
            highlightthickness=0,
            cursor="hand2",
        )
        cb.pack(anchor="w")
        tk.Label(
            inner,
            text="When Windows starts, the app opens in the system tray only\n"
                 "(no main window until you click the tray icon).",
            font=("Segoe UI", 9),
            bg=Theme.SURFACE2,
            fg=Theme.TEXT_MUTED,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        status = tk.Label(body, text="", bg=Theme.SURFACE, fg=Theme.TEXT_MUTED,
                          font=("Segoe UI", 9), justify="left")
        status.pack(anchor="w", pady=(8, 0))

        if not HAS_PYSTRAY:
            status.configure(
                text="Install pystray for tray mode:  pip install pystray",
                fg=Theme.DANGER,
            )
        if sys.platform != "win32":
            cb.configure(state="disabled")
            status.configure(text="Start with Windows is only available on Windows.",
                             fg=Theme.TEXT_MUTED)

        def save():
            want = bool(startup_var.get())
            ok, msg = set_start_with_windows(want)
            if not ok:
                status.configure(text=msg, fg=Theme.DANGER)
                return
            self.settings["start_with_windows"] = want
            self._save()
            status.configure(text=msg, fg=Theme.SUCCESS if want else Theme.TEXT_MUTED)
            self.status_var.set(msg)

        def close():
            win.destroy()

        btn_row = tk.Frame(body, bg=Theme.SURFACE)
        btn_row.pack(fill=tk.X, pady=(20, 0))
        tk.Button(
            btn_row, text="  Save  ", font=("Segoe UI", 10, "bold"),
            bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
            width=10, pady=7, command=save,
            activebackground=Theme.ACCENT_HOV, activeforeground="white",
        ).pack(side=tk.RIGHT)
        tk.Button(
            btn_row, text="  Close  ", font=("Segoe UI", 10),
            bg=Theme.SURFACE2, fg=Theme.TEXT, relief="flat", cursor="hand2",
            width=10, pady=7, command=close,
            activebackground=Theme.BORDER, activeforeground=Theme.TEXT,
        ).pack(side=tk.RIGHT, padx=(0, 8))

        win.bind("<Escape>", lambda e: close())
        win.bind("<Return>", lambda e: save())

    def show_ra_settings(self):
        win = tk.Toplevel(self)
        win.title("RetroAchievements Login")
        win.geometry("460x360")
        win.minsize(400, 320)
        win.configure(bg=Theme.SURFACE)
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        # Content
        content = tk.Frame(win, bg=Theme.SURFACE)
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        tk.Label(content, text="RetroAchievements", font=("Segoe UI", 14, "bold"),
                 bg=Theme.SURFACE, fg=Theme.TEXT).pack(pady=(0, 4))
        tk.Label(content, text="Get your Web API key from:\nretroachievements.org → Settings → Keys",
                 bg=Theme.SURFACE, fg=Theme.TEXT_MUTED, font=("Segoe UI", 9),
                 justify="center").pack(pady=(0, 16))

        tk.Label(content, text="Username", bg=Theme.SURFACE, fg=Theme.TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w")
        user_var = tk.StringVar(value=self.ra.get("username", ""))
        user_entry = tk.Entry(content, textvariable=user_var, bg=Theme.SURFACE2, fg=Theme.TEXT,
                              insertbackground=Theme.TEXT, relief="flat", font=("Segoe UI", 11))
        user_entry.pack(fill=tk.X, ipady=8, pady=(2, 12))

        tk.Label(content, text="Web API Key", bg=Theme.SURFACE, fg=Theme.TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w")
        key_var = tk.StringVar(value=self.ra.get("api_key", ""))
        key_entry = tk.Entry(content, textvariable=key_var, bg=Theme.SURFACE2, fg=Theme.TEXT,
                             insertbackground=Theme.TEXT, relief="flat", font=("Segoe UI", 11),
                             show="•")
        key_entry.pack(fill=tk.X, ipady=8, pady=(2, 8))

        status = tk.Label(content, text="", bg=Theme.SURFACE, fg=Theme.TEXT_MUTED,
                          font=("Segoe UI", 9), height=2)
        status.pack(fill=tk.X)

        def save_and_test():
            self.ra["username"] = user_var.get().strip()
            self.ra["api_key"] = key_var.get().strip()
            self._save()
            client = self._ra_client()
            if not client:
                status.configure(text="Enter username and API key", fg=Theme.DANGER)
                return
            status.configure(text="Checking…", fg=Theme.TEXT_MUTED)
            win.update()

            def work():
                try:
                    profile = client.validate()
                    name = profile.get("User", self.ra["username"])
                    points = profile.get("TotalPoints", "?")
                    self.after(0, lambda: (
                        status.configure(
                            text=f"Logged in as {name}  •  {points} points",
                            fg=Theme.SUCCESS
                        ),
                        self._update_ra_btn(),
                        self.status_var.set(f"RA: signed in as {name}")
                    ))
                except Exception as e:
                    err = str(e)
                    self.after(0, lambda: status.configure(
                        text=f"Login failed: {err}", fg=Theme.DANGER))

            threading.Thread(target=work, daemon=True).start()

        # Buttons always visible at bottom
        btn_row = tk.Frame(win, bg=Theme.SURFACE)
        btn_row.pack(side=tk.BOTTOM, fill=tk.X, padx=24, pady=(0, 20))

        save_btn = tk.Button(
            btn_row, text="  Save & Test  ",
            font=("Segoe UI", 11, "bold"),
            bg=Theme.ACCENT, fg="white",
            activebackground=Theme.ACCENT_HOV, activeforeground="white",
            relief="flat", cursor="hand2",
            padx=16, pady=8, command=save_and_test
        )
        save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        close_btn = tk.Button(
            btn_row, text="  Close  ",
            font=("Segoe UI", 11),
            bg=Theme.SURFACE2, fg=Theme.TEXT,
            activebackground=Theme.BORDER, activeforeground=Theme.TEXT,
            relief="flat", cursor="hand2",
            padx=16, pady=8, command=win.destroy
        )
        close_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(6, 0))

        # Enter key submits
        win.bind("<Return>", lambda e: save_and_test())
        user_entry.focus_set()

    def link_ra_game(self, game: dict):
        if not self._ra_client():
            messagebox.showinfo("RA Login", "Sign in to RetroAchievements first (RA button).")
            self.show_ra_settings()
            return

        client = self._ra_client()
        win = tk.Toplevel(self)
        win.title("Link RetroAchievements Game")
        win.geometry("560x520")
        win.minsize(480, 400)
        win.configure(bg=Theme.SURFACE)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text=f"Link: {game.get('name', 'Game')}",
                 font=("Segoe UI", 13, "bold"), bg=Theme.SURFACE, fg=Theme.TEXT).pack(
                     anchor="w", padx=16, pady=(14, 4))
        tk.Label(win, text="Search by name across popular systems + your played games",
                 font=("Segoe UI", 9), bg=Theme.SURFACE, fg=Theme.TEXT_MUTED).pack(
                     anchor="w", padx=16, pady=(0, 8))

        search_row = tk.Frame(win, bg=Theme.SURFACE)
        search_row.pack(fill=tk.X, padx=16, pady=(0, 6))

        q_var = tk.StringVar(value=game.get("name", ""))
        q_entry = tk.Entry(search_row, textvariable=q_var, bg=Theme.SURFACE2, fg=Theme.TEXT,
                           insertbackground=Theme.TEXT, relief="flat", font=("Segoe UI", 11))
        q_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)

        search_btn = tk.Button(search_row, text="Search", font=("Segoe UI", 10, "bold"),
                               bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
                               width=10, pady=6, command=lambda: do_search())
        search_btn.pack(side=tk.LEFT, padx=(8, 0))

        status = tk.Label(win, text="", bg=Theme.SURFACE, fg=Theme.TEXT_MUTED, font=("Segoe UI", 9))
        status.pack(anchor="w", padx=16)

        list_frame = tk.Frame(win, bg=Theme.BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        canvas = tk.Canvas(list_frame, bg=Theme.BG, highlightthickness=0)
        sb = ModernScrollbar(list_frame, command=canvas.yview)
        results_inner = tk.Frame(canvas, bg=Theme.BG)
        results_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=results_inner, anchor="nw", tags="ri")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("ri", width=e.width))

        selected = {"id": game.get("ra_game_id"), "title": "", "console": "", "icon": ""}
        search_icons = {}
        dialog_alive = {"ok": True}

        def _alive() -> bool:
            try:
                return bool(dialog_alive["ok"] and win.winfo_exists())
            except Exception:
                return False

        def clear_results():
            if not _alive():
                return
            try:
                for w in results_inner.winfo_children():
                    w.destroy()
            except tk.TclError:
                pass

        def add_result_row(item: dict):
            if not _alive():
                return
            try:
                row = tk.Frame(results_inner, bg=Theme.SURFACE2, cursor="hand2",
                               highlightthickness=1, highlightbackground=Theme.BORDER, height=52)
                row.pack(fill=tk.X, pady=2, padx=2)
                row.pack_propagate(False)
            except tk.TclError:
                return

            icon_box = tk.Frame(row, bg=Theme.SURFACE2, width=48, height=48)
            icon_box.pack(side=tk.LEFT, padx=4, pady=2)
            icon_box.pack_propagate(False)
            icon_lbl = tk.Label(icon_box, text="🎮", bg=Theme.SURFACE2, fg=Theme.TEXT_MUTED,
                                font=("Segoe UI", 14))
            icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

            icon_path = item.get("icon") or ""
            if icon_path:
                def load_icon(path=icon_path, lbl=icon_lbl, gid=item.get("id")):
                    try:
                        # Download only for this search row — memory only, no disk cache
                        if path.startswith("/"):
                            url = RA_MEDIA + path
                        elif path.startswith("http"):
                            url = path
                        else:
                            url = f"{RA_MEDIA}/Images/{path}"
                        data = fetch_image_bytes(url, timeout=10)
                        photo = photo_from_bytes(data, size=44)
                        if not photo:
                            return
                        search_icons[gid] = photo

                        def apply_icon(p=photo, l=lbl):
                            if not _alive():
                                return
                            try:
                                l.configure(image=p, text="")
                            except tk.TclError:
                                pass
                        self.after(0, apply_icon)
                    except Exception:
                        pass
                threading.Thread(target=load_icon, daemon=True).start()

            text_fr = tk.Frame(row, bg=Theme.SURFACE2)
            text_fr.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
            title = item.get("title", "?")
            console = item.get("console", "")
            gid = item.get("id")
            t1 = tk.Label(text_fr, text=title, font=("Segoe UI", 10, "bold"),
                          bg=Theme.SURFACE2, fg=Theme.TEXT, anchor="w")
            t1.pack(fill=tk.X, pady=(8, 0))
            sub = f"ID {gid}" + (f"  •  {console}" if console else "")
            t2 = tk.Label(text_fr, text=sub, font=("Segoe UI", 9),
                          bg=Theme.SURFACE2, fg=Theme.TEXT_MUTED, anchor="w")
            t2.pack(fill=tk.X)

            def on_click(e=None, it=item, r=row):
                if not _alive():
                    return
                selected["id"] = it["id"]
                selected["title"] = it.get("title", "")
                selected["console"] = it.get("console", "")
                selected["icon"] = it.get("icon", "")
                try:
                    for w in results_inner.winfo_children():
                        w.configure(highlightbackground=Theme.BORDER)
                    r.configure(highlightbackground=Theme.ACCENT)
                    status.configure(text=f"Selected: {it.get('title')} (ID {it['id']})", fg=Theme.ACCENT)
                except tk.TclError:
                    pass

            def on_double(e=None):
                on_click()
                confirm_link()

            for w in (row, icon_box, icon_lbl, text_fr, t1, t2):
                w.bind("<Button-1>", on_click)
                w.bind("<Double-Button-1>", on_double)

        def do_search():
            if not _alive():
                return
            query = q_var.get().strip()
            if len(query) < 2:
                status.configure(text="Type at least 2 characters", fg=Theme.DANGER)
                return
            status.configure(text="Searching popular systems…", fg=Theme.TEXT_MUTED)
            clear_results()
            try:
                win.update()
            except tk.TclError:
                return

            def work():
                try:
                    items = client.search_games(query)

                    def show():
                        if not _alive():
                            return
                        clear_results()
                        try:
                            if not items:
                                status.configure(
                                    text="No games found — try a shorter name",
                                    fg=Theme.TEXT_MUTED,
                                )
                                return
                            status.configure(
                                text=f"{len(items)} result(s) — click one, then Link",
                                fg=Theme.TEXT_MUTED,
                            )
                            for it in items:
                                if not _alive():
                                    return
                                add_result_row(it)
                        except tk.TclError:
                            pass

                    self.after(0, show)
                except Exception as e:
                    err = str(e)

                    def show_err():
                        if not _alive():
                            return
                        try:
                            status.configure(text=err, fg=Theme.DANGER)
                        except tk.TclError:
                            pass

                    self.after(0, show_err)

            threading.Thread(target=work, daemon=True).start()

        def confirm_link():
            if not _alive():
                return
            gid = selected.get("id")
            if not gid:
                status.configure(text="Select a game from the list first", fg=Theme.DANGER)
                return
            game["ra_game_id"] = int(gid)
            title = selected.get("title") or f"Game {gid}"
            console = (selected.get("console") or "").strip()
            # Auto-fill system from RA console name
            if console:
                game["system"] = console
            self._save()
            self.status_var.set(f"Linked to RA: {title}" + (f" ({console})" if console else ""))
            dialog_alive["ok"] = False

            def after_link():
                try:
                    self._fetch_ra_progress(game)
                except Exception:
                    pass

                def finish():
                    self.refresh_library()
                    messagebox.showinfo("Linked", f"Linked to:\n{title}\n{console}".strip())
                    try:
                        if win.winfo_exists():
                            win.destroy()
                    except tk.TclError:
                        pass

                self.after(0, finish)

            threading.Thread(target=after_link, daemon=True).start()

        def unlink():
            game["ra_game_id"] = None
            game.pop("ra_progress", None)
            self._save()
            self.status_var.set("RA link removed")
            self.refresh_library()
            dialog_alive["ok"] = False
            win.destroy()

        def manual_id():
            if not _alive():
                return
            val = themed_input(win, "RA Game ID", "Enter the RetroAchievements Game ID:", initial="")
            if not val or not val.strip():
                return
            try:
                gid = int(val.strip())
            except ValueError:
                messagebox.showerror("Invalid", "Must be a number.", parent=win)
                return
            status.configure(text="Looking up…", fg=Theme.TEXT_MUTED)

            def work():
                try:
                    info = client.get_game(gid)
                    item = {
                        "id": gid,
                        "title": info.get("Title") or info.get("GameTitle") or f"Game {gid}",
                        "console": info.get("ConsoleName") or info.get("Console") or "",
                        "icon": info.get("ImageIcon") or info.get("imageIcon") or "",
                    }

                    def show():
                        if not _alive():
                            return
                        try:
                            clear_results()
                            add_result_row(item)
                            selected.update(item)
                            status.configure(
                                text=f"Selected: {item['title']}", fg=Theme.ACCENT
                            )
                        except tk.TclError:
                            pass

                    self.after(0, show)
                except Exception as e:
                    err = str(e)

                    def show_err():
                        if not _alive():
                            return
                        try:
                            status.configure(text=err, fg=Theme.DANGER)
                        except tk.TclError:
                            pass

                    self.after(0, show_err)

            threading.Thread(target=work, daemon=True).start()

        def on_close():
            dialog_alive["ok"] = False
            try:
                win.destroy()
            except tk.TclError:
                pass

        win.protocol("WM_DELETE_WINDOW", on_close)

        btn_row = tk.Frame(win, bg=Theme.SURFACE)
        btn_row.pack(fill=tk.X, padx=16, pady=(4, 16))

        link_btn = tk.Button(btn_row, text="Link Selected", font=("Segoe UI", 10, "bold"),
                             bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
                             width=14, pady=8, command=confirm_link)
        link_btn.pack(side=tk.LEFT)

        if game.get("ra_game_id"):
            tk.Button(btn_row, text="Unlink", font=("Segoe UI", 10),
                      bg=Theme.SURFACE2, fg=Theme.DANGER, relief="flat", cursor="hand2",
                      width=10, pady=8, command=unlink).pack(side=tk.LEFT, padx=8)

        tk.Button(btn_row, text="Cancel", font=("Segoe UI", 10),
                  bg=Theme.SURFACE2, fg=Theme.TEXT, relief="flat", cursor="hand2",
                  width=10, pady=8, command=on_close).pack(side=tk.RIGHT)

        tk.Button(btn_row, text="Enter ID…", font=("Segoe UI", 10),
                  bg=Theme.SURFACE2, fg=Theme.TEXT_MUTED, relief="flat", cursor="hand2",
                  width=10, pady=8, command=manual_id).pack(side=tk.RIGHT, padx=(0, 8))

        q_entry.bind("<Return>", lambda e: do_search())
        q_entry.focus_set()
        q_entry.select_range(0, tk.END)
        if q_var.get().strip():
            win.after(200, do_search)

    def _progress_game_id(self, game: dict) -> int | None:
        """RA set ID used for card progress (core or chosen subset)."""
        for key in ("ra_display_set_id", "ra_game_id"):
            val = game.get(key)
            if val:
                try:
                    return int(val)
                except Exception:
                    pass
        return None

    def _fetch_ra_progress(self, game: dict):
        """Fetch and cache achievement progress for the selected set."""
        client = self._ra_client()
        ra_id = self._progress_game_id(game)
        if not client or not ra_id:
            return None
        try:
            data = client.get_game_progress(int(ra_id))
            total = data.get("NumAchievements") or len(data.get("Achievements") or {})
            awarded = data.get("NumAwardedToUser") or 0
            awarded_hc = data.get("NumAwardedToUserHardcore") or 0
            pct = data.get("UserCompletion") or "0%"
            total_i = int(total) if total else 0
            awarded_i = int(awarded)
            awarded_hc_i = int(awarded_hc)
            progress = {
                "awarded": awarded_i,
                "awarded_hc": awarded_hc_i,
                "total": total_i,
                "pct": str(pct),
                "mastered": total_i > 0 and awarded_i >= total_i,
                "hc_mastered": total_i > 0 and awarded_hc_i >= total_i,
                "icon": data.get("ImageIcon") or data.get("imageIcon") or "",
                "boxart": data.get("ImageBoxArt") or data.get("imageBoxArt") or "",
                "title": data.get("Title") or data.get("title") or "",
                "console": data.get("ConsoleName") or data.get("Console") or "",
                "set_id": int(ra_id),
            }
            game["ra_progress"] = progress
            console = (progress.get("console") or "").strip()
            if console and not (game.get("system") or "").strip():
                game["system"] = console
            self._save()
            return progress
        except Exception:
            return None

    def set_ra_display_set(self, game: dict, set_id: int | None, label: str = ""):
        """Choose which achievement set shows on the game card."""
        game["ra_display_set_id"] = int(set_id) if set_id else None
        self._save()
        self.status_var.set(
            f"Card set: {label}" if label else "Card set: Core achievements"
        )

        def work():
            self._fetch_ra_progress(game)
            self.after(0, self.refresh_library)

        threading.Thread(target=work, daemon=True).start()

    def _pick_subset_for_card(self, game: dict):
        """Load subsets and let the user pick which set shows on the card."""
        client = self._ra_client()
        core = game.get("ra_game_id")
        if not client or not core:
            return
        self.status_var.set("Looking up subsets…")

        def work():
            try:
                subsets = client.find_subsets(int(core))
            except Exception as e:
                self.after(0, lambda: (
                    self.status_var.set("Subset lookup failed"),
                    messagebox.showerror("Subsets", str(e)),
                ))
                return

            def show():
                if not subsets:
                    messagebox.showinfo(
                        "Subsets",
                        "No subset sets found for this game on RetroAchievements.",
                    )
                    self.status_var.set("No subsets found")
                    return
                win = tk.Toplevel(self)
                win.title("Card achievement set")
                win.geometry("440x420")
                win.minsize(380, 320)
                win.configure(bg=Theme.SURFACE)
                win.transient(self)
                win.grab_set()
                try:
                    self.update_idletasks()
                    px = self.winfo_rootx() + (self.winfo_width() - 440) // 2
                    py = self.winfo_rooty() + (self.winfo_height() - 420) // 2
                    win.geometry(f"+{max(0, px)}+{max(0, py)}")
                except Exception:
                    pass

                # Header
                tk.Label(
                    win, text="Choose set for card progress",
                    font=("Segoe UI", 13, "bold"),
                    bg=Theme.SURFACE, fg=Theme.TEXT,
                ).pack(anchor="w", padx=18, pady=(16, 4))
                tk.Label(
                    win,
                    text="This controls the progress badge on the game card.",
                    font=("Segoe UI", 9),
                    bg=Theme.SURFACE, fg=Theme.TEXT_MUTED,
                ).pack(anchor="w", padx=18, pady=(0, 10))

                # Close pinned to bottom
                bottom = tk.Frame(win, bg=Theme.SURFACE)
                bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=(8, 16))
                tk.Button(
                    bottom, text="  Close  ", font=("Segoe UI", 10),
                    bg=Theme.SURFACE2, fg=Theme.TEXT, relief="flat",
                    cursor="hand2", padx=14, pady=7, command=win.destroy,
                    activebackground=Theme.BORDER, activeforeground=Theme.TEXT,
                ).pack(side=tk.RIGHT)

                # Scrollable list of sets
                list_outer = tk.Frame(win, bg=Theme.SURFACE)
                list_outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 4))
                sc = tk.Canvas(list_outer, bg=Theme.SURFACE, highlightthickness=0)
                sb = ModernScrollbar(list_outer, command=sc.yview)
                body = tk.Frame(sc, bg=Theme.SURFACE)
                body.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
                sc.create_window((0, 0), window=body, anchor="nw", tags="body")
                sc.configure(yscrollcommand=sb.set)
                sc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                sb.pack(side=tk.RIGHT, fill=tk.Y)
                sc.bind("<Configure>", lambda e: sc.itemconfig("body", width=e.width))

                def _wheel(e):
                    sc.yview_scroll(int(-1 * (e.delta / 120)), "units")
                sc.bind_all("<MouseWheel>", _wheel)
                win.bind("<Destroy>", lambda e: sc.unbind_all("<MouseWheel>") if e.widget == win else None)

                cur = game.get("ra_display_set_id")

                def pick(sid, label):
                    self.set_ra_display_set(game, sid, label)
                    win.destroy()

                def add_row(parent, title, subtitle, selected, on_click):
                    row = tk.Frame(
                        parent, bg=Theme.SURFACE2, cursor="hand2",
                        highlightthickness=1,
                        highlightbackground=Theme.ACCENT if selected else Theme.BORDER,
                    )
                    row.pack(fill=tk.X, padx=6, pady=4)
                    tk.Label(
                        row, text=title, font=("Segoe UI", 10, "bold"),
                        bg=Theme.SURFACE2, fg=Theme.TEXT, anchor="w",
                    ).pack(fill=tk.X, padx=12, pady=(10, 0 if subtitle else 10))
                    if subtitle:
                        tk.Label(
                            row, text=subtitle, font=("Segoe UI", 8),
                            bg=Theme.SURFACE2, fg=Theme.TEXT_MUTED, anchor="w",
                        ).pack(fill=tk.X, padx=12, pady=(2, 10))
                    row.bind("<Button-1>", lambda e: on_click())
                    for w in row.winfo_children():
                        w.bind("<Button-1>", lambda e: on_click())
                    return row

                add_row(
                    body, "Core set", None,
                    selected=not cur,
                    on_click=lambda: pick(None, "Core achievements"),
                )
                for s in subsets:
                    sid = int(s["id"])
                    label = s.get("label") or s.get("title") or str(sid)
                    on = bool(cur) and int(cur) == sid
                    add_row(
                        body, label, s.get("title", ""),
                        selected=on,
                        on_click=lambda i=sid, lab=label: pick(i, lab),
                    )

                self.status_var.set(f"{len(subsets)} subset(s) found")

            self.after(0, show)

        threading.Thread(target=work, daemon=True).start()

    def _refresh_progress_ui(self, game: dict):
        self.status_var.set("Refreshing RA progress…")

        def work():
            p = self._fetch_ra_progress(game)
            self.after(0, lambda: (
                self.refresh_library(),
                self.status_var.set(
                    f"Progress: {p['awarded']}/{p['total']} ({p['pct']})" if p else "Could not refresh progress"
                )
            ))

        threading.Thread(target=work, daemon=True).start()

    def use_ra_icon(self, game: dict, prefer: str = "icon"):
        """
        Set library cover from RA images.
        prefer="icon" → ImageIcon (the small icon next to the title on the RA game page)
        prefer="box"  → ImageBoxArt
        """
        client = self._ra_client()
        if not client or not game.get("ra_game_id"):
            messagebox.showinfo("RA", "Link this game to RetroAchievements first.")
            return
        self.status_var.set("Downloading RA icon…")

        def work():
            try:
                data = client.get_game(int(game["ra_game_id"]))
                if prefer == "box":
                    path = (
                        data.get("ImageBoxArt") or data.get("imageBoxArt")
                        or data.get("ImageIcon") or data.get("imageIcon")
                        or ""
                    )
                else:
                    # Same icon as on the RA game page header (next to the title)
                    path = (
                        data.get("ImageIcon") or data.get("imageIcon")
                        or data.get("ImageTitle") or data.get("imageTitle")
                        or data.get("ImageBoxArt") or data.get("imageBoxArt")
                        or ""
                    )
                if not path:
                    raise RuntimeError("No image available on RA for this game")
                if path.startswith("/"):
                    url = RA_MEDIA + path
                elif path.startswith("http"):
                    url = path
                else:
                    url = f"{RA_MEDIA}/Images/{path}"
                req = urllib.request.Request(url, headers={"User-Agent": "LocalGameLibrary/1.0"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    img_bytes = resp.read()
                ext = ".jpg" if (".jpg" in path.lower() or ".jpeg" in path.lower()) else ".png"
                dest = COVERS_DIR / f"{game['id']}_ra{ext}"
                dest.write_bytes(img_bytes)
                old = game.get("cover")
                game["cover"] = str(dest)
                game.setdefault("cover_mode", "fill")
                if old and Path(old).exists() and Path(old) != dest:
                    try:
                        Path(old).unlink()
                    except Exception:
                        pass
                self._save()
                self.after(0, lambda: (
                    self.refresh_library(),
                    self.status_var.set("Cover set to RA game icon")
                ))
            except Exception as e:
                err = str(e)
                self.after(0, lambda: (
                    self.status_var.set("Failed to get RA icon"),
                    messagebox.showerror("RA Icon", err)
                ))

        threading.Thread(target=work, daemon=True).start()

    def show_achievements(self, game: dict):
        client = self._ra_client()
        if not client:
            messagebox.showinfo("RA Login", "Sign in to RetroAchievements first (RA button).")
            self.show_ra_settings()
            return
        ra_id = game.get("ra_game_id")
        if not ra_id:
            if themed_confirm(self, "Not linked", "This game is not linked to RA.\nLink it now?"):
                self.link_ra_game(game)
            return

        win = tk.Toplevel(self)
        win.title(f"Achievements — {game.get('name', 'Game')}")
        win.geometry("600x680")
        win.configure(bg=Theme.BG)
        win.transient(self)

        header = tk.Frame(win, bg=Theme.SURFACE)
        header.pack(fill=tk.X)

        def _short_title(text: str, max_len: int = 42) -> str:
            t = (text or "").strip()
            if len(t) <= max_len:
                return t
            return t[: max_len - 1] + "…"

        # Row 1: title (left) + fixed progress column (right) — pack right first
        top_row = tk.Frame(header, bg=Theme.SURFACE)
        top_row.pack(fill=tk.X, padx=16, pady=(12, 6))

        right_col = tk.Frame(top_row, bg=Theme.SURFACE)
        right_col.pack(side=tk.RIGHT, padx=(10, 0))

        progress_lbl = tk.Label(
            right_col, text="", font=("Segoe UI", 9),
            bg=Theme.SURFACE, fg=Theme.TEXT_MUTED, anchor="e", justify="right",
        )
        progress_lbl.pack(anchor="e")

        card_set_btn = tk.Button(
            right_col, text="Use on card", font=("Segoe UI", 8, "bold"),
            bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
            padx=10, pady=3,
            activebackground=Theme.ACCENT_HOV, activeforeground="white",
        )
        card_set_btn.pack(anchor="e", pady=(5, 0))

        title_lbl = tk.Label(
            top_row, text="Loading…",
            font=("Segoe UI", 13, "bold"), bg=Theme.SURFACE, fg=Theme.TEXT,
            anchor="w",
        )
        title_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Hover marquee for long titles (scroll left ↔ right)
        title_marquee = {
            "full": "",
            "after_id": None,
            "pos": 0.0,
            "direction": 1,
            "running": False,
            "pause": 0,
            "visible": 56,
        }

        def _title_visible_chars() -> int:
            """Fit as many characters as possible before the Use on card column."""
            try:
                w = max(0, int(title_lbl.winfo_width()) - 6)
                if w < 60:
                    # Before first layout pass, estimate from row minus right column
                    w = max(
                        60,
                        int(top_row.winfo_width()) - int(right_col.winfo_reqwidth()) - 28,
                    )
                # Segoe UI 13 bold ≈ 8.2 px/char
                return max(20, min(140, int(w / 8.2)))
            except Exception:
                return title_marquee["visible"]

        def _title_refresh_visible():
            title_marquee["visible"] = _title_visible_chars()
            if not title_marquee["running"]:
                try:
                    title_lbl.configure(text=_title_short())
                except Exception:
                    pass

        def _title_short():
            return _short_title(title_marquee["full"], title_marquee["visible"])

        def _title_step():
            if not title_marquee["running"]:
                return
            full = title_marquee["full"]
            vis = title_marquee["visible"]
            if len(full) <= vis:
                try:
                    title_lbl.configure(text=full)
                except Exception:
                    pass
                return
            if title_marquee["pause"] > 0:
                title_marquee["pause"] -= 1
                title_marquee["after_id"] = win.after(28, _title_step)
                return
            max_offset = max(0.0, float(len(full) - vis))
            title_marquee["pos"] += title_marquee["direction"] * 0.35
            if title_marquee["pos"] >= max_offset:
                title_marquee["pos"] = max_offset
                title_marquee["direction"] = -1
                title_marquee["pause"] = 22
            elif title_marquee["pos"] <= 0:
                title_marquee["pos"] = 0.0
                title_marquee["direction"] = 1
                title_marquee["pause"] = 22
            start = int(title_marquee["pos"])
            try:
                title_lbl.configure(text=full[start: start + vis + 1])
            except Exception:
                return
            title_marquee["after_id"] = win.after(30, _title_step)

        def _title_start_marquee(_e=None):
            if title_marquee["running"]:
                return
            full = title_marquee["full"]
            if len(full) <= title_marquee["visible"]:
                return
            title_marquee["running"] = True
            title_marquee["pos"] = 0.0
            title_marquee["direction"] = 1
            title_marquee["pause"] = 10
            _title_step()

        def _title_stop_marquee(_e=None):
            title_marquee["running"] = False
            if title_marquee["after_id"] is not None:
                try:
                    win.after_cancel(title_marquee["after_id"])
                except Exception:
                    pass
                title_marquee["after_id"] = None
            try:
                title_lbl.configure(text=_title_short())
            except Exception:
                pass

        def _set_title_text(full: str):
            title_marquee["full"] = full or ""
            _title_stop_marquee()
            _title_refresh_visible()
            try:
                title_lbl.configure(text=_title_short())
            except Exception:
                pass

        title_lbl.bind("<Enter>", _title_start_marquee)
        title_lbl.bind("<Leave>", _title_stop_marquee)
        title_lbl.bind("<Configure>", lambda e: _title_refresh_visible())
        top_row.bind("<Configure>", lambda e: _title_refresh_visible())

        def use_on_card():
            set_id = int(active_tab["id"])
            if set_id == int(ra_id):
                store_id = None
                label = "Core achievements"
            else:
                store_id = set_id
                try:
                    label = tab_buttons.get(set_id).cget("text").strip() if set_id in tab_buttons else "Subset"
                except Exception:
                    label = "Subset"
            self.set_ra_display_set(game, store_id, label)
            update_card_btn()

        def update_card_btn():
            cur_disp = game.get("ra_display_set_id") or game.get("ra_game_id")
            is_card = str(cur_disp) == str(active_tab["id"])
            try:
                if is_card:
                    card_set_btn.configure(
                        text="✓ On card", state="disabled",
                        bg=Theme.SURFACE2, fg=Theme.TEXT_MUTED,
                    )
                else:
                    card_set_btn.configure(
                        text="Use on card", state="normal",
                        bg=Theme.ACCENT, fg="white",
                    )
            except Exception:
                pass

        card_set_btn.configure(command=use_on_card)

        # Row 2: horizontally scrollable set tabs + arrow buttons
        tab_outer = tk.Frame(header, bg=Theme.SURFACE)
        tab_outer.pack(fill=tk.X, padx=8, pady=(2, 10))

        def _tab_scroll_by(steps: int):
            tab_canvas.xview_scroll(steps, "units")
            _update_tab_arrows()

        tab_left_btn = tk.Button(
            tab_outer, text="◀", font=("Segoe UI", 9, "bold"),
            bg=Theme.SURFACE2, fg=Theme.TEXT, relief="flat", cursor="hand2",
            width=2, pady=2,
            activebackground=Theme.BORDER, activeforeground=Theme.TEXT,
            command=lambda: _tab_scroll_by(-3),
        )
        tab_left_btn.pack(side=tk.LEFT, padx=(0, 4))

        tab_right_btn = tk.Button(
            tab_outer, text="▶", font=("Segoe UI", 9, "bold"),
            bg=Theme.SURFACE2, fg=Theme.TEXT, relief="flat", cursor="hand2",
            width=2, pady=2,
            activebackground=Theme.BORDER, activeforeground=Theme.TEXT,
            command=lambda: _tab_scroll_by(3),
        )
        tab_right_btn.pack(side=tk.RIGHT, padx=(4, 0))

        tab_canvas = tk.Canvas(tab_outer, bg=Theme.SURFACE, highlightthickness=0, height=34)
        tab_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tab_bar = tk.Frame(tab_canvas, bg=Theme.SURFACE)
        tab_window = tab_canvas.create_window((0, 0), window=tab_bar, anchor="nw")

        def _update_tab_arrows(_event=None):
            try:
                bbox = tab_canvas.bbox("all")
                if not bbox:
                    tab_left_btn.configure(state="disabled", fg=Theme.TEXT_MUTED)
                    tab_right_btn.configure(state="disabled", fg=Theme.TEXT_MUTED)
                    return
                total = bbox[2]
                visible = max(1, tab_canvas.winfo_width())
                if total <= visible + 2:
                    tab_left_btn.configure(state="disabled", fg=Theme.TEXT_MUTED)
                    tab_right_btn.configure(state="disabled", fg=Theme.TEXT_MUTED)
                    return
                left, right = tab_canvas.xview()
                tab_left_btn.configure(
                    state="normal" if left > 0.005 else "disabled",
                    fg=Theme.TEXT if left > 0.005 else Theme.TEXT_MUTED,
                )
                tab_right_btn.configure(
                    state="normal" if right < 0.995 else "disabled",
                    fg=Theme.TEXT if right < 0.995 else Theme.TEXT_MUTED,
                )
            except Exception:
                pass

        def _sync_tab_scroll(_event=None):
            tab_bar.update_idletasks()
            bbox = tab_canvas.bbox("all")
            if bbox:
                tab_canvas.configure(scrollregion=bbox)
                h = max(28, tab_bar.winfo_reqheight())
                tab_canvas.configure(height=h)
            _update_tab_arrows()

        tab_bar.bind("<Configure>", _sync_tab_scroll)
        tab_canvas.bind("<Configure>", lambda e: _update_tab_arrows())

        def _tab_wheel(e):
            tab_canvas.xview_scroll(int(-1 * (e.delta / 120)), "units")
            _update_tab_arrows()
            return "break"

        tab_canvas.bind("<MouseWheel>", _tab_wheel)
        tab_bar.bind("<MouseWheel>", _tab_wheel)

        # Click-drag to pan tabs
        tab_drag = {"x": 0, "view": 0.0}

        def _tab_press(e):
            tab_drag["x"] = e.x_root
            tab_drag["view"] = tab_canvas.xview()[0]

        def _tab_motion(e):
            if tab_canvas.bbox("all") is None:
                return
            dx = e.x_root - tab_drag["x"]
            total = tab_canvas.bbox("all")[2]
            visible = max(1, tab_canvas.winfo_width())
            if total <= visible:
                return
            frac = tab_drag["view"] - (dx / total)
            frac = max(0.0, min(1.0, frac))
            tab_canvas.xview_moveto(frac)
            _update_tab_arrows()

        tab_canvas.bind("<ButtonPress-1>", _tab_press)
        tab_canvas.bind("<B1-Motion>", _tab_motion)
        tab_bar.bind("<ButtonPress-1>", _tab_press)
        tab_bar.bind("<B1-Motion>", _tab_motion)

        tab_buttons = {}
        active_tab = {"id": int(ra_id)}

        list_wrap = tk.Frame(win, bg=Theme.BG)
        list_wrap.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        canvas = tk.Canvas(list_wrap, bg=Theme.BG, highlightthickness=0)
        sb = ModernScrollbar(list_wrap, command=canvas.yview)
        inner = tk.Frame(canvas, bg=Theme.BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", tags="inner")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("inner", width=e.width))

        def on_wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_wheel)
        win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>") if e.widget == win else None)

        def clear_list():
            for w in inner.winfo_children():
                w.destroy()

        def style_tabs():
            for tid, btn in tab_buttons.items():
                on = tid == active_tab["id"]
                btn.configure(
                    bg=Theme.ACCENT if on else Theme.SURFACE2,
                    fg="white" if on else Theme.TEXT,
                )

        def render_list(data: dict):
            clear_list()
            title = data.get("Title") or game.get("name", "Game")
            num = data.get("NumAchievements") or len(data.get("Achievements") or {})
            awarded = data.get("NumAwardedToUser") or 0
            awarded_hc = data.get("NumAwardedToUserHardcore") or 0
            completion = data.get("UserCompletion") or "0%"
            _set_title_text(title)
            # Two-line progress so it never collides with the title
            progress_lbl.configure(
                text=f"{awarded}/{num}  ({completion})\nHC: {awarded_hc}"
            )
            update_card_btn()
            achievements = data.get("Achievements") or {}
            items = sorted(
                achievements.values(),
                key=lambda a: (a.get("DisplayOrder") or a.get("displayOrder") or 0,
                               a.get("ID") or a.get("id") or 0)
            )
            BADGE_SIZE = 64
            try:
                desc_wrap = max(220, int(canvas.winfo_width()) - 170)
            except Exception:
                desc_wrap = 360

            for ach in items:
                title_a = ach.get("Title") or ach.get("title") or "?"
                desc = ach.get("Description") or ach.get("description") or ""
                points = ach.get("Points") or ach.get("points") or 0
                badge = ach.get("BadgeName") or ach.get("badgeName") or ""
                ach_id = ach.get("ID") or ach.get("id")
                earned = ach.get("DateEarned") or ach.get("dateEarned")
                earned_hc = ach.get("DateEarnedHardcore") or ach.get("dateEarnedHardcore")
                unlocked = bool(earned or earned_hc)
                ach_url = f"https://retroachievements.org/achievement/{ach_id}" if ach_id else None

                row_bg = Theme.SURFACE if unlocked else Theme.SURFACE2
                # No fixed height — long descriptions expand the row instead of clipping
                row = tk.Frame(inner, bg=row_bg,
                               highlightthickness=1, highlightbackground=Theme.BORDER)
                row.pack(fill=tk.X, pady=2, padx=4)

                def open_ach(e=None, url=ach_url):
                    if url:
                        webbrowser.open(url)

                badge_box = tk.Frame(row, bg=row_bg, width=BADGE_SIZE, height=BADGE_SIZE,
                                     cursor="hand2")
                badge_box.pack(side=tk.LEFT, padx=(0, 0), pady=6)
                badge_box.pack_propagate(False)
                badge_box.bind("<Button-1>", open_ach)

                badge_lbl = tk.Label(
                    badge_box,
                    text="🏆" if unlocked else "🔒",
                    font=("Segoe UI", 22),
                    bg=row_bg,
                    fg="#fbbf24" if unlocked else Theme.TEXT_MUTED,
                    cursor="hand2"
                )
                badge_lbl.place(relx=0.5, rely=0.5, anchor="center")
                badge_lbl.bind("<Button-1>", open_ach)

                if badge:
                    def load_badge(b=badge, lbl=badge_lbl, is_on=unlocked, box_bg=row_bg, size=BADGE_SIZE):
                        try:
                            suffix = "" if is_on else "_lock"
                            cache_key = f"{b}{suffix}_{size}"
                            if cache_key in self._ra_badge_images:
                                photo = self._ra_badge_images[cache_key]
                            else:
                                url = f"{RA_MEDIA}/Badge/{b}{suffix}.png"
                                data_b = fetch_image_bytes(url, timeout=12)
                                photo = photo_from_bytes(data_b, size=max(16, size - 4))
                                if not photo:
                                    return
                                self._ra_badge_images[cache_key] = photo

                            def apply(p=photo, l=lbl):
                                try:
                                    l.configure(image=p, text="", bg=box_bg)
                                except tk.TclError:
                                    pass
                            self.after(0, apply)
                        except Exception:
                            pass
                    threading.Thread(target=load_badge, daemon=True).start()

                pts_text = f"{points} pts"
                if earned_hc:
                    pts_text += "\nHC ✓"
                elif earned:
                    pts_text += "\n✓"
                pts_lbl = tk.Label(row, text=pts_text, font=("Segoe UI", 9),
                                   bg=row_bg, fg=Theme.ACCENT if unlocked else Theme.TEXT_MUTED,
                                   justify="right", cursor="hand2")
                pts_lbl.pack(side=tk.RIGHT, padx=12, pady=8)
                pts_lbl.bind("<Button-1>", open_ach)

                text_fr = tk.Frame(row, bg=row_bg, cursor="hand2")
                text_fr.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 6), pady=8)
                text_fr.bind("<Button-1>", open_ach)

                t1 = tk.Label(text_fr, text=title_a, font=("Segoe UI", 10, "bold"),
                              bg=row_bg, fg=Theme.TEXT if unlocked else Theme.TEXT_MUTED,
                              anchor="w", cursor="hand2")
                t1.pack(fill=tk.X)
                t1.bind("<Button-1>", open_ach)

                t2 = tk.Label(text_fr, text=desc, font=("Segoe UI", 9),
                              bg=row_bg, fg=Theme.TEXT_MUTED, anchor="nw",
                              wraplength=desc_wrap, justify="left", cursor="hand2")
                t2.pack(fill=tk.X, pady=(2, 0))
                t2.bind("<Button-1>", open_ach)
                # Keep wrap in sync when the window is resized
                t2._is_ach_desc = True

                row.bind("<Button-1>", open_ach)

            def _update_desc_wrap(event=None):
                try:
                    wrap = max(220, int(canvas.winfo_width()) - 170)
                except Exception:
                    return
                for child in inner.winfo_children():
                    for sub in child.winfo_children():
                        if isinstance(sub, tk.Frame):
                            for lab in sub.winfo_children():
                                if getattr(lab, "_is_ach_desc", False):
                                    try:
                                        lab.configure(wraplength=wrap)
                                    except Exception:
                                        pass

            canvas.bind("<Configure>", lambda e: (
                canvas.itemconfig("inner", width=e.width),
                _update_desc_wrap(),
            ))

        def load_set(set_id: int, update_card_progress: bool = False):
            active_tab["id"] = int(set_id)
            style_tabs()
            _set_title_text("Loading…")
            progress_lbl.configure(text="")
            update_card_btn()
            clear_list()
            # Scroll active tab into view
            try:
                btn = tab_buttons.get(int(set_id))
                if btn is not None:
                    tab_bar.update_idletasks()
                    bx = btn.winfo_x()
                    bw = btn.winfo_width()
                    total = max(1, tab_bar.winfo_reqwidth())
                    visible = max(1, tab_canvas.winfo_width())
                    if total > visible:
                        # Center tab roughly in view
                        target = max(0, bx - (visible - bw) // 2)
                        tab_canvas.xview_moveto(target / total)
                    _update_tab_arrows()
            except Exception:
                pass

            def work():
                try:
                    data = client.get_game_progress(int(set_id))
                    if update_card_progress and self._progress_game_id(game) == int(set_id):
                        total = data.get("NumAchievements") or len(data.get("Achievements") or {})
                        awarded = data.get("NumAwardedToUser") or 0
                        awarded_hc = data.get("NumAwardedToUserHardcore") or 0
                        total_i = int(total) if total else 0
                        awarded_i = int(awarded)
                        awarded_hc_i = int(awarded_hc)
                        game["ra_progress"] = {
                            "awarded": awarded_i,
                            "awarded_hc": awarded_hc_i,
                            "total": total_i,
                            "pct": str(data.get("UserCompletion") or "0%"),
                            "mastered": total_i > 0 and awarded_i >= total_i,
                            "hc_mastered": total_i > 0 and awarded_hc_i >= total_i,
                            "icon": data.get("ImageIcon") or "",
                            "boxart": data.get("ImageBoxArt") or "",
                            "title": data.get("Title") or "",
                            "console": data.get("ConsoleName") or data.get("Console") or "",
                            "set_id": int(set_id),
                        }
                        console = (game["ra_progress"].get("console") or "").strip()
                        if console and not (game.get("system") or "").strip():
                            game["system"] = console
                        self._save()
                        self.after(0, self.refresh_library)
                    self.after(0, lambda: render_list(data))
                except Exception as e:
                    err = str(e)
                    self.after(0, lambda: title_lbl.configure(text=f"Error: {err}", fg=Theme.DANGER))

            threading.Thread(target=work, daemon=True).start()

        def add_tab(set_id: int, label: str):
            btn = tk.Button(
                tab_bar, text=f"  {label}  ", font=("Segoe UI", 9, "bold"),
                bg=Theme.SURFACE2, fg=Theme.TEXT, relief="flat", cursor="hand2",
                padx=6, pady=3,
                command=lambda sid=set_id: load_set(sid),
            )
            btn.pack(side=tk.LEFT, padx=(0, 6))
            btn.bind("<MouseWheel>", _tab_wheel)
            tab_buttons[int(set_id)] = btn

        # Load core + discover subsets
        def bootstrap():
            try:
                subsets = client.find_subsets(int(ra_id))
            except Exception:
                subsets = []

            def build_tabs():
                add_tab(int(ra_id), "Core")
                for s in subsets:
                    add_tab(int(s["id"]), s.get("label") or "Subset")
                if not subsets:
                    # still show core only
                    pass
                style_tabs()
                # Prefer opening the set currently shown on the card
                open_id = self._progress_game_id(game) or int(ra_id)
                load_set(int(open_id), update_card_progress=True)

            self.after(0, build_tabs)

        threading.Thread(target=bootstrap, daemon=True).start()

    @staticmethod
    def _menu_label(icon: str, text: str) -> str:
        """Consistent menu row: two spaces, icon, two spaces, label."""
        return f"  {icon}  {text}"

    def show_context_menu(self, game: dict):
        menu = tk.Menu(self, tearoff=0, bg=Theme.SURFACE2, fg=Theme.TEXT,
                       activebackground=Theme.ACCENT, activeforeground="white",
                       relief="flat", font=("Segoe UI", 10), bd=0)
        L = self._menu_label
        menu.add_command(label=L("▶", "Play"), command=lambda: self.launch_game(game))
        menu.add_command(label=L("🔑", "Play as Administrator"),
                         command=lambda: self.launch_game(game, as_admin=True))
        menu.add_separator()

        # RA
        if game.get("ra_game_id"):
            menu.add_command(label=L("🏆", "View Achievements"),
                             command=lambda: self.show_achievements(game))
            menu.add_command(label=L("🔄", "Refresh RA Progress"),
                             command=lambda: self._refresh_progress_ui(game))
            # Choose which set feeds the card progress badge
            set_menu = tk.Menu(menu, tearoff=0, bg=Theme.SURFACE2, fg=Theme.TEXT,
                               activebackground=Theme.ACCENT, activeforeground="white",
                               relief="flat", font=("Segoe UI", 10))
            core_id = int(game["ra_game_id"])
            cur = game.get("ra_display_set_id")
            core_mark = "✓ " if not cur or int(cur) == core_id else ""
            set_menu.add_command(
                label=f"{core_mark}Core set",
                command=lambda: self.set_ra_display_set(game, None, "Core achievements"),
            )
            set_menu.add_separator()
            set_menu.add_command(
                label="Find subsets…",
                command=lambda: self._pick_subset_for_card(game),
            )
            menu.add_cascade(label=L("📑", "Card achievement set"), menu=set_menu)
            menu.add_command(label=L("🖼", "Use RA Game Icon as Cover"),
                             command=lambda: self.use_ra_icon(game, prefer="icon"))
            menu.add_command(label=L("🖼", "Use RA Box Art as Cover"),
                             command=lambda: self.use_ra_icon(game, prefer="box"))
            menu.add_command(label=L("🔗", "Change RA Link…"),
                             command=lambda: self.link_ra_game(game))
        else:
            menu.add_command(label=L("🔗", "Link RetroAchievements…"),
                             command=lambda: self.link_ra_game(game))
            menu.add_command(label=L("🏆", "View Achievements"),
                             command=lambda: self.show_achievements(game))

        menu.add_separator()

        # Favorites
        is_fav = "favorites" in game.get("collections", [])
        menu.add_command(
            label=L("★", "Remove from Favorites" if is_fav else "Add to Favorites"),
            command=lambda: self.toggle_favorite(game)
        )

        # Collections submenu (tree order with indentation)
        if self.collections:
            col_menu = tk.Menu(menu, tearoff=0, bg=Theme.SURFACE2, fg=Theme.TEXT,
                               activebackground=Theme.ACCENT, activeforeground="white",
                               relief="flat", font=("Segoe UI", 10))
            game_cols = game.get("collections", [])
            for col, depth in self._iter_collection_tree(None, 0):
                in_col = col["id"] in game_cols
                indent = "   " * depth  # 3 spaces per level
                mark = "✓" if in_col else "○"
                label = f"  {indent}{mark}  {col['name']}"
                if in_col:
                    col_menu.add_command(
                        label=label,
                        command=lambda c=col["id"]: self.remove_from_collection(game, c)
                    )
                else:
                    col_menu.add_command(
                        label=label,
                        command=lambda c=col["id"]: self.add_to_collection(game, c)
                    )
            menu.add_cascade(label=L("📁", "Collections"), menu=col_menu)

        menu.add_separator()
        menu.add_command(label=L("⚙", "Set Launch Options…"),
                         command=lambda: self.set_launch_options(game))
        menu.add_command(label=L("🎮", "Set System…"),
                         command=lambda: self.set_system(game))
        menu.add_command(label=L("📂", "Open file location"),
                         command=lambda: self.open_location(game))
        menu.add_command(label=L("🖼", "Customize cover…"),
                         command=lambda: self.customize_cover(game))
        menu.add_command(label=L("✏", "Rename"),
                         command=lambda: self.rename_game(game))
        menu.add_separator()
        menu.add_command(label=L("🗑", "Remove from library"),
                         command=lambda: self.remove_game(game))
        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()

    def open_location(self, game: dict):
        path = Path(game["path"])
        if path.parent.exists():
            if sys.platform == "win32":
                subprocess.run(["explorer", "/select,", str(path)])
            else:
                subprocess.run(["xdg-open", str(path.parent)])
        else:
            messagebox.showerror("Not found", "Folder no longer exists.")

    def customize_cover(self, game: dict):
        """Dialog to pick a cover image, choose fit mode, preview, or remove cover."""
        win = tk.Toplevel(self)
        win.title(f"Customize Cover — {game.get('name', 'Game')}")
        win.geometry("480x560")
        win.minsize(420, 500)
        win.configure(bg=Theme.SURFACE)
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)
        try:
            self.update_idletasks()
            px = self.winfo_rootx() + (self.winfo_width() - 480) // 2
            py = self.winfo_rooty() + (self.winfo_height() - 560) // 2
            win.geometry(f"+{max(0, px)}+{max(0, py)}")
        except Exception:
            pass

        state = {
            "path": game.get("cover") or "",
            "mode": (game.get("cover_mode") or "fill").lower(),
            "preview_img": None,
        }
        if state["mode"] not in ("fill", "fit", "stretch"):
            state["mode"] = "fill"

        # Button row first so it stays pinned to the bottom
        btn_row = tk.Frame(win, bg=Theme.SURFACE)
        btn_row.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(8, 18))

        body = tk.Frame(win, bg=Theme.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=(16, 8))

        tk.Label(body, text="Cover image", font=("Segoe UI", 13, "bold"),
                 bg=Theme.SURFACE, fg=Theme.TEXT).pack(anchor="w")
        hint = "Choose an image and how it should appear on the card."
        if not HAS_PIL:
            hint += "  (Install Pillow for Fill/Fit modes:  pip install Pillow)"
        tk.Label(body, text=hint,
                 font=("Segoe UI", 9), bg=Theme.SURFACE, fg=Theme.TEXT_MUTED).pack(
                     anchor="w", pady=(2, 12))

        # Preview area
        prev_w, prev_h = 200, 200  # same square as library cards
        preview_frame = tk.Frame(body, bg=Theme.SURFACE2, width=prev_w, height=prev_h,
                                 highlightthickness=1, highlightbackground=Theme.BORDER)
        preview_frame.pack(pady=(0, 12))
        preview_frame.pack_propagate(False)
        preview_lbl = tk.Label(preview_frame, text="No cover", font=("Segoe UI", 11),
                               bg=Theme.SURFACE2, fg=Theme.TEXT_MUTED)
        preview_lbl.place(relx=0.5, rely=0.5, anchor="center")

        def refresh_preview():
            path = state["path"]
            if path and Path(path).exists():
                img = prepare_cover_image(path, prev_w, prev_h, state["mode"])
                if img:
                    state["preview_img"] = img
                    preview_lbl.configure(image=img, text="")
                    return
            state["preview_img"] = None
            letter = (game.get("name") or "?")[0].upper()
            palette = ["#3b82f6", "#8b5cf6", "#ec4899", "#14b8a6", "#f59e0b", "#ef4444"]
            c1 = palette[hash(game["id"]) % len(palette)]
            preview_lbl.configure(image="", text=letter, font=("Segoe UI", 48, "bold"),
                                  bg=c1, fg="white")
            preview_frame.configure(bg=c1)
            preview_lbl.configure(bg=c1)

        # Browse / clear
        file_row = tk.Frame(body, bg=Theme.SURFACE)
        file_row.pack(fill=tk.X, pady=(0, 10))

        path_var = tk.StringVar(value=Path(state["path"]).name if state["path"] else "No image selected")
        path_lbl = tk.Label(file_row, textvariable=path_var, font=("Segoe UI", 9),
                            bg=Theme.SURFACE, fg=Theme.TEXT_MUTED, anchor="w")
        path_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def browse():
            cover_file = filedialog.askopenfilename(
                title="Select cover image",
                parent=win,
                filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"), ("All files", "*.*")]
            )
            if not cover_file:
                return
            state["path"] = cover_file  # temporary path until save
            path_var.set(Path(cover_file).name)
            preview_frame.configure(bg=Theme.SURFACE2)
            preview_lbl.configure(bg=Theme.SURFACE2)
            refresh_preview()

        def clear_cover():
            state["path"] = ""
            path_var.set("No image selected")
            preview_frame.configure(bg=Theme.SURFACE2)
            refresh_preview()

        tk.Button(file_row, text="Browse…", font=("Segoe UI", 9, "bold"),
                  bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
                  padx=10, pady=4, command=browse,
                  activebackground=Theme.ACCENT_HOV, activeforeground="white").pack(
                      side=tk.RIGHT, padx=(6, 0))
        tk.Button(file_row, text="Remove", font=("Segoe UI", 9),
                  bg=Theme.SURFACE2, fg=Theme.DANGER, relief="flat", cursor="hand2",
                  padx=10, pady=4, command=clear_cover,
                  activebackground=Theme.BORDER, activeforeground=Theme.DANGER).pack(
                      side=tk.RIGHT)

        # Fit mode
        tk.Label(body, text="Display mode", font=("Segoe UI", 10, "bold"),
                 bg=Theme.SURFACE, fg=Theme.TEXT).pack(anchor="w", pady=(4, 6))

        mode_var = tk.StringVar(value=state["mode"])
        modes = [
            ("fill", "Fill", "Scale and crop to cover the whole card (no bars)"),
            ("fit", "Fit", "Show the whole image; letterbox if needed"),
            ("stretch", "Stretch", "Force exact size (may distort)"),
        ]
        mode_frame = tk.Frame(body, bg=Theme.SURFACE)
        mode_frame.pack(fill=tk.X)

        def on_mode():
            state["mode"] = mode_var.get()
            if state["path"] and Path(state["path"]).exists():
                preview_frame.configure(bg=Theme.SURFACE2)
                preview_lbl.configure(bg=Theme.SURFACE2)
            refresh_preview()

        for val, label, desc in modes:
            row = tk.Frame(mode_frame, bg=Theme.SURFACE)
            row.pack(fill=tk.X, pady=2)
            rb = tk.Radiobutton(
                row, text=label, variable=mode_var, value=val,
                command=on_mode,
                bg=Theme.SURFACE, fg=Theme.TEXT, selectcolor=Theme.SURFACE2,
                activebackground=Theme.SURFACE, activeforeground=Theme.TEXT,
                font=("Segoe UI", 10), highlightthickness=0, cursor="hand2",
            )
            rb.pack(side=tk.LEFT)
            tk.Label(row, text=f"— {desc}", font=("Segoe UI", 8),
                     bg=Theme.SURFACE, fg=Theme.TEXT_MUTED).pack(side=tk.LEFT, padx=(4, 0))

        refresh_preview()

        def _is_under_covers(p: Path) -> bool:
            try:
                p = Path(p).resolve()
                root = COVERS_DIR.resolve()
                return root == p or root in p.parents
            except Exception:
                return False

        def _find_game() -> dict | None:
            gid = game.get("id")
            for g in self.games:
                if g.get("id") == gid:
                    return g
            return game

        def apply():
            # Always read latest mode from the radio buttons
            state["mode"] = mode_var.get() or "fill"
            target = _find_game()
            if target is None:
                messagebox.showerror("Cover", "Game not found in library.", parent=win)
                return

            old = target.get("cover")
            new_path = (state.get("path") or "").strip()
            try:
                if not new_path:
                    if old:
                        old_p = Path(old)
                        if old_p.exists() and _is_under_covers(old_p):
                            try:
                                old_p.unlink()
                            except Exception:
                                pass
                    target["cover"] = None
                else:
                    src = Path(new_path)
                    if not src.is_file():
                        messagebox.showerror(
                            "Cover",
                            f"Selected image not found:\n{src}",
                            parent=win,
                        )
                        return

                    # Always copy into covers/ with a fresh name so the UI
                    # cannot keep showing a stale cached image.
                    ext = src.suffix.lower()
                    if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"):
                        ext = ".png"
                    dest = COVERS_DIR / (
                        f"{target['id']}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{ext}"
                    )
                    shutil.copy2(str(src), str(dest))
                    target["cover"] = str(dest)

                    if old:
                        old_p = Path(old)
                        try:
                            if (
                                old_p.exists()
                                and old_p.resolve() != dest.resolve()
                                and _is_under_covers(old_p)
                            ):
                                old_p.unlink()
                        except Exception:
                            pass

                target["cover_mode"] = state["mode"]
                # Keep the dialog's game ref in sync too
                game["cover"] = target.get("cover")
                game["cover_mode"] = target["cover_mode"]

                self._save()
                win.destroy()
                self.refresh_library()
                mode_label = {"fill": "Fill", "fit": "Fit", "stretch": "Stretch"}.get(
                    target["cover_mode"], target["cover_mode"]
                )
                self.status_var.set(f"Cover updated ({mode_label})")
            except Exception as e:
                messagebox.showerror("Cover", f"Could not save cover:\n{e}", parent=win)

        def cancel():
            win.destroy()

        apply_btn = tk.Button(
            btn_row, text="  Apply  ", font=("Segoe UI", 10, "bold"),
            bg=Theme.ACCENT, fg="white", relief="flat", cursor="hand2",
            width=12, pady=8, command=apply,
            activebackground=Theme.ACCENT_HOV, activeforeground="white",
        )
        apply_btn.pack(side=tk.RIGHT)
        tk.Button(
            btn_row, text="  Cancel  ", font=("Segoe UI", 10),
            bg=Theme.SURFACE2, fg=Theme.TEXT, relief="flat", cursor="hand2",
            width=10, pady=8, command=cancel,
            activebackground=Theme.BORDER, activeforeground=Theme.TEXT,
        ).pack(side=tk.RIGHT, padx=(0, 8))

        win.bind("<Escape>", lambda e: cancel())
        win.bind("<Return>", lambda e: apply())

    def set_system(self, game: dict):
        """Manually set or clear the system/platform shown on the cover."""
        current = game.get("system") or ""
        value = themed_input(
            self,
            "Set System",
            f"System / platform for “{game.get('name', 'this game')}”\n"
            "Examples: PS1, SNES, GBA, PC\n"
            "Leave empty to clear. RA link can auto-fill this.",
            initial=current,
            width=460,
            height=240,
        )
        if value is None:
            return
        game["system"] = value.strip()
        self._save()
        self.refresh_library()
        if game["system"]:
            self.status_var.set(f'System set to “{game["system"]}”')
        else:
            self.status_var.set("System cleared")

    def rename_game(self, game: dict):
        new_name = themed_input(self, "Rename", "New name for this game:",
                                initial=game.get("name", ""))
        if new_name and new_name.strip():
            game["name"] = new_name.strip()
            self._save()
            self.apply_filter()
            self.status_var.set("Renamed")

    def remove_game(self, game: dict):
        if not themed_confirm(
            self,
            "Remove game",
            f'Remove “{game.get("name")}” from your library?\n\n'
            "Game files on disk are not deleted."
        ):
            return
        cover = game.get("cover")
        if cover and Path(cover).exists() and str(COVERS_DIR) in str(cover):
            try:
                Path(cover).unlink()
            except Exception:
                pass
        self.games = [g for g in self.games if g["id"] != game["id"]]
        self._save()
        self.refresh_sidebar()
        self.apply_filter()
        self.status_var.set(f'Removed “{game.get("name")}”')


# ---------------------------------------------------------------------------
# Single instance: second launch restores the tray app instead of opening another
# ---------------------------------------------------------------------------

SINGLE_INSTANCE_PORT = 47391
SINGLE_INSTANCE_MUTEX = "LocalGameLibrary_SingleInstance_Mutex"


def _signal_running_instance() -> bool:
    """Ask the already-running app to show its window. Returns True if contacted."""
    import socket
    try:
        with socket.create_connection(("127.0.0.1", SINGLE_INSTANCE_PORT), timeout=1.0) as sock:
            sock.sendall(b"SHOW\n")
        return True
    except Exception:
        return False


def _acquire_single_instance_mutex():
    """
    Windows named mutex so only one process owns the app.
    Returns (is_primary: bool, handle_or_None).
    """
    if sys.platform != "win32":
        return True, None
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.CreateMutexW(None, False, SINGLE_INSTANCE_MUTEX)
        ERROR_ALREADY_EXISTS = 183
        already = kernel32.GetLastError() == ERROR_ALREADY_EXISTS
        return (not already), handle
    except Exception:
        return True, None


def _start_instance_listener(app: "LocalGameLibrary"):
    """Background server: other launches connect and send SHOW."""
    import socket

    def run():
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", SINGLE_INSTANCE_PORT))
            srv.listen(5)
            srv.settimeout(1.0)
        except Exception:
            try:
                srv.close()
            except Exception:
                pass
            return

        app._instance_server = srv
        while not getattr(app, "_really_quit", False):
            try:
                conn, _addr = srv.accept()
            except socket.timeout:
                continue
            except Exception:
                break
            try:
                data = conn.recv(64)
                conn.close()
            except Exception:
                data = b""
            if data and b"SHOW" in data:
                try:
                    app.after(0, app._restore_from_tray)
                except Exception:
                    pass
        try:
            srv.close()
        except Exception:
            pass

    t = threading.Thread(target=run, daemon=True, name="SingleInstanceListener")
    t.start()
    app._instance_listener_thread = t


if __name__ == "__main__":
    is_primary, _mutex_handle = _acquire_single_instance_mutex()
    if not is_primary:
        # Another copy is already running (often in the tray)
        if _signal_running_instance():
            sys.exit(0)
        # Mutex held but listener not ready yet — brief retries
        for _ in range(8):
            time.sleep(0.15)
            if _signal_running_instance():
                sys.exit(0)
        # Could not contact primary; exit anyway to avoid duplicate apps
        sys.exit(0)

    # Also guard non-Windows (or mutex failure) via the listen port
    if _signal_running_instance():
        sys.exit(0)

    app = LocalGameLibrary()
    _start_instance_listener(app)
    app.mainloop()
