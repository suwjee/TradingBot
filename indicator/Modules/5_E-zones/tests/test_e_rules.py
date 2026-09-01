from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import MethodType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[4]
MODULES = ROOT / "indicator" / "Modules"
ENGINE_PATH = MODULES / "5_E-zones" / "app" / "e_detector.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("e_rules_under_test", ENGINE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_bridge():
    path = ROOT / "indicator" / "indicator-settings" / "backend" / "reaction_bridge.py"
    spec = importlib.util.spec_from_file_location("reaction_bridge_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_bridge(arguments):
    bridge = load_bridge()
    previous = sys.argv
    output = io.StringIO()
    try:
        sys.argv = ["reaction_bridge.py", *arguments]
        with redirect_stdout(output):
            assert bridge.main() == 0
    finally:
        sys.argv = previous
    return json.loads(output.getvalue())


def make_candles(engine):
    base = datetime(2026, 7, 14, 5, 0)
    result = []
    for index in range(6):
        value = Decimal(10 - index)
        timestamp = base + timedelta(minutes=index)
        result.append(SimpleNamespace(
            index=index, timestamp=timestamp,
            display_time=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            tag="GREEN", open=value, high=value + 1, low=value, close=value,
        ))
    return result


def test_order_b_gate_preserves_reset_context_in_both_directions():
    path = MODULES / "1_reaction-detector/app/Reaction-detection-new.py"
    spec = importlib.util.spec_from_file_location("reaction_gate_rules", path)
    assert spec is not None and spec.loader is not None
    reaction_engine = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = reaction_engine
    spec.loader.exec_module(reaction_engine)
    base = datetime(2026, 7, 14, 10, 0)

    def candle(index, tag, high, low):
        timestamp = base + timedelta(seconds=index * 60)
        return reaction_engine.Candle(
            index=index,
            timestamp=timestamp,
            display_time=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            tag=tag,
            open=Decimal(str(low)),
            high=Decimal(str(high)),
            low=Decimal(str(low)),
            close=Decimal(str(high)),
        )

    def selected(direction):
        first_tag = "GREEN" if direction == "bearish" else "RED"
        context_tag = "RED" if direction == "bearish" else "GREEN"
        main = [
            candle(0, context_tag, 7, 3),
            candle(1, context_tag, 7, 3),
            candle(2, first_tag, 7, 3),
            candle(3, first_tag, 8 if direction == "bullish" else 7,
                   2 if direction == "bearish" else 3),
        ]
        detector = reaction_engine.UnifiedReactionDetector(
            main, [], 0, len(main) - 1, direction
        )
        candidate = reaction_engine.Candidate(
            first_idx=2, first_time=main[2].display_time,
            box_top_source_idx=2, box_top_source_time=main[2].display_time,
            box_top=Decimal("7"),
            box_bottom_source_idx=2,
            box_bottom_source_time=main[2].display_time,
            box_bottom=Decimal("3"),
            mode="A",
        )
        detector._build_direct_candidate = MethodType(
            lambda _self, _direction, _reset, first: (
                candidate if first == 2 else None
            ),
            detector,
        )
        return detector.first_simple_geometry_after_gate(
            direction, 0, 2, 3
        )

    bearish = selected("bearish")
    bullish = selected("bullish")
    assert (bearish.first_idx, bearish.break_idx) == (2, 3)
    assert (bullish.first_idx, bullish.break_idx) == (2, 3)


def test_order_b_waits_for_active_canonical_owner_then_restarts_in_both_directions():
    """A healthy canonical opposite Reaction owns the leg until its Reset."""
    engine = load_engine()
    base = datetime(2026, 7, 16, 17, 0)
    candles = []
    for index in range(9):
        timestamp = base + timedelta(minutes=index)
        candles.append(SimpleNamespace(
            index=index, timestamp=timestamp,
            display_time=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            tag="GREEN", open=Decimal("10"), high=Decimal("11"),
            low=Decimal("9"), close=Decimal("10"),
        ))

    for direction in ("bullish", "bearish"):
        owner = reaction(1, 2, 8, 12)
        provisional = reaction(3, 4, 8, 12)
        replacement = reaction(6, 7, 8, 12)
        owner_reset = SimpleNamespace(
            from_first_idx=owner.first_idx,
            timestamp=candles[5].timestamp,
            display_time=candles[5].display_time,
            second_time=None,
        )

        def geometry_finder(_order_direction, start_index, _end_index):
            return provisional if start_index < 5 else replacement

        detector = engine.EDetector(
            direction, [], [owner, replacement], [], [], [owner_reset],
            candles, candles, 60, geometry_finder=geometry_finder,
        )
        number, selected, confirmation = detector._first_order_b_geometry(
            candles[0].timestamp, candles[3].timestamp, candles[8].timestamp,
        )
        assert number == 2
        assert selected is replacement
        assert confirmation == candles[7].timestamp


def test_order_b_keeps_pre_gate_owner_across_trend_reset_in_both_directions():
    """A trend-direction Reset cannot release an opposite Reaction owner."""
    engine = load_engine()
    base = datetime(2026, 7, 13, 9, 58)
    candles = []
    for index in range(6):
        timestamp = base + timedelta(minutes=index)
        candles.append(SimpleNamespace(
            index=index, timestamp=timestamp,
            display_time=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            tag="GREEN", open=Decimal("10"), high=Decimal("11"),
            low=Decimal("9"), close=Decimal("10"),
        ))

    for direction in ("bullish", "bearish"):
        owner = reaction(0, 1, 8, 12)
        provisional = reaction(3, 4, 8, 12)
        trend_reset = SimpleNamespace(
            from_first_idx=0, timestamp=candles[2].timestamp,
            display_time=candles[2].display_time, second_time=None,
        )
        detector = engine.EDetector(
            direction, [], [owner], [], [trend_reset], [], candles, candles, 60,
            geometry_finder=lambda _direction, _start, _end: provisional,
        )
        assert detector._first_order_b_geometry(
            candles[0].timestamp, candles[3].timestamp, candles[5].timestamp,
        ) is None


def reaction(first_idx, break_idx, bottom, top, anchor=None):
    return SimpleNamespace(
        first_idx=first_idx, break_idx=break_idx,
        box_bottom=Decimal(str(bottom)), box_top=Decimal(str(top)),
        box_bottom_source_idx=first_idx, box_top_source_idx=first_idx,
        mode="A",
        anchor_idx=first_idx if anchor is not None else None,
        anchor_value=Decimal(str(anchor)) if anchor is not None else None,
        leg_boundary_value=Decimal(str(anchor)) if anchor is not None else None,
    )


def test_parent_stop_is_strict():
    engine = load_engine()
    main = make_candles(engine)
    detector = engine.EDetector("bullish", [], [], [], [], [], main, main, 60)
    assert detector._first_parent_stop(main[2].timestamp, Decimal("8")) is not None
    assert detector._first_parent_stop(main[2].timestamp, Decimal("5")) is None


def test_order_stop_is_directional_mirror():
    engine = load_engine()
    main = make_candles(engine)
    bullish = engine.EDetector(
        "bullish", [], [reaction(2, 3, 8, 11, anchor=11)], [], [], [], main, main, 60
    )
    bearish = engine.EDetector(
        "bearish", [], [reaction(2, 3, 8, 11, anchor=8)], [], [], [], main, main, 60
    )
    assert bullish._order_stop(1, bullish.opposite_reactions[0])[0] == Decimal("11")
    assert bearish._order_stop(1, bearish.opposite_reactions[0])[0] == Decimal("8")


def test_reset_leg_boundary_is_inclusive_break_to_reset_exact_mirror():
    engine = load_engine()
    main = make_candles(engine)
    owner = reaction(0, 1, 8, 11, anchor=11)
    main[1].low, main[2].low, main[3].low = (
        Decimal("7"), Decimal("5"), Decimal("6")
    )
    main[1].high, main[2].high, main[3].high = (
        Decimal("12"), Decimal("15"), Decimal("14")
    )
    reset = SimpleNamespace(from_first_idx=0)
    bullish = engine.EDetector(
        "bullish", [], [owner], [], [], [], main, main, 60
    )
    bearish = engine.EDetector(
        "bearish", [], [owner], [], [], [], main, main, 60
    )
    assert bullish._reset_leg_geometry(reset, main[3].timestamp) == (
        main[1].timestamp, Decimal("5")
    )
    assert bearish._reset_leg_geometry(reset, main[3].timestamp) == (
        main[1].timestamp, Decimal("15")
    )


def test_e_requires_strict_order_stop_cross():
    engine = load_engine()
    main = make_candles(engine)
    lower = [SimpleNamespace(timestamp=main[1].timestamp, high=Decimal("9"), low=Decimal("7"))]
    bullish = engine.EDetector("bullish", [], [], [], [], [], main, lower, 60)
    bearish = engine.EDetector("bearish", [], [], [], [], [], main, lower, 60)
    # A Bearish order in Bullish E space stops strictly above its stop level.
    assert bullish._cross_order(main[1].timestamp, Decimal("9")) is None
    assert bullish._cross_order(main[1].timestamp, Decimal("8.9")) is not None
    # The Bearish chart mirror uses a Bullish order stopped strictly below.
    assert bearish._cross_order(main[1].timestamp, Decimal("7")) is None
    assert bearish._cross_order(main[1].timestamp, Decimal("7.1")) is not None


def test_order_cause_audit_preserves_direct_reset_and_carried_paths():
    engine = load_engine()
    main = make_candles(engine)
    direct = reaction(2, 3, 8, 11, anchor=11)
    detector = engine.EDetector(
        "bullish", [], [direct], [], [], [], main, main, 60
    )
    causes = detector._order_cause_evidence(
        direct, main[2].timestamp, selected_from_direct_search=True
    )
    assert causes == (("parent-stop",), main[2].timestamp, None, None)
    carried = detector._order_cause_evidence(
        direct, main[3].timestamp, selected_from_direct_search=False
    )
    assert carried == (("carried-live",), None, None, None)


def test_order_cause_audit_keeps_both_causes_without_duplicate_or_weight():
    engine = load_engine()
    main = make_candles(engine)
    selected = reaction(2, 3, 8, 11, anchor=11)
    detector = engine.EDetector(
        "bullish", [], [selected], [], [], [], main, main, 60
    )
    reset_time = main[1].timestamp
    break_time = main[2].timestamp
    detector._reset_leg_evidence = lambda item, start: (reset_time, break_time)
    causes = detector._order_cause_evidence(
        selected, main[2].timestamp, selected_from_direct_search=True
    )
    assert causes == (
        ("parent-stop", "reset-leg"),
        main[2].timestamp,
        reset_time,
        break_time,
    )
    # Multiple causes describe one Boolean-eligible order; they never create
    # multiple order objects or a stronger calculation result.
    assert len({(selected.first_idx, selected.break_idx) for _ in causes[0]}) == 1


def test_order_audit_requires_a_proven_cause_but_not_a_reaction_number():
    engine = load_engine()
    main = make_candles(engine)

    for direction in ("bullish", "bearish"):
        valid = reaction(2, 3, 8, 11, anchor=11)
        invalid = reaction(3, 4, 7, 10, anchor=10)
        detector = engine.EDetector(
            direction, [], [valid, invalid], [], [], [], main, main, 60
        )
        reset_time = main[1].timestamp
        boundary_break = main[2].timestamp
        stop_cross = (4, main[4].timestamp, main[4].timestamp)
        detector.order_candidates = lambda start, deadline=None: [
            (
                0, valid, main[3].timestamp, Decimal("11"), 2,
                main[2].timestamp, stop_cross, ("reset-leg",),
                None, reset_time, boundary_break,
            ),
            (
                2, invalid, main[4].timestamp, Decimal("10"), 3,
                main[3].timestamp, stop_cross, ("reset-leg",),
                None, reset_time, boundary_break,
            ),
        ]
        detector._legacy_reset_leg_evidence = lambda item, start: (
            (reset_time, boundary_break) if item is valid else None
        )
        detector._gate_owned_initial_order = lambda stop: None
        detector._carried_order_for_parent = lambda parent, stop: None
        parent = SimpleNamespace(
            source_time=main[0].timestamp, family="red", number=1,
        )

        detector._register_order_audit("E", parent, main[1].timestamp)

        assert (valid.first_idx, valid.break_idx) in detector.order_audit
        assert detector.order_audit[(valid.first_idx, valid.break_idx)][
            "reaction_number"
        ] == 0
        assert detector.order_audit[(valid.first_idx, valid.break_idx)][
            "causes"
        ] == {("reset-leg", reset_time, boundary_break)}
        assert (invalid.first_idx, invalid.break_idx) not in detector.order_audit

        owner = reaction(1, 2, 7, 12, anchor=12)
        owner_reset = SimpleNamespace(
            from_first_idx=owner.first_idx,
            display_time=main[3].display_time,
            second_time=None,
        )
        initial = {
            (owner.first_idx, owner.break_idx): {
                "reaction_number": 1,
                "reaction": owner,
                "confirmation_time": main[2].timestamp,
                "stop_level": Decimal("12"),
                "stop_source_index": 1,
                "stop_source_time": main[1].timestamp,
                "causes": {("parent-stop", "A", "", main[1].timestamp,
                            main[0].timestamp)},
            },
        }
        blocked = engine.EDetector(
            direction, [], [owner], [], [], [owner_reset], main, main, 60,
            initial_order_audit=initial,
        )
        blocked.order_candidates = lambda start, deadline=None: [
            (
                0, valid, main[4].timestamp, Decimal("11"), 2,
                main[2].timestamp, stop_cross, ("reset-leg",),
                None, reset_time, boundary_break,
            ),
        ]
        blocked._gate_owned_initial_order = lambda stop: None
        blocked._carried_order_for_parent = lambda parent, stop: None

        blocked._register_order_audit("E", parent, main[1].timestamp)

        assert (valid.first_idx, valid.break_idx) not in blocked.order_audit


def test_order_ledger_gate_and_carry_rules_are_directional_mirrors():
    engine = load_engine()
    main = make_candles(engine)
    owner = reaction(1, 2, 8, 11, anchor=11)
    initial = {
        (1, 2): {
            "reaction_number": 1,
            "reaction": owner,
            "confirmation_time": main[2].timestamp,
            "stop_level": Decimal("11"),
            "stop_source_index": 1,
            "stop_source_time": main[1].timestamp,
            "a_source_time": main[0].timestamp,
            "a_stop_event_time": main[1].timestamp,
        }
    }
    for direction in ("bullish", "bearish"):
        detector = engine.EDetector(
            direction, [], [owner], [], [], [], main, main, 60,
            initial_order_audit=initial,
        )
        detector._cross_order = MethodType(
            lambda self, start, level: (
                5, main[5].timestamp, main[5].timestamp
            ),
            detector,
        )
        gate = detector._gate_owned_initial_order(main[1].timestamp)
        assert gate is not None and gate[1] is owner
        blocked = SimpleNamespace(
            order_causes=("parent-stop",),
            parent_stop_event_time=main[1].timestamp,
            order_first_time=main[3].timestamp,
        )
        independent = SimpleNamespace(
            order_causes=("parent-stop", "reset-leg"),
            parent_stop_event_time=main[1].timestamp,
            order_first_time=main[3].timestamp,
        )
        assert detector._blocked_by_gate_owned_order(blocked)
        assert not detector._blocked_by_gate_owned_order(independent)

        detector.order_audit[(1, 2)] = {
            "reaction_number": 1,
            "reaction": owner,
            "confirmation_time": main[2].timestamp,
            "stop_level": Decimal("11"),
            "stop_source_index": 1,
            "stop_source_time": main[1].timestamp,
            "stop_cross": (5, main[5].timestamp, main[5].timestamp),
            "causes": {(
                "parent-stop", "S", "red", main[2].timestamp,
                main[1].timestamp,
            )},
        }
        parent = SimpleNamespace(decision_event_time=main[1].timestamp)
        carried = detector._carried_order_for_parent(
            parent, main[4].timestamp
        )
        assert carried is not None
        assert carried[7] == ("carried-live",)


def test_extreme_interval_uses_complete_parent_and_order_containing_candles():
    engine = load_engine()
    main = make_candles(engine)
    main[3].low = Decimal("5")
    lower = [
        SimpleNamespace(
            timestamp=main[1].timestamp + timedelta(seconds=30),
            low=Decimal("8"), high=Decimal("11"),
        ),
        SimpleNamespace(
            timestamp=main[3].timestamp + timedelta(seconds=30),
            low=Decimal("7"), high=Decimal("12"),
        ),
    ]
    bullish = engine.EDetector("bullish", [], [], [], [], [], main, lower, 60)
    index, timestamp, value = bullish._extreme_between(
        main[1].timestamp + timedelta(seconds=30),
        main[3].timestamp + timedelta(seconds=30),
    )
    assert index == 3
    assert timestamp == main[3].timestamp
    assert value == Decimal("5")

    main[2].high = Decimal("12")
    main[3].high = Decimal("15")
    bearish = engine.EDetector("bearish", [], [], [], [], [], main, lower, 60)
    index, timestamp, value = bearish._extreme_between(
        main[1].timestamp + timedelta(seconds=30),
        main[3].timestamp + timedelta(seconds=30),
    )
    assert index == 3
    assert timestamp == main[3].timestamp
    assert value == Decimal("15")


def test_post_e_s_requires_fresh_origin_and_unbroken_boundary_in_both_directions():
    bridge = load_bridge()
    base = datetime(2026, 7, 14, 5, 0)
    bullish_e = SimpleNamespace(source_time=base, price=Decimal("10"))
    bearish_e = SimpleNamespace(source_time=base, price=Decimal("10"))
    stale = SimpleNamespace(
        source_time=base + timedelta(minutes=2),
        a_source_time=base - timedelta(minutes=1),
        a_price=Decimal("11"), price=Decimal("11"),
    )
    bullish_broken = SimpleNamespace(
        source_time=base + timedelta(minutes=3), a_source_time=base + timedelta(minutes=1),
        a_price=Decimal("11"), price=Decimal("9"),
    )
    bullish_valid = SimpleNamespace(
        source_time=base + timedelta(minutes=4), a_source_time=base + timedelta(minutes=1),
        a_price=Decimal("11"), price=Decimal("10.5"),
    )
    bearish_broken = SimpleNamespace(
        source_time=base + timedelta(minutes=3), a_source_time=base + timedelta(minutes=1),
        a_price=Decimal("9"), price=Decimal("11"),
    )
    bearish_valid = SimpleNamespace(
        source_time=base + timedelta(minutes=4), a_source_time=base + timedelta(minutes=1),
        a_price=Decimal("9"), price=Decimal("9.5"),
    )
    assert bridge.visible_s_zones_after_module_resets(
        [stale, bullish_broken, bullish_valid], [bullish_e], "bullish"
    ) == [bullish_valid]
    assert bridge.visible_s_zones_after_module_resets(
        [stale, bearish_broken, bearish_valid], [bearish_e], "bearish"
    ) == [bearish_valid]


def test_fxcm_s_to_e_chain_reclassifies_invalid_a():
    """The verified 21:27/21:40 transition must be S -> E1 -> E2."""
    bridge = ROOT / "indicator" / "indicator-settings" / "backend" / "reaction_bridge.py"
    data = ROOT / "market-data" / "raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    paths = [
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", "1783703530", "--to-time", "1783708110",
        "--direction", "bullish",
    ]
    payload = run_bridge(paths)
    group = payload["directions"]["bullish"]
    assert (1783704630, "blue") in {
        (item["sourceTime"], item["color"]) for item in group["sZones"]
    }
    assert 1783707000 not in {item["sourceTime"] for item in group["sZones"]}
    assert [
        (item["number"], item["sourceTime"]) for item in group["eZones"]
    ] == [
        (1, 1783706250),
        (2, 1783707000),
    ]
    assert 1783704180 in {item["sourceTime"] for item in group["aZones"]}


def test_fxcm_confirmed_e_behavioral_reset_chain():
    """The real range must preserve reset-owned orders and E source labels."""
    bridge = ROOT / "indicator" / "indicator-settings" / "backend" / "reaction_bridge.py"
    data = ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    paths = [
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", "1783703550", "--to-time", "1783943820",
        "--direction", "bullish",
    ]
    group = run_bridge(paths)["directions"]["bullish"]
    from zoneinfo import ZoneInfo
    tehran = ZoneInfo("Asia/Tehran")
    def stamp(value):
        return datetime.fromtimestamp(value, tehran).strftime("%Y-%m-%d %H:%M:%S")
    assert [(item["number"], stamp(item["sourceTime"])) for item in group["eZones"]] == [
        (1, "2026-07-10 21:27:30"),
        (2, "2026-07-10 21:40:00"),
        (1, "2026-07-13 06:08:30"),
        (2, "2026-07-13 10:44:30"),
        (3, "2026-07-13 11:10:00"),
        (4, "2026-07-13 11:59:00"),
        (5, "2026-07-13 13:06:30"),
    ]
    assert [stamp(item["orderFirstTime"]) for item in group["eZones"]] == [
        "2026-07-10 21:23:30", "2026-07-10 21:50:00",
        "2026-07-13 06:05:30", "2026-07-13 10:33:00",
        "2026-07-13 11:08:00", "2026-07-13 11:58:30",
        "2026-07-13 13:01:00",
    ]
    assert stamp(group["eZones"][1]["orderStopSourceTime"]) == "2026-07-10 21:48:30"
    for item in group["eZones"]:
        assert item["orderCauses"]
        if "parent-stop" in item["orderCauses"]:
            assert item["orderParentStopCauseTime"] is not None
        if "reset-leg" in item["orderCauses"]:
            assert item["orderResetLegResetTime"] is not None
            assert item["orderResetLegBreakTime"] is not None
    forbidden_a = {
        "2026-07-13 10:01:00", "2026-07-13 10:44:30",
        "2026-07-13 11:10:00", "2026-07-13 11:39:30",
        "2026-07-13 11:59:00", "2026-07-13 12:48:00",
        "2026-07-13 12:53:30", "2026-07-13 13:06:30",
        "2026-07-13 14:37:00",
    }
    assert forbidden_a.isdisjoint({stamp(item["sourceTime"]) for item in group["aZones"]})
    assert ("2026-07-13 14:37:00", "red") in {
        (stamp(item["sourceTime"]), item["color"]) for item in group["sZones"]
    }
    forbidden_s = {
        "2026-07-13 09:51:30", "2026-07-13 11:33:00",
        "2026-07-13 11:43:00", "2026-07-13 12:48:00",
    }
    assert forbidden_s.isdisjoint({stamp(item["sourceTime"]) for item in group["sZones"]})


def test_fxcm_bullish_target_range_restarts_e_numbering_without_lookahead():
    """A strict slice rebuilds E from E1 and excludes post-TO decisions."""
    data = ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    paths = [
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", "1783921650", "--to-time", "1783935390",
        "--direction", "bullish",
    ]
    group = run_bridge(paths)["directions"]["bullish"]
    from zoneinfo import ZoneInfo
    tehran = ZoneInfo("Asia/Tehran")

    def stamp(value):
        return datetime.fromtimestamp(value, tehran).strftime("%Y-%m-%d %H:%M:%S")

    assert [
        (item["family"], item["number"], stamp(item["sourceTime"]),
         stamp(item["orderFirstTime"]))
        for item in group["eZones"]
    ] == [
        ("blue", 1, "2026-07-13 10:44:30", "2026-07-13 10:33:00"),
        ("blue", 2, "2026-07-13 11:10:00", "2026-07-13 11:08:00"),
        ("blue", 3, "2026-07-13 11:59:00", "2026-07-13 11:58:30"),
    ]
    assert "2026-07-13 13:06:30" not in {
        stamp(item["sourceTime"]) for item in group["eZones"]
    }
    assert "2026-07-13 12:53:30" not in {
        stamp(item["sourceTime"]) for item in group["eZones"]
    }

    bridge = load_bridge()
    engine_path = MODULES / "1_reaction-detector/app/Reaction-detection-new.py"
    spec = importlib.util.spec_from_file_location("target_reaction_engine", engine_path)
    assert spec is not None and spec.loader is not None
    reaction_engine = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = reaction_engine
    spec.loader.exec_module(reaction_engine)
    rows = json.loads(data.read_text(encoding="utf-8-sig"))
    seconds, candles = bridge.build_candle_views(reaction_engine, rows, 30)
    start = datetime(2026, 7, 13, 9, 17, 30)
    end = datetime(2026, 7, 13, 13, 6, 30)
    eligible = [
        index for index, candle in enumerate(candles)
        if start <= candle.timestamp <= end
    ]
    opposite = reaction_engine.UnifiedReactionDetector(
        candles, seconds, eligible[0], eligible[-1], "bearish"
    ).detect()
    modes = {
        candles[item.first_idx].timestamp.strftime("%Y-%m-%d %H:%M:%S"): item.mode
        for item in opposite.reactions
    }
    assert {time: modes[time] for time in [
        "2026-07-13 09:34:00", "2026-07-13 09:44:30",
        "2026-07-13 10:05:30", "2026-07-13 10:33:00",
        "2026-07-13 11:08:00", "2026-07-13 11:33:00",
        "2026-07-13 11:58:30", "2026-07-13 12:20:30",
        "2026-07-13 12:47:30", "2026-07-13 13:01:00",
    ]} == {
        "2026-07-13 09:34:00": "B",
        "2026-07-13 09:44:30": "A",
        "2026-07-13 10:05:30": "A",
        "2026-07-13 10:33:00": "A",
        "2026-07-13 11:08:00": "B",
        "2026-07-13 11:33:00": "B",
        "2026-07-13 11:58:30": "A",
        "2026-07-13 12:20:30": "B",
        "2026-07-13 12:47:30": "B",
        "2026-07-13 13:01:00": "A",
    }
    reset_firsts = {
        candles[item.from_first_idx].timestamp.strftime("%Y-%m-%d %H:%M:%S")
        for item in opposite.resets
    }
    assert "2026-07-13 12:23:30" in reset_firsts
    assert "2026-07-13 12:31:00" in modes

    e_engine = load_engine()
    trend = reaction_engine.UnifiedReactionDetector(
        candles, seconds, eligible[0], eligible[-1], "bullish"
    ).detect()
    detector = e_engine.EDetector(
        "bullish", trend.reactions, opposite.reactions, [],
        trend.resets, opposite.resets, candles, seconds, 30,
        eligible[0], eligible[-1],
    )
    expected_stops = {
        "2026-07-13 09:44:30": ("74.589", "2026-07-13 09:42:00"),
        "2026-07-13 10:05:30": ("74.339", "2026-07-13 10:04:30"),
        "2026-07-13 10:33:00": ("74.198", "2026-07-13 10:31:00"),
        "2026-07-13 11:08:00": ("74.072", "2026-07-13 11:05:00"),
        "2026-07-13 11:33:00": ("74.054", "2026-07-13 11:29:30"),
        "2026-07-13 11:58:30": ("73.469", "2026-07-13 11:56:30"),
        "2026-07-13 12:20:30": ("73.274", "2026-07-13 12:18:00"),
        "2026-07-13 13:01:00": ("72.898", "2026-07-13 13:00:00"),
    }
    serialized_orders = {
        stamp(item["firstTime"]): item for item in group["orderAudit"]
    }
    assert {
        "2026-07-13 12:47:30",
        "2026-07-13 13:02:00",
    }.isdisjoint(serialized_orders)
    assert set(expected_stops) <= set(serialized_orders)
    assert {
        time: (
            serialized_orders[time]["reactionMode"],
            serialized_orders[time]["stopLevel"],
            stamp(serialized_orders[time]["stopSourceTime"]),
        )
        for time in expected_stops
    } == {
        time: (modes[time], stop_level, stop_time)
        for time, (stop_level, stop_time) in expected_stops.items()
    }
    actual_stops = {}
    for number, item in enumerate(opposite.reactions, 1):
        first = candles[item.first_idx].timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if first not in expected_stops:
            continue
        level, _source_index, source_time = detector._order_stop(number, item)
        actual_stops[first] = (
            str(level), source_time.strftime("%Y-%m-%d %H:%M:%S")
        )
    assert actual_stops == expected_stops

    early_paths = paths.copy()
    early_paths[early_paths.index("--from-time") + 1] = "1783908000"
    early_paths[early_paths.index("--to-time") + 1] = "1783913400"
    early = run_bridge(early_paths)["directions"]["bullish"]
    early_orders = {stamp(item["firstTime"]) for item in early["orderAudit"]}
    assert {
        "2026-07-13 06:05:30", "2026-07-13 06:16:30",
        "2026-07-13 06:24:30",
    }.isdisjoint(early_orders)


def test_order_audit_excludes_ordinary_bearish_reactions():
    data = ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    from zoneinfo import ZoneInfo
    tehran = ZoneInfo("Asia/Tehran")
    value = lambda text: int(
        datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
        .replace(tzinfo=tehran).timestamp()
    )
    group = run_bridge([
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", str(value("2026-07-10 20:42:30")),
        "--to-time", str(value("2026-07-10 21:20:00")),
        "--direction", "bullish",
    ])["directions"]["bullish"]
    order_times = {
        datetime.fromtimestamp(item["firstTime"], tehran).strftime("%H:%M:%S")
        for item in group["orderAudit"]
    }
    assert order_times == {"21:09:00"}
    assert {"20:49:30", "20:53:30", "21:11:00"}.isdisjoint(order_times)


def test_fxcm_verified_colored_multi_chain_examples():
    """User-verified E families and greatest-stopped-number priority."""
    data = ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    paths = [
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", "1783703550", "--to-time", "1784050950",
        "--direction", "bullish",
    ]
    group = run_bridge(paths)["directions"]["bullish"]
    from zoneinfo import ZoneInfo
    tehran = ZoneInfo("Asia/Tehran")

    def stamp(value):
        return datetime.fromtimestamp(value, tehran).strftime("%Y-%m-%d %H:%M:%S")

    s_by_time = {
        stamp(item["sourceTime"]): item["color"] for item in group["sZones"]
    }
    assert s_by_time["2026-07-13 15:31:30"] == "blue"
    assert s_by_time["2026-07-14 00:17:00"] == "blue"
    assert s_by_time["2026-07-14 04:15:30"] == "blue"

    e_by_time = {
        stamp(item["sourceTime"]): (
            item["family"], item["number"], stamp(item["orderFirstTime"])
        )
        for item in group["eZones"]
    }
    assert e_by_time["2026-07-13 15:41:00"][:2] == ("blue", 1)
    assert e_by_time["2026-07-13 16:52:30"][:2] == ("red", 1)
    assert "2026-07-13 12:53:30" not in e_by_time
    expected = {
        "2026-07-14 04:30:00": ("blue", 1),
        "2026-07-14 06:06:00": ("red", 1),
        "2026-07-14 09:15:00": ("red", 2),
        "2026-07-14 11:57:30": ("red", 1),
        "2026-07-14 15:29:30": ("red", 2),
        "2026-07-14 17:38:00": ("red", 3),
        "2026-07-14 18:39:00": ("red", 4),
    }
    assert {
        time: e_by_time[time][:2] for time in expected
    } == expected
    assert e_by_time["2026-07-14 15:29:30"][2] == "2026-07-14 14:56:30"
    assert e_by_time["2026-07-14 17:16:00"][:2] == ("red", 1)
    assert e_by_time["2026-07-14 09:15:00"][2] == "2026-07-14 09:14:00"
    assert e_by_time["2026-07-14 11:57:30"][2] == "2026-07-14 11:51:00"
    assert e_by_time["2026-07-14 17:38:00"][2] == "2026-07-14 17:37:00"
    assert "2026-07-14 15:59:30" not in e_by_time


def test_fxcm_parent_s_color_priority_and_same_family_continuation():
    """Parent S owns color unless a stopped Red E continues at max(n)+1."""
    data = ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    from zoneinfo import ZoneInfo
    tehran = ZoneInfo("Asia/Tehran")

    def epoch(text):
        return str(int(
            datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
            .replace(tzinfo=tehran).timestamp()
        ))

    def stamp(value):
        return datetime.fromtimestamp(value, tehran).strftime("%Y-%m-%d %H:%M:%S")

    group = run_bridge([
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", epoch("2026-07-14 04:00:00"),
        "--to-time", epoch("2026-07-16 07:10:00"),
        "--direction", "bullish",
    ])["directions"]["bullish"]

    s_colors = {
        stamp(item["sourceTime"]): item["color"] for item in group["sZones"]
    }
    assert s_colors["2026-07-14 05:25:00"] == "red"
    assert s_colors["2026-07-15 14:11:00"] == "blue"
    assert s_colors["2026-07-16 06:30:00"] == "blue"

    e_labels = {
        stamp(item["sourceTime"]): (item["family"], item["number"])
        for item in group["eZones"]
    }
    assert e_labels["2026-07-14 06:06:00"] == ("red", 1)
    # The older Red S at 13:11:30 is the stopped parent. The intervening
    # Blue S at 14:11:00 cannot recolor that accepted parent or its child.
    assert e_labels["2026-07-15 15:16:00"] == ("red", 1)
    assert e_labels["2026-07-15 15:27:00"] == ("red", 2)
    assert e_labels["2026-07-16 05:26:30"] == ("red", 2)
    assert e_labels["2026-07-16 07:00:00"] == ("red", 3)


def test_fxcm_pending_s_cycle_and_completed_e_are_not_retroactively_removed():
    """A locked S race and a completed E survive unrelated later candidates."""
    data = ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    from zoneinfo import ZoneInfo
    tehran = ZoneInfo("Asia/Tehran")

    def epoch(text):
        return str(int(
            datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
            .replace(tzinfo=tehran).timestamp()
        ))

    def stamp(value):
        return datetime.fromtimestamp(value, tehran).strftime("%Y-%m-%d %H:%M:%S")

    group = run_bridge([
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", epoch("2026-07-16 10:30:00"),
        "--to-time", epoch("2026-07-16 17:50:00"),
        "--direction", "bullish",
    ])["directions"]["bullish"]

    s_by_source = {
        stamp(item["sourceTime"]): item for item in group["sZones"]
    }
    locked_s = s_by_source["2026-07-16 11:31:30"]
    assert locked_s["color"] == "red"
    assert stamp(locked_s["aSourceTime"]) == "2026-07-16 11:16:00"
    assert stamp(locked_s["orderFirstTime"]) == "2026-07-16 11:44:00"
    assert stamp(locked_s["decisionEventTime"]) == "2026-07-16 12:05:15"

    e_by_source = {
        stamp(item["sourceTime"]): item for item in group["eZones"]
    }
    assert (e_by_source["2026-07-16 17:14:00"]["family"],
            e_by_source["2026-07-16 17:14:00"]["number"]) == ("blue", 1)
    e2 = e_by_source["2026-07-16 17:36:00"]
    assert (e2["family"], e2["number"]) == ("blue", 2)
    assert stamp(e2["orderFirstTime"]) == "2026-07-16 17:35:00"


def test_fxcm_user_verified_orders_and_e_through_2026_07_15_221400():
    """Integrated Bullish 30-second acceptance range from the raw-file start."""
    data = ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    from zoneinfo import ZoneInfo
    tehran = ZoneInfo("Asia/Tehran")

    def epoch(text):
        return str(int(datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
                       .replace(tzinfo=tehran).timestamp()))

    def stamp(value):
        return datetime.fromtimestamp(value, tehran).strftime("%Y-%m-%d %H:%M:%S")

    group = run_bridge([
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", epoch("2026-07-10 20:42:10"),
        "--to-time", epoch("2026-07-15 22:14:00"),
        "--direction", "bullish",
    ])["directions"]["bullish"]

    orders = {stamp(item["firstTime"]) for item in group["orderAudit"]}
    required = {
        "2026-07-10 21:50:00",
        "2026-07-13 06:05:30", "2026-07-13 09:44:30",
        "2026-07-13 10:05:30",
        "2026-07-13 10:14:30", "2026-07-13 10:33:00",
        "2026-07-13 11:33:00", "2026-07-13 12:20:30",
        "2026-07-13 13:01:00", "2026-07-14 00:25:00",
        "2026-07-14 03:39:00", "2026-07-14 04:25:00",
        "2026-07-14 04:31:30", "2026-07-14 05:39:00",
        "2026-07-14 06:01:30", "2026-07-14 11:51:00",
        "2026-07-14 14:49:30", "2026-07-14 14:56:30",
        "2026-07-14 18:00:00", "2026-07-14 18:15:30",
        "2026-07-14 21:27:00", "2026-07-14 05:00:30",
        "2026-07-14 09:14:00", "2026-07-14 17:37:00",
        "2026-07-14 22:49:30", "2026-07-14 23:03:00",
        "2026-07-15 03:18:00", "2026-07-15 18:20:30",
    }
    forbidden = {
        "2026-07-10 21:44:00", "2026-07-13 10:01:00",
        "2026-07-13 12:47:30", "2026-07-13 13:02:00",
        "2026-07-13 06:24:30", "2026-07-14 05:58:30",
        "2026-07-14 15:19:00", "2026-07-14 18:55:30",
        "2026-07-14 21:41:00",
        "2026-07-14 04:58:30", "2026-07-14 17:15:30",
        "2026-07-14 17:43:30", "2026-07-14 17:58:00",
        "2026-07-14 22:57:30",
        "2026-07-15 03:04:30", "2026-07-15 03:38:00",
        "2026-07-15 07:39:00",
    }
    assert required <= orders
    assert forbidden.isdisjoint(orders)

    order_by_time = {
        stamp(item["firstTime"]): item for item in group["orderAudit"]
    }
    order_1220 = order_by_time["2026-07-13 12:20:30"]
    assert [cause["kind"] for cause in order_1220["causes"]] == [
        "parent-stop", "reset-leg",
    ]
    assert order_1220["causes"][0]["parentType"] == "E4"
    assert stamp(order_1220["causes"][0]["parentSourceTime"]) == (
        "2026-07-13 11:59:00"
    )
    assert stamp(order_by_time["2026-07-14 00:25:00"]["stopSourceTime"]) == (
        "2026-07-14 00:21:00"
    )
    order_1005 = order_by_time["2026-07-13 10:05:30"]
    assert order_1005["reactionNumber"] > 0
    assert [cause["kind"] for cause in order_1005["causes"]] == ["reset-leg"]
    assert stamp(order_1005["causes"][0]["resetTime"]) == (
        "2026-07-13 09:51:45"
    )
    assert stamp(order_1005["causes"][0]["boundaryBreakTime"]) == (
        "2026-07-13 10:00:50"
    )
    assert [
        cause["kind"]
        for cause in order_by_time["2026-07-14 18:00:00"]["causes"]
    ] == ["parent-stop", "reset-leg"]
    assert all(item["causes"] for item in group["orderAudit"])
    order_1820 = order_by_time["2026-07-15 18:20:30"]
    assert any(
        cause["kind"] == "reset-leg"
        and stamp(cause["resetTime"]) == "2026-07-15 18:09:00"
        and stamp(cause["boundaryBreakTime"]) == "2026-07-15 18:18:15"
        for cause in order_1820["causes"]
    )

    e_labels = {
        stamp(item["sourceTime"]): (item["family"], item["number"])
        for item in group["eZones"]
    }
    assert e_labels["2026-07-13 06:08:30"] == ("red", 1)
    assert e_labels["2026-07-13 13:06:30"] == ("red", 5)
    assert e_labels["2026-07-14 04:30:00"] == ("blue", 1)
    assert e_labels["2026-07-14 06:06:00"] == ("red", 1)
    assert "2026-07-14 17:16:00" not in e_labels
    assert e_labels["2026-07-14 17:38:00"] == ("red", 3)
    assert e_labels["2026-07-15 03:30:00"] == ("red", 1)

    e_by_time = {
        stamp(item["sourceTime"]): item for item in group["eZones"]
    }
    assert stamp(e_by_time["2026-07-14 09:15:00"]["orderFirstTime"]) == (
        "2026-07-14 09:14:00"
    )
    assert stamp(e_by_time["2026-07-14 11:57:30"]["orderFirstTime"]) == (
        "2026-07-14 11:51:00"
    )
    assert stamp(e_by_time["2026-07-14 17:38:00"]["orderFirstTime"]) == (
        "2026-07-14 17:37:00"
    )
    assert stamp(e_by_time["2026-07-14 22:54:00"]["orderFirstTime"]) == (
        "2026-07-14 22:49:30"
    )
    assert stamp(e_by_time["2026-07-15 03:30:00"]["orderFirstTime"]) == (
        "2026-07-15 03:18:00"
    )


def test_fxcm_full_file_order_b_active_owner_regression():
    """Full-file Bullish 30-second regression for canonical Order_B ownership."""
    data = ROOT / "market-data/raw" / (
        "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 "
        "to 2026-07-23 21-36-55 .json"
    )
    from zoneinfo import ZoneInfo
    tehran = ZoneInfo("Asia/Tehran")

    def epoch(text):
        return str(int(datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
                       .replace(tzinfo=tehran).timestamp()))

    def stamp(value):
        return datetime.fromtimestamp(value, tehran).strftime("%Y-%m-%d %H:%M:%S")

    group = run_bridge([
        "--engine", str(MODULES / "1_reaction-detector/app/Reaction-detection-new.py"),
        "--blue-engine", str(MODULES / "2_blue-line/app/blue_line.py"),
        "--a-engine", str(MODULES / "3_A-zone/app/a_detector.py"),
        "--s-engine", str(MODULES / "4_S-zones/app/s_detector.py"),
        "--e-engine", str(MODULES / "5_E-zones/app/e_detector.py"),
        "--data", str(data), "--timeframe", "30",
        "--from-time", epoch("2026-07-10 20:42:10"),
        "--to-time", epoch("2026-07-23 21:36:55"),
        "--direction", "bullish",
    ])["directions"]["bullish"]

    assert {
        key: len(group[key])
        for key in (
            "reactions", "resets", "blueLines", "aZones", "sZones",
            "eZones", "orderAudit",
        )
    } == {
        "reactions": 2107, "resets": 990, "blueLines": 1134,
        "aZones": 187, "sZones": 93, "eZones": 99, "orderAudit": 270,
    }
    orders = {stamp(item["firstTime"]): item for item in group["orderAudit"]}
    assert {
        "2026-07-16 17:16:00", "2026-07-17 22:58:00",
        "2026-07-20 23:21:30",
    } <= orders.keys()
    assert {
        "2026-07-15 07:39:00", "2026-07-16 17:14:00",
        "2026-07-16 20:46:30", "2026-07-17 08:06:30",
        "2026-07-17 08:31:30", "2026-07-17 22:59:30",
        "2026-07-20 23:20:30", "2026-07-22 14:21:00",
        "2026-07-16 09:00:30",
    }.isdisjoint(orders)
    assert all(item["causes"] for item in group["orderAudit"])
    assert [
        cause["kind"]
        for cause in orders["2026-07-20 23:21:30"]["causes"]
    ] == ["parent-stop", "reset-leg"]

    e_by_source = {stamp(item["sourceTime"]): item for item in group["eZones"]}
    first = e_by_source["2026-07-16 17:14:00"]
    assert (first["family"], first["number"], stamp(first["orderFirstTime"])) == (
        "blue", 1, "2026-07-16 17:16:00",
    )
    second = e_by_source["2026-07-16 17:36:00"]
    assert (second["family"], second["number"], stamp(second["orderFirstTime"])) == (
        "blue", 2, "2026-07-16 17:35:00",
    )
    later = e_by_source["2026-07-20 23:04:00"]
    assert stamp(later["orderFirstTime"]) == "2026-07-20 23:21:30"
    assert stamp(later["decisionEventTime"]) == "2026-07-20 23:47:55"
