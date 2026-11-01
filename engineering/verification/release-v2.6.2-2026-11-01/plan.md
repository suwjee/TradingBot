---
title: v2.6.2 repository and runtime release plan
document_role: evidence
lifecycle: historical
owner: release-tooling
created_at: 2026-11-01T20:47:11+03:30
last_modified_at: 2026-11-01T20:57:41+03:30
---

# v2.6.2 release plan

**Goal:** Audit the complete live project structure, preserve all user work, publish complete eligible project content to main and dependency-validated runtime content to production, then create GitHub release v2.6.2 through the maintained git.bat workflow.

**Spec:** Current explicit user authorization in this chat; root AGENTS and scripts/git/README.md define release mechanics. No new Auto/Manual functionality is authorized.

**Architecture:** Existing inclusion-first main policy and dependency-derived production inventory own selection. Use the actual main checkout and isolated temporary production snapshots provided by the maintained manager. Independently verify exact remote refs and release/CI metadata after publication. Keep project state/RAW/secrets/dependencies/build/cache/temp excluded and preserved locally.

## Tasks

- [x] Recursively inventory live files, candidate paths, runtime imports and all applicable instructions; preserve initial dirty/index bytes. Classify each folder by producer/consumer/lifecycle. Independent read-only inventory and runtime reviews run in parallel.
- [x] Correct only evidence-backed policy/ignore gaps if present; use current release regression tests. Confirm tag uniqueness, authentication and remote baseline. Run Engine/Chart/docs and exact-source checks, production closure/runtime build validation and a non-publishing maintained Dry Run.
- [ ] Run X:/My-Projects/TradingBot/scripts/git/git.bat, choose Both, tag target production with main-source provenance, create Latest release titled v2.6.2. Existing authorization covers its final Continue confirmation. Inspect candidate tree and validation before supplying confirmation. No force push or history rewriting.
- [ ] Independently compare remote/local main, production and annotated tag/release target; verify main completeness and production inventory, forbidden-path absence, changed/new runtime bytes, release metadata, GitHub checks and final local state. Record any partial failure honestly.

## Safety and initial observations

- Initial main/remote main: c2e7903890dddfaf8526cb9b11dd1c5e490c7410. Initial production/remote production: b73336e64247b42d43838f2a428242bc202eda8d. No v2.6.2 remote tag was present at inspection.
- Snapshot: apps/chart/state/tmp/release-v2.6.2/initial-files.json, before/, initial-status.txt, initial-diff.patch and initial-index.patch;64 existing dirty/untracked files preserved before edits.
- Complete recursive filesystem inventory contains6474 names/sizes outside Git internals, including ignored material; paths alone were inventoried under secrets/local state. The live release policy performs independent Git tracked/untracked/ignored classification.
- Existing engine/engine.zip has18 clean source archive entries and no cache/tmp/dependency members. Preserve it locally; its main eligibility follows current inclusion-first policy and content checks, while production excludes ZIPs.
- Ruling: use the user's requested current main checkout rather than merge the earlier Codex worktree. All legitimate current changes are in release scope; preserve machine-local state and avoid whole-file formatting churn.
- Ruling: do not add redundant directory allowlists if current policy already includes new runtime files automatically. Add folders/rules only when a verified ownership/dependency gap requires them.

## Progress

Pre-publication audit, minimal policy correction and all fresh validation are complete. This historical plan snapshot precedes publication; final results are recorded by the release tag and ignored task receipt.
