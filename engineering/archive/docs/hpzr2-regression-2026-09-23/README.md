# HPZR2 exact-output regression evidence

The nine production modules were copied to a frozen temporary engine tree before
the optimization edit. `frozen-baseline-source.zip` preserves those exact files
for comparison only. The `baselineSourceSha256` and `candidateSourceSha256`
entries in each manifest identify the two trees. The only production source
difference is in `_bridge_proven_strict_event()` in
`engine/bridge/trading_pipeline.py`; `production-change.diff` records it.

`scripts/hpzr2_regression.py` runs the frozen engine and current engine against
each physical RAW file independently. It saves the complete ordered output from
each run as `case-NN.baseline.json.gz` and `case-NN.candidate.json.gz`, then
compares both parsed objects and normalized JSON bytes. Normalization removes
only the top-level `timings` value, which is inherently nondeterministic. The
manifest records RAW and source hashes, per-stage hashes and counts, run times,
and a PASS/FAIL/INCOMPLETE result after each pair of runs.

The `default/` directory covers the production default payload. The
`bridge-output/` directory repeats the comparison with `--bridge-output`, the
path changed by this refactor. Its two large cases were rerun with longer
timeouts in `bridge-output-large/`. `summary.json` combines the successful runs:
**14/14 exact comparisons on all seven physical RAW files**, each in default
and Bridge Output modes. The independent `scripts/hpzr2_verify_saved.py` check
reopens every saved output, recomputes hashes for each stage, checks exact
ordered bytes and parsed objects, verifies current RAW hashes, and checks the
frozen-source archive against the source hashes. The short synthetic matrix
also checks both directions independently, a one-second analysis timeframe,
and a partial display range while calculation still receives the complete input.

This is an output-equivalence check. It does not turn timing telemetry into a
stable output field or prove that every possible RAW input has been exercised.

## Change and measurement

Profiling a 60,000-row synthetic input with Bridge Output enabled found 1,658
calls to `_bridge_proven_strict_event()` and roughly 95.7 million `getattr`
calls, mostly from rebuilding the entire lower timestamp list each time. The
production change uses `MarketChronology.second_times`, which the Reaction
engine builds from the same `market.seconds` sequence. The fixture fallback is
used only when a stand-alone projection fixture lacks that chronology field.

Three repeated full-process runs on the identical 60,000-row input, both
directions, 30-second analysis timeframe, and Bridge Output enabled gave median
wall time **4.978 s before** and **1.138 s after** (4.38×). Median CPU time was
4.922 s before and 1.109 s after. Normalized JSON was byte-identical in every
run (SHA-256 `ec11fd91c85e96dde5be1d6cdf363a3aad08e1a29c7f9d1e491d6195e0c7ed3d`).
The default path measured 1.126 s before and 1.138 s after, within run noise;
this change only executes when Bridge Output is requested.

The individual benchmark summaries, representative exact outputs, generated
60,000-row input, and replay scripts are in `synthetic-benchmark/`. The
`raw_sha256` field in the copied benchmark script is its unnormalized **stdout**
hash, so it varies with timing telemetry; `normalized_sha256` identifies the
comparable output. `summary.json` names this field accordingly and records the
physical benchmark input hash separately.

| Stage, median ms across three Bridge Output runs | Before | After |
| --- | ---: | ---: |
| Reaction | 70.68 | 69.07 |
| Blue | 8.23 | 8.10 |
| A | 46.18 | 44.81 |
| S | 17.00 | 17.42 |
| E | 354.61 | 353.34 |
| Lifecycle | 23.61 | 22.70 |
| Serialization, including Bridge Output projection | 3920.80 | 39.19 |

The seven physical RAW Bridge Output runs each had exact output equality.
Their single-run times are diagnostic rather than controlled repeat-run
benchmarks: 14,140 rows 1.60→0.86 s; 36,821 rows 9.91→2.72 s; 57,963 rows
34.48→6.60 s; 161,376 rows 56.15→3.73 s; 183,741 rows 433.28→79.93 s;
354,698 rows 1738.35→266.95 s; and 621,326 rows 1048.85→51.64 s.

The change eliminates one temporary timestamp-list allocation per proven event.
Median peak working set in the repeated synthetic runs was 96,763,904 bytes
before and 97,239,040 bytes after. There is no measured peak-memory reduction
to claim from those runs.

## Validation boundary

- Both default and Bridge Output comparisons finished on all seven physical RAW
  files, from 14,140 to 621,326 rows; every case has exact object and
  ordered-JSON equality. The two original Bridge Output runs marked
  `INCOMPLETE` in `bridge-output/manifest.json` were rerun successfully in
  `bridge-output-large/manifest.json` and remain visible as an audit trail.
- The synthetic matrix in the temporary benchmark workspace passed six more
  exact comparisons, including separate Bullish/Bearish requests, a one-second
  timeframe, and a partial display window over complete input.
- `npm.cmd test` passed 156/156 and `npm.cmd run build` exited 0. The full Python
  bridge suite ran 11 tests with 9 passes and two pre-existing errors in
  `test_trading_pipeline.py`: both call the absent `_report_category` helper.
  The new projection performance tests and existing projection tests pass 9/9.
- An isolated Graphify engine update found 626 nodes and 1,666 raw edges.
  Diagnostics reported no missing or dangling endpoints and 59 same-endpoint
  relation variants that its simple graph collapses. The dirty, user-owned
  repository Graphify snapshots were preserved.

A timed-out or interrupted baseline is `INCOMPLETE`, never PASS.
