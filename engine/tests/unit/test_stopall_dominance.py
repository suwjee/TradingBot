"""Exact-owner StopAll regressions using real lower-timeframe stop geometry."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))

from lifecycle_engine import StopAllDetector
from reaction_engine import Candle, MarketChronology


BASE = datetime(2000, 1, 1)


def moment(seconds: int) -> datetime:
    return BASE + timedelta(seconds=seconds)


def candle(index: int, seconds: int, *, low: str = "100", high: str = "100") -> Candle:
    stamp = moment(seconds)
    return Candle(
        index, stamp, stamp.strftime("%Y-%m-%d %H:%M:%S"), "GREEN",
        Decimal("100"), Decimal(high), Decimal(low), Decimal("100"),
    )


def chronology(direction: str, stop_seconds: tuple[int, ...] = ()) -> MarketChronology:
    lower = [
        candle(
            index, index * 5,
            low="99" if direction == "bullish" and index * 5 in stop_seconds else "100",
            high="101" if direction == "bearish" and index * 5 in stop_seconds else "100",
        )
        for index in range(61)
    ]
    main = [candle(index, index * 30) for index in range(11)]
    return MarketChronology(main, lower, 30)


def s(source: int, decision: int, color: str = "blue") -> SimpleNamespace:
    return SimpleNamespace(
        color=color, source_index=source // 30, source_time=moment(source),
        decision_index=decision // 30, decision_time=moment(decision // 30 * 30),
        decision_event_time=moment(decision), price=Decimal("100"),
        order_mode="B" if color == "red" else None,
    )


def e(
    source: int, decision: int, family: str = "red", number: int = 1,
) -> SimpleNamespace:
    return SimpleNamespace(
        family=family, number=number, source_index=source // 30,
        source_time=moment(source), price=Decimal("100"),
        decision_index=decision // 30, decision_time=moment(decision // 30 * 30),
        decision_event_time=moment(decision), order_direction="bullish",
        order_reaction_number=1, order_mode="B", order_causes=(),
        order_parent_stop_cause_time=None,
        order_first_index=source // 30, order_first_time=moment(source),
        order_break_index=source // 30, order_break_time=moment(source),
        order_confirmation_time=moment(decision),
        order_box_top=Decimal("100"), order_box_top_source_index=source // 30,
        order_box_top_source_time=moment(source),
        order_box_bottom=Decimal("100"), order_box_bottom_source_index=source // 30,
        order_box_bottom_source_time=moment(source),
        order_stop_level=Decimal("100"), order_stop_source_index=source // 30,
        order_stop_source_time=moment(source),
    )


def detect(
    direction: str, s_items: list[object], e_items: list[object],
    stops: tuple[int, ...] = (),
):
    return StopAllDetector(direction, s_items, e_items, chronology(direction, stops)).detect()


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("count", [1, 2, 3])
def test_exact_e_owner_arms_only_after_second_occurrence(direction, count):
    owner = [e(index * 30, index * 30 + 10) for index in range(count)]
    result = detect(direction, [], [*owner, e(180, 190, number=2)], (120,))
    assert len(result) == (1 if count >= 2 else 0)
    if result:
        assert (result[0].stopped_behavior_key, result[0].stopped_behavior_count) == (
            "E1 red", count,
        )


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_equal_level_does_not_stop_armed_blue_owner(direction):
    assert detect(direction, [s(0, 10), s(30, 40), s(180, 190, "red")], []) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize(
    ("s_items", "e_items"),
    [
        ([s(0, 10), s(30, 40)], [e(90, 190, "blue")]),
        ([s(90, 190, "red")], [e(0, 10, "blue"), e(30, 40, "blue")]),
        ([s(0, 10, "red"), s(30, 40, "red")], [e(90, 190, "red")]),
    ],
)
def test_higher_priority_formation_before_stop_disarms_lower_owner(
    direction, s_items, e_items,
):
    assert detect(direction, s_items, e_items, (120,)) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_stop_before_higher_priority_formation_remains_valid(direction):
    result = detect(direction, [s(0, 10), s(30, 40)], [e(90, 190, "blue")], (80,))
    assert len(result) == 1
    assert (result[0].gate_type, result[0].gate_event_time) == (
        "sequence-group-stop", moment(80),
    )


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("same_parent", [False, True])
@pytest.mark.parametrize("color", ["blue", "red"])
def test_e_child_of_armed_owner_can_donate_at_its_retrospective_source(
    direction, same_parent, color,
):
    first = s(0, 10, color)
    latest = s(30, 40, color)
    donor = e(120, 190, color)
    donor.parent_type = "S"
    donor.parent_source_index = latest.source_index
    donor.parent_source_time = latest.source_time if same_parent else first.source_time
    donor.parent_price = latest.price
    donor.parent_stop_event_time = moment(120)

    result = detect(direction, [first, latest], [donor], (120,))

    if not same_parent:
        assert result == []
    else:
        assert len(result) == 1
        assert (
            result[0].gate_type,
            result[0].gate_event_time,
            result[0].stopped_behavior_key,
            result[0].stopped_behavior_count,
        ) == ("sequence-group-stop", moment(120), f"S {color}", 2)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_single_s_owner_cannot_use_direct_e_child_stop(direction):
    owner = s(30, 40, "red")
    donor = e(120, 190, "red")
    donor.parent_type = "S"
    donor.parent_source_index = owner.source_index
    donor.parent_source_time = owner.source_time
    donor.parent_price = owner.price
    donor.parent_stop_event_time = moment(120)

    assert detect(direction, [owner], [donor], (120,)) == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_stopped_blue_e_owner_can_use_later_red_s_donor(direction):
    result = detect(
        direction, [s(180, 190, "red")],
        [e(0, 10, "blue"), e(30, 40, "blue")], (120,),
    )
    assert len(result) == 1
    assert (result[0].gate_type, result[0].gate_event_time) == (
        "opposite-s-group-stop", moment(120),
    )
    assert (result[0].stopped_behavior_key, result[0].stopped_behavior_count) == (
        "E1 blue", 2,
    )


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_completed_stop_survives_intervening_higher_s_without_s_donor(direction):
    higher_s = s(90, 100, "red")
    higher_s.order_mode = "A"
    result = detect(
        direction, [s(0, 10), s(30, 40), higher_s],
        [e(180, 190, "red")], (80,),
    )
    assert len(result) == 1
    assert (result[0].gate_type, result[0].gate_event_time) == (
        "sequence-group-stop", moment(80),
    )
    assert (result[0].stopped_behavior_key, result[0].stopped_behavior_count) == (
        "S blue", 2,
    )


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("family", ["blue", "red"])
def test_different_e_numbers_do_not_form_an_exact_repeat(direction, family):
    result = detect(
        direction, [s(180, 190, "red")],
        [e(0, 10, family, 1), e(30, 40, family, 2)], (120,),
    )
    assert result == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_lower_blue_occurrences_cannot_arm_behind_red_e(direction):
    result = detect(
        direction, [s(60, 70), s(90, 100), s(180, 190, "red")],
        [e(0, 10, "red")], (120,),
    )
    assert result == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_lower_e_blue_occurrences_cannot_arm_behind_red_e(direction):
    result = detect(
        direction, [s(180, 190, "red")],
        [e(0, 10, "red"), e(60, 70, "blue"), e(90, 100, "blue")],
        (120,),
    )
    assert result == []


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_hard_stopall_resets_exact_owner_count(direction):
    result = detect(
        direction,
        [s(0, 10), s(30, 40), s(150, 160), s(210, 220, "red")],
        [e(90, 110, "blue")], (80, 180),
    )
    assert len(result) == 1
    assert result[0].source_time == moment(90)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_valid_stopall_chain_keeps_existing_numbering(direction):
    result = detect(
        direction,
        [s(0, 10), s(30, 40)],
        [e(90, 110, "blue"), e(180, 190, "red")],
        (80, 120),
    )
    assert [(item.number, item.gate_type, item.gate_event_time) for item in result] == [
        (1, "sequence-group-stop", moment(80)),
        (2, "stopall-stop", moment(120)),
    ]
