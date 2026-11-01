"""The first bearish Reaction owns fresh input, then normal Reset resumes."""
from dataclasses import replace
from decimal import Decimal

from test_bullish_trend_start import candles, sample
from reaction_engine import UnifiedReactionDetector, classify_candle_color


def reflected(rows):
    return [replace(row, open=-row.open, high=-row.low, low=-row.high,
                    close=-row.close, tag=classify_candle_color(-row.open, -row.close))
            for row in rows]


def test_first_green_seeds_bearish_reaction_without_prior_red_or_reset():
    rows = reflected(sample())
    result = UnifiedReactionDetector(rows, rows, 0, 4, "bearish",
                                    initial_bearish_trend=True).detect()
    first = result.reactions[0]
    assert (first.first_idx, first.box_bottom_source_idx,
            first.box_top_source_idx, first.break_idx) == (0, 0, 2, 3)
    assert (first.box_bottom, first.box_top) == (Decimal("-10"), Decimal("-6"))
    assert first.leg_boundary_value == Decimal("-8")


def test_normal_bearish_reset_resumes_after_first_confirmation():
    rows = reflected(sample())
    result = UnifiedReactionDetector(rows, rows, 0, 4, "bearish",
                                    initial_bearish_trend=True).detect()
    assert [(item.index, item.broken_level) for item in result.resets] == [(4, Decimal("-6"))]


def test_equal_low_does_not_confirm_the_new_bearish_reaction():
    rows = reflected(candles([("9", "10", "8", "8"),
                             ("8", "10", "7", "9"),
                             ("9", "10.001", "8", "10")]))
    result = UnifiedReactionDetector(rows, rows, 0, 2, "bearish",
                                    initial_bearish_trend=True).detect()
    assert result.reactions[0].break_idx == 2


def test_bearish_bootstrap_keeps_market_doji_green_and_eligible_as_first():
    rows = candles([("10", "11", "9", "10"), ("10", "12", "8", "9")])
    result = UnifiedReactionDetector(rows, rows, 0, 1, "bearish",
                                    initial_bearish_trend=True).detect()
    assert rows[0].tag == "GREEN"
    assert result.reactions[0].first_idx == 0
    assert result.reactions[0].break_idx == 1


def test_disabled_bearish_bootstrap_preserves_ordinary_detection():
    rows = reflected(sample())
    ordinary = UnifiedReactionDetector(rows, rows, 0, 4, "bearish").detect()
    explicit = UnifiedReactionDetector(rows, rows, 0, 4, "bearish",
                                      initial_bearish_trend=False).detect()
    assert explicit == ordinary
