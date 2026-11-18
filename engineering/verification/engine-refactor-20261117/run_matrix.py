"""Serial paired fresh-process measurements; fail on any exact stable difference."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / "apps/chart/state/tmp/engine-refactor-20261117"
EVIDENCE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--symbols", nargs="+", default=["USOIL", "XAUUSD"])
    args = parser.parse_args()
    results = []
    for symbol in args.symbols:
        for direction in ("bullish", "bearish"):
            measurements = {"removed": [], "optimized": []}
            for run in range(args.runs):
                outputs = {}
                for variant in (("removed", "optimized") if run % 2 == 0 else ("optimized", "removed")):
                    output = SCRATCH / "matrix" / f"{variant}-{symbol}-{direction}-{run}"
                    command = [sys.executable, "-B", str(EVIDENCE / "run_case.py"), "--root", str(SCRATCH / variant),
                               "--data", str(SCRATCH / "inputs" / (symbol + "-full.json")),
                               "--out", str(output), "--direction", direction]
                    print(f"START {variant} {symbol} {direction} run {run + 1}", flush=True)
                    completed = subprocess.run(command, env={**os.environ, "PYTHONHASHSEED": "0"}, capture_output=True, text=True)
                    if completed.returncode:
                        raise RuntimeError(completed.stderr + completed.stdout)
                    summary = json.loads(output.with_suffix(".summary.json").read_bytes())
                    measurements[variant].append(summary)
                    outputs[variant] = output.with_suffix(".stable.json").read_bytes()
                    print(f"DONE {variant} {summary['wall_seconds']:.3f}s peak {summary['peak_working_set_bytes']}", flush=True)
                if outputs["removed"] != outputs["optimized"]:
                    raise AssertionError(f"Exact stable bytes differ: {symbol} {direction} run {run}")
                print(f"EXACT PASS {symbol} {direction} run {run + 1}", flush=True)
            baseline = statistics.median(x["wall_seconds"] for x in measurements["removed"])
            candidate = statistics.median(x["wall_seconds"] for x in measurements["optimized"])
            result = dict(symbol=symbol, direction=direction, runs=args.runs, baseline_median_seconds=baseline,
                          optimized_median_seconds=candidate, speedup=baseline / candidate, measurements=measurements,
                          stable_comparison="PASS: direct byte equality excluding only top-level timings")
            results.append(result)
            (EVIDENCE / "performance-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
            print(f"RESULT {symbol} {direction} {baseline / candidate:.3f}x", flush=True)


if __name__ == "__main__":
    main()
