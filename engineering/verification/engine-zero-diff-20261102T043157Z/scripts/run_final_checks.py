"""Run current verification sequentially after measurements and reference sync."""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from matrix import EVIDENCE, ROOT, file_sha, phase_source_guard, save

RECORDS = []


def check(name, command):
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(list(map(str, command)), cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    path = EVIDENCE / "discovery" / f"final-{name}.log"
    path.write_bytes(result.stdout)
    record = {"name": name, "command": list(map(str, command)), "started_utc": started,
              "exit_code": result.returncode, "status": "PASS" if result.returncode == 0 else "FAIL", "log": str(path)}
    RECORDS.append(record)
    save(EVIDENCE / "discovery/final-checks.json", RECORDS)
    print(json.dumps(record), flush=True)
    return result


def main():
    paired = json.loads((EVIDENCE / "discovery/paired-progress.json").read_bytes())
    if paired.get("stage") != "complete" or paired.get("status") != "PASS":
        raise RuntimeError("Finish sequential performance measurements first")
    if json.loads((EVIDENCE / "discovery/frozen-allocation-completion.json").read_bytes())["status"] != "PASS":
        raise RuntimeError("Finish the separate frozen-source allocation probe first")
    if json.loads((EVIDENCE / "discovery/controlled-progress.json").read_bytes())["status"] != "PASS":
        raise RuntimeError("Finish explicit bytecode-cache controlled pairs first")
    manifest = phase_source_guard("after", ROOT)
    compile_records = []
    for relative, digest in manifest.items():
        path = ROOT / relative
        compile(path.read_bytes(), str(path), "exec")
        compile_records.append({"path": relative, "sha256": digest, "status": "PASS"})
    save(EVIDENCE / "discovery/final-source-compilation.json", compile_records)
    raw_records = []
    for initial in json.loads((EVIDENCE / "discovery/raw-inputs-before.json").read_bytes()):
        current = file_sha(Path(initial["path"]))
        raw_records.append({"path": initial["path"], "before": initial["sha256"], "after": current, "status": "PASS" if current == initial["sha256"] else "FAIL"})
    save(EVIDENCE / "discovery/raw-inputs-final.json", raw_records)
    python = sys.executable
    venv = ROOT / "apps/chart/state/tmp/engine-audit-20261102T043157Z-venv/Scripts/python.exe"
    scripts = Path(__file__).resolve().parent
    check("lexical-output", [python, "-B", scripts / "lexical_output_check.py"])
    check("cli-contract", [python, "-B", scripts / "cli_contract_check.py"])
    check("engine-unit", [venv, "-B", "-m", "pytest", "engine/tests/unit", "-q", "-p", "no:cacheprovider"])
    check("allocation-pretraced", [venv, "-B", "-X", "tracemalloc=1", "-m", "pytest", "engine/tests/unit/test_carried_order_query.py::test_creation_lists_do_not_retain_both_dense_parent_and_b_history", "-q", "-p", "no:cacheprovider"])
    check("harness-unit", [python, "-B", scripts / "test_harness.py"])
    check("lexical-harness-unit", [python, "-B", scripts / "test_lexical_output.py"])
    check("references", [python, "-B", "engine/tests/verification/verify_order_references.py"])
    check("anti-drift-unit", [python, "-B", "scripts/verification/test_anti_drift.py"])
    check("anti-drift-full", [python, "-B", "scripts/verification/anti_drift.py", "--mode", "full", "--format", "human", "--verbose"])
    check("chart-contracts", ["node", "--test", "apps/chart/tests/unit/manual-review.test.mjs", "apps/chart/tests/unit/calculation-cache.test.mjs", "apps/chart/tests/unit/indicator-cache.test.mjs"])
    for phase in ["before", "after"]:
        for case, flag in [("xau-sep28-30s-bearish", "--xauusd-user-example"), ("usoil-month-30s-bearish", "--usoil-user-example")]:
            check(f"{phase}-{case}-anchors", [python, "-B", "engine/tests/regression/verify_pl_ph_raw.py", "--after", EVIDENCE / phase / case / "run-01.stdout.json", flag, "--formed-mbls"])
    workloads = json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())
    alignments = []
    for direction in ["bullish", "bearish"]:
        case = next(case for case in workloads if case["id"] == f"usoil-oct22-5s-{direction}-legacy-no-primary")
        raw = json.loads(Path(case["input"]).read_bytes())
        aligned = all(int(row["time"]) % 5 == 0 for row in raw)
        alignments.append({"case": case["id"], "rows": len(raw), "all_times_aligned_to_5s": aligned})
        if not aligned:
            raise RuntimeError("Known Order_B helper condition is not equivalent at these timestamps")
        for phase in ["before", "after"]:
            check(f"{phase}-order-b-{direction}", [python, "-B", "engine/tests/verification/verify_order_b_raw.py", "--raw", case["input"], "--payload", EVIDENCE / phase / case["id"] / "run-01.stdout.json", "--timeframe", "5"])
    save(EVIDENCE / "discovery/order-b-raw-alignment.json", alignments)
    if any(record["status"] != "PASS" for record in RECORDS) or any(record["status"] != "PASS" for record in raw_records):
        raise RuntimeError("Final checks contain failures; retain logs and classify before verdict")


if __name__ == "__main__":
    main()
