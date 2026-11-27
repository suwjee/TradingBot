"""Exercise each directional position family and its chronology."""
from decimal import Decimal

import pytest

from engine.buy_algorithm import calculate_buy_positions
from engine.sell_algorithm import calculate_sell_positions


@pytest.fixture(params=["buy", "sell"])
def market(request):
    buy = request.param == "buy"
    direction = "bullish" if buy else "bearish"
    primary = "primaryLows" if buy else "primaryHighs"
    calculate = calculate_buy_positions if buy else calculate_sell_positions
    suffix = "B" if buy else "S"

    def price(value):
        value = Decimal(value)
        return str(value if buy else Decimal(300) - value)

    def row(source, value, *, decision=None, number=None, verdict="T", color="red"):
        decision = source if decision is None else decision
        detail = {"color": color} if number is None else {"family": color, "number": number}
        return dict(sourceTime=source, decisionTime=decision, decisionEventTime=decision + 1,
                    price=price(value), trueFalse=verdict, **detail)

    def positions(group, crosses=(), *, through=800, formed=None, entry=120):
        def first_crossing(side, start, level):
            assert side == direction
            compare = Decimal.__lt__ if buy else Decimal.__gt__
            return next((time for time, value in crosses if start <= time < through
                         and compare(Decimal(price(value)), Decimal(level))), None)

        return calculate(group, lambda _: Decimal(price(entry)), first_crossing, timeframe=10,
                         closed_through=through,
                         source_event_at=lambda _, time, __: (formed or {}).get(time, time))

    return primary, suffix, row, positions, price


def test_foundation_f_requires_record_rank_and_unbroken_source(market):
    _, suffix, row, positions, price = market
    group = {
        "eZones": [row(30, 100, number=2),
                   row(100, 95, number=1, verdict="F"),
                   row(150, 90, number=3, verdict="F"),
                   row(200, 80, number=4, verdict="F"),
                   row(300, 75, number=5, verdict="F")],
        "sZones": [row(10, 105), row(50, 102), row(120, 96), row(180, 92),
                   row(240, 84), row(330, 83)],
    }
    crosses = [(90, 99), (155, 89), (280, 79)]
    result = positions(group, crosses)
    assert [(p["type"], p["anchorSourceTime"], p["triggerSourceTime"]) for p in result] == [
        ("1.1" + suffix, 30, 50),
        ("1.2" + suffix, 200, 240),
    ]
    assert [p["stopEventTime"] for p in result] == [90, 280]
    assert result[0]["targetPrice"] == price(200)
    assert [p["type"] for p in positions(group, [(90, 100)])] == ["1.1" + suffix]


def test_stopall_pre_entry_stop_keeps_drawing_and_enables_second_stage(market):
    _, suffix, row, positions, price = market
    group = {
        "stopAlls": [row(30, 100, number=1), row(70, 90, number=2, verdict="F"),
                     row(140, 86, number=3), row(190, 76, number=4, verdict="F")],
        "sZones": [row(50, 110, decision=70), row(90, 110), row(160, 105), row(210, 101)],
    }
    crosses = [(74, 100), (75, 99), (110, 89), (180, 85)]
    result = positions(group, crosses, formed={70: 76})
    assert [(p["type"], p["entryTime"], p["anchorSourceTime"]) for p in result] == [
        ("2.1" + suffix, 70, 30), ("2.2" + suffix, 90, 70),
    ]
    assert result[0]["preEntryStop"] is True
    assert result[0]["stopEventTime"] == 75
    assert result[0]["targetPrice"] == price(200)
    assert not positions(group, crosses, formed={70: 76}, through=79)
    assert [p["type"] for p in positions(group, crosses, formed={70: 74})] == ["2.1" + suffix, "2.2" + suffix]
    assert positions(group, crosses, formed={70: 74})[-1]["anchorSourceTime"] == 190
    assert positions(group, crosses, formed={70: 75})[-1]["anchorSourceTime"] == 70


def test_pre_entry_crossing_keeps_original_stop_when_close_is_beyond_it(market):
    _, suffix, row, positions, price = market
    group = {"stopAlls": [row(30, 100, number=1)],
             "sZones": [row(50, 110, decision=70)]}
    entry, = positions(group, [(75, 98)], entry=98)
    assert (entry["type"], entry["entryPrice"], entry["stopPrice"], entry["targetPrice"]) == (
        "2.1" + suffix, price(98), price(100), price(106),
    )
    assert entry["preEntryStop"] is True


def test_foundation_restarts_after_stopall_and_coexists_with_stopall_entry(market):
    _, suffix, row, positions, _ = market
    group = {
        "stopAlls": [row(90, 94, number=1)],
        "sZones": [row(30, 100), row(60, 110), row(110, 101), row(140, 105)],
    }
    result = positions(group)
    assert [(p["type"], p["anchorSourceTime"]) for p in result] == [
        ("1.1" + suffix, 30),
        ("2.1" + suffix, 90),
        ("1.1" + suffix, 110),
    ]


def test_stopall_first_eligible_t_owner_and_primary_reset(market):
    primary, suffix, row, positions, _ = market
    group = {
        "stopAlls": [row(30, 100, number=1), row(50, 95, number=2, verdict="F"),
                     row(90, 85, number=3), row(230, 75, number=1)],
        "sZones": [row(70, 115), row(110, 112), row(250, 110)],
        primary: [row(170, 80, number=2)],
    }
    result = positions(group)
    assert [(p["type"], p["anchorSourceTime"]) for p in result if p["type"].startswith("2.")] == [
        ("2.1" + suffix, 90), ("2.1" + suffix, 230),
    ]


def test_primary_three_requires_no_primary_one_entry_and_respects_stops(market):
    primary, suffix, row, positions, price = market
    group = {primary: [row(30, 100, number=1), row(100, 90, number=2),
                       row(180, 80, number=3)]}
    result = positions(group, [(170, 88)])
    assert [(p["type"], p["entryTime"], p["stopPrice"]) for p in result] == [
        ("3.2" + suffix, 100, price(90)), ("3.3" + suffix, 180, price(80)),
    ]
    assert [p["type"] for p in positions(group)] == ["3.2" + suffix]
    group["sZones"] = [row(60, 100), row(70, 110)]
    assert [p["type"] for p in positions(group) if p["type"].startswith("3.")] == ["3.1" + suffix]
    result = [p for p in positions(group, [(96, 99), (170, 88)]) if p["type"].startswith("3.")]
    assert [p["type"] for p in result] == ["3.1" + suffix, "3.2" + suffix]
    assert result[0]["triggerSourceTime"] == 70


def test_stop_before_s_formation_does_not_draw_or_enable_second_stage(market):
    _, _, row, positions, _ = market
    group = {"stopAlls": [row(30, 100, number=1), row(110, 90, number=2, verdict="F")],
             "sZones": [row(70, 110), row(140, 112)]}
    assert not positions(group, [(60, 99)])


def test_nearest_stopall_owns_s_even_if_its_confirmation_is_later(market):
    _, _, row, positions, _ = market
    group = {
        "stopAlls": [row(30, 100, number=1), row(60, 90, number=2, decision=120, verdict="F")],
        "sZones": [row(90, 115)],
    }
    assert not positions(group, through=105)


def test_first_confirmed_s_supplies_entry_in_source_window(market):
    _, suffix, row, positions, _ = market
    group = {
        "stopAlls": [row(30, 100, number=1)],
        "sZones": [row(60, 110, decision=110), row(80, 112, decision=90)],
    }
    first = positions(group, through=100)
    assert first == positions(group, through=120)
    assert [(p["type"], p["triggerSourceTime"]) for p in first] == [("2.1" + suffix, 80)]


def test_regime_cutoff_caps_pending_confirmation_and_followup_stop(market):
    _, suffix, row, positions, _ = market
    group = {
        "calculationEndTime": 110,
        "stopAlls": [row(30, 100, number=1), row(90, 90, number=2, verdict="F")],
        "sZones": [row(60, 110), row(100, 112, decision=110)],
    }
    result = positions(group, [(115, 99)])
    assert [p["type"] for p in result] == ["2.1" + suffix]
    assert not result[0].get("stopEventTime")
