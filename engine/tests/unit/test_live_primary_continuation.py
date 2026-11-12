from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from test_pl_ph_detector import fixture, initial, order
from test_bullish_primary_mirror import mirror_values
import PL_PH_detector as primary
from reaction_engine import MarketChronology


class Orders:
    def __init__(self, market, kind, stops, *, forbidden=()):
        self.market = market
        self.kind = kind
        self.stops = stops
        self.forbidden = forbidden
        self.committed = []

    def __call__(self, kind, number, gate_index, event):
        assert gate_index not in self.forbidden, "A settled primary point was reselected"
        stop = self.stops.get(gate_index) if kind == self.kind else None
        return [] if stop is None else [order(self.market, gate_index, stop)]

    def confirm_high(self, point):
        self.committed.append(point)


@pytest.mark.parametrize("direction", ["bearish", "bullish"])
def test_resume_retains_first_point_and_registers_it_before_new_orders(direction):
    market, s, e, stops = fixture(initial({
        12: ("111", "90"), 13: ("120", "90"), 16: ("121", "90"),
        17: ("130", "90"), 20: ("131", "90"),
    }), size=22)
    kind = "PH" if direction == "bearish" else "PL"
    if direction == "bullish":
        market, s, e, stops = mirror_values((market, s, e, stops))
    prefix = MarketChronology(market.candles[:11], market.seconds[:11], 30)
    first = Orders(prefix, kind, {8: 10})
    session = primary.LivePrimaryContinuation(direction, prefix, s, e, stops, first)
    assert [point.number for point in first.committed] == [1]

    current = {8: 10, 12: 14, 16: 18}
    fresh = Orders(market, kind, current)
    batch = primary.detect_bearish if direction == "bearish" else primary.detect_bullish
    expected = batch(market, s, e, stops, fresh)
    resumed = Orders(market, kind, current, forbidden={8})
    actual = session.update(market, s, e, stops, resumed, first_dirty_event=market.times[11])
    assert actual == expected
    assert resumed.committed == fresh.committed
    assert resumed.committed[0] is first.committed[0]
    assert [point.number for point in resumed.committed] == [1, 2, 3]
    assert actual.transition.index == 20


def test_missing_seed_rewinds_before_the_reported_order_change():
    market, s, e, stops = fixture(initial())
    first = Orders(market, "PH", {8: 10})
    session = primary.LivePrimaryContinuation("bearish", market, s, e, stops, first)
    assert len(first.committed) == 1
    resumed = Orders(market, "PH", {8: 10}, forbidden={8})
    actual = session.update(market, s[:1], e, stops, resumed, first_dirty_event=market.times[20])
    assert actual == primary.detect_bearish(market, s[:1], e, stops, resumed)
    assert not resumed.committed
    assert not actual.highs


def test_new_candle_can_close_the_mbl_without_reselecting_the_old_high():
    market, s, e, stops = fixture(initial({13: ("99", "79")}))
    prefix = MarketChronology(market.candles[:11], market.seconds[:11], 30)
    session = primary.LivePrimaryContinuation(
        "bearish", prefix, s, e, stops, Orders(prefix, "PH", {8: 10}),
    )
    point = session.result.highs[0]
    assert session.result.mbl.stop_index is None
    resumed = Orders(market, "PH", {8: 10}, forbidden={8})
    actual = session.update(market, s, e, stops, resumed, first_dirty_event=market.times[11])
    assert actual == primary.detect_bearish(market, s, e, stops, Orders(market, "PH", {8: 10}))
    assert actual.highs[0] is point
    assert actual.mbl.price == Decimal("80")
    assert actual.mbl.stop_index == 13


def test_later_tick_in_stop_main_rewinds_its_primary_source():
    market, s, e, stops = fixture(initial(), size=11)
    session = primary.LivePrimaryContinuation(
        "bearish", market, s, e, stops, Orders(market, "PH", {8: 10}),
    )
    assert session.result.highs[0].source_index == 9
    candle = SimpleNamespace(**{**vars(market.candles[10]), "high": Decimal("111")})
    event_time = candle.timestamp + timedelta(seconds=5)
    tick = SimpleNamespace(**{**vars(candle), "timestamp": event_time})
    revised = MarketChronology(
        [*market.candles[:10], candle], [*market.seconds, tick], 30,
    )
    actual = session.update(
        revised, s, e, stops, Orders(revised, "PH", {8: 10}), first_dirty_event=event_time,
    )
    assert actual == primary.detect_bearish(revised, s, e, stops, Orders(revised, "PH", {8: 10}))
    assert actual.highs[0].source_index == 10
