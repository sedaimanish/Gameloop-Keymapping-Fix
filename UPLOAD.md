# Maintainer — upload new payload (you only)

Build working files in **Gameloop-Fix** repo:

```
Optimized and purged config/
  DefaultKeyMapping.xml
  smk.conf
  smka.conf
  GameSidebar.xml
  translate.conf
  AEngine.dll
```

## 1. Make payload.zip

Zip **those 6 files at the root** of the zip (not inside a subfolder):

```
payload.zip
  DefaultKeyMapping.xml
  smk.conf
  smka.conf
  GameSidebar.xml
  translate.conf
  AEngine.dll
```

On Windows: select all 6 files → right-click → Send to → Compressed folder → rename to `payload.zip`

## 2. Upload via GitHub web (no clone)

1. Open [Releases](https://github.com/sedaimanish/Gameloop-Keymapping-Fix/releases)
2. **Draft new release** or **Edit** the latest release
3. Attach these assets:
   - `payload.zip` ← your working files from Gameloop-Fix
   - `GameloopFix-Loader.cmd` ← from `release/` folder on `maintainer` branch (only when loader changed)
   - `Install-GameloopFix.ps1` ← from `release/` folder (only when script changed)
4. Publish release

Users download **only** `GameloopFix-Loader.cmd`. The loader fetches the PS1 + payload from the same release.

## Important

- **Do not** commit `payload.zip` or game files to the public `main` branch.
- `files/` folder on `maintainer` branch is for your local paste only — zip and upload to Releases.
- Build scripts stay in **Gameloop-Fix** repo, not here.
