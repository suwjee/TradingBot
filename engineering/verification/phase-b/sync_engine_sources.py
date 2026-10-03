"""Synchronize embedded Engine Source blocks in both Algorithm References."""
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

# Only modules that changed and need embedded-source refresh.
TARGETS = [
    "pipeline/order_audit_engine.py",
    "pipeline/lifecycle_engine.py",
]


def source_meta(path: Path) -> dict:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    version_match = re.search(
        r'(?:ORDER_AUDIT_ENGINE_VERSION|STOP_ALL_VERSION) = "([^"]+)"', text
    )
    return {
        "raw": raw,
        "sha": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "lf": raw.count(b"\n"),
        "version": version_match.group(1) if version_match else "unknown",
    }


def sync_one(ref_path: Path, rel: str, meta: dict) -> None:
    ref = ref_path.read_text(encoding="utf-8")
    begin = f"<!-- EXACT-SOURCE-BEGIN:{rel} -->"
    end = f"<!-- EXACT-SOURCE-END:{rel} -->"
    b = ref.find(begin)
    e = ref.find(end)
    if b < 0 or e < 0:
        raise SystemExit(f"markers missing for {rel} in {ref_path.name}")
    src_for_embed = meta["raw"].decode("utf-8")
    if src_for_embed.endswith("\n"):
        new_block = begin + "\n````python\n" + src_for_embed + "````\n" + end
    else:
        new_block = begin + "\n````python\n" + src_for_embed + "\n````\n" + end
    ref = ref[:b] + new_block + ref[e + len(end) :]

    # Manifest table row: | `pipeline/x.py` | Label | `ver` | lines | bytes | `sha` |
    # Find the row by path prefix.
    row_re = re.compile(
        r"(\| `" + re.escape(rel) + r"` \| [^|]+ \| `)([^`]+)(` \| )(\d+)( \| )(\d+)( \| `)([0-9a-f]+)(` \|)"
    )
    ref, n = row_re.subn(
        lambda m: (
            f"{m.group(1)}{meta['version']}{m.group(3)}"
            f"{meta['lf']}{m.group(5)}{meta['bytes']}{m.group(7)}{meta['sha']}{m.group(9)}"
        ),
        ref,
    )
    if n != 1:
        raise SystemExit(f"manifest replacements={n} for {rel} in {ref_path.name}")

    # Per-section metadata immediately above the exact source.
    bpos = ref.find(begin)
    window_start = ref.rfind("**SHA-256:**", 0, bpos)
    if window_start < 0:
        raise SystemExit(f"section metadata missing for {rel}")
    window_end = ref.find("\n\n", window_start)
    window = ref[window_start:window_end]
    section_re = re.compile(
        r"(\*\*SHA-256:\*\* `)([0-9a-f]+)(`  \n\*\*Bytes:\*\* `)(\d+)(`  \n\*\*LF count:\*\* `)(\d+)(`)"
    )
    window2, sn = section_re.subn(
        lambda m: (
            f"{m.group(1)}{meta['sha']}{m.group(3)}"
            f"{meta['bytes']}{m.group(5)}{meta['lf']}{m.group(7)}"
        ),
        window,
    )
    if sn != 1:
        raise SystemExit(f"section replacements={sn} for {rel} in {ref_path.name}")
    ref = ref[:window_start] + window2 + ref[window_end:]

    ref_path.write_text(ref, encoding="utf-8", newline="\n")
    print(f"updated {ref_path.name} :: {rel}")


def main() -> int:
    for rel in TARGETS:
        meta = source_meta(ENGINE / rel)
        print(f"{rel} version={meta['version']} bytes={meta['bytes']} sha={meta['sha'][:16]}")
        for ref_path in REFS:
            sync_one(ref_path, rel, meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
