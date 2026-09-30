# Single-root migration evidence

Status: **STRUCTURAL MIGRATION VERIFIED** on 2026-09-29. All applicable structural checks passed. Complete before/after calculation evidence is **BOUNDED_VALIDATION** for two RAW inputs, both directions; independent trading correctness is not established by this task.

## 1. Initial structural problems

Source/test/documentation owners were scattered across root categories; workstation state and historical artifacts were in a sibling TradingBot-Local directory. Sixteen tracked documentation deletions and nine untracked replacement documents already existed before this task. Those user changes and the untracked docs.zip were preserved. The old resolver explicitly prohibited internal state.

## 2. Architectural reasoning

Browser UI, HTTP middleware and persistence form the chart workstation owner. Python calculation stages and their exact embedded-source contracts form the Engine owner. Maintained guidance, historical evidence and engineering verification form the engineering owner. No trading module extraction or behavior refactor is included.

## 3. Final ownership model

```text
TradingBot/
  apps/chart/                 application, local state, chart tests
  engine/                     calculation source, exact references, Engine tests
  engineering/                docs, historical archives, local verification
  scripts/                    established Windows/VMware launcher contract
  AGENTS.md                   instruction discovery
  README.md                   project entry point
  .gitignore                  local-only owner subtrees
  .gitattributes              exact source bytes and text conventions
  .editorconfig               editor discovery
  .git/                       existing version-control metadata
```

## 4. Complete final tree

The final audit produces the [complete physical file tree](../../verification/single-root-2026-09-29/physical-tree.txt), [complete metadata inventory](../../verification/single-root-2026-09-29/final-physical-inventory.csv) and [source delivery tree](../../verification/single-root-2026-09-29/source-tree.txt). Git internals are represented as a preserved metadata boundary; the index and HEAD are checked independently. Generated dependencies remain beside the application. No root docs/, tests/ or loose archive remains.

## 5. Complete old-to-new map

The [exhaustive path map](../../verification/single-root-2026-09-29/path-map.csv) accounts for all **1,408 initial physical files** in both roots. **884 mapped file moves** completed without overwriting destinations. The two original launcher paths remain compatibility exceptions. Recovery snapshot, initial index and original dirty state remain in the same ignored verification folder. The sibling state folder was removed only after becoming empty. No RAW, saved cache, archive or authentication file was deleted.

## 6. Meaningful naming changes

Maintained documents now use concise responsibility-specific names under engineering/docs. AI protocol belongs to ai; architecture references belong to architecture; source/refactor/test guidance belongs to development; integrity/audit/migration evidence belongs to verification; storage policy belongs to operations. Engine test helpers are standalone verification tools and now live under engine/tests/verification. User docs.zip is preserved unchanged under engineering/archive/documentation.

## 7. Root exceptions

scripts/ preserves an externally used startup contract. Windows Restart Manager identified VMware holding both launch files; the VM process was not terminated. The user closed its project execution before configuration changes. Git/editor/AGENTS/README entries stay at their conventional discovery boundaries. No root archive, RAW, test or loose engineering directory remains.

## 8. Path and configuration repairs

The dedicated state resolver defaults to apps/chart/state and permits profiles beneath it. It rejects external/source paths and escaping junctions. The Windows launcher invokes the same resolver. Component test imports/discovery and test-only production manifests were repaired. Engine filenames, module names, source paths, references and browser source remain unchanged. Vite denies static state access and excludes local state/evidence from its watcher.

Independent review found that an initial watcher edit replaced the existing VMware default `ignored: ['**/*']`. The final configuration preserves that default and appends dedicated exclusions. Two tests import the actual exported configuration in separate processes; the default-watcher test failed before correction and both passed afterward. The existing six state-policy tests were observed RED before the resolver repair and GREEN afterward. Source fingerprints, API handlers and serialized contracts remain unchanged.

## 9. Duplicate and historical content

Historical bundles retain exact bytes and old coordinates. Two separate Graphify bundles remain separately classified to preserve the user's evidence and avoid collisions. Archived copies are not Current production or runnable tooling. No Graphify command was run.

The [recursive old-path audit](../../verification/single-root-2026-09-29/old-path-audit.json) searches moved paths and meaningful former documentation filenames in readable non-private content and classifies retained matches. Dated architecture bodies have leading notes superseding all old paths. The older operating protocol has an explicit current-authority precedence note. Private state is metadata-inventoried; generated dependencies and binary historical bundles are preserved separately. An empty generated benchmark folder was preserved in verification rather than deleted.

## 10. Public compatibility

Keep apps/chart depth, HTTP/SSE endpoints, resource IDs, RAW/sidecar filenames, drawing/calculation/template identities, browser storage keys, named-pipe inputs and dynamic Engine loading. Existing scripts/launch.bat remains valid. Optional external state overrides are intentionally superseded by the user's single-root requirement.

An old external `TRADINGBOT_LOCAL_STATE_ROOT` setting must be removed or changed to the dedicated internal subtree before startup. Local-only tests require the accompanying test bundle on a fresh clone. Application state remains Git-ignored despite being physically inside the checkout.

## 11. Verification

| Check | Baseline | Final evidence |
| --- | --- | --- |
| Chart discovery/suite | PASS 159/159 | PASS **164/164**, exit 0, after clean npm.cmd ci |
| Engine local unit suite | PASS 21/21 | PASS **21/21**, exit 0 |
| Vite production build | PASS 55 modules | PASS **55 modules**; JS/CSS asset names and bytes equal baseline |
| Exact reference reconstruction | PASS 13 modules each | PASS **13 production modules in each directional reference** |
| Syntax, imports and local links | Existing source frozen | PASS Python AST and Node syntax; zero broken current relative imports or links |
| Windows PowerShell 5 launcher | External storage policy | PASS parser, shared default/relative resolver, source rejection and internal directories; profile containing spaces independently checked |
| Clean dependency installation | Existing lock | PASS 18 installed packages, unchanged lock |
| Actual HTTP runtime | Existing API | PASS 9 requests: 4 allowed routes, including exact 14,140-row RAW API; 5 forbidden state/evidence routes returning 403 |
| Actual browser initialization | Existing shell | PASS Chrome headless: chart canvas and review shell initialized; zero page errors |
| Frozen protected bytes | Initial hashes | PASS **16 Engine/reference/style files**, **20 RAW/metadata files**, **747 archived evidence files**; zero protected mismatches |
| Physical ownership/ignores | Two roots | PASS all mapped destinations present, sibling absent, local owners excluded from source delivery |
| Git safety | Original dirty work/index | PASS original index bytes and HEAD unchanged; no staging, commit or push |
| Independent review | Three read-only audits | No unresolved implementation blocker after watcher correction |

The existing large JS chunk warning remains. The actual validation server was stopped after HTTP/browser checks; no validation server is left running. Fresh details are in the [integrity manifest](../../verification/single-root-2026-09-29/integrity-results.json), [chart log](../../verification/single-root-2026-09-29/chart-tests-final.log), [runtime manifest](../../verification/single-root-2026-09-29/runtime-smoke-results.json) and [delivery manifest](../../verification/single-root-2026-09-29/delivery-manifest.json).

## 12. Regression scope

Complete selected XAUUSD input (14,140 RAW rows) and USOIL input (30,935 RAW rows), at 30 seconds, both directions, all pipeline stages and Bridge Output: before/after stable ordered payloads are exactly equal, excluding only top-level timings. This is BOUNDED_VALIDATION and does not claim independent market correctness. Full-all-market regression is NOT APPLICABLE under the storage-integrity policy for unchanged calculation and RAW bytes.

XAUUSD covers 2026-09-16 22:35:00 to 2026-09-17 19:15:35, Asia/Tehran; stable SHA-256 is `a16fef03e75d5931db6c0edc383b0a485cf1ddf53c6a4ea2514525c5f83b4550`. USOIL covers 2026-09-21 22:50:00 to 2026-09-24 00:26:20, Asia/Tehran; stable SHA-256 is `e8c93c2fb51c387322a470e79e83d002a8b1f48ba39284b51722b9be4ff376d0`. Both baseline and final processes exited 0. Collections, ordering, fields, nulls, provenance and all remaining payload content are compared as complete ordered bytes.

Sequential wall times were approximately 1.30/3.39 seconds before and 1.20/2.96 seconds afterward. This bounded sanity check is not a benchmark improvement claim. The state resolver runs at initialization, not in calculation loops. Source-direction safety and target-direction unchanged output are verified for these inputs; independent target-direction correctness and a new mirror/metamorphic campaign are **NOT_TESTED**. Input hashes and stage counts remain in the [runtime comparison manifest](../../verification/single-root-2026-09-29/after-runtime-regression.json).

## 13. Risks and limitations

Four pre-existing canonical Source/Reference narrative scope discrepancies remain disclosed by the Plugin. Exact reconstruction does not resolve those claims. The unsupported package import surface remains unchanged; the normal bridge path is the supported initialization check. Historical archive scripts retain original path assumptions. No authenticated FARAZ action or complete independent trading review is included.

The four narrative discrepancies are `REF-BLUE-ENDPOINT`, `REF-REACTION-SUCCESSOR`, `REF-E-TIE-SCOPE` and `REF-S-MODE-B`. Authentication has no baseline hash by design: native relocation and matching size are verified, but independent authentication byte-hash equality is **NOT_TESTED**. Historical HPZR2 tools retain old source expectations; empty-input proof and absolute-RAW-path comparison limitations remain disclosed rather than represented as current correctness evidence.

Source ZIP delivery excludes private state, local tests, dependencies and historical outputs. The [local test ZIP](../../verification/single-root-2026-09-29/TradingBot-local-tests.zip) restores component verification paths. Existing RAW/authentication state is preserved in this checkout and is not embedded in the source package.

## 14. Final status

**STRUCTURAL MIGRATION VERIFIED.** All 1,408 baseline files are accounted for; 884 moves completed; protected source/RAW/evidence hashes match; all applicable test, build, runtime, launcher, link and ownership checks passed. No broken active structural dependency remains within the reviewed layout. The full diff is classified in the [change ledger](../../verification/single-root-2026-09-29/final-diff-classification.csv). Complete selected-input calculation equality is **BOUNDED_VALIDATION**; this is not an independent global trading-correctness claim.

The [source ZIP](../../verification/single-root-2026-09-29/TradingBot-single-root-source.zip) contains current distributable source and readme.txt. Every packaged source/test entry is compared to the current file bytes. No commit, push, reset, clean, stash or unrelated staging was performed. Start the workstation from the existing root with `.\scripts\launch.bat`.
