#!/usr/bin/env python3
"""Build Purged Universal Configs — PUBG Mobile + system entries only."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Official-Files"
OUTPUT = ROOT / ".build" / "Purged Universal Configs"

FILES_FROM_SOURCE = [
    "AEngine.dll",
    "DefaultKeyMapping.xml",
    "GameSidebar.xml",
    "smk.conf",
    "smka.conf",
    "translate.conf",
]

PUBG_PACKAGE_PATTERNS = [
    r"^com\.tencent\.ig(_ss)?$",
    r"^com\.pubg\.krmobile(_ss)?$",
    r"^com\.vng\.pubgmobile(_ss)?$",
    r"^com\.rekoo\.pubgm(_ss)?$",
    r"^com\.tencent\.tmgp\.pubgm",
]

SYSTEM_PACKAGE_PATTERNS = [
    r"^com\.android\.",
    r"^com\.tencent\.loginapp$",
    r"^com\.tencent\.mobileqq$",
    r"^com\.tencent\.mm$",
]

TRANSLATE_PUBG_PATTERNS = [
    r"^com\.tencent\.ig=",
    r"^com\.pubg\.krmobile=",
    r"^com\.vng\.pubgmobile=",
    r"^com\.tencent\.tmgp\.pubgm",
    r"^com\.tencent\.gamehelper\.pg=",
    r"^com\.tencent\.shootgame",
]

TRANSLATE_SYSTEM_PATTERNS = [
    r"^com\.tencent\.mm",
    r"^com\.xx\.xx=",
]

SMK_PUBG_PACKAGES = {
    "com.tencent.ig",
    "com.tencent.tmgp.pubgmhd",
    "com.pubg.krmobile",
    "com.rekoo.pubgm",
    "com.vng.pubgmobile",
}

SIDEBAR_PUBG_PACKAGES = {
    "com.tencent.ig",
    "com.tencent.tmgp.pubgmhd",
    "com.vng.pubgmobile",
    "com.pubg.krmobile",
    "com.rekoo.pubgm",
}


def matches_any(package: str, patterns: list[str]) -> bool:
    return any(re.match(p, package) for p in patterns)


def should_keep_package(package: str) -> bool:
    return matches_any(package, PUBG_PACKAGE_PATTERNS) or matches_any(
        package, SYSTEM_PACKAGE_PATTERNS
    )


def purge_default_keymapping(text: str) -> tuple[str, dict[str, int]]:
    pattern = re.compile(
        r"<(Item|ItemEx) ApkName=\"([^\"]+)\"[^>]*>.*?</\1>", re.S
    )
    kept: list[str] = []
    stats = {"kept": 0, "removed": 0, "pubg": 0, "system": 0}

    for match in pattern.finditer(text):
        pkg = match.group(2)
        if should_keep_package(pkg):
            kept.append(match.group(0))
            stats["kept"] += 1
            if matches_any(pkg, PUBG_PACKAGE_PATTERNS):
                stats["pubg"] += 1
            else:
                stats["system"] += 1
        else:
            stats["removed"] += 1

    return "\n".join(kept) + ("\n" if kept else ""), stats


def extract_smk_items(text: str) -> list[tuple[str, str]]:
    """Return (package, full_block) for each top-level smk item."""
    items: list[tuple[str, str]] = []
    pos = 0
    open_re = re.compile(r'<item pkgname="([^"]+)"\s*>', re.I)
    while True:
        open_match = open_re.search(text, pos)
        if not open_match:
            break
        pkg = open_match.group(1)
        start = open_match.start()
        close_idx = text.find("</item>", open_match.end())
        if close_idx == -1:
            raise RuntimeError(f"Unclosed smk item for {pkg}")
        end = close_idx + len("</item>")
        items.append((pkg, text[start:end]))
        pos = end
    return items


def purge_smk(text: str) -> tuple[str, dict[str, int]]:
    kept_blocks: list[str] = []
    stats = {"kept": 0, "removed": 0}

    for pkg, block in extract_smk_items(text):
        if pkg in SMK_PUBG_PACKAGES:
            kept_blocks.append(block)
            stats["kept"] += 1
        else:
            stats["removed"] += 1

    return "<root>" + "".join(kept_blocks) + "</root>\n", stats


def purge_sidebar(text: str) -> tuple[str, dict[str, int]]:
    games = list(
        re.finditer(r"<game name=\"([^\"]+)\"[^>]*>.*?</game>", text, re.S)
    )
    language_match = re.search(r"(<Language>.*?</Language>)", text, re.S)
    if not language_match:
        raise RuntimeError("GameSidebar.xml: <Language> block not found")

    kept_games: list[str] = []
    stats = {"kept": 0, "removed": 0}
    for match in games:
        pkg = match.group(1)
        if pkg in SIDEBAR_PUBG_PACKAGES:
            kept_games.append(match.group(0))
            stats["kept"] += 1
        else:
            stats["removed"] += 1

    body = "<GameSidebar>\n\t" + "\n\t".join(kept_games) + "\n</GameSidebar>\n"
    return body + language_match.group(1) + "\n", stats


def purge_translate(text: str) -> tuple[str, dict[str, int]]:
    kept: list[str] = []
    stats = {"kept": 0, "removed": 0}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if matches_any(stripped, TRANSLATE_PUBG_PATTERNS) or matches_any(
            stripped, TRANSLATE_SYSTEM_PATTERNS
        ):
            kept.append(stripped)
            stats["kept"] += 1
        else:
            stats["removed"] += 1
    return "\n".join(kept) + "\n", stats


def purge_smka(_: str) -> str:
    return "<root></root>\n"


def validate_pubg_preserved(source_keymap: str, purged_keymap: str) -> list[str]:
    issues: list[str] = []
    item_pattern = re.compile(
        r"<(Item|ItemEx) ApkName=\"([^\"]+)\"[^>]*>.*?</\1>", re.S
    )

    def count_entries(text: str, pkg: str) -> int:
        return sum(
            1
            for m in item_pattern.finditer(text)
            if m.group(2) == pkg and matches_any(pkg, PUBG_PACKAGE_PATTERNS)
        )

    pubg_packages = sorted(
        {
            m.group(2)
            for m in item_pattern.finditer(source_keymap)
            if matches_any(m.group(2), PUBG_PACKAGE_PATTERNS)
        }
    )

    for pkg in pubg_packages:
        src_n = count_entries(source_keymap, pkg)
        dst_n = count_entries(purged_keymap, pkg)
        if src_n != dst_n:
            issues.append(f"{pkg}: expected {src_n} keymap blocks, got {dst_n}")

    return issues


def build() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()

    shutil.copy2(SOURCE / "AEngine.dll", OUTPUT / "AEngine.dll")

    source_keymap = (SOURCE / "DefaultKeyMapping.xml").read_text(
        encoding="utf-8", errors="replace"
    )
    purged_keymap, km_stats = purge_default_keymapping(source_keymap)
    issues = validate_pubg_preserved(source_keymap, purged_keymap)
    if issues:
        raise RuntimeError("PUBG keymap preservation failed:\n  - " + "\n  - ".join(issues))
    (OUTPUT / "DefaultKeyMapping.xml").write_text(purged_keymap, encoding="utf-8")

    source_sidebar = (SOURCE / "GameSidebar.xml").read_text(
        encoding="utf-8", errors="replace"
    )
    purged_sidebar, sb_stats = purge_sidebar(source_sidebar)
    (OUTPUT / "GameSidebar.xml").write_text(purged_sidebar, encoding="utf-8")

    source_smk = (SOURCE / "smk.conf").read_text(encoding="utf-8", errors="replace")
    purged_smk, smk_stats = purge_smk(source_smk)
    (OUTPUT / "smk.conf").write_text(purged_smk, encoding="utf-8")

    source_translate = (SOURCE / "translate.conf").read_text(
        encoding="utf-8", errors="replace"
    )
    purged_translate, tr_stats = purge_translate(source_translate)
    (OUTPUT / "translate.conf").write_text(purged_translate, encoding="utf-8")

    (OUTPUT / "smka.conf").write_text(purge_smka(""), encoding="utf-8")

    print(f"Built: {OUTPUT}")
    print(
        "DefaultKeyMapping: kept {kept} ({pubg} pubg + {system} system), "
        "removed {removed}".format(**km_stats)
    )
    print(
        "GameSidebar: kept {kept} pubg games, removed {removed}".format(**sb_stats)
    )
    print("smk.conf: kept {kept} sections, removed {removed}".format(**smk_stats))
    print(
        "translate.conf: kept {kept} lines, removed {removed}".format(**tr_stats)
    )
    print("smka.conf: cleared (was Free Fire only)")
    print("PUBG preservation check: OK")


if __name__ == "__main__":
    build()
