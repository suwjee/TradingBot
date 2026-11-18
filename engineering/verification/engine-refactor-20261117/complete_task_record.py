"""Finalize local task records from completed, scoped verification evidence."""
from datetime import datetime
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo


EVIDENCE = Path(__file__).resolve().parent


def main():
    checks_path = EVIDENCE / "checks-complete.json"
    checks = json.loads(checks_path.read_bytes())
    assert checks["status"] == "PASS"
    assert (EVIDENCE / "FINAL_REPORT.md").is_file()
    links = json.loads((EVIDENCE / "link-verification.json").read_bytes())
    assert links["status"] == "PASS"
    live = json.loads((EVIDENCE / "live-variant-results.json").read_bytes())
    assert len(live) == 4 and all(row["runs"] == 6 and row["cpu_measured_runs"] == 3 for row in live)
    variants = json.loads((EVIDENCE / "variant-results.json").read_bytes())
    assert sum(row["execution"] == "SUCCESS" for row in variants) == 42
    assert sum(row["execution"] == "UNCHANGED BASELINE FAILURE" for row in variants) == 4
    stamp = datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds")
    checks.update(completed_at=stamp, supplementary_live_wall_runs=6,
                  supplementary_live_cpu_runs=3, local_links=links["checked"],
                  scope="Exact preservation of tested successful outputs and four unchanged optional-configuration errors; not universal correctness.")
    checks_path.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    plan_path = EVIDENCE / "implementation-plan.md"
    plan = plan_path.read_text(encoding="utf-8").replace("- [ ]", "- [x]")
    plan = re.sub(r"(?m)^last_modified_at: .+$", "last_modified_at: " + stamp, plan)
    plan += "\n## Completion evidence\n\nAll plan steps completed for the stated preservation scope. See [the final report](FINAL_REPORT.md) for the measured full-file speedups, six-repeat bounded live results, the four unchanged disabled-behavior errors, exact output checks and unperformed independent market-correctness certification. No release or external Vault rebuild was performed.\n"
    plan_path.write_text(plan, encoding="utf-8", newline="\n")
    state = dict(status="COMPLETE: local implementation and scoped verification", completed_at=stamp,
                 final_source_frozen_at="2026-11-18T07:10:09+03:30", source_stable=True,
                 report="engineering/verification/engine-refactor-20261117/FINAL_REPORT.md",
                 engine_unit="PASS: 507 tests", chart_unit="PASS: 329 tests", build="PASS",
                 full_raw="PASS: four modes, three repeats per variant, direct stable bytes",
                 bounded_options="PASS equivalence: 42 successful outputs and four identical pre-existing errors",
                 bounded_live="PASS exact bytes: four modes, six horizons, six repeats per variant",
                 browser="PASS desktop/mobile Chart and Manual Review on fresh isolated server",
                 references="PASS: both directional references reconstruct current source exactly",
                 publication="No staging, commit, push, tag or release",
                 limitations=["Optional disabled Blue/A/S configuration retains its pre-existing KeyError.",
                              "Short live updates are not uniformly faster; wall and CPU results are disclosed.",
                              "External Vault snapshot and historical engine/engine.zip were not rebuilt.",
                              "Restart the ordinary local server and refresh/reapply the indicator to load current source.",
                              "No universal correctness proof for arbitrary inputs."])
    (EVIDENCE / "execution-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print("Finalized task records with explicit verification scope and limitations")


if __name__ == "__main__":
    main()
