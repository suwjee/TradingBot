"""A live inherited order closes only its own E-space eligibility window."""
from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from test_e_rules import load_engine


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_order_confirmation_is_bounded_by_the_inherited_decision(direction, offset):
    engine = load_engine()
    base = datetime(2025, 3, 8)
    candles = [SimpleNamespace(
        index=i, timestamp=base + timedelta(minutes=i),
        high=Decimal(12), low=Decimal(8),
    ) for i in range(6)]
    detector = engine.EDetector(direction, [], [], [], [], [], candles, candles, 60)
    deadline = base + timedelta(seconds=100)
    confirmation = deadline + timedelta(seconds=offset)
    reaction = SimpleNamespace(first_idx=1, break_idx=2)
    detector._first_healthy_direct_geometry = lambda start: (0, reaction, confirmation)
    detector._order_stop = lambda number, order: (Decimal(12), 0, base)
    detector._cross_order = lambda event, level: (4, candles[4].timestamp, candles[4].timestamp)

    bounded = detector.order_candidates(base, deadline)
    # The inherited decision closes the same lifecycle in either direction.
    assert bool(bounded) == (offset <= 0)
    # The cutoff is contextual. It must not poison cached geometry for a later search.
    assert detector.order_candidates(base)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("confirmation_offset", [-1, 0, 1])
def test_superseding_red_s_cannot_seed_orders_from_a_closed_blue_e(direction, confirmation_offset):
    engine = load_engine()
    base = datetime(2025, 3, 8)
    candles = [SimpleNamespace(
        index=i, timestamp=base + timedelta(minutes=i),
        high=Decimal(12), low=Decimal(8),
    ) for i in range(6)]
    gate = candles[4].timestamp
    red_s = SimpleNamespace(
        color="red", source_time=candles[2].timestamp, source_index=2,
        decision_event_time=gate + timedelta(seconds=confirmation_offset),
    )
    detector = engine.EDetector(direction, [], [], [red_s], [], [], candles, candles, 60)
    parent = SimpleNamespace(family="blue", source_time=base, decision_event_time=base)
    calls = []
    detector.order_candidates = lambda *args: calls.append(args) or []
    detector._register_order_audit("E", parent, gate)
    assert bool(calls) == (confirmation_offset >= 0)
    # A later S source is required; an older Red S does not supersede this E.
    red_s.source_time = base
    calls.clear()
    detector._register_order_audit("E", parent, gate)
    assert calls
