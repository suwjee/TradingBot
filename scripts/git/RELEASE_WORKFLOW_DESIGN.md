# TradingBot Git and Release Workflow Design

**Status:** Proposed and approved for planning  
**Project root for this task:** `X:\TradingBot`  
**Scope:** Repository policy and Git/GitHub release automation only. Trading calculations, UI behavior, and runtime behavior are out of scope.

## 1. Verified starting point

- The resolved repository root is `X:\TradingBot`. All implementation paths derive from the repository root discovered by Git and script location; no implementation path may depend on `D:`.
- The active branch is `main`, and its working tree intentionally contains user changes. The workflow must not reset, clean, stash, discard, or silently unstage that work.
- `origin` is the existing GitHub remote for `suwjee/TradingBot`. The existing GitHub CLI session is authenticated as `suwjee`; the workflow must reuse it without reading or writing credentials.
- The remote currently has both `main` and `production`. The current remote heads resolve to the same commit, although no local `production` tracking branch is currently present.
- The normal startup path is `scripts/launch.bat` to `scripts/start.ps1`, then the chart Vite server and the Python bridge/pipeline. `apps/chart/state` is initialized at runtime and contains local RAW, cache, and credential state; its existing contents are not production inputs.
- Existing tags use mixed `2.0.0` and `v*` forms. The workflow will require valid, unused Git tag names but will not impose a new naming convention.

## 2. Goals and non-goals

The workflow provides one normal PowerShell entry point that prepares `main`, produces a dependency-derived `production` snapshot in an isolated temporary worktree, validates both locally, creates a production tag, pushes safely, and creates the matching GitHub Release.

It must provide a real `-DryRun` that builds and validates temporary snapshots but never pushes, publishes a tag, or creates a GitHub Release.

It does not alter TradingBot business rules, trade calculations, app behavior, account configuration, remote configuration, credentials, or published history. Implementing and testing this workflow does not authorize a release.

## 3. Repository classification model

### Main: inclusion first

`main` is the long-lived engineering record. Source, maintained documentation, scripts, all legitimate tests, references, fixtures, baselines, regression evidence, migration records, audit material, and meaningful Graphify output remain eligible by default.

The root `.gitignore` will be re-audited and narrowed to evidence-backed exclusions. It must not broadly ignore `data`, `raw`, `state`, `engineering`, `archive`, `verification`, or Graphify solely because of their names.

Current decisions derived from the audit are:

- `apps/chart/tests` and `engine/tests` are test source and must be eligible for `main`.
- `engineering/docs` is maintained documentation and must be eligible.
- Graphify reports, graphs, inventories, manifests, health reports, labels, and audit evidence under `engineering/archive/repository-graphify` are meaningful engineering artifacts and must be eligible.
- Reconstructible Graphify AST/stat caches and query stamps are disposable and remain ignored through narrow cache rules.
- Historical regression manifests and selected input/output evidence are eligible; generated validation-build output, interpreter bytecode, live runtime logs, process IDs, and transient working files remain excluded only where their producer and role establish that they are disposable.
- `apps/chart/state/cache`, `apps/chart/state/secret`, and `apps/chart/state/tmp` are machine-local. RAW is not treated as a blanket category: the inspected `apps/chart/state/data/raw/BaseLine` reference remains eligible, while ordinary acquired RAW remains local unless separately classified.
- Dependency installations, virtual environments, language caches, and the chart build output remain excluded because manifests and supported build/install commands recreate them.

`Test-MainPolicy` will inspect tracked, staged, untracked, and ignored paths. It will fail on sensitive candidate paths/content, report ignored files in meaningful areas, and identify policy drift instead of silently suppressing it.

### Production: default deny and dependency-derived

`production` is a deployable runtime snapshot, not a reduced copy of `main`. A file is selected only when the current startup/dependency analysis proves that it is required.

The production resolver starts from these audited runtime boundaries:

1. `scripts/launch.bat` and `scripts/start.ps1`.
2. `apps/chart/package.json`, lockfile, Vite configuration, HTML module entries, and the chart development-server script.
3. The local JavaScript and CSS import closure of the HTML/Vite entries, including server modules imported by `vite.config.js`.
4. `engine/bridge/trading_pipeline.py`, its configured detector paths, and the local Python import closure needed by those detector modules.

The resolver includes only resolved local files plus the explicit startup/package seeds. Package dependencies are restored with `npm ci`; `node_modules` is never copied. Runtime state directories are created by the existing launcher; no current `apps/chart/state` contents are copied. Documentation, tests, release tooling, engineering archives, build output, caches, secrets, and unreferenced source are excluded from production.

New reachable local imports are included and reported. New unreferenced files under runtime-adjacent directories are reported as production drift rather than automatically deployed. This makes the policy dependency-aware without a fragile per-file allowlist.

## 4. Automation package

All new task artifacts remain under `scripts/git`:

| File | Responsibility |
| --- | --- |
| `Invoke-TradingBotRelease.ps1` | The sole normal entry point; accepts `-DryRun`, optional non-interactive message/tag values, and a concise verbose/report mode. |
| `Release.Workflow.psm1` | Root discovery, classification, dependency closure, safety checks, temporary-worktree lifecycle, validation, and reporting functions. |
| `production-policy.psd1` | Declarative runtime seeds, required checks, sensitive-path rules, and narrowly classified exclusions. |
| `Test-ReleaseWorkflow.ps1` | Deterministic local tests for policy resolution, traceability, dry-run behavior, and failure paths. |
| `README.md` | Operational command reference, architecture, policy rationale, failure recovery, and maintenance instructions. |

The module derives `PROJECT_ROOT` from the script location and verifies it with `git rev-parse --show-toplevel`, `AGENTS.md`, `apps/chart`, and `engine`. The resolved root is used for every subsequent operation.

## 5. Main preparation

Before a normal release, the entry point will:

1. Verify Git, repository identity, branch topology, worktree state, merge/rebase state, remote URL, tag/release uniqueness, and existing authentication without exposing secrets.
2. Refresh remote references safely and require `main` to contain the fetched `origin/main` history; divergence fails safely.
3. Run the main-policy classification and secret checks before staging.
4. Stage only the policy-allowed working-tree result. Existing staged content that violates policy causes failure; the workflow never unstages or discards it.
5. Create one `main` commit with the entered message when the resulting index differs. If there is no main change, retain the existing main SHA without an empty commit.

Because the user explicitly runs the release entry point and supplies its message and tag, this staging step is the release authorization for eligible content only. Implementation and dry-run never stage the active worktree.

## 6. Production construction and validation

The workflow obtains the exact committed main SHA, then creates a uniquely named temporary worktree outside `.git` and outside the permanent project layout. It starts from the existing `production` branch/history after remote refresh, while its desired filesystem is selected from the exact main commit.

The worktree procedure is convergent:

1. Resolve the production dependency closure from the main commit.
2. Replace only the temporary worktree's tracked snapshot with that closure; remove stale deployed files there.
3. Compare the resulting tree with the current production tree.
4. If the tree changed, create a production commit on top of the current production head using the same user-supplied commit message and the trailer `TradingBot-Main-Source: <main SHA>`.
5. If the tree did not change, do not create an empty production commit.
6. Validate the final production tree in that isolated worktree, then always remove the temporary worktree. Cleanup status is reported separately.

Validation includes dependency-closure integrity, excluded-content checks, sensitive-content checks, PowerShell parsing, JavaScript syntax checks, Python AST parsing, engine bridge help/import smoke checks, lockfile-driven dependency restoration in the temporary tree, and the chart build. It intentionally does not run the interactive launcher because that can install packages and start a long-running server.

`-DryRun` uses an isolated temporary index/commit and temporary worktree to model the policy-allowed main candidate and resulting production tree. It cleans every temporary ref/index/worktree it creates and makes no branch, tag, release, or remote update.

## 7. Release, traceability, and publication

The release tag is an annotated tag pointing to the exact final production commit. It contains `TradingBot-Main-Source: <main SHA>` in its annotation. A changed production commit contains the same trailer. Therefore the trace is deterministic:

```text
release tag -> exact production commit -> main SHA
```

When production has no changes, the production commit remains unchanged and the tag annotation, plus GitHub Release metadata, records the exact source main SHA. No meaningless commit is created.

Only after local main and production validation succeeds does a normal run create the local tag and publish the branch refs and tag. It uses the existing `origin` credentials and GitHub CLI session, verifies repository access without exposing credentials, and requires safe publication. The GitHub Release is created only after its tag is confirmed on the remote, targets that tag/production commit, and repeats the main SHA metadata.

Existing tags or GitHub Releases are never overwritten. Push, tag, and Release outcomes are reported separately; a GitHub Release failure after successful ref publication is a partial result, not success. No force push or history rewrite is used.

## 8. Failure handling and idempotency

Every run reports independent status for local main, local production, remote main, remote production, tag, GitHub Release, and temporary worktree cleanup. Failures preserve prepared local state for explicit recovery; the workflow never compensates by rewriting remote history.

Repeated runs detect an existing tag/release, local/remote divergence, and stale temporary resources before publishing. They do not reuse release names, duplicate commits without content changes, or leave unmanaged worktrees as normal behavior.

## 9. Acceptance criteria

The implementation is complete only when all of the following are evidenced:

1. `.gitignore`/`.gitattributes` are re-read and policy-checked; meaningful tests, docs, engineering evidence, Graphify reports, and the Baseline reference are not hidden by broad rules.
2. PowerShell scripts parse successfully and deterministic policy tests pass.
3. A real dry run creates, validates, summarizes, and removes a temporary production worktree without publishing anything.
4. Main and production classification reports demonstrate the intended asymmetry and policy-drift handling.
5. The temporary production tree contains its complete runtime closure but no test, state, cache, secret, archive, or release-tooling content.
6. Production syntax/build/smoke checks pass or any dependency-limited result is precisely reported.
7. Existing authenticated GitHub identity and repository access are verified safely; no credentials appear in source, reports, or output.
8. Traceability and tag semantics are verified locally without creating or publishing a real release.
9. The final repository status is inspected and unrelated application behavior remains unchanged.
