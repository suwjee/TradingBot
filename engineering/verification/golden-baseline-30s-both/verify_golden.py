#!/usr/bin/env python3
"""Fail-closed, immutable 30-second BOTH-direction TradingBot Golden verification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ZIP_SHA256 = "080175abbd7a3895596230b40783062901deb38c0cc8dd3b97fc058ef21cbb88"

def digest(content):
    return hashlib.sha256(content).hexdigest()

def stable_payload(raw):
    obj = json.loads(raw)
    if "error" in obj:
        raise ValueError("Engine returned error: " + repr(obj["error"]))
    if obj.get("timeframe") != 30 or set(obj.get("directions", [])) != {"bullish", "bearish"}:
        raise ValueError("Wrong timeframe or directions")
    marker = b',"timings":'
    offset = raw.rfind(marker)
    if offset < 0 or not raw.endswith(b"}"):
        raise ValueError("Missing final timings object")
    timing = obj["timings"]
    if not isinstance(timing, dict):
        raise ValueError("Wrong timing schema")
    phase = timing["phasesMs"]
    if not isinstance(phase, dict):
        raise ValueError("Missing timings.phasesMs")
    schema = {"phase_keys": list(phase), "phase_types": [type(v).__name__ for v in phase.values()],
              "total_type": type(timing["bridgeTotalMs"]).__name__}
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in phase.values()):
        raise ValueError("Non-numeric timing measurement")
    return raw[:offset] + b"}", schema

def command(engine, raw_path, item):
    p = engine / "pipeline"
    cmd = [sys.executable, "-B", str(engine / "bridge/trading_pipeline.py")]
    for flag, file in [
        ("reaction-engine", "reaction_engine.py"),
        ("blue-line-engine", "blue_line_detector.py"),
        ("a-zone-engine", "a_zone_detector.py"),
        ("s-zone-engine", "s_zone_detector.py"),
        ("e-zone-engine", "e_zone_detector.py"),
        ("lifecycle-engine", "lifecycle_engine.py"),
    ]:
        cmd += ["--" + flag, str(p / file)]
    cmd += ["--data", str(raw_path), "--timeframe", "30", "--raw-timeframe", "5",
            "--direction", "both", "--from-time", str(item["first_time"]), "--to-time", str(item["last_time"]),
            "--blue-lines", "enabled", "--a-zones", "enabled", "--s-zones", "enabled",
            "--pl-ph", "enabled", "--bridge-output"]
    return cmd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-zip", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    report = args.out_dir.resolve()
    report.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((HERE / "inputs.json").read_text(encoding="utf-8"))
    if digest(args.baseline_zip.read_bytes()) != ZIP_SHA256:
        sys.exit("FAIL: baseline ZIP SHA256 changed or wrong artifact")
    results = []
    with ZipFile(args.baseline_zip) as z:
        if z.testzip() is not None:
            sys.exit("FAIL: corrupted baseline ZIP")
        original_manifest = json.loads(z.read("input_manifest.json"))
        if original_manifest.get("commit") != manifest["baseline_git_commit"]:
            sys.exit("FAIL: wrong GitHub source commit")
        originals = {d["name"]: d for d in original_manifest["dataset"] if d["nominal_raw_seconds"] == 5}
        if set(originals) != {d["file"] for d in manifest["datasets"]}:
            sys.exit("FAIL: dataset identity mismatch")
        for item in manifest["datasets"]:
            outcome = {"id": item["id"], "file": item["file"], "status": "FAIL"}
            results.append(outcome)
            path = args.raw_dir / item["file"]
            try:
                if not path.is_file() or digest(path.read_bytes()) != item["raw_sha256"]:
                    raise ValueError("Missing or modified RAW input")
                if originals[item["file"]]["sha256"] != item["raw_sha256"]:
                    raise ValueError("Frozen ZIP RAW hash mismatch")
                stem = path.stem.replace(" ", "_")
                prefix = "runs/github_baseline/" + stem
                expected = z.read(prefix + ".stable.json")
                metrics = json.loads(z.read(prefix + ".metrics.json"))
                if digest(expected) != item["stable_output_sha256"]:
                    raise ValueError("Golden stable output hash mismatch")
                output = report / (stem + ".candidate.json")
                stderr = report / (stem + ".stderr.log")
                start = time.perf_counter()
                with output.open("wb") as fout, stderr.open("wb") as ferr:
                    proc = subprocess.run(command(args.candidate_root.resolve(), path.resolve(), item),
                                          stdout=fout, stderr=ferr,
                                          env={**os.environ, "PYTHONHASHSEED": "0",
                                               "PYTHONDONTWRITEBYTECODE": "1"})
                outcome["wall_s"] = round(time.perf_counter() - start, 5)
                outcome["exit_code"] = proc.returncode
                if proc.returncode:
                    raise ValueError("Engine execution failed")
                candidate, schema = stable_payload(output.read_bytes())
                if schema != metrics["telemetry_contract"]:
                    raise ValueError("Timing schema changed")
                outcome["candidate_stable_sha256"] = digest(candidate)
                outcome["golden_stable_sha256"] = digest(expected)
                if candidate != expected:
                    offset = next((i for i, (a, b) in enumerate(zip(expected, candidate)) if a != b),
                                  min(len(expected), len(candidate)))
                    outcome["first_diff_byte"] = offset
                    raise ValueError("Stable output differs from original baseline")
                outcome["status"] = "PASS"
            except Exception as exc:
                outcome["error"] = str(exc)
            (report / "comparison.json").write_text(json.dumps(results, indent=2, ensure_ascii=False),
                                                     encoding="utf-8")
            print(item["id"], outcome["status"], outcome.get("error", ""), flush=True)
    passed = sum(row["status"] == "PASS" for row in results)
    print("Exact golden verification:", passed, "/", len(results))
    return 0 if passed == len(manifest["datasets"]) else 1

if __name__ == "__main__":
    raise SystemExit(main())
