# TradingBot Project Knowledge and Agent Rules

This file is the root navigation and operating guide for AI-assisted work in the current TradingBot checkout. The current working tree is intentionally dirty. Current source files, configuration, and user changes are authoritative for describing executable state. Trading semantics, behavior definitions, lifecycle rules, ownership rules, Order rules, directional rules, and other algorithmic intent must be resolved through the TradingBot Intelligence Plugin and the canonical Knowledge Vault first. Generated artifacts, historical references, old AI output, and memory are supporting evidence only.

## 0. Governing Rules

### 0.1 Instruction and Trading Authority

For TradingBot work, apply this order:

1. Current explicit user instruction.
2. This root `AGENTS.md` and any nearer applicable project instruction.
3. TradingBot Intelligence Plugin retrieval.
4. Canonical / verified / normative TradingBot Knowledge Vault content.
5. Accepted algorithm/reference documents identified by the Vault.
6. Current production source and configuration as evidence of executable behavior.
7. Approved regression fixtures and reproducible RAW/runtime evidence.
8. Historical documentation, previous AI output, memory, and model inference.

Use Plugin/Vault to determine what the system **should** do.

Use current source and runtime evidence to determine what the system **currently does**.

If canonical knowledge and executable source disagree, do not silently reconcile them. Report the mismatch and determine whether the task is to fix implementation, update knowledge, or clarify the intended rule.

### 0.2 Mandatory Plugin/Vault-First Workflow

Before interpreting, explaining, debugging, validating, or changing any TradingBot semantic rule, first query the TradingBot Intelligence Plugin and inspect the relevant canonical Vault knowledge.

This is mandatory for:

- Reaction;
- Reset;
- Blue;
- A;
- S;
- E;
- StopAll;
- Orders and OrderAudit;
- lifecycle transitions;
- ownership;
- dominance;
- strictness;
- source/confirmation semantics;
- mirror rules;
- regression fixtures;
- special cases;
- algorithm references;
- canonical status.

Do not rely on memory, previous AI summaries, old conversations, or remembered examples as the primary authority when Plugin/Vault knowledge is available.

If the Plugin is unavailable, inspect the Vault directly if available. If canonical semantics still cannot be established, state the limitation and ask a precise clarifying question.

### 0.3 AGENTS Is Not the Algorithm

This file defines project navigation, authority, safety, workflow, and durable operating constraints.

It must not become a second copy of volatile TradingBot algorithm rules.

Do not hard-code changing semantics such as:

- current Order status;
- Order formation details;
- exact StopAll grouping;
- behavior counters;
- S/E subtype edge cases;
- ownership refresh rules;
- dominance exceptions;
- special candle outcomes.

Resolve volatile trading semantics from the current Plugin/Vault at task time.

### 0.4 Clarification — Hard Stop

Material ambiguity in TradingBot semantics must be resolved before implementation.

If uncertainty remains about behavior definition, source candle, confirmation candle, breakout, Reset, stop condition, strictness, direction, timeframe, lower-timeframe chronology, ownership, Order semantics, dominance, lifecycle transition, expected output, fixture meaning, canonical status, or mirror behavior:

1. Investigate everything discoverable from Plugin/Vault, source, tests, RAW, logs, and references.
2. Ask a precise technical question for what remains unresolved.
3. Continue asking follow-up questions until the material ambiguity is actually resolved.
4. Do not silently guess or convert an example into a general rule.

### 0.5 Independent Evaluation

Treat user-provided expected outputs, candle labels, diagnoses, root-cause theories, previous AI conclusions, old documentation, and memory as claims or evidence, not automatic proof.

Actively test competing explanations.

A user correction is important evidence, but production logic must still be based on a general canonical rule rather than a timestamp, OHLC fingerprint, fixture identity, or hidden special case.

When evidence contradicts the initial theory, state the contradiction clearly.

### 0.6 Strict Language Policy

Only Persian and English may be authored as natural-language content.

All developer-facing TradingBot technical content must be English, including:

- source identifiers;
- filenames created by the AI;
- comments;
- docstrings;
- technical logs;
- error messages;
- test names;
- assertion messages;
- technical Markdown;
- algorithm references;
- Vault knowledge;
- Plugin documentation;
- commit messages;
- changelog entries.

Do not introduce any third human language.

Persian may be used for user-facing conversation or dedicated Persian content/localization when explicitly required.

Existing third-language content required for compatibility, localization, data fidelity, or historical preservation must not be destructively rewritten without explicit authorization.

### 0.7 Truthfulness and Evidence Labels

Never claim to have read, executed, tested, verified, benchmarked, modified, committed, pushed, deployed, synchronized, or validated something unless that action actually occurred.

When the distinction matters, use:

- `VERIFIED FACT`
- `USER CLAIM`
- `DOCUMENTED CLAIM`
- `INFERENCE`
- `ASSUMPTION`
- `HYPOTHESIS`
- `UNVERIFIED RESULT`

Do not generalize bounded validation into full correctness.

### 0.8 Git and Dirty-Work Safety

Preserve all pre-existing tracked and untracked work.

Do not reset, clean, stash, overwrite, broad-delete, or stage unrelated dirty files without explicit authorization.

Remote push requires explicit authorization for the current task. Previous push authorization does not carry forward.

Before claiming a push or publication succeeded, verify the actual remote state.

### 0.9 Graphify Approval Rule

Graphify is a navigation and source-orientation tool, not algorithmic authority.

Every Graphify execution requires explicit user approval for that specific execution.

This includes:

- `build`;
- `update`;
- `query`;
- `graph`;
- `path`;
- `explain`;
- `export`;
- `diagnose`;
- dependency analysis.

Do not automatically run Graphify after implementation changes.

If Graphify would materially help, explain why and ask for approval first.

### 0.10 Supporting Skills

Supporting skills may improve workflow but do not define TradingBot semantics.

Examples include:

- Mirror Trading Pipeline;
- Property-Based Testing;
- Spec-to-Code Compliance;
- Differential Review;
- Persian Writing;
- `i-have-adhd`.

Trading-related supporting skills must operate only after Plugin/Vault retrieval.

No skill may override current user instructions, this `AGENTS.md`, canonical TradingBot knowledge, or safety constraints.

### 0.11 No Hidden Hardcoding

Production trading logic must not branch on known:

- timestamps;
- candle identities;
- symbols;
- RAW filenames;
- timeframe identities;
- OHLC fingerprints;
- fixture IDs;
- expected labels.

unless those values are genuinely part of the formal canonical specification.

Fixtures validate general logic. They must not become the logic.

### 0.12 Final Trading Workflow

Use this process for TradingBot tasks:

`Project instructions -> Plugin/Vault first -> Confirm authority -> Verify current source and RAW/runtime evidence -> Clarify ambiguity -> Find the first divergent stage/root cause -> Make the smallest correct change -> Validate protected regression -> Synchronize durable knowledge if needed -> Report honestly`

## A. Project Identity

TradingBot is a Windows-oriented local candlestick/chart workstation. The browser application acquires and displays RAW candle data, manages drawings and indicator state, and requests calculations from a local Vite middleware. The calculation authority is Python under `engine/`; it produces Reaction, Blue Line, A, S, E, StopAll, and OrderAudit results for Bullish and Bearish directions.

Snapshot note: the chart package was recorded as `apps/chart` version `3.4.1`. Its recorded runtime used native ES modules, Vite `8.2.1`, Lightweight Charts `5.2.1`, Node's built-in test runner, and Playwright Core for local FARAZ workflows. The launcher was recorded as expecting Node `20.19+`, Python `3.12+`, `orjson`, and `tzdata`. The audited environment used Node `24.19.0` and Python `3.14.6`. Re-verify all version/runtime facts before relying on them.

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
| `apps/chart/tests/unit/` | 30 local-only Node test files; the 2026-09-29 baseline had 159 tests; internal-state and watcher coverage add five tests. |
| `engine/bridge/trading_pipeline.py` | Authoritative CLI, dynamic engine loading, market context, stage orchestration, lifecycle, visibility, and JSON serialization. |
| `engine/pipeline/` | Reaction, Blue, A, S, E, StopAll, chronology, direction policy, Decimal/order helpers, and lifecycle logic. |
| `apps/chart/state/data/raw/` | Project-local candle arrays and metadata sidecars. |
| `apps/chart/state/cache/`, `apps/chart/state/secret/` | Project-local user drawings, templates, calculations and FARAZ authentication; ignored and preserved by default. |
| `engineering/docs/`, `engineering/archive/`, `engineering/verification/` | Maintained guidance, ignored historical evidence and local verification artifacts. |

Baseline snapshot: the tracked checkout was recorded at `0d084590fb1ba1b57bcac6d4f19c977557830c2d` on `main`, two commits ahead of `origin/main`. Re-verify the current commit/branch/remote state before relying on this snapshot. The worktree contains or may contain user-owned tracked edits, deletions, and untracked replacement engine/frontend files. Never reset, clean, stash, rename, overwrite, or stage those paths without explicit authorization.

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

1. `scripts/start.ps1` validates files/runtimes, may install dependencies, creates project-local state directories through the shared resolver, sets `TRADINGBOT_PYTHON`, `TRADINGBOT_PROJECT_ROOT`, and `TRADINGBOT_LOCAL_STATE_ROOT`, and starts Vite on `0.0.0.0`.
2. `apps/chart/src/main.js` loads `/api/symbols`, restores workspace state, reads `/api/candles`, and creates Lightweight Charts.
3. Indicator actions post validated direction, analysis timeframe, chart timeframe, inclusive chart-candle range, and Blue-line settings to `/api/reactions`; progress is streamed through `/api/reactions/progress` SSE.
4. `vite.config.js` builds a cache key from engine source fingerprint, RAW identity/mtime, input scope, chart/analysis timeframes, range, direction, and Blue-line flags, then spawns `engine/bridge/trading_pipeline.py`.
5. `prepare_market_context()` parses the complete supplied input (the original RAW file or an in-memory selected-range stream), builds lower-timeframe and main-candle chronology, and computes visible indexes.
6. `prepare_pipeline_state()` prepares both directional Reaction contexts when dependent stages are enabled. `calculate_full_direction_state()` runs Blue, A, S, initial E, S validity/rebuild, A/order context, final E audit, shared Order-stop reconciliation, and consumed-S continuation.
7. `finalize_direction_visibility()` applies A/S/E/StopAll lifecycle ownership, restores allowed historical lineage, filters display-range objects, and prepares OrderAudit.
8. The bridge serializes versioned stage collections and timings as compact JSON. The Vite API caches/persists the result and the browser renders chart overlays, tables, progress, and review state.

## E. Engine Knowledge

Executable snapshot: recorded source versions were Reaction `9.5.2`, Blue `2.3.0`, A `1.6.3`, S `4.13.1`, E `6.6.2`, StopAll/lifecycle `1.10.1`, and shared `core_utils`/`direction_policy` `1.0.0`. Re-read current source and Plugin/Vault knowledge before treating these values as current.

- `reaction_engine.py` defines Candle, Candidate, ResetEvent, chronology indexes, BullishDetector, the reflected BearishDetector, and UnifiedReactionDetector.
- `blue_line_detector.py` implements Fibonacci `0.618`, scale/reset strike counts, directional line prices, and public/internal filters.
- `a_zone_detector.py` pairs Blue formations and inherited stops with exact temporal boundaries.
- `s_zone_detector.py` races Order-backed, trend, and Reset-leg candidates, including shared Order-stop recoloring.
- `e_zone_detector.py` merges direct/inherited/carried Order causes, selects source/decision ranges, recursively continues families, and reconciles same-source conflicts.
- `lifecycle_engine.py` applies StopAll priority, one-pass historical reconciliation, and final visibility/lineage filtering.
- `core_utils.py` owns Decimal conversion and Order identity; `direction_policy.py` owns directional strictness, extrema, colors, and confirmation rules.

Numerical invariants: use Decimal semantics; preserve strict `<`/`>` crossings and explicit inclusive windows; retain physical source indexes/times, parent/order provenance, cause objects, nulls, version fields, and serialization ordering. Do not infer Bearish as a blanket inverse of Bullish. Current directional exceptions must be retrieved from the canonical Vault and verified against the current Source; do not infer them from a recorded snapshot.

Before engine changes, query the TradingBot Intelligence Plugin, inspect canonical Vault knowledge, then read [Technical architecture](engineering/docs/architecture/technical-architecture.md) and the directional references identified as current by the Vault. The current Python package import surface is not a supported smoke path: flat imports can fail with `ModuleNotFoundError: direction_policy` or `ImportError: run_blue_line`; the production bridge uses dynamic file loading to work around this migration state.

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

Graphify shows source-linked relationships and may include explicitly marked inferred edges. The project-local historical `engineering/archive/docs/graphify/rebuild-2026-09-23/` snapshot supplements detector-unclassified files with path nodes and the sensitive `tokens.css` file with custom-property names only; CSS values and RAW/runtime contents are not indexed. Treat its health diagnostics and direct source tracing as the evidence boundary.

## I. Graphify Integration

Recorded tool snapshot: `graphify 0.9.63`, Python package `graphifyy 0.9.42`. Re-verify installed versions before relying on them. Installation does not grant execution permission; every Graphify execution requires explicit user approval.

Verified commands:

```powershell
graphify update . --no-cluster
graphify cluster-only . --no-label
graphify query "pipeline execution" --graph graphify-out/graph.json --budget 800
graphify diagnose multigraph --graph graphify-out/graph.json --json
```

The dated Graphify snapshot is ignored project-local archived evidence under `engineering/archive/docs/graphify/rebuild-2026-09-23/`. It is not part of the tracked repository. The snapshot covers classified source/docs, records literal HTML references, represents unclassified configuration/style files as path nodes, and indexes only custom-property names from detector-classified `apps/chart/src/styles/tokens.css` (never its values). RAW candle and runtime/cache data are represented only by directory-scope markers; their contents and credential/session values are not read or copied. `engineering/archive/repository-graphify/rebuild-2026-09-19/` remains preserved as historical evidence.

After implementation changes, do not automatically rerun Graphify. If graph refresh or diagnosis would materially help, explain why and obtain explicit user approval for that execution. When approved, compare representative query results to direct source tracing and record stale/unresolved relationships. Do not invent edges or promote inferred relationships to implementation facts.

## J. Development and Validation

Supported package commands, run from `apps/chart`:

```powershell
npm.cmd test
npm.cmd run build
npm.cmd run dev
npm.cmd run preview
```

The first two are check/build commands. `dev`, `preview`, and `scripts/start.ps1` start services or mutate runtime/dependency state. Local-only Python tests are under ignored `engine/tests/unit/`; run `python -B -m pytest -q -p no:cacheprovider -p no:benchmark engine/tests/unit` from the repository root. No repository lint, type-check, CI, or SonarQube CLI configuration was found. Safe source checks are Node `--check` for project JS/MJS and `ast.parse` for Engine Python. Do not report a check as PASS without fresh output and an exit code.

## K. AI-Agent Operating Instructions

- Preserve all pre-existing tracked and untracked work; never reset, clean, stash, overwrite, or broad-delete without explicit authorization.
- For trading semantics, consult the TradingBot Intelligence Plugin and canonical Vault before relying on technical references, source intuition, memory, or old examples.
- Read the relevant current source and accepted references before changing a subsystem.
- Graphify may be used only after explicit user approval for that specific execution; verify important relationships and behavior directly in source.
- Treat Python engine code as the numerical/executable authority while preserving canonical Plugin/Vault semantics and exact Decimal, temporal, provenance, strictness, null, identity, ownership, lifecycle, and ordering contracts.
- Do not patch UI-only code to change trading semantics.
- Avoid unrelated modifications, dependency upgrades, formatting writes, migrations, and runtime behavior changes.
- Run the narrowest relevant tests first, then protected regression and broader safe validation according to risk.
- Do not report build, static review, unit tests, mirror parity, browser checks, or bounded fixtures as stronger evidence than they actually provide.
- Update durable references/Vault knowledge when durable behavior or architecture changes. Do not create temporary knowledge noise.
- Do not automatically refresh Graphify artifacts; request approval first if a graph refresh would materially help.
- Keep credential/session values private. Do not expose or copy `apps/chart/state/secret/` values into logs, reports or delivery packages.
- Report unresolved ambiguity instead of guessing.
- Never introduce hidden hardcoding for known timestamps, OHLC fingerprints, filenames, symbols, fixtures, or expected outputs.
- All developer-facing technical content, comments, docstrings, logs, tests, commit messages, and documentation authored by the AI must be English.
- Do not push to a remote without explicit authorization for the current task.

### K.1 Validation Language

Use precise validation labels when relevant:

- `PASS`
- `FAIL`
- `INCOMPLETE`
- `NOT_TESTED`
- `NOT_TESTED_DEPENDENCY_UNAVAILABLE`
- `STATIC_REVIEW_ONLY`
- `BOUNDED_VALIDATION`

Mirror/metamorphic parity is not independent Bearish correctness. Report source-direction regression safety, mirror parity, and independent target-direction real-data validation separately.

A user-provided candle correction is important evidence, but it must be explained by a general canonical rule and must never become a hidden production branch.

## L. Documentation Index

- [Engineering index](engineering/docs/README.md): current maintained document navigation.
- [Operating protocol](engineering/docs/ai/operating-protocol.md): engineering and delivery requirements, subordinate to root authority.
- [Technical architecture](engineering/docs/architecture/technical-architecture.md) and [UI/UX reference](engineering/docs/architecture/ui-ux-reference.md): dated evidence with current navigation notes.
- [Local storage](engineering/docs/operations/local-state.md), [Local tests](engineering/docs/development/local-tests.md) and [Repository integrity](engineering/docs/verification/repository-integrity.md): current storage and validation rules.
- [Single-root migration](engineering/docs/verification/single-root-migration.md): complete movement and validation evidence.
- [Bullish Reference](engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V5.4.19_EX1_Source_Synchronized.md) and [Bearish Reference](engine/algorithms/TradingBot_Bearish_Algorithm_Reference_V5.4.19_EX1_Source_Synchronized.md): unchanged current exact-source references.

Historical Graphify/regression material stays in ignored `engineering/archive/`; old build scripts and path strings inside those bundles are historical evidence, not active tool entry points. Every Graphify execution still requires explicit approval.

`AGENTS.md` is the canonical root entry point. No nested project AGENTS was found in the current source inventory.

## M. Repository Storage Policy

All project-owned content stays inside `D:\My-Projects\TradingBot`. Three primary owners are `apps/`, `engine/` and `engineering/`. `scripts/` remains a root tooling exception preserving established Windows/VMware startup paths. Root Git/editor configuration, AGENTS and README stay at discovery boundaries.

`TRADINGBOT_LOCAL_STATE_ROOT` defaults to `apps/chart/state`; configured roots may select only that dedicated subtree or a descendant. The shared resolver rejects source directories, external paths and escaping junctions. The launcher uses the same resolver. RAW, caches, secrets and temporary files remain project-local and Git-ignored. Direct Vite file access to state is denied; its normal API contracts remain available.

Tests live beside their owners under ignored `apps/chart/tests/` and `engine/tests/`; chart tests run with `npm.cmd test` from `apps/chart`. Engine production-source discovery excludes test code. Dependencies/build output remain reproducible and ignored. Historical Graphify/regression artifacts live in ignored `engineering/archive/`; migration snapshots, maps and logs live in ignored `engineering/verification/`. Only the two source-synchronized references under `engine/algorithms/` are current references.
