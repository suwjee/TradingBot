# TradingBot Technical Architecture Reference

**Audit snapshot:** 2026-09-22

**Repository:** `//vmware-host/Shared Folders/My-Projects/TradingBot`

**Branch / HEAD:** `main` / `9ad5a9021edb7e663751f692f173726850c05dda`
**Authority:** current working-tree source. Existing documents and Graphify are supporting evidence only.

## 1. Executive Summary

TradingBot is a local Windows-oriented candlestick workstation. A native-ES-module browser UI renders RAW candles and drawings, manages workspaces and indicator settings, and calls Vite middleware over local HTTP/SSE. Vite validates resource identifiers and requests, persists user state, and invokes the Python bridge. Python under `engine/` is the calculation authority for Reaction, Blue Line, A, S, E, StopAll, lifecycle visibility, and OrderAudit.

The checkout is intentionally dirty. This audit changed documentation only. It did not reset, stage, clean, rename, or modify application source or runtime data.

## 2. Evidence and Confidence Model

Evidence priority is: current source and lock files; fresh command output; rendered local runtime; tests; current generated structural artifacts; historical documentation. A claim is **verified** only when supported by one of the first four classes. External FARAZ behavior, authenticated workflows, production firewall posture, and deployment outside the local launcher remain unverified.

## 3. Repository Baseline

- Git remote: `origin https://github.com/suwjee/TradingBot.git`.
- Current package: `apps/chart` version `3.4.1`.
- Current repository count: 686 non-`.git` files.
- Current project-owned audit set: 118 files, including this audit plan; 430 installed dependency files, 44 Graphify artifacts, 52 runtime/cache files, and 14 RAW/sidecar data files are separately classified.
- Pre-existing dirty paths at audit start: `AGENTS.md`, `apps/chart/src/main.js`, `apps/chart/vite.config.js`, both directional reference documents, and four untracked indicator-range/request source or test files.
- Audit-created path: `docs/superpowers/plans/2026-09-21-complete-project-engineering-audit.md`; this file and the two required references are the only intended audit writes.

## 4. Coverage Accounting

All 118 project-owned files were inventoried and assigned a subsystem/role. Large orchestration and detector files were reviewed by symbols and logical ranges. Generated, third-party, runtime, and RAW content was classified rather than line-reviewed. Secret-file contents under `runtime/cache/secret` were not opened or emitted.

## 5. Repository Tree

```text
TradingBot/
├─ .editorconfig, .gitignore, AGENTS.md
├─ scripts/
│  ├─ launch.bat
│  └─ start.ps1
├─ apps/chart/
│  ├─ index.html, review.html, package.json, package-lock.json
│  ├─ scripts/dev-server.mjs
│  ├─ vite.config.js
│  ├─ server/                 # persistence, FARAZ, transfer, range transport
│  ├─ src/
│  │  ├─ main.js             # browser composition/state owner
│  │  ├─ algorithm/          # in-app algorithm reference
│  │  ├─ chart/              # state, LOD, coordinate and range contracts
│  │  ├─ drawings/           # drawing geometry and presentation
│  │  ├─ features/           # RAW, FARAZ, cache, review, sessions
│  │  ├─ platform/           # browser compatibility
│  │  ├─ styles/             # global tokens and layouts
│  │  └─ ui/                 # shared feedback, icons, popovers and identity
│  ├─ tests/                 # 27 Node test files / 147 tests
│  └─ node_modules/          # installed third-party dependencies
├─ engine/
│  ├─ bridge/trading_pipeline.py
│  ├─ pipeline/              # deterministic calculation authority
│  ├─ algorithms/            # standalone supporting references
│  └─ styles/
├─ data/raw/                 # authoritative user candle data and sidecars
├─ runtime/cache/            # drawings, templates, results, FARAZ session
└─ docs/                     # maintained references and Graphify snapshots
```

## 6. Folder Responsibilities

| Folder | Responsibility | Runtime authority |
|---|---|---|
| `scripts/` | Runtime checks, optional dependency installation, environment setup, Vite launch | Startup only |
| `apps/chart/src/` | Browser UI, interaction and presentation state | UI authority, not trading-rule authority |
| `apps/chart/server/` | File/session/FARAZ service modules | Persistence and integration authority |
| `apps/chart/vite.config.js` | Local API, SSE, cache and Python-process boundary | HTTP orchestration authority |
| `engine/bridge/` | Input normalization, pipeline orchestration and serialization | Calculation/API contract authority |
| `engine/pipeline/` | Deterministic indicator algorithms | Numerical authority |
| `data/raw/` | Candle arrays and metadata | User data |
| `runtime/cache/` | Mutable local state | User/runtime data |
| `apps/chart/tests/` | Node contract/regression tests | Verification only |
| `docs/graphify/` | Dated generated relationship evidence | Supporting, not authoritative |

## 7. Complete File Responsibility Matrix

The following compact matrix covers every current project-owned path. A comma-separated row means every named file was reviewed and has the stated role.

| Files | Responsibility |
|---|---|
| `.editorconfig`, `.gitignore` | Editing and repository exclusion policy |
| `AGENTS.md` | Canonical AI operating guide; reviewed, not changed by this audit |
| `scripts/launch.bat`, `scripts/start.ps1` | Windows bootstrap, runtime validation, optional install, host launch |
| `apps/chart/package.json`, `apps/chart/package-lock.json` | Package commands and resolved dependency graph |
| `apps/chart/index.html`, `apps/chart/review.html` | Main and manual-review HTML entry points |
| `apps/chart/scripts/dev-server.mjs` | Direct Vite development entry |
| `apps/chart/vite.config.js` | API/SSE/cache/Python middleware and `/info` fallback |
| `apps/chart/server/chart-transfer.js` | Chart bundle import/export validation |
| `apps/chart/server/faraz-candle-api.js` | FARAZ auth/history/export/update/coverage workflow |
| `apps/chart/server/indicator-range-input.js` | Full-path or Windows named-pipe indicator input |
| `apps/chart/server/migrate-raw-resources.js` | RAW migration dry-run/apply support |
| `apps/chart/server/raw-integrity.js` | RAW gap/integrity analysis |
| `apps/chart/server/raw-resource-store.js` | RAW validation, metadata, identifiers and atomic-ish writes |
| `apps/chart/src/main.js` | Main DOM, chart, state, events, drawings, indicator and workspace composition |
| `apps/chart/src/platform/browser-compat.js` | Browser feature normalization |
| `apps/chart/src/chart/state.js`, `progress.js` | Chart/request state and progress projection |
| `apps/chart/src/chart/lod.js`, `view-transform.js`, `zoom-config.js` | Large-data display reduction and coordinate/zoom contracts |
| `apps/chart/src/chart/drawing-coordinates.js`, `indicator-range.js` | Canonical drawing anchors and inclusive selected range |
| `apps/chart/src/drawings/drawing-math.js` | Drawing geometry/hit-testing |
| `apps/chart/src/drawings/drawing.css`, `object-tree.css` | Drawing and tree presentation |
| `apps/chart/src/features/candle-export.js` | FARAZ workspace UI and job polling |
| `apps/chart/src/features/candle-update.js` | Exclusive update modes, merge and bounded write batches |
| `apps/chart/src/features/faraz-symbol.js` | FARAZ symbol normalization |
| `apps/chart/src/features/indicator-cache.js`, `indicator-lifecycle.js` | Browser cache identity and result lifecycle |
| `apps/chart/src/features/indicator-calculation-request.js` | Request payload/range contract |
| `apps/chart/src/features/raw-file-contract.js`, `raw-inventory.js` | RAW filename/metadata and inventory UI contracts |
| `apps/chart/src/features/screenshot-overlay.js` | Screenshot overlay composition |
| `apps/chart/src/features/workspace-session.js` | Workspace persistence and restoration |
| `apps/chart/src/features/manual-review/entry.js`, `render.js`, `tab.js`, `review.css` | Manual-review transport, rendering, runtime and styles |
| `apps/chart/src/algorithm/page.js`, `mirror.js`, `styles.css` | Algorithm workspace routing, directional text reflection and styles |
| `apps/chart/src/algorithm/content/bridge-content.js`, `calculation-guides.js`, `content.js`, `glossary.js`, `i18n.js`, `module-summaries.js`, `object-catalog.js`, `type-module-summaries.js` | Source-backed in-app reference data |
| `apps/chart/src/styles/tokens.css`, `app.css`, `qg-modern.css`, `candle-export.css` | Tokens, shell, chart/panel and FARAZ visual system |
| `apps/chart/src/ui/chart-identity.js`, `symbol-format.js` | Stable chart identity and display formatting |
| `apps/chart/src/ui/feedback.js`, `log-window.js`, `popover.js`, `icons.js`, `workspace-state.js` | Shared feedback, logs, popovers, SVG icons and workspace header state |
| all 27 `apps/chart/tests/*.test.mjs` files | Contract tests for the same-named feature plus drawing tools and chart update |
| `engine/bridge/trading_pipeline.py` | CLI, dynamic loading, chronology, pipeline stages, visibility and JSON |
| `engine/bridge/test_trading_pipeline.py` | Bridge serialization regression test |
| `engine/pipeline/reaction_engine.py` | Bullish detector and reflected Bearish detector |
| `engine/pipeline/blue_line_detector.py` | Scale/Reset Blue and private state inputs |
| `engine/pipeline/a_zone_detector.py` | A formation and provenance |
| `engine/pipeline/s_zone_detector.py` | S candidate races and Order-stop reconciliation |
| `engine/pipeline/e_zone_detector.py` | Recursive E families and Order causes |
| `engine/pipeline/lifecycle_engine.py` | StopAll, ownership, history and visibility |
| `engine/pipeline/core_utils.py`, `direction_policy.py` | Decimal/Order identity and direction policy |
| `engine/**/__init__.py` | Python package markers |
| `engine/algorithms/*.md` | Supporting standalone algorithm references |
| `engine/styles/reaction-detector.css` | Historical/reference detector styling |
| `docs/TradingBot_*.md`, `docs/superpowers/plans/*.md` | Maintained architecture, algorithm, audit, validation and plan evidence |

## 8. Entry Points

- User startup: `scripts/launch.bat` -> `scripts/start.ps1`.
- Dev server: `apps/chart/scripts/dev-server.mjs` or `npm run dev`.
- Main page: `apps/chart/index.html` -> `src/main.js`.
- Review page: `/info` -> `review.html` -> `manual-review/entry.js`.
- Python CLI: `engine/bridge/trading_pipeline.py`.

## 9. Technology Stack

| Layer | Verified technology |
|---|---|
| Browser | Native ES modules, HTML/CSS, Lightweight Charts `5.2.1` |
| Local server/build | Node `20.19+` expected, Vite `8.2.1` |
| Browser automation | Playwright Core lock resolution `1.63.0` |
| Calculation | Python `3.12+` expected, `Decimal`, `orjson`, `tzdata` |
| Tests | Node built-in test runner; one Python `unittest` file |
| Structural support | Graphify CLI `0.9.63` / package `0.9.42` in dated snapshot; current CLI unavailable |

## 10. Dependency Architecture

`main.js` imports chart/feature/UI modules and Lightweight Charts. Vite imports the server modules and spawns Python. The bridge dynamically loads pipeline files to avoid the incomplete flat-package import surface. Python stages exchange typed dataclasses/objects, not browser-owned calculations. No React, database server, WebSocket, or production cloud deployment is present.

## 11. Startup and Runtime

`start.ps1` validates Node and Python versions, may install Node/Python dependencies, creates runtime directories, sets `TRADINGBOT_PYTHON` and `TRADINGBOT_PROJECT_ROOT`, then invokes Vite on `0.0.0.0` (`scripts/start.ps1:217`). These are environment/runtime mutations, so the audit used a temporary mirror and direct Vite launch on `127.0.0.1`.

## 12. System Architecture

```text
RAW JSON + sidecar
  -> Vite/raw-resource-store
  -> full RAW path OR in-memory selected rows via Windows named pipe
  -> Python bridge
  -> Reaction -> Blue -> A -> S -> E -> StopAll/lifecycle -> OrderAudit
  -> compact JSON stdout
  -> Vite cache/API + SSE progress
  -> browser overlays, tables, report and manual review
```

## 13. Backend Architecture

Vite middleware is an in-process local backend. It owns request-body limits, status codes, cache directories, file-store construction, Python spawning, SSE subscribers, and endpoint composition. `raw-resource-store.js` owns path containment, strict candle schema, OHLC/chronology checks, canonical names, SHA-256 metadata and writes. `faraz-candle-api.js` owns outbound allowlisting, login capture, job state, packet retries, bounded concurrency, coverage recovery and final persistence.

## 14. Frontend Architecture

`main.js` is the approximately 6,834-line composition/state owner. It creates the chart and drawing layer, loads inventory/candles, coordinates workspaces, renders indicator results, stores drawings, handles updates and opens manual review. Smaller modules isolate deterministic view contracts. The browser is a projection/interaction layer; it must not become a second trading-rule implementation.

## 15. End-to-End Data Flow

1. `/api/symbols` inventories RAW resources and returns metadata.
2. `/api/candles?id=...` returns validated candle rows.
3. Browser posts direction, analysis/chart timeframes, range and switches to `/api/reactions`.
4. Vite validates the inventory identity, constructs a source fingerprint/cache key and chooses full-file or selected-range transport.
5. Bridge normalizes candles and chronology, calculates enabled stages for dependent directions, reconciles visibility and serializes versioned collections.
6. Vite stores result/cache metadata and returns JSON; SSE reports progress.
7. Browser renders stage overlays, status, report and review snapshot.

## 16. HTTP and Communication Interfaces

The repository exposes 26 API route families plus `/` and `/info` (28 discovered HTTP routes). Methods are enforced inside middleware.

| Route | Purpose |
|---|---|
| `GET /api/symbols`, `GET /api/candles?id=` | RAW inventory and candle rows |
| `POST /api/reactions`, `GET /api/reactions/progress`, `DELETE /api/reactions/cache` | Calculation, SSE progress and cache reset |
| `GET /api/info/:symbol/:timeframe/:direction/:filename` | Saved result/report payload |
| `GET/PUT /api/drawings` | Drawing persistence |
| `GET/PUT /api/indicator-templates` | Template persistence |
| `GET /api/chart-transfer/export`, `POST /api/chart-transfer/import` | Bundle transfer |
| `POST /api/candle-files/delete|cut|migrate|update|verification` | RAW lifecycle and verification |
| `POST /api/faraz/auth/open|browser|logout`, `GET /api/faraz/auth/status` | FARAZ browser/session lifecycle |
| `POST /api/faraz/candles/start|cancel|coverage-decision|open`, `GET /api/faraz/candles/status|download` | Export job lifecycle |
| `POST /api/faraz/history` | Bounded history request |
| `/`, `/info` | Main application and manual-review page |

SSE is one-way progress; there is no WebSocket. Python is a child process using JSON stdout and `QG_PROGRESS:` stderr. Selected ranges use an ephemeral Windows named pipe; no second RAW file is written.

## 17. Core Data Structures

- RAW candle: integer Unix `time` plus numeric `open`, `high`, `low`, `close`; ordered, unique timestamps and valid OHLC envelope.
- RAW metadata: broker/symbol/timeframe, chart ID, readable Tehran bounds, hashes, counts, source and coverage data.
- Engine objects: Candle, Candidate, Reaction/Reset, BlueLine, AZone, SZone, EZone, StopAll and OrderAudit with physical indices/times, parent identities, cause objects and nullable provenance.
- Response: versioned stage collections, direction maps, lifecycle visibility, timings and input identity.

## 18. Numerical and Temporal Invariants

The engine uses `Decimal`; strict `<`/`>` crossings must not be relaxed. Windows are explicitly inclusive/exclusive by source contract. Physical source indices/times, ordering, nulls and provenance are observable behavior. Bearish uses reflected detector coordinates plus direction policy, not a blanket browser-side inversion. A known intentional Reaction asymmetry remains in the post-Reset same-Break branch.

## 19. State, Lifecycle and Ownership

Browser state includes selected RAW/chart identity, visible range, drawings, toolbar and workspace preferences, indicator settings/results, update progress and review snapshots. Engine lifecycle is separate: accepted A/S/E parents, exact stops, Order identity, consumed-S continuation, StopAll sequence ownership and historical visibility are reconciled before serialization.

## 20. Persistence

RAW and sidecars live in `data/raw`; drawings/templates/calculation cache and the FARAZ session live under `runtime/cache`. Browser preferences also use local storage. `raw-resource-store.list()` validates every RAW file and can rewrite stale/missing sidecars while servicing inventory (`raw-resource-store.js:152-177`), so a nominal GET has a metadata-repair side effect.

## 21. Cache Architecture

Calculation cache identity includes engine-source fingerprint, RAW identity/mtime, selected scope, chart/analysis timeframes, direction and Blue settings. Browser cache code separates source identity from display settings. Cache invalidation is explicit through the API/UI and through source fingerprint changes.

## 22. Error Handling

API handlers return JSON errors with bounded request-body parsing. The bridge prints progress to stderr and reserves stdout for JSON. UI errors flow to health state, toast/log surfaces and operation-specific status. FARAZ jobs keep error/cancel/coverage-decision states. Some broad catch blocks intentionally suppress malformed inventory entries; this favors continued listing but reduces diagnosis detail.

## 23. Logging and Observability

Observability consists of Vite console output, browser health/error logs, SSE indicator progress, FARAZ packet logs and bridge timings. There is no centralized telemetry service. Optional FARAZ response auditing writes response bodies to a temporary NDJSON file and therefore requires careful handling.

## 24. Performance Architecture

- Chart LOD activates for very large datasets and preserves raw coordinate anchors.
- RAW reads, JSON parsing, hashing and `list()` traversal are synchronous and can block the Node event loop for large inventories.
- Indicator cache avoids repeat Python work; selected ranges reduce input through memory/named pipe.
- FARAZ uses packet size 1,000, 30 ms scheduling, bounded concurrency and coalesced recovery gaps.
- Chart update batches writes with a 20 MB bound and merges chronologically without overwriting valid collisions.
- Current production bundle is 763.91 kB JS (219.08 kB gzip), triggering Vite's >500 kB warning.

## 25. Security Threat Model

Assets are RAW market data, drawing/templates, indicator outputs, FARAZ credentials/session state and local file integrity. Trust boundaries are browser-to-local HTTP, untrusted import/RAW JSON, local filesystem paths, Vite-to-Python arguments/pipe, local-to-FARAZ HTTPS and browser automation. Plausible attackers are a malicious webpage in the same user's browser, another LAN host when the launcher binds broadly, or another local process/user with filesystem access.

## 26. Validated Security Findings

| ID | Severity | Finding | Evidence and validation | Remediation direction |
|---|---|---|---|---|
| SEC-01 | High | Local service binds to all interfaces while mutation, deletion, browser-launch and session-dependent APIs have no application authentication | `start.ps1:217`; route registrations at `vite.config.js:291-664` and `faraz-candle-api.js:1235-1499`; no auth middleware found | Default to loopback; require an unguessable local session token and explicit LAN opt-in/firewall guidance |
| SEC-02 | High | FARAZ credentials and complete browser storage state are persisted as editable clear-text JSON despite a `.dpapi.json` name | `faraz-candle-api.js:414-477` writes `x-access-token`, cookie/storage state and history auth as JSON; POSIX mode hints do not provide DPAPI confidentiality on Windows | Use Windows DPAPI/Credential Manager; migrate v3; enforce ACLs and rotate exposed sessions |
| SEC-03 | Medium | State-changing endpoints do not enforce `Origin`/CSRF tokens; combined with broad binding, a malicious webpage can issue blind requests to local APIs | Manual source search across all middleware; body readers do not establish origin trust | Reject non-local/unknown origins, require token/header and narrow content types |
| SEC-04 | Medium | Unauthenticated status can disclose FARAZ profile identifiers to a reachable LAN client | auth status builds user ID/name/phone; UI consumes them in `candle-export.js:344-353` | Authenticate status, minimize returned identity and redact by default |
| SEC-05 | Low | Inventory GET performs synchronous full-file parse/hash and metadata repair, enabling availability pressure and a read-side write | `raw-resource-store.js:152-177`, called by `/api/symbols` | Separate repair from reads; cache inventory; bound files/bytes and schedule work |

Controls validated: RAW identifiers and paths are contained; candle schema/OHLC/chronology is checked; FARAZ hosts are allowlisted; Python arguments are constructed, not shell-concatenated; chart-transfer input is validated; `npm audit` found zero known dependency vulnerabilities. No command-injection or arbitrary SSRF path was confirmed.

## 27. Codex Security Deep Scan Status

The requested read-only Deep Scan started but stopped after three unsuccessful discovery workers because the account usage limit was reached. It returned no successful discovery manifest, no saved validated findings and no canonical coverage artifact. Per the scanner contract it was not retried, completed, or represented as a successful/no-findings scan. Scanner coverage is therefore **Incomplete**; SEC-01 through SEC-05 are manual, source-validated findings.

## 28. Dependency Security

Fresh `npm audit --json --fetch-retries=0 --fetch-timeout=15000` completed with exit code 0 and zero vulnerabilities across 42 dependencies. This is registry advisory coverage, not proof of application security. External font requests to Google Fonts expose client metadata and reduce offline reliability; self-hosting would reduce both concerns.

## 29. Testing Architecture

The 27 Node files contain 147 tests covering RAW validation/cut/inventory/store, FARAZ retry/coverage/session behavior, transfers, updates, range input, indicator cache/lifecycle/request, drawings, view transforms, review, screenshots, feedback, popovers, symbols and workspace state. A small Python bridge `unittest` covers serialization behavior. There is no repository CI workflow, unified Python test runner, lint task or type-check task.

## 30. Fresh Verification Results

To avoid UNC/npm and runtime-data side effects, `apps/chart` and `engine` were copied to a temporary local mirror.

| Check | Result |
|---|---|
| Vite production build | PASS, exit 0; 55 modules; 575 ms; bundle-size warning only |
| Node tests with explicit bundled Python | PARTIAL: 145/147 pass |
| Remaining test 1 | Windows DPAPI CurrentUser unavailable in the runner's impersonated context |
| Remaining test 2 | Bundled Python lacks `orjson` for one subprocess-based end-boundary test |
| npm audit | PASS, zero known vulnerabilities |
| Browser smoke | PASS for main, Algorithm, FARAZ, `/info`, 360 px responsive DOM and zero captured console warning/error |

No dependency was installed and no failure is claimed as an application defect without a compatible runtime rerun.

## 31. Build and Deployment

`npm run build` emits Vite static assets. `npm run dev`, `preview`, and `start.ps1` launch services; `start.ps1` can also install dependencies and create runtime directories. No Dockerfile, service unit, cloud manifest, release workflow or CI configuration exists. Production deployment topology is not defined in current source.

## 32. Coding Conventions

JavaScript uses native ESM, semicolons and small pure helper modules around a large composition root. Python uses dataclasses, explicit version constants, dynamic loading and Decimal conversion helpers. Public contracts preserve snake/camel case as serialized. Errors are user-oriented sentences. Tests use Node's `test`/`assert` and temporary directories.

## 33. Graphify Evidence

The newest checked-in snapshot is `docs/graphify/rebuild-2026-09-19/`: 1,240 nodes, 2,774 directed links and 54 communities, with no duplicate/self/dangling links in its health report. It was built at an older commit and skipped `tokens.css` as sensitive. The current Graphify CLI was unavailable, so current relationships were confirmed by imports, handlers and calls rather than regenerated.

## 34. Large Files

Large source was reviewed by logical sections: `main.js` 6,834 lines; `trading_pipeline.py` 1,918; Reaction 2,376; S 1,344; E 2,690; lifecycle 1,645; FARAZ server 1,546. Generated Graphify HTML/JSON, lock files, RAW datasets and dependencies were classified rather than treated as handwritten logic.

## 35. Sensitive Data Handling

The audit identified the FARAZ session path and data categories but did not read or print the file. No token, cookie, phone, credential, password or session value is present in this reference. Optional response-audit and exported RAW files should be treated as sensitive operational data.

## 36. Change Impact Map

| Desired change | Primary owner | Mandatory consumers/tests |
|---|---|---|
| Indicator math | `engine/pipeline/*` | bridge serializers, lifecycle, all dependent stages, chart tests/sanity data |
| Payload contract | `trading_pipeline.py` | Vite cache/API, `main.js`, manual review, algorithm catalog |
| Selected range | range request + named-pipe modules | `/api/reactions`, bridge chronology, range tests |
| RAW schema/name | raw contract/store | inventory, update, FARAZ, transfer, cut/migration tests |
| FARAZ coverage | `faraz-candle-api.js` | exporter UI and FARAZ tests |
| Drawing coordinates | chart/drawing modules | main canvas, persistence, drawing tests |
| Global layout/token | style files | all workspaces and responsive/browser checks |
| New endpoint | Vite/FARAZ middleware | frontend consumer, security origin/auth controls and tests |

## 37. Where to Make Changes

- Calculation semantics: start in the relevant `engine/pipeline` detector and trace through bridge/lifecycle.
- Browser calculation request: `indicator-calculation-request.js`, `main.js`, `vite.config.js`, then range transport.
- RAW storage: `raw-file-contract.js` and `raw-resource-store.js`.
- FARAZ networking/coverage: `faraz-candle-api.js`; UI in `candle-export.js`.
- Chart/drawing UX: `main.js`, the relevant `chart/` or `drawings/` helper, then CSS.
- Manual report: `manual-review/render.js`, with bridge payload ownership respected.

## 38. Technical Debt and Inconsistencies

- `main.js` and several engine/server files are high-coupling, high-review-cost modules.
- Python flat-package imports are not a supported smoke path; the bridge works around migration state with dynamic loading.
- The FARAZ v3 filename implies DPAPI while the content is plaintext.
- `rawStore.list()` mixes read, validation, hashing and repair writes.
- Default LAN binding is inconsistent with unauthenticated local-control endpoints.
- In-app algorithm `AUDITED_FILES` line/version metadata is stale relative to current engine source.
- AGENTS baseline commit and several engine versions are stale relative to current source.
- No CI, lint, type check, browser regression suite or supported complete Python environment is declared.

## 39. Open Questions

1. Is LAN exposure intentional, and what trusted network/firewall policy is required?
2. Should FARAZ session persistence return to DPAPI CurrentUser or use Credential Manager?
3. What Python environment is the supported test/runtime authority, including `orjson`?
4. Should inventory repair become an explicit maintenance operation?

## 40. Unverified Areas

Authenticated FARAZ login/history, real market downloads, saved-session migration, Windows shell-open behavior, production network/firewall posture, indicator correctness against an independent oracle, complete high-volume chart performance, and any deployment outside local Vite were not verified at runtime.

## 41. Operational Versions

Current source constants: bridge `1.4.0`, Reaction `9.6.0`, Blue `2.3.0`, A `1.6.3`, S `4.14.0`, E `6.8.0`, StopAll/lifecycle `1.12.0`, core/direction policy `1.0.0`.

## 42. AGENTS.md Review

`AGENTS.md` remains the canonical operating guide and correctly emphasizes dirty-tree preservation, Python authority, Decimal/strict crossing semantics, browser evidence and secret protection. Its commit/test-count/version snapshot has drifted, but the durable operating rules are sound. It was left unchanged because the user prohibited project-file changes beyond the required audit documentation and no new operational rule was necessary.

## 43. Traceability Index

- Startup: `scripts/launch.bat`, `scripts/start.ps1`.
- API/process/cache: `apps/chart/vite.config.js`.
- RAW: `server/raw-resource-store.js`, `raw-integrity.js`, frontend raw modules.
- FARAZ: `server/faraz-candle-api.js`, `src/features/candle-export.js`.
- Browser: `src/main.js`, chart/feature/UI modules and styles.
- Engine: `engine/bridge/trading_pipeline.py`, `engine/pipeline/*.py`.
- Tests: `apps/chart/tests/*.test.mjs`, `engine/bridge/test_trading_pipeline.py`.
- UI details: `docs/TradingBot_UI_UX_Technical_Reference.md`.

## 44. Completion Statement

Repository inventory, project-owned review, architecture reconstruction, manual security validation, safe build/test/browser checks and both required references are complete. Codex Security Deep Scan coverage is incomplete because its workers hit the account usage limit and produced no canonical manifest. Runtime verification is partial for authenticated FARAZ and the two environment-dependent tests. No production-readiness claim is made.
