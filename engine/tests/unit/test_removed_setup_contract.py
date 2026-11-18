"""Supported calculation paths publish native structures without setup assessment."""
import json

import pytest

from test_live_pipeline_continuation import pipeline, setup


REMOVED_FIELDS = {
    "setupVersion", "setupPhase", "positionSetups", "stopAllAssessments",
    "behaviorAssessments", "setupReferenceBreaks",
}


def assert_native_payload(value):
    if isinstance(value, dict):
        assert not REMOVED_FIELDS.intersection(value)
        for item in value.values():
            assert_native_payload(item)
    elif isinstance(value, list):
        for item in value:
            assert_native_payload(item)


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_manual_and_live_calculations_publish_native_contract_without_assessments(direction, tmp_path):
    from live_pipeline import LivePipelineContinuation

    source = tmp_path / "native.json"
    first = 1_795_000_020
    rows = []
    for index in range(300):
        mid = 100 + (index * 13 % 41) - index // 17
        opening, closing = mid + index % 3, mid - index % 2
        rows.append(dict(time=first + index * 5, open=opening,
                         high=max(opening, closing) + index % 7,
                         low=min(opening, closing) - index % 5, close=closing))
    if direction == "bullish":
        rows = [{**row, "open": 200-row["open"], "high": 200-row["low"],
                 "low": 200-row["high"], "close": 200-row["close"]} for row in rows]
    args = setup(direction, source, first, rows[-1]["time"])
    source.write_text(json.dumps(rows), encoding="utf-8")
    engines = pipeline.load_engines(args, {})
    market = pipeline.prepare_market_context(args, engines, {})
    manual = pipeline.build_response_payload(
        args, engines, market, pipeline.prepare_pipeline_state(args, engines, market, {}), {}, 0,
    )
    live = LivePipelineContinuation(args, engines).append(rows)
    for payload in (manual, live):
        assert_native_payload(payload)
        group = payload["directions"][direction]
        for key in ("reactions", "resets", "sZones", "eZones", "stopAlls", "orderAudit"):
            assert isinstance(group[key], list)
        assert group["reactions"], "Native Reaction discovery must remain active."
        assert "primaryHighs" in group and "primaryLows" in group
    manual.pop("timings")
    live.pop("timings")
    assert manual == live
