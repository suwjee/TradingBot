# ownership-report.md

**created_at:** `2026-09-30T15:43:03+03:30`
**last_modified_at:** `2026-09-30T15:43:03+03:30`

## Ownership model (AGENTS.md-aligned)

| Owner | Scope |
| --- | --- |
| Engine | `engine/pipeline`, `engine/bridge`, algorithm implementation |
| Chart | `apps/chart/src` presentation/UI |
| Vite | `apps/chart/vite.config.js`, `apps/chart/server` transport/orchestration |
| FARAZ | external market-data acquisition modules |
| Testing | `**/tests/**`, regression, benchmarks, verification helpers |
| Documentation | `engineering/docs`, root `AGENTS.md` / `README.md` |
| Tooling | `scripts/**` |
| EngineeringSupport | `engineering/verification`, `engineering/archive` |
| LocalState | `apps/chart/state/**` |
| External | `node_modules` (excluded from source scan by rule) |

## Counts

- Chart: 52
- Documentation: 12
- Engine: 17
- EngineeringSupport: 308
- FARAZ: 6
- LocalState: 86
- Project: 3
- Testing: 38
- Tooling: 12
- Vite: 10

## Classification is rule-based

Ownership is determined from live path/subsystem rules and AGENTS.md boundaries, not filename guesses alone. New files under known roots inherit ownership automatically.
