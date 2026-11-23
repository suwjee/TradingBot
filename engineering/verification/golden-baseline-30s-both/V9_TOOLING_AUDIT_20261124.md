# TradingBot V9 — deep profiling and trace tooling audit (2026-11-24)

**Release status: `INCOMPLETE` / `TRACE_COVERAGE_PARTIAL`; NOT `TOOLING VERIFIED`; no performance promotion.** This is an append-only verification record; no trading runtime, algorithm reference, RAW, pinned Golden ZIP, or frozen oracle was changed.

## Immutable anchors
- Correctness oracle: pinned Git commit `01d54ecf0149ebd15de92798be18810b6e2eb791`; all 15 production Git blob hashes matched.
- Original Golden ZIP: `TradingBot_GitHubMain_Baseline_30s_Both_01d54ecf_20261123_v1.zip`, SHA256 `080175abbd7a3895596230b40783062901deb38c0cc8dd3b97fc058ef21cbb88`.
- V8.1 remains the unchanged performance reference. V8.2 was not promoted. V9 is **test-only** tooling; there is **no new production source version**.
- Seven pinned real 5s RAW (791,174 total records), native `--timeframe 30 --raw-timeframe 5 --direction both` with all stages and bridge enabled in one invocation each.

## Completed verification (new observations, not copied speedup claims)
- Frozen archive SHA256SUMS/CRC, all seven RAW SHA/count/time and seven original stable SHA: **PASS**.
- Full **7/7** untouched V8.1 native both-direction outputs byte-equal to pinned Golden stable bytes, with telemetry key/order/type validated: **PASS**. Sum of freshly observed unprofiled V8.1 seven wall times: **138.375 s** (host-dependent).
- Original vs unchanged V8.1 synthetic native output parity at **100k, 250k, 500k, 1M 5s rows: 4/4 PASS**; one complete, unprofiled run per source/size (not a paired performance promotion test).
- At 1M synthetic, frozen original: **435.6737 s, 1653.152 MiB sampled peak RSS**; V8.1: **374.5539 s, 1655.715 MiB sampled peak RSS**. This is **one non-paired observation**, NOT a V9 speedup and NOT a stable V8.1 promotion proof.
- Deterministic final-output-stage JSONL+gzip boundary snapshots: **7/7 equal**, 61,418 records from each source and both directions. Source bytes unaffected. Important: this is `STAGE_BOUNDARY_ONLY`, not full in-process semantic execution tracing.
- Strict test-only Golden verifier: **16/16 controlled assertion/mutation tests PASS**. Audited existing GitHub verifier defects: valid native JSON with trailing newline rejected; extra sibling keys in final `timings` not rejected. The upstream checker and immutable artifacts remain untouched.
- Selected internal E state comparisons on two short RAWs: XAU 15/15 and OIL 20/20 E runs equal; native stage return snapshots XAU 37/37 and OIL 42/42 equal. This does not prove all hidden state.
- Live seed/append, delta mismatch, changed-RAW error behavior: **3/3 PASS**. Short synthetic edge variants incl. Doji, flat candles, chronology gaps and duplicate epoch: **6/6 PASS**.
- Source/CLI static signature and compilation audits: PASS. cProfile independently measured 15k and 97,930 real rows; the 97k E `_discover_candidate_chains` had 114 calls / 12.438 s cumulative, `_zone` 33,305 calls / 10.621 s cumulative. These call times overlap with parent functions.
- A separate 15k `tracemalloc`/GC sample preserved Golden stable byte parity; it is **not** used in unprofiled wall benchmarks.
- 1M V8.1 E-stage observed wall telemetry: **202.8766 s** of ~372.0219 s Bridge wall; candidate indexing risk is evidence-led but `O(N²)` is **not formally proved** from these limited samples.

## Open mandatory gates and release decision
`INCOMPLETE`: full lossless in-process semantic tracing of candidate rejection, pre/post state, Parent Stop/StopAll, OrderAudit, all seven RAW and synthetic, plus ON/OFF instrumentation equivalence; high-volume scanned-row/cache/heap/sort/allocation counter coverage; complete official regression suite; reproducible 1M AB/BA paired benchmark repeats. Neither final-output equality nor stage-output projections can replace these gates. No runtime code was refactored, and no algorithm outputs or source hashes were changed by this tooling.

## Immutable packaged evidence in ChatGPT Library
Stored under `/TradingBot/Versions/V9-2026-11-24/`, uploaded and independently round-trip SHA-verified:
- `TradingBot_Engine_V9_30S_BOTH_TOOLING_20261124.zip`: **509,548 bytes**, SHA256 `e60115fb92c2f09fe2a21be1af456dade0b658b132ebc9dd3d7ef579add54a10`.
- `TradingBot_Engine_V9_30S_BOTH_VERIFICATION_20261124.zip`: **41,310,042 bytes**, SHA256 `5d320795f49870533bb077c5190b52676fd473aca95464327c0fd62de2eb872f`.

Both archives passed extracted CRC, every member SHA256SUMS, all embedded Python compile checks and (verification ZIP) native 15,542-row complete smoke calculation with exact Golden stable SHA. Supporting files include `MANIFEST.json`, `ENGINE_V9_AUDIT.md`, `V9_COMPLEXITY_MAP.md`, `V9_PROFILING.csv`, `V9_TRACE_COVERAGE.json`, `V9_FIRST_DIFF_TESTS.json`, `V9_GOLDEN_TRACE_SPEC.md`, scaling and call graph plots, CPU/RSS and first-divergence tools.

**No historical Golden documentation, source runtime, or raw dataset was overwritten.**