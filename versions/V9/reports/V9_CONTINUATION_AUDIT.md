# TradingBot V9 continuation — refactor-branch execution audit

**Final status: `INCOMPLETE` — `TRACE_COVERAGE_PARTIAL` — NO-GO for `TOOLING VERIFIED`.**

All newly authored tooling/report changes were committed **only to the existing `refactor` branch**, under `engineering/refactor-v9/`. The branch was not merged with `main`; no engine runtime file, trading behavior or RAW input was overwritten. The pinned correctness anchor remains `01d54ecf0149ebd15de92798be18810b6e2eb791` and V8.1 remains the unchanged prior performance reference. The older V9 audit previously placed on `main` remains historical and was *copied* into `refactor`; this continuation made **no new `main` modifications**.

## Reused verified V9 baseline evidence

- Golden ZIP SHA/CRC and 15 original Git blob SHA: `PASS`.
- 7/7 complete original-vs-V8.1 native both-direction real RAW outputs at 30s from 5s rows: strict stable JSON and telemetry contract `PASS`.
- All 4 full-length synthetic scales (100k, 250k, 500k, 1M): native stable result parity `PASS` (previous single runs, not ABBA confidence).
- 7/7 stage-boundary JSONL snapshots equal. This is **final-output projection**, not internal event proof.
- Previous 3 Live selected and 6 synthetic edge scenarios passed; strict Golden verifier controlled mutation assertions re-run 16/16 `PASS`.

## Work executed in this continuation

1. Implemented **test-only** dynamic in-process method-result observer, versioned JSONL gzip event manifest, semantic dataclass/Decimal/datetime serializer, family-local deterministic comparator and fail-closed mutation tests. No Engine source edited.
2. Confirmed observer ON output equals pinned Golden on complete 15,061-row USOIL and 15,542-row XAUUSD for **both pinned original and V8.1** (4 complete executions). Collected ~16k/15k internal observer events per original/candidate USOIL and ~14k/14k for XAU.
3. For USOIL, the AST-instrumented `_zone` semantic rejection decision produced **151 identical `NO_ELIGIBLE_ORDER_AFTER_CANONICAL_ROUTE_FILTER` events per source**, without output change.
4. Compared 3,896 USOIL and 3,581 XAU function-return semantic events in **family-local execution order**: all compared families returned equal values and limited pre/post state summary. Excluded implementation-only method call patterns: USOIL 12,476 original invocations, XAU 11,240. The observer also revealed two families with input-level drift (`EZoneDetector._zone` and `SZoneDetector.reconcile_shared_order_stops`). These drifts are preserved in diagnostic reports, **not concealed** as full-pass results.
5. Developed an AST-based test-copy operation meter for selected Python `for`/`while`, sort, heap and E parent-stop cache paths; smoke output remained byte-identical. Complete metered raw jobs: 5/7 V8.1 datasets **PASS**; 247,851-row job hit tool execution timeout, 284,184-row not run. Exact counters are only for instrumented statement sites and exclude comprehensions/uninstrumented functions; these cannot be promoted to whole-Engine operation totals.
6. Executed one complete **unprofiled native 100k ABBA block (Original, V8.1, V8.1, Original), 4/4 stable parity PASS**; observed median Original/V8.1 wall ratio ~1.184 in this small sample. Not a V9 speedup, not a repeated 1M ABBA benchmark, and not a basis for performance promotion.
7. Controlled internal comparator mutation suite **6/6 assertions PASS**. Its deliberate cross-family reorder is *not* detected by the scoped family-local comparison; this known gap is included rather than represented as full chronological trace equality.
8. Added 25 previous V9 verification/profiling tools and eight new observer/counter/benchmark tools to `engineering/refactor-v9/` on the **refactor** branch; pinned source and archived Baseline remain untouched.

## Why V9 is not complete

Hard gates still missing: full lossless in-process event capture of candidate rejection, stage handoff, OrderAudit, Parent Stop/StopAll and pre/post accepted ledgers on **all seven** real RAW and 1M synthetic; trace-global chronological tie comparison (not only family local); complete precise per-operation scanner/cache/sort/heap/allocation statistics, including large metered jobs; three or more 1M ABBA blocks with unprofiled CPUs/RSS; and the full official regression suite. Some tests are **NOT RUN** and one large metered run was **INTERRUPTED BY TOOL TIMEOUT**. The existing successful 7/7 native output parity does not discharge those independent trace/benchmark gates.

## Release decision

`INCOMPLETE / TRACE_COVERAGE_PARTIAL / NO PERFORMANCE PROMOTION`. Preserve V8.1 as the previous performance reference and keep this V9 tooling in `refactor` only. Archive JSON/CSV plus source alongside the preceding V9 TOOLING and VERIFICATION ZIPs in ChatGPT Library `/TradingBot/Versions/V9-2026-11-24/`. No claim of universal semantic equality, no `TOOLING VERIFIED` status and no change to production code.
