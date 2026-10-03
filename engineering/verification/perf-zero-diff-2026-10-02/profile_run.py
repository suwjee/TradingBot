"""Profile TradingBot Engine on one eligible RAW workload via cProfile."""

from __future__ import annotations

import argparse
import contextlib
import cProfile
import io
import json
import pstats
import sys
import time
from pathlib import Path

import orjson

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "engine"
RAW_ROOT = ROOT / "apps" / "chart" / "state" / "data" / "RAW"
SIZE_LIMIT = 10 * 1024 * 1024


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--timeframe", type=int, required=True)
    parser.add_argument("--direction", required=True, choices=("bullish", "bearish", "both"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--top", type=int, default=40)
    args = parser.parse_args()

    raw_path = args.raw
    if not raw_path.is_absolute():
        raw_path = RAW_ROOT / raw_path
    size = raw_path.stat().st_size
    if size >= SIZE_LIMIT:
        print(f"NOT APPLICABLE DATASET_SIZE_LIMIT size={size}", file=sys.stderr)
        return 2

    rows = orjson.loads(raw_path.read_bytes())
    first = min(int(r["time"]) for r in rows)
    last = max(int(r["time"]) for r in rows)
    del rows

    bridge = ENGINE / "bridge" / "trading_pipeline.py"
    pipeline = ENGINE / "pipeline"
    argv = [
        str(bridge),
        "--engine", str(pipeline / "reaction_engine.py"),
        "--blue-engine", str(pipeline / "blue_line_detector.py"),
        "--a-engine", str(pipeline / "a_zone_detector.py"),
        "--s-engine", str(pipeline / "s_zone_detector.py"),
        "--e-engine", str(pipeline / "e_zone_detector.py"),
        "--stopall-engine", str(pipeline / "lifecycle_engine.py"),
        "--data", str(raw_path),
        "--timeframe", str(args.timeframe),
        "--from-time", str(first),
        "--to-time", str(last),
        "--direction", args.direction,
    ]
    sys.argv = argv

    import importlib.util

    spec = importlib.util.spec_from_file_location("trading_pipeline_profile", bridge)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module

    profiler = cProfile.Profile()
    started = time.perf_counter()
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(io.StringIO()):
        profiler.enable()
        spec.loader.exec_module(module)
        code = module.main()
        profiler.disable()
    wall = time.perf_counter() - started
    if code != 0:
        raise SystemExit(f"bridge exit {code}")

    args.output.mkdir(parents=True, exist_ok=True)
    profile_bin = args.output / f"{args.raw.name}.{args.direction}.prof"
    stats_txt = args.output / f"{args.raw.name}.{args.direction}.pstats.txt"
    profiler.dump_stats(profile_bin)

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative").print_stats(args.top)
    stats.sort_stats("tottime").print_stats(args.top)
    stats_txt.write_text(stream.getvalue(), encoding="utf-8")

    # compact top-function table
    rows_out = []
    for func, (cc, nc, tt, ct, callers) in stats.stats.items():
        rows_out.append(
            {
                "file": func[0],
                "line": func[1],
                "func": func[2],
                "calls": nc,
                "tottime": round(tt, 4),
                "cumtime": round(ct, 4),
            }
        )
    rows_out.sort(key=lambda r: r["tottime"], reverse=True)
    top_self = rows_out[: args.top]
    rows_out.sort(key=lambda r: r["cumtime"], reverse=True)
    top_cum = rows_out[: args.top]
    summary = {
        "raw": str(raw_path),
        "size_bytes": size,
        "direction": args.direction,
        "timeframe": args.timeframe,
        "wallSeconds": wall,
        "exitCode": code,
        "topSelf": top_self,
        "topCumulative": top_cum,
    }
    (args.output / f"{args.raw.name}.{args.direction}.summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps({"wallSeconds": wall, "profile": str(profile_bin)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
