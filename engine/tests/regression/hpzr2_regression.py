"""Compare the frozen pre-refactor engine with a candidate on physical RAW files.

The script writes each baseline output before running its candidate counterpart.
Only nondeterministic top-level timing telemetry is removed from exact JSON
comparison. RAW input files are read, never changed.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

import orjson


MODULES = (
    "pipeline/reaction_engine.py",
    "pipeline/blue_line_detector.py",
    "pipeline/a_zone_detector.py",
    "pipeline/s_zone_detector.py",
    "pipeline/e_zone_detector.py",
    "pipeline/lifecycle_engine.py",
    "bridge/trading_pipeline.py",
    "pipeline/direction_policy.py",
    "pipeline/core_utils.py",
)
STAGES = (
    "reactions",
    "resets",
    "blueLines",
    "aZones",
    "sZones",
    "eZones",
    "stopAlls",
    "orderAudit",
    "bridgeOutput",
)


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def source_hashes(root: Path) -> dict[str, str]:
    return {
        name: sha256((root / "engine" / name).read_bytes())
        for name in MODULES
    }


def command(root: Path, raw: Path, first: int, last: int, args) -> list[str]:
    engine = root / "engine"
    pipeline = engine / "pipeline"
    result = [
        sys.executable,
        str(engine / "bridge" / "trading_pipeline.py"),
        "--engine", str(pipeline / "reaction_engine.py"),
        "--blue-engine", str(pipeline / "blue_line_detector.py"),
        "--a-engine", str(pipeline / "a_zone_detector.py"),
        "--s-engine", str(pipeline / "s_zone_detector.py"),
        "--e-engine", str(pipeline / "e_zone_detector.py"),
        "--stopall-engine", str(pipeline / "lifecycle_engine.py"),
        "--data", str(raw),
        "--timeframe", str(args.timeframe),
        "--from-time", str(first),
        "--to-time", str(last),
        "--direction", args.direction,
    ]
    if args.bridge_output:
        result.append("--bridge-output")
    return result


def run(root: Path, raw: Path, first: int, last: int, args) -> tuple[dict, bytes, float]:
    started = perf_counter()
    completed = subprocess.run(
        command(root, raw, first, last, args),
        capture_output=True,
        timeout=args.timeout_seconds,
        check=False,
    )
    elapsed = perf_counter() - started
    if completed.returncode:
        raise RuntimeError(
            f"engine exit {completed.returncode}: "
            + completed.stderr.decode("utf-8", errors="replace")[-2000:]
        )
    payload = json.loads(completed.stdout)
    timings = payload.pop("timings", None)
    normalized = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode()
    return {"timings": timings, "wallSeconds": elapsed}, normalized, len(completed.stdout)


def stage_hashes(normalized: bytes) -> dict[str, dict[str, dict[str, object]]]:
    payload = json.loads(normalized)
    result = {}
    for direction, items in payload["directions"].items():
        result[direction] = {}
        for stage in STAGES:
            if stage not in items:
                continue
            value = items[stage]
            encoded = json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode()
            result[direction][stage] = {
                "count": len(value),
                "sha256": sha256(encoded),
            }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--timeframe", type=int, default=30)
    parser.add_argument("--direction", choices=("bullish", "bearish", "both"), default="both")
    parser.add_argument("--bridge-output", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--select", action="append", default=[])
    args = parser.parse_args()
    baseline = args.baseline_root.resolve()
    candidate = args.candidate_root.resolve()
    raw_root = args.raw_root.resolve()
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=True)
    files = sorted((
        item for item in raw_root.rglob("*.json")
        if not item.name.endswith(".meta.json")
        and (not args.select or any(token in str(item) for token in args.select))
    ), key=lambda item: (item.stat().st_size, str(item)))
    manifest = {
        "comparison": "ordered JSON bytes after removing top-level timings only",
        "baselineSourceSha256": source_hashes(baseline),
        "candidateSourceSha256": source_hashes(candidate),
        "timeframe": args.timeframe,
        "direction": args.direction,
        "bridgeOutput": args.bridge_output,
        "cases": [],
    }
    manifest_path = output / "manifest.json"
    for index, raw in enumerate(files, start=1):
        raw_bytes = raw.read_bytes()
        rows = orjson.loads(raw_bytes)
        first = int(rows[0]["time"])
        last = int(rows[-1]["time"])
        name = f"case-{index:02d}"
        record = {
            "name": name,
            "rawPath": str(raw.relative_to(raw_root)),
            "rawSha256": sha256(raw_bytes),
            "rawRows": len(rows),
            "rawFirst": first,
            "rawLast": last,
            "status": "running baseline",
        }
        manifest["cases"].append(record)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{name} {record['rawPath']} rows={len(rows)}", flush=True)
        del raw_bytes, rows
        try:
            baseline_meta, baseline_json, baseline_stdout_bytes = run(
                baseline, raw, first, last, args
            )
            with gzip.open(output / f"{name}.baseline.json.gz", "wb") as saved:
                saved.write(baseline_json)
            record["baseline"] = {
                **baseline_meta,
                "stdoutBytes": baseline_stdout_bytes,
                "normalizedBytes": len(baseline_json),
                "normalizedSha256": sha256(baseline_json),
                "stages": stage_hashes(baseline_json),
            }
            record["rawSha256AfterBaseline"] = sha256(raw.read_bytes())
            if record["rawSha256AfterBaseline"] != record["rawSha256"]:
                raise RuntimeError("RAW changed during the baseline calculation")
            record["status"] = "baseline saved; running candidate"
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            candidate_meta, candidate_json, candidate_stdout_bytes = run(
                candidate, raw, first, last, args
            )
            with gzip.open(output / f"{name}.candidate.json.gz", "wb") as saved:
                saved.write(candidate_json)
            record["candidate"] = {
                **candidate_meta,
                "stdoutBytes": candidate_stdout_bytes,
                "normalizedBytes": len(candidate_json),
                "normalizedSha256": sha256(candidate_json),
                "stages": stage_hashes(candidate_json),
            }
            record["exactJsonEqual"] = baseline_json == candidate_json
            record["exactObjectsEqual"] = json.loads(baseline_json) == json.loads(candidate_json)
            record["rawSha256AfterCandidate"] = sha256(raw.read_bytes())
            raw_unchanged = record["rawSha256AfterCandidate"] == record["rawSha256"]
            record["status"] = (
                "PASS" if record["exactJsonEqual"] and record["exactObjectsEqual"]
                and raw_unchanged else "FAIL"
            )
            if record["status"] == "FAIL":
                print(f"{name}: FAIL", flush=True)
                manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
                return 1
            print(f"{name}: PASS", flush=True)
        except subprocess.TimeoutExpired:
            record["status"] = "INCOMPLETE"
            record["error"] = f"engine timed out after {args.timeout_seconds} seconds"
            print(f"{name}: INCOMPLETE {record['error']}", flush=True)
        except (RuntimeError, ValueError, KeyError) as exc:
            record["status"] = "INCOMPLETE"
            record["error"] = str(exc)
            print(f"{name}: INCOMPLETE {exc}", flush=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if all(case["status"] == "PASS" for case in manifest["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
