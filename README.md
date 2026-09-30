---
title: TradingBot
document_role: reference
lifecycle: maintained
owner: project-navigation
last_modified_at: 2026-09-30T11:40:11+03:30
---

# TradingBot

TradingBot is a Windows candlestick workstation. The chart application acquires and displays candles, drawings, indicators and review tables. Python under `engine/` owns trading calculations; the browser renders serialized results.

## Project ownership

| Owner | Responsibility |
| --- | --- |
| `apps/chart/` | Browser application, local HTTP/SSE server, application state and chart tests |
| `engine/` | Calculation bridge, stage owners, current exact-source references and local Engine verification |
| `engineering/` | Maintained documentation, historical archives and local verification evidence |

The root `scripts/` directory preserves the public Windows startup paths used by existing shortcuts and the VMware shared checkout. Root Git/editor files, `AGENTS.md` and this README stay at their tool discovery boundaries.

**Every project-owned file stays inside this TradingBot directory.** RAW and sidecars use `apps/chart/state/data/raw/`, persistent drawings/calculations/templates use `apps/chart/state/cache/`, FARAZ authentication uses `apps/chart/state/secret/`, and temporary files use `apps/chart/state/tmp/`. Machine-local state, dependencies, caches, temporary files and rebuildable output are excluded according to current repository policy; legitimate tests, maintained documentation, curated baseline evidence and meaningful engineering evidence may be tracked. See [local storage](engineering/docs/operations/local-state.md).

`TRADINGBOT_LOCAL_STATE_ROOT` is optional. Its default is `apps/chart/state`; a configured value must resolve to that directory or a descendant. External roots and source directories are rejected. Vite denies direct static access to state; the established `/api` resources remain available.

## Install and start

Use Node.js `20.19+` (Node.js 22 requires `22.12+`) and Python `3.12+`. Python runtime dependencies are `orjson` and `tzdata`.

```powershell
Set-Location 'D:\My-Projects\TradingBot'
.\scripts\launch.bat
```

The launcher checks runtimes and installs missing dependencies before starting Vite. For manual development:

```powershell
python -m pip install orjson tzdata
Set-Location apps/chart
npm.cmd ci
npm.cmd run dev -- --host 127.0.0.1 --configLoader native
```

Build with `npm.cmd run build` from `apps/chart`. These commands keep generated output inside the project.

## Local verification and navigation

Tests are discovered from the current repository, manifests and runners rather than treated as a fixed local-only bundle. The current project contains Chart and Engine test/verification trees, but their layout and runner set are not permanent contracts. See [Testing](engineering/docs/development/testing.md) for dynamic discovery, execution status, RAW and regression policy.

Read [AGENTS.md](AGENTS.md) and the [AI engineering workflow](engineering/docs/ai/engineering-workflow.md) before engineering work. Trading semantics require the Intelligence Plugin and canonical Knowledge Vault. Use the [engineering document index](engineering/docs/README.md) for Current maintained navigation. Historical single-root migration evidence is preserved at [engineering/verification/history/single-root-migration.md](engineering/verification/history/single-root-migration.md).
