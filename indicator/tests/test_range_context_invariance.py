"""A selected calculation range behaves as an independent virtual file."""

from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime
import importlib.util
import io
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

import orjson


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "market-data/raw/RAW_FOREXCOM_XAUUSD_1S_FROM_2026_08_18_04_44_40_TO_2026_09_05_00.json"
TEHRAN = ZoneInfo("Asia/Tehran")
MODULES = ROOT / "indicator/Modules"


def epoch(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=TEHRAN).timestamp())


def run_bridge(from_time: int, to_time: int, source: Path = SOURCE) -> dict:
    bridge_path = ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"
    name = f"range_context_bridge_{from_time}_{to_time}"
    spec = importlib.util.spec_from_file_location(name, bridge_path)
    assert spec is not None and spec.loader is not None
    bridge = importlib.util.module_from_spec(spec)
    sys.modules[name] = bridge
    spec.loader.exec_module(bridge)
    arguments = [
        str(bridge_path),
        "--data", str(source),
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


def test_selected_range_matches_a_physical_file_with_only_that_range(tmp_path):
    from_time = epoch("2026-08-20 00:00:00")
    to_time = epoch("2026-08-20 06:00:00")
    end_exclusive = to_time + 30
    source_rows = orjson.loads(SOURCE.read_bytes())
    isolated_rows = [
        row for row in source_rows
        if from_time <= int(row["time"]) < end_exclusive
    ]
    isolated_source = tmp_path / "isolated-range.json"
    isolated_source.write_bytes(orjson.dumps(isolated_rows))

    selected = run_bridge(from_time, to_time)
    physical = run_bridge(from_time, to_time, isolated_source)
    assert selected == physical

    time_fields = {
        "reactions": "firstTime",
        "resets": "time",
        "blueLines": "sourceTime",
        "aZones": "sourceTime",
        "sZones": "sourceTime",
        "eZones": "sourceTime",
        "stopAlls": "sourceTime",
        "orderAudit": "firstTime",
    }
    for collection, time_field in time_fields.items():
        assert all(
            from_time <= item[time_field] <= to_time
            for item in selected[collection]
        ), collection


def test_repeated_selected_range_is_deterministic():
    from_time = epoch("2026-08-20 00:00:00")
    to_time = epoch("2026-08-20 06:00:00")
    assert run_bridge(from_time, to_time) == run_bridge(from_time, to_time)
