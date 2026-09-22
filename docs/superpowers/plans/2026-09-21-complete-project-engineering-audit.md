# TradingBot Complete Project Engineering Audit Plan

> **For agentic workers:** This is a documentation-only audit plan. Application source is read-only. Steps use checkbox syntax for traceable progress.

**Goal:** Produce a source-grounded, security-reviewed, fully traceable Digital Engineering Map of the current TradingBot repository without changing application behavior.

**Architecture:** Execute the audit in evidence waves: immutable baseline and inventory; source-first architecture reconstruction; frontend/UI mapping; manual and Codex Security review; optional runtime verification; documentation reconciliation; and final completeness accounting. Existing documentation and the dated Graphify snapshot are supporting evidence only; current source and directly observed runtime behavior remain authoritative.

**Tech Stack:** PowerShell, Git, native ES modules, Vite, Lightweight Charts, Node test runner, Playwright Core, Python, `Decimal`, `orjson`, Graphify, Superpowers, Codex Security, and Build Web Apps frontend verification.

**Spec:** `C:/Users/suwji/.codex/attachments/a1c88a48-1b16-46e6-ad52-8a4539e07c26/Pasted text.txt`

## Global Constraints

- Do not modify application source, algorithms, frontend behavior, styles, dependencies, configuration behavior, or runtime data.
- Preserve every pre-existing tracked and untracked change; never reset, clean, stash, rename, stage, or overwrite user work.
- Project writes are restricted to the required audit documentation and this plan. Update `AGENTS.md` only when a verified operational gap remains after the references are complete.
- Never reveal credentials, session values, tokens, keys, passwords, or private runtime-cache contents. Identify sensitive inputs by variable/file role and redact values.
- Every material claim must point to current source, current configuration, test evidence, or explicitly labeled runtime evidence.
- Mark uncertainty as `Not verified from current source`, `Not verified from current runtime`, or `External integration not verified`.
- Graphify output is supporting evidence. Validate important relationships directly in source and retain provenance labels.
- Codex Security runs in analyze-only mode. Validate every meaningful finding manually and do not apply fixes.
- Tests, builds, servers, and browser workflows run only after static review establishes that they are safe and relevant; record exact commands and exit status.

## Baseline

- Repository root: `//vmware-host/Shared Folders/My-Projects/TradingBot`
- Branch: `main`
- Starting `HEAD`: `9ad5a9021edb7e663751f692f173726850c05dda`
- Pre-existing dirty paths:
  - `AGENTS.md`
  - `apps/chart/src/main.js`
  - `apps/chart/vite.config.js`
  - `docs/TradingBot_Bearish_Algorithm_Reference.md`
  - `docs/TradingBot_Bullish_Algorithm_Reference.md`
  - `docs/TradingBot_Technical_Architecture.md`
  - `apps/chart/server/indicator-range-input.js`
  - `apps/chart/src/features/indicator-calculation-request.js`
  - `apps/chart/tests/indicator-calculation-request.test.mjs`
  - `apps/chart/tests/indicator-range-input.test.mjs`

## Completion Dashboard

| Workstream | Prompt stages | Status | Completion evidence |
|---|---:|---|---|
| Audit orchestration and baseline | 0-1 | Complete | Plan plus immutable Git baseline |
| Repository inventory and classification | 2-10 | Complete | 686-file inventory; 118 project-owned responsibility map |
| Dependencies and architecture | 11-14 | Complete | Source-verified dependency/runtime maps |
| Runtime, data, API, state, errors, performance | 15-22 | Complete | End-to-end source traces and labeled runtime evidence |
| Manual security and Codex Security | 23-26, 65 | Partial | Manual review complete; Deep Scan stopped at account usage limit without a manifest |
| Testing, build, and deployment | 27-29 | Complete | Fresh mirror build, tests, dependency audit and limitations |
| Frontend and page inventory | 30-36 | Complete | Complete page/tab/screen/component source map |
| Design system and UI components | 37-48 | Complete | Token, layout, state, motion, icon and accessibility evidence |
| Trading/special pages and responsive UI | 49-58 | Complete | Per-page references and page/backend/change matrices |
| Traceability and technical debt | 59-60 | Complete | Evidence-linked findings with confidence labels |
| Operational AI guide | 61-62 | Complete | `AGENTS.md` reviewed and intentionally unchanged |
| Coverage and final quality gates | 63-70 | Complete | 44-section architecture reference, 49-section UI reference, syntax checks, rendered checks and final Git comparison |

## Cross-Stage Dependencies

- File classification depends on the immutable inventory and Git ownership baseline.
- Runtime, API, and data-flow maps depend on entry-point and dependency tracing.
- Page documentation depends on route/tab discovery, DOM ownership, state ownership, and backend endpoint mapping.
- Security reconciliation depends on manual trust-boundary review and the completed Codex Security report.
- Runtime UI claims depend on safe server startup and rendered Browser evidence; static inspection alone cannot satisfy them.
- Final coverage status depends on the reviewed-file manifest, per-page matrix, security validation, and final Git comparison.

## Execution Tasks

### Task 1: Freeze the baseline and build the complete inventory

- [ ] Capture branch, `HEAD`, remotes, status, tracked files, untracked files, ignored/generated roots, and top-level metadata.
- [ ] Enumerate every file while excluding `.git` object storage from content review.
- [ ] Classify each path as project-owned, third-party, generated, runtime/user data, binary, documentation, test, fixture, or unknown.
- [ ] Record size, extension, subsystem, review status, and verification status for every project-owned file.
- [ ] Identify very large files and divide them into symbol/section review ranges.
- [ ] Reconcile inventory counts against Git tracked/untracked sets and document all exclusions.

### Task 2: Reconstruct configuration, dependencies, startup, and deployment

- [ ] Read manifests, lock files, launch scripts, Vite configuration, environment access, ignore files, editor files, and deployment/CI candidates.
- [ ] Trace `launch.bat -> start.ps1 -> Vite -> browser` and every mutation-capable bootstrap step.
- [ ] Distinguish installed dependencies from imported/used dependencies and record exact versions only when verified.
- [ ] Map production entry points, build outputs, host/port behavior, environment variables, and unavailable external deployment systems.
- [ ] Verify Graphify structural relationships with direct imports, calls, and route handlers.

### Task 3: Reconstruct backend, bridge, and deterministic pipeline architecture

- [ ] Read all project-owned server, bridge, and engine files, including every large detector in logical sections.
- [ ] Map HTTP/SSE endpoints, request validation, cache keys, persistence, subprocess/named-pipe transport, JSON contracts, and error propagation.
- [ ] Trace RAW input through chronology, Reaction, Blue, A, S, E, StopAll/lifecycle, serialization, cache, and frontend consumers.
- [ ] Record Decimal, strict-crossing, time-window, ordering, identity, provenance, null, and direction invariants.
- [ ] Map tests and fixtures to each critical backend subsystem and identify unprotected paths.

### Task 4: Reconstruct frontend architecture and every user-facing surface

- [ ] Read `index.html`, `main.js` in complete logical sections, every project-owned feature/chart/ui/drawing/algorithm module, and all styles/assets.
- [ ] Inventory every page, route, tab, workspace, panel, dialog, drawer, popover, menu, table, chart, toolbar, form, status view, loading state, empty state, and error state.
- [ ] Build component/DOM hierarchy, state ownership, local-storage/persistence, event wiring, API dependencies, and shared-consumer maps.
- [ ] Extract exact tokens, colors, typography, spacing, borders, radii, shadows, dimensions, breakpoints, z-index, motion, icon, focus, ARIA, and keyboard behavior.
- [ ] Create complete page-to-backend and page-change-impact matrices.

### Task 5: Perform manual security and performance review

- [ ] Trace applicable trust boundaries: HTTP input, file paths, RAW import/export, templates, sessions, external requests, subprocess arguments, named pipes, browser rendering, and persistence.
- [ ] Inspect secrets/environment/session handling without emitting values.
- [ ] Follow data flow to dangerous sinks before classifying any issue.
- [ ] Review dependency exposure from lock/manifests and actual imports.
- [ ] Identify performance-sensitive loops, scans, parsing, serialization, chart rendering, caching, indexing, batching, and large-data safeguards.
- [ ] Record confirmed findings separately from risks and improvement opportunities.

### Task 6: Complete and reconcile Codex Security

- [ ] Rejoin the existing repository-wide Deep Scan; do not launch a duplicate.
- [ ] When the coordinator returns, verify the canonical manifest, findings, and coverage artifacts and complete that scan exactly once.
- [ ] Manually validate every meaningful finding against current source, entry point, reachability, validation, trust boundary, impact, and existing protection.
- [ ] Classify findings as Confirmed, Likely but not fully verified, False Positive, Not Applicable, or Not verifiable from current source.
- [ ] Reconcile manual-only, Codex-Security-only, and overlapping findings; keep remediation as documentation only.

### Task 7: Verify safe build, test, and rendered runtime behavior

- [ ] Derive commands from current manifests/scripts before execution.
- [ ] Run the narrowest safe static checks and tests, then the full safe chart suite and build if they do not mutate source/user data.
- [ ] Define the UI flow: app loads -> chart workspace renders -> primary visible controls respond without relevant console/framework errors.
- [ ] Prefer the available Browser/computer-use path; capture page identity, DOM, console, screenshot, interaction, desktop, and mobile evidence.
- [ ] Label FARAZ/external service behavior unverified unless exercised safely without exposing session data.
- [ ] Record every command, exit code, environment, limitation, and generated artifact.

### Task 8: Expand and reconcile the required references

**Files:** `docs/TradingBot_Technical_Architecture.md`, `docs/TradingBot_UI_UX_Technical_Reference.md`.

- [ ] Preserve current user edits and merge source-verified corrections.
- [ ] Add the complete repository tree, folder map, file responsibility matrix, technology/dependency map, runtime/data/API/state/lifecycle/error/performance/testing/build/deployment/security sections.
- [ ] Add global UI architecture plus a dedicated complete reference for every discovered page/tab/screen.
- [ ] Add component, page/backend, shared-component, change-impact, and “Where To Make Changes” matrices.
- [ ] Include explicit unverified areas and exact evidence paths/symbols/lines where practical.
- [ ] Keep `AGENTS.md` concise; update it only if the completed references expose an operationally important verified gap.

### Task 9: Run completeness, documentation, and integrity gates

- [ ] Compare all 70 prompt stages with the final references and this dashboard.
- [ ] Reconcile repository inventory against reviewed and documented file matrices.
- [ ] Reconcile page/route/tab/screen inventory against per-page sections and backend dependencies.
- [ ] Re-read both references for internal consistency, stale claims, missing evidence, and unsupported certainty.
- [ ] Perform the Superpowers verification-before-completion gate with fresh commands.
- [ ] Compare final Git state with the baseline and list only intentional documentation changes plus preserved user changes.
- [ ] State `Full project review completed` only if every completion criterion is evidenced; otherwise report exact incomplete items.

## Open Questions and Unverified Areas

- Codex Security Deep Scan terminated after three discovery-worker failures caused by the account usage limit; no manifest or scanner findings were produced, and it was not retried or finalized.
- FARAZ external behavior and authenticated session-dependent flows remain `External integration not verified`.
- Two tests remain environment-limited: DPAPI is unavailable in the impersonated runner and the bundled Python lacks `orjson`.
- Runtime/cache and RAW contents were classified without exposing private values or performing full semantic review.
- The dated Graphify snapshot lags the dirty working tree; current relationships were verified directly in source because the CLI was unavailable.

## Execution Outcome

Tasks 1-5 and 7-9 were completed. Task 6 completed the manual reconciliation path but the native Deep Scan portion is incomplete for the terminal usage-limit reason above. The final references record that limitation and do not claim a successful or no-findings scan.

## Plan Self-Review

- Spec coverage: stages 0-70 are grouped in the completion dashboard and assigned to Tasks 1-9.
- Placeholder scan: no implementation placeholder is used; unresolved runtime/external/security evidence is explicitly listed.
- Interface consistency: inventory feeds architecture; architecture and manual review feed security; source maps feed UI/runtime verification; all workstreams feed final coverage.
- Review focus: dirty-tree ownership, complete file accounting, large-file coverage, scanner/source reconciliation, and static-versus-runtime evidence are explicit gates.
