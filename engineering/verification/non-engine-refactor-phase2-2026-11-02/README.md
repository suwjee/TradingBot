---
title: Non-Engine Refactor Phase 2 — Local Calculation FIFO and RAW Validation
document_role: evidence
lifecycle: historical
owner: chart-server
created_at: 2026-11-02T07:02:45.741Z
last_modified_at: 2026-11-02T07:02:45.741Z
---

# Non-Engine Refactor Phase 2 — FIFO Scheduling and RAW Validation

## Scope, authorization and immutable boundary

- Target: `refactor` branch of `suwjee/TradingBot`.
- Baseline branch: `main@afb586b69ecd6e12bcef30e2dbc4163e764dfcdb`.
- All files beneath `engine/` are strictly **read-only**; no modification, reference synchronization, fixture edits, generated files or repackaging is permitted.
- The Engine retains exclusive authority for Bullish/Bearish trading calculations. This phase changes **only non-Engine implementation details** in Chart-owned infrastructure.
- This is a bounded performance refactor, not a claim that all Chart/Vite/FARAZ performance improvements are complete.

## Source investigation

### Calculation queue

`apps/chart/server/calculation-coordinator.js` previously used `pending.shift()` for each dequeued job. For a long backlog, repeated front deletion can move the remaining array elements repeatedly.

The changed queue uses a read cursor (`pendingHead`), clears each consumed slot immediately, resets the array when empty, and compacts the consumed prefix only when it is substantial (at least 1024 items and at least half of the array).

Preserved contracts: max parallel active jobs; first-in-first-out order; in-flight key deduplication; shared Promise results; progress replay; cancellation and shutdown; rejection propagation; exact `stats()` object shape.

### RAW validation

`apps/chart/server/raw-resource-store.js` previously built an `Object.fromEntries` result and intermediate per-candle arrays for each row, although only five numeric values were needed. The changed validator reads the same five values directly, using the same `Number()` conversion, the same complete-key schema check, and the same finite/chronological/OHLC predicates.

The bytes of stored RAW inputs, filename/sidecar policy, source identity, coverage, read JSON shape, public output and authoritative trading rules are not intentionally modified.

## Regression-first workflow

1. Added a deterministic standalone benchmark at `apps/chart/tests/benchmarks/server-hot-paths.mjs` **before changing source**.
2. Added three independent contract tests at `apps/chart/tests/unit/server-hot-path-contract.test.mjs` **before changing source**: 4,000-job FIFO/dedup/results, 4,000-job shutdown/rejection, and RAW accepted/rejected-schema/chronology equivalence.
3. Baseline tests with new contract cases passed in [CI run 41403400907](https://github.com/suwjee/TradingBot/actions/runs/41403400907), including both Windows and Linux.
4. Applied FIFO implementation refactor in commit `889097f980fd89bda3aa31a9e0a75a76fed6f9f3`.
5. Applied RAW validation allocation refactor in commit `ba1a7d077e7e00edcefda58fa1408799eb36cf72`.
6. Final post-refactor [CI run 41403516091](https://github.com/suwjee/TradingBot/actions/runs/41403516091) passed on Ubuntu and Windows; [anti-drift 41403515990](https://github.com/suwjee/TradingBot/actions/runs/41403515990) passed.
7. Verified the full branch comparison contains **no `engine/` changes**. The CI workflow additionally compares SHA-256 of *all* files under `engine/` before and after its tests/build on both operating systems, with `PYTHONDONTWRITEBYTECODE=1`.

## Final verification

| Check | Ubuntu | Windows |
| --- | --- | --- |
| Full Chart/API unit suite | PASS — 267 tests, 262 passed, 5 skipped, 0 failed | PASS — 267 tests, 267 passed, 0 skipped, 0 failed |
| Vite client production build | PASS | PASS |
| Deterministic hot-path benchmark | PASS | PASS |
| Branch-to-main no Engine file changes | PASS | PASS |
| Engine filesystem pre/post SHA-256 equality | PASS | PASS |
| Anti-drift | PASS | PASS |

The Linux skipped tests are platform-specific, not failed cases. Compilation/build and non-Engine tests are not substitutes for independent real-market Engine correctness.

## Benchmark measurements

Environment: GitHub-hosted Node 22 CI runners, 5 measured samples, medians below. Workloads: read, JSON-parse and validate 40,000 synthetic 5s candle rows; enqueue/drain 20,000 unique work items with one active slot. The benchmark validates FIFO result identity and queue cleanup. It does not use or modify any production/authoritative RAW.

**Original baseline on same OS runner class:** [run 41403249589](https://github.com/suwjee/TradingBot/actions/runs/41403249589), commit `7d9cc7b571e4964eef264b22970bc03f2f525808`.

**Final refactor:** [run 41403516091](https://github.com/suwjee/TradingBot/actions/runs/41403516091), commit `ba1a7d077e7e00edcefda58fa1408799eb36cf72`.

| Measurement (median milliseconds; lower is faster) | Ubuntu before | Ubuntu after | Windows before | Windows after |
| --- | ---: | ---: | ---: | ---: |
| RAW read/parse/validate, 40k rows | 54.053 | 23.538 | 49.800 | 27.648 |
| FIFO queue, 20k jobs | 191.639 | 38.596 | 228.541 | 45.199 |

These are **runner-local indicative** comparisons, not guaranteed production speedups. They include JSON parsing and disk cache in RAW read timing and task scheduling/Promise work in queue timing. CI VMs vary in hardware allocation and contention; repeated independent CI rounds or same-host A/B are needed for high-confidence performance claims. Memory reductions were not directly benchmarked: fewer temporary per-row objects are an implementation fact, not an independently measured peak-RAM reduction.

## Review and limitations

- All behavior-sensitive queue paths are exercised through existing and new contract tests. The GUI itself, live FARAZ authentication, and a whole-workstation CPU/RAM profile were **NOT RUN**.
- No Engine Source, Reference, test, archive, or RAW evidence was touched. Neither `main` nor `production` was changed.
- Further work on disk-backed calculation cache, frontend render lifecycle, Vite synchronous I/O, and persistent state must be separately analyzed and tested. Existing caching/RAW security contracts must be preserved; do not make unauthorized cache eviction or history-truncation decisions.
- No merge, tag, release or deployment is implied by this report.

## Files in the Phase 2 diff

- `apps/chart/server/calculation-coordinator.js`
- `apps/chart/server/raw-resource-store.js`
- `apps/chart/tests/unit/server-hot-path-contract.test.mjs`
- `apps/chart/tests/benchmarks/server-hot-paths.mjs`
- `.github/workflows/chart-refactor.yml` (benchmark execution added)
- This report.
