# TradingBot

TradingBot is a Windows-oriented local candlestick workstation. The chart application acquires and displays candles, drawings, indicators, and review tables. Python under `engine/` owns trading calculations; the browser renders serialized results.

## Repository

| Path | Purpose |
| --- | --- |
| `apps/chart/` | Vite application, browser source, and local HTTP/SSE server |
| `engine/bridge/`, `engine/pipeline/` | Calculation entry point and stage owners |
| `engine/algorithms/` | Current source-synchronized Bullish and Bearish references |
| `engine/styles/` | Styles imported by the chart application |
| `scripts/`, `docs/` | Windows startup and maintained engineering documentation |

Machine state resolves through `TRADINGBOT_LOCAL_STATE_ROOT`, defaulting to a sibling directory named `<checkout-name>-Local`. RAW and sidecars use `data/raw/` under that external root, persistent user state uses `cache/`, authentication uses `secret/`, and temporary exports use `tmp/`. The application rejects a state root inside the checkout. See [external local state](docs/operations/Local_State.md).

## Install and start

Use Node.js `20.19+` (Node.js 22 requires `22.12+`) and Python `3.12+`. Python dependencies are `orjson` and `tzdata`.

```powershell
python -m pip install orjson tzdata
cd apps/chart
npm.cmd ci
npm.cmd run dev -- --host 127.0.0.1 --configLoader native
```

The Windows launcher is `scripts/launch.bat`; it checks runtimes and installs missing dependencies before starting Vite. Build with `npm.cmd run build` from `apps/chart`. Dependency installations and build output are reproducible local artifacts excluded from Git.

## Local verification and engineering

Tests are intentionally local-only under ignored `/tests/`; a fresh GitHub clone does not include them. In the maintained local checkout, run `npm.cmd test` from `apps/chart` and `python -B -m pytest -q -p no:cacheprovider tests/engine/unit` from the repository root. See [local verification](docs/development/Local_Test_Workflow.md).

Read [AGENTS.md](AGENTS.md) and the [operating protocol](docs/development/TradingBot_AI_Operating_Protocol.md) before engineering work. Trading semantics require the TradingBot Intelligence Plugin and canonical Knowledge Vault. Use the [documentation index](docs/README.md) for current reference navigation. Historical documents retain their dated evidence limits.
