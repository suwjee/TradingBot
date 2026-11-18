"""Physical-parent and child-race contracts for local E lookup indexes."""

from dataclasses import replace
from decimal import Decimal

import pytest

from test_e_source_ownership import lineages
from test_order_audit_lifecycle_contracts import detector_state, moment
from e_zone_detector import EZoneDetector, LiveEContinuation
from lifecycle_engine import sequence_priority
from reaction_engine import MarketChronology


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
@pytest.mark.parametrize("first_is_valid", (False, True))
def test_e_duplicate_s_parent_retains_first_physical_parent(direction, first_is_valid):
    detector, candidates = lineages(direction)
    parent = detector.s_zones[-1]
    invalid = replace(parent, a_source_time=moment(90))
    pair = (parent, invalid) if first_is_valid else (invalid, parent)
    detector.s_zones = [*detector.s_zones[:-1], *pair]
    actual = detector._reconcile_candidate_chains(candidates)
    expected_sources = [120, 210, 300] if first_is_valid else [120, 300]
    assert [zone.source_time for zone in actual] == list(map(moment, expected_sources))


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
@pytest.mark.parametrize("child_decision", (334, 335, 336))
@pytest.mark.parametrize("reverse_children", (False, True))
def test_e_future_child_race_uses_maximum_decision_with_inclusive_tie(
    direction, child_decision, reverse_children,
):
    detector, candidates = lineages(direction, red_source=150)
    first, child, competing_s, independent, _secondary = candidates
    competing_s = replace(competing_s, family="blue", decision_event_time=moment(335))
    future = replace(
        child, source_index=11, source_time=moment(330),
        decision_event_time=moment(child_decision),
    )
    earlier = replace(future, decision_event_time=moment(333))
    children = [future, earlier] if reverse_children else [earlier, future]
    actual = detector._reconcile_candidate_chains([first, independent, competing_s, *children])
    expected_final = (330, "E") if child_decision >= 335 else (300, "S")
    assert [(zone.source_time, zone.parent_type) for zone in actual] == [
        (moment(120), "S"), (moment(210), "S"),
        (moment(expected_final[0]), expected_final[1]),
    ]


def new_detector(direction, chronology):
    return EZoneDetector(direction, [], [], [], [], chronology,
                         sequence_priority=sequence_priority)


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_e_sparse_main_extremes_are_reused_only_within_one_immutable_chronology(direction):
    original, _parent, _physical = detector_state(direction)
    chronology = MarketChronology(original.candles, original.lower, 30)
    first = new_detector(direction, chronology)
    second = new_detector(direction, chronology)
    assert second._stop_values is first._stop_values
    assert second._candle_codes is first._candle_codes
    assert second._extreme_sparse is first._extreme_sparse

    opposite = new_detector(chronology.opposite_direction(direction), chronology)
    assert opposite._stop_values is not first._stop_values
    assert opposite._extreme_sparse is not first._extreme_sparse

    price = "90.000" if direction == "bullish" else "130.000"
    attribute = "low" if direction == "bullish" else "high"
    revised = [*chronology.candles]
    revised[6] = replace(revised[6], **{attribute: Decimal(price)})
    updated = MarketChronology(revised, chronology.seconds, 30)
    third = new_detector(direction, updated)
    assert third._extreme_sparse is not first._extreme_sparse
    assert third._find_extreme(4, 6)[0:2] == (6, moment(180))
    assert str(third._find_extreme(4, 6)[2]) == price
    assert first._find_extreme(4, 6)[0:2] == (4, moment(120))


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_e_legacy_chronology_without_sparse_cache_retains_local_tables(direction):
    original, _parent, _physical = detector_state(direction)
    chronology = MarketChronology(original.candles, original.lower, 30)
    del chronology._e_main_extremes
    first, second = new_detector(direction, chronology), new_detector(direction, chronology)
    assert first._extreme_sparse is not second._extreme_sparse
    assert first._find_extreme(4, 6) == second._find_extreme(4, 6)


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_e_live_extreme_cache_remains_owned_by_its_continuation(direction):
    original, _parent, _physical = detector_state(direction)
    chronology = MarketChronology(original.candles, original.lower, 30)
    continuation = LiveEContinuation()
    continuation.advance(chronology, first_dirty_main=0)
    detector = EZoneDetector(
        direction, [], [], [], [], chronology,
        sequence_priority=sequence_priority, live_continuation=continuation,
    )
    assert detector._extreme_between(moment(125), moment(190))[:2] == (4, moment(120))
    assert chronology._e_main_extremes == {}
