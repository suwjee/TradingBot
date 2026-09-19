"""Production trading pipeline orchestration, input normalization, and serialization.

Owns request parsing, raw-range isolation, candle construction, engine loading,
stage orchestration, progress/timing telemetry, and JSON serialization. Trading
validity/ownership rules belong to their calculation engines; this module must
not reimplement them.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import orjson
from bisect import bisect_left
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from zoneinfo import ZoneInfo

# This bridge lives in ``engine/bridge`` while the calculation modules live in
# the sibling ``engine/pipeline`` package.  Put that directory on the module
# search path before importing shared helpers or dynamically loading detectors.
# The detector files intentionally keep their flat local imports
# (``core_utils`` / ``direction_policy``), so this single bootstrap point keeps
# every production module aligned with the deployed folder structure.
_ENGINE_ROOT = Path(__file__).resolve().parents[1]
_PIPELINE_DIR = _ENGINE_ROOT / "pipeline"
_pipeline_dir_text = str(_PIPELINE_DIR)
if _pipeline_dir_text not in sys.path:
    sys.path.insert(0, _pipeline_dir_text)

from core_utils import as_decimal

_DTFMT = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}"


TRADING_PIPELINE_VERSION = "1.2.5"
TRADING_PIPELINE_LAST_MODIFIED = "2026-09-19"

TEHRAN = ZoneInfo("Asia/Tehran")


def emit_progress(status: str, label: str, duration_ms: float | None = None):
    """Send machine-readable lifecycle events without contaminating JSON stdout."""
    event = {"status": status, "label": label}
    if duration_ms is not None:
        event["durationMs"] = round(duration_ms, 2)
    print(f"QG_PROGRESS:{json.dumps(event, separators=(',', ':'))}", file=sys.stderr, flush=True)


def timed(timings: dict[str, float], label: str, work):
    """Measure an existing pipeline phase without changing its inputs or output."""
    started = perf_counter()
    emit_progress("started", label)
    try:
        return work()
    finally:
        duration_ms = (perf_counter() - started) * 1000
        timings[label] = timings.get(label, 0.0) + duration_ms
        emit_progress("completed", label, duration_ms)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load reaction engine: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_engine(path: Path):
    return load_module("reaction_engine", path)


_local_dt_cache: dict[int, datetime] = {}


def local_datetime(epoch: int) -> datetime:
    cached = _local_dt_cache.get(epoch)
    if cached is not None:
        return cached
    result = datetime.fromtimestamp(epoch, TEHRAN).replace(tzinfo=None)
    _local_dt_cache[epoch] = result
    return result


_epoch_cache: dict[datetime, int] = {}


def epoch(local: datetime) -> int:
    cached = _epoch_cache.get(local)
    if cached is not None:
        return cached
    result = int(local.replace(tzinfo=TEHRAN).timestamp())
    _epoch_cache[local] = result
    return result


_display_epoch_cache: dict[str, int] = {}


def display_epoch(value: str) -> int:
    """Convert an engine display timestamp once per pipeline process."""
    cached = _display_epoch_cache.get(value)
    if cached is not None:
        return cached
    result = epoch(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
    _display_epoch_cache[value] = result
    return result


def build_candle_buckets(rows: list[dict], timeframe: int):
    """Normalize raw rows once, preserving lower and selected-timeframe buckets."""
    second_buckets: list[dict] = []
    current_second = None
    buckets: list[dict] = []
    current = None
    to_decimal = as_decimal
    decimal_cache: dict[tuple[type, object], Decimal] = {}

    def cached_decimal(value: object) -> Decimal:
        # Raw prices repeat heavily. Cache by both type and value so values
        # such as ``10`` and ``10.0`` retain their exact string-normalized
        # Decimal representation instead of being conflated by Python's
        # numeric equality rules.
        key = (type(value), value)
        try:
            return decimal_cache[key]
        except KeyError:
            normalized = to_decimal(value)
            decimal_cache[key] = normalized
            return normalized

    for row in rows:
        timestamp = int(row["time"])
        o = cached_decimal(row["open"])
        high = cached_decimal(row["high"])
        low = cached_decimal(row["low"])
        close = cached_decimal(row["close"])
        if current_second is None or current_second["time"] != timestamp:
            current_second = {
                "time": timestamp,
                "open": o,
                "high": high,
                "low": low,
                "close": close,
            }
            second_buckets.append(current_second)
        else:
            current_second["high"] = max(current_second["high"], high)
            current_second["low"] = min(current_second["low"], low)
            current_second["close"] = close
        bucket_time = timestamp if timeframe == 1 else timestamp // timeframe * timeframe
        if current is None or current["time"] != bucket_time:
            current = {
                "time": bucket_time,
                "open": o,
                "high": high,
                "low": low,
                "close": close,
            }
            buckets.append(current)
        else:
            current["high"] = max(current["high"], high)
            current["low"] = min(current["low"], low)
            current["close"] = close
    return second_buckets, buckets


def build_candle_objects(engine, buckets: list[dict]):
    """Create maintained engine candles from already-normalized buckets."""
    candles = []
    append = candles.append
    candle_type = engine.Candle
    classify = engine.classify_candle_color
    local = local_datetime
    fmt = _DTFMT.format
    for index, item in enumerate(buckets):
        stamp = local(item["time"])
        append(candle_type(
            index=index,
            timestamp=stamp,
            display_time=fmt(
                stamp.year,
                stamp.month,
                stamp.day,
                stamp.hour,
                stamp.minute,
                stamp.second,
            ),
            tag=classify(item["open"], item["close"]),
            open=item["open"],
            high=item["high"],
            low=item["low"],
            close=item["close"],
        ))
    return candles


def _index_selected(index: object, start_index: int | None, end_index: int | None) -> bool:
    return (
        start_index is None
        or end_index is None
        or start_index <= int(index) <= end_index
    )


def serialize(result, start_index=None, end_index=None, reaction_transform=None):

    resets = [{
        "index": item.index,
        "time": display_epoch(item.display_time),
        "secondTime": (
            display_epoch(item.second_time)
            if item.second_time is not None
            else None
        ),
        "brokenLevel": str(item.broken_level),
        "fromFirstIndex": item.from_first_idx,
    } for item in result.resets if _index_selected(item.index, start_index, end_index)]
    reactions = []
    for item in result.reactions:
        if not _index_selected(item.first_idx, start_index, end_index):
            continue
        public_item = reaction_transform(item) if reaction_transform is not None else item
        reactions.append({
            "firstIndex": public_item.first_idx,
            "firstTime": display_epoch(public_item.first_time),
            "boxTopSourceIndex": public_item.box_top_source_idx,
            "boxTopSourceTime": display_epoch(public_item.box_top_source_time),
            "boxTop": str(public_item.box_top),
            "boxBottomSourceIndex": public_item.box_bottom_source_idx,
            "boxBottomSourceTime": display_epoch(public_item.box_bottom_source_time),
            "boxBottom": str(public_item.box_bottom),
            "breakIndex": public_item.break_idx,
            "breakTime": display_epoch(public_item.break_time),
            # Keep the exact lower-timeframe confirmation available to the
            # presentation serializer while preserving the legacy breakTime.
            "breakEventTime": (
                epoch(public_item.behavior_confirmation_time)
                if getattr(public_item, "behavior_confirmation_time", None)
                is not None
                else display_epoch(public_item.break_time)
            ),
            "mode": public_item.mode,
        })
    return reactions, resets


def serialize_blue_lines(items, start_index=None, end_index=None):
    return [{
        "direction": item.direction,
        "kind": item.kind,
        "reactionNumber": item.reaction_number,
        "previousStrikeCount": item.previous_strike_count,
        "strikeCount": item.strike_count,
        "fibonacciLevel": str(item.fibonacci_level) if item.fibonacci_level is not None else None,
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "sourceExtreme": str(item.source_extreme),
        "brokenLevel": str(item.broken_level) if item.broken_level is not None else None,
        "linePrice": str(item.line_price),
        "startTime": epoch(item.start_time),
        "endTime": epoch(item.end_time),
    } for item in items if _index_selected(
        getattr(item, "source_index"), start_index, end_index
    )]


def serialize_a_zones(items):
    return [{
        "direction": item.direction,
        "blue1Ordinal": item.blue_1_ordinal,
        "blue2Ordinal": item.blue_2_ordinal,
        "blue1SourceTime": epoch(item.blue_1_source_time),
        "blue2SourceTime": epoch(item.blue_2_source_time),
        "blue1StopTime": epoch(item.blue_1_stop_time),
        "blue2StopTime": epoch(item.blue_2_stop_time),
        "blue1StopLevel": str(item.blue_1_stop_level),
        "blue2StopLevel": str(item.blue_2_stop_level),
        "continuationLevel": str(item.continuation_level),
        "continuationSourceIndex": item.continuation_source_index,
        "continuationSourceTime": epoch(item.continuation_source_time),
        "triggerIndex": item.trigger_index,
        "triggerTime": epoch(item.trigger_time),
        "triggerEventTime": epoch(item.trigger_event_time),
        "reactionNumber": item.reaction_number,
        "reactionFirstTime": epoch(item.reaction_first_time),
        "reactionBreakTime": epoch(item.reaction_break_time),
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "calculationValid": True,
    } for item in items]


def serialize_s_zones(items):
    return [{
        "direction": item.direction,
        "color": item.color,
        "formationType": item.formation_type,
        "aOrdinal": item.a_ordinal,
        "aSourceIndex": item.a_source_index,
        "aSourceTime": epoch(item.a_source_time),
        "aPrice": str(item.a_price),
        "aStopIndex": item.a_stop_index,
        "aStopTime": epoch(item.a_stop_time),
        "aStopEventTime": epoch(item.a_stop_event_time),
        "orderDirection": item.order_direction,
        "orderReactionNumber": item.order_reaction_number,
        "orderMode": item.order_mode,
        "orderFirstIndex": item.order_first_index,
        "orderFirstTime": (
            epoch(item.order_first_time) if item.order_first_time is not None else None
        ),
        "orderBreakIndex": item.order_break_index,
        "orderBreakTime": (
            epoch(item.order_break_time) if item.order_break_time is not None else None
        ),
        "orderConfirmationTime": (
            epoch(item.order_confirmation_time)
            if item.order_confirmation_time is not None
            else None
        ),
        "orderBoxTop": str(item.order_box_top) if item.order_box_top is not None else None,
        "orderBoxTopSourceIndex": item.order_box_top_source_index,
        "orderBoxTopSourceTime": (
            epoch(item.order_box_top_source_time)
            if item.order_box_top_source_time is not None
            else None
        ),
        "orderBoxBottom": (
            str(item.order_box_bottom) if item.order_box_bottom is not None else None
        ),
        "orderBoxBottomSourceIndex": item.order_box_bottom_source_index,
        "orderBoxBottomSourceTime": (
            epoch(item.order_box_bottom_source_time)
            if item.order_box_bottom_source_time is not None
            else None
        ),
        "orderStopLevel": (
            str(item.order_stop_level) if item.order_stop_level is not None else None
        ),
        "orderStopSourceIndex": item.order_stop_source_index,
        "orderStopSourceTime": (
            epoch(item.order_stop_source_time)
            if item.order_stop_source_time is not None
            else None
        ),
        "resetReactionNumber": item.reset_reaction_number,
        "resetTime": epoch(item.reset_time) if item.reset_time is not None else None,
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "decisionIndex": item.decision_index,
        "decisionTime": epoch(item.decision_time),
        "decisionEventTime": epoch(item.decision_event_time),
        "calculationValid": True,
    } for item in items]


def serialize_e_zones(items):
    return [{
        "direction": item.direction,
        "family": item.family,
        "number": item.number,
        "parentType": item.parent_type,
        "parentSourceIndex": item.parent_source_index,
        "parentSourceTime": epoch(item.parent_source_time),
        "parentPrice": str(item.parent_price),
        "parentStopIndex": item.parent_stop_index,
        "parentStopTime": epoch(item.parent_stop_time),
        "parentStopEventTime": epoch(item.parent_stop_event_time),
        "orderDirection": item.order_direction,
        "orderReactionNumber": item.order_reaction_number,
        "orderMode": item.order_mode,
        "orderCauses": list(item.order_causes),
        "orderParentStopCauseTime": (
            epoch(item.order_parent_stop_cause_time)
            if item.order_parent_stop_cause_time is not None else None
        ),
        "orderResetLegResetTime": (
            epoch(item.order_reset_leg_reset_time)
            if item.order_reset_leg_reset_time is not None else None
        ),
        "orderResetLegBreakTime": (
            epoch(item.order_reset_leg_break_time)
            if item.order_reset_leg_break_time is not None else None
        ),
        "orderFirstIndex": item.order_first_index,
        "orderFirstTime": epoch(item.order_first_time),
        "orderBreakIndex": item.order_break_index,
        "orderBreakTime": epoch(item.order_break_time),
        "orderConfirmationTime": epoch(item.order_confirmation_time),
        "orderBoxTop": str(item.order_box_top),
        "orderBoxTopSourceIndex": item.order_box_top_source_index,
        "orderBoxTopSourceTime": epoch(item.order_box_top_source_time),
        "orderBoxBottom": str(item.order_box_bottom),
        "orderBoxBottomSourceIndex": item.order_box_bottom_source_index,
        "orderBoxBottomSourceTime": epoch(item.order_box_bottom_source_time),
        "orderStopLevel": str(item.order_stop_level),
        "orderStopSourceIndex": item.order_stop_source_index,
        "orderStopSourceTime": epoch(item.order_stop_source_time),
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "decisionIndex": item.decision_index,
        "decisionTime": epoch(item.decision_time),
        "decisionEventTime": epoch(item.decision_event_time),
    } for item in items]


def serialize_stopalls(items):
    return [{
        "direction": item.direction,
        "number": item.number,
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "decisionIndex": item.decision_index,
        "decisionTime": epoch(item.decision_time),
        "decisionEventTime": epoch(item.decision_event_time),
        "gateType": item.gate_type,
        "gateEventTime": epoch(item.gate_event_time),
        "stoppedBehaviorType": item.stopped_behavior_type,
        "stoppedBehaviorKey": item.stopped_behavior_key,
        "stoppedBehaviorCount": item.stopped_behavior_count,
        "underlyingEFamily": item.underlying_e_family,
        "underlyingENumber": item.underlying_e_number,
        "orderDirection": item.order_direction,
        "orderReactionNumber": item.order_reaction_number,
        "orderMode": item.order_mode,
        "orderCauses": list(item.order_causes),
        "orderParentStopCauseTime": (
            epoch(item.order_parent_stop_cause_time)
            if item.order_parent_stop_cause_time is not None else None
        ),
        "orderResetLegResetTime": (
            epoch(item.order_reset_leg_reset_time)
            if item.order_reset_leg_reset_time is not None else None
        ),
        "orderResetLegBreakTime": (
            epoch(item.order_reset_leg_break_time)
            if item.order_reset_leg_break_time is not None else None
        ),
        "orderFirstIndex": item.order_first_index,
        "orderFirstTime": (
            epoch(item.order_first_time) if item.order_first_time is not None else None
        ),
        "orderBreakIndex": item.order_break_index,
        "orderBreakTime": (
            epoch(item.order_break_time) if item.order_break_time is not None else None
        ),
        "orderConfirmationTime": (
            epoch(item.order_confirmation_time)
            if item.order_confirmation_time is not None else None
        ),
        "orderBoxTop": (
            str(item.order_box_top) if item.order_box_top is not None else None
        ),
        "orderBoxTopSourceIndex": item.order_box_top_source_index,
        "orderBoxTopSourceTime": (
            epoch(item.order_box_top_source_time)
            if item.order_box_top_source_time is not None else None
        ),
        "orderBoxBottom": (
            str(item.order_box_bottom) if item.order_box_bottom is not None else None
        ),
        "orderBoxBottomSourceIndex": item.order_box_bottom_source_index,
        "orderBoxBottomSourceTime": (
            epoch(item.order_box_bottom_source_time)
            if item.order_box_bottom_source_time is not None else None
        ),
        "orderStopLevel": (
            str(item.order_stop_level) if item.order_stop_level is not None else None
        ),
        "orderStopSourceIndex": item.order_stop_source_index,
        "orderStopSourceTime": (
            epoch(item.order_stop_source_time)
            if item.order_stop_source_time is not None else None
        ),
        "stopIndex": item.stop_index,
        "stopTime": epoch(item.stop_time) if item.stop_time else None,
        "stopEventTime": epoch(item.stop_event_time) if item.stop_event_time else None,
    } for item in items]


def serialize_order_audit(prepared_items, detector):
    """Serialize already-resolved Order Audit identities without business filtering."""
    output = []
    for prepared in prepared_items:
        entry = prepared["entry"]
        reaction = prepared["reaction"]
        crossed = prepared["crossed"]
        first_index = int(getattr(reaction, "first_idx"))
        causes = []
        for cause in prepared["causes"]:
            if cause["kind"] == "parent-stop":
                causes.append({
                    "kind": cause["kind"],
                    "parentType": cause["parentType"],
                    "parentFamily": cause["parentFamily"],
                    "eventTime": epoch(cause["eventTime"]),
                    "parentSourceTime": epoch(cause["parentSourceTime"]),
                })
            else:
                causes.append({
                    "kind": cause["kind"],
                    "resetTime": epoch(cause["resetTime"]),
                    "boundaryBreakTime": epoch(cause["boundaryBreakTime"]),
                })
        output.append({
            "direction": detector.order_direction,
            "reactionNumber": int(
                getattr(reaction, "behavior_public_number", None)
                or entry["reaction_number"]
            ),
            "reactionMode": str(getattr(reaction, "mode")),
            "firstIndex": first_index,
            "firstTime": epoch(detector.candles[first_index].timestamp),
            "boxTopSourceIndex": int(getattr(reaction, "box_top_source_idx")),
            "boxTopSourceTime": display_epoch(getattr(reaction, "box_top_source_time")),
            "boxTop": str(getattr(reaction, "box_top")),
            "boxBottomSourceIndex": int(getattr(reaction, "box_bottom_source_idx")),
            "boxBottomSourceTime": display_epoch(getattr(reaction, "box_bottom_source_time")),
            "boxBottom": str(getattr(reaction, "box_bottom")),
            "breakIndex": int(getattr(reaction, "break_idx")),
            "breakTime": epoch(
                detector.candles[int(getattr(reaction, "break_idx"))].timestamp
            ),
            "confirmationTime": epoch(entry["confirmation_time"]),
            "stopLevel": str(entry["stop_level"]),
            "stopSourceIndex": entry["stop_source_index"],
            "stopSourceTime": epoch(entry["stop_source_time"]),
            "stopHitIndex": crossed[0] if crossed is not None else None,
            "stopHitTime": epoch(crossed[1]) if crossed is not None else None,
            "stopHitEventTime": epoch(crossed[2]) if crossed is not None else None,
            "causes": causes,
        })
    return sorted(output, key=lambda item: (item["firstTime"], item["breakTime"]))


def _report_time(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return _DTFMT.format(value.year, value.month, value.day, value.hour, value.minute, value.second)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        stamp = local_datetime(int(value))
        return _DTFMT.format(stamp.year, stamp.month, stamp.day, stamp.hour, stamp.minute, stamp.second)
    text = str(value)
    return text if text else None


def _report_direction(value):
    return {"bullish": "Bullish", "bearish": "Bearish"}.get(
        str(value).lower(), value
    )


def _report_first_candle(direction):
    return {"type": "First Red" if direction == "Bullish" else "First Green"}


def _report_mode(value):
    return {"A": "Leg Start", "B": "Normal"}.get(str(value), value)


def _report_kind(value):
    return {
        "scale": "Scale",
        "reset": "Reset",
        "simple": "Simple",
        "advanced": "Advanced",
        "type3": "Type-3",
    }.get(str(value), value)


def _report_order_formation(causes=None, mode=None):
    """Expose the engine's Order mode without deriving a new order type."""
    normalized = str(mode or "").strip().upper()
    kinds = {
        str(item.get("kind")) if isinstance(item, dict) else str(item)
        for item in causes or []
    }
    if {"parent-stop", "reset-leg"}.issubset(kinds):
        return "Order_A | Order_B"
    if normalized in {"A", "B"}:
        return f"Order_{normalized}"
    return "Order_A" if "parent-stop" in kinds else "Order_B"


def _report_family(value):
    return {"blue": "Blue", "red": "Red"}.get(str(value).lower(), value)


def _report_trigger(value):
    return {
        "sequence-group-stop": "Behavior Group",
        "opposite-s-group-stop": "Behavior Group",
        "stopall-stop": "Previous StopAll",
    }.get(str(value), _report_kind(value))


def _report_behavior_key(value):
    text = str(value or "")
    if text.startswith("StopAll"):
        return {"type": "StopAll", "number": text.split()[0]}
    if text.startswith("E"):
        parts = text.split()
        return {
            "type": "E",
            "number": parts[0],
            "color": _report_family(parts[1]) if len(parts) > 1 else None,
        }
    if text.startswith("S"):
        parts = text.split()
        return {
            "type": "S Blue" if len(parts) > 1 and parts[1].lower() == "blue" else "S Red",
            "color": _report_family(parts[1]) if len(parts) > 1 else None,
        }
    return {"type": text} if text else None


def _report_clean(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            item = _report_clean(item)
            if item is None or item == {} or item == []:
                continue
            cleaned[key] = item
        return cleaned
    if isinstance(value, list):
        return [item for item in (_report_clean(item) for item in value)
                if item is not None and item != {} and item != []]
    return value


def _report_point(price, time):
    stamp = _report_time(time)
    if stamp is None or price is None:
        return None
    return {"time": stamp, "price": str(price)}


def _report_reaction(reaction, direction):
    readable = _report_direction(direction)
    breakout_price = reaction.get("boxTop") if str(direction).lower() == "bullish" else reaction.get("boxBottom")
    return _report_clean({
        "type": "Reaction",
        "direction": readable,
        "mode": _report_mode(reaction.get("mode")),
        "firstCandle": {
            **_report_first_candle(readable),
            "time": _report_time(reaction.get("firstTime")),
        },
        "structure": {
            "boxTop": _report_point(
                reaction.get("boxTop"), reaction.get("boxTopSourceTime")
            ),
            "boxBottom": _report_point(
                reaction.get("boxBottom"), reaction.get("boxBottomSourceTime")
            ),
            "breakout": _report_point(
                breakout_price, reaction.get("breakEventTime") or reaction.get("breakTime")
            ),
        },
    })


def _report_reaction_ref(reaction, direction):
    if not reaction:
        return None
    breakout_price = reaction.get("boxTop") if str(direction).lower() == "bullish" else reaction.get("boxBottom")
    return _report_clean({
        "mode": _report_mode(reaction.get("mode")),
        "firstCandle": {
            **_report_first_candle(_report_direction(direction)),
            "time": _report_time(reaction.get("firstTime")),
        },
        "structure": {
            "boxTop": _report_point(
                reaction.get("boxTop"), reaction.get("boxTopSourceTime")
            ),
            "boxBottom": _report_point(
                reaction.get("boxBottom"), reaction.get("boxBottomSourceTime")
            ),
            "breakout": _report_point(
                breakout_price, reaction.get("breakEventTime") or reaction.get("breakTime")
            ),
        },
    })


def _report_order_provenance(causes, details_by_ref):
    parents = []
    extra = []
    for cause in causes or []:
        if not isinstance(cause, dict):
            continue
        kind = cause.get("kind")
        if kind == "parent-stop":
            parent_type = str(cause.get("parentType") or "")
            ref_kind = (
                "A" if parent_type == "A" else
                "S" if parent_type == "S" else
                "E" if parent_type == "E" or parent_type.startswith("E") else
                "StopAll" if parent_type == "StopAll" or parent_type.startswith("StopAll") else
                parent_type
            )
            parent_time = _report_time(cause.get("parentSourceTime"))
            source = details_by_ref.get((ref_kind, parent_time)) if details_by_ref else None
            parents.append(_report_clean({
                **_report_parent_summary(parent_type, parent_time, source, cause.get("eventTime")),
                "orderRelation": "Created This Order",
            }))
        elif kind == "carried-live":
            extra.append({"type": "Existing Active Order"})
        elif kind == "reset-leg":
            extra.append(_report_clean({
                "type": "Reset Structure",
                "resetAt": {"time": _report_time(cause.get("resetTime"))},
                "brokenAt": {"time": _report_time(cause.get("boundaryBreakTime"))},
            }))
    return parents, extra


def _report_order_from_row(
    row, audits_by_identity, direction, parents=None, extra_reasons=None,
    details_by_ref=None,
):
    first = row.get("orderFirstTime")
    break_time = row.get("orderBreakTime")
    if first is None and break_time is None:
        return None
    identity = (_report_time(first), _report_time(break_time))
    audit = audits_by_identity.get(identity)
    audit_causes = (audit or {}).get("causes") or []
    row_causes = row.get("orderCauses") or []
    causes = [*audit_causes]
    for cause in row_causes:
        if cause not in causes:
            causes.append(cause)
    derived_parents, derived_extra = _report_order_provenance(
        audit_causes, details_by_ref
    )
    if parents is None:
        parents = derived_parents
    if extra_reasons is None:
        extra_reasons = derived_extra
    relations = []
    for cause in causes:
        kind = cause.get("kind") if isinstance(cause, dict) else str(cause)
        relation = {
            "parent-stop": "Created By Parent Stop",
            "carried-live": "Existing Active Order",
            "reset-leg": "Reset Structure",
        }.get(kind)
        if relation and relation not in relations:
            relations.append(relation)
    order = {
        "type": "Order Audit",
        "formation": _report_order_formation(
            causes, row.get("orderMode") or (audit or {}).get("reactionMode")
        ),
        "direction": _report_direction(row.get("orderDirection") or direction),
        "firstCandle": {
            **_report_first_candle(
                _report_direction(row.get("orderDirection") or direction)
            ),
            "time": _report_time(first),
        },
        "structure": {
            "boxTop": _report_point(
                row.get("orderBoxTop"), row.get("orderBoxTopSourceTime")
            ),
            "boxBottom": _report_point(
                row.get("orderBoxBottom"), row.get("orderBoxBottomSourceTime")
            ),
            "breakout": _report_point(
                row.get("orderBoxTop")
                if str(row.get("orderDirection") or direction).lower() == "bullish"
                else row.get("orderBoxBottom"),
                row.get("orderConfirmationTime") or (audit or {}).get("confirmationTime") or break_time,
            ),
        },
        "stop": _report_point(
            row.get("orderStopLevel"),
            row.get("orderStopSourceTime"),
        ),
    }
    if parents:
        order["parents"] = parents
    if relations:
        order["relation"] = relations if len(relations) > 1 else relations[0]
    if extra_reasons:
        order["extraReasons"] = extra_reasons
    return _report_clean(order)


def _report_blue_detail(line, raw_line=None, stop=None, direction="bullish"):
    item = raw_line or {}
    kind = getattr(line, "kind", None) if line is not None else item.get("kind")
    source_time = (
        getattr(line, "source_time", None) if line is not None
        else item.get("sourceTime")
    )
    source_extreme = (
        getattr(line, "source_extreme", None) if line is not None
        else item.get("sourceExtreme")
    )
    line_price = (
        getattr(line, "line_price", None) if line is not None
        else item.get("linePrice")
    )
    result = {
        "kind": _report_kind(kind),
        "formedAt": {
            "time": _report_time(source_time),
            "linePrice": str(line_price) if line_price is not None else None,
            "stopPrice": str(source_extreme) if source_extreme is not None else None,
        },
    }
    if stop:
        result["stoppedAt"] = _report_clean({
            "time": _report_time(stop.get("time")),
            "price": stop.get("price"),
        })
    if str(kind) == "scale":
        result["scale"] = _report_clean({
            "fibonacciPrice": (
                str(getattr(line, "fibonacci_level", None))
                if line is not None and getattr(line, "fibonacci_level", None) is not None
                else item.get("fibonacciLevel")
            ),
            "previousStrikes": (
                getattr(line, "previous_strike_count", None)
                if line is not None else item.get("previousStrikeCount")
            ),
            "currentStrikes": (
                getattr(line, "strike_count", None)
                if line is not None else item.get("strikeCount")
            ),
        })
    return _report_clean(result)


def _report_category(group, row, direction):
    readable = _report_direction(direction)
    if group == "reactions":
        return {"key": f"reaction:{str(direction).lower()}", "family": "Reaction",
                "label": f"{readable} Reaction"}
    if group == "resets":
        return {"key": "reset", "family": "Reset", "label": "Reset"}
    if group == "blueLines":
        kind = str(row.get("kind") or "").lower()
        label = _report_kind(kind) or "Blue Line"
        return {"key": f"blue:{kind or 'unknown'}", "family": "Blue Line",
                "label": f"Blue Line / {label}"}
    if group == "aZones":
        formation = "double-stop" if row.get("formation") == "Double Stop" else "normal"
        return {"key": f"a:{formation}", "family": "A",
                "label": f"A / {'Double Stop' if formation == 'double-stop' else 'Normal'}"}
    if group == "sZones":
        color = str(row.get("color") or "").lower()
        if color == "red":
            return {"key": "s:red", "family": "S Red", "label": "S Red"}
        formation = str(row.get("formationType") or "unknown").lower()
        return {"key": f"s:blue:{formation}", "family": "S Blue",
                "label": f"S Blue / {_report_kind(formation)}"}
    if group == "eZones":
        family = str(row.get("family") or "").lower()
        number = row.get("number")
        family_label = _report_family(family)
        return {"key": f"e:{family}:{number}", "family": f"E {family_label}",
                "label": f"E {family_label} / E{number}"}
    if group == "stopAlls":
        number = row.get("number")
        return {"key": f"stopall:{number}", "family": "StopAll",
                "label": f"StopAll{number}"}
    if group == "orderAudit":
        formation = _report_order_formation(
            row.get("causes"), row.get("reactionMode")
        )
        key_formation = formation.lower().replace(" | ", "|")
        return {"key": f"order:{key_formation}", "family": "Order Audit",
                "label": formation}
    return {"key": group, "family": group, "label": group}


def _report_parent_summary(kind, source_time, source, stop_time=None):
    source_type = source.get("type") if source else None
    result = {"type": source_type or ("E" if str(kind).startswith("E") else kind)}
    if source:
        result.update({
            key: source[key] for key in (
                "formation", "color", "number", "price", "formedAt"
            ) if key in source
        })
    if stop_time is not None:
        stopped = {"time": _report_time(stop_time)}
        formed = source.get("formedAt") if source else None
        if isinstance(formed, dict) and formed.get("price") is not None:
            stopped["price"] = str(formed["price"])
        result["stoppedAt"] = _report_clean(stopped)
    return _report_clean(result)


def serialize_human_report(direction, serialized, state, visibility):
    """Build a presentation-only report from accepted, serialized state."""
    readable = _report_direction(direction)
    reactions = serialized["reactions"]
    resets = serialized["resets"]
    blue_rows = serialized["blueLines"]
    a_rows = serialized["aZones"]
    s_rows = serialized["sZones"]
    e_rows = serialized["eZones"]
    stop_rows = serialized["stopAlls"]
    audits = serialized["orderAudit"]
    reactions_by_first = {item.get("firstIndex"): item for item in reactions}
    reactions_by_number = {}
    serialized_by_first = {item.get("firstIndex"): item for item in reactions}
    for number, native in enumerate(
        state.results[direction].reactions, start=1
    ):
        item = serialized_by_first.get(int(getattr(native, "first_idx")))
        if item is not None:
            reactions_by_number[number] = item
    blue_rows_by_ordinal = {
        index + 1: item for index, item in enumerate(blue_rows)
    }
    full_lines = state.full_lines_by_direction.get(direction, [])
    full_lines_by_time = {
        _report_time(getattr(item, "source_time", None)): item
        for item in full_lines
    }
    audits_by_identity = {
        (_report_time(item.get("firstTime")), _report_time(item.get("breakTime"))): item
        for item in audits
    }
    a_by_time = {_report_time(item.get("sourceTime")): item for item in a_rows}
    s_by_time = {_report_time(item.get("sourceTime")): item for item in s_rows}
    e_by_ref = {
        (str(item.get("family")), item.get("number")): item for item in e_rows
    }
    e_by_time = {_report_time(item.get("sourceTime")): item for item in e_rows}
    stop_by_number = {item.get("number"): item for item in stop_rows}
    stop_by_time = {_report_time(item.get("sourceTime")): item for item in stop_rows}
    s_stop_by_time = {
        _report_time(item.get("parentSourceTime")): item
        for item in e_rows if str(item.get("parentType")) == "S"
    }
    e_stop_by_time = {
        _report_time(item.get("parentSourceTime")): item
        for item in e_rows if str(item.get("parentType")) == "E"
    }
    stopall_stop_by_number = {
        str(item.get("stoppedBehaviorKey")): item
        for item in stop_rows
        if str(item.get("stoppedBehaviorType")) == "StopAll"
    }
    report = []
    details_by_ref = {}
    created_by_ref = {}

    def add(group, index, row, details, time):
        category = _report_category(group, row, direction)
        record = {
            "id": f"{str(direction).lower()}:{group}:{index}",
            "time": _report_time(time),
            "direction": readable,
            "label": category["label"],
            "category": category,
            "details": _report_clean(details),
        }
        report.append(_report_clean(record))
        return record["details"]

    for index, row in enumerate(reactions):
        details = _report_reaction(row, direction)
        details_by_ref[("Reaction", _report_time(row.get("firstTime")))] = details
        add("reactions", index, row, details, row.get("firstTime"))

    for index, row in enumerate(resets):
        owner = reactions_by_first.get(row.get("fromFirstIndex"))
        details = {
            "type": "Reset",
            "direction": readable,
            "reset": {
                "time": _report_time(row.get("secondTime") or row.get("time")),
                "brokenPrice": str(row.get("brokenLevel"))
                if row.get("brokenLevel") is not None else None,
            },
            "reaction": _report_reaction_ref(owner, direction),
        }
        details_by_ref[("Reset", _report_time(row.get("secondTime") or row.get("time")))] = details
        add("resets", index, row, details, row.get("secondTime") or row.get("time"))

    blue_stops = {}
    for row in a_rows:
        for prefix in ("blue1", "blue2"):
            key = _report_time(row.get(f"{prefix}SourceTime"))
            blue_stops.setdefault(key, {
                "time": row.get(f"{prefix}StopTime"),
                "price": row.get(f"{prefix}StopLevel"),
            })
    for index, row in enumerate(blue_rows):
        native = next((line for line in full_lines
                       if _report_time(getattr(line, "source_time", None)) == _report_time(row.get("sourceTime"))), None)
        reaction = reactions_by_number.get(getattr(native, "reaction_number", None))
        details = {
            "type": "Blue Line",
            "direction": readable,
            "kind": _report_kind(row.get("kind")),
            **_report_blue_detail(native, row, blue_stops.get(_report_time(row.get("sourceTime"))), direction),
            "reaction": _report_reaction_ref(reaction, direction),
        }
        details_by_ref[("Blue Line", _report_time(row.get("sourceTime")))] = details
        add("blueLines", index, row, details, row.get("sourceTime"))

    for index, row in enumerate(a_rows):
        formation = "Double Stop" if any(
            int(getattr(line, "source_index", -1)) == int(row.get("sourceIndex", -2))
            and not bool(getattr(line, "calculation_valid", True))
            for line in full_lines
        ) else "Normal"
        stop = next((item for item in s_rows
                     if _report_time(item.get("aSourceTime")) == _report_time(row.get("sourceTime"))), None)
        formed_stops = []
        for ordinal, prefix in ((row.get("blue1Ordinal"), "blue1"), (row.get("blue2Ordinal"), "blue2")):
            source_time = _report_time(row.get(f"{prefix}SourceTime"))
            native = full_lines_by_time.get(source_time)
            raw_blue = next(
                (
                    item for item in blue_rows
                    if _report_time(item.get("sourceTime")) == source_time
                ),
                None,
            )
            formed_stops.append(_report_blue_detail(native, raw_blue, {
                "time": row.get(f"{prefix}StopTime"),
                "price": row.get(f"{prefix}StopLevel"),
            }, direction))
        details = {
            "type": "A",
            "direction": readable,
            "formation": formation,
            "formedAt": _report_point(row.get("price"), row.get("sourceTime")),
            "stoppedAt": _report_point(row.get("price"),
                stop.get("aStopEventTime") if stop else None),
            "formedFromStops": formed_stops,
            "continuation": _report_point(row.get("continuationLevel"), row.get("continuationSourceTime")),
            "trigger": _report_point(row.get("price"), row.get("triggerEventTime") or row.get("triggerTime")),
            "confirmationReaction": _report_reaction_ref(
                reactions_by_number.get(row.get("reactionNumber")), direction
            ),
        }
        ref = ("A", _report_time(row.get("sourceTime")))
        details_by_ref[ref] = details
        add("aZones", index, {**row, "formation": formation}, details, row.get("sourceTime"))

    for index, row in enumerate(s_rows):
        color = str(row.get("color") or "").lower()
        s_stop = s_stop_by_time.get(_report_time(row.get("sourceTime")))
        parent_a = a_by_time.get(_report_time(row.get("aSourceTime")))
        parent = {
            "type": "A",
            "formedAt": _report_point(
                parent_a.get("price") if parent_a else row.get("aPrice"),
                row.get("aSourceTime"),
            ),
            "stoppedAt": _report_point(
                parent_a.get("price") if parent_a else row.get("aPrice"),
                row.get("aStopEventTime") or row.get("aStopTime"),
            ),
        }
        details = {
            "type": "S Blue" if color == "blue" else "S Red",
            "direction": readable,
            "formation": _report_kind(row.get("formationType")) if color == "blue" else None,
            "formedAt": _report_point(row.get("price"), row.get("sourceTime")),
            "stoppedAt": _report_point(
                row.get("price"),
                s_stop.get("parentStopEventTime") if s_stop else None,
            ),
            "formedFromStop": parent,
            "formationOrder": None if str(row.get("formationType")) == "type3" else _report_order_from_row(row, audits_by_identity, direction, details_by_ref=details_by_ref),
            "nestedReaction": _report_reaction_ref(
                reactions_by_number.get(row.get("resetReactionNumber")), direction
            ) if color == "blue" and str(row.get("formationType")) == "advanced" else None,
            "reset": {
                "time": _report_time(row.get("resetTime")),
                "reaction": _report_reaction_ref(
                    reactions_by_number.get(row.get("resetReactionNumber")), direction
                ),
            } if str(row.get("formationType")) == "type3" else None,
            "decision": {"time": _report_time(row.get("decisionEventTime") or row.get("decisionTime"))},
        }
        ref = ("S", _report_time(row.get("sourceTime")))
        details_by_ref[ref] = details
        add("sZones", index, row, details, row.get("sourceTime"))

    for index, row in enumerate(e_rows):
        family = str(row.get("family") or "").lower()
        parent_type = str(row.get("parentType") or "")
        parent_ref_kind = (
            "S" if parent_type == "S" else
            "E" if parent_type == "E" or parent_type.startswith("E") else
            "StopAll" if parent_type == "StopAll" or parent_type.startswith("StopAll") else
            parent_type
        )
        parent_key = (parent_ref_kind, _report_time(row.get("parentSourceTime")))
        parent_source = details_by_ref.get(parent_key)
        parent = _report_parent_summary(
            "S Blue" if row.get("parentType") == "S" and str(row.get("parentFamily")) == "blue" else
            "S Red" if row.get("parentType") == "S" else
            f"E{row.get('number')}" if row.get("parentType") == "E" else
            str(row.get("parentType")),
            row.get("parentSourceTime"), parent_source,
            row.get("parentStopEventTime") or row.get("parentStopTime"),
        )
        details = {
            "type": "E",
            "direction": readable,
            "color": "Blue" if family == "blue" else "Red",
            "number": f"E{row.get('number')}",
            "formedAt": _report_point(row.get("price"), row.get("sourceTime")),
            "stoppedAt": _report_point(
                row.get("price"),
                e_stop_by_time.get(_report_time(row.get("sourceTime")), {}).get("parentStopEventTime"),
            ),
            "formedFromStop": parent,
            "formationOrder": _report_order_from_row(row, audits_by_identity, direction, details_by_ref=details_by_ref),
            "decision": {"time": _report_time(row.get("decisionEventTime") or row.get("decisionTime"))},
        }
        ref = ("E", _report_time(row.get("sourceTime")))
        details_by_ref[ref] = details
        add("eZones", index, row, details, row.get("sourceTime"))

    for index, row in enumerate(stop_rows):
        source_e = e_by_ref.get((str(row.get("underlyingEFamily")), row.get("underlyingENumber")))
        stopped_behavior = _report_behavior_key(row.get("stoppedBehaviorKey")) or {
            "type": row.get("stoppedBehaviorType")
        }
        stopped_behavior["count"] = row.get("stoppedBehaviorCount")
        details = {
            "type": "StopAll",
            "direction": readable,
            "number": f"StopAll{row.get('number')}",
            "formedAt": _report_point(row.get("price"), row.get("sourceTime")),
            "trigger": _report_clean({
                "type": _report_trigger(row.get("gateType")),
                "time": _report_time(row.get("gateEventTime")),
                "stopped": {
                    **stopped_behavior,
                },
            }),
            "formedFromStop": {
                "type": _report_trigger(row.get("gateType")),
                "stoppedBehavior": stopped_behavior,
            },
            "sourceE": _report_clean({
                "color": _report_family(row.get("underlyingEFamily")),
                "number": f"E{row.get('underlyingENumber')}" if row.get("underlyingENumber") is not None else None,
                "formedAt": _report_point(
                    source_e.get("price") if source_e else None,
                    source_e.get("sourceTime") if source_e else None,
                ),
            }),
            "formationOrder": _report_order_from_row(row, audits_by_identity, direction, details_by_ref=details_by_ref),
            "decision": {"time": _report_time(row.get("decisionEventTime") or row.get("decisionTime"))},
            "stoppedAt": _report_point(row.get("price"), row.get("stopEventTime") or row.get("stopTime")),
        }
        ref = ("StopAll", _report_time(row.get("sourceTime")))
        details_by_ref[ref] = details
        add("stopAlls", index, row, details, row.get("sourceTime"))

    for index, row in enumerate(audits):
        parents, extra = _report_order_provenance(
            row.get("causes"), details_by_ref
        )
        order_direction = _report_direction(row.get("direction") or direction)
        details = {
            "type": "Order Audit",
            "formation": _report_order_formation(
                row.get("causes"), row.get("reactionMode")
            ),
            "direction": order_direction,
            "firstCandle": {
                **_report_first_candle(order_direction),
                "time": _report_time(row.get("firstTime")),
            },
            "structure": {
                "boxTop": _report_point(row.get("boxTop"), row.get("boxTopSourceTime")),
                "boxBottom": _report_point(row.get("boxBottom"), row.get("boxBottomSourceTime")),
                "breakout": _report_point(
                    row.get("boxTop")
                    if str(row.get("direction") or direction).lower() == "bullish"
                    else row.get("boxBottom"),
                    row.get("confirmationTime") or row.get("breakTime"),
                ),
                "stop": _report_point(row.get("stopLevel"), row.get("stopSourceTime")),
            },
            "stoppedAt": _report_clean({
                "time": _report_time(row.get("stopHitEventTime") or row.get("stopHitTime")),
                "price": row.get("stopLevel"),
            }),
            "parents": parents,
            "extraReasons": extra,
        }
        add("orderAudit", index, row, details, row.get("firstTime"))

    for item in report:
        for cause in audits:
            for raw_cause in cause.get("causes") or []:
                if not isinstance(raw_cause, dict) or raw_cause.get("kind") != "parent-stop":
                    continue
                source_time = _report_time(raw_cause.get("parentSourceTime"))
                parent_type = str(raw_cause.get("parentType") or "")
                ref_kind = (
                    "A" if parent_type == "A" else
                    "S" if parent_type == "S" else
                    "E" if parent_type == "E" or parent_type.startswith("E") else
                    "StopAll" if parent_type == "StopAll" or parent_type.startswith("StopAll") else
                    parent_type
                )
                if (ref_kind, source_time) in details_by_ref:
                    identity = (
                        _report_time(cause.get("firstTime")),
                        _report_time(cause.get("breakTime")),
                    )
                    existing = created_by_ref.setdefault((ref_kind, source_time), [])
                    if identity not in existing:
                        existing.append(identity)

    for item in report:
        group = item["category"]["family"]
        ref_kind = {"A": "A", "S Blue": "S", "S Red": "S", "E Blue": "E", "E Red": "E", "StopAll": "StopAll"}.get(group)
        if not ref_kind:
            continue
        source_time = _report_time(item.get("time"))
        created = []
        for identity in created_by_ref.get((ref_kind, source_time), []):
            audit = audits_by_identity.get(identity)
            if audit:
                created.append(_report_order_from_row({
                    "orderFirstTime": audit.get("firstTime"),
                    "orderBreakTime": audit.get("breakTime"),
                    "orderDirection": audit.get("direction"),
                    "orderBoxTop": audit.get("boxTop"),
                    "orderBoxTopSourceTime": audit.get("boxTopSourceTime"),
                    "orderBoxBottom": audit.get("boxBottom"),
                    "orderBoxBottomSourceTime": audit.get("boxBottomSourceTime"),
                    "orderStopLevel": audit.get("stopLevel"),
                    "orderStopSourceTime": audit.get("stopSourceTime"),
                    "orderCauses": audit.get("causes"),
                }, audits_by_identity, direction))
        if created:
            item["details"]["createdOrder"] = created[0] if len(created) == 1 else created

    return sorted(report, key=lambda item: (item.get("time") or "", item.get("id") or ""))


@dataclass(frozen=True, slots=True)
class EngineBundle:
    reaction: object
    blue_line: object
    a_zone: object
    s_zone: object
    e_zone: object | None
    lifecycle: object | None


@dataclass(frozen=True, slots=True)
class MarketContext:
    seconds: list[object]
    candles: list[object]
    lower_index: object
    chronology: object
    start_index: int
    end_index: int


def parse_arguments(argv=None):
    """Parse and validate the production pipeline command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reaction-engine",
        "--engine",
        dest="reaction_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--blue-line-engine",
        "--blue-engine",
        dest="blue_line_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--a-zone-engine",
        "--a-engine",
        dest="a_zone_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--s-zone-engine",
        "--s-engine",
        dest="s_zone_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--e-zone-engine",
        "--e-engine",
        dest="e_zone_engine",
        type=Path,
        required=False,
    )
    parser.add_argument(
        "--lifecycle-engine",
        "--stopall-engine",
        dest="lifecycle_engine",
        type=Path,
        required=False,
    )
    parser.add_argument(
        "--blue-lines", choices=("enabled", "disabled"), default="enabled"
    )
    parser.add_argument(
        "--a-zones", choices=("enabled", "disabled"), default="enabled"
    )
    parser.add_argument(
        "--s-zones", choices=("enabled", "disabled"), default="enabled"
    )
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--timeframe", type=int, required=True)
    parser.add_argument("--from-time", type=int, required=True)
    parser.add_argument("--to-time", type=int, required=True)
    parser.add_argument(
        "--direction", choices=("bullish", "bearish", "both"), required=True
    )
    args = parser.parse_args(argv)
    if args.timeframe < 1:
        raise ValueError("Timeframe must be at least one second.")
    return args


def load_engines(args, timings: dict[str, float]) -> EngineBundle:
    """Load every configured calculation engine exactly once."""
    reaction = timed(
        timings, "Load Reaction engine", lambda: load_engine(args.reaction_engine)
    )
    blue_line = timed(
        timings,
        "Load Blue Line engine",
        lambda: load_module("blue_line_detector", args.blue_line_engine),
    )
    a_zone = timed(
        timings, "Load A engine", lambda: load_module("a_zone_detector", args.a_zone_engine)
    )
    s_zone = timed(
        timings, "Load S engine", lambda: load_module("s_zone_detector", args.s_zone_engine)
    )
    e_zone = (
        timed(
            timings,
            "Load E engine",
            lambda: load_module("e_zone_detector", args.e_zone_engine),
        )
        if args.e_zone_engine is not None
        else None
    )
    lifecycle_path = args.lifecycle_engine or (_PIPELINE_DIR / "lifecycle_engine.py")
    lifecycle = timed(
        timings,
        "Load Lifecycle engine",
        lambda: load_module("lifecycle_engine", lifecycle_path),
    )
    return EngineBundle(reaction, blue_line, a_zone, s_zone, e_zone, lifecycle)


def prepare_market_context(
    args, engines: EngineBundle, timings: dict[str, float]
) -> MarketContext:
    """Read, isolate, normalize and index the selected raw-data range."""
    source_bytes = timed(
        timings, "Read source file", lambda: args.data.read_bytes()
    )
    # Match the former ``utf-8-sig`` behavior without decoding the entire raw
    # payload to a Python string before orjson parses it.
    source_bytes = source_bytes.removeprefix(b"\xef\xbb\xbf")
    source_rows = timed(
        timings, "Parse source JSON", lambda: orjson.loads(source_bytes)
    )
    # The requested range is an execution boundary, not just a presentation
    # window.  Excluding both sides before bucket construction prevents a
    # reaction, reset, or dependent zone outside the selected interval from
    # changing the result.  Higher-timeframe end buckets include their full
    # source interval so the selected chart candle remains complete.
    source_from = int(args.from_time)
    source_to = int(args.to_time) if args.timeframe == 1 else int(args.to_time) + int(args.timeframe) - 1
    rows = timed(
        timings,
        "Filter raw range",
        lambda: [row for row in source_rows if source_from <= int(row["time"]) <= source_to],
    )
    if not rows:
        raise ValueError("The selected range contains no raw candles.")

    second_buckets, timeframe_buckets = timed(
        timings,
        "Normalize raw candles",
        lambda: build_candle_buckets(rows, args.timeframe),
    )
    seconds = timed(
        timings,
        "Build lower candle views",
        lambda: build_candle_objects(engines.reaction, second_buckets),
    )
    lower_index = engines.reaction.shared_lower_timeframe_index(seconds)
    candles = (
        seconds
        if args.timeframe == 1
        else timed(
            timings,
            "Build timeframe candle views",
            lambda: build_candle_objects(engines.reaction, timeframe_buckets),
        )
    )
    chronology = engines.reaction.MarketChronology(
        candles, seconds, args.timeframe, lower_index
    )

    # Resolve the visible main-candle range inside the prefix calculation.
    # Bucket boundaries are epoch-aligned exactly as ``build_candle_buckets``
    # constructs them, which also keeps full-run source indexes/ordinals
    # stable in a short-window request.
    main_bucket_times = [int(item["time"]) for item in timeframe_buckets]
    requested_start_bucket = (
        args.from_time
        if args.timeframe == 1
        else args.from_time // args.timeframe * args.timeframe
    )
    requested_end_bucket = (
        args.to_time
        if args.timeframe == 1
        else args.to_time // args.timeframe * args.timeframe
    )
    start_index = bisect_left(main_bucket_times, requested_start_bucket)
    end_index = bisect_left(main_bucket_times, requested_end_bucket + args.timeframe) - 1
    if start_index >= len(candles) or end_index < start_index:
        raise ValueError("The selected range contains no timeframe candles.")
    end_index = min(end_index, len(candles) - 1)

    return MarketContext(
        seconds=seconds,
        candles=candles,
        lower_index=lower_index,
        chronology=chronology,
        start_index=start_index,
        end_index=end_index,
    )

@dataclass(slots=True)
class PipelineState:
    """Mutable calculation state shared across direction serialization passes."""

    directions: tuple[str, ...]
    results: dict[str, object]
    reusable_full_context: bool
    initial_order_geometry: dict[str, object]
    internal_reaction_identities: dict[str, set[tuple[int, int]]]
    full_e_zones: dict[str, list[object]]
    full_e_detectors: dict[str, object]
    full_s_detectors: dict[str, object]
    full_lines_by_direction: dict[str, list[object]]
    full_a_by_direction: dict[str, list[object]]
    invalid_a_identities_by_direction: dict[str, set[tuple[datetime, int]]]
    invalid_s_identities_by_direction: dict[str, set[tuple[datetime, int]]]
    full_s_by_direction: dict[str, list[object]]
    full_s_candidates_by_direction: dict[str, list[object]]


@dataclass(slots=True)
class FullDirectionState:
    """Authoritative full-range behavior state for one trend direction."""

    e_zones: list[object]
    e_detector: object
    s_detector: object
    blue_lines: list[object]
    a_zones: list[object]
    invalid_a_identities: set[tuple[datetime, int]]
    invalid_s_identities: set[tuple[datetime, int]]
    s_zones: list[object]
    s_candidates: list[object]


def create_e_detector(
    direction: str,
    e_engine,
    full_results: dict[str, object],
    s_zones: list[object],
    chronology,
    geometry_detectors: dict[str, object],
    initial_order_audit,
    lifecycle_engine,
    *,
    blocked_order_first_times: set[datetime] | None = None,
    invalid_s_root_identities: set[tuple[datetime, int]] | None = None,
):
    """Construct one E detector from the shared geometry/lifecycle contract."""
    opposite = chronology.opposite_direction(direction)
    end_index = len(chronology.candles) - 1

    def reset_geometry(geometry_direction, geometry_start, geometry_end):
        return geometry_detectors[geometry_direction].first_geometry_after_reset(
            geometry_direction,
            max(0, geometry_start - 1),
            geometry_end,
        )

    def direct_geometry(
        geometry_direction, geometry_start, geometry_end, gate_event
    ):
        return geometry_detectors[geometry_direction].first_order_reaction_after_gate(
            geometry_direction,
            geometry_start,
            geometry_end,
            gate_event,
        )

    def simple_reset_geometry(
        geometry_direction, reset_index, gate_index, geometry_end
    ):
        return geometry_detectors[geometry_direction].first_simple_geometry_after_gate(
            geometry_direction,
            reset_index,
            gate_index,
            geometry_end,
        )

    return e_engine.EZoneDetector(
        direction,
        full_results[direction].reactions,
        full_results[opposite].reactions,
        s_zones,
        full_results[direction].resets,
        full_results[opposite].resets,
        chronology,
        0,
        end_index,
        reset_geometry,
        direct_geometry,
        blocked_order_first_times=blocked_order_first_times,
        initial_order_audit=initial_order_audit,
        reset_geometry_finder=simple_reset_geometry,
        sequence_priority=lifecycle_engine.sequence_priority,
        invalid_s_root_identities=invalid_s_root_identities,
    )


def calculate_full_direction_state(
    direction: str,
    engines: EngineBundle,
    market: MarketContext,
    full_results: dict[str, object],
    geometry_detectors: dict[str, object],
    initial_order_geometry: dict[str, object],
    timings: dict[str, float],
) -> FullDirectionState:
    """Run Blue→A→S→E calculation and lifecycle reconciliation for one direction."""
    blue_engine = engines.blue_line
    a_engine = engines.a_zone
    s_engine = engines.s_zone
    e_engine = engines.e_zone
    lifecycle_engine = engines.lifecycle
    assert e_engine is not None
    candles = market.candles
    chronology = market.chronology
    opposite = engines.reaction.opposite_direction(direction)

    blue_lines = timed(
        timings,
        f"Blue Line • {direction.title()}",
        lambda: blue_engine.detect_blue_lines(
            direction,
            full_results[direction].reactions,
            chronology,
            full_results[direction].resets,
        ),
    )
    a_zones = timed(
        timings,
        f"A • {direction.title()}",
        lambda: a_engine.detect_a_zones(
            direction,
            full_results[direction].reactions,
            blue_lines,
            chronology,
        ),
    )
    s_detector = s_engine.SZoneDetector(
        direction,
        full_results[direction].reactions,
        full_results[opposite].reactions,
        blue_lines,
        a_zones,
        chronology,
        0,
        len(candles) - 1,
        full_results[opposite].resets,
        initial_order_geometry=initial_order_geometry[direction],
    )
    s_zones = timed(timings, f"S • {direction.title()}", s_detector.detect)
    s_candidates = list(s_zones)

    historical_e_rescues: list[object] = []
    accepted_e_history: list[object] = []

    def collect_accepted_e_history(zones) -> None:
        existing = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in accepted_e_history
        }
        for item in zones:
            # Keep this safeguard intentionally narrow: only the E-parented
            # Blue Order_B lineage is known to be vulnerable to later-pass
            # retroactive suppression. Other families/modes retain the exact
            # legacy reconciliation behavior.
            if str(getattr(item, "parent_type", "")).upper() != "E":
                continue
            if str(getattr(item, "family", "")).lower() != "blue":
                continue
            if str(getattr(item, "order_mode", "")).upper() != "B":
                continue
            identity = (
                int(getattr(item, "source_index")),
                getattr(item, "source_time"),
            )
            if identity not in existing:
                accepted_e_history.append(item)
                existing.add(identity)

    def collect_historical_e_rescues(detector) -> None:
        existing = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in historical_e_rescues
        }
        for item in getattr(detector, "historical_rescued_zones", []):
            identity = (
                int(getattr(item, "source_index")),
                getattr(item, "source_time"),
            )
            if identity not in existing:
                historical_e_rescues.append(item)
                existing.add(identity)

    e_detector = create_e_detector(
        direction,
        e_engine,
        full_results,
        s_zones,
        chronology,
        geometry_detectors,
        s_detector.order_audit,
        lifecycle_engine,
    )
    e_zones = timed(
        timings, f"E • {direction.title()} • initial", e_detector.detect
    )
    collect_historical_e_rescues(e_detector)
    collect_accepted_e_history(e_zones)
    valid_s_zones = lifecycle_engine.s_zones_for_module_engines(
        s_zones, e_zones, direction
    )
    if len(valid_s_zones) != len(s_zones):
        e_detector = create_e_detector(
            direction,
            e_engine,
            full_results,
            valid_s_zones,
            chronology,
            geometry_detectors,
            s_detector.order_audit,
            lifecycle_engine,
            blocked_order_first_times={
                getattr(item, "source_time")
                for item in s_zones
                if item not in valid_s_zones
            },
        )
        e_zones = timed(
            timings,
            f"E • {direction.title()} • S reconciliation",
            e_detector.detect,
        )
        collect_historical_e_rescues(e_detector)
        collect_accepted_e_history(e_zones)
        s_zones = valid_s_zones

    candidate_a = lifecycle_engine.visible_a_zones(
        s_detector.eligible_a_zones, s_zones
    )
    candidate_a = lifecycle_engine.visible_a_zones_after_s_stops(
        candidate_a, s_zones, candles
    )
    _calculation_a, invalid_a = lifecycle_engine.split_a_zones_by_dominant_stops(
        candidate_a,
        s_candidates,
        e_zones,
        [],
        candles,
        direction,
        lambda item: e_detector.parent_stop(
            "S" if hasattr(item, "a_source_time") else "E", item
        ),
        trend_reactions=s_detector.trend_reactions,
        confirmation_finder=s_detector.reaction_confirmation_time,
        a_stop_event_finder=lambda item: s_detector.first_a_stop(
            Decimal(str(getattr(item, "price"))),
            s_detector.reaction_confirmation_time(
                s_detector.trend_reactions[int(getattr(item, "reaction_number")) - 1],
                direction,
            ),
        ),
    )
    invalid_a_identities = {
        (getattr(item, "source_time"), int(getattr(item, "source_index")))
        for item in invalid_a
    }
    invalid_a_source_times = {source_time for source_time, _ in invalid_a_identities}
    invalid_s = [
        item for item in s_candidates
        if getattr(item, "a_source_time") in invalid_a_source_times
    ]
    invalid_s_identities = {
        (getattr(item, "source_time"), int(getattr(item, "source_index")))
        for item in invalid_s
    }

    accepted_a_sources = {
        getattr(item, "source_time")
        for item in s_detector.eligible_a_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in invalid_a_identities
    }
    pending_s_a_sources = {getattr(item, "a_source_time") for item in s_candidates}
    accepted_orders, blocked_order_first_times = lifecycle_engine.resolve_order_context(
        s_detector.order_audit,
        accepted_a_sources,
        set(getattr(e_detector, "blocked_order_first_times", set())),
        invalid_a,
        pending_s_a_sources,
        full_results[opposite].reactions,
        candles,
        direction,
        lambda item: s_detector.first_a_stop(
            Decimal(str(getattr(item, "price"))),
            getattr(item, "source_time"),
        ),
    )
    e_detector = create_e_detector(
        direction,
        e_engine,
        full_results,
        s_zones,
        chronology,
        geometry_detectors,
        accepted_orders,
        lifecycle_engine,
        blocked_order_first_times=blocked_order_first_times,
        invalid_s_root_identities=invalid_s_identities,
    )
    e_zones = timed(
        timings, f"E • {direction.title()} • final audit", e_detector.detect
    )
    collect_historical_e_rescues(e_detector)
    collect_accepted_e_history(e_zones)

    # A still-open S candidate may be decided by the strict stop of a later
    # calculation-accepted physical Order in the same chronology.  Reconcile
    # against accepted ledgers only; arbitrary opposite Reactions are never
    # promoted into Orders by this pass.  Rebuild E once when S provenance or
    # decision chronology changes because E consumes S as authoritative input.
    shared_order_entries = [
        *accepted_orders.values(),
        *e_detector.order_audit.values(),
    ]
    reconciled_s_zones = s_detector.reconcile_shared_order_stops(
        s_zones, shared_order_entries
    )
    if reconciled_s_zones != s_zones:
        s_zones = reconciled_s_zones
        reconciled_by_identity = {
            (getattr(item, "a_source_time"), getattr(item, "source_time")): item
            for item in s_zones
        }
        s_candidates = [
            reconciled_by_identity.get(
                (getattr(item, "a_source_time"), getattr(item, "source_time")),
                item,
            )
            for item in s_candidates
        ]
        e_detector = create_e_detector(
            direction,
            e_engine,
            full_results,
            s_zones,
            chronology,
            geometry_detectors,
            accepted_orders,
            lifecycle_engine,
            blocked_order_first_times=blocked_order_first_times,
            invalid_s_root_identities=invalid_s_identities,
        )
        e_zones = timed(
            timings,
            f"E • {direction.title()} • shared Order-stop reconciliation",
            e_detector.detect,
        )
        collect_historical_e_rescues(e_detector)
        collect_accepted_e_history(e_zones)

    consumed_s_evidence = lifecycle_engine.consumed_s_evidence_after_larger_stop(
        s_candidates,
        s_zones,
        e_zones,
        direction,
        lambda item: e_detector.parent_stop("E", item),
        candles,
    )
    for evidence_s, original_owner in consumed_s_evidence:
        owner = next(
            (
                item for item in e_zones
                if int(getattr(item, "source_index")) == int(getattr(original_owner, "source_index"))
                and getattr(item, "source_time") == getattr(original_owner, "source_time")
            ),
            None,
        )
        if owner is None:
            continue
        continuation = e_detector.continuation_chain_from_s(owner, evidence_s)
        e_zones = e_detector.replace_with_earlier_continuation(
            e_zones, owner, continuation
        )

    s_zones = [
        item for item in s_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in invalid_s_identities
    ]

    # Preserve presentation-only historical E acceptance without changing
    # calculation ownership. An earlier accepted E that disappears during a
    # later detector rebuild is recoverable only when it is not merely a
    # hidden intermediate parent of a surviving final E. Hidden intermediate
    # parents remain intentionally non-public; independent accepted history is
    # retained for reporting.
    if accepted_e_history:
        historical_e_rescues.extend(accepted_e_history)
    if historical_e_rescues:
        historical_e_rescues = e_detector.resolve_same_source_conflicts(
            historical_e_rescues
        )
        final_e_ids = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in e_zones
        }
        referenced_e_parent_ids = {
            (
                int(getattr(item, "parent_source_index")),
                getattr(item, "parent_source_time"),
            )
            for item in e_zones
            if str(getattr(item, "parent_type", "")).upper() == "E"
        }
        def blocked_by_dominant_final_e(item) -> bool:
            candidate_priority = lifecycle_engine.sequence_priority(
                "e", str(getattr(item, "family"))
            )
            candidate_decision = getattr(item, "decision_event_time")
            for owner in e_zones:
                if getattr(owner, "source_time") >= getattr(item, "source_time"):
                    continue
                owner_priority = lifecycle_engine.sequence_priority(
                    "e", str(getattr(owner, "family"))
                )
                if owner_priority <= candidate_priority:
                    continue
                stop = e_detector.parent_stop("E", owner)
                if stop is None or stop[1] >= candidate_decision:
                    return True
            return False

        e_detector.historical_rescued_zones = [
            item for item in historical_e_rescues
            if (int(getattr(item, "source_index")), getattr(item, "source_time"))
            not in final_e_ids
            and (int(getattr(item, "source_index")), getattr(item, "source_time"))
            not in referenced_e_parent_ids
            and not blocked_by_dominant_final_e(item)
        ]

    return FullDirectionState(
        e_zones=e_zones,
        e_detector=e_detector,
        s_detector=s_detector,
        blue_lines=blue_lines,
        a_zones=a_zones,
        invalid_a_identities=invalid_a_identities,
        invalid_s_identities=invalid_s_identities,
        s_zones=s_zones,
        s_candidates=s_candidates,
    )


def prepare_pipeline_state(
    args,
    engines: EngineBundle,
    market: MarketContext,
    timings: dict[str, float],
) -> PipelineState:
    """Run shared calculation stages once and retain reusable detector state."""
    engine = engines.reaction
    e_engine = engines.e_zone
    seconds = market.seconds
    candles = market.candles
    chronology = market.chronology
    initial_order_geometry = {
        direction: engine.directional_a_stop_order_finder(
            candles, seconds, direction
        )
        for direction in ("bullish", "bearish")
    }
    directions = ("bullish", "bearish") if args.direction == "both" else (args.direction,)
    behavior_modules_enabled = (
        args.blue_lines == "enabled"
        or args.a_zones == "enabled"
        or args.s_zones == "enabled"
    )
    required_directions = (
        ("bullish", "bearish") if behavior_modules_enabled else directions
    )
    reusable_full_context = e_engine is not None and args.s_zones == "enabled"

    full_e_zones: dict[str, list[object]] = {}
    full_e_detectors: dict[str, object] = {}
    full_s_detectors: dict[str, object] = {}
    full_lines_by_direction: dict[str, list[object]] = {}
    full_a_by_direction: dict[str, list[object]] = {}
    invalid_a_identities_by_direction: dict[str, set[tuple[datetime, int]]] = {}
    invalid_s_identities_by_direction: dict[str, set[tuple[datetime, int]]] = {}
    full_s_by_direction: dict[str, list[object]] = {}
    full_s_candidates_by_direction: dict[str, list[object]] = {}

    if reusable_full_context:
        geometry_detectors = {
            direction: engine.UnifiedReactionDetector(
                candles, seconds, 0, len(candles) - 1, direction
            )
            for direction in ("bullish", "bearish")
        }
        results = {
            direction: timed(
                timings,
                f"Reaction geometry • {direction.title()}",
                detector.detect,
            )
            for direction, detector in geometry_detectors.items()
        }
        _, _, internal_reaction_identities, _ = timed(
            timings,
            "Internal Reaction ownership",
            lambda: engine.build_behavior_reaction_views(results, chronology),
        )
        for direction in directions:
            state = calculate_full_direction_state(
                direction,
                engines,
                market,
                results,
                geometry_detectors,
                initial_order_geometry,
                timings,
            )
            full_e_zones[direction] = state.e_zones
            full_e_detectors[direction] = state.e_detector
            full_s_detectors[direction] = state.s_detector
            full_lines_by_direction[direction] = state.blue_lines
            full_a_by_direction[direction] = state.a_zones
            invalid_a_identities_by_direction[direction] = state.invalid_a_identities
            invalid_s_identities_by_direction[direction] = state.invalid_s_identities
            full_s_by_direction[direction] = state.s_zones
            full_s_candidates_by_direction[direction] = state.s_candidates
    else:
        results = {
            direction: timed(
                timings,
                f"Reaction • {direction.title()}",
                lambda direction=direction: engine.UnifiedReactionDetector(
                    candles, seconds, 0, len(candles) - 1, direction
                ).detect(),
            )
            for direction in required_directions
        }
        if behavior_modules_enabled:
            _, _, internal_reaction_identities, _ = timed(
                timings,
                "Internal Reaction ownership",
                lambda: engine.build_behavior_reaction_views(results, chronology),
            )
        else:
            internal_reaction_identities = {"bullish": set(), "bearish": set()}

    return PipelineState(
        directions=tuple(directions),
        results=results,
        reusable_full_context=reusable_full_context,
        initial_order_geometry=initial_order_geometry,
        internal_reaction_identities=internal_reaction_identities,
        full_e_zones=full_e_zones,
        full_e_detectors=full_e_detectors,
        full_s_detectors=full_s_detectors,
        full_lines_by_direction=full_lines_by_direction,
        full_a_by_direction=full_a_by_direction,
        invalid_a_identities_by_direction=invalid_a_identities_by_direction,
        invalid_s_identities_by_direction=invalid_s_identities_by_direction,
        full_s_by_direction=full_s_by_direction,
        full_s_candidates_by_direction=full_s_candidates_by_direction,
    )


@dataclass(slots=True)
class DirectionRangeState:
    """Unserialized calculation state for one requested direction/range."""

    blue_lines: list[object]
    a_zones: list[object]
    s_candidates: list[object]
    accepted_s_zones: list[object]
    e_zones: list[object]
    invalid_a_identities: set[tuple[datetime, int]]
    invalid_s_identities: set[tuple[datetime, int]]


@dataclass(slots=True)
class DirectionVisibilityState:
    """Final public behavior state after lifecycle and internal-Reaction rules."""

    blue_lines: list[object]
    a_zones: list[object]
    s_zones: list[object]
    e_zones: list[object]
    stopalls: list[object]
    prepared_order_audit: list[object]


def calculate_direction_range_state(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    timings: dict[str, float],
) -> DirectionRangeState:
    """Collect detector output for one requested direction before visibility rules."""
    result = state.results[direction]
    opposite = engines.reaction.opposite_direction(direction)
    start_index = market.start_index
    end_index = market.end_index

    requires_blue_lines = (
        args.blue_lines == "enabled"
        or args.a_zones == "enabled"
        or args.s_zones == "enabled"
    )
    if state.reusable_full_context and requires_blue_lines:
        blue_lines = [
            item
            for item in state.full_lines_by_direction[direction]
            if start_index <= int(getattr(item, "source_index")) <= end_index
        ]
    elif requires_blue_lines:
        blue_lines = timed(
            timings,
            f"Blue Line - {direction.title()}",
            lambda: engines.blue_line.detect_blue_lines(
                direction,
                result.reactions,
                market.chronology,
                result.resets,
            ),
        )
    else:
        blue_lines = []

    requires_a_zones = args.a_zones == "enabled" or args.s_zones == "enabled"
    if state.reusable_full_context and requires_a_zones:
        a_zones = [
            item
            for item in state.full_a_by_direction[direction]
            if start_index <= int(getattr(item, "source_index")) <= end_index
        ]
    elif requires_a_zones:
        a_zones = timed(
            timings,
            f"A - {direction.title()}",
            lambda: engines.a_zone.detect_a_zones(
                direction,
                result.reactions,
                blue_lines,
                market.chronology,
            ),
        )
    else:
        a_zones = []

    s_candidates: list[object] = []
    accepted_s_zones: list[object] = []
    if args.s_zones == "enabled":
        if state.reusable_full_context:
            s_candidates = state.full_s_candidates_by_direction[direction]
            accepted_s_zones = state.full_s_by_direction[direction]
            a_zones = state.full_s_detectors[direction].eligible_a_zones
        else:
            s_detector = engines.s_zone.SZoneDetector(
                direction,
                result.reactions,
                state.results[opposite].reactions,
                blue_lines,
                a_zones,
                market.chronology,
                0,
                len(market.candles) - 1,
                state.results[opposite].resets,
                initial_order_geometry=state.initial_order_geometry[direction],
            )
            s_candidates = timed(
                timings, f"S - {direction.title()}", s_detector.detect
            )
            state.full_s_detectors[direction] = s_detector
            accepted_s_zones = s_candidates
            a_zones = s_detector.eligible_a_zones

    return DirectionRangeState(
        blue_lines=blue_lines,
        a_zones=a_zones,
        s_candidates=s_candidates,
        accepted_s_zones=accepted_s_zones,
        e_zones=list(state.full_e_zones.get(direction, [])),
        invalid_a_identities=state.invalid_a_identities_by_direction.get(
            direction, set()
        ),
        invalid_s_identities=state.invalid_s_identities_by_direction.get(
            direction, set()
        ),
    )


def finalize_direction_visibility(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    direction_state: DirectionRangeState,
    timings: dict[str, float],
) -> DirectionVisibilityState:
    """Apply lifecycle, range and Internal-Reaction rules to detector output."""
    lifecycle_engine = engines.lifecycle
    opposite = engines.reaction.opposite_direction(direction)
    start_index = market.start_index
    end_index = market.end_index

    visible_a_zones = lifecycle_engine.visible_a_zones(
        direction_state.a_zones, direction_state.accepted_s_zones
    )
    visible_a_zones = lifecycle_engine.visible_a_zones_after_s_stops(
        visible_a_zones,
        direction_state.accepted_s_zones,
        market.candles,
    )

    e_zones = list(direction_state.e_zones)
    stopalls: list[object] = []
    stopall_enabled = (
        args.lifecycle_engine is not None
        and engines.e_zone is not None
        and args.s_zones == "enabled"
    )
    if stopall_enabled and direction in state.full_e_detectors:
        e_zones, stopalls = lifecycle_engine.reconcile_stopall_lifecycle(
            state.full_e_detectors[direction],
            direction_state.accepted_s_zones,
            e_zones,
            market.chronology,
            direction,
            lambda label, work: timed(timings, label, work),
        )

    if direction in state.full_e_detectors:
        # Dominant E ownership drives StopAll.  After those hard boundaries are
        # fixed, restore direct E1 roots of accepted S behaviors so independent
        # E formation remains visible without letting lower-priority roots
        # rewrite the dominant StopAll sequence.
        e_zones = state.full_e_detectors[direction].restore_independent_s_roots(
            e_zones
        )
        visibility_stop = lambda item: state.full_e_detectors[direction].parent_stop(
            "S" if hasattr(item, "a_source_time") else "E", item
        )
    else:
        visibility_stop = lambda item: state.full_s_detectors[direction].first_a_stop(
            Decimal(str(item.price)), item.decision_event_time
        )

    e_zones, visible_s_zones, visible_a_zones = timed(
        timings,
        f"Apply visibility filters - {direction.title()}",
        lambda: lifecycle_engine.finalize_behavior_visibility(
            visible_a_zones,
            direction_state.s_candidates,
            e_zones,
            stopalls,
            direction,
            direction_state.invalid_s_identities,
            visibility_stop,
            lambda item: state.full_s_detectors[direction].candidate_event_time(
                item.source_index, item.price, item.source_time
            ),
            market.candles,
            all_a_zones=direction_state.a_zones,
        ),
    )

    visible_s_zones = [
        item
        for item in visible_s_zones
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]
    visible_a_zones = [
        item
        for item in visible_a_zones
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]
    e_zones = [
        item
        for item in e_zones
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]
    stopalls = [
        item
        for item in stopalls
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]

    display_a_zones = [
        item
        for item in visible_a_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in direction_state.invalid_a_identities
    ]
    display_s_zones = [
        item
        for item in visible_s_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in direction_state.invalid_s_identities
    ]
    order_audit_a_sources = {
        getattr(item, "source_time") for item in display_a_zones
    }

    all_behavior_reactions = [
        reaction
        for result_item in state.results.values()
        for reaction in result_item.reactions
    ]
    engines.blue_line.mark_internal_blue_lines(
        direction_state.blue_lines,
        state.results[direction].reactions,
        all_behavior_reactions,
    )
    display_a_zones, display_s_zones, e_zones, stopalls = (
        lifecycle_engine.filter_internal_behavior_outputs(
            display_a_zones,
            display_s_zones,
            e_zones,
            stopalls,
            state.results[opposite].reactions,
            state.internal_reaction_identities.get(opposite, set()),
            all_behavior_reactions,
        )
    )

    # Historical rescue is presentation-only.  It runs after all lifecycle,
    # StopAll, visibility, and OrderAudit ownership calculations so restoring a
    # fully formed historical E can never rewrite an already-correct behavior,
    # number, parent, StopAll sequence, or physical Order provenance.
    if direction in state.full_e_detectors:
        detector = state.full_e_detectors[direction]
        occupied_e_sources = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in e_zones
        }
        occupied_stopall_sources = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in stopalls
        }
        rescued_e_zones = [
            item
            for item in getattr(detector, "historical_rescued_zones", [])
            if start_index <= int(getattr(item, "source_index")) <= end_index
            and (int(getattr(item, "source_index")), getattr(item, "source_time"))
                not in occupied_e_sources
            and (int(getattr(item, "source_index")), getattr(item, "source_time"))
                not in occupied_stopall_sources
            and not lifecycle_engine.forbidden_internal_order_b(
                item, state.internal_reaction_identities.get(opposite, set())
            )
        ]
        if rescued_e_zones:
            e_zones = sorted(
                [*e_zones, *rescued_e_zones],
                key=lambda item: (
                    getattr(item, "source_time"),
                    int(getattr(item, "source_index")),
                    getattr(item, "decision_event_time"),
                ),
            )

    prepared_order_audit = (
        lifecycle_engine.prepare_order_audit(
            state.full_e_detectors[direction],
            start_index,
            end_index,
            state.full_s_detectors.get(direction),
            order_audit_a_sources,
        )
        if direction in state.full_e_detectors
        else []
    )
    return DirectionVisibilityState(
        blue_lines=engines.blue_line.public_blue_lines(direction_state.blue_lines),
        a_zones=display_a_zones,
        s_zones=display_s_zones,
        e_zones=e_zones,
        stopalls=stopalls,
        prepared_order_audit=prepared_order_audit,
    )


def serialize_direction_payload(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    visibility: DirectionVisibilityState,
    timings: dict[str, float],
):
    """Serialize one direction without applying any trading rule."""
    result = state.results[direction]
    reactions, resets = timed(
        timings,
        f"Serialize Reaction - {direction.title()}",
        lambda: serialize(
            result,
            market.start_index,
            market.end_index,
            reaction_transform=lambda item: engines.reaction.published_reaction_candidate(
                direction, item, market.chronology
            ),
        ),
    )

    def build_payload():
        payload = {
            "reactions": reactions,
            "resets": resets,
            "blueLines": serialize_blue_lines(
                visibility.blue_lines if args.blue_lines == "enabled" else [],
                market.start_index,
                market.end_index,
            ),
            "aZones": serialize_a_zones(
                visibility.a_zones if args.a_zones == "enabled" else []
            ),
            "sZones": serialize_s_zones(visibility.s_zones),
            "eZones": serialize_e_zones(visibility.e_zones),
            "stopAlls": serialize_stopalls(visibility.stopalls),
            "orderAudit": (
                serialize_order_audit(
                    visibility.prepared_order_audit,
                    state.full_e_detectors[direction],
                )
                if direction in state.full_e_detectors
                else []
            ),
        }
        payload["report"] = serialize_human_report(
            direction, payload, state, visibility
        )
        return payload

    return timed(
        timings, f"Serialize output - {direction.title()}", build_payload
    )


def build_direction_output(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    timings: dict[str, float],
):
    """Calculate, finalize and serialize one requested trend direction."""
    direction_state = calculate_direction_range_state(
        direction, args, engines, market, state, timings
    )
    visibility = finalize_direction_visibility(
        direction,
        args,
        engines,
        market,
        state,
        direction_state,
        timings,
    )
    return serialize_direction_payload(
        direction, args, engines, market, state, visibility, timings
    )

def build_response_payload(
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    timings: dict[str, float],
    pipeline_started: float,
) -> dict[str, object]:
    """Build the public response envelope around serialized direction outputs."""
    e_enabled = engines.e_zone is not None and args.s_zones == "enabled"
    stop_all_enabled = (
        args.lifecycle_engine is not None
        and engines.e_zone is not None
        and args.s_zones == "enabled"
    )
    payload: dict[str, object] = {
        "engine": "reaction_engine.py",
        "version": engines.reaction.REACTION_ENGINE_VERSION,
        "pipelineVersion": TRADING_PIPELINE_VERSION,
        "blueLineVersion": engines.blue_line.BLUE_LINE_VERSION,
        "aVersion": engines.a_zone.A_ZONE_VERSION,
        "sVersion": engines.s_zone.S_ZONE_VERSION,
        "eVersion": engines.e_zone.E_ZONE_VERSION if engines.e_zone else None,
        "stopAllVersion": (
            engines.lifecycle.STOP_ALL_VERSION
            if args.lifecycle_engine is not None
            else None
        ),
        "blueLinesEnabled": args.blue_lines == "enabled",
        "aEnabled": args.a_zones == "enabled",
        "sEnabled": args.s_zones == "enabled",
        "eEnabled": e_enabled,
        "stopAllEnabled": stop_all_enabled,
        "timeframe": args.timeframe,
        "calculationRange": {
            "from": int(args.from_time),
            "to": int(args.to_time),
            "sourceFrom": int(args.from_time),
            "sourceTo": int(args.to_time) if args.timeframe == 1 else int(args.to_time) + int(args.timeframe) - 1,
            "isolated": True,
        },
        "actualFrom": epoch(market.candles[market.start_index].timestamp),
        "actualTo": epoch(market.candles[market.end_index].timestamp),
        "directions": {},
    }
    direction_payloads = payload["directions"]
    assert isinstance(direction_payloads, dict)
    for direction in state.directions:
        direction_payloads[direction] = build_direction_output(
            direction, args, engines, market, state, timings
        )
    payload["report"] = sorted(
        [
            item
            for direction_payload in direction_payloads.values()
            for item in direction_payload.get("report", [])
        ],
        key=lambda item: (item.get("time") or "", item.get("id") or ""),
    )
    payload["timings"] = {
        "phasesMs": {
            label: round(duration, 2) for label, duration in timings.items()
        },
        "bridgeTotalMs": round((perf_counter() - pipeline_started) * 1000, 2),
    }
    return payload


def main() -> int:
    pipeline_started = perf_counter()
    timings: dict[str, float] = {}
    validation_started = perf_counter()
    emit_progress("started", "Validate request")
    args = parse_arguments()
    validation_ms = (perf_counter() - validation_started) * 1000
    timings["Validate request"] = validation_ms
    emit_progress("completed", "Validate request", validation_ms)

    engines = load_engines(args, timings)
    market = prepare_market_context(args, engines, timings)
    state = prepare_pipeline_state(args, engines, market, timings)
    payload = build_response_payload(
        args, engines, market, state, timings, pipeline_started
    )

    emit_progress(
        "completed",
        "Calculation pipeline",
        (perf_counter() - pipeline_started) * 1000,
    )
    encoding_started = perf_counter()
    encoded_payload = json.dumps(payload, separators=(",", ":"))
    emit_progress(
        "completed",
        "Encode response JSON",
        (perf_counter() - encoding_started) * 1000,
    )
    print(encoded_payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        raise SystemExit(1)
