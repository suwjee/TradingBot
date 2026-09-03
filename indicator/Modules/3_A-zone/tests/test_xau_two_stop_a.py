"""Regression coverage for ordinary and special two-Blue-stop A ownership."""

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
def test_bullish_two_stop_a_ownership_and_source_range(monkeypatch):
    bridge_path = ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"
    spec = importlib.util.spec_from_file_location("xau_two_stop_a_bridge", bridge_path)
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
        arguments.extend(["--" + flag, str(ROOT / "indicator/Modules" / module)])
    arguments.extend(
        [
            "--data",
            str(SOURCE),
            "--timeframe",
            "30",
            "--from-time",
            str(epoch("2026-08-18 04:44:40")),
            "--to-time",
            str(epoch("2026-08-20 21:24:00")),
            "--direction",
            "bullish",
        ]
    )
    monkeypatch.setattr(sys, "argv", arguments)
    output = io.StringIO()
    with redirect_stdout(output):
        assert bridge.main() == 0

    zones = json.loads(output.getvalue())["directions"]["bullish"]["aZones"]
    by_source = {item["sourceTime"]: item for item in zones}

    ordinary = by_source[epoch("2026-08-19 23:44:30")]
    assert ordinary["blue1SourceTime"] == epoch("2026-08-19 23:23:00")
    assert ordinary["blue2SourceTime"] == epoch("2026-08-19 23:39:00")
    assert ordinary["triggerTime"] == epoch("2026-08-19 23:42:30")
    assert ordinary["reactionFirstTime"] == epoch("2026-08-19 23:45:30")
    assert ordinary["reactionBreakTime"] == epoch("2026-08-19 23:46:00")
    assert ordinary["price"] == "4505.28"

    assert epoch("2026-08-19 23:42:00") not in by_source
    assert epoch("2026-08-20 02:02:00") not in by_source
    assert epoch("2026-08-20 02:09:30") in by_source
    assert epoch("2026-08-20 15:56:00") in by_source
    assert epoch("2026-08-20 16:00:00") not in by_source

    reaction_times = [item["reactionFirstTime"] for item in zones]
    assert len(reaction_times) == len(set(reaction_times))
