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
        "T", "T", "T", "F", "T", "F", "T", "F", "T", "T",
    ]
    assert [i for i, row in enumerate(group["stopAlls"]) if row.get("trueFalseRepeated")] == [1, 6, 7, 8]
    assert [row["trueFalse"] for row in group[primary_key]] == ["T", "F", "F"]
    assert "trueFalse" not in group[other_key][0]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("colors, expected", [
    ("bB bB bbbB", "TFTFTTTT"),
    ("bB bB bb rR", "TFTFTTTF"),
    ("rbbrR", "TTTTF"),
])
def test_basic_schematic_repetition_restarts(direction, colors, expected):
    from true_false import apply_true_false

    group = {"sZones": [], "eZones": []}
    rows = []
    for time, marker in enumerate(colors.replace(" ", "")):
        family = "blue" if marker.lower() == "b" else "red"
        if marker.islower():
            parent = time
            row = behavior(time, family=family)
            group["sZones"].append(row)
        else:
            row = behavior(time, number=1, family=family, parent=parent)
            group["eZones"].append(row)
        rows.append(row)
    apply_true_false(direction, group)
    assert [row["trueFalse"] for row in rows] == list(expected)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
@pytest.mark.parametrize("lengths, verdicts, overlaps", [
    ((3, 4), ("TFT", "TFTT"), (0, 3)),
    ((3, 3, 2, 4, 1, 2, 5), ("TFT", "TFT", "TF", "TFTT", "T", "TT", "TFTFT"), (0, 3, 0, 3, 0, 1, 4)),
    ((1, 2, 2), ("T", "TT", "TF"), (0, 1, 2)),
])
def test_stopall_schematic_series(direction, lengths, verdicts, overlaps):
    from true_false import apply_true_false

    series = []
    start = 0
    for length in lengths:
        series.append([behavior(start + number, number=number) for number in range(1, length + 1)])
        start += length
    apply_true_false(direction, {"stopAlls": [row for rows in series for row in rows]})
    assert ["".join(row["trueFalse"] for row in rows) for rows in series] == list(verdicts)
    assert [[row.get("trueFalseRepeated", False) for row in rows] for rows in series] == [
        [number < overlap for number in range(length)] for length, overlap in zip(lengths, overlaps)
    ]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_largest_stopall_repeat_rebases_the_prefix_only_after_confirmation_close(direction):
    from true_false import apply_true_false

    prior = [behavior(time, number=number) for time, number in enumerate((1, 2, 3, 4, 1))]
    current = [behavior(4 + number, number=number) for number in range(1, 6)]

    def evaluate(visible, closed_through):
        apply_true_false(direction, {"stopAlls": prior + visible},
                         stopall_confirmation_closed=lambda row: row["sourceTime"] <= closed_through)
        return ("".join(row["trueFalse"] for row in visible),
                [row["number"] for row in visible if row.get("trueFalseRepeated")])

    assert evaluate(current[:3], 7) == ("TTF", [1])
    assert evaluate(current[:4], 7) == ("TTFT", [1])
    assert evaluate(current[:4], 8) == ("TFTF", [1, 2, 3, 4])
    assert evaluate(current, 9) == ("TFTFT", [1, 2, 3, 4])


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


@pytest.mark.parametrize("direction, primary_key", [("bullish", "primaryLows"), ("bearish", "primaryHighs")])
def test_after_primary_the_first_series_has_no_repetition_marker(direction, primary_key):
    from true_false import apply_true_false

    stops = [behavior(time, number=number) for time, number in [(1, 1), (3, 1), (4, 1), (5, 1), (6, 2)]]
    apply_true_false(direction, {"stopAlls": stops, primary_key: [behavior(2, number=1)]})
    assert [row["trueFalse"] for row in stops] == ["T"] * 5
    assert [row.get("trueFalseRepeated", False) for row in stops] == [False, False, True, True, False]


def test_live_stopall_repeats_only_after_the_confirmation_candle_closes(tmp_path, monkeypatch):
    from live_pipeline import LivePipelineContinuation

    start = 1_795_000_020
    args = setup("bullish", tmp_path / "raw.json", start, start + 210)
    args.raw_timeframe = 5
    worker = LivePipelineContinuation(args, pipeline.load_engines(args, {}))
    stopalls = [dict(behavior(start + offset, number=number), decisionTime=start + decision)
                for offset, number, decision in [(0, 1, 30), (30, 2, 60), (60, 3, 90),
                                                  (90, 1, 120), (120, 2, 150), (150, 3, 180)]]
    group = {"stopAlls": stopalls}
    monkeypatch.setattr(pipeline, "build_direction_output", lambda *_: deepcopy(group))
    rows = [dict(time=start + offset, low=100, high=101, open=100, close=101)
            for offset in range(0, 210, 5)]
    before = worker.append(rows[:-1])["directions"]["bullish"]["stopAlls"]
    assert [row["trueFalse"] for row in before[3:]] == ["T", "F", "T"]
    assert all("trueFalseRepeated" not in row for row in before)
    closed = worker.append(rows[-1:])["directions"]["bullish"]["stopAlls"]
    assert [row["trueFalse"] for row in closed[3:]] == ["T", "F", "T"]
    assert all(row["trueFalseRepeated"] for row in closed[3:])


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
