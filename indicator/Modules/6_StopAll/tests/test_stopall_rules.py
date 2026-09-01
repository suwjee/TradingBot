from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[4]
MODULES = ROOT / "indicator" / "Modules"


def load_bridge():
    path = ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"
    spec = importlib.util.spec_from_file_location("stopall_test_bridge", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_stopall():
    path = MODULES / "6_StopAll/app/stopall_detector.py"
    spec = importlib.util.spec_from_file_location("stopall_test_detector", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_strict_bullish_range(start, end):
    bridge = load_bridge()
    tz = ZoneInfo("Asia/Tehran")
    def epoch(value):
        return str(int(datetime.fromisoformat(value).replace(tzinfo=tz).timestamp()))
    paths = [("engine", "1_reaction-detector/app/Reaction-detection-new.py"),
             ("blue-engine", "2_blue-line/app/blue_line.py"),
             ("a-engine", "3_A-zone/app/a_detector.py"),
             ("s-engine", "4_S-zones/app/s_detector.py"),
             ("e-engine", "5_E-zones/app/e_detector.py"),
             ("stopall-engine", "6_StopAll/app/stopall_detector.py")]
    arguments = [part for flag, path in paths for part in ("--" + flag, str(MODULES / path))]
    arguments += ["--data", str(ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 to 2026-07-23 21-36-55 .json")),
        "--timeframe", "30", "--from-time", epoch(start), "--to-time", epoch(end), "--direction", "bullish"]
    previous, output = sys.argv, io.StringIO()
    try:
        sys.argv = ["reaction_bridge.py", *arguments]
        with redirect_stdout(output):
            assert bridge.main() == 0
    finally:
        sys.argv = previous
    return json.loads(output.getvalue())


def test_clarified_range_continues_after_stopall_with_exclusive_labels_and_order_causes():
    payload = run_strict_bullish_range("2026-07-13 13:09:30", "2026-07-17 11:43:00")
    group = payload["directions"]["bullish"]
    tz = ZoneInfo("Asia/Tehran")
    def stamp(value):
        return datetime.fromtimestamp(value, tz).strftime("%Y-%m-%d %H:%M:%S")
    e_by_time = {stamp(item["sourceTime"]): item for item in group["eZones"]}
    expected = {
        "2026-07-13 15:41:00": ("blue", 1, "73.622"),
        "2026-07-13 16:52:30": ("red", 1, "73.423"),
        "2026-07-14 06:06:00": ("red", 1, "78.914"),
        "2026-07-17 11:34:00": ("blue", 1, "79.217"),
    }
    for time, result in expected.items():
        zone = e_by_time[time]
        assert (zone["family"], zone["number"], zone["price"]) == result
    assert stamp(e_by_time["2026-07-17 11:34:00"]["decisionEventTime"]) == "2026-07-17 11:43:20"
    first = group["stopAlls"][0]
    assert (stamp(first["sourceTime"]), first["number"], first["stoppedBehaviorKey"],
            first["stoppedBehaviorCount"]) == ("2026-07-14 09:15:00", 1, "E1 red", 2)
    reset_sources = {item["sourceTime"] for item in group["stopAlls"]}
    for zone in group["eZones"]:
        if zone["parentType"] == "E":
            assert not any(zone["parentSourceTime"] < reset <= zone["sourceTime"] for reset in reset_sources)
    sources = [item["sourceTime"] for key in ("aZones", "sZones", "eZones", "stopAlls") for item in group[key]]
    assert len(sources) == len(set(sources))
    parent_causes = [cause for item in group["orderAudit"] for cause in item["causes"]
                     if cause["kind"] == "parent-stop"]
    assert any(cause["parentType"].startswith("StopAll") for cause in parent_causes)
    assert not any(cause["parentType"].startswith("E") and cause["parentSourceTime"] in reset_sources
                   for cause in parent_causes)
    repeated_reset = next(item for item in group["stopAlls"]
                          if stamp(item["sourceTime"]) == "2026-07-15 09:07:30")
    assert repeated_reset["orderCauses"] == ["parent-stop", "reset-leg"]
    assert repeated_reset["orderParentStopCauseTime"] is not None


def test_strict_range_real_order_ledger_is_deterministic_on_repeated_detect(monkeypatch):
    """Reusing the reconciled detector must not inherit its previous order ledger."""
    bridge = load_bridge()
    reconcile = bridge.reconcile_stopall_lifecycle
    captured = []

    def capture_reconciled_detector(*args, **kwargs):
        zones, stopalls = reconcile(*args, **kwargs)
        captured.append((args, zones, stopalls))
        return zones, stopalls

    # Observe the real pipeline without stubbing order discovery or audit writes.
    monkeypatch.setattr(bridge, "reconcile_stopall_lifecycle", capture_reconciled_detector)
    monkeypatch.setattr(sys.modules[__name__], "load_bridge", lambda: bridge)
    payload = run_strict_bullish_range("2026-07-13 13:09:30", "2026-07-17 11:43:00")
    assert len(captured) == 1
    args, zones, stopalls = captured[0]
    detector, stopall_engine, s_zones, _, candles, seconds, timeframe, direction = args
    assert detector.order_audit
    assert detector.sequence_resets
    assert bridge.epoch(candles[0].timestamp) == payload["actualFrom"]
    assert bridge.epoch(candles[-1].timestamp) == payload["actualTo"]

    def audit_snapshot():
        return bridge.serialize_order_audit(detector, 0, len(candles) - 1)

    expected_zones = bridge.serialize_e_zones(zones)
    expected_stopalls = bridge.serialize_stopalls(stopalls)
    expected_audit = audit_snapshot()
    assert expected_audit
    assert any(
        cause["kind"] == "parent-stop" and cause["parentType"].startswith("StopAll")
        for order in expected_audit for cause in order["causes"]
    )
    expected_resets = dict(detector.sequence_resets)
    expected_lifecycle_starts = set(detector.visual_lifecycle_starts)
    reset_sources = {item["sourceTime"] for item in expected_stopalls}
    assert [item for item in expected_zones if item["sourceTime"] not in reset_sources] == (
        payload["directions"]["bullish"]["eZones"]
    )
    assert expected_stopalls == payload["directions"]["bullish"]["stopAlls"]

    for _ in range(2):
        # Deliberately retain the nonempty real ledger before each detect call.
        assert detector.order_audit
        repeated_zones = detector.detect()
        assert bridge.serialize_e_zones(repeated_zones) == expected_zones
        assert audit_snapshot() == expected_audit
        assert detector.sequence_resets == expected_resets
        assert detector.visual_lifecycle_starts == expected_lifecycle_starts
        visible_s = bridge.visible_s_zones_after_module_resets(
            s_zones, repeated_zones, direction,
        )
        repeated_stopalls = stopall_engine.detect_stopalls(
            direction, visible_s, repeated_zones, candles, seconds, timeframe,
        )
        assert bridge.serialize_stopalls(repeated_stopalls) == expected_stopalls


def test_clarified_red_transition_requires_order_confirmation_inside_to():
    payload = run_strict_bullish_range("2026-07-13 13:09:30", "2026-07-13 17:03:30")
    group = payload["directions"]["bullish"]
    tz = ZoneInfo("Asia/Tehran")
    assert [datetime.fromtimestamp(item["sourceTime"], tz).strftime("%Y-%m-%d %H:%M:%S")
            for item in group["eZones"]] == ["2026-07-13 15:41:00"]
    assert group["stopAlls"] == []


def test_strict_stop_is_exact_directional_mirror():
    module = load_stopall()
    times = [datetime(2026, 1, 1, 0, 0, second) for second in (0, 30, 59)]
    candles = [
        SimpleNamespace(timestamp=times[0]),
        SimpleNamespace(timestamp=times[1]),
    ]

    bullish = module.StopAllDetector(
        "bullish", [], [], candles,
        [
            SimpleNamespace(timestamp=times[0], low=Decimal("10"), high=Decimal("10")),
            SimpleNamespace(timestamp=times[1], low=Decimal("9"), high=Decimal("10")),
            SimpleNamespace(timestamp=times[2], low=Decimal("8.99"), high=Decimal("10")),
        ],
        30,
    )
    bearish = module.StopAllDetector(
        "bearish", [], [], candles,
        [
            SimpleNamespace(timestamp=times[0], low=Decimal("10"), high=Decimal("10")),
            SimpleNamespace(timestamp=times[1], low=Decimal("10"), high=Decimal("11")),
            SimpleNamespace(timestamp=times[2], low=Decimal("10"), high=Decimal("11.01")),
        ],
        30,
    )

    assert bullish._strict_stop(times[0], Decimal("9"))[2] == times[2]
    assert bearish._strict_stop(times[0], Decimal("11"))[2] == times[2]


def test_red_e_family_always_dominates_blue_regardless_of_number():
    module = load_stopall()

    assert module.StopAllDetector._dominates_e(("red", 1), ("blue", 5))
    assert not module.StopAllDetector._dominates_e(("blue", 5), ("red", 1))
    assert module.StopAllDetector._dominates_e(("red", 2), ("red", 1))
    assert not module.StopAllDetector._dominates_e(("red", 1), ("red", 2))


def test_sequence_priority_is_red_first_then_behavior_type():
    module = load_stopall()

    priorities = module.StopAllDetector._SEQUENCE_PRIORITY
    assert priorities[("e", "red")] > priorities[("s", "red")]
    assert priorities[("s", "red")] > priorities[("e", "blue")]
    assert priorities[("e", "blue")] > priorities[("s", "blue")]


def test_stopall_preserves_authoritative_e_source_and_order_audit():
    module = load_stopall()
    stamp = datetime(2026, 1, 1, 12, 0, 0)
    reset = datetime(2026, 1, 1, 11, 55, 0)
    reset_break = datetime(2026, 1, 1, 11, 56, 0)
    e_zone = SimpleNamespace(
        source_index=7,
        source_time=stamp,
        price=Decimal("91.25"),
        decision_index=8,
        decision_time=stamp,
        decision_event_time=stamp,
        family="red",
        number=2,
        order_direction="bearish",
        order_reaction_number=4,
        order_mode="B",
        order_causes=("parent-stop", "reset-leg"),
        order_parent_stop_cause_time=reset,
        order_reset_leg_reset_time=reset,
        order_reset_leg_break_time=reset_break,
        order_first_index=5,
        order_first_time=reset,
        order_break_index=6,
        order_break_time=reset_break,
        order_confirmation_time=reset_break,
        order_box_top=Decimal("92"),
        order_box_top_source_index=5,
        order_box_top_source_time=reset,
        order_box_bottom=Decimal("90"),
        order_box_bottom_source_index=6,
        order_box_bottom_source_time=reset_break,
        order_stop_level=Decimal("92"),
        order_stop_source_index=5,
        order_stop_source_time=reset,
    )
    detector = module.StopAllDetector("bullish", [], [], [], [], 30)

    result = detector._stopall_from_e(
        e_zone, 1, "sequence-group-stop", reset_break,
        "E", "E1 red", 2,
    )

    assert (result.source_index, result.source_time, result.price) == (
        e_zone.source_index, e_zone.source_time, e_zone.price,
    )
    assert result.order_causes == ("parent-stop", "reset-leg")
    assert result.order_parent_stop_cause_time == reset
    assert result.order_reset_leg_reset_time == reset
    assert result.order_reset_leg_break_time == reset_break


def test_unbroken_dominant_e_blocks_a_lower_s_group():
    module = load_stopall()
    start = datetime(2026, 1, 1, 12, 0, 0)
    times = [start.replace(minute=minute) for minute in range(4)]
    gate = times[2].replace(second=10)
    decision = times[3].replace(second=20)
    candles = [SimpleNamespace(timestamp=value) for value in times]
    lower = [
        SimpleNamespace(timestamp=times[0], low=Decimal("100"), high=Decimal("110")),
        SimpleNamespace(timestamp=times[1], low=Decimal("105"), high=Decimal("110")),
        SimpleNamespace(timestamp=times[2], low=Decimal("104"), high=Decimal("110")),
        SimpleNamespace(timestamp=gate, low=Decimal("103"), high=Decimal("110")),
        SimpleNamespace(timestamp=times[3], low=Decimal("102"), high=Decimal("110")),
        SimpleNamespace(timestamp=decision, low=Decimal("101"), high=Decimal("110")),
    ]
    dominant_e = SimpleNamespace(
        source_index=0,
        source_time=times[0],
        decision_event_time=times[0],
        family="red",
        number=5,
        price=Decimal("90"),
    )
    s_zones = [
        SimpleNamespace(
            source_index=index,
            source_time=times[index],
            decision_event_time=times[index],
            color="red",
            price=Decimal(str(106 - index)),
        )
        for index in (1, 2)
    ]
    lower_e = SimpleNamespace(
        source_index=3,
        source_time=times[3],
        price=Decimal("101"),
        decision_index=3,
        decision_time=times[3],
        decision_event_time=decision,
        family="red",
        number=1,
        order_direction="bearish",
        order_reaction_number=1,
        order_mode="A",
        order_causes=("parent-stop",),
        order_parent_stop_cause_time=gate,
        order_reset_leg_reset_time=None,
        order_reset_leg_break_time=None,
        order_first_index=2,
        order_first_time=times[2],
        order_break_index=3,
        order_break_time=times[3],
        order_confirmation_time=times[3],
        order_box_top=Decimal("110"),
        order_box_top_source_index=2,
        order_box_top_source_time=times[2],
        order_box_bottom=Decimal("100"),
        order_box_bottom_source_index=3,
        order_box_bottom_source_time=times[3],
        order_stop_level=Decimal("110"),
        order_stop_source_index=2,
        order_stop_source_time=times[2],
    )

    result = module.detect_stopalls(
        "bullish", s_zones, [dominant_e, lower_e], candles, lower, 60
    )

    assert result == []


def test_stopped_red_s_group_claims_lower_priority_blue_e_order_in_both_directions():
    module = load_stopall()
    start = datetime(2026, 1, 1, 12, 0, 0)
    times = [start.replace(minute=minute) for minute in range(4)]
    gate = times[2].replace(second=10)
    decision = times[3].replace(second=20)
    candles = [SimpleNamespace(timestamp=value) for value in times]

    for direction in ("bullish", "bearish"):
        bullish = direction == "bullish"
        prices = (Decimal("100"), Decimal("99")) if bullish else (
            Decimal("100"), Decimal("101")
        )
        lower = [
            SimpleNamespace(
                timestamp=times[0], low=Decimal("100"), high=Decimal("100")
            ),
            SimpleNamespace(
                timestamp=times[1], low=Decimal("99"), high=Decimal("101")
            ),
            SimpleNamespace(
                timestamp=gate, low=Decimal("98"), high=Decimal("102")
            ),
            SimpleNamespace(
                timestamp=decision, low=Decimal("97"), high=Decimal("103")
            ),
        ]
        s_zones = [
            SimpleNamespace(
                source_index=index,
                source_time=times[index],
                decision_event_time=times[index],
                color="red",
                price=prices[index],
            )
            for index in range(2)
        ]
        confirming_e = SimpleNamespace(
            source_index=3,
            source_time=times[3],
            price=Decimal("97" if bullish else "103"),
            decision_index=3,
            decision_time=times[3],
            decision_event_time=decision,
            family="blue",
            number=2,
            order_direction="bearish" if bullish else "bullish",
            order_reaction_number=1,
            order_mode="A",
            order_causes=("parent-stop",),
            order_parent_stop_cause_time=gate,
            order_reset_leg_reset_time=None,
            order_reset_leg_break_time=None,
            order_first_index=2,
            order_first_time=times[2],
            order_break_index=3,
            order_break_time=times[3],
            order_confirmation_time=times[3],
            order_box_top=Decimal("103"),
            order_box_top_source_index=2,
            order_box_top_source_time=times[2],
            order_box_bottom=Decimal("97"),
            order_box_bottom_source_index=3,
            order_box_bottom_source_time=times[3],
            order_stop_level=Decimal("103" if bullish else "97"),
            order_stop_source_index=2,
            order_stop_source_time=times[2],
        )

        result = module.detect_stopalls(
            direction, s_zones, [confirming_e], candles, lower, 60
        )

        assert len(result) == 1
        assert (
            result[0].stopped_behavior_key,
            result[0].stopped_behavior_count,
            result[0].underlying_e_family,
            result[0].underlying_e_number,
            result[0].gate_event_time,
        ) == ("S red", 2, "blue", 2, gate)


def test_strict_range_fxcm_bullish_acceptance():
    bridge = load_bridge()
    data = ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    tehran = ZoneInfo("Asia/Tehran")

    def epoch(text: str) -> str:
        return str(int(datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
                       .replace(tzinfo=tehran).timestamp()))

    args = [
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--stopall-engine", str(MODULES / "6_StopAll/app/stopall_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", epoch("2026-07-13 13:09:30"),
        "--to-time", epoch("2026-07-15 10:23:00"),
        "--direction", "bullish",
    ]
    previous, output = sys.argv, io.StringIO()
    try:
        sys.argv = ["reaction_bridge.py", *args]
        with redirect_stdout(output):
            assert bridge.main() == 0
    finally:
        sys.argv = previous
    payload = json.loads(output.getvalue())
    group = payload["directions"]["bullish"]
    assert payload["stopAllVersion"] == "1.3.0"
    assert all("orderCauses" in item for item in group["stopAlls"])

    def stamp(value: int) -> str:
        return datetime.fromtimestamp(value, tehran).strftime("%Y-%m-%d %H:%M:%S")

    assert [
        (stamp(item["sourceTime"]), item["number"], item["stoppedBehaviorCount"])
        for item in group["stopAlls"]
    ] == [
        ("2026-07-14 09:15:00", 1, 2),
        ("2026-07-14 18:39:00", 2, 1),
        ("2026-07-15 08:25:30", 1, 3),
        ("2026-07-15 09:07:30", 2, 1),
    ]
    e_times = {stamp(item["sourceTime"]) for item in group["eZones"]}
    assert "2026-07-13 13:06:30" not in e_times
    assert [
        (stamp(item["sourceTime"]), item["number"], item["family"])
        for item in group["eZones"][:2]
    ] == [
        ("2026-07-13 15:41:00", 1, "blue"),
        ("2026-07-13 16:52:30", 1, "red"),
    ]
    assert not any(
        item["number"] == 5 and item["family"] == "red"
        for item in group["eZones"]
    )
    assert {stamp(item["sourceTime"]) for item in group["stopAlls"]}.isdisjoint(e_times)
    assert ("2026-07-14 06:06:00", 1, "red") in {
        (stamp(item["sourceTime"]), item["number"], item["family"])
        for item in group["eZones"]
    }
    red_transition = group["eZones"][1]
    assert red_transition["parentType"] == "S"
    assert stamp(red_transition["parentSourceTime"]) == "2026-07-13 14:37:00"
    assert stamp(red_transition["parentStopEventTime"]) == "2026-07-13 16:51:20"
    assert group["stopAlls"][0]["stoppedBehaviorKey"] == "E1 red"
    # All serialized source labels are exclusive, including StopAll vs S/A.
    sources = [item["sourceTime"] for key in ("aZones", "sZones", "eZones", "stopAlls")
               for item in group[key]]
    assert len(sources) == len(set(sources))


def test_full_file_dominant_e_blocks_early_s_and_preserves_stopall_lineage():
    bridge = load_bridge()
    data = ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    rows = json.loads(data.read_text(encoding="utf-8-sig"))
    from_time = int(rows[0]["time"]) // 30 * 30
    to_time = int(rows[-1]["time"]) // 30 * 30
    args = [
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--stopall-engine", str(MODULES / "6_StopAll/app/stopall_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", str(from_time), "--to-time", str(to_time),
        "--direction", "bullish",
    ]
    previous, output = sys.argv, io.StringIO()
    try:
        sys.argv = ["reaction_bridge.py", *args]
        with redirect_stdout(output):
            assert bridge.main() == 0
    finally:
        sys.argv = previous
    payload = json.loads(output.getvalue())
    stopalls = payload["directions"]["bullish"]["stopAlls"]
    tehran = ZoneInfo("Asia/Tehran")

    def stamp(value: int) -> str:
        return datetime.fromtimestamp(value, tehran).strftime("%Y-%m-%d %H:%M:%S")

    assert payload["stopAllVersion"] == "1.3.0"
    assert not any(
        stamp(item["sourceTime"]) == "2026-07-16 05:05:00"
        for item in stopalls
    )
    assert (
        stamp(stopalls[0]["sourceTime"]),
        stopalls[0]["number"],
        stopalls[0]["stoppedBehaviorKey"],
        stopalls[0]["stoppedBehaviorCount"],
        stamp(stopalls[0]["gateEventTime"]),
    ) == (
        "2026-07-16 12:37:30",
        1,
        "E5 red",
        3,
        "2026-07-16 12:34:10",
    )
    target = next(
        item for item in stopalls
        if stamp(item["sourceTime"]) == "2026-07-21 11:45:00"
    )
    assert (
        target["number"],
        target["stoppedBehaviorKey"],
        target["stoppedBehaviorCount"],
    ) == (4, "StopAll3", 1)
    assert not any(
        stamp(item["sourceTime"]) == "2026-07-21 11:45:00"
        for item in payload["directions"]["bullish"]["eZones"]
    )
    july_17_target = next(
        item for item in stopalls
        if stamp(item["sourceTime"]) == "2026-07-17 18:40:00"
    )
    assert (
        july_17_target["number"],
        july_17_target["stoppedBehaviorKey"],
        july_17_target["stoppedBehaviorCount"],
        stamp(july_17_target["gateEventTime"]),
        july_17_target["underlyingEFamily"],
        july_17_target["underlyingENumber"],
    ) == (1, "S red", 3, "2026-07-17 18:33:45", "red", 1)
    assert not any(
        stamp(item["sourceTime"]) == "2026-07-17 18:40:00"
        for item in payload["directions"]["bullish"]["eZones"]
    )
