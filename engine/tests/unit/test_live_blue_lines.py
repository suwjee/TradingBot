from dataclasses import replace
from decimal import Decimal

import pytest

from test_live_reaction_continuation import bars
from reaction_engine import MarketChronology, UnifiedReactionDetector, mirror_candle
from blue_line_detector import LiveBlueLineContinuation, detect_blue_lines
import blue_line_detector as blue


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_late_reset_updates_only_its_own_reaction_tail(direction, monkeypatch):
    candles = bars([
        ("10", "11", "8", "9"), ("9", "12", "9", "11.5"),
        ("11.5", "13", "10", "12.5"), ("12.5", "12.8", "9", "10"),
        ("10", "14", "9.1", "13"), ("13", "13.2", "7.5", "9"),
        ("9", "10", "8", "9.5"), ("9.5", "9.8", "8.5", "9"),
        ("9", "11", "8.5", "10.5"),
    ])
    if direction == "bearish":
        candles = list(map(mirror_candle, candles))
    options = {f"initial_{direction}_trend": True}
    before = candles[:5]
    old_market = MarketChronology(before, before, 30)
    old = UnifiedReactionDetector(before, before, 0, 4, direction, **options).detect()
    assert len(old.reactions) == 2 and not old.resets
    session = LiveBlueLineContinuation(direction, old.reactions, old_market, old.resets)

    market = MarketChronology(candles, candles, 30)
    current = UnifiedReactionDetector(candles, candles, 0, 8, direction, **options).detect()
    expected = detect_blue_lines(direction, current.reactions, market, current.resets)
    assert any(line.kind == "reset" for line in expected)
    calls = []
    count = blue.count_scale_strikes

    def track(direction, reaction, *args, **kwargs):
        calls.append(reaction.first_idx)
        return count(direction, reaction, *args, **kwargs)

    monkeypatch.setattr(blue, "count_scale_strikes", track)
    assert session.update(current.reactions, market, current.resets, first_changed=1) == expected
    assert calls == [reaction.first_idx for reaction in current.reactions[1:]]


def test_a_revised_reset_candle_updates_blue_even_when_reaction_events_are_identical():
    candles = bars([
        ("10", "11", "8", "9"), ("9", "12", "9", "11.5"),
        ("11.5", "13", "10", "12.5"), ("12.5", "12.8", "9", "10"),
        ("10", "14", "9.1", "13"), ("13", "13.2", "7.5", "9"),
    ])
    result = UnifiedReactionDetector(candles, candles, 0, 5, "bullish", initial_bullish_trend=True).detect()
    assert len(result.resets) == 1
    market = MarketChronology(candles, candles, 30)
    session = LiveBlueLineContinuation("bullish", result.reactions, market, result.resets)
    old = session.result
    revised = [*candles[:-1], replace(candles[-1], low=Decimal("7.0"))]
    updated_market = MarketChronology(revised, revised, 30)
    expected = detect_blue_lines("bullish", result.reactions, updated_market, result.resets)
    assert old != expected
    assert session.update(
        result.reactions, updated_market, result.resets,
        first_changed=len(result.reactions), first_dirty_main=5,
    ) == expected
