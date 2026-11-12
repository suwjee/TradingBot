from dataclasses import replace
from decimal import Decimal
from types import SimpleNamespace

import pytest

from test_live_reaction_continuation import bars
from reaction_engine import Candidate, MarketChronology, mirror_candidate, mirror_candle
from s_zone_detector import LiveSZoneContinuation, SZoneDetector


def make_detector(direction, count, *, public_blue=True, revision=None):
    candles = bars([
        ("10", "10.5", "9.9", "10"),
        ("10", "11", "10", "10.8"),
        ("10.8", "11", "9.8", "10"),
        ("10", "12", "9.5", "11.5"),
        ("11.5", "11.6", "9.3", "10"),
        ("10", "11", "9.7", "10.5"),
    ])[:count]
    if revision is not None:
        candles[4] = replace(candles[4], low=Decimal(revision))
    trend = [
        Candidate(
            first, candles[first].display_time,
            first, candles[first].display_time, Decimal(top),
            first, candles[first].display_time, Decimal("9"),
            "A", break_idx=end, break_time=candles[end].display_time,
        )
        for first, end, top in ((0, 1, "10.5"), (2, 3, "11"))
    ]
    if direction == "bearish":
        candles = [mirror_candle(candle) for candle in candles]
        trend = [mirror_candidate(item) for item in trend]
    blue = SimpleNamespace(
        kind="scale", source_index=3, reaction_number=2,
        formation_time=candles[3].timestamp, behavior_internal=not public_blue,
    )
    a = SimpleNamespace(
        source_index=0, source_time=candles[0].timestamp,
        reaction_number=1, reaction_break_time=candles[1].timestamp,
        price=Decimal("10" if direction == "bullish" else "-10"),
    )
    return SZoneDetector(
        direction, trend, [], [blue], [a], MarketChronology(candles, candles, 30),
    )


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_open_s_can_decide_and_then_reuse_the_original_candidate(direction, monkeypatch):
    live = LiveSZoneContinuation()
    assert live.update(make_detector(direction, 4), first_dirty_main=0) == []
    decided = make_detector(direction, 5)
    initial = live.update(decided, first_dirty_main=4)
    assert len(initial) == 1
    assert initial[0].formation_type == "type4"
    fresh = make_detector(direction, 6)
    expected = fresh.detect()
    continued = make_detector(direction, 6)

    def replay(*_args, **_kwargs):
        pytest.fail("A settled Type-4 candidate was evaluated again.")

    monkeypatch.setattr(continued, "_first_type4", replay)
    output = live.update(continued, first_dirty_main=5)
    assert output == expected
    assert output[0] is initial[0]
    assert continued.a_ownership_windows == fresh.a_ownership_windows
    assert continued.order_audit == fresh.order_audit


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_earlier_blue_ownership_revision_reopens_an_s_candidate(direction):
    live = LiveSZoneContinuation()
    assert live.update(make_detector(direction, 5), first_dirty_main=0)
    revised = make_detector(direction, 6, public_blue=False)
    expected = revised.detect()
    continued = make_detector(direction, 6, public_blue=False)
    assert live.update(continued, first_dirty_main=5) == expected == []
    assert continued.a_ownership_windows == revised.a_ownership_windows


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_main_candle_revision_reopens_an_s_candidate(direction):
    live = LiveSZoneContinuation()
    assert live.update(make_detector(direction, 5), first_dirty_main=0)
    revised = make_detector(direction, 6, revision="9.5")
    expected = revised.detect()
    continued = make_detector(direction, 6, revision="9.5")
    assert live.update(continued, first_dirty_main=4) == expected == []
    assert continued.a_ownership_windows == revised.a_ownership_windows
