"""User-specified bearish primary structures, independent of Order discovery."""
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace as NS
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from reaction_engine import MarketChronology


BASE = datetime(2026, 1, 1)


def fixture(changes=None, size=32):
    candles = []
    for i in range(size):
        high, low = (changes or {}).get(i, ("100" if i < 3 else "99", "90"))
        candles.append(NS(index=i, timestamp=BASE + timedelta(seconds=30*i),
                          high=Decimal(high), low=Decimal(low),
                          open=Decimal(low), close=Decimal(high), tag="GREEN"))
    chronology = MarketChronology(candles, candles, 30)
    def event(i, **kw):
        return NS(source_index=i, source_time=candles[i].timestamp,
                  decision_event_time=candles[i].timestamp,
                  calculation_valid=True, **kw)
    stops = [event(i, number=i+1, price=Decimal("100")) for i in range(3)]
    behaviors = [event(i, color="red") for i in (3, 5)]
    return chronology, behaviors, [], stops


def order(chronology, gate, stop, cause="parent-stop", direction="bearish"):
    from PL_PH_detector import StructureOrder
    return StructureOrder(direction=direction, reaction_number=1,
        first_index=gate+1, break_index=gate+1,
        confirmation_event_time=chronology.times[gate+1],
        stop_level=Decimal("100"), stop_source_index=gate+1,
        stop_index=stop, stop_event_time=chronology.times[stop],
        causes=(cause,))


def run(values, choices):
    from PL_PH_detector import detect_bearish
    chronology = values[0]
    def resolve(kind, number, index, event):
        return [order(chronology, index, *args) for args in choices.get((kind, index), [])]
    return detect_bearish(*values, resolve)


def initial(extra=None):
    return {7:("99","80"), 8:("101","85"), 9:("110","90"), **(extra or {})}


def test_ph_source_differs_from_confirmation_and_mbl_is_inclusive():
    result = run(fixture(initial()), {("PH",8):[(10,)]})
    assert [(p.number,p.source_index,p.decision_index,p.price) for p in result.highs] == [(1,9,10,Decimal("110"))]
    assert (result.mbl.source_index,result.mbl.price) == (7,Decimal("80"))


def test_reference_equality_does_not_open_ph_space():
    assert run(fixture({8:("100","80")}), {}).mbl is None


def test_second_behavior_and_break_candles_belong_to_mbl_range():
    for source in (5,8):
        result = run(fixture(initial({source:("101" if source==8 else "99","75")})), {})
        assert result.mbl.source_index == source


def test_later_stopall_does_not_cancel_an_already_qualified_matching_leg():
    values = fixture(initial())
    values[3].append(NS(source_index=6,source_time=values[0].times[6],
        decision_event_time=values[0].times[6],number=1,price=Decimal("200")))
    assert len(run(values,{("PH",8):[(10,)]}).highs) == 1


def test_highs_continue_through_four_and_beyond():
    extra={12:("111","90"),13:("120","90"),16:("121","90"),17:("130","90"),20:("131","90"),21:("140","90")}
    result=run(fixture(initial(extra)),{("PH",8):[(10,)],("PH",12):[(14,)],("PH",16):[(18,)],("PH",20):[(22,)]})
    assert [p.number for p in result.highs] == [1,2,3,4]


def test_first_stopped_order_wins_regardless_of_formation_order():
    result=run(fixture(initial()),{("PH",8):[(13,),(10,"reset-leg")]})
    assert result.highs[0].decision_index == 10
    assert result.highs[0].order.causes == ("reset-leg",)


def test_equal_extrema_choose_first_candle():
    result=run(fixture(initial({6:("99","80"),10:("110","90")})),{("PH",8):[(11,)]})
    assert result.highs[0].source_index == 9
    assert result.mbl.source_index == 6


def test_mbl_break_cancels_pending_first_high_and_opens_low():
    result=run(fixture(initial({10:("99","79"),11:("99","70")})),{("PH",8):[(12,)],("PL",10):[(14,"reset-leg","bullish")]})
    assert result.highs == []
    assert [(p.number,p.source_index) for p in result.lows] == [(1,11)]


def test_mbl_break_cancels_pending_second_high():
    result=run(fixture(initial({12:("111","90"),14:("99","79"),15:("99","60")})),{("PH",8):[(10,)],("PH",12):[(16,)],("PL",14):[(17,"reset-leg","bullish")]})
    assert [p.number for p in result.highs] == [1]
    assert result.lows[0].source_index == 15


def test_high_break_before_low_confirmation_cancels_low_and_continues_ph():
    result=run(fixture(initial({12:("99","79"),14:("111","90"),15:("120","90")})),{("PH",8):[(10,)],("PL",12):[(18,"reset-leg","bullish")],("PH",14):[(16,)]})
    assert result.lows == []
    assert [p.number for p in result.highs] == [1,2]


def test_ph_reset_preserves_mbl_and_pl_number_and_previous_low_gate():
    extra={12:("99","79"),13:("99","70"),16:("111","90"),17:("120","90"),20:("99","75"),22:("99","69"),23:("99","60")}
    result=run(fixture(initial(extra)),{("PH",8):[(10,)],("PL",12):[(14,"reset-leg","bullish")],("PH",16):[(18,"reset-leg")],("PL",22):[(24,"parent-stop","bullish")]})
    assert [p.number for p in result.highs] == [1,1]
    assert [p.number for p in result.lows] == [1,2]
    assert result.lows[-1].trigger_index == 22
    assert (result.mbl.source_index,result.mbl.price)==(7,Decimal("80"))


def test_incomplete_order_does_not_create_a_point():
    assert run(fixture(initial()),{}).highs == []


def test_mbl_equality_does_not_cancel_pending_high():
    result=run(fixture(initial({10:("99","80")})),{("PH",8):[(12,)]})
    assert len(result.highs)==1


def test_matching_excludes_different_e_numbers():
    values=fixture(initial())
    values[1].clear()
    for i,n in ((3,1),(5,2)):
        values[2].append(NS(source_index=i,source_time=values[0].times[i],
            decision_event_time=values[0].times[i],family="red",number=n))
    assert run(values,{}).mbl is None


def test_stopall_donor_is_not_an_independent_matching_behavior():
    values=fixture(initial())
    values[3].append(NS(source_index=5,source_time=values[0].times[5],
        decision_event_time=values[0].times[5],number=1,price=Decimal("100")))
    assert run(values,{}).mbl is None


def test_native_order_a_uses_canonical_direction_stop_and_identity():
    from PL_PH_detector import NativePrimaryOrders
    from test_order_audit_lifecycle_contracts import detector_state, moment
    from lifecycle_engine import module_priority
    service, _, physical = detector_state("bearish")
    resolver=NativePrimaryOrders(service.chronology, {"bearish":{"OrderAudit":[accepted_order(service, physical)]}})
    matches=resolver("PH",2,4,moment(125))
    assert len(matches)==1
    actual=matches[0]
    assert (actual.direction,actual.first_index,actual.break_index)==("bullish",physical.first_idx,physical.break_idx)
    assert (actual.stop_level,actual.stop_event_time)==(Decimal("100"),moment(215))
    assert actual.causes == ("parent-stop",)


def test_canonical_reaction_without_accepted_audit_is_not_an_order():
    from PL_PH_detector import NativePrimaryOrders
    from test_order_audit_lifecycle_contracts import detector_state, moment
    from lifecycle_engine import module_priority
    service, _, _ = detector_state("bearish")
    resolver=NativePrimaryOrders(service.chronology, {"bullish":{"OrderAudit":[]}})
    assert resolver("PL",1,4,moment(125)) == []


def test_initial_low_accepts_order_a_after_first_valid_bearish_reaction():
    from dataclasses import replace
    from PL_PH_detector import NativePrimaryOrders
    from test_order_audit_lifecycle_contracts import detector_state, moment, candidate
    from lifecycle_engine import module_priority
    service, _, physical = detector_state("bullish")
    resolver=NativePrimaryOrders(service.chronology, {"bullish":{"OrderAudit":[accepted_order(service, physical)]}})
    matches=resolver("PL",1,4,moment(125))
    assert len(matches)==1
    assert matches[0].direction=="bearish"
    assert matches[0].stop_event_time==moment(215)
    assert matches[0].causes==("parent-stop",)


def accepted_order(service, reaction, cause="parent-stop"):
    level,source,source_time=service.order_stop(1,reaction)
    return {"reaction":reaction,"entry":{"reaction_number":1,
        "stop_level":level,"stop_source_index":source,"stop_source_time":source_time},
        "crossed":service.cross_order(service.chronology.reaction_confirmation(service.order_direction,reaction),level),
        "causes":[{"kind":cause}]}


def test_ph_after_first_excludes_reset_leg_only_order_b():
    from PL_PH_detector import NativePrimaryOrders
    from test_order_audit_lifecycle_contracts import detector_state, moment
    service,_,physical=detector_state("bearish")
    resolver=NativePrimaryOrders(service.chronology,{"bearish":{"OrderAudit":[accepted_order(service,physical,"reset-leg")]}})
    assert resolver("PH",2,4,moment(125)) == []
    assert resolver("PH",1,4,moment(125))[0].causes == ("reset-leg",)


def test_after_pl3_break_evaluates_orders_without_inventing_pl4():
    extra={12:("99","79"),13:("99","70"),16:("99","69"),17:("99","60"),20:("99","59"),21:("99","50"),24:("99","49"),25:("99","40")}
    result=run(fixture(initial(extra)),{("PH",8):[(10,)],("PL",12):[(14,"parent-stop","bearish")],("PL",16):[(18,"parent-stop","bearish")],("PL",20):[(22,"parent-stop","bearish")],("PL",24):[(26,"parent-stop","bearish")]})
    assert [p.number for p in result.lows] == [1,2,3]
    assert len(result.post_pl3_orders)==1


def test_pl_first_valid_a_is_not_replaced_because_it_has_not_stopped():
    from dataclasses import replace
    from PL_PH_detector import NativePrimaryOrders
    from test_order_audit_lifecycle_contracts import detector_state, moment
    service,_,physical=detector_state("bullish")
    earlier=accepted_order(service,physical)
    earlier["crossed"]=None
    later=accepted_order(service,physical)
    later["reaction"]=replace(physical,first_idx=6)
    resolver=NativePrimaryOrders(service.chronology,{"bullish":{"OrderAudit":[earlier,later]}})
    assert resolver("PL",1,4,moment(125)) == []


def test_lower_timeframe_orders_opposing_breaks_inside_one_main_candle():
    values=fixture(initial({12:("111","79"),13:("99","60")}))
    main=values[0].candles
    lower=[]
    for candle in main:
        for n in range(6):
            high,low=candle.high,candle.low
            if candle.index==12:
                high,low=(Decimal("111"),Decimal("90")) if n==0 else (Decimal("99"),Decimal("79"))
            lower.append(NS(index=len(lower),timestamp=candle.timestamp+timedelta(seconds=5*n),
                            high=high,low=low))
    fine=MarketChronology(main,lower,30)
    result=run((fine,*values[1:]),{("PH",8):[(10,)],("PH",12):[(14,)],("PL",12):[(15,"reset-leg","bearish")]})
    assert [point.number for point in result.highs] == [1]
    assert result.lows[0].trigger_event_time == main[12].timestamp+timedelta(seconds=5)
    assert result.lows[0].source_index == 13


def test_equal_raw_timestamp_does_not_invent_boundary_ordering():
    result=run(fixture(initial({10:("99","79")})),{("PH",8):[(10,)]})
    assert result.highs == []
    assert result.status == "ambiguous-raw-boundary-order"


def test_stopall_confirmation_cannot_be_used_before_it_exists():
    values=fixture(initial())
    values[3][-1].decision_event_time=values[0].times[10]
    assert run(values,{}).mbl is None


def test_selected_native_order_preserves_full_cause_and_reaction_mode():
    from PL_PH_detector import NativePrimaryOrders
    from test_order_audit_lifecycle_contracts import detector_state, moment
    service,_,physical=detector_state("bearish")
    prepared=accepted_order(service,physical)
    prepared["causes"]=[{"kind":"parent-stop","parentType":"A",
                         "parentSourceTime":moment(75),"eventTime":moment(125),
                         "physicalOrderIdentity":[5,6]}]
    resolver=NativePrimaryOrders(service.chronology,{"bearish":{"OrderAudit":[prepared]}})
    selected=resolver("PH",1,4,moment(125))[0]
    assert selected.reaction_mode==physical.mode
    assert selected.audit_causes==tuple(prepared["causes"])
    prepared["causes"][0]["parentType"]="changed"
    assert selected.audit_causes[0]["parentType"]=="A"
    prepared["causes"][0]["physicalOrderIdentity"][0]=-1
    assert selected.audit_causes[0]["physicalOrderIdentity"]==[5,6]


def test_ph_cancel_cannot_order_opposing_breaks_inside_one_raw_candle():
    result=run(fixture(initial({12:("111","90"),14:("111","79"),15:("99","60")})),
        {("PH",8):[(10,)],("PH",12):[(16,)],("PL",14):[(17,"reset-leg")]})
    assert result.status=="ambiguous-raw-boundary-order"
    assert result.lows==[]
    assert [point.number for point in result.highs]==[1]


def test_pl_cancel_cannot_order_opposing_breaks_inside_one_raw_candle():
    result=run(fixture(initial({12:("99","79"),14:("111","79"),15:("120","90")})),
        {("PH",8):[(10,)],("PL",12):[(18,"reset-leg")],("PH",14):[(16,)]})
    assert result.status=="ambiguous-raw-boundary-order"
    assert [point.number for point in result.highs]==[1]


def test_post_pl3_high_transition_also_requires_resolvable_raw_order():
    extra={12:("99","79"),13:("99","70"),16:("99","69"),17:("99","60"),20:("99","59"),21:("99","50"),24:("99","49"),26:("111","49"),27:("120","90")}
    result=run(fixture(initial(extra)),{("PH",8):[(10,)],("PL",12):[(14,"parent-stop")],("PL",16):[(18,"parent-stop")],("PL",20):[(22,"parent-stop")],("PH",26):[(28,)]})
    assert result.status=="ambiguous-raw-boundary-order"
    assert [point.number for point in result.highs]==[1]


def test_lower_priority_intervening_e_does_not_break_matching_s():
    values=fixture(initial())
    values[2].append(NS(source_index=4,source_time=values[0].times[4],
        decision_event_time=values[0].times[4],family="blue",number=3))
    assert run(values,{}).mbl is not None


def test_higher_priority_owner_replacement_restarts_matching_count():
    values=fixture(initial())
    values[2].append(NS(source_index=4,source_time=values[0].times[4],
        decision_event_time=values[0].times[4],family="red",number=1))
    assert run(values,{}).mbl is None


def test_two_matching_behaviors_before_stopall_three_are_insufficient():
    values=fixture(initial())
    values[3][-1].number=2
    assert run(values,{}).mbl is None


def later_setup(*, old_break=None):
    changes={i:("89","80") for i in range(10,32)}
    changes.update({4:("101","90"),10:("90","80"),15:("91","78"),16:("95","80")})
    if old_break is not None:
        changes[old_break]=("101","80")
    values=fixture(changes)
    values[3].append(NS(source_index=10,source_time=values[0].times[10],
        decision_event_time=values[0].times[10],number=4,price=Decimal("90")))
    values[1].extend(NS(source_index=i,source_time=values[0].times[i],
        decision_event_time=values[0].times[i],color="red") for i in (11,13))
    return values


def test_unbroken_first_setup_does_not_block_later_qualified_leg():
    result=run(later_setup(),{("PH",15):[(18,)]})
    assert len(result.highs)==1
    assert (result.highs[0].trigger_index,result.highs[0].source_index)==(15,16)
    assert result.mbl.reference_stopall_index==10
    assert result.mbl.price==Decimal("78")


def test_first_actual_break_wins_over_first_qualification():
    result=run(later_setup(old_break=20),{("PH",15):[(18,)]})
    assert result.highs, "The later qualified setup must not be ignored."
    assert result.highs[0].trigger_index==15
    assert result.mbl.reference_stopall_index==10


def test_earlier_setup_remains_eligible_after_later_numbered_stopall():
    values=fixture({10:("101","85")})
    values[3].append(NS(source_index=10,source_time=values[0].times[10],
        decision_event_time=values[0].times[10],number=4,price=Decimal("101")))
    values[1].extend(NS(source_index=i,source_time=values[0].times[i],
        decision_event_time=values[0].times[i],color="red") for i in (11,13))
    result=run(values,{("PH",10):[(12,)]})
    assert result.highs[0].trigger_index==10
    assert result.mbl.reference_stopall_index==2


def test_confirmed_ph_replaces_only_the_same_stopall_candle():
    from PL_PH_detector import resolve_stopall_ownership
    values=fixture(initial())
    result=run(values,{("PH",8):[(10,)]})
    promoted=NS(source_index=9,source_time=values[0].times[9],number=4)
    different_candle=NS(source_index=9,source_time=values[0].times[9]+timedelta(days=1),number=5)
    history=[*values[3],promoted,different_candle]
    remaining=resolve_stopall_ownership(history,result,through_index=31)
    assert remaining==[*values[3],different_candle]
    assert history[-2] is promoted, "Historical calculation provenance must be retained."
    assert [point.kind for point in result.highs]==["PH"]


def test_future_ph_confirmation_does_not_erase_stopall_from_an_earlier_window():
    from PL_PH_detector import resolve_stopall_ownership
    values=fixture(initial())
    result=run(values,{("PH",8):[(10,)]})
    promoted=NS(source_index=9,source_time=values[0].times[9],number=4)
    assert resolve_stopall_ownership([promoted],result,through_index=9)==[promoted]
    assert resolve_stopall_ownership([promoted],result,through_index=10)==[]


def test_unconfirmed_ph_space_does_not_replace_stopall():
    from PL_PH_detector import resolve_stopall_ownership
    values=fixture(initial())
    pending=run(values,{})
    existing=NS(source_index=9,source_time=values[0].times[9],number=4)
    assert pending.highs==[]
    assert resolve_stopall_ownership([existing],pending,through_index=31)==[existing]


def test_confirmed_high_is_committed_before_resolving_its_next_order():
    from PL_PH_detector import detect_bearish
    values=fixture(initial({12:("111","90"),13:("120","90")}))
    class CausalOrders:
        def __init__(self):
            self.confirmed=[]
        def confirm_high(self, point):
            self.confirmed.append(point)
        def __call__(self, kind, number, gate, event):
            if (kind,gate)==("PH",8):
                return [order(values[0],8,10)]
            if (kind,gate)==("PH",12) and self.confirmed:
                return [order(values[0],12,14)]
            return []
    result=detect_bearish(*values,CausalOrders())
    assert [(point.number,point.source_index) for point in result.highs]==[(1,9),(2,13)]


def serialized_leg(*, source=10, size=140, gap=False):
    from PL_PH_detector import MatchingBehaviorLeg, PrimaryResult, PrimaryPoint, StructureOrder
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"bridge"))
    from trading_pipeline import serialize_primary_structures
    candles=[NS(timestamp=BASE+timedelta(seconds=30*i+(172800 if gap and i>=50 else 0)))
             for i in range(size)]
    leg=MatchingBehaviorLeg(source,candles[source].timestamp,Decimal("80"),2,5,
        source,candles[source].timestamp,None,None)
    market=NS(candles=candles,start_index=0,end_index=size-1,
              chronology=NS(timeframe=timedelta(seconds=30)))
    accepted=StructureOrder("bullish",1,source,source,candles[source].timestamp,
        Decimal("85"),source,source,candles[source].timestamp,("parent-stop",))
    high=PrimaryPoint("PH",1,source,candles[source].timestamp,Decimal("90"),
        source,candles[source].timestamp,source,candles[source].timestamp,accepted)
    return serialize_primary_structures(PrimaryResult(mbl=leg,highs=[high]),market)["matchingBehaviorLegs"][0]


def test_mbl_extension_is_one_hundred_actual_candles_across_session_gap():
    from zoneinfo import ZoneInfo
    row=serialized_leg(gap=True)
    expected=int((BASE+timedelta(seconds=176100)).replace(tzinfo=ZoneInfo("Asia/Tehran")).timestamp())
    assert row["capTime"]==expected


def test_mbl_extension_extrapolates_one_hundred_slots_when_history_ends():
    from zoneinfo import ZoneInfo
    row=serialized_leg(source=28,size=30)
    expected=int((BASE+timedelta(seconds=3840)).replace(tzinfo=ZoneInfo("Asia/Tehran")).timestamp())
    assert row["capTime"]==expected


def test_ph_can_use_an_earlier_first_confirmed_at_the_structure_break():
    from dataclasses import replace
    from PL_PH_detector import detect_bearish
    values=fixture(initial({9:("100","90")}))
    eligible=replace(order(values[0],8,10),first_index=6,break_index=8,
                     confirmation_event_time=values[0].times[8])
    def resolve(kind,number,index,event):
        return [eligible] if (kind,index)==("PH",8) else []
    result=detect_bearish(*values,resolve)
    assert [(p.number,p.source_index,p.decision_index) for p in result.highs]==[(1,8,10)]
    assert result.highs[0].order.first_index==6


def test_native_ph_accepts_earlier_first_on_or_after_exact_gate_confirmation():
    from PL_PH_detector import NativePrimaryOrders
    from test_order_audit_lifecycle_contracts import detector_state,moment
    service,_,physical=detector_state("bearish")
    resolver=NativePrimaryOrders(service.chronology,{"bearish":{"OrderAudit":[accepted_order(service,physical)]}})
    for number in (1,2):
        for event in (moment(185),moment(190)):
            matches=resolver("PH",number,6,event)
            assert [(item.first_index,item.break_index) for item in matches]==[(5,6)]


def test_native_ph_rejects_confirmation_before_the_structure_break():
    from PL_PH_detector import NativePrimaryOrders
    from test_order_audit_lifecycle_contracts import detector_state,moment
    service,_,physical=detector_state("bearish")
    resolver=NativePrimaryOrders(service.chronology,{"bearish":{"OrderAudit":[accepted_order(service,physical)]}})
    assert resolver("PH",1,6,moment(195))==[]


def test_pl_does_not_inherit_the_clarified_ph_confirmation_gate():
    from PL_PH_detector import NativePrimaryOrders
    from test_order_audit_lifecycle_contracts import detector_state,moment
    service,_,physical=detector_state("bullish")
    resolver=NativePrimaryOrders(service.chronology,{"bullish":{"OrderAudit":[accepted_order(service,physical)]}})
    assert resolver("PL",1,6,moment(190))==[]


def overlapping_setups(extra=None):
    values=fixture(initial({10:("100","90"),14:("99","82"),
        15:("105","85"),16:("106","90"),20:("111","90"),
        21:("120","90"),**(extra or {})}))
    values[3].append(NS(source_index=10,source_time=values[0].times[10],
        decision_event_time=values[0].times[10],number=4,price=Decimal("100")))
    values[1].extend(NS(source_index=i,source_time=values[0].times[i],
        decision_event_time=values[0].times[i],color="red") for i in (11,13))
    return values


def test_overlapping_cycles_keep_both_high_sequences_and_immutable_legs():
    result=run(overlapping_setups(),{("PH",8):[(10,)],("PH",15):[(18,)],
        ("PH",20):[(22,)]})
    assert [(p.number,p.trigger_index,p.decision_index) for p in result.highs]==[
        (1,8,10),(1,15,18),(2,20,22),(2,20,22)]
    first,second=result.cycles
    assert [p.number for p in first.highs]==[1,2]
    assert [p.number for p in second.highs]==[1,2]
    assert [(cycle.mbl.source_index,cycle.mbl.price) for cycle in result.cycles]==[
        (7,Decimal("80")),(14,Decimal("82"))]
    assert result.mbl is first.mbl
    assert first.cycle_id != second.cycle_id
    assert all(p.cycle_id==cycle.cycle_id for cycle in result.cycles for p in cycle.highs)


def test_confirmed_ph_source_cannot_be_reused_as_a_stopall_cycle_reference():
    for first_confirmation in (10,14):
        values=overlapping_setups()
        reference=values[3][-1]
        reference.source_index=9
        reference.source_time=values[0].times[9]
        reference.decision_event_time=values[0].times[10]
        reference.price=Decimal("110")
        result=run(values,{("PH",8):[(first_confirmation,)],("PH",20):[(22,)]})
        assert [(point.number,point.source_index) for point in result.highs]==[(1,9),(2,21)]
        assert len(result.cycles)==1
        assert result.cycles[0].mbl.reference_stopall_index==2


def test_invalid_ph_reference_cycle_cannot_commit_native_order_causes():
    from PL_PH_detector import detect_bearish
    values=overlapping_setups()
    values[3][-1].source_index=9
    values[3][-1].source_time=values[0].times[9]
    values[3][-1].decision_event_time=values[0].times[10]
    committed=[]
    def resolve(kind,number,gate,event):
        return [order(values[0],gate,{8:10,20:22}[gate])] if kind=="PH" and gate in (8,20) else []
    resolve.confirm_high=committed.append
    detect_bearish(*values,resolve)
    assert [(point.number,point.source_index) for point in committed]==[(1,9),(2,21)]


def test_one_cycle_low_and_high_reset_do_not_reset_another_cycle():
    values=overlapping_setups({23:("99","81"),24:("99","80.5"),
        27:("121","90"),28:("125","90")})
    result=run(values,{("PH",8):[(10,)],("PH",15):[(18,)],
        ("PH",20):[(22,)],("PL",23):[(25,"parent-stop","bullish")],
        ("PH",27):[(29,)]})
    assert [p.number for p in result.highs]==[1,1,2,2,3,1]
    first,second=result.cycles
    assert first.lows==[]
    assert [p.number for p in second.lows]==[1]
    assert (first.mbl.price,second.mbl.price)==(Decimal("80"),Decimal("82"))


def test_native_callbacks_follow_global_decision_order_and_recheck_pending_orders():
    from PL_PH_detector import detect_bearish
    values=overlapping_setups()
    class SharedOrders:
        def __init__(self):
            self.confirmed=[]
        def confirm_high(self,point):
            self.confirmed.append(point)
        def __call__(self,kind,number,gate,event):
            if kind!="PH":
                return []
            if gate==8:
                # Initially this earlier cycle only has a late accepted Order.
                stopped=19 if any(p.trigger_index==15 for p in self.confirmed) else 24
                return [order(values[0],8,stopped)]
            if gate==15:
                return [order(values[0],15,18)]
            return []
    orders=SharedOrders()
    result=detect_bearish(*values,orders)
    assert [(p.trigger_index,p.decision_index) for p in result.highs]==[(15,18),(8,19)]
    assert [(p.trigger_index,p.decision_index) for p in orders.confirmed]==[(15,18),(8,19)]


def test_waiting_cycle_wakes_after_shared_native_order_acceptance_changes():
    from PL_PH_detector import detect_bearish
    values=overlapping_setups({25:("99","79")})
    class SharedOrders:
        def __init__(self):
            self.confirmed=[]
        def confirm_high(self,point):
            self.confirmed.append(point)
        def __call__(self,kind,number,gate,event):
            if (kind,gate)==("PH",15):
                return [order(values[0],15,18)]
            if (kind,gate)==("PH",8) and self.confirmed:
                return [order(values[0],8,19)]
            return []
    result=detect_bearish(*values,SharedOrders())
    assert [(p.trigger_index,p.decision_index) for p in result.highs]==[(15,18),(8,19)]


def test_repeated_matching_occurrences_do_not_manufacture_extra_cycles():
    values=overlapping_setups()
    # Duplicate accepted inputs retain their physical identity; later matching
    # repetitions under the same reference do not replace its first pair.
    values[3].append(values[3][-1])
    values[1].extend([values[1][-1],NS(source_index=14,source_time=values[0].times[14],
        decision_event_time=values[0].times[14],color="red")])
    result=run(values,{})
    assert [(c.mbl.reference_stopall_index,c.mbl.second_behavior_index) for c in result.cycles]==[(2,5),(10,13)]


def test_duplicate_first_occurrence_cannot_qualify_a_cycle():
    values=fixture(initial())
    values[1][:]=[values[1][0],values[1][0]]
    result=run(values,{("PH",8):[(10,)]})
    assert result.highs==[]
    assert result.cycles==[]


def test_qualification_provenance_preserves_earliest_pair_and_each_cycle():
    values=later_setup(old_break=20)
    result=run(values,{})
    assert result.qualification_event_time==values[0].times[5]
    assert [cycle.qualification_event_time for cycle in result.cycles]==[
        values[0].times[13],values[0].times[5]]


def test_qualified_unbroken_setup_retains_qualification_provenance():
    values=fixture()
    result=run(values,{})
    assert result.cycles==[]
    assert result.status=="waiting-for-stopall-break"
    assert result.qualification_event_time==values[0].times[5]
    values[1].clear()
    assert run(values,{}).qualification_event_time is None


def test_qualification_provenance_uses_exact_decision_order_not_source_order():
    values=later_setup(old_break=26)
    values[1][1].decision_event_time=values[0].times[25]
    result=run(values,{})
    assert result.qualification_event_time==values[0].times[13]
    assert [cycle.qualification_event_time for cycle in result.cycles]==[
        values[0].times[13],values[0].times[25]]


def test_activation_equal_to_a_decision_preserves_both_contexts_deterministically():
    values=fixture(initial({6:("110","90"),7:("99","95"),
        8:("101","95"),10:("111","90")}))
    values[3].append(NS(source_index=6,source_time=values[0].times[6],
        decision_event_time=values[0].times[6],number=4,price=Decimal("110")))
    values[1].extend(NS(source_index=i,source_time=values[0].times[i],
        decision_event_time=values[0].times[i],color="red") for i in (7,8))
    result=run(values,{("PH",6):[(10,)],("PH",10):[(12,)]})
    assert [(p.trigger_index,p.decision_index) for p in result.highs]==[(6,10),(10,12)]
    assert [c.mbl.trigger_index for c in result.cycles]==[6,10]
    assert result==run(values,{("PH",6):[(10,)],("PH",10):[(12,)]})
