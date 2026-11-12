from dataclasses import replace
from decimal import Decimal

from test_bullish_setup_engine import Market
from bullish_setup_engine import LiveBullishSetupContinuation, calculate_bullish_setups
from reaction_engine import MarketChronology


def inputs(market):
    lower = list(market.rows)
    main = []
    for index in range(len(lower) // 6):
        rows = lower[index * 6:(index + 1) * 6]
        main.append(replace(
            rows[0], index=index, high=max(row.high for row in rows),
            low=min(row.low for row in rows), close=rows[-1].close,
        ))
    return MarketChronology(main, lower, 30), market.s, market.e, market.stops, market.pl


def batch(market, through):
    return calculate_bullish_setups(*inputs(market), through_index=through)


def test_live_setup_keeps_reference_break_open_and_updates_old_parity_statuses():
    market = Market(count=30)
    market.primary(2, 1, 2)
    market.high(4, "120")
    market.stopall(1, 3, 5, stop=9)
    market.behavior(6, 7)
    market.stopall(2, 10, 11, stop=15, price="99")
    market.behavior(12, 13, kind="E", color="red")
    market.high(16, "120")
    market.high(18, "120.001", 5)

    live = LiveBullishSetupContinuation(*inputs(market), through_index=14)
    first = live.result
    assert first == batch(market, 14)
    assert first.assessments[1].status is None
    after_stop = live.update(*inputs(market), first_dirty_event=market.time(15), through_index=17)
    assert after_stop == batch(market, 17)
    assert [row.status for row in after_stop.assessments] == ["F", "F"]
    assert first.assessments[1].status is None
    assert not after_stop.breakouts
    final = live.update(*inputs(market), first_dirty_event=market.time(18), through_index=20)
    assert final == batch(market, 20)
    assert final.breakouts[0].reference_high == Decimal("120")
    assert final.breakouts[0].event_time == market.time(18, 5)


def test_live_pl_stop_and_earlier_behavior_revision_rewind_only_affected_results():
    market = Market(count=30)
    market.primary(1, 1, 2)
    market.behavior(3, 5)
    market.low(4, "89.9", 5)
    live = LiveBullishSetupContinuation(*inputs(market), through_index=3)
    assert not live.result.setups
    stopped = live.update(*inputs(market), first_dirty_event=market.time(4), through_index=7)
    assert stopped == batch(market, 7)
    assert not stopped.setups

    # Correction removes the old stop and makes the original setup eligible.
    market.low(4, "90", 5)
    entered = live.update(*inputs(market), first_dirty_event=market.time(4, 5), through_index=7)
    assert entered == batch(market, 7)
    assert entered.setups[0].entry_index == 5

    # Removing an upstream event earlier than the next market append still
    # withdraws its setup while retaining the accepted PL anchor.
    market.s.clear()
    revised = live.update(*inputs(market), first_dirty_event=market.time(8), through_index=8)
    assert revised == batch(market, 8)
    assert not revised.setups
