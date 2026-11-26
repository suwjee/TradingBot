from decimal import Decimal
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "bridge"))
from trading_pipeline import LiveMarketBuckets, build_candle_buckets


def row(time, opening, high, low, close):
    return dict(zip(("time", "open", "high", "low", "close"),
                    (time, *map(Decimal, (opening, high, low, close)))))


@pytest.mark.parametrize("timeframe", (1, 5, 30))
def test_each_suffix_matches_batch_and_preserves_settled_buckets(timeframe):
    rows = [
        row(60, "10.0", "11", "9", "10.0"),
        row(65, "10.00", "12", "8", "8"),
        row(65, "8.00", "13", "7", "13.00"),
        row(89, "13", "14", "12", "12.00"),
        row(90, "12", "15", "11", "13.000"),
        row(3600, "13", "16", "11", "16"),
    ]
    state = LiveMarketBuckets(timeframe)
    for index, candle in enumerate(rows, start=1):
        stable_seconds = tuple(state.second_buckets[:-1])
        stable_main = tuple(state.main_buckets[:-1])
        delta = state.append([candle])
        seconds, main = build_candle_buckets(rows[:index], timeframe)
        # repr also checks Decimal exponent and the identity of equal extrema.
        assert repr(state.second_buckets) == repr(seconds)
        assert repr(state.main_buckets) == repr(main)
        assert delta.settled_seconds == len(seconds) - 1
        assert delta.settled_main == len(main) - 1
        assert all(previous is state.second_buckets[i] for i, previous in enumerate(stable_seconds))
        assert all(previous is state.main_buckets[i] for i, previous in enumerate(stable_main))


def test_appending_inside_last_main_bucket_only_replaces_the_unsettled_bucket():
    state = LiveMarketBuckets(30)
    state.append([row(60, "10", "11", "8", "9"), row(90, "10", "13", "8", "12")])
    first, old_tail = state.main_buckets
    delta = state.append([row(115, "12", "15", "9", "9"), row(120, "9", "10", "8", "10")])
    assert (delta.first_dirty_second, delta.first_dirty_main) == (2, 1)
    assert state.main_buckets[0] is first
    assert old_tail["close"] == Decimal("12")
    assert state.main_buckets[1]["close"] == Decimal("9")
    assert delta.settled_main == 2


def test_rejecting_a_nonappend_batch_keeps_buckets_and_decimal_representation():
    state = LiveMarketBuckets(30)
    state.append([row(60, "10", "11", "8", "9")])
    before = repr(state.main_buckets), repr(state.second_buckets)
    with pytest.raises(ValueError, match="chronological"):
        state.append([row(65, "12.00", "13", "8", "12.00"), row(59, "9", "10", "8", "10")])
    assert (repr(state.main_buckets), repr(state.second_buckets)) == before
    state.append([row(90, "12.0", "13", "8", "12.0")])
    assert str(state.main_buckets[-1]["open"]) == "12.0"


def test_segment_index_keeps_exact_bounds_and_first_equal_price_across_offsets():
    from types import SimpleNamespace

    from reaction_engine import LowerTimeframeIndex
    from trading_pipeline import MarketIndexWindow

    lows = ("1", "6.00", "5.00", "5.0", "7", "1")
    highs = ("99", "9.0", "12.00", "12.0", "9", "99")
    candles = [SimpleNamespace(timestamp=i, low=Decimal(low), high=Decimal(high))
               for i, (low, high) in enumerate(zip(lows, highs))]
    base = LowerTimeframeIndex(candles, retain_crossings=True)
    middle = MarketIndexWindow(base, candles[1:5], 1, 5)
    nested = MarketIndexWindow(middle, candles[2:4], 1, 3)
    for window in (middle, nested):
        fresh = LowerTimeframeIndex(window.candles)
        assert window.times == fresh.times
        for left in range(-1, len(window.candles) + 1):
            for right in range(left, len(window.candles) + 2):
                for level in map(Decimal, ("5", "6", "12", "13")):
                    assert window.first_less(left, right, level) == fresh.first_less(left, right, level)
                    assert window.first_greater(left, right, level) == fresh.first_greater(left, right, level)
                for method in ("range_minimum", "range_maximum"):
                    query = getattr(window, method)
                    if 0 <= left < right <= len(window.candles):
                        assert repr(query(left, right)) == repr(getattr(fresh, method)(left, right))
                    else:
                        with pytest.raises(ValueError, match="Range contains no lower-timeframe candles"):
                            query(left, right)
