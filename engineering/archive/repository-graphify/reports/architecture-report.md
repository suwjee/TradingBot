# architecture-report.md

**created_at:** `2026-09-30T15:43:03+03:30`
**last_modified_at:** `2026-09-30T15:43:03+03:30`

## Subsystem clusters

| Subsystem | Files | Ownership |
| --- | ---: | --- |
| AlgorithmReferences | 2 | Engine |
| Archive | 142 | EngineeringSupport |
| Chart | 41 | Chart |
| Chart-AlgorithmUI | 11 | Chart |
| ChartTests | 30 | Testing |
| Documentation | 10 | Documentation |
| Engine | 2 | Engine |
| EngineBenchmarks | 2 | Testing |
| EngineBridge | 2 | Engine |
| EnginePipeline | 10 | Engine |
| EngineRegression | 4 | Testing |
| EngineStyles | 1 | Engine |
| EngineUnitTests | 2 | Testing |
| EngineVerification | 2 | Testing |
| Governance | 2 | Documentation |
| GraphifyOutput | 44 | EngineeringSupport |
| LocalState | 51 | LocalState |
| RAWData | 39 | LocalState |
| ReleaseTooling | 9 | Tooling |
| Root | 3 | Project |
| Tooling | 3 | Tooling |
| Verification | 122 | EngineeringSupport |
| Vite | 2 | Vite |
| ViteServer | 8 | Vite |

## Dependency direction

```text
Chart UI  ->  Vite/transport  ->  Engine bridge/pipeline  ->  core/domain modules
   |               |                      |
   +---- tests ----+                      +---- tests/regression/benchmarks
   |
FARAZ acquisition (server) -> RAW/local-state stores
```

## Ownership summary

- Chart: 52 files
- Documentation: 12 files
- Engine: 17 files
- EngineeringSupport: 308 files
- FARAZ: 6 files
- LocalState: 86 files
- Project: 3 files
- Testing: 38 files
- Tooling: 12 files
- Vite: 10 files

## Lifecycle summary

- archive: 142 files
- generated-artifact: 44 files
- maintained: 92 files
- maintained-documentation: 11 files
- reference: 2 files
- runtime-data: 90 files
- test: 38 files
- verification: 125 files
