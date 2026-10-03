"""Phase A targeted diagnostic: inspect E/StopAll identity (47608, 47610)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "engine" / "bridge"))
sys.path.insert(0, str(ROOT / "engine" / "pipeline"))

TARGET = (47608, 47610)
OUT = Path(__file__).with_name("target-identity-report.json")

import trading_pipeline as tp  # noqa: E402
import order_audit_engine as oae  # noqa: E402

report: dict = {"target": list(TARGET)}


def zone_brief(zone):
    return {
        "family": getattr(zone, "family", None),
        "number": getattr(zone, "number", None),
        "parent_type": getattr(zone, "parent_type", None),
        "parent_source_time": str(getattr(zone, "parent_source_time", None)),
        "parent_stop_event_time": str(getattr(zone, "parent_stop_event_time", None)),
        "source_time": str(getattr(zone, "source_time", None)),
        "source_index": getattr(zone, "source_index", None),
        "order_first_index": getattr(zone, "order_first_index", None),
        "order_break_index": getattr(zone, "order_break_index", None),
        "order_causes": list(getattr(zone, "order_causes", ()) or ()),
        "order_parent_stop_cause_time": str(
            getattr(zone, "order_parent_stop_cause_time", None)
        ),
        "order_mode": getattr(zone, "order_mode", None),
        "order_reaction_number": getattr(zone, "order_reaction_number", None),
    }


def dump_audit(detector, label):
    entries = []
    for identity, entry in detector.order_audit.items():
        if identity == TARGET or (
            abs(identity[0] - TARGET[0]) <= 3 and abs(identity[1] - TARGET[1]) <= 3
        ):
            entries.append(
                {
                    "identity": list(map(int, identity)),
                    "causes": [list(map(str, c)) for c in entry.get("causes", set())],
                    "order_b_causes": entry.get("order_b_causes"),
                    "confirmation_time": str(entry.get("confirmation_time")),
                }
            )
    report[label] = {
        "has_target": TARGET in detector.order_audit,
        "count": len(detector.order_audit),
        "near": entries,
        "has_sequence_reset_between_parent_and_stop": detector._has_sequence_reset_between(
            __import__("datetime").datetime(2026, 9, 15, 15, 5, 15),
            __import__("datetime").datetime(2026, 9, 15, 15, 7),
        ),
        "sequence_resets_near": {
            str(k): v
            for k, v in getattr(detector, "sequence_resets", {}).items()
            if str(k).startswith("2026-09-15")
        },
    }


# Patch ensure_accepted_order_audit to inspect after rebuild.
ORIG_ENSURE = oae.OrderAuditEngineMixin.ensure_accepted_order_audit


def ensure_patched(self, zones, supplemental_s_zones=()):
    result = ORIG_ENSURE(self, zones, supplemental_s_zones)
    target_zones = [
        zone_brief(z)
        for z in list(zones)
        if getattr(z, "order_first_index", None) == TARGET[0]
        and getattr(z, "order_break_index", None) == TARGET[1]
    ]
    report["ensure_zones_with_target"] = target_zones
    report["ensure_zone_count"] = len(list(zones))
    dump_audit(self, "audit_after_ensure")
    # Simulate rebuild cause generation for target zone.
    for z in list(zones):
        if (
            getattr(z, "order_first_index", None) == TARGET[0]
            and getattr(z, "order_break_index", None) == TARGET[1]
        ):
            causes = []
            if getattr(z, "order_parent_stop_cause_time", None) is not None:
                causes.append(
                    {
                        "kind": "parent-stop",
                        "parent_label": z.parent_type,
                        "parent_source_time": str(z.parent_source_time),
                        "parent_stop_event_time": str(z.parent_stop_event_time),
                        "parent_source_in_sequence_resets": z.parent_source_time
                        in getattr(self, "sequence_resets", {}),
                    }
                )
            report["simulated_rebuild_causes"] = causes
            report["would_skip_due_to_sequence_reset"] = (
                self._has_sequence_reset_between(
                    z.parent_source_time, z.parent_stop_event_time
                )
            )
    return result


oae.OrderAuditEngineMixin.ensure_accepted_order_audit = ensure_patched

# Also patch _rebuild to record whether target is registered.
ORIG_REBUILD = oae.OrderAuditEngineMixin._rebuild_accepted_order_audit


def rebuild_patched(self, numbered, supplemental_s_zones=()):
    target_in_numbered = any(
        getattr(z, "order_first_index", None) == TARGET[0]
        and getattr(z, "order_break_index", None) == TARGET[1]
        for z in numbered
    )
    report["rebuild_target_in_numbered"] = target_in_numbered
    result = ORIG_REBUILD(self, numbered, supplemental_s_zones)
    report["audit_after_rebuild"] = {
        "has_target": TARGET in self.order_audit,
        "count": len(self.order_audit),
    }
    return result


oae.OrderAuditEngineMixin._rebuild_accepted_order_audit = rebuild_patched

# Capture stopalls with target identity at validate time.
ORIG_VALIDATE = tp.validate_order_audit_bridge


def validate_patched(prepared, s_zones, e_zones, stopalls):
    report["stopalls_with_target"] = [
        zone_brief(x)
        for x in stopalls
        if getattr(x, "order_first_index", None) == TARGET[0]
        and getattr(x, "order_break_index", None) == TARGET[1]
    ]
    report["e_with_target"] = [
        zone_brief(x)
        for x in e_zones
        if getattr(x, "order_first_index", None) == TARGET[0]
        and getattr(x, "order_break_index", None) == TARGET[1]
    ]
    report["s_with_target"] = [
        zone_brief(x)
        for x in s_zones
        if getattr(x, "order_first_index", None) == TARGET[0]
        and getattr(x, "order_break_index", None) == TARGET[1]
    ]
    prepared_ids = [
        [
            int(getattr(p["reaction"], "first_idx")),
            int(getattr(p["reaction"], "break_idx")),
        ]
        for p in prepared
    ]
    report["prepared_has_target"] = list(TARGET) in prepared_ids
    OUT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print("TARGET_REPORT_WRITTEN", OUT, file=sys.stderr)
    return ORIG_VALIDATE(prepared, s_zones, e_zones, stopalls)


tp.validate_order_audit_bridge = validate_patched

ORIG_LOAD = tp.load_module


def load_patched(name, path):
    module = ORIG_LOAD(name, path)
    if name == "lifecycle_engine":
        module.prepare_order_audit = oae.prepare_order_audit
    return module


tp.load_module = load_patched

if __name__ == "__main__":
    raise SystemExit(tp.main())
