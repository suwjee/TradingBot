"""Bounded state regressions for accepted Order causes and hard resets.

The artificial chronology below exercises production owners with real Candle,
Candidate, MarketChronology, SZone, and EZoneDetector objects. It is not market
RAW, a market fixture, or independent real-data validation of either direction.
"""

from __future__ import annotations

import sys
from dataclasses import fields, replace
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

PIPELINE = Path(__file__).resolve().parents[3] / "engine" / "pipeline"
sys.path.insert(0, str(PIPELINE))

from e_zone_detector import EZoneDetector
from lifecycle_engine import reconcile_stopall_lifecycle, sequence_priority
from order_audit_engine import OrderBResetLeg, PostBehaviorStop, prepare_order_audit
from reaction_engine import Candle, Candidate, MarketChronology
from s_zone_detector import SZone


BASE = datetime(2000, 1, 1)


def moment(seconds: int) -> datetime:
    return BASE + timedelta(seconds=seconds)


def candle(index: int, seconds: int, low: str = "100", high: str = "120") -> Candle:
    stamp = moment(seconds)
    return Candle(
        index, stamp, stamp.strftime("%Y-%m-%d %H:%M:%S"), "GREEN",
        Decimal("110"), Decimal(high), Decimal(low), Decimal("110"),
    )


def candidate(first: int = 5, breakout: int = 6) -> Candidate:
    first_time = moment(first * 30).strftime("%Y-%m-%d %H:%M:%S")
    return Candidate(
        first, first_time, first, first_time, Decimal("120"),
        first, first_time, Decimal("100"), "A",
        break_idx=breakout,
        break_time=moment(breakout * 30).strftime("%Y-%m-%d %H:%M:%S"),
    )


def s_zone(direction: str, source: int = 60, decision: int = 110) -> SZone:
    values = {field.name: None for field in fields(SZone)}
    values.update(
        direction=direction, color="blue", formation_type="type4", a_ordinal=1,
        a_source_index=0, a_source_time=moment(0), a_price=Decimal("110"),
        a_stop_index=1, a_stop_time=moment(30), a_stop_event_time=moment(35),
        source_index=source // 30, source_time=moment(source),
        price=Decimal("100" if direction == "bullish" else "120"),
        decision_index=decision // 30,
        decision_time=moment((decision // 30) * 30), decision_event_time=moment(decision),
    )
    return SZone(**values)


def detector_state(direction: str, *, invalid: bool = False):
    lower = [
        candle(
            index, index,
            "99" if index in ({125, 190} if direction == "bullish" else {215}) else "100",
            "121" if index in ({215} if direction == "bullish" else {125, 190}) else "120",
        )
        for index in range(360)
    ]
    chronology = MarketChronology(
        [candle(index, index * 30) for index in range(12)], lower, 30,
    )
    parent = s_zone(direction)
    physical = candidate()
    detector = EZoneDetector(
        direction, [], [physical], [parent], [], chronology,
        sequence_priority=sequence_priority,
        invalid_s_root_identities={(parent.source_time, parent.source_index)} if invalid else set(),
    )
    assert detector.parent_stop("S", parent) == (4, moment(125))
    assert detector._opposite_confirmations == [moment(190)]
    return detector, parent, physical


def parent_causes(detector: EZoneDetector):
    return {
        cause
        for entry in detector.order_audit.values()
        for cause in entry["causes"]
    }


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_extreme_range_query_keeps_first_equal_source(direction):
    detector, _parent, _physical = detector_state(direction)
    index, source_time, value = detector._extreme_between(moment(125), moment(190))
    assert (index, source_time) == (4, moment(120))
    assert value == Decimal("100" if direction == "bullish" else "120")


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_explicitly_invalid_s_cannot_freshly_create_parent_stop_order(direction):
    detector, parent, _physical = detector_state(direction, invalid=True)
    detector._rebuild_accepted_order_audit([])
    assert parent_causes(detector) == set(), "An explicitly invalid S created a fresh Order_A cause."
    assert detector.order_audit == {}


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_invalid_s_cause_is_not_reconstructed_from_internal_e_evidence(direction):
    detector, parent, _physical = detector_state(direction, invalid=True)
    evidence = detector._zone("blue", 1, "S", parent, moment(125))
    assert evidence is not None
    assert evidence.order_parent_stop_cause_time == moment(125)
    detector._rebuild_accepted_order_audit([evidence])
    assert parent_causes(detector) == set(), "Internal E evidence recreated its invalid S Order_A cause."


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_public_e_reference_cannot_create_an_order_without_valid_cause(direction):
    """A consumer identity cannot manufacture an Order from an invalid S."""
    detector, parent, _physical = detector_state(direction, invalid=True)
    evidence = detector._zone("blue", 1, "S", parent, moment(125))
    assert evidence is not None
    identity = (int(evidence.order_first_index), int(evidence.order_break_index))
    detector._rebuild_accepted_order_audit([evidence])
    assert parent_causes(detector) == set()
    assert identity not in detector.order_audit


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_invalid_s_order_cannot_enter_accepted_e_lifecycle(direction):
    detector, parent, _physical = detector_state(direction, invalid=True)
    evidence = detector._zone("blue", 1, "S", parent, moment(125))
    assert evidence is not None
    assert detector._reconcile_candidate_chains([evidence]) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_invalid_s_order_cannot_be_restored_as_independent_e_root(direction):
    detector, parent, _physical = detector_state(direction, invalid=True)
    evidence = detector._zone("blue", 1, "S", parent, moment(125))
    assert evidence is not None
    detector._last_candidate_zones = [evidence]
    assert detector.restore_independent_s_roots([]) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_valid_s_order_can_be_restored_as_independent_e_root(direction):
    detector, parent, _physical = detector_state(direction)
    evidence = detector._zone("blue", 1, "S", parent, moment(125))
    assert evidence is not None
    detector._last_candidate_zones = [evidence]
    assert detector.restore_independent_s_roots([]) == [evidence]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_invalid_s_root_with_reset_leg_order_can_be_restored(direction):
    detector, parent, physical = detector_state(direction, invalid=True)
    evidence = detector._zone("blue", 1, "S", parent, moment(125))
    assert evidence is not None
    detector.order_audit[(physical.first_idx, physical.break_idx)] = {
        "causes": set(), "order_b_causes": [{"kind": "reset-leg"}],
    }
    detector._last_candidate_zones = [evidence]
    assert detector.restore_independent_s_roots([]) == [evidence]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_invalid_s_order_cannot_start_consumed_s_continuation(direction):
    detector, parent, _physical = detector_state(direction, invalid=True)
    owner = detector._zone("blue", 1, "S", parent, moment(125))
    assert owner is not None
    assert detector.continuation_chain_from_s(owner, parent) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_consumed_s_continuation_uses_independent_a_order_cause(direction):
    detector, parent, physical = detector_state(direction, invalid=True)
    owner = detector._zone("blue", 1, "S", parent, moment(125))
    assert owner is not None
    identity = (physical.first_idx, physical.break_idx)
    assert detector.continuation_chain_from_s(owner, parent, frozenset({identity}))
    assert detector.continuation_chain_from_s(owner, parent, frozenset({(0, 1)})) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_invalid_s_chain_cannot_publish_cause_less_descendant(direction):
    detector, parent, _physical = detector_state(direction, invalid=True)
    evidence = detector._zone("blue", 1, "S", parent, moment(125))
    assert evidence is not None
    child = replace(
        evidence, number=2, parent_type="E",
        parent_source_index=evidence.source_index,
        parent_source_time=evidence.source_time,
        source_index=evidence.source_index + 1,
        source_time=evidence.source_time + timedelta(seconds=30),
        decision_event_time=evidence.decision_event_time + timedelta(seconds=30),
    )
    assert detector._reconcile_candidate_chains([evidence, child]) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_invalid_s_root_can_use_independent_reset_leg_order(direction):
    detector, parent, physical = detector_state(direction, invalid=True)
    evidence = detector._zone("blue", 1, "S", parent, moment(125))
    assert evidence is not None
    detector.order_audit[(physical.first_idx, physical.break_idx)] = {
        "causes": set(), "order_b_causes": [{"kind": "reset-leg"}],
    }
    assert detector._reconcile_candidate_chains([evidence]) == [evidence]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_valid_s_order_enters_accepted_e_lifecycle(direction):
    detector, parent, _physical = detector_state(direction)
    evidence = detector._zone("blue", 1, "S", parent, moment(125))
    assert evidence is not None
    assert detector._reconcile_candidate_chains([evidence]) == [evidence]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_required_identity_does_not_prepare_cause_less_order(direction):
    detector, _parent, physical = detector_state(direction)
    identity = (int(physical.first_idx), int(physical.break_idx))
    detector.order_audit[identity] = {
        "reaction_number": 1,
        "reaction": physical,
        "confirmation_time": moment(190),
        "stop_level": Decimal("120" if direction == "bullish" else "100"),
        "stop_source_index": 4,
        "stop_source_time": moment(125),
        "stop_cross": None,
        "causes": set(),
    }
    prepared = prepare_order_audit(
        detector, 0, 10, required_identities={identity}
    )
    assert prepared == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_same_identity_same_ledger_size_changed_causes_refresh_carried_query(direction):
    detector, parent, physical = detector_state(direction)
    detector._register_order_audit("S", parent, moment(125))
    assert detector._carried_orders_for_parent(parent, moment(205))
    entry = detector.order_audit[(physical.first_idx, physical.break_idx)]
    entry["causes"] = {
        ("parent-stop", "S", "blue", moment(100), parent.source_time)
    }
    detector._carried_orders_cache.clear()
    assert detector._carried_orders_for_parent(parent, moment(205)) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.xfail(
    strict=True,
    reason="Pinned GitHub 989647b also omits restored Order_B rows from its confirmation index",
)
def test_ensure_restored_order_is_visible_through_confirmation_query(direction):
    detector, parent, physical = detector_state(direction)
    identity = (int(physical.first_idx), int(physical.break_idx))
    detector.s_zones = []
    detector.order_audit[identity] = {
        "reaction_number": 1,
        "reaction": physical,
        "confirmation_time": moment(190),
        "stop_level": Decimal("120" if direction == "bullish" else "100"),
        "stop_source_index": 4,
        "stop_source_time": moment(125),
        "stop_cross": (7, moment(210), moment(215)),
        "causes": set(),
        "order_b_causes": [{"kind": "reset-leg", "physicalOrderConfirmationTime": moment(190)}],
    }
    detector._index_order_audit_identity(identity, moment(190))
    assert detector._post_stop_accepted_orders_for_parent(parent, moment(125))
    detector.ensure_accepted_order_audit([])
    matches = detector._post_stop_accepted_orders_for_parent(parent, moment(125))
    assert [int(item[1].first_idx) for item in matches] == [int(physical.first_idx)]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_valid_historical_s_creation_cause_survives_public_parent_removal(direction):
    detector, parent, _physical = detector_state(direction)
    accepted = detector._zone("blue", 1, "S", parent, moment(125))
    assert accepted is not None
    expected = ("parent-stop", "S", "blue", moment(125), parent.source_time)
    assert expected in parent_causes(detector)
    detector.s_zones = []
    accepted = replace(accepted, order_causes=("accepted-live",), order_parent_stop_cause_time=None)
    detector._rebuild_accepted_order_audit([accepted])
    assert parent_causes(detector) == {expected}
    assert detector.order_audit[(5, 6)]["reaction"] is _physical


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_invalid_s_removal_retains_shared_physical_order_b_reset_cause(direction):
    detector, parent, physical = detector_state(direction, invalid=True)
    leg = OrderBResetLeg(
        post_stop=PostBehaviorStop("A", 0, moment(0), moment(35)),
        anchor_behavior_type="A", anchor_behavior_source_index=0,
        anchor_behavior_source_time=moment(0),
        anchor_behavior_extreme=Decimal("100" if direction == "bullish" else "120"),
        reset_reaction=candidate(1, 2), reset_confirmation_time=moment(70),
        reset_source_index=3, reset_broken_level=Decimal("110"), reset_time=moment(105),
        leg_boundary=Decimal("100" if direction == "bullish" else "120"),
        leg_source_index=2, leg_source_time=moment(60), strict_break_time=moment(140),
        reaction_number=1, physical_reaction=physical, physical_confirmation_time=moment(190),
    )
    detector.order_b_legs = (leg,)
    detector.register_order_b_reset_legs([leg])
    expected_b_cause = dict(detector.order_audit[(5, 6)]["order_b_causes"][0])
    detector.order_audit[(5, 6)]["causes"].add(
        ("parent-stop", "S", "blue", moment(125), parent.source_time)
    )
    detector._rebuild_accepted_order_audit([])
    entry = detector.order_audit[(5, 6)]
    assert entry["causes"] == set()
    assert entry["order_b_causes"] == [expected_b_cause]
    assert entry["reaction"] is physical


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_real_stopall_publication_refreshes_reset_queries_and_context_caches(direction):
    detector, parent, _physical = detector_state(direction)
    detector._register_order_audit("S", parent, moment(125))
    assert detector._post_stop_accepted_orders_for_parent(parent, moment(60))
    assert detector.order_candidates(moment(125), allow_bounded_continue=True)
    assert detector._carried_orders_for_parent(parent, moment(205))
    assert detector._order_candidates_cache and detector._carried_orders_cache
    physical_crosses = dict(detector._cross_order_cache)
    physical_stops = dict(detector._canonical_order_stop_cache)
    historical_causes = parent_causes(detector)
    accepted_s = [
        s_zone(direction, source=0, decision=5),
        s_zone(direction, source=30, decision=35),
        replace(s_zone(direction, source=90, decision=100), color="red", order_mode="B"),
    ]

    accepted_e, stopalls = reconcile_stopall_lifecycle(
        detector, accepted_s, [], detector.chronology, direction,
    )

    assert accepted_e == []
    assert len(stopalls) == 1
    assert stopalls[0].source_time == moment(90)
    assert detector.sequence_resets == {moment(90): 1}
    assert detector._has_sequence_reset_between(moment(60), moment(125))
    assert not detector._has_sequence_reset_between(moment(90), moment(125))
    assert detector._has_sequence_reset_between(moment(60), moment(90))
    assert detector._order_candidates_cache == {}
    assert detector._carried_orders_cache == {}
    assert detector._cross_order_cache == physical_crosses
    assert detector._canonical_order_stop_cache == physical_stops
    assert parent_causes(detector) == historical_causes
    assert detector._post_stop_accepted_orders_for_parent(parent, moment(60)) == []
    detector._rebuild_accepted_order_audit([])
    assert parent_causes(detector) == historical_causes
    detector._clear_order_audit()
    detector._register_order_audit("S", parent, moment(125))
    assert parent_causes(detector) == set()


def test_reset_publication_builds_one_sorted_index_and_copies_the_supplied_map():
    detector, _parent, _physical = detector_state("bullish")
    supplied = {moment(120): 2, moment(90): 1}
    detector.sequence_resets = supplied
    expected_index = detector._sequence_reset_times
    assert expected_index == [moment(90), moment(120)]
    supplied.clear()
    assert detector.sequence_resets == {moment(120): 2, moment(90): 1}
    for _query in range(5):
        assert detector._has_sequence_reset_between(moment(60), moment(90))
        assert detector._sequence_reset_times is expected_index
