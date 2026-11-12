"""Repeated directional regimes retain deterministic projection field order."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

BRIDGE = Path(__file__).resolve().parents[2] / "bridge"
sys.path.insert(0, str(BRIDGE))
from trading_pipeline import merge_regime_outputs


@pytest.mark.parametrize("seed", ["0", "1", "2", "3"])
def test_merged_projection_keys_follow_first_appearance_across_hash_seeds(seed):
    script = """
import json, sys
sys.path.insert(0, sys.argv[1])
from trading_pipeline import merge_regime_outputs
first = {'reactions': [{'id': 'first'}], 'bridgeOutput': {'reactions': [{'firstIndex': 1}], 'resets': [], 'aZones': []}}
last = {'reactions': [{'id': 'last'}], 'bridgeOutput': {'aZones': [], 'orderAudit': [{'firstIndex': 2}]}}
print(json.dumps(merge_regime_outputs([('bullish', first), ('bullish', last)]), separators=(',', ':')))
"""
    completed = subprocess.run(
        [sys.executable, "-B", "-c", script, str(BRIDGE)],
        env={**os.environ, "PYTHONHASHSEED": seed},
        capture_output=True, check=True,
    )
    result = json.loads(completed.stdout)["bullish"]
    assert list(result["bridgeOutput"]) == ["reactions", "resets", "aZones", "orderAudit"]
    assert result["reactions"] == [{"id": "first"}, {"id": "last"}]
    assert result["bridgeOutput"]["reactions"] == [{"firstIndex": 1}]
    assert result["bridgeOutput"]["orderAudit"] == [{"firstIndex": 2}]


def test_single_regime_preserves_original_group_identity():
    group = {"reactions": [], "bridgeOutput": {"resets": [], "reactions": []}}
    result = merge_regime_outputs([("bearish", group)])
    assert result["bearish"] is group
    assert list(result["bearish"]["bridgeOutput"]) == ["resets", "reactions"]


def test_merge_preserves_row_identity_segment_order_and_final_metadata():
    first_row, last_row = {"firstIndex": 1}, {"firstIndex": 2}
    first = {"reactions": [first_row], "primaryStatus": "old", "calculationEndTime": 10,
             "bridgeOutput": {"reactions": [first_row]}}
    last = {"reactions": [last_row], "primaryStatus": "final", "bridgeOutput": {"reactions": [last_row]}}
    result = merge_regime_outputs([("bearish", first), ("bullish", {"reactions": []}), ("bearish", last)])
    group = result["bearish"]
    assert list(result) == ["bearish", "bullish"]
    assert group["primaryStatus"] == "final"
    assert group["reactions"][0] is first_row and group["reactions"][1] is last_row
    assert group["bridgeOutput"]["reactions"][0] is first_row
    assert group["bridgeOutput"]["reactions"][1] is last_row
    assert group["calculationSegments"][0] is first and group["calculationSegments"][1] is last
    assert "calculationEndTime" not in group
    assert first["calculationEndTime"] == 10


def test_empty_projection_segments_remain_empty():
    result = merge_regime_outputs([
        ("bullish", {"reactions": [], "bridgeOutput": {}}),
        ("bullish", {"reactions": [], "bridgeOutput": {}}),
    ])
    assert result["bullish"]["bridgeOutput"] == {}
    assert result["bullish"]["reactions"] == []
