from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import orjson
from bisect import bisect_left, bisect_right
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from zoneinfo import ZoneInfo
import calendar
_DTFMT = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}"


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
    return load_module("reaction_detection_new", path)


def decimal(value: object) -> Decimal:
    return Decimal(str(value))


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


def build_candles(engine, rows: list[dict], timeframe: int):
    buckets: list[dict] = []
    current = None
    for row in rows:
        timestamp = int(row["time"])
        bucket_time = timestamp if timeframe == 1 else timestamp // timeframe * timeframe
        o, h, low, close = map(decimal, (row["open"], row["high"], row["low"], row["close"]))
        if current is None or current["time"] != bucket_time:
            current = {"time": bucket_time, "open": o, "high": h, "low": low, "close": close}
            buckets.append(current)
        else:
            current["high"] = max(current["high"], h)
            current["low"] = min(current["low"], low)
            current["close"] = close
    candles = []
    for index, item in enumerate(buckets):
        stamp = local_datetime(item["time"])
        candles.append(engine.Candle(
            index=index,
            timestamp=stamp,
            display_time=stamp.strftime("%Y-%m-%d %H:%M:%S"),
            tag=engine.classify_candle_color(item["open"], item["close"]),
            open=item["open"], high=item["high"], low=item["low"], close=item["close"],
        ))
    return candles


def build_candle_buckets(rows: list[dict], timeframe: int):
    """Normalize raw rows once, preserving lower and selected-timeframe buckets."""
    second_buckets: list[dict] = []
    current_second = None
    buckets: list[dict] = []
    current = None
    to_decimal = decimal
    for row in rows:
        timestamp = int(row["time"])
        o = to_decimal(row["open"])
        high = to_decimal(row["high"])
        low = to_decimal(row["low"])
        close = to_decimal(row["close"])
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
            display_time=fmt(stamp.year, stamp.month, stamp.day, stamp.hour, stamp.minute, stamp.second),
            tag=classify(item["open"], item["close"]),
            open=item["open"],
            high=item["high"],
            low=item["low"],
            close=item["close"],
        ))
    return candles


def build_candle_views(engine, rows: list[dict], timeframe: int):
    """Build lower and main candles in one Decimal-normalization pass."""
    second_buckets, buckets = build_candle_buckets(rows, timeframe)
    seconds = build_candle_objects(engine, second_buckets)
    if timeframe == 1:
        return seconds, seconds
    candles = build_candle_objects(engine, buckets)
    return seconds, candles


def bullish_a_stop_order_finder(engine, candles, seconds):
    """Reuse ordinary Reaction discovery for a bullish A-stop continuation.

    The pre-First context remains inside the already selected input. Reaction
    owns all geometry and stop-boundary calculations; no prices are rebuilt here.
    Only S's exact same-candle ownership path calls this resolver.
    """
    cache = {}

    def find(gate_index, gate_event, end_index):
        key = (gate_index, gate_event, end_index)
        if key in cache:
            return cache[key]
        first = next((
            index for index in range(max(1, gate_index), end_index + 1)
            if candles[index].tag == "GREEN" and candles[index - 1].tag == "RED"
        ), None)
        if first is None:
            cache[key] = None
            return None
        context = first - 1
        while context > 0 and candles[context - 1].tag == "RED":
            context -= 1
        result = engine.UnifiedReactionDetector(
            candles, seconds, context, end_index, "bearish"
        ).detect()
        order = next((
            reaction for reaction in result.reactions
            if int(getattr(reaction, "first_idx")) >= gate_index
        ), None)
        cache[key] = order
        return order

    return find


def serialize(result):
    resets = [{
        "index": item.index,
        "time": epoch(datetime.strptime(item.display_time, "%Y-%m-%d %H:%M:%S")),
        "secondTime": (
            epoch(datetime.strptime(item.second_time, "%Y-%m-%d %H:%M:%S"))
            if item.second_time is not None
            else None
        ),
        "brokenLevel": str(item.broken_level),
        "fromFirstIndex": item.from_first_idx,
    } for item in result.resets]
    reactions = []
    for item in result.reactions:
        reactions.append({
            "firstIndex": item.first_idx,
            "firstTime": epoch(datetime.strptime(item.first_time, "%Y-%m-%d %H:%M:%S")),
            "boxTopSourceIndex": item.box_top_source_idx,
            "boxTopSourceTime": epoch(datetime.strptime(item.box_top_source_time, "%Y-%m-%d %H:%M:%S")),
            "boxTop": str(item.box_top),
            "boxBottomSourceIndex": item.box_bottom_source_idx,
            "boxBottomSourceTime": epoch(datetime.strptime(item.box_bottom_source_time, "%Y-%m-%d %H:%M:%S")),
            "boxBottom": str(item.box_bottom),
            "breakIndex": item.break_idx,
            "breakTime": epoch(datetime.strptime(item.break_time, "%Y-%m-%d %H:%M:%S")),
            "mode": item.mode,
        })
    return reactions, resets


def serialize_blue_lines(items):
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
    } for item in items if bool(getattr(item, "calculation_valid", True))]


def serialize_a_zones(items, invalid_identities=None):
    invalid = invalid_identities or set()
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
    } for item in items if (
        getattr(item, "source_time"), int(getattr(item, "source_index"))
    ) not in invalid]


def serialize_s_zones(items, invalid_identities=None):
    invalid = invalid_identities or set()
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
        "orderFirstTime": epoch(item.order_first_time) if item.order_first_time is not None else None,
        "orderBreakIndex": item.order_break_index,
        "orderBreakTime": epoch(item.order_break_time) if item.order_break_time is not None else None,
        "orderConfirmationTime": epoch(item.order_confirmation_time) if item.order_confirmation_time is not None else None,
        "orderBoxTop": str(item.order_box_top) if item.order_box_top is not None else None,
        "orderBoxTopSourceIndex": item.order_box_top_source_index,
        "orderBoxTopSourceTime": epoch(item.order_box_top_source_time) if item.order_box_top_source_time is not None else None,
        "orderBoxBottom": str(item.order_box_bottom) if item.order_box_bottom is not None else None,
        "orderBoxBottomSourceIndex": item.order_box_bottom_source_index,
        "orderBoxBottomSourceTime": epoch(item.order_box_bottom_source_time) if item.order_box_bottom_source_time is not None else None,
        "orderStopLevel": str(item.order_stop_level) if item.order_stop_level is not None else None,
        "orderStopSourceIndex": item.order_stop_source_index,
        "orderStopSourceTime": epoch(item.order_stop_source_time) if item.order_stop_source_time is not None else None,
        "resetReactionNumber": item.reset_reaction_number,
        "resetTime": epoch(item.reset_time) if item.reset_time is not None else None,
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "decisionIndex": item.decision_index,
        "decisionTime": epoch(item.decision_time),
        "decisionEventTime": epoch(item.decision_event_time),
        "calculationValid": True,
    } for item in items if (
        getattr(item, "source_time"), int(getattr(item, "source_index"))
    ) not in invalid]


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
        "stopIndex": item.stop_index,
        "stopTime": epoch(item.stop_time) if item.stop_time else None,
        "stopEventTime": epoch(item.stop_event_time) if item.stop_event_time else None,
    } for item in items]


def serialize_order_audit(
    detector, start_index: int, end_index: int, s_detector=None,
):
    """Serialize valid order genders for audit without changing chart drawing."""
    output = []
    combined = []
    if s_detector is not None:
        for entry in s_detector.order_audit.values():
            combined.append((entry, [{
                "kind": "parent-stop",
                "parentType": "A",
                "parentFamily": None,
                "eventTime": epoch(entry["a_stop_event_time"]),
                "parentSourceTime": epoch(entry["a_source_time"]),
            }]))
    for entry in detector.order_audit.values():
        causes = []
        for cause in sorted(entry["causes"], key=str):
            if cause[0] == "parent-stop":
                causes.append({
                    "kind": cause[0],
                    "parentType": cause[1],
                    "parentFamily": cause[2],
                    "eventTime": epoch(cause[3]),
                    "parentSourceTime": epoch(cause[4]),
                })
            else:
                causes.append({
                    "kind": cause[0],
                    "resetTime": epoch(cause[1]),
                    "boundaryBreakTime": epoch(cause[2]),
                })
        combined.append((entry, causes))
    merged = {}
    for entry, supplied_causes in combined:
        reaction = entry["reaction"]
        first_index = int(getattr(reaction, "first_idx"))
        if not start_index <= first_index <= end_index:
            continue
        crossed = entry.get("stop_cross")
        if "stop_cross" not in entry:
            crossed = detector._cross_order(
                entry["confirmation_time"], entry["stop_level"]
            )
        identity = (first_index, int(getattr(reaction, "break_idx")))
        existing = merged.get(identity)
        if existing is not None:
            existing["causes"].extend(
                cause for cause in supplied_causes
                if cause not in existing["causes"]
            )
            continue
        serialized = {
            "direction": detector.order_direction,
            "reactionNumber": entry["reaction_number"],
            "reactionMode": str(getattr(reaction, "mode")),
            "firstIndex": first_index,
            "firstTime": epoch(detector.candles[first_index].timestamp),
            "boxTopSourceIndex": int(getattr(reaction, "box_top_source_idx")),
            "boxTopSourceTime": epoch(datetime.strptime(
                getattr(reaction, "box_top_source_time"), "%Y-%m-%d %H:%M:%S"
            )),
            "boxTop": str(getattr(reaction, "box_top")),
            "boxBottomSourceIndex": int(getattr(reaction, "box_bottom_source_idx")),
            "boxBottomSourceTime": epoch(datetime.strptime(
                getattr(reaction, "box_bottom_source_time"), "%Y-%m-%d %H:%M:%S"
            )),
            "boxBottom": str(getattr(reaction, "box_bottom")),
            "breakIndex": int(getattr(reaction, "break_idx")),
            "breakTime": epoch(
                detector.candles[int(getattr(reaction, "break_idx"))].timestamp
            ),
            "stopLevel": str(entry["stop_level"]),
            "stopSourceIndex": entry["stop_source_index"],
            "stopSourceTime": epoch(entry["stop_source_time"]),
            "stopHitIndex": crossed[0] if crossed is not None else None,
            "stopHitTime": epoch(crossed[1]) if crossed is not None else None,
            "stopHitEventTime": epoch(crossed[2]) if crossed is not None else None,
            "causes": supplied_causes,
        }
        merged[identity] = serialized
        output.append(serialized)
    return sorted(output, key=lambda item: (item["firstTime"], item["breakTime"]))


def visible_a_zones_after_s_stops(a_zones, s_zones, candles):
    """Suppress the A candle that contains an already-confirmed S stop.

    That candle is the S-stop/E transition candle. It may still carry the
    order box's BoxBottom, but it cannot receive a new A label.
    """
    times = [getattr(item, "timestamp") for item in candles]
    stop_indices = {
        bisect_left(times, getattr(item, "decision_event_time"))
        for item in s_zones
    }
    return [
        item for item in a_zones
        if int(getattr(item, "source_index")) not in stop_indices
    ]


def _module_priority(item):
    """Return the confirmed behavioral ownership priority.

    StopAll > E red > S red > E blue > S blue.  A is intentionally absent:
    this helper is used only after A has become an S candidate.
    """
    if hasattr(item, "stopped_behavior_type"):
        return 5
    if hasattr(item, "family"):
        return 4 if str(getattr(item, "family")).lower() == "red" else 2
    if hasattr(item, "a_source_time"):
        return 3 if str(getattr(item, "color")).lower() == "red" else 1
    return 0


def _module_identity(item):
    return (
        type(item).__name__,
        getattr(item, "family", getattr(item, "color", None)),
        getattr(item, "number", None),
        getattr(item, "source_time"),
        getattr(item, "source_index", None),
    )


def _module_stop_event(item, stop_event_finder=None):
    """Resolve the strict one-second stop event of an S/E/StopAll object."""
    explicit = getattr(item, "stop_event_time", None)
    if explicit is not None:
        return explicit
    if stop_event_finder is None:
        return None
    found = stop_event_finder(item)
    if found is None:
        return None
    if isinstance(found, tuple):
        return found[-1]
    return found


def _strictly_beyond_boundary(price, boundary, direction):
    return price < boundary if direction == "bullish" else price > boundary


def _dominant_module(modules):
    return max(
        modules,
        key=lambda item: (
            _module_priority(item),
            int(getattr(item, "number", 0)),
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    )


def split_a_zones_by_dominant_stops(
    a_zones, s_zones, e_zones, stopalls, candles, direction,
    stop_event_finder=None, trend_reactions=None, confirmation_finder=None,
):
    """Separate visible A labels from A objects allowed into downstream math.

    A/Reaction/Blue discovery remains independent inside every half-leg.  Once
    an accepted S/E/StopAll is strictly stopped, however, the main candle that
    contains that stop begins the next leg comparison.  An A whose source
    extreme is strictly beyond the highest-priority stopped owner is the
    leg-start candidate, but it cannot re-enter calculation as an equal or
    smaller behavior. That candidate consumes the closed owner for subsequent
    half-leg A discovery while remaining absent from the public output.

    Equality is deliberately valid.  Stop chronology is exact at one second,
    while leg ownership is assigned to the containing main candle.
    """
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    candle_times = [getattr(item, "timestamp") for item in candles]
    modules = sorted(
        [*s_zones, *e_zones, *stopalls],
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    )
    stopped = []
    for module in modules:
        stop_event = _module_stop_event(module, stop_event_finder)
        if stop_event is None:
            continue
        stop_index = bisect_right(candle_times, stop_event) - 1
        if stop_index < 0:
            continue
        stopped.append((module, stop_index, stop_event))

    valid = []
    invalid = []
    consumed = set()
    for a_zone in sorted(
        a_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ),
    ):
        source_index = int(getattr(a_zone, "source_index"))
        eligible = [
            module for module, stop_index, _stop_event in stopped
            if getattr(module, "source_time") < getattr(a_zone, "source_time")
            and stop_index <= source_index
            and _module_identity(module) not in consumed
        ]
        if not eligible:
            valid.append(a_zone)
            continue
        dominant = _dominant_module(eligible)
        crosses_dominant = _strictly_beyond_boundary(
            Decimal(str(getattr(a_zone, "price"))),
            Decimal(str(getattr(dominant, "price"))),
            direction,
        )
        if not crosses_dominant:
            valid.append(a_zone)
            continue

        # A confirmed bullish Reaction may establish a lower leg head inside
        # the closed owner's range before this A. Preserve that A as an
        # interior-leg behavior, while retaining the existing owner
        # consumption below. This is provenance-based and uses no fixture data.
        interior = False
        if (
            direction == "bullish"
            and trend_reactions is not None
            and confirmation_finder is not None
            and source_index > 0
            and getattr(a_zone, "reaction_first_time", None) is not None
        ):
            owner_stop = next(
                stop_event for module, stop_index, stop_event in stopped
                if _module_identity(module) == _module_identity(dominant)
            )
            owner_stop_index = bisect_right(candle_times, owner_stop) - 1
            first_red_index = bisect_right(
                candle_times, getattr(a_zone, "reaction_first_time")
            ) - 1
            if 0 <= owner_stop_index <= first_red_index < len(candles):
                head = min(
                    candles[owner_stop_index:first_red_index + 1],
                    key=lambda candle: Decimal(str(getattr(candle, "low"))),
                )
                if (
                    int(getattr(head, "index", -1)) < source_index
                    and Decimal(str(getattr(head, "low")))
                    < Decimal(str(getattr(a_zone, "price")))
                ):
                    interior = any(
                        int(getattr(reaction, "first_idx"))
                        >= int(getattr(head, "index"))
                        and int(getattr(reaction, "first_idx"))
                        <= first_red_index
                        and int(getattr(reaction, "break_idx")) < source_index
                        and confirmation_finder(reaction, direction)
                        < getattr(a_zone, "source_time")
                        for reaction in trend_reactions
                    )
        if interior:
            valid.append(a_zone)
            # Continue into the common consumption logic below.
            dominant_priority = _module_priority(dominant)
            for module in eligible:
                if _module_priority(module) <= dominant_priority:
                    consumed.add(_module_identity(module))
            continue

        invalid.append(a_zone)
        dominant_priority = _module_priority(dominant)
        for module in eligible:
            if _module_priority(module) <= dominant_priority:
                consumed.add(_module_identity(module))
    return valid, invalid


def blocked_orders_while_invalid_leg_heads_are_live(
    invalid_a_zones, opposite_reactions, candles, direction, stop_finder,
):
    """Return order First times owned by a still-live invalid leg head.

    A strict dominant-boundary crossing can expose a new leg head without
    making its A calculation-valid. Until that head itself stops, an internal
    opposite Reaction cannot take over the larger owner's resumed E space.
    """
    if direction != "bullish":
        return set()
    blocked = set()
    for a_zone in invalid_a_zones:
        stop = stop_finder(a_zone)
        if stop is None:
            continue
        stop_event = stop[2]
        source_time = getattr(a_zone, "source_time")
        for reaction in opposite_reactions:
            first_time = getattr(candles[int(getattr(reaction, "first_idx"))], "timestamp")
            if source_time <= first_time < stop_event:
                blocked.add(first_time)
    return blocked


def _s_zones_for_module_engines(s_zones, e_zones, direction):
    """Preserve the established S eligibility contract consumed by E/StopAll."""
    ordered_e = sorted(e_zones, key=lambda item: getattr(item, "source_time"))
    visible = []
    for s_zone in sorted(s_zones, key=lambda item: getattr(item, "source_time")):
        prior_modules = [
            item for item in [*ordered_e, *visible]
            if getattr(item, "source_time") < getattr(s_zone, "source_time")
        ]
        if prior_modules:
            prior = max(prior_modules, key=lambda item: getattr(item, "source_time"))
            if getattr(s_zone, "a_source_time") < getattr(prior, "source_time"):
                continue
            boundary = Decimal(str(getattr(prior, "price")))
            if _strictly_beyond_boundary(
                Decimal(str(getattr(s_zone, "a_price"))), boundary, direction
            ):
                continue
            if _strictly_beyond_boundary(
                Decimal(str(getattr(s_zone, "price"))), boundary, direction
            ):
                continue
        visible.append(s_zone)
    return visible


def visible_s_zones_after_module_resets(
    s_zones, e_zones, direction, stop_event_finder=None, source_event_finder=None,
):
    """Apply dominant-behavior ownership to successive S candidates.

    Bullish/bearish half-leg calculations remain active under a larger
    behavior.  But once the currently dominant S/E/StopAll and the candidate
    S's parent A have both stopped, that A belongs to the next larger module
    lifecycle.  The would-be S is therefore consumed, while its historical
    inputs remain available for chart rendering and audits.
    """
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    ordered_external = sorted(
        e_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    )
    visible = []
    consumed = set()
    for s_zone in sorted(
        s_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    ):
        a_stop_event = getattr(s_zone, "a_stop_event_time", None)
        ownership_event = a_stop_event
        if direction == "bullish":
            # The larger head may stop while the internal S search is open,
            # after A stops but before the candidate's own extreme forms.
            # A later stop after that extreme must not rewrite its ownership.
            ownership_event = (
                source_event_finder(s_zone) if source_event_finder is not None
                else getattr(s_zone, "source_time")
            )
        prior_modules = [
            item for item in [*ordered_external, *visible]
            if getattr(item, "source_time") < getattr(s_zone, "source_time")
            and _module_identity(item) not in consumed
        ]
        if prior_modules and ownership_event is not None:
            stopped_prior = [
                module for module in prior_modules
                if (
                    module_stop := _module_stop_event(module, stop_event_finder)
                ) is not None
                and module_stop <= ownership_event
            ]
            if stopped_prior:
                dominant = _dominant_module(stopped_prior)
                # A stopped owner advances the lifecycle only when the new S
                # is itself the strict directional extreme of that leg.
                # Equality belongs to the earlier owner and remains valid.
                if not _strictly_beyond_boundary(
                    Decimal(str(getattr(s_zone, "price"))),
                    Decimal(str(getattr(dominant, "price"))),
                    direction,
                ):
                    visible.append(s_zone)
                    continue
                # All lower/equal stopped owners involved in this transition
                # leave subsequent calculation ownership together.  The
                # highest-priority object determines the next module number.
                dominant_priority = _module_priority(dominant)
                for module in stopped_prior:
                    module_stop = _module_stop_event(module, stop_event_finder)
                    if (
                        _module_priority(module) <= dominant_priority
                    ):
                        consumed.add(_module_identity(module))
                continue
        # An active larger behavior does not disable the independent A/S
        # lifecycle inside the current half-leg.
        visible.append(s_zone)
    return visible


def _a_zones_for_module_engines(a_zones, s_zones, e_zones, direction):
    """Preserve established A eligibility for S/E order-ledger ownership."""
    modules = sorted(
        [*s_zones, *e_zones],
        key=lambda item: (
            getattr(item, "source_time"), int(getattr(item, "source_index")),
        ),
    )
    valid = []
    for a_zone in sorted(
        a_zones,
        key=lambda item: (
            getattr(item, "source_time"), int(getattr(item, "source_index")),
        ),
    ):
        prior = None
        for module in modules:
            if getattr(module, "source_time") <= getattr(a_zone, "source_time"):
                prior = module
            else:
                break
        if prior is not None:
            provenance_times = (
                getattr(a_zone, "blue_1_source_time"),
                getattr(a_zone, "blue_2_source_time"),
                getattr(a_zone, "continuation_source_time"),
                getattr(a_zone, "reaction_first_time"),
            )
            if min(provenance_times) < getattr(prior, "source_time"):
                continue
            if _strictly_beyond_boundary(
                Decimal(str(getattr(a_zone, "price"))),
                Decimal(str(getattr(prior, "price"))),
                direction,
            ):
                continue
        valid.append(a_zone)
    return valid


def reconcile_stopall_lifecycle(detector, stopall_engine, s_zones, e_zones,
                                candles, seconds, timeframe, direction, timed_step=None):
    """Feed accepted reset boundaries back into authoritative E ownership.

    Geometry and eligible orders remain owned by E. Reconcile until both
    stages agree; a cycle is an error, never a partially corrected payload.
    """
    seen = set()
    pass_number = 1
    measure = timed_step or (lambda _label, work: work())
    while True:
        visible_s = measure(
            f"Reconcile S visibility - {direction.title()} - pass {pass_number}",
            lambda: _s_zones_for_module_engines(s_zones, e_zones, direction),
        )
        stopalls = measure(
            f"StopAll - {direction.title()} - pass {pass_number}",
            lambda: stopall_engine.detect_stopalls(
                direction, visible_s, e_zones, candles, seconds, timeframe,
            ),
        )
        resets = {item.source_time: item.number for item in stopalls}
        if resets == detector.sequence_resets:
            return e_zones, stopalls
        identity = tuple(sorted(resets.items()))
        if identity in seen:
            raise ValueError("E/StopAll lifecycle reconciliation did not converge")
        seen.add(identity)
        detector.sequence_resets = resets
        e_zones = measure(
            f"E - {direction.title()} - StopAll reconciliation {pass_number}",
            detector.detect,
        )
        pass_number += 1


def visible_a_zones_after_module_boundaries(
    a_zones, s_zones, e_zones, direction, stop_event_finder=None,
):
    """Require A provenance to rebuild after the dominant strict stop.

    A price is deliberately not compared with the old module price.  Reactions
    and Blue Lines remain valid inside every half-leg; only provenance that
    straddles the dominant stop belongs to the closed lifecycle.
    """
    del direction  # Exact-stop ownership is directionally mirrored.
    modules = sorted(
        [*s_zones, *e_zones],
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ),
    )
    valid = []
    for a_zone in sorted(
        a_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ),
    ):
        stopped_prior = [
            module for module in modules
            if getattr(module, "source_time") <= getattr(a_zone, "source_time")
            and (
                stop_event := _module_stop_event(module, stop_event_finder)
            ) is not None
            and stop_event <= getattr(a_zone, "source_time")
        ]
        if stopped_prior:
            dominant = _dominant_module(stopped_prior)
            boundary_event = _module_stop_event(dominant, stop_event_finder)
            provenance_times = (
                getattr(a_zone, "blue_1_source_time"),
                getattr(a_zone, "blue_2_source_time"),
                getattr(a_zone, "continuation_source_time"),
                getattr(a_zone, "reaction_first_time"),
            )
            if min(provenance_times) < boundary_event:
                continue
        valid.append(a_zone)
    return valid


def main() -> int:
    bridge_started = perf_counter()
    timings: dict[str, float] = {}
    validation_started = perf_counter()
    emit_progress("started", "Validate request")
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--blue-engine", type=Path, required=True)
    parser.add_argument("--a-engine", type=Path, required=True)
    parser.add_argument("--s-engine", type=Path, required=True)
    parser.add_argument("--e-engine", type=Path, required=False)
    parser.add_argument("--stopall-engine", type=Path, required=False)
    parser.add_argument("--blue-lines", choices=("enabled", "disabled"), default="enabled")
    parser.add_argument("--a-zones", choices=("enabled", "disabled"), default="enabled")
    parser.add_argument("--s-zones", choices=("enabled", "disabled"), default="enabled")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--timeframe", type=int, required=True)
    parser.add_argument("--from-time", type=int, required=True)
    parser.add_argument("--to-time", type=int, required=True)
    parser.add_argument("--direction", choices=("bullish", "bearish", "both"), required=True)
    args = parser.parse_args()
    if args.timeframe < 1:
        raise ValueError("Timeframe must be at least one second.")
    validation_ms = (perf_counter() - validation_started) * 1000
    timings["Validate request"] = validation_ms
    emit_progress("completed", "Validate request", validation_ms)
    source_text = timed(
        timings, "Read source file", lambda: args.data.read_text(encoding="utf-8-sig")
    )
    source_rows = timed(timings, "Parse source JSON", lambda: orjson.loads(source_text))
    range_end_exclusive = args.to_time + args.timeframe
    rows = timed(timings, "Filter raw range", lambda: [
        row for row in source_rows
        if args.from_time <= int(row["time"]) < range_end_exclusive
    ])
    if not rows:
        raise ValueError("The selected range contains no raw candles.")
    engine = timed(timings, "Load Reaction engine", lambda: load_engine(args.engine))
    blue_engine = timed(timings, "Load Blue Line engine", lambda: load_module("blue_line_engine", args.blue_engine))
    a_engine = timed(timings, "Load A engine", lambda: load_module("a_zone_engine", args.a_engine))
    s_engine = timed(timings, "Load S engine", lambda: load_module("s_zone_engine", args.s_engine))
    e_engine = (
        timed(timings, "Load E engine", lambda: load_module("e_zone_engine", args.e_engine))
        if args.e_engine is not None
        else None
    )
    stopall_engine = (
        timed(timings, "Load StopAll engine", lambda: load_module("stopall_engine", args.stopall_engine))
        if args.stopall_engine is not None else None
    )
    second_buckets, timeframe_buckets = timed(
        timings, "Normalize raw candles", lambda: build_candle_buckets(rows, args.timeframe)
    )
    seconds = timed(
        timings, "Build lower candle views", lambda: build_candle_objects(engine, second_buckets)
    )
    candles = seconds if args.timeframe == 1 else timed(
        timings, "Build timeframe candle views", lambda: build_candle_objects(engine, timeframe_buckets)
    )
    eligible = timed(timings, "Select candle range", lambda: [
        i for i, c in enumerate(candles)
        if args.from_time <= epoch(c.timestamp) <= args.to_time
    ])
    if not eligible:
        raise ValueError("The selected range contains no candles at this timeframe.")
    start_index, end_index = eligible[0], eligible[-1]
    initial_bullish_order_geometry = bullish_a_stop_order_finder(engine, candles, seconds)
    directions = ("bullish", "bearish") if args.direction == "both" else (args.direction,)
    required_directions = (
        ("bullish", "bearish")
        if args.s_zones == "enabled"
        else directions
    )
    # E already builds a full-range geometry pipeline. When the selected output
    # covers that exact same candle window, its Reaction/Blue/A values are the
    # same objects the presentation pass would otherwise calculate again.
    # Preserve the independent legacy path for every partial-window request.
    reusable_full_context = (
        e_engine is not None
        and args.s_zones == "enabled"
        and end_index == len(candles) - 1
    )
    results = {} if reusable_full_context else {
        direction: timed(
            timings,
            f"Reaction • {direction.title()}",
            lambda direction=direction: engine.UnifiedReactionDetector(
                candles, seconds, start_index, end_index, direction
            ).detect(),
        )
        for direction in required_directions
    }
    full_e_zones = {}
    full_e_detectors = {}
    full_s_detectors = {}
    full_lines_by_direction = {}
    full_a_by_direction = {}
    invalid_a_identities_by_direction = {}
    invalid_s_identities_by_direction = {}
    full_s_by_direction = {}
    full_s_candidates_by_direction = {}
    if e_engine is not None and args.s_zones == "enabled":
        geometry_detectors = {
            direction: engine.UnifiedReactionDetector(
                candles, seconds, 0, len(candles) - 1, direction
            )
            for direction in ("bullish", "bearish")
        }
        full_results = {
            direction: timed(
                timings, f"Reaction geometry • {direction.title()}", detector.detect
            )
            for direction, detector in geometry_detectors.items()
        }
        if reusable_full_context:
            _has_extra = False
            for _dir in required_directions:
                for _r in full_results[_dir].reactions:
                    if int(getattr(_r, "first_idx")) < start_index:
                        _has_extra = True
                        break
                if _has_extra:
                    break
            if not _has_extra:
                for _dir in required_directions:
                    for _r in full_results[_dir].resets:
                        if int(getattr(_r, "from_first_idx")) < start_index:
                            _has_extra = True
                            break
                    if _has_extra:
                        break
            if _has_extra:
                reusable_full_context = False
                results = {
                    direction: timed(
                        timings,
                        f"Reaction • {direction.title()}",
                        lambda direction=direction: engine.UnifiedReactionDetector(
                            candles, seconds, start_index, end_index, direction
                        ).detect(),
                    )
                    for direction in required_directions
                }
            else:
                results = full_results
        for direction in directions:
            opposite = "bearish" if direction == "bullish" else "bullish"
            full_lines = timed(timings, f"Blue Line • {direction.title()}", lambda: blue_engine.detect_blue_lines(
                direction,
                full_results[direction].reactions,
                candles,
                seconds,
                args.timeframe,
                full_results[direction].resets,
            ))
            full_a = timed(timings, f"A • {direction.title()}", lambda: a_engine.detect_a_zones(
                direction,
                full_results[direction].reactions,
                full_lines,
                candles,
                seconds,
                args.timeframe,
            ))
            full_lines_by_direction[direction] = full_lines
            full_a_by_direction[direction] = full_a
            full_s_detector = s_engine.SDetector(
                direction,
                full_results[direction].reactions,
                full_results[opposite].reactions,
                full_lines,
                full_a,
                candles,
                seconds,
                args.timeframe,
                0,
                len(candles) - 1,
                full_results[opposite].resets,
                initial_order_geometry=(
                    initial_bullish_order_geometry if direction == "bullish" else None
                ),
            )
            full_s = timed(timings, f"S • {direction.title()}", full_s_detector.detect)
            full_s_candidates_by_direction[direction] = list(full_s)
            full_s_detectors[direction] = full_s_detector
            full_e_detector = e_engine.EDetector(
                direction,
                full_results[direction].reactions,
                full_results[opposite].reactions,
                full_s,
                full_results[direction].resets,
                full_results[opposite].resets,
                candles,
                seconds,
                args.timeframe,
                0,
                len(candles) - 1,
                lambda geometry_direction, geometry_start, geometry_end: (
                    geometry_detectors[geometry_direction]._first_geometry_after_reset(
                        geometry_direction,
                        max(0, geometry_start - 1),
                        geometry_end,
                    )
                ),
                lambda geometry_direction, geometry_start, geometry_end, gate_event: (
                    geometry_detectors[geometry_direction].first_order_reaction_after_gate(
                        geometry_direction,
                        geometry_start,
                        geometry_end,
                        gate_event,
                    )
                ),
                initial_order_audit=full_s_detector.order_audit,
                reset_geometry_finder=(
                    lambda geometry_direction, reset_index, gate_index, geometry_end: (
                        geometry_detectors[geometry_direction].first_simple_geometry_after_gate(
                            geometry_direction,
                            reset_index,
                            gate_index,
                            geometry_end,
                        )
                    )
                ),
            )
            preliminary_e = timed(timings, f"E • {direction.title()} • initial", full_e_detector.detect)
            valid_full_s = _s_zones_for_module_engines(
                full_s, preliminary_e, direction
            )
            if len(valid_full_s) != len(full_s):
                full_e_detector = e_engine.EDetector(
                    direction,
                    full_results[direction].reactions,
                    full_results[opposite].reactions,
                    valid_full_s,
                    full_results[direction].resets,
                    full_results[opposite].resets,
                    candles,
                    seconds,
                    args.timeframe,
                    0,
                    len(candles) - 1,
                    lambda geometry_direction, geometry_start, geometry_end: (
                        geometry_detectors[geometry_direction]._first_geometry_after_reset(
                            geometry_direction,
                            max(0, geometry_start - 1),
                            geometry_end,
                        )
                    ),
                    lambda geometry_direction, geometry_start, geometry_end, gate_event: (
                        geometry_detectors[geometry_direction].first_order_reaction_after_gate(
                            geometry_direction,
                            geometry_start,
                            geometry_end,
                            gate_event,
                        )
                    ),
                    blocked_order_first_times={
                        getattr(item, "source_time")
                        for item in full_s if item not in valid_full_s
                    },
                    initial_order_audit=full_s_detector.order_audit,
                    reset_geometry_finder=(
                        lambda geometry_direction, reset_index, gate_index, geometry_end: (
                            geometry_detectors[geometry_direction].first_simple_geometry_after_gate(
                                geometry_direction,
                                reset_index,
                                gate_index,
                                geometry_end,
                            )
                        )
                    ),
                )
                preliminary_e = timed(timings, f"E • {direction.title()} • S reconciliation", full_e_detector.detect)
                full_s = valid_full_s
            leg_candidate_a = s_engine.visible_a_zones(
                full_s_detector.eligible_a_zones, full_s
            )
            leg_candidate_a = visible_a_zones_after_s_stops(
                leg_candidate_a, full_s, candles
            )
            calculation_a, invalid_a = split_a_zones_by_dominant_stops(
                leg_candidate_a,
                full_s_candidates_by_direction[direction],
                preliminary_e,
                [],
                candles,
                direction,
                lambda item: full_e_detector._parent_stop(
                    "S" if hasattr(item, "a_source_time") else "E", item
                ),
                trend_reactions=(
                    full_s_detector.trend_reactions if direction == "bullish" else None
                ),
                confirmation_finder=(
                    full_s_detector._reaction_confirmation_time
                    if direction == "bullish" else None
                ),
            )
            invalid_a_identities = {
                (getattr(item, "source_time"), int(getattr(item, "source_index")))
                for item in invalid_a
            }
            invalid_a_identities_by_direction[direction] = invalid_a_identities
            invalid_a_source_times = {
                source_time for source_time, _source_index in invalid_a_identities
            }
            invalid_s = [
                item for item in full_s_candidates_by_direction[direction]
                if getattr(item, "a_source_time") in invalid_a_source_times
            ]
            invalid_s_identities = {
                (getattr(item, "source_time"), int(getattr(item, "source_index")))
                for item in invalid_s
            }
            invalid_s_identities_by_direction[direction] = invalid_s_identities
            accepted_a_sources = {
                getattr(item, "source_time")
                for item in _a_zones_for_module_engines(
                    full_s_detector.eligible_a_zones, full_s, preliminary_e, direction
                )
            }
            accepted_initial_orders = {
                key: value
                for key, value in full_s_detector.order_audit.items()
                if value["a_source_time"] in accepted_a_sources
            }
            blocked_order_first_times = set(
                getattr(full_e_detector, "blocked_order_first_times", set())
            )
            pending_s_a_sources = {
                getattr(item, "a_source_time")
                for item in full_s_candidates_by_direction[direction]
            }
            blocked_order_first_times.update(
                blocked_orders_while_invalid_leg_heads_are_live(
                    [
                        item for item in invalid_a
                        if getattr(item, "source_time") in pending_s_a_sources
                    ],
                    full_results[opposite].reactions,
                    candles,
                    direction,
                    lambda item: full_s_detector._first_a_stop(
                        Decimal(str(getattr(item, "price"))),
                        getattr(item, "source_time"),
                    ),
                )
            )
            full_e_detector = e_engine.EDetector(
                direction,
                full_results[direction].reactions,
                full_results[opposite].reactions,
                full_s,
                full_results[direction].resets,
                full_results[opposite].resets,
                candles,
                seconds,
                args.timeframe,
                0,
                len(candles) - 1,
                lambda geometry_direction, geometry_start, geometry_end: (
                    geometry_detectors[geometry_direction]._first_geometry_after_reset(
                        geometry_direction,
                        max(0, geometry_start - 1),
                        geometry_end,
                    )
                ),
                lambda geometry_direction, geometry_start, geometry_end, gate_event: (
                    geometry_detectors[geometry_direction].first_order_reaction_after_gate(
                        geometry_direction,
                        geometry_start,
                        geometry_end,
                        gate_event,
                    )
                ),
                blocked_order_first_times=blocked_order_first_times,
                initial_order_audit=accepted_initial_orders,
                reset_geometry_finder=(
                    lambda geometry_direction, reset_index, gate_index, geometry_end: (
                        geometry_detectors[geometry_direction].first_simple_geometry_after_gate(
                            geometry_direction,
                            reset_index,
                            gate_index,
                            geometry_end,
                        )
                    )
                ),
            )
            preliminary_e = timed(timings, f"E • {direction.title()} • final audit", full_e_detector.detect)
            full_s = [
                item for item in full_s
                if (
                    getattr(item, "source_time"), int(getattr(item, "source_index"))
                ) not in invalid_s_identities
            ]
            full_e_zones[direction] = preliminary_e
            full_e_detectors[direction] = full_e_detector
            # For a full-window request E's upstream S pass is also the
            # presentation S pass. Keep its final, reset-filtered result so
            # the payload phase does not execute S (and its A eligibility
            # derivation) a second time.
            full_s_by_direction[direction] = full_s
            accepted_a_sources = {
                getattr(item, "source_time")
                for item in _a_zones_for_module_engines(
                    full_s_detector.eligible_a_zones, full_s, preliminary_e, direction
                )
            } - invalid_a_source_times
            full_s_detector.order_audit = {
                key: value
                for key, value in full_s_detector.order_audit.items()
                if value["a_source_time"] in accepted_a_sources
            }
    payload = {"engine": "reaction-detector/Reaction-detection-new.py", "version": engine.ENGINE_VERSION, "blueLineVersion": "2.0.1", "aVersion": a_engine.A_VERSION, "sVersion": s_engine.S_VERSION, "eVersion": e_engine.E_VERSION if e_engine else None, "stopAllVersion": stopall_engine.STOPALL_VERSION if stopall_engine else None, "blueLinesEnabled": args.blue_lines == "enabled", "aEnabled": args.a_zones == "enabled", "sEnabled": args.s_zones == "enabled", "eEnabled": e_engine is not None and args.s_zones == "enabled", "stopAllEnabled": stopall_engine is not None and e_engine is not None and args.s_zones == "enabled", "timeframe": args.timeframe, "actualFrom": epoch(candles[start_index].timestamp), "actualTo": epoch(candles[end_index].timestamp), "directions": {}}
    for direction in directions:
        result = results[direction]
        reactions, resets = timed(
            timings, f"Serialize Reaction - {direction.title()}", lambda: serialize(result)
        )
        requires_blue_lines = (
            args.blue_lines == "enabled"
            or args.a_zones == "enabled"
            or args.s_zones == "enabled"
        )
        all_blue_lines = (
            full_lines_by_direction[direction]
            if reusable_full_context and requires_blue_lines
            else timed(timings, f"Blue Line - {direction.title()}", lambda: blue_engine.detect_blue_lines(
                direction, result.reactions, candles, seconds, args.timeframe,
                result.resets,
            )) if requires_blue_lines else []
        )
        requires_a_zones = args.a_zones == "enabled" or args.s_zones == "enabled"
        all_a_zones = (
            full_a_by_direction[direction]
            if reusable_full_context and requires_a_zones
            else timed(timings, f"A - {direction.title()}", lambda: a_engine.detect_a_zones(
                direction,
                result.reactions,
                all_blue_lines,
                candles,
                seconds,
                args.timeframe,
            )) if requires_a_zones else []
        )
        opposite = "bearish" if direction == "bullish" else "bullish"
        s_zones = []
        accepted_s_zones = []
        if args.s_zones == "enabled":
            if reusable_full_context:
                # Preserve all candidates so ownership filtering is idempotent
                # across the E/StopAll reconciliation passes. E consumes the
                # already accepted subset kept separately below.
                s_zones = full_s_candidates_by_direction[direction]
                accepted_s_zones = full_s_by_direction[direction]
                all_a_zones = full_s_detectors[direction].eligible_a_zones
            else:
                s_detector = s_engine.SDetector(
                    direction,
                    result.reactions,
                    results[opposite].reactions,
                    all_blue_lines,
                    all_a_zones,
                    candles,
                    seconds,
                    args.timeframe,
                    start_index,
                    end_index,
                    results[opposite].resets,
                    initial_order_geometry=(
                        initial_bullish_order_geometry if direction == "bullish" else None
                    ),
                )
                s_zones = timed(timings, f"S - {direction.title()}", s_detector.detect)
                accepted_s_zones = s_zones
                all_a_zones = s_detector.eligible_a_zones
        visible_a_zones = s_engine.visible_a_zones(all_a_zones, accepted_s_zones)
        visible_a_zones = visible_a_zones_after_s_stops(
            visible_a_zones, accepted_s_zones, candles
        )
        e_zones = [
            item for item in full_e_zones.get(direction, [])
            if start_index <= int(getattr(item, "source_index")) <= end_index
        ]
        stopalls = []
        if stopall_engine is not None and direction in full_e_detectors:
            e_zones, stopalls = reconcile_stopall_lifecycle(
                full_e_detectors[direction], stopall_engine, accepted_s_zones, e_zones,
                candles, seconds, args.timeframe, direction,
                lambda label, work: timed(timings, label, work),
            )
        def finalize_visibility():
            stopall_source_indices = {item.source_index for item in stopalls}
            final_e_zones = [
                item for item in e_zones
                if int(getattr(item, "source_index")) not in stopall_source_indices
            ]
            e_source_indices = {
                int(getattr(item, "source_index")) for item in final_e_zones
            }
            final_s_zones = visible_s_zones_after_module_resets(
                s_zones, [*final_e_zones, *stopalls], direction,
                lambda item: full_e_detectors[direction]._parent_stop(
                    "S" if hasattr(item, "a_source_time") else "E", item
                ),
                source_event_finder=(
                    lambda item: full_s_detectors[direction]._candidate_event_time(
                        item.source_index, item.price, item.source_time
                    )
                ) if direction == "bullish" else None,
            )
            # Presentation is a lineage closure over accepted calculations.
            # If a final E explicitly references an S parent, that historical
            # S must remain available to the chart even when it no longer owns
            # downstream lifecycle calculation. Transition-only S candidates
            # have no final child reference and remain filtered.
            referenced_s_sources = {
                getattr(item, "parent_source_time")
                for item in final_e_zones
                if str(getattr(item, "parent_type", "")).upper() == "S"
            }
            final_s_identities = {_module_identity(item) for item in final_s_zones}
            final_s_zones.extend(
                item for item in s_zones
                if getattr(item, "source_time") in referenced_s_sources
                and _module_identity(item) not in final_s_identities
            )
            final_s_zones.sort(key=lambda item: (
                getattr(item, "source_time"), int(getattr(item, "source_index"))
            ))
            final_a_zones = visible_a_zones_after_module_boundaries(
                visible_a_zones, final_s_zones, [*final_e_zones, *stopalls], direction,
                lambda item: full_e_detectors[direction]._parent_stop(
                    "S" if hasattr(item, "a_source_time") else "E", item
                ),
            )
            referenced_a_sources = {
                getattr(item, "a_source_time") for item in final_s_zones
            }
            final_a_identities = {
                (getattr(item, "source_time"), int(getattr(item, "source_index")))
                for item in final_a_zones
            }
            final_a_zones.extend(
                item for item in all_a_zones
                if getattr(item, "source_time") in referenced_a_sources
                and (
                    getattr(item, "source_time"), int(getattr(item, "source_index"))
                ) not in final_a_identities
            )
            final_a_zones.sort(key=lambda item: (
                getattr(item, "source_time"), int(getattr(item, "source_index"))
            ))
            final_a_zones = [
                item for item in final_a_zones
                if int(getattr(item, "source_index")) not in e_source_indices | stopall_source_indices
            ]
            final_s_zones = [
                item for item in final_s_zones
                if int(getattr(item, "source_index")) not in e_source_indices | stopall_source_indices
                and (
                    getattr(item, "source_time"), int(getattr(item, "source_index"))
                ) not in invalid_s_identities_by_direction.get(direction, set())
            ]
            return final_e_zones, final_s_zones, final_a_zones

        e_zones, visible_s_zones, visible_a_zones = timed(
            timings, f"Apply visibility filters - {direction.title()}", finalize_visibility
        )
        invalid_a_identities = invalid_a_identities_by_direction.get(direction, set())
        display_a_zones = [
            item for item in visible_a_zones
            if (
                getattr(item, "source_time"), int(getattr(item, "source_index"))
            ) not in invalid_a_identities
        ]
        invalid_s_identities = invalid_s_identities_by_direction.get(direction, set())
        display_s_zones = [
            item for item in visible_s_zones
            if (
                getattr(item, "source_time"), int(getattr(item, "source_index"))
            ) not in invalid_s_identities
        ]
        def serialize_direction():
            return {
                "reactions": reactions,
                "resets": resets,
                "blueLines": serialize_blue_lines(
                    all_blue_lines if args.blue_lines == "enabled" else []
                ),
                "aZones": serialize_a_zones(
                    display_a_zones if args.a_zones == "enabled" else [],
                    invalid_a_identities,
                ),
                "sZones": serialize_s_zones(display_s_zones, invalid_s_identities),
                "eZones": serialize_e_zones(e_zones),
                "stopAlls": serialize_stopalls(stopalls),
                "orderAudit": (
                    serialize_order_audit(
                        full_e_detectors[direction], start_index, end_index,
                        full_s_detectors.get(direction),
                    )
                    if direction in full_e_detectors else []
                ),
            }

        payload["directions"][direction] = timed(
            timings, f"Serialize output - {direction.title()}", serialize_direction
        )
    payload["timings"] = {
        "phasesMs": {label: round(duration, 2) for label, duration in timings.items()},
        "bridgeTotalMs": round((perf_counter() - bridge_started) * 1000, 2),
    }
    emit_progress("completed", "Calculation pipeline", (perf_counter() - bridge_started) * 1000)
    encoding_started = perf_counter()
    encoded_payload = json.dumps(payload, separators=(",", ":"))
    emit_progress("completed", "Encode response JSON", (perf_counter() - encoding_started) * 1000)
    print(encoded_payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        raise SystemExit(1)
