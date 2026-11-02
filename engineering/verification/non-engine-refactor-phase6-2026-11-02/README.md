---
title: Non-Engine Refactor Phase 6 — Historical Hitbox Compaction and Browser Memory Profile
document_role: evidence
lifecycle: historical
owner: chart-presentation
created_at: 2026-11-02T09:35:21.368+00:00
last_modified_at: 2026-11-02T09:35:21.368+00:00
---

# Non-Engine Refactor Phase 6 — Hitbox Collection and Large-Chart Memory Verification

## Baseline, scope and authority

- Target branch: `refactor` in `suwjee/TradingBot`.
- Previous accepted phase baseline: `654a29531e6d2a72cb701bc09d79fbac9efb77f9`.
- Baseline `main` at inspection: `afb586b69ecd6e12bcef30e2dbc4163e764dfcdb`.
- Root `AGENTS.md`, GPT_bot companion instructions, maintained Zero-Difference Refactor/Testing/UI-UX documents, current Chart Source/tests, and **both** accepted V5.4.33 Bullish/Bearish References were inspected read-only.
- The historical user-supplied `engine.zip` was safely extracted and recursively inspected **outside** the project. The package contains 14 files and historical V5.4.32 References; it was not used to override current GitHub Source.
- The user prohibits **all** changes to `engine/`; none were made. Immutable market RAW evidence, trading direction, calculation rules, persisted result fields, public HTTP routes and calculation cache identity were not modified.

## Production changes

### Hitbox clipping and large overlay compaction

Owner: `apps/chart/src/chart/primary-structure.js`, called from `apps/chart/src/main.js` `drawIndicator()`.

**Original:** Each historically clipped calculation segment did
`hitBoxes.push(...clipHistoricalHitBoxes(hitBoxes.splice(firstHitIndex), historicalEndX))`, temporarily creating the spliced segment, `flatMap` arrays and a flattened clone array, then spreading the output as individual function arguments.

**Refactor:** Added a shared single-hitbox clipping primitive used by both the unchanged public array-returning `clipHistoricalHitBoxes(hits,right)` contract and the new `clipHistoricalHitBoxesInPlace(hits,startIndex,right)`. The `drawIndicator()` caller now compacts **only that newly rendered segment** in place, leaving earlier directional/segment hitbox references unchanged.

Preserved properties:
- Existing Rectangle/Line/Point clipping predicates, strict boundary behavior, right-hand clipping geometry, `clipRight`, radius defaults, and no clipping when nonfinite historical end coordinate.
- Exact source order; segment ownership and pre-existing prefix; cloned hitbox objects rather than mutation of original hitboxes; original array-returning public helper.
- Sparse-array skip semantics and prior behavior for other/unknown hitbox shapes.
- Actual indicator painting, clip regions, selection lookup, hit-test identity fields, and Engine-owned Bullish/Bearish decisions were not changed.

Removed operations at the production call site: `splice` segment allocation, `flatMap` flatten allocation, and `push(...largeArray)` with engine-dependent maximum argument count. There is no cap or truncation of historical or RAW state.

## Test-first evidence

The shared clipping primitive and in-place candidate helper were added **before changing the production caller**, with:
- `apps/chart/tests/unit/historical-hitbox-buffer.test.mjs`: independent copy of the original reference clipping algorithm, exact output comparisons for negative, zero, equality, large and NaN boundaries, all shapes, sparse arrays, earlier segment reference ownership, original-clone nonmutation, and **150,000** large synthetic hits.
- `apps/chart/tests/benchmarks/historical-hitbox-buffer.mjs`: same runner/process comparison of old `splice+flatMap+spread` vs new compaction on 10,000 hits (7 samples). An independent 80,000-hit optimized stress measurement verifies large input handling.
- The previous `apps/chart/tests/unit/primary-structure.test.mjs` historical boundary, multi-regime and drawing tests still pass.

**Pre-caller-change CI:** [run 41421303991](https://github.com/suwjee/TradingBot/actions/runs/41421303991) successful on Ubuntu/Windows.

**Post-caller-change CI:** [run 41421522004](https://github.com/suwjee/TradingBot/actions/runs/41421522004) successful on Ubuntu/Windows. This run includes full Chart tests, browser tests, both synthetic performance harnesses, Vite build and before-after Engine SHA-256 comparison.

## Chrome/Chromium retained-heap profiling

Extended the real browser smoke at `apps/chart/tests/e2e/chart-startup-smoke.mjs` with optional `--profile-memory`. The existing normal smoke remains intact.

The separate profile mode:
1. Creates a **new, disposable**, Chart-owned state directory and 12,000 synthetic 5s candle records; no uploaded authoritative RAW is read or modified.
2. Starts the real Vite/Chart workspace in Chrome/Chromium.
3. Loads the synthetic Chart, opens the Drawing Object Tree, verifies drawing ordering/search/pointer behavior.
4. Uses Chrome DevTools Protocol to request garbage collection and read `JSHeapUsedSize`, `Nodes` and `JSEventListeners`.
5. Repeats 100 open/search/close cycles in the **same page**, measures again after GC, asserts no unexpected DOM-node/listener growth, and writes full raw metrics to CI logs.
6. Cleans up its sandbox and browser/server processes.

**Browser profile results (one run per OS, same virtual runner class, values in bytes unless stated):**

| Scenario | Ubuntu before production caller change | Ubuntu after | Windows before | Windows after |
| --- | ---: | ---: | ---: | ---: |
| Retained JS heap increase over 100 cycles | 15,796 | 15,732 | 34,232 | 19,112 |
| Added DOM nodes after 100 cycles | 54 | 54 | 54 | 55 |
| Added `JSEventListeners` after 100 cycles | 0 | 0 | 0 | 0 |

**Crucial limit:** This browser profile exercises chart load and repeated Object Tree DOM work, **not** Engine-fed Indicator hitboxes. Do **not** attribute the small cross-run differences in browser heap to the Hitbox change. Browser/GPU memory, long-running market/live FARAZ sessions, large real Indicator payloads and user workstation RAM/CPU use were NOT measured. This scenario detects gross panel/lifecycle retention only and cannot establish the absence of all leaks.

## Performance results for the changed hot path

Each original/new pair ran in the **same Node process, on the same CI runner**, with identical 10k synthetic hitboxes; median of seven timed runs.

| Operation | Ubuntu legacy | Ubuntu optimized | Windows legacy | Windows optimized |
| --- | ---: | ---: | ---: | ---: |
| Clip 10,000 historical Hitboxes, ms | 1.138 | 0.873 | 2.330 | 1.498 |
| Maximum observed per-sample JS heap delta, bytes | 3,373,000 | 2,306,072 | 3,368,192 | 2,301,080 |

The optimized path also completed a separate **80,000-hit** stress case with median **3.438 ms (Ubuntu)** and **6.998 ms (Windows)**. The regression suite includes **150,000** hits for correctness and argument-spread safety.

The per-sample heap delta is a noisy Node heap-use sample, *not* peak RSS, retained Chrome memory, or a guarantee of specific RAM savings in production. Avoid extrapolating a universal percentage from these microbenchmarks.

## Final CI verification

| Gate | Ubuntu | Windows |
| --- | --- | --- |
| Full Chart/API unit suite | **PASS**, 296 total: 291 passed, 5 platform skips, 0 failed | **PASS**, 296/296 passed, 0 failed |
| Original 900-candle real browser smoke | PASS | PASS |
| 12,000-candle real browser/heap profile | PASS | PASS |
| Hitbox original-vs-optimized benchmark | PASS | PASS |
| Existing RAW/FIFO/drawing benchmarks | PASS | PASS |
| Vite production build | PASS | PASS |
| Every Engine file SHA-256 before/after tests | PASS | PASS |
| Branch diff against `main` touching `engine/` | **None** | **None** |

The repository anti-drift CI is also enabled for this branch. Do not classify a successful UI smoke as real Engine semantic regression proof.

## Changed paths relative to Phase 5

- `apps/chart/src/chart/primary-structure.js` — original helper retains contract, shared clipping primitive and in-place helper.
- `apps/chart/src/main.js` — call-site replacement only.
- `apps/chart/tests/unit/historical-hitbox-buffer.test.mjs` — regression and 150k stress.
- `apps/chart/tests/benchmarks/historical-hitbox-buffer.mjs` — old-vs-new 10k measurement plus 80k stress.
- `apps/chart/tests/e2e/chart-startup-smoke.mjs` — opt-in, CDP-based large-chart retained heap profile.
- `.github/workflows/chart-refactor.yml` — cross-platform benchmark/profile gates.
- This report.

## Completion boundaries and future work

This **Phase 6 scope** is complete for bounded historical hitbox allocation reduction and a reproducible large-chart browser memory baseline. It is **not** a claim that the ~7K-line Chart entrypoint, every overlay/tool or all memory leaks have been eliminated.

Further engineering needs to use instrumented **actual Engine-output** Indicator overlay sessions with baseline/repeated viewport/GC data to evaluate overlay performance and real retention; do not approximate trading results from synthetic RAW. Other isolated UI avenues include hot-path `drawIndicator()` geometry allocation and Document Object Tree incremental updates, but these require separate behavioral and accessibility contracts.

No changes were made to `main`, `production`, `engine/` or immutable RAW; no PR, merge, tag, release or deployment was performed.
