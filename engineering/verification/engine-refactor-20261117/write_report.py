"""Write the final task report only after the recorded acceptance checks pass."""
from datetime import datetime
import json
from pathlib import Path
import re
import statistics
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent


def main():
    checks = json.loads((EVIDENCE / "checks-complete.json").read_bytes())
    assert checks["status"] == "PASS"
    assert json.loads((EVIDENCE / "paired-replacement-complete.json").read_bytes())["status"] == "PASS"
    results = json.loads((EVIDENCE / "performance-results.json").read_bytes())
    assert len(results) == 4 and all(row["runs"] == 3 for row in results)
    assert all(row["speedup"] > 1 for row in results), "A completed workload did not improve; performance acceptance needs review."
    variants = json.loads((EVIDENCE / "variant-results.json").read_bytes())
    assert len(variants) == 46 and all(row["comparison"] == "PASS" for row in variants)
    assert sum(row["execution"] == "SUCCESS" for row in variants) == 42
    assert sum(row["execution"] == "UNCHANGED BASELINE FAILURE" for row in variants) == 4
    live_variants = json.loads((EVIDENCE / "live-variant-results.json").read_bytes())
    assert len(live_variants) == 4 and all(row["runs"] >= 3 and row["comparison"].startswith("PASS") for row in live_variants)
    live_runs = {row["runs"] for row in live_variants}
    assert len(live_runs) == 1
    live_runs = live_runs.pop()
    manifest = json.loads((EVIDENCE / "source-input-manifest.json").read_bytes())
    engine_log = (EVIDENCE / "engine-final.log").read_text(encoding="utf-8")
    engine_count = re.findall(r"(\d+) passed", engine_log)[-1]
    chart_log = (EVIDENCE / "chart-final.log").read_text(encoding="utf-8")
    chart_count = re.findall(r"(?:#|ℹ)\s+pass\s+(\d+)", chart_log)[-1]
    stamp = datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds")
    created = stamp
    target = EVIDENCE / "FINAL_REPORT.md"
    if target.exists():
        found = re.search(r"(?m)^created_at: (.+)$", target.read_text(encoding="utf-8"))
        if found:
            created = found[1]
    performance = ["| RAW | Initial request direction | Baseline median (s) | Final median (s) | Wall speedup | CPU speedup |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    memory = ["| RAW | Initial request direction | Baseline median peak (MiB) | Final median peak (MiB) |", "| --- | --- | ---: | ---: |"]
    for row in results:
        performance.append(f"| {row['symbol']} | {row['direction']} | {row['baseline_median_seconds']:.3f} | {row['optimized_median_seconds']:.3f} | {row['speedup']:.3f}x | {row['cpu_speedup']:.3f}x |")
        memory.append(f"| {row['symbol']} | {row['direction']} | {row['baseline_peak_working_set_median_bytes']/2**20:.2f} | {row['optimized_peak_working_set_median_bytes']/2**20:.2f} |")
    raw_rows = "\n".join(f"- `{item['path']}`: {item['rows']:,} original rows; epoch range `{item['start_epoch']}..{item['end_epoch']}`; finest supplied positive step `{item['finest_positive_step_seconds']}s`." for item in manifest["inputs"])
    live_table = ["| RAW | Direction | Seed median before / after (ms) | Five appends median before / after (ms) | Seed CPU ratio | Appends CPU ratio |",
                  "| --- | --- | ---: | ---: | ---: | ---: |"]
    for row in live_variants:
        values = {}
        for mode in ("seed_seconds", "append_seconds"):
            values[mode] = " / ".join(f"{statistics.median(item[mode] for item in row['measurements'][variant])*1000:.1f}" for variant in ("removed", "optimized"))
        live_table.append(f"| {row['symbol']} | {row['direction']} | {values['seed_seconds']} | {values['append_seconds']} | {row['seed_cpu_seconds_speedup']:.3f}x | {row['append_cpu_seconds_speedup']:.3f}x |")
    report = f"""---
title: Engine assessment removal and zero-difference performance report
document_role: evidence
lifecycle: historical
owner: engine-refactor-20261117
created_at: {created}
last_modified_at: {stamp}
---

# Engine removal and performance report

The requested T/F assessment and trading-position extension has been removed. The separate implementation refactor preserves every tested remaining stable output, including Decimal strings, event chronology, physical identities, provenance, lifecycle, array order and mapping order. This is exact equivalence to the post-removal baseline for the executed cases; it is not a formal proof for every possible input or independent certification of unchanged trading rules.

## Completed scope

- Removed the standalone automatic bullish setup Engine, Bridge projection/execution and live setup state. The six retired fields are `setupVersion`, `setupPhase`, `positionSetups`, `stopAllAssessments`, `behaviorAssessments` and `setupReferenceBreaks`, including independent regimes.
- Removed automatic Chart T/F/Buy annotations, manual Long/Short tools, position geometry controls, and Manual Review verdict selection, bulk actions, storage integration and verdict export column. Native report data, category/date filters, Bridge detail, copy/download, Measure and unrelated drawings remain. Legacy retired drawings are omitted by scoped normalization; unrelated state is retained.
- Reviewed the live production Python closure and relevant runtime imports, current engineering procedures, both directional References and affected tests/consumers. Physical Order/OrderAudit, Reaction, Reset, Blue, A, S, E, StopAll and PL/PH/MBL formation remain native calculation owners. Ordinary Boolean validity/state flags remain.
- No RAW modification, staging, commit, push, tag, publication or Graphify execution occurred. The initial working tree was clean; work is uncommitted on `main` from HEAD `26a61a08328e71c478d73eb866b346df1b8e7fdd`.

## Implementation changes

| Owner | Change and preservation contract |
| --- | --- |
| Reaction | Reuse main-candle range indexes for longer extrema queries; reflected queries reuse the original opposite extreme and `copy_negate`. Earliest equal source, Decimal representation and live index release remain unchanged. |
| A | Reuse the existing lower range index instead of allocating/scanning a window. Inclusive exact endpoint and main-only fallback remain unchanged. |
| E | Reuse immutable directional sparse geometry within one chronology; index first physical S parents and maximum child decisions during enqueue. Native parent/child ownership and dynamic replacement remain unchanged. |
| Lifecycle | Replace repeated full-history S predecessor scans with ordered queries and repeated lifetime dominance scans with a sweep. Strict predecessor time, first equal winner, E-before-S ties and inclusive lifetimes remain unchanged. |
| OrderAudit | Index carried creation time, avoid invalidating it for later/equal parent provenance, and lazily merge accepted post-stop candidates. All causes remain in the authoritative ledger. New identity/earlier creation, reparent/revocation/rebuild invalidation and exact tie order remain protected. Conservative legacy paths retain demonstrated malformed-row exception behavior and Decimal flags. |

## Exact-equivalence evidence

- The original full USOIL bullish output versus the isolated feature-removal baseline differs only by the six retired annotation fields. The baseline retains the original native calculation source; only the removal-owned Bridge paths differ.
- Four complete RAW/request modes were each executed three times before and three times after optimization. All six stable serialized outputs within each mode are directly byte-identical after excluding only the top-level `timings` telemetry. The first optimized matrix sample was superseded by final-source review fixes; that candidate and its paired baseline were both actually rerun in immediate succession. Earlier sample summaries were retained separately rather than relabeled as final evidence.
- The 46 bounded option/timeframe/direction/hash-seed cases comprise 42 successful exact stable byte comparisons and four reproduced unchanged baseline failures. Successful cases cover 1/5/30/60-second calculation timeframes, both individual directions and combined output, presentation clipping, legacy projection, disabled primary/lifecycle options and process seed repeats. The bounded fixtures retain the original JSON price lexemes by exact byte-prefix slicing. The four disabled-behavior cases compare exception type/arguments, owning Engine call chain, Decimal flags and empty stdout exactly; they are not described as successful calculations.
- Targeted range, source-ownership, lifecycle, malformed-row, eager-error, identity replacement, reset, mirror and live-continuation tests pass. The separate E route comparator exercises 3,456 bounded scenarios; it compares frozen original E route code with current eager/lazy query behavior, not an independently reconstructed market algorithm.
- Bounded real-data live continuation also passes: two symbols, both initial directions, six successive horizons through 8,000 original rows and {live_runs} repeats per variant. Seed and append timings are recorded separately in [live continuation results](live-variant-results.json); they are distinct from the full-file manual-calculation speed table.

## Performance

The table reports end-to-end fresh-process pipeline time at a 30-second calculation timeframe with the complete supplied 5-second RAW, primary/lifecycle behavior and Bridge Output enabled. An individual initial direction can require both native directions and later independent reversal regimes. The baseline already excludes the retired setup extension, so the ratios measure refactoring rather than feature-removal savings. Values are medians of three executions; no profiler was active during these measurements. [Environment](environment.json), [raw measurements and phases](performance-results.json), [source/input identities](source-input-manifest.json).

{chr(10).join(performance)}

The shared workstation showed runtime variation. The complete per-run wall/CPU durations remain in the linked measurements; the ratios apply to these recorded inputs and configuration, not every future dataset or computer.

### Short live continuations

These bounded updates take fractions of a second and do not reproduce the full-file workload. After the first three runs showed mixed wall-clock results, three additional runs recorded CPU time as well. All original runs remain included: {live_runs} wall-time repeats and three instrumented CPU repeats per variant. A CPU ratio below 1 means slower in this sample. Initial [three-run evidence](live-variant-results-first-three.json) is retained separately. There is no claim that every short live update is faster.

{chr(10).join(live_table)}

## Peak memory

Windows process peak working set is measured separately from elapsed time. The optimization does not clip historical input or remove required calculation state.

{chr(10).join(memory)}

## Inputs

{raw_rows}

These are frozen copies inside ignored project-local scratch. The original acquired RAW was not rewritten. No finer supplied dataset was discovered for these selected spans. Input hashes and interval metadata are evidence, not trading-rule authority.

## Verification status

| Check | Status | Evidence |
| --- | --- | --- |
| Final Engine unit and contract suite | PASS | {engine_count} tests; [log](engine-final.log) |
| Final Chart unit suite | PASS | {chart_count} tests; [log](chart-final.log) |
| Build | PASS | [log](build-final.log); existing Vite large-chunk warning remains |
| Live worker restart/recovery integration | PASS | [log](live-recovery-final.log) |
| Full RAW exact equality and deterministic repeats | PASS | [summary](summary.log), [measurements](performance-results.json) |
| Bounded option/timeframe/process-seed equivalence | PASS | [46 results](variant-results.json): 42 successful outputs, four identical pre-existing errors |
| Simultaneously disabled Blue/A/S with PL/PH disabled | FAIL | Pre-existing in both baseline and final; see the limitation below |
| Bounded real-data live continuation and repeats | PASS | [results](live-variant-results.json), six horizons and {live_runs} repeats per mode |
| E route adjudication comparison | PASS | [log](e-routes-final.log) |
| Directional exact-source Reference reconstruction | PASS | [log](references-final.log), both References reconstruct the live source byte-for-byte |
| Source/input snapshot isolation | PASS | [log](manifest-final.log) |
| Desktop/mobile Chart and Manual Review browser interaction | PASS | [contract audit](contracts-audit.md), [Chart screenshot](browser/chart-removal-desktop.png), [review screenshot](browser/manual-report-desktop.png) |
| Source review | PASS | [review report](final-code-review.md); requested reviewer-authored compatibility fixes are disclosed |
| Documentation integrity and final whitespace diff | PASS | [anti-drift](anti-drift-final.log), [diff](diff-final.log) |
| Independent correctness of all unchanged trading rules on arbitrary markets | NOT RUN | Outside behavior-preserving comparison; no universal market-correctness claim |

`ZERO-DIFFERENCE REFACTOR VERIFIED` for the executed post-removal behavior contract and stated scope.

## Operational and evidence limits

- The existing user server on port5173 retained old transformed modules because its watcher was disabled. Browser verification used a fresh isolated server, which was stopped afterward. Restart the ordinary workstation server and refresh/reapply the indicator to load the new code; no user acquisition/session process was stopped by this task.
- The existing `engine/engine.zip` remains an unchanged earlier archive. It is not current runtime source and was not used as authority or silently regenerated.
- The connected Vault is a separately pinned older, scoped snapshot. Its captured source/reference copies were not rebuilt. Current local References, live Source and this explicit user instruction govern this change; local synchronization is not a claim of completed external Vault synchronization.
- Review found and corrected private accepted-ledger error/ordering differences before final acceptance. Arbitrary adversarial private-helper objects were not exhaustively tested. No history clipping, float shortcut, fixture-specific production branch or parallel chronology execution was introduced.
- An existing optional-configuration defect remains: `--blue-lines disabled --a-zones disabled --s-zones disabled --pl-ph disabled` reaches an unconditional `full_s_detectors[direction]` lookup in `finalize_direction_visibility`, although the disabled behavior branch never populates that map. Both snapshots fail with the same directional `KeyError`, call chain, Decimal flags and empty stdout on both symbols/directions. The normal complete-indicator path passes. This defect was not introduced or repaired by the refactor; changing that baseline behavior would be a separate behavioral fix. [Initial finding](variants-initial-failure.log), [exact error/output comparisons](variant-results.json).

## Reproduction and artifacts

Preserved local snapshots are under `apps/chart/state/tmp/engine-refactor-20261117/`: `original`, `removed`, `optimized`, frozen `inputs`, exact outputs and profiles. [Task plan](implementation-plan.md), [stage audit](stage-audit.md), [removal/Bridge audit](contracts-audit.md), [source/input manifest](source-input-manifest.json), [checks](checks-complete.json).

Run the task scripts from the repository root. `run_matrix.py --runs 3` performs serial paired measurements, `summarize_results.py` validates saved exact repeats and computes representative ratios, and `verify_variants.py` checks the bounded request modes. `engine/tests/verification/verify_order_references.py` reconstructs both exact-source references. The task source bundle is generated from final live files; no old package is represented as current.
"""
    (EVIDENCE / "FINAL_REPORT.md").write_text(report, encoding="utf-8", newline="\n")
    print("Wrote FINAL_REPORT.md from completed verification artifacts")


if __name__ == "__main__":
    main()
