"""A new bullish regime owns its first Reaction without pre-boundary context."""
from datetime import timedelta
from decimal import Decimal

from test_pl_ph_detector import BASE
from reaction_engine import Candle, UnifiedReactionDetector, classify_candle_color


def candles(values):
    output = []
    for index, prices in enumerate(values):
        opening, high, low, close = map(Decimal, prices)
        time = BASE + timedelta(seconds=30*index)
        output.append(Candle(index,time,str(time),classify_candle_color(opening,close),
                             opening,high,low,close))
    return output


def sample():
    return candles([("9","10","8","8"),("8","9","7","8.5"),
        ("8.5","9","6","7"),("7","11","7","10"),
        ("7","8","5","6")])


def test_initial_red_seeds_first_bullish_reaction_and_bottom_may_fall():
    rows = sample()
    result = UnifiedReactionDetector(rows,rows,0,len(rows)-1,"bullish",
                                    initial_bullish_trend=True).detect()
    first = result.reactions[0]
    assert (first.first_idx,first.box_top_source_idx,first.box_bottom_source_idx,
            first.break_idx) == (0,0,2,3)
    assert (first.box_top,first.box_bottom) == (Decimal("10"),Decimal("6"))


def test_normal_reset_resumes_immediately_after_first_confirmation():
    rows = sample()
    result = UnifiedReactionDetector(rows,rows,0,len(rows)-1,"bullish",
                                    initial_bullish_trend=True).detect()
    assert [(item.index,item.broken_level) for item in result.resets] == [(4,Decimal("6"))]


def test_equal_high_does_not_confirm_the_initial_trend_reaction():
    rows = candles([("9","10","8","8"),("8","10","7","9"),
                    ("9","10.001","8","10")])
    result = UnifiedReactionDetector(rows,rows,0,2,"bullish",
                                    initial_bullish_trend=True).detect()
    assert result.reactions[0].break_idx == 2


def test_explicitly_disabled_bootstrap_preserves_standard_detection():
    rows = sample()
    ordinary = UnifiedReactionDetector(rows,rows,0,4,"bullish").detect()
    explicit = UnifiedReactionDetector(rows,rows,0,4,"bullish",
                                      initial_bullish_trend=False).detect()
    assert explicit == ordinary


def test_initial_reaction_keeps_the_new_leg_head_for_native_blue_calculation():
    from blue_line_detector import detect_blue_lines
    from reaction_engine import MarketChronology
    rows = sample()
    result = UnifiedReactionDetector(rows,rows,0,4,"bullish",
                                    initial_bullish_trend=True).detect()
    assert result.reactions[0].leg_boundary_value == Decimal("8")
    detect_blue_lines("bullish",result.reactions,MarketChronology(rows,rows,30),result.resets)
