"""Bridge acceptance for the verified XAUUSD Reset-window A correction."""

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
SOURCE = ROOT / "market-data/raw/RAW FOREXCOM_XAUUSD 5S FROM 2026-08-25 04-23-20 TO 2026-09-01 14-59-50.json"
TEHRAN = ZoneInfo("Asia/Tehran")


def epoch(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=TEHRAN).timestamp())


@pytest.mark.skipif(not SOURCE.is_file(), reason="The selected XAUUSD history is unavailable")
def test_bearish_reset_windows_remove_early_a(monkeypatch):
    bridge_path = ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"
    spec = importlib.util.spec_from_file_location("xau_reset_window_bridge", bridge_path)
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
    arguments.extend([
        "--data", str(SOURCE),
        "--timeframe", "30",
        "--from-time", str(epoch("2026-08-25 23:40:00")),
        "--to-time", str(epoch("2026-08-26 02:22:00")),
        "--direction", "bearish",
    ])
    monkeypatch.setattr(sys, "argv", arguments)
    output = io.StringIO()
    with redirect_stdout(output):
        assert bridge.main() == 0

    payload = json.loads(output.getvalue())
    result = payload["directions"]["bearish"]
    reset_sources = [
        item["sourceTime"] for item in result["blueLines"] if item["kind"] == "reset"
    ]
    assert reset_sources == [
        epoch("2026-08-25 23:46:00"),
        epoch("2026-08-26 00:02:30"),
        epoch("2026-08-26 00:16:00"),
    ]
    assert epoch("2026-08-26 01:30:30") not in {
        item["sourceTime"] for item in result["blueLines"]
    }
    assert [item["sourceTime"] for item in result["aZones"]] == [
        epoch("2026-08-26 01:46:30")
    ]
    target = result["aZones"][0]
    assert target["reactionFirstTime"] == epoch("2026-08-26 01:47:00")
    assert target["reactionBreakTime"] == epoch("2026-08-26 01:52:00")
