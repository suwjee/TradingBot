---
title: Non-Engine Refactor Phase 4 — Chart Viewport Events, Drawing Tree, Render Allocations
document_role: evidence
lifecycle: historical
owner: chart-presentation
created_at: 2026-11-02T08:06:42.652+00:00
last_modified_at: 2026-11-02T08:06:42.652+00:00
---

# Non-Engine Refactor Phase 4 — Chart Events, Drawing Tree and Redraws

## Scope, source authority and immutable Engine firewall

- Approved target: **`refactor`** branch of `suwjee/TradingBot`.
- Previous successful phase baseline: `ba20c97f914d80a279b8ff8e0caba735245266f6` (phase 3).
- Base main at task start: `afb586b69ecd6e12bcef30e2dbc4163e764dfcdb`.
- Source authority: the GitHub `refactor` branch, root `AGENTS.md`, maintained development/testing/UI-UX documents, current V5.4.33 Bullish and Bearish Algorithm References as **read-only** context, and production `apps/chart/src/main.js` and related Chart modules.
- Explicit user guard: no file in `engine/` may be modified, even for metadata, references, tests or temporary files. Engine sources and both references were not edited. Authoritative uploaded market RAW evidence was not edited.
- All changed code is browser-side presentation code; no Engine trading semantics, candle identity, prices, algorithm-stage ordering, raw file storage contract, serialized result, Cache identity or HTTP API was changed.

## Changes delivered

### Ordered Object Tree drawing groups

Owner: `apps/chart/src/chart/object-tree-groups.js`; call site: `renderObjectTree()` in `apps/chart/src/main.js`.

The previous implementation scanned **all** manual drawings once **per** folder using `state.drawings.filter(...)`. The new implementation builds a **transient Map from folder ID to ordered drawing references** in a single pass for each requested tree render, then renders each folder using that map.

The grouping operation preserves:
- `drawing.folderId || "manual-unfiled"` fallback;
- exact original case-normalized search matching of the display type label;
- global drawing order **within** each folder and per-folder row numbering;
- hidden/locked drawing presence in the tree and the original display code;
- duplicate folder IDs, unknown/orphan folder IDs and special IDs;
- existing HTML generation, row controls, selection, persistence, and data ownership.

The Map is **transient**, not a persistent cross-file, per-symbol or run-scoped trading cache.

### Viewport and pointer event ownership

Owner: `apps/chart/src/chart/viewport-events.js`; call sites: `main.js`.

The pre-existing viewport timeout/rAF scheduling and range/size/pointer listeners were extracted into:
- `createViewportScheduler`, preserving 140 ms default debounce, one queued frame, pointer-pan freeze and the existing `preserveRange: true` render call;
- `bindViewportEvents`, preserving registration order and the original logical range, time range, resize, pointermove, pointerdown, pointerup and pointercancel callback sequencing and 0/90/140 ms delays.

It also offers explicit optional unsubscribe/removal for future ownership-aware teardown, but **does not invoke any new teardown automatically**. No change to TradingView's state, displayed LOD selection, chart series or full/selected calculation input is intended.

### No per-frame filtered drawing array

The high-frequency `drawAll()` overlay pass now iterates `state.drawings` directly, skips hidden drawings and draws visible ones in existing source order. This removes the temporary `filter(...)` array allocation at each pointer-driven redraw. `drawOne` is a presentation-only draw operation and the selection predicate is unchanged.

## Tests and verification sequence

1. **Before touching production `main.js`**, created:
   - `apps/chart/tests/unit/object-tree-groups.test.mjs` — original filter equality, order/indices, hidden/orphan/duplicate/special folder IDs, search, reference ownership, no mutation.
   - `apps/chart/tests/unit/viewport-events.test.mjs` — exact debounce/cancel/frame/pan behavior, original event order, delays, passive event registration and optional disposer.
   - `apps/chart/tests/benchmarks/object-tree-index.mjs` — original repeated full scan vs one-pass grouping in the **same Node process**.
2. Ran the new tests, browser smoke and Vite build against the original `main.js`: **[phase 4 pre-refactor baseline](https://github.com/suwjee/TradingBot/actions/runs/41409496270)**, PASS on Ubuntu and Windows.
3. Wired the helpers into the production entrypoint and removed the repeated drawing filter allocation.
4. Expanded `apps/chart/tests/e2e/chart-startup-smoke.mjs` to create and later delete a **new isolated chart-owned synthetic State sandbox** with 900 generated 5s candles and 6 drawings; it verifies:
   - Vite/Chart startup with a real RAW inventory entry from a temporary fixture, with no real RAW modification;
   - clock visibility behavior from phase 3;
   - persisted Drawing Tree row identity and order;
   - exact display-name search for Line drawings;
   - real mouse pointer movement/down/up and resize without uncaught JavaScript errors.
5. Final post-refactor **[GitHub Actions run 41410264554](https://github.com/suwjee/TradingBot/actions/runs/41410264554)** PASSED on Ubuntu and Windows. The parallel anti-drift workflow passed.
6. Verified the full branch-relative Engine diff is empty. CI also SHA-256 checks **every file** in `engine/` before and after test/build on each runner.

### Final CI results

| Gate | Ubuntu | Windows |
| --- | --- | --- |
| Node Chart Unit/API suite | **PASS** (286 total, 281 passed, 5 platform skips, 0 failed) | **PASS** (286/286, 0 skipped/failed) |
| Real Chrome/Chromium browser smoke with synthetic RAW and drawings | **PASS** | **PASS** |
| Object Tree and render-iteration benchmark | **PASS** | **PASS** |
| Production Vite build | **PASS** | **PASS** |
| Engine branch-diff and pre/post SHA-256 immutable guard | **PASS** | **PASS** |
| Anti-drift GitHub workflow | **PASS** | **PASS** |

## Performance measurements, with careful interpretation

**Synthetic same-process comparison:** 30,000 manual drawings, 80 folders, seven runs; medians in ms (lower is faster). Both old and new implementations were timed **within one CI job** for each OS.

| Operation | Ubuntu original | Ubuntu new | Windows original | Windows new |
| --- | ---: | ---: | ---: | ---: |
| Building ordered Object Tree folder items | 25.283 | 0.869 | 33.160 | 1.831 |
| Traversing visible drawings, excluding canvas paint | 1.219 | 1.056 | 2.106 | 0.166 |

Performance is strongly workload/JIT/runner-dependent: the first metric reflects a complexity improvement from repeated per-folder O(drawings) scans to one traversal. The second includes potential JIT warm-up artifacts and does not establish a universal speedup. **Neither metric includes full DOM reconciliation, canvas painting, chart LOD rendering, actual broker RAW calculation, or workstation-wide CPU/RAM peaks.**

A prior original-main baseline before wiring the new index measured 33.098 ms vs 0.946 ms for the same grouping-only synthetic benchmark on Ubuntu, [run 41409496270](https://github.com/suwjee/TradingBot/actions/runs/41409496270). Those samples are corroborating but not exact paired-commit hardware-identical results.

## Evidence limitations and next isolated work

- **PASS:** bounded deterministic presentation tests, browser integration with synthetic candles/drawings, build/CI, Engine file protection.
- **NOT RUN:** authoritative market RAW-based end-to-end Bullish/Bearish algorithm correctness, interactive large-data user workstation FPS/CPU/RAM profiling, complete multi-chart lifetime/GC retention testing, full user drawing gesture inventory, real FARAZ login.
- This phase is a **bounded Chart UI refactor**. It does **not** represent complete decomposition of the entire `src/main.js`, nor elimination of every expensive redraw. Current Vite build may continue to warn about a large JavaScript bundle; the current UI/UX architecture and loading contract were not redesigned.
- Remaining candidate areas must be separately measured and verified: larger overlay rendering primitives, object-tree DOM incremental updates, complex drawing-tool gesture lifecycle, and long-session performance; do not change trading state or Engine.

## Changed paths relative to Phase 3

- `apps/chart/src/chart/object-tree-groups.js` (new).
- `apps/chart/src/chart/viewport-events.js` (new).
- `apps/chart/src/main.js` (narrow renderer/event wiring and allocation change).
- `apps/chart/tests/unit/object-tree-groups.test.mjs` (new).
- `apps/chart/tests/unit/viewport-events.test.mjs` (new).
- `apps/chart/tests/benchmarks/object-tree-index.mjs` (new).
- `apps/chart/tests/e2e/chart-startup-smoke.mjs` (isolated synthetic RAW + drawing/viewport checks).
- `.github/workflows/chart-refactor.yml` (same-process benchmark).
- This report.

No change or merge into `main` or `production`; no tag, release, deployment or algorithm-reference editing was performed.
