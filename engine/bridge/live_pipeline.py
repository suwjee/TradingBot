"""RAW session transport for independent indicator calculations."""

from __future__ import annotations

from bisect import bisect_left
from copy import copy
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import sys

from trading_pipeline import (
    LiveMarketBuckets, LiveMarketViews, calculate_live_from_buckets, emit_progress, load_engines, parse_arguments, progress_events_to,
)


LIVE_PIPELINE_VERSION = "1.3.0"


class LivePipelineContinuation:
    """Keep normalized RAW input and replay every trading stage on each request."""

    def __init__(self, args, engines):
        if engines.e_zone is None or args.s_zones != "enabled":
            raise ValueError("Live indicator requires the complete behavior pipeline.")
        if type(args.timeframe) is not int or args.timeframe < 1:
            raise ValueError("Live timeframe must be a positive integer number of seconds.")
        self.args = copy(args)
        self.engines = engines
        self._buckets = LiveMarketBuckets(args.timeframe)
        self._market_views = LiveMarketViews()

    def append(self, rows: list[dict]) -> dict[str, object]:
        previous_time = self._buckets.last_raw_time
        for row in rows:
            event_time = int(row["time"])
            if event_time != row["time"] or event_time <= 0:
                raise ValueError("Live RAW requires positive integer times.")
            if previous_time is not None and event_time < previous_time:
                raise ValueError("Live RAW must be appended in chronological order.")
            previous_time = event_time
        if previous_time is None:
            raise ValueError("The selected range contains no timeframe candles.")

        args = copy(self.args)
        args.to_time = previous_time
        direction_count = 2 if self.engines.primary is not None or args.direction == "both" else 1
        completed_stages = 0

        def report_stage(label):
            nonlocal completed_stages
            completed_stages += 1
            emit_progress("completed", label, liveProgress=True, completedStages=completed_stages,
                          totalStages=direction_count + 4)

        emit_progress("started", "Build live market chronology", liveProgress=True)
        try:
            with self._buckets.stage_append(rows) as delta:
                payload = calculate_live_from_buckets(
                    args, self.engines, self._buckets, live_views=self._market_views, bucket_delta=delta,
                    report_stage=report_stage,
                )
                report_stage("Calculated result ready for validation")
        except BaseException:
            # The input transaction rolled back. Rebuild geometry on retry.
            self._market_views = LiveMarketViews()
            raise
        return payload


class LiveRawChanged(ValueError):
    """A previously observed source candle was removed or revised."""


class LiveRawDeltaMismatch(ValueError):
    """The private append message could not prove byte-exact continuity."""


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
        if selected is not original and selected != original[start:end]:
            raise LiveRawChanged("The selected range differs from the original RAW precision. Use Apply again.")
        self._catchup = original[end:]
        self._last_time = original[-1]["time"]
        self._remember_prefix(data)

    def _remember_prefix(self, data):
        # The RAW writer preserves everything before the closing bracket.
        # Hash the bytes without parsing or normalizing the previous candles.
        self._end = data.rfind(b"]")
        self._prefix_hash = hashlib.sha256(memoryview(data)[:self._end])
        self._ending = data[self._end:]
        self._raw_sha256 = self._file_digest(self._prefix_hash, self._ending)

    @staticmethod
    def _file_digest(prefix_hash, ending):
        digest = prefix_hash.copy()
        digest.update(ending)
        return digest.hexdigest()

    def append_delta(self, data, base_sha256, raw_sha256, pipeline):
        if base_sha256 != self._raw_sha256 or not data.startswith(b","):
            raise LiveRawDeltaMismatch
        prefix = self._prefix_hash.copy()
        prefix.update(data)
        if self._file_digest(prefix, self._ending) != raw_sha256:
            raise LiveRawDeltaMismatch

        new_rows = _decode_raw(b"[" + data[1:] + b"]")
        result = self._append_rows(new_rows, pipeline)
        self._end += len(data)
        self._prefix_hash = prefix
        self._raw_sha256 = raw_sha256
        return result

    def append(self, data, pipeline):
        if len(data) <= self._end or hashlib.sha256(memoryview(data)[:self._end]).digest() != self._prefix_hash.digest():
            raise LiveRawChanged("Existing RAW candles changed. Use Apply again.")
        tail = data[self._end:].lstrip()
        if tail.startswith(b","):
            new_rows = _decode_raw(b"[" + tail[1:])
        elif tail.rstrip() == b"]":
            new_rows = []
        else:
            raise LiveRawChanged("The RAW file is no longer an append of the original source. Use Apply again.")
        result = self._append_rows(new_rows, pipeline)
        if new_rows:
            self._remember_prefix(data)
        elif data[self._end:] != self._ending:
            self._ending = data[self._end:]
            self._raw_sha256 = self._file_digest(self._prefix_hash, self._ending)
        return result

    def _append_rows(self, new_rows, pipeline):
        previous = self._last_time
        for row in new_rows:
            if row["time"] <= previous:
                raise LiveRawChanged("RAW candles no longer extend the previous history. Use Apply again.")
            previous = row["time"]
        result = pipeline.append(self._catchup + new_rows)
        self._catchup = []
        self._last_time = previous
        return result


def _send_worker_message(kind, **fields):
    print(json.dumps({"type": kind, **fields}, separators=(",", ":")), flush=True)


def _report_worker_progress(event):
    if event["status"] == "started" or "completedStages" in event:
        _send_worker_message("progress", event=event)


def main():
    """Replay the selected RAW history for each request on the private pipe."""
    try:
        args = parse_arguments()
        original_path = Path(os.environ["TRADINGBOT_LIVE_RAW_SOURCE"])
        selected_data = args.data.read_bytes()
        selected = _decode_raw(selected_data)
        original_data = selected_data if args.data == original_path else original_path.read_bytes()
        original = selected if args.data == original_path else _decode_raw(original_data)
        lineage = LiveRawSource(selected, original_data, original)
        del original, selected_data, original_data
        pipeline = LivePipelineContinuation(args, load_engines(args, {}))
        _send_worker_message("seed", ready=True, payload=pipeline.append(selected))
        del selected
        # The server supplies exact append bytes when it owns the commit lineage.
        pipe = sys.stdin.buffer
        while header := pipe.readline(256):
            if not header.endswith(b"\n"):
                raise ValueError("Invalid live RAW update header.")
            request = json.loads(header)
            size = request.get("bytes")
            digest = request.get("sha256")
            base_digest = request.get("baseSha256")
            if type(size) is not int or size <= 0 or not isinstance(digest, str) or len(digest) != 64:
                raise ValueError("Invalid live RAW update header.")
            raw = pipe.read(size)
            if len(raw) != size:
                raise ValueError("Incomplete live RAW update.")
            sink = _report_worker_progress if request.get("progress") is True else lambda _event: None
            with progress_events_to(sink):
                if base_digest is not None:
                    try:
                        updated = lineage.append_delta(raw, base_digest, digest, pipeline)
                    except LiveRawDeltaMismatch:
                        _send_worker_message("error", code="RAW_DELTA_MISMATCH",
                                             message="The RAW append could not be verified against the live checkpoint.")
                        continue
                elif hashlib.sha256(raw).hexdigest() != digest:
                    _send_worker_message("error", code="RAW_RETRY",
                                         message="RAW changed during the indicator update. Retrying at the next check.")
                    continue
                else:
                    updated = lineage.append(raw, pipeline)
            _send_worker_message("update", payload=updated)
            del updated, raw
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
