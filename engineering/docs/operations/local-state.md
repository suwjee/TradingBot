# Project-local workstation state

All TradingBot-owned files stay inside the existing project root. The chart and FARAZ servers share `apps/chart/server/local-state-paths.js`; the Windows launcher invokes this same resolver after validating Node.js.

`TRADINGBOT_LOCAL_STATE_ROOT` defaults to `<project>/apps/chart/state`. Absolute and project-relative overrides are accepted only within this dedicated subtree. The resolver rejects external paths, source paths and junctions escaping the subtree.

```powershell
# Default state: no override is needed.
.\scripts\launch.bat

# Optional profile inside the same project.
$env:TRADINGBOT_LOCAL_STATE_ROOT = 'apps/chart/state/profile'
.\scripts\launch.bat
```

| Path below the state root | Owner and contents |
| --- | --- |
| `data/raw/` | Market candle arrays and metadata sidecars, preserving resource IDs and filenames |
| `cache/drawings/` | Persistent user drawings |
| `cache/indicator-calculations/`, `cache/indicator-templates/` | Serialized calculations and templates |
| `secret/` | FARAZ authentication; Git-ignored and never included in reports or delivery packages |
| `tmp/faraz-candle-exports/` | Temporary acquisition and export files on the same volume as RAW |

Vite denies direct static access to state, local tests and engineering archives/verification through both normal paths and `/@fs/`. State changes are excluded from the development watcher. Existing `/api` persistence and RAW response contracts remain active.

The 2026-09-29 migration moved the former sibling directory's data, caches and authentication into state without rewriting their contents. Historical archives moved to `engineering/archive/`; previous cleanup proof moved to `engineering/verification/history/cleanup-2026-09-29/`. The former `TradingBot-Local` directory was removed only after becoming empty. Root `scripts/` stays as a compatibility boundary for existing Windows and VMware startup commands.

RAW inventory APIs may regenerate metadata sidecars during ordinary use. That runtime behavior is distinct from the byte-preserving file migration. User-requested export destinations remain user-selected external deliverables, rather than the application's persistent state location.
