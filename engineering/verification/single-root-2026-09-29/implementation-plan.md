# Single-root repository migration implementation plan

**Goal:** Keep every TradingBot-owned source, test, RAW file, saved state, archive and verification artifact inside the existing TradingBot root.

**Architecture:** Retain the existing chart application and calculation Engine owners. Add an engineering owner for maintained documents, historical evidence and local verification. Retain scripts/ as the public startup exception. Application state belongs to the chart workstation and remains Git-ignored; component verification lives beside its owner.

**Authority:** Current working tree and the user's 2026-09-29 structural request. AGENTS and the current operating protocol govern safety. The current repository-integrity policy explicitly permits storage-only migration without rerunning every large market dataset when calculation and RAW bytes remain exact.

**Constraints:** No trading-code, current-reference, RAW, serialization or browser source changes. Preserve all current user document moves and docs.zip. No commit, push, reset, clean, stash or Graphify execution. Local tests, authentication, caches, archives and generated verification remain ignored. Technical authored text is English.

**Review focus:** Every old path; test discovery; exact references excluding new tests; public startup commands; Vite must deny direct state access and ignore state changes for HMR. Path selection must reject source paths and outside roots.

## Tasks

- [x] 1. Inspect current architecture; query Plugin and inspect canonical reference registry; record working tree, index, full physical inventory and collision-free path map; save recoverable project snapshot.
- [x] 2. Run baseline chart/Python tests, exact reference reconstruction and build. Run complete small continuous XAUUSD and USOIL RAW in both directions; compare the full ordered payload after migration, removing only top-level timings.
- [x] 3. Move each file using the frozen map, hash-checked before movement; preserve all engine source/reference and market-data bytes; stop the verified Vite process before storage migration.
- [x] 4. Repair state resolver and Windows launcher at its existing compatibility path, Vite file access/watching, component test paths, test-only source inventory and verification output paths. Retain runtime module names and browser contracts.
- [x] 5. Normalize engineering document paths; repair current links and commands; classify historical paths; document migration and root exceptions; configure ignore rules for every local-only owner subtree.
- [x] 6. Repeat all applicable baseline checks, compare complete serialized payloads, test actual HTTP storage and access denial, review full tree/path map/diffs, preserve source/RAW identity, package current release artifacts with readme.txt and report limitations.

## Decisions

Use three primary owner directories: apps, engine, engineering. Root README/AGENTS and Git/editor files stay at their tool discovery boundaries; scripts/ is a root tooling exception preserving the public Windows entry point. Windows Restart Manager identified vmware-vmx.exe as holding scripts/launch.bat open after the verified host launcher processes were closed. Retain both original launcher paths to preserve this active external contract; no VMware process is terminated. Keep engine filenames, imports, paths, versions, styles and current reference names intact because they are synchronized/public path contracts.

The old external archive maps into engineering/archive. Previous cleanup proof maps to engineering/verification/history. Current docs/graphify is preserved separately as engineering/archive/repository-graphify to avoid collisions with external historical snapshots. Existing docs.zip is historical user evidence under engineering/archive/documentation. Historical archive contents stay byte-identical and are not active dependencies.

All current state paths use apps/chart/state/{data/raw,cache,secret,tmp}. A configured state root may select this dedicated subtree or a descendant only. It cannot target a source directory or external directory. Vite direct file serving must block state by explicit fs.deny and middleware, while intended /api resources retain their existing HTTP contract.

## Execution ledger

Baseline chart: PASS 159/159. Baseline Python: PASS 21/21. Baseline exact references: PASS 13 production modules per direction. Baseline build: PASS, existing large-chunk warning unchanged.

Full-all-market regression: NOT APPLICABLE to byte-identical calculation modules and inputs under the current storage-integrity policy. Two complete selected RAW inputs provide additional bounded before/after runtime equivalence; they do not establish independent trading correctness or canonical narrative agreement.

Final chart: PASS 164/164 after clean npm ci. Final Python: PASS 21/21. Build: PASS 55 modules, unchanged JS/CSS assets. Exact references: PASS 13 modules each. Real HTTP: PASS 9 checks with 5 forbidden routes returning 403. Browser: PASS canvas/review initialization, no page errors. Windows PowerShell 5 shared-resolver startup functions: PASS. Runtime selected-input payloads: exact ordered equality, excluding only top-level timings, XAUUSD and USOIL, both directions.

Completed moves: 884 of 1,408 mapped initial files. Protected bytes: 16 Engine/reference/style files, 20 RAW/metadata files and 747 archived evidence files unchanged. All mapped destinations exist; sibling TradingBot-Local no longer exists; original index and HEAD unchanged. Authentication was moved natively with size preserved, but no baseline hash was captured and byte-hash equality is NOT_TESTED.

Independent review identified an unintended replacement of the original VMware watcher ignore list. The correction retains **/* in default mode and appends internal-state exclusions; actual-configuration tests proved the failure before repair and passed afterward. Review now has no unresolved implementation blocker. Detailed final evidence, classifications, full trees and verified ZIP entries are in this directory. No Git stage/commit/push or Graphify execution occurred.
