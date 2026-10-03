---
title: TradingBot Repository Integrity
document_role: procedure
lifecycle: maintained
owner: repository-integrity
scope:
  - git
  - tracking
  - generated-content
  - archive
  - verification
last_modified_at: 2026-09-30T16:33:27+03:30
---

# TradingBot Repository Integrity

## 1. Purpose and boundary

This document owns the durable repository-integrity procedure:

> What belongs in the engineering repository, how is repository content classified/tracked, and how is integrity verified without destroying user work or historical evidence?

Use root [`AGENTS.md`](../../../AGENTS.md) for project authority and dirty-work safety, [Documentation Governance](../documentation-governance.md) for document lifecycle/ownership, [Testing](../development/testing.md) for test execution/RAW verification, [Local State](../operations/local-state.md) for operational persistence, [Historical Evidence](../../archive/README.md) for archive lifecycle, and [Release Operations](../../../scripts/git/README.md) for publication/package mechanics.

This document does not define trading semantics, local-state implementation, test selection, or release composition.

## 2. Integrity evidence model

Repository truth must be established from the live repository, not from a remembered tree or one policy file.

Use these evidence types together:

- Current Git/index state;
- Current `.gitignore` and `.gitattributes`;
- Current Source/configuration/manifests;
- maintained ownership documentation;
- current release policy where production inclusion matters;
- verification/archive lifecycle classification;
- runtime/local-state ownership where a path can contain machine-local data.

Do not infer authority or cleanup safety from path names, timestamps, hashes, versions, or old reports.

## 3. Repository content classes

Classify by owner and lifecycle rather than folder name alone.

| Class | Repository expectation | Authority / integrity rule |
| --- | --- | --- |
| Production Source | Tracked in engineering `main` when Current | Live Current Source is executable authority; stale copies cannot replace it |
| Maintained documentation | Tracked | Authority depends on document owner/lifecycle, not recency |
| Tests and verification tooling | Tracked when maintained/current policy includes them | Tests verify behavior; they are not trading-semantic authority |
| Tooling/scripts/configuration | Tracked when project-owned | Read Current implementation before relying on old commands |
| RAW evidence | Policy-dependent | Immutable evidence; tracking state does not change evidence semantics |
| Generated artifacts | Policy-dependent | Generated does not imply ignored, disposable, or non-evidence |
| Verification evidence | Often intentionally tracked | Records the execution it represents; old PASS is not Current PASS |
| Historical/archive material | May be tracked | Preserves provenance; never Current authority solely because it is tracked/recent |
| Local runtime state | Normally excluded unless explicitly curated | Ownership belongs to [Local State](../operations/local-state.md) |
| Temporary/cache material | Usually excluded when proven rebuildable/disposable | Name alone never authorizes deletion |
| Secret-sensitive state | Must not be committed | Report classification only; never disclose values |

Repository integrity is a classification problem first and a cleanup problem only after evidence establishes safety.

## 4. Tracked, untracked, and ignored are different states

Definitions:

- **tracked** — the path is in the Git index/history for the selected revision;
- **untracked** — the working-tree path is not in the index;
- **ignored** — an ignore rule tells Git not to present an otherwise-untracked path normally;
- **generated** — describes how content was produced, not its Git state;
- **historical** — describes lifecycle/authority, not its Git state.

`.gitignore` does not override an already tracked path. A tracked file may match a later ignore pattern. An ignored or untracked file can still contain unique user work, RAW evidence, credentials, or forensic evidence.

Current `main` provides concrete examples without turning them into permanent inventories:

- Chart and Engine tests are tracked;
- engineering archive and verification evidence contain intentionally tracked material;
- curated `BaseLine` RAW is intentionally tracked under the Current policy;
- machine-local Chart cache, secret, temporary state, and ordinary acquired RAW are excluded by Current policy.

These facts must be rediscovered when policy or live Git changes.

## 5. Working-tree safety and actual Git evidence

When a working tree is available, inspect it before editing or staging:

1. current branch and upstream;
2. configured remote;
3. staged changes;
4. unstaged changes;
5. untracked paths;
6. deletions and renames;
7. ignored/local-only paths where relevant.

Use actual Git/index evidence to answer tracking questions. Typical evidence commands include `git status --short --branch`, `git diff`, `git diff --cached`, `git ls-files`, and `git check-ignore -v`; adapt to the Current environment/tooling.

Never use `git reset`, `git clean`, broad restore, unrelated stashing, history rewriting, or force-push as a repository-integrity shortcut.

A remote repository view can prove what is committed remotely, but it cannot prove the local working tree is clean or reveal every ignored/untracked local artifact. Report that distinction explicitly.

## 6. Tracked is not production-included

Current release policy deliberately separates engineering `main` from the production snapshot.

Therefore:

`tracked in the engineering repository != included in production output`

and:

`excluded from production != Git-ignored`

Maintained tests, engineering documentation/evidence, release tooling, and selected reproducibility evidence may be legitimate tracked engineering content while being excluded from the runtime production closure.

Detailed selection, publication, tags, remote updates, and recovery mechanics belong to [Release Operations](../../../scripts/git/README.md) and Current release policy. Do not duplicate them here.

## 7. Generated content

Generated content must be classified by:

- producer;
- consumer;
- rebuildability;
- evidence value;
- lifecycle;
- Git policy;
- release relevance.

Generated does not automatically mean:

- ignored;
- untracked;
- disposable;
- safe to regenerate;
- non-evidence.

Examples include dependency graphs, verification reports, static-analysis output, benchmark output, generated manifests, and build products. Some are disposable build residue; others are deliberately retained evidence.

Delete or regenerate only through the owning workflow and only after confirming that no unique evidence will be lost.

## 8. Graphify classification

Current Graphify material under the engineering archive is generated repository-analysis evidence and navigation support.

It may help with:

- repository navigation;
- ownership/dependency hints;
- duplicate/stale-copy discovery.

It is not:

- production Source;
- semantic authority;
- Technical Architecture;
- canonical project truth.

Graphify timestamps or graph recency never outrank live Current Source. Validate important relationships directly against Current Source. Running Graphify requires its own current authorization; repository-integrity work does not silently regenerate it.

See [Graphify Artifacts](../../archive/repository-graphify/README.md).

## 9. Historical and archive material

Historical does not mean useless.

Tracked archive material can preserve:

- old Source/reference snapshots;
- migration/recovery evidence;
- benchmarks;
- regression baselines;
- old path/configuration facts;
- one-time audit results.

But tracked Historical material does not become Current authority. A newer timestamp does not promote it. Preserve unique evidence and keep it clearly separated from maintained Current guidance.

Do not automatically delete duplicate-looking archive files. First determine their owner, lifecycle, authority, and whether they preserve unique provenance.

## 10. Verification evidence

`engineering/verification/` contains evidence from specific executions and migrations according to Current governance.

Durable rule:

`old PASS != Current PASS`

A historical report proves only the run, inputs, Source/revision, environment, and assertions it recorded. It cannot substitute for a fresh required verification after Current changes.

Do not hard-code verification-file totals or treat a previous status as the current repository status.

## 11. Test repository ownership

Repository Integrity owns whether tests are correctly classified/tracked as engineering content.

[Testing](../development/testing.md) owns:

- how tests are discovered;
- which suites/runners are selected;
- how RAW/regression evidence is used;
- result-status interpretation.

Current Git shows maintained Chart and Engine tests as tracked engineering content. Do not revive stale assumptions that tests are inherently local-only or ignored.

## 12. Duplicate and stale-copy risk

Search for risks such as:

- duplicate Source copies;
- extracted packages;
- historical Source snapshots;
- duplicate maintained documents;
- duplicate Algorithm References;
- generated snapshots mistaken for Source;
- archive material mistaken for maintained Current guidance.

A duplicate-looking file is a review trigger, not a deletion command.

Before action determine:

1. owner;
2. lifecycle;
3. authority;
4. purpose;
5. whether the bytes are unique evidence;
6. whether an active import/runtime/reference points to it.

## 13. Source authority and archive/package safety

Current production Source is discovered from the live Current project according to root [`AGENTS.md`](../../../AGENTS.md), runtime/import closure, manifests, and Current project conventions.

Neither an extracted archive, historical copy, generated snapshot, Graphify output, verification artifact, nor Source copied into an old report may silently replace live Source.

A ZIP/package is not automatically Current authority. The Current engineering tree may contain package/archive artifacts, including Source snapshots. Their presence does not make them the executable owner and does not make any particular package filename a permanent project requirement.

When a package is supplied for a task:

- inspect it recursively when relevant;
- identify stale/duplicate content;
- compare with live repository authority;
- establish Current ownership before using it to change behavior.

## 14. Path and case integrity

TradingBot is developed across Windows and environments where case rules can differ.

Integrity review must check:

- exact tracked casing;
- case-only collisions;
- rename correctness;
- relative paths;
- Markdown links;
- import/load paths;
- cross-platform path assumptions.

Do not rely on Windows case-insensitivity as proof that a path is repository-correct elsewhere.

Case-only renames require deliberate Git verification so the intended tree is represented remotely.

## 15. Line endings and byte integrity

Follow Current `.gitattributes` rather than inventing a universal newline rule.

Current policy establishes:

- `* text=auto` for general text normalization;
- `engine/** -text` so Engine and exact-source reference bytes retain their byte identity;
- `*.bat text eol=crlf`;
- `*.ps1 text eol=crlf`;
- Markdown whitespace handling that preserves intentional trailing-space line breaks.

The Current editor configuration prefers LF for normal text editing, but `.gitattributes` is the Git content policy.

Avoid accidental whole-file line-ending churn. In particular, do not normalize protected Engine/reference bytes merely to satisfy an editor preference.

## 16. Large, binary, RAW, and archive artifacts

Do not invent Git LFS, size limits, or package rules that Current configuration does not define.

Current `.gitattributes` does not establish a Git LFS policy. Binary/archive/large artifacts must therefore be reviewed under Current repository/release policy and evidence value.

RAW, ZIPs, compressed regression evidence, generated graphs, and similar artifacts can be legitimate engineering evidence. Their size or extension alone does not establish authority, tracking, or deletion safety.

When adding or changing a large/binary artifact, verify:

- ownership;
- need for retention;
- reproducibility;
- sensitivity;
- repository policy;
- release exclusion/inclusion;
- whether a lighter manifest/reference could preserve the required evidence without losing provenance.

## 17. Secret integrity

Secret-sensitive state must never be staged merely because it exists under the checkout.

Before committing:

- inspect the exact candidate paths;
- exclude Current secret-state owners and environment/private-key material;
- inspect generated reports/bundles for accidental secret capture;
- redact sensitive log content before retention;
- never copy actual tokens, cookies, passwords, API keys, session identifiers, or private keys into documentation, tests, reports, commit messages, or release metadata.

If a potentially sensitive file is discovered, report safe classification information only.

## 18. Conservative repository cleanup

Repository-integrity verification does not authorize broad cleanup.

Before deleting, moving, or untracking a path determine:

- owner;
- lifecycle;
- actual index/ignore state;
- rebuildability;
- evidence value;
- user-created status;
- runtime use;
- secret sensitivity;
- release relevance;
- inbound references.

Never infer:

`untracked = disposable`  
`ignored = disposable`  
`generated = disposable`  
`historical = disposable`  
`production-excluded = disposable`

Prefer preserving unique evidence over destructive cleanup.

## 19. Integrity verification procedure

For a repository-structure/documentation task:

1. discover the live repository root;
2. inspect applicable root/nearer instructions;
3. inspect branch, remote, upstream, and working-tree state when available;
4. inventory the relevant Current repository tree;
5. inspect `.gitignore`, `.gitattributes`, manifests/configuration, and release policy where applicable;
6. classify Current Source, tests, documentation, RAW, generated output, verification evidence, archive, local state, and secrets by owner/lifecycle;
7. verify duplicate/stale-copy risks without deleting by appearance;
8. verify exact path/case and changed links;
9. review the exact task diff;
10. confirm protected Source/tests/RAW/References/runtime state were not changed unless the task explicitly owns them;
11. validate timestamps/metadata for changed maintained documents;
12. stage only task-owned files when local Git is used;
13. review the staged diff;
14. perform only the currently authorized commit/push/release action;
15. verify the resulting remote state independently.

If a required evidence source is unavailable, report `NOT VERIFIED`/`INCOMPLETE` rather than substituting an old report.

## 20. Acceptance scenarios

This procedure remains valid when:

- test count doubles — no fixed-count rule breaks;
- a tracked file matches an ignore pattern — the index still determines tracked state;
- historical archive is tracked — lifecycle remains Historical;
- generated verification evidence is tracked — generated does not imply disposable;
- a tracked file is production-excluded — it remains legitimate engineering content;
- two paths differ only by case — cross-platform integrity review detects the risk;
- a ZIP containing Source appears — live Current Source authority is established before use;
- Git HEAD changes — maintained rules remain valid;
- verification output grows — no fixed-total assumption breaks;
- Graphify is newer than maintained docs — it remains supporting/generated evidence, not semantic authority.

## 21. Ownership boundaries

Keep responsibilities separate:

- [Local State](../operations/local-state.md) — operational/local persistence and cleanup safety;
- [Documentation Governance](../documentation-governance.md) — document role/lifecycle/ownership;
- [Technical Architecture](../architecture/technical-architecture.md) — subsystem/process/data-flow architecture;
- [UI/UX Reference](../architecture/ui-ux-reference.md) — user-facing interaction/state contract;
- [Testing](../development/testing.md) — test/RAW/regression execution methodology;
- Algorithm Reference Maintenance — Reference synchronization procedure;
- Zero-Difference Refactor — behavior-preserving refactor/performance methodology;
- [Release Operations](../../../scripts/git/README.md) — production/release/push/package mechanics.

Repository Integrity owns classification/tracking/integrity, not those other procedures.

## 22. Automated anti-drift verification gate

The maintained structural/documentation gate is:

`python scripts/verification/anti_drift.py --mode full --format human --verbose`

The verifier is read-only. It discovers the repository root from its own location/current checkout or accepts an explicit `--root`; it does not rewrite documents, mutate RAW/local state, stage files, commit, push, or fetch external URLs.

### Modes and output

- `--mode full` is the authoritative whole-repository mode used by CI.
- `--mode changed` is an optional local working-tree mode that scopes per-document checks to staged, unstaged, and untracked changes while still running global navigation/authority/path-integrity checks.
- `--format human` prints stable diagnostic codes and readable messages.
- `--format json` emits deterministic machine-readable `errors`, `warnings`, `info`, and summary counts.
- `--verbose` adds remediation hints to human output.

Exit behavior is stable:

- `0` — verification completed with no `ERROR` diagnostics;
- `1` — objective anti-drift violations were found;
- `2` — verifier/configuration/runtime failure prevented a valid verification run.

`ERROR` is reserved for mechanically provable contract violations such as required metadata/timestamp defects, missing internal links, case/path mismatches, invalid Current navigation, or required repository-governance paths that are absent. `WARNING` is non-blocking and is used for conservative heuristics such as suspicious mutable snapshot wording or an anchor that cannot be validated robustly.

### Checks owned by the gate

The verifier implements machine-checkable portions of the current governance/integrity contract, including:

- maintained-document metadata and lifecycle placement;
- required timestamp format;
- internal Markdown link and path-case integrity;
- maintained navigation lifecycle checks;
- root `AGENTS.md` structural links;
- superseded-path use in Current navigation where derivable from metadata;
- conservative mutable-snapshot drift detection in maintained general engineering prose;
- required repository-governance paths;
- tracked case-only collisions when Git is available.

Historical/archive evidence, Graphify output, Algorithm References, release manifests/evidence, lockfiles, and generated verification evidence are not subjected to general maintained-document snapshot heuristics. The gate does not encode current Engine file counts, test counts, repository totals, Source hashes, Reference versions, package versions, or Git HEAD as durable truth.

The gate intentionally does **not** decide trading semantics, validate Reaction/Blue/A/S/E/Order correctness, read secret contents, scan RAW payload contents, replace the Testing owner, replace Algorithm Reference Maintenance, or perform the broader Phase 8 semantic/manual documentation audit.

### Tests and CI

Run the verifier's tests with:

`python -m unittest discover -s scripts/verification -p "test_*.py" -v`

The minimal GitHub Actions workflow at `.github/workflows/anti-drift.yml` runs on pushes and pull requests with read-only repository permission. It runs the verifier tests, full-repository verification, and a repeated JSON comparison for deterministic output. Ordinary verification requires no project secrets and does not run Graphify, deploy, release, or mutate repository content.

### Extending the gate safely

When adding a rule:

1. establish the durable owner/rule in [Documentation Governance](../documentation-governance.md), this document, or the appropriate maintained owner;
2. automate only an objectively machine-verifiable portion;
3. define scope and lifecycle exclusions explicitly;
4. choose `ERROR` only for deterministic violations and `WARNING` for ambiguous heuristics;
5. add positive, negative, and false-positive tests;
6. keep diagnostics stable/deterministic;
7. update this owner documentation when the verification contract changes.

Governance remains authority; the verifier is an implementation of selected objective rules. Phase 8 uses this automated gate as one input and remains responsible for the final comprehensive semantic/manual documentation audit.

## 23. Review triggers

Review this document when a durable repository-integrity contract changes, including:

- Git tracking/ignore policy;
- repository content classification;
- generated/evidence tracking policy;
- archive lifecycle/integrity handling;
- path/case or line-ending policy;
- secret-staging protection;
- engineering-vs-production boundary;
- package/archive authority rules.

Do not rewrite it merely because repository counts, test counts, verification totals, hashes, versions, package contents, or Git HEAD change.
