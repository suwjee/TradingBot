---
title: Final Engine optimization report
document_role: evidence
lifecycle: generated
owner: engine-zero-difference-audit
created_at: 2026-11-02T12:27:57+03:30
last_modified_at: 2026-11-02T12:31:27+03:30
---

# Final Engine optimization report

**ZERO-DIFFERENCE REFACTOR VERIFIED**, scoped to the retained optimization versus the separately established stable post-repair baseline. Original calculation content remains exact; the separately delegated preparatory mapping-key-order correction is disclosed and is not claimed byte-identical to original nondeterministic serialization.

Live project: X:/My-Projects/TradingBot; main at afb586b69ecd6e12bcef30e2dbc4163e764dfcdb. Initial Git tree was clean. Task changes remain uncommitted/unstaged: two production modules, two accepted References, two new focused unit files and this unique evidence directory. No pre-existing user file was discarded, no RAW changed, no Git publication/Graphify/dependency upgrade occurred. Full14production-file read coverage and exact paths are in01_ENGINE_FILE_INVENTORY.csv, discovery/full-read-coverage.json and per-owner review/read ledgers. New/current byte metadata is in discovery/source-manifest-final.json.

The retained local optimization reuses the parent-created scratch list in OrderAudit._carried_orders_for_parent, releases multi-parent history before building B creations and appends B confirmations eagerly. It preserves minimum-parent selection, eager extraction/error precedence, strict/inclusive time predicates, native physical Order identity, cache validity and stable insertion/sort ties. No index/cache or trading decision changes. Measured other hotspots—post-stop accepted Orders, repeated E detector/reconciliation and Blue internal geometry—remain unchanged because stronger lifetime/invalidation/semantic proofs would be needed.

| Scenario | BEFORE wall s | AFTER wall s | Wall delta | BEFORE/AFTER CPU s (delta) | BEFORE/AFTER peak MiB (delta) | Repetitions each |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| xau-oct26-30s-bullish | 9.876267 | 9.824490 | -0.52% | 9.484375 / 9.296875 (-1.98%) | 174.238 / 174.156 (-0.05%) | 5 |
| xau-oct26-30s-bearish | 6.482395 | 6.003732 | -7.38% | 6.265625 / 5.765625 (-7.98%) | 152.152 / 151.961 (-0.13%) | 5 |
| usoil-oct22-5s-bearish-legacy-no-primary | 3.483498 | 3.576881 | +2.68% | 3.328125 / 3.250000 (-2.35%) | 70.266 / 70.484 (+0.31%) | 5 |

All22 default cold scenarios and their actual medians/ranges/counts plus3warm cases are in11_PERFORMANCE_AND_MEMORY_RESULTS.csv. Device variability is material: do not attribute the large unpaired month timing movement to this patch. Matched auxiliary pairs and the focused allocation result support the explicit retention rationale in discovery/retention-decision.json;11_PERFORMANCE_METHODS.md gives exact boundaries.

Verification:0 ordered/typed stable differences across 104 AFTER cold runs,0 lexical differences outside root timing values,0 differences across 447 reached native hook snapshots. Full current Engine330tests, focused pretraced allocation, comparison harness, supported CLI switch/error cases, bounded active RAW anchors and Order_B, Reference reconstruction and Anti-Drift are recorded in12_REGRESSION_VERIFICATION.md and actual logs. Both directional References are synchronized. These are equivalence and bounded anchor results, not universal market correctness.

Unresolved pre-existing issues remain separate: REF-REACTION-SUCCESSOR narrative ambiguity, stale100-versus400 Reference example, older Vault pins and scoped stale RAW-helper assumptions. The supported S-disabled switch also already returns exit1/error'bullish' on both baseline and final; it is recorded without an output-changing fix. No optimization depends on selecting a new semantic interpretation; these discrepancies still limit independent behavior-level assertions. Unavailable1s/historical datasets, browser/runtime visualization and global market correctness are NOT RUN. No package/archive is required by the applicable current protocol; no release/publication was attempted.

Reproduce on the same Python3.15/orjson3.13.0/tzdata2026.5 environment using commands saved per run. To create new measurements, use a **new phase name**, preserve immutable baselines and pass --baseline-phase repaired-before to scripts/matrix.py; normal entry points and input paths are retained in metrics. Use compare_snapshots.py repaired-before <new-phase> <case> for new native graph collections. For existing evidence, run lexical_output_check.py, current tests, reference verifier and final raw/source guards. Never overwrite old stdout or silently reuse evidence after a Source/input/command/baseline/seed/cache-control change. paired_benchmark.py and controlled_pairs.py use frozen postrepair Source explicitly; recorded seeds/order/cache roots are auxiliary controls. Their fixed phase names resume existing immutable measurements; use unique names in a new run to gather new samples.

Numbered artifacts00-14, complete original/repaired/after stdout/stderr, profiles/allocation/native graphs, exact patches, Source backups, workload/hash/environment manifests and independent reviews are retained here. No original FAIL is relabeled PASS. See10_ZERO_DIFFERENCE_COMPARISON.md for the exact preparatory/optimization comparison boundary.
