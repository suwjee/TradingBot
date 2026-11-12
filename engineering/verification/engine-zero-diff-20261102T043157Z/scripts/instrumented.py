"""Separate profiling/native snapshot/warm-process probes; never normal timings."""
from __future__ import annotations
import argparse
import contextlib
import cProfile
import dataclasses
from datetime import datetime, timedelta
from decimal import Decimal
import functools
import gzip
import importlib.util
import io
import json
from pathlib import Path
import pstats
import sys
import time
import tracemalloc
from matrix import EVIDENCE, ROOT, command, first_diff, phase_source_guard, save, stable_bytes


class GraphSnapshot:
    """Capture field types, ordered containers, exact values and object aliasing."""
    def __init__(self):
        self.seen = {}
        self.keepalive = []

    def encode(self, value):
        if value is None or type(value) in (str, int, float, bool):
            return value
        if isinstance(value, Decimal):
            return {"decimal": str(value)}
        if isinstance(value, datetime):
            return {"datetime": value.isoformat(), "fold": value.fold}
        if isinstance(value, timedelta):
            return {"timedelta": [value.days, value.seconds, value.microseconds]}
        identity = id(value)
        if identity in self.seen:
            return {"ref": self.seen[identity]}
        token = len(self.seen) + 1
        self.seen[identity] = token
        self.keepalive.append(value)
        if isinstance(value, (set, frozenset)):
            ordered = sorted(value, key=lambda item: json.dumps(GraphSnapshot().encode(item), sort_keys=True))
            return {"id": token, "type": type(value).__name__, "items": [self.encode(item) for item in ordered]}
        if isinstance(value, dict):
            return {"id": token, "type": "dict", "items": [[self.encode(key), self.encode(item)] for key, item in value.items()]}
        if isinstance(value, (list, tuple)):
            return {"id": token, "type": type(value).__name__, "items": [self.encode(item) for item in value]}
        if dataclasses.is_dataclass(value):
            fields = {item.name: getattr(value, item.name) for item in dataclasses.fields(value)}
            fields.update(vars(value) if hasattr(value, "__dict__") else {})
            return {"id": token, "type": type(value).__qualname__, "fields": self.encode(fields)}
        if hasattr(value, "__dict__"):
            fields = {key: item for key, item in vars(value).items() if not callable(item)}
            return {"id": token, "type": type(value).__qualname__, "fields": self.encode(fields)}
        slots = [name for base in type(value).__mro__ for name in getattr(base, "__slots__", ())
                 if name not in {"__dict__", "__weakref__"} and hasattr(value, name)]
        if slots:
            return {"id": token, "type": type(value).__qualname__,
                    "fields": self.encode({name: getattr(value, name) for name in slots})}
        return {"type": type(value).__qualname__}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("profile", "alloc", "snapshot", "warm"))
    parser.add_argument("phase")
    parser.add_argument("case")
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--baseline-phase", default="before")
    args = parser.parse_args()
    source_manifest = phase_source_guard(args.phase, args.source_root)
    cases = json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())
    case = next(item for item in cases if item["id"] == args.case)
    output = EVIDENCE / args.phase / args.mode / args.case
    output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location("audit_bridge", args.source_root / "engine/bridge/trading_pipeline.py")
    bridge = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = bridge
    spec.loader.exec_module(bridge)
    cli = command(case, args.source_root)[3:]
    sys.argv = [str(spec.origin), *cli]
    hook_events = []
    if args.mode == "snapshot":
        def store_snapshot(name, value):
            index = len(hook_events)
            path = output / f"{index:03d}-{name}.json.gz"
            with gzip.open(path, "wt", encoding="utf-8", newline="\n") as stream:
                json.dump(GraphSnapshot().encode(value), stream, separators=(",", ":"))
            hook_events.append({"index": index, "stage": name, "path": path.name})
        def wrap(name, project):
            original = getattr(bridge, name)
            @functools.wraps(original)
            def wrapped(*positional, **keyword):
                result = original(*positional, **keyword)
                store_snapshot(name, project(result))
                return result
            setattr(bridge, name, wrapped)
        wrap("prepare_market_context", lambda market: {"seconds": market.seconds, "candles": market.candles,
                                                       "start_index": market.start_index, "end_index": market.end_index})
        wrap("calculate_full_direction_state", lambda state: {
            **{name: getattr(state, name) for name in ["e_zones", "blue_lines", "a_zones", "invalid_a_identities", "invalid_s_identities", "s_zones", "s_candidates", "initial_s_zones"]},
            "accepted_order_audit": state.e_detector.order_audit, "s_order_audit": state.s_detector.order_audit,
            "eligible_a_zones": state.s_detector.eligible_a_zones})
        wrap("prepare_pipeline_state", lambda state: {"results": state.results, "internal_reaction_identities": state.internal_reaction_identities,
                                                      "full_e_zones": state.full_e_zones, "full_s_by_direction": state.full_s_by_direction,
                                                      "full_a_by_direction": state.full_a_by_direction, "full_lines_by_direction": state.full_lines_by_direction})
        wrap("calculate_direction_range_state", lambda value: value)
        wrap("finalize_direction_visibility", lambda value: value)
        wrap("calculate_primary_structures", lambda value: value)
    profile = cProfile.Profile() if args.mode == "profile" else None
    if args.mode == "alloc":
        tracemalloc.start(5)
    started = time.perf_counter()
    cpu_started = time.process_time()
    error = None
    code = 1
    with (output / "stdout.json").open("w", encoding="utf-8", newline="\n") as stdout, (output / "stderr.log").open("w", encoding="utf-8", newline="\n") as stderr, contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            if profile:
                profile.enable()
            if args.mode == "warm":
                parsed = bridge.parse_arguments(cli)
                timings = {}
                engines = bridge.load_engines(parsed, timings)
                market = bridge.prepare_market_context(parsed, engines, timings)
                measurements = []
                for repeat in range(6):
                    phase_times = {}
                    begin = time.perf_counter()
                    cpu = time.process_time()
                    state = bridge.prepare_pipeline_state(parsed, engines, market, phase_times)
                    payload = bridge.build_response_payload(parsed, engines, market, state, phase_times, begin)
                    encoded = json.dumps(payload, separators=(",", ":")).encode()
                    measured_wall = time.perf_counter()-begin
                    measured_cpu = time.process_time()-cpu
                    (output / f"warm-{repeat}.json").write_bytes(encoded)
                    stable = stable_bytes(encoded)
                    reference = gzip.decompress((EVIDENCE / args.baseline_phase / case["id"] / "run-01.stable.json.gz").read_bytes())
                    measurements.append({"repeat": repeat, "warmup": repeat == 0, "wall_seconds": measured_wall,
                                         "cpu_seconds": measured_cpu, "stable_bytes_equal": stable == reference,
                                         "first_difference": first_diff(json.loads(reference), json.loads(stable))})
                    del state, payload
                save(output / "warm-metrics.json", measurements)
                code = 0 if all(item["stable_bytes_equal"] for item in measurements) else 1
            else:
                code = bridge.main()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            error = {"type": type(exc).__name__, "message": str(exc)}
        finally:
            if profile:
                profile.disable()
    metadata = {"case": case["id"], "mode": args.mode, "command_arguments": cli, "exit_code": code,
                "source_manifest": source_manifest,
                "status": "PASS" if code == 0 else "FAIL", "error": error,
                "instrumented_wall_seconds": time.perf_counter()-started, "instrumented_cpu_seconds": time.process_time()-cpu_started}
    if profile:
        profile.dump_stats(str(output / "cpu.prof"))
        with (output / "top-cumulative.txt").open("w", encoding="utf-8") as stream:
            pstats.Stats(profile, stream=stream).strip_dirs().sort_stats("cumulative").print_stats(80)
        stats = pstats.Stats(profile)
        save(output / "stats.json", [{"file": key[0], "line": key[1], "function": key[2], "primitive_calls": value[0],
                                      "calls": value[1], "self_seconds": value[2], "cumulative_seconds": value[3]}
                                     for key, value in sorted(stats.stats.items(), key=lambda pair: -pair[1][3])])
    if args.mode == "alloc":
        metadata["tracemalloc_current_bytes"], metadata["tracemalloc_peak_bytes"] = tracemalloc.get_traced_memory()
        save(output / "allocations.json", [{"traceback": str(item.traceback), "bytes": item.size, "count": item.count}
                                           for item in tracemalloc.take_snapshot().statistics("lineno")[:80]])
        tracemalloc.stop()
    if args.mode == "snapshot":
        save(output / "snapshot-index.json", hook_events)
    if code == 0 and args.mode != "warm":
        raw = (output / "stdout.json").read_bytes()
        stable = stable_bytes(raw)
        reference = gzip.decompress((EVIDENCE / args.baseline_phase / case["id"] / "run-01.stable.json.gz").read_bytes())
        metadata["stable_bytes_equal_to_cli"] = stable == reference
        metadata["first_difference"] = first_diff(json.loads(reference), json.loads(stable))
        if stable != reference:
            metadata["status"] = "FAIL"
    save(output / "metadata.json", metadata)
    print(json.dumps(metadata), flush=True)
    return 0 if metadata["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
