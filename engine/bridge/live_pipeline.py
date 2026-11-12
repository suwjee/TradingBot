"""Stateful market and detector continuation for the existing indicator pipeline."""

from __future__ import annotations

from bisect import bisect_left
from collections import defaultdict
from copy import copy
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import sys
from time import perf_counter

from trading_pipeline import (
    LiveMarketBuckets, MarketContext, build_candle_objects, build_response_payload,
    load_engines, parse_arguments, prepare_pipeline_state,
)
from order_audit_engine import LiveOrderBResetLegs


LIVE_PIPELINE_VERSION = "1.0.1"


def _blue_dependencies(result):
    resets = defaultdict(list)
    for item in result.resets:
        resets[item.from_first_idx].append(item)
    return [repr((item, resets[item.first_idx])) for item in result.reactions]


class LivePipelineStages:
    """Own stage state for one independently clocked calculation regime."""

    def __init__(self, engines):
        self.engines = engines
        self._reactions = {}
        self._reaction_inputs = {}
        self._order_gates = {}
        self._previous_order_gates = {}
        self._gate_dirty = {}
        self._ownership = None
        self._blue = {}
        self._blue_inputs = {}
        self._a = {}
        self._s = {}
        self._stopall = {}
        self._order_b = {}
        self._primary = {}
        self._primary_ledger = {}
        self._primary_dependencies = {}
        self._setup = None
        self._active_regimes = {}
        self._closed_regimes = {}
        self._used_regimes = set()
        self._committed_main = self._committed_lower = 0
        self.e_continuation = engines.e_zone.LiveEContinuation()

    def begin(self, market, first_dirty_main):
        self._market = market
        self.first_dirty_main = first_dirty_main
        self._used_regimes.clear()
        self._previous_order_gates, self._order_gates = self._order_gates, {}
        self.e_continuation.advance(market.chronology, first_dirty_main=first_dirty_main)

    def _dirty_absolute(self):
        return self._market.index_offset + self.first_dirty_main

    def closed_regime(self, direction, context, boundary, work):
        end = context.index_offset + boundary
        key = (direction, context.index_offset, end, context.start_index,
               min(context.end_index, boundary - 1))
        self._used_regimes.add(key)
        if key not in self._closed_regimes or self._dirty_absolute() < end:
            self._closed_regimes[key] = work()
        return self._closed_regimes[key]

    def active_regime(self, context, direction):
        key = (direction, context.index_offset)
        self._used_regimes.add(key)
        dirty = max(0, min(len(context.candles), self._dirty_absolute() - context.index_offset))
        stage = self._active_regimes.get(key)
        if stage is None or dirty < stage._committed_main:
            stage = self._active_regimes[key] = LivePipelineStages(self.engines)
            dirty = 0
        stage.begin(context, dirty)
        return stage

    def finish_regimes(self):
        self._active_regimes = {key: value for key, value in self._active_regimes.items() if key in self._used_regimes}
        self._closed_regimes = {key: value for key, value in self._closed_regimes.items() if key in self._used_regimes}

    def reactions(self, detectors):
        engine = self.engines.reaction
        market = self._market
        chronology = market.chronology
        timeframe = int(chronology.timeframe.total_seconds())
        committed_main = len(market.candles) - 1
        if committed_main < 2:
            results = {direction: detector.detect() for direction, detector in detectors.items()}
            self._update_order_dependencies(results)
            return results
        if self.first_dirty_main < self._committed_main:
            raise ValueError("Previously committed Reaction candles were revised.")
        committed_lower = bisect_left(chronology.second_times, chronology.times[committed_main])
        new_main = market.candles[self._committed_main:committed_main]
        new_lower = market.seconds[self._committed_lower:committed_lower]
        preview_main = market.candles[committed_main:]
        preview_lower = market.seconds[committed_lower:]
        results = {}
        for direction, detector in detectors.items():
            stage = self._reactions.get(direction)
            if stage is None:
                stage = self._reactions[direction] = engine.LiveReactionContinuation(
                    new_main, new_lower, direction, timeframe_seconds=timeframe,
                    initial_bullish_trend=market.initial_bullish_trend and direction == "bullish",
                    initial_bearish_trend=market.initial_bearish_trend and direction == "bearish",
                )
            else:
                stage.advance(new_main, new_lower)
            result = results[direction] = stage.preview(preview_main, preview_lower)
            # The bounded native Order_A finder reads the accepted continuous
            # Reaction context from this detector.
            detector.all_reactions[direction] = result.reactions
            detector.all_resets[direction] = result.resets
        self._committed_main, self._committed_lower = committed_main, committed_lower
        self._update_order_dependencies(results)
        return results

    def _update_order_dependencies(self, results):
        for direction, result in results.items():
            current = (
                [(repr(item), item.break_idx) for item in result.reactions],
                {(repr(item), item.index) for item in result.resets},
            )
            previous = self._reaction_inputs.get(direction)
            dirty = self.first_dirty_main
            if previous is not None:
                for before, after in zip(previous[0], current[0]):
                    if before != after:
                        dirty = min(dirty, before[1], after[1])
                        break
                shared = min(len(previous[0]), len(current[0]))
                for sequence in (previous[0], current[0]):
                    if shared < len(sequence):
                        dirty = min(dirty, sequence[shared][1])
                for _, index in previous[1] ^ current[1]:
                    dirty = min(dirty, index)
            self._reaction_inputs[direction] = current
            self._gate_dirty[direction] = dirty

    def order_geometry(self, detector, direction, gate, limit, event):
        key = (direction, gate, event)
        current = self._order_gates.get(key)
        if current is None:
            previous = self._previous_order_gates.get(key)
            if previous is not None and previous.break_idx < self._gate_dirty[direction]:
                current = previous
        if current is not None and gate < limit and current.break_idx <= limit:
            self._order_gates[key] = current
            return replace(current)
        result = detector.first_order_reaction_after_gate(direction, gate, limit, event)
        if result is not None and len(self._order_gates) < 32_768:
            self._order_gates[key] = replace(result)
        return result

    def ownership(self, results):
        chronology = self._market.chronology
        if self._ownership is None:
            self._ownership = self.engines.reaction.LiveBehaviorReactionViews(results, chronology)
            return {
                direction: {(item.first_idx, item.break_idx) for item in group.reactions if item.behavior_internal}
                for direction, group in results.items()
            }
        return self._ownership.update(results, chronology, first_dirty_main=self.first_dirty_main)[2]

    def blue_lines(self, direction, result):
        chronology = self._market.chronology
        stage = self._blue.get(direction)
        current = _blue_dependencies(result)
        if stage is None:
            stage = self._blue[direction] = self.engines.blue_line.LiveBlueLineContinuation(
                direction, result.reactions, chronology, result.resets,
            )
            lines = stage.result
        else:
            previous = self._blue_inputs[direction]
            first = next((i for i, (old, new) in enumerate(zip(previous, current)) if old != new),
                         min(len(previous), len(current)))
            lines = stage.update(
                result.reactions, chronology, result.resets,
                first_changed=first, first_dirty_main=self.first_dirty_main,
            )
        self._blue_inputs[direction] = current
        return lines

    def a_zones(self, direction, reactions, blue_lines):
        chronology = self._market.chronology
        stage = self._a.get(direction)
        if stage is None:
            stage = self._a[direction] = self.engines.a_zone.LiveAZoneContinuation(
                direction, reactions, blue_lines, chronology,
            )
            return stage.result
        return stage.update(reactions, blue_lines, chronology, first_dirty_main=self.first_dirty_main)

    def s_zones(self, direction, detector):
        stage = self._s.get(direction)
        if stage is None:
            stage = self._s[direction] = self.engines.s_zone.LiveSZoneContinuation()
        return stage.update(detector, first_dirty_main=self.first_dirty_main)

    def stopall_finder(self, scope):
        def find(direction, s_zones, e_zones, chronology):
            key = (scope, direction)
            stage = self._stopall.get(key)
            if stage is None:
                stage = self._stopall[key] = self.engines.lifecycle.LiveStopAllContinuation(
                    direction, s_zones, e_zones, chronology,
                )
                return stage.result
            return stage.update(s_zones, e_zones, chronology, first_dirty_main=self.first_dirty_main)
        return find

    def order_b_finder(self, scope):
        def find(direction, chronology, trend, resets, opposite, stops, formations, *, behavior_anchors):
            key = (scope, direction)
            stage = self._order_b.get(key)
            if stage is None:
                stage = self._order_b[key] = LiveOrderBResetLegs(direction)
            return stage.update(
                chronology, trend, resets, opposite, stops, formations,
                behavior_anchors=behavior_anchors, first_dirty_main=self.first_dirty_main,
            )
        return find

    def primary(self, direction, groups, orders, detector):
        market = self._market
        chronology = market.chronology
        stage = self._primary.get(direction)
        ledger = {}
        for owner, group in groups.items():
            physical = chronology.opposite_direction(owner)
            for item in group["OrderAudit"]:
                reaction = item["reaction"]
                entry = item["entry"]
                first, end = reaction.first_idx, reaction.break_idx
                key = (owner, first, end)
                ledger[key] = (
                    repr((reaction, entry["reaction_number"], entry["stop_level"],
                          entry["stop_source_index"], item["causes"])),
                    chronology.reaction_confirmation(physical, reaction),
                    item["crossed"],
                )
        previous_dependencies = self._primary_dependencies.get(direction, ())
        if stage is None:
            stage = self._primary[direction] = self.engines.primary.LivePrimaryContinuation(
                direction, chronology, groups[direction]["S"], groups[direction]["E"],
                groups[direction]["StopAll"], orders,
            )
            result = stage.result
        else:
            dirty = (chronology.times[self.first_dirty_main]
                     if self.first_dirty_main < len(chronology.times)
                     else chronology.times[-1] + chronology.timeframe)
            previous = self._primary_ledger[direction]
            for key in previous.keys() | ledger.keys():
                before, after = previous.get(key), ledger.get(key)
                if before == after:
                    continue
                if before is not None and after is not None and before[:2] == after[:2]:
                    dirty = min(dirty, *(row[2][2] for row in (before, after) if row[2] is not None))
                else:
                    dirty = min(dirty, chronology.times[key[1]])
            for point, dependency in previous_dependencies:
                if point.decision_event_time < dirty and detector.primary_order_dependency(point) != dependency:
                    dirty = point.decision_event_time
            result = stage.update(
                chronology, groups[direction]["S"], groups[direction]["E"],
                groups[direction]["StopAll"], orders, first_dirty_event=dirty,
            )
        self._primary_ledger[direction] = ledger
        points = result.lows if direction == "bullish" else result.highs
        self._primary_dependencies[direction] = [
            (point, detector.primary_order_dependency(point)) for point in points
        ]
        return result

    def bullish_setups(self, groups, primary_lows):
        from bullish_setup_engine import LiveBullishSetupContinuation

        market = self._market
        chronology = market.chronology
        inputs = (chronology, groups["S"], groups["E"], groups["StopAll"], primary_lows)
        if self._setup is None:
            self._setup = LiveBullishSetupContinuation(*inputs, through_index=market.end_index)
            return self._setup.result
        dirty = (chronology.times[self.first_dirty_main]
                 if self.first_dirty_main < len(chronology.times)
                 else chronology.times[-1] + chronology.timeframe)
        return self._setup.update(*inputs, first_dirty_event=dirty, through_index=market.end_index)


class LivePipelineContinuation:
    """Build the standard indicator payload over append-only market input."""

    def __init__(self, args, engines):
        if engines.e_zone is None or args.s_zones != "enabled":
            raise ValueError("Live indicator requires the complete behavior pipeline.")
        self.args = copy(args)
        self.engines = engines
        self._buckets = LiveMarketBuckets(args.timeframe)
        self._main = []
        self._seconds = []
        self._stages = LivePipelineStages(engines)

    def append(self, rows):
        started = perf_counter()
        timings = {}
        engine = self.engines.reaction
        delta = self._buckets.append(rows)
        self._main = [
            *self._main[:delta.first_dirty_main],
            *build_candle_objects(engine, self._buckets.main_buckets[delta.first_dirty_main:],
                                  start_index=delta.first_dirty_main),
        ]
        self._seconds = [
            *self._seconds[:delta.first_dirty_second],
            *build_candle_objects(engine, self._buckets.second_buckets[delta.first_dirty_second:],
                                  start_index=delta.first_dirty_second),
        ]
        timeframe = self.args.timeframe
        candles = self._seconds if timeframe == 1 else self._main
        first_bucket = self.args.from_time if timeframe == 1 else self.args.from_time // timeframe * timeframe
        start = bisect_left(self._buckets.main_buckets, first_bucket, key=lambda bucket: bucket["time"])
        if start >= len(candles):
            raise ValueError("The selected range contains no timeframe candles.")
        chronology = engine.MarketChronology(candles, self._seconds, timeframe)
        market = MarketContext(self._seconds, candles, chronology.lower_index, chronology, start, len(candles) - 1)
        try:
            self._stages.begin(market, delta.first_dirty_main)
            state = prepare_pipeline_state(self.args, self.engines, market, timings, live=self._stages)
            payload = build_response_payload(self.args, self.engines, market, state, timings, started)
            self._stages.finish_regimes()
            return payload
        finally:
            engine.LiveReactionContinuation._release_indexes(candles, self._seconds)


class LiveRawChanged(ValueError):
    """A previously observed source candle was removed or revised."""


def _decode_raw(data):
    rows = json.loads(data, parse_float=Decimal)
    if not isinstance(rows, list) or not rows:
        raise LiveRawChanged("The RAW source is empty. Use Apply again.")
    return rows


class LiveRawSource:
    """Bind a manual range to its exact original RAW prefix across renames."""

    def __init__(self, selected, data, original):
        start = bisect_left(original, selected[0]["time"], key=lambda item: item["time"])
        end = start + len(selected)
        if selected != original[start:end]:
            raise LiveRawChanged("The selected range differs from the original RAW precision. Use Apply again.")
        self._catchup = original[end:]
        self._last_time = original[-1]["time"]
        self._remember_prefix(data)

    def _remember_prefix(self, data):
        # The RAW writer preserves everything before the closing bracket.
        # Hash the bytes without parsing or normalizing the previous candles.
        self._end = data.rfind(b"]")
        self._signature = hashlib.sha256(memoryview(data)[:self._end]).digest()

    def append(self, data, pipeline):
        if len(data) <= self._end or hashlib.sha256(memoryview(data)[:self._end]).digest() != self._signature:
            raise LiveRawChanged("Existing RAW candles changed. Use Apply again.")
        tail = data[self._end:].lstrip()
        if tail.startswith(b","):
            new_rows = _decode_raw(b"[" + tail[1:])
            previous = self._last_time
            for row in new_rows:
                if row["time"] <= previous:
                    raise LiveRawChanged("RAW candles no longer extend the previous history. Use Apply again.")
                previous = row["time"]
        elif tail.rstrip() == b"]":
            new_rows = []
        else:
            raise LiveRawChanged("The RAW file is no longer an append of the original source. Use Apply again.")
        batch = self._catchup + new_rows
        result = pipeline.append(batch) if batch else None
        self._catchup = []
        if new_rows:
            self._last_time = new_rows[-1]["time"]
            self._remember_prefix(data)
        return result


def _send_worker_message(kind, **fields):
    print(json.dumps({"type": kind, **fields}, separators=(",", ":")), flush=True)


def main():
    """Keep one exact manual calculation alive over the server's private pipe."""
    try:
        args = parse_arguments()
        original_path = Path(os.environ["TRADINGBOT_LIVE_RAW_SOURCE"])
        selected_data = args.data.read_bytes()
        selected = _decode_raw(selected_data)
        original_data = selected_data if args.data == original_path else original_path.read_bytes()
        original = selected if args.data == original_path else _decode_raw(original_data)
        lineage = LiveRawSource(selected, original_data, original)
        pipeline = LivePipelineContinuation(args, load_engines(args, {}))
        payload = pipeline.append(selected)
        del selected, original, selected_data, original_data
        _send_worker_message("seed", ready=True, payload=payload)
        # Updates carry a short JSON header followed by the unchanged RAW bytes.
        pipe = sys.stdin.buffer
        while header := pipe.readline(256):
            if not header.endswith(b"\n"):
                raise ValueError("Invalid live RAW update header.")
            request = json.loads(header)
            size = request.get("bytes")
            digest = request.get("sha256")
            if type(size) is not int or size <= 0 or not isinstance(digest, str) or len(digest) != 64:
                raise ValueError("Invalid live RAW update header.")
            raw = pipe.read(size)
            if len(raw) != size:
                raise ValueError("Incomplete live RAW update.")
            if hashlib.sha256(raw).hexdigest() != digest:
                _send_worker_message("error", code="RAW_RETRY",
                                     message="RAW changed during the indicator update. Retrying at the next check.")
                continue
            updated = lineage.append(raw, pipeline)
            if updated is not None:
                payload = updated
            _send_worker_message("update", payload=payload)
    except LiveRawChanged as exc:
        _send_worker_message("error", code="RAW_CHANGED", message=str(exc))
        return 1
    except Exception as exc:
        print(f"Live Engine: {exc}", file=sys.stderr, flush=True)
        _send_worker_message("error", code="LIVE_ENGINE_FAILED",
                             message="The live Engine could not continue this calculation. Use Apply again.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
