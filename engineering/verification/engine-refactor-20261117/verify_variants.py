"""Bounded entry-point, option, timeframe and process-hash-seed comparisons."""
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
SCRATCH = ROOT / "apps/chart/state/tmp/engine-refactor-20261117"


def main():
    cases = []
    options = [[], ["--pl-ph", "disabled"], ["--no-lifecycle"],
               ["--legacy-output"], ["--presentation-middle"],
               ["--no-behavior", "--pl-ph", "disabled"]]
    for symbol, direction, timeframe in itertools.product(
            ("USOIL", "XAUUSD"), ("bullish", "bearish"), (1, 5, 30, 60)):
        cases.append((symbol, direction, timeframe, [], "0"))
    for symbol, direction, option in itertools.product(
            ("USOIL", "XAUUSD"), ("bullish", "bearish"), options[1:]):
        cases.append((symbol, direction, 30, option, "0"))
    for symbol in ("USOIL", "XAUUSD"):
        cases.append((symbol, "both", 30, [], "0"))
    for symbol, direction, seed in itertools.product(("USOIL", "XAUUSD"), ("bullish", "bearish"), ("1", "2")):
        cases.append((symbol, direction, 30, [], seed))
    completed = []
    deterministic = {}
    for number, (symbol, direction, timeframe, options, seed) in enumerate(cases):
        stable = {}
        failures = {}
        for variant in ("removed", "optimized"):
            out = SCRATCH / "variants" / f"{number}-{variant}"
            result = subprocess.run([sys.executable, "-B", str(EVIDENCE / "run_case.py"),
                "--root", str(SCRATCH / variant), "--data", str(SCRATCH / "inputs" / f"{symbol}-8000.json"),
                "--direction", direction, "--timeframe", str(timeframe), "--out", str(out), *options],
                env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True, text=True)
            if result.returncode:
                if options != ["--no-behavior", "--pl-ph", "disabled"]:
                    raise RuntimeError(f"Case {number} {variant}: {result.stderr} {result.stdout}")
                failures[variant] = json.loads(out.with_suffix(".failure.json").read_bytes())
            else:
                stable[variant] = out.with_suffix(".stable.json").read_bytes()
        if failures:
            assert set(failures) == {"removed", "optimized"}, (number, "failure changed to success or vice versa")
            assert failures["removed"] == failures["optimized"], (number, "error contract changed", failures)
            assert failures["removed"]["exception_type"] == "builtins.KeyError"
            assert failures["removed"]["exception_args"] == repr((direction,))
            assert failures["removed"]["engine_frames"][-1] == ["bridge/trading_pipeline.py", "finalize_direction_visibility"]
            assert failures["removed"]["stdout"] == ""
            outcome = "UNCHANGED BASELINE FAILURE"
        else:
            assert stable["removed"] == stable["optimized"], (number, symbol, direction, timeframe, options, seed)
            key = symbol, direction, timeframe, tuple(options)
            assert deterministic.setdefault(key, stable["optimized"]) == stable["optimized"], ("seed difference", key, seed)
            outcome = "SUCCESS"
        completed.append(dict(symbol=symbol, direction=direction, timeframe=timeframe, options=options, seed=seed,
                              comparison="PASS", execution=outcome, failure=failures.get("removed")))
        if number % 20 == 0:
            print("PASS", number + 1, "of", len(cases), flush=True)
    (EVIDENCE / "variant-results.json").write_text(json.dumps(completed, indent=2), encoding="utf-8")
    print("PASS equivalence", len(completed), "bounded cases;", sum(row["execution"] == "SUCCESS" for row in completed),
          "successful outputs;", sum(row["execution"] != "SUCCESS" for row in completed), "unchanged baseline failures")
    # This changes no timed full-file measurement: the driver invokes these
    # continuation checks only after the serial benchmark matrix has finished.
    subprocess.run([sys.executable, str(EVIDENCE / "verify_live.py")], check=True)


if __name__ == "__main__":
    main()
