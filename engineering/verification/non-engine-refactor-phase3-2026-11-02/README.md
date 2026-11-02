---
title: Non-Engine Refactor Phase 3 — Vite Cache Boundaries and Chart Presentation Lifecycle
document_role: evidence
lifecycle: historical
owner: chart-vite
created_at: 2026-11-02T07:46:50.911Z
last_modified_at: 2026-11-02T07:46:50.911Z
---

# Non-Engine Refactor Phase 3 — Vite Cache Boundaries and Chart Presentation Lifecycle

## Authority, boundary, and baseline

- Target branch: `refactor`; previous accepted Phase 2 head: `7bd127c06010c991f5a24c013afd7b4ab4707c9b`.
- Upstream baseline: `main@afb586b69ecd6e12bcef30e2dbc4163e764dfcdb`.
- Explicit user constraint: **all files in `engine/` are immutable**, including Source, tests, Algorithm References and archives.
- This phase is **outside** trading semantics: no Bullish/Bearish geometry, Engine subprocess specification, RAW evidence, price chronology, direction, calculation-cache key format, or serialized Engine result was intentionally changed.
- Root `AGENTS.md` and maintained `engineering/docs/development/{zero-difference-refactor,testing}.md` guide regression/ownership. The supplied local `engine.zip` is a historical V5.4.32 copy; the live GitHub branch is current authority, and no historical Engine copy was edited.

## Completed code changes

### 1. Vite cache-clear API modularization

- New `apps/chart/server/local-cache-clear.js` owns the `/api/reactions/cache` request handler and file-count helpers, previously declared directly in `vite.config.js`.
- The server still supplies its original chart-owned cache directories, local-state paths and `cacheSegment` sanitization callback.
- Preserved: HTTP method validation; query scope/layer parsing; safe symbol path containment; calculation JSON counting excluding `.info.json`; drawing file counting excluding `.gitkeep`; removal scopes; error text; public JSON body shape; and the prohibition on clearing FARAZ session secrets for a symbol.
- The deletion logic itself was moved without changing its behaviors; no broad cleanup or user RAW deletion was performed.

### 2. Content-exact calculation Source fingerprint

- New `apps/chart/server/calculation-source-fingerprint.js` isolates the ordered, content-derived SHA-256 composition.
- The original algorithm (per ordered source: **basename + NUL byte + binary SHA-256 of full file content**, then outer SHA-256) is preserved byte-for-byte.
- The input list and ordering remain in `vite.config.js`; no change to cache keys or source-fingerprint API output is intended.
- No mtime-only or size-only memoization was introduced: same-size edits with restored timestamps still change the digest.

### 3. Chart-only candle aggregation extraction

- New `apps/chart/src/chart/candle-aggregation.js` owns the existing presentation `aggregate(rows, seconds)` implementation formerly local to `src/main.js`.
- Chart `main.js` imports the function; bucket rounding, first open, max high, min low, last close, numeric conversion and source-timeframe identity behavior were preserved.
- This function is for the **visual chart only**; it is not a second Bullish/Bearish trading engine.

### 4. Background UI timer reduction

- New `apps/chart/src/features/visible-clock.js` owns the workstation display clock's interval lifecycle.
- The visible tab retains its one-second update interval; hidden tabs do not keep the timer running, and visibility restoration renders the clock immediately.
- The previous unconditional global interval was removed from `src/main.js`. This **intentionally changes hidden-tab timer behavior only**; it is not a pure zero-difference transformation in that narrow implementation sense.
- This does not pause data acquisition, Engine calculations, SSE progress handling, or user-visible timers associated with a running operation.

## Tests added

- `apps/chart/tests/unit/vite-local-cache-contract.test.mjs`: stable public Source identity, method guard, calculation and drawing counts, symbol isolation, secret preservation.
- `apps/chart/tests/unit/calculation-source-fingerprint.test.mjs`: exact digest composition and content drift with restored timestamps.
- `apps/chart/tests/unit/candle-aggregation.test.mjs`: OHLC bucket output, chronology, non-mutation, numeric-string behavior and identity.
- `apps/chart/tests/unit/visible-clock.test.mjs`: initial visible tick, one active timer, hidden tab no work, safe restart, disposal.
- `apps/chart/tests/e2e/chart-startup-smoke.mjs`: launches the real Vite dev server and installed Chrome/Chromium, verifies Chart entrypoint initializes without uncaught JS page errors, hides the tab to confirm the displayed clock does not update, and shows the tab to confirm immediate update. Runs on both supported CI OSes.
- Existing `.github/workflows/chart-refactor.yml` now requires the browser smoke in **both Windows and Ubuntu** jobs as well as the original Chart unit/API tests, hot-path benchmark, production build and strict before/after Engine filesystem SHA-256 guard.

## Regression evidence and execution

**Original source before phase-3 production changes:** [GitHub Actions 41406883766](https://github.com/suwjee/TradingBot/actions/runs/41406883766) passed the newly introduced Vite source/cache baseline tests: 270 total tests (Windows 270 passed; Ubuntu 265 passed and 5 platform-specific skipped).

**Final candidate after all source and cross-platform smoke changes:** [GitHub Actions 41408240378](https://github.com/suwjee/TradingBot/actions/runs/41408240378), commit `13be2b12637bd0e7dbc0d9eac7aa11214dbf5ed9`, successfully completed.

| Gate | Ubuntu | Windows |
| --- | --- | --- |
| Chart unit and API test suite | PASS — 280 total, 275 passed, 5 platform skips, 0 failed | PASS — 280/280 passed, 0 failed |
| Real Chrome/Chromium Vite startup and clock visibility E2E | PASS | PASS |
| Chart Vite production build | PASS | PASS |
| Synthetic non-Engine hot-path benchmark execution | PASS | PASS |
| Branch-relative `engine/` file diff gate | PASS | PASS |
| All Engine files SHA-256 identical before/after execution | PASS | PASS |

**Anti-drift:** The phase-3 candidate is also subject to the existing repository anti-drift workflow; inspect the latest run for each commit. Full source-level branch compare showed **zero file changes beneath `engine/`**.

## Evidence limits and performance claims

- The Clock improvement is verified by an absence of scheduled interval work during simulated hidden visibility (unit + real browser), **not** by an independently measured systemwide CPU/RAM reduction on a user's workstation.
- The Vite and OHLC changes are ownership-preserving structural refactors, **not** claims of measured cache speed improvement or graphical frame-rate improvement.
- Existing synthetic benchmark results in this phase run, but the benchmark covers the earlier Phase 2 RAW/FIFO paths; it is **not** a before/after performance test of Vite routing or `main.js` viewport rendering.
- **NOT RUN**: real FARAZ login to external service, real broker RAW-based end-to-end trading correctness, long-running UI memory profiling, every Chart drawing/indicator interaction, Windows workstation profiling over a market session.
- Phase 3 finishes its specified **Vite cache boundary / source identity / presentation aggregation / clock lifecycle** change set, not all possible refactors of the ~7K-line Chart entrypoint or every service API. Future chunks require their own baselines and strict regression gates.

## Changed paths in this phase

- `apps/chart/server/calculation-source-fingerprint.js` (new).
- `apps/chart/server/local-cache-clear.js` (new).
- `apps/chart/vite.config.js` (small extraction and delegating import).
- `apps/chart/src/chart/candle-aggregation.js` (new).
- `apps/chart/src/features/visible-clock.js` (new).
- `apps/chart/src/main.js` (import extracted aggregation and visibility-aware clock).
- `apps/chart/tests/unit/calculation-source-fingerprint.test.mjs` (new).
- `apps/chart/tests/unit/candle-aggregation.test.mjs` (new).
- `apps/chart/tests/unit/visible-clock.test.mjs` (new).
- `apps/chart/tests/unit/vite-local-cache-contract.test.mjs` (new).
- `apps/chart/tests/e2e/chart-startup-smoke.mjs` (new).
- `.github/workflows/chart-refactor.yml` (cross-platform browser CI).
- This phase evidence report.

The maintained architecture document describes the same ownership boundaries, and its §20 explicitly discourages changing it merely for an internal Cache implementation extraction; therefore the architecture text was not churned.

No merge, production push, tag, release or publication was requested or performed. Work remains exclusively on `refactor`.
