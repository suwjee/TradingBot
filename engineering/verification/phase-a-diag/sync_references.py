"""Synchronize embedded order_audit_engine.py Source in both Algorithm References."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(r"D:\My-Projects\TradingBot")
SRC = ROOT / "engine" / "pipeline" / "order_audit_engine.py"
ALGO = ROOT / "engine" / "algorithms"
REFS = [
    ALGO / "TradingBot_Bullish_Algorithm_Reference_V5.4.21_Source_Synchronized.md",
    ALGO / "TradingBot_Bearish_Algorithm_Reference_V5.4.21_Source_Synchronized.md",
]

raw = SRC.read_bytes()
text_src = raw.decode("utf-8")
src_for_embed = text_src
sha = hashlib.sha256(raw).hexdigest()
lf_count = raw.count(b"\n")
line_count = text_src.count("\n") + (0 if text_src.endswith("\n") else 1)
byte_count = len(raw)
version_match = re.search(r'ORDER_AUDIT_ENGINE_VERSION = "([^"]+)"', text_src)
version = version_match.group(1) if version_match else "unknown"
print(f"Source version={version} lines={line_count} bytes={byte_count} sha={sha}")

BEGIN = "<!-- EXACT-SOURCE-BEGIN:pipeline/order_audit_engine.py -->"
END = "<!-- EXACT-SOURCE-END:pipeline/order_audit_engine.py -->"

for ref_path in REFS:
    ref = ref_path.read_text(encoding="utf-8")
    b = ref.find(BEGIN)
    e = ref.find(END)
    if b < 0 or e < 0:
        raise SystemExit(f"markers missing in {ref_path}")
    # Replace entire BEGIN..END including markers.
    # The closing fence sits immediately after the exact Source bytes, so a
    # Source that already ends in a newline is NOT followed by an extra blank
    # line before ````.
    if src_for_embed.endswith("\n"):
        new_block = BEGIN + "\n````python\n" + src_for_embed + "````\n" + END
    else:
        new_block = BEGIN + "\n````python\n" + src_for_embed + "\n````\n" + END

    ref = ref[:b] + new_block + ref[e + len(END) :]

    # Update manifest row for order_audit_engine.py
    # | `pipeline/order_audit_engine.py` | Order / OrderAudit | `1.5.1` | 1863 | 75219 | `hash` |
    pattern = re.compile(
        r"(\| `pipeline/order_audit_engine\.py` \| Order / OrderAudit \| `)([^`]+)(` \| )(\d+)( \| )(\d+)( \| `)([0-9a-f]+)(` \|)"
    )
    def repl(m):
        return f"{m.group(1)}{version}{m.group(3)}{line_count}{m.group(5)}{byte_count}{m.group(7)}{sha}{m.group(9)}"

    ref2, n = pattern.subn(repl, ref)
    if n != 1:
        raise SystemExit(f"manifest row replacements={n} in {ref_path}")
    ref = ref2

    # Update the per-section metadata block immediately above the exact source.
    section = (
        f"**SHA-256:** `{sha}`  \n"
        f"**Bytes:** `{byte_count}`  \n"
        f"**LF count:** `{lf_count}`"
    )
    section_pattern = re.compile(
        r"(\*\*SHA-256:\*\* `)([0-9a-f]+)(`  \n\*\*Bytes:\*\* `)(\d+)(`  \n\*\*LF count:\*\* `)(\d+)(`)"
    )
    def section_repl(m):
        return f"{m.group(1)}{sha}{m.group(3)}{byte_count}{m.group(5)}{lf_count}{m.group(7)}"

    # Only replace the section belonging to order_audit_engine (the one just
    # before BEGIN).
    bpos = ref.find(BEGIN)
    if bpos < 0:
        raise SystemExit("BEGIN lost after manifest update")
    # search backward for the nearest SHA-256 block
    window_start = ref.rfind("**SHA-256:**", 0, bpos)
    if window_start < 0:
        raise SystemExit("section metadata missing")
    window_end = ref.find("\n\n", window_start)
    window = ref[window_start:window_end]
    new_window, sn = section_pattern.subn(section_repl, window)
    if sn != 1:
        raise SystemExit(f"section metadata replacements={sn} in {ref_path}")
    ref = ref[:window_start] + new_window + ref[window_end:]

    ref_path.write_text(ref, encoding="utf-8", newline="\n")
    print(f"updated {ref_path.name} block_bytes={len(new_block.encode('utf-8'))}")
