"""Collect final candidate evidence sequentially; fail closed on any difference."""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from matrix import EVIDENCE, ROOT, save

SCRIPTS = Path(__file__).resolve().parent


def progress(stage, **extra):
    value = {"stage": stage, "utc": datetime.now(timezone.utc).isoformat(), **extra}
    save(EVIDENCE / "discovery/after-collection-progress.json", value)
    print(json.dumps(value), flush=True)


def invoke(*arguments):
    process = subprocess.run([sys.executable, "-B", *map(str, arguments)], cwd=ROOT)
    if process.returncode:
        raise RuntimeError(f"Evidence command failed ({process.returncode}): {arguments}")


def instrument(mode, case):
    target = EVIDENCE / "after" / mode / case / "metadata.json"
    if not target.exists():
        invoke(SCRIPTS / "instrumented.py", mode, "after", case, "--baseline-phase", "repaired-before")
    if json.loads(target.read_bytes())["status"] != "PASS":
        raise RuntimeError(f"Instrumented output differs: {mode}/{case}")


def main():
    cases = json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())
    for case in ["xau-oct26-30s-bullish", "usoil-oct22-5s-bearish-legacy-no-primary"]:
        progress("early-native-gate", case=case)
        instrument("snapshot", case)
        invoke(SCRIPTS / "compare_snapshots.py", "repaired-before", "after", case)
    progress("normal-cold-matrix")
    invoke(SCRIPTS / "matrix.py", "after", "--baseline-phase", "repaired-before", "--repeats", "2")
    practical = [case["id"] for case in cases if not case["id"].startswith("usoil-month-")]
    progress("additional-normal-repetitions")
    invoke(SCRIPTS / "matrix.py", "after", "--baseline-phase", "repaired-before", "--repeats", "5", "--select", ",".join(practical))
    for index, case in enumerate(cases, 1):
        progress("native-snapshots", case=case["id"], index=index, total=len(cases))
        instrument("snapshot", case["id"])
        invoke(SCRIPTS / "compare_snapshots.py", "repaired-before", "after", case["id"])
    progress("separate-profiles")
    for case in ["xau-oct26-30s-bullish", "xau-oct26-30s-bearish"]:
        instrument("profile", case)
    progress("warm-processing")
    for case in ["usoil-oct22-5s-bullish-legacy-no-primary", "usoil-oct22-5s-bearish-legacy-no-primary", "xau-oct26-30s-bearish"]:
        instrument("warm", case)
    progress("separate-allocation-trace")
    instrument("alloc", "usoil-oct22-5s-bearish-legacy-no-primary")
    progress("complete", status="PASS", scenarios=len(cases))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        progress("failed", status="INCOMPLETE", error=str(error))
        raise
