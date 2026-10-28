# Local Game Library

A modern, Steam-style **local game library** for Windows 11.  
Manage executables and shortcuts, organize collections, launch games with custom options, and track [RetroAchievements](https://retroachievements.org) progress — all from one dark, polished desktop app.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%2011-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

### Library
- Add games from **`.exe`** or Windows **`.lnk` shortcuts** (target path and launch arguments are read automatically)
- Custom **covers** (Fill / Fit / Stretch) with live preview
- **Launch options** (command-line arguments)
- Play as administrator
- Playtime tracking and last played
- Single-instance app — opening the EXE again restores the running window (including from the tray)

### Collections
- Steam-like **collections** and **sub-collections**
- Expand / collapse parents
- Reorder with move up/down, context menu, or drag
- Favorites
- Sidebar filtering

### RetroAchievements
- Login with **username + Web API key** (not password — that is how the official RA API works)
- Link games by **name search**
- Achievement panel with badges and unlock status
- **Core + subset sets** as tabs (e.g. Bonus, class subsets)
- Horizontally scrollable subset tabs (◀ ▶, mouse wheel, or drag)
- Choose which set feeds the **progress badge on the game card**
- Use RA game icon or box art as cover

### Desktop integration
- System tray (minimize to tray on close)
- **Start with Windows** in tray mode
- Custom `app.ico` for window, taskbar, and tray

---

## Requirements

- **Windows 10/11** (primary target)
- **Python 3.10+**

### Optional (recommended)

```bash
pip install pillow pystray
```

| Package   | Purpose                          |
|-----------|----------------------------------|
| `pillow`  | Cover scaling, icons, badges     |
| `pystray` | System tray                      |

---

## Run from source

1. Clone or download this repo.
2. Put `LocalGameLibrary.py` and `app.ico` in the same folder.
3. Install optional dependencies (recommended):

   ```bash
   pip install pillow pystray
   ```

4. Start the app:

   ```bash
   python LocalGameLibrary.py
   ```

---

## Build a standalone `.exe`

1. Place these in one folder:
   - `LocalGameLibrary.py`
   - `app.ico`
   - `build.bat`
2. Double-click **`build.bat`** (or run it in a terminal).
3. Find the build at:

   ```text
   dist\Local Game Library.exe
   ```

`build.bat` installs/updates PyInstaller, Pillow, and pystray, then builds a windowed one-file EXE.

Manual build:

```bash
pyinstaller --noconfirm --onefile --windowed --name "Local Game Library" --icon app.ico --add-data "app.ico;." LocalGameLibrary.py
```

---

## RetroAchievements setup

1. Create an account at [retroachievements.org](https://retroachievements.org).
2. Open **Settings → Keys** and copy your **Web API Key**.
3. In the app, click **RA Login** and enter:
   - Username
   - Web API Key  

> The public Web API does **not** accept your account password. Username + API key is the official method for third-party apps.

4. On a game card → **⋯ → Link RetroAchievements…** and search by name.
5. **⋯ → View Achievements** for the full list (Core + subsets).
6. **⋯ → Card achievement set** to choose which set appears on the card badge.

---

## Data location

User data is stored under:

```text
%APPDATA%\LocalGameLibrary\
```

| Path / file        | Contents                                      |
|--------------------|-----------------------------------------------|
| `library.json`     | Games, collections, RA credentials, settings  |
| `covers\`          | Local cover images                            |
| `app.ico`          | Cached default icon if needed                 |

RA badge/icon downloads are loaded when needed and **not** kept as permanent disk caches.

---

## Usage tips

| Action | How |
|--------|-----|
| Add a game | **＋ Add Game** → pick `.exe` or `.lnk` |
| Context menu | **⋯** on a card |
| Collections | Sidebar **＋**, or right-click a collection |
| Reorder collections | Right-click → Move up/down, or use hover arrows |
| Collapse folder | Click **▶ / ▼** on a parent collection |
| Tray | Close the window (does not quit); right-click tray icon → Exit |
| Start with Windows | **⚙ Settings** → enable **Start with Windows** |

---

## Project files

```text
LocalGameLibrary.py   # Main application
app.ico               # Application icon
build.bat             # One-click Windows EXE build
README.md             # This file
```

---

## Privacy & network

- Library data stays on your PC.
- Network is used only for:
  - RetroAchievements API (login, search, progress, images)
  - Opening achievement pages in your browser when you click them

---

## License

MIT — free to use, modify, and share.

---

## Credits

- [RetroAchievements](https://retroachievements.org) for the achievement platform and API  
- UI inspired by Steam’s library layout  
```
