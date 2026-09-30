TradingBot repository cleanup source package
Classification: infrastructure/path/documentation cleanup; no algorithm/source byte change.
Baseline: 822c5ce1c1e7f464d2e08085fd6d991ee1d5d8ed; branch main; initial current working tree is authority.
Reference version before/after: 5.4.19-EX1 unchanged.
REGRESSION VERIFIED for applicable structural/local contract checks; full market/independent directional correctness NOT APPLICABLE to this cleanup.
Full staged whitespace check: inherited protected-file warnings preserved.
No commit, push or Graphify run. Tests, RAW, authentication and state are excluded.

Current package files (version before -> after; timestamp; purpose):
.editorconfig | unversioned -> unversioned | 2026-09-13 10:36:01 +0330 Asia/Tehran | retained/organized current project content
.gitattributes | unversioned -> unversioned | 2026-09-29 13:44:01 +0330 Asia/Tehran | storage/configuration/documentation update
.gitignore | unversioned -> unversioned | 2026-09-29 13:34:09 +0330 Asia/Tehran | storage/configuration/documentation update
AGENTS.md | unversioned -> unversioned | 2026-09-29 13:37:06 +0330 Asia/Tehran | storage/configuration/documentation update
README.md | unversioned -> unversioned | 2026-09-29 13:34:09 +0330 Asia/Tehran | storage/configuration/documentation update
apps/chart/index.html | unversioned -> unversioned | 2026-09-13 15:42:22 +0330 Asia/Tehran | retained/organized current project content
apps/chart/package-lock.json | 3.4.1 -> 3.4.1 | 2026-09-13 10:37:30 +0330 Asia/Tehran | retained/organized current project content
apps/chart/package.json | 3.4.1 -> 3.4.1 | 2026-09-29 13:29:58 +0330 Asia/Tehran | storage/configuration/documentation update
apps/chart/review.html | unversioned -> unversioned | 2026-09-13 16:40:45 +0330 Asia/Tehran | retained/organized current project content
apps/chart/scripts/dev-server.mjs | unversioned -> unversioned | 2026-09-13 10:36:01 +0330 Asia/Tehran | retained/organized current project content
apps/chart/server/candle-file-response.js | unversioned -> unversioned | 2026-09-22 15:11:36 +0330 Asia/Tehran | retained/organized current project content
apps/chart/server/chart-transfer.js | unversioned -> unversioned | 2026-09-20 01:02:15 +0330 Asia/Tehran | retained/organized current project content
apps/chart/server/faraz-candle-api.js | unversioned -> unversioned | 2026-09-29 13:26:05 +0330 Asia/Tehran | storage/configuration/documentation update
apps/chart/server/indicator-range-input.js | unversioned -> unversioned | 2026-09-21 03:04:57 +0330 Asia/Tehran | retained/organized current project content
apps/chart/server/local-state-paths.js | unversioned -> unversioned | 2026-09-29 13:26:05 +0330 Asia/Tehran | retained/organized current project content
apps/chart/server/migrate-raw-resources.js | unversioned -> unversioned | 2026-09-15 09:51:22 +0330 Asia/Tehran | retained/organized current project content
apps/chart/server/raw-integrity.js | unversioned -> unversioned | 2026-09-15 09:40:47 +0330 Asia/Tehran | retained/organized current project content
apps/chart/server/raw-resource-store.js | unversioned -> unversioned | 2026-09-22 15:12:45 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/content/bridge-content.js | unversioned -> unversioned | 2026-09-13 23:40:10 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/content/calculation-guides.js | unversioned -> unversioned | 2026-09-13 10:33:50 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/content/content.js | unversioned -> unversioned | 2026-09-13 23:41:28 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/content/glossary.js | unversioned -> unversioned | 2026-09-13 23:40:10 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/content/i18n.js | unversioned -> unversioned | 2026-09-13 10:33:50 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/content/module-summaries.js | unversioned -> unversioned | 2026-09-13 23:41:28 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/content/object-catalog.js | unversioned -> unversioned | 2026-09-13 10:33:50 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/content/type-module-summaries.js | unversioned -> unversioned | 2026-09-13 23:41:28 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/mirror.js | unversioned -> unversioned | 2026-09-11 16:50:21 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/page.js | unversioned -> unversioned | 2026-09-13 23:41:28 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/algorithm/styles.css | unversioned -> unversioned | 2026-09-13 16:31:52 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/chart/drawing-coordinates.js | unversioned -> unversioned | 2026-09-13 22:52:16 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/chart/indicator-range.js | unversioned -> unversioned | 2026-09-19 14:53:03 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/chart/lod.js | unversioned -> unversioned | 2026-09-01 07:59:21 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/chart/progress.js | unversioned -> unversioned | 2026-09-01 04:08:07 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/chart/state.js | unversioned -> unversioned | 2026-08-30 19:21:49 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/chart/view-transform.js | unversioned -> unversioned | 2026-09-13 21:29:22 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/chart/zoom-config.js | unversioned -> unversioned | 2026-09-13 22:29:55 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/drawings/drawing-math.js | unversioned -> unversioned | 2026-09-19 15:06:45 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/drawings/drawing.css | unversioned -> unversioned | 2026-09-01 07:21:44 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/drawings/object-tree.css | unversioned -> unversioned | 2026-09-13 21:30:35 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/candle-export.js | unversioned -> unversioned | 2026-09-22 15:13:46 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/candle-update.js | unversioned -> unversioned | 2026-09-16 00:50:17 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/faraz-symbol.js | unversioned -> unversioned | 2026-09-16 01:12:23 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/indicator-cache.js | unversioned -> unversioned | 2026-09-15 10:06:31 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/indicator-calculation-request.js | unversioned -> unversioned | 2026-09-21 02:50:46 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/indicator-lifecycle.js | unversioned -> unversioned | 2026-09-15 09:34:43 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/manual-review/entry.js | unversioned -> unversioned | 2026-09-13 16:40:45 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/manual-review/render.js | unversioned -> unversioned | 2026-09-23 21:37:45 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/manual-review/review.css | unversioned -> unversioned | 2026-09-19 23:13:43 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/manual-review/tab.js | unversioned -> unversioned | 2026-09-13 10:32:10 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/raw-file-contract.js | unversioned -> unversioned | 2026-09-16 00:48:09 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/raw-inventory.js | unversioned -> unversioned | 2026-09-19 15:33:22 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/screenshot-overlay.js | unversioned -> unversioned | 2026-09-15 09:41:41 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/features/workspace-session.js | unversioned -> unversioned | 2026-09-22 15:11:36 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/main.js | unversioned -> unversioned | 2026-09-22 15:13:46 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/platform/browser-compat.js | unversioned -> unversioned | 2026-09-06 08:35:17 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/styles/app.css | unversioned -> unversioned | 2026-09-20 00:41:04 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/styles/candle-export.css | unversioned -> unversioned | 2026-09-19 18:47:58 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/styles/qg-modern.css | unversioned -> unversioned | 2026-09-13 16:44:02 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/styles/tokens.css | unversioned -> unversioned | 2026-09-13 22:29:56 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/ui/chart-identity.js | unversioned -> unversioned | 2026-09-19 19:15:40 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/ui/feedback.js | unversioned -> unversioned | 2026-09-15 09:36:55 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/ui/icons.js | unversioned -> unversioned | 2026-09-20 00:41:04 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/ui/log-window.js | unversioned -> unversioned | 2026-09-13 16:43:41 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/ui/popover.js | unversioned -> unversioned | 2026-09-13 22:20:55 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/ui/symbol-format.js | unversioned -> unversioned | 2026-09-15 21:07:21 +0330 Asia/Tehran | retained/organized current project content
apps/chart/src/ui/workspace-state.js | unversioned -> unversioned | 2026-09-13 16:24:54 +0330 Asia/Tehran | retained/organized current project content
apps/chart/vite.config.js | unversioned -> unversioned | 2026-09-29 13:32:29 +0330 Asia/Tehran | storage/configuration/documentation update
docs/README.md | unversioned -> unversioned | 2026-09-29 13:34:09 +0330 Asia/Tehran | retained/organized current project content
docs/algorithms/README.md | unversioned -> unversioned | 2026-09-29 13:34:09 +0330 Asia/Tehran | retained/organized current project content
docs/architecture/TradingBot_Technical_Architecture.md | unversioned -> unversioned | 2026-09-29 13:29:58 +0330 Asia/Tehran | retained/organized current project content
docs/architecture/TradingBot_UI_UX_Technical_Reference.md | unversioned -> unversioned | 2026-09-29 13:29:58 +0330 Asia/Tehran | retained/organized current project content
docs/development/Local_Test_Workflow.md | unversioned -> unversioned | 2026-09-29 13:34:09 +0330 Asia/Tehran | retained/organized current project content
docs/development/Standalone_Reference_Specification.md | unversioned -> unversioned | 2026-09-23 07:43:50 +0330 Asia/Tehran | retained/organized current project content
docs/development/TradingBot_AI_Operating_Protocol.md | unversioned -> unversioned | 2026-09-29 13:44:01 +0330 Asia/Tehran | retained/organized current project content
docs/development/Zero_Difference_Refactor_Specification.md | unversioned -> unversioned | 2026-09-23 07:51:52 +0330 Asia/Tehran | retained/organized current project content
docs/development/plans/2026-09-23-bridge-output-projection.md | unversioned -> unversioned | 2026-09-29 13:29:58 +0330 Asia/Tehran | retained/organized current project content
docs/development/specs/Bridge_Output_Projection.md | unversioned -> unversioned | 2026-09-23 16:19:57 +0330 Asia/Tehran | retained/organized current project content
docs/history/README.md | unversioned -> unversioned | 2026-09-29 13:34:09 +0330 Asia/Tehran | retained/organized current project content
docs/history/TradingBot_Cleanup_Report.md | unversioned -> unversioned | 2026-09-29 13:29:58 +0330 Asia/Tehran | retained/organized current project content
docs/history/TradingBot_Project_Audit.md | unversioned -> unversioned | 2026-09-29 13:29:58 +0330 Asia/Tehran | retained/organized current project content
docs/history/TradingBot_Repository_Baseline.md | unversioned -> unversioned | 2026-09-29 13:29:58 +0330 Asia/Tehran | retained/organized current project content
docs/history/TradingBot_Validation_Report.md | unversioned -> unversioned | 2026-09-29 13:29:58 +0330 Asia/Tehran | retained/organized current project content
docs/operations/Local_State.md | unversioned -> unversioned | 2026-09-29 13:34:09 +0330 Asia/Tehran | retained/organized current project content
docs/verification/Repository_Integrity.md | unversioned -> unversioned | 2026-09-29 13:34:09 +0330 Asia/Tehran | retained/organized current project content
engine/__init__.py | unversioned -> unversioned | 2026-09-27 23:29:49 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/algorithms/TradingBot_Bearish_Algorithm_Reference_V5.4.19_EX1_Source_Synchronized.md | 5.4.19-EX1 -> 5.4.19-EX1 | 2026-09-28 23:02:59 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V5.4.19_EX1_Source_Synchronized.md | 5.4.19-EX1 -> 5.4.19-EX1 | 2026-09-28 23:02:59 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/bridge/__init__.py | unversioned -> unversioned | 2026-09-27 23:14:32 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/bridge/trading_pipeline.py | TRADING_PIPELINE_VERSION=1.7.0 -> 1.7.0; TRADING_PIPELINE_IMPLEMENTATION_VERSION=1.8.0 -> 1.8.0 | 2026-09-27 23:17:33 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/pipeline/__init__.py | unversioned -> unversioned | 2026-09-27 23:14:32 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/pipeline/a_zone_detector.py | A_ZONE_VERSION=1.6.4 -> 1.6.4 | 2026-09-24 03:20:53 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/pipeline/blue_line_detector.py | BLUE_LINE_VERSION=2.3.0 -> 2.3.0 | 2026-09-24 03:20:53 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/pipeline/core_utils.py | CORE_UTILS_VERSION=1.0.0 -> 1.0.0 | 2026-09-24 03:20:52 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/pipeline/direction_policy.py | DIRECTION_POLICY_VERSION=1.0.0 -> 1.0.0 | 2026-09-24 03:20:52 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/pipeline/e_zone_detector.py | E_ZONE_VERSION=6.16.1 -> 6.16.1; E_ZONE_IMPLEMENTATION_VERSION=6.18.1 -> 6.18.1 | 2026-09-28 23:02:12 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/pipeline/lifecycle_engine.py | STOP_ALL_VERSION=1.17.0 -> 1.17.0; STOP_ALL_IMPLEMENTATION_VERSION=1.18.0 -> 1.18.0 | 2026-09-27 23:17:33 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/pipeline/order_audit_engine.py | ORDER_AUDIT_ENGINE_VERSION=1.5.1 -> 1.5.1 | 2026-09-28 19:35:55 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/pipeline/reaction_engine.py | REACTION_ENGINE_VERSION=9.8.0 -> 9.8.0 | 2026-09-24 03:20:52 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/pipeline/s_zone_detector.py | S_ZONE_VERSION=4.20.0 -> 4.20.0; S_ZONE_IMPLEMENTATION_VERSION=4.21.0 -> 4.21.0 | 2026-09-27 23:17:33 +0330 Asia/Tehran | protected current Engine/reference bytes
engine/styles/reaction-detector.css | unversioned -> unversioned | 2026-09-13 16:44:02 +0330 Asia/Tehran | protected current Engine/reference bytes
scripts/launch.bat | unversioned -> unversioned | 2026-09-13 19:49:50 +0330 Asia/Tehran | retained/organized current project content
scripts/start.ps1 | unversioned -> unversioned | 2026-09-29 13:36:13 +0330 Asia/Tehran | storage/configuration/documentation update
