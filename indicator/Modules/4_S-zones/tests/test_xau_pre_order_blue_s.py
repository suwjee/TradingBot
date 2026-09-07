"""Regression for the user-confirmed XAUUSD pre-order Blue S."""

from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime
import importlib.util
import io
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

import pytest


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "market-data/raw" / (
    "RAW_FOREXCOM_XAUUSD_1S_FROM_2026_08_18_04_44_40_TO_2026_09_05_00.json"
)
TEHRAN = ZoneInfo("Asia/Tehran")


def epoch(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=TEHRAN).timestamp())


def run_bullish_window(monkeypatch, from_time: str, to_time: str):
    bridge_path = ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"
    spec = importlib.util.spec_from_file_location(
        "xau_pre_order_blue_s_bridge", bridge_path
    )
    assert spec is not None and spec.loader is not None
    bridge = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = bridge
    spec.loader.exec_module(bridge)

    arguments = [str(bridge_path)]
    for flag, module in [
        ("engine", "1_reaction-detector/app/Reaction-detection-new.py"),
        ("blue-engine", "2_blue-line/app/blue_line.py"),
        ("a-engine", "3_A-zone/app/a_detector.py"),
        ("s-engine", "4_S-zones/app/s_detector.py"),
        ("e-engine", "5_E-zones/app/e_detector.py"),
        ("stopall-engine", "6_StopAll/app/stopall_detector.py"),
    ]:
        arguments.extend(
            ["--" + flag, str(ROOT / "indicator/Modules" / module)]
        )
    arguments.extend(
        [
            "--data",
            str(SOURCE),
            "--timeframe",
            "30",
            "--from-time",
            str(epoch(from_time)),
            "--to-time",
            str(epoch(to_time)),
            "--direction",
            "bullish",
        ]
    )
    monkeypatch.setattr(sys, "argv", arguments)
    output = io.StringIO()
    with redirect_stdout(output):
        assert bridge.main() == 0
    return json.loads(output.getvalue())["directions"]["bullish"]


@pytest.mark.skipif(not SOURCE.is_file(), reason="The selected XAUUSD history is unavailable")
def test_bullish_pre_order_candidate_becomes_blue_s(monkeypatch):
    bullish = run_bullish_window(
        monkeypatch, "2026-08-19 22:00:00", "2026-08-20 04:00:00"
    )

    a_by_source = {item["sourceTime"]: item for item in bullish["aZones"]}
    assert epoch("2026-08-20 02:09:30") in a_by_source

    s_by_source = {item["sourceTime"]: item for item in bullish["sZones"]}
    target = s_by_source[epoch("2026-08-20 02:29:00")]
    assert target["color"] == "blue"
    assert target["price"] == "4516.63"
    assert target["aSourceTime"] == epoch("2026-08-20 02:09:30")
    assert target["aStopEventTime"] == epoch("2026-08-20 02:29:02")
    assert target["orderFirstTime"] == epoch("2026-08-20 02:37:30")
    assert target["orderStopLevel"] == "4523.715"
    assert target["orderStopSourceTime"] == epoch("2026-08-20 02:36:30")
    assert target["decisionTime"] == epoch("2026-08-20 02:53:30")
    assert target["decisionEventTime"] == epoch("2026-08-20 02:53:30")
    assert epoch("2026-08-20 03:05:00") not in s_by_source


@pytest.mark.skipif(not SOURCE.is_file(), reason="The selected XAUUSD history is unavailable")
def test_stopped_dominant_s_advances_lifecycle_without_hiding_half_leg_a(monkeypatch):
    bullish = run_bullish_window(
        monkeypatch, "2026-08-18 21:34:00", "2026-08-18 23:18:00"
    )
    assert [
        item["sourceTime"] for item in bullish["aZones"]
        if item["calculationValid"]
    ] == [
        epoch("2026-08-18 21:47:00"),
        epoch("2026-08-18 22:26:30"),
        epoch("2026-08-18 22:40:00"),
        epoch("2026-08-18 23:04:30"),
    ]
    assert [item["sourceTime"] for item in bullish["sZones"]] == [
        epoch("2026-08-18 21:53:30"),
        epoch("2026-08-18 23:07:00"),
    ]
    assert bullish["eZones"] == []
    assert bullish["stopAlls"] == []


@pytest.mark.skipif(not SOURCE.is_file(), reason="The selected XAUUSD history is unavailable")
def test_strict_leg_start_dominance_hides_invalid_labels_and_blocks_downstream(monkeypatch):
    bullish = run_bullish_window(
        monkeypatch, "2026-08-18 18:54:00", "2026-08-18 23:19:30"
    )
    a_by_time = {item["sourceTime"]: item for item in bullish["aZones"]}
    expected_valid = {
        epoch("2026-08-18 19:47:00"),
        epoch("2026-08-18 20:43:30"),
        epoch("2026-08-18 21:47:00"),
        epoch("2026-08-18 22:26:30"),
        epoch("2026-08-18 22:40:00"),
        epoch("2026-08-18 23:04:30"),
    }
    expected_invalid = {
        epoch("2026-08-18 20:07:00"),
        epoch("2026-08-18 21:34:00"),
        epoch("2026-08-18 22:18:30"),
        epoch("2026-08-18 23:15:00"),
    }

    assert {
        source for source, item in a_by_time.items()
        if item["calculationValid"]
    } == expected_valid
    assert expected_invalid.isdisjoint(a_by_time)
    assert all(item["calculationValid"] for item in a_by_time.values())
    assert {
        item["sourceTime"] for item in bullish["sZones"]
        if item["calculationValid"]
    } == {
        epoch("2026-08-18 20:02:00"),
        epoch("2026-08-18 20:49:30"),
        epoch("2026-08-18 21:53:30"),
        epoch("2026-08-18 23:07:00"),
    }
    # E4 was formed by state before this independent range and must disappear.
    # The Blue E formed entirely inside the selected virtual file remains.
    assert [
        (item["sourceTime"], item["family"], item["number"])
        for item in bullish["eZones"]
    ] == [
        (epoch("2026-08-18 20:20:00"), "blue", 1),
    ]


@pytest.mark.skipif(not SOURCE.is_file(), reason="The selected XAUUSD history is unavailable")
def test_isolated_range_does_not_inherit_the_prior_stopped_owner(monkeypatch):
    bullish = run_bullish_window(
        monkeypatch, "2026-08-20 08:08:00", "2026-08-20 11:01:00"
    )
    a_sources = {item["sourceTime"] for item in bullish["aZones"]}

    assert a_sources == {
        epoch("2026-08-20 08:44:00"),
        epoch("2026-08-20 09:49:00"),
    }


@pytest.mark.skipif(not SOURCE.is_file(), reason="The selected XAUUSD history is unavailable")
def test_full_file_preserves_verified_half_leg_behaviors(monkeypatch):
    bullish = run_bullish_window(
        monkeypatch, "2026-08-18 04:44:40", "2026-09-03 00:29:39"
    )
    a_sources = {
        item["sourceTime"] for item in bullish["aZones"]
        if item["calculationValid"]
    }
    s_sources = {
        item["sourceTime"] for item in bullish["sZones"]
        if item["calculationValid"]
    }
    assert {
        epoch("2026-08-18 21:47:00"),
        epoch("2026-08-18 22:26:30"),
        epoch("2026-08-18 22:40:00"),
        epoch("2026-08-18 23:04:30"),
    } <= a_sources
    assert {
        epoch("2026-08-18 21:53:30"),
        epoch("2026-08-18 23:07:00"),
    } <= s_sources
    assert epoch("2026-08-18 22:55:00") not in s_sources


@pytest.mark.skipif(not SOURCE.is_file(), reason="The selected XAUUSD history is unavailable")
def test_stopped_s_parent_remains_visible_when_it_builds_e(monkeypatch):
    bullish = run_bullish_window(
        monkeypatch, "2026-08-18 04:44:40", "2026-08-18 18:54:30"
    )
    s_by_source = {item["sourceTime"]: item for item in bullish["sZones"]}
    parent = s_by_source[epoch("2026-08-18 14:35:00")]
    assert parent["color"] == "blue"
    assert parent["price"] == "4393.685"
    assert parent["aSourceTime"] in {
        item["sourceTime"] for item in bullish["aZones"]
    }

    e_by_source = {item["sourceTime"]: item for item in bullish["eZones"]}
    child = e_by_source[epoch("2026-08-18 14:41:30")]
    assert (child["family"], child["number"]) == ("blue", 1)
    assert child["parentSourceTime"] == parent["sourceTime"]
    assert child["parentPrice"] == parent["price"]
