# External local state

The chart and FARAZ servers share `apps/chart/server/local-state-paths.js`. They read `TRADINGBOT_LOCAL_STATE_ROOT`; the default is a sibling of the checkout named `<checkout-name>-Local`. The Windows launcher applies the same policy. An override may be absolute or relative to the checkout, but must resolve outside it.

```powershell
$env:TRADINGBOT_LOCAL_STATE_ROOT = 'D:\TradingBot-State'
.\scripts\launch.bat
```

| External path | Contents |
| --- | --- |
| `data/raw/` | Immutable candle arrays and metadata sidecars |
| `cache/drawings/` | Persistent user drawings |
| `cache/indicator-calculations/`, `cache/indicator-templates/` | Serialized calculations and user templates |
| `secret/` | FARAZ authentication state; never include in Git or reports |
| `tmp/faraz-candle-exports/` | Temporary acquisition/export files |

The cleanup migration preserves existing RAW, caches, templates, and authentication bytes. Historical regression/Graphify/source-recovery evidence is retained under `archive/` in the external root. Baselines, manifests, logs, and release packages also stay external. Any external `runtime/` directory preserves historical local state.

The launcher recreates required external state directories. Dependency/build commands may temporarily create ignored installation or build output within the checkout. Remove generated artifacts after validation when preparing a physically clean source-only repository.
