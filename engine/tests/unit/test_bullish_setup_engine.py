"""Approved bullish schematic rules, independently of detector construction."""
from datetime import datetime, timedelta
from decimal import Decimal as D
import importlib
from pathlib import Path
from types import SimpleNamespace as NS
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from reaction_engine import Candle, MarketChronology

BASE = datetime(2026, 1, 1)


class Market:
    def __init__(self, count=100):
        self.rows = [Candle(i, BASE + timedelta(seconds=5*i), "", "GREEN", D(110), D(115), D(105), D(110))
                     for i in range(count*6)]
        self.stops, self.s, self.e, self.pl = [], [], [], []

    def time(self, bar, offset=0):
        return BASE + timedelta(seconds=30*bar+offset)

    def low(self, bar, price, offset=0):
        from dataclasses import replace
        i = bar*6+offset//5
        self.rows[i] = replace(self.rows[i], low=D(price))

    def high(self, bar, price, offset=0):
        from dataclasses import replace
        i = bar*6+offset//5
        self.rows[i] = replace(self.rows[i], high=D(price))

    def stopall(self, number, source, decision, *, stop=None, price="100"):
        item = NS(direction="bullish", number=number, source_index=source,
                  source_time=self.time(source), price=D(price), decision_index=decision,
                  decision_time=self.time(decision), decision_event_time=self.time(decision, 5),
                  stop_event_time=self.time(stop, 5) if stop is not None else None,
                  stopped_behavior_key=f"StopAll{number-1}" if number>1 else "S blue")
        self.low(source, price)
        if stop is not None:
            self.low(stop, str(D(price)-D("0.01")), 5)
        self.stops.append(item)
        return item

    def behavior(self, source, decision, *, kind="S", color="blue", offset=10):
        item=NS(direction="bullish", source_index=source, source_time=self.time(source),
                decision_index=decision, decision_event_time=self.time(decision, offset),
                price=D(103), color=color, family=color, number=1)
        (self.s if kind=="S" else self.e).append(item)
        return item

    def primary(self, number, source, decision, *, price="90", cycle="first"):
        item=NS(kind="PL", number=number, source_index=source, source_time=self.time(source),
                decision_index=decision, decision_event_time=self.time(decision, 5),
                price=D(price), cycle_id=cycle)
        self.low(source, price)
        self.pl.append(item)
        return item

    def calculate(self, through=None):
        assert importlib.util.find_spec("bullish_setup_engine") is not None, "Bullish setup stage is missing"
        engine=importlib.import_module("bullish_setup_engine")
        candles=[]
        for i in range(len(self.rows)//6):
            rows=self.rows[i*6:(i+1)*6]
            candles.append(Candle(i, self.time(i), "", "GREEN", rows[0].open, max(r.high for r in rows),
                                  min(r.low for r in rows), rows[-1].close))
        chronology=MarketChronology(candles, self.rows, 30)
        return engine.calculate_bullish_setups(chronology, self.s, self.e, self.stops,
                                              self.pl, through_index=through)


def test_first_stopall_uses_first_behavior_confirmation_close_and_four_r():
    m=Market(); m.stopall(1,1,2); m.behavior(3,5); m.behavior(6,7)
    result=m.calculate()
    assert len(result.setups)==1
    setup=result.setups[0]
    assert (setup.anchor_kind,setup.anchor_number,setup.entry_index)==("StopAll",1,5)
    assert setup.entry_time==m.time(5) and setup.close_event_time==m.time(6)
    assert (setup.entry_price,setup.stop_price,setup.target_price)==(D(110),D(100),D(150))
    assert setup.behavior_source_time==m.time(3) and setup.width_bars==50


def test_only_original_one_to_two_path_enters_without_new_behavior():
    m=Market(); m.stopall(1,1,2,stop=6); m.behavior(3,4)
    m.stopall(2,7,8,stop=11,price="99"); m.stopall(3,12,13,stop=16,price="98")
    m.stopall(4,17,18,price="97")
    result=m.calculate()
    assert [(s.anchor_number,s.entry_index) for s in result.setups]==[(1,4),(2,8)]
    assert result.assessments[0].status=="F"
    assert [r.status for r in result.assessments]==["F","T","F",None]
    assert result.assessments[2].status_event_time==m.time(13,5)


def test_no_behavior_stop_stays_true_and_next_even_waits_for_behavior():
    m=Market();m.stopall(1,1,2,stop=6);m.behavior(3,4)
    m.stopall(2,7,8,stop=11,price="99");m.stopall(3,12,13,stop=16,price="98")
    m.stopall(4,17,18,price="97");m.behavior(19,20,color="red")
    assert [(s.anchor_number,s.entry_index) for s in m.calculate().setups]==[(1,4),(2,8),(4,20)]


def test_even_failure_relabels_prior_even_and_failed_behavior():
    m=Market();m.stopall(1,1,2,stop=6);m.behavior(3,4)
    m.stopall(2,7,8,stop=11,price="99");m.stopall(3,12,13,stop=16,price="98")
    m.stopall(4,17,18,stop=23,price="97");m.behavior(19,20,color="red")
    result=m.calculate()
    assert [r.status for r in result.assessments]==["F"]*4
    assert all(r.status=="F" for r in result.behaviors)
    before=m.calculate(22)
    assert before.assessments[1].status=="T"
    assert before.assessments[3].status is None


def test_successor_before_stop_confirms_true_without_waiting_for_stop():
    m=Market();m.stopall(1,1,2);m.behavior(3,4);m.stopall(1,6,7,price="102")
    result=m.calculate(8)
    assert result.assessments[0].status=="T"
    assert result.assessments[0].status_event_time==m.time(7,5)


def test_repeated_prefix_is_ignored_and_first_true_parity_has_priority():
    m=Market();m.stopall(1,1,2)
    m.stopall(1,10,11,stop=14)
    m.stopall(2,15,16,stop=19,price="99")
    m.stopall(3,20,21,stop=24,price="98")
    m.stopall(4,25,26,stop=29,price="97")
    m.stopall(5,30,31,stop=35,price="96");m.behavior(32,33)
    m.stopall(6,36,37,price="95");m.behavior(38,39)
    result=m.calculate()
    assert result.assessments[1].ignored_prefix
    assert [(s.anchor_number,s.entry_index) for s in result.setups]==[(6,39)]
    assert result.assessments[4].status=="T"


def test_fresh_scope_does_not_inherit_false_from_ignored_prefix():
    m=Market();m.stopall(1,1,2,stop=5);m.stopall(2,6,7,stop=9,price="99")
    m.stopall(3,10,11,stop=13,price="98")
    m.stopall(1,20,21,stop=24);m.behavior(22,23)
    m.stopall(2,25,26,stop=29,price="99");m.behavior(27,28)
    m.stopall(3,30,31,stop=34,price="98")
    m.stopall(4,35,36,stop=39,price="97")
    m.stopall(5,40,41,stop=44,price="96")
    m.stopall(6,45,46,price="95");m.behavior(47,48)
    result=m.calculate()
    assert [s.anchor_number for s in result.setups]==[6]
    assert result.assessments[5].ignored_prefix
    assert result.assessments[-1].status is None
    assert result.assessments[-3].status=="T"


def test_first_true_fallback_waits_for_odd_behavior_after_even_failure():
    m=Market();m.stopall(1,1,2)
    m.stopall(1,10,11,stop=14);m.stopall(2,15,16,stop=19,price="99")
    m.stopall(3,20,21,stop=24,price="98")
    m.stopall(4,25,26,stop=30,price="97");m.behavior(27,28)
    m.stopall(5,31,32,stop=35,price="96")
    m.stopall(6,36,37,stop=40,price="95");m.behavior(38,39)
    m.stopall(7,41,42,price="94");m.behavior(43,44,color="red")
    assert [s.anchor_number for s in m.calculate().setups]==[4,7]


def test_strict_reference_high_is_frozen_and_uses_preceding_pl_confirmation():
    m=Market();m.high(0,"130");m.primary(2,1,2)
    m.high(4,"120");m.stopall(1,3,5,stop=9);m.behavior(6,7)
    m.stopall(2,10,11,stop=15,price="99");m.behavior(12,13,kind="E",color="red")
    m.high(16,"120");m.high(18,"120.001",5)
    result=m.calculate()
    assert len(result.breakouts)==1
    assert result.breakouts[0].reference_high==D("120")
    assert result.breakouts[0].event_time==m.time(18,5)
    assert result.breakouts[0].reference_source_index==4
    assert m.calculate(17).breakouts==[]


def test_larger_pl_has_priority_and_enters_on_first_post_confirmation_behavior():
    m=Market();m.stopall(1,1,2,stop=6);m.behavior(3,4)
    m.stopall(2,7,8,stop=12,price="99");m.behavior(9,10)
    m.high(13,"116");m.primary(1,14,16)
    m.behavior(17,19,color="red");m.behavior(20,21,kind="E")
    result=m.calculate()
    assert result.setups[-1].anchor_kind=="PL" and result.setups[-1].entry_index==19
    assert result.setups[-1].stop_price==D(90)
    assert len([s for s in result.setups if s.anchor_kind=="PL"])==1


def test_behavior_before_pl_confirmation_cannot_trigger_its_entry():
    m=Market();m.primary(1,1,6);m.behavior(3,5);m.behavior(7,8,kind="E")
    assert [(s.anchor_kind,s.entry_index) for s in m.calculate().setups]==[("PL",8)]


def test_future_confirmations_and_stops_are_not_used_in_an_earlier_horizon():
    m=Market();m.stopall(1,1,2,stop=10);m.behavior(4,8)
    assert m.calculate(7).setups==[]
    result=m.calculate(9)
    assert result.assessments[0].status is None and len(result.setups)==1
    assert m.calculate(10).assessments[0].status=="F"


def test_low_equality_and_same_instant_behavior_do_not_make_false():
    m=Market();m.stopall(1,1,2);m.low(5,"100")
    assert m.calculate().assessments[0].status is None
    m.low(6,"99.99",5);m.stops[0].stop_event_time=m.time(6,5)
    m.behavior(4,6,offset=5)
    assert m.calculate().assessments[0].status=="T"


def test_upstream_inputs_are_immutable_and_results_are_deterministic():
    import copy
    m=Market();m.stopall(1,1,2,stop=8);m.behavior(3,4)
    before=copy.deepcopy((m.s,m.stops,m.pl,m.rows))
    first=m.calculate();m.s.reverse();m.stops.reverse()
    assert m.calculate()==first
    assert (m.s,m.stops,m.pl,m.rows)==before


def test_nonpositive_entry_risk_does_not_emit_invalid_geometry():
    m=Market();m.stopall(1,1,2,price="111");m.behavior(3,4)
    assert m.calculate().setups==[]


def test_overlapping_native_chains_join_under_the_highest_stopped_predecessor():
    m=Market();m.stopall(1,1,2,stop=6);m.behavior(3,4)
    m.stopall(2,7,8,stop=11,price="99")
    m.stopall(3,12,13,stop=30,price="98")
    m.stopall(1,14,15,stop=19,price="102")
    m.stopall(2,20,21,stop=24,price="101")
    m.stopall(4,31,32,price="97");m.behavior(33,34)
    result=m.calculate()
    assert result.assessments[-1].scope_id==result.assessments[0].scope_id
    assert result.assessments[-1].predecessor_source_indexes==(12,20)
    assert result.assessments[3].ignored_prefix


def test_successor_at_exact_stop_time_does_not_win_true_over_behavior_failure():
    m=Market();m.stopall(1,1,2,stop=7);m.behavior(3,4)
    m.stopall(1,6,7,price="102")
    assert m.calculate().assessments[0].status=="F"


def test_larger_pl_numbers_advance_within_a_cycle_and_reset_in_a_new_native_cycle():
    m=Market();m.primary(1,1,2);m.behavior(3,4)
    m.primary(1,8,9);m.behavior(10,11)
    m.primary(2,12,13);m.behavior(14,15)
    m.primary(1,20,21,cycle="second");m.behavior(22,23)
    assert [(s.anchor_number,s.entry_index) for s in m.calculate().setups]==[(1,4),(2,15),(1,23)]


def test_later_primary_role_cannot_rewrite_an_earlier_physical_setup():
    m=Market();m.primary(1,1,2);m.behavior(3,4)
    m.primary(2,1,20,cycle="second");m.behavior(21,22)
    early=m.calculate(10)
    assert m.calculate().setups==early.setups


def test_a_stopped_pl_cannot_take_a_later_behavior():
    m=Market();m.primary(1,1,2);m.low(5,"89.9",5);m.behavior(6,7)
    assert m.calculate().setups==[]


def test_all_s_e_families_and_e_numbers_are_eligible():
    for kind in ("S","E"):
        for color in ("blue","red"):
            m=Market();m.stopall(1,1,2)
            m.behavior(3,4,kind=kind,color=color).number=3
            assert m.calculate().setups[0].behavior_kind==kind


def test_decimal_risk_reward_does_not_round_through_binary_floats():
    m=Market();m.stopall(1,1,2,price="100.00000000000001");m.behavior(3,4)
    assert m.calculate().setups[0].target_price==D("149.99999999999996")


def test_inherited_false_still_stops_before_subsequent_unowned_behavior():
    m=Market();m.stopall(1,1,2,stop=6);m.behavior(3,4)
    m.stopall(2,7,8,stop=11,price="99")
    m.stopall(3,12,13,stop=16,price="98");m.behavior(17,18)
    assert all(r.source_index!=17 for r in m.calculate().behaviors)


def test_post_pl_stopall_eligibility_uses_confirmation_not_retrospective_source():
    m=Market();m.primary(1,5,6);m.behavior(7,8)
    m.stopall(1,3,10);m.behavior(11,12)
    assert [(s.anchor_kind,s.entry_index) for s in m.calculate().setups]==[("PL",8),("StopAll",12)]


def test_s_donated_stopall_one_resets_native_active_predecessors():
    m=Market();m.stopall(1,1,2,stop=10)
    donor=m.stopall(1,5,6,stop=11,price="102");donor.donor_type="S"
    m.stopall(2,12,13,price="101")
    assert m.calculate().assessments[-1].predecessor_source_indexes==(5,)


def test_contemporaneous_primary_roles_choose_the_largest_confirmed_number():
    m=Market();m.primary(1,1,2,cycle="first");m.primary(2,1,2,cycle="second")
    m.behavior(3,4)
    assert m.calculate().setups[0].anchor_number==2


def test_larger_pl_phase_precedes_a_still_waiting_even_candidate():
    m=Market();m.stopall(1,1,2,stop=6);m.behavior(3,4)
    m.stopall(2,7,8,stop=11,price="99");m.stopall(3,12,13,stop=16,price="98")
    m.stopall(4,17,18,stop=21,price="97")
    m.primary(1,22,24);m.behavior(25,26)
    assert m.calculate().setups[-1].anchor_kind=="PL"
    assert m.calculate().setups[-1].entry_index==26


def test_previous_extent_includes_its_last_false_stopall():
    m=Market();m.stopall(1,1,2,stop=5);m.stopall(2,6,7,stop=9,price="99")
    m.stopall(3,10,11,stop=15,price="98");m.behavior(12,13)
    m.stopall(1,20,21,stop=24);m.stopall(2,25,26,stop=29,price="99")
    m.stopall(3,30,31,stop=34,price="98");m.stopall(4,35,36,price="97")
    result=m.calculate()
    assert result.assessments[2].status=="F"
    assert [r.ignored_prefix for r in result.assessments[3:]]==[True,True,True,False]


def test_a_qualified_larger_stopall_entry_leaves_the_waiting_phase():
    m=Market();m.stopall(1,1,2,stop=6);m.behavior(3,4)
    m.stopall(2,7,8,stop=12,price="99");m.behavior(9,10);m.high(13,"116")
    donor=m.stopall(1,20,21,stop=24);donor.donor_type="S"
    m.stopall(2,25,26,stop=29,price="99")
    m.stopall(3,30,31,stop=34,price="98");m.stopall(4,35,36,stop=39,price="97")
    m.stopall(5,40,41,price="96");m.behavior(42,43)
    result=m.calculate()
    assert result.setups[-1].anchor_number==5
    assert result.phase=="stopall"
