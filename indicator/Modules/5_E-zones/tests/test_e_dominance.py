"""Isolated accepted-order inputs exercise E ownership, not Reaction discovery."""
from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from test_e_rules import load_engine


def scenario(direction, lows, s_specs, edges, resets=(), shift=0, dual_cause=False):
    engine = load_engine()
    base = datetime(2026, 1, 1) + timedelta(days=shift)
    mirror = lambda value: Decimal(value) if direction == "bullish" else Decimal(300) - Decimal(value)
    candles = []
    for index, low in enumerate(lows):
        first, second = mirror(low), mirror(Decimal(low) + 3)
        candles.append(SimpleNamespace(
            index=index, timestamp=base + timedelta(minutes=index),
            open=first, close=second, low=min(first, second), high=max(first, second),
        ))
    zones = [SimpleNamespace(
        source_index=index, source_time=candles[index].timestamp,
        decision_event_time=candles[index].timestamp + timedelta(seconds=30),
        a_source_time=candles[index].timestamp, price=mirror(price), color=family,
    ) for index, price, family in s_specs]
    detector = engine.EDetector(direction, [], [], zones, [], [], candles, candles, 60,
        sequence_resets={candles[index].timestamp: number for index, number in resets})

    def candidate(family, number, kind, parent, gate):
        index = edges.get((kind, parent.source_index))
        if index is None:
            return None
        time = candles[index].timestamp
        return engine.EZone(
            direction=direction, family=family, number=number, parent_type=kind,
            parent_source_index=parent.source_index, parent_source_time=parent.source_time,
            parent_price=parent.price, parent_stop_index=detector._main_index(gate),
            parent_stop_time=candles[detector._main_index(gate)].timestamp,
            parent_stop_event_time=gate, order_direction=detector.order_direction,
            order_reaction_number=1, order_mode="A",
            order_causes=("parent-stop", "reset-leg") if dual_cause else ("reset-leg",),
            order_parent_stop_cause_time=gate if dual_cause else None, order_reset_leg_reset_time=gate,
            order_reset_leg_break_time=gate, order_first_index=index,
            order_first_time=time, order_break_index=index, order_break_time=time,
            order_confirmation_time=time, order_box_top=candles[index].high,
            order_box_top_source_index=index, order_box_top_source_time=time,
            order_box_bottom=candles[index].low, order_box_bottom_source_index=index,
            order_box_bottom_source_time=time, order_stop_level=candles[index].high,
            order_stop_source_index=index, order_stop_source_time=time,
            source_index=index, source_time=time, price=mirror(lows[index]),
            decision_index=index, decision_time=time,
            decision_event_time=time + timedelta(seconds=30),
        )

    detector._zone = candidate
    detector._register_order_audit = lambda *args: None
    if dual_cause:
        detector._reset_evidence_for_order = lambda first, _break: (detector.times[first], detector.times[first])
    return detector


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("shift", [0, 53])
def test_older_single_red_s_owns_joint_stop_over_nested_blue_e(direction, shift):
    detector = scenario(direction, [100, 105, 104, 106, 99, 110],
        [(0, 100, "red"), (1, 105, "blue")],
        {("S", 0): 4, ("S", 1): 2, ("E", 2): 4}, shift=shift)
    zones = detector.detect()
    assert [(z.source_index, z.family, z.number) for z in zones] == [
        (2, "blue", 1), (4, "red", 1)]
    assert zones[-1].parent_type == "S"
    assert zones[-1].parent_source_index == 0
    assert zones[-1].parent_stop_event_time == detector.times[4]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_unstopped_red_s_does_not_recolor_nested_blue_e(direction):
    # Equality at the Red boundary stops only the Blue E, not the Red S.
    detector = scenario(direction, [100, 105, 104, 106, 100, 110],
        [(0, 100, "red"), (1, 105, "blue")],
        {("S", 0): 4, ("S", 1): 2, ("E", 2): 4})
    assert [(z.family, z.number) for z in detector.detect()] == [("blue", 1), ("blue", 2)]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("family", ["red", "blue"])
def test_e_owns_joint_stop_over_later_same_family_s(direction, family):
    detector = scenario(direction, [110, 111, 104, 106, 99, 112],
        [(0, 110, family), (3, 106, family)],
        {("S", 0): 2, ("S", 3): 4, ("E", 2): 4})
    zones = detector.detect()
    assert [(z.family, z.number) for z in zones] == [(family, 1), (family, 2)]
    assert zones[-1].parent_type == "E"
    assert zones[-1].parent_source_index == 2


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("dual_cause", [False, True])
def test_stopall_reset_preserves_order_child_but_restarts_e_numbering(direction, dual_cause):
    detector = scenario(direction, [110, 111, 108, 111, 106, 111, 104, 111, 102],
        [(0, 110, "blue")],
        {("S", 0): 2, ("E", 2): 4, ("E", 4): 6, ("E", 6): 8}, resets=[(4, 1)], dual_cause=dual_cause)
    zones = detector.detect()
    assert [(z.source_index, z.number) for z in zones] == [(2, 1), (4, 2), (6, 1), (8, 2)]
    assert zones[2].parent_type == "StopAll"
    assert zones[2].parent_source_index == 4
    if dual_cause:
        assert zones[2].order_causes == ("parent-stop", "reset-leg")
        assert zones[2].order_parent_stop_cause_time == detector.times[6]
    assert detector.detect() == zones
