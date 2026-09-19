# TradingBot Repository Baseline

Captured on 2026-09-17 before repository analysis, Graphify generation, cleanup, validation, or release staging. The execution plan was intentionally created first because the user-mandated workflow order placed `writing-plans` before the repository baseline.

## Git Identity

| Field | Baseline value |
|---|---|
| Repository root | `D:/My-Projects/TradingBot` |
| Branch | `main` |
| Starting HEAD | `0d084590fb1ba1b57bcac6d4f19c977557830c2d` |
| HEAD subject | `refactor: standardize runtime project layout` |
| Upstream | `origin/main` |
| Upstream state | Local `main` was ahead by 2 commits |
| Remote | `origin https://github.com/suwjee/TradingBot.git` |
| Remote HEAD at capture | `ff17450` (`algorithm bug fix`) |

## Existing Tags

`0.01`, `0.0.2`, `0.0.3`, `0.0.4`, `0.1.1`, `0.1.2`, `0.1.3`, and `1.0.0` existed locally. No local `v2.0.0` tag existed at baseline capture.

## File Inventory

- `rg --files -uu -g '!.git/**'` reported 600 files, including ignored runtime data, caches, installed dependencies, and build output.
- The tracked tree contained 53 paths at baseline HEAD.
- `AGENTS.md` was not present in the checkout.
- A session cache with a DPAPI-oriented filename was present under `runtime/cache/secret/`; the baseline did not assume encryption or reproduce its values. Later source inspection identified a clear-text version-3 envelope.

## Working-Tree Ownership Boundary

The first full status captured 90 paths:

- 89 pre-existing user-owned changes: 34 tracked modifications/deletions and 55 untracked paths.
- 1 task-created path: `docs/superpowers/plans/2026-09-17-tradingbot-v2-stable-audit.md`.

All 89 pre-existing paths are protected from reset, overwrite, deletion, staging, or release-commit inclusion by this task. Their contents are nevertheless the current implementation state and therefore the source for this read-only audit.

## Pre-Existing Tracked Changes

```text
 M apps/chart/index.html
 M apps/chart/package.json
 M apps/chart/review.html
 M apps/chart/server/faraz-candle-api.js
 M apps/chart/src/algorithm/content/bridge-content.js
 M apps/chart/src/algorithm/content/content.js
 M apps/chart/src/algorithm/content/glossary.js
 M apps/chart/src/algorithm/content/module-summaries.js
 M apps/chart/src/algorithm/content/type-module-summaries.js
 M apps/chart/src/algorithm/page.js
 M apps/chart/src/algorithm/styles.css
 M apps/chart/src/drawings/object-tree.css
 M apps/chart/src/features/candle-export.js
 M apps/chart/src/features/indicator-cache.js
 M apps/chart/src/features/manual-review/entry.js
 M apps/chart/src/features/manual-review/render.js
 M apps/chart/src/main.js
 M apps/chart/src/styles/app.css
 M apps/chart/src/styles/candle-export.css
 M apps/chart/src/styles/qg-modern.css
 M apps/chart/src/styles/tokens.css
 M apps/chart/src/ui/icons.js
 M apps/chart/vite.config.js
 D engine/bridge/reaction_bridge.py
 M engine/pipeline/__init__.py
 D engine/pipeline/a_zone.py
 D engine/pipeline/blue_line.py
 D engine/pipeline/e_zone.py
 D engine/pipeline/reaction.py
 D engine/pipeline/s_zone.py
 D engine/pipeline/stop_all.py
 M engine/styles/reaction-detector.css
 M scripts/launch.bat
 M scripts/start.ps1
```

The baseline diff stat for these tracked changes was 34 files, 2,733 insertions, and 10,673 deletions. This task did not create those changes.

## Pre-Existing Untracked Changes

```text
apps/chart/ Folders/My-Projects/TradingBot/apps/chart/.vite/deps/_metadata.json
apps/chart/ Folders/My-Projects/TradingBot/apps/chart/.vite/deps/package.json
apps/chart/server/migrate-raw-resources.js
apps/chart/server/raw-integrity.js
apps/chart/server/raw-resource-store.js
apps/chart/src/chart/drawing-coordinates.js
apps/chart/src/chart/view-transform.js
apps/chart/src/chart/zoom-config.js
apps/chart/src/features/candle-update.js
apps/chart/src/features/faraz-symbol.js
apps/chart/src/features/indicator-lifecycle.js
apps/chart/src/features/manual-review/review.css
apps/chart/src/features/raw-file-contract.js
apps/chart/src/features/raw-inventory.js
apps/chart/src/features/screenshot-overlay.js
apps/chart/src/features/workspace-session.js
apps/chart/src/ui/feedback.js
apps/chart/src/ui/log-window.js
apps/chart/src/ui/popover.js
apps/chart/src/ui/symbol-format.js
apps/chart/src/ui/workspace-state.js
apps/chart/tests/candle-export-log.test.mjs
apps/chart/tests/candle-update.test.mjs
apps/chart/tests/chart-update-contract.test.mjs
apps/chart/tests/drawing-coordinates.test.mjs
apps/chart/tests/faraz-candle-api.test.mjs
apps/chart/tests/faraz-symbol.test.mjs
apps/chart/tests/feedback.test.mjs
apps/chart/tests/indicator-cache.test.mjs
apps/chart/tests/indicator-lifecycle.test.mjs
apps/chart/tests/manual-review.test.mjs
apps/chart/tests/popover.test.mjs
apps/chart/tests/raw-file-contract.test.mjs
apps/chart/tests/raw-integrity.test.mjs
apps/chart/tests/raw-inventory.test.mjs
apps/chart/tests/raw-resource-store.test.mjs
apps/chart/tests/screenshot-overlay.test.mjs
apps/chart/tests/symbol-format.test.mjs
apps/chart/tests/view-transform.test.mjs
apps/chart/tests/workspace-session.test.mjs
apps/chart/tests/workspace-state.test.mjs
apps/chart/tests/zoom-config.test.mjs
engine/TradingBot_Bearish_Algorithm_Reference.md
engine/TradingBot_Bullish_Algorithm_Reference.md
engine/algorithms/TradingBot_Bearish_Algorithm_Reference_V4.0.1.md
engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V4.0.1.md
engine/bridge/trading_pipeline.py
engine/pipeline/a_zone_detector.py
engine/pipeline/blue_line_detector.py
engine/pipeline/core_utils.py
engine/pipeline/direction_policy.py
engine/pipeline/e_zone_detector.py
engine/pipeline/lifecycle_engine.py
engine/pipeline/reaction_engine.py
engine/pipeline/s_zone_detector.py
```

## Baseline Interpretation

The checkout represents an in-progress layout and runtime migration rather than a clean release tree. The current working files, including the untracked replacement engine and tests, are treated as the implementation under audit. The release commit must not absorb these pre-existing paths unless the user separately authorizes their inclusion; the present task may stage only its own documentation/Graphify outputs and any independently proven safe non-code deletion.

## Current-turn baseline reconciliation (2026-09-19)

The starting state for the current audit turn matched the recorded `HEAD` (`0d084590fb1ba1b57bcac6d4f19c977557830c2d`), branch (`main`), remote (`origin`), and dirty user-owned implementation paths above. Before this turn generated new artifacts, the worktree already contained the tracked frontend/engine edits, deleted legacy detector files, untracked replacement engine modules, untracked frontend/server/tests, `agent.md`, and the existing `docs/` audit and Graphify snapshot.

Current-turn task-owned additions are limited to the uppercase root `AGENTS.md`, `docs/TradingBot_Validation_Report.md`, the dated `docs/graphify/rebuild-2026-09-19/` snapshot (including preserved `raw-run/` intermediates), and this reconciliation text. The original `graphify-out/` path was moved intact under that snapshot. The lowercase `agent.md` and all pre-existing documentation/source changes remain preserved.

The local and remote `v2.0.0` tag checks were empty. No release commit, tag, push, reset, clean, stash, source edit, dependency change, or runtime order operation was performed by this turn.
