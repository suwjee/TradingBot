"""Bullish PL parents use native physical bearish Orders and provenance."""
from decimal import Decimal
from types import SimpleNamespace as NS

from test_order_audit_lifecycle_contracts import detector_state, moment
from order_audit_engine import prepare_order_audit


def setup():
    detector, _, _ = detector_state("bullish")
    parent = NS(kind="PL", number=2, source_index=2, source_time=moment(60),
                decision_index=3, decision_event_time=moment(110), price=Decimal("100"))
    return detector, parent


def test_pl_stop_creates_native_order_a_with_actual_pl_parent():
    detector, parent = setup()
    assert detector.register_primary_low(parent) == (5, 6)
    rows = prepare_order_audit(detector, 0, 11)
    assert rows[0]["causes"] == [{"kind": "parent-stop", "parentType": "PL2",
        "parentFamily": "", "eventTime": moment(125), "parentSourceTime": moment(60)}]
    assert rows[0]["crossed"][2] == moment(215)


def test_equal_pl_low_does_not_create_native_parent_order():
    detector, parent = setup()
    parent.price = Decimal("99")
    assert detector.register_primary_low(parent) is None
    assert not detector.order_audit


def test_final_pl_names_reconcile_all_causes_without_moving_the_order():
    detector, parent = setup()
    detector.register_primary_low(parent)
    entry = detector.order_audit[(5, 6)]
    entry["order_b_causes"] = [{"kind": "reset-leg", "postBehaviorType": "PL1",
        "postBehaviorSourceTime": moment(60), "anchorBehaviorType": "PL2",
        "anchorBehaviorSourceTime": moment(60)}]
    before = (entry["reaction"], entry["stop_level"], entry["stop_cross"])
    detector.reconcile_primary_low_labels([NS(source_time=moment(60), number=3)])
    assert entry["causes"] == {("parent-stop", "PL3", "", moment(125), moment(60))}
    assert entry["order_b_causes"][0]["postBehaviorType"] == "PL3"
    assert entry["order_b_causes"][0]["anchorBehaviorType"] == "PL3"
    assert (entry["reaction"], entry["stop_level"], entry["stop_cross"]) == before


def test_pl_replaces_only_the_stopall_cause_at_its_actual_confirmed_stop():
    detector, parent = setup()
    detector.register_primary_low(parent)
    entry = detector.order_audit[(5, 6)]
    historical = ("parent-stop", "StopAll7", "", moment(105), moment(60))
    entry["causes"] = {historical, ("parent-stop", "StopAll7", "", moment(125), moment(60))}
    detector.register_primary_low(parent)
    assert entry["causes"] == {historical, ("parent-stop", "PL2", "", moment(125), moment(60))}
