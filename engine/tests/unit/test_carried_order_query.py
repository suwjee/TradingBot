"""Exact carried-Order boundaries, eager failures, identity and temporary memory."""
from __future__ import annotations
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
