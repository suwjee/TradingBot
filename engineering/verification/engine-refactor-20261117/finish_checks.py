"""Finish this execution serially after all paired measurements have completed."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
SCRATCH = ROOT / "apps/chart/state/tmp/engine-refactor-20261117"


def run(name, command, *, cwd=ROOT):
    print("START", name, flush=True)
    with (EVIDENCE / (name + ".log")).open("w", encoding="utf-8") as stream:
        result = subprocess.run(command, cwd=cwd, env={**os.environ, "PYTHONHASHSEED": "0"}, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"{name}: exit {result.returncode}; read {name}.log")
    print("PASS", name, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume-after-measurements", action="store_true")
    args = parser.parse_args()
    while True:
        try:
            result = json.loads((EVIDENCE / "performance-results.json").read_bytes())
            if len(result) == 4:
                break
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        time.sleep(10)
    # The very first optimized sample ran before the last source review fixes.
    # Replace it with an actual final-source execution; never relabel old data.
    if args.resume_after_measurements:
        assert json.loads((EVIDENCE / "paired-replacement-complete.json").read_bytes())["status"] == "PASS"
        print("REUSED actual completed final-source paired measurement; no timings were relabeled", flush=True)
    else:
        run("replacement-final-sample", [sys.executable, "-B", str(EVIDENCE / "run_case.py"),
            "--root", str(SCRATCH / "optimized"), "--data", str(SCRATCH / "inputs/USOIL-full.json"),
            "--out", str(SCRATCH / "matrix/optimized-USOIL-bullish-0"), "--direction", "bullish"])
    run("summary", [sys.executable, str(EVIDENCE / "summarize_results.py")])
    run("variants", [sys.executable, str(EVIDENCE / "verify_variants.py")])
    run("e-routes-final", [sys.executable, str(EVIDENCE / "compare_e_zone_routes.py")])
    run("engine-final", [sys.executable, "-m", "pytest", "engine/tests/unit", "-q"])
    chart = ROOT / "apps/chart"
    run("chart-final", ["npm.cmd", "test"], cwd=chart)
    run("build-final", ["npm.cmd", "run", "build"], cwd=chart)
    run("live-recovery-final", ["node", "--test", "tests/integration/live-indicator-recovery.test.mjs"], cwd=chart)
    run("references-final", [sys.executable, "engine/tests/verification/verify_order_references.py"])
    run("manifest-final", [sys.executable, str(EVIDENCE / "capture_manifest.py")])
    run("anti-drift-final", [sys.executable, "scripts/verification/anti_drift.py", "--mode", "changed", "--format", "human"])
    run("diff-final", ["git", "diff", "--check"])
    (EVIDENCE / "checks-complete.json").write_text(json.dumps(dict(status="PASS", checks=[
        "replacement-final-sample", "summary", "variants", "e-routes-final", "engine-final", "chart-final",
        "build-final", "live-recovery-final", "references-final", "manifest-final", "anti-drift-final", "diff-final"]), indent=2), encoding="utf-8")
    print("ALL REQUIRED SERIAL CHECKS PASS", flush=True)


if __name__ == "__main__":
    main()
