<div align="center">

# GameLoop Keymapping Fix

**Optimized PUBG Mobile keymapping and performance tweaks for GameLoop — one click, no Python, no cloning.**

[![Latest release](https://img.shields.io/github/v/release/sedaimanish/Gameloop-Keymapping-Fix?label=latest&color=2ea44f)](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/sedaimanish/Gameloop-Keymapping-Fix/total?color=blue)](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)](#requirements)

<br>

[![Download GameloopFix-Loader.bat](https://img.shields.io/badge/Download-GameloopFix--Loader.bat-2ea44f?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest/download/GameloopFix-Loader.bat)

[Latest release](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest) &nbsp;·&nbsp; [All releases](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases)

Made by **MANISH SEDAI** · [sedaimanish.vercel.app](https://sedaimanish.vercel.app)

</div>

---

## Quick start

1. **[Download `GameloopFix-Loader.bat`](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest/download/GameloopFix-Loader.bat)** — that one file is all you need.
2. Save it anywhere, then **right-click → Run as administrator**.
3. Pick **Optimize keymapping** and follow the on-screen prompts (press Enter to accept the recommended defaults).
4. Relaunch **GameLoop** and **PUBG Mobile**.

> [!NOTE]
> The loader automatically downloads the installer and the patched files from the [latest release](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest) — you don't download anything else by hand. Your original files are backed up to a `Backup\` folder next to the loader before anything is changed.

---

## Requirements

- **Windows** with **GameLoop** installed
- **Administrator** rights (needed to edit the hosts file and files under `Program Files`)
- An **internet connection** (the loader fetches the installer and patched files)

---

## What it does

- Applies an **optimized keymapping** profile for PUBG Mobile on GameLoop
- Writes tuned **GameLoop registry settings** (resolution, FPS, engine, RAM, CPU cores, DPI, and more)
- Adds a **hosts block** to steady the emulator
- Removes a stale emulator cache file (`TVM_100.xml`) so new key settings apply cleanly
- Keeps a **backup** of every file it touches so you can roll back anytime

---

## Menu guide

When the installer opens, you'll see the main menu:

| Option | What it does |
| --- | --- |
| **1. Optimize keymapping** | Full fix — patched keymaps + hosts block + registry tweaks (recommended) |
| **2. GameLoop tweaks** | Registry performance settings only, no keymap changes |
| **3. Restore backup** | Puts your original files back from `Backup\` |
| **4. Exit** | Close without changes |

---

## Configuration wizard

Choosing **Optimize keymapping** (or **GameLoop tweaks**) walks you through a short wizard. Every step has a sensible **default** — just press **Enter** to accept it.

| Step | Choices | Default |
| --- | --- | --- |
| PUBG version | Global · Korean · Taiwan · Vietnam · BGMI · All | Global |
| Game definition | 720P · 1080P · 1440P | 1080P |
| Render engine | DirectX+ · OpenGL+ | DirectX+ |
| Target FPS | 40 · 60 · 90 · 120 | 90 |
| Graphic quality | Smooth · Balanced · HD | Balanced |
| Anti-aliasing (FXAA) | Disabled · Balanced · Ultra | Disabled |
| CPU cores | 1–10 | 8 |
| RAM allocation | 4 · 8 · 12 · 16 GB | 8 GB |
| Emulator DPI | 240 · 320 · 400 · 480 | 320 |
| iPad view (3:2 / 4:3) | Yes / No | No |
| Screen resolution | 1280×720 · 1600×900 · 1920×1080 · 2560×1440 | 1920×1080 |

> [!TIP]
> If you're not sure, keep the defaults — they suit most 16:9 setups.

---

## After install — layout tips

- **16:9 screens** → use PUBG **Layout 1** (default).
- **4:3 / iPad view** → use **Layout 3**, turn on **Show taps**, and drag the buttons onto the tap dots.
- If **Tab** or other keys feel wrong after editing layouts, run the installer again and let it delete the emulator cache (`TVM_100.xml`).

These tips are also saved to `USAGE-TIPS.txt` next to the loader after installation.

---

## Restore / undo

Made a change you didn't like? Run the loader again and choose **Restore backup**. It copies your original keymaps, config, and hosts file back from the `Backup\` folder.

---

## After a PUBG season update

If bag lock or mouse lock acts up after a season update, repair **HD resources in-game first** — texture detection affects bag lock. Then re-run **Optimize keymapping** if needed.

---

## Support

Questions, issues, and updates live on the **[Releases page](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases)**. Always grab the newest `GameloopFix-Loader.bat` there.
