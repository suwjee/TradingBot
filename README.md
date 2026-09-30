# TradingBot

TradingBot is a Windows candlestick workstation. The chart application acquires and displays candles, drawings, indicators and review tables. Python under `engine/` owns trading calculations; the browser renders serialized results.

## Project ownership

| Owner | Responsibility |
| --- | --- |
| `apps/chart/` | Browser application, local HTTP/SSE server, application state and chart tests |
| `engine/` | Calculation bridge, stage owners, current exact-source references and local Engine verification |
| `engineering/` | Maintained documentation, historical archives and local verification evidence |

The root `scripts/` directory preserves the public Windows startup paths used by existing shortcuts and the VMware shared checkout. Root Git/editor files, `AGENTS.md` and this README stay at their tool discovery boundaries.

**Every project-owned file stays inside this TradingBot directory.** RAW and sidecars use `apps/chart/state/data/raw/`, persistent drawings/calculations/templates use `apps/chart/state/cache/`, FARAZ authentication uses `apps/chart/state/secret/`, and temporary files use `apps/chart/state/tmp/`. State, component tests, archives, verification output, dependencies and build output remain Git-ignored. See [local storage](engineering/docs/operations/local-state.md).

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

Tests are intentionally local-only under `apps/chart/tests/` and `engine/tests/`; a fresh GitHub clone requires the local test bundle. Run `npm.cmd test` from `apps/chart` and `python -B -m pytest -q -p no:cacheprovider -p no:benchmark engine/tests/unit` from the root. See [local verification](engineering/docs/development/local-tests.md).

Read [AGENTS.md](AGENTS.md) and the [operating protocol](engineering/docs/ai/operating-protocol.md) before engineering work. Trading semantics require the Intelligence Plugin and canonical Knowledge Vault. The [engineering document index](engineering/docs/README.md) and [single-root migration report](engineering/docs/verification/single-root-migration.md) describe current navigation and the dated migration evidence.
