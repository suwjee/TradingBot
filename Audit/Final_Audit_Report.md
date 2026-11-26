# Final audit report — PARTIALLY_VERIFIED

## Pinned baseline and evidence

Baseline: 466eb875070f02cd0dbfb105033422bbe2fd8c70. Previous source inventory: 64 engine files, consisting of 13 operational modules, 3 package markers, 44 test/tool files, 1 CSS and 3 references. Previous manifest: 17,119 Python lines, 576 lexical def declarations and 85 class declarations. These are inventory counts, not coverage. The prior review compared all 16 Python files with the two directional references (16/16 each). The later review compared all embedded blocks across all three references (16/16 each after normalizing path keys). This equality is not evidence of algorithmic equivalence. English publication has reconfirmed equality of the three embedded snapshots.

## Recorded tests from the earlier partial package

- Exact Git blob hash validated for core_utils.py, direction_policy.py and true_false.py in the local isolated oracle.
- Seeds 31, 73 and 191: 1,460 comparisons each; 4,380 total, zero observed differences. 1,200 containment, 30 ordered datetime/Decimal, 450 direction comparisons, 2,400 T/F annotations and 300 synthetic aggregation comparisons. T/F used synthetic crossing/closure callbacks and the isolated priority mapping, not the full lifecycle/lower-index integration.
- Seven complete RAW files (791,174 rows), no sampling, 21 aggregation comparisons for 1, 60 and 300 seconds. Exact timestamp, sequence, counts and Decimal sign/digits/exponent hashed; all equal. Timeframe 1 uses lower_only=true. Combined measured dataset read/check/aggregate/hash elapsed time 43.466 seconds, not total project runtime. Per-case times in Benchmark_Report.json. No nonincreasing timestamp pair or invalid OHLC row was observed in these seven inputs.
- These results came from the previous partial execution. The English publication does not count them again or assert new full-engine runtime tests.

| Gate | Result |
|---|---|
| Inventory and reference-block equality | VERIFIED in stated scope |
| Module-level semantic description | DOCUMENTED / INCOMPLETE |
| Source-to-function mapping | INCOMPLETE |
| Branch coverage | NOT MEASURED |
| Isolated differential tests | PASS |
| Full engine unit/regression | NOT RUN |
| Full RAW indicator calculation | NOT RUN |
| Complete Bullish/Bearish reconstruction | NOT VERIFIED |
| Batch/Live integration | NOT RUN |
| Complete exact JSON schema | INCOMPLETE |
| Independent clean-room reconstruction | NOT RUN |
| Formal equivalence | NOT PROVEN |
| Full-engine performance and peak memory | NOT MEASURED |

## Limits and publication decisions

The prior local clone failed DNS; no complete local checkout or engine.zip was available. The partial package used direct GitHub textual access, isolated oracle fragments and independent narrow implementations. The English edition consolidates and expands semantic summaries with the existing pinned English reference prose (without complete source appendices). The earlier long request is consolidated in Requested_Prompt.md, not translated verbatim. Reports preserve the actual prior measurements. Source files, existing project tests, the official synchronized references, and main are unchanged. External RAW files remain external; their identifiers and digests are recorded. A successful publication or limited test does not qualify this package as a complete production reconstruction.

See Ambiguities_And_Conflicts.md, Function_Coverage.json, Branch_Coverage.json, Verification_Report.json, Benchmark_Report.json and Regression_Report.json.
