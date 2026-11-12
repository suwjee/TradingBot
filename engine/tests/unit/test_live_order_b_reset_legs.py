from copy import copy

from test_order_b_reset_leg import scenario
import order_audit_engine as order


def test_live_order_b_reuses_the_boundary_and_extends_an_open_strict_crossing(monkeypatch):
    chronology, trend, resets, opposite, stops, formations = scenario()
    prefix = copy(chronology)
    prefix.seconds = chronology.seconds[:31]
    prefix.second_times = chronology.second_times[:31]
    anchor = order.OrderBBehaviorAnchor("A", 0, chronology.times[0], 0, 1)
    live = order.LiveOrderBResetLegs("bullish")
    assert live.update(
        prefix, trend, resets, opposite, stops, formations, behavior_anchors=[anchor],
        first_dirty_main=0,
    ) == []
    expected = order.discover_order_b_reset_legs(
        "bullish", chronology, trend, resets, opposite, stops, formations,
        behavior_anchors=[anchor],
    )
    assert expected

    def no_closed_boundary(*args):
        raise AssertionError("An unchanged historic leg boundary was recalculated")

    monkeypatch.setattr(order, "_order_b_boundary", no_closed_boundary)
    actual = live.update(
        chronology, trend, resets, opposite, stops, formations, behavior_anchors=[anchor],
        first_dirty_main=5,
    )
    assert actual == expected
    assert actual[0].strict_break_time == chronology.second_times[31]


def test_live_order_b_invalidates_a_revised_strict_crossing():
    chronology, trend, resets, opposite, stops, formations = scenario()
    anchor = order.OrderBBehaviorAnchor("A", 0, chronology.times[0], 0, 1)
    live = order.LiveOrderBResetLegs("bullish")
    assert live.update(
        chronology, trend, resets, opposite, stops, formations, behavior_anchors=[anchor],
        first_dirty_main=0,
    )
    revised, *_ = scenario(crossing_low="9")
    assert live.update(
        revised, trend, resets, opposite, stops, formations, behavior_anchors=[anchor],
        first_dirty_main=5,
    ) == []
