"""Independently verify saved HPZR2 RAW regression evidence.

The comparison runner writes each baseline result before its candidate result.
This reader verifies the saved bytes, their manifest hashes, current RAW hashes,
and coverage across the default and Bridge Output runs without executing engines.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path
from statistics import median
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[3]
LOCAL_STATE = Path(os.environ.get("TRADINGBOT_LOCAL_STATE_ROOT", ROOT / "apps" / "chart" / "state"))
EVIDENCE = ROOT / "engineering" / "archive" / "docs" / "hpzr2-regression-2026-09-23"
RAW = LOCAL_STATE / "data" / "raw"
RUNS = ("default", "bridge-output", "bridge-output-large")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def benchmark_summary() -> dict:
    folder = EVIDENCE / "synthetic-benchmark"
    fixture_sha = digest((folder / "synthetic-60000.json").read_bytes())
    result = {}
    for mode, prefix in (("default", "repeat-default-"), ("bridgeOutput", "repeat-")):
        sides = {}
        for side in ("baseline", "optimized"):
            rows = [
                json.loads((folder / f"{prefix}{side}-{index}.summary.json").read_text(encoding="utf-8"))
                for index in (1, 2, 3)
            ]
            assert len({row["normalized_sha256"] for row in rows}) == 1
            groups = {
                "Reaction": lambda phase: phase.startswith("Reaction geometry") or phase == "Internal Reaction ownership",
                "Blue": lambda phase: phase.startswith("Blue Line •"),
                "A": lambda phase: phase.startswith("A •"),
                "S": lambda phase: phase.startswith("S •"),
                "E": lambda phase: phase.startswith("E •"),
                "Lifecycle": lambda phase: phase.startswith(("Reconcile S visibility", "StopAll -", "Apply visibility filters")),
                "Serialization": lambda phase: phase.startswith(("Serialize Reaction", "Serialize output")),
            }
            sides[side] = {
                "wallSeconds": [row["wall_seconds"] for row in rows],
                "cpuSeconds": [row["cpu_seconds"] for row in rows],
                "peakWorkingSetBytes": [row["peak_working_set_bytes"] for row in rows],
                "medianWallSeconds": median(row["wall_seconds"] for row in rows),
                "medianCpuSeconds": median(row["cpu_seconds"] for row in rows),
                "medianPeakWorkingSetBytes": median(row["peak_working_set_bytes"] for row in rows),
                "medianStageMs": {
                    stage: median(
                        sum(value for phase, value in row["timings"]["phasesMs"].items() if match(phase))
                        for row in rows
                    )
                    for stage, match in groups.items()
                },
                "stdoutSha256IncludingTimings": [row["raw_sha256"] for row in rows],
                "outputSha256": rows[0]["normalized_sha256"],
            }
        assert sides["baseline"]["outputSha256"] == sides["optimized"]["outputSha256"]
        for side in ("baseline", "optimized"):
            saved_output = (folder / f"{prefix}{side}-1.normalized.json").read_bytes().rstrip(b"\r\n")
            assert digest(saved_output) == sides[side]["outputSha256"]
        result[mode] = {
            "inputSha256": fixture_sha,
            **sides,
            "medianWallSpeedup": sides["baseline"]["medianWallSeconds"] / sides["optimized"]["medianWallSeconds"],
        }
    return result


def verify() -> dict:
    manifests = {
        name: json.loads((EVIDENCE / name / "manifest.json").read_text(encoding="utf-8"))
        for name in RUNS
    }
    baseline_hashes = manifests["default"]["baselineSourceSha256"]
    candidate_hashes = manifests["default"]["candidateSourceSha256"]
    with zipfile.ZipFile(EVIDENCE / "frozen-baseline-source.zip") as frozen:
        for module, expected in baseline_hashes.items():
            assert digest(frozen.read(f"engine/{module}")) == expected, module
    for module, expected in candidate_hashes.items():
        assert digest((ROOT / "engine" / module).read_bytes()) == expected, module

    coverage: dict[str, dict[str, dict]] = {"default": {}, "bridgeOutput": {}}
    incomplete = []
    verified = []
    for run_name, manifest in manifests.items():
        assert manifest["baselineSourceSha256"] == baseline_hashes, run_name
        assert manifest["candidateSourceSha256"] == candidate_hashes, run_name
        assert manifest["direction"] == "both" and manifest["timeframe"] == 30
        mode = "bridgeOutput" if manifest["bridgeOutput"] else "default"
        for case in manifest["cases"]:
            if case["status"] != "PASS":
                incomplete.append({"run": run_name, "case": case["name"], "rawPath": case["rawPath"]})
                continue
            raw_path = case["rawPath"]
            raw_sha = digest((RAW / raw_path).read_bytes())
            assert raw_sha == case["rawSha256"], (run_name, raw_path, "current RAW")
            for suffix in ("AfterBaseline", "AfterCandidate"):
                if f"rawSha256{suffix}" in case:
                    assert case[f"rawSha256{suffix}"] == raw_sha, (run_name, raw_path, suffix)
            assert case["exactJsonEqual"] and case["exactObjectsEqual"]
            saved = {}
            for side in ("baseline", "candidate"):
                with gzip.open(EVIDENCE / run_name / f"{case['name']}.{side}.json.gz", "rb") as stream:
                    content = stream.read()
                assert len(content) == case[side]["normalizedBytes"]
                assert digest(content) == case[side]["normalizedSha256"]
                parsed = json.loads(content)
                for direction, stages in case[side]["stages"].items():
                    for stage, recorded in stages.items():
                        value = parsed["directions"][direction][stage]
                        stage_bytes = json.dumps(
                            value, separators=(",", ":"), ensure_ascii=True
                        ).encode()
                        assert len(value) == recorded["count"]
                        assert digest(stage_bytes) == recorded["sha256"]
                saved[side] = content
            assert saved["baseline"] == saved["candidate"], (run_name, raw_path)
            payload = json.loads(saved["baseline"])
            assert "timings" not in payload
            assert payload["directions"].keys() == {"bullish", "bearish"}
            assert case["baseline"]["stages"] == case["candidate"]["stages"]
            assert raw_path not in coverage[mode], (mode, raw_path, "duplicate PASS")
            item = {
                "run": run_name,
                "case": case["name"],
                "rawRows": case["rawRows"],
                "rawSha256": raw_sha,
                "outputSha256": digest(saved["baseline"]),
                "baselineSeconds": case["baseline"]["wallSeconds"],
                "candidateSeconds": case["candidate"]["wallSeconds"],
                "speedup": case["baseline"]["wallSeconds"] / case["candidate"]["wallSeconds"],
            }
            coverage[mode][raw_path] = item
            verified.append({"mode": mode, "rawPath": raw_path, **item})
    assert coverage["default"].keys() == coverage["bridgeOutput"].keys(), "mode coverage differs"
    return {
        "result": "PASS",
        "comparison": "saved ordered JSON bytes and parsed objects, excluding top-level timings only",
        "physicalRawFiles": len(coverage["default"]),
        "verifiedComparisons": len(verified),
        "allCurrentRawHashesMatch": True,
        "allSavedOutputHashesMatch": True,
        "allSavedOutputsExactlyEqual": True,
        "supersededIncompleteRuns": incomplete,
        "syntheticBenchmark": benchmark_summary(),
        "cases": verified,
    }


if __name__ == "__main__":
    try:
        summary = verify()
    except (AssertionError, KeyError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
    path = EVIDENCE / "summary.json"
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"PASS: {summary['verifiedComparisons']} exact saved comparisons across "
          f"{summary['physicalRawFiles']} physical RAW files; {path}")
