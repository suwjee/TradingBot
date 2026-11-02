---
title: Non-Engine Refactor Phase 5 — Drawing Stroke Projection and Object Tree Rendering
document_role: evidence
lifecycle: historical
owner: chart-presentation
created_at: 2026-11-02T08:47:02.181+00:00
last_modified_at: 2026-11-02T08:47:02.181+00:00
---

# Non-Engine Refactor Phase 5 — Drawing Stroke Projection and Object Tree Rendering

## Scope and authority

- Target branch: **`refactor`** in `suwjee/TradingBot`.
- Previous phase-4 source baseline: `62b90ad9158b1918ec55bf675d71be53359951d6`.
- Current project authorities reviewed: root `AGENTS.md`, `GPT_bot/AGENTS.md`, `GPT_bot/TradingBot_AI_Operating_Protocol.md`, maintained development/testing/UI reference documents, current `apps/chart/src/main.js` and its Chart dependencies, current V5.4.33 Bullish/Bearish Algorithm References (read-only).
- Historical provided `engine.zip` was enumerated/read without changes (14 files, V5.4.32 references); current GitHub `engine/` is authoritative, and the user has prohibited **all modifications to it**.
- Neither Bullish/Bearish Engine Source, accepted References, RAW evidence, market chronology, calculation identity, pricing semantics, nor public APIs were changed.
- This is a **bounded Chart UI rendering and memory-allocation refactor**; it does not claim complete refactoring of every Drawing tool or all of `main.js`.

## Completed production changes

### A. Brush/path point projection: one pass, no intermediate arrays

`apps/chart/src/drawings/stroke-projection.js` implements `collectProjectedStrokePoints(drawing, project, valid)`.

The former `drawOne()` branch in `apps/chart/src/main.js` built `(d.points || []).map(xy).filter(valid)` on every redraw. It now projects and accepts points in **one indexed pass**. The Canvas polyline no longer allocates `pts.slice(1)` to draw subsequent line segments; it iterates the existing projected list. The selected, unlocked Path handles likewise iterate the same list without calling `forEach` on a newly created view.

Preserved contracts:
- strictly original point order;
- original `xy` and `valid` predicates, including invalid point logs;
- sparse-array `Array#map` semantics (skips absent slots but reads inherited positions);
- optional Path preview appended last and never appended to Brush;
- no drawing when no valid points;
- stroke style, line dash, canvas API call sequence, selected Path handles and locked state.

The result still builds one output point array because selection handles and Canvas drawing need the ordered projected list; it does **not** claim all per-stroke allocations were eliminated.

### B. Object Tree label and multi-selection ownership

`apps/chart/src/main.js` now shares one frozen, immutable Drawing-type label map across `renderObjectTree()` calls instead of constructing a new object on every render.

Within each render, a **transient Set** of selected Object Tree IDs replaces repeated `state.treeSelectedIds.includes(id)` scans as rows are serialized. The Set does not persist between renders, does not affect stored selection state, and follows the same SameValueZero comparison as `Array#includes`.

### C. One-pass Indicator Object Tree direction grouping

`apps/chart/src/chart/object-tree-groups.js` adds `groupIndicatorRowsForTree(objects, query)`. Instead of building the visible Indicator list and then independently filtering that list once for Bullish and again for Bearish, it produces the visible row list and both direction buckets in a single pass.

Preserved contracts:
- original case-normalized `name + type` search predicate;
- original directional ID test using `:bullish:` and `:bearish:`;
- exact source order in each direction bucket;
- a row matching both direction tokens still appears in both;
- unknown/non-directional rows count as visible but do not acquire an invented direction;
- sparse arrays skip missing slots as the historical `Array#filter` did.

These groups are presentation-only; Bullish/Bearish calculation rules, directional mirrors and accepted output remain entirely Engine-owned.

## Tests, benchmarks, and CI

Before wiring new Stroke projection into `main.js`, the new helper was tested and a microbenchmark was captured using the **legacy implementation and candidate on the same runners**.

Added/extended tests:
- `apps/chart/tests/unit/stroke-projection.test.mjs`: old/new equivalent point outputs, invalid-point filtering, source callback index/order, sparse arrays, preview rules, selected Path handles, source immutability.
- `apps/chart/tests/unit/object-tree-groups.test.mjs`: exact previous per-direction filters, unusual dual-direction IDs, query behavior, selected Set membership, sparse indicator arrays.
- `apps/chart/tests/e2e/chart-startup-smoke.mjs`: existing real Vite + Chrome/Chromium integration extended to load stored synthetic Brush and Path strokes alongside other drawings; verify visible Object Tree rows/search and run **30 Object Tree open/close cycles** without duplicate DOM rows or uncaught JS errors.
- `apps/chart/tests/benchmarks/stroke-projection.mjs`: old/new 50,000-point projection, 9 same-job samples.
- `apps/chart/tests/benchmarks/object-tree-index.mjs`: old/new 30,000-indicator grouping plus 8,000 row-selection candidates and 800 selected IDs, 7 same-job samples.
- `.github/workflows/chart-refactor.yml`: runs the new Stroke benchmark alongside the existing tests/build, browser smoke, previous synthetic benchmarks, and strict Engine SHA-256 firewall.

**Final complete source candidate:** [GitHub Actions run 41415205943](https://github.com/suwjee/TradingBot/actions/runs/41415205943), before adding this documentation-only report.

| Verification gate | Ubuntu | Windows |
| --- | --- | --- |
| Node Chart/API unit tests | **PASS** (292 total: 287 passed, 5 platform skips, 0 failures) | **PASS** (292 passed, 0 skipped/failed) |
| Real Chrome/Chromium Chart/browser smoke | **PASS** | **PASS** |
| Object Tree + Indicator/selection microbenchmarks | **PASS** | **PASS** |
| Brush/Path projection microbenchmarks | **PASS** | **PASS** |
| Production Vite build | **PASS** | **PASS** |
| Branch-relative tracked `engine/` diff guard | **PASS** | **PASS** |
| All `engine/` file SHA-256 before/after CI run | **PASS** | **PASS** |
| Anti-drift | **PASS** | **PASS** |

## Performance: measured, not inferred

Measurements are **same-run runner-local medians**; each method was timed on the same GitHub-hosted Node 22 runner within a job, on synthetic UI data. Time is in milliseconds; lower is faster.

| Synthetic presentation operation | Ubuntu old | Ubuntu refactor | Windows old | Windows refactor |
| --- | ---: | ---: | ---: | ---: |
| 50,000-point Path projection (9 samples) | 3.005 | 2.002 | 2.836 | 1.712 |
| 30,000 Indicator Object Tree direction grouping (7 samples) | 5.467 | 4.285 | 6.928 | 5.530 |
| Membership check for 8,000 rows / 800 selected IDs (7 samples) | 10.164 | 0.590 | 9.084 | 0.494 |

Benchmark source and full samples are in the above CI job logs. The original grouping/selection results are timed as the **original algorithm in the same final job**, not a historical result collected from a differently provisioned runner.

**NOT MEASURED:** overall Chart frame rate/FPS, actual Chrome heap/GC reduction, native user workstation CPU/RAM load, drawing strokes at millions of points, real-market Engine calculations, live FARAZ integration. These microbenchmarks are evidence for scoped hot-path costs, not global application speedups or memory stability guarantees.

## Why no aggressive DOM virtualization or persistent cache was added

Virtualization would change material Object Tree focus, drag/drop, keyboard navigation, accessibility, selection, and visible DOM behavior unless separately specified and integration-tested. Persistent geometry/indicator presentation caches could become stale after scale/viewport/setting changes. Both were deliberately excluded rather than changing stable behavior under a refactor-only label.

## Changed files relative to Phase 4

- `apps/chart/src/drawings/stroke-projection.js` (new).
- `apps/chart/src/chart/object-tree-groups.js` (indicator grouping).
- `apps/chart/src/main.js` (new helpers, shared labels, Set membership, stroke loops).
- `apps/chart/tests/unit/stroke-projection.test.mjs` (new).
- `apps/chart/tests/unit/object-tree-groups.test.mjs` (extended).
- `apps/chart/tests/e2e/chart-startup-smoke.mjs` (Brush/Path and repeated panel lifecycles).
- `apps/chart/tests/benchmarks/stroke-projection.mjs` (new).
- `apps/chart/tests/benchmarks/object-tree-index.mjs` (extended).
- `.github/workflows/chart-refactor.yml` (Stroke benchmark step).
- This report.

## Final limitations and next candidate phase

This Phase 5 scope is complete with PASS on unit, browser, build, performance harness and Engine-immutability checks. This does **not** demonstrate complete refactoring of all Chart modules or full UI memory leak absence.

Possible next phase: measure long-session Chart heap allocation with actual Chrome tracing and representative large RAW charts, then selectively optimize Indicator overlay projection/hitbox generation and toolbar behavior under real-window interaction; retain current Engine immutability and source/Reference authority boundaries.

No `main` or `production` branch change, merge, PR, tag, release or deployment was performed.
