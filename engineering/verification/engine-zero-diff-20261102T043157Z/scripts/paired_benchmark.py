"""Alternating uninstrumented before/after pairs with explicit shared hash seeds."""
from __future__ import annotations
from datetime import datetime, timezone
import gzip
import json
import ctypes
from pathlib import Path
import time
from matrix import EVIDENCE, ROOT, calculation_arguments, first_diff, run, save
from lexical_output_check import first_byte_difference, stable_serialized_bytes

SELECTED = ["xau-oct26-30s-bullish", "xau-oct26-30s-bearish", "usoil-oct22-5s-bearish-legacy-no-primary"]


def system_cpu_ticks():
    counters = [ctypes.c_ulonglong() for _ in range(3)]
    if not ctypes.windll.kernel32.GetSystemTimes(*[ctypes.byref(value) for value in counters]):
        return None
    return [value.value for value in counters]


def main():
    # This controller intentionally waits without executing another workload.
    progress_path = EVIDENCE / "discovery/after-collection-progress.json"
    while True:
        if progress_path.exists():
            state = json.loads(progress_path.read_bytes())
            if state["stage"] == "failed":
                raise RuntimeError("AFTER collection failed; paired workload not started")
            if state["stage"] == "complete" and state["status"] == "PASS":
                break
        time.sleep(3)
    workloads = {item["id"]: item for item in json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())}
    frozen = EVIDENCE / "discovery/repaired-source-before"
    report = {"method": "Five seed-matched cold CLI pairs, AB/BA/AB/BA/AB; each side separate process; no profiler; explicitly auxiliary to default-randomized baseline", "pairs": []}
    for case_id in SELECTED:
        for seed in range(5):
            phase = {side: f"paired-{side}-seed{seed}" for side in ("before", "after")}
            sides = ["before", "after"] if seed % 2 == 0 else ["after", "before"]
            records = {}
            for side in sides:
                save(EVIDENCE / "discovery/paired-progress.json", {"stage": "measuring", "case": case_id, "seed": seed, "side": side, "utc": datetime.now(timezone.utc).isoformat()})
                system_before = system_cpu_ticks()
                records[side] = run(workloads[case_id], phase[side], 1, 1800, frozen if side == "before" else ROOT, phase[side], str(seed))
                system_after = system_cpu_ticks()
                if system_before and system_after:
                    delta = [after-before for before,after in zip(system_before, system_after)]
                    records[side]["observed_system_busy_percent_over_controller_interval"] = (1-delta[0]/(delta[1]+delta[2]))*100
                if records[side]["status"] != "PASS":
                    raise RuntimeError(f"Paired process failed: {case_id}/{seed}/{side}")
            raw = {side: gzip.decompress((EVIDENCE / phase[side] / case_id / "run-01.stable.json.gz").read_bytes()) for side in sides}
            difference = first_diff(json.loads(raw["before"]), json.loads(raw["after"]))
            lexical = {side: stable_serialized_bytes((EVIDENCE / phase[side] / case_id / "run-01.stdout.json").read_bytes()) for side in sides}
            lexical_difference = first_byte_difference(lexical["before"], lexical["after"])
            context = (records["before"]["input_sha256_before"] == records["after"]["input_sha256_before"]
                       and calculation_arguments(records["before"]["command"]) == calculation_arguments(records["after"]["command"]))
            pair = {"case": case_id, "seed": seed, "execution_order": sides, "context_equal": context,
                    "stable_bytes_equal": raw["before"] == raw["after"], "first_difference": difference,
                    "lexical_first_difference": lexical_difference,
                    "before": records["before"], "after": records["after"]}
            pair["status"] = "PASS" if context and pair["stable_bytes_equal"] and difference is None and lexical_difference is None else "FAIL"
            report["pairs"].append(pair)
            save(EVIDENCE / "discovery/paired-benchmark.json", report)
            print(json.dumps({"case": case_id, "seed": seed, "status": pair["status"], "before_wall": records["before"]["wall_seconds"], "after_wall": records["after"]["wall_seconds"]}), flush=True)
            if pair["status"] != "PASS":
                raise RuntimeError(f"Paired first difference: {case_id}/{seed}")
    report["status"] = "PASS"
    save(EVIDENCE / "discovery/paired-benchmark.json", report)
    save(EVIDENCE / "discovery/paired-progress.json", {"stage": "complete", "status": "PASS", "pairs": len(report["pairs"]), "utc": datetime.now(timezone.utc).isoformat()})


if __name__ == "__main__":
    main()
