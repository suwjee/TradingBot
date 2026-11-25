# Partial verification — documented test scope

Baseline: 466eb875070f02cd0dbfb105033422bbe2fd8c70. The following is a semantic description of the previously measured suite, not a runnable test program.

| Check | Per seed | Three seeds |
|---|---:|---:|
| Chronological containment against ordered direct scan | 400 | 1200 |
| Decimal normalization and ordered-naive datetime checks | 10 | 30 |
| Strict cross, confirmation cross and better extreme in both directions | 150 | 450 |
| Final T/F annotation against baseline with synthetic callbacks | 800 | 2400 |
| Synthetic RAW aggregation | 100 | 300 |
| Total | 1460 | 4380 |

Seeds 31, 73, 191. Original execution and migration retest each recorded zero differences in this scope. Compare Decimal sign, digit sequence and exponent as well as values; compare T/F group mutation including labels, repair and repeated flags.

## RAW aggregation

Use the seven exact input files identified in the historical report, without sampling. For each, test timeframe 1 (lower-only), 60 and 300 seconds. Compare lower and main counts and exact ordered timestamps/OHLC Decimal representations. A missing dataset is not a pass. Historical observations: 791,174 rows and 21 successful comparisons. Full RAW indicator calculation, lower-index T/F integration, Live transaction tests and all project unit/regression tests were not covered.

## Evidence

See [verification report](../Audit/Verification_Report.json), [retest](../Audit/Migration_Synthetic_Retest.json), and [benchmark report](../Audit/Benchmark_Report.json). The executable scripts have been removed from the current tree, not from the shared history. This document does not claim independent rerun of the original random fixture generator.
