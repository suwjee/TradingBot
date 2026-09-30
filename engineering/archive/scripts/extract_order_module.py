"""Perform the one-time, baseline-guarded Order ownership extraction."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/manifest.json"
E_PATH = ROOT / "engine/pipeline/e_zone_detector.py"
LIFECYCLE_PATH = ROOT / "engine/pipeline/lifecycle_engine.py"
ORDER_PATH = ROOT / "engine/pipeline/order_audit_engine.py"

E_TOP_LEVEL = {
    "PostBehaviorStop", "OrderBResetLeg", "dominant_post_behavior_stops",
    "order_b_reset_event_time", "discover_order_b_reset_legs",
    "discover_accepted_order_b_reset_legs", "OrderMatch",
}
E_METHODS = {
    "_order_stop", "order_stop", "_first_healthy_direct_geometry",
    "_trend_leg_direct_order", "_direct_parent_stop_order",
    "_merge_order_candidate", "_enforce_single_parent_stop_owner",
    "order_candidates", "_first_order", "_has_sequence_reset_between",
    "_blue_parent_superseded", "_index_order_audit_identity",
    "_clear_order_audit", "register_order_b_reset_legs",
    "_register_order_audit", "visual_order_lifecycle", "_cross_order",
    "cross_order", "_unconsumed_s_orders", "_initial_order_records",
    "_initial_record_match", "_initial_order_match", "_gate_owned_initial_order",
    "_carried_orders_for_parent", "_post_stop_accepted_orders_for_parent",
    "_blocked_by_gate_owned_order", "_rebuild_accepted_order_audit",
    "rebuild_accepted_order_audit", "ensure_accepted_order_audit",
}
LIFECYCLE_FUNCTIONS = {
    "prepare_order_audit", "accepted_audit_entry",
    "order_identity_is_internal",
}


def span(node: ast.AST) -> tuple[int, int]:
    decorators = getattr(node, "decorator_list", ())
    start = min([node.lineno, *(item.lineno for item in decorators)]) - 1
    return start, node.end_lineno


def extract(source: str, selected: list[ast.AST]) -> tuple[str, list[str]]:
    lines = source.splitlines(keepends=True)
    blocks: list[tuple[int, str]] = []
    occupied: set[int] = set()
    for node in selected:
        start, end = span(node)
        if occupied.intersection(range(start, end)):
            raise ValueError("Overlapping extraction ranges")
        occupied.update(range(start, end))
        blocks.append((start, "".join(lines[start:end])))
    for index in occupied:
        lines[index] = ""
    return "".join(lines), [block for _start, block in sorted(blocks)]


def main() -> None:
    import hashlib

    manifest = json.loads(BASELINE.read_text(encoding="utf-8"))
    for path in (E_PATH, LIFECYCLE_PATH):
        relative = path.relative_to(ROOT).as_posix()
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != manifest["sourceHashes"][relative]:
            raise ValueError(f"Source changed after Phase 1 baseline: {relative}")
    if ORDER_PATH.exists():
        raise FileExistsError(ORDER_PATH)

    e_source = E_PATH.read_text(encoding="utf-8")
    e_tree = ast.parse(e_source)
    e_class = next(
        node for node in e_tree.body
        if isinstance(node, ast.ClassDef) and node.name == "EZoneDetector"
    )
    selected_top = [
        node for node in e_tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.Assign))
        and getattr(node, "name", None) in E_TOP_LEVEL
        or isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id in E_TOP_LEVEL
                for target in node.targets)
    ]
    selected_methods = [
        node for node in e_class.body
        if isinstance(node, ast.FunctionDef) and node.name in E_METHODS
    ]
    if len(selected_top) != len(E_TOP_LEVEL) or len(selected_methods) != len(E_METHODS):
        raise ValueError("Order extraction inventory does not match source")
    e_remaining, e_blocks = extract(e_source, selected_top + selected_methods)
    e_remaining = e_remaining.replace(
        "from direction_policy import policy_for\n",
        "from direction_policy import policy_for\n"
        "from order_audit_engine import (\n"
        "    OrderAuditEngineMixin, OrderBResetLeg, OrderMatch, PostBehaviorStop,\n"
        "    discover_accepted_order_b_reset_legs, discover_order_b_reset_legs,\n"
        "    dominant_post_behavior_stops, order_b_reset_event_time,\n"
        ")\n",
        1,
    ).replace("class EZoneDetector:\n", "class EZoneDetector(OrderAuditEngineMixin):\n", 1)

    lifecycle_source = LIFECYCLE_PATH.read_text(encoding="utf-8")
    lifecycle_tree = ast.parse(lifecycle_source)
    selected_lifecycle = [
        node for node in lifecycle_tree.body
        if isinstance(node, ast.FunctionDef) and node.name in LIFECYCLE_FUNCTIONS
    ]
    if len(selected_lifecycle) != len(LIFECYCLE_FUNCTIONS):
        raise ValueError("Lifecycle Order function inventory does not match source")
    lifecycle_remaining, lifecycle_blocks = extract(
        lifecycle_source, selected_lifecycle,
    )
    lifecycle_remaining = lifecycle_remaining.replace(
        "from core_utils import as_decimal, order_identity\n",
        "from core_utils import as_decimal, order_identity\n"
        "from order_audit_engine import (\n"
        "    accepted_audit_entry, order_identity_is_internal, prepare_order_audit,\n"
        ")\n",
        1,
    )

    header = '''"""Central physical Order discovery, reuse, provenance, and audit ownership."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from typing import Callable, Sequence

from core_utils import as_decimal, order_identity, reaction_identity

ORDER_AUDIT_ENGINE_VERSION = "1.0.0"
ORDER_AUDIT_ENGINE_LAST_MODIFIED = "2026-09-27 23:00:00 +03:30"

'''
    top_blocks = e_blocks[:len(selected_top)]
    method_blocks = e_blocks[len(selected_top):]
    # Extraction preserves source order, and top-level declarations precede
    # detector methods in the Phase 1 source.
    module = header + "\n\n".join(top_blocks) + "\n\n"
    module += "class OrderAuditEngineMixin:\n"
    module += "    \"\"\"Order methods shared by the accepted E lifecycle detector.\"\"\"\n\n"
    module += "\n\n".join(method_blocks) + "\n\n"
    module += "\n\n".join(lifecycle_blocks) + "\n"

    ast.parse(module)
    ast.parse(e_remaining)
    ast.parse(lifecycle_remaining)
    ORDER_PATH.write_text(module, encoding="utf-8", newline="\n")
    E_PATH.write_text(e_remaining, encoding="utf-8", newline="\n")
    LIFECYCLE_PATH.write_text(lifecycle_remaining, encoding="utf-8", newline="\n")
    print(
        f"Extracted {len(selected_top)} Order declarations, "
        f"{len(selected_methods)} E Order methods, "
        f"{len(selected_lifecycle)} lifecycle Order functions"
    )


if __name__ == "__main__":
    main()
