"""Cross-stage price/role reflection against the maintained bullish rules.

Family colors are behavioral labels and stay fixed. Market dojis stay GREEN;
the reflected reference swaps their internal role, not their chart color.
"""

from dataclasses import asdict, is_dataclass, replace
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from decimal import Decimal
import importlib.util
import io
import json
from pathlib import Path
import random
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / "indicator/Modules"


def load(name, relative):
    spec = importlib.util.spec_from_file_location("symmetry_" + name, MODULES / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


REACTION = load("reaction", "1_reaction-detector/app/Reaction-detection-new.py")
BLUE = load("blue", "2_blue-line/app/blue_line.py")
A = load("a", "3_A-zone/app/a_detector.py")
S = load("s", "4_S-zones/app/s_detector.py")
E = load("e", "5_E-zones/app/e_detector.py")
STOP = load("stop", "6_StopAll/app/stopall_detector.py")


def reflect_candles(candles):
    # Independent oracle: do not call the engine's mirror helpers.
    return [replace(c, open=c.open.copy_negate(), high=c.low.copy_negate(),
                    low=c.high.copy_negate(), close=c.close.copy_negate(),
                    tag={"GREEN": "RED", "RED": "GREEN"}[c.tag]) for c in candles]


def reflected(value):
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            target = key
            for top, bottom in (("box_top", "box_bottom"), ("high", "low")):
                if top in key:
                    target = key.replace(top, bottom)
                    break
                if bottom in key:
                    target = key.replace(bottom, top)
                    break
            result[target] = reflected(item)
        return result
    if isinstance(value, (tuple, list)):
        return type(value)(reflected(item) for item in value)
    if isinstance(value, Decimal):
        return value.copy_negate()
    if isinstance(value, str):
        return {"bullish": "bearish", "bearish": "bullish"}.get(value, value)
    return value


def plain(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return type(value)(plain(item) for item in value)
    return value


def sample(seed, size=360, timeframe=5):
    rng = random.Random(seed)
    start = datetime(2026, 1, 1)
    seconds = []
    price = Decimal(1000)
    for index in range(size * timeframe):
        close = price + Decimal(rng.randint(-9, 9))
        high = max(price, close) + rng.randint(0, 4)
        low = min(price, close) - rng.randint(0, 4)
        stamp = start + timedelta(seconds=index)
        seconds.append(REACTION.Candle(index, stamp, str(stamp),
                       "GREEN" if price <= close else "RED", price, high, low, close))
        price = close
    candles = []
    for index in range(size):
        rows = seconds[index * timeframe:(index + 1) * timeframe]
        first, last = rows[0], rows[-1]
        candles.append(replace(first, index=index, high=max(c.high for c in rows),
                               low=min(c.low for c in rows), close=last.close,
                               tag="GREEN" if first.open <= last.close else "RED"))
    return candles, seconds


def pipeline(candles, seconds, direction, timeframe=5):
    detectors = {d: REACTION.UnifiedReactionDetector(candles, seconds, 0,
                  len(candles) - 1, d) for d in ("bullish", "bearish")}
    results = {d: detector.detect() for d, detector in detectors.items()}
    opposite = "bearish" if direction == "bullish" else "bullish"
    trend, order = results[direction], results[opposite]
    lines = BLUE.detect_blue_lines(direction, trend.reactions, candles, seconds,
                                  timeframe, trend.resets)
    zones_a = A.detect_a_zones(direction, trend.reactions, lines, candles, seconds, timeframe)
    detector_s = S.SDetector(direction, trend.reactions, order.reactions, lines, zones_a,
                            candles, seconds, timeframe, opposite_resets=order.resets)
    zones_s = detector_s.detect()
    detector_e = E.EDetector(
        direction, trend.reactions, order.reactions, zones_s, trend.resets, order.resets,
        candles, seconds, timeframe,
        geometry_finder=lambda d, start, end: detectors[d]._first_geometry_after_reset(
            d, max(0, start - 1), end),
        direct_geometry_finder=lambda d, start, end, event: detectors[d].first_order_reaction_after_gate(
            d, start, end, event),
        reset_geometry_finder=lambda d, reset, gate, end: detectors[d].first_simple_geometry_after_gate(
            d, reset, gate, end),
        initial_order_audit=detector_s.order_audit,
    )
    zones_e = detector_e.detect()
    stops = STOP.detect_stopalls(direction, zones_s, zones_e, candles, seconds, timeframe)
    return {"reaction": trend, "orders": order, "blue": lines, "a": zones_a,
            "s": zones_s, "e": zones_e, "stopall": stops,
            "s_audit": detector_s.order_audit, "e_audit": detector_e.order_audit}


@pytest.mark.parametrize("timeframe", (1, 5, 30))
@pytest.mark.parametrize("seed", range(40))
def test_all_stages_reflect_bullish_rules(seed, timeframe):
    candles, seconds = sample(seed, timeframe=timeframe)
    actual = pipeline(candles, seconds, "bearish", timeframe)
    reference = pipeline(reflect_candles(candles), reflect_candles(seconds), "bullish", timeframe)
    for stage in actual:
        assert plain(actual[stage]) == reflected(reference[stage]), (seed, stage)


def test_type3_keeps_blue_family_in_both_directions():
    candles, seconds = sample(17)
    for direction, main, lower in (
        ("bearish", candles, seconds),
        ("bullish", reflect_candles(candles), reflect_candles(seconds)),
    ):
        zones = pipeline(main, lower, direction)["s"]
        type3 = [zone for zone in zones if zone.formation_type == "type3"]
        assert len(type3) == 1
        assert (type3[0].source_index, type3[0].color) == (278, "blue")
        assert type3[0].order_direction is None


def test_bearish_type3_does_not_promote_its_e_chain_to_red():
    candles, seconds = sample(1, timeframe=1)
    result = pipeline(candles, seconds, "bearish", 1)
    parent = next(zone for zone in result["s"] if zone.source_index == 81)
    assert (parent.formation_type, parent.color) == ("type3", "blue")
    child = next(zone for zone in result["e"] if zone.source_index == 104)
    assert (child.parent_type, child.parent_source_index, child.family) == ("S", 81, "blue")


def run_bridge(data, timeframe, direction, *, mirror=False, s_path=None):
    bridge = load("bridge", "../indicator-settings/backend/reaction_bridge.py")
    if mirror:
        build = bridge.build_candle_objects
        bridge.build_candle_objects = lambda engine, rows: reflect_candles(build(engine, rows))
    rows = json.loads(data.read_text(encoding="utf-8"))
    arguments = ["reaction_bridge.py", "--data", str(data), "--timeframe", str(timeframe),
                 "--from-time", str(int(rows[0]["time"]) // timeframe * timeframe),
                 "--to-time", str(int(rows[-1]["time"]) // timeframe * timeframe),
                 "--direction", direction]
    for flag, relative in (
        ("engine", "1_reaction-detector/app/Reaction-detection-new.py"),
        ("blue-engine", "2_blue-line/app/blue_line.py"),
        ("a-engine", "3_A-zone/app/a_detector.py"),
        ("s-engine", "4_S-zones/app/s_detector.py"),
        ("e-engine", "5_E-zones/app/e_detector.py"),
        ("stopall-engine", "6_StopAll/app/stopall_detector.py"),
    ):
        arguments.extend(["--" + flag, str(s_path if flag == "s-engine" and s_path else MODULES / relative)])
    previous = sys.argv
    output = io.StringIO()
    try:
        sys.argv = arguments
        with redirect_stdout(output):
            assert bridge.main() == 0
    finally:
        sys.argv = previous
    return json.loads(output.getvalue())["directions"]


def reflect_payload(value, key=""):
    if isinstance(value, list):
        return [reflect_payload(item) for item in value]
    if isinstance(value, dict):
        result = {}
        for field, item in value.items():
            target = field.replace("Top", "Bottom") if "Top" in field else field.replace("Bottom", "Top")
            result[target] = reflect_payload(item, field)
        return result
    if value is not None and (key.endswith(("Price", "Level", "Extreme", "BoxTop", "BoxBottom"))
                              or key in ("price", "boxTop", "boxBottom")):
        return str(Decimal(value).copy_negate())
    if isinstance(value, str):
        return {"bullish": "bearish", "bearish": "bullish"}.get(value, value)
    return value


@pytest.mark.parametrize("seed", range(40))
def test_complete_bridge_reflection_and_both_mode(seed, tmp_path):
    _, seconds = sample(seed)
    data = tmp_path / "candles.json"
    data.write_text(json.dumps([dict(time=1767225600 + c.index, open=str(c.open),
                                   high=str(c.high), low=str(c.low), close=str(c.close))
                               for c in seconds]), encoding="utf-8")
    actual = run_bridge(data, 5, "both")
    reference = run_bridge(data, 5, "bullish", mirror=True)
    assert actual["bearish"] == reflect_payload(reference["bullish"])
    assert actual["bullish"] == run_bridge(data, 5, "bullish")["bullish"]


@pytest.mark.parametrize("filename", (
    "RAW FOREXCOM_XAUUSD 1S FROM 2026-09-04 04-52-39 TO 2026-09-04 07-37-46.json",
    "RAW FXCM_USOIL 1S FROM 2026-09-03 13-46-40 TO 2026-09-05 00-14-59.json",
))
def test_real_history_reflection(filename, tmp_path):
    source = ROOT / "market-data/raw" / filename
    if not source.is_file():
        pytest.skip("Optional local market history is unavailable")
    rows = json.loads(source.read_text(encoding="utf-8-sig"))[:7200]
    data = tmp_path / "history.json"
    data.write_text(json.dumps(rows), encoding="utf-8")
    actual = run_bridge(data, 30, "bearish")["bearish"]
    reference = run_bridge(data, 30, "bullish", mirror=True)["bullish"]
    assert actual == reflect_payload(reference)
