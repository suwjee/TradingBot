---
title: Non-Engine Refactor Phase 8 — Object Tree Multi-Selection Work
document_role: evidence
lifecycle: historical
owner: chart-presentation
created_at: 2026-11-02T10:30:13.030+00:00
last_modified_at: 2026-11-02T10:30:13.030+00:00
---

# Non-Engine Refactor Phase 8 — Object Tree Multi-Selection

## Baseline and evidence scope

- Target: `refactor`, `suwjee/TradingBot`.
- Starting live branch: `49b645e35f1ffb0869ebab063f8e7bdad5e60d08`; current main `afb586b69ecd6e12bcef30e2dbc4163e764dfcdb`.
- At startup, the live branch had advanced since the prior conversation's phase-six result. Its already-existing `apps/chart/src/chart/indicator-order-keys.js` implementation and real Engine-overlay browser CI were inspected; no parallel changes were overwritten.
- Grounding: live root `AGENTS.md`, `GPT_bot/AGENTS.md`, `GPT_bot/TradingBot_AI_Operating_Protocol.md`, maintained Zero Difference Refactor procedures, current `apps/chart/src/main.js`, current tests/CI, current V5.4.33 reference context read-only.
- User restriction: **zero changes in `engine/`**, immutable RAW, preserved `main`/production. This phase is purely Chart user selection; it changes no Engine calculation semantics, directional logic, RAW processing or Indicator geometry.

## Actual change

The Object Tree `selectTreeObject(id, append)` handler in `apps/chart/src/main.js` previously checked every selected ID against **every drawing** using a nested `state.drawings.some(...)` search. With thousands of Drawing objects and a large multi-selection this repeatedly scans the same array.

A new pure, transient helper `apps/chart/src/chart/object-tree-selection.js` exports `partitionObjectTreeSelection(selectedIds,drawings,indicatorMap)`:

- Build a temporary `Set` of drawing IDs once per selection action.
- Filter the original selected IDs against the Set for manual objects, and against the existing Indicator `Map` for Indicator objects.
- Preserve original selection list order, duplicates, manual/indicator dual membership, missing IDs and fallback semantics.
- Do not persist, cache across sessions, mutate drawing objects, change Indicator object maps or alter UI selection precedence.

The production handler now delegates its two previous filters to the helper; surrounding selection, toolbar, DOM, redraw and gesture logic remains unchanged.

## Tests and benchmarks

Added `apps/chart/tests/unit/object-tree-selection.test.mjs` with independent legacy-oracle equality cases covering alternating manual/Indicator selection, duplicate IDs, both maps owning an ID, unknown IDs and changing drawing entries. Added a real Chrome/Chromium UI interaction to `apps/chart/tests/e2e/chart-startup-smoke.mjs` that selects a drawing, Shift-clicks a second drawing, verifies both selected rows, Shift-clicks to remove one and verifies resulting DOM state.

Added `apps/chart/tests/benchmarks/object-tree-selection.mjs` and wired it to the cross-platform `.github/workflows/chart-refactor.yml` gate. It measures the original nested `some` logic against a temporary `Set` with exactly 20,000 synthetic Drawing IDs and 800 selected IDs, seven samples each, old/new on the same runner.

**Complete post-change CI:** [GitHub Actions 41428911307](https://github.com/suwjee/TradingBot/actions/runs/41428911307), SHA `2d4c9cc80be677f42b360714f8430a9cfef4cb56`, success on Ubuntu and Windows.

| Gate | Ubuntu | Windows |
| --- | --- | --- |
| Chart/API Node tests | **297 passed**, 5 platform skips, 0 failures | **302 passed**, 0 skipped/failed |
| Browser smoke with actual selection and redraw | PASS | PASS |
| Browser real Engine-overlay integration inherited from current workflow | PASS | PASS |
| Production build | PASS | PASS |
| Existing performance and memory profiling CI | PASS | PASS |
| Every `engine/` file SHA-256 before/after | PASS | PASS |
| Branch diff against main for `engine/` | Zero changed files | Zero changed files |

## Benchmark evidence, ms (lower is faster)

| Operation: 20k drawings / 800 selections | Ubuntu | Windows |
| --- | ---: | ---: |
| Original repeated `drawings.some` search | 57.977 | 71.500 |
| Transient Set partition | 2.067 | 2.329 |

Runner-local synthetic microbenchmarks establish a decrease in selection-partition CPU work. **They are not proof of a similar full browser FPS, Chrome heap or user workstation CPU/RAM reduction.** Actual Indicator Engine overlay correctness is covered only to the extent of the existing UI integration tests, not a complete independent all-RAW behavioral oracle.

## Files changed relative to task baseline

- `apps/chart/src/chart/object-tree-selection.js` (new)
- `apps/chart/src/main.js` (narrow call-site replacement)
- `apps/chart/tests/unit/object-tree-selection.test.mjs` (new)
- `apps/chart/tests/benchmarks/object-tree-selection.mjs` (new)
- `apps/chart/tests/e2e/chart-startup-smoke.mjs` (Shift-click selection regression)
- `.github/workflows/chart-refactor.yml` (benchmark verification)
- This evidence report

No `engine/`, immutable RAW, main or production edits. No release, merge, tag, PR or deployment performed. This is the *bounded* next presentation optimization, not a claim that every Overlay/Indicator renderer or the entire Chart workstation is refactored.
