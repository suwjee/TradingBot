"""First strict PH3 stop terminates the complete bearish regime."""
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"bridge"))

from test_pl_ph_detector import fixture, initial, order, run


def three_highs(last_high="130", crossing="131"):
    values = fixture(initial({12:("111","90"),13:("120","90"),
        16:("121","90"),17:(last_high,"90"),20:(crossing,"90"),
        21:("140","90")}))
    choices = {("PH",8):[(10,)],("PH",12):[(14,)],
               ("PH",16):[(18,)],("PH",20):[(22,)]}
    return values, choices


def test_first_strict_ph3_stop_reverses_without_committing_ph4():
    values, choices = three_highs()
    result = run(values, choices)
    assert [point.number for point in result.highs] == [1,2,3]
    assert result.transition.index == 20
    assert result.transition.event_time == values[0].times[20]
    assert result.transition.level == Decimal("130")
    assert result.status == "reversed-to-bullish"


def test_equal_ph3_high_does_not_reverse_until_a_strict_crossing():
    values, choices = three_highs(crossing="130")
    result = run(values, choices)
    assert result.transition.index == 21
    assert [point.number for point in result.highs] == [1,2,3]


def test_no_later_strict_crossing_preserves_three_highs_without_transition():
    values, choices = three_highs(crossing="130")
    chronology = values[0]
    chronology.candles[21].high = Decimal("130")
    # Build fresh chronology indexes after changing the fixture's immutable input.
    from reaction_engine import MarketChronology
    values = (MarketChronology(chronology.candles,list(chronology.candles),30),*values[1:])
    result = run(values, choices)
    assert result.transition is None
    assert [point.number for point in result.highs] == [1,2,3]


def test_order_resolver_is_not_asked_for_ph4_after_reversal():
    from PL_PH_detector import detect_bearish
    values, choices = three_highs()
    calls = []
    def resolve(kind, number, index, event):
        calls.append((kind,number,event))
        return [order(values[0],index,*args) for args in choices.get((kind,index),[])]
    result = detect_bearish(*values,resolve)
    assert result.transition.index == 20
    assert not any(kind == "PH" and number > 3 for kind,number,_ in calls)


def test_first_ph3_stop_is_selected_across_independent_cycle_owners():
    from types import SimpleNamespace as NS
    from PL_PH_detector import first_bullish_transition
    from test_primary_high_numbering import high
    values = fixture({10:("110","90"),16:("100","90"),
                      19:("100","90"),20:("101","90"),22:("111","90")})
    result = NS(highs=[high(3,10,12,"110","first"),high(3,16,18,"100","second")])
    transition = first_bullish_transition(values[0],result)
    assert transition.index == 20
    assert transition.high.cycle_id == "second"


def test_later_qualified_cycles_cannot_activate_after_the_global_reversal():
    from types import SimpleNamespace as NS
    values, choices = three_highs()
    values[3].append(NS(source_index=24,source_time=values[0].times[24],
        decision_event_time=values[0].times[24],number=4,price=Decimal("99")))
    values[1].extend(NS(source_index=i,source_time=values[0].times[i],
        decision_event_time=values[0].times[i],color="red") for i in (25,27))
    result = run(values,choices)
    assert result.transition.index == 20
    assert len(result.cycles) == 1


def test_pretransition_horizon_does_not_publish_a_completed_reversal_status():
    from types import SimpleNamespace as NS
    from trading_pipeline import serialize_primary_structures
    values, choices = three_highs()
    result = run(values,choices)
    context = NS(candles=values[0].candles,chronology=values[0],start_index=0,end_index=19)
    status = serialize_primary_structures(result,context)["primaryStatus"]
    assert status not in {"reversed-to-bullish","stopped-on-trend-reversal"}
