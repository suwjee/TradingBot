"""Compare supported switch and invalid-input CLI responses without changing RAW."""
from __future__ import annotations
import json
import argparse
from pathlib import Path
import subprocess
from lexical_output_check import first_byte_difference, stable_serialized_bytes
from matrix import EVIDENCE, ROOT, command, file_sha, phase_source_guard, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-name", default="cli-contract-v2")
    args = parser.parse_args()
    if Path(args.evidence_name).name != args.evidence_name:
        raise ValueError("Evidence name must be one local directory component")
    workloads = json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())
    base = dict(next(case for case in workloads if case["id"] == "synthetic1200-30s-bullish"))
    base["direction"] = "both"
    empty = EVIDENCE / "discovery/derived-fixtures/empty-contract.json"
    if empty.exists() and empty.read_bytes() != b"[]\n":
        raise RuntimeError("Existing derived fixture differs; preserve it")
    if not empty.exists():
        empty.write_bytes(b"[]\n")
    missing = EVIDENCE / "discovery/derived-fixtures/missing-contract-never-created.json"
    if missing.exists():
        raise RuntimeError("Missing-input contract path unexpectedly exists")
    cases = [
        ("s-disabled", {}, ["--s-zones", "disabled"]),
        ("all-secondary-disabled", {"primary": "disabled", "omit_e_engine": True}, ["--blue-lines", "disabled", "--a-zones", "disabled", "--s-zones", "disabled"]),
        ("zero-timeframe", {"timeframe": 0}, []),
        ("empty-input", {"input": str(empty)}, []),
        ("missing-input", {"input": str(missing)}, []),
        ("reversed-window", {"from_time": base["to_time"], "to_time": base["from_time"]}, []),
        ("unknown-switch", {}, ["--not-a-tradingbot-switch"]),
    ]
    frozen = EVIDENCE / "discovery/repaired-source-before"
    report = {"scope": "Public stdout/exit-code exactness; complete stderr retained, progress duration telemetry is not a stable error contract; no arbitrary user-defined private-ledger objects or traceback-frame equality claim", "cases": []}
    for name, overrides, flags in cases:
        outputs = {}
        for phase, source_root in [("repaired-before", frozen), ("after", ROOT)]:
            phase_source_guard(phase, source_root)
            case = {**base, **overrides}
            cmd = command(case, source_root) + flags
            if case.get("omit_e_engine"):
                position = cmd.index("--e-engine")
                del cmd[position:position+2]
            directory = EVIDENCE / args.evidence_name / name / phase
            directory.mkdir(parents=True, exist_ok=False)
            result = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (directory / "stdout.json").write_bytes(result.stdout)
            (directory / "stderr.log").write_bytes(result.stderr)
            save(directory / "metadata.json", {"command": cmd, "exit_code": result.returncode, "input_sha256": file_sha(Path(case["input"])) if Path(case["input"]).exists() else None})
            has_stdout = bool(result.stdout.strip())
            if not has_stdout and result.returncode == 0:
                raise RuntimeError("A successful Bridge invocation must return JSON")
            outputs[phase] = (result.returncode, stable_serialized_bytes(result.stdout) if has_stdout else result.stdout,
                              json.loads(result.stdout).get("error") if has_stdout else None,
                              result.stderr if not has_stdout else None)
        difference = first_byte_difference(outputs["repaired-before"][1], outputs["after"][1])
        stderr_equal = outputs["repaired-before"][3] == outputs["after"][3]
        report["cases"].append({"case": name, "status": "PASS" if outputs["repaired-before"][0] == outputs["after"][0] and difference is None and stderr_equal else "FAIL", "before_exit": outputs["repaired-before"][0], "after_exit": outputs["after"][0], "before_error": outputs["repaired-before"][2], "after_error": outputs["after"][2], "bare_error_stderr_equal": stderr_equal, "first_byte_difference": difference})
    report["status"] = "PASS" if all(item["status"] == "PASS" for item in report["cases"]) else "FAIL"
    save(EVIDENCE / "discovery/cli-contract-comparison.json", report)
    print(json.dumps(report))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
