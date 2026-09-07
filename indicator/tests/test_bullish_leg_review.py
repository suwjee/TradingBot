"""Acceptance requirements from the user's evolving bullish leg lesson.

Historical timestamps are test inputs only. Production engines must never read
this file or the review CSV to decide which behaviors to produce. Failing
requirements describe outstanding work; they are not expected-failure tests.
"""

from __future__ import annotations

import csv
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

import pytest


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "docs/algorithms/examples/2026-09-06-bullish-leg-user-review.csv"
SOURCE = ROOT / "market-data/raw" / (
    "RAW FOREXCOM_XAUUSD 1S FROM 2026-08-18 04-44-40 TO 2026-09-05 00-29-39.json"
)
TEHRAN = ZoneInfo("Asia/Tehran")
with REVIEW.open(encoding="utf-8", newline="") as review_file:
    EXPECTATIONS = list(csv.DictReader(review_file))


def epoch(local_time: str) -> int:
    return int(datetime.fromisoformat(local_time).replace(tzinfo=TEHRAN).timestamp())


@pytest.fixture(scope="module")
def bullish():
    if not SOURCE.is_file():
        pytest.skip("The user-selected XAUUSD source file is unavailable.")
    command = [
        sys.executable,
        str(ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"),
    ]
    for flag, relative in (
        ("engine", "1_reaction-detector/app/Reaction-detection-new.py"),
        ("blue-engine", "2_blue-line/app/blue_line.py"),
        ("a-engine", "3_A-zone/app/a_detector.py"),
        ("s-engine", "4_S-zones/app/s_detector.py"),
        ("e-engine", "5_E-zones/app/e_detector.py"),
        ("stopall-engine", "6_StopAll/app/stopall_detector.py"),
    ):
        command.extend(["--" + flag, str(ROOT / "indicator/Modules" / relative)])
    command.extend([
        "--data", str(SOURCE), "--timeframe", "30", "--direction", "bullish",
        "--from-time", str(epoch("2026-08-18 04:44:40")),
        "--to-time", str(epoch("2026-08-19 05:54:00")),
    ])
    completed = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["timeframe"] == 30
    assert payload["actualTo"] == epoch("2026-08-19 05:54:00")
    return payload["directions"]["bullish"]


def matching_rows(bullish, local_time: str, behavior: str):
    target = epoch(local_time)
    if behavior == "A":
        return [row for row in bullish["aZones"] if row["sourceTime"] == target]
    if behavior == "Order audit":
        return [row for row in bullish["orderAudit"] if row["firstTime"] == target]
    name, color = behavior.split()
    if name == "S":
        return [row for row in bullish["sZones"]
                if row["sourceTime"] == target and row["color"] == color]
    assert name.startswith("E"), f"Unsupported review behavior: {behavior}"
    return [row for row in bullish["eZones"]
            if row["sourceTime"] == target and row["family"] == color
            and row["number"] == int(name[1:])]


@pytest.mark.parametrize(
    "expected", EXPECTATIONS,
    ids=[f"{index + 1}-{row['local_datetime']}-{row['behavior']}"
         for index, row in enumerate(EXPECTATIONS)],
)
def test_user_review_presence_and_validity(bullish, expected):
    """Requested behaviors are valid; rejected candidates never reach output."""
    assert expected["direction"] == "bullish"
    verdict = expected["user_verdict"]
    assert verdict in {"True", "False", "not_computed"}
    rows = matching_rows(bullish, expected["local_datetime"], expected["behavior"])
    valid = [row for row in rows if row.get("calculationValid", True)]
    assert (bool(valid) if verdict != "False" else not rows), (
        f"{expected['local_datetime']} Asia/Tehran | {expected['behavior']} | "
        f"expected={verdict}; returned={rows}"
    )


def test_first_blue_e_uses_the_provisionally_accepted_order_b(bullish):
    """Order_B is a formation cause, not merely Reaction mode B."""
    rows = matching_rows(bullish, "2026-08-18 06:13:30", "E1 blue")
    assert len(rows) == 1
    assert rows[0]["orderFirstTime"] == epoch("2026-08-18 06:05:30")
    assert "reset-leg" in rows[0]["orderCauses"]


def test_blue_e_0230_uses_confirmed_s_parent_and_a_carried_order(bullish):
    rows = matching_rows(bullish, "2026-08-19 02:30:00", "E1 blue")
    assert len(rows) == 1
    zone = rows[0]
    assert zone["parentType"] == "S"
    assert zone["parentSourceTime"] == epoch("2026-08-19 02:10:30")
    assert zone["orderFirstTime"] == epoch("2026-08-19 02:07:30")
    assert zone["orderStopSourceTime"] == epoch("2026-08-19 02:05:30")
    assert zone["orderStopLevel"] == "4336.57"
    assert "carried-live" in zone["orderCauses"]


def test_a_stop_order_020730_has_its_own_confirmed_stop_source(bullish):
    rows = matching_rows(bullish, "2026-08-19 02:07:30", "Order audit")
    assert len(rows) == 1
    assert rows[0]["stopSourceTime"] == epoch("2026-08-19 02:05:30")
    assert rows[0]["stopLevel"] == "4336.57"
    assert any(
        cause.get("kind") == "parent-stop"
        and cause.get("parentType") == "A"
        and cause.get("parentSourceTime") == epoch("2026-08-19 01:52:30")
        for cause in rows[0]["causes"]
    )


def test_red_e4_does_not_depend_on_the_rejected_red_e1(bullish):
    rows = matching_rows(bullish, "2026-08-18 18:54:00", "E4 red")
    assert len(rows) == 1
    assert not (
        rows[0]["parentType"].startswith("E")
        and rows[0]["parentSourceTime"] == epoch("2026-08-18 18:02:00")
    ), "A correct E4 label cannot inherit the user-rejected E1 at 18:02:00."
