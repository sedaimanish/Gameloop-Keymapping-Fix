# Publish this repository to GitHub

The Cloud Agent token cannot create new repositories on your account. Create the repo once, then push:

## Option A — GitHub website

1. Go to https://github.com/new
2. Repository name: **Gameloop-Keymapping-Fix**
3. Public, **no** README / .gitignore (already in this folder)
4. Create repository
5. In this folder run:

```bash
git remote add origin https://github.com/sedaimanish/Gameloop-Keymapping-Fix.git
git push -u origin main
```

## Option B — GitHub CLI (on your PC)

```bash
cd Gameloop-Keymapping-Fix
gh repo create sedaimanish/Gameloop-Keymapping-Fix --public --source=. --remote=origin --push
```

After push, clients can run `client/Install-GameloopFix.bat` — it downloads from:

`https://raw.githubusercontent.com/sedaimanish/Gameloop-Keymapping-Fix/main/Patched-Files/`
