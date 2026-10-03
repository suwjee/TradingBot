<!-- created_at: 2026-09-30T17:56:06+03:30 -->
<!-- last_modified_at: 2026-09-30T17:56:06+03:30 -->

# TradingBot repository graph report

## 1. Repository overview

Live physical files: 1001; directories: 179. The graph contains 2966 nodes and 9549 directed edges. Graphify AST contributed 1652 symbols/modules and 4411 extracted relationship records. This is structural evidence, not trading correctness.

Lifecycle counts: {'maintained': 105, 'generated': 65, 'dependency': 430, 'runtime-data': 90, 'test': 40, 'reference': 2, 'historical': 143, 'verification': 126}. Git internals and the generating snapshot are excluded from self-reference. Dependencies, local state, archived and verification material are classified by path and metadata; historical Markdown is read only to check relative links. Other historical content is not indexed.

## 2. Architecture map

Subsystem counts: {'Root': 4, 'Governance': 2, 'Chart': 52, 'ViteServer': 8, 'GeneratedDist': 3, 'Dependencies': 430, 'FARAZ': 2, 'LocalState': 90, 'ChartTests': 30, 'Engine': 3, 'LanguageCache': 11, 'AlgorithmReferences': 2, 'EngineBridge': 2, 'EnginePipeline': 10, 'EngineTests': 10, 'Archive': 143, 'GraphifyOutput': 51, 'Documentation': 10, 'Verification': 126, 'Tooling': 12}. Engine (`engine/pipeline`, `engine/bridge`) owns calculation; Vite/server owns transport and local orchestration; Chart owns presentation; FARAZ owns acquisition. These boundaries follow current `AGENTS.md` and were checked against live imports/entry points.

## 3. Engine analysis

`engine/bridge/trading_pipeline.py:L25-L38` flat-imports pipeline helpers, `L1669-L1700` dynamically loads detector stages, and `L3004-L3034` serializes output. `engine/pipeline/order_audit_engine.py` is imported by S, E, lifecycle, and the bridge. Both current reference candidates under `engine/algorithms/` contain source-manifest paths linked in the graph to the live Engine files; `verify_order_references.py` and `order_regression.py` glob for these documents. Their source synchronization and semantics were not independently verified in this analysis. A targeted package import with the bridge pipeline path on `sys.path` failed: `engine/pipeline/__init__.py:L9` imports missing `run_blue_line` from `blue_line_detector.py`. This does not establish whether the flat-import bridge path is affected.

## 4. Chart, FARAZ and Vite analysis

`apps/chart/index.html:L15` loads `src/main.js`. `apps/chart/vite.config.js:L234-L254` spawns the Python bridge and `L558-L653` mediates calculation requests. `apps/chart/server/faraz-candle-api.js:L414-L422,L1257-L1290` owns session-bound acquisition routes. Browser filtering of invalid calculation objects at `apps/chart/src/main.js:L2825-L2833,L5849` is an inferred boundary review item, not a confirmed defect.

## 5. Test architecture

Direct test-import links: 40; tests without a direct source import: 10; maintained source files without a direct test import: 29. These are structural links, not coverage or test-quality claims.

## 6. Documentation architecture

`engineering/docs/README.md` is the maintained index. `engineering/docs/documentation-governance.md` classifies maintained, generated, and historical material. `engineering/archive/repository-graphify` is generated evidence. Local broken relative links detected in indexed maintained files: 0; historical broken links: 2.

## 7. Dependency hotspots

- `apps/chart/src/algorithm/content/type-module-summaries.js (95 direct non-ownership relationships)`
- `engine/pipeline/e_zone_detector.py (61 direct non-ownership relationships)`
- `scripts/git/Test-ReleaseWorkflow.ps1 (52 direct non-ownership relationships)`
- `apps/chart/src/algorithm/content/module-summaries.js (43 direct non-ownership relationships)`
- `engine/pipeline/s_zone_detector.py (40 direct non-ownership relationships)`
- `apps/chart/server/raw-resource-store.js (39 direct non-ownership relationships)`
- `engine/pipeline/reaction_engine.py (39 direct non-ownership relationships)`
- `scripts/git/IMPLEMENTATION_PLAN.md (39 direct non-ownership relationships)`
- `apps/chart/src/main.js (36 direct non-ownership relationships)`
- `engine/bridge/trading_pipeline.py (34 direct non-ownership relationships)`
- `engine/pipeline/a_zone_detector.py (32 direct non-ownership relationships)`
- `engineering/docs/documentation-governance.md (30 direct non-ownership relationships)`
- `engineering/docs/architecture/technical-architecture.md (28 direct non-ownership relationships)`
- `engineering/docs/verification/repository-integrity.md (28 direct non-ownership relationships)`
- `apps/chart/tests/unit/raw-resource-store.test.mjs (27 direct non-ownership relationships)`

## 8. Important files

- `AGENTS.md`: project authority and operating boundaries.
- `engine/bridge/trading_pipeline.py`: Engine bridge and serialized output.
- `apps/chart/vite.config.js`: local request and subprocess boundary.
- `apps/chart/src/main.js`: browser calculation and rendering entry point.
- `engineering/docs/README.md`: maintained document index.

## 9. High impact areas

Reverse import/reference edges are marked INFERRED. The machine-readable `analysis.change_impact` map in `graph.json` is the direct one-hop map; it is not proof of runtime propagation.

## 10. Duplicate authority risks

0 non-generic basename groups span archive and non-archive paths; 0 exact-content groups were found among safely readable maintained files. The archived local-tests document still declares `lifecycle: maintained` despite a current testing supersession. Older algorithm references and prior Graphify outputs are historical evidence only.

## 11. Missing relationships

Dynamic Python loads, string-generated references, implicit test calls, and runtime-only routing may lack a direct static edge. A missing direct import is not proof that source is unused. Graphify AST has 354 raw edges with unresolved endpoints and 17 self loops; all raw edges are retained, with unresolved endpoints marked AMBIGUOUS. Confidence and source locations are retained where available.

## 12. Recommended future improvements

Review the current repository-integrity guide's references to absent `scripts/verification/anti_drift.py` and `.github/workflows/anti-drift.yml`. Correct the confirmed `engine.pipeline` package import failure through the owning Engine path after evaluating its callers. Keep generated graph evidence separate from maintained semantics.
