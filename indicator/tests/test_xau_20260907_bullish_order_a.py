"""Regression for verified bullish 30-second XAUUSD lifecycles."""

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


ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / "indicator/Modules"
SOURCE = ROOT / (
    "market-data/raw/"
    "RAW FOREXCOM_XAUUSD 1S FROM 2026-09-04 16-48-10 "
    "TO 2026-09-08 02-49-33.json"
)
TEHRAN = ZoneInfo("Asia/Tehran")


def epoch(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=TEHRAN).timestamp())


def run_bridge() -> dict:
    bridge_path = ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"
    spec = importlib.util.spec_from_file_location(
        "xau_20260907_bullish_order_a_bridge", bridge_path
    )
    assert spec is not None and spec.loader is not None
    bridge = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = bridge
    spec.loader.exec_module(bridge)
    arguments = [
        str(bridge_path),
        "--data", str(SOURCE),
        "--timeframe", "30",
        "--direction", "bullish",
        "--from-time", str(epoch("2026-09-04 16:48:00")),
        "--to-time", str(epoch("2026-09-08 02:49:30")),
        "--blue-lines", "enabled",
        "--a-zones", "enabled",
        "--s-zones", "enabled",
    ]
    for flag, relative in (
        ("engine", "1_reaction-detector/app/Reaction-detection-new.py"),
        ("blue-engine", "2_Blue-line/app/blue_line.py"),
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


def parent_stop_cause(order: dict, parent_type: str, source_time: str) -> bool:
    return any(
        cause["kind"] == "parent-stop"
        and cause["parentType"] == parent_type
        and cause["parentSourceTime"] == epoch(source_time)
        for cause in order["causes"]
    )


@pytest.mark.skipif(not SOURCE.is_file(), reason="Exact user XAUUSD source unavailable")
def test_verified_a_order_s_order_and_special_a_chronology():
    group = run_bridge()

    order_from_old_a = next(
        order for order in group["orderAudit"]
        if order["firstTime"] == epoch("2026-09-07 03:06:30")
    )
    assert parent_stop_cause(
        order_from_old_a, "A", "2026-09-07 01:56:00"
    )
    assert order_from_old_a["reactionMode"] == "A"
    assert order_from_old_a["stopSourceTime"] == epoch("2026-09-07 03:06:00")
    assert order_from_old_a["stopLevel"] == "4430.545"
    assert order_from_old_a["stopHitEventTime"] == epoch("2026-09-07 03:15:03")

    assert all(
        order["firstTime"] != epoch("2026-09-07 03:14:30")
        for order in group["orderAudit"]
    )
    order_from_s = next(
        order for order in group["orderAudit"]
        if order["firstTime"] == epoch("2026-09-07 03:17:00")
    )
    assert parent_stop_cause(order_from_s, "S", "2026-09-07 02:55:00")

    e1 = next(
        zone for zone in group["eZones"]
        if zone["sourceTime"] == epoch("2026-09-07 03:11:00")
        and zone["family"] == "red"
        and zone["number"] == 1
    )
    assert e1["orderFirstTime"] == epoch("2026-09-07 03:06:30")
    assert e1["orderStopSourceTime"] == epoch("2026-09-07 03:06:00")
    assert e1["orderStopLevel"] == "4430.545"
    assert e1["decisionEventTime"] == epoch("2026-09-07 03:15:03")

    special_a = next(
        zone for zone in group["aZones"]
        if zone["sourceTime"] == epoch("2026-09-07 15:15:00")
    )
    assert special_a["blue1SourceTime"] == epoch("2026-09-07 15:11:00")
    assert special_a["blue2SourceTime"] == epoch("2026-09-07 15:14:30")
    assert special_a["triggerEventTime"] == epoch("2026-09-07 15:14:37")
    assert special_a["reactionFirstTime"] == epoch("2026-09-07 15:17:00")
    assert special_a["reactionBreakTime"] == epoch("2026-09-07 15:18:00")
    assert special_a["price"] == "4386.075"
    assert all(
        zone["sourceTime"] != epoch("2026-09-07 15:28:30")
        for zone in group["aZones"]
    )


@pytest.mark.skipif(not SOURCE.is_file(), reason="Exact user XAUUSD source unavailable")
def test_every_stopped_a_keeps_its_order_a_parent_stop_cause():
    """A-stop Order_A provenance is additive and is never overwritten."""
    group = run_bridge()
    a_causes = [
        cause
        for order in group["orderAudit"]
        for cause in order["causes"]
        if cause.get("kind") == "parent-stop"
        and cause.get("parentType") == "A"
    ]
    assert any(
        cause["parentSourceTime"] == epoch("2026-09-07 01:56:00")
        for cause in a_causes
    )
    assert any(
        sum(
            1
            for cause in order["causes"]
            if cause.get("kind") == "parent-stop"
            and cause.get("parentType") == "A"
        ) > 1
        for order in group["orderAudit"]
    )
    for order in group["orderAudit"]:
        sources = [
            cause["parentSourceTime"]
            for cause in order["causes"]
            if cause.get("kind") == "parent-stop"
            and cause.get("parentType") == "A"
        ]
        assert len(sources) == len(set(sources))


@pytest.mark.skipif(not SOURCE.is_file(), reason="Exact user XAUUSD source unavailable")
def test_rejected_a_cannot_create_public_order_audit():
    group = run_bridge()

    rejected_a = epoch("2026-09-07 12:28:00")
    rejected_order = epoch("2026-09-07 12:49:30")
    assert all(zone["sourceTime"] != rejected_a for zone in group["aZones"])
    assert all(
        order["firstTime"] != rejected_order
        for order in group["orderAudit"]
    )

    # The two already verified independent orders remain intact.
    assert any(
        order["firstTime"] == epoch("2026-09-07 03:06:30")
        for order in group["orderAudit"]
    )
    assert any(
        order["firstTime"] == epoch("2026-09-07 03:17:00")
        for order in group["orderAudit"]
    )
