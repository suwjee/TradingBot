# TradingBot v2.0.0 Stable Audit and Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruct and document the existing TradingBot implementation, generate a verified Graphify model, conservatively clean only proven disposable non-code artifacts, validate the unchanged source tree, and publish an annotated `v2.0.0` stable checkpoint.

**Architecture:** The repository implementation remains read-only. Independent agents inspect architecture, trading-engine behavior, UI/UX, and Bullish/Bearish algorithms; the coordinating agent reconciles every claim against source, generates the required English documentation and Graphify artifacts, then conducts independent review and fresh validation before staging only permitted paths.

**Tech Stack:** Existing repository languages and tools as discovered from manifests and source; Superpowers skills; Graphify CLI; PowerShell; Git; authenticated GitHub CLI.

**Spec:** `C:/Users/msadr/.gapcode/attachments/b2c0135b-93bc-4c93-96a8-e820a065b42c/pasted-text.txt`

## Global Constraints

- Do not modify project source code, implementation behavior, dependencies, build configuration, trading calculations, pipeline logic, bridge logic, or UI behavior.
- All task-generated documentation must be English and live under `docs/**`, except the required root-level `agent.md`.
- All Graphify output must live under `docs/graphify/**`.
- Source code is the source of truth whenever documentation disagrees.
- Bullish and Bearish implementations must be verified independently; do not infer one as the inverse of the other.
- Preserve all pre-existing user changes and distinguish them from task-generated changes.
- Delete a non-code artifact only after proving it has no imports, references, build/config/runtime/test/deployment role, or unique project information; otherwise retain it.
- Use read-only/check-only validation modes. Never use auto-fix, formatting-write, migration, dependency-upgrade, force-push, or history-rewrite operations.
- Commit only intended documentation, Graphify artifacts, `agent.md`, and any independently proven safe non-code deletions.
- Create annotated tag `v2.0.0` with message `TradingBot v2.0.0 Stable Version`; do not overwrite an existing local or remote tag.

---

### Task 1: Capture the immutable repository baseline

**Files:**
- Create: `docs/TradingBot_Repository_Baseline.md`
- Inspect: entire repository tree and Git metadata

**Interfaces:**
- Produces: baseline commit SHA, branch, remotes, tags, status, existing tracked/untracked/deleted paths, and a file inventory used by every later task.

- [ ] Run `git status --short --branch`, `git branch --verbose --all`, `git remote -v`, `git log --oneline --decorate -n 50`, and `git tag --list --sort=version:refname`.
- [ ] Record the starting `HEAD` SHA and classify every pre-existing working-tree change before any additional artifact is generated.
- [ ] Inventory repository files with `rg --files -uu`, excluding only Git object storage from the human-readable listing.
- [ ] Write `docs/TradingBot_Repository_Baseline.md` with exact command outputs or concise normalized tables and explicit pre-existing-change ownership.
- [ ] Verify the baseline document contains the starting SHA, current branch, configured remotes, local tags, and pre-existing dirty paths.

### Task 2: Dispatch independent read-only analysis workstreams

**Files:**
- Inspect: repository source, manifests, tests, configuration, existing documentation, and assets
- Create: no agent-owned repository files

**Interfaces:**
- Consumes: Task 1 baseline and source-freeze constraints.
- Produces: finding reports for architecture/runtime, engine/pipeline/bridge, UI/UX, and directional algorithms/dependencies.

- [ ] Invoke `superpowers:dispatching-parallel-agents` and dispatch isolated agents with explicit instructions to return findings only and never edit repository files.
- [ ] Assign one workstream to repository architecture, entry points, configuration, build/test tooling, and runtime lifecycle.
- [ ] Assign one workstream to `engine`, pipeline, bridge, data contracts, stage order, failure behavior, and performance-sensitive paths.
- [ ] Assign one workstream to UI structure, components, styles, tokens, responsive behavior, charts, interaction states, and layering.
- [ ] Assign one workstream to dependency/data/event/state flows and independent Bullish/Bearish implementation tracing, reusing an available slot sequentially when required.
- [ ] Reconcile conflicts by opening the cited source symbols and recording only evidence-backed conclusions.

### Task 3: Generate and verify the project Graphify

**Files:**
- Create/replace task output only: `docs/graphify/**`
- Inspect: entire repository implementation

**Interfaces:**
- Consumes: final repository inventory and discovered project structure.
- Produces: Graphify graph data, report, visualization, and query evidence used by architecture documentation.

- [ ] Read the complete Graphify skill instructions and inspect the installed CLI help/version without changing the repository.
- [ ] Configure Graphify so every generated artifact is written under `docs/graphify` and no source file is modified.
- [ ] Run the deepest appropriate directed analysis mode that covers hierarchy, symbols, imports, dependencies, calls, and relationships supported by the installed version.
- [ ] Inspect Graphify output structure, graph health, node/link counts, dangling endpoints, extraction provenance, and generated report.
- [ ] Query or explain the UI-to-bridge-to-pipeline-to-engine/result path and compare it with direct source tracing.
- [ ] Preserve Graphify findings as supporting evidence, not as a substitute for source inspection.

### Task 4: Build the technical architecture and project audit references

**Files:**
- Create/replace: `docs/TradingBot_Technical_Architecture.md`
- Create/replace: `docs/TradingBot_Project_Audit.md`

**Interfaces:**
- Consumes: reconciled source findings and Graphify evidence.
- Produces: exact architecture, runtime, dependency, data-flow, risk, testing, and maintenance reference for later documents and review.

- [ ] Document actual purpose, technology stack, important directories, entry points, runtime lifecycle, modules, classes, and non-trivial functions with exact paths and symbols.
- [ ] Trace acquisition, parsing, validation, transformation, bridge, pipeline, indicators, algorithms, state, and UI/output in actual execution order.
- [ ] Document configuration, persistence, networking, logging, error propagation, retries/fallbacks, external integrations, tests, and performance-sensitive paths without unsupported claims.
- [ ] Add concise Mermaid diagrams for major runtime and dependency flows where the source evidence supports them.
- [ ] Record technical risks, architecture concerns, documentation mismatches, coupling, dead-code candidates, and observed defects in the audit report without fixing implementation.
- [ ] Run an exact-path and exact-symbol spot check over every high-risk claim.

### Task 5: Build the UI/UX technical reference

**Files:**
- Create/replace: `docs/TradingBot_UI_UX_Technical_Reference.md`

**Interfaces:**
- Consumes: UI agent findings plus direct HTML/CSS/JS/TS/JSX/TSX/SVG verification.
- Produces: implementation-faithful UI architecture and reusable visual/interaction rules.

- [ ] Map actual pages, views, layout regions, panels, dialogs, popovers, menus, tabs, charts, forms, tables, and status components to their source paths.
- [ ] Extract exact typography, colors, CSS variables, spacing, dimensions, border/shadow/radius values, icon conventions, and chart colors.
- [ ] Document component states, UI state ownership, persistence, event wiring, responsive breakpoints, overflow behavior, chart resizing, and visibility changes.
- [ ] Document z-index and overlay relationships with exact selectors or constants.
- [ ] Explicitly mark unsupported or absent mobile behavior instead of inventing it.
- [ ] Cross-check reusable UI rules against the actual selector/component implementation.

### Task 6: Rebuild the Bullish and Bearish algorithm references

**Files:**
- Create/replace: `docs/TradingBot_Bullish_Algorithm_Reference.md`
- Create/replace: `docs/TradingBot_Bearish_Algorithm_Reference.md`

**Interfaces:**
- Consumes: engine/pipeline/bridge source traces, directional algorithm findings, and existing algorithm documents as style references only.
- Produces: two independently verified implementation references with exact conditions, transitions, contracts, and output semantics.

- [ ] Trace Bullish inputs, preprocessing, ordered pipeline stages, indicators, constants, thresholds, lookbacks, windows, state transitions, invalid/failure states, and final outputs directly from source.
- [ ] Trace Bearish behavior independently from source and explicitly record all asymmetries rather than deriving an inverse model.
- [ ] Link every non-trivial algorithm statement to exact files and symbols; include actual-behavior pseudocode where it improves determinism.
- [ ] Document bridge message formats, pipeline data contracts, missing-data behavior, temporal assumptions, ordering dependencies, and edge cases for each direction.
- [ ] Compare existing references with implementation and correct only documentation, recording significant mismatches in `docs/TradingBot_Project_Audit.md`.
- [ ] Perform a condition-by-condition cross-check against source for both references.

### Task 7: Create the operational AI-agent map

**Files:**
- Create/replace: `agent.md`

**Interfaces:**
- Consumes: verified architecture, UI/UX, algorithm, Graphify, and validation-command findings.
- Produces: concise repository entry map for future AI agents.

- [ ] Describe project identity, repository root, main runtime components, architecture flow, critical directories, and high-risk engine/pipeline/bridge areas.
- [ ] Add direct links to all required documents and `docs/graphify/`.
- [ ] State algorithm and UI modification gates that require reading the corresponding references and inspecting relevant source.
- [ ] List only repository-supported build, test, type-check, lint, static-analysis, startup, and engine-check commands discovered from manifests/scripts.
- [ ] State deterministic source-of-truth rules and avoid generic agent advice.
- [ ] Verify every linked path and command exists in the final repository state.

### Task 8: Perform conservative non-code cleanup and document decisions

**Files:**
- Create/replace: `docs/TradingBot_Cleanup_Report.md`
- Delete only: individually proven disposable non-code artifacts, if any

**Interfaces:**
- Consumes: baseline inventory, import/reference searches, build/config/runtime/test/deployment evidence.
- Produces: auditable deletion/retention decisions and a final file inventory for documentation cross-validation.

- [ ] Identify only obvious cache, temporary log, old export, editor/OS metadata, accidental copy, backup, or obsolete generated-output candidates.
- [ ] For each candidate, search imports, references, scripts, configuration, runtime paths, tests, deployment, and unique-content evidence.
- [ ] Retain every uncertain candidate and record why it was retained.
- [ ] Delete only candidates that pass all nine safety checks from the spec, using explicit literal paths.
- [ ] Record each deletion, artifact type, evidence, reason, and recoverability in the cleanup report.
- [ ] Re-run the repository inventory and ensure no source, test, manifest, lockfile, config, required asset, model, data, script, or documentation was deleted.

### Task 9: Independently review and correct documentation

**Files:**
- Review: `agent.md`, `docs/*.md`, `docs/graphify/**`
- Modify: documentation files only when review identifies evidence-backed inaccuracies

**Interfaces:**
- Consumes: all generated documentation and final post-cleanup source tree.
- Produces: independent findings covering architecture, UI/UX, Bullish, Bearish, Graphify, and agent-map accuracy.

- [ ] Invoke `superpowers:requesting-code-review` with an isolated read-only reviewer and exact baseline/current SHAs or working-tree diff scope.
- [ ] Require the reviewer to verify exact paths, symbols, conditions, directional asymmetries, Graphify relationships, links, and validation commands against source.
- [ ] Classify findings as Critical, Important, or Minor and challenge unsupported feedback with source evidence.
- [ ] Correct all valid Critical and Important documentation findings without modifying implementation.
- [ ] Re-run targeted source/path checks for every correction.
- [ ] Record unresolved uncertainty explicitly rather than presenting it as fact.

### Task 10: Validate the unchanged implementation and generated artifacts

**Files:**
- Create/replace: `docs/TradingBot_Validation_Report.md`

**Interfaces:**
- Consumes: final repository state and repository-supported commands.
- Produces: fresh PASS/FAIL/NOT EXECUTED/NOT APPLICABLE evidence for build, tests, static checks, runtime sanity, Graphify, documentation, and source integrity.

- [ ] Discover validation commands only from actual manifests, scripts, CI, test configuration, and documented repository tooling.
- [ ] Run build, unit tests, integration tests, type checking, lint, static analysis, startup sanity, and engine sanity checks only where safe check-only commands exist.
- [ ] If a command fails, invoke `superpowers:systematic-debugging`, capture exact output, identify the likely root cause, and document it without changing source.
- [ ] Verify Graphify artifacts are readable and internally consistent, and verify all required documentation files, links, paths, symbols, and diagrams.
- [ ] Compare the current tree against Task 1 baseline and explicitly classify all pre-existing versus task-generated changes.
- [ ] Write one status and evidence block per validation category; never assign PASS without a fresh exit-zero command or equivalent direct evidence.

### Task 11: Execute the verification-before-completion gate

**Files:**
- Inspect: complete final diff, staged candidate paths, required deliverables, and validation evidence

**Interfaces:**
- Consumes: plan checklist, baseline, review result, cleanup report, validation report, and final working tree.
- Produces: a verified allowlist for release staging or a precise blocker report.

- [ ] Invoke `superpowers:verification-before-completion` and re-read this plan plus the full spec line by line.
- [ ] Run fresh existence, link, path, symbol, Graphify, Git diff, diff-stat, and source-extension integrity checks.
- [ ] Confirm task-generated paths are restricted to `docs/**`, `agent.md`, and documented safe non-code deletions.
- [ ] Confirm the validation report states `SOURCE CODE MODIFIED BY THIS TASK: NO` only if the diff/baseline evidence proves it.
- [ ] Inspect the exact staged candidate list and reject any pre-existing user change or implementation file.
- [ ] Proceed to release operations only when all required deliverables and integrity gates have current evidence.

### Task 12: Create and publish the v2.0.0 stable checkpoint

**Files:**
- Stage: verified task-generated allowlist only
- Git objects: one release commit and one annotated tag

**Interfaces:**
- Consumes: Task 11 verified allowlist and configured existing GitHub remote.
- Produces: pushed release commit and annotated `v2.0.0` tag without altering unrelated history.

- [ ] Re-check branch, remote identity, authenticated `gh` state, remote branch state, and local/remote `v2.0.0` tag absence.
- [ ] Stage only the verified documentation, Graphify, `agent.md`, and any documented safe-deletion paths; inspect `git diff --cached --name-status` and `git diff --cached`.
- [ ] Commit with exact message `release: TradingBot v2.0.0 stable`.
- [ ] Create annotated tag `v2.0.0` with exact message `TradingBot v2.0.0 Stable Version` only if no local or remote conflict exists.
- [ ] Push the current intended branch and then the `v2.0.0` tag to the existing configured remote without force.
- [ ] Verify the remote branch contains the release commit and the remote annotated tag resolves to that commit.
- [ ] Run final `git status --short --branch` and distinguish a clean tree from any preserved pre-existing user changes.

## Plan Self-Review

- Spec coverage: all required analysis, Graphify, seven primary documents plus baseline/plan artifacts, `agent.md`, conservative cleanup, review, validation, source integrity, commit, annotated tag, and GitHub push are assigned to explicit tasks.
- Placeholder scan: the plan contains no deferred implementation placeholders; repository-specific command names are deliberately discovered from authoritative manifests before execution rather than invented.
- Interface consistency: Task 1 baseline feeds all later ownership checks; agent findings and Graphify feed documentation; final cleanup state feeds independent review and validation; verification gates the exact release allowlist.
