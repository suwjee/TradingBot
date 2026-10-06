"""Deduplicate unchanged-source Order-tie observations and join final visible E.

This reads the root's observation-only trace and independently checks that its
stable payload equals the completed uninstrumented calculation. It does not
rerun or mutate Engine or market RAW. Candidate eligibility is recorded at the
actual _first_order boundary by trace_pipeline.py --order-ties.
"""
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
TEHRAN = timezone(timedelta(hours=3, minutes=30))
TRACE = AUDIT / "traces/raw-08-30s-ties.events.json"
PAYLOAD = AUDIT / "traces/raw-08-30s-ties.payload.json"
BASELINE = AUDIT / "raw-30s/raw-08-30s-1.stdout.json"


def local(epoch):
    return datetime.fromtimestamp(epoch, TEHRAN).replace(tzinfo=None).isoformat(sep=" ")


def normalize_public(zone):
    row = {}
    for key, value in zone.items():
        name = "".join("_" + c.lower() if c.isupper() else c for c in key)
        row[name] = local(value) if key.endswith("Time") and value is not None else value
    return row


def core_identity(zone):
    # Family/number may be recanonicalized after a recursive branch; retain
    # physical parent, exact stop, Order, source and decision identity instead.
    fields = (
        "direction", "parent_type", "parent_source_index", "parent_source_time",
        "parent_price", "parent_stop_event_time", "order_direction",
        "order_first_index", "order_break_index", "order_confirmation_time",
        "source_index", "source_time", "price", "decision_index",
        "decision_event_time",
    )
    return tuple(zone.get(k) for k in fields)


def main():
    events = json.loads(TRACE.read_text(encoding="utf-8"))
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE.read_bytes())
    stable_payload = {k: v for k, v in payload.items() if k != "timings"}
    stable_baseline = {k: v for k, v in baseline.items() if k != "timings"}
    assert stable_payload == stable_baseline, "Observation payload changed stable result"
    ties = [r for r in events if r.get("kind") == "order-tie-subroute"]
    surviving = [r for r in ties if r["wrongOrderSurvivesZone"]]
    routes = {
        (r["direction"], r["parentStop"], r["actualFirst"], r["actualBreak"],
         r["expectedFirst"], r["expectedBreak"], r["sameStrictStop"])
        for r in ties
    }
    native_zones = {json.dumps(r["zone"], sort_keys=True) for r in surviving}
    by_core = {}
    for r in surviving:
        assert r["expectedFirst"] > r["actualFirst"]
        assert r["zone"]["order_first_index"] == r["actualFirst"]
        assert r["zone"]["decision_event_time"] == r["sameStrictStop"]
        by_core.setdefault(core_identity(r["zone"]), []).append(r)
    final = []
    for direction, body in payload["directions"].items():
        ledger = {(r["firstIndex"], r["breakIndex"]): r for r in body["orderAudit"]}
        for public in body["eZones"]:
            zone = normalize_public(public)
            matches = by_core.get(core_identity(zone), [])
            if not matches:
                continue
            candidate_ids = sorted({(m["expectedFirst"], m["expectedBreak"]) for m in matches})
            actual = ledger[(public["orderFirstIndex"], public["orderBreakIndex"])]
            expected_orders = []
            for order_id in candidate_ids:
                expected = ledger[order_id]
                assert expected["stopHitEventTime"] == actual["stopHitEventTime"]
                assert local(expected["stopHitEventTime"]) == zone["decision_event_time"]
                confirmation = next(m["expectedConfirmation"] for m in matches
                                    if (m["expectedFirst"], m["expectedBreak"]) == order_id)
                expected_orders.append({**normalize_public(expected),
                                        "recorded_confirmation_time": confirmation})
            final.append({
                "direction": direction,
                "final_E": zone,
                "selected_Order": normalize_public(actual),
                "expected_Orders": expected_orders,
                "matching_native_observations": len(matches),
                "native_route_causes": sorted({cause for m in matches for cause in m["expectedRoutes"]}),
            })
    result = {
        "classification": "Confirmed RAW spec-to-code divergence; unchanged Source",
        "trace": str(TRACE), "payload": str(PAYLOAD), "baseline": str(BASELINE),
        "stable_uninstrumented_equality": True,
        "tie_observations": len(ties),
        "wrong_order_survives_zone_observations": len(surviving),
        "unique_subroute_conflicts": len(routes),
        "unique_native_zone_variants_with_wrong_order": len(native_zones),
        "unique_physical_zone_cores_with_wrong_order": len(by_core),
        "unique_final_visible_E_with_wrong_order": len(final),
        "final_visible_by_direction": dict(Counter(r["direction"] for r in final)),
        "final_visible_cases": final,
        "duplicate_policy": "Final cases are enumerated once per actual public E row; intermediate family/number variants collapse by physical parent/Order/source/decision identity.",
    }
    target = AUDIT / "s-e-audit/RAW-tie-confirmation.json"
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "final_visible_cases"}, indent=2))
    for direction in ("bullish", "bearish"):
        cases = [r for r in final if r["direction"] == direction]
        if cases:
            example = next((r for r in cases if r["final_E"]["source_index"] == 2847), cases[0])
            print(json.dumps(example, indent=2))


if __name__ == "__main__":
    main()
