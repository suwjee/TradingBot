from copy import deepcopy
from datetime import datetime, timedelta
from decimal import Decimal
import json
from types import SimpleNamespace

import pytest

from test_live_pipeline_continuation import pipeline, setup


def behavior(time, *, number=None, family="red", parent=None, price="100"):
    row = {"sourceTime": time, "price": price}
    if number is None:
        row["color"] = family
    else:
        row.update(number=number, family=family, parentSourceTime=parent)
    return row


@pytest.mark.parametrize("direction, primary_key, other_key", [
    ("bullish", "primaryLows", "primaryHighs"),
    ("bearish", "primaryHighs", "primaryLows"),
])
def test_three_groups_and_unequal_repeat_labels(direction, primary_key, other_key):
    from true_false import apply_true_false

    group = {
        "sZones": [behavior(1), behavior(2), behavior(7)],
        "eZones": [
            behavior(3, number=1, parent=2),
            behavior(4, number=2, parent=3),
            behavior(8, number=1, parent=7),
            behavior(9, number=2, parent=8),
        ],
        "stopAlls": [behavior(time, number=number) for time, number in
                     enumerate((1, 1, 2, 3, 1, 2, 1, 2, 3, 4), 20)],
        primary_key: [behavior(i + 35, number=i) for i in (1, 2, 3)],
        other_key: [behavior(40, number=1)],
    }
    apply_true_false(direction, group)
    assert [row["trueFalse"] for row in group["sZones"]] == ["T", "T", "T"]
    assert [row["trueFalse"] for row in group["eZones"]] == ["T", "F", "F", "T"]
    assert [row["trueFalse"] for row in group["stopAlls"]] == [
        "T", None, "T", "F", None, None, None, None, "T", "F",
    ]
    assert [row["trueFalse"] for row in group[primary_key]] == ["T", "F", "F"]
    assert "trueFalse" not in group[other_key][0]


@pytest.mark.parametrize("direction, primary_key, other_key", [
    ("bullish", "primaryLows", "primaryHighs"),
    ("bearish", "primaryHighs", "primaryLows"),
])
def test_each_directional_primary_restarts_stopall_verdicts(direction, primary_key, other_key):
    from true_false import apply_true_false

    stops = [
        behavior(time, number=number)
        for time, number in [(20, 1), (21, 2), (22, 3), (23, 4),
                             (25, 1), (27, 2), (28, 3), (30, 4), (31, 5)]
    ]
    group = {
        "stopAlls": list(reversed(stops)),
        primary_key: [
            {**behavior(24, number=1), "decisionEventTime": 28},
            behavior(29, number=2),
        ],
        other_key: [behavior(26, number=1)],
    }
    apply_true_false(direction, group)

    assert [row["trueFalse"] for row in stops] == [
        "T", "F", "T", "F", "T", "F", "T", "T", "F",
    ]
    assert [row["trueFalse"] for row in group[primary_key]] == ["T", "F"]
    assert "trueFalse" not in group[other_key][0]


@pytest.mark.parametrize("direction, price, peer_price, cross", [
    ("bullish", "100", "99", "99.5"),
    ("bearish", "100", "101", "100.5"),
])
def test_repeated_f_uses_latest_reference_and_strict_original_direction(
    direction, price, peer_price, cross,
):
    from true_false import apply_true_false, repair_crossing_lookup

    start = datetime(2026, 1, 1)
    to_time = lambda second: start + timedelta(seconds=second)
    to_epoch = lambda timestamp: int((timestamp - start).total_seconds())
    from reaction_engine import LowerTimeframeIndex

    index = LowerTimeframeIndex([
        SimpleNamespace(timestamp=to_time(second), low=Decimal(value), high=Decimal(value))
        for second, value in [(1, peer_price), (5, price), (12, price), (14, cross)]
    ])
    group = {
        "sZones": [behavior(0, family="blue"), behavior(3, family="blue"), behavior(7)],
        "eZones": [behavior(1, number=1, family="blue", parent=0, price=peer_price),
                   behavior(5, number=1, family="blue", parent=3, price=price)],
    }
    earlier_horizon = deepcopy(group)
    apply_true_false(direction, earlier_horizon,
                     repair_crossing_lookup(index, to_time, to_epoch, through=to_time(13)))
    assert "trueFalseRepairTime" not in earlier_horizon["eZones"][1]
    apply_true_false(direction, group,
                     repair_crossing_lookup(index, to_time, to_epoch, through=to_time(15)))
    first, second = group["eZones"]
    assert first["trueFalse"] == second["trueFalse"] == "F"
    assert "trueFalseRepairTime" not in first
    assert second["trueFalseRepairTime"] == 14
    assert group["sZones"][-1]["trueFalse"] == "T"


def test_final_behavior_takes_precedence_over_hidden_donor():
    from true_false import apply_true_false

    group = {
        "sZones": [behavior(1), behavior(2), behavior(4)],
        "eZones": [behavior(3, number=1, parent=1)],
        "stopAlls": [behavior(2, number=1)],
    }
    apply_true_false("bullish", group)
    assert "trueFalse" not in group["sZones"][1]
    assert group["eZones"][0]["trueFalse"] == "F"
    assert group["stopAlls"][0]["trueFalse"] == "T"


def test_repair_uses_lower_raw_inside_last_visible_candle(tmp_path, monkeypatch):
    from live_pipeline import LivePipelineContinuation

    start = 1_795_000_020
    source = tmp_path / "raw.json"
    rows = [
        dict(time=start + offset, low=low, high=105, open=104, close=104)
        for offset, low in [(0, 102), (30, 98), (60, 101), (90, 100), (120, 100), (125, 99), (150, 96)]
    ]
    source.write_text(json.dumps(rows), encoding="utf-8")
    args = setup("bullish", source, start, start + 120)
    engines = pipeline.load_engines(args, {})
    market = pipeline.prepare_market_context(args, engines, {})
    group = {
        "sZones": [behavior(start, family="blue"), behavior(start + 60, family="blue")],
        "eZones": [
            behavior(start + 30, number=1, family="blue", parent=start, price="98"),
            behavior(start + 90, number=1, family="blue", parent=start + 60),
        ],
    }
    monkeypatch.setattr(pipeline, "build_direction_output", lambda *_: deepcopy(group))
    state = SimpleNamespace(directions=("bullish",), primary_result=None)
    result = pipeline.build_response_payload(args, engines, market, state, {}, 0)
    assert result["actualTo"] == start + 120
    assert result["directions"]["bullish"]["eZones"][1]["trueFalseRepairTime"] == start + 125

    live_args = setup("bullish", source, start, start + 90)
    live = LivePipelineContinuation(live_args, engines)
    seed = live.append(rows[:4])
    assert "trueFalseRepairTime" not in seed["directions"]["bullish"]["eZones"][1]
    updated = live.append(rows[4:6])
    assert updated["directions"]["bullish"]["eZones"][1]["trueFalseRepairTime"] == start + 125
