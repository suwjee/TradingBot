# GRAPH_REPORT.md

**created_at:** `2026-09-30T15:43:03+03:30`
**last_modified_at:** `2026-09-30T15:43:03+03:30`
**repository:** TradingBot
**analysis:** live repository rebuild (not derived from prior graph snapshots)

## 1. Repository overview

| Metric | Value |
| --- | --- |
| Files scanned | 544 |
| Directories | 92 |
| Graph nodes | 662 |
| Graph edges | 2038 |
| Subsystems | 26 |

Top-level anchors: `engine/`, `apps/chart/`, `engineering/`, `scripts/`.

## 2. Architecture map

```text
[Documentation / AGENTS.md]
        | governance
        v
[Engine pipeline + bridge]  --->  [Vite local server / transport]  --->  [Chart UI]
        |                                 |                              |
        v                                 v                              v
[Algorithm References]            [FARAZ acquisition]            [LocalState / RAW]
        |
        v
[Engine tests / regression / benchmarks]
```

Ownership boundaries (from AGENTS.md and live source):

- Engine owns authoritative trading calculation (`engine/pipeline`, `engine/bridge`).
- Chart owns visualization/UI (`apps/chart/src`).
- Vite/server owns local API and orchestration (`apps/chart/vite.config.js`, `apps/chart/server`).
- FARAZ owns external market-data acquisition (`faraz-*` modules).
- Documentation is entry-pointed by `engineering/docs/README.md`.

## 3. Engine analysis

Production Engine modules (maintained):

- `engine/bridge/__init__.py`
- `engine/bridge/trading_pipeline.py`
- `engine/pipeline/__init__.py`
- `engine/pipeline/a_zone_detector.py`
- `engine/pipeline/blue_line_detector.py`
- `engine/pipeline/core_utils.py`
- `engine/pipeline/direction_policy.py`
- `engine/pipeline/e_zone_detector.py`
- `engine/pipeline/lifecycle_engine.py`
- `engine/pipeline/order_audit_engine.py`
- `engine/pipeline/reaction_engine.py`
- `engine/pipeline/s_zone_detector.py`

Algorithm authority documents:

- `engine/algorithms/TradingBot_Bearish_Algorithm_Reference_V5.4.21_Source_Synchronized.md`
- `engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V5.4.21_Source_Synchronized.md`

Engine test surfaces:

- `engine/tests/unit/test_order_audit_lifecycle_contracts.py`
- `engine/tests/unit/test_order_b_reset_leg.py`

Import hot path (verified from Source imports): `trading_pipeline` / detectors / lifecycle / order audit share `core_utils`, `direction_policy`, and `order_audit_engine` identities.

## 4. Chart / FARAZ / Vite analysis

Chart source cluster under `apps/chart/src` (main entry `src/main.js`).
Vite boundary: `apps/chart/vite.config.js` wires `server/faraz-candle-api.js`, `chart-transfer.js`, `indicator-range-input.js`, `raw-resource-store.js`, `candle-file-response.js`, `local-state-paths.js`.
FARAZ ownership files: `server/faraz-candle-api.js`, `src/features/faraz-symbol.js`, related export/update features.

## 5. Test architecture

Chart unit tests: `apps/chart/tests/unit/*.test.mjs` (Node test runner).
Engine unit tests: `engine/tests/unit/`.
Regression: `engine/tests/regression/` (hpzr2, order regression, compare).
Benchmarks: `engine/tests/benchmarks/`.
Verification helpers: `engine/tests/verification/`.

Test→source edges extracted from imports. Uncovered maintained sources are listed under analysis.uncovered_production_sources in `graph.json`.

## 6. Documentation architecture

Maintained documentation entry: `engineering/docs/README.md`.
Governance: `AGENTS.md`, `engineering/docs/documentation-governance.md`.
Architecture / development / operations / verification docs are linked from the docs index.

Broken documentation references found: 4.

## 7. Dependency hotspots

Highest relationship-count maintained files:

| Path | Relationships | Subsystem |
| --- | ---: | --- |
| `apps/chart/server/raw-resource-store.js` | 35 | ViteServer |
| `apps/chart/src/main.js` | 33 | Chart |
| `engineering/docs/architecture/technical-architecture.md` | 24 | Documentation |
| `engineering/docs/architecture/ui-ux-reference.md` | 23 | Documentation |
| `engineering/docs/documentation-governance.md` | 23 | Documentation |
| `apps/chart/tests/unit/raw-resource-store.test.mjs` | 22 | ChartTests |
| `engineering/docs/ai/engineering-workflow.md` | 19 | Documentation |
| `engineering/docs/development/testing.md` | 19 | Documentation |
| `AGENTS.md` | 18 | Governance |
| `engine/tests/unit/test_order_audit_lifecycle_contracts.py` | 17 | EngineUnitTests |
| `engineering/docs/development/zero-difference-refactor.md` | 17 | Documentation |
| `engineering/docs/README.md` | 17 | Documentation |
| `engine/bridge/trading_pipeline.py` | 16 | EngineBridge |
| `engine/pipeline/order_audit_engine.py` | 16 | EnginePipeline |
| `engine/tests/regression/order_regression.py` | 15 | EngineRegression |
| `engine/pipeline/e_zone_detector.py` | 13 | EnginePipeline |
| `engine/pipeline/lifecycle_engine.py` | 13 | EnginePipeline |
| `engine/tests/benchmarks/bench.py` | 13 | EngineBenchmarks |
| `apps/chart/src/algorithm/page.js` | 12 | Chart-AlgorithmUI |
| `engine/tests/unit/test_order_b_reset_leg.py` | 12 | EngineUnitTests |
| `engineering/docs/development/algorithm-reference-maintenance.md` | 12 | Documentation |
| `engineering/docs/operations/local-state.md` | 12 | Documentation |
| `engine/pipeline/s_zone_detector.py` | 11 | EnginePipeline |
| `engine/pipeline/direction_policy.py` | 10 | EnginePipeline |
| `engine/pipeline/reaction_engine.py` | 10 | EnginePipeline |

## 8. Important files

Critical / high-importance nodes:

- `AGENTS.md` (critical, Governance)
- `apps/chart/package.json` (high, Chart)
- `apps/chart/server/candle-file-response.js` (high, ViteServer)
- `apps/chart/server/chart-transfer.js` (high, ViteServer)
- `apps/chart/server/faraz-candle-api.js` (high, ViteServer)
- `apps/chart/server/indicator-range-input.js` (high, ViteServer)
- `apps/chart/server/local-state-paths.js` (high, ViteServer)
- `apps/chart/server/migrate-raw-resources.js` (high, ViteServer)
- `apps/chart/server/raw-integrity.js` (high, ViteServer)
- `apps/chart/server/raw-resource-store.js` (high, ViteServer)
- `apps/chart/src/chart/drawing-coordinates.js` (high, Chart)
- `apps/chart/src/chart/indicator-range.js` (high, Chart)
- `apps/chart/src/chart/view-transform.js` (high, Chart)
- `apps/chart/src/chart/zoom-config.js` (high, Chart)
- `apps/chart/src/drawings/drawing-math.js` (high, Chart)
- `apps/chart/src/features/candle-export.js` (high, Chart)
- `apps/chart/src/features/candle-update.js` (high, Chart)
- `apps/chart/src/features/faraz-symbol.js` (high, Chart)
- `apps/chart/src/features/indicator-cache.js` (high, Chart)
- `apps/chart/src/features/indicator-calculation-request.js` (high, Chart)
- `apps/chart/src/features/indicator-lifecycle.js` (high, Chart)
- `apps/chart/src/features/manual-review/render.js` (high, Chart)
- `apps/chart/src/features/raw-file-contract.js` (high, Chart)
- `apps/chart/src/features/raw-inventory.js` (high, Chart)
- `apps/chart/src/features/screenshot-overlay.js` (high, Chart)
- `apps/chart/src/features/workspace-session.js` (high, Chart)
- `apps/chart/src/main.js` (critical, Chart)
- `apps/chart/src/ui/chart-identity.js` (high, Chart)
- `apps/chart/src/ui/feedback.js` (high, Chart)
- `apps/chart/src/ui/log-window.js` (high, Chart)
- `apps/chart/src/ui/popover.js` (high, Chart)
- `apps/chart/src/ui/symbol-format.js` (high, Chart)
- `apps/chart/src/ui/workspace-state.js` (high, Chart)
- `apps/chart/vite.config.js` (critical, Vite)
- `engine/algorithms/TradingBot_Bearish_Algorithm_Reference_V5.4.21_Source_Synchronized.md` (high, AlgorithmReferences)
- `engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V5.4.21_Source_Synchronized.md` (high, AlgorithmReferences)
- `engine/bridge/__init__.py` (critical, EngineBridge)
- `engine/bridge/trading_pipeline.py` (critical, EngineBridge)
- `engine/pipeline/__init__.py` (critical, EnginePipeline)
- `engine/pipeline/a_zone_detector.py` (critical, EnginePipeline)
- `engine/pipeline/blue_line_detector.py` (critical, EnginePipeline)
- `engine/pipeline/core_utils.py` (critical, EnginePipeline)
- `engine/pipeline/direction_policy.py` (critical, EnginePipeline)
- `engine/pipeline/e_zone_detector.py` (critical, EnginePipeline)
- `engine/pipeline/lifecycle_engine.py` (critical, EnginePipeline)
- `engine/pipeline/order_audit_engine.py` (critical, EnginePipeline)
- `engine/pipeline/reaction_engine.py` (critical, EnginePipeline)
- `engine/pipeline/s_zone_detector.py` (critical, EnginePipeline)
- `engineering/docs/ai/engineering-workflow.md` (high, Documentation)
- `engineering/docs/architecture/technical-architecture.md` (high, Documentation)
- `engineering/docs/architecture/ui-ux-reference.md` (high, Documentation)
- `engineering/docs/development/algorithm-reference-maintenance.md` (high, Documentation)
- `engineering/docs/development/testing.md` (high, Documentation)
- `engineering/docs/development/zero-difference-refactor.md` (high, Documentation)
- `engineering/docs/documentation-governance.md` (high, Documentation)
- `engineering/docs/operations/local-state.md` (high, Documentation)
- `engineering/docs/README.md` (high, Documentation)
- `engineering/docs/verification/repository-integrity.md` (high, Documentation)
- `README.md` (critical, Governance)

## 9. High impact areas

Change-impact edges are derived from reverse imports/tests. Editing a shared module (`core_utils.py`, `order_audit_engine.py`, `raw-file-contract.js`, `candle-update.js`, `vite.config.js`) affects multiple subsystems.

## 10. Duplicate authority risks

Basename duplicates across subsystems/archives: 39.
Identical content groups: 8.

These are **report-only** relationships. Nothing was deleted. Archive copies and live sources must not be treated as equal authority.

## 11. Missing relationships

- Production sources without extracted test links: 28
- Orphan tests (no extracted target): 9
- Orphan maintained files (no non-ownership edges): 23

## 12. Recommended future improvements

1. Keep test import style explicit (relative imports already good for chart).
2. Document Engine runner `sys.path` conventions near `engine/tests`.
3. When adding new Engine modules, add them to `engine/pipeline/__init__.py` exports if they are public.
4. Re-run this analysis after large moves; classification is path-rule based and will pick up new files automatically.
5. Do not treat `engineering/archive/**` or prior `repository-graphify/**` outputs as current authority.

## Algorithm trace graph

```text
engine/algorithms/*_Algorithm_Reference_*.md
        | documented semantics (authority: intended trading rules)
        v
engine/pipeline/*.py + engine/bridge/trading_pipeline.py
        | executable behavior
        v
engine/tests/unit + regression + verification + benchmarks
        | evidence
        v
engineering/archive/** regression snapshots (historical)
```

Missing / weak links observed:

- Algorithm references are Markdown and are not symbol-linked to specific Python functions; the graph records cluster-level INFERRED documentation edges from each Algorithm Reference to Engine production modules.
- No dedicated unit test file names map 1:1 onto `blue_line_detector.py` / `a_zone_detector.py` / `s_zone_detector.py` / `reaction_engine.py`; order/lifecycle coverage is concentrated in `test_order_audit_lifecycle_contracts.py` and `test_order_b_reset_leg.py`.
- Chart algorithm UI content under `apps/chart/src/algorithm/content/` is presentation/reference UI and is not Engine authority.

## Durable design

Node identity is repository-relative path. Ownership/lifecycle/importance are rule-classified from live paths and AGENTS.md boundaries. Graph identity does not depend on commit hashes, file counts, or version numbers, so new engine files, plugins, and tests are included on the next live rebuild.

---
Generated by `engineering/archive/repository-graphify/cache/build_graphify.py`.
