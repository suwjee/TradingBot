"""Project independent primary cycles without making trading decisions."""
from datetime import datetime,timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace as NS
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"bridge"))
from trading_pipeline import serialize_primary_structures
from PL_PH_detector import StructureOrder,MatchingBehaviorLeg,PrimaryPoint

BASE=datetime(2026,1,1)


def independent_results(*, coincident=False):
    candles=[NS(timestamp=BASE+timedelta(seconds=30*i)) for i in range(150)]
    market=NS(candles=candles,start_index=0,end_index=149,
              chronology=NS(timeframe=timedelta(seconds=30)))
    def cycle(reference,second,source,gate,decision,status):
        identity=f"bearish:cycle:{reference}:{second}"
        order=StructureOrder("bullish",1,gate,gate,candles[gate].timestamp,
            Decimal("90"),gate,decision,candles[decision].timestamp,("parent-stop",))
        point=PrimaryPoint(kind="PH",number=1,source_index=gate,source_time=candles[gate].timestamp,
            price=Decimal("110"),trigger_index=gate,trigger_event_time=candles[gate].timestamp,
            decision_index=decision,decision_event_time=candles[decision].timestamp,
            order=order,cycle_id=identity)
        leg=MatchingBehaviorLeg(source,candles[source].timestamp,Decimal("80"),
            reference,second,gate,candles[gate].timestamp,None,None)
        return NS(highs=[point],lows=[],mbl=leg,status=status,
                  post_pl3_orders=[],cycle_id=identity,
                  qualification_event_time=candles[second].timestamp)
    first=cycle(2,5,7,20 if coincident else 8,23 if coincident else 10,"waiting-for-structure-break")
    second=cycle(15,17,18,20,23,"waiting-for-ph-order-stop")
    aggregate=NS(highs=[*first.highs,*second.highs],lows=[],mbl=first.mbl,
        status=second.status,post_pl3_orders=[],cycles=[first,second],cycle_id=None,
        qualification_event_time=first.qualification_event_time)
    return aggregate,market


def test_independent_cycles_publish_both_immutable_legs_and_number_one_highs():
    result,market=independent_results()
    payload=serialize_primary_structures(result,market)
    assert [leg["referenceStopAllIndex"] for leg in payload["matchingBehaviorLegs"]]==[2,15]
    assert [point["number"] for point in payload["primaryHighs"]]==[1,1]
    assert [point["cycleId"] for point in payload["primaryHighs"]]==["bearish:cycle:2:5","bearish:cycle:15:17"]
    assert [leg["cycleId"] for leg in payload["matchingBehaviorLegs"]]==["bearish:cycle:2:5","bearish:cycle:15:17"]


def test_coincident_cycle_points_publish_one_owner_with_both_cycle_memberships():
    result,market=independent_results(coincident=True)
    payload=serialize_primary_structures(result,market)
    rows=payload["primaryHighs"]
    assert len(rows)==1
    assert rows[0]["id"]=="bearish:PH:1:20:23"
    assert rows[0]["cycleIds"]==["bearish:cycle:2:5","bearish:cycle:15:17"]
    assert [c["highIds"] for c in payload["primaryCycles"]]==[[rows[0]["id"]],[rows[0]["id"]]]
    assert [c["highCount"] for c in payload["primaryCycles"]]==[1,1]


def test_visible_window_keeps_numbering_from_earlier_confirmed_highs():
    from dataclasses import replace
    result,market=independent_results()
    result.highs[0]=replace(result.highs[0],number=4)
    result.cycles[0].highs=[result.highs[0]]
    result.highs[1]=replace(result.highs[1],price=Decimal("120"))
    result.cycles[1].highs=[result.highs[1]]
    market.start_index=19
    rows=serialize_primary_structures(result,market)["primaryHighs"]
    assert [(r["number"],r["sourceIndex"]) for r in rows]==[(5,20)]


def test_later_higher_role_keeps_the_first_physical_id_across_horizons():
    from dataclasses import replace
    result,market=independent_results(coincident=True)
    later=replace(result.highs[1],number=4,decision_index=30,
                  decision_event_time=market.candles[30].timestamp)
    result.highs[1]=later
    result.cycles[1].highs=[later]
    market.end_index=25
    earlier=serialize_primary_structures(result,market)["primaryHighs"]
    market.end_index=30
    final=serialize_primary_structures(result,market)["primaryHighs"]
    assert [(p["id"],p["number"]) for p in earlier]==[("bearish:PH:1:20:23",1)]
    assert [(p["id"],p["number"]) for p in final]==[("bearish:PH:1:20:23",4)]
    assert final[0]["decisionIndex"]==30
    assert final[0]["cycleId"]=="bearish:cycle:15:17"


def test_cycle_metadata_and_leg_visibility_follow_each_activation_horizon():
    result,market=independent_results()
    market.end_index=19
    payload=serialize_primary_structures(result,market)
    assert len(payload["matchingBehaviorLegs"])==1
    assert len(payload["primaryCycles"])==1
    assert payload["primaryCycles"][0]["id"]=="bearish:cycle:2:5"
    assert payload["primaryCycles"][0]["status"]=="waiting-for-structure-break"
    assert payload["primaryCycles"][0]["highCount"]==1
    assert payload["primaryStatus"]=="waiting-for-structure-break"
    assert payload["matchingBehaviorLegs"][0]["capTime"]-payload["matchingBehaviorLegs"][0]["sourceTime"]==3000


def test_post_pl3_order_usage_retains_each_independent_cycle_identity():
    result,market=independent_results()
    shared=result.highs[1].order
    for cycle in result.cycles:cycle.post_pl3_orders=[shared]
    result.post_pl3_orders=[shared]
    rows=serialize_primary_structures(result,market)["postPL3Orders"]
    assert len(rows)==2
    assert {row["cycleId"] for row in rows}=={"bearish:cycle:2:5","bearish:cycle:15:17"}


def test_prequalification_horizon_does_not_report_a_future_cycle_status():
    result,market=independent_results()
    market.end_index=4
    payload=serialize_primary_structures(result,market)
    assert payload["primaryCycles"]==[]
    assert payload["primaryStatus"]=="waiting-for-matching-behaviors"


def test_qualified_but_unbroken_horizon_reports_waiting_for_the_reference_break():
    result,market=independent_results()
    market.end_index=6
    payload=serialize_primary_structures(result,market)
    assert payload["primaryCycles"]==[]
    assert payload["primaryStatus"]=="waiting-for-stopall-break"


def test_matching_leg_is_not_formed_before_its_first_ph_confirmation():
    result,market=independent_results()
    market.end_index=9
    before=serialize_primary_structures(result,market)
    assert before["matchingBehaviorLegs"]==[]
    assert len(before["primaryCycles"])==1
    market.end_index=10
    formed=serialize_primary_structures(result,market)["matchingBehaviorLegs"]
    assert len(formed)==1
    assert formed[0]["confirmationIndex"]==10
    assert formed[0]["confirmationEventTime"]==serialize_primary_structures(result,market)["primaryHighs"][0]["decisionEventTime"]


def test_matching_leg_without_any_confirmed_ph_never_becomes_public():
    result,market=independent_results()
    for cycle in result.cycles:cycle.highs=[]
    result.highs=[]
    assert serialize_primary_structures(result,market)["matchingBehaviorLegs"]==[]


def test_another_cycles_ph_does_not_confirm_a_still_pending_matching_leg():
    result,market=independent_results()
    market.end_index=21
    payload=serialize_primary_structures(result,market)
    assert len(payload["primaryCycles"])==2
    assert [leg["referenceStopAllIndex"] for leg in payload["matchingBehaviorLegs"]]==[2]
