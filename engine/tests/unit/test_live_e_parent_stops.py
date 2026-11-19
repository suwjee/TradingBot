from copy import deepcopy
from dataclasses import replace
from decimal import Decimal

import pytest

from test_order_audit_lifecycle_contracts import candle, candidate, detector_state, moment
from e_zone_detector import EZoneDetector, LiveEContinuation
from lifecycle_engine import sequence_priority
from reaction_engine import MarketChronology, mirror_candle


def market(direction, count, *, crossing=None):
    main = [candle(index, index * 30) for index in range(count)]
    lower = [
        candle(index, index, low="99" if index == crossing else "100")
        for index in range(30 * count)
    ]
    if direction == "bearish":
        main = [mirror_candle(item) for item in main]
        lower = [mirror_candle(item) for item in lower]
    return MarketChronology(main, lower, 30)


def detector(direction, chronology, live=None, end_index=None):
    return EZoneDetector(
        direction, [], [], [], [], chronology, end_index=end_index,
        sequence_priority=sequence_priority, live_continuation=live,
    )


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_live_accepted_order_stream_reuses_the_proven_crossing_state(direction, monkeypatch):
    live = LiveEContinuation()
    initial = market(direction, 3)
    _, parent, _ = detector_state(direction)
    physical = candidate(1, 2)
    level = Decimal("120.00" if direction == "bullish" else "-120.00")
    confirmation = moment(65)

    def register(engine):
        crossed = engine.cross_order(confirmation, level)
        engine.order_audit[(1, 2)] = {
            "reaction_number": 1,
            "reaction": physical,
            "confirmation_time": confirmation,
            "stop_level": level,
            "stop_source_index": 1,
            "stop_source_time": moment(30),
            "stop_cross": crossed,
        }
        engine._index_order_audit_identity((1, 2), confirmation)

    def full_ledger_scan(*_args):
        pytest.fail("A proven crossing state must be eligible for the native accepted-Order stream.")

    live.advance(initial, first_dirty_main=0)
    seed = detector(direction, initial, live)
    register(seed)
    monkeypatch.setattr(seed, "_post_stop_accepted_orders_for_parent", full_ledger_scan)
    assert list(seed._iter_post_stop_accepted_orders(parent, moment(60))) == []

    extension = market(direction, 4)
    crossing = candle(95, 95, high="121")
    if direction == "bearish":
        crossing = mirror_candle(crossing)
    lower = [*extension.seconds]
    lower[95] = crossing
    revised = MarketChronology(extension.candles, lower, 30)
    live.advance(revised, first_dirty_main=3)
    warm = detector(direction, revised, live)
    register(warm)
    warm.sequence_resets = {moment(95): 1}
    monkeypatch.setattr(warm, "_post_stop_accepted_orders_for_parent", full_ledger_scan)
    assert list(warm._iter_post_stop_accepted_orders(parent, moment(60))) == []

    warm.sequence_resets = {}
    match, = warm._iter_post_stop_accepted_orders(parent, moment(60))
    assert match[1] is physical
    assert match[3].as_tuple() == level.as_tuple()
    assert match[6] == (3, moment(90), moment(95))
    with pytest.raises(ValueError, match="Advance the live E state"):
        seed.cross_order(confirmation, level)


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_open_e_parent_stop_resumes_at_the_first_new_lower_row(direction, monkeypatch):
    level = Decimal("100" if direction == "bullish" else "-100")
    live = LiveEContinuation()
    initial = market(direction, 3)
    live.advance(initial, first_dirty_main=0)
    assert detector(direction, initial, live)._first_parent_stop(moment(12), level) is None

    extension = market(direction, 4, crossing=95)
    live.advance(extension, first_dirty_main=3)
    engine = detector(direction, extension, live)
    calls = []
    scan = engine._search_parent_stop

    def track(start, stop, price):
        calls.append(start)
        return scan(start, stop, price)

    monkeypatch.setattr(engine, "_search_parent_stop", track)
    assert engine._first_parent_stop(moment(12), level) == (3, moment(95))
    assert calls == [moment(90)]

    extension = market(direction, 5, crossing=95)
    live.advance(extension, first_dirty_main=4)
    engine = detector(direction, extension, live)

    def replay(*_args):
        pytest.fail("An already confirmed strict parent stop was searched again.")

    monkeypatch.setattr(engine, "_search_parent_stop", replay)
    assert engine._first_parent_stop(moment(12), level) == (3, moment(95))
    assert detector(direction, extension, live, end_index=2)._first_parent_stop(moment(12), level) is None


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_dirty_preview_revokes_parent_stop_and_retains_negative_prefix(direction, monkeypatch):
    level = Decimal("100" if direction == "bullish" else "-100")
    live = LiveEContinuation()
    initial = market(direction, 4, crossing=95)
    live.advance(initial, first_dirty_main=0)
    assert detector(direction, initial, live)._first_parent_stop(moment(12), level) == (3, moment(95))

    revised = market(direction, 5, crossing=124)
    live.advance(revised, first_dirty_main=3)
    engine = detector(direction, revised, live)
    calls = []
    scan = engine._search_parent_stop

    def track(start, stop, price):
        calls.append(start)
        return scan(start, stop, price)

    monkeypatch.setattr(engine, "_search_parent_stop", track)
    expected = detector(direction, revised)._first_parent_stop(moment(12), level)
    assert engine._first_parent_stop(moment(12), level) == expected == (4, moment(124))
    assert calls == [moment(90)]


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_unchanged_e_races_reuse_candidate_and_accepted_state(direction, monkeypatch):
    reference, parent, physical = detector_state(direction)
    chronology = reference.chronology
    live = LiveEContinuation()

    def fresh(current):
        return EZoneDetector(
            direction, [], [physical], [parent], [], current,
            sequence_priority=sequence_priority, live_continuation=live,
        )

    live.advance(chronology, first_dirty_main=0)
    seed = fresh(chronology)
    expected = seed.detect()
    assert expected and seed._last_candidate_zones
    next_chronology = MarketChronology(
        [*chronology.candles, candle(12, 360)],
        [*chronology.seconds, *(candle(i, i) for i in range(360, 390))],
        30,
    )
    live.advance(next_chronology, first_dirty_main=12)
    extended = fresh(next_chronology)

    def replay(*_args, **_kwargs):
        pytest.fail("An unchanged E candidate or reconciliation was calculated again.")

    monkeypatch.setattr(extended, "_build_zone", replay)
    monkeypatch.setattr(extended, "_compute_reconciliation", replay)
    actual = extended.detect()
    assert actual == expected
    assert extended._last_candidate_zones[0] is seed._last_candidate_zones[0]
    assert extended.visual_lifecycle_starts == seed.visual_lifecycle_starts
    assert extended.order_audit == seed.order_audit


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_changed_accepted_order_provenance_reopens_reconciliation(direction):
    reference, parent, physical = detector_state(direction)
    chronology = reference.chronology
    live = LiveEContinuation()
    live.advance(chronology, first_dirty_main=0)
    engine = EZoneDetector(
        direction, [], [physical], [parent], [], chronology,
        sequence_priority=sequence_priority, live_continuation=live,
    )
    candidate = engine._zone("blue", 1, "S", parent, moment(125))
    assert candidate is not None
    assert engine._reconcile_candidate_chains([candidate]) == [candidate]
    engine.invalid_s_root_identities.add((parent.source_time, parent.source_index))
    assert engine._reconcile_candidate_chains([candidate]) == []


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_a_new_independent_e_root_keeps_the_settled_prefix(direction):
    reference, parent, physical = detector_state(direction)
    chronology = reference.chronology
    live = LiveEContinuation()
    live.advance(chronology, first_dirty_main=0)
    initial = EZoneDetector(
        direction, [], [physical], [parent], [], chronology,
        sequence_priority=sequence_priority, live_continuation=live,
    )
    candidate = initial._zone("blue", 1, "S", parent, moment(125))
    assert candidate is not None
    original, = initial._reconcile_candidate_chains([candidate])

    new_parent = replace(parent, source_index=10, source_time=moment(300),
                         a_source_time=candidate.source_time, decision_event_time=moment(302))
    later = replace(
        candidate, parent_source_index=10, parent_source_time=moment(300),
        parent_stop_event_time=moment(305), source_index=11, source_time=moment(330),
        decision_event_time=moment(340),
    )
    live.advance(chronology, first_dirty_main=10)
    extended = EZoneDetector(
        direction, [], [physical], [parent, new_parent], [], chronology,
        sequence_priority=sequence_priority, live_continuation=live,
    )
    extended.order_audit = deepcopy(initial.order_audit)
    batch = EZoneDetector(direction, [], [physical], [parent, new_parent], [], chronology,
                          sequence_priority=sequence_priority)
    batch.order_audit = deepcopy(initial.order_audit)
    expected = batch._reconcile_candidate_chains([candidate, later])
    result = extended._reconcile_candidate_chains([candidate, later])
    assert len(result) == 2
    assert result == expected
    assert result[0] is original
