# GameLoop Keymapping Fix

Separate package: **maintainer build** (Python) + **client install** (PowerShell only, no Python).

```
Gameloop-Keymapping-Fix/
├── Official-Files/       # INPUT — paste fresh GameLoop UI files after an update
├── Patched-Files/        # OUTPUT — committed to GitHub; client downloads these
├── Fixed-Assets/
│   └── AEngine.dll       # YOUR fixed DLL (never overwritten by build)
├── build_patched.py      # Maintainer: purge + optimize (needs Python 3)
├── build_patched.bat
├── scripts/              # Internal build steps
└── client/               # Give this folder to end users
    ├── Install-GameloopFix.bat
    ├── Install-GameloopFix.ps1
    └── hosts_entries.txt
```

---

## Maintainer — after a new GameLoop update

1. Close GameLoop.
2. Copy from `C:\Program Files\TxGameAssistant\UI\` into **`Official-Files/`**:
   - `DefaultKeyMapping.xml`
   - `smk.conf`
   - `smka.conf`
   - `GameSidebar.xml`
   - `translate.conf`
   - `AEngine.dll` (stock — reference only; not used in patched output)
3. Ensure **`Fixed-Assets/AEngine.dll`** is your patched DLL.
4. Run:
   ```bat
   build_patched.bat
   ```
   or `python3 build_patched.py`
5. Check **`Patched-Files/`**, test locally, commit + push to GitHub.

**Do not** hand-edit `Patched-Files/` — always rebuild from `Official-Files/`.

---

## Client — end user install

1. Download the **`client/`** folder (or full repo).
2. Right-click **`Install-GameloopFix.bat`** → **Run as administrator**.
3. Choose **Full install**:
   - GameLoop tweaks (FPS, resolution, CPU/RAM, engine, etc.)
   - Downloads pre-patched files from GitHub
   - Backs up originals → `client/Backup/`
   - Replaces UI folder files
   - **Deletes** `%APPDATA%\AndroidTbox\TVM_100.xml`
   - Updates **hosts** file (telemetry block)
4. Relaunch GameLoop and PUBG.

No Python required on the client machine.

---

## What the build applies

Same optimizations as the main repo (`build_optimized_purged.py`):

- PUBG-only purge, WheelSlip removed, instant swipes, plain V, F2, side button 2
- Tips off, WASD speed 100, Tab LockEnemy stripped, Global ItemEx sync
- `EnableSwitchViewLockMethod="0"`, RClick Shop1 fix, mouse-lock tag normalization
- Fixed `AEngine.dll` from `Fixed-Assets/`

---

## Repository

Standalone repo: **https://github.com/sedaimanish/Gameloop-Keymapping-Fix**

Client downloads from:

```
https://raw.githubusercontent.com/sedaimanish/Gameloop-Keymapping-Fix/main/Patched-Files/
```

Edit `$GithubOwner`, `$GithubRepo`, `$GithubBranch` at the top of `client/Install-GameloopFix.ps1` if you fork.

---

## If bag/mouse lock acts up after a PUBG season update

Repair or redownload **HD resources in-game** first — texture detection affects bag lock. Then rebuild from new Official files if GameLoop shipped new `smk`/`DefaultKeyMapping`.
