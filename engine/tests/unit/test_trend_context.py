"""Trend segmentation isolates input and preserves absolute public indexes."""
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"bridge"))

from test_bullish_trend_start import candles
from reaction_engine import MarketChronology
from trading_pipeline import MarketContext


def market():
    rows = candles([("9","10","8","8"),("8","9","7","8.5"),
                    ("8.5","9","6","7"),("7","11","7","10")])
    chronology = MarketChronology(rows,rows,30)
    return MarketContext(rows,rows,chronology.lower_index,chronology,0,3)


def test_suffix_contains_only_boundary_and_later_candles_with_fresh_indexes():
    from trading_pipeline import market_segment
    original = market()
    suffix = market_segment(original,2,4,initial_bullish_trend=True)
    assert [row.timestamp for row in suffix.candles] == [row.timestamp for row in original.candles[2:]]
    assert [row.index for row in suffix.candles] == [0,1]
    assert suffix.seconds[0].timestamp == original.candles[2].timestamp
    assert suffix.index_offset == 2
    assert suffix.initial_bullish_trend is True
    assert [row.index for row in original.candles] == [0,1,2,3]


def test_serialized_index_translation_preserves_numbers_times_and_sentinels():
    from trading_pipeline import absolute_payload_indexes
    payload = {"reactions":[{"firstIndex":0,"breakIndex":3,"number":1,"firstTime":100}],
               "nested":{"sourceIndex":None,"stopIndex":-1,"index":2},"id":"opaque"}
    translated = absolute_payload_indexes(payload,10)
    assert translated == {"reactions":[{"firstIndex":10,"breakIndex":13,"number":1,"firstTime":100}],
        "nested":{"sourceIndex":None,"stopIndex":-1,"index":12},"id":"opaque"}
    assert payload["reactions"][0]["firstIndex"] == 0


def test_fiftieth_icon_candle_counts_actual_candles_and_includes_start():
    from trading_pipeline import serialize_trend_transition
    from PL_PH_detector import TrendTransition
    from test_primary_high_numbering import high
    rows = candles([("9","10","8","9")] * 55)
    # A session gap must not change the selected actual candle number.
    from datetime import timedelta
    rows[30:] = [replace(row,timestamp=row.timestamp+timedelta(days=2)) for row in rows[30:]]
    chrono = MarketChronology(rows,rows,30)
    context = MarketContext(rows,rows,chrono.lower_index,chrono,0,54)
    event = TrendTransition(2,rows[2].timestamp,Decimal("10"),high(3,0,1,"10"))
    result = serialize_trend_transition(event,context)
    assert result["iconCandleIndex"] == 51
    assert result["iconCandleTime"] == int(rows[51].timestamp.replace(tzinfo=__import__('zoneinfo').ZoneInfo('Asia/Tehran')).timestamp())
    assert result["iconCandleHigh"] == "10"


def test_icon_target_is_absent_until_fifty_actual_candles_exist():
    from trading_pipeline import serialize_trend_transition
    from PL_PH_detector import TrendTransition
    from test_primary_high_numbering import high
    context = market()
    event = TrendTransition(2,context.candles[2].timestamp,Decimal("10"),high(3,0,1,"10"))
    result = serialize_trend_transition(event,context)
    assert result["iconCandleTime"] is None
    assert result["iconCandleHigh"] is None


def test_future_transition_does_not_replace_an_earlier_presentation_window(monkeypatch):
    from types import SimpleNamespace as NS
    import trading_pipeline as bridge
    context = replace(market(),end_index=1)
    state = NS(directions=("bullish","bearish"),primary_result=NS(transition=NS(index=3)))
    engines = NS(reaction=NS(REACTION_ENGINE_VERSION="test"),primary=None,
        blue_line=NS(BLUE_LINE_VERSION="test"),a_zone=NS(A_ZONE_VERSION="test"),
        s_zone=NS(S_ZONE_VERSION="test"),e_zone=None,lifecycle=None)
    args = NS(s_zones="enabled",blue_lines="enabled",a_zones="enabled",lifecycle_engine=None,timeframe=30)
    monkeypatch.setattr(bridge,"build_direction_output",lambda direction,*args:{"direction":direction})
    monkeypatch.setattr(bridge,"build_reversed_trend_outputs",lambda *args:{"bearish":{"status":"reversed"}})
    result = bridge.build_response_payload(args,engines,context,state,{},0)
    assert result["directions"] == {"bullish":{"direction":"bullish"},"bearish":{"direction":"bearish"}}
    assert "activeDirection" not in result
