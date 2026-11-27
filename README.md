---
title: TradingBot
document_role: reference
lifecycle: maintained
owner: project-navigation
last_modified_at: 2026-11-27T06:27:55+03:30
---

# TradingBot

TradingBot is a Windows candlestick workstation for inspecting market history, drawing on charts, running indicators, and opening calculation reports. It can acquire candles from FARAZ and continue an applied indicator as confirmed candles arrive. The browser shows the chart and results. The local Vite server coordinates RAW files and calculation requests. The Python Engine owns trading calculations.

## Project ownership

| Owner | Responsibility |
| --- | --- |
| `apps/chart/` | Browser application, local HTTP/SSE server, application state and chart tests |
| `engine/` | Calculation bridge, stage owners, current exact-source references and local Engine verification |
| `scripts/` | Workstation startup, GitHub release tooling, and repository verification |
| `engineering/` | Maintained documentation, historical archives and local verification evidence |

## Install and start

Double-click [`scripts/launch.bat`](scripts/launch.bat) on Windows, or run the PowerShell launcher directly. On Windows, the launcher opens Chart in the default browser at the actual local URL after the HTTP readiness check passes.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Use `pwsh -NoProfile -File ./scripts/start.ps1` with PowerShell 7 on Linux. The runner shows the installed version, GitHub update status, checked runtime versions, and the server PID and uptime. An interactive ANSI terminal pins the local and IPv4 network addresses and keyboard shortcuts in a separate footer. Press **C** to copy the actual local address, **H** to check the current Chart HTTP response, **D** for runtime and state paths, or **E** to filter warnings and errors. Use **Page Up / Page Down** to review activity and **End** to follow the latest entries. Press **R** to restart Chart or **Q / Ctrl+C** to quit. The local URL becomes available once the server passes its HTTP readiness check. The server prefers port 5173, and browser storage is specific to the URL origin.

The launcher shows the installed release and the published `production` revision from the configured GitHub `origin`. Press **U** to check again. On a `production` checkout with a highlighted update, **U** downloads the selected revision, validates and applies its tracked runtime changes, and restarts TradingBot. The download bar reports the Git object percentage when Git supplies it. The update bar tracks the completed download, installation, and HTTP readiness milestones. Development checkouts report the production version and preserve their working files. The updater checks for local conflicts and advances only to a descendant revision while preserving workstation state.

Use `-Console` for plain, scrollable output, `-Loopback` to restrict Chart to this computer, or `-SkipUpdateCheck` to start without querying GitHub. The launcher installs missing Python packages and restores Chart dependencies from the lockfile. It can install the required Node.js and Python runtimes through winget on Windows. On Linux, install the host runtimes before starting the launcher. If Linux Python needs packages, the launcher creates a project-local virtual environment and uses that interpreter for the Engine.

For manual development on the local computer, use Node.js 20.19 or newer in the 20.x line, or Node.js 22.12 or newer. Use Python 3.12 or newer.

```powershell
python -m pip install orjson tzdata
Set-Location apps/chart
npm.cmd ci --include=dev
npm.cmd run dev -- --host 127.0.0.1 --configLoader native
```

Build with `npm.cmd run build` from `apps/chart`. These commands keep generated output inside the project.

## Workstation workflows

- Open a RAW file in Chart, choose a display timeframe, and add drawings or apply an indicator to the full chart or a selected range.
- Use Real-time Chart to acquire confirmed candles and continue the applied indicator. The chart restores its latest saved result for the selected timeframe. Apply and Live calculate from RAW and share one active calculation slot by default. Set `TRADINGBOT_MAX_ENGINE_CONCURRENCY` to an integer from `1` to `8` before launch to change that limit.
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
