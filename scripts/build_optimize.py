#!/usr/bin/env python3
"""Build Optimized and purged config from Purged Universal Configs.

Surgical optimizations agreed with user (not a blind script port):
- Remove WheelSlip (pickup scroll) from Smart modes; fix gun-wheel Pickup disable
- F2 single-tap at former F3 position; remove F2/F3 chat macros
- Replace FoldClick2 grenade/heal with PS1 fixed instant swipe wheel coords
- Inject plain-tap V key (user-tested in GameLoop; coords per Smart mode)
- Normalize AutoActive mouse tags + PS1 Pickup disable-flag fix (bag mouse lock)
- Strip zombie LockEnemy Tab ops; sync Global ItemEx Smart 1080P/2K from Item block
- WASD CrossKey speed 100, tips off; Global defaults to Smart 2K when resolution is 2K
- smk.conf residue cleanup (no Global->Korean texture clone)
- Generate TVM Templates/ for Smart 720P / 1080P / 2K
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / ".build" / "Purged Universal Configs"
OUTPUT = ROOT / "Patched-Files"

DEFAULT_LAST_MODE_ID = "3"  # Smart 1080P default; Global ig uses 4 when game is 2K
GLOBAL_2K_LAST_MODE_ID = "4"  # GameLoop auto-picks Smart 2K for Global at 2K resolution
GLOBAL_2K_PACKAGES = frozenset({"com.tencent.ig", "com.tencent.ig_ss"})

FILES_TO_COPY = [
    "AEngine.dll",
    "GameSidebar.xml",
    "smk.conf",
    "smka.conf",
    "translate.conf",
]

PUBG_PACKAGE_RE = re.compile(
    r"^com\.(?:tencent\.ig|pubg\.|vng\.|rekoo\.|tencent\.tmgp\.pubgm)"
)

CJK_LETTER_KEY = "字母键"
CJK_SLIDE_KEY = "字母键划线"

SIDE_BUTTON = (
    '\t<KeyMapping ItemName="Mouse side button 2" Point_X="0.907345" Point_Y="0.661647" '
    f'Description="{CJK_LETTER_KEY}" MiniVisiable="true" MiniDisable="false" '
    'AutoCancel="0" AsciiCode="6"/>'
)

# Fixed 1080P radial wheel from fix_gameloop_script.ps1 (normalized 0-1 coords).
SWIPE_BLOCK = """
\t<KeyMapping ItemName="4" Point_X="0.637801" Point_Y="0.888855" Description="{slide}" MiniVisiable="true" MiniDisable="false" AutoCancel="0" AsciiCode="52" KeyMouseSlideType="1" KeyMouseSlidePoints="(0.637801,0.963855,0)(0.637801,0.953141,120)(0.637801,0.942426,20)(0.637801,0.931712,20)(0.637801,0.920998,20)(0.637801,0.910284,20)(0.637801,0.899569,20)(0.637801,0.888855,0)"/>
\t<KeyMapping ItemName="5" Point_X="0.690834" Point_Y="0.910822" Description="{slide}" MiniVisiable="true" MiniDisable="false" AutoCancel="0" AsciiCode="53" KeyMouseSlideType="1" KeyMouseSlidePoints="(0.637801,0.963855,0)(0.645377,0.956279,120)(0.652953,0.948703,20)(0.660529,0.941127,20)(0.668106,0.933550,20)(0.675682,0.925974,20)(0.683258,0.918398,20)(0.690834,0.910822,0)"/>
\t<KeyMapping ItemName="6" Point_X="0.584768" Point_Y="0.910822" Description="{slide}" MiniVisiable="true" MiniDisable="false" AutoCancel="0" AsciiCode="54" KeyMouseSlideType="1" KeyMouseSlidePoints="(0.637801,0.963855,0)(0.630225,0.956279,120)(0.622649,0.948703,20)(0.615073,0.941127,20)(0.607496,0.933550,20)(0.599920,0.925974,20)(0.592344,0.918398,20)(0.584768,0.910822,0)"/>
\t<KeyMapping ItemName="7" Point_X="0.436000" Point_Y="0.963855" Description="{slide}" MiniVisiable="true" MiniDisable="false" AutoCancel="0" AsciiCode="55" KeyMouseSlideType="1" KeyMouseSlidePoints="(0.361000,0.963855,0)(0.371714,0.963855,120)(0.382429,0.963855,20)(0.393143,0.963855,20)(0.403857,0.963855,20)(0.414571,0.963855,20)(0.425286,0.963855,20)(0.436000,0.963855,0)"/>
\t<KeyMapping ItemName="8" Point_X="0.361000" Point_Y="0.888855" Description="{slide}" MiniVisiable="true" MiniDisable="false" AutoCancel="0" AsciiCode="56" KeyMouseSlideType="1" KeyMouseSlidePoints="(0.361000,0.963855,0)(0.361000,0.953141,120)(0.361000,0.942426,20)(0.361000,0.931712,20)(0.361000,0.920998,20)(0.361000,0.910284,20)(0.361000,0.899569,20)(0.361000,0.888855,0)"/>
\t<KeyMapping ItemName="0" Point_X="0.307967" Point_Y="0.910822" Description="{slide}" MiniVisiable="true" MiniDisable="false" AutoCancel="0" AsciiCode="48" KeyMouseSlideType="1" KeyMouseSlidePoints="(0.361000,0.963855,0)(0.353424,0.956279,120)(0.345848,0.948703,20)(0.338272,0.941127,20)(0.330695,0.933550,20)(0.323119,0.925974,20)(0.315543,0.918398,20)(0.307967,0.910822,0)"/>
\t<KeyMapping ItemName="X" Point_X="0.286000" Point_Y="0.963855" Description="{slide}" MiniVisiable="true" MiniDisable="false" AutoCancel="0" AsciiCode="88" KeyMouseSlideType="1" KeyMouseSlidePoints="(0.361000,0.963855,0)(0.350286,0.963855,120)(0.339571,0.963855,20)(0.328857,0.963855,20)(0.318143,0.963855,20)(0.307429,0.963855,20)(0.296714,0.963855,20)(0.286000,0.963855,0)"/>
""".strip().format(slide=CJK_SLIDE_KEY)

# Key 9 = painkiller (separate from bandage on X); uses PS1 heal-wheel diagonal slot.
PAINKILLER_9_SWIPE = (
    '\t<KeyMapping ItemName="9" Point_X="0.414033" Point_Y="0.910822" '
    f'Description="{CJK_SLIDE_KEY}" MiniVisiable="true" MiniDisable="false" AutoCancel="0" '
    'AsciiCode="57" KeyMouseSlideType="1" '
    'KeyMouseSlidePoints="(0.361000,0.963855,0)(0.368576,0.956279,120)(0.376152,0.948703,20)'
    '(0.383728,0.941127,20)(0.391305,0.933550,20)(0.398881,0.925974,20)(0.406457,0.918398,20)'
    '(0.414033,0.910822,0)"/>'
)

SWIPE_ASCII_CODES = ("52", "53", "54", "55", "56", "48", "88", "57")

# Plain V tap from user-tested Korean TVM (works; Sw1to3 SwitchOperation did not on KR).
V_KEY_COORDS = {
    "4": ("0.240678", "0.945674"),  # Smart 2K
    "default": ("0.253107", "0.936747"),  # Smart 720P / 1080P
}

PICKUP_DISABLE_REPLACEMENTS = (
    (
        "InSetUp|Pickup|AdjustMultiples|AdjustMultiplesPressed",
        "InSetUp|AdjustMultiples|AdjustMultiplesPressed",
    ),
    ('InSetUp|Pickup"', 'InSetUp|AdjustMultiples|AdjustMultiplesPressed"'),
    ("InSetUp|Pickup ", "InSetUp|AdjustMultiples|AdjustMultiplesPressed "),
    (
        "InSetUp|PickupDown|PacketLeft|ReturnSetUp\"",
        "InSetUp|AdjustMultiples|AdjustMultiplesPressed\"",
    ),
    (
        "InSetUp|PickupDown|PacketLeft|ReturnSetUp ",
        "InSetUp|AdjustMultiples|AdjustMultiplesPressed ",
    ),
)

SMK_RESIDUE_COMMS = [
    "手雷", "手雷下", "手雷低抛", "手雷高抛", "手雷、药品的框",
    "烟雾弹", "燃烧瓶", "燃烧弹", "震爆弹", "绷带", "急救包", "急救箱",
    "止痛药", "肾上腺素", "能量饮料", "苹果", "吃药上面的三角形",
    "吃药上箭头", "吃药的边框", "取消吃药", "取消手雷", "平底锅",
    "大砍刀", "小刀", "地雷", "快速说话", "捡东西鼠标滚轮",
]

SMART_MODE_RE = re.compile(
    r"(?s)(<KeyMapMode (?![^>]*ModeID=\"1\")(?![^>]*Name=\"Normal)[^>]*>)"
    r"(.*?)"
    r"(\r?\n[\t ]*</KeyMapMode>)"
)

ITEM_BLOCK_RE = re.compile(
    r"<(Item|ItemEx)\s+ApkName=\"([^\"]+)\"([^>]*)>(.*?)</\1>",
    re.S,
)

F2_MULTI_RE = re.compile(
    r'(?s)[\t ]*<KeyMappingEx[^>]*ItemName="F2"[^>]*Type="MultiPoint"[^>]*>.*?</KeyMappingEx>\r?\n?',
)
F3_MULTI_RE = re.compile(
    r'(?s)[\t ]*<KeyMappingEx[^>]*ItemName="F3"[^>]*Type="MultiPoint"[^>]*>.*?</KeyMappingEx>\r?\n?',
)
WHEEL_SLIP_RE = re.compile(
    r'(?s)[\t ]*<KeyMappingEx[^>]*Type="WheelSlip"[^>]*>.*?</KeyMappingEx>\r?\n?',
)
GUN_WHEEL_RE = re.compile(
    r'(?s)(<KeyMappingEx[^>]*ItemName="滚轮切枪"[^>]*>.*?</KeyMappingEx>)',
)
OLD_SLIDE_RE = re.compile(
    r'(?s)[\t ]*<KeyMapping[^>]*KeyMouseSlideType="1"[^>]*/>\r?\n?',
)
EMOJI_KEY_RE = re.compile(
    r'(?s)[\t ]*<KeyMapping[^>]*Description="[^"]*表情[^"]*"[^>]*>.*?</KeyMapping>\r?\n?',
)
HEAL_TAP_RE = re.compile(
    r'(?s)[\t ]*<KeyMapping[^>]*ItemName="9"[^>]*Description="吃药"[^>]*>.*?</KeyMapping>\r?\n?',
)
SIDE_BTN_PAIRED_RE = re.compile(
    r'(?s)[\t ]*<KeyMapping (?![^>]*/>)[^>]*ItemName="Mouse side button 2"[^>]*>.*?</KeyMapping>\r?\n?'
)
SIDE_BTN_SELF_RE = re.compile(
    r'[\t ]*<KeyMapping (?=[^>]*/>)[^>]*ItemName="Mouse side button 2"[^>]*/>\r?\n?'
)
V_KEY_RE = re.compile(
    r'(?s)[\t ]*<KeyMapping (?![^>]*/>)[^>]*AsciiCode="86"[^>]*>.*?</KeyMapping>\r?\n?'
)
V_KEY_SELF_RE = re.compile(
    r'[\t ]*<KeyMapping (?=[^>]*/>)[^>]*AsciiCode="86"[^>]*/>\r?\n?'
)
BANDAGE_FOLD_RE = re.compile(
    r'(?s)[\t ]*<KeyMappingEx[^>]*AsciiCode="57"[^>]*Description="[^"]*绷带[^"]*"[^>]*>.*?</KeyMappingEx>\r?\n?'
)
SWIPE_FOLD_RE = re.compile(
    r'(?s)[\t ]*<KeyMappingEx[^>]*AsciiCode="(?:52|53|54|55|56|48|88)"[^>]*>.*?</KeyMappingEx>\r?\n?'
)
SWIPE_KEY_PAIRED_RE = re.compile(
    r'(?s)[\t ]*<KeyMapping (?![^>]*/>)[^>]*AsciiCode="(?:52|53|54|55|56|48|88)"[^>]*>.*?</KeyMapping>\r?\n?'
)
SWIPE_KEY_SELF_RE = re.compile(
    r'[\t ]*<KeyMapping (?=[^>]*/>)[^>]*AsciiCode="(?:52|53|54|55|56|48|88)"[^>]*/>\r?\n?'
)
KEY9_SWIPE_RE = re.compile(
    r'(?s)[\t ]*<KeyMapping[^>]*AsciiCode="57"[^>]*KeyMouseSlideType="1"[^>]*/>\r?\n?'
)
KEY9_FOLD_RE = re.compile(
    r'(?s)[\t ]*<KeyMappingEx[^>]*AsciiCode="57"[^>]*>.*?</KeyMappingEx>\r?\n?'
)
KEY9_KEY_RE = re.compile(
    r'(?s)[\t ]*<KeyMapping (?![^>]*/>)[^>]*AsciiCode="57"[^>]*>.*?</KeyMapping>\r?\n?'
)
KEY9_KEY_SELF_RE = re.compile(
    r'[\t ]*<KeyMapping (?=[^>]*/>)[^>]*AsciiCode="57"[^>]*/>\r?\n?'
)
TAB_KEY_RE = re.compile(
    r'(?s)(<KeyMapping[^>]*ItemName="Tab"[^>]*>)(.*?)(</KeyMapping>)'
)
TAB_LOCK_ENEMY_OP_RE = re.compile(
    r'(?s)[\t ]*<SwitchOperation[^>]*EnableSwitch="(?:LockEnemy2?|CancelLockEnemy2?)"[^>]*/>\r?\n?'
)
SMART_MODE_ID_RE = re.compile(r'ModeID="([234])"')
RClick_VIEW_OP_RE = re.compile(
    r'(<SwitchOperation Description="视角" EnableSwitch="SetUp" DisableSwitch="[^"]*)"',
)
SHOP1_SWITCH = '<Switch Name="Shop1" TextureId="108"/>\r\n'


def purge_swipe_bindings(mode_body: str) -> str:
    mode_body = SWIPE_FOLD_RE.sub("", mode_body)
    mode_body = BANDAGE_FOLD_RE.sub("", mode_body)
    mode_body = SWIPE_KEY_PAIRED_RE.sub("", mode_body)
    mode_body = SWIPE_KEY_SELF_RE.sub("", mode_body)
    mode_body = KEY9_SWIPE_RE.sub("", mode_body)
    mode_body = KEY9_FOLD_RE.sub("", mode_body)
    mode_body = KEY9_KEY_RE.sub("", mode_body)
    mode_body = KEY9_KEY_SELF_RE.sub("", mode_body)
    mode_body = OLD_SLIDE_RE.sub("", mode_body)
    return mode_body


def purge_v_key(mode_body: str) -> tuple[str, int]:
    before = len(V_KEY_RE.findall(mode_body)) + len(V_KEY_SELF_RE.findall(mode_body))
    mode_body = V_KEY_RE.sub("", mode_body)
    mode_body = V_KEY_SELF_RE.sub("", mode_body)
    return mode_body, before


def v_key_plain(mode_id: str) -> str:
    px, py = V_KEY_COORDS.get(mode_id, V_KEY_COORDS["default"])
    return (
        f'\t<KeyMapping ItemName="V" Point_X="{px}" Point_Y="{py}" '
        f'Description="{CJK_LETTER_KEY}" MiniVisiable="true" MiniDisable="false" '
        f'AutoCancel="0" AsciiCode="86"/>'
    )


def fix_pickup_disable_flags(text: str) -> tuple[str, int]:
    fixed = 0
    for old, new in PICKUP_DISABLE_REPLACEMENTS:
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            fixed += count
    return text, fixed


def normalize_autolock_mouse_tags(text: str) -> tuple[str, int]:
    """Match working TVM: named mouse buttons + drop LOCK_AsciiCode2 on LClick."""
    fixed = 0

    def patch_lclick(m: re.Match[str]) -> str:
        nonlocal fixed
        tag = m.group(0)
        if 'ItemName="Left Mouse Button"' in tag and 'LOCK_AsciiCode2=' not in tag:
            return tag
        fixed += 1
        tag = re.sub(r'ItemName="[^"]*"', 'ItemName="Left Mouse Button"', tag, count=1)
        tag = tag.replace(' LOCK_AsciiCode2="17"', "")
        if "MiniVisiable=" not in tag:
            tag = tag.replace('Type="LClick"', 'MiniVisiable="false" MiniDisable="false" Type="LClick"', 1)
        return tag

    def patch_rclick(m: re.Match[str]) -> str:
        nonlocal fixed
        tag = m.group(0)
        if 'ItemName="Move with Mouse"' in tag and 'LOCK_AsciiCode2=' not in tag:
            return tag
        fixed += 1
        tag = re.sub(r'ItemName="[^"]*"', 'ItemName="Move with Mouse"', tag, count=1)
        tag = tag.replace(' LOCK_AsciiCode2="17"', "")
        if "MiniVisiable=" not in tag:
            tag = tag.replace('Type="RClick"', 'MiniVisiable="false" MiniDisable="false" Type="RClick"', 1)
        return tag

    text = re.sub(
        r'(?s)<KeyMappingEx[^>]*Type="LClick"[^>]*AutoActive="1"[^>]*>.*?</KeyMappingEx>',
        patch_lclick,
        text,
    )
    text = re.sub(
        r'(?s)<KeyMappingEx[^>]*Type="RClick"[^>]*AutoActive="1"[^>]*>.*?</KeyMappingEx>',
        patch_rclick,
        text,
    )
    return text, fixed


def strip_tab_lockenemy_ops(text: str) -> tuple[str, int]:
    """Remove zombie LockEnemy Tab ops — working TVM/KR use bag-only Tab switches."""
    removed = 0

    def fix_tab(m: re.Match[str]) -> str:
        nonlocal removed
        head, body, tail = m.group(1), m.group(2), m.group(3)
        body, n = TAB_LOCK_ENEMY_OP_RE.subn("", body)
        removed += n
        return head + body + tail

    text = TAB_KEY_RE.sub(fix_tab, text)
    return text, removed


def ensure_lastmode_view_lock_method(text: str) -> tuple[str, int]:
    """Working TVM always sets EnableSwitchViewLockMethod=\"0\" on PUBG LastMode."""
    fixed = 0

    def patch_lastmode(m: re.Match[str]) -> str:
        nonlocal fixed
        tag = m.group(0)
        if "EnableSwitchViewLockMethod=" in tag:
            if 'EnableSwitchViewLockMethod="0"' not in tag:
                tag = re.sub(
                    r'EnableSwitchViewLockMethod="[^"]*"',
                    'EnableSwitchViewLockMethod="0"',
                    tag,
                )
                fixed += 1
            return tag
        fixed += 1
        return tag.replace("/>", ' EnableSwitchViewLockMethod="0"/>', 1)

    def patch_item(m: re.Match[str]) -> str:
        tag, pkg, attrs, body = m.group(1), m.group(2), m.group(3), m.group(4)
        if not PUBG_PACKAGE_RE.match(pkg):
            return m.group(0)
        body = re.sub(r"<LastMode[^>]*/>", patch_lastmode, body)
        return f'<{tag} ApkName="{pkg}"{attrs}>{body}</{tag}>'

    text = ITEM_BLOCK_RE.sub(patch_item, text)
    return text, fixed


def fix_global_rclick_view_disable(text: str) -> tuple[str, int]:
    """Match working Global/KR TVM: RClick view uses Shop1, not zombie-mode Rapidly."""
    fixed = 0

    def patch_block(m: re.Match[str]) -> str:
        nonlocal fixed
        tag, pkg, attrs, body = m.group(1), m.group(2), m.group(3), m.group(4)
        if pkg not in GLOBAL_2K_PACKAGES:
            return m.group(0)

        def patch_mode(mm: re.Match[str]) -> str:
            nonlocal fixed
            open_tag, mode_body, close_tag = mm.group(1), mm.group(2), mm.group(3)
            if not SMART_MODE_ID_RE.search(open_tag):
                return mm.group(0)
            new_body, n = RClick_VIEW_OP_RE.subn(
                lambda sm: sm.group(1).replace("Rapidly", "Shop1").replace("|Hook", "")
                + '"',
                mode_body,
            )
            fixed += n
            return open_tag + new_body + close_tag

        body = re.sub(
            r"(<KeyMapMode[^>]*>)(.*?)(</KeyMapMode>)",
            patch_mode,
            body,
            flags=re.S,
        )
        if 'Name="Shop1"' not in body:
            rapidly = re.search(r'<Switch Name="Rapidly"[^/]*/>', body)
            if rapidly:
                insert_at = rapidly.end()
                body = body[:insert_at] + "\r\n" + SHOP1_SWITCH.strip() + body[insert_at:]
                fixed += 1
        return f'<{tag} ApkName="{pkg}"{attrs}>{body}</{tag}>'

    text = ITEM_BLOCK_RE.sub(patch_block, text)
    return text, fixed


def normalize_global_mouse_lock_tags(text: str) -> tuple[str, int]:
    """TVM-format flags on Tab/Esc + RClick sensitivity for Global smart modes."""
    fixed = 0

    def patch_block(m: re.Match[str]) -> str:
        nonlocal fixed
        tag, pkg, attrs, body = m.group(1), m.group(2), m.group(3), m.group(4)
        if pkg not in GLOBAL_2K_PACKAGES:
            return m.group(0)

        def patch_mode(mm: re.Match[str]) -> str:
            nonlocal fixed
            open_tag, mode_body, close_tag = mm.group(1), mm.group(2), mm.group(3)
            if not SMART_MODE_ID_RE.search(open_tag):
                return mm.group(0)

            def add_mini(tab_m: re.Match[str]) -> str:
                nonlocal fixed
                head = tab_m.group(1)
                if "MiniVisiable=" in head:
                    return tab_m.group(0)
                fixed += 1
                return head + ' MiniVisiable="false" MiniDisable="false"' + tab_m.group(2)

            mode_body = re.sub(
                r'(<KeyMapping[^>]*ItemName="(?:Tab|Esc)"[^>]*)(/?>)',
                add_mini,
                mode_body,
            )

            def add_sensi(rc_m: re.Match[str]) -> str:
                nonlocal fixed
                block = rc_m.group(0)
                if "Sensi_X=" in block:
                    return block
                fixed += 1
                return block.replace(
                    'Type="RClick"',
                    'Type="RClick" Sensi_X="1.000000" Sensi_Y="1.000000"',
                    1,
                )

            mode_body = re.sub(
                r'(?s)<KeyMappingEx[^>]*Type="RClick"[^>]*AutoActive="1"[^>]*>.*?</KeyMappingEx>',
                add_sensi,
                mode_body,
            )
            return open_tag + mode_body + close_tag

        body = re.sub(
            r"(<KeyMapMode[^>]*>)(.*?)(</KeyMapMode>)",
            patch_mode,
            body,
            flags=re.S,
        )
        return f'<{tag} ApkName="{pkg}"{attrs}>{body}</{tag}>'

    text = ITEM_BLOCK_RE.sub(patch_block, text)
    return text, fixed


def sync_itemex_smart_modes_from_item(text: str) -> tuple[str, int]:
    """GameLoop uses ItemEx at modern VersionCode; copy Item Smart 1080P/2K layout."""
    synced = 0
    for pkg in GLOBAL_2K_PACKAGES:
        item_m = re.search(
            rf'<Item\s+ApkName="{re.escape(pkg)}"[^>]*>(.*?)</Item>',
            text,
            re.S,
        )
        if not item_m:
            continue
        item_body = item_m.group(1)

        def repl_ex(m: re.Match[str]) -> str:
            nonlocal synced
            tag, attrs, ex_body = m.group(1), m.group(2), m.group(3)
            new_body = ex_body
            for mode_id in ("3", "4"):
                src = re.search(
                    rf'(<KeyMapMode[^>]*ModeID="{mode_id}"[^>]*>)(.*?)(</KeyMapMode>)',
                    item_body,
                    re.S,
                )
                if not src:
                    continue
                replacement = src.group(1) + src.group(2) + src.group(3)
                new_body, n = re.subn(
                    rf'<KeyMapMode[^>]*ModeID="{mode_id}"[^>]*>.*?</KeyMapMode>',
                    replacement,
                    new_body,
                    count=1,
                    flags=re.S,
                )
                synced += n
            return f'<{tag} ApkName="{pkg}"{attrs}>{new_body}</{tag}>'

        text = re.sub(
            rf'<(ItemEx)\s+ApkName="{re.escape(pkg)}"([^>]*)>(.*?)</ItemEx>',
            repl_ex,
            text,
            count=1,
            flags=re.S,
        )
    return text, synced


def inject_script_bindings(mode_body: str, mode_id: str) -> tuple[str, int, int]:
    mode_body = purge_swipe_bindings(mode_body)
    mode_body, v_removed = purge_v_key(mode_body)
    mode_body = SIDE_BTN_PAIRED_RE.sub("", mode_body)
    mode_body = SIDE_BTN_SELF_RE.sub("", mode_body)
    additions = [v_key_plain(mode_id), SIDE_BUTTON, SWIPE_BLOCK, PAINKILLER_9_SWIPE]
    mode_body = mode_body.rstrip() + "\r\n" + "\r\n".join(additions) + "\r\n"
    return mode_body, len(SWIPE_ASCII_CODES), v_removed


def remove_conflicting_smart_keys(mode_body: str) -> str:
    mode_body = EMOJI_KEY_RE.sub("", mode_body)
    mode_body = HEAL_TAP_RE.sub("", mode_body)
    return mode_body


def f3_coords(mode_body: str) -> tuple[str, str] | None:
    m = re.search(
        r'<KeyMappingEx[^>]*ItemName="F3"[^>]*Point_X="([^"]+)"[^>]*Point_Y="([^"]+)"',
        mode_body,
    )
    if not m:
        return None
    return m.group(1), m.group(2)


def optimize_smart_mode(mode_body: str, mode_id: str) -> tuple[str, dict[str, int]]:
    stats = {
        "wheel_slip": 0,
        "gun_wheel": 0,
        "f2f3": 0,
        "swipes": 0,
        "v_key": 0,
    }

    before = len(WHEEL_SLIP_RE.findall(mode_body))
    mode_body = WHEEL_SLIP_RE.sub("", mode_body)
    stats["wheel_slip"] = before

    def fix_gun(m: re.Match[str]) -> str:
        stats["gun_wheel"] += 1
        block = m.group(1)

        def fix_disable(dm: re.Match[str]) -> str:
            tokens = [t for t in dm.group(1).split("|") if t and t != "Pickup"]
            return f'DisableSwitch="{"|".join(tokens)}"'

        return re.sub(r'DisableSwitch="([^"]*)"', fix_disable, block)

    mode_body = GUN_WHEEL_RE.sub(fix_gun, mode_body)
    mode_body = remove_conflicting_smart_keys(mode_body)

    coords = f3_coords(mode_body)
    stats["f2f3"] += len(F2_MULTI_RE.findall(mode_body)) + len(F3_MULTI_RE.findall(mode_body))
    mode_body = F2_MULTI_RE.sub("", mode_body)
    mode_body = F3_MULTI_RE.sub("", mode_body)
    if coords:
        px, py = coords
        f2 = (
            f'\t<KeyMapping ItemName="F2" Point_X="{px}" Point_Y="{py}" '
            f'Description="{CJK_LETTER_KEY}" MiniVisiable="true" MiniDisable="false" '
            f'AutoCancel="0" AsciiCode="113"/>'
        )
        mode_body = mode_body.rstrip() + "\r\n" + f2 + "\r\n"

    mode_body, swipe_n, v_removed = inject_script_bindings(mode_body, mode_id)
    stats["swipes"] = swipe_n
    stats["v_key"] = 1

    return mode_body, stats


def apply_mode_tweaks(mode_open: str, mode_body: str, mode_close: str) -> str:
    mode_open = mode_open.replace('ShowTipsAlways="1"', 'ShowTipsAlways="0"')
    mode_open = mode_open.replace('CurrModeEnableTips="1"', 'CurrModeEnableTips="0"')
    mode_open = mode_open.replace('EnableTips="1"', 'EnableTips="0"')

    def fix_speed(m: re.Match[str]) -> str:
        tag = m.group(0)
        if 'speed="0"' in tag:
            return tag.replace('speed="0"', 'speed="100"')
        if "speed=" not in tag:
            return tag.replace("Type=\"CrossKey\"", 'Type="CrossKey" speed="100"', 1)
        return tag

    mode_body = re.sub(
        r'<KeyMappingEx (?=[^>]*Type="CrossKey")[^>]*>',
        fix_speed,
        mode_body,
    )
    return mode_open + mode_body + mode_close


def optimize_keymapping(text: str) -> tuple[str, dict]:
    totals = {
        "smart_modes": 0,
        "wheel_slip": 0,
        "gun_wheel": 0,
        "f2f3": 0,
        "swipes": 0,
        "v_key": 0,
        "pickup_flags": 0,
        "mouse_tags": 0,
        "tab_lockenemy": 0,
        "itemex_sync": 0,
        "view_lock_method": 0,
        "rclick_shop1": 0,
        "mouse_lock_tags": 0,
    }

    def mode_replacer(m: re.Match[str]) -> str:
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        mode_id_m = re.search(r'ModeID="(\d+)"', open_tag)
        mode_id = mode_id_m.group(1) if mode_id_m else DEFAULT_LAST_MODE_ID
        new_body, stats = optimize_smart_mode(body, mode_id)
        totals["smart_modes"] += 1
        for k in ("wheel_slip", "gun_wheel", "f2f3", "swipes", "v_key"):
            totals[k] += stats[k]
        return apply_mode_tweaks(open_tag, new_body, close_tag)

    text = SMART_MODE_RE.sub(mode_replacer, text)
    text, totals["pickup_flags"] = fix_pickup_disable_flags(text)
    text, totals["mouse_tags"] = normalize_autolock_mouse_tags(text)
    text, totals["tab_lockenemy"] = strip_tab_lockenemy_ops(text)
    text, totals["itemex_sync"] = sync_itemex_smart_modes_from_item(text)
    text, totals["view_lock_method"] = ensure_lastmode_view_lock_method(text)
    text, totals["rclick_shop1"] = fix_global_rclick_view_disable(text)
    text, totals["mouse_lock_tags"] = normalize_global_mouse_lock_tags(text)

    text = text.replace('ShowTipsAlways="1"', 'ShowTipsAlways="0"')
    text = text.replace('CurrModeEnableTips="1"', 'CurrModeEnableTips="0"')

    def lastmode_repl(m: re.Match[str]) -> str:
        tag, pkg, attrs, body = m.group(1), m.group(2), m.group(3), m.group(4)
        if not PUBG_PACKAGE_RE.match(pkg):
            return m.group(0)
        mode_id = (
            GLOBAL_2K_LAST_MODE_ID
            if pkg in GLOBAL_2K_PACKAGES
            else DEFAULT_LAST_MODE_ID
        )
        body = re.sub(
            r'(<LastMode[^>]*?)ModeID="[0-9]+"',
            r'\g<1>ModeID="' + mode_id + '"',
            body,
            count=1,
        )
        body = re.sub(
            r'(<LastMode[^>]*?)EnableGameKeyDT="0"',
            r'\1EnableGameKeyDT="1"',
            body,
        )
        body = body.replace('EnableTips="1"', 'EnableTips="0"')
        body = re.sub(
            r'(<Switch Name="SetUp"[^>]*ModeID=")2(")',
            r"\g<1>" + mode_id + r"\g<2>",
            body,
        )
        return f'<{tag} ApkName="{pkg}"{attrs}>{body}</{tag}>'

    text = ITEM_BLOCK_RE.sub(lastmode_repl, text)
    return text, totals


def clean_smk_residue(text: str) -> tuple[str, int]:
    removed = 0
    for comm in SMK_RESIDUE_COMMS:
        esc = re.escape(comm)
        for tag in ("Tex", "reg"):
            pat = rf'[\t ]*<{tag} [^>]*comm="{esc}[^"]*"[^>]*/>\r?\n?'
            n = len(re.findall(pat, text))
            text = re.sub(pat, "", text)
            removed += n
    return text, removed


def strip_for_tvm(body: str) -> str:
    body = re.sub(r"<Resolution[^>]*>.*?</Resolution[^>]*>\s*", "", body, flags=re.S)
    modes = re.findall(r"<KeyMapMode[^>]*>.*?</KeyMapMode>", body, flags=re.S)
    keep: list[str] = []
    for mode in modes:
        if re.search(r'ModeID="[1-4]"', mode.split(">", 1)[0]):
            keep.append(mode.strip())
    return "\r\n".join(keep)


def strip_switch_comm(switch_line: str) -> str:
    return re.sub(r'\s+comm="[^"]*"', "", switch_line)


def item_to_tvm_entry(
    tag: str, pkg: str, attrs: str, body: str, mode_id: str, version_code: str | None
) -> str:
    note_m = re.search(r'备注="([^"]*)"', attrs)
    note = note_m.group(1) if note_m else ""

    vc_attr = ""
    if version_code:
        vc_attr = f' VersionCode="{version_code}"'
    elif (vc := re.search(r'VersionCode="(\d+)"', attrs)):
        vc_attr = f' VersionCode="{vc.group(1)}"'

    lastmode_m = re.search(r"<LastMode[^>]*/>", body)
    version_m = re.search(r"<VersionInfo[^>]*/>", body)
    if not lastmode_m or not version_m:
        return ""

    lastmode = lastmode_m.group(0)
    lastmode = re.sub(r'ModeID="[0-9]+"', f'ModeID="{mode_id}"', lastmode)
    lastmode = lastmode.replace('EnableTips="1"', 'EnableTips="0"')
    if 'EnableGameKeyDT="0"' in lastmode:
        lastmode = lastmode.replace('EnableGameKeyDT="0"', 'EnableGameKeyDT="1"')
    if "EnableSwitchViewLockMethod=" not in lastmode:
        lastmode = lastmode.replace(
            "/>", ' EnableSwitchViewLockMethod="0"/>', 1
        )
    elif 'EnableSwitchViewLockMethod="0"' not in lastmode:
        lastmode = re.sub(
            r'EnableSwitchViewLockMethod="[^"]*"',
            'EnableSwitchViewLockMethod="0"',
            lastmode,
        )

    version = version_m.group(0)
    if "CurFeatureVer=" not in version:
        version = version.replace("/>", ' CurFeatureVer="8"/>')

    switches = re.findall(r"<Switch [^>]+/>", body)
    switch_lines = [strip_switch_comm(s) for s in switches]

    modes = strip_for_tvm(body)

    lines = [
        f'<Item ApkName="{pkg}" 备注="{note}"{vc_attr}>',
        "<StartInfo StartTimes=\"2\"/>",
        lastmode,
        version,
        *switch_lines,
        modes,
        "</Item>",
    ]
    return "\r\n".join(lines)


def launcher_tvm_entry() -> str:
    return (
        '<Item ApkName="com.android.launcherex" 备注="">\r\n'
        "<StartInfo StartTimes=\"2\"/>\r\n"
        '<LastMode ModeID="0" EnableTips="0" EnableGameKeyDT="0" '
        'TipsTransparent="0.500000" Lightness="1.000000" EnableSwitchViewLockMethod="0"/>\r\n'
        "</Item>"
    )


def settings_tvm_entry() -> str:
    return (
        '<Item ApkName="com.android.settings" 备注="设置">\r\n'
        "<StartInfo StartTimes=\"2\"/>\r\n"
        '<LastMode ModeID="1" EnableTips="0" EnableGameKeyDT="0" '
        'TipsTransparent="0.500000" Lightness="1.000000" EnableSwitchViewLockMethod="0"/>\r\n'
        '<VersionInfo Version="1"/>\r\n'
        '<KeyMapMode ModeID="1" Name="普通模式"/>\r\n'
        "</Item>"
    )


def build_global_ready_tvm(optimized_keymap: str) -> None:
    """Single-file Global TVM (like user-saved KR TVM) — copy to %APPDATA%\\AndroidTbox\\."""
    if GLOBAL_TVM_READY.exists():
        shutil.rmtree(GLOBAL_TVM_READY)
    GLOBAL_TVM_READY.mkdir(parents=True)

    entries = [launcher_tvm_entry(), settings_tvm_entry()]
    global_packages = ("com.tencent.ig", "com.tencent.ig_ss")

    for m in ITEM_BLOCK_RE.finditer(optimized_keymap):
        tag, pkg, attrs, body = m.group(1), m.group(2), m.group(3), m.group(4)
        if pkg not in global_packages:
            continue
        vc = re.search(r'VersionCode="(\d+)"', attrs)
        vc_str = vc.group(1) if vc else None
        entry = item_to_tvm_entry(tag, pkg, attrs, body, GLOBAL_2K_LAST_MODE_ID, vc_str)
        if entry:
            entries.append(entry)

    (GLOBAL_TVM_READY / "TVM_100.xml").write_text(
        "\r\n".join(entries) + "\r\n", encoding="utf-8"
    )


def build_tvm_templates(optimized_keymap: str) -> None:
    if TVM_ROOT.exists():
        shutil.rmtree(TVM_ROOT)

    mode_folders = {
        "2": TVM_ROOT / "Smart-720P",
        "3": TVM_ROOT / "Smart-1080P",
        "4": TVM_ROOT / "Smart-2K",
    }
    for folder in mode_folders.values():
        folder.mkdir(parents=True)

    entries_by_mode: dict[str, list[str]] = {
        k: [launcher_tvm_entry(), settings_tvm_entry()] for k in mode_folders
    }

    for m in ITEM_BLOCK_RE.finditer(optimized_keymap):
        tag, pkg, attrs, body = m.group(1), m.group(2), m.group(3), m.group(4)
        if not PUBG_PACKAGE_RE.match(pkg):
            continue
        vc = re.search(r'VersionCode="(\d+)"', attrs)
        vc_str = vc.group(1) if vc else None
        for mode_id in mode_folders:
            entry = item_to_tvm_entry(tag, pkg, attrs, body, mode_id, vc_str)
            if entry:
                entries_by_mode[mode_id].append(entry)

    for mode_id, folder in mode_folders.items():
        content = "\r\n".join(entries_by_mode[mode_id]) + "\r\n"
        (folder / "TVM_100.xml").write_text(content, encoding="utf-8")


def build() -> None:
    if not SOURCE.is_dir():
        raise SystemExit(f"Missing source folder: {SOURCE}")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()

    keymap = (SOURCE / "DefaultKeyMapping.xml").read_text(
        encoding="utf-8", errors="replace"
    )
    optimized, stats = optimize_keymapping(keymap)
    (OUTPUT / "DefaultKeyMapping.xml").write_text(optimized, encoding="utf-8")

    smk = (SOURCE / "smk.conf").read_text(encoding="utf-8", errors="replace")
    smk, smk_removed = clean_smk_residue(smk)
    (OUTPUT / "smk.conf").write_text(smk, encoding="utf-8")

    for name in FILES_TO_COPY:
        shutil.copy2(SOURCE / name, OUTPUT / name)

    smka_official = ROOT / "Official-Files" / "smka.conf"
    if smka_official.is_file():
        shutil.copy2(smka_official, OUTPUT / "smka.conf")

    print(f"Built: {OUTPUT}")
    print(f"Smart modes processed: {stats['smart_modes']}")
    print(f"WheelSlip removed: {stats['wheel_slip']}")
    print(f"Gun wheels fixed: {stats['gun_wheel']}")
    print(f"F2/F3 macros removed: {stats['f2f3']}")
    print(f"Swipe keys written: {stats['swipes']}")
    print(f"V keys injected: {stats['v_key']}")
    print(f"Pickup disable flags fixed: {stats['pickup_flags']}")
    print(f"AutoActive mouse tags normalized: {stats['mouse_tags']}")
    print(f"Tab LockEnemy ops removed: {stats['tab_lockenemy']}")
    print(f"Global ItemEx mode 3/4 synced: {stats['itemex_sync']}")
    print(f"LastMode EnableSwitchViewLockMethod=0: {stats['view_lock_method']}")
    print(f"Global RClick Shop1 fixes: {stats['rclick_shop1']}")
    print(f"Global mouse-lock tag normalizations: {stats['mouse_lock_tags']}")
    print(f"smk residue lines removed: {smk_removed}")
    print(f"PUBG LastMode -> ModeID {DEFAULT_LAST_MODE_ID} (Global ig -> {GLOBAL_2K_LAST_MODE_ID})")


if __name__ == "__main__":
    build()
