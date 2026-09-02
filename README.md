# GameLoop Keymapping Fix

**Users:** download the installer from [Releases](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest) — not from browsing repo source files.

| Who | What to download | Where |
|-----|------------------|-------|
| **Users** | `GameloopFix-Installer.zip` | [Releases](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest) (public) |
| **Maintainer (you)** | `GameloopFix-Builder.zip` | Draft release on same repo (collaborators only) |

Patched game files are **not** stored in the repo tree. The client loader fetches them from the latest GitHub Release at install time.

---

## User install

1. Download **`GameloopFix-Installer.zip`** from [Releases](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases/latest).
2. Extract anywhere.
3. Right-click **`Install-GameloopFix.bat`** → **Run as administrator**.
4. Choose **Full install**.
5. Relaunch GameLoop and PUBG.

No Python required.

---

## Maintainer — after a GameLoop update

See **[MAINTAINER.md](MAINTAINER.md)** for the full workflow.

Quick version:

1. Paste fresh UI files into `Official-Files/`.
2. Put your patched DLL in `Fixed-Assets/AEngine.dll`.
3. Run `build_patched.bat`.
4. Run `pack_release.bat` (or `python scripts/pack_release.py`).
5. Publish:
   ```bat
   gh release create v1.0.1 dist\GameloopFix-Installer.zip dist\gameloop-fix-payload.zip
   gh release create v1.0.1-builder --draft dist\GameloopFix-Builder.zip
   ```

Or push a tag `v1.0.1` and let GitHub Actions build + publish automatically.

---

## Repository layout (maintainer)

```
Official-Files/     # INPUT — paste fresh GameLoop UI files
Patched-Files/      # OUTPUT — local only (not committed); goes into release zip
Fixed-Assets/       # YOUR fixed AEngine.dll
build_patched.bat   # Build patched payload
pack_release.bat    # Pack installer + payload + builder zips
client/             # User loader (also inside GameloopFix-Installer.zip)
scripts/            # Internal build steps
```

---

## If bag/mouse lock acts up after a PUBG season update

Repair or redownload **HD resources in-game** first. Then rebuild from new Official files if GameLoop shipped new `smk`/`DefaultKeyMapping`.
