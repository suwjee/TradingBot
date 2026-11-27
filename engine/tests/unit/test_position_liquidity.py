"""Check liquidity geometry, publication, and shared sweeps in both directions."""

from decimal import Decimal

import pytest

from engine.pipeline.position_rules import calculate_liquidity


@pytest.fixture(params=["bullish", "bearish"])
def market(request):
    direction = request.param
    bullish = direction == "bullish"

    def price(value):
        return str(value if bullish else 200 - value)

    def event(source, level, *, number=1, verdict="F", decision=None, color="red"):
        return {"sourceTime": source, "decisionTime": source if decision is None else decision,
                "price": price(level), "number": number, "color": color, "family": color,
                "trueFalse": verdict}

    def calculate(group, raw, *, through=2000, times=tuple(range(1, 3001))):
        def crossing(side, start, level):
            level = Decimal(level)
            for time, low, high in raw:
                if not start <= time < through:
                    continue
                raw_low, raw_high = (low, high) if bullish else (200 - high, 200 - low)
                if raw_low < level if side == "bullish" else raw_high > level:
                    return time
            return None

        rows = calculate_liquidity(
            group, crossing, direction=direction, timeframe=1, closed_through=through,
            source_event_at=None, candle_times=times,
        )
        return {row["sourceTime"]: row for row in rows}

    return event, calculate, price, "primaryLows" if bullish else "primaryHighs"


def test_movement_and_chart_trigger_are_distinct(market):
    event, calculate, price, _ = market
    group = {"eZones": [event(10, 100)]}
    raw = [(11, 100, 107), (16, 100, 105), (18, 99, 103)]
    level = calculate(group, raw)[10]
    assert level["price"] == price(100)
    assert level["movementTime"] == 11
    assert level["collectedTime"] == 18
    assert level["visibleFrom"] is None

    group["sZones"] = [event(16, 102, verdict="T", decision=20)]
    assert calculate(group, raw, through=20)[10]["visibleFrom"] is None
    level = calculate(group, raw)[10]
    assert (level["visibleFrom"], level["lineEndTime"]) == (21, 18)

    group["sZones"] = [event(18, 102, verdict="T")]
    assert calculate(group, raw)[10]["visibleFrom"] is None


def test_repeated_line_uses_its_confirmation_and_newest_sweep_collects_older(market):
    event, calculate, _, _ = market
    group = {"eZones": [event(10, 100, number=3), event(20, 100, number=3, verdict="T"),
                        event(30, 110, number=3), event(60, 120, number=3, decision=63)],
             "sZones": [event(40, 115, verdict="T")]}
    raw = [(11, 100, 105), (31, 110, 114), (65, 119, 122), (70, 110, 116), (75, 109, 115)]
    levels = calculate(group, raw)
    assert list(levels) == [10, 30, 60]
    assert levels[60]["visibleFrom"] == 64
    assert {row["repeatGroupSourceTime"] for row in levels.values()} == {10}
    assert {row["collectedTime"] for row in levels.values()} == {65}
    assert levels[10]["directSweepTime"] is None
    assert levels[10]["lineEndTime"] == 1510
    assert levels[30]["lineEndTime"] == 75


@pytest.mark.parametrize("separator", ["larger", "stopAlls", "primary"])
def test_larger_behavior_and_window_resets_split_runs(market, separator):
    event, calculate, _, primary = market
    group = {"eZones": [event(10, 100), event(40, 100)]}
    middle = event(20, 100, number=2, verdict="T")
    if separator == "larger":
        group["eZones"].append(middle)
    else:
        group[primary if separator == "primary" else separator] = [middle]
    levels = calculate(group, [(11, 100, 110), (41, 100, 110)])
    assert all(row["repeatGroupSourceTime"] is None for row in levels.values())
    assert all(row["visibleFrom"] is None for row in levels.values())


def test_geometry_cap_counts_candles_and_keeps_later_lifecycle(market):
    event, calculate, _, _ = market
    times = tuple([10, 11] + list(range(500, 3001)))
    group = {"eZones": [event(10, 100)], "sZones": [event(11, 105, verdict="T")]}
    level = calculate(group, [(11, 105, 110), (2500, 99, 101)], through=3001, times=times)[10]
    assert level["lineEndTime"] == times[1500]
    assert level["collectedTime"] == 2500
