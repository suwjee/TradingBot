"""Accepted E sources cannot reopen provisional S roots or creator causes.

These artificial state regressions exercise real production reconciliation and
physical Order audit owners; they are independent of any market timestamp.
"""
from dataclasses import replace
from decimal import Decimal

import pytest

from test_order_audit_lifecycle_contracts import (
    EZoneDetector, MarketChronology, candidate, detector_state, moment,
    parent_causes, s_zone,
)
from lifecycle_engine import sequence_priority
from order_audit_engine import OrderBResetLeg, PostBehaviorStop


def lineages(direction, red_source=120):
    detector, parent, _physical = detector_state(direction)
    first = detector._zone("blue", 1, "S", parent, moment(125))
    assert first is not None and first.source_time == moment(120)
    red = replace(s_zone(direction, source=red_source, decision=215),
                  color="red", a_source_time=moment(90))
    independent_s = replace(s_zone(direction, source=180, decision=200),
                            a_source_time=moment(150))
    detector.s_zones = [parent, red, independent_s]
    independent = replace(
        first, parent_source_index=6, parent_source_time=moment(180),
        parent_price=independent_s.price, parent_stop_event_time=moment(205),
        source_index=7, source_time=moment(210), price=Decimal("110"),
        decision_index=8, decision_time=moment(240), decision_event_time=moment(245),
    )
    child_price = Decimal("90" if direction == "bullish" else "130")
    child = replace(
        first, parent_type="E", number=2,
        parent_source_index=first.source_index, parent_source_time=first.source_time,
        parent_price=first.price, parent_stop_event_time=moment(270),
        source_index=10, source_time=moment(300), price=child_price,
        decision_index=11, decision_time=moment(330), decision_event_time=moment(335),
    )
    secondary_child = replace(
        child, parent_source_index=independent.source_index,
        parent_source_time=independent.source_time, parent_price=independent.price,
        parent_stop_event_time=moment(300),
    )
    competing_red = replace(
        child, family="red", number=1, parent_type="S",
        parent_source_index=red.source_index, parent_source_time=red.source_time,
    )
    return detector, [first, child, competing_red, independent, secondary_child]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_same_source_s_cannot_replace_accepted_blue_e_continuation(direction):
    detector, candidates = lineages(direction)
    result = detector._reconcile_candidate_chains(candidates)
    final = next(zone for zone in result if zone.source_time == moment(300))
    assert (final.family, final.number, final.parent_type) == ("blue", 2, "E")
    assert [(zone.source_time, zone.family, zone.number) for zone in result[:-1]] == [
        (moment(120), "blue", 1), (moment(210), "blue", 1),
    ]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_distinct_source_red_s_retains_its_existing_precedence(direction):
    detector, candidates = lineages(direction, red_source=150)
    final = detector._reconcile_candidate_chains(candidates)[-1]
    assert (final.family, final.number, final.parent_type) == ("red", 1, "S")


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_unaccepted_e_candidate_does_not_take_source_ownership_from_s(direction):
    detector, candidates = lineages(direction)
    first = candidates[0]
    detector.invalid_s_root_identities.add((first.parent_source_time, first.parent_source_index))
    final = detector._reconcile_candidate_chains(candidates)[-1]
    assert (final.family, final.number, final.parent_type) == ("red", 1, "S")


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_e_owned_s_cannot_veto_another_accepted_e_parent(direction):
    detector, candidates = lineages(direction, red_source=210)
    final = detector._reconcile_candidate_chains(candidates)[-1]
    assert (final.family, final.number, final.parent_source_time) == ("blue", 2, moment(120))


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_reconciliation_recomputes_source_ownership_from_current_acceptance(direction):
    detector, candidates = lineages(direction)
    detector._reconcile_candidate_chains(candidates)
    first = candidates[0]
    detector.invalid_s_root_identities.add((first.parent_source_time, first.parent_source_index))
    final = detector._reconcile_candidate_chains(candidates)[-1]
    assert (final.family, final.number, final.parent_type) == ("red", 1, "S")


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("reverse", [False, True])
def test_restoring_independent_roots_cannot_revive_a_newly_e_owned_s(direction, reverse):
    detector, candidates = lineages(direction)
    first, _child, red_root = candidates[:3]
    detector._last_candidate_zones = [red_root, first] if reverse else [first, red_root]
    restored = detector.restore_independent_s_roots([])
    assert [(zone.source_time, zone.family, zone.number) for zone in restored] == [
        (moment(120), "blue", 1),
    ]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_same_source_s_evidence_cannot_reopen_consumed_continuation(direction):
    detector, parent, _physical = detector_state(direction)
    owner = detector._zone("blue", 1, "S", parent, moment(125))
    assert owner is not None
    owner = replace(owner, source_time=parent.source_time, source_index=parent.source_index)
    assert detector.continuation_chain_from_s(owner, parent) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("operation", ["replacement", "restoration"])
def test_external_acceptance_blocks_later_same_source_s_evidence(direction, operation):
    initial, parent, _physical = detector_state(direction)
    lower = list(initial.chronology.seconds)
    for time in [250, 275]:
        cross_low = (time == 250) == (direction == "bullish")
        lower[time] = replace(lower[time],
                              low=Decimal("99" if cross_low else "100"),
                              high=Decimal("120" if cross_low else "121"))
    later_s = s_zone(direction, source=120, decision=180)
    detector = EZoneDetector(
        direction, [], [candidate(5, 6), candidate(7, 8)], [parent, later_s], [],
        MarketChronology(initial.chronology.candles, lower, 30),
        sequence_priority=sequence_priority,
    )
    template = detector._zone("blue", 1, "S", parent, moment(125))
    assert template is not None
    first_owner = replace(template, source_index=0, source_time=moment(0),
                          decision_event_time=moment(100))
    second_owner = replace(template, family="red", source_index=1,
                           source_time=moment(30), decision_event_time=moment(100))
    late_child = replace(template, parent_type="E", parent_source_index=0,
                         parent_source_time=moment(0), source_index=10,
                         source_time=moment(300), decision_event_time=moment(330))
    base = detector.rebuild_accepted_order_audit([first_owner, second_owner, late_child])
    if operation == "replacement":
        continuation = detector.continuation_chain_from_s(first_owner, parent)
        assert continuation and continuation[0].source_time == moment(120)
        selected = detector.replace_with_earlier_continuation(base, first_owner, continuation)
    else:
        detector._last_candidate_zones = [template]
        selected = detector.restore_independent_s_roots(base)
    assert any(item.source_time == later_s.source_time for item in selected)
    assert detector.continuation_chain_from_s(second_owner, later_s) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("creation", ["none", "a", "reset-leg"])
def test_e_continuation_requires_an_independent_cause_after_s_loses_source(direction, creation):
    initial, parent, _physical = detector_state(direction)
    lower = list(initial.chronology.seconds)
    for time in [230, 250, 275]:
        cross_low = (time != 275) == (direction == "bullish")
        lower[time] = replace(lower[time],
                              low=Decimal("99" if cross_low else "100"),
                              high=Decimal("120" if cross_low else "121"))
    detector = EZoneDetector(
        direction, [], [candidate(5, 6), candidate(6, 8)],
        [parent, s_zone(direction, source=120, decision=180)], [],
        MarketChronology(initial.chronology.candles, lower, 30),
        sequence_priority=sequence_priority,
    )
    physical = detector.opposite_reactions[1]
    if creation == "a":
        level, source_index, source_time = detector._order_stop(2, physical, moment(250))
        detector.initial_order_audit[(6, 8)] = {
            "reaction_number": 2, "reaction": physical, "confirmation_time": moment(250),
            "stop_level": level, "stop_source_index": source_index, "stop_source_time": source_time,
            "a_source_time": moment(150), "a_stop_event_time": moment(175),
        }
    elif creation == "reset-leg":
        detector.order_b_legs = (replace(reset_leg(direction, physical),
                                          physical_confirmation_time=moment(250)),)
    accepted = detector.detect()
    assert {(zone.order_first_index, zone.order_break_index) for zone in accepted} <= set(detector.order_audit)
    if creation == "none":
        assert [(zone.source_time, zone.family, zone.number) for zone in accepted] == [
            (moment(120), "blue", 1),
        ]
        assert (6, 8) not in detector.order_audit
    else:
        assert any(zone.source_time == moment(210) for zone in accepted)
        entry = detector.order_audit[(6, 8)]
        assert entry["reaction"] is physical
        assert not any(cause[1] == "S" for cause in entry["causes"])
        if creation == "a":
            assert any(cause[1] == "A" for cause in entry["causes"])
        else:
            assert entry["order_b_causes"]


def alternative_order_state(direction, moved_source=False):
    initial, parent, _physical = detector_state(direction)
    lower = list(initial.chronology.seconds)
    for time, low, high in [(245, "98", "120"), (280, "98", "120"),
                            (310, "97", "120"), (305, "100", "122"),
                            (335, "100", "123")]:
        if direction == "bearish":
            low, high = str(Decimal(220) - Decimal(high)), str(Decimal(220) - Decimal(low))
        lower[time] = replace(lower[time], low=Decimal(low), high=Decimal(high))
    if moved_source:
        lower[340] = replace(lower[340], **{
            "low" if direction == "bullish" else "high": Decimal("96" if direction == "bullish" else "124"),
        })
    main = [replace(candle, low=min(row.low for row in lower[index * 30:(index + 1) * 30]),
                    high=max(row.high for row in lower[index * 30:(index + 1) * 30]))
            for index, candle in enumerate(initial.chronology.candles)]
    field = "box_bottom" if direction == "bullish" else "box_top"
    physical = [candidate(5, 6),
                replace(candidate(6, 9), **{field: Decimal("99" if direction == "bullish" else "121")}),
                replace(candidate(8, 10), **{field: Decimal("98" if direction == "bullish" else "122")})]
    detector = EZoneDetector(direction, [], physical,
                            [parent, s_zone(direction, source=120, decision=180)], [],
                            MarketChronology(main, lower, 30), sequence_priority=sequence_priority)
    return detector, parent


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("moved_source", [False, True])
def test_invalid_creator_reselects_the_next_native_order_without_losing_e(direction, moved_source):
    detector, _parent = alternative_order_state(direction, moved_source)
    accepted = detector.detect()
    assert accepted[0].source_time == moment(120)
    final = accepted[-1]
    assert final.source_time == moment(330 if moved_source else 300)
    assert (final.order_first_index, final.order_break_index) == (8, 10)
    assert final.family == "blue" and final.number == 2
    assert {(zone.order_first_index, zone.order_break_index) for zone in accepted} <= set(detector.order_audit)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_consumed_s_recursion_reselects_after_its_new_e_disowns_a_creator(direction):
    detector, parent = alternative_order_state(direction)
    detector._discover_candidate_chains()
    template = detector._zone("blue", 1, "S", parent, moment(125))
    assert template is not None
    owner = replace(template, source_index=0, source_time=moment(0), decision_event_time=moment(100))
    detector.rebuild_accepted_order_audit([owner])
    continuation = detector.continuation_chain_from_s(owner, parent)
    assert continuation[0].source_time == moment(120)
    assert continuation[-1].source_time == moment(300)
    assert (continuation[-1].order_first_index, continuation[-1].order_break_index) == (8, 10)
    assert not any((zone.order_first_index, zone.order_break_index) == (6, 9) for zone in continuation)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_independent_root_restoration_reselects_a_valid_native_order(direction):
    detector, _parent = alternative_order_state(direction)
    independent = s_zone(direction, source=180, decision=220)
    detector.s_zones.append(independent)
    detector._last_candidate_zones = detector._discover_candidate_chains()
    restored = detector.restore_independent_s_roots([])
    assert restored[0].source_time == moment(120)
    final = next(zone for zone in restored if zone.parent_source_time == independent.source_time)
    assert final.source_time == moment(300)
    assert (final.order_first_index, final.order_break_index) == (8, 10)
    assert (final.family, final.number, final.parent_type) == ("blue", 1, "S")


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("hard_reset", [False, True])
def test_later_source_ownership_reselects_an_earlier_parents_native_order(direction, hard_reset):
    detector, parent = alternative_order_state(direction)
    ghost = replace(detector.s_zones[1], source_index=6, source_time=moment(180))
    independent_s = replace(s_zone(direction, source=150, decision=200), a_source_time=moment(150))
    detector.s_zones = [parent, ghost, independent_s]
    discovered = detector._discover_candidate_chains()
    first = next(zone for zone in discovered if zone.source_time == moment(120))
    child = next(zone for zone in discovered if zone.parent_type == "E"
                 and zone.parent_source_time == first.source_time)
    independent_e = replace(first, parent_source_index=5, parent_source_time=moment(150),
                            source_index=6, source_time=moment(180),
                            price=Decimal("90" if direction == "bullish" else "130"),
                            decision_event_time=moment(220))
    if hard_reset:
        detector.sequence_resets = {moment(120): 1}
    accepted = detector._reconcile_candidate_chains([first, independent_e, child])
    final = next(zone for zone in accepted if zone.source_time == moment(300))
    # Without a reset the competing independent E is rejected by the live
    # parent; its merely provisional source must not disown the existing S.
    assert (final.order_first_index, final.order_break_index) == ((8, 10) if hard_reset else (6, 9))
    assert final.parent_type == ("StopAll" if hard_reset else "E")


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_moved_fallback_rebuilds_its_native_descendant_after_hard_reset(direction):
    initial, parent = alternative_order_state(direction, moved_source=True)
    lower = list(initial.chronology.seconds)
    for time in range(360, 480):
        lower.append(replace(lower[-1], index=time, timestamp=moment(time),
                             display_time=moment(time).strftime("%Y-%m-%d %H:%M:%S"),
                             low=Decimal("100"), high=Decimal("120")))
    for time, low, high in [(380, "95", "120"), (400, "94", "120"), (435, "100", "124")]:
        if direction == "bearish":
            low, high = str(Decimal(220) - Decimal(high)), str(Decimal(220) - Decimal(low))
        lower[time] = replace(lower[time], low=Decimal(low), high=Decimal(high))
    main = [replace(lower[index * 30], index=index,
                    low=min(row.low for row in lower[index * 30:(index + 1) * 30]),
                    high=max(row.high for row in lower[index * 30:(index + 1) * 30]))
            for index in range(16)]
    ghost = replace(initial.s_zones[1], source_index=6, source_time=moment(180))
    independent_s = replace(s_zone(direction, source=150, decision=200), a_source_time=moment(150))
    fourth = replace(candidate(12, 13), **{
        "box_bottom" if direction == "bullish" else "box_top": Decimal("95" if direction == "bullish" else "125"),
    })
    detector = EZoneDetector(direction, [], [*initial.opposite_reactions, fourth],
                            [parent, ghost, independent_s], [], MarketChronology(main, lower, 30),
                            sequence_priority=sequence_priority)
    discovered = detector._discover_candidate_chains()
    first = next(zone for zone in discovered if zone.source_time == moment(120))
    child = next(zone for zone in discovered if zone.parent_type == "E"
                 and zone.parent_source_time == first.source_time)
    independent_e = replace(first, parent_source_index=5, parent_source_time=moment(150),
                            source_index=6, source_time=moment(180),
                            price=Decimal("90" if direction == "bullish" else "130"),
                            decision_event_time=moment(220))
    detector.sequence_resets = {moment(120): 1}
    accepted = detector._reconcile_candidate_chains([first, independent_e, child])
    moved = next(zone for zone in accepted if zone.source_time == moment(330))
    descendant = next(zone for zone in accepted if zone.source_time == moment(390))
    assert (moved.order_first_index, moved.order_break_index) == (8, 10)
    assert (descendant.order_first_index, descendant.order_break_index) == (12, 13)
    assert descendant.parent_source_time == moved.source_time
    assert descendant.number == moved.number + 1


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_prospective_e_source_cannot_disown_its_orders_only_creator(direction):
    initial, parent, _physical = detector_state(direction)
    lower = list(initial.chronology.seconds)
    for time, low, high in [(155, "100", "130"), (215, "100", "120"),
                            (280, "99", "120"), (305, "100", "121")]:
        if direction == "bearish":
            low, high = str(Decimal(220) - Decimal(high)), str(Decimal(220) - Decimal(low))
        lower[time] = replace(lower[time], low=Decimal(low), high=Decimal(high))
    main = [replace(candle, low=min(row.low for row in lower[index * 30:(index + 1) * 30]),
                    high=max(row.high for row in lower[index * 30:(index + 1) * 30]))
            for index, candle in enumerate(initial.chronology.candles)]
    main[5] = replace(main[5], tag="RED" if direction == "bullish" else "GREEN",
                      open=Decimal("111" if direction == "bullish" else "109"))
    later_s = replace(s_zone(direction, source=120, decision=180), formation_type="simple",
                      a_source_index=3, a_source_time=moment(90), a_stop_index=4,
                      a_stop_time=moment(120), a_stop_event_time=moment(126))
    detector = EZoneDetector(
        direction, [], [candidate(5, 6), replace(candidate(7, 9), anchor_idx=6)],
        [parent, later_s], [], MarketChronology(main, lower, 30), sequence_priority=sequence_priority,
    )
    detector._register_order_audit("S", later_s, moment(190))
    assert (7, 9) in detector.order_audit
    assert detector._zone("blue", 1, "S", parent, moment(125)) is None
    accepted = detector.detect()
    assert all(zone.source_time != moment(120) for zone in accepted)
    assert {(zone.order_first_index, zone.order_break_index) for zone in accepted} <= set(detector.order_audit)


def reset_leg(direction, physical):
    return OrderBResetLeg(
        post_stop=PostBehaviorStop("A", 0, moment(0), moment(35)),
        anchor_behavior_type="A", anchor_behavior_source_index=0,
        anchor_behavior_source_time=moment(0),
        anchor_behavior_extreme=physical.box_bottom if direction == "bullish" else physical.box_top,
        reset_reaction=candidate(1, 2), reset_confirmation_time=moment(70),
        reset_source_index=3, reset_broken_level=physical.box_top, reset_time=moment(105),
        leg_boundary=physical.box_bottom if direction == "bullish" else physical.box_top,
        leg_source_index=2, leg_source_time=moment(60), strict_break_time=moment(140),
        reaction_number=1, physical_reaction=physical, physical_confirmation_time=moment(190),
    )


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("ensure", [False, True])
@pytest.mark.parametrize("independent", ["none", "e", "reset-leg"])
def test_e_owned_s_loses_only_its_order_creation_cause(direction, ensure, independent):
    detector, parent, physical = detector_state(direction)
    evidence = detector._zone("blue", 1, "S", parent, moment(125))
    assert evidence is not None
    identity = (physical.first_idx, physical.break_idx)
    valid_e_cause = ("parent-stop", "E1", "blue", moment(125), parent.source_time)
    if independent == "e":
        detector.order_audit[identity]["causes"].add(valid_e_cause)
    elif independent == "reset-leg":
        detector.order_b_legs = (reset_leg(direction, physical),)
        detector.register_order_b_reset_legs(detector.order_b_legs)
    owner = replace(
        evidence, source_index=parent.source_index, source_time=parent.source_time,
        parent_type="E", order_causes=("accepted-live",), order_parent_stop_cause_time=None,
    )
    rebuild = detector.ensure_accepted_order_audit if ensure else detector.rebuild_accepted_order_audit
    rebuild([owner])
    assert not any(cause[1] == "S" for cause in parent_causes(detector))
    if independent == "none":
        assert identity not in detector.order_audit
    else:
        entry = detector.order_audit[identity]
        assert entry["reaction"] is physical
        assert entry["confirmation_time"] == moment(190)
        if independent == "e":
            assert entry["causes"] == {valid_e_cause}
        else:
            assert entry["causes"] == set()
            assert len(entry["order_b_causes"]) == 1
    # Repeating the final rebuild must not resurrect a rejected creator.
    rebuild([owner])
    assert not any(cause[1] == "S" for cause in parent_causes(detector))
