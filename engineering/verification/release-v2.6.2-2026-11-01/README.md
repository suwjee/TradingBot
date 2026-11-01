---
title: v2.6.2 pre-publication structure and release validation
document_role: evidence
lifecycle: historical
owner: release-tooling
created_at: 2026-11-01T20:57:41+03:30
last_modified_at: 2026-11-01T20:57:41+03:30
---

# v2.6.2 pre-publication validation

This report records the audited candidate before publishing through the maintained `scripts/git/git.bat`. The annotated GitHub v2.6.2 tag/release is the final publication authority and records the exact production commit and main source SHA. No final remote success is asserted by this pre-publication record.

## Structure and branch classification

The complete live project was recursively inventoried, including ignored names/sizes, while excluding Git's internal database. The initial inventory contained6474 files; dependencies and local state were inventoried by metadata without printing their content. Initial staged/unstaged/untracked work was preserved in ignored task backups before editing.

| Owner/class | main | production |
|---|---|---|
| Chart frontend/server/assets/manifests | Included | Included from runtime-owned roots and validated imports |
| Engine package markers, pipeline and bridge | Included | Included |
| Startup scripts | Included | Included |
| Tests and verification/release tooling | Included | Excluded |
| Maintained docs, AI companion guidance, accepted References | Included | Excluded |
| Classified engineering/archive/Graphify evidence and clean source ZIPs | Included | Excluded |
| Curated BaseLine reference data | Included where current policy allows | Excluded |
| Acquired RAW, drawings/calculations/templates, sessions and other local state | Excluded, preserved locally | Excluded |
| Dependencies, build outputs, caches, tmp/temp, bytecode and editor state | Excluded, preserved locally | Excluded |

The existing ignore and main policies already cover the new project paths. No broader exclusion or directory relocation was needed. All eight eligible ZIP archives passed disposable/unsafe-member inspection. `engine/engine.zip` remains legitimate source-package evidence on main, not production runtime.

## Minimal corrections

Two obsolete filename exclusions prevented the documented runtime-ownership policy from including `engine/bridge/__init__.py` and `apps/chart/server/raw-integrity.js`. They were removed. The package marker is part of the maintained production Engine inventory; the pure server helper is retained like other unreferenced runtime neighbors. The new regression uses the maintained policy itself and first failed on the missing package marker, then passed after correction. Category exclusions and import validation remain intact.

The existing untracked GEMINI guide was retained. Its authority order was aligned to root AGENTS, intended-vs-executable semantics separated, and absolute sibling paths/counts/generated descriptions explicitly classified as recorded workstation navigation requiring live rediscovery. Existing creation time, links and companion content were preserved. GPT_bot companion rules already follow the root authority model and were not edited.

## Fresh checks

| Check | Result |
|---|---|
| Main policy/tracked forbidden artifacts/ignored meaningful paths | PASS: no drift or policy errors |
| Candidate sensitive-content markers and eligible ZIP safety | PASS: no errors or skipped-large-file gap |
| Production runtime closure and file-set integrity | PASS |
| Regression for maintained runtime package/helper inclusion | PASS after witnessed failure |
| Release Workflow | PASS:7 test groups |
| Git Manager | PASS:17 tests, including actual git.bat publishing to disposable local remote |
| Engine+documentation tests | PASS:273 tests (242 Engine and31 documentation) |
| Chart unit suite | PASS:260 tests |
| Both exact Algorithm References | PASS:14 dynamically discovered Python owners each |
| Full anti-drift | PASS:zero diagnostics |
| Maintained non-publishing release DryRun | PASS |
| Isolated production tree/state exclusion/sensitive scan | PASS |
| PowerShell parse, JavaScript syntax, Python AST, bridge --help | PASS |
| Clean production npm ci and npm run build | PASS |
| New independent market/FARAZ/browser replay in this release task | NOT RUN: no calculation/UI behavior was changed by this packaging audit |

The prior approved primary-mirror and100px-icon changes are part of the release source. Their earlier bounded market/browser evidence remains in its dated reports; those past results are not reused as a new release-task market PASS. No Auto/Manual feature is included. Dependencies/build products created during validation stay in disposable isolated worktrees and are not part of either committed tree.

## Publication procedure

Use the actual interactive git.bat, choose Both, select production as the annotated v2.6.2 tag target with main-source provenance, title the GitHub release v2.6.2 and mark it Latest. Validate the exact preview before answering its final confirmation under the user's explicit authorization. Verify remote branches/tag/release and checks independently afterward. No force-push or user-work cleanup is authorized.

[Plan](plan.md) | [Final candidate path inventory](inventory.json) | [Maintained release operations](../../../scripts/git/README.md)
