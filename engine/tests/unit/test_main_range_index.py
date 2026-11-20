"""Main-candle range indexes retain exact winning Decimal and Candle identity."""
from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from reaction_engine import (
    Candle, DetectorBase, MarketChronology, BearishDetector, LiveReactionContinuation,
    LowerTimeframeIndex, _LOWER_TIMEFRAME_INDEXES,
)


def candles():
    values = ("-0.00", "0.000", "2.00", "2.0", "-3.00", "-3.0")
    return [Candle(i, datetime(2026, 1, 1) + timedelta(seconds=i * 30), str(i), "GREEN",
                   Decimal("0"), Decimal(values[i % 6]) + 4, Decimal(values[i % 6]), Decimal("0"))
            for i in range(90)]


@pytest.mark.parametrize("attribute,method", (("low", "minimum_low"), ("high", "maximum_high")))
def test_all_main_ranges_keep_earliest_extreme_identity_and_decimal_tuple(attribute, method):
    rows = candles()
    detector = DetectorBase(rows, rows, 0, len(rows) - 1)
    for left in range(len(rows)):
        for right in range(left, len(rows)):
            expected = rows[left]
            for item in rows[left + 1:right + 1]:
                if (getattr(item, attribute) < getattr(expected, attribute) if attribute == "low"
                        else getattr(item, attribute) > getattr(expected, attribute)):
                    expected = item
            value, owner = getattr(detector, method)(left, right)
            assert owner is expected
            assert value.as_tuple() == getattr(expected, attribute).as_tuple()


def test_reversed_legacy_range_keeps_start_owner():
    rows = candles()
    detector = DetectorBase(rows, rows, 0, len(rows) - 1)
    assert detector.minimum_low(12, 10)[1] is rows[12]
    assert detector.maximum_high(12, 10)[1] is rows[12]


def test_immutable_e_indexes_are_scoped_to_each_chronology():
    rows = candles()
    first, second = MarketChronology(rows, rows, 30), MarketChronology(rows, rows, 30)
    assert first._e_main_extremes == second._e_main_extremes == {}
    assert first._e_main_extremes is not second._e_main_extremes


def test_reflected_main_queries_share_original_index_and_release_with_source():
    rows = candles()
    detector = BearishDetector(rows, rows, 0, len(rows) - 1).reference
    for method, attribute in (("minimum_low", "low"), ("maximum_high", "high")):
        value, owner = getattr(detector, method)(0, len(rows) - 1)
        key = lambda item: getattr(item, attribute)
        expected = (min if attribute == "low" else max)(detector.candles, key=key)
        assert owner is expected and value.as_tuple() == key(expected).as_tuple()
    assert id(detector.candles) not in _LOWER_TIMEFRAME_INDEXES
    LiveReactionContinuation._release_indexes(rows)
    assert id(rows) not in _LOWER_TIMEFRAME_INDEXES


@pytest.mark.parametrize("retain_crossings", (False, True))
def test_refreshed_index_retains_strict_crossings_and_earliest_extrema(retain_crossings):
    rows = candles()
    history = rows[:10]
    index = LowerTimeframeIndex(history, retain_crossings=retain_crossings)
    assert index.first_less(0, 10, Decimal("-9")) is None
    assert index.first_greater(0, 10, Decimal("5")) == 2
    original_prefix = history[:9]
    history[9:] = [replace(rows[9], low=Decimal("-10.00")), *rows[10:16]]
    index.refresh_suffix(9)
    assert all(actual is expected for actual, expected in zip(history, original_prefix))
    assert index.times == [row.timestamp for row in history]
    assert index.first_less(0, 16, Decimal("-9")) == 9
    assert index.first_less(0, 9, Decimal("-9")) is None
    for left in range(-1, len(history) + 1):
        for right in range(left, len(history) + 2):
            positions = range(max(0, left), min(len(history), right))
            for level in map(Decimal, ("-10.00", "-3.0", "0", "2.00", "5", "6")):
                assert index.first_less(left, right, level) == next(
                    (position for position in positions if history[position].low < level), None,
                )
                assert index.first_greater(left, right, level) == next(
                    (position for position in positions if history[position].high > level), None,
                )
            if 0 <= left < right <= len(history):
                expected = min(positions, key=lambda position: history[position].low)
                value, owner = index.range_minimum(left, right)
                assert owner == expected and value.as_tuple() == history[expected].low.as_tuple()
