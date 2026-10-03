"""Phase A forensic diagnostic: dump audit/StopAll state at invariant failure.

Does not modify production Source. Wraps validate_order_audit_bridge to capture
the exact missing identity, public StopAll provenance, and canonical audit keys
before the RuntimeError is raised.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "engine" / "bridge"))
sys.path.insert(0, str(ROOT / "engine" / "pipeline"))

import trading_pipeline as tp  # noqa: E402

ORIGINAL = tp.validate_order_audit_bridge


def dump_item(item, limit=40):
    data = {}
    for name in dir(item):
        if name.startswith("_"):
            continue
        try:
            value = getattr(item, name)
        except Exception:
            continue
        if callable(value):
            continue
        data[name] = repr(value)[:200]
    return data


def patched(prepared_items, s_zones, e_zones, stopalls):
    missing_ids = []
    audit_identities = {
        tp.order_identity(
            int(getattr(item["reaction"], "first_idx")),
            int(getattr(item["reaction"], "break_idx")),
        )
        for item in prepared_items
    }
    for behavior_type, items in (
        ("S", s_zones),
        ("E", e_zones),
        ("StopAll", stopalls),
    ):
        for item in items:
            fi = getattr(item, "order_first_index", None)
            bi = getattr(item, "order_break_index", None)
            if fi is None or bi is None:
                continue
            identity = tp.order_identity(int(fi), int(bi))
            if identity not in audit_identities:
                missing_ids.append(
                    {
                        "behavior_type": behavior_type,
                        "source_time": str(getattr(item, "source_time", None)),
                        "identity": [int(identity[0]), int(identity[1])],
                        "item": dump_item(item),
                    }
                )

    if missing_ids:
        # Capture nearest neighbors around missing identity indices.
        report = {
            "missing": missing_ids,
            "audit_identity_count": len(audit_identities),
            "audit_identities_sample": sorted(list(audit_identities))[:30]
            + ["..."]
            + sorted(list(audit_identities))[-30:],
            "prepared_count": len(prepared_items),
            "prepared_summaries": [
                {
                    "identity": [
                        int(getattr(p["reaction"], "first_idx")),
                        int(getattr(p["reaction"], "break_idx")),
                    ],
                    "causes": p.get("causes"),
                    "entry_keys": sorted(p.get("entry", {}).keys()),
                }
                for p in prepared_items
            ],
        }
        out = Path(__file__).with_name("invariant-dump.json")
        out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"DIAG_DUMPED {out}", file=sys.stderr)

        # Also dump detector.order_audit / s_detector.order_audit if reachable
        # via prepare_order_audit call context is not available here; instead
        # scan stopalls for the missing identity details.
    return ORIGINAL(prepared_items, s_zones, e_zones, stopalls)


tp.validate_order_audit_bridge = patched

# Also instrument prepare_order_audit to record filtering decisions.
import order_audit_engine as oae  # noqa: E402

PREPARE = oae.prepare_order_audit


def prepare_instrumented(
    detector,
    start_index,
    end_index,
    s_detector=None,
    accepted_a_sources=None,
    required_identities=None,
):
    required = set(required_identities or set())
    s_values = list(s_detector.order_audit.values()) if s_detector else []
    e_values = list(detector.order_audit.values())
    dump = {
        "start_index": start_index,
        "end_index": end_index,
        "required_identities": sorted([list(map(int, i)) for i in required]),
        "s_order_audit_identities": sorted(
            [
                [
                    int(getattr(e["reaction"], "first_idx")),
                    int(getattr(e["reaction"], "break_idx")),
                ]
                for e in s_values
            ]
        ),
        "e_order_audit_identities": sorted(
            [
                [
                    int(getattr(e["reaction"], "first_idx")),
                    int(getattr(e["reaction"], "break_idx")),
                ]
                for e in e_values
            ]
        ),
        "accepted_a_sources": sorted(str(x) for x in (accepted_a_sources or [])),
        "s_entry_a_causes": [
            {
                "identity": [
                    int(getattr(e["reaction"], "first_idx")),
                    int(getattr(e["reaction"], "break_idx")),
                ],
                "a_causes": e.get("a_causes"),
                "a_source_time": str(e.get("a_source_time")),
            }
            for e in s_values
        ],
        "e_entry_causes": [
            {
                "identity": [
                    int(getattr(e["reaction"], "first_idx")),
                    int(getattr(e["reaction"], "break_idx")),
                ],
                "causes": e.get("causes"),
                "order_b_causes": e.get("order_b_causes"),
            }
            for e in e_values
        ],
    }
    result = PREPARE(
        detector,
        start_index,
        end_index,
        s_detector,
        accepted_a_sources,
        required_identities,
    )
    dump["prepared_identities"] = sorted(
        [
            [
                int(getattr(p["reaction"], "first_idx")),
                int(getattr(p["reaction"], "break_idx")),
            ]
            for p in result
        ]
    )
    dump["prepared_count"] = len(result)
    Path(__file__).with_name("prepare-dump.json").write_text(
        json.dumps(dump, indent=2, default=str), encoding="utf-8"
    )
    print("PREPARE_DUMPED", file=sys.stderr)
    return result


oae.prepare_order_audit = prepare_instrumented

# load_module() loads lifecycle_engine after this patch; its
# `from order_audit_engine import prepare_order_audit` binds the instrumented
# function. Also register under the load_module name if already present.
if "lifecycle_engine" in sys.modules:
    sys.modules["lifecycle_engine"].prepare_order_audit = prepare_instrumented

# Wrap load_module so the patched prepare_order_audit is bound after each load.
ORIGINAL_LOAD = tp.load_module


def load_module_patched(name, path):
    module = ORIGINAL_LOAD(name, path)
    if name == "lifecycle_engine" and hasattr(module, "prepare_order_audit"):
        module.prepare_order_audit = prepare_instrumented
    return module


tp.load_module = load_module_patched

if __name__ == "__main__":
    raise SystemExit(tp.main())
