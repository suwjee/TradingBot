# TradingBot Project Audit

Audit date: 2026-09-18  
Method: read-only source and artifact inspection, full-file inventory, Graphify, bounded data validation, independent agent analysis, and command-based validation  
Implementation changes made by this task: none

## 1. Executive Assessment

TradingBot has a clear calculation boundary: the browser owns acquisition, interaction, persistence, and rendering; Python owns `Reaction -> Blue Line -> A -> S -> E -> StopAll`. The current working implementation contains strong deterministic data handling, explicit versioning, Decimal-based price logic, strict RAW validation, stage telemetry, large-dataset LOD, and broad JavaScript tests.

The checkout is not presently reproducible from Git alone. The runtime configuration points to untracked replacement engine modules while the tracked legacy modules are deleted. This is the dominant release risk and is pre-existing user work; the present documentation task does not alter or stage it.

## 2. Scope and Evidence

- Starting HEAD: `0d084590fb1ba1b57bcac6d4f19c977557830c2d`.
- Branch: `main`, initially two commits ahead of `origin/main`.
- Initial working tree: 34 tracked source changes/deletions and 55 untracked paths before task artifacts.
- Graphify extraction checkpoint: 620 non-Git files. Final post-cleanup inventory: 619 non-Git files, each recorded with path, size, role, and SHA-256 in `docs/graphify/full-file-inventory.json` (the inventory's own hash is intentionally self-referential/null).
- No project file was excluded as sensitive. `skipped_sensitive=0`.
- Credential/session values were not reproduced; their container schema, role, reference paths, and storage format were inspected.

Inventory groups at the historical 2026-09-18 full-scan checkpoint (not the current one-file RAW inventory):

| Group | Files | Interpretation |
|---|---:|---|
| Vendored dependencies | 430 | Installed `node_modules`; not project-owned logic |
| Project implementation | 108 | Historical full-scan grouping; the current dated Graphify rebuild classifies 88 code files and 20 documents separately |
| Runtime cache | 41 | Drawings, calculations, templates, session, bytecode |
| Graphify/task artifacts | 19 | In-progress generated analysis files at checkpoint |
| RAW market data | 9 | Four candle arrays, four sidecars, placeholder |
| Documentation | 6 | Existing algorithm documents and task documents at checkpoint |
| Generated/accidental build artifacts | 5 | `dist`, Vite cache, and mirrored-path artifacts |
| Repository metadata | 2 | `.editorconfig`, `.gitignore` |

## 3. Architecture Strengths

### 3.1 Deterministic calculation authority

`engine/bridge/trading_pipeline.py` loads explicit engine modules, normalizes prices with `Decimal`, constructs a full market context, calculates the entire physical RAW file, and limits only final visibility to the requested range. This avoids browser-side rule duplication and reduces range-boundary drift.

### 3.2 Direction-aware shared context

The bridge calculates both directions when S/E behavior requires opposite-direction reactions, resets, order geometry, or shared ownership. This is more faithful than treating Bullish and Bearish as isolated single-pass calculations.

### 3.3 RAW integrity controls

`apps/chart/server/raw-resource-store.js` validates exact row structure, numeric OHLC, chronology, logical identifiers, and traversal boundaries. RAW data and sidecars use atomic temporary-file replacement. The current active `FOREXCOM/XAUUSD` file contains 70,125 candles and passed bounded integrity validation; its sidecar SHA-256, size, and count matched the data file. The four-file totals recorded in the historical checkpoint are not current inventory.

### 3.4 Explicit telemetry

The Python bridge emits structured `QG_PROGRESS` events. Node separates progress from ordinary stderr and publishes status through SSE. Response timing/version metadata supports diagnosis of stage costs and stale cached payloads.

### 3.5 Large-chart controls

The browser retains RAW candles as authority and uses LOD only for display. View transforms use indexed/binary-search-style logic rather than assuming perfectly uniform timestamps.

### 3.6 JavaScript test coverage

The current tree contains 21 Node test files and 111 declared test cases covering RAW storage/integrity, FARAZ behavior, workspace state, chart updates, indicator cache/lifecycle, view transforms, drawings, popovers, feedback, and manual review.

## 4. Critical and High Findings

### A-01 — Current runtime is not reproducible from the committed tree

Severity: Critical  
Evidence:

- Tracked files such as `engine/bridge/reaction_bridge.py` and the legacy `engine/pipeline/{reaction,blue_line,a_zone,s_zone,e_zone,stop_all}.py` are deleted in the working tree.
- Active replacements including `engine/bridge/trading_pipeline.py` and detector/engine modules are untracked.
- `apps/chart/vite.config.js` and `scripts/start.ps1` already reference the replacements.

Impact: a fresh checkout of HEAD does not contain the runtime currently being documented and validated. This task preserves the user-owned changes and does not add them to the documentation-only release commit.

### A-02 — LAN-bound mutation surface has no application authentication layer

Severity: High  
Evidence: `scripts/start.ps1` binds Vite to `0.0.0.0`; Vite middleware exposes deletion, migration, update, drawing/template write, cache/session deletion, FARAZ browser/session, export, and calculation routes. No application authentication, CSRF token, or origin/referer authorization layer was found.

Impact: any client that can reach the local server may be able to invoke mutation-capable APIs. This is a static source finding; network reachability was not tested.

### A-03 — Session envelope is clear text

Severity: High  
Evidence: `runtime/cache/secret/faraz-session.dpapi.json` is a version-3 clear-text envelope despite the DPAPI-oriented filename. The file contains session/cookie/storage-state fields. Values are intentionally omitted from this report.

Impact: filesystem access can expose an authenticated browser session.

### A-04 — Calculation cache identity is not content-hash based

Severity: High  
Evidence: calculation cache identity includes RAW logical identity and `mtimeMs`, while RAW sidecars already carry a content SHA-256.

Impact: if RAW content changes while mtime is preserved or restored, stale calculations can be selected.

### A-05 — Read inventory can write metadata

Severity: High  
Evidence: `/api/symbols` calls inventory/list logic; RAW listing can repair/rewrite sidecar metadata through atomic writes.

Impact: a nominal read request has disk side effects and scales with complete RAW validation/hashing.

## 5. Medium Findings

### A-06 — Some writes are non-atomic

Calculation payloads, drawing files, and templates use direct writes. Process interruption can leave truncated JSON. RAW data/metadata are stronger because they use temporary-file replacement.

### A-07 — Workspace-root resolution is inconsistent

Local-data paths derive from module location, while `createFarazCandleApi()` defaults from `process.cwd()/../..`. The launcher starts in the expected directory, but alternative manual invocation can redirect session/raw/temp paths. `TRADINGBOT_PROJECT_ROOT` is set by the launcher but unused.

### A-08 — Startup is mutating and Windows-specific

`scripts/start.ps1` can install Node/Python/packages and create directories. It also uses interactive Windows behavior. It should not be presented as a pure validation command.

### A-09 — No standard Python dependency/test contract

Python requirements exist as launcher literals. No `pyproject.toml`, `requirements.txt`, lockfile, or Python test suite exists for approximately 8,000 lines of active engine/bridge code.

### A-10 — Large ownership hotspots

Approximate current sizes:

- `apps/chart/src/main.js`: 6,503 lines.
- `apps/chart/server/faraz-candle-api.js`: 1,547 lines.
- `engine/pipeline/e_zone_detector.py`: 2,520 lines.
- `engine/pipeline/reaction_engine.py`: 2,436 lines.

These are not defects by themselves, but they increase coupling, review cost, and regression risk.

### A-11 — Generated artifact drift

- `apps/chart/dist` is not proven equivalent to current working source.
- Five calculation caches carry Reaction versions 9.4.2–9.4.4, older than current 9.5.2.
- Stale CPython bytecode exists for deleted legacy modules.
- `apps/chart/ Folders/.../.vite/deps` is an accidental-looking mirrored path with generated metadata; origin is not proven.

Historical artifacts must not be treated as current-engine truth.

### A-12 — Package surface does not reflect full pipeline ownership

`engine/pipeline/__init__.py` still presents a Blue-Line-oriented package interface while the directory now contains the complete calculation chain. Dynamic loading bypasses the package API.

### A-13 — Stage-completion telemetry can appear on failures

`trading_pipeline.py:timed()` records completion in `finally`. A stage that raises can therefore emit a completion timing before the final failure event.

## 6. Trading Engine Findings

- Current sequence is not a single linear pass. Later stages use opposite-direction state and E can run multiple reconciliation passes; StopAll/lifecycle detection itself runs once after the final E state.
- Complete physical RAW context is processed before final visibility filtering.
- `Open <= Close` is the maintained GREEN/doji rule.
- `Asia/Tehran` is the display/temporal contract.
- Price comparisons use `Decimal`; converting rule calculations to binary floats would change observable semantics.
- Bullish and Bearish are implemented through shared abstractions plus explicit directional policy, but correctness must still be checked independently.
- Cached payload equality cannot be inferred from counts alone; arrays, order audit, versions, ordering, and serialized content matter.

Detailed stage rules are documented in the directional algorithm references.

## 7. UI/UX Findings

- The UI is a dense, chart-first desktop workstation using neutral light surfaces and compact controls.
- `apps/chart/src/styles/tokens.css` is the design-token authority.
- Core colors include accent `#2962ff`, chart Bullish `#089981`, chart Bearish `#f23645`, canvas `#f5f7fa`, and surface `#ffffff`.
- Primary responsive thresholds occur at 1180, 900, 760, 520/490/440/420/400, plus algorithm/review-specific thresholds.
- The z-index scale is tokenized from chart `1` through toast `120`.
- Focus-visible rules, reduced-motion overrides, touch targets, semantic controls, and mobile panel transformations exist, but mobile support is adaptive rather than a separate mobile application.
- `src/main.js` remains a UI/state ownership hotspot.

## 8. Dependency and Supply-Chain Findings

Direct manifest dependencies are intentionally small: Lightweight Charts, Playwright Core, and Vite. The installed tree includes transitive Rolldown, Lightning CSS, PostCSS, source-map, globbing, native bindings, fonts, WASM, and generated Playwright UI assets. All vendor files were included in the full inventory; they are not described as project-owned behavior.

No dependency upgrade was performed. No vulnerability result is claimed unless the validation report records an executed command.

## 9. Data Findings (historical checkpoint)

| Dataset | Candles | Cadence | Integrity result |
|---|---:|---:|---|
| FOREXCOM XAUUSD | 161,376 | 1 s | Schema/OHLC/order/duplicates/sidecar hash PASS |
| FXCM USOIL (Sep 8–12) | 57,963 | 5 s | PASS |
| FXCM USOIL (Sep 11–17) | 68,489 | 5 s | PASS |
| FXCM USOIL (Sep 16–17) | 15,237 | 5 s | PASS |

Gaps exist in all datasets. They are reported as coverage characteristics, not integrity failures, because market closures, provider coverage, and acquisition boundaries can be legitimate causes.

The table above is retained as historical evidence from the 2026-09-18 checkpoint. At the 2026-09-19 continuation checkpoint, only the `FOREXCOM/XAUUSD` 5-second file and sidecar are present under `data/raw`, with 70,125 candles. The current file passed the same bounded integrity checks; no claim is made that the historical FXCM files still exist in the current tree.

## 10. Documentation Drift

- Existing root-of-engine algorithm documents are extensive historical/normative references and predate parts of the current refactored file layout.
- Frozen V4.0.1 references remain useful for intent/completeness comparison but are not runtime authority.
- Cached payloads and bytecode expose earlier module versions and filenames.
- The new `docs/TradingBot_*` references use current paths and version constants and explicitly distinguish source facts from historical documentation.

## 11. Cleanup Decision

No pre-existing file is deleted by this task. Several artifacts are likely disposable, but the dirty-tree migration and user requirement to examine every file make retention safer:

- `apps/chart/ Folders/.../.vite/deps` — probable accidental cache, retained because origin is unproven.
- `engine/**/__pycache__` — stale/generated, retained as pre-existing user state.
- `apps/chart/dist` — generated and possibly stale, retained because deployment usage is not proven absent.
- `runtime/cache/**` — historical/runtime state, retained because it contains user data and diagnostic evidence.
- `node_modules` — reinstallable, retained because it supports current validation without dependency mutation.

## 12. Validation Limits

Static source inspection does not prove external FARAZ availability, browser compatibility, live session behavior, network isolation, or identical current engine outputs. Those results are reported only if corresponding commands were executed successfully in `TradingBot_Validation_Report.md`.

## 13. Current-turn corroboration (2026-09-19)

The independent read-only workstreams and fresh checks corroborated the following additional risks. They remain documentation findings; no implementation was changed.

### A-15 — Calculation cache fingerprint omits shared policy modules (confirmed)

`apps/chart/vite.config.js` fingerprints the bridge and six detector files for calculation caching, but the active bridge imports shared `engine/pipeline/core_utils.py` and `engine/pipeline/direction_policy.py`. A change to either shared module can therefore leave an apparently valid cache entry. The current cache key also uses RAW `mtimeMs`, so a content rewrite that preserves a timestamp remains a stale-result risk. Evidence: `vite.config.js` source-fingerprint construction and `engine/bridge/trading_pipeline.py` dynamic module loading.

### A-16 — Clear-text FARAZ credential persistence (confirmed)

`apps/chart/server/faraz-candle-api.js` persists `x-access-token`, `farazSession`, and storage state in an editable clear-text JSON envelope at `runtime/cache/secret/faraz-session.dpapi.json`. The API reports `credentialStorage: 'Editable clear-text secret cache'`. The filename is not encryption evidence. The local server is also launched on `0.0.0.0` without an application authentication/CSRF boundary around destructive cache, drawing, template, calculation, and session endpoints.

### A-17 — Package import surface is broken during the engine migration (confirmed)

`py -B -c "import engine.pipeline"` fails with `ModuleNotFoundError: direction_policy`; adding the flat pipeline directory then exposes a second `ImportError` for the missing `run_blue_line` export. The production bridge currently avoids this package import path through dynamic file loading. This is a release/reproducibility defect in the current dirty worktree, not a reason to alter source in a documentation audit.

### A-18 — Read and write paths have inconsistent atomicity (confirmed)

RAW resources use atomic temporary-file replacement in `raw-resource-store.js`, while drawings, templates, and calculation cache payloads in `vite.config.js` use direct `fs.writeFileSync` calls. An interruption can leave truncated JSON in those non-RAW stores. `/api/symbols` also calls a listing path that may rewrite sidecar metadata, so an inventory read has disk side effects and full-file hashing cost.

### Graphify evidence boundary

The dated directed rebuild under `docs/graphify/rebuild-2026-09-19/` is internally healthy but intentionally code-focused. Graphify classified `apps/chart/src/styles/tokens.css` as sensitive and skipped it; the UI review covers that file directly. Graph queries are useful navigation evidence, not proof of behavior. The top-level historical graph includes vendored/generated dependencies and should not be treated as a current implementation snapshot without checking its manifest date and commit.

## 13. Recommended Remediation Backlog

This audit does not implement these actions.

1. Resolve and commit the intended runtime migration as a separate source release with full review.
2. Add an application authentication/origin policy before LAN exposure.
3. Protect or remove clear-text session persistence and align the filename with the actual format.
4. Make calculation cache identity content-hash based.
5. Separate read-only inventory from metadata repair.
6. Add atomic writes to calculations, drawings, and templates.
7. Establish Python dependency locking and an engine test suite.
8. Reduce central-module ownership through carefully tested decomposition.
9. Define generated-artifact retention and reproducibility policy.
10. Make `TRADINGBOT_PROJECT_ROOT` the single runtime-root authority.
