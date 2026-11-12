"""Generate honest phase matrices from completed metric artifacts only."""
from __future__ import annotations
import csv
from datetime import datetime
import json
from pathlib import Path
import statistics
from zoneinfo import ZoneInfo
from matrix import EVIDENCE


def matrix(phase):
    cases = json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())
    result = []
    for case in cases:
        records = [json.loads(path.read_bytes()) for path in sorted((EVIDENCE / phase / case["id"]).glob("run-*.metrics.json"))]
        done = [item for item in records if item["exit_code"] == 0 and not item["timeout"]]
        status = "FAIL" if any(item["status"] == "FAIL" for item in records) else "PASS" if len(records) >= 2 and all(item["status"] == "PASS" for item in records) else "INCOMPLETE" if records else "NOT RUN"
        result.append({"scenario": case["id"], "input": case["input"], "input_kind": case["kind"], "rows": case["rows"],
                       "timeframe_seconds": case["timeframe"], "direction": case["direction"], "from_epoch": case["from_time"], "to_epoch": case["to_time"],
                       "primary": case.get("primary", "enabled"), "stopall": case.get("stopall", True), "bridge_output": case.get("bridge_output", True),
                       "runs": len(records), "engine_exit_zero_runs": len(done), "status": status,
                       "median_wall_seconds": statistics.median(item["wall_seconds"] for item in done) if done else "",
                       "min_wall_seconds": min((item["wall_seconds"] for item in done), default=""),
                       "max_wall_seconds": max((item["wall_seconds"] for item in done), default=""),
                       "median_cpu_seconds": statistics.median(item["cpu_seconds"] for item in done) if done else "",
                       "median_sampled_peak_working_set_bytes": statistics.median(item["peak_working_set_bytes"] for item in done) if done else "",
                       "max_sampled_peak_working_set_bytes": max((item["peak_working_set_bytes"] for item in done), default=""),
                       "raw_unchanged": all(item["input_sha256_before"] == item["input_sha256_after"] for item in records) if records else "NOT RUN",
                       "ordered_repeat_differences": sum(item.get("stable_bytes_equal") is False for item in records),
                       "evidence_directory": str(EVIDENCE / phase / case["id"])})
    return result


def write_csv(name, rows):
    with (EVIDENCE / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    original, repaired = matrix("before"), matrix("repaired-before")
    write_csv("04_BEFORE_BASELINE_MATRIX.csv", original)
    write_csv("04_REPAIRED_BEFORE_BASELINE_MATRIX.csv", repaired)
    stamp = datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds")
    original_status = {status: sum(row["status"] == status for row in original) for status in ["PASS", "FAIL", "INCOMPLETE", "NOT RUN"]}
    repaired_status = {status: sum(row["status"] == status for row in repaired) for status in ["PASS", "FAIL", "INCOMPLETE", "NOT RUN"]}
    text = f"""---
title: Engine baseline validity evidence
document_role: evidence
lifecycle: generated
owner: engine-zero-difference-audit
last_modified_at: {stamp}
---

# Baseline validity

Original pre-edit matrix: {original_status}, {sum(row['runs'] for row in original)} actual cold CLI runs. All44 original executions exited0 and retained complete stdout/stderr, but two ordered stable-repeat comparisons failed. Their two changed mapping-order paths and zero non-order differences were independently confirmed; see discovery/determinism-first-differences.json and reviews/determinism-review.md. Original exact determinism status remains FAIL. No timing exclusion beyond the documented top-level timings envelope is used.

The user subsequently delegated the explicitly proposed deterministic-key correction while preserving exact calculation content. That separate repair is recorded in08_CHANGE_LEDGER.md. The named repaired-before matrix is {repaired_status}, {sum(row['runs'] for row in repaired)} completed runs at this export. It is not valid for performance implementation until every required row is PASS and the separate original-calculation comparison has zero unexpected differences. Original failed outputs are never overwritten or relabeled.

## Reproduction and evidence

Workloads and original immutable input hashes are under discovery/. Supported actual Bridge CLI arguments are recorded per run in *.metrics.json; source bytes are captured under discovery/source-before/engine/. Each original RAW is hashed before/after each run. Full original serialized JSON bytes, full stderr progress/errors, compressed ordered stable JSON, per-stage counts/digests, wall/CPU and sampled OS PeakWorkingSet are retained. No historical size cap is applied: all five available RAW inputs including the309,266-row month are exercised, both directions independently, at5/30/60s with primary, StopAll, legacy/projection and presentation-window variants.

Normal CLI measurements exclude controller input hashing and after-run comparison, include Python import/startup/load/JSON I/O, and use the same interpreter/environment. Profiling and allocation tracing are separate runs. Windows process CPU is queried from native100ns counters. PeakWorkingSet is the OS-maintained peak sampled every50ms up to the final successful query; a peak only in the last sampling gap may be missed. Report this precision limit, not a stronger exact-at-exit memory claim.

Two cold repetitions were collected initially for every scenario to audit determinism before spending more benchmark time. Month executions take several minutes each; dispersion is retained, not reduced to a fastest-run claim. Additional comparable repetitions and warm measurements are required where practical for retained performance candidates. No speedup is claimed by these baseline measurements.

## Limitations and separate statuses

- Finest locally available real RAW in this discovered input set is5s. No1s RAW was available; exact sub-5s market ordering is NOT RUN.
- Synthetic1200-row smoke and current unit boundary/mirror/identity tests are artificial evidence, not market correctness.
- Complete public stage arrays are retained for each scenario; selective native stage graph collection and explicit native equality are separate pending gates, not implied by final JSON hashes.
- Cold import/runtime initialization PASS is supported by all successful actual CLI invocations and exact reconstructed-source compilation. Initial Engine296 tests and structural verifier31 tests passed; preparatory repair suite303 passed.
- Current accepted Reference byte/manifest/reconstruction validation PASS14files per document after the repair. This is separate from pre-existing Source/Vault/Reference semantic ambiguities.
- Independent real-market correctness needs approved anchor assertions/oracles and is not inferred from successful execution or mirror parity.
- No performance optimization has been accepted merely because the repair tests pass.
"""
    (EVIDENCE / "05_BASELINE_VALIDITY_REPORT.md").write_text(text, encoding="utf-8")
    print(json.dumps({"original": original_status, "repaired": repaired_status}, indent=2))


if __name__ == "__main__":
    main()
