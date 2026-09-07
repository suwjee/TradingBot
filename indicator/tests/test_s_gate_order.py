"""S order ownership must follow exact events, not rounded candle timestamps."""

from datetime import datetime, timedelta
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "s_gate_order_test_engine", ROOT / "indicator/Modules/4_S-zones/app/s_detector.py"
)
S = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = S
SPEC.loader.exec_module(S)
BASE = datetime(2026, 1, 1)


@pytest.mark.parametrize("event_offset", [-1, 0, 1])
def test_only_the_confirmation_that_stops_a_opens_the_new_order_context(event_offset):
    candles = [SimpleNamespace(timestamp=BASE + timedelta(seconds=30 * i)) for i in range(4)]
    stop = BASE + timedelta(seconds=34)
    previous = SimpleNamespace(first_idx=0, break_idx=1, confirmation=stop + timedelta(seconds=event_offset))
    continuation = SimpleNamespace(
        first_idx=1, break_idx=2, mode="B", intrabar_start=candles[1].timestamp,
        confirmation=BASE + timedelta(seconds=70),
    )
    later = SimpleNamespace(first_idx=2, break_idx=3, confirmation=BASE + timedelta(seconds=95))
    fresh_order = SimpleNamespace(
        first_idx=1, break_idx=2, mode="A", confirmation=BASE + timedelta(seconds=70),
    )
    calls = []

    def resolve(index, event, end):
        calls.append((index, event, end))
        return fresh_order

    detector = S.SDetector(
        "bullish", [], [previous, continuation, later], [], [], candles, [], 30,
        initial_order_geometry=resolve,
    )
    detector._reaction_confirmation_time = lambda reaction, direction: reaction.confirmation
    result = detector._first_order_after(stop)
    if event_offset == 0:
        assert calls == [(1, stop, 3)]
        assert result == (2, fresh_order, fresh_order.confirmation)
        assert result[1] is not continuation  # Do not inherit global Mode-B stop geometry.
    else:
        assert calls == []
        assert result == (3, later, later.confirmation)


def test_without_new_context_resolver_existing_bearish_selection_is_preserved():
    candles = [SimpleNamespace(timestamp=BASE + timedelta(seconds=30 * i)) for i in range(4)]
    stop = BASE + timedelta(seconds=34)
    previous = SimpleNamespace(first_idx=0, break_idx=1, confirmation=stop)
    continuation = SimpleNamespace(
        first_idx=1, break_idx=2, intrabar_start=candles[1].timestamp,
        confirmation=BASE + timedelta(seconds=70),
    )
    later = SimpleNamespace(first_idx=2, break_idx=3, confirmation=BASE + timedelta(seconds=95))
    detector = S.SDetector("bearish", [], [previous, continuation, later], [], [], candles, [], 30)
    detector._reaction_confirmation_time = lambda reaction, direction: reaction.confirmation
    assert detector._first_order_after(stop) == (3, later, later.confirmation)
