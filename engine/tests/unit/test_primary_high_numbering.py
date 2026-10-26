"""Final PH ownership reconciles independent roles before chart publication."""
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace as NS

from test_pl_ph_detector import BASE, fixture, order


def high(number, source, decision, price, cycle="first"):
    from PL_PH_detector import PrimaryPoint
    chronology=fixture()[0]
    return PrimaryPoint("PH",number,source,BASE+timedelta(seconds=30*source),
        Decimal(price),source-1,chronology.times[source-1],decision,
        chronology.times[decision],order(chronology,source-1,decision),cycle_id=cycle)


def resolved(*roles, through=31):
    from PL_PH_detector import resolve_primary_highs
    return resolve_primary_highs(NS(highs=list(roles)),through_index=through)


def test_coincident_high_keeps_larger_number_and_one_physical_owner():
    four=high(4,10,12,"110")
    one=high(1,10,12,"110","second")
    rows=resolved(one,four)
    assert [(p.number,p.source_index) for p in rows]==[(4,10)]
    assert rows[0].cycle_id=="first"
    assert resolved(four,one)==rows


def test_new_cycle_ph_one_above_previous_high_continues_numbering():
    rows=resolved(high(4,10,12,"110"),high(1,16,18,"120","second"),
                  high(5,23,25,"130"))
    assert [(p.number,p.source_index) for p in rows]==[(4,10),(5,16),(6,23)]


def test_equal_or_lower_new_cycle_high_preserves_reset_one():
    for price in ("110","109.999"):
        assert [p.number for p in resolved(high(4,10,12,"110"),
            high(1,16,18,price,"second"))]==[4,1]
    assert [p.number for p in resolved(high(4,10,12,"110"),
        high(1,16,18,"109","second"),high(2,23,25,"109.5","second"))]==[4,1,2]


def test_greater_local_number_is_not_reduced_by_a_lower_prior_counter():
    assert [p.number for p in resolved(high(1,10,12,"110"),
        high(7,16,18,"120","second"))]==[1,7]


def test_future_role_does_not_promote_an_earlier_horizon():
    earlier=high(1,10,12,"110","second")
    later=high(4,10,18,"110")
    assert [(p.number,p.decision_index) for p in resolved(earlier,later,through=15)]==[(1,12)]
    assert [p.number for p in resolved(earlier,later)]==[4]


def test_confirmation_order_controls_numbering_without_changing_logical_roles():
    first=high(4,10,12,"110")
    second=high(1,16,18,"120","second")
    assert [p.number for p in resolved(second,first)]==[4,5]
    assert (first.number,second.number)==(4,1)


def test_retrospective_source_candle_cannot_reorder_confirmation_chronology():
    rows=resolved(high(4,16,18,"110"),high(1,10,20,"120","second"))
    assert [(p.number,p.source_index,p.decision_index) for p in rows]==[(4,16,18),(5,10,20)]


def test_canonical_order_provenance_uses_final_ph_names_without_mutation():
    from PL_PH_detector import relabel_primary_order
    ph=high(5,16,18,"120")
    causes=({"kind":"parent-stop","parentType":"PH1","parentSourceTime":ph.source_time},
        {"kind":"reset-leg","postBehaviorType":"PH1","postBehaviorSourceTime":ph.source_time,
         "anchorBehaviorType":"PH1","anchorBehaviorSourceTime":ph.source_time},
        {"kind":"parent-stop","parentType":"StopAll1","parentSourceTime":ph.source_time})
    original=replace(ph.order,audit_causes=causes)
    result=relabel_primary_order(original,[ph])
    assert result.audit_causes[0]["parentType"]=="PH5"
    assert result.audit_causes[1]["postBehaviorType"]=="PH5"
    assert result.audit_causes[1]["anchorBehaviorType"]=="PH5"
    assert result.audit_causes[2]["parentType"]=="StopAll1"
    assert original.audit_causes[0]["parentType"]=="PH1"
    assert replace(result,audit_causes=original.audit_causes)==original
