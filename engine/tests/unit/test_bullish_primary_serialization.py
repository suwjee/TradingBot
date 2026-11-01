"""Directional bridge projection and actual-bar reversal metadata."""
from dataclasses import replace
from decimal import Decimal
from types import SimpleNamespace as NS
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "bridge"))
import trading_pipeline as bridge
from PL_PH_detector import TrendTransition
from test_bullish_primary_mirror import mirror_values, run_bullish
from test_pl_ph_detector import fixture, initial
from test_trend_context import market


def test_bullish_projection_keeps_real_kind_direction_and_low_cycle_joins():
    values = mirror_values(fixture(initial()))
    result = run_bullish(values, {("PL", 8): [(10,)]})
    context = NS(candles=values[0].candles, chronology=values[0],
                 start_index=0, end_index=31, index_offset=0)
    output = bridge.serialize_primary_structures(result, context)
    low = output["primaryLows"][0]
    assert low["direction"] == "bullish"
    assert low["kind"] == "PL"
    assert low["id"].startswith("bullish:PL:")
    assert low["price"] == "-110"
    assert output["matchingBehaviorLegs"][0]["price"] == "-80"
    assert output["primaryCycles"][0]["lowIds"] == [low["id"]]
    assert "postPH3Orders" in output


def test_fresh_same_direction_segments_cannot_reuse_primary_ids():
    values = mirror_values(fixture(initial()))
    result = run_bullish(values, {("PL", 8): [(10,)]})
    context = NS(candles=values[0].candles, chronology=values[0],
                 start_index=0, end_index=31, index_offset=0)
    first = bridge.serialize_primary_structures(result, context)
    context.index_offset = 500
    later = bridge.serialize_primary_structures(result, context)
    assert first["primaryLows"][0]["id"] != later["primaryLows"][0]["id"]
    assert first["primaryCycles"][0]["id"] != later["primaryCycles"][0]["id"]
    assert first["matchingBehaviorLegs"][0]["id"] != later["matchingBehaviorLegs"][0]["id"]


def test_bearish_start_metadata_uses_pl_provenance_and_target_low():
    context = market()
    stopped = NS(source_index=0, source_time=context.candles[0].timestamp)
    event = TrendTransition(2, context.candles[2].timestamp, Decimal("7"), stopped, "bearish")
    # Use fifty actual remaining candles without changing the input chronology.
    rows = [replace(context.candles[0], index=i,
                    timestamp=context.candles[0].timestamp + context.chronology.timeframe*i)
            for i in range(55)]
    context = replace(context, candles=rows, end_index=54)
    output = bridge.serialize_trend_transition(event, context)
    assert output["direction"] == "bearish"
    assert output["previousDirection"] == "bullish"
    assert output["plNumber"] == 3
    assert output["plSourceIndex"] == 0
    assert output["iconCandleIndex"] == 51
    assert output["iconCandleLow"] == "8"
    assert "phNumber" not in output


def test_bearish_segment_contains_whole_boundary_and_has_fresh_bootstrap():
    context = market()
    suffix = bridge.market_segment(context, 2, 4, initial_bearish_trend=True)
    assert suffix.initial_bearish_trend is True
    assert suffix.initial_bullish_trend is False
    assert suffix.candles[0].timestamp == context.candles[2].timestamp
    prefix = bridge.market_segment(suffix, 0, 1)
    assert prefix.initial_bearish_trend is True


def test_merging_repeated_direction_preserves_each_historical_boundary():
    first = {"direction": "bearish", "reactions": [{"firstIndex": 1}],
             "bridgeOutput": {"reactions": [{"firstIndex": 1}]},
             "calculationEndTime": 100, "primaryStatus": "reversed-to-bullish"}
    later = {"direction": "bearish", "reactions": [{"firstIndex": 50}],
             "bridgeOutput": {"reactions": [{"firstIndex": 50}]},
             "calculationStartTime": 200, "primaryStatus": "waiting-for-matching-behaviors"}
    output = bridge.merge_regime_outputs([("bearish", first), ("bearish", later)])
    group = output["bearish"]
    assert group["reactions"] == [{"firstIndex": 1}, {"firstIndex": 50}]
    assert group["calculationSegments"] == [first, later]
    assert group["primaryStatus"] == later["primaryStatus"]
    assert "calculationEndTime" not in group
    assert "calculationSegments" not in first
    assert group["bridgeOutput"]["reactions"] == group["reactions"]


def test_absolute_projection_translates_order_identity_pairs_without_changing_other_lists():
    row = {"physicalOrderIdentity": [0, 2], "resetReactionIdentity": [1, 2],
           "values": [0, 2], "stopIndex": -1}
    assert bridge.absolute_payload_indexes(row, 10) == {
        "physicalOrderIdentity": [10, 12], "resetReactionIdentity": [11, 12],
        "values": [0, 2], "stopIndex": -1}


def test_repeated_reversals_rebuild_each_direction_from_its_whole_start_candle(monkeypatch):
    from test_bullish_trend_start import candles
    from reaction_engine import MarketChronology
    rows = candles([("9", "10", "8", "9")] * 7)
    chronology = MarketChronology(rows, rows, 30)
    context = bridge.MarketContext(rows, rows, chronology.lower_index, chronology, 0, 6)
    def event(context, target):
        stopped = NS(source_index=0, source_time=context.candles[0].timestamp)
        return TrendTransition(2, context.candles[2].timestamp, Decimal("10"), stopped, target)
    seen = []
    def prepare(args, engines, context, timings):
        seen.append((args.direction, context))
        transition = (event(context, "bearish") if context.index_offset == 2
                      and len(context.candles) > 2 else None)
        point = NS(number=3, source_time=context.candles[0].timestamp, price=Decimal("10"))
        return NS(primary_result=NS(transition=transition, points=[point]))
    def build(direction, args, engines, context, state, timings):
        return {"reactions": [{"firstIndex": 0}], "resets": [],
                "primaryCycles": [], "matchingBehaviorLegs": []}
    monkeypatch.setattr(bridge, "prepare_pipeline_state", prepare)
    monkeypatch.setattr(bridge, "build_direction_output", build)
    engines = NS(primary=NS(resolve_primary_highs=lambda result, **kw: result.points,
                           resolve_primary_lows=lambda result, **kw: result.points))
    output = bridge.build_reversed_trend_outputs(NS(), engines, context,
                                                event(context, "bullish"), {})
    bear = output["bearish"]["calculationSegments"]
    assert [item["firstIndex"] for item in output["bearish"]["reactions"]] == [0, 4]
    assert bear[0]["calculationEndTime"] == bridge.epoch(rows[2].timestamp)
    assert bear[1]["calculationStartTime"] == bridge.epoch(rows[4].timestamp)
    assert bear[1]["trendTransitions"][0]["plSourceIndex"] == 2
    for direction, segment in seen:
        assert segment.candles[0].index == 0
        assert segment.seconds[0].timestamp == segment.candles[0].timestamp
        if segment.index_offset == 2:
            assert segment.initial_bullish_trend is True
        if segment.index_offset == 4:
            assert segment.initial_bearish_trend is True
