# Publish to GitHub

Full package is also on **Gameloop-Fix** branch `export/gameloop-keymapping-fix` if you need it.

## One-time sync (your PC — uses your GitHub login)

Cloud Agent cannot push to this repo until **Cursor** or your **PAT** has write access here.

```bash
git clone https://github.com/sedaimanish/Gameloop-Keymapping-Fix.git
cd Gameloop-Keymapping-Fix
git fetch https://github.com/sedaimanish/Gameloop-Fix.git export/gameloop-keymapping-fix
git reset --hard FETCH_HEAD
git push origin main --force
```

Or with GitHub CLI (already logged in as you):

```bash
gh repo clone sedaimanish/Gameloop-Keymapping-Fix
cd Gameloop-Keymapping-Fix
git fetch https://github.com/sedaimanish/Gameloop-Fix.git export/gameloop-keymapping-fix
git reset --hard FETCH_HEAD
git push origin main --force
```

## Grant Cloud Agent push access (optional)

GitHub → **Settings** → **Applications** → **Cursor** → **Repository access** → add **Gameloop-Keymapping-Fix**.

Then a future agent run can `git push` directly.

## After push

Clients download from:

`https://raw.githubusercontent.com/sedaimanish/Gameloop-Keymapping-Fix/main/Patched-Files/`

Run `client/Install-GameloopFix.bat` as Administrator.
