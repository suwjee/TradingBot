from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[4]
DETECTOR_ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = Path(__file__).with_name("Reaction-detection-new.py")
MODULES_ROOT = ROOT / "indicator" / "Modules"
BLUE_ENGINE_PATH = MODULES_ROOT / "2_blue-line" / "app" / "blue_line.py"
A_ENGINE_PATH = MODULES_ROOT / "3_A-zone" / "app" / "a_detector.py"
S_ENGINE_PATH = MODULES_ROOT / "4_S-zones" / "app" / "s_detector.py"
BRIDGE_PATH = ROOT / "indicator" / "indicator-settings" / "backend" / "reaction_bridge.py"
RESULTS_DIR = ROOT / "Results" / "test-runs" / "reaction-detector"


@dataclass(frozen=True)
class Case:
    filename: str
    direction: str
    start: str
    end: str


@dataclass(frozen=True)
class ACase:
    filename: str
    source_pattern: str
    start: str
    end: str
    expected: tuple[tuple[str, str, str], ...]
    expected_blue_sources: tuple[str, ...]


@dataclass(frozen=True)
class SCase:
    filename: str
    start: str
    end: str
    expected: tuple[tuple[str, str, str, str, str], ...]
    expected_visible_a_sources: tuple[str, ...] = ()
    required_visible_a_sources: tuple[str, ...] = ()
    forbidden_visible_a_sources: tuple[str, ...] = ()


CASES = (
    Case(
        "01_bullish_2026-07-28_01-55-30_to_03-30-00.json",
        "bullish",
        "2026-07-28 01:55:30",
        "2026-07-28 03:30:00",
    ),
    Case(
        "02_bearish_2026-07-28_03-29-30_to_09-12-00.json",
        "bearish",
        "2026-07-28 03:29:30",
        "2026-07-28 09:12:00",
    ),
    Case(
        "03_bullish_2026-07-28_09-02-30_to_12-03-00.json",
        "bullish",
        "2026-07-28 09:02:30",
        "2026-07-28 12:03:00",
    ),
    Case(
        "04_bearish_2026-07-28_11-35-30_to_18-11-30.json",
        "bearish",
        "2026-07-28 11:35:30",
        "2026-07-28 18:11:30",
    ),
    Case(
        "05_bullish_2026-07-28_17-49-00_to_19-56-00.json",
        "bullish",
        "2026-07-28 17:49:00",
        "2026-07-28 19:56:00",
    ),
    Case(
        "06_bearish_2026-07-28_19-24-00_to_2026-07-29_05-00-00.json",
        "bearish",
        "2026-07-28 19:24:00",
        "2026-07-29 05:00:00",
    ),
)


A_CASES = (
    ACase(
        "07_a_bullish_2026-06-30_05-39-30_to_05-56-00.json",
        "candle-history FOREXCOM_XAUUSD 5S from 2026-06-30*.json",
        "2026-06-30 05:39:30",
        "2026-06-30 05:56:00",
        (("2026-06-30 05:52:00", "3956.04", "2026-06-30 05:54:00"),),
        ("2026-06-30 05:45:30", "2026-06-30 05:50:30"),
    ),
    ACase(
        "08_a_bullish_2026-06-30_07-03-30_to_09-00-30.json",
        "candle-history FOREXCOM_XAUUSD 5S from 2026-06-30*.json",
        "2026-06-30 07:03:30",
        "2026-06-30 09:00:30",
        (("2026-06-30 08:57:00", "3979.69", "2026-06-30 08:59:00"),),
        (
            "2026-06-30 07:13:00",
            "2026-06-30 07:21:30",
            "2026-06-30 07:29:00",
            "2026-06-30 07:46:30",
            "2026-06-30 07:50:30",
            "2026-06-30 08:05:00",
            "2026-06-30 08:55:30",
        ),
    ),
    ACase(
        "09_a_bullish_2026-06-30_10-42-00_to_11-41-00.json",
        "candle-history FOREXCOM_XAUUSD 5S from 2026-06-30*.json",
        "2026-06-30 10:42:00",
        "2026-06-30 11:41:00",
        (("2026-06-30 11:20:30", "4025.675", "2026-06-30 11:21:30"),),
        ("2026-06-30 10:48:30", "2026-06-30 10:59:30"),
    ),
    ACase(
        "10_a_bullish_2026-08-10_05-11-00_to_06-28-30.json",
        "candle-history FOREXCOM_XAUUSD 1S from 2026-08-10*.json",
        "2026-08-10 05:11:00",
        "2026-08-10 06:28:30",
        (
            ("2026-08-10 05:27:30", "4317.845", "2026-08-10 05:28:30"),
            ("2026-08-10 06:24:30", "4319.49", "2026-08-10 06:25:30"),
        ),
        (
            "2026-08-10 05:22:30",
            "2026-08-10 05:26:30",
            "2026-08-10 05:36:00",
            "2026-08-10 05:42:30",
            "2026-08-10 05:49:30",
            "2026-08-10 06:00:30",
        ),
    ),
    ACase(
        "11_a_bullish_2026-08-10_10-42-30_to_11-53-30.json",
        "candle-history FOREXCOM_XAUUSD 1S from 2026-08-10*.json",
        "2026-08-10 10:42:30",
        "2026-08-10 11:53:30",
        (
            ("2026-08-10 11:39:00", "4351.67", "2026-08-10 11:40:30"),
            ("2026-08-10 11:51:00", "4353.355", "2026-08-10 11:51:30"),
        ),
        (
            "2026-08-10 10:51:30",
            "2026-08-10 11:00:30",
            "2026-08-10 11:11:00",
            "2026-08-10 11:29:30",
            "2026-08-10 11:45:00",
            "2026-08-10 11:47:30",
        ),
    ),
    ACase(
        "12_a_bullish_2026-07-13_14-37-00_to_15-41-00.json",
        "candle-history FXCM_USOIL 5S from 2026-07-10*.json",
        "2026-07-13 14:37:00",
        "2026-07-13 15:41:00",
        (
            ("2026-07-13 15:16:00", "73.663", "2026-07-13 15:17:30"),
            ("2026-07-13 15:24:00", "73.763", "2026-07-13 15:26:00"),
        ),
        (
            "2026-07-13 14:44:00",
            "2026-07-13 15:05:00",
            "2026-07-13 15:19:30",
            "2026-07-13 15:24:00",
        ),
    ),
    ACase(
        "13_a_bullish_2026-07-13_17-45-00_to_18-20-00.json",
        "candle-history FXCM_USOIL 5S from 2026-07-10*.json",
        "2026-07-13 17:45:00",
        "2026-07-13 18:20:00",
        (("2026-07-13 18:08:30", "74.547", "2026-07-13 18:09:30"),),
        (
            "2026-07-13 17:54:00",
            "2026-07-13 18:02:00",
            "2026-07-13 18:08:30",
        ),
    ),
)


S_CASES = (
    SCase(
        "14_s_bullish_2026-07-10_20-42-00_to_21-30-30.json",
        "2026-07-10 20:42:00",
        "2026-07-10 21:30:30",
        ((
            "2026-07-10 21:00:30",
            "blue",
            "2026-07-10 20:53:00",
            "2026-07-10 21:09:00",
            "2026-07-10 21:08:00",
        ),),
    ),
    SCase(
        "15_s_bullish_2026-07-13_13-14-30_to_15-45-00.json",
        "2026-07-13 13:14:30",
        "2026-07-13 15:45:00",
        (
            (
                "2026-07-13 14:37:00",
                "red",
                "2026-07-13 14:19:00",
                "2026-07-13 14:41:30",
                "2026-07-13 14:41:00",
            ),
            (
                "2026-07-13 15:31:30",
                "blue",
                "2026-07-13 15:24:00",
                "2026-07-13 15:39:00",
                "2026-07-13 15:38:00",
            ),
        ),
    ),
    SCase(
        "16_s_bullish_2026-07-13_17-28-30_to_18-45-00.json",
        "2026-07-13 17:28:30",
        "2026-07-13 18:45:00",
        (
            (
                "2026-07-13 18:20:30",
                "red",
                "2026-07-13 18:08:30",
                "2026-07-13 18:12:00",
                "2026-07-13 18:10:30",
            ),
        ),
    ),
    SCase(
        "17_s_bullish_2026-07-13_23-38-00_to_2026-07-14_00-29-30.json",
        "2026-07-13 23:38:00",
        "2026-07-14 00:29:30",
        ((
            "2026-07-14 00:17:00",
            "blue",
            "2026-07-14 00:05:00",
            "2026-07-14 00:18:00",
            "2026-07-14 00:14:30",
        ),),
    ),
    SCase(
        "18_s_bullish_2026-07-14_07-54-30_to_09-00-00.json",
        "2026-07-14 07:54:30",
        "2026-07-14 09:00:00",
        ((
            "2026-07-14 08:47:00",
            "blue",
            "2026-07-14 08:30:00",
            "2026-07-14 08:56:30",
            "2026-07-14 08:55:00",
        ),),
    ),
    SCase(
        "19_s_bullish_2026-07-15_00-00-00_to_10-00-00.json",
        "2026-07-15 00:00:00",
        "2026-07-15 10:00:00",
        (
            (
                "2026-07-15 01:31:00",
                "red",
                "2026-07-15 00:25:00",
                "2026-07-15 01:38:30",
                "2026-07-15 01:37:30",
            ),
            (
                "2026-07-15 02:56:00",
                "blue",
                "2026-07-15 02:00:00",
                "2026-07-15 03:18:00",
                "2026-07-15 03:16:30",
            ),
            (
                "2026-07-15 06:39:30",
                "red",
                "2026-07-15 06:33:00",
                "2026-07-15 06:43:30",
                "2026-07-15 06:42:00",
            ),
            (
                "2026-07-15 07:20:30",
                "blue",
                "2026-07-15 07:00:30",
                "2026-07-15 07:33:00",
                "2026-07-15 07:32:00",
            ),
            (
                "2026-07-15 08:24:00",
                "blue",
                "2026-07-15 07:56:30",
                "2026-07-15 08:07:30",
                "2026-07-15 08:04:30",
            ),
            (
                "2026-07-15 09:07:30",
                "red",
                "2026-07-15 08:25:30",
                "2026-07-15 09:05:30",
                "2026-07-15 09:04:00",
            ),
            (
                "2026-07-15 09:54:00",
                "red",
                "2026-07-15 09:42:00",
                "2026-07-15 09:52:00",
                "2026-07-15 09:49:00",
            ),
        ),
        (),
        ("2026-07-15 09:42:00",),
        ("2026-07-15 09:24:30",),
    ),
    SCase(
        "20_s_bullish_2026-07-15_18-59-30_to_23-00-00.json",
        "2026-07-15 18:59:30",
        "2026-07-15 23:00:00",
        (
            (
                "2026-07-15 21:01:30",
                "red",
                "2026-07-15 20:16:30",
                "2026-07-15 21:08:30",
                "2026-07-15 21:05:30",
            ),
        ),
        (),
        ("2026-07-15 20:16:30", "2026-07-15 22:45:00"),
    ),
    SCase(
        "21_s_bullish_2026-07-13_21-35-30_to_23-00-00.json",
        "2026-07-13 21:35:30",
        "2026-07-13 23:00:00",
        (
            (
                "2026-07-13 22:13:00",
                "blue",
                "2026-07-13 21:44:00",
                "2026-07-13 22:13:00",
                "2026-07-13 22:10:00",
            ),
        ),
        (),
        ("2026-07-13 21:44:00",),
    ),
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def validate_result(
    engine, case: Case, result, candles, seconds, start_index, end_index
) -> None:
    assert result.direction == case.direction
    assert result.start_index == start_index
    assert result.end_index == end_index
    previous_break = start_index - 1
    reset_firsts = {item.from_first_idx for item in result.resets}

    for number, reaction in enumerate(result.reactions, start=1):
        assert start_index <= reaction.first_idx <= reaction.break_idx <= end_index
        assert reaction.break_idx >= previous_break
        assert reaction.box_bottom < reaction.box_top
        assert reaction.mode in {"A", "B"}
        if number == 1:
            assert reaction.mode == "A"
        break_candle = candles[reaction.break_idx]
        if case.direction == "bullish":
            assert break_candle.high > reaction.box_top
        else:
            assert break_candle.low < reaction.box_bottom
        previous_break = reaction.break_idx

    reaction_by_first = {
        reaction.first_idx: reaction for reaction in result.reactions
    }
    for reset in result.resets:
        assert reset.from_first_idx in reaction_by_first
        assert start_index <= reset.index <= end_index
        candle = candles[reset.index]
        if case.direction == "bullish":
            assert candle.low < reset.broken_level
        else:
            assert candle.high > reset.broken_level

    for index, reaction in enumerate(result.reactions[:-1]):
        if reaction.first_idx not in reset_firsts:
            continue
        next_reaction = result.reactions[index + 1]
        assert next_reaction.mode == "A"

    for reset in result.resets:
        next_reaction = next(
            (
                reaction
                for reaction in result.reactions
                if reaction.first_idx > reset.index
            ),
            None,
        )
        owner = engine.UnifiedReactionDetector(
            candles, seconds, start_index, end_index, case.direction
        )
        expected = owner._first_direct_same_direction_after_reset(
            case.direction, reset.index
        )
        if next_reaction is None:
            continue
        assert expected is not None
        assert (
            next_reaction.first_idx,
            next_reaction.break_idx,
        ) == (
            expected.first_idx,
            expected.break_idx,
        )


def synthetic_owner_regression(engine) -> None:
    base = datetime(2026, 1, 1)

    def candle(index, tag, open_, high, low, close):
        timestamp = base + timedelta(seconds=30 * index)
        return engine.Candle(
            index=index,
            timestamp=timestamp,
            display_time=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            tag=tag,
            open=Decimal(open_),
            high=Decimal(high),
            low=Decimal(low),
            close=Decimal(close),
        )

    bearish = [
        candle(0, "GREEN", "9.0", "10.0", "9.0", "9.5"),
        candle(1, "RED", "9.0", "9.8", "8.0", "8.5"),
        candle(2, "GREEN", "8.5", "9.5", "8.2", "9.0"),
        candle(3, "RED", "9.0", "9.4", "8.6", "8.7"),
        candle(4, "GREEN", "8.7", "9.3", "8.5", "9.0"),
        candle(5, "RED", "9.0", "9.2", "8.4", "8.6"),
        candle(6, "GREEN", "8.6", "10.1", "8.7", "9.8"),
        candle(7, "RED", "9.8", "10.0", "9.0", "9.2"),
        candle(8, "GREEN", "9.2", "9.9", "8.9", "9.6"),
        candle(9, "RED", "9.6", "9.7", "8.8", "9.0"),
    ]
    detector = engine.UnifiedReactionDetector(
        bearish, bearish, 0, len(bearish) - 1, "bearish"
    )
    candidate = detector._first_direct_same_direction_after_reset("bearish", 0)
    assert candidate is not None
    assert candidate.first_idx == 8
    assert candidate.break_idx == 9

    equal_bearish = list(bearish)
    equal_bearish[2] = candle(
        2, "GREEN", "8.5", "10.0", "8.2", "9.0"
    )
    detector = engine.UnifiedReactionDetector(
        equal_bearish, equal_bearish, 0, len(equal_bearish) - 1, "bearish"
    )
    assert detector._build_direct_candidate("bearish", 0, 2) is not None

    bullish = []
    for item in bearish:
        bullish.append(
            engine.Candle(
                index=item.index,
                timestamp=item.timestamp,
                display_time=item.display_time,
                tag="RED" if item.tag == "GREEN" else "GREEN",
                open=Decimal("20") - item.open,
                high=Decimal("20") - item.low,
                low=Decimal("20") - item.high,
                close=Decimal("20") - item.close,
            )
        )
    detector = engine.UnifiedReactionDetector(
        bullish, bullish, 0, len(bullish) - 1, "bullish"
    )
    candidate = detector._first_direct_same_direction_after_reset("bullish", 0)
    assert candidate is not None
    assert candidate.first_idx == 8
    assert candidate.break_idx == 9

    equal_bullish = list(bullish)
    equal_source = equal_bearish[2]
    equal_bullish[2] = engine.Candle(
        index=equal_source.index,
        timestamp=equal_source.timestamp,
        display_time=equal_source.display_time,
        tag="RED",
        open=Decimal("20") - equal_source.open,
        high=Decimal("20") - equal_source.low,
        low=Decimal("20") - equal_source.high,
        close=Decimal("20") - equal_source.close,
    )
    detector = engine.UnifiedReactionDetector(
        equal_bullish, equal_bullish, 0, len(equal_bullish) - 1, "bullish"
    )
    assert detector._build_direct_candidate("bullish", 0, 2) is not None


def synthetic_a_mirror_regression(engine, a_engine) -> None:
    base = datetime(2026, 1, 1)

    def candle(index, tag, open_, high, low, close):
        timestamp = base + timedelta(seconds=30 * index)
        return engine.Candle(
            index=index,
            timestamp=timestamp,
            display_time=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            tag=tag,
            open=Decimal(open_),
            high=Decimal(high),
            low=Decimal(low),
            close=Decimal(close),
        )

    bullish = [
        candle(0, "GREEN", "11", "12", "10", "11.5"),
        candle(1, "RED", "11", "11", "9", "9.5"),
        candle(2, "GREEN", "11", "12", "11", "11.5"),
        candle(3, "GREEN", "9", "10", "8", "9.5"),
        candle(4, "RED", "10", "10", "9", "9.2"),
        candle(5, "GREEN", "9.2", "13", "9", "12.5"),
    ]
    bullish_reaction = SimpleNamespace(
        first_idx=4,
        break_idx=5,
        box_top=Decimal("12"),
        box_bottom=Decimal("9"),
    )
    bullish_blues = [
        SimpleNamespace(
            reaction_number=1,
            kind="reset",
            source_index=0,
            source_time=bullish[0].timestamp,
            source_extreme=Decimal("10"),
            broken_level=Decimal("11"),
        ),
        SimpleNamespace(
            reaction_number=1,
            kind="reset",
            source_index=2,
            source_time=bullish[2].timestamp,
            source_extreme=Decimal("11"),
            broken_level=Decimal("12"),
        ),
    ]
    bullish_a = a_engine.detect_a_zones(
        "bullish",
        [bullish_reaction],
        bullish_blues,
        bullish,
        bullish,
        30,
    )
    assert len(bullish_a) == 1
    assert bullish_a[0].source_index == 3
    assert bullish_a[0].price == Decimal("8")

    bearish = [
        engine.Candle(
            index=item.index,
            timestamp=item.timestamp,
            display_time=item.display_time,
            tag="RED" if item.tag == "GREEN" else "GREEN",
            open=Decimal("20") - item.open,
            high=Decimal("20") - item.low,
            low=Decimal("20") - item.high,
            close=Decimal("20") - item.close,
        )
        for item in bullish
    ]
    bearish_reaction = SimpleNamespace(
        first_idx=4,
        break_idx=5,
        box_top=Decimal("11"),
        box_bottom=Decimal("8"),
    )
    bearish_blues = [
        SimpleNamespace(
            reaction_number=1,
            kind="reset",
            source_index=0,
            source_time=bearish[0].timestamp,
            source_extreme=Decimal("10"),
            broken_level=Decimal("9"),
        ),
        SimpleNamespace(
            reaction_number=1,
            kind="reset",
            source_index=2,
            source_time=bearish[2].timestamp,
            source_extreme=Decimal("9"),
            broken_level=Decimal("8"),
        ),
    ]
    bearish_a = a_engine.detect_a_zones(
        "bearish",
        [bearish_reaction],
        bearish_blues,
        bearish,
        bearish,
        30,
    )
    assert len(bearish_a) == 1
    assert bearish_a[0].source_index == 3
    assert bearish_a[0].price == Decimal("12")

    formation_bullish = [
        candle(0, "GREEN", "10", "11", "10", "10.5"),
        candle(1, "RED", "10", "10.5", "9", "9.5"),
        candle(2, "RED", "9", "9.5", "8", "8.5"),
        candle(3, "RED", "9", "10", "9", "9.5"),
        candle(4, "GREEN", "9.5", "13", "9.5", "12.5"),
    ]
    formation_reaction = SimpleNamespace(
        first_idx=3,
        break_idx=4,
        box_top=Decimal("12"),
        box_bottom=Decimal("9"),
    )
    formation_blues = [
        SimpleNamespace(
            reaction_number=1,
            kind="reset",
            source_index=0,
            source_time=formation_bullish[0].timestamp,
            source_extreme=Decimal("10"),
            broken_level=Decimal("11"),
        ),
        SimpleNamespace(
            reaction_number=1,
            kind="reset",
            source_index=2,
            source_time=formation_bullish[2].timestamp,
            source_extreme=Decimal("8"),
            broken_level=Decimal("9"),
        ),
    ]
    formation_a = a_engine.detect_a_zones(
        "bullish",
        [formation_reaction],
        formation_blues,
        formation_bullish,
        formation_bullish,
        30,
    )
    assert len(formation_a) == 1
    assert (
        formation_a[0].continuation_level,
        formation_a[0].trigger_index,
        formation_a[0].source_index,
        formation_a[0].price,
    ) == (Decimal("9"), 2, 2, Decimal("8"))

    formation_bearish = [
        engine.Candle(
            index=item.index,
            timestamp=item.timestamp,
            display_time=item.display_time,
            tag="RED" if item.tag == "GREEN" else "GREEN",
            open=Decimal("20") - item.open,
            high=Decimal("20") - item.low,
            low=Decimal("20") - item.high,
            close=Decimal("20") - item.close,
        )
        for item in formation_bullish
    ]
    formation_bearish_reaction = SimpleNamespace(
        first_idx=3,
        break_idx=4,
        box_top=Decimal("11"),
        box_bottom=Decimal("8"),
    )
    formation_bearish_blues = [
        SimpleNamespace(
            reaction_number=1,
            kind="reset",
            source_index=0,
            source_time=formation_bearish[0].timestamp,
            source_extreme=Decimal("10"),
            broken_level=Decimal("9"),
        ),
        SimpleNamespace(
            reaction_number=1,
            kind="reset",
            source_index=2,
            source_time=formation_bearish[2].timestamp,
            source_extreme=Decimal("12"),
            broken_level=Decimal("11"),
        ),
    ]
    formation_bearish_a = a_engine.detect_a_zones(
        "bearish",
        [formation_bearish_reaction],
        formation_bearish_blues,
        formation_bearish,
        formation_bearish,
        30,
    )
    assert len(formation_bearish_a) == 1
    assert (
        formation_bearish_a[0].continuation_level,
        formation_bearish_a[0].trigger_index,
        formation_bearish_a[0].source_index,
        formation_bearish_a[0].price,
    ) == (Decimal("11"), 2, 2, Decimal("12"))


def synthetic_s_mirror_regression(engine, s_engine) -> None:
    base = datetime(2026, 1, 1)

    def candle(index, tag, open_, high, low, close):
        timestamp = base + timedelta(seconds=30 * index)
        return engine.Candle(
            index=index,
            timestamp=timestamp,
            display_time=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            tag=tag,
            open=Decimal(open_),
            high=Decimal(high),
            low=Decimal(low),
            close=Decimal(close),
        )

    bullish = [
        candle(0, "GREEN", "10", "11", "10", "10.5"),
        candle(1, "GREEN", "10.5", "12", "10.2", "11.5"),
        candle(2, "RED", "11.5", "12.5", "8", "9"),
        candle(3, "GREEN", "9", "11", "9", "10"),
        candle(4, "RED", "10", "12", "8.5", "9"),
        candle(5, "GREEN", "9", "14", "8.2", "13"),
    ]
    trend_reaction = SimpleNamespace(
        first_idx=0,
        break_idx=1,
        box_top=Decimal("11"),
        box_bottom=Decimal("10"),
        intrabar_start=None,
    )
    post_trend_reaction = SimpleNamespace(
        first_idx=4,
        break_idx=5,
        box_top=Decimal("13"),
        box_bottom=Decimal("8.5"),
        mode="A",
        anchor_idx=2,
        anchor_value=Decimal("8"),
        leg_boundary_value=Decimal("8"),
        intrabar_start=None,
    )
    order_reaction = SimpleNamespace(
        first_idx=3,
        break_idx=4,
        box_top=Decimal("11"),
        box_top_source_idx=3,
        box_bottom=Decimal("9"),
        box_bottom_source_idx=3,
        mode="A",
        anchor_idx=2,
        anchor_value=Decimal("12.5"),
        leg_boundary_value=Decimal("12.5"),
        intrabar_start=None,
    )
    a_zone = SimpleNamespace(
        reaction_number=1,
        reaction_break_time=bullish[1].timestamp,
        source_index=0,
        source_time=bullish[0].timestamp,
        price=Decimal("10"),
    )
    bullish_s = s_engine.detect_s_zones(
        "bullish",
        [trend_reaction, post_trend_reaction],
        [order_reaction],
        [],
        [a_zone],
        bullish,
        bullish,
        30,
        0,
        len(bullish) - 1,
    )
    assert len(bullish_s) == 1
    assert (
        bullish_s[0].color,
        bullish_s[0].source_index,
        bullish_s[0].order_stop_level,
        bullish_s[0].decision_index,
    ) == ("red", 2, Decimal("12.5"), 5)
    blue_candles = bullish + [
        candle(6, "GREEN", "10", "12", "7.5", "10")
    ]
    blue_line = SimpleNamespace(
        kind="reset",
        reaction_number=2,
        source_index=6,
        source_time=blue_candles[6].timestamp,
        broken_level=Decimal("8"),
        source_extreme=Decimal("7.5"),
    )
    blue_order = SimpleNamespace(
        first_idx=3,
        break_idx=4,
        box_top=Decimal("11"),
        box_top_source_idx=3,
        box_bottom=Decimal("9"),
        box_bottom_source_idx=3,
        mode="A",
        anchor_idx=2,
        anchor_value=Decimal("15"),
        leg_boundary_value=Decimal("15"),
        intrabar_start=None,
    )
    blue_s = s_engine.detect_s_zones(
        "bullish",
        [trend_reaction, post_trend_reaction],
        [blue_order],
        [blue_line],
        [a_zone],
        blue_candles,
        blue_candles,
        30,
        0,
        len(blue_candles) - 1,
    )
    assert len(blue_s) == 1
    assert blue_s[0].color == "blue"

    bearish = [
        engine.Candle(
            index=item.index,
            timestamp=item.timestamp,
            display_time=item.display_time,
            tag="RED" if item.tag == "GREEN" else "GREEN",
            open=Decimal("20") - item.open,
            high=Decimal("20") - item.low,
            low=Decimal("20") - item.high,
            close=Decimal("20") - item.close,
        )
        for item in bullish
    ]
    mirrored_trend = SimpleNamespace(
        first_idx=0,
        break_idx=1,
        box_top=Decimal("10"),
        box_bottom=Decimal("9"),
        intrabar_start=None,
    )
    mirrored_post_trend = SimpleNamespace(
        first_idx=4,
        break_idx=5,
        box_top=Decimal("11.5"),
        box_bottom=Decimal("7"),
        mode="A",
        anchor_idx=2,
        anchor_value=Decimal("12"),
        leg_boundary_value=Decimal("12"),
        intrabar_start=None,
    )
    mirrored_order = SimpleNamespace(
        first_idx=3,
        break_idx=4,
        box_top=Decimal("11"),
        box_top_source_idx=3,
        box_bottom=Decimal("9"),
        box_bottom_source_idx=3,
        mode="A",
        anchor_idx=2,
        anchor_value=Decimal("7.5"),
        leg_boundary_value=Decimal("7.5"),
        intrabar_start=None,
    )
    mirrored_a = SimpleNamespace(
        reaction_number=1,
        reaction_break_time=bearish[1].timestamp,
        source_index=0,
        source_time=bearish[0].timestamp,
        price=Decimal("10"),
    )
    bearish_s = s_engine.detect_s_zones(
        "bearish",
        [mirrored_trend, mirrored_post_trend],
        [mirrored_order],
        [],
        [mirrored_a],
        bearish,
        bearish,
        30,
        0,
        len(bearish) - 1,
    )
    assert len(bearish_s) == 1
    assert (
        bearish_s[0].color,
        bearish_s[0].source_index,
        bearish_s[0].order_stop_level,
        bearish_s[0].decision_index,
    ) == ("red", 2, Decimal("7.5"), 5)
    assert s_engine.visible_a_zones(
        [SimpleNamespace(source_index=2), SimpleNamespace(source_index=4)],
        bearish_s,
    ) == [SimpleNamespace(source_index=4)]


def synthetic_s_candidate_timing_regression(engine, s_engine) -> None:
    """Candidate timing must mirror strictly around the order box boundary."""
    base = datetime(2026, 1, 2)

    def candle(index, high, low):
        timestamp = base + timedelta(seconds=30 * index)
        return engine.Candle(
            index=index,
            timestamp=timestamp,
            display_time=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            tag="GREEN",
            open=Decimal("10"),
            high=Decimal(high),
            low=Decimal(low),
            close=Decimal("10"),
        )

    bullish_candles = [
        candle(0, "11", "10"),
        candle(1, "11", "9"),
        candle(2, "11", "8"),
        candle(3, "12", "8"),
    ]
    bullish = s_engine.SDetector(
        "bullish",
        [],
        [],
        [],
        [],
        bullish_candles,
        bullish_candles,
        30,
    )
    order = SimpleNamespace(box_bottom=Decimal("9"), first_idx=2)
    assert bullish._candidate_timing(1, order, bullish_candles[2].timestamp) == "after"
    order = SimpleNamespace(box_bottom=Decimal("9.1"), first_idx=2)
    assert bullish._candidate_timing(1, order, bullish_candles[2].timestamp) == "before"
    assert bullish._candidate_before_order(1, order)[0] == 2

    bearish_candles = [
        candle(0, "10", "9"),
        candle(1, "11", "9"),
        candle(2, "12", "9"),
        candle(3, "12", "8"),
    ]
    bearish = s_engine.SDetector(
        "bearish",
        [],
        [],
        [],
        [],
        bearish_candles,
        bearish_candles,
        30,
    )
    order = SimpleNamespace(box_top=Decimal("11"), first_idx=2)
    assert bearish._candidate_timing(1, order, bearish_candles[2].timestamp) == "after"
    order = SimpleNamespace(box_top=Decimal("10.9"), first_idx=2)
    assert bearish._candidate_timing(1, order, bearish_candles[2].timestamp) == "before"
    assert bearish._candidate_before_order(1, order)[0] == 2


def final_visible_a_zones(s_engine, a_zones, s_zones):
    visible = s_engine.visible_a_zones(a_zones, s_zones)
    a_sources = {int(item.source_index) for item in visible}
    s_sources = {int(item.source_index) for item in s_zones}
    assert a_sources.isdisjoint(s_sources)
    return visible


def validate_a_case(
    engine,
    bridge,
    blue_engine,
    a_engine,
    s_engine,
    case: ACase,
    source: Path,
    rows: list[dict],
    write: bool,
) -> dict:
    lower = bridge.build_candles(engine, rows, 1)
    candles = bridge.build_candles(engine, rows, 30)
    start = datetime.fromisoformat(case.start)
    end = datetime.fromisoformat(case.end)
    eligible = [
        index
        for index, candle in enumerate(candles)
        if start <= candle.timestamp <= end
    ]
    assert eligible
    result = engine.UnifiedReactionDetector(
        candles, lower, eligible[0], eligible[-1], "bullish"
    ).detect()
    validate_result(
        engine,
        Case(case.filename, "bullish", case.start, case.end),
        result,
        candles,
        lower,
        eligible[0],
        eligible[-1],
    )
    blue_lines = blue_engine.detect_blue_lines(
        "bullish",
        result.reactions,
        candles,
        lower,
        30,
        result.resets,
    )
    a_zones = a_engine.detect_a_zones(
        "bullish",
        result.reactions,
        blue_lines,
        candles,
        lower,
        30,
    )
    opposite = engine.UnifiedReactionDetector(
        candles, lower, eligible[0], eligible[-1], "bearish"
    ).detect()
    s_zones = s_engine.detect_s_zones(
        "bullish",
        result.reactions,
        opposite.reactions,
        blue_lines,
        a_zones,
        candles,
        lower,
        30,
        eligible[0],
        eligible[-1],
    )
    visible_a = final_visible_a_zones(s_engine, a_zones, s_zones)

    blue_times = {
        getattr(item, "source_time").strftime("%Y-%m-%d %H:%M:%S")
        for item in blue_lines
    }
    for expected in case.expected_blue_sources:
        assert expected in blue_times

    actual = tuple(
        (
            item.source_time.strftime("%Y-%m-%d %H:%M:%S"),
            str(item.price),
            item.reaction_first_time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        for item in a_zones
    )
    if actual != case.expected:
        assert actual == case.expected

    if case is A_CASES[1]:
        assert a_zones[0].continuation_level == Decimal("3979.72")
        assert a_zones[0].continuation_source_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ) == "2026-06-30 08:50:00"
    if case is A_CASES[2]:
        assert a_zones[0].continuation_level == Decimal("4027.2")
        assert a_zones[0].continuation_source_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ) == "2026-06-30 10:52:30"
        assert a_zones[0].trigger_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ) == "2026-06-30 11:01:30"
    if case.filename.startswith("12_a_bullish_2026-07-13"):
        second = a_zones[1]
        assert second.continuation_level == Decimal("73.767")
        assert second.continuation_source_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ) == "2026-07-13 15:20:30"
        assert second.trigger_event_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ) == "2026-07-13 15:24:10"
        assert second.blue_2_stop_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ) == "2026-07-13 15:24:00"
    if case.filename.startswith("13_a_bullish_2026-07-13"):
        reaction = next(
            item
            for item in result.reactions
            if item.first_time == "2026-07-13 18:04:00"
        )
        assert (
            reaction.box_top_source_time,
            reaction.box_top,
            reaction.box_bottom_source_time,
            reaction.box_bottom,
            reaction.break_time,
        ) == (
            "2026-07-13 18:03:30",
            Decimal("74.704"),
            "2026-07-13 18:04:30",
            Decimal("74.582"),
            "2026-07-13 18:05:30",
        )
        zone = a_zones[0]
        assert zone.continuation_level == Decimal("74.582")
        assert zone.continuation_source_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ) == "2026-07-13 18:02:30"
        assert zone.trigger_event_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ) == "2026-07-13 18:08:35"

    reactions, resets = bridge.serialize(result)
    payload = {
        "snapshotVersion": "5",
        "source": project_path(source),
        "sourceSha256": sha256(source),
        "engine": project_path(ENGINE_PATH),
        "engineSha256": sha256(ENGINE_PATH),
        "engineVersion": engine.ENGINE_VERSION,
        "blueEngine": project_path(BLUE_ENGINE_PATH),
        "blueEngineSha256": sha256(BLUE_ENGINE_PATH),
        "aEngine": project_path(A_ENGINE_PATH),
        "aEngineSha256": sha256(A_ENGINE_PATH),
        "aVersion": a_engine.A_VERSION,
        "sEngine": project_path(S_ENGINE_PATH),
        "sEngineSha256": sha256(S_ENGINE_PATH),
        "sVersion": s_engine.S_VERSION,
        "blueLinesTested": True,
        "aTested": True,
        "sTested": True,
        "previousBaselineUsed": False,
        "timeframeSeconds": 30,
        "direction": "bullish",
        "requestedFrom": case.start,
        "requestedTo": case.end,
        "actualFrom": candles[eligible[0]].display_time,
        "actualTo": candles[eligible[-1]].display_time,
        "startIndex": eligible[0],
        "endIndex": eligible[-1],
        "reactions": reactions,
        "resets": resets,
        "blueLines": bridge.serialize_blue_lines(blue_lines),
        "aZones": bridge.serialize_a_zones(visible_a),
        "sZones": bridge.serialize_s_zones(s_zones),
    }
    if write:
        (RESULTS_DIR / case.filename).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return {
        "file": case.filename,
        "direction": "bullish",
        "from": case.start,
        "to": case.end,
        "reactions": len(reactions),
        "resets": len(resets),
        "blueLines": len(blue_lines),
        "aZones": len(visible_a),
        "sZones": len(s_zones),
        "startIndex": eligible[0],
        "endIndex": eligible[-1],
    }


def validate_s_case(
    engine,
    bridge,
    blue_engine,
    a_engine,
    s_engine,
    case: SCase,
    source: Path,
    rows: list[dict],
    write: bool,
) -> dict:
    lower = bridge.build_candles(engine, rows, 1)
    candles = bridge.build_candles(engine, rows, 30)
    start = datetime.fromisoformat(case.start)
    end = datetime.fromisoformat(case.end)
    eligible = [
        index
        for index, candle in enumerate(candles)
        if start <= candle.timestamp <= end
    ]
    assert eligible
    results = {
        direction: engine.UnifiedReactionDetector(
            candles, lower, eligible[0], eligible[-1], direction
        ).detect()
        for direction in ("bullish", "bearish")
    }
    validate_result(
        engine,
        Case(case.filename, "bullish", case.start, case.end),
        results["bullish"],
        candles,
        lower,
        eligible[0],
        eligible[-1],
    )
    blue_lines = blue_engine.detect_blue_lines(
        "bullish",
        results["bullish"].reactions,
        candles,
        lower,
        30,
        results["bullish"].resets,
    )
    a_zones = a_engine.detect_a_zones(
        "bullish",
        results["bullish"].reactions,
        blue_lines,
        candles,
        lower,
        30,
    )
    s_zones = s_engine.detect_s_zones(
        "bullish",
        results["bullish"].reactions,
        results["bearish"].reactions,
        blue_lines,
        a_zones,
        candles,
        lower,
        30,
        eligible[0],
        eligible[-1],
    )
    visible_a = final_visible_a_zones(s_engine, a_zones, s_zones)
    if case.expected_visible_a_sources:
        assert tuple(
            item.source_time.strftime("%Y-%m-%d %H:%M:%S")
            for item in visible_a
        ) == case.expected_visible_a_sources
    visible_a_sources = {
        item.source_time.strftime("%Y-%m-%d %H:%M:%S")
        for item in visible_a
    }
    assert set(case.required_visible_a_sources) <= visible_a_sources
    assert visible_a_sources.isdisjoint(case.forbidden_visible_a_sources)
    actual = tuple(
        (
            item.source_time.strftime("%Y-%m-%d %H:%M:%S"),
            item.color,
            item.a_source_time.strftime("%Y-%m-%d %H:%M:%S"),
            item.order_first_time.strftime("%Y-%m-%d %H:%M:%S"),
            item.order_stop_source_time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        for item in s_zones
    )
    assert actual == case.expected, {
        "case": case.filename,
        "actual": actual,
        "expected": case.expected,
    }
    assert all(item.order_direction == "bearish" for item in s_zones)
    assert all(item.order_box_bottom < item.order_box_top for item in s_zones)

    reactions, resets = bridge.serialize(results["bullish"])
    payload = {
        "snapshotVersion": "5",
        "source": project_path(source),
        "sourceSha256": sha256(source),
        "engine": project_path(ENGINE_PATH),
        "engineSha256": sha256(ENGINE_PATH),
        "engineVersion": engine.ENGINE_VERSION,
        "blueEngine": project_path(BLUE_ENGINE_PATH),
        "blueEngineSha256": sha256(BLUE_ENGINE_PATH),
        "aEngine": project_path(A_ENGINE_PATH),
        "aEngineSha256": sha256(A_ENGINE_PATH),
        "aVersion": a_engine.A_VERSION,
        "sEngine": project_path(S_ENGINE_PATH),
        "sEngineSha256": sha256(S_ENGINE_PATH),
        "sVersion": s_engine.S_VERSION,
        "blueLinesTested": True,
        "aTested": True,
        "sTested": True,
        "previousBaselineUsed": False,
        "timeframeSeconds": 30,
        "direction": "bullish",
        "requestedFrom": case.start,
        "requestedTo": case.end,
        "actualFrom": candles[eligible[0]].display_time,
        "actualTo": candles[eligible[-1]].display_time,
        "startIndex": eligible[0],
        "endIndex": eligible[-1],
        "reactions": reactions,
        "resets": resets,
        "blueLines": bridge.serialize_blue_lines(blue_lines),
        "aZones": bridge.serialize_a_zones(visible_a),
        "sZones": bridge.serialize_s_zones(s_zones),
    }
    if write:
        (RESULTS_DIR / case.filename).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return {
        "file": case.filename,
        "direction": "bullish",
        "from": case.start,
        "to": case.end,
        "reactions": len(reactions),
        "resets": len(resets),
        "blueLines": len(blue_lines),
        "aZones": len(visible_a),
        "sZones": len(s_zones),
        "startIndex": eligible[0],
        "endIndex": eligible[-1],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--reactions-only", action="store_true")
    args = parser.parse_args()

    engine = load_module("reaction_detection_integrated_ranges", ENGINE_PATH)
    bridge = load_module("reaction_bridge_integrated_ranges", BRIDGE_PATH)
    blue_engine = (
        None
        if args.reactions_only
        else load_module("blue_line_integrated_ranges", BLUE_ENGINE_PATH)
    )
    a_engine = (
        None
        if args.reactions_only
        else load_module("a_zone_integrated_ranges", A_ENGINE_PATH)
    )
    s_engine = (
        None
        if args.reactions_only
        else load_module("s_zone_integrated_ranges", S_ENGINE_PATH)
    )
    synthetic_owner_regression(engine)
    if a_engine is not None:
        synthetic_a_mirror_regression(engine, a_engine)
    if s_engine is not None:
        synthetic_s_mirror_regression(engine, s_engine)
        synthetic_s_candidate_timing_regression(engine, s_engine)

    source = next(
        (ROOT / "market-data" / "raw").glob(
            "candle-history FOREXCOM_XAUUSD 1S "
            "from 2026-07-28 01-55-38*.json"
        )
    )
    rows = json.loads(source.read_text(encoding="utf-8-sig"))
    seconds = bridge.build_candles(engine, rows, 1)
    candles = bridge.build_candles(engine, rows, 30)
    source_hash = sha256(source)
    engine_hash = sha256(ENGINE_PATH)
    blue_engine_hash = (
        None if args.reactions_only else sha256(BLUE_ENGINE_PATH)
    )
    a_engine_hash = None if args.reactions_only else sha256(A_ENGINE_PATH)
    s_engine_hash = None if args.reactions_only else sha256(S_ENGINE_PATH)
    manifest_cases = []

    for case in CASES:
        start = datetime.fromisoformat(case.start)
        end = datetime.fromisoformat(case.end)
        eligible = [
            index
            for index, candle in enumerate(candles)
            if start <= candle.timestamp <= end
        ]
        result = engine.UnifiedReactionDetector(
            candles, seconds, eligible[0], eligible[-1], case.direction
        ).detect()
        opposite_direction = (
            "bearish" if case.direction == "bullish" else "bullish"
        )
        opposite_result = (
            None
            if args.reactions_only
            else engine.UnifiedReactionDetector(
                candles,
                seconds,
                eligible[0],
                eligible[-1],
                opposite_direction,
            ).detect()
        )
        validate_result(
            engine, case, result, candles, seconds, eligible[0], eligible[-1]
        )
        blue_lines = (
            []
            if blue_engine is None
            else blue_engine.detect_blue_lines(
                case.direction,
                result.reactions,
                candles,
                seconds,
                30,
                result.resets,
            )
        )
        a_zones = (
            []
            if a_engine is None
            else a_engine.detect_a_zones(
                case.direction,
                result.reactions,
                blue_lines,
                candles,
                seconds,
                30,
            )
        )
        s_zones = (
            []
            if s_engine is None
            else s_engine.detect_s_zones(
                case.direction,
                result.reactions,
                opposite_result.reactions,
                blue_lines,
                a_zones,
                candles,
                seconds,
                30,
                eligible[0],
                eligible[-1],
            )
        )
        visible_a = (
            a_zones
            if s_engine is None
            else final_visible_a_zones(s_engine, a_zones, s_zones)
        )
        for line in blue_lines:
            assert line.direction == case.direction
            assert eligible[0] <= line.source_index <= eligible[-1]
            assert line.start_time < line.end_time
            assert line.kind in {"scale", "reset"}

        by_first = {item.first_time: item for item in result.reactions}
        if case is CASES[3]:
            assert "2026-07-28 14:09:00" not in by_first
            assert "2026-07-28 17:56:00" not in by_first
            for expected in (
                "2026-07-28 17:21:00",
                "2026-07-28 17:23:30",
                "2026-07-28 18:05:00",
            ):
                assert expected in by_first
        if case is CASES[5]:
            assert "2026-07-29 03:34:30" not in by_first
            assert "2026-07-29 03:53:30" in by_first

        reactions, resets = bridge.serialize(result)
        payload = {
            "snapshotVersion": "5",
            "source": project_path(source),
            "sourceSha256": source_hash,
            "engine": project_path(ENGINE_PATH),
            "engineSha256": engine_hash,
            "engineVersion": engine.ENGINE_VERSION,
            "blueEngine": project_path(BLUE_ENGINE_PATH),
            "blueEngineSha256": blue_engine_hash,
            "aEngine": project_path(A_ENGINE_PATH),
            "aEngineSha256": a_engine_hash,
            "aVersion": None if a_engine is None else a_engine.A_VERSION,
            "sEngine": project_path(S_ENGINE_PATH),
            "sEngineSha256": s_engine_hash,
            "sVersion": None if s_engine is None else s_engine.S_VERSION,
            "blueLinesTested": not args.reactions_only,
            "aTested": not args.reactions_only,
            "sTested": not args.reactions_only,
            "previousBaselineUsed": False,
            "timeframeSeconds": 30,
            "direction": case.direction,
            "requestedFrom": case.start,
            "requestedTo": case.end,
            "actualFrom": candles[eligible[0]].display_time,
            "actualTo": candles[eligible[-1]].display_time,
            "startIndex": eligible[0],
            "endIndex": eligible[-1],
            "reactions": reactions,
            "resets": resets,
            "blueLines": bridge.serialize_blue_lines(blue_lines),
            "aZones": (
                [] if a_engine is None else bridge.serialize_a_zones(visible_a)
            ),
            "sZones": (
                [] if s_engine is None else bridge.serialize_s_zones(s_zones)
            ),
        }
        if args.write:
            (RESULTS_DIR / case.filename).write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        manifest_cases.append(
            {
                "file": case.filename,
                "direction": case.direction,
                "from": case.start,
                "to": case.end,
                "reactions": len(reactions),
                "resets": len(resets),
                "blueLines": len(blue_lines),
                "aZones": len(visible_a),
                "sZones": len(s_zones),
                "startIndex": eligible[0],
                "endIndex": eligible[-1],
            }
        )
        if args.reactions_only:
            print(
                f"PASS {case.filename}: "
                f"{len(reactions)} reactions, {len(resets)} resets"
            )
        else:
            print(
                f"PASS {case.filename}: {len(reactions)} reactions, "
                f"{len(resets)} resets, {len(blue_lines)} blue lines, "
                f"{len(visible_a)} A, {len(s_zones)} S"
            )

    if not args.reactions_only:
        source_cache: dict[Path, list[dict]] = {}
        for case in A_CASES:
            a_source = next(
                (ROOT / "market-data" / "raw").glob(case.source_pattern)
            )
            if a_source not in source_cache:
                source_cache[a_source] = json.loads(
                    a_source.read_text(encoding="utf-8-sig")
                )
            summary = validate_a_case(
                engine,
                bridge,
                blue_engine,
                a_engine,
                s_engine,
                case,
                a_source,
                source_cache[a_source],
                args.write,
            )
            manifest_cases.append(summary)
            print(
                f"PASS {case.filename}: {summary['reactions']} reactions, "
                f"{summary['resets']} resets, {summary['blueLines']} blue lines, "
                f"{summary['aZones']} A, {summary['sZones']} S"
            )

        s_source = next(
            (ROOT / "market-data" / "raw").glob(
                "candle-history FXCM_USOIL 5S from 2026-07-10*.json"
            )
        )
        s_rows = json.loads(s_source.read_text(encoding="utf-8-sig"))
        for case in S_CASES:
            summary = validate_s_case(
                engine,
                bridge,
                blue_engine,
                a_engine,
                s_engine,
                case,
                s_source,
                s_rows,
                args.write,
            )
            manifest_cases.append(summary)
            print(
                f"PASS {case.filename}: {summary['reactions']} reactions, "
                f"{summary['resets']} resets, {summary['blueLines']} blue lines, "
                f"{summary['aZones']} A, {summary['sZones']} S"
            )

    if args.write:
        manifest = {
            "sourceSha256": source_hash,
            "engineSha256": engine_hash,
            "blueEngineSha256": blue_engine_hash,
            "aEngineSha256": a_engine_hash,
            "aVersion": None if a_engine is None else a_engine.A_VERSION,
            "sEngineSha256": s_engine_hash,
            "sVersion": None if s_engine is None else s_engine.S_VERSION,
            "engineVersion": engine.ENGINE_VERSION,
            "blueLinesTested": not args.reactions_only,
            "aTested": not args.reactions_only,
            "sTested": not args.reactions_only,
            "previousBaselineUsed": False,
            "cases": manifest_cases,
        }
        (RESULTS_DIR / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
