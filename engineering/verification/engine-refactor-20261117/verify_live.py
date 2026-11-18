"""Compare bounded real-data continuation outputs and seed/append timings."""
import argparse
import contextlib
from decimal import Decimal
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
SCRATCH = ROOT / "apps/chart/state/tmp/engine-refactor-20261117"


def worker(args):
    sys.path.insert(0, str(args.root / "engine/bridge"))
    import trading_pipeline as pipeline
    from live_pipeline import LivePipelineContinuation
    rows = json.loads(args.data.read_bytes(), parse_float=Decimal)
    flags = []
    for flag, module in (("engine", "reaction_engine"), ("blue-engine", "blue_line_detector"),
                         ("a-engine", "a_zone_detector"), ("s-engine", "s_zone_detector"),
                         ("e-engine", "e_zone_detector"), ("stopall-engine", "lifecycle_engine")):
        flags += ["--" + flag, str(args.root / "engine/pipeline" / (module + ".py"))]
    flags += ["--data", str(args.data), "--timeframe", "30", "--direction", args.direction,
              "--from-time", str(rows[0]["time"]), "--to-time", str(rows[3999]["time"]), "--bridge-output"]
    native_args = pipeline.parse_arguments(flags)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    payloads, durations, cpu_durations = [], [], []
    with args.out.with_suffix(".stderr.log").open("w", encoding="utf-8") as log, contextlib.redirect_stderr(log):
        engines = pipeline.load_engines(native_args, {})
        live = LivePipelineContinuation(native_args, engines)
        previous = 0
        for count in (4000, 4001, 4127, 4853, 6200, 8000):
            start = time.perf_counter()
            cpu_start = time.process_time()
            payload = live.append(rows[previous:count])
            durations.append(time.perf_counter() - start)
            cpu_durations.append(time.process_time() - cpu_start)
            previous = count
            payload.pop("timings")
            payloads.append(payload)
    args.out.with_suffix(".stable.json").write_text(json.dumps(payloads, separators=(",", ":")), encoding="utf-8")
    summary = dict(seed_seconds=durations[0], append_seconds=sum(durations[1:]), per_step_seconds=durations,
                   seed_cpu_seconds=cpu_durations[0], append_cpu_seconds=sum(cpu_durations[1:]))
    args.out.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--direction")
    parser.add_argument("--additional-runs", type=int, default=0)
    args = parser.parse_args()
    if args.worker:
        return worker(args)
    previous_results = {}
    if args.additional_runs:
        assert args.additional_runs > 0
        prior_path = EVIDENCE / "live-variant-results.json"
        previous_results = {(row["symbol"], row["direction"]): row for row in json.loads(prior_path.read_bytes())}
        assert len(previous_results) == 4
    results = []
    for symbol in ("USOIL", "XAUUSD"):
        for direction in ("bullish", "bearish"):
            measurements = {"removed": [], "optimized": []}
            stable = None
            existing = previous_results.get((symbol, direction))
            start_run, total_runs = 0, 3
            if existing:
                measurements = existing["measurements"]
                start_run = existing["runs"]
                total_runs = start_run + args.additional_runs
                stable = (SCRATCH / "live-variants" / f"removed-{symbol}-{direction}-0.stable.json").read_bytes()
            for run in range(start_run, total_runs):
                for variant in (("removed", "optimized") if run % 2 == 0 else ("optimized", "removed")):
                    out = SCRATCH / "live-variants" / f"{variant}-{symbol}-{direction}-{run}"
                    result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--worker",
                        "--root", str(SCRATCH / variant), "--data", str(SCRATCH / "inputs" / f"{symbol}-8000.json"),
                        "--out", str(out), "--direction", direction], env={**os.environ, "PYTHONHASHSEED": "0"}, capture_output=True, text=True)
                    if result.returncode:
                        raise RuntimeError(result.stderr + result.stdout)
                    content = out.with_suffix(".stable.json").read_bytes()
                    if stable is None:
                        stable = content
                    assert stable == content, (symbol, direction, variant, run)
                    measurements[variant].append(json.loads(out.with_suffix(".summary.json").read_bytes()))
            row = dict(symbol=symbol, direction=direction, rows=8000, horizons=[4000,4001,4127,4853,6200,8000], runs=total_runs,
                       comparison="PASS: exact stable bytes across all horizons and repeats", measurements=measurements)
            for mode in ("seed_seconds", "append_seconds"):
                row[mode + "_speedup"] = statistics.median(x[mode] for x in measurements["removed"]) / statistics.median(x[mode] for x in measurements["optimized"])
            for mode in ("seed_cpu_seconds", "append_cpu_seconds"):
                row[mode + "_speedup"] = statistics.median(x[mode] for x in measurements["removed"] if mode in x) / statistics.median(x[mode] for x in measurements["optimized"] if mode in x)
            row["cpu_measured_runs"] = sum("seed_cpu_seconds" in x for x in measurements["optimized"])
            results.append(row)
            print("PASS bounded live", symbol, direction, "seed", round(row["seed_seconds_speedup"],3), "append", round(row["append_seconds_speedup"],3), flush=True)
    (EVIDENCE / "live-variant-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
