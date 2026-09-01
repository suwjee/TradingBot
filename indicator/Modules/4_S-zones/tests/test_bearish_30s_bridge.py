"""User-approved A/S acceptance through the complete maintained bridge."""

from datetime import datetime
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

import pytest


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "market-data/raw/candle-history FXCM_USOIL 1S from 2026-08-25 09-34-17 to 2026-08-31 02-56-49 .json"
XAU_SOURCE = ROOT / "market-data/raw/candle-history FOREXCOM_XAUUSD 1S from 2026-08-18 04-05-01 to 2026-09-01 00-29-31 .json"


def epoch(value):
    return int(datetime.fromisoformat(value).replace(tzinfo=ZoneInfo("Asia/Tehran")).timestamp())


@pytest.mark.skipif(not SOURCE.is_file(), reason="The selected user-supplied one-second history is unavailable")
def test_confirmed_bearish_a_to_s_ownership(monkeypatch):
    path = ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"
    spec = importlib.util.spec_from_file_location("s_acceptance_bridge", path)
    bridge = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = bridge
    spec.loader.exec_module(bridge)
    arguments = [str(path)]
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
        "--data", str(SOURCE), "--timeframe", "30", "--direction", "bearish",
        "--from-time", str(epoch("2026-08-25 18:00:00")),
        "--to-time", str(epoch("2026-08-26 19:55:30")),
    ])
    monkeypatch.setattr(sys, "argv", arguments)
    output = io.StringIO()
    with redirect_stdout(output):
        assert bridge.main() == 0
    payload = json.loads(output.getvalue())
    assert payload["timeframe"] == 30
    assert payload["actualFrom"] == epoch("2026-08-25 18:00:00")
    assert payload["actualTo"] == epoch("2026-08-26 19:55:30")
    result = payload["directions"]["bearish"]
    a_sources = {x["sourceTime"] for x in result["aZones"]}
    for source in ["2026-08-25 19:52:00", "2026-08-26 03:02:30", "2026-08-26 03:16:30"]:
        assert epoch(source) not in a_sources
    assert epoch("2026-08-25 19:31:00") in a_sources
    assert epoch("2026-08-26 02:42:00") in a_sources
    s_by_source = {x["sourceTime"]: x for x in result["sZones"]}
    target = s_by_source[epoch("2026-08-25 19:52:00")]
    assert target["color"] == "red"
    assert target["price"] == "82.299"
    assert target["aSourceTime"] == epoch("2026-08-25 19:31:00")
    assert target["orderFirstTime"] == epoch("2026-08-25 19:51:00")
    assert target["decisionEventTime"] == epoch("2026-08-25 19:53:37")
    assert epoch("2026-08-25 19:52:30") not in s_by_source
    assert a_sources.isdisjoint(s_by_source)
    rejected = {epoch("2026-08-26 03:02:30"), epoch("2026-08-26 03:16:30")}
    assert not any(
        cause.get("parentType") == "A" and cause.get("parentSourceTime") in rejected
        for order in result["orderAudit"] for cause in order["causes"]
    )


@pytest.mark.skipif(not XAU_SOURCE.is_file(), reason="The selected XAUUSD history is unavailable")
def test_xau_bullish_visual_blue_a_type3_and_red_s(monkeypatch):
    path = ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"
    spec = importlib.util.spec_from_file_location("xau_s_acceptance_bridge", path)
    bridge = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = bridge
    spec.loader.exec_module(bridge)
    arguments = [str(path)]
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
        "--data", str(XAU_SOURCE), "--timeframe", "30", "--direction", "both",
        "--from-time", str(epoch("2026-08-18 09:00:00")),
        "--to-time", str(epoch("2026-08-18 14:20:00")),
    ])
    monkeypatch.setattr(sys, "argv", arguments)
    output = io.StringIO()
    with redirect_stdout(output):
        assert bridge.main() == 0
    payload = json.loads(output.getvalue())
    bullish = payload["directions"]["bullish"]

    blue_by_source = {item["sourceTime"]: item for item in bullish["blueLines"]}
    prior = blue_by_source[epoch("2026-08-18 13:23:00")]
    visual = blue_by_source[epoch("2026-08-18 13:26:30")]
    assert prior["sourceExtreme"] == "4393.23"
    assert prior["calculationValid"] is True
    assert visual["calculationValid"] is False

    a_by_source = {item["sourceTime"]: item for item in bullish["aZones"]}
    special_a = a_by_source[epoch("2026-08-18 13:26:30")]
    assert special_a["price"] == "4392.97"
    assert special_a["reactionFirstTime"] == epoch("2026-08-18 13:27:00")
    assert epoch("2026-08-18 13:30:00") not in a_by_source

    s_by_source = {item["sourceTime"]: item for item in bullish["sZones"]}
    type3 = s_by_source[epoch("2026-08-18 12:37:00")]
    assert type3["formationType"] == "type3"
    assert type3["color"] == "blue"
    assert type3["price"] == "4391.2"
    assert type3["decisionTime"] == epoch("2026-08-18 12:46:00")
    assert type3["orderFirstTime"] is None

    red = s_by_source[epoch("2026-08-18 13:30:00")]
    assert red["color"] == "red"
    assert red["orderFirstTime"] == epoch("2026-08-18 13:35:00")
