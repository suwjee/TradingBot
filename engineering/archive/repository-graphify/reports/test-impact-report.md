# test-impact-report.md

**created_at:** `2026-09-30T15:43:03+03:30`
**last_modified_at:** `2026-09-30T15:43:03+03:30`

## Test surfaces

- `apps/chart/tests/unit/candle-export-log.test.mjs`
- `apps/chart/tests/unit/candle-file-response.test.mjs`
- `apps/chart/tests/unit/candle-update.test.mjs`
- `apps/chart/tests/unit/chart-transfer.test.mjs`
- `apps/chart/tests/unit/chart-update-contract.test.mjs`
- `apps/chart/tests/unit/drawing-coordinates.test.mjs`
- `apps/chart/tests/unit/drawing-tools.test.mjs`
- `apps/chart/tests/unit/faraz-candle-api.test.mjs`
- `apps/chart/tests/unit/faraz-symbol.test.mjs`
- `apps/chart/tests/unit/feedback.test.mjs`
- `apps/chart/tests/unit/indicator-cache.test.mjs`
- `apps/chart/tests/unit/indicator-calculation-request.test.mjs`
- `apps/chart/tests/unit/indicator-lifecycle.test.mjs`
- `apps/chart/tests/unit/indicator-range-input.test.mjs`
- `apps/chart/tests/unit/indicator-range.test.mjs`
- `apps/chart/tests/unit/local-state-paths.test.mjs`
- `apps/chart/tests/unit/manual-review.test.mjs`
- `apps/chart/tests/unit/popover.test.mjs`
- `apps/chart/tests/unit/raw-cut.test.mjs`
- `apps/chart/tests/unit/raw-file-contract.test.mjs`
- `apps/chart/tests/unit/raw-integrity.test.mjs`
- `apps/chart/tests/unit/raw-inventory.test.mjs`
- `apps/chart/tests/unit/raw-resource-store.test.mjs`
- `apps/chart/tests/unit/screenshot-overlay.test.mjs`
- `apps/chart/tests/unit/symbol-format.test.mjs`
- `apps/chart/tests/unit/view-transform.test.mjs`
- `apps/chart/tests/unit/vite-state-policy.test.mjs`
- `apps/chart/tests/unit/workspace-session.test.mjs`
- `apps/chart/tests/unit/workspace-state.test.mjs`
- `apps/chart/tests/unit/zoom-config.test.mjs`
- `engine/tests/unit/test_order_audit_lifecycle_contracts.py`
- `engine/tests/unit/test_order_b_reset_leg.py`

## Covered production sources (extracted import links)

- `apps/chart/server/candle-file-response.js` <- `apps/chart/tests/unit/candle-file-response.test.mjs`
- `apps/chart/server/chart-transfer.js` <- `apps/chart/tests/unit/chart-transfer.test.mjs`
- `apps/chart/server/faraz-candle-api.js` <- `apps/chart/tests/unit/faraz-candle-api.test.mjs`
- `apps/chart/server/indicator-range-input.js` <- `apps/chart/tests/unit/indicator-range-input.test.mjs`
- `apps/chart/server/local-state-paths.js` <- `apps/chart/tests/unit/local-state-paths.test.mjs`
- `apps/chart/server/migrate-raw-resources.js` <- `apps/chart/tests/unit/raw-resource-store.test.mjs`
- `apps/chart/server/raw-integrity.js` <- `apps/chart/tests/unit/raw-integrity.test.mjs`
- `apps/chart/server/raw-resource-store.js` <- `apps/chart/tests/unit/chart-transfer.test.mjs`, `apps/chart/tests/unit/raw-cut.test.mjs`, `apps/chart/tests/unit/raw-resource-store.test.mjs`
- `apps/chart/src/chart/drawing-coordinates.js` <- `apps/chart/tests/unit/drawing-coordinates.test.mjs`
- `apps/chart/src/chart/indicator-range.js` <- `apps/chart/tests/unit/indicator-range.test.mjs`
- `apps/chart/src/chart/view-transform.js` <- `apps/chart/tests/unit/view-transform.test.mjs`
- `apps/chart/src/chart/zoom-config.js` <- `apps/chart/tests/unit/zoom-config.test.mjs`
- `apps/chart/src/drawings/drawing-math.js` <- `apps/chart/tests/unit/drawing-tools.test.mjs`
- `apps/chart/src/features/candle-update.js` <- `apps/chart/tests/unit/candle-update.test.mjs`, `apps/chart/tests/unit/faraz-candle-api.test.mjs`
- `apps/chart/src/features/faraz-symbol.js` <- `apps/chart/tests/unit/faraz-symbol.test.mjs`
- `apps/chart/src/features/indicator-cache.js` <- `apps/chart/tests/unit/indicator-cache.test.mjs`
- `apps/chart/src/features/indicator-calculation-request.js` <- `apps/chart/tests/unit/indicator-calculation-request.test.mjs`
- `apps/chart/src/features/indicator-lifecycle.js` <- `apps/chart/tests/unit/indicator-lifecycle.test.mjs`
- `apps/chart/src/features/manual-review/render.js` <- `apps/chart/tests/unit/manual-review.test.mjs`
- `apps/chart/src/features/raw-file-contract.js` <- `apps/chart/tests/unit/raw-file-contract.test.mjs`
- `apps/chart/src/features/raw-inventory.js` <- `apps/chart/tests/unit/raw-inventory.test.mjs`
- `apps/chart/src/features/screenshot-overlay.js` <- `apps/chart/tests/unit/screenshot-overlay.test.mjs`
- `apps/chart/src/features/workspace-session.js` <- `apps/chart/tests/unit/workspace-session.test.mjs`
- `apps/chart/src/ui/chart-identity.js` <- `apps/chart/tests/unit/raw-inventory.test.mjs`
- `apps/chart/src/ui/feedback.js` <- `apps/chart/tests/unit/feedback.test.mjs`
- `apps/chart/src/ui/log-window.js` <- `apps/chart/tests/unit/candle-export-log.test.mjs`
- `apps/chart/src/ui/popover.js` <- `apps/chart/tests/unit/popover.test.mjs`
- `apps/chart/src/ui/symbol-format.js` <- `apps/chart/tests/unit/symbol-format.test.mjs`
- `apps/chart/src/ui/workspace-state.js` <- `apps/chart/tests/unit/workspace-state.test.mjs`
- `engine/pipeline/e_zone_detector.py` <- `engine/tests/unit/test_order_audit_lifecycle_contracts.py`, `engine/tests/unit/test_order_b_reset_leg.py`
- `engine/pipeline/lifecycle_engine.py` <- `engine/tests/unit/test_order_audit_lifecycle_contracts.py`, `engine/tests/unit/test_order_b_reset_leg.py`
- `engine/pipeline/order_audit_engine.py` <- `engine/tests/unit/test_order_audit_lifecycle_contracts.py`, `engine/tests/unit/test_order_b_reset_leg.py`
- `engine/pipeline/reaction_engine.py` <- `engine/tests/unit/test_order_audit_lifecycle_contracts.py`
- `engine/pipeline/s_zone_detector.py` <- `engine/tests/unit/test_order_audit_lifecycle_contracts.py`
- `engine/tests/verification/verify_order_b_raw.py` <- `engine/tests/regression/order_regression.py`

## Uncovered maintained sources (no extracted test import)

Count: 28

- `apps/chart/scripts/dev-server.mjs`
- `apps/chart/src/algorithm/content/bridge-content.js`
- `apps/chart/src/algorithm/content/calculation-guides.js`
- `apps/chart/src/algorithm/content/content.js`
- `apps/chart/src/algorithm/content/glossary.js`
- `apps/chart/src/algorithm/content/i18n.js`
- `apps/chart/src/algorithm/content/module-summaries.js`
- `apps/chart/src/algorithm/content/object-catalog.js`
- `apps/chart/src/algorithm/content/type-module-summaries.js`
- `apps/chart/src/algorithm/mirror.js`
- `apps/chart/src/algorithm/page.js`
- `apps/chart/src/chart/lod.js`
- `apps/chart/src/chart/progress.js`
- `apps/chart/src/chart/state.js`
- `apps/chart/src/features/candle-export.js`
- `apps/chart/src/features/manual-review/entry.js`
- `apps/chart/src/features/manual-review/tab.js`
- `apps/chart/src/main.js`
- `apps/chart/src/platform/browser-compat.js`
- `apps/chart/src/ui/icons.js`
- `apps/chart/vite.config.js`
- `engine/bridge/__init__.py`
- `engine/bridge/trading_pipeline.py`
- `engine/pipeline/__init__.py`
- `engine/pipeline/a_zone_detector.py`
- `engine/pipeline/blue_line_detector.py`
- `engine/pipeline/core_utils.py`
- `engine/pipeline/direction_policy.py`

## Orphan tests

Count: 9

- `apps/chart/tests/unit/chart-update-contract.test.mjs`
- `apps/chart/tests/unit/vite-state-policy.test.mjs`
- `engine/tests/benchmarks/bench.py`
- `engine/tests/benchmarks/generate_fixture.py`
- `engine/tests/regression/compare_order_regressions.py`
- `engine/tests/regression/hpzr2_regression.py`
- `engine/tests/regression/hpzr2_verify_saved.py`
- `engine/tests/verification/verify_order_b_raw.py`
- `engine/tests/verification/verify_order_references.py`

## Method

Test→source edges come from import statements in test files. This is structural mapping, not a test-quality judgment.

## Method notes (structural only)

- Chart unit tests use Node import/wait import of production modules; those links are EXTRACTED.
- Engine unit tests import pipeline modules via flat module names (runner sys.path); those links are EXTRACTED via a stable flat-name map.
- Regression / benchmark / verification tools under engine/tests/{regression,benchmarks,verification} often invoke the engine via subprocess, CLI, or fixture comparison rather than Python imports. They appear as structural orphans for import-based mapping but remain active test/verification surfaces. Examples: hpzr2_regression.py, order_regression.py, ench.py, erify_order_references.py.
- chart-update-contract.test.mjs and ite-state-policy.test.mjs assert contracts via filesystem/config inspection rather than direct module imports.

This report maps structure only. It does not judge test quality or assertion completeness.
