"""Integrated Reaction -> Blue -> A -> S -> E smoke test for the supplied USOIL history."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "market-data" / "raw" / "candle-history FXCM_USOIL 5S from 2026-07-10 20-42-10 to 2026-07-23 21-36-55 .json"
BRIDGE = ROOT / "indicator" / "indicator-settings" / "backend" / "reaction_bridge.py"
MODULES = ROOT / "indicator" / "Modules"
ENGINE = MODULES / "1_reaction-detector" / "app" / "Reaction-detection-new.py"
BLUE = MODULES / "2_blue-line" / "app" / "blue_line.py"
A = MODULES / "3_A-zone" / "app" / "a_detector.py"
S = MODULES / "4_S-zones" / "app" / "s_detector.py"
E = MODULES / "5_E-zones" / "app" / "e_detector.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    bridge = load("e_integrated_bridge", BRIDGE)
    engine = load("e_integrated_engine", ENGINE)
    blue = load("e_integrated_blue", BLUE)
    a_engine = load("e_integrated_a", A)
    s_engine = load("e_integrated_s", S)
    e_engine = load("e_integrated_e", E)
    rows = json.loads(DATA.read_text(encoding="utf-8-sig"))
    seconds = bridge.build_candles(engine, rows, 1)
    candles = bridge.build_candles(engine, rows, 30)
    from datetime import datetime
    start = datetime(2026, 7, 14, 4, 49, 30)
    end = datetime(2026, 7, 15, 7, 15)
    eligible = [i for i, candle in enumerate(candles) if start <= candle.timestamp <= end]
    start_index, end_index = eligible[0], eligible[-1]
    for direction in ("bullish", "bearish"):
        result = engine.UnifiedReactionDetector(
            candles, seconds, start_index, end_index, direction
        ).detect()
        opposite = "bearish" if direction == "bullish" else "bullish"
        opposite_result = engine.UnifiedReactionDetector(
            candles, seconds, start_index, end_index, opposite
        ).detect()
        lines = blue.detect_blue_lines(
            direction, result.reactions, candles, seconds, 30, result.resets
        )
        zones_a = a_engine.detect_a_zones(
            direction, result.reactions, lines, candles, seconds, 5
        )
        zones_s = s_engine.detect_s_zones(
            direction,
            result.reactions,
            opposite_result.reactions,
            lines,
            zones_a,
            candles,
            seconds,
            30,
            start_index,
            end_index,
        )
        zones_e = e_engine.detect_e_zones(
            direction,
            result.reactions,
            opposite_result.reactions,
            zones_s,
            result.resets,
            opposite_result.resets,
            candles,
            seconds,
            30,
            start_index,
            end_index,
        )
        assert isinstance(zones_e, list)
        print(
            f"{direction}: {len(result.reactions)} reactions, "
            f"{len(lines)} blue lines, {len(zones_a)} A, "
            f"{len(zones_s)} S, {len(zones_e)} E"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
