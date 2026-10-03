"""Synchronize embedded Engine Source in both Algorithm References."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(r"D:\My-Projects\TradingBot")
ENGINE = ROOT / "engine"
ALGO = ENGINE / "algorithms"
REFS = [
    ALGO / "TradingBot_Bullish_Algorithm_Reference_V5.4.21_Source_Synchronized.md",
    ALGO / "TradingBot_Bearish_Algorithm_Reference_V5.4.21_Source_Synchronized.md",
]

VERSION_KEYS = (
    "ORDER_AUDIT_ENGINE_VERSION",
    "E_ZONE_VERSION",
    "E_ZONE_IMPLEMENTATION_VERSION",
    "A_ZONE_VERSION",
    "CORE_UTILS_VERSION",
    "REACTION_ENGINE_VERSION",
    "REACTION_ENGINE_IMPLEMENTATION_VERSION",
    "STOP_ALL_VERSION",
    "STOP_ALL_IMPLEMENTATION_VERSION",
    "S_ZONE_VERSION",
    "BLUE_LINE_VERSION",
    "PIPELINE_VERSION",
)


def source_version(text: str) -> str:
    primary = None
    impls = []
    for key in VERSION_KEYS:
        m = re.search(rf'{key}\s*=\s*"([^"]+)"', text)
        if not m:
            continue
        if "IMPLEMENTATION" in key:
            impls.append(m.group(1))
        elif primary is None:
            primary = m.group(1)
    if primary is None:
        return "unversioned"
    if impls and impls[0] != primary:
        return f"{primary} (impl {impls[0]})"
    return primary


def sync_one(ref_path: Path, relative: str) -> bool:
    src_path = ENGINE / relative
    raw = src_path.read_bytes()
    text_src = raw.decode("utf-8")
    sha = hashlib.sha256(raw).hexdigest()
    lf_count = raw.count(b"\n")
    byte_count = len(raw)
    line_count = text_src.count("\n") + (0 if text_src.endswith("\n") else 1)
    version = source_version(text_src)

    BEGIN = f"<!-- EXACT-SOURCE-BEGIN:{relative} -->"
    END = f"<!-- EXACT-SOURCE-END:{relative} -->"
    ref = ref_path.read_text(encoding="utf-8")
    b = ref.find(BEGIN)
    e = ref.find(END)
    if b < 0 or e < 0:
        print(f"  skip missing block {relative}")
        return False

    # Closing fence must follow the exact Source bytes with no added newline
    # so extraction equals the production file byte-for-byte.
    new_block = BEGIN + "\n````python\n" + text_src + "````\n" + END
    ref = ref[:b] + new_block + ref[e + len(END) :]

    # Manifest row: | `path` | Owner | `ver` | lines | bytes | `hash` |
    row_pattern = re.compile(
        rf"(\| `{re.escape(relative)}` \| [^|]+ \| `)([^`]+)(` \| )(\d+)( \| )(\d+)( \| `)([0-9a-f]+)(` \|)"
    )

    def row_repl(m: re.Match) -> str:
        return f"{m.group(1)}{version}{m.group(3)}{line_count}{m.group(5)}{byte_count}{m.group(7)}{sha}{m.group(9)}"

    ref, nrow = row_pattern.subn(row_repl, ref)
    if nrow != 1:
        print(f"  warn manifest rows={nrow} for {relative}")

    # Section metadata immediately before BEGIN.
    bpos = ref.find(BEGIN)
    window_start = ref.rfind("**SHA-256:**", 0, bpos)
    if window_start < 0:
        print(f"  warn section metadata missing for {relative}")
    else:
        window_end = ref.find("\n\n", window_start)
        if window_end < 0:
            window_end = bpos
        window = ref[window_start:window_end]
        section_pattern = re.compile(
            r"(\*\*SHA-256:\*\* `)([0-9a-f]+)(`  \n\*\*Bytes:\*\* `)(\d+)(`  \n\*\*LF count:\*\* `)(\d+)(`)"
        )
        new_window, sn = section_pattern.subn(
            lambda m: f"{m.group(1)}{sha}{m.group(3)}{byte_count}{m.group(5)}{lf_count}{m.group(7)}",
            window,
        )
        if sn == 1:
            ref = ref[:window_start] + new_window + ref[window_end:]
        else:
            print(f"  warn section replacements={sn} for {relative}")

    ref_path.write_text(ref, encoding="utf-8", newline="\n")
    print(f"  updated {relative} -> {ref_path.name}")
    return True


def main() -> int:
    files = [
        "__init__.py",
        "bridge/__init__.py",
        "bridge/trading_pipeline.py",
        "pipeline/__init__.py",
        "pipeline/a_zone_detector.py",
        "pipeline/blue_line_detector.py",
        "pipeline/core_utils.py",
        "pipeline/direction_policy.py",
        "pipeline/e_zone_detector.py",
        "pipeline/lifecycle_engine.py",
        "pipeline/order_audit_engine.py",
        "pipeline/reaction_engine.py",
        "pipeline/s_zone_detector.py",
    ]
    for ref in REFS:
        print("SYNC", ref.name)
        for rel in files:
            sync_one(ref, rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
