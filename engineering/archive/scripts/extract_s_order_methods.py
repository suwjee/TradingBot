"""Move S-owned physical Order creation and stop lookup to the Order module."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/manifest.json"
S_PATH = ROOT / "engine/pipeline/s_zone_detector.py"
ORDER_PATH = ROOT / "engine/pipeline/order_audit_engine.py"
METHODS = {
    "_first_order_after", "_order_matches_after", "_record_a_order_audit",
    "_audit_stopped_a", "_order_stop", "_order_stop_crossed",
    "_shared_order_stop_cross",
}


def main() -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    if hashlib.sha256(S_PATH.read_bytes()).hexdigest() != baseline["sourceHashes"][
        "engine/pipeline/s_zone_detector.py"
    ]:
        raise ValueError("S source changed after the Phase 1 baseline")
    source = S_PATH.read_text(encoding="utf-8")
    order_source = ORDER_PATH.read_text(encoding="utf-8")
    if "class SOrderAuditMixin:" in order_source:
        raise ValueError("S Order methods are already extracted")
    tree = ast.parse(source)
    detector = next(
        item for item in tree.body
        if isinstance(item, ast.ClassDef) and item.name == "SZoneDetector"
    )
    selected = [
        item for item in detector.body
        if isinstance(item, ast.FunctionDef) and item.name in METHODS
    ]
    if len(selected) != len(METHODS):
        raise ValueError("S Order method inventory does not match source")
    lines = source.splitlines(keepends=True)
    blocks = []
    for item in selected:
        start = min([item.lineno, *(decorator.lineno for decorator in item.decorator_list)]) - 1
        blocks.append((start, "".join(lines[start:item.end_lineno])))
        for index in range(start, item.end_lineno):
            lines[index] = ""
    remaining = "".join(lines)
    remaining = remaining.replace(
        "from core_utils import as_decimal, reaction_identity\n",
        "from core_utils import as_decimal, reaction_identity\n"
        "from order_audit_engine import SOrderAuditMixin\n",
        1,
    ).replace("class SZoneDetector:\n", "class SZoneDetector(SOrderAuditMixin):\n", 1)
    new_order_source = order_source.rstrip() + "\n\n\nclass SOrderAuditMixin:\n"
    new_order_source += "    \"\"\"Physical Order_A and shared Order stop operations for S.\"\"\"\n\n"
    new_order_source += "\n\n".join(block for _start, block in sorted(blocks)) + "\n"
    ast.parse(remaining)
    ast.parse(new_order_source)
    S_PATH.write_text(remaining, encoding="utf-8", newline="\n")
    ORDER_PATH.write_text(new_order_source, encoding="utf-8", newline="\n")
    print(f"Extracted {len(selected)} S Order methods")


if __name__ == "__main__":
    main()
