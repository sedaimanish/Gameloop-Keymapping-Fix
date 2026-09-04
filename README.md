# GameLoop Keymapping Fix

Optimized PUBG Mobile keymapping and performance tweaks for GameLoop — one click, no Python, no cloning.

**Download:** [`Tencent-Medicine.bat`](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest/download/Tencent-Medicine.bat) (from the [latest release](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest))

Made by MANISH SEDAI · [sedaimanish.vercel.app](https://sedaimanish.vercel.app)

---

## Quick start

1. Download **`Tencent-Medicine.bat`** (link above).
2. Right-click it → **Run as administrator**.
3. Choose **Optimize keymapping** and follow the prompts — press **Enter** to accept the recommended defaults.
4. Relaunch **GameLoop** and **PUBG Mobile**.

> [!NOTE]
> `Tencent-Medicine.bat` fetches the installer and patched files automatically, and backs up your original files to a `Backup\` folder before changing anything.

## Requirements

- **Windows** with **GameLoop** installed
- **Administrator** rights (to edit the hosts file and files under `Program Files`)
- An **internet connection**

## What it does

- Applies an optimized **keymapping** profile for PUBG Mobile
- Writes tuned **GameLoop settings** (resolution, FPS, engine, RAM, CPU cores, DPI, and more)
- Adds a **hosts block** to steady the emulator
- Removes a stale cache file (`TVM_100.xml`) so new key settings apply cleanly
- Keeps a **backup** of everything it touches

## Menu

| Option | What it does |
| --- | --- |
| Optimize keymapping | Full fix — keymaps + hosts block + settings (recommended) |
| GameLoop tweaks | Performance settings only, no keymap changes |
| Restore backup | Puts your original files back from `Backup\` |
| Exit | Close without changes |

## Configuration wizard

Choosing **Optimize keymapping** walks you through a short wizard. Every step has a default — press **Enter** to accept it.

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

Not sure? Keep the defaults — they suit most 16:9 setups.

## Tips

- **16:9 screens** → PUBG **Layout 1** (default).
- **4:3 / iPad view** → **Layout 3**, turn on **Show taps**, and drag buttons onto the tap dots.
- If keys feel wrong after editing layouts, run it again and let it delete the cache (`TVM_100.xml`).
- After a PUBG season update, repair **HD resources in-game first** (texture detection affects bag lock), then re-run if needed.

## Restore

Run `Tencent-Medicine.bat` again and choose **Restore backup** to put your original files back.

## Support

Questions, issues, and updates: the [Releases page](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases).
