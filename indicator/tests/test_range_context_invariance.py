"""The calculation result must not depend on the selected viewport start."""

from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime
import importlib.util
import io
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "market-data/raw/RAW FOREXCOM_XAUUSD 1S FROM 2026-08-18 04-44-40 TO 2026-09-05 00-29-39.json"
TEHRAN = ZoneInfo("Asia/Tehran")
MODULES = ROOT / "indicator/Modules"


def epoch(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=TEHRAN).timestamp())


def run_bridge(from_time: int, to_time: int) -> dict:
    bridge_path = ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"
    name = f"range_context_bridge_{from_time}_{to_time}"
    spec = importlib.util.spec_from_file_location(name, bridge_path)
    assert spec is not None and spec.loader is not None
    bridge = importlib.util.module_from_spec(spec)
    sys.modules[name] = bridge
    spec.loader.exec_module(bridge)
    arguments = [
        str(bridge_path),
        "--data", str(SOURCE),
        "--timeframe", "30",
        "--direction", "bullish",
        "--from-time", str(from_time),
        "--to-time", str(to_time),
    ]
    for flag, relative in (
        ("engine", "1_reaction-detector/app/Reaction-detection-new.py"),
        ("blue-engine", "2_blue-line/app/blue_line.py"),
        ("a-engine", "3_A-zone/app/a_detector.py"),
        ("s-engine", "4_S-zones/app/s_detector.py"),
        ("e-engine", "5_E-zones/app/e_detector.py"),
        ("stopall-engine", "6_StopAll/app/stopall_detector.py"),
    ):
        arguments.extend([f"--{flag}", str(MODULES / relative)])
    previous = sys.argv
    output = io.StringIO()
    try:
        sys.argv = arguments
        with redirect_stdout(output):
            assert bridge.main() == 0
    finally:
        sys.argv = previous
    return json.loads(output.getvalue())["directions"]["bullish"]


def test_common_output_is_invariant_to_viewport_start():
    early_from = epoch("2026-08-18 04:44:40")
    late_from = epoch("2026-08-20 00:00:00")
    common_to = epoch("2026-08-21 00:00:00")
    early = run_bridge(early_from, common_to)
    late = run_bridge(late_from, common_to)
    fields = {
        "reactions": "firstTime",
        "resets": "time",
        "blueLines": "sourceTime",
        "aZones": "sourceTime",
        "sZones": "sourceTime",
        "eZones": "sourceTime",
        "stopAlls": "sourceTime",
        "orderAudit": "firstTime",
    }
    for collection, time_field in fields.items():
        early_common = [
            item for item in early[collection]
            if late_from <= item[time_field] <= common_to
        ]
        assert early_common == late[collection], collection
