# Maintainer guide

## Access model

| Asset | Visibility | Contents |
|-------|------------|----------|
| `GameloopFix-Installer.zip` | **Public** release | `client/` loader only |
| `gameloop-fix-payload.zip` | Public release asset | Patched UI files + DLL (loader downloads this) |
| `GameloopFix-Builder.zip` | **Draft** release only | Full repo toolkit (you + collaborators only) |

Regular users browsing GitHub see the repo source and the public Releases page. Patched files are **not** committed to git (`Patched-Files/` is gitignored). The installer script contains the release API URL — determined users can still extract payload URLs from the script; this setup stops casual repo browsing from exposing files.

---

## After a GameLoop update

1. Close GameLoop.
2. Copy from `C:\Program Files\TxGameAssistant\UI\` into **`Official-Files/`**:
   - `DefaultKeyMapping.xml`, `smk.conf`, `smka.conf`, `GameSidebar.xml`, `translate.conf`, `AEngine.dll` (stock reference)
3. Ensure **`Fixed-Assets/AEngine.dll`** is your patched DLL.
4. Run:
   ```bat
   build_patched.bat
   ```
5. Pack zips:
   ```bat
   pack_release.bat
   ```
   Output in `dist/`:
   - `GameloopFix-Installer.zip`
   - `gameloop-fix-payload.zip`
   - `GameloopFix-Builder.zip`

---

## Publish a release

### Option A — GitHub CLI (local)

```bat
gh release create v1.0.0 dist\GameloopFix-Installer.zip dist\gameloop-fix-payload.zip
gh release create v1.0.0-builder --draft --title "Builder v1.0.0" dist\GameloopFix-Builder.zip
```

Users get updates when they run the installer (it pulls **latest** release). Pin a version in `client/Install-GameloopFix.ps1` by setting `$GithubReleaseTag = 'v1.0.0'` before packing if needed.

### Option B — Git tag (GitHub Actions)

```bat
git tag v1.0.0
git push origin v1.0.0
```

The **Release** workflow builds, packs, and creates the public release. For a draft builder zip, also run **Actions → Release → Run workflow** with version `v1.0.0` and “publish builder draft” enabled.

---

## Get the full builder on a new PC

1. GitHub → **Releases** → open the latest **Draft** release (`v*-builder`).
2. Download **`GameloopFix-Builder.zip`**.
3. Extract and work from there.

Only repo collaborators see draft releases.

---

## Build fix (Windows)

If `build_purge.py` failed with `FileNotFoundError` on `.build\Purged Universal Configs`, update to the latest repo — `mkdir` now creates parent folders automatically.
