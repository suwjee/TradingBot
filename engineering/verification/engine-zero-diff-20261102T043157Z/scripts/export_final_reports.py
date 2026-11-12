"""Build final reports from completed, retained execution evidence only."""
from __future__ import annotations
import csv
from datetime import datetime
import difflib
import gzip
import hashlib
import json
from pathlib import Path
import re
import statistics
import subprocess
from zoneinfo import ZoneInfo
from export_baseline_reports import matrix, write_csv
from matrix import EVIDENCE, ROOT, file_sha, phase_source_guard, save


def load(relative):
    return json.loads((EVIDENCE / relative).read_bytes())


def md(name, title, body):
    path = EVIDENCE / name
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    created = re.search(r"(?m)^created_at: (.+)$", existing)
    stamp = datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds")
    birth = getattr(path.stat(), "st_birthtime", None) if path.exists() else None
    created_stamp = created[1] if created else datetime.fromtimestamp(birth, ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds") if birth else stamp
    path.write_text(f"---\ntitle: {title}\ndocument_role: evidence\nlifecycle: generated\nowner: engine-zero-difference-audit\ncreated_at: {created_stamp}\nlast_modified_at: {stamp}\n---\n\n# {title}\n\n{body.rstrip()}\n", encoding="utf-8", newline="\n")


def stats(records, key):
    values = [record[key] for record in records if record.get(key) is not None]
    return {"median": statistics.median(values), "min": min(values), "max": max(values)} if values else {"median": "", "min": "", "max": ""}


def performance_row(kind, case, before, after, memory_key="peak_working_set_bytes", memory_kind="sampled OS PeakWorkingSet bytes"):
    row = {"measurement_kind": kind, "scenario": case["id"], "input": case["input"], "rows": case["rows"],
           "direction": case["direction"], "timeframe_seconds": case["timeframe"], "before_repetitions": len(before), "after_repetitions": len(after),
           "memory_metric": memory_kind}
    for label, key in [("wall_seconds", "wall_seconds"), ("cpu_seconds", "cpu_seconds"), ("peak_memory_bytes", memory_key)]:
        values = {side: stats(records, key) for side, records in [("before", before), ("after", after)]}
        for side in values:
            for measure, number in values[side].items():
                row[f"{side}_{label}_{measure}"] = number
        b, a = values["before"]["median"], values["after"]["median"]
        row[f"{label}_delta_percent"] = (a / b - 1) * 100 if b != "" and a != "" and b else ""
    return row


def nodes(value):
    return 1 + sum(nodes(item) for item in (value.values() if isinstance(value, dict) else value)) if isinstance(value, (dict, list)) else 1


def main():
    assert load("discovery/after-collection-progress.json")["stage"] == "complete"
    assert load("discovery/paired-benchmark.json")["status"] == "PASS"
    assert load("discovery/controlled-benchmark.json")["status"] == "PASS"
    lexical = load("discovery/lexical-repaired-before-vs-after.json")
    assert lexical["status"] == "PASS"
    checks = load("discovery/final-checks.json")
    assert all(record["status"] == "PASS" for record in checks)
    assert load("discovery/cli-contract-comparison.json")["status"] == "PASS"
    assert all(record["status"] == "PASS" for record in load("discovery/raw-inputs-final.json"))
    assert load("discovery/retention-decision.json")["status"] == "RETAINED"
    source_manifest = phase_source_guard("after", ROOT)
    workloads = load("discovery/workloads.json")
    cases = {case["id"]: case for case in workloads}
    after_matrix = matrix("after")
    assert all(row["status"] == "PASS" for row in after_matrix)
    write_csv("09_AFTER_BASELINE_MATRIX.csv", after_matrix)
    rows = []
    comparison_rows = []
    for case in workloads:
        records = {phase: [json.loads(path.read_bytes()) for path in sorted((EVIDENCE / phase / case["id"]).glob("run-*.metrics.json"))] for phase in ["repaired-before", "after"]}
        rows.append(performance_row("default-randomized-cold-CLI-unpaired", case, records["repaired-before"], records["after"]))
        native = load(f"after/snapshot/{case['id']}/native-comparison.json")
        assert native["status"] == "PASS" and native["stable_difference_count"] == 0
        payload = json.loads(gzip.decompress((EVIDENCE / "repaired-before" / case["id"] / "run-01.stable.json.gz").read_bytes()))
        comparison_rows.append({"case": case["id"], "directions_present": list(payload.get("directions", {})), "typed_payload_nodes": nodes(payload), "native_hook_snapshots": len(native["stages"]), "after_runs": len(records["after"]), "stable_difference_count": 0,
                                "public_stage_keys": {direction: list(group) for direction, group in payload.get("directions", {}).items()}})
    paired = load("discovery/paired-benchmark.json")["pairs"]
    for case_id in dict.fromkeys(pair["case"] for pair in paired):
        pairs = [pair for pair in paired if pair["case"] == case_id]
        rows.append(performance_row("seed-matched-alternating-cold-CLI", cases[case_id], [pair["before"] for pair in pairs], [pair["after"] for pair in pairs]))
    controlled = load("discovery/controlled-benchmark.json")["pairs"]
    for case_id in dict.fromkeys(pair["case"] for pair in controlled):
        pairs = [pair for pair in controlled if pair["case"] == case_id]
        rows.append(performance_row("seed-and-bytecode-cache-controlled-cold-CLI", cases[case_id], [pair["before"] for pair in pairs], [pair["after"] for pair in pairs]))
    for case_id in ["usoil-oct22-5s-bullish-legacy-no-primary", "usoil-oct22-5s-bearish-legacy-no-primary", "xau-oct26-30s-bearish"]:
        measured = {phase: [row for row in load(f"{phase}/warm/{case_id}/warm-metrics.json") if not row["warmup"]] for phase in ["repaired-before", "after"]}
        rows.append(performance_row("warm-inprocess-after-one-warmup", cases[case_id], measured["repaired-before"], measured["after"], memory_kind="NOT MEASURED in warm mode"))
    allocation_case = cases["usoil-oct22-5s-bearish-legacy-no-primary"]
    traced = {phase: load(f"{phase}/alloc/{allocation_case['id']}/metadata.json") for phase in ["repaired-before", "after"]}
    assert all(item["status"] == "PASS" and item["stable_bytes_equal_to_cli"] for item in traced.values())
    rows.append(performance_row("separate-tracemalloc-depth5-no-normal-timing", allocation_case,
                                [traced["repaired-before"]], [traced["after"]], "tracemalloc_peak_bytes", "Python traced peak bytes depth5; normal wall/CPU intentionally blank"))
    focused = load("discovery/carried-allocation-before-after.json")
    rows.append(performance_row("artificial-native-query-depth1-no-market-reachability-claim",
                                {"id": "dense-native-creation-query", "input": str(ROOT / "engine/tests/unit/test_carried_order_query.py"), "rows": "10000parent+10000B causes", "direction": "bullish", "timeframe": "NOT APPLICABLE"},
                                [{"tracemalloc_peak_bytes": focused["before_peak_bytes"]}], [{"tracemalloc_peak_bytes": focused["after_peak_bytes"]}], "tracemalloc_peak_bytes", "Python traced temporary query peak bytes depth1"))
    write_csv("11_PERFORMANCE_AND_MEMORY_RESULTS.csv", rows)
    save(EVIDENCE / "discovery/final-comparison-summary.json", {"status": "PASS", "cases": comparison_rows, "after_runs": sum(row["runs"] for row in after_matrix), "stable_difference_count": 0, "typed_payload_nodes_per_first_run_total": sum(row["typed_payload_nodes"] for row in comparison_rows), "native_hook_snapshots_total": sum(row["native_hook_snapshots"] for row in comparison_rows)})
    table = "| Scenario | BEFORE wall s | AFTER wall s | Wall delta | BEFORE/AFTER CPU s (delta) | BEFORE/AFTER peak MiB (delta) | Repetitions each |\n| --- | ---: | ---: | ---: | ---: | ---: | ---: |\n"
    for row in rows:
        if row["measurement_kind"] == "seed-and-bytecode-cache-controlled-cold-CLI":
            table += f"| {row['scenario']} | {row['before_wall_seconds_median']:.6f} | {row['after_wall_seconds_median']:.6f} | {row['wall_seconds_delta_percent']:+.2f}% | {row['before_cpu_seconds_median']:.6f} / {row['after_cpu_seconds_median']:.6f} ({row['cpu_seconds_delta_percent']:+.2f}%) | {row['before_peak_memory_bytes_median']/1048576:.3f} / {row['after_peak_memory_bytes_median']/1048576:.3f} ({row['peak_memory_bytes_delta_percent']:+.2f}%) | 5 |\n"
    md("05_BASELINE_VALIDITY_REPORT.md", "Baseline validity", """The original immutable BEFORE remains **FAIL for exact repeat determinism**:22scenarios/44actual cold runs, all exit0,20scenarioPASS and2scenarioFAIL. Only aggregate bridgeOutput mapping-key order differed in USOIL month Bearish and XAU September28 Bullish; independent full typed traversal found0other calculation differences. Original stdout/stderr/hashes/Source are preserved, never rewritten or normalized to manufacture PASS.

After the separately proposed repair, the user delegated the decision while requiring identical calculation outputs. The named repaired-before baseline is **PASS**:22scenarios/104cold runs, five practical repetitions and two multi-minute untrimmed month repetitions. Its complete collection ended before any optimization Source edit; see discovery/repaired-collection-progress.json and immutable14Source bytes under discovery/repaired-source-before. Full native snapshots for all22scenarios, separate fresh profiles and warm probes were collected before O1. Original-versus-repaired comparison PASS22 with0unexpected typed/value/string/array differences; only the disclosed aggregate mapping-order repair delta is allowed in that separate comparison.

04_BEFORE_BASELINE_MATRIX.csv preserves original statuses, while04_REPAIRED_BEFORE_BASELINE_MATRIX.csv records the optimization baseline. collection-policy.json formalizes the controllers' explicit actual repetition counts; workloads.repeats=5 was a general recommendation, not a false claim of five completed month runs. No historical RAW size cap is applied. All five discovered real5s RAW inputs are complete, including309266month rows; synthetic1200and5/30/60s, independent directions, primary/legacy, StopAll/projection and narrow presentation cases are recorded with every CLI argument and immutable input hash.

Only root timings is excluded as documented nonstable telemetry. Complete stdout/stderr remains retained; final additional lexical checking preserves all other original JSON bytes. Normal cold wall/CPU/OS-peak measurements are separate from instrumentation, with methods and native50ms memory-sampling precision limits in11_PERFORMANCE_METHODS.md. No1s data was available, historical registry inputs were unavailable, and broad independent real-market correctness is not implied by baseline validity. Source and RAW hashes support integrity, not semantic authority.
""")
    allocation = load("discovery/carried-allocation-before-after.json")
    md("08_CHANGE_LEDGER.md", "Change ledger", f"""## R1: Separately delegated deterministic Bridge key order

Owner: engine/bridge/trading_pipeline.py, merge_regime_outputs. Replace set key collection with dict.fromkeys in first-appearance order; existing public pipeline version1.13.0 unchanged, implementation1.16.0 ->1.16.1. This is a disclosed preparatory serialization-order correction, not a performance claim. Original44runs/2repeatFAIL remain intact. Original versus repaired22case comparison:0unexpected typed/value/Decimal/string/array differences. Repaired-before104cold runs and all22native collections completed before O1. RED4determinism failures/3preservation passes; GREEN full303tests. Both exact-source References synchronized and verified. Temporary key collection stays O(K); no persistent cache/state. Final status: RETAINED under the user's delegated proposal choice.

## O1: Carried-Order scratch allocation

Owner: engine/pipeline/order_audit_engine.py, _carried_orders_for_parent. Internal version1.8.1 ->1.8.2, actual Source timestamp2026-11-02T11:23:50+03:30. Reuse eagerly extracted parent list, call min only for multiple parents, release that scratch history before eagerly appending all B confirmations. Native minimum/tie identity, strict lifecycle bounds, inclusive confirmation/stop, error precedence, ledger iteration/stable sort order, cache keys/invalidation and returned tuple/Decimal fields remain unchanged. No trading rule, public envelope metadata or input filter changes. No new retained cache/index; broad scan/sort asymptotics unchanged, temporary reference lifetime changes from roughly p+1+b to max(p,1+b) on the measured CPython path.

Characterization tests pin both directions, earliest-parent/all-B semantics, strict/equal boundaries, literal Decimal text, shared Order identity, insertion ties, cache freshness and partial/malformed native rows. The artificial dense-provenance allocation test RED1fail/26pass (baseline peak171032B), GREEN full330PASS. Isolated child probing also works with a pre-existing parent tracemalloc session. Measured focused scratch peak {allocation['before_peak_bytes']} -> {allocation['after_peak_bytes']}B ({(allocation['after_peak_bytes']/allocation['before_peak_bytes']-1)*100:+.2f}%). This artificial row is not asserted market-reachable; full process RSS does not halve.

Full final22scenario104cold matrix, ordered/typed comparison, raw lexical comparison and all native hook snapshots:0differences versus repaired-before. Current tests/anchors/reference/Anti-Drift PASS; real timings and actual memory variability are in11_PERFORMANCE_AND_MEMORY_RESULTS.csv, with matched controls/methods in11_PERFORMANCE_METHODS.md. Final status: RETAINED; exact rationale in discovery/retention-decision.json. Independent review found no supported production regression; all identified harness/test gaps were fixed and reread.

{table}
## Scope and discarded proposals

Exact patches from original Source are under source-diffs/. Only the two owning production modules, both required exact-source References and two new tests changed. No pre-existing user change, original RAW, expected result, historical artifact, global environment, dependency manifest, Git index/HEAD or remote was altered. Live checkout is explicitly user-selected. No worktree/commit/publication/Graphify action was inferred from skill defaults.

Naive metadata-first eligibility was rejected because it hides malformed eager extraction errors. New mutable creation/liveness indexes, shared E tables across regimes and Blue containment indexing were deferred pending stronger lifetime/chronology/identity/invalidation proofs. No unmeasured candidate is retained merely for fewer lines. Public versions and canonical Vault trading semantics remain unchanged; pre-existing Source/Reference/Vault semantic conflicts remain separate.
""")
    md("11_PERFORMANCE_METHODS.md", "Performance methods and limits", f"""The optimization baseline is immutable repaired-before, not the original nondeterministic serialization. All normal process measurements include startup/import/input loading/full calculation/encoding/stdout I/O; controller hashing and equality checks are outside the timed region. Process CPU comes from Windows100ns native counters. OS PeakWorkingSet is sampled every50ms; the final sampling gap may miss a last-moment peak. Every input file is consumed completely. No profiler or other deliberate audit workload runs concurrently with measurements.

{table}
The CSV contains all22 default-randomized cold scenarios,3 initial matched-seed paired scenarios,3 additional seed-and-bytecode-cache-controlled scenarios and3 warm cases, plus separate allocation observations. The displayed table uses the final cache-controlled pairs. Negative delta is a reduction. Median/min/max and actual repetition counts are retained. Cold means a fresh Python process, not a flushed OS file cache: controller pre-run hashing reads the complete input and Source before the clock, warming file pages equally. Native CPU counters are queried in100ns units but observed scheduling granularity matters on short cases. The default cold phases were collected at different times and show substantial device/power/background variability; large apparent month speedups are **not causal estimates**. The paired auxiliary sequences use seeds0..4 shared by each before/after pair and execution orderAB/BA/AB/BA/AB. The additional control applies the same empty PYTHONPYCACHEPREFIX only to each child, with -B preventing writes; the directory remains empty. This prevents asymmetric reading of existing bytecode in live versus frozen Source paths. No global setting or existing cache was changed. These controls are explicitly recorded and never replace or secretly pin the default-randomized determinism matrix. Source-root path normalization applies only to module paths for frozen-source comparison, not market parameters.

Warm mode loads engines/market once, discards one warmup, measures five fresh full pipeline/result constructions, and stops clocks before writing/comparing outputs. It does not measure OS peak memory and does not establish persistent cache safety. Profiles and tracemalloc are separate instrumented runs, never normal wall/CPU benchmarks. Their raw records are preserved under repaired-before/profile, after/profile, repaired-before/alloc and after/alloc.

The artificial dense-provenance native query probe demonstrates lower temporary Python allocation at the supported interpreter; it does not prove that10k simultaneous parent/B causes occur in markets or that full process RSS halves. See discovery/carried-allocation-before-after.json. The scratch asymptotic bound remains O(p+b); the reduction concerns simultaneous reference collections and generator work. No retained cache/index/state is added. No whole-market correctness or universal speedup claim follows from these finite datasets.
""")
    native_count = sum(row["native_hook_snapshots"] for row in comparison_rows)
    md("10_ZERO_DIFFERENCE_COMPARISON.md", "Exact comparison result", f"""**PASS:0 stable differences** for the optimization versus the immutable post-repair baseline:22 scenarios, {sum(row['runs'] for row in after_matrix)} actual cold AFTER runs, {len(lexical['comparisons'])} exact serialized-byte comparisons and {native_count} native hook snapshots.

Every recursive ordered/typed comparison traverses actual retained content; a final digest is supporting integrity evidence only. Complete actual stdout/stderr and compressed stable payloads remain in before/, repaired-before/ and after/. The only excluded output telemetry is the root timings value. The additional lexical scanner replaces only that value with null in original stdout bytes, preserving every other byte: numeric spelling, string escapes, whitespace/newline, field presence, object-key order and array order. Missing required cases/repeats, invalid input/command/baseline context or tampered outputs cannot PASS that gate. See discovery/lexical-repaired-before-vs-after.json and collection-policy.json.

Native graph comparison captures Decimal/datetime and container types, ordered fields/collections and shared object aliases. Hooks include complete input seconds/candles and selected market bounds, full-direction E/Blue/A/S and invalid/internal evidence, accepted and S OrderAudit, eligible A, prepared pipeline state, direction-range/visibility and primary results when reached. Every reached hook index/name and decompressed graph byte matches; dynamic stage/key inventories are recorded in discovery/final-comparison-summary.json. Sets are compared as typed canonical membership, preserving aliases. This is selective authoritative semantic state, not every private derived cache. Cache/native identity/fresh-list and malformed-row behavior are additionally pinned by focused tests and owner proof.

**Original versus final boundary:** the original22scenario/44run exact determinism gate remains FAIL in2 repeat cases, solely aggregate multi-regime bridgeOutput mapping-key order. The user delegated a separately shown dict.fromkeys preparatory repair. discovery/preparatory-repair-comparison.json reports22PASS and0 unexpected calculation/type/value/Decimal/array differences. Transitivity with the exact post-repair comparison preserves that content in the final output; original raw serialization bytes are not claimed identical where the disclosed key order changed. Neither baseline nor expectations were rewritten to accept an optimization difference.

Strict/equal boundaries, both directions, parent/B earliest/all selection, native Order identity, residual sort insertion ties, Decimal string precision, partial/malformed native rows and cache freshness are exercised by current tests. CLI supplemental switch/error cases compare exact public stdout/exit code; stderr progress is retained. Arbitrary injected custom magic methods and byte-identical traceback-frame text are outside the native ledger/input contract and are not claimed equivalent. See reviews/independent-candidate-review.md.
""")
    tests_table = "| Check | Status | Command / evidence |\n| --- | --- | --- |\n" + "".join(f"| {row['name']} | {row['status']} | `{' '.join(row['command'])}`; `{Path(row['log']).name}` |\n" for row in checks)
    md("12_REGRESSION_VERIFICATION.md", "Regression verification", tests_table + """
All commands above actually completed on final Source; full outputs are in discovery/final-*.log and structured invocations in discovery/final-checks.json. Final-source compilation and five RAW hash guards are separate JSON records. All22 normal full-history scenarios, repeated determinism, all reached native stages, exact lexical stdout, switch/error-response preservation and auxiliary paired/warm output comparisons are PASS. Current totals:330Engine unit cases,31Anti-Drift unit cases,29focused Chart/cache cases,10comparison-harness cases and9lexical-harness cases; the allocation case also passes under pre-existing tracemalloc.

The initial CLI helper run failed because the audit helper incorrectly supplied nonexistent --e-zones and assumed every failure emits JSON. This was a verification-tool defect, not a before/after Source difference. The corrected helper uses the actual optional E-engine argument, handles empty parser-error stdout explicitly, compares bare-error stderr exactly and passes all7cases. Initial FAIL/log/partial outputs remain in discovery/final-checks-initial.json, final-cli-contract.log and cli-contract/; successful rerun uses cli-contract-v2/ and final-cli-contract-rerun.log. Only changed/failed comparison checks were rerun; successful Engine/RAW/reference checks were retained with their actual timestamps.

Separate pre-existing operational failure: --s-zones disabled (also the all-secondary-disabled variant) returns exit1 with public error 'bullish' in BOTH frozen baseline and final Source. The CLI equivalence check PASS preserves that failure; it does not call the option operationally correct. No output-changing repair is included in this refactor.

Existing RAW helpers are used without editing expectations. XAUUSD September28 and USOIL month primary anchors plus formed-MBL assertions are run on both original saved output and final output. Order_B RAW helper is bounded to both5s legacy scenarios after actual all-row5s alignment preflight:60Bullish and107Bearish reset-leg causes validate on BOTH original and final outputs, so the bounded assertions are non-vacuous. Its coarse30s exact First-time restriction and the primary helper's superseded global one-cycle/three-high/one-reversal assertions are NOT APPLICABLE as general current aggregate validators, with exact Source/Reference evidence in reviews/regression-applicability.md. No output was clipped or repaired to satisfy them.

NOT RUN: unavailable1s RAW/sub-5s chronology; unavailable historical registry files; independent broad real-market correctness beyond bounded approved anchors; browser/manual visualization and live external FARAZ acquisition; security scanner/Graphify/release/publication. They are not implied by unit counts, mirror parity, completed calculation or structural reconstruction. No UI, server transport, acquisition code or dependency manifest changed.
""")
    diff_directory = EVIDENCE / "source-diffs"
    diff_directory.mkdir(exist_ok=True)
    diffs = []
    for relative in source_manifest:
        original = EVIDENCE / "discovery/source-before" / relative
        current = ROOT / relative
        if original.read_bytes() != current.read_bytes():
            patch = "".join(difflib.unified_diff(original.read_text(encoding="utf-8").splitlines(keepends=True), current.read_text(encoding="utf-8").splitlines(keepends=True), fromfile="original/"+relative, tofile="final/"+relative))
            target = diff_directory / (Path(relative).stem + "-final.patch")
            target.write_text(patch, encoding="utf-8", newline="\n")
            diffs.append(relative)
    save(EVIDENCE / "discovery/source-manifest-final.json", source_manifest)
    md("13_REFERENCE_AND_VERSION_SYNC.md", "Reference and version synchronization", f"""Both accepted local Bullish/Bearish V5.4.33 Source_Synchronized documents retain their accepted identities and existing created_at/history. Exact current changed Source bodies, SHA-256, byte/LF counts, Source manifest/version rows and AST symbol indexes are regenerated; a truthful unreleased implementation audit note distinguishes the preparatory repair and optimization. Existing trading teaching text and pre-existing semantic discrepancies are preserved.

Source modules changed: {', '.join(f'`{path}`' for path in diffs)}. Bridge public API1.13.0 remains unchanged; its existing implementation1.16.0 ->1.16.1. OrderAudit internal Source version1.8.1 ->1.8.2; no public serialized version field changes. Exact final hashes are in discovery/source-manifest-final.json, source patches in source-diffs/. No unrelated module metadata changes.

The maintained verify_order_references.py verifier recovered every dynamically discovered production file from **both** References, verified exact bytes/hash/LF and compiled recovered modules: PASS; full log discovery/final-references.log. Anti-Drift unit/full and final Engine tests were rerun after synchronization: PASS. This establishes exact local reconstruction, not trading-semantic consistency. Canonical Vault/Plugin intended semantics and exclusions are unchanged; no clean-source Vault capture/synchronization or new primary material was requested/performed. The older Vault executable pins remain explicitly stale relative to current local Source.
""")
    md("14_FINAL_ENGINE_OPTIMIZATION_REPORT.md", "Final Engine optimization report", f"""**ZERO-DIFFERENCE REFACTOR VERIFIED**, scoped to the retained optimization versus the separately established stable post-repair baseline. Original calculation content remains exact; the separately delegated preparatory mapping-key-order correction is disclosed and is not claimed byte-identical to original nondeterministic serialization.

Live project: X:/My-Projects/TradingBot; main at afb586b69ecd6e12bcef30e2dbc4163e764dfcdb. Initial Git tree was clean. Task changes remain uncommitted/unstaged: two production modules, two accepted References, two new focused unit files and this unique evidence directory. No pre-existing user file was discarded, no RAW changed, no Git publication/Graphify/dependency upgrade occurred. Full14production-file read coverage and exact paths are in01_ENGINE_FILE_INVENTORY.csv, discovery/full-read-coverage.json and per-owner review/read ledgers. New/current byte metadata is in discovery/source-manifest-final.json.

The retained local optimization reuses the parent-created scratch list in OrderAudit._carried_orders_for_parent, releases multi-parent history before building B creations and appends B confirmations eagerly. It preserves minimum-parent selection, eager extraction/error precedence, strict/inclusive time predicates, native physical Order identity, cache validity and stable insertion/sort ties. No index/cache or trading decision changes. Measured other hotspots—post-stop accepted Orders, repeated E detector/reconciliation and Blue internal geometry—remain unchanged because stronger lifetime/invalidation/semantic proofs would be needed.

{table}
All22 default cold scenarios and their actual medians/ranges/counts plus3warm cases are in11_PERFORMANCE_AND_MEMORY_RESULTS.csv. Device variability is material: do not attribute the large unpaired month timing movement to this patch. Matched auxiliary pairs and the focused allocation result support the explicit retention rationale in discovery/retention-decision.json;11_PERFORMANCE_METHODS.md gives exact boundaries.

Verification:0 ordered/typed stable differences across {sum(row['runs'] for row in after_matrix)} AFTER cold runs,0 lexical differences outside root timing values,0 differences across {native_count} reached native hook snapshots. Full current Engine330tests, focused pretraced allocation, comparison harness, supported CLI switch/error cases, bounded active RAW anchors and Order_B, Reference reconstruction and Anti-Drift are recorded in12_REGRESSION_VERIFICATION.md and actual logs. Both directional References are synchronized. These are equivalence and bounded anchor results, not universal market correctness.

Unresolved pre-existing issues remain separate: REF-REACTION-SUCCESSOR narrative ambiguity, stale100-versus400 Reference example, older Vault pins and scoped stale RAW-helper assumptions. The supported S-disabled switch also already returns exit1/error'bullish' on both baseline and final; it is recorded without an output-changing fix. No optimization depends on selecting a new semantic interpretation; these discrepancies still limit independent behavior-level assertions. Unavailable1s/historical datasets, browser/runtime visualization and global market correctness are NOT RUN. No package/archive is required by the applicable current protocol; no release/publication was attempted.

Reproduce on the same Python3.15/orjson3.13.0/tzdata2026.5 environment using commands saved per run. To create new measurements, use a **new phase name**, preserve immutable baselines and pass --baseline-phase repaired-before to scripts/matrix.py; normal entry points and input paths are retained in metrics. Use compare_snapshots.py repaired-before <new-phase> <case> for new native graph collections. For existing evidence, run lexical_output_check.py, current tests, reference verifier and final raw/source guards. Never overwrite old stdout or silently reuse evidence after a Source/input/command/baseline/seed/cache-control change. paired_benchmark.py and controlled_pairs.py use frozen postrepair Source explicitly; recorded seeds/order/cache roots are auxiliary controls. Their fixed phase names resume existing immutable measurements; use unique names in a new run to gather new samples.

Numbered artifacts00-14, complete original/repaired/after stdout/stderr, profiles/allocation/native graphs, exact patches, Source backups, workload/hash/environment manifests and independent reviews are retained here. No original FAIL is relabeled PASS. See10_ZERO_DIFFERENCE_COMPARISON.md for the exact preparatory/optimization comparison boundary.
""")
    print(json.dumps({"status": "PASS", "after_runs": sum(row["runs"] for row in after_matrix), "native_snapshots": native_count, "performance_rows": len(rows)}))


if __name__ == "__main__":
    main()
