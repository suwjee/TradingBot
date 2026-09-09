"""XAUUSD acceptance for optional S-only bridge and exact directional reflection."""

from contextlib import redirect_stdout
import io
import json
import sys

import pytest

from test_directional_symmetry import ROOT, MODULES, load, reflect_candles, reflect_payload


SOURCE = ROOT / "market-data/raw/RAW_FOREXCOM_XAUUSD_1S_FROM_2026_08_18_04_44_40_TO_2026_09_05_00.json"


def run_without_e(direction, mirror=False):
    bridge = load("xau_optional_e", "../indicator-settings/backend/reaction_bridge.py")
    if mirror:
        original = bridge.build_candle_objects
        bridge.build_candle_objects = lambda engine, rows: reflect_candles(original(engine, rows))
    arguments = ["reaction_bridge.py", "--data", str(SOURCE), "--timeframe", "30",
                 "--from-time", "1787015680", "--to-time", "1787106240",
                 "--direction", direction]
    for flag, relative in (
        ("engine", "1_reaction-detector/app/Reaction-detection-new.py"),
        ("blue-engine", "2_blue-line/app/blue_line.py"),
        ("a-engine", "3_A-zone/app/a_detector.py"),
        ("s-engine", "4_S-zones/app/s_detector.py"),
    ):
        arguments.extend(["--" + flag, str(MODULES / relative)])
    previous = sys.argv
    output = io.StringIO()
    try:
        sys.argv = arguments
        with redirect_stdout(output):
            assert bridge.main() == 0
    finally:
        sys.argv = previous
    return json.loads(output.getvalue())


@pytest.mark.skipif(not SOURCE.is_file(), reason="Exact user XAUUSD source unavailable")
def test_xau_s_without_e_returns_complete_mirrored_payload():
    bullish = run_without_e("bullish")
    bearish = run_without_e("bearish")
    oracle = run_without_e("bullish", mirror=True)
    assert bullish["directions"]["bullish"]["sZones"]
    assert bearish["directions"]["bearish"]["sZones"]
    assert not bearish["eEnabled"]
    assert bearish["directions"]["bearish"] == reflect_payload(oracle["directions"]["bullish"])
