"""Compare legacy arrays and verify user-taught primary-structure anchors.

This verification helper consumes saved full-pipeline JSON; no RAW is modified
and no fixture identity participates in the production detector.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def verify_example(payload):
    group = payload["directions"]["bearish"]
    stamp = lambda value: datetime.fromtimestamp(value, ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")
    leg, = [row for row in group["matchingBehaviorLegs"]
            if stamp(row["sourceTime"]) == "2026-09-29 21:28:00"]
    high = next(row for row in group["primaryHighs"]
                if row.get("cycleId") == leg.get("cycleId") and row["number"] == 1)
    assert high["number"] == 1
    assert Decimal(high["price"]) == Decimal("4175.755")
    assert stamp(high["sourceTime"]) == "2026-09-29 22:10:00"
    assert stamp(high["triggerTime"]) == "2026-09-29 22:09:00"
    assert stamp(high["decisionTime"]) == "2026-09-29 23:12:00"
    assert stamp(high["decisionEventTime"]) == "2026-09-29 23:12:15"
    assert Decimal(leg["price"]) == Decimal("4142.445")
    assert stamp(leg["sourceTime"]) == "2026-09-29 21:28:00"
    assert high["order"]["ownerDirection"] == "bearish"
    assert high["order"]["direction"] == "bullish"
    assert high["order"]["causes"] == ["parent-stop"]


def verify_usoil_example(payload):
    group = payload["directions"]["bearish"]
    stamp = lambda value: datetime.fromtimestamp(value, ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")
    reference, = [row for row in group["stopAlls"]
                  if stamp(row["sourceTime"]) == "2026-10-06 08:21:00"]
    second, = [row for row in group["sZones"]
               if stamp(row["sourceTime"]) == "2026-10-06 14:37:00"]
    leg, = [row for row in group["matchingBehaviorLegs"]
            if row["secondBehaviorIndex"] == second["sourceIndex"]]
    high = next(row for row in group["primaryHighs"]
                if row.get("cycleId") == leg.get("cycleId") and row["number"] == 1)
    assert reference["number"] == 5
    assert Decimal(reference["price"]) == Decimal("90.028")
    assert leg["referenceStopAllIndex"] == reference["sourceIndex"]
    assert leg["secondBehaviorIndex"] == second["sourceIndex"]
    assert high["number"] == 1
    assert stamp(high["sourceTime"]) == "2026-10-07 00:13:30"
    assert Decimal(high["price"]) == Decimal("90.034")
    assert stamp(high["triggerEventTime"]) == "2026-10-07 00:13:45"
    assert stamp(high["decisionEventTime"]) == "2026-10-07 01:31:00"
    order = high["order"]
    assert stamp(order["firstTime"]) == "2026-10-07 00:10:30"
    assert order["confirmationEventTime"] == high["triggerEventTime"]
    assert order["stopHitEventTime"] == high["decisionEventTime"]
    assert order["types"] == ["Order_A"]
    assert order["ownerDirection"] == "bearish"
    assert order["direction"] == "bullish"
    assert stamp(leg["sourceTime"]) == "2026-10-06 15:50:30"
    assert Decimal(leg["price"]) == Decimal("86.867")
    assert stamp(leg["capTime"]) == "2026-10-06 19:10:30"
    assert not any(row["sourceIndex"] == high["sourceIndex"] for row in group["stopAlls"])


def verify_independent_usoil_example(payload):
    """The first PH3 stop globally excludes later qualified October cycles."""
    verify_usoil_example(payload)
    group = payload["directions"]["bearish"]
    stamp = lambda value: datetime.fromtimestamp(value, ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")
    earlier = [row for row in group["primaryCycles"]
               if stamp(row["triggerEventTime"]) == "2026-10-07 00:13:45"]
    assert len(earlier) == 1 and len(group["primaryCycles"]) == 1
    assert earlier[0]["status"] == "stopped-on-trend-reversal"
    assert len({row["id"] for row in group["primaryHighs"]}) == len(group["primaryHighs"])
    assert len({row["id"] for row in group["matchingBehaviorLegs"]}) == len(group["matchingBehaviorLegs"])


def verify_usoil_ph_number_priority(payload):
    """Final PH1..PH3 ownership survives the global reversal unchanged."""
    group = payload["directions"]["bearish"]
    stamp = lambda value: datetime.fromtimestamp(value, ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")
    highs = group["primaryHighs"]
    assert len({(row["sourceIndex"], row["sourceTime"]) for row in highs}) == len(highs)
    by_time = {stamp(row["sourceTime"]): row for row in highs}
    for instant, number in (("2026-10-07 00:13:30", 1),
                            ("2026-10-07 03:55:30", 2),
                            ("2026-10-07 04:47:00", 3)):
        assert by_time[instant]["number"] == number, (instant, number)
    assert len(highs) == 3
    labels = {row["sourceTime"]: f"PH{row['number']}" for row in highs}
    causes = [cause for row in group["orderAudit"] for cause in row["causes"]]
    causes += [cause for row in [*highs, *group["primaryLows"]]
               for cause in row["order"]["auditCauses"]]
    for cause in causes:
        for field, source in (("parentType", "parentSourceTime"),
                              ("postBehaviorType", "postBehaviorSourceTime"),
                              ("anchorBehaviorType", "anchorBehaviorSourceTime")):
            if str(cause.get(field, "")).startswith("PH") and cause.get(source) in labels:
                assert cause[field] == labels[cause[source]], cause


def verify_usoil_trend_reversal(payload):
    """Current complete user acceptance example, including fresh bullish state."""
    verify_independent_usoil_example(payload)
    verify_usoil_ph_number_priority(payload)
    stamp = lambda value: datetime.fromtimestamp(value, ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")
    bearish,bullish = payload["directions"]["bearish"],payload["directions"]["bullish"]
    assert payload["activeDirection"] == "bullish"
    transition, = bullish["trendTransitions"]
    assert stamp(transition["sourceTime"]) == "2026-10-07 16:57:30"
    assert stamp(transition["eventTime"]) == "2026-10-07 16:57:30"
    assert transition["level"] == "90.573"
    assert transition["iconCandleIndex"]-transition["sourceIndex"] == 49
    assert stamp(transition["iconCandleTime"]) == "2026-10-07 17:22:00"
    first = bullish["reactions"][0]
    for field,expected in (("firstTime","16:57:30"),("boxTopSourceTime","16:57:30"),
                           ("boxBottomSourceTime","16:59:30"),("breakTime","17:00:30")):
        assert stamp(first[field]) == "2026-10-07 "+expected
    assert first["boxTop"] == "90.622" and first["boxBottom"] == "90.364"
    assert all(row["firstTime"] >= transition["sourceTime"] for row in bullish["reactions"])
    assert all(row["firstTime"] < transition["sourceTime"] for row in bearish["reactions"])


def verify_formed_mbls(payload):
    """Full-stream MBLs require a valid StopAll reference and confirmed PH."""
    group = payload["directions"]["bearish"]
    high_sources = {row["sourceIndex"] for row in group["primaryHighs"]}
    stopalls = {row["sourceIndex"]: row for row in group["stopAlls"]}
    cycles = {row["id"]: row for row in group["primaryCycles"]}
    for leg in group["matchingBehaviorLegs"]:
        assert leg["referenceStopAllIndex"] not in high_sources, leg
        assert stopalls[leg["referenceStopAllIndex"]]["number"] >= 3, leg
        assert cycles[leg["cycleId"]]["highCount"] >= 1, leg
        assert leg["confirmationIndex"] >= leg["triggerIndex"], leg
        assert leg["confirmationEventTime"] >= leg["triggerEventTime"], leg


def compare(before, after):
    for direction, group in before["directions"].items():
        for key, value in group.items():
            assert value == after["directions"][direction][key], (direction, key)
    assert "primaryHighs" not in after["directions"].get("bullish", {})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--xauusd-user-example", action="store_true")
    parser.add_argument("--usoil-user-example", action="store_true")
    parser.add_argument("--usoil-independent-cycles", action="store_true")
    parser.add_argument("--usoil-ph-number-priority", action="store_true")
    parser.add_argument("--usoil-trend-reversal", action="store_true")
    parser.add_argument("--formed-mbls", action="store_true")
    args = parser.parse_args()
    if args.before is None and not (args.xauusd_user_example or args.usoil_user_example or args.usoil_independent_cycles or args.usoil_ph_number_priority or args.usoil_trend_reversal or args.formed_mbls):
        parser.error("Provide --before or select a user acceptance example.")
    after = json.loads(args.after.read_bytes())
    checks = []
    if args.before is not None:
        compare(json.loads(args.before.read_bytes()), after)
        checks.append("existing arrays unchanged")
    if args.xauusd_user_example:
        verify_example(after)
        checks.append("XAUUSD PH-1/MBL anchor matches")
    if args.usoil_user_example:
        verify_usoil_example(after)
        checks.append("USOIL PH-1/MBL and joint-confirmation anchor matches")
    if args.usoil_independent_cycles:
        verify_independent_usoil_example(after)
        checks.append("USOIL first PH3 stop excludes later October cycles")
    if args.usoil_ph_number_priority:
        verify_usoil_ph_number_priority(after)
        checks.append("USOIL PH1/2/3 and native parent names match")
    if args.usoil_trend_reversal:
        verify_usoil_trend_reversal(after)
        checks.append("USOIL global PH3 reversal and isolated bullish Reaction match")
    if args.formed_mbls:
        verify_formed_mbls(after)
        checks.append("MBLs have valid StopAll references and confirmed PH")
    print("PASS: " + "; ".join(checks))
