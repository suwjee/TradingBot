---
title: Independent carried-Order candidate and evidence-harness review
document_role: evidence
lifecycle: generated
owner: independent-code-review
created_at: 2026-11-02T11:40:52+03:30
last_modified_at: 2026-11-02T12:30:38+03:30
---

# Independent candidate review

## Scope and review cutoff

Read-only code review against `discovery/USER_REQUEST.md`, `07_OPTIMIZATION_PLAN.md`, the actual root `AGENTS.md`, the maintained zero-difference procedure and the requested Superpowers code-review template. The inspected checkout is `X:/My-Projects/TradingBot`, branch `main`, HEAD `afb586b69ecd6e12bcef30e2dbc4163e764dfcdb`. The changes are uncommitted. This reviewer did not execute tests, workloads, profiles, allocation probes or Graphify; did not mutate Source, References, the index, HEAD or branch state; and wrote only this report. Parent fixes described below were reread from the shared checkout.

This is an independent review of the proposed production deltas, their immediate ownership/call/mutation closure and comparison machinery. It does not claim a second complete line-by-line read of every Engine module or both complete Algorithm References. Final after-matrix collection, performance acceptance, final Reference synchronization and final reporting were still in progress at the review cutoff.

## Strengths

- The optimization is confined to creation-history scratch storage in `engine/pipeline/order_audit_engine.py:1423-1432`. Comparing every frozen repaired-before production Python file with its current counterpart found only this module different; its complete diff contains this local transformation and its version/timestamp updates. Reviewed Source SHA-256: `a74cb24f100477fc3fc5cb1197cb0e57d40c400b8cbd7029813e8ac9e064393f`.
- The transformation preserves the relevant native-record evaluation order. Parent tuple fields are all extracted before a multi-parent minimum; the empty/singleton lists already have the required reduced shape; the multi-parent minimum traverses the same list and retains the same first equal winner. Every B confirmation is extracted before metadata access and before the unchanged eligibility predicates. No early rejection, lazy B eligibility, new cache or new index was added.
- Strict lifecycle bounds, inclusive confirmation/cross boundaries, Decimal conversion, canonical Reaction references, ledger iteration, initial-ledger append order, stable residual sort ties and cache-hit list isolation remain in the unchanged remainder of `_carried_orders_for_parent:1433-1468`. The sole production call, `EZoneDetector._zone:391`, still precedes current-parent registration at392. Registration/reparent/relabel/rebuild/restoration and cache invalidation paths remain unchanged.
- The preparatory Bridge repair is separately disclosed. `engine/bridge/trading_pipeline.py:3252` replaces a set with an insertion-ordered key collector; it does not modify key membership, row identity or segment concatenation. Single-regime identity is preserved. The reviewed Bridge hash is `1de8bc3d98686c54a5942956734aca7fbdfe2a85f29d04bd6f072d9efa0c8a10`. Public envelope version fields at3347-3360 do not expose the changed OrderAudit implementation version.
- The new characterization tests use native detector/Reaction objects and literal domain expectations, including both directions, earliest-parent versus later-parent behavior, B-only/shared creation, boundaries, tie order, `is` identity, cache list isolation and eager missing-field failures. The dense provenance allocation case is explicitly artificial and is not represented as market reachability.
- Original failed baseline evidence is retained. Reading completed metric records found44 original executions with42 record-level PASS and2 record-level FAIL, and104 repaired-before record-level PASS. The preparatory comparison reports22 scenarios and zero unexpected typed/content differences, with only the two disclosed aggregate Bridge key-order deltas. These are artifact observations, not executions by this reviewer.

## Issues and dispositions

### Critical

None found in the reviewed production/test delta.

### Important

1. **Parsed JSON alone could not establish exact serialized formatting.** Initial `scripts/matrix.py:106-111` loads and reserializes the payload. For example, `{"x":1e0}` and `{"x":1.0}`, or `{"x":"a"}` and `{"x":"\\u0061"}`, can become the same canonical payload despite different stable wire bytes. Key order and typed content comparison are useful but do not cover this lexical contract. **Disposition:** the parent added `scripts/lexical_output_check.py:8-47`, which preserves the original UTF-8 text and replaces only the complete top-level `timings` value with `null`. I reread the scanner and its tests. The original parsed comparison/baselines remain intact. Actual complete-matrix lexical results are still a required final gate; the scanner's existence is not that result.

2. **Resumed comparisons initially ignored the requested baseline phase.** The initial `scripts/matrix.py:142-157` could reuse an existing repaired-before comparison after a caller requested `--baseline-phase before`, because resume validation omitted the saved `baseline_phase`. The two original order-delta scenarios give a concrete changed-context example. **Disposition:** corrected at current `matrix.py:147-149` by requiring exact baseline-phase equality. I reread the new regression in `scripts/test_harness.py`; the saved `discovery/harness-tests-final.log` records9 tests passing. This reviewer did not rerun them. The actual intended repaired-before candidate context was not shown to be invalid by this finding.

3. **The first supplemental lexical report could label partial scenario coverage PASS.** An initial glob-only loop could see one matching scenario and silently omit all missing scenarios. **Disposition:** current `scripts/lexical_output_check.py:64-91` requires each scenario/repeat from `discovery/collection-policy.json`, validates completed metric/input/command/output context and emits `INCOMPLETE` for a missing repeat. The explicit policy records2 runs for each multi-minute month scenario and5 for practical scenarios, matching the actual collection controllers. This avoids both partial-coverage PASS and the incorrect requirement for5 month runs merely because the general workload recommendation is5. The new missing-repeat test and recorded8-test lexical log were inspected. Complete lexical execution remains pending.

There are no unresolved production correctness findings from this review. The three evidence issues above must remain distinguished from actual candidate calculation differences; none established such a difference.

### Minor

1. **The allocation test initially assumed global tracing was disabled.** Initial `test_carried_order_query.py:94-99` called `tracemalloc.start()` without handling an existing tracer, so a `-X tracemalloc`/`PYTHONTRACEMALLOC` run could consume an earlier process peak and then disable the caller's tracer. **Disposition:** current test lines108-126 run the probe in a separate interpreter and remove only the child's `PYTHONTRACEMALLOC`; the parent tracer is untouched. I reread the updated helper/imports and subprocess invocation. The final focused/full test reruns on this revised test file are pending at cutoff.

## Harness and evidence conclusions

The current matrix compares ordered canonical stable bytes and recursively checks exact Python types, dict key order, list order and values; it removes only root `timings`. Candidate runs require a matching successful baseline/input/arguments/hash-seed context. Resume checks recorded raw/stable artifact hashes and immutable phase Source. Failed comparisons propagate nonzero status. The supplemental lexical check closes the lexical-normalization gap without rewriting baseline artifacts.

`scripts/compare_snapshots.py` compares the complete hook indexes and every captured decompressed graph, requiring both exact graph bytes and recursive typed/ordered content equality, and requires snapshot collection to reproduce normal CLI output. The encoder preserves Decimal text, datetime ISO/fold, ordered containers and intra-snapshot alias topology, including sets and slot-only objects. Set traversal is canonicalized because native sets are unordered; this is not a claim that set iteration order was compared as a public sequence.

Native projections are selective: market candles/seconds/bounds; finalized stage collections and accepted E/S audit/eligible-A state; selected pipeline collections; complete returned range/visibility/primary objects. They do not cover every private detector/cache field or aliases across different hook invocations. Those limits must be stated in the final report. Unchanged production cache code plus direct identity/cache tests support this local optimization, but selective graph capture must not be called universal internal-state verification.

Cold measurements run sequentially in fresh interpreters; profiles/allocation tracing and warm-process probes are separate. Warm measurement stops after calculation plus public encoding and before verification I/O. OS memory is the successfully sampled Windows lifetime-peak counter and can miss an unobserved exit tail; it is not a guaranteed exact-at-exit peak. The inspected completed records had usable nonzero CPU and memory values. No performance improvement is established by this static review or by the scratch-allocation proof alone.

## Declined to judge

- Existing canonical Source/Vault/Reference trading-semantic discrepancies: this request authorizes implementation equivalence, not resolution of trading rules. No semantic repair is approved by this review.
- Independent real-market correctness and sub-5-second event ordering: no new market oracle or finer RAW was executed or inspected by this reviewer.
- Full-engine read-coverage completeness and final Reference reconstruction integrity: parent-owned audit gates were not independently repeated here; final candidate Reference synchronization was not yet complete.
- Arbitrary custom objects injected into the private native ledger: production writers and exercised stubs use dict/tuple/datetime/Decimal-compatible shapes. For example, a custom B cause whose `__getitem__` raises `StopIteration` would encounter different PEP479 wrapping after generator removal. No current writer, accepted input API or test supplies that shape. This review does not claim equivalence for arbitrary user-defined magic-method side effects. Supported malformed native rows retain the inspected extraction/failure ordering; traceback frame/line text is not byte-identical.
- Potential nondeterminism in the unchanged aggregate list-key set at Bridge3246: current same-direction segment producers emit the same list-key schema and the final segment already establishes their insertion slots. No reachable new regression from the authorized one-line Bridge repair was demonstrated. This is not permission to enlarge that repair.

## Exact inspected files

All paths below are relative to the repository; evidence paths are relative to this report's evidence root where indicated.

- Governance/requirements: root `AGENTS.md`; `engineering/docs/README.md`; relevant sections of `engineering/docs/development/zero-difference-refactor.md`; `discovery/USER_REQUEST.md`; `07_OPTIMIZATION_PLAN.md`; `05_BASELINE_VALIDITY_REPORT.md`; `08_CHANGE_LEDGER.md`; the requested `requesting-code-review/SKILL.md` and `code-reviewer.md` template. No nearer Engine/engineering `AGENTS.md` was found by the scoped instruction search.
- Production: complete current/frozen diffs for `engine/pipeline/order_audit_engine.py` and `engine/bridge/trading_pipeline.py`; OrderAudit declarations and sections1390-1530,901-1220,1566-1825; E `_zone` and immediate context351-500; Bridge envelope/merge/regime-publication and relevant serialization sections. Every frozen repaired-before production Python file was hash-compared with current Source. Both accepted Reference diffs were sampled for the preparatory repair; their full bodies were not reread.
- Tests: complete `engine/tests/unit/test_carried_order_query.py` and `test_regime_output_determinism.py`; fixture setup1-115 and lifecycle anchors235-375 in `test_order_audit_lifecycle_contracts.py`; B-only anchor235-275 in `test_order_b_reset_leg.py`; E-ownership anchor375-413 in `test_e_source_ownership.py`.
- Evidence scripts read completely: `scripts/matrix.py`, `instrumented.py`, `compare_snapshots.py`, `collect_after.py`, `collect_repaired_baseline.py`, `compare_preparatory_repair.py`, `diagnose_determinism.py`, `export_baseline_reports.py`, `test_harness.py`, `lexical_output_check.py`, `test_lexical_output.py`. Later lexical/test changes were reread through their final inspected revisions.
- Supporting evidence: `reviews/carried-query-candidate.md` equivalence/mutation/verification sections; `reviews/harness-review.md`; complete `discovery/workloads.json`, `collection-policy.json`, `preparatory-repair-comparison.json`; metric summaries from all completed original/repaired/current-after record files; relevant saved RED/GREEN/harness/lexical logs; an early XAU native collection metadata/comparison sample. This reviewer did not independently decompress/compare every RAW/native/output artifact or rehash market RAW while parent measurements were running.

## Assessment and retention judgment

**Production candidate:** acceptable to continue verification; no supported production regression was found by inspection. The smaller list lifetime and eager B loop are auditable and preserve the native-record calculation contract without new retained state. All discovered evidence/test issues were communicated and their code corrections reread.

**Ready for final retention/completion:** not yet at this review cutoff. Retain O1 only after the complete ordered/typed/native/lexical after gates pass, final focused/full/reference/integrity checks finish and comparable uninstrumented CPU/wall/memory evidence justifies the optimization. A scratch allocation reduction does not override an unexplained whole-run regression or inconclusive performance evidence. The final parent report may supersede this time-bounded gate status by linking completed evidence; it must not present this static review as independently executed runtime validation.

## Follow-up addendum: controlled measurements and retention

The parent requested a further read-only review after collection. No tests, workloads, Source edits or new runtime measurements were performed by this reviewer. The original review and its cutoff remain historical; this addendum records later saved evidence and control code.

### Evidence now observed

- Enumerating completed `after/**/run-*.metrics.json` finds104 cold runs, all PASS, with zero stable-byte differences. The current lexical report contains104 required comparisons, all PASS.
- All22 native-comparison reports are PASS. Their447 stage rows all have exact graph-byte equality, typed/ordered equality and no first difference. The selective-native and cross-hook identity limits stated above remain unchanged.
- The initial auxiliary paired report contains15 PASS pairs, each with matching calculation/input context and no typed, stable-byte or lexical difference. The subsequent controlled report contains another15 PASS pairs. These are separate experiments; they are not30 identically controlled performance pairs.
- Saved final logs record330 Engine unit tests passing, the allocation test passing with parent tracing already enabled,10 harness tests passing, and successful reconstruction of14 Source files per accepted Reference. These are parent-run results read from logs, not independent reruns.

### New controls inspected

I read complete `scripts/controlled_pairs.py` and `paired_benchmark.py`, the changed `matrix.py` run/resume/environment sections and the new cache-context regression in `test_harness.py`. I inspected `discovery/controlled-benchmark.json` as a compact projection of every pair's timings/CPU/RSS/order/seeds/context/Source/input/control fields, read `controlled-effect-summary.json` and `retention-decision.json`, and matched every controlled aggregate timing/CPU/RSS/hash/status/cache-prefix value back to its30 actual saved child metric records. There were no aggregate/record mismatches.

Each controlled side is a fresh process with the same interpreter, `-B`, explicit matched hash seed and explicit empty `PYTHONPYCACHEPREFIX`. The controller checks prefix emptiness before collection and after each pair; the completion record reports it remained empty. The matrix sets the prefix only in child environment and records/checks it during resume. This addresses asymmetric existing Python bytecode-cache reads without modifying global Python settings or Source. Source hashes identify the frozen repaired-before OrderAudit and current candidate, with matching Bridge and other module content. The execution order is AB/BA/AB/BA/AB; this reduces simple order bias but is a small deterministic schedule, not a randomized or noise-free experiment.

The first15 auxiliary pairs do not have this added cache control. Their outputs remain valuable equality evidence; their timings must not be pooled with the controlled15 as though the experimental conditions were identical. The large earlier unpaired month differences likewise remain descriptive observations, not causal estimates of O1 speedup.

### Statistics checked

I independently recomputed the statistics from the15 controlled saved record pairs, without rerunning calculations. Marginal median change is `100 * (median(after) / median(before) - 1)`; median paired change is `median(100 * (after_i / before_i - 1))`. These answer different questions and are not interchangeable.

| Controlled scenario | Marginal wall medians, seconds | Marginal wall change | Median paired wall change | Marginal CPU medians, seconds | Marginal CPU change | Median paired CPU change |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| XAU Oct26,30s,initial Bullish | 9.876267 ->9.824490 | -0.52% | -5.57% | 9.484375 ->9.296875 | -1.98% | -4.62% |
| XAU Oct26,30s,initial Bearish | 6.482395 ->6.003732 | -7.38% | -8.26% | 6.265625 ->5.765625 | -7.98% | -7.63% |
| USOIL Oct22,5s,Bearish,legacy/no-primary | 3.483498 ->3.576881 | +2.68% | -10.33% | 3.328125 ->3.250000 | -2.35% | -10.00% |

There are5 pairs per row. XAU Bearish wall and CPU decrease in all5 pairs and provide the clearest consistent whole-run evidence. XAU Bullish improves in4 of5 CPU/wall pairs, with substantial variation and one unusually slow first baseline. USOIL wall improves in3 of5 pairs and CPU in4 of5; its marginal wall median increases. Retaining the USOIL marginal increase and all ranges is necessary; quoting only its negative paired median as a uniform wall improvement would overstate the result. No confidence interval or significance claim is established by these5-pair samples.

Controlled sampled process peak medians vary by approximately-0.05%, -0.13% and+0.31% respectively; these are sub-percent changes and do not establish meaningful whole-process memory savings. The171032 ->85720-byte scratch result concerns the explicitly artificial dense native row. It must not become a claim of50% lower whole-process RSS or an assertion that such provenance density is market-reachable.

### Retention assessment and remaining gate

No material performance overclaim was found in the inspected `retention-decision.json`: it preserves the USOIL marginal-wall increase, distinguishes paired from marginal statistics, rejects universal speedup and large unpaired-month causal claims, and does not present the scratch result as whole-process memory savings. Given the tiny local patch, absence of new retained state, complete observed equality gates and consistent XAU Bearish CPU improvement, retaining O1 is a reasonable bounded engineering decision. This is not evidence that every workload becomes faster or that a systematic USOIL regression has been statistically excluded.

At this addendum's check, `discovery/final-checks.json` still records a CLI-contract check FAIL. Its retained log shows the verification helper attempting to parse empty stdout as an object (`lexical_output_check.py:20`, `IndexError`), not an identified production calculation mismatch. The parent was notified. That check must be diagnosed and successfully rerun, or completion must remain unverified. Final artifacts09-14 and the final repository-evidence export had not yet been reviewed by this reviewer. The remaining final consistency pass must also confirm that no later Source change invalidates the exact comparison hashes.

## Final report consistency pass

The final pass read complete reports10,11methods,12,13,14 and INDEX, the updated08 ledger, all22 rows of09 by structured status/count checks, and the performance CSV schema plus representative default, all displayed controlled, warm and allocation rows. It also read the corrected complete `scripts/cli_contract_check.py`, successful rerun log, current final-check metadata, final Source-compilation records and relevant final unit/Reference/Order_B logs. No tests or workloads were reexecuted. Read-only Git status/diff/HEAD inspection and Source hashing were performed; this reviewer still modified only this report.

The earlier CLI gate concern is closed. The corrected helper uses omission of the actual optional E-engine argument, handles empty parser-error stdout separately and compares bare-error stderr exactly. All7 comparison cases PASS. The current18-check registry is entirely PASS and explicitly identifies the superseded initial helper failure; original failure metadata/logs/partial outputs remain available. The S-disabled and all-secondary-disabled variants still fail with exit1/error`'bullish'` on both Source copies. Reports12/14 correctly distinguish preservation of that existing failure from operational success, and no behavioral repair was introduced.

The final artifact set is present and internally consistent. Report09 contains22 PASS scenarios and104 runs, with zero ordered-repeat differences and unchanged RAW flags. Reports10/14 match the previously checked104 exact lexical comparisons and447 identical native graph rows. Final logs record330 Engine cases,31 Anti-Drift cases,29 selected Chart/cache cases,10 harness cases,9 lexical-harness cases, successful pretraced allocation, both accepted Reference reconstructions and bounded active anchors. Order_B logs give60 Bullish and107 Bearish causes, avoiding a vacuous zero-cause interpretation. The five final RAW-guard records are retained separately; this reviewer did not rehash the large RAW files.

The displayed performance tables match the saved controlled marginal medians and include the USOIL+2.68% wall increase. The methods document separates uncontrolled, seed-matched, cache-controlled, warm and traced measurements and rejects causal interpretation of large unpaired month changes. The CSV retains the warm XAU Bearish increase (+3.60% wall,+0.61% CPU) and other variable observations; the bounded retention rationale must continue to be read with those limits. Neither the tables nor the completion recommendation establish a universal performance improvement.

All14 final Source-manifest hashes were checked directly against the current live files with zero mismatches. Current HEAD remains `afb586b69ecd6e12bcef30e2dbc4163e764dfcdb`; `git diff --check` succeeds. The saved final Git summary records no staged bytes and the expected uncommitted changes. The finalizer's20 added local INDEX links all have successful existence records. References and the change ledger now represent O1; the original comparison boundary and original two determinism failures are preserved rather than relabeled.

One nonblocking wording refinement was communicated for report10: “full input market” should mean complete input seconds/candles with selected bounds, not every `MarketContext` field. Its explicit selective-state/private-cache qualification already limits that statement. The underlying snapshot scope has not changed.

**Final recommendation:** no unresolved Critical or Important finding remains from this scoped review. Completion is supportable as **ZERO-DIFFERENCE REFACTOR VERIFIED for O1 against the separately established repaired-before baseline**, with the disclosed preparatory key-order delta, finite-data/performance limits and pre-existing semantic/operational issues preserved. This recommendation does not approve publication, assert universal market correctness or claim that the reviewer independently reran the parent's verification.
