"""Verify user acceptance anchors against a completed native pipeline replay.

Fixture timestamps live only in this verification helper, never production.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "apps/chart/state/tmp/bullish-setups"
NEW_FIELDS = {"setupVersion", "setupPhase", "positionSetups", "stopAllAssessments",
              "behaviorAssessments", "setupReferenceBreaks"}


def without_annotations(value):
    if isinstance(value, dict):
        return {k: without_annotations(v) for k, v in value.items() if k not in NEW_FIELDS}
    if isinstance(value, list):
        return [without_annotations(v) for v in value]
    return value


def stamp(value):
    return datetime.fromtimestamp(value, ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")


def verify(payload, baseline, rows):
    assert payload["directions"] and baseline["directions"] == without_annotations(payload["directions"])
    bars = {}
    for row in rows:
        time = int(row["time"])//30*30
        bar = bars.setdefault(time, {"time": time, "open": row["open"], "high": row["high"],
                                     "low": row["low"], "close": row["close"]})
        bar.update(high=max(bar["high"], row["high"]), low=min(bar["low"], row["low"]), close=row["close"])
    times = sorted(bars)
    group = payload["directions"]["bullish"]
    expected = [
        ("StopAll", 1, "2026-10-14 08:03:00", "2026-10-14 08:59:30"),
        ("StopAll", 2, "2026-10-14 09:01:00", "2026-10-14 09:19:30"),
        ("StopAll", 4, "2026-10-14 11:42:00", "2026-10-14 12:09:30"),
        ("PL", 1, "2026-10-15 05:28:30", "2026-10-15 06:33:30"),
        ("StopAll", 4, "2026-10-16 01:44:00", "2026-10-16 03:00:30"),
        ("StopAll", 7, "2026-10-16 05:54:30", "2026-10-16 06:40:00"),
    ]
    matched = []
    for kind, number, source, entry in expected:
        found = [r for r in group["positionSetups"] if r["anchorKind"] == kind
                 and r["anchorNumber"] == number and stamp(r["anchorSourceTime"]) == source]
        assert len(found) == 1, (kind, number, source, found)
        record, = found
        assert stamp(record["entryTime"]) == entry, record
        assert Decimal(record["entryPrice"]) == bars[record["entryTime"]]["close"]
        assert Decimal(record["stopPrice"]) == bars[record["anchorSourceTime"]]["low"]
        matched.append({"anchor": f"{kind}-{number}", "source": source, "entry": entry,
                        "entryPrice": record["entryPrice"], "stopPrice": record["stopPrice"]})
    root, = [r for r in group["stopAllAssessments"] if stamp(r["sourceTime"]) == "2026-10-14 08:03:00"]
    assert root["referenceHigh"] == "95.388"
    assert stamp(times[root["referenceSourceIndex"]]) == "2026-10-14 05:12:30"
    ignored, = [r for r in group["stopAllAssessments"] if stamp(r["sourceTime"]) == "2026-10-15 22:50:30"]
    assert ignored["ignoredPrefix"]
    setups = group["positionSetups"]
    assert len({r["id"] for r in setups}) == len(setups)
    cycles = {r["id"] for r in group["primaryCycles"]}
    for row in setups:
        entry, stop, target = map(Decimal, (row["entryPrice"], row["stopPrice"], row["targetPrice"]))
        assert entry > stop and target-entry == 4*(entry-stop)
        assert row["widthBars"] == 50 and row["riskReward"] == "4"
        assert row["entryTime"] == row["confirmationEventTime"]//30*30
        assert row["closeEventTime"] == row["entryTime"]+30
        assert row["anchorDecisionEventTime"] <= row["confirmationEventTime"]
        if row["behaviorKind"] is None:
            assert row["anchorKind"] == "StopAll" and row["anchorNumber"] == 2
        if row["cycleId"] is not None:
            assert row["cycleId"] in cycles, row
    report = {"status": "PASS", "legacyDirectionsEqual": True, "matchedAnchors": matched,
              "referenceHigh": root["referenceHigh"], "referenceCandle": "2026-10-14 05:12:30",
              "setupCount": len(setups), "assessmentCount": len(group["stopAllAssessments"]),
              "note": "S Blue source06:22:30 confirms06:33:30; entry uses the confirmation candle Close."}
    return report, bars


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, default=WORK/"final.json")
    parser.add_argument("--baseline", type=Path, default=WORK/"baseline.json")
    parser.add_argument("--make-browser-fixture", action="store_true")
    args = parser.parse_args()
    command = json.loads((WORK/"baseline-command.json").read_text())
    raw = Path(command[command.index("--data")+1])
    rows = json.loads(raw.read_text(), parse_float=Decimal)
    payload = json.loads(args.payload.read_text())
    report, bars = verify(payload, json.loads(args.baseline.read_text()), rows)
    report["rawSha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
    (WORK/"raw-verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if args.make_browser_fixture:
        window = [dict(row) for time, row in bars.items()
                  if "2026-10-14 07:00:00" <= stamp(time) <= "2026-10-14 14:45:00"]
        start, end = window[0]["time"], window[-1]["time"]
        group = dict(payload["directions"]["bullish"])
        for key, value in list(group.items()):
            if isinstance(value, list):
                group[key] = [r for r in value if isinstance(r, dict)
                              and start <= r.get("entryTime", r.get("sourceTime", r.get("firstTime", -1))) <= end]
        group.pop("calculationSegments", None)
        fixture = {**payload, "directions": {"bullish": group}, "actualFrom": start, "actualTo": end}
        (WORK/"browser-fixture.json").write_text(json.dumps({"rows": window, "payload": fixture},
            default=lambda v: float(v) if isinstance(v, Decimal) else v), encoding="utf-8")
