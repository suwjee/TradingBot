"""Checks for the exact-output regression reporter."""

from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "regression"))

from hpzr2_regression import first_difference


def test_first_difference_reports_stable_json_key_order() -> None:
    baseline = b'{"directions":{"bullish":{"reactions":[{"a":1,"b":2}]}}}'
    candidate = b'{"directions":{"bullish":{"reactions":[{"b":2,"a":1}]}}}'

    assert json.loads(baseline) == json.loads(candidate)
    assert baseline != candidate
    difference = first_difference(baseline, candidate)
    assert difference is not None
    assert difference["stage"] == "stable JSON bytes"
    assert isinstance(difference["byteOffset"], int)


def test_first_difference_reports_numeric_json_representation() -> None:
    baseline = b'{"directions":{"bullish":{"reactions":[{"value":1}]}}}'
    candidate = b'{"directions":{"bullish":{"reactions":[{"value":1.0}]}}}'

    assert json.loads(baseline) == json.loads(candidate)
    difference = first_difference(baseline, candidate)
    assert difference is not None
    assert difference["stage"] == "stable JSON bytes"
    assert difference["baselineByte"] != difference["candidateByte"]
