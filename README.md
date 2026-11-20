---
title: TradingBot
document_role: reference
lifecycle: maintained
owner: project-navigation
last_modified_at: 2026-11-20T11:55:09+03:30
---

# TradingBot

TradingBot is a Windows candlestick workstation for inspecting market history, drawing on charts, running indicators, and opening calculation reports. It can acquire candles from FARAZ and continue an applied indicator as confirmed candles arrive. The browser shows the chart and results. The local Vite server coordinates RAW files and calculation requests. The Python Engine owns trading calculations.

## Project ownership

| Owner | Responsibility |
| --- | --- |
| `apps/chart/` | Browser application, local HTTP/SSE server, application state and chart tests |
| `engine/` | Calculation bridge, stage owners, current exact-source references and local Engine verification |
| `scripts/` | Windows startup, GitHub release tooling, and repository verification |
| `engineering/` | Maintained documentation, historical archives and local verification evidence |

## Install and start

Run the Windows launcher from the repository root. It locates or installs the supported runtimes, checks Python dependencies, and installs Chart dependencies with the lockfile when needed. It starts the installed Vite CLI directly with the native configuration loader for compatibility with the VMware shared checkout.

```powershell
.\scripts\launch.bat
```

Open the URL printed by the launcher. For manual development on the local computer, use Node.js 20.19 or newer in the 20.x line, or Node.js 22.12 or newer. Use Python 3.12 or newer.

```powershell
python -m pip install orjson tzdata
Set-Location apps/chart
npm.cmd ci
npm.cmd run dev -- --host 127.0.0.1 --configLoader native
```

Build with `npm.cmd run build` from `apps/chart`. These commands keep generated output inside the project.

## Workstation workflows

- Open a RAW file in Chart, choose a display timeframe, and add drawings or apply an indicator to the full chart or a selected range.
- Use Real-time Chart to acquire confirmed candles and continue an indicator applied in the current tab. Apply and Live run a fresh calculation and share one active calculation slot by default. Set `TRADINGBOT_MAX_ENGINE_CONCURRENCY` to an integer from `1` to `8` before launch to change that limit.
- Open Manual Review from a completed calculation to inspect or export the saved report separately from the active Chart.
- Use FARAZ for acquisition and coverage decisions, Algorithm for the searchable reference, and Alerts to monitor configured rules against published live events. [Workstation controls and behavior](engineering/docs/architecture/ui-ux-reference.md)

In dev mode, saving a stylesheet or an indicator-renderer module updates the open chart. Saving a watched Python calculation file refreshes an already-applied indicator for its selected chart and range. The tab stays open when a change requires loading a new interface shell. The chart displays a notification for such changes. Dev mode polls the UI and active Python sources every 1,500 ms by default. Set `TRADINGBOT_VITE_POLLING=false` before starting Vite to disable this check, or set `TRADINGBOT_VITE_POLL_INTERVAL_MS` to adjust it with a 500 ms minimum.

## Local data

The default Chart state root is `apps/chart/state`. RAW and sidecars use `data/raw/`, drawings and saved reports and templates use `cache/`, FARAZ authentication uses `secret/`, and temporary files use `tmp/`. Set `TRADINGBOT_LOCAL_STATE_ROOT` to a descendant of this state root to isolate a workstation run or test. The launcher and server both enforce that boundary.

Git and release rules exclude machine-local state, credentials, installed dependencies, and fresh build output. Curated baseline data and classified engineering evidence can be tracked by the main branch. [Local State](engineering/docs/operations/local-state.md)

## Verify and publish

Run `npm.cmd test` from `apps/chart` for Chart unit checks. Discover the appropriate integration, browser, Engine and repository checks in [Testing](engineering/docs/development/testing.md).

The Git Manager entry point is `scripts\git\git.bat`. The maintained workflow validates candidates for `main` and the runtime-only `production` branch before publishing a tag and GitHub Release. [Release Operations](scripts/git/README.md)

## Documentation

Start with the [Engineering Documentation index](engineering/docs/README.md) and [root operating contract](AGENTS.md). Trading semantics are maintained through the Intelligence Plugin, canonical Knowledge Vault, and accepted Algorithm References. The [historical migration record](engineering/verification/history/single-root-migration.md) preserves the transition to the present directory layout.
