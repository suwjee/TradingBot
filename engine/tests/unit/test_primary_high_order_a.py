"""PH ownership uses native canonical Order_A and exact RAW chronology."""
from dataclasses import replace
from decimal import Decimal
from types import SimpleNamespace as NS

from test_order_audit_lifecycle_contracts import candle, candidate, moment
from e_zone_detector import EZoneDetector
from lifecycle_engine import sequence_priority
from order_audit_engine import OrderBResetLeg, PostBehaviorStop, prepare_order_audit
from reaction_engine import MarketChronology


def setup(*, early=False, stopped=True):
    lower=[candle(i,i,"99" if stopped and i==215 else "100",
                  "121" if i in {125,190} else "120") for i in range(360)]
    chronology=MarketChronology([candle(i,i*30) for i in range(12)],lower,30)
    physical=candidate()
    reactions=[candidate(4,4),physical] if early else [physical]
    detector=EZoneDetector("bearish",[],reactions,[],[],chronology,
        sequence_priority=sequence_priority,sequence_resets={moment(60):7,moment(90):8})
    parent=NS(kind="PH",number=2,source_index=2,source_time=moment(60),
              decision_index=3,decision_event_time=moment(110),price=Decimal("120"))
    return detector,parent


def test_ph_stop_creates_native_order_a_despite_historical_stopall_reset():
    detector,parent=setup()
    assert detector.register_primary_high(parent)==(5,6)
    rows=prepare_order_audit(detector,0,11)
    assert len(rows)==1
    assert rows[0]["causes"]==[{"kind":"parent-stop","parentType":"PH2",
        "parentFamily":"","eventTime":moment(125),"parentSourceTime":moment(60)}]
    assert rows[0]["crossed"][2]==moment(215)
    assert detector.sequence_resets=={moment(60):7,moment(90):8}


def test_ph_stop_equality_cannot_create_order_a():
    detector,parent=setup()
    parent.price=Decimal("121")
    assert detector.register_primary_high(parent) is None
    assert detector.order_audit=={}


def test_ph_order_requires_confirmation_strictly_after_its_stop():
    detector,parent=setup(early=True)
    assert detector.register_primary_high(parent)==(5,6)
    assert (4,4) not in detector.order_audit


def test_superseded_stopall_cannot_steal_ph_cause_with_an_ineligible_order():
    detector,parent=setup(early=True)
    detector.sequence_resets={moment(60):7}
    detector._register_order_audit("StopAll",parent,moment(125))
    assert (4,4) in detector.order_audit
    assert detector.register_primary_high(parent)==(5,6)
    rows=prepare_order_audit(detector,0,11)
    ph_orders=[(row["reaction"].first_idx,row["reaction"].break_idx)
               for row in rows if any(c.get("parentType")=="PH2" for c in row["causes"])]
    assert ph_orders==[(5,6)]


def test_revoked_ph_cause_cannot_survive_in_native_accepted_order_queries():
    detector,parent=setup(early=True)
    detector.sequence_resets={moment(60):7}
    detector._register_order_audit("StopAll",parent,moment(125))
    before=detector._post_stop_accepted_orders_for_parent(parent,moment(120))
    assert any((row[1].first_idx,row[1].break_idx)==(4,4) for row in before)
    detector.register_primary_high(parent)
    after=detector._post_stop_accepted_orders_for_parent(parent,moment(120))
    assert [(row[1].first_idx,row[1].break_idx) for row in after]==[(5,6)]
    assert (4,4) not in detector.order_audit
    assert all(row[1:]!=(4,4) for row in detector._order_audit_confirmation_index)


def test_ph_open_order_is_retained_and_registration_is_idempotent():
    detector,parent=setup(stopped=False)
    assert detector.register_primary_high(parent)==(5,6)
    assert detector.register_primary_high(parent)==(5,6)
    assert detector.order_audit[(5,6)]["stop_cross"] is None
    assert len(detector.order_audit[(5,6)]["causes"])==1
    assert len(detector._order_audit_confirmation_index)==1


def test_final_ph_label_reconciles_native_causes_without_changing_physical_orders():
    detector,parent=setup()
    detector.register_primary_high(parent)
    entry=detector.order_audit[(5,6)]
    entry["causes"].add(("parent-stop","PH1","",moment(125),moment(60)))
    historical=("parent-stop","StopAll7","",moment(105),moment(60))
    entry["causes"].add(historical)
    entry["order_b_causes"]=[{"kind":"reset-leg","postBehaviorType":"PH1",
        "postBehaviorSourceTime":moment(60),"anchorBehaviorType":"PH2",
        "anchorBehaviorSourceTime":moment(60)}]
    before=(entry["reaction"],entry["stop_level"],entry["stop_cross"],
            list(detector._order_audit_confirmation_index))
    final=NS(source_time=moment(60),number=5)
    detector.reconcile_primary_high_labels([final])
    assert entry["causes"]=={historical,("parent-stop","PH5","",moment(125),moment(60))}
    assert entry["order_b_causes"][0]["postBehaviorType"]=="PH5"
    assert entry["order_b_causes"][0]["anchorBehaviorType"]=="PH5"
    assert (entry["reaction"],entry["stop_level"],entry["stop_cross"],
            list(detector._order_audit_confirmation_index))==before
    rows=prepare_order_audit(detector,0,11)
    assert any(c.get("parentType")=="PH5" for row in rows for c in row["causes"])


def test_stopall_parent_cause_is_reparented_only_at_the_confirmed_ph_stop():
    detector,parent=setup()
    detector.register_primary_high(parent)
    entry=detector.order_audit[(5,6)]
    historical=("parent-stop","StopAll7","",moment(105),moment(60))
    entry["causes"]={historical,("parent-stop","StopAll7","",moment(125),moment(60))}
    detector.register_primary_high(parent)
    assert entry["causes"]=={historical,("parent-stop","PH2","",moment(125),moment(60))}


def reset_leg(detector, *, post=125, first=5):
    return OrderBResetLeg(
        post_stop=PostBehaviorStop("StopAll",2,moment(60),moment(post)),
        anchor_behavior_type="StopAll",anchor_behavior_source_index=2,
        anchor_behavior_source_time=moment(60),anchor_behavior_extreme=Decimal("120"),
        reset_reaction=candidate(first,first+1),reset_confirmation_time=moment(160),
        reset_source_index=6,reset_broken_level=Decimal("119"),reset_time=moment(170),
        leg_boundary=Decimal("122"),leg_source_index=4,leg_source_time=moment(120),
        strict_break_time=moment(180),reaction_number=1,
        physical_reaction=detector.opposite_reactions[0],physical_confirmation_time=moment(190))


def test_independent_reset_leg_keeps_its_type_with_temporally_current_ph_owner():
    detector,parent=setup()
    detector.register_order_b_reset_legs([reset_leg(detector)])
    original=dict(detector.order_audit[(5,6)]["order_b_causes"][0])
    detector.register_primary_high(parent)
    cause=detector.order_audit[(5,6)]["order_b_causes"][0]
    assert cause=={**original,"postBehaviorType":"PH2","anchorBehaviorType":"PH2"}
    assert cause["kind"]=="reset-leg"


def test_reset_roles_before_ph_confirmation_retain_historical_stopall_owner():
    detector,parent=setup()
    detector.register_order_b_reset_legs([reset_leg(detector,post=105,first=3)])
    original=dict(detector.order_audit[(5,6)]["order_b_causes"][0])
    detector.register_primary_high(parent)
    assert detector.order_audit[(5,6)]["order_b_causes"]==[original]


def test_ph_cannot_claim_a_different_stopall_stop_or_anchor():
    detector,parent=setup()
    unrelated=replace(reset_leg(detector),anchor_behavior_source_index=3,
        anchor_behavior_source_time=moment(90),
        post_stop=PostBehaviorStop("StopAll",3,moment(90),moment(125)))
    detector.register_order_b_reset_legs([unrelated])
    original=dict(detector.order_audit[(5,6)]["order_b_causes"][0])
    detector.register_primary_high(parent)
    assert detector.order_audit[(5,6)]["order_b_causes"]==[original]
