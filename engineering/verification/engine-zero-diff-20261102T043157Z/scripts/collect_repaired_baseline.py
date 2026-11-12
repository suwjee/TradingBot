"""Sequential remaining BEFORE collection; all normal/profiling runs stay separate."""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from matrix import EVIDENCE, ROOT, file_sha, save

SCRIPTS = Path(__file__).resolve().parent
PHASE = "repaired-before"
PROGRESS = EVIDENCE / "discovery/repaired-collection-progress.json"


def progress(stage, **extra):
    value = {"stage": stage, "utc": datetime.now(timezone.utc).isoformat(), **extra}
    save(PROGRESS, value)
    print(json.dumps(value), flush=True)


def invoke(*arguments):
    result = subprocess.run([sys.executable, "-B", *map(str, arguments)], cwd=ROOT)
    if result.returncode:
        raise RuntimeError(f"Collection command failed ({result.returncode}): {arguments}")


def main():
    cases = json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())
    progress("waiting-for-initial-repaired-matrix")
    started = time.monotonic()
    while True:
        records = []
        for case in cases:
            path = EVIDENCE / PHASE / case["id"] / "run-02.metrics.json"
            if path.exists():
                try:
                    records.append(json.loads(path.read_bytes()))
                except json.JSONDecodeError:
                    pass
        if any(record["status"] != "PASS" for record in records):
            raise RuntimeError("Initial repaired matrix failed; preserve evidence and stop")
        if len(records) == len(cases):
            break
        if time.monotonic() - started > 5400:
            raise RuntimeError("Initial matrix did not complete; do not fabricate a baseline")
        time.sleep(3)
    progress("additional-normal-repetitions")
    practical = [case["id"] for case in cases if not case["id"].startswith("usoil-month-")]
    invoke(SCRIPTS / "matrix.py", PHASE, "--baseline-phase", PHASE, "--repeats", "5", "--select", ",".join(practical))
    progress("original-calculation-comparison")
    invoke(SCRIPTS / "compare_preparatory_repair.py")
    manifest = json.loads((EVIDENCE / PHASE / "source-manifest.json").read_bytes())
    frozen = EVIDENCE / "discovery/repaired-source-before"
    frozen.mkdir(exist_ok=True)
    for relative, expected in manifest.items():
        source, destination = ROOT / relative, frozen / relative
        if file_sha(source) != expected:
            raise RuntimeError(f"Source drift before freeze: {relative}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if file_sha(destination) != expected:
                raise RuntimeError(f"Frozen Source changed: {relative}")
        else:
            shutil.copyfile(source, destination)
    progress("fresh-separate-profiles")
    for case in ["xau-oct26-30s-bullish", "xau-oct26-30s-bearish"]:
        target = EVIDENCE / PHASE / "profile" / case / "metadata.json"
        if not target.exists():
            invoke(SCRIPTS / "instrumented.py", "profile", PHASE, case, "--baseline-phase", PHASE)
        if json.loads(target.read_bytes())["status"] != "PASS":
            raise RuntimeError(f"Repaired profile output differs: {case}")
    progress("warm-processing")
    for case in ["usoil-oct22-5s-bullish-legacy-no-primary", "usoil-oct22-5s-bearish-legacy-no-primary", "xau-oct26-30s-bearish"]:
        target = EVIDENCE / PHASE / "warm" / case / "metadata.json"
        if not target.exists():
            invoke(SCRIPTS / "instrumented.py", "warm", PHASE, case, "--baseline-phase", PHASE)
        if json.loads(target.read_bytes())["status"] != "PASS":
            raise RuntimeError(f"Warm baseline differs: {case}")
    for index, case in enumerate(cases, start=1):
        progress("native-snapshots", case=case["id"], index=index, total=len(cases))
        target = EVIDENCE / PHASE / "snapshot" / case["id"] / "metadata.json"
        if not target.exists():
            invoke(SCRIPTS / "instrumented.py", "snapshot", PHASE, case["id"], "--baseline-phase", PHASE)
        if json.loads(target.read_bytes())["status"] != "PASS":
            raise RuntimeError(f"Native snapshot collection differs from CLI: {case['id']}")
    invoke(SCRIPTS / "export_baseline_reports.py")
    progress("complete", status="PASS", source_manifest=manifest, scenarios=len(cases))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        progress("failed", status="INCOMPLETE", error=str(error))
        raise
