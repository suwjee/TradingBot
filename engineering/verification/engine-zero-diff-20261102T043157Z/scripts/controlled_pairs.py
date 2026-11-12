"""Control bytecode-cache reads as well as seeds/order in fresh CLI pairs."""
from __future__ import annotations
import gzip
import json
from pathlib import Path
from lexical_output_check import first_byte_difference, stable_serialized_bytes
from matrix import EVIDENCE, ROOT, calculation_arguments, first_diff, run, save
from paired_benchmark import SELECTED, system_cpu_ticks


def main():
    assert json.loads((EVIDENCE / "discovery/frozen-allocation-completion.json").read_bytes())["status"] == "PASS"
    prefix = ROOT / "apps/chart/state/tmp/engine-audit-pycache-control-20261102T043157Z"
    prefix.mkdir(exist_ok=True)
    if any(prefix.rglob("*")):
        raise RuntimeError("The explicit cache-control directory must remain empty")
    workloads = {item["id"]: item for item in json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())}
    frozen = EVIDENCE / "discovery/repaired-source-before"
    report = {"method": "Five seed-matched fresh-process CLI pairs per case; AB/BA/AB/BA/AB; both children use the same explicit empty PYTHONPYCACHEPREFIX and -B, eliminating asymmetric existing Source bytecode reads; no global settings/cache files modified", "pycache_prefix": str(prefix), "pairs": []}
    for case_id in SELECTED:
        for seed in range(5):
            order = ["before", "after"] if seed % 2 == 0 else ["after", "before"]
            phases = {side: f"controlled-{side}-seed{seed}" for side in order}
            records = {}
            for side in order:
                save(EVIDENCE / "discovery/controlled-progress.json", {"stage": "measuring", "case": case_id, "seed": seed, "side": side})
                begin = system_cpu_ticks()
                records[side] = run(workloads[case_id], phases[side], 1, 1800, frozen if side == "before" else ROOT, phases[side], str(seed), str(prefix))
                end = system_cpu_ticks()
                assert records[side]["status"] == "PASS"
                if begin and end:
                    delta = [after-before for before,after in zip(begin,end)]
                    records[side]["observed_system_busy_percent_over_controller_interval"] = (1-delta[0]/(delta[1]+delta[2]))*100
            raw = {side: (EVIDENCE / phases[side] / case_id / "run-01.stdout.json").read_bytes() for side in order}
            lexical = first_byte_difference(stable_serialized_bytes(raw["before"]), stable_serialized_bytes(raw["after"]))
            payloads = {side: json.loads(gzip.decompress((EVIDENCE / phases[side] / case_id / "run-01.stable.json.gz").read_bytes())) for side in order}
            difference = first_diff(payloads["before"], payloads["after"])
            context = calculation_arguments(records["before"]["command"]) == calculation_arguments(records["after"]["command"]) and records["before"]["input_sha256_before"] == records["after"]["input_sha256_before"]
            pair = {"case": case_id, "seed": seed, "execution_order": order, "before": records["before"], "after": records["after"], "context_equal": context, "first_difference": difference, "lexical_first_difference": lexical, "status": "PASS" if context and difference is None and lexical is None else "FAIL"}
            report["pairs"].append(pair)
            save(EVIDENCE / "discovery/controlled-benchmark.json", report)
            print(json.dumps({"case": case_id, "seed": seed, "status": pair["status"], "before_wall": records["before"]["wall_seconds"], "after_wall": records["after"]["wall_seconds"]}), flush=True)
            assert pair["status"] == "PASS"
            assert not any(prefix.rglob("*")), "-B cache-control run unexpectedly wrote files"
    report["status"] = "PASS"
    save(EVIDENCE / "discovery/controlled-benchmark.json", report)
    save(EVIDENCE / "discovery/controlled-progress.json", {"stage": "complete", "status": "PASS", "pairs": len(report["pairs"]), "cache_directory_empty": not any(prefix.rglob("*"))})


if __name__ == "__main__":
    main()
