TradingBot single-root structural migration - 2026-09-29

REGRESSION VERIFIED: applicable structural migration checks.
Trading calculation evidence: BOUNDED_VALIDATION, not independent market correctness.

All project-owned physical contents are inside D:\My-Projects\TradingBot.
Three primary owners: apps/, engine/, engineering/.
scripts/ retains the public Windows/VMware startup contract.
Default local state: apps/chart/state/{data/raw,cache,secret,tmp}.
TRADINGBOT_LOCAL_STATE_ROOT may select that subtree or a descendant only.

Delivery source excludes RAW, saved caches, authentication, local tests,
dependencies, build output and historical evidence. The separate local test
ZIP restores tests beneath their owners. Existing machine state remains
preserved in the original checkout. Source package version remains 3.4.1;
Engine source/reference names and versions are unchanged.

Start from project root: .\scripts\launch.bat
Chart checks from apps/chart: npm.cmd ci; npm.cmd test; npm.cmd run build
Engine check from root:
python -B -m pytest -q -p no:cacheprovider -p no:benchmark engine/tests/unit

Baseline: chart 159/159, Python 21/21, build 55 modules, references 13 each.
Final: chart 164/164, Python 21/21, build 55 modules, references 13 each.
Runtime: 9 HTTP checks, five private/evidence routes denied with 403;
Chrome chart/review initialized, zero page errors; validation server stopped.
Selected full RAW: XAUUSD 14,140 rows and USOIL 30,935 rows, 30 seconds,
both directions, all stages and Bridge Output. Ordered output bytes equal
baseline after removing only top-level timings. Full-all-market regression
is NOT APPLICABLE to this storage/layout migration under the integrity policy.

1,408 initial files accounted for; 884 moves; source/RAW/evidence hashes match.
Authentication: native move and matching size verified; no baseline hash,
so independent authentication byte-hash equality is NOT_TESTED.
No authenticated FARAZ action; no independent trading-correctness claim.
Existing four Source/Reference narrative discrepancies remain unresolved.
No commit, push, staging, reset, clean, stash or Graphify execution occurred.

Full report: engineering/docs/verification/single-root-migration.md
Checkout evidence: engineering/verification/single-root-2026-09-29/
The evidence directory contains the full map/tree, initial recovery snapshot,
command logs, output comparison, change classification and package manifest.

Changed/moved executable or maintained files
Old path | New path | Version | Final modification datetime
.gitignore | .gitignore | not separately versioned | 2026-09-29T18:01:08+03:30
AGENTS.md | AGENTS.md | not separately versioned | 2026-09-29T18:21:42+03:30
README.md | README.md | not separately versioned | 2026-09-29T18:05:03+03:30
apps/chart/package.json | apps/chart/package.json | 3.4.1 | 2026-09-29T17:58:02+03:30
apps/chart/server/local-state-paths.js | apps/chart/server/local-state-paths.js | not separately versioned | 2026-09-29T17:59:31+03:30
tests/chart/unit/candle-export-log.test.mjs | apps/chart/tests/unit/candle-export-log.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/candle-file-response.test.mjs | apps/chart/tests/unit/candle-file-response.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/candle-update.test.mjs | apps/chart/tests/unit/candle-update.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/chart-transfer.test.mjs | apps/chart/tests/unit/chart-transfer.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/drawing-coordinates.test.mjs | apps/chart/tests/unit/drawing-coordinates.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/drawing-tools.test.mjs | apps/chart/tests/unit/drawing-tools.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/faraz-candle-api.test.mjs | apps/chart/tests/unit/faraz-candle-api.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/faraz-symbol.test.mjs | apps/chart/tests/unit/faraz-symbol.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/feedback.test.mjs | apps/chart/tests/unit/feedback.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/indicator-cache.test.mjs | apps/chart/tests/unit/indicator-cache.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/indicator-calculation-request.test.mjs | apps/chart/tests/unit/indicator-calculation-request.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/indicator-lifecycle.test.mjs | apps/chart/tests/unit/indicator-lifecycle.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/indicator-range-input.test.mjs | apps/chart/tests/unit/indicator-range-input.test.mjs | not separately versioned | 2026-09-29T18:02:14+03:30
tests/chart/unit/indicator-range.test.mjs | apps/chart/tests/unit/indicator-range.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/local-state-paths.test.mjs | apps/chart/tests/unit/local-state-paths.test.mjs | not separately versioned | 2026-09-29T17:58:31+03:30
tests/chart/unit/manual-review.test.mjs | apps/chart/tests/unit/manual-review.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/popover.test.mjs | apps/chart/tests/unit/popover.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/raw-cut.test.mjs | apps/chart/tests/unit/raw-cut.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/raw-file-contract.test.mjs | apps/chart/tests/unit/raw-file-contract.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/raw-integrity.test.mjs | apps/chart/tests/unit/raw-integrity.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/raw-inventory.test.mjs | apps/chart/tests/unit/raw-inventory.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/raw-resource-store.test.mjs | apps/chart/tests/unit/raw-resource-store.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/screenshot-overlay.test.mjs | apps/chart/tests/unit/screenshot-overlay.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/symbol-format.test.mjs | apps/chart/tests/unit/symbol-format.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/view-transform.test.mjs | apps/chart/tests/unit/view-transform.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
(new) | apps/chart/tests/unit/vite-state-policy.test.mjs | not separately versioned | 2026-09-29T18:19:36+03:30
tests/chart/unit/workspace-session.test.mjs | apps/chart/tests/unit/workspace-session.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/workspace-state.test.mjs | apps/chart/tests/unit/workspace-state.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
tests/chart/unit/zoom-config.test.mjs | apps/chart/tests/unit/zoom-config.test.mjs | not separately versioned | 2026-09-29T17:58:02+03:30
apps/chart/vite.config.js | apps/chart/vite.config.js | not separately versioned | 2026-09-29T18:19:37+03:30
tests/engine/regression/hpzr2_verify_saved.py | engine/tests/regression/hpzr2_verify_saved.py | not separately versioned | 2026-09-29T18:02:14+03:30
tests/engine/regression/order_regression.py | engine/tests/regression/order_regression.py | not separately versioned | 2026-09-29T17:58:02+03:30
tests/engine/helpers/verify_order_references.py | engine/tests/verification/verify_order_references.py | not separately versioned | 2026-09-29T17:58:02+03:30
(new) | engineering/docs/README.md | not separately versioned | 2026-09-29T18:05:03+03:30
docs/AI/AI_Operating_Protocol.md | engineering/docs/ai/operating-protocol.md | not separately versioned | 2026-09-29T18:05:03+03:30
docs/architecture/Project/Technical_Architecture.md | engineering/docs/architecture/technical-architecture.md | not separately versioned | 2026-09-29T18:05:03+03:30
docs/architecture/Frontend/UI_UX_Technical_Reference.md | engineering/docs/architecture/ui-ux-reference.md | not separately versioned | 2026-09-29T18:05:03+03:30
docs/development/Test_Rules/Local_Test_Workflow.md | engineering/docs/development/local-tests.md | not separately versioned | 2026-09-29T18:05:03+03:30
docs/development/General_Rules/Standalone_Reference_Specification.md | engineering/docs/development/standalone-reference-specification.md | not separately versioned | 2026-09-29T18:05:03+03:30
docs/development/Refactor_Rules/Zero_Difference_Refactor_Performance_Rules.md | engineering/docs/development/zero-difference-refactor.md | not separately versioned | 2026-09-29T18:05:03+03:30
docs/operations/Local_State.md | engineering/docs/operations/local-state.md | not separately versioned | 2026-09-29T18:05:03+03:30
docs/Project_Audit/Engineering_Audit_Workflow.md | engineering/docs/verification/engineering-audit-workflow.md | not separately versioned | 2026-09-29T18:37:33+03:30
docs/development/Test_Rules/Repository_Integrity.md | engineering/docs/verification/repository-integrity.md | not separately versioned | 2026-09-29T18:05:03+03:30
(new) | engineering/docs/verification/single-root-migration.md | not separately versioned | 2026-09-29T18:32:26+03:30
scripts/start.ps1 | scripts/start.ps1 | not separately versioned | 2026-09-29T18:16:26+03:30
