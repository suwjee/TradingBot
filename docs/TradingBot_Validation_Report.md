# TradingBot Validation Report

Validation date: 2026-09-20
Repository: `D:/My-Projects/TradingBot`  
Scope: safe, non-trading checks against the current dirty worktree. No orders, live FARAZ requests, production data writes, or application-source edits were performed by this audit turn.

## Range/Cut/Identity Addendum

Fresh release-candidate validation on the main checkout after integrating the chart-transfer, RAW-cut, chart-identity, report, drawing-tool, and indicator-range changes:

| Check | Result | Evidence |
| --- | --- | --- |
| Chart Node suite | PASS | `npm.cmd test`: 134 tests, 134 pass, 0 fail/cancelled/skipped; exit 0; 9.58 s. |
| Syntax | PASS | `node --check` for modified JS modules and `ast.parse` for `engine/bridge/trading_pipeline.py`; exit 0. |
| Production build | PASS | `npm.cmd run build`: Vite 8.2.1 transformed 54 modules; exit 0. Existing >500 kB bundle warning remains. |
| Vite/browser smoke | PASS | Local Vite on `127.0.0.1:5180` loaded successfully; Playwright verified `#cutCandlesBtn`, the scissors icon, `#cutCandlesModal`, and `#chartTransferModal`; no page errors. |
| RAW/chart contracts | PASS | Focused tests cover inclusive Cut, replace/new identity rules, metadata healing, range snapping, Measure math, and Long/Short levels. |
| Graphify | PASS | Fresh `graphify update . --no-cluster` rebuilt 2,672 nodes and 5,816 raw edges; `diagnose multigraph` reported zero missing/dangling endpoints and 15 self-loops. Generated `graphify-out/` was removed after diagnosis. |

The browser smoke used the local Chrome executable because the Browser plugin was unavailable in this environment.

## Status Summary

| Category | Status | Evidence |
| --- | --- | --- |
| JavaScript unit/contract tests | PASS | `npm.cmd test` from `apps/chart`: 134 tests, 134 pass, 0 fail/cancelled/skipped; exit 0; 9.58 s. |
| Production build | PASS | `npm.cmd run build -- --outDir <external temp>`: Vite 8.2.1 transformed 51 modules and exited 0. Output was written outside the repository. |
| JavaScript syntax | PASS | `node --check` over 63 project `.js`/`.mjs` files excluding vendored/build/temporary directories: 63 checked, 0 failed. |
| Python syntax | PASS | `ast.parse` over 12 `engine/**/*.py` files with `PYTHONDONTWRITEBYTECODE=1`: 12 checked, 0 failed. |
| Bridge CLI startup | PASS | `py -B engine/bridge/trading_pipeline.py --help` exited 0 and printed the request contract; it emitted the normal `QG_PROGRESS` startup event. |
| Python package import smoke check | FAIL | `py -B -c "import engine.pipeline"` fails because flat imports cannot resolve `direction_policy` from the package context. This is pre-existing migration state; source was not changed. |
| Engine numerical/integrated fixture run | NOT EXECUTED | No repository-local Python test/spec/fixture command exists, and executing a real calculation would require selecting a trading dataset and could mutate/cache runtime state. |
| Browser visual/a11y/integration run | NOT EXECUTED | No browser test script or configured browser harness is present; static/UI contract tests are covered by the Node suite. |
| Type checking | NOT APPLICABLE | No TypeScript/type-check configuration or package script was found. |
| Lint | NOT APPLICABLE | No lint script or repository-local lint configuration was found. |
| Static analysis | NOT EXECUTED | SonarQube CLI is not installed/authenticated, no SonarQube MCP tools are exposed, and the container runtime required by the documented fallback is unavailable. |
| Graphify generation | PASS | Graphify `0.9.63` / `graphifyy 0.9.42` rebuilt the dated directed snapshot; see below. |
| Graphify query/health validation | PASS | `graphify diagnose multigraph` reports 1,240 nodes, 2,774 directed links, zero dangling endpoints/self-loops/duplicate directed pairs; representative queries returned source-linked nodes. |
| Documentation/path validation | PASS | Required references and links were checked against the current tree; the uppercase root `AGENTS.md` remains authoritative and the pre-existing lowercase `agent.md` deletion was preserved. |
| Source integrity | PASS | The main checkout contains the integrated frontend/backend/engine changes, their contract tests, and the relocated current algorithm references; generated Graphify and plan/spec artifacts are excluded from the release. |

## Commands and Context

Commands were run with PowerShell from the repository root unless noted. `npm.cmd` was used to avoid PowerShell execution-policy issues. The build used a unique directory under the OS temporary folder, so it did not replace the pre-existing repository `dist` output. Graphify's task-owned intermediate run was moved intact under `docs/graphify/rebuild-2026-09-19/raw-run/` after the dated snapshot was verified.

## Graphify Evidence

The current snapshot is `docs/graphify/rebuild-2026-09-19/`. It was produced from the current worktree with Git-ignore handling and explicit directed graph construction because this CLI version rejects `--directed` on `graphify update`.

- Detection: 108 files, 88 code and 20 documents; one detector-classified sensitive file (`apps/chart/src/styles/tokens.css`) was skipped and manually covered by source review.
- Graph: 1,240 nodes, 2,774 directed links, 54 communities.
- Health: zero missing/dangling endpoints, self-loops, exact duplicates, or unverified nodes; one undirected endpoint collapse is diagnostic-only.
- Queries: module dependencies, UI-to-bridge communication, pipeline execution, engine calculations, Bullish logic, Bearish logic, and result propagation returned source-linked nodes. `application initialization` returned no matching node and remains an unresolved vocabulary/coverage limitation.

## Safety and Limitations

The passing JavaScript tests validate local contracts and data/state behavior, not live broker access or trading profitability. The build warning about a JavaScript chunk larger than 500 kB is retained as a performance finding. The package import failure is documented rather than repaired because production uses the dynamic bridge loader. SonarQube results cannot be claimed without an installed/authenticated CLI or MCP analysis.

## Final Integrity Gate

The final completion check confirms that the release includes the requested implementation files and tests, excludes generated `graphify-out/` and internal range-cut plan/spec artifacts, and passes the full Node suite, production build, JavaScript syntax checks, Python AST checks, and Graphify diagnosis.

## Release Gate Result

The `v2.1.0` release is prepared from the verified integrated tree. The application package remains `3.4.1`; repository release numbering is represented by the annotated Git tag `v2.1.0`, consistent with the architecture note that package and repository tag versions are separate. Commit and push evidence is recorded in Git after the release operations complete.
