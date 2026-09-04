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
SOURCE = (
    ROOT
    / "market-data/raw"
    / "RAW FOREXCOM_XAUUSD 1S FROM 2026-08-18 04-44-40 TO 2026-09-03 00-29-39.json"
)
TEHRAN = ZoneInfo("Asia/Tehran")


def epoch(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=TEHRAN).timestamp())


@pytest.mark.skipif(not SOURCE.is_file(), reason="The selected XAUUSD history is unavailable")
def test_bullish_pre_order_candidate_becomes_blue_s(monkeypatch):
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
            str(epoch("2026-08-19 22:00:00")),
            "--to-time",
            str(epoch("2026-08-20 04:00:00")),
            "--direction",
            "bullish",
        ]
    )
    monkeypatch.setattr(sys, "argv", arguments)
    output = io.StringIO()
    with redirect_stdout(output):
        assert bridge.main() == 0

    bullish = json.loads(output.getvalue())["directions"]["bullish"]
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
