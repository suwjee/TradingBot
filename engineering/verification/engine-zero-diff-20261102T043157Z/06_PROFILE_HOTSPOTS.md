---
title: Engine CPU and allocation hotspots
document_role: evidence
lifecycle: generated
owner: engine-zero-difference-audit
created_at: 2026-11-02T10:51:48+03:30
last_modified_at: 2026-11-02T12:10:16+03:30
---

# Engine CPU and allocation hotspots



These are separate cProfile/tracemalloc runs of the complete supported Bridge pipeline. Instrumented wall/CPU figures are not normal benchmark results and are never used as a before/after speedup. The initial Bridge module import precedes cProfile enablement; engine loading/main processing are instrumented. Normal cold CLI measurements independently include startup/import and output I/O.

Original profiles were captured against the unchanged initial production manifest before the separately authorized key-order repair. Three normal-output comparisons PASS; XAU historical Bullish profile completes normally but retains the known aggregate-key-order comparison FAIL. That failure is not normalized to PASS. Fresh post-repair profiling remains a separate gate before implementation.

## usoil-oct22-5s-bearish-legacy-no-primary

Engine exit: 0; stable CLI comparison: PASS; instrumented wall 15.106750s, CPU 13.937500s. Raw cpu.prof, stats.json and top-cumulative.txt are retained in `before/profile/usoil-oct22-5s-bearish-legacy-no-primary/`.

| Owner / function | Original line | Calls | Self seconds | Cumulative seconds | Fraction of main cumulative |
| --- | ---: | ---: | ---: | ---: | ---: |
| e_zone_detector.py:_zone | 378 | 8682 | 0.270786 | 8.623955 | 57.12% |
| order_audit_engine.py:_carried_orders_for_parent | 1410 | 8682 | 2.470452 | 4.415682 | 29.25% |
| order_audit_engine.py:_post_stop_accepted_orders_for_parent | 1471 | 8682 | 0.747852 | 2.209818 | 14.64% |
| order_audit_engine.py:_register_order_audit | 1136 | 12103 | 0.196255 | 1.271517 | 8.42% |
| blue_line_detector.py:geometry_is_internal | 458 | 548 | 0.426219 | 0.721888 | 4.78% |
| e_zone_detector.py:__init__ | 71 | 12 | 0.142880 | 0.677543 | 4.49% |
| s_zone_detector.py:__init__ | 67 | 1 | 0.001582 | 0.029520 | 0.20% |
| reaction_engine.py:__init__ | 819 | 1 | 0.011943 | 0.021903 | 0.15% |
| a_zone_detector.py:__init__ | 68 | 1 | 0.000819 | 0.010446 | 0.07% |
| reaction_engine.py:__init__ | 993 | 1 | 0.001581 | 0.002732 | 0.02% |

## xau-oct26-30s-bearish

Engine exit: 0; stable CLI comparison: PASS; instrumented wall 36.525179s, CPU 34.593750s. Raw cpu.prof, stats.json and top-cumulative.txt are retained in `before/profile/xau-oct26-30s-bearish/`.

| Owner / function | Original line | Calls | Self seconds | Cumulative seconds | Fraction of main cumulative |
| --- | ---: | ---: | ---: | ---: | ---: |
| e_zone_detector.py:_zone | 378 | 19081 | 0.659048 | 21.037073 | 57.62% |
| order_audit_engine.py:_carried_orders_for_parent | 1410 | 19081 | 6.466691 | 11.273165 | 30.87% |
| order_audit_engine.py:_post_stop_accepted_orders_for_parent | 1471 | 19081 | 1.680456 | 4.568176 | 12.51% |
| order_audit_engine.py:_register_order_audit | 1136 | 25189 | 0.413499 | 3.396574 | 9.30% |
| e_zone_detector.py:__init__ | 71 | 24 | 0.304436 | 1.624053 | 4.45% |
| blue_line_detector.py:geometry_is_internal | 458 | 1002 | 0.819994 | 1.618278 | 4.43% |
| reaction_engine.py:__init__ | 819 | 1 | 0.130952 | 0.222980 | 0.61% |
| s_zone_detector.py:__init__ | 67 | 2 | 0.006652 | 0.112254 | 0.31% |
| a_zone_detector.py:__init__ | 68 | 2 | 0.002842 | 0.037644 | 0.10% |
| reaction_engine.py:__init__ | 105 | 284 | 0.001283 | 0.008142 | 0.02% |

## xau-oct26-30s-bullish

Engine exit: 0; stable CLI comparison: PASS; instrumented wall 61.780460s, CPU 58.390625s. Raw cpu.prof, stats.json and top-cumulative.txt are retained in `before/profile/xau-oct26-30s-bullish/`.

| Owner / function | Original line | Calls | Self seconds | Cumulative seconds | Fraction of main cumulative |
| --- | ---: | ---: | ---: | ---: | ---: |
| e_zone_detector.py:_zone | 378 | 27911 | 1.043773 | 31.734592 | 51.39% |
| order_audit_engine.py:_carried_orders_for_parent | 1410 | 27911 | 8.523152 | 14.924125 | 24.17% |
| order_audit_engine.py:_post_stop_accepted_orders_for_parent | 1471 | 27911 | 2.768516 | 7.558272 | 12.24% |
| order_audit_engine.py:_register_order_audit | 1136 | 39813 | 0.714388 | 6.751399 | 10.93% |
| blue_line_detector.py:geometry_is_internal | 458 | 2004 | 1.729125 | 3.721560 | 6.03% |
| e_zone_detector.py:__init__ | 71 | 69 | 0.685769 | 3.524972 | 5.71% |
| reaction_engine.py:__init__ | 819 | 3 | 0.236497 | 0.405701 | 0.66% |
| reaction_engine.py:__init__ | 993 | 3 | 0.016239 | 0.295279 | 0.48% |
| s_zone_detector.py:__init__ | 67 | 6 | 0.012845 | 0.214384 | 0.35% |
| PL_PH_detector.py:__init__ | 603 | 2 | 0.028956 | 0.178372 | 0.29% |

## xau-sep28-30s-bullish

Engine exit: 0; stable CLI comparison: FAIL; instrumented wall 67.765188s, CPU 64.281250s. Raw cpu.prof, stats.json and top-cumulative.txt are retained in `before/profile/xau-sep28-30s-bullish/`.

| Owner / function | Original line | Calls | Self seconds | Cumulative seconds | Fraction of main cumulative |
| --- | ---: | ---: | ---: | ---: | ---: |
| e_zone_detector.py:_zone | 378 | 28959 | 0.964213 | 33.964280 | 50.13% |
| order_audit_engine.py:_carried_orders_for_parent | 1410 | 28959 | 7.810092 | 13.718344 | 20.25% |
| order_audit_engine.py:_post_stop_accepted_orders_for_parent | 1471 | 28959 | 3.825686 | 10.605378 | 15.65% |
| order_audit_engine.py:_register_order_audit | 1136 | 46889 | 0.631223 | 7.027323 | 10.37% |
| e_zone_detector.py:__init__ | 71 | 105 | 0.738597 | 3.811246 | 5.63% |
| blue_line_detector.py:geometry_is_internal | 458 | 2924 | 2.013726 | 3.630599 | 5.36% |
| reaction_engine.py:__init__ | 819 | 5 | 0.293966 | 0.527605 | 0.78% |
| reaction_engine.py:__init__ | 993 | 5 | 0.029992 | 0.423516 | 0.63% |
| PL_PH_detector.py:__init__ | 603 | 3 | 0.037954 | 0.288267 | 0.43% |
| s_zone_detector.py:__init__ | 67 | 10 | 0.017141 | 0.284989 | 0.42% |

## Allocation probe

USOIL October22,15,061 RAW rows,5s Bearish, legacy/primary disabled: engine exit0, stable comparisonPASS. Python traced current 15,792,547B, peak 40,726,876B at trace depth5. Instrumented wall 60.216s is tracing overhead evidence, not a normal runtime. Raw allocations.json retains eighty line/size/count records. Python allocations exclude much native/runtime memory; OS process WorkingSet is a separate metric.

## Ranked interpretation and protections

1. **Carried accepted Orders, OrderAudit original1410-1468:** each miss scans mutable ledger rows and eagerly allocates parent creation history, a second creation list and B generator before unchanged strict lifecycle/confirmation/stop predicates. The XAU October26 Bullish profile records27,911calls and14.924 cumulative seconds; the B extraction generator resumes4,638,677times. Broad scan cost remains O(ledger + causes + initial window + output sort). The first experiment should remove redundant temporary history/generator work, preserve eager failure order, minimum-parent selection, native object identity, stable insertion/sort ties and all cache invalidation. No new retained memory or index is needed. Detailed schema/mutation/error audit: reviews/carried-query-candidate.md. Regression protection includes real ledger fixtures, malformed/partial rows, strict/inclusive boundaries, both directions, native snapshots and all22 RAW/smoke scenarios.

2. **Post-stop accepted Order query, OrderAudit1471:** scans candidate confirmation suffixes and constructs/sorts physical matches. Existing cache depends on confirmation-index size and resets. A creation/liveness index would need all cause-only mutations, revocations/restorations and residual insertion rank; adding it now is materially riskier than local allocation reduction. Worst-case extra index O(ledger+causes) plus mutation cost; no such index is accepted.

3. **E discovery/rebuild, E378/788/1218 and Bridge1939/2274:** dominates cumulative runtime through repeated _zone calls, accepted Order queries and dependent reconciliation. Existing NlogN sparse extreme tables are reconstructed per detector; reuse across rebuilt detectors or regimes broadens lifetime and could retain stale mutable context. Repeated fresh prefixes/suffixes are an explicit semantic isolation obligation. Do not remove passes or share detector state merely to improve the displayed time.

4. **Blue internal geometry, Blue458:** repeated full behavior geometry checks are measurable in the supplied profile. A per-invocation containment index may be a later opportunity, but it must preserve exact inclusive/strict containment, identity and first/last semantics. Public Blue version/output compatibility also needs current convention review. No proposed indexed rule has been implemented or claimed equivalent.

Cumulative function fractions overlap along call chains and must not be summed. Counts/profile percentages are input-specific observations, not permanent project facts. Fewer source lines, static complexity bounds and historical improvements are not measurements of the current candidate.

## Final separate profile comparison

| Case | Function | BEFORE/AFTER calls | BEFORE/AFTER cumulative seconds |
| --- | --- | ---: | ---: |
| xau-oct26-30s-bullish | order_audit_engine.py:_carried_orders_for_parent | 27911 / 27911 | 8.158253 / 5.900777 |
| xau-oct26-30s-bullish | order_audit_engine.py:_post_stop_accepted_orders_for_parent | 27911 / 27911 | 3.974280 / 3.862855 |
| xau-oct26-30s-bullish | e_zone_detector.py:_zone | 27911 / 27911 | 16.532631 / 14.127352 |
| xau-oct26-30s-bullish | blue_line_detector.py:geometry_is_internal | 2004 / 2004 | 1.238359 / 1.668888 |
| xau-oct26-30s-bearish | order_audit_engine.py:_carried_orders_for_parent | 19081 / 19081 | 9.169965 / 4.577187 |
| xau-oct26-30s-bearish | order_audit_engine.py:_post_stop_accepted_orders_for_parent | 19081 / 19081 | 4.068156 / 2.395282 |
| xau-oct26-30s-bearish | e_zone_detector.py:_zone | 19081 / 19081 | 17.545258 / 9.367184 |
| xau-oct26-30s-bearish | blue_line_detector.py:geometry_is_internal | 1002 / 1002 | 1.396450 / 0.805829 |

The fresh post-repair baseline and final profiles reproduce their actual CLI outputs exactly. Raw pstats are retained in repaired-before/profile and after/profile;06_PROFILE_BEFORE_AFTER.csv includes exact line/call/self/cumulative records. These are instrumented observations: removing generator calls also removes profiling overhead. Profile timing ratios are never quoted as normal runtime speedup; use the uninstrumented matched pairs/actual CPU/wall medians and dispersion. Cumulative values overlap and must not be summed. Bridge-reported phase timing comparisons are retained in11_STAGE_TIMING_RESULTS.csv and are wall telemetry, not process CPU.
