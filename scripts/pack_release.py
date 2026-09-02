#!/usr/bin/env python3
"""Pack release zips for GitHub Releases.

Outputs (under dist/):
  GameloopFix-Installer.zip   — public: client loader only
  gameloop-fix-payload.zip    — public: patched files (loader downloads this)
  GameloopFix-Builder.zip     — draft only: full maintainer toolkit
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
CLIENT = ROOT / "client"
PATCHED = ROOT / "Patched-Files"
PAYLOAD_FILES = (
    "DefaultKeyMapping.xml",
    "smk.conf",
    "smka.conf",
    "GameSidebar.xml",
    "translate.conf",
    "AEngine.dll",
)

BUILDER_SKIP_DIRS = {".git", "dist", ".build", "__pycache__", "client/Backup"}
BUILDER_SKIP_FILES = {".DS_Store"}


def zip_dir(zf: zipfile.ZipFile, folder: Path, arc_prefix: str = "") -> None:
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(folder).as_posix()
        arc = f"{arc_prefix}{rel}" if arc_prefix else rel
        zf.write(path, arc)


def pack_client(dest: Path) -> None:
    if not CLIENT.is_dir():
        raise SystemExit(f"Missing folder: {CLIENT}")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        zip_dir(zf, CLIENT)


def pack_payload(dest: Path) -> None:
    missing = [n for n in PAYLOAD_FILES if not (PATCHED / n).is_file()]
    if missing:
        raise SystemExit(
            "Missing Patched-Files/: "
            + ", ".join(missing)
            + "\nRun build_patched.bat first."
        )
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in PAYLOAD_FILES:
            zf.write(PATCHED / name, name)


def should_skip_builder(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if parts and parts[0] in BUILDER_SKIP_DIRS:
        return True
    if any(part in BUILDER_SKIP_DIRS for part in parts):
        return True
    if path.name in BUILDER_SKIP_FILES:
        return True
    if path.suffix == ".pyc":
        return True
    return False


def pack_builder(dest: Path) -> None:
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or should_skip_builder(path):
                continue
            zf.write(path, path.relative_to(ROOT).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack GitHub release zips.")
    parser.add_argument(
        "--target",
        choices=("all", "client", "payload", "builder"),
        default="all",
        help="Which zip(s) to create (default: all)",
    )
    args = parser.parse_args()

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    targets = {
        "client": DIST / "GameloopFix-Installer.zip",
        "payload": DIST / "gameloop-fix-payload.zip",
        "builder": DIST / "GameloopFix-Builder.zip",
    }

    if args.target in ("all", "client"):
        pack_client(targets["client"])
        print(f"Wrote {targets['client']}")
    if args.target in ("all", "payload"):
        pack_payload(targets["payload"])
        print(f"Wrote {targets['payload']}")
    if args.target in ("all", "builder"):
        pack_builder(targets["builder"])
        print(f"Wrote {targets['builder']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
