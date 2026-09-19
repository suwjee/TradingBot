# TradingBot Agent Guide

Project: TradingBot / QG Chart Workstation  
Canonical root: `D:/My-Projects/TradingBot`  
Application package version: `apps/chart/package.json` = `3.4.1`  
Release checkpoint: Git tag `v2.0.0` is a repository/documentation checkpoint; it does not replace the application package version.

## Documentation Index

- `docs/TradingBot_Technical_Architecture.md`: system boundaries, startup, data flow, contracts, integrations, and risks.
- `docs/TradingBot_Project_Audit.md`: evidence-backed findings, severity, cleanup candidates, and remediation order.
- `docs/TradingBot_UI_UX_Technical_Reference.md`: UI structure, tokens, states, breakpoints, layering, and preservation rules.
- `docs/TradingBot_Bullish_Algorithm_Reference.md`: current Bullish engine semantics and invariants.
- `docs/TradingBot_Bearish_Algorithm_Reference.md`: current Bearish engine semantics and real asymmetries.
- `docs/TradingBot_Repository_Baseline.md`: protected pre-existing working-tree ownership boundary.
- `docs/TradingBot_Validation_Report.md`: most recent executable evidence and limitations, when present.
- `docs/graphify/README.md`: graph scope, health interpretation, output map, and inventory rules.

Bullish/Bearish engine changes require both directional references. UI work requires the UI/UX reference. Cross-cutting work requires the architecture, audit, baseline, and Graphify README.

## Critical Directory Map

| Path | Role |
|---|---|
| `scripts/` | Windows launcher/bootstrap; can install dependencies and mutate runtime state |
| `apps/chart/index.html`, `apps/chart/src/main.js` | Main browser shell and composition/state root |
| `apps/chart/src/chart/`, `features/`, `ui/`, `drawings/` | Chart, data, persistence, feedback, and drawing mechanics |
| `apps/chart/vite.config.js`, `apps/chart/server/` | Local HTTP API, Python boundary, RAW/FARAZ storage and acquisition |
| `apps/chart/tests/` | Node test suite |
| `engine/bridge/trading_pipeline.py` | Authoritative CLI/orchestration/serialization boundary |
| `engine/pipeline/` | Reaction, Blue, A, S, E, StopAll, chronology, direction policy, shared utilities |
| `data/raw/` | Authoritative RAW candle arrays and sidecars |
| `runtime/cache/` | User/runtime state and generated calculations; preserve by default |
| `docs/` | Maintained technical references and validation evidence |

## Authority

- Read `AGENTS.md` if one is added later, this file, current diffs, and the relevant maintained skill before work.
- Python under `engine/bridge` and `engine/pipeline` is the trading-rule authority. Browser code renders and orchestrates; it must not duplicate engine decisions.
- Treat generated payloads, caches, screenshots, and historical algorithm documents as evidence, not runtime authority.

## Safety

- Preserve unrelated and uncommitted user changes. Stage only paths owned by the current task.
- Never hardcode timestamps, OHLC values, source identities, fixtures, or expected results into runtime calculations.
- Keep credential/session values private even when every file is included in an audit.
- Do not silently normalize results to old caches or documentation.

## Required Analysis Order

1. Capture Git status, HEAD, remote, tags, and the exact requested scope.
2. Trace `scripts -> Vite/backend -> Python bridge -> Reaction -> Blue -> A -> S -> E -> StopAll -> serialization -> UI`.
3. Use Graphify for repository-wide architecture and impact questions; validate its real `links`, endpoints, and graph health.
4. Separate source findings, generated-artifact findings, tests, and real browser-session evidence.
5. Report contradictions before changing trading semantics.

## Engine Invariants

- Calculate from the complete physical RAW dataset and apply requested ranges only to presentation.
- Preserve exact direction, strict-crossing, source-index, lineage, Order, cause, version, and ordering semantics.
- Validate the integrated chain, not an isolated detector, for behavior work.
- Equal counts are not parity: compare protected arrays, order audit, versions, serialization, and hashes.
- Distinguish missing-data limitations from behavior failures.

## UI Invariants

- Prefer CSS-first, minimal-JS changes.
- Preserve DOM IDs, persisted state, drawing anchors, chart coordinates, indicator lifecycle, and accessibility behavior.
- Use existing design tokens and verify responsive and reduced-motion behavior.
- For visual claims, distinguish static inspection from a real browser check.

## Validation

- Run tests from the owning package/directory.
- Use `npm.cmd` on Windows when PowerShell blocks `npm.ps1`.
- Avoid bytecode/cache pollution during Python inspection.
- Build into a temporary task-owned directory when the existing `dist` is user-owned.
- Record commands, exit codes, important counts, limitations, and exact failures in `docs/`.

Supported chart commands from `apps/chart/package.json`:

```powershell
Set-Location D:\My-Projects\TradingBot\apps\chart
npm.cmd test
npm.cmd run build
npm.cmd run dev
npm.cmd run preview
```

For a non-destructive release build, override Vite's output directory with a verified task-owned temporary path. Do not use `scripts/start.ps1` as a read-only validator: it may install software/packages and create directories. There is no repository-local Python test, lint, type-check, or CI command; record that limitation instead of inventing one.

## Documentation

- Keep current references under `docs/` and label older snapshots historical.
- Include exact file paths, symbols, versions, data flow, risks, and verification status.
- Update docs when source behavior changes; never claim current behavior from an old generated payload alone.
