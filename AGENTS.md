# TradingBot Project Knowledge

This file is the root navigation and operating guide for AI-assisted work in the current TradingBot checkout. The current working tree is intentionally dirty; source files and user changes are authoritative, while generated artifacts and historical references are supporting evidence only.

## A. Project Identity

TradingBot is a Windows-oriented local candlestick/chart workstation. The browser application acquires and displays RAW candle data, manages drawings and indicator state, and requests calculations from a local Vite middleware. The calculation authority is Python under `engine/`; it produces Reaction, Blue Line, A, S, E, StopAll, and OrderAudit results for Bullish and Bearish directions.

The chart package is `apps/chart` version `3.4.1`. Its runtime uses native ES modules, Vite `8.2.1`, Lightweight Charts `5.2.1`, Node's built-in test runner, and Playwright Core for local FARAZ workflows. The launcher currently expects Node `20.19+`, Python `3.12+`, `orjson`, and `tzdata`. The installed audit environment used Node `24.19.0` and Python `3.14.6`.

The repository checkpoint/tag version and the chart package version are separate. A `v2.0.0` release tag is not present in the baseline audited state.

## B. Repository Map

| Path | Use |
| --- | --- |
| `scripts/launch.bat`, `scripts/start.ps1` | Windows startup and dependency/bootstrap checks; these scripts can mutate the environment. |
| `apps/chart/index.html`, `apps/chart/src/main.js` | Browser shell, composition root, mutable workstation state, chart and interaction orchestration. |
| `apps/chart/src/chart/` | Chart state, LOD, coordinate transforms, progress, and zoom contracts. |
| `apps/chart/src/features/` | RAW inventory/update, FARAZ integration, indicator cache/lifecycle, workspace sessions, screenshots, and manual review. |
| `apps/chart/src/ui/`, `src/drawings/` | Feedback, logs, popovers, icons, workspace state, and drawing presentation. |
| `apps/chart/src/algorithm/` | In-app algorithm reference content and directional mirror documentation. |
| `apps/chart/server/`, `apps/chart/vite.config.js` | Local HTTP API, Python subprocess boundary, RAW/FARAZ persistence, caches, SSE, drawings, and templates. |
| `apps/chart/tests/` | 27 Node test files; the current suite has 147 tests. |
| `engine/bridge/trading_pipeline.py` | Authoritative CLI, dynamic engine loading, market context, stage orchestration, lifecycle, visibility, and JSON serialization. |
| `engine/pipeline/` | Reaction, Blue, A, S, E, StopAll, chronology, direction policy, Decimal/order helpers, and lifecycle logic. |
| `data/raw/` | Authoritative candle arrays and metadata sidecars. |
| `runtime/cache/` | User drawings, templates, calculation caches, and FARAZ session state; preserve by default. |
| `docs/` | Maintained architecture, algorithm, UI, audit, cleanup, validation, and Graphify evidence. |

The tracked checkout is at `0d084590fb1ba1b57bcac6d4f19c977557830c2d` on `main`, two commits ahead of `origin/main` at baseline. The worktree contains user-owned tracked edits, deletions, and untracked replacement engine/frontend files. Never reset, clean, stash, rename, or stage those paths without explicit authorization.

## C. Architecture Overview

The runtime boundary is:

```text
launch.bat -> start.ps1 -> Vite middleware/browser
browser -> HTTP JSON/SSE -> vite.config.js/server/*.js
Vite -> Python subprocess -> trading_pipeline.py
bridge -> Reaction -> Blue -> A -> S -> E -> StopAll/visibility -> JSON stdout
JSON -> Vite cache/API -> browser chart, panels, review, and audit views
```

`vite.config.js` anchors paths from the configuration file, spawns Python with explicit bridge and detector paths, parses `QG_PROGRESS:` stderr, and returns serialized stdout. For a full-chart request it passes the original RAW path. For a partial indicator range it filters RAW rows by the inclusive chart-candle buckets in Node memory and streams that JSON through a Windows named pipe; no second RAW file is written. The unchanged bridge calculates from the complete input it receives, so a partial request starts with empty state at `from` and cannot use chronology outside `to`. The browser must not become a second trading-rule authority.

## D. Runtime Execution Flow

1. `scripts/start.ps1` validates files/runtimes, may install dependencies, creates runtime directories, sets `TRADINGBOT_PYTHON` and `TRADINGBOT_PROJECT_ROOT`, and starts Vite on `0.0.0.0`.
2. `apps/chart/src/main.js` loads `/api/symbols`, restores workspace state, reads `/api/candles`, and creates Lightweight Charts.
3. Indicator actions post validated direction, analysis timeframe, chart timeframe, inclusive chart-candle range, and Blue-line settings to `/api/reactions`; progress is streamed through `/api/reactions/progress` SSE.
4. `vite.config.js` builds a cache key from engine source fingerprint, RAW identity/mtime, input scope, chart/analysis timeframes, range, direction, and Blue-line flags, then spawns `engine/bridge/trading_pipeline.py`.
5. `prepare_market_context()` parses the complete supplied input (the original RAW file or an in-memory selected-range stream), builds lower-timeframe and main-candle chronology, and computes visible indexes.
6. `prepare_pipeline_state()` prepares both directional Reaction contexts when dependent stages are enabled. `calculate_full_direction_state()` runs Blue, A, S, initial E, S validity/rebuild, A/order context, final E audit, shared Order-stop reconciliation, and consumed-S continuation.
7. `finalize_direction_visibility()` applies A/S/E/StopAll lifecycle ownership, restores allowed historical lineage, filters display-range objects, and prepares OrderAudit.
8. The bridge serializes versioned stage collections and timings as compact JSON. The Vite API caches/persists the result and the browser renders chart overlays, tables, progress, and review state.

## E. Engine Knowledge

Critical versions in the current source are Reaction `9.5.2`, Blue `2.3.0`, A `1.6.3`, S `4.13.1`, E `6.6.2`, StopAll/lifecycle `1.10.1`, and shared `core_utils`/`direction_policy` `1.0.0`.

- `reaction_engine.py` defines Candle, Candidate, ResetEvent, chronology indexes, BullishDetector, the reflected BearishDetector, and UnifiedReactionDetector.
- `blue_line_detector.py` implements Fibonacci `0.618`, scale/reset strike counts, directional line prices, and public/internal filters.
- `a_zone_detector.py` pairs Blue formations and inherited stops with exact temporal boundaries.
- `s_zone_detector.py` races Order-backed, trend, and Reset-leg candidates, including shared Order-stop recoloring.
- `e_zone_detector.py` merges direct/inherited/carried Order causes, selects source/decision ranges, recursively continues families, and reconciles same-source conflicts.
- `lifecycle_engine.py` applies StopAll priority, one-pass historical reconciliation, and final visibility/lineage filtering.
- `core_utils.py` owns Decimal conversion and Order identity; `direction_policy.py` owns directional strictness, extrema, colors, and confirmation rules.

Numerical invariants: use Decimal semantics; preserve strict `<`/`>` crossings and explicit inclusive windows; retain physical source indexes/times, parent/order provenance, cause objects, nulls, version fields, and serialization ordering. Do not infer Bearish as a blanket inverse of Bullish. A known asymmetry is the Unified post-Reset same-Break reset level: Bullish uses `analysis.extreme` while Bearish uses stored `box_top` in the corresponding branch.

Read [TradingBot_Technical_Architecture.md](docs/TradingBot_Technical_Architecture.md) and the two directional references before engine changes. The current Python package import surface is not a supported smoke path: flat imports can fail with `ModuleNotFoundError: direction_policy` or `ImportError: run_blue_line`; the production bridge uses dynamic file loading to work around this migration state.

## F. Bullish and Bearish Knowledge

The authoritative implementations are independent paths in `engine/pipeline/reaction_engine.py`, with directional policy in `direction_policy.py` and reflected Bearish coordinates in `mirror_candle()`, `mirror_candidate()`, and `BearishDetector`. The rest of the pipeline consumes directional contracts rather than duplicating the state machine.

- Bullish uses GREEN context/First RED, strict Low-based invalidation and High-based confirmation, lower-timeframe extrema, and Bullish directional stop formulas.
- Bearish uses RED context/First GREEN through reflected coordinates, strict High-based invalidation and Low-based confirmation, and Bearish formulas/ownership. It has verified refinement and same-Break reset differences.

Before changing either direction, read both references, inspect the shared detector and policy, trace the integrated Reaction -> Blue -> A -> S -> E -> StopAll path, and run the full chart test suite plus any safe engine sanity check. Do not “fix” a directional mismatch by changing only one side.

## G. Frontend Knowledge

`main.js` is the composition and state owner (about 6,500 lines). It creates the chart, loads RAW inventory/candles, owns indicator progress/result application, drawing persistence, workspace transitions, and chart updates. `tokens.css` defines neutral surfaces, blue action color, green/red chart colors, compact 10-17px typography, and z-index layers. Main responsive breakpoints are approximately 1180, 900, 760, 520, 420, and 400px; algorithm/review styles add their own breakpoints.

The UI uses HTTP JSON and SSE, not a WebSocket. Preserve DOM IDs, persisted local-storage contracts, canonical raw-time drawing anchors, LOD/view-transform behavior, chart resize/overflow rules, reduced-motion behavior, and existing icon/accessibility conventions. Static inspection is not browser evidence; distinguish it from a real browser run.

## H. Dependency and Data-Flow Map

- Browser `main.js` -> Vite middleware endpoints -> bridge JSON/SSE.
- Vite -> `raw-resource-store.js` for strict OHLC/chronology/schema validation and atomic RAW/sidecar writes.
- Vite -> `faraz-candle-api.js` for FARAZ login/history/update/verification. Session data is currently an editable clear-text envelope despite the `.dpapi.json` filename.
- Bridge -> dynamically loaded detector files, then serializers -> cache/API -> browser.
- Public contracts preserve physical indexes/times and provenance. Reaction, Blue, A, S, E, StopAll, and OrderAudit collections have distinct ownership and nullable fields; see the architecture and algorithm references for exact fields.

Graphify shows source-linked relationships but may include inferred edges or omit detector-classified files. Treat `docs/graphify/rebuild-2026-09-19/graph-health.json` and direct source tracing as the evidence boundary.

## I. Graphify Integration

Installed tools: `graphify 0.9.63`, Python package `graphifyy 0.9.42`.

Verified commands:

```powershell
graphify update . --no-cluster
graphify cluster-only . --no-label
graphify query "pipeline execution" --graph graphify-out/graph.json --budget 800
graphify diagnose multigraph --graph graphify-out/graph.json --json
```

The dated verified snapshot is `docs/graphify/rebuild-2026-09-19/`. It contains a directed 1,240-node/2,774-link graph, report, HTML visualization, manifest, and health diagnostics. One detector-classified file, `apps/chart/src/styles/tokens.css`, was skipped as sensitive and must be checked directly. The existing top-level `docs/graphify/` snapshot is retained as historical/supporting evidence; do not assume its larger vendored-dependency graph is current.

After implementation changes, rerun the update and diagnose commands, compare representative query results to direct source tracing, and record stale/unresolved relationships. Do not invent edges or promote inferred relationships to implementation facts.

## J. Development and Validation

Supported package commands, run from `apps/chart`:

```powershell
npm.cmd test
npm.cmd run build
npm.cmd run dev
npm.cmd run preview
```

The first two are check/build commands. `dev`, `preview`, and `scripts/start.ps1` start services or mutate runtime/dependency state. There is no repository-local Python test, lint, type-check, CI, or SonarQube CLI configuration. Safe source checks used in the current audit are Node `--check` for project JS/MJS and `ast.parse` for engine Python. Do not report a check as PASS without fresh output and an exit code.

## K. AI-Agent Operating Instructions

- Preserve all pre-existing tracked and untracked work; never reset, clean, stash, or broad-delete.
- Read the relevant technical reference and current source before changing a subsystem.
- Use Graphify to locate dependencies, then verify important relationships and behavior directly in source.
- Treat Python engine code as the numerical authority and preserve exact Decimal, temporal, provenance, strictness, null, and ordering semantics.
- Avoid unrelated modifications, dependency upgrades, formatting writes, migrations, and runtime behavior changes.
- Run the narrowest relevant tests, then the full safe suite; record failures and limitations accurately.
- Update affected references and Graphify artifacts when implementation changes, while keeping generated findings labeled as such.
- Keep credential/session values private. Do not expose or copy `runtime/cache/secret` contents.
- Report unresolved ambiguity instead of guessing, and do not claim production readiness from documentation or unit tests alone.

## L. Documentation Index

- [Repository Baseline](docs/TradingBot_Repository_Baseline.md): ownership boundary, Git identity, and pre-existing dirty state.
- [Technical Architecture](docs/TradingBot_Technical_Architecture.md): runtime, modules, APIs, data flow, contracts, and risks.
- [Project Audit](docs/TradingBot_Project_Audit.md): confirmed defects, potential risks, and verification status.
- [UI/UX Technical Reference](docs/TradingBot_UI_UX_Technical_Reference.md): selectors, tokens, layout, states, breakpoints, and overlays.
- [Bullish Reference](docs/TradingBot_Bullish_Algorithm_Reference.md): implementation-faithful Bullish path.
- [Bearish Reference](docs/TradingBot_Bearish_Algorithm_Reference.md): implementation-faithful Bearish path and asymmetries.
- [Cleanup Report](docs/TradingBot_Cleanup_Report.md): conservative retention/deletion decisions.
- [Validation Report](docs/TradingBot_Validation_Report.md): fresh commands, statuses, evidence, and limitations.
- [Graphify README](docs/graphify/README.md): prior repository-wide snapshot and interpretation notes.
- [Current Graphify Rebuild](docs/graphify/rebuild-2026-09-19/README.md): current directed structural snapshot and health evidence.
- `agent.md`: pre-existing lowercase guide retained for compatibility; this uppercase file is the canonical root entry point.

No nested `AGENTS.md` is currently needed: the root file contains the engine-specific numerical rules and links to the detailed references without adding contradictory context.
