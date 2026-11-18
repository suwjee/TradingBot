"""Exact carried-Order boundaries, eager failures, identity and temporary memory."""
from __future__ import annotations
from datetime import timezone
from decimal import InvalidOperation, localcontext
from types import SimpleNamespace
import json
import os
from pathlib import Path
import subprocess
import sys
import tracemalloc

import pytest

from test_order_audit_lifecycle_contracts import candidate, detector_state, moment


def ledger_entry(physical, *, parents=(), b_events=(), confirmation=190, crossing=215, number=1):
    return {
        "reaction": physical, "reaction_number": number,
        "confirmation_time": moment(confirmation), "stop_level": "120.00",
        "stop_source_index": physical.first_idx, "stop_source_time": moment(physical.first_idx * 30),
        "stop_cross": None if crossing is None else (crossing // 30, moment(crossing // 30 * 30), moment(crossing)),
        "causes": {("parent-stop", "S", "blue", moment(event), moment(60)) for event in parents},
        "order_b_causes": [{"physicalOrderConfirmationTime": moment(event)} for event in b_events],
    }


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("parents,b_events,accepted", [
    ((), (), False), ((110,), (), False), ((200,), (), False),
    ((125,), (), True), ((90, 125), (), False), ((125, 150), (), True),
    ((90,), (150,), True), ((), (110, 200), False), ((), (150,), True),
])
def test_carried_creation_uses_earliest_parent_and_all_b_events(direction, parents, b_events, accepted):
    detector, _, physical = detector_state(direction)
    detector.order_audit = {(physical.first_idx, physical.break_idx): ledger_entry(physical, parents=parents, b_events=b_events)}
    matches = detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(110)), moment(200))
    assert bool(matches) is accepted
    if accepted:
        assert len(matches) == 1 and matches[0][1] is physical
        assert str(matches[0][3]) == "120.00"
        assert matches[0][7:] == (("carried-live",), None)


@pytest.mark.parametrize("confirmation,crossing,accepted", [
    (200, 200, True), (201, 215, False), (190, 199, False), (190, None, False),
])
def test_carried_confirmation_and_stop_boundaries(confirmation, crossing, accepted):
    detector, _, physical = detector_state("bullish")
    detector.order_audit = {(5,6): ledger_entry(physical, parents=(125,), confirmation=confirmation, crossing=crossing)}
    assert bool(detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(110)), moment(200))) is accepted


def test_carried_exact_sort_ties_keep_ledger_insertion_and_cache_returns_fresh_lists():
    detector, _, _ = detector_state("bearish")
    first, second = candidate(5, 7), candidate(5, 6)
    detector.order_audit = {(5,7): ledger_entry(first, parents=(125,), number=2),
                            (5,6): ledger_entry(second, parents=(125,), number=1)}
    parent = SimpleNamespace(decision_event_time=moment(110))
    matches = detector._carried_orders_for_parent(parent, moment(200))
    assert [item[1] for item in matches] == [first, second]
    assert matches[0][1] is first and matches[1][1] is second
    matches.clear()
    assert [item[1] for item in detector._carried_orders_for_parent(parent, moment(200))] == [first, second]


def test_causeless_partial_row_is_skipped_before_physical_field_access():
    detector, _, _ = detector_state("bullish")
    detector.order_audit = {(5,6): {}}
    assert detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(110)), moment(200)) == []


def test_every_b_creation_is_extracted_before_metadata_rejection():
    detector, _, physical = detector_state("bullish")
    entry = ledger_entry(physical, parents=(125,), confirmation=300, crossing=None)
    entry["order_b_causes"] = [{"physicalOrderConfirmationTime": moment(150)}, {}]
    del entry["confirmation_time"]
    detector.order_audit = {(5,6): entry}
    with pytest.raises(KeyError, match="physicalOrderConfirmationTime"):
        detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(110)), moment(200))


def test_nonempty_creation_keeps_missing_confirmation_error():
    detector, _, physical = detector_state("bullish")
    entry = ledger_entry(physical, parents=(125,))
    del entry["confirmation_time"]
    detector.order_audit = {(5,6): entry}
    with pytest.raises(KeyError, match="confirmation_time"):
        detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(110)), moment(200))


def test_carried_preserves_earlier_selected_metadata_error_before_later_creation_error():
    detector, _, physical = detector_state("bullish")
    first = ledger_entry(physical, parents=(125,))
    first["stop_level"] = "invalid-decimal"
    later = ledger_entry(physical)
    later["order_b_causes"] = [{}]
    detector.order_audit = {(5, 6): first, (7, 8): later}
    with pytest.raises(InvalidOperation):
        detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(110)), moment(200))


def test_carried_keeps_creation_short_circuit_before_an_unhashable_later_b_event():
    detector, _, physical = detector_state("bullish")
    entry = ledger_entry(physical, parents=(125,), b_events=(150,))
    entry["order_b_causes"].append({"physicalOrderConfirmationTime": []})
    detector.order_audit = {(5, 6): entry}
    matches = detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(110)), moment(200))
    assert len(matches) == 1 and matches[0][1] is physical


def test_carried_keeps_creation_short_circuit_before_an_incomparable_later_b_event():
    detector, _, physical = detector_state("bullish")
    entry = ledger_entry(physical, parents=(125,))
    entry["order_b_causes"] = [{"physicalOrderConfirmationTime": moment(150).replace(tzinfo=timezone.utc)}]
    detector.order_audit = {(5, 6): entry}
    matches = detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(110)), moment(200))
    assert len(matches) == 1 and matches[0][1] is physical


def test_carried_guard_does_not_change_decimal_flags_for_an_unselected_invalid_price():
    detector, _, physical = detector_state("bullish")
    entry = ledger_entry(physical, parents=(90,))
    entry["stop_level"] = "invalid-decimal"
    detector.order_audit = {(5, 6): entry}
    with localcontext() as context:
        context.clear_flags()
        assert detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(110)), moment(200)) == []
        assert not context.flags[InvalidOperation]


def test_distinct_parent_queries_reuse_creation_index_and_invalidate_on_new_cause():
    detector, _, physical = detector_state("bullish")
    class Ledger(dict):
        scans = 0
        def values(self):
            self.scans += 1
            return super().values()
    detector.order_audit = Ledger({(5, 6): ledger_entry(physical, parents=(125,))})
    for start in range(100, 110):
        assert detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(start)), moment(200))
    assert detector.order_audit.scans == 1, "Different parents must share the current ledger creation index."
    detector.order_audit[(5, 6)]["causes"].add(("parent-stop", "S", "blue", moment(90), moment(60)))
    detector._invalidate_carried_order_caches()
    assert not detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(110)), moment(200))
    assert detector.order_audit.scans == 2


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_later_parent_provenance_keeps_creation_cache_but_earlier_parent_invalidates(direction):
    detector, parent, physical = detector_state(direction)
    detector._register_order_audit("S", parent, moment(125))
    assert detector._carried_orders_for_parent(parent, moment(205))
    indexed = detector._carried_creation_index
    detector._register_order_audit("S", parent, moment(145))
    assert detector._carried_orders_cache, "A later cause cannot change the earliest parent creation."
    assert detector._carried_creation_index is indexed
    assert {cause[3] for cause in detector.order_audit[(5, 6)]["causes"]} == {moment(125), moment(145)}
    detector._register_order_audit("S", parent, moment(120))
    assert not detector._carried_orders_cache
    assert not detector._carried_orders_for_parent(SimpleNamespace(decision_event_time=moment(122)), moment(205))


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_lazy_post_stop_stream_matches_complete_query_across_mutation_and_reset(direction):
    detector, parent, physical = detector_state(direction)
    for first, stop in ((5, 215), (6, 230), (7, 215), (8, 270)):
        reaction = candidate(first, first + 2)
        entry = ledger_entry(reaction, parents=(125,), confirmation=190 + first, crossing=stop)
        identity = reaction.first_idx, reaction.break_idx
        detector.order_audit[identity] = entry
        detector._index_order_audit_identity(identity, entry["confirmation_time"])
    for resets in ({}, {moment(250): 1}, {moment(215): 1}):
        detector.sequence_resets = resets
        for stop in (125, 190, 195, 200, 215, 240, 280):
            expected = detector._post_stop_accepted_orders_for_parent(parent, moment(stop))
            actual = list(detector._iter_post_stop_accepted_orders(parent, moment(stop)))
            assert repr(actual) == repr(expected)
            assert all(a[1] is b[1] for a, b in zip(actual, expected))
    detector._clear_order_audit()
    assert list(detector._iter_post_stop_accepted_orders(parent, moment(125))) == detector._post_stop_accepted_orders_for_parent(parent, moment(125))


def test_post_stop_stream_skips_unselected_malformed_price_without_decimal_flags():
    detector, parent, physical = detector_state("bullish")
    entry = ledger_entry(physical, confirmation=100)
    entry["stop_level"] = "invalid-decimal"
    detector.order_audit[(5, 6)] = entry
    detector._index_order_audit_identity((5, 6), entry["confirmation_time"])
    assert detector._post_stop_accepted_orders_for_parent(parent, moment(200)) == []
    with localcontext() as context:
        context.clear_flags()
        assert list(detector._iter_post_stop_accepted_orders(parent, moment(200))) == []
        assert not context.flags[InvalidOperation]


def test_post_stop_stream_preserves_selected_metadata_failure_at_query_call():
    detector, parent, physical = detector_state("bullish")
    entry = ledger_entry(physical, confirmation=190)
    entry["stop_level"] = "invalid-decimal"
    detector.order_audit[(5, 6)] = entry
    detector._index_order_audit_identity((5, 6), entry["confirmation_time"])
    with pytest.raises(InvalidOperation):
        detector._post_stop_accepted_orders_for_parent(parent, moment(125))
    # E constructs this route before evaluating direct Order candidates.
    # Deferring the failure until next() would change that failure precedence.
    with pytest.raises(InvalidOperation):
        detector._iter_post_stop_accepted_orders(parent, moment(125))


def test_post_stop_stream_preserves_legacy_cross_lookup_for_partial_row():
    detector, parent, physical = detector_state("bullish")
    entry = ledger_entry(physical, confirmation=190, crossing=None)
    detector.order_audit[(5, 6)] = entry
    detector._index_order_audit_identity((5, 6), entry["confirmation_time"])
    expected = detector._post_stop_accepted_orders_for_parent(parent, moment(125))
    assert expected
    assert repr(list(detector._iter_post_stop_accepted_orders(parent, moment(125)))) == repr(expected)


def test_post_stop_stream_does_not_inspect_excluded_mixed_timezone_cross():
    detector, parent, physical = detector_state("bullish")
    entry = ledger_entry(physical, confirmation=100)
    entry["stop_cross"] = tuple(value.replace(tzinfo=timezone.utc) if hasattr(value, "tzinfo") else value
                                for value in entry["stop_cross"])
    detector.order_audit[(5, 6)] = entry
    detector._index_order_audit_identity((5, 6), entry["confirmation_time"])
    assert detector._post_stop_accepted_orders_for_parent(parent, moment(200)) == []
    assert list(detector._iter_post_stop_accepted_orders(parent, moment(200))) == []


def test_native_post_stop_stream_reuses_generation_without_rescanning_ledger():
    detector, parent, physical = detector_state("bullish")
    class Ledger(dict):
        reads = 0
        def get(self, *args):
            self.reads += 1
            return super().get(*args)
    detector.order_audit = Ledger({(5, 6): ledger_entry(physical)})
    detector._index_order_audit_identity((5, 6), moment(190))
    assert list(detector._iter_post_stop_accepted_orders(parent, moment(125)))
    assert list(detector._iter_post_stop_accepted_orders(parent, moment(150)))
    assert detector.order_audit.reads == 1
    detector.order_audit[(7, 8)] = ledger_entry(candidate(7, 8), confirmation=195, crossing=230)
    detector._index_order_audit_identity((7, 8), moment(195))
    assert len(list(detector._iter_post_stop_accepted_orders(parent, moment(125)))) == 2
    assert detector.order_audit.reads == 3


@pytest.mark.parametrize("consumer", ("query", "zone"))
def test_post_stop_replacement_keeps_initial_identity_insertion_tie(consumer):
    from e_zone_detector import EZoneDetector
    from lifecycle_engine import sequence_priority
    from reaction_engine import MarketChronology
    from test_order_audit_lifecycle_contracts import candle

    lower = [candle(index, index, high="122" if index == 230 else "121" if index == 215 else "120")
             for index in range(360)]
    chronology = MarketChronology([candle(index, index * 30) for index in range(12)], lower, 30)
    first, second = candidate(5, 8), candidate(5, 6)
    initial = ledger_entry(first, confirmation=130)
    initial["stop_level"] = "121.00"
    detector = EZoneDetector("bullish", [], [], [], [], chronology,
                            initial_order_audit={(5, 8): initial}, sequence_priority=sequence_priority)
    for physical in (first, second):
        entry = ledger_entry(physical, confirmation=190, crossing=215)
        identity = physical.first_idx, physical.break_idx
        detector.order_audit[identity] = entry
        detector._index_order_audit_identity(identity, entry["confirmation_time"])
    _, parent, _ = detector_state("bullish")
    # Initial X is inserted before audit Y. Replacing X with an earlier-stop
    # audit match must keep X's insertion position when final sort keys tie.
    if consumer == "query":
        assert [match[1].break_idx for match in detector._post_stop_accepted_orders_for_parent(parent, moment(125))] == [8, 6]
        assert [match[1].break_idx for match in detector._iter_post_stop_accepted_orders(parent, moment(125))] == [8, 6]
    else:
        zone = detector._zone("blue", 1, "S", parent, moment(125))
        assert zone is not None and zone.order_break_index == 8


def measure_dense_query_allocation():
    """Measure only native query scratch memory in an isolated interpreter."""
    detector, _, physical = detector_state("bullish")
    count = 10_000
    entry = ledger_entry(physical, parents=range(125, 125+count), b_events=[150]*count)
    detector.order_audit = {(5,6): entry}
    detector._initial_order_records()
    parent = SimpleNamespace(decision_event_time=moment(110))
    tracemalloc.start(1)
    try:
        matches = detector._carried_orders_for_parent(parent, moment(200))
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return {"identity_preserved": len(matches) == 1 and matches[0][1] is physical, "peak_bytes": peak}


def test_creation_lists_do_not_retain_both_dense_parent_and_b_history():
    """A high-provenance row should need one history-sized scratch collection."""
    # Do not consume a pre-existing global tracing peak or stop the caller's
    # tracer when pytest is launched with -X tracemalloc/PYTHONTRACEMALLOC.
    environment = dict(os.environ)
    environment.pop("PYTHONTRACEMALLOC", None)
    code = (
        "import json,sys; "
        f"sys.path.insert(0, {str(Path(__file__).parent)!r}); "
        "from test_carried_order_query import measure_dense_query_allocation; "
        "print(json.dumps(measure_dense_query_allocation()))"
    )
    completed = subprocess.run([sys.executable, "-B", "-c", code], env=environment,
                               capture_output=True, text=True, check=True)
    result = json.loads(completed.stdout)
    assert result["identity_preserved"]
    # Two simultaneous 10k-pointer histories exceed160kB on supported64-bit
    # Python. Leave ample overhead above a single history for query/results.
    assert result["peak_bytes"] < 140_000, f"Carried query retained redundant scratch histories: {result['peak_bytes']} bytes"
