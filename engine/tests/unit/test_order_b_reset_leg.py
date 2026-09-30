"""Focused contract tests for post-stop Order_B reset-leg discovery."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace


sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "engine" / "pipeline"))

from e_zone_detector import (
    EZoneDetector,
    PostBehaviorStop,
    discover_order_b_reset_legs,
    dominant_post_behavior_stops,
)
from lifecycle_engine import prepare_order_audit
from order_audit_engine import OrderBBehaviorAnchor


def scenario(*, crossing_low="8", opposite_first=6, a_cutoff=7, direction="bullish"):
    base = datetime(2026, 9, 27, 12, 0, 0)
    times = [base + timedelta(seconds=30 * index) for index in range(7)]
    candles = [
        SimpleNamespace(low=Decimal(value), high=Decimal("20"))
        for value in ("12", "11", "10", "9", "10", "10", "10")
    ]
    lower_times = [base + timedelta(seconds=5 * index) for index in range(42)]
    lower = [SimpleNamespace(low=Decimal("10"), high=Decimal("20")) for _ in lower_times]
    if direction == "bullish":
        lower[18].low = Decimal("12")
        lower[19].low = Decimal("12")
        lower[20].low = Decimal("10")
        lower[21].low = Decimal("9")
        for index in range(24, 28):
            lower[index].low = Decimal("12")
        lower[28].low = Decimal("10")
        lower[31].low = Decimal(crossing_low)
    else:
        for index, candle in enumerate(candles):
            candle.high = Decimal(("22", "24", "26", "31", "29", "29", "29")[index])
        lower[20].high = Decimal("31")
        for index in range(24, 28):
            lower[index].high = Decimal("29")
        lower[28].high = Decimal("31")
        lower[31].high = Decimal(crossing_low)
    previous = SimpleNamespace(first_idx=0, break_idx=1, confirmed_at=base + timedelta(seconds=35))
    current = SimpleNamespace(first_idx=4, break_idx=4, confirmed_at=base + timedelta(seconds=125))
    opposite = SimpleNamespace(
        first_idx=opposite_first,
        break_idx=opposite_first,
        confirmed_at=base + timedelta(seconds=195),
    )
    chronology = SimpleNamespace(
        candles=candles,
        seconds=lower,
        second_times=lower_times,
        lower_index=None,
        times=times,
        timeframe=timedelta(seconds=30),
        opposite_direction=lambda direction: "bearish" if direction == "bullish" else "bullish",
        reaction_confirmation=lambda _direction, reaction: reaction.confirmed_at,
        reset_time=lambda reset: reset.event_time,
    )
    stop = PostBehaviorStop("A", 0, base, base + timedelta(seconds=1))
    reset = SimpleNamespace(
        index=4, from_first_idx=4,
        broken_level=Decimal("11" if direction == "bullish" else "30"),
        second_time=None, event_time=base + timedelta(seconds=140),
    )
    formations = [base + timedelta(seconds=30 * a_cutoff)]
    return chronology, [previous, current], [reset], [opposite], [stop], formations


def discover(**kwargs):
    direction = kwargs.get("direction", "bullish")
    values = scenario(**kwargs)
    return discover_order_b_reset_legs(direction, *values, behavior_anchors=[
        OrderBBehaviorAnchor("A", 0, values[0].times[0], 0, 1),
    ])


def test_strict_lower_crossing_and_inclusive_leg_source():
    matches = discover()
    assert len(matches) == 1
    assert matches[0].reset_time == datetime(2026, 9, 27, 12, 2, 20)
    assert matches[0].leg_boundary == Decimal("9")
    assert matches[0].leg_source_index == 3
    assert matches[0].strict_break_time == datetime(2026, 9, 27, 12, 2, 35)


def test_equal_boundary_does_not_create_order():
    assert discover(crossing_low="9") == []


def test_opposite_first_candle_must_begin_at_or_after_break():
    assert discover(opposite_first=5) == []


def test_next_a_formation_expires_incomplete_candidate():
    assert discover(a_cutoff=5) == []


def test_bearish_direction_uses_strict_high_above_inclusive_ceiling():
    matches = discover(direction="bearish", crossing_low="32")
    bullish = discover()[0]
    assert len(matches) == 1
    assert matches[0].leg_boundary == Decimal("31")
    assert matches[0].leg_source_index == 3
    assert matches[0].strict_break_time == bullish.strict_break_time
    assert matches[0].physical_reaction.first_idx == bullish.physical_reaction.first_idx
    assert discover(direction="bearish", crossing_low="31") == []


def test_latest_accepted_behavior_is_anchor_independent_of_previous_reaction():
    chronology, same, resets, opposite, stops, formations = scenario()
    middle = SimpleNamespace(
        first_idx=1,
        break_idx=2,
        confirmed_at=datetime(2026, 9, 27, 12, 1, 5),
    )
    matches = discover_order_b_reset_legs(
        "bullish", chronology, [same[0], middle, same[1]], resets,
        opposite, stops, formations, behavior_anchors=[
            OrderBBehaviorAnchor("A", 0, chronology.times[0], 0, 1),
            OrderBBehaviorAnchor("S", 1, chronology.times[1], 1, 1),
        ],
    )
    assert len(matches) == 1
    assert matches[0].reset_reaction is same[1]
    assert matches[0].anchor_behavior_type == "S"
    assert matches[0].anchor_behavior_source_index == 1
    assert matches[0].leg_source_index == 3


def test_dominant_stop_owns_one_main_candle_transition():
    chronology, *_ = scenario()
    chronology.main_index = lambda event, clamp=True: max(
        0, min(len(chronology.times) - 1, int((event - chronology.times[0]).total_seconds() // 30))
    )
    a = SimpleNamespace(source_time=chronology.times[0], source_index=0, number=1, rank=0)
    e = SimpleNamespace(source_time=chronology.times[0], source_index=0, number=2, rank=4)
    stops = [
        ("A", a, chronology.times[1] + timedelta(seconds=20)),
        ("E", e, chronology.times[1] + timedelta(seconds=5)),
    ]
    result = dominant_post_behavior_stops(
        chronology, stops, lambda item: item.rank
    )
    assert len(result) == 1
    assert result[0].behavior_type == "E"
    assert result[0].event_time == datetime(2026, 9, 27, 12, 0, 35)


def test_open_higher_priority_behavior_blocks_lower_priority_stop():
    chronology, *_ = scenario()
    chronology.main_index = lambda event, clamp=True: max(
        0, min(len(chronology.times) - 1, int((event - chronology.times[0]).total_seconds() // 30))
    )
    a = SimpleNamespace(source_time=chronology.times[0], source_index=0, number=1, rank=0)
    e = SimpleNamespace(source_time=chronology.times[0], source_index=1, number=1, rank=4)
    result = dominant_post_behavior_stops(
        chronology,
        [("A", a, chronology.times[1]), ("E", e, None)],
        lambda item: item.rank,
    )
    assert result == []


def test_same_physical_identity_keeps_parent_and_all_reset_leg_causes():
    chronology, same, resets, opposite, stops, formations = scenario()
    resets.append(SimpleNamespace(
        index=4, from_first_idx=4, broken_level=Decimal("12"),
        second_time=None, event_time=datetime(2026, 9, 27, 12, 2, 20),
    ))
    legs = discover_order_b_reset_legs(
        "bullish", chronology, same, resets, opposite, stops, formations,
        behavior_anchors=[OrderBBehaviorAnchor("A", 0, chronology.times[0], 0, 1)],
    )
    assert len(legs) == 2
    assert legs[0].physical_reaction is legs[1].physical_reaction

    reaction = opposite[0]
    a_source = chronology.times[0]
    a_stop = chronology.times[0] + timedelta(seconds=1)
    first_entry = {
        "reaction": reaction,
        "reaction_number": 1,
        "confirmation_time": reaction.confirmed_at,
        "stop_level": Decimal("11"),
        "stop_source_index": 1,
        "stop_source_time": chronology.times[1],
        "stop_cross": None,
        "a_causes": [(a_source, a_stop)],
    }
    b_entry = {
        **first_entry,
        "causes": set(),
        "order_b_causes": [
            {
                "kind": "reset-leg", "resetTime": leg.reset_time,
                "resetBrokenLevel": str(leg.reset_broken_level),
            }
            for leg in legs
        ],
    }
    detector = SimpleNamespace(order_audit={(5, 5): b_entry})
    s_detector = SimpleNamespace(order_audit={(5, 5): first_entry})
    prepared = prepare_order_audit(
        detector, 0, 6, s_detector, {a_source}, set()
    )
    assert len(prepared) == 1
    assert [cause["kind"] for cause in prepared[0]["causes"]] == [
        "parent-stop", "reset-leg", "reset-leg",
    ]


def test_b_only_accepted_order_can_carry_into_next_parent_lifecycle():
    chronology, _same, _resets, opposite, _stops, _formations = scenario()
    base = chronology.times[0]
    reaction = opposite[0]
    fake = SimpleNamespace(
        order_audit={(5, 5): {
            "reaction": reaction,
            "reaction_number": 1,
            "confirmation_time": base + timedelta(seconds=145),
            "stop_level": Decimal("11"),
            "stop_source_index": 1,
            "stop_source_time": chronology.times[1],
            "stop_cross": (1, 1, base + timedelta(seconds=210)),
            "causes": set(),
            "order_b_causes": [{
                "physicalOrderConfirmationTime": base + timedelta(seconds=145),
            }],
        }},
        _initial_order_first_times=[],
        _initial_order_records=lambda: [],
        _carried_orders_cache={},
    )
    parent = SimpleNamespace(decision_event_time=base + timedelta(seconds=120))
    matches = EZoneDetector._carried_orders_for_parent(
        fake, parent, base + timedelta(seconds=180),
    )
    assert len(matches) == 1
    assert matches[0][1] is reaction
