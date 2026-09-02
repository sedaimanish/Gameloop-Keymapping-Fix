# Publish to GitHub

## Users (public)

Published releases live at:

https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases

They download **`GameloopFix-Installer.zip`** only. The loader fetches **`gameloop-fix-payload.zip`** from the same release.

## Maintainer (you)

1. `build_patched.bat`
2. `pack_release.bat`
3. `gh release create vX.Y.Z dist\GameloopFix-Installer.zip dist\gameloop-fix-payload.zip`
4. `gh release create vX.Y.Z-builder --draft dist\GameloopFix-Builder.zip`

See **[MAINTAINER.md](MAINTAINER.md)** for full details.

## Cloud Agent push access

GitHub → **Settings** → **Applications** → **Cursor** → **Repository access** → add **Gameloop-Keymapping-Fix**.

## Legacy sync from Gameloop-Fix

```bash
git fetch https://github.com/sedaimanish/Gameloop-Fix.git export/gameloop-keymapping-fix
git reset --hard FETCH_HEAD
```
