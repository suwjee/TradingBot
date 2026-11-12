"""Summarize actual paired timing dispersion and separate profiling evidence."""
from __future__ import annotations
import json
import argparse
from pathlib import Path
import re
import statistics
from export_baseline_reports import write_csv
from export_final_reports import md
from matrix import EVIDENCE, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--controlled", action="store_true")
    args = parser.parse_args()
    tag = "controlled" if args.controlled else "paired"
    paired = json.loads((EVIDENCE / f"discovery/{tag}-benchmark.json").read_bytes())
    assert paired["status"] == "PASS"
    summaries = []
    phases = []
    for case_id in dict.fromkeys(pair["case"] for pair in paired["pairs"]):
        pairs = [pair for pair in paired["pairs"] if pair["case"] == case_id]
        summary = {"case": case_id, "pairs": len(pairs)}
        for key in ["wall_seconds", "cpu_seconds", "peak_working_set_bytes"]:
            deltas = [(pair["after"][key]/pair["before"][key]-1)*100 for pair in pairs]
            summary[key] = {"median_pair_delta_percent": statistics.median(deltas), "min_pair_delta_percent": min(deltas), "max_pair_delta_percent": max(deltas)}
        summaries.append(summary)
        values = {"before": [], "after": []}
        for pair in pairs:
            for side in values:
                path = EVIDENCE / f"{tag}-{side}-seed{pair['seed']}" / case_id / "run-01.stdout.json"
                values[side].append(json.loads(path.read_bytes())["timings"]["phasesMs"])
        labels = set().union(*(value for collection in values.values() for value in collection))
        for label in sorted(labels):
            before = [value[label] for value in values["before"] if label in value]
            after = [value[label] for value in values["after"] if label in value]
            b, a = statistics.median(before), statistics.median(after)
            phases.append({"case": case_id, "reported_phase": label, "before_samples": len(before), "after_samples": len(after),
                           "before_median_ms": b, "after_median_ms": a, "delta_percent": (a/b-1)*100 if b else "", "metric": "Bridge-reported wall phase telemetry, not process CPU; nested timings can overlap"})
    save(EVIDENCE / f"discovery/{tag}-effect-summary.json", summaries)
    write_csv("11_STAGE_TIMING_RESULTS.csv" if args.controlled else "11_STAGE_TIMING_INITIAL_PAIRS.csv", phases)
    profiles = []
    for case in ["xau-oct26-30s-bullish", "xau-oct26-30s-bearish"]:
        measured = {side: json.loads((EVIDENCE / phase / "profile" / case / "stats.json").read_bytes()) for side, phase in [("before", "repaired-before"), ("after", "after")]}
        for owner, function in [("order_audit_engine.py", "_carried_orders_for_parent"), ("order_audit_engine.py", "_post_stop_accepted_orders_for_parent"), ("e_zone_detector.py", "_zone"), ("blue_line_detector.py", "geometry_is_internal")]:
            pair = {side: next(row for row in records if Path(row["file"]).name == owner and row["function"] == function) for side, records in measured.items()}
            profiles.append({"case": case, "owner": owner, "function": function,
                             **{f"{side}_{key}": row[key] for side, row in pair.items() for key in ["line", "calls", "self_seconds", "cumulative_seconds"]}})
    write_csv("06_PROFILE_BEFORE_AFTER.csv", profiles)
    path = EVIDENCE / "06_PROFILE_HOTSPOTS.md"
    original = path.read_text(encoding="utf-8").split("\n## Final separate profile comparison")[0]
    table = "| Case | Function | BEFORE/AFTER calls | BEFORE/AFTER cumulative seconds |\n| --- | --- | ---: | ---: |\n"
    for row in profiles:
        table += f"| {row['case']} | {row['owner']}:{row['function']} | {row['before_calls']} / {row['after_calls']} | {row['before_cumulative_seconds']:.6f} / {row['after_cumulative_seconds']:.6f} |\n"
    text = original + "\n## Final separate profile comparison\n\n" + table + "\nThe fresh post-repair baseline and final profiles reproduce their actual CLI outputs exactly. Raw pstats are retained in repaired-before/profile and after/profile;06_PROFILE_BEFORE_AFTER.csv includes exact line/call/self/cumulative records. These are instrumented observations: removing generator calls also removes profiling overhead. Profile timing ratios are never quoted as normal runtime speedup; use the uninstrumented matched pairs/actual CPU/wall medians and dispersion. Cumulative values overlap and must not be summed. Bridge-reported phase timing comparisons are retained in11_STAGE_TIMING_RESULTS.csv and are wall telemetry, not process CPU.\n"
    # Preserve original evidence body/header; use the governing generated-document writer.
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    body = re.sub(r"\A\s*#[^\n]*\n", "", body, count=1)
    md("06_PROFILE_HOTSPOTS.md", "Engine CPU and allocation hotspots", body)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
