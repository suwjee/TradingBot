# TradingBot Git and Release Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Build a safe PowerShell workflow that prepares inclusion-first main and dependency-derived production, validates both locally, and can then publish two branches, an exact-production tag, and its GitHub Release.

**Architecture:** Invoke-TradingBotRelease.ps1 is the single normal command and delegates decisions to Release.Workflow.psm1. A declarative policy defines seeds and safety rules; the module derives the production dependency closure from an exact main commit, creates the result in a temporary production worktree, and records main provenance in either a changed production commit or its annotated tag.

**Tech Stack:** Windows PowerShell, standard Git and GitHub CLI, Node.js/npm, Python, Vite, and current TradingBot tooling. No added package dependency or credential storage.

**Spec:** scripts/git/RELEASE_WORKFLOW_DESIGN.md

## Global Constraints

- PROJECT_ROOT is derived and verified from script location plus Git, and resolves to X:\TradingBot in this task. No implementation path may reference D:\My-Projects\TradingBot.
- Preserve the intentionally dirty main worktree. Never reset, clean, stash, discard, silently unstage, force-push, or rewrite history.
- Main is inclusion-first: legitimate tests, maintained documents, valuable engineering evidence, Graphify reports, and the classified BaseLine reference remain eligible.
- Classify by producer, consumer, and enduring value. Never broadly ignore data, raw, state, engineering, archive, verification, or Graphify merely by path name.
- Production is default-deny and dependency-derived from the exact committed main SHA. State contents, tests, docs, archives, caches, secrets, dependencies, and release tooling are excluded.
- A missing local production branch is supported. Normal runs fetch origin/production, establish a safe local upstream relationship if needed, and always publish with explicit production refspecs.
- Prompt for commit message and release tag no more than once. Check Git tag syntax, uniqueness, and consistency only; do not impose a new tag format.
- Reuse current Git/GitHub authentication without printing or storing credentials. Independently test Git push authentication with a non-mutating dry-run.
- Prefer one atomic push for main, production, and tag. Fall back only after proving atomic support is unavailable and all target remote refs are unchanged; record each ref outcome.
- Changed production commits contain TradingBot-Main-Source: <SHA>. Unchanged production has no empty commit; the annotated tag and GitHub Release metadata contain the source main SHA.
- Dry-run uses only temporary index/ref/worktree artifacts and never stages the active index, pushes, publishes a tag, or creates a GitHub Release.
- Use First map → Then target → Then verify globally. Reuse established evidence; do not recursively read large dependency, cache, Graphify AST, RAW, archive, or generated-output trees unless their contents materially affect a decision.

## Review Focus

1. An absent local production branch with a valid origin/production must be safe in normal mode and ref-neutral in dry-run. Test in Task 4.
2. Atomic-push failure may fall back only when no target remote ref changed; any partial or indeterminate remote state must stop. Test in Task 5.
3. Test source, Graphify reports, engineering evidence, and BaseLine must be main-eligible while state cache, secret, and acquired RAW remain excluded. Test in Task 2.
4. A newly imported local runtime file must enter production, while an unreferenced neighbor is drift and not deployment content. Test in Task 3.
5. A dirty active worktree must be classified without reset, clean, stash, or active-index mutation in dry-run. Test in Tasks 2 and 4.

---

## File Structure

| Path | Responsibility |
| --- | --- |
| .gitignore | Evidence-backed main exclusions, without broad suppression of meaningful categories. |
| scripts/git/production-policy.psd1 | Data-only runtime seeds, main-sensitive rules, production exclusions, and narrow transient patterns. |
| scripts/git/Release.Workflow.psm1 | Testable Git wrappers, policy classification, closure resolver, preflight, worktree lifecycle, validation, publication, and reporting. |
| scripts/git/Invoke-TradingBotRelease.ps1 | The sole normal command; parameter parsing, one-time prompts, and orchestration call. |
| scripts/git/Test-ReleaseWorkflow.ps1 | Self-contained PowerShell tests built on temporary local repositories; no Pester dependency. |
| scripts/git/README.md | Operations, policy maintenance, recovery, and non-publication behavior. |

### Task 1: Establish the test harness and verified root boundary

**Files:**

- Create: scripts/git/Test-ReleaseWorkflow.ps1
- Create: scripts/git/Release.Workflow.psm1
- Test: scripts/git/Test-ReleaseWorkflow.ps1

**Interfaces:**

- Produces Resolve-TradingBotProjectRoot([string] ScriptPath) -> [string].
- Produces Invoke-ReleaseGit([string] Root, [string[]] Arguments, [string] WorkingDirectory) -> object with ExitCode, StdOut, StdErr, Arguments.
- Produces Assert-ReleaseCondition([bool] Condition, [string] Message) -> void.
- Every later task uses these interfaces for path/root/Git handling.

- [ ] **Step 1: Write failing root-resolution tests**

Create a temporary Git fixture containing AGENTS.md, apps/chart/package.json, and engine/bridge/trading_pipeline.py. Assert valid Git-root return, rejection of missing markers, and rejection of any legacy D: path.

- [ ] **Step 2: Run root-resolution tests and verify failure**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case RootResolution

Expected: FAIL because the module and resolver are absent.

- [ ] **Step 3: Implement the minimal harness and wrappers**

Create only temporary repositories below the system temporary directory and remove only a validated fixture in finally. Resolve root from the module/script boundary, verify it with git rev-parse --show-toplevel plus all three required project markers, and never emit credential data.

- [ ] **Step 4: Run focused root-resolution tests**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case RootResolution

Expected: PASS for valid root, invalid marker, and legacy-path rejection.

- [ ] **Step 5: Commit the focused boundary**

Run:

    git add scripts/git/Release.Workflow.psm1 scripts/git/Test-ReleaseWorkflow.ps1
    git commit -m "test: add release workflow harness"

### Task 2: Encode and verify the inclusion-first main policy

**Files:**

- Modify: .gitignore
- Create: scripts/git/production-policy.psd1
- Modify: scripts/git/Release.Workflow.psm1
- Modify: scripts/git/Test-ReleaseWorkflow.ps1

**Interfaces:**

- Consumes Task 1 root and Git functions.
- Produces Import-ReleasePolicy([string] Root) -> [hashtable].
- Produces Get-MainPolicyReport([string] Root, [string] IndexPath) -> object with Eligible, Excluded, Drift, Errors.
- Produces Test-SensitiveCandidate([string] Root, [string[]] Paths, [string] Commitish) -> object with redacted Findings and Errors.
- Tasks 3–5 must stop when Errors is nonempty.

- [ ] **Step 1: Write failing main-policy tests**

Model chart and engine tests, maintained engineering docs, Graphify report plus AST cache, BaseLine reference RAW, ordinary acquired RAW, state cache, state secret, chart build output, and a private-key marker. Assert only semantically meaningful content is eligible and secret values are never printed.

- [ ] **Step 2: Run policy tests and verify failure**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case MainPolicy

Expected: FAIL because policy import and classification do not exist.

- [ ] **Step 3: Narrow .gitignore using current evidence**

Remove whole-directory suppression for tests, engineering, archives, verification, Graphify, and generic root data/raw/state. Retain narrow exclusions for node dependencies, virtual environments, language caches, chart build output, local state cache/secret/tmp, ordinary acquired RAW, and disposable Graphify AST/stat-cache/query-stamp artifacts. Explicitly leave the inspected BaseLine eligible. Keep meaningful historical graphs, reports, manifests, inventories, fixtures, and evidence eligible.

- [ ] **Step 4: Implement policy and redacted secret checks**

Keep production-policy.psd1 data-only. Inspect tracked, staged, untracked, and ignored inventories with git check-ignore -v without changing the active index. Detect high-confidence private-key/token markers but return only path and rule identifiers.

- [ ] **Step 5: Run focused and real-repository checks**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case MainPolicy

Run: git check-ignore -v apps/chart/tests/unit/zoom-config.test.mjs engine/tests/unit/test_order_b_reset_leg.py engineering/archive/repository-graphify/graph.json apps/chart/state/data/raw/BaseLine/<actual-baseline-file>

Expected: PASS; meaningful probes are not ignored and local cache/secret/acquired-RAW probes match narrow rules.

- [ ] **Step 6: Commit the main-policy deliverable**

Run:

    git add .gitignore scripts/git/production-policy.psd1 scripts/git/Release.Workflow.psm1 scripts/git/Test-ReleaseWorkflow.ps1
    git commit -m "build: define release main policy"

### Task 3: Derive the production dependency closure from an exact main tree

**Files:**

- Modify: scripts/git/production-policy.psd1
- Modify: scripts/git/Release.Workflow.psm1
- Modify: scripts/git/Test-ReleaseWorkflow.ps1

**Interfaces:**

- Produces Get-GitTreePaths([string] Root, [string] Commitish) -> [string[]].
- Produces Get-GitBlobText([string] Root, [string] Commitish, [string] RelativePath) -> [string].
- Produces Get-ProductionFileSet([string] Root, [string] MainSha, [hashtable] Policy) -> object with Paths, Drift, Errors.
- Produces Test-ProductionFileSet(object FileSet, [hashtable] Policy) -> object with Errors.
- Task 4 uses Paths as the only source for production content.

- [ ] **Step 1: Write failing closure tests**

In a temporary fixture, model HTML module entries, local JS/CSS imports, Vite server imports, Python bridge/detector imports, required dynamic-detector seeds, bare npm imports, and unreferenced files beside runtime files. Assert reachable/seeded local files are selected; bare packages are not copied; unreferenced neighbors appear only as Drift.

- [ ] **Step 2: Run closure tests and verify failure**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case ProductionClosure

Expected: FAIL because committed-tree closure functions do not exist.

- [ ] **Step 3: Implement committed-tree resolution**

Read paths using git ls-tree and source text using git show <main SHA>:<path>; never use the dirty active worktree. Seed launch.bat, start.ps1, chart manifests/lockfile/Vite/HTML/dev-server, bridge, package markers, and detector files configured by Vite. Follow only relative JavaScript, CSS, and Python imports. Treat unresolved local imports as Errors and runtime-root files not reachable from any seed as Drift.

- [ ] **Step 4: Implement production integrity checks**

Require every startup seed and resolved closure member, reject excluded/sensitive paths, and require no apps/chart/state content. Directory initialization remains the existing launcher's responsibility and does not justify copying local contents.

- [ ] **Step 5: Run fixture and current-main checks**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case ProductionClosure

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Import-Module ./scripts/git/Release.Workflow.psm1 -Force; Get-ProductionFileSet -Root (Resolve-TradingBotProjectRoot './scripts/git') -MainSha (git rev-parse HEAD) -Policy (Import-ReleasePolicy (Resolve-TradingBotProjectRoot './scripts/git')) | Format-List"

Expected: PASS; no unresolved runtime dependency and no state/test/doc/release-tooling path in Paths.

- [ ] **Step 6: Commit the closure resolver**

Run:

    git add scripts/git/production-policy.psd1 scripts/git/Release.Workflow.psm1 scripts/git/Test-ReleaseWorkflow.ps1
    git commit -m "feat: derive production dependency closure"

### Task 4: Prepare isolated production snapshots and real dry-run validation

**Files:**

- Modify: scripts/git/Release.Workflow.psm1
- Modify: scripts/git/Test-ReleaseWorkflow.ps1

**Interfaces:**

- Produces Test-ReleasePreflight([string] Root, [string] Tag, [switch] RequireGitHubCli) -> object.
- Produces New-TemporaryReleaseContext([string] Root) -> object.
- Produces New-ProductionSnapshot([string] Root, [string] SourceMainSha, [string] ProductionBaseSha, object FileSet, [string] CommitMessage, [switch] DryRun) -> object.
- Produces Test-ProductionSnapshot(object Snapshot) -> object.
- Produces Remove-TemporaryReleaseContext(object Context) -> object.
- Task 5 consumes the prepared main/production SHAs, remote baseline OIDs, and status report.

- [ ] **Step 1: Write failing preflight and snapshot tests**

Cover a dirty but policy-valid active tree; absent local production with origin/production present; a divergent local production branch; state excluded from snapshot; and dry-run cleanup. Assert dry-run leaves active index, permanent branches, tags, remote, and GitHub unchanged while producing a temporary candidate report.

- [ ] **Step 2: Run snapshot tests and verify failure**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case Snapshot

Expected: FAIL because preflight and worktree functions do not exist.

- [ ] **Step 3: Implement preflight**

Check Git, verified root, active main, merge/rebase state, remote identity, fetched branch topology, tag/release uniqueness, managed-worktree safety, and GitHub identity/repository access. Use git push --dry-run with the configured repository to verify Git push authentication independently. Do not inspect credential stores or require a clean active worktree.

- [ ] **Step 4: Implement normal and dry-run worktree construction**

Fetch origin. In normal mode, create local production from refs/remotes/origin/production and set its upstream only when local production is absent; otherwise require local/upstream synchronization. Add a unique temporary worktree outside .git based on production, replace only that validated worktree's tracked tree with the exact main-SHA Paths, compare trees, and commit only changed production content with the user message plus the provenance trailer.

In dry-run, use a temporary index to create a candidate main tree, a detached worktree based on origin/production, and a temporary candidate production commit/tree. Remove all temporary index/ref/worktree artifacts in finally and do not mutate active index or permanent refs.

- [ ] **Step 5: Implement local production validation**

Validate policy/closure/sensitive content, PowerShell parsing, node --check for selected JavaScript/MJS, Python ast.parse, bridge --help, npm ci from lockfile inside the temporary worktree, and npm.cmd run build. Check launcher-required paths but do not start its installing/server loop. Label each check PASS, FAIL, NOT_TESTED, or dependency-limited precisely.

- [ ] **Step 6: Run snapshot tests and a real dry run**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case Snapshot

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Invoke-TradingBotRelease.ps1 -DryRun -CommitMessage "dry-run validation" -ReleaseTag "dry-run-local-20260929"

Expected: PASS and a cleaned temporary snapshot. No ref, tag, push, or GitHub Release changes.

- [ ] **Step 7: Commit snapshot support**

Run:

    git add scripts/git/Release.Workflow.psm1 scripts/git/Test-ReleaseWorkflow.ps1
    git commit -m "feat: prepare release snapshots safely"

### Task 5: Add one-command input, provenance, atomic publication, and guarded fallback

**Files:**

- Create: scripts/git/Invoke-TradingBotRelease.ps1
- Modify: scripts/git/Release.Workflow.psm1
- Modify: scripts/git/Test-ReleaseWorkflow.ps1

**Interfaces:**

- Produces Read-ReleaseInputs([string] CommitMessage, [string] ReleaseTag) -> object.
- Produces New-ReleaseTag([string] Root, [string] Tag, [string] ProductionSha, [string] MainSha) -> object.
- Produces Publish-ReleaseRefs([string] Root, object PreparedRelease) -> object.
- Produces New-GitHubRelease([string] Root, object PreparedRelease) -> object.
- Produces Invoke-TradingBotRelease([hashtable] Parameters) -> object.

- [ ] **Step 1: Write failing publication tests**

Use local bare remotes plus command adapters to assert one prompt per missing input, invalid/existing tag failure, annotated-tag provenance, changed-production trailer, unchanged-production no-empty-commit behavior, atomic success, unsupported-atomic fallback only after unchanged-ref proof, and stop-on-partial behavior.

- [ ] **Step 2: Run publication tests and verify failure**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case Publication

Expected: FAIL because input/tag/publication functions do not exist.

- [ ] **Step 3: Implement entry and local tag preparation**

The entry accepts -DryRun, -CommitMessage, -ReleaseTag, and -VerboseReport, prompting once only for missing values. Validate nonempty message, git check-ref-format refs/tags/<tag>, local/remote tag absence, and existing GitHub Release absence. Create an annotated local tag at exact production SHA containing TradingBot-Main-Source: <main SHA>; never overwrite.

- [ ] **Step 4: Implement atomic publication and safe fallback**

Attempt one explicit git push --atomic origin for refs/heads/main:refs/heads/main, refs/heads/production:refs/heads/production, and refs/tags/<tag>:refs/tags/<tag>. On failure, re-query each remote ref against pre-push and desired OIDs. Fall back only with evidence of unsupported atomic push and proof no target ref changed. The fallback pushes each explicit non-force refspec separately, verifies immediately, and records RemoteMain, RemoteProduction, and RemoteTag. Stop without retry after partial or indeterminate state.

- [ ] **Step 5: Implement GitHub Release and outcome report**

Create one GitHub Release only after all three refs are confirmed remote. Its target is the annotated tag/exact production commit and metadata includes main SHA, explicitly noting tag-sourced provenance if production was unchanged. Report LOCAL MAIN, LOCAL PRODUCTION, REMOTE MAIN, REMOTE PRODUCTION, TAG, GITHUB RELEASE, and TEMP WORKTREE independently with safe recovery directions.

- [ ] **Step 6: Run publication tests and parser-only entry check**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case Publication

Run: powershell.exe -NoProfile -Command "[void][scriptblock]::Create((Get-Content -Raw scripts/git/Invoke-TradingBotRelease.ps1)); 'PASS: entry-point parsed'"

Expected: PASS; no real push, tag publication, or GitHub Release.

- [ ] **Step 7: Commit guarded publication**

Run:

    git add scripts/git/Invoke-TradingBotRelease.ps1 scripts/git/Release.Workflow.psm1 scripts/git/Test-ReleaseWorkflow.ps1
    git commit -m "feat: add guarded TradingBot release workflow"

### Task 6: Document operations and validate globally without publishing

**Files:**

- Create: scripts/git/README.md
- Modify: scripts/git/Test-ReleaseWorkflow.ps1
- Modify: scripts/git/Release.Workflow.psm1 only if validation exposes a defect

**Interfaces:**

- Consumes complete workflow from Tasks 1–5.
- Produces documented normal/dry-run commands, policy-maintenance instructions, recovery guidance, and final evidence.

- [ ] **Step 1: Write failing documentation/report tests**

Assert README covers root derivation, inclusion-first main, dependency-derived production, BaseLine/Graphify classification, state handling, missing local production, authentication reuse, dry-run, temporary worktree, atomic/fallback behavior, provenance, GitHub Release, recovery, and non-publication validation. Assert dry-run output has all required status categories.

- [ ] **Step 2: Run documentation tests and verify failure**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1 -Case Documentation

Expected: FAIL because operational README is absent.

- [ ] **Step 3: Write concise operations documentation**

Describe Invoke-TradingBotRelease.ps1 as the one normal command and -DryRun as validation; document prompt/parameter behavior, policy drift, production creation from origin/production, worktree cleanup, atomic/fallback behavior, tag/release provenance, dirty-tree protection, authentication reuse, recovery, and the rule that implementation validation cannot publish.

- [ ] **Step 4: Run final focused and global validation**

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Test-ReleaseWorkflow.ps1

Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/git/Invoke-TradingBotRelease.ps1 -DryRun -CommitMessage "dry-run validation" -ReleaseTag "dry-run-local-20260929"

Run: powershell.exe -NoProfile -Command "Get-ChildItem scripts/git -Filter '*.ps1' | ForEach-Object { [void][scriptblock]::Create((Get-Content -Raw $_)); Write-Output ('PASS: ' + $_.Name) }"

Run: Set-Location apps/chart; npm.cmd test; npm.cmd run build

Run: python -B -m pytest -q -p no:cacheprovider -p no:benchmark engine/tests/unit

Expected: all available checks report PASS. Dependency limitations or unrelated pre-existing failures are labeled precisely. No real push, tag publication, or GitHub Release occurs.

- [ ] **Step 5: Inspect final policy and Git state**

Run: git diff --check; git status --short; git check-ignore -v <meaningful-probes> <transient-probes>

Expected: probes match documented classifications, no secret candidate is staged, and TradingBot behavior has not changed.

- [ ] **Step 6: Commit operations docs and final tests**

Run:

    git add scripts/git/README.md scripts/git/Test-ReleaseWorkflow.ps1 scripts/git/Release.Workflow.psm1
    git commit -m "docs: document TradingBot release operations"

## Plan Self-Review

- **Spec coverage:** Tasks 1–6 cover root discovery, inclusion-first main, test/Graphify/BaseLine classification, dependency-derived production, state exclusion, absent/present production branches, dirty-tree protection, authentication reuse, traceability, dry-run, atomic/fallback publication, recovery, and documentation.
- **Step scan:** Every task begins with a failing test, defines its exact interfaces, implements the smallest boundary, verifies it, and has a focused commit.
- **Type consistency:** Get-ProductionFileSet is the sole production-membership authority; New-ProductionSnapshot is the sole production-worktree constructor; later task signatures match their producing tasks.
- **Review focus:** All five high-risk conditions have a named owning test task.
- **Proportion:** The plan specifies paths, interfaces, assertions, commands, and evidence without embedding implementation bodies.
