from dataclasses import replace
from decimal import Decimal
from types import SimpleNamespace

import pytest

from test_live_reaction_continuation import bars
from a_zone_detector import AZoneDetector, LiveAZoneContinuation, detect_a_zones
from reaction_engine import MarketChronology, mirror_candle


def stage_inputs(direction, route):
    candles = bars([
        ("10", "11", low, "10")
        for low in ("9", "9", "9", "9", "7", "8", "8", "9", "9", "9")
    ])
    sign = 1 if direction == "bullish" else -1
    if sign == -1:
        candles = list(map(mirror_candle, candles))
    reactions = [
        SimpleNamespace(
            first_idx=first, break_idx=last,
            box_top=Decimal("10"), box_bottom=Decimal("-10"),
        )
        for first, last in ((0, 1), (2, 3), (5, 6), (7, 8))
    ]

    def blue(kind, ordinal, source, level, *, valid=True):
        return SimpleNamespace(
            kind=kind, reaction_number=ordinal, source_index=source,
            source_time=candles[source].timestamp, source_extreme=Decimal(level) * sign,
            broken_level=Decimal("9") * sign, calculation_valid=valid,
            behavior_internal=False,
        )

    first = blue("scale", 1, 0, "8")
    second = blue("scale", 2, 2, "8") if route == "ordinary" else blue(
        "reset", 2, 4, "7", valid=False,
    )
    return candles, reactions, [first, second, blue("scale", 4, 7, "8")]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("route", ["ordinary", "double-stop"])
def test_pending_a_continues_and_preserves_its_frozen_source(direction, route, monkeypatch):
    candles, reactions, blues = stage_inputs(direction, route)
    before = MarketChronology(candles[:5], candles[:5], 30)
    state = LiveAZoneContinuation(direction, reactions[:2], blues[:2], before)
    assert not state.result

    confirmed = MarketChronology(candles[:9], candles[:9], 30)
    expected = detect_a_zones(direction, reactions, blues, confirmed)
    assert len(expected) == 1 and expected[0].formation_route == route
    assert state.update(reactions, blues, confirmed, first_dirty_main=5) == expected
    previous = state.result[0]

    new = MarketChronology(candles, candles, 30)
    expected = detect_a_zones(direction, reactions, blues, new)
    original = AZoneDetector._a_source
    frozen_break = reactions[previous.reaction_number - 1].break_idx

    def check_source(detector, trigger, reaction):
        assert reaction.break_idx != frozen_break
        return original(detector, trigger, reaction)

    monkeypatch.setattr(AZoneDetector, "_a_source", check_source)
    assert state.update(reactions, blues, new, first_dirty_main=9) == expected
    assert state.result[0] is previous


def test_revised_lower_tail_withdraws_an_old_stop_and_a():
    candles, reactions, blues = stage_inputs("bullish", "ordinary")
    market = MarketChronology(candles, candles, 30)
    state = LiveAZoneContinuation("bullish", reactions, blues, market)
    assert len(state.result) == 1
    revised_lower = [*candles[:4], replace(candles[4], low=Decimal("8")), *candles[5:]]
    updated = MarketChronology(candles, revised_lower, 30)
    expected = detect_a_zones("bullish", reactions, blues, updated)
    assert not expected
    assert state.update(reactions, blues, updated, first_dirty_main=4) == expected


def test_open_lower_search_does_not_fall_back_to_new_mains_with_no_lower_rows():
    candles, reactions, blues = stage_inputs("bullish", "ordinary")
    before = MarketChronology(candles[:4], candles[:4], 30)
    state = LiveAZoneContinuation("bullish", reactions[:2], blues[:2], before)

    after = MarketChronology(candles[:7], candles[:4], 30)
    expected = detect_a_zones("bullish", reactions[:3], blues[:2], after)
    assert not expected
    assert state.update(reactions[:3], blues[:2], after, first_dirty_main=4) == expected


def test_first_appended_lower_rows_supersede_an_old_main_only_fallback():
    candles, reactions, blues = stage_inputs("bullish", "ordinary")
    before = MarketChronology(candles[:7], [], 30)
    state = LiveAZoneContinuation("bullish", reactions[:3], blues[:2], before)
    assert len(state.result) == 1

    after = MarketChronology(candles, candles[8:], 30)
    expected = detect_a_zones("bullish", reactions, blues, after)
    assert not expected
    assert state.update(reactions, blues, after, first_dirty_main=7) == expected
