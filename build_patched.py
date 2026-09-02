#!/usr/bin/env python3
"""Build Patched-Files from Official-Files (maintainer only — needs Python 3).

1. Purge Official-Files -> .build/Purged Universal Configs
2. Optimize purged -> Patched-Files
3. Overwrite Patched-Files/AEngine.dll with Fixed-Assets/AEngine.dll
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OFFICIAL = ROOT / "Official-Files"
PATCHED = ROOT / "Patched-Files"
FIXED_DLL = ROOT / "Fixed-Assets" / "AEngine.dll"
SCRIPTS = ROOT / "scripts"

REQUIRED = (
    "DefaultKeyMapping.xml",
    "smk.conf",
    "smka.conf",
    "GameSidebar.xml",
    "translate.conf",
    "AEngine.dll",
)


def main() -> int:
    missing = [n for n in REQUIRED if not (OFFICIAL / n).is_file()]
    if missing:
        print("Missing in Official-Files/: " + ", ".join(missing))
        print("Paste fresh GameLoop UI files there, then re-run.")
        return 1

    if not FIXED_DLL.is_file():
        print(f"Missing patched DLL: {FIXED_DLL}")
        print("Copy your fixed AEngine.dll into Fixed-Assets/.")
        return 1

    for script in ("build_purge.py", "build_optimize.py"):
        path = SCRIPTS / script
        if not path.is_file():
            print(f"Missing script: {path}")
            return 1
        print(f"\n=== {script} ===")
        rc = subprocess.call([sys.executable, str(path)])
        if rc != 0:
            return rc

    shutil.copy2(FIXED_DLL, PATCHED / "AEngine.dll")
    print(f"\nDone. Patched payload: {PATCHED}")
    print(f"Fixed AEngine.dll -> {PATCHED / 'AEngine.dll'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
