from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from reaction_engine import (
    BullishDetector, Candle, LiveReactionContinuation, LiveReactionUnavailable,
    UnifiedReactionDetector, classify_candle_color, mirror_candle,
)


def bars(values):
    start = datetime(2026, 1, 1)
    output = []
    for i, (opening, high, low, close) in enumerate(values):
        opening, high, low, close = map(Decimal, (opening, high, low, close))
        time = start + timedelta(seconds=i * 30)
        output.append(Candle(i, time, str(time), classify_candle_color(opening, close),
                             opening, high, low, close))
    return output


@pytest.fixture
def bullish():
    return bars([
        ("10", "11", "8", "9"), ("9", "12", "9", "11.5"),
        ("11.5", "13", "10", "12.5"), ("12.5", "12.8", "9", "10"),
        ("10", "14", "9.1", "13"), ("13", "13.2", "8.5", "9"),
    ])


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_open_normal_reaction_continues_across_the_boundary(bullish, direction, monkeypatch):
    candles = bullish if direction == "bullish" else list(map(mirror_candle, bullish))
    options = {f"initial_{direction}_trend": True}
    seed, extension = candles[:4], candles[4:5]
    expected = UnifiedReactionDetector(candles[:5], candles[:5], 0, 4, direction, **options).detect()
    session = LiveReactionContinuation(seed, seed, direction, timeframe_seconds=30, **options)
    assert len(session.result.reactions) == 1
    assert [(item.first_idx, item.break_idx) for item in expected.reactions] == [(0, 1), (3, 4)]

    def no_bootstrap(*_args):
        pytest.fail("The completed Leg-Start was calculated again.")

    monkeypatch.setattr(UnifiedReactionDetector, "_first_initial", no_bootstrap)
    assert session.advance(extension, extension) == expected
    assert session.processed_main_candles == 1


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_reset_keeps_its_open_search_between_polls(direction):
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
    session = LiveReactionContinuation(candles[:5], candles[:5], direction, timeframe_seconds=30, **options)
    settled = session.result.reactions[:]
    for end in range(6, len(candles) + 1):
        output = session.advance(candles[end - 1:end], candles[end - 1:end])
        expected = UnifiedReactionDetector(candles[:end], candles[:end], 0, end - 1, direction, **options).detect()
        assert output == expected
        assert output.reactions[:len(settled)] == settled
        assert len(output.resets) == 1
    assert len(output.reactions) == 3


def test_invalid_append_does_not_replace_the_committed_result(bullish):
    session = LiveReactionContinuation(
        bullish[:5], bullish[:5], "bullish", timeframe_seconds=30, initial_bullish_trend=True,
    )
    before = session.result
    with pytest.raises(LiveReactionUnavailable, match="timeframe grid"):
        session.advance(bullish[4:], bullish[4:])
    assert session.result == before
    assert session.processed_main_candles == 0


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_unconfirmed_initial_candidate_survives_first_poll(direction, monkeypatch):
    candles = bars([
        ("10", "12", "9", "11"), ("11", "11.5", "9.5", "10"),
        ("10", "13", "9.6", "12.5"),
    ])
    if direction == "bearish":
        candles = list(map(mirror_candle, candles))
    expected = UnifiedReactionDetector(candles, candles, 0, 2, direction).detect()
    assert [(item.first_idx, item.break_idx) for item in expected.reactions] == [(1, 2)]
    session = LiveReactionContinuation(candles[:2], candles[:2], direction, timeframe_seconds=30)
    assert not session.result.reactions

    def no_earlier_first_candle(*_args):
        pytest.fail("The pending First candle should not be rediscovered on append.")

    monkeypatch.setattr(BullishDetector, "green_run_peak_before", no_earlier_first_candle)
    assert session.advance(candles[2:], candles[2:]) == expected


def test_preview_does_not_commit_a_confirmation_on_a_mutable_analysis_bar(bullish):
    session = LiveReactionContinuation(
        bullish[:4], bullish[:4], "bullish", timeframe_seconds=30, initial_bullish_trend=True,
    )
    before = session.result
    assert len(session.preview(bullish[4:5], bullish[4:5]).reactions) == 2
    assert session.result == before
    assert session.processed_main_candles == 0

    final_bar = replace(bullish[4], high=Decimal("12.9"), close=Decimal("12.8"))
    full = [*bullish[:4], final_bar]
    expected = UnifiedReactionDetector(full, full, 0, 4, "bullish", initial_bullish_trend=True).detect()
    assert session.advance([final_bar], [final_bar]) == expected
    assert len(session.result.reactions) == 1


def test_initial_market_gap_does_not_define_the_append_grid(bullish):
    candles = bullish[:1]
    for candle in bullish[1:]:
        stamp = candle.timestamp + timedelta(seconds=30)
        candles.append(replace(candle, timestamp=stamp, display_time=str(stamp)))
    initial = candles[:2]
    session = LiveReactionContinuation(
        initial, initial, "bullish", timeframe_seconds=30, initial_bullish_trend=True,
    )
    expected = UnifiedReactionDetector(
        candles, candles, 0, len(candles) - 1, "bullish", initial_bullish_trend=True,
    ).detect()
    assert session.advance(candles[2:], candles[2:]) == expected
