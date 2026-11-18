"""Exact range-query equivalence for the behavior-preserving stage refactor."""

from bisect import bisect_right
from datetime import datetime, timedelta
from decimal import Decimal, localcontext
from itertools import combinations_with_replacement, product
from types import SimpleNamespace

import pytest

from test_live_reaction_continuation import bars
from a_zone_detector import AZoneDetector
from reaction_engine import MarketChronology


BASE = datetime(2026, 1, 1)


def range_detector(direction, values, *, indexed=True):
    mains = bars([("0", "11", "-11", "0")] * 4)
    lower = [
        SimpleNamespace(
            index=index, timestamp=BASE + timedelta(seconds=second),
            low=Decimal(value), high=Decimal(value),
        )
        for index, (second, value) in enumerate(zip((2, 17, 31, 69), values))
    ]
    chronology = MarketChronology(mains, lower, 30)
    if not indexed:
        chronology.lower_index = None
    return AZoneDetector(direction, [], [], chronology)


def scan_range(detector, start, end):
    """Independent linear oracle retaining the earliest equal owning row."""
    rows = [row for row in detector.lower if start <= row.timestamp <= end]
    choose = min if detector.direction == "bullish" else max
    attribute = "low" if detector.direction == "bullish" else "high"
    if rows:
        row = choose(rows, key=lambda item: getattr(item, attribute))
        source_index = detector.chronology.main_index(row.timestamp)
        return getattr(row, attribute), source_index, detector.candle_times[source_index]
    left = max(0, bisect_right(detector.candle_times, start) - 1)
    right = min(len(detector.candles) - 1,
                max(left, bisect_right(detector.candle_times, end) - 1))
    row = choose(detector.candles[left:right + 1],
                 key=lambda item: getattr(item, attribute))
    return getattr(row, attribute), row.index, row.timestamp


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
@pytest.mark.parametrize("indexed", (False, True))
def test_a_range_matches_scan_for_all_ties_and_irregular_boundary_windows(direction, indexed):
    # Every four-row combination includes signed zero, equal numeric values
    # with distinct representations, and strictly better/worse prices.
    lexemes = ("-0.00", "0", "1.000", "-1.00")
    boundaries = (0, 2, 3, 17, 18, 30, 31, 32, 69, 70, 119)
    for values in product(lexemes, repeat=4):
        detector = range_detector(direction, values, indexed=indexed)
        for first, last in combinations_with_replacement(boundaries, 2):
            start, end = (BASE + timedelta(seconds=value) for value in (first, last))
            expected = scan_range(detector, start, end)
            actual = detector._range_extreme(start, end)
            assert actual[1:] == expected[1:]
            assert actual[0].as_tuple() == expected[0].as_tuple()
            assert actual[0] is expected[0]


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_a_range_keeps_exact_long_decimal_at_inclusive_microsecond_end(direction):
    detector = range_detector(direction, (
        "1.123456789012345678901234567890123456789", "-0.000", "0", "-0.00",
    ))
    start = BASE + timedelta(seconds=2)
    end = BASE + timedelta(seconds=17)
    with localcontext() as context:
        context.prec = 5
        for stop in (end - timedelta(microseconds=1), end, end + timedelta(microseconds=1)):
            expected = scan_range(detector, start, stop)
            actual = detector._range_extreme(start, stop)
            assert actual[1:] == expected[1:]
            assert actual[0].as_tuple() == expected[0].as_tuple()


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_a_range_falls_back_to_first_main_extreme_when_lower_is_empty(direction):
    detector = range_detector(direction, ())
    expected_price = Decimal("-11" if direction == "bullish" else "11")
    assert detector._range_extreme(BASE, BASE + timedelta(seconds=119)) == (
        expected_price, 0, BASE,
    )


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_a_range_reuses_the_existing_index_without_materializing_lower_windows(direction):
    detector = range_detector(direction, ("1.000", "-1.00", "-1.0", "1"))

    class IndexOnlyRows(list):
        def __getitem__(self, key):
            if isinstance(key, slice):
                pytest.fail("An indexed A range allocated a lower-history window.")
            return super().__getitem__(key)

    # The immutable index has already been built over these exact rows.
    detector.lower = detector.chronology.seconds = IndexOnlyRows(detector.lower)
    expected = scan_range(detector, BASE, BASE + timedelta(seconds=119))
    actual = detector._range_extreme(BASE, BASE + timedelta(seconds=119))
    assert actual[1:] == expected[1:]
    assert actual[0].as_tuple() == expected[0].as_tuple()


def test_a_range_rejects_reversed_time_before_any_index_query():
    detector = range_detector("bullish", ("0",) * 4)
    with pytest.raises(ValueError, match="end precedes its start"):
        detector._range_extreme(BASE + timedelta(seconds=1), BASE)
