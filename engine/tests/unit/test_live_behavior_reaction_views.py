from dataclasses import replace
from decimal import Decimal

import pytest

from test_live_reaction_continuation import bars
import reaction_engine as engine


def candidate(candles, first, end, top, bottom):
    return engine.Candidate(
        first, candles[first].display_time,
        first, candles[first].display_time, Decimal(top),
        first, candles[first].display_time, Decimal(bottom),
        "A", break_idx=end, break_time=candles[end].display_time,
    )


def results(candles, bullish, bearish):
    return {
        direction: engine.DetectionResult(
            direction, list(map(replace, items)), [], 0, len(candles) - 1,
        )
        for direction, items in (("bullish", bullish), ("bearish", bearish))
    }


@pytest.mark.parametrize("inner_direction", ("bullish", "bearish"))
def test_new_opposite_owner_can_hide_and_release_an_older_reaction(inner_direction, monkeypatch):
    candles = bars([("10", "11", "9", "10")] * 6)
    inner = candidate(candles, 2, 3, "11", "9")
    owners = [
        candidate(candles, 0, 4, "12", "8"),
        candidate(candles, 1, 5, "13", "7"),
    ]

    def inputs(count, outer):
        if inner_direction == "bullish":
            return results(candles[:count], [inner], outer)
        return results(candles[:count], outer, [inner])

    seed = engine.MarketChronology(candles[:4], candles[:4], 30)
    checkpoint = engine.LiveBehaviorReactionViews(inputs(4, []), seed)
    calls = []
    project = engine.published_reaction_candidate

    def track(direction, reaction, market):
        calls.append((direction, reaction.first_idx))
        return project(direction, reaction, market)

    monkeypatch.setattr(engine, "published_reaction_candidate", track)
    market = engine.MarketChronology(candles, candles, 30)
    for outer, blocked in ((owners, True), (owners[1:], True), ([], False)):
        expected = engine.build_behavior_reaction_views(inputs(6, outer), market)
        calls.clear()
        actual = checkpoint.update(inputs(6, outer), market, first_dirty_main=4)
        assert actual == expected
        assert ((2, 3) in actual[2][inner_direction]) == blocked
        assert (inner_direction, 2) not in calls


def test_lower_timeframe_revision_rechecks_containment_with_identical_reactions():
    candles = bars([("10", "11", "9", "10")] * 5)
    inner = candidate(candles, 2, 3, "11", "9")
    outer = candidate(candles, 0, 4, "12", "8")
    market = engine.MarketChronology(candles, candles, 30)
    initial = results(candles, [inner], [outer])
    checkpoint = engine.LiveBehaviorReactionViews(initial, market)
    assert initial["bullish"].reactions[0].behavior_internal
    revised = candles.copy()
    revised[3] = replace(revised[3], low=Decimal("7"))
    market = engine.MarketChronology(candles, revised, 30)
    updated = checkpoint.update(results(candles, [inner], [outer]), market, first_dirty_main=3)
    assert updated == engine.build_behavior_reaction_views(results(candles, [inner], [outer]), market)
    assert not updated[0]["bullish"].reactions[0].behavior_internal


def test_live_view_preserves_the_public_decimal_representation():
    candles = bars([("10", "11", "9", "10")] * 4)
    first = candidate(candles, 1, 2, "11.0", "9")
    market = engine.MarketChronology(candles, candles, 30)
    checkpoint = engine.LiveBehaviorReactionViews(results(candles, [first], []), market)
    revised = replace(first, box_top=Decimal("11.00"))
    fresh = results(candles, [revised], [])
    checkpoint.update(fresh, market, first_dirty_main=3)
    assert str(fresh["bullish"].reactions[0].behavior_public_box_top) == "11.00"
