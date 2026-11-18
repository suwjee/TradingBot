"""Compare E route arbitration with the task's frozen original Source.

Run from any directory with Python. The bounded artificial chronology is not
market RAW; it exercises duplicate physical identities and route sort contracts.
"""

from dataclasses import fields, is_dataclass
from decimal import Decimal
import importlib.util
from itertools import product
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "engine/pipeline"), str(ROOT / "engine/tests/unit")]

from e_zone_detector import EZoneDetector
from lifecycle_engine import sequence_priority
from reaction_engine import MarketChronology
from test_order_audit_lifecycle_contracts import candle, candidate, moment, s_zone


def freeze(value):
    """Preserve complete field order and Decimal representation across modules."""
    if isinstance(value, Decimal):
        return "Decimal", value.as_tuple()
    if is_dataclass(value):
        return tuple((field.name, freeze(getattr(value, field.name))) for field in fields(value))
    if isinstance(value, dict):
        return tuple((freeze(key), freeze(item)) for key, item in value.items())
    if isinstance(value, (set, frozenset)):
        return tuple(sorted(map(freeze, value), key=repr))
    if isinstance(value, (tuple, list)):
        return tuple(map(freeze, value))
    return value


def load_original():
    path = ROOT / "apps/chart/state/tmp/engine-refactor-20261117/original/engine/pipeline/e_zone_detector.py"
    if not path.is_file():
        raise FileNotFoundError(f"Frozen original Source is required: {path}")
    spec = importlib.util.spec_from_file_location("stage_legacy_e_zone", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.EZoneDetector


def ledger_entry(reaction, confirmation, stopped, number):
    return {
        "reaction": reaction, "reaction_number": number,
        "confirmation_time": moment(confirmation), "stop_level": Decimal("120.000"),
        "stop_source_index": reaction.first_idx,
        "stop_source_time": moment(reaction.first_idx * 30),
        "stop_cross": None if stopped is None else (
            stopped // 30, moment(stopped // 30 * 30), moment(stopped),
        ),
        "causes": set(),
    }


def main():
    original = load_original()
    count = 0
    for direction in ("bullish", "bearish"):
        crossing_times = {140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340}
        lower = [
            candle(index, index,
                   low="90" if index in crossing_times else "100",
                   high="130" if index in crossing_times else "120")
            for index in range(360)
        ]
        chronology = MarketChronology([candle(index, index * 30) for index in range(12)], lower, 30)
        parent = s_zone(direction, source=60, decision=110)
        physical = candidate(5, 6)
        for case in product(
            (130, 140, 160), ("120.00", "121.000"), (130, 140, 160),
            (160, 180, None), (5, 6), (130, 160), (160, 180),
            (False, True), (None, 160),
        ):
            initial_confirmation, initial_level, audit_confirmation, audit_stop, first, other_confirmation, other_stop, reverse, reset = case
            initial = {(5, 6): {
                "reaction": physical, "reaction_number": 1,
                "confirmation_time": moment(initial_confirmation),
                "stop_level": Decimal(initial_level), "stop_source_index": 5,
                "stop_source_time": moment(150),
            }}
            rows = [
                ((5, 6), ledger_entry(physical, audit_confirmation, audit_stop, 2)),
                ((first, 7), ledger_entry(candidate(first, 7), other_confirmation, other_stop, 3)),
            ]
            if reverse:
                rows.reverse()
            outputs, ledgers = [], []
            for detector_type in (original, EZoneDetector):
                detector = detector_type(
                    direction, [], [], [], [], chronology,
                    initial_order_audit=initial, sequence_priority=sequence_priority,
                )
                detector.order_audit = {identity: dict(row, causes=set()) for identity, row in rows}
                for identity, row in detector.order_audit.items():
                    detector._index_order_audit_identity(identity, row["confirmation_time"])
                detector.sequence_resets = {} if reset is None else {moment(reset): 1}
                eager = detector._post_stop_accepted_orders_for_parent(parent, moment(125))
                streamed = list(detector._iter_post_stop_accepted_orders(parent, moment(125)))
                assert freeze(eager) == freeze(streamed), ("stream", direction, case)
                outputs.append(freeze(detector._zone("blue", 1, "S", parent, moment(125))))
                ledgers.append(freeze(detector.order_audit))
            assert outputs[0] == outputs[1], ("zone", direction, case)
            assert ledgers[0] == ledgers[1], ("ledger", direction, case)
            count += 1
    print(f"PASS: {count} frozen-original/current E._zone scenarios and eager/lazy post-stop comparisons.")


if __name__ == "__main__":
    main()
