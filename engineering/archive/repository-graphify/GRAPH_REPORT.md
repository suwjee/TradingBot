<!-- created_at: 2026-10-04T03:38:42+03:30 -->
<!-- last_modified_at: 2026-10-04T03:38:45+03:30 -->

# TradingBot repository graph report

## Scope

The live tree contains 1456 physical files and 344 directories outside Git internals and this generating snapshot. The directed graph has 4455 nodes and 14460 edges across 20 classified subsystems. Graphify 0.9.63 extracted 2516 nodes and 6888 edges from 137 current code files. Historical, generated, dependency, verification, and local-state content is represented by path and metadata only; historical Markdown receives local-link checks. The source code extraction and structural documentation links do not establish trading correctness.

## Relationships

- ownership: 6032
- calls: 2813
- contains: 1464
- references: 1257
- method: 464
- imports: 456
- imports_from: 421
- rationale_for: 404
- impact: 383
- external: 382
- documentation: 191
- indirect_call: 73

Graphify AST calls and reverse impact edges retain their confidence labels. Inferred edges are navigation hints; direct Source is required for important dependency decisions.

## Main subsystems

- Dependencies: 430 physical files
- Verification: 351 physical files
- LocalState: 226 physical files
- Archive: 143 physical files
- GraphifyOutput: 107 physical files
- Chart: 52 physical files
- ChartTests: 36 physical files
- Engine: 17 physical files
- Root: 14 physical files
- ViteServer: 14 physical files
- Tooling: 13 physical files
- LanguageCache: 11 physical files
- EngineTests: 11 physical files
- EnginePipeline: 10 physical files
- Documentation: 10 physical files
- GeneratedDist: 3 physical files
- Governance: 2 physical files
- FARAZ: 2 physical files
- AlgorithmReferences: 2 physical files
- EngineBridge: 2 physical files

## High-link files

- `apps/chart/src/algorithm/content/type-module-summaries.js (95 direct links)`
- `engineering/docs/architecture/technical-architecture.md (67 direct links)`
- `scripts/git/Test-ReleaseWorkflow.ps1 (66 direct links)`
- `engine/pipeline/e_zone_detector.py (62 direct links)`
- `apps/chart/src/main.js (59 direct links)`
- `apps/chart/vite.config.js (45 direct links)`
- `apps/chart/src/algorithm/content/module-summaries.js (43 direct links)`
- `engine/pipeline/s_zone_detector.py (41 direct links)`
- `engine/pipeline/reaction_engine.py (40 direct links)`
- `apps/chart/server/raw-resource-store.js (39 direct links)`
- `scripts/git/IMPLEMENTATION_PLAN.md (39 direct links)`
- `engine/bridge/trading_pipeline.py (38 direct links)`

## Test and documentation signals

Static analysis found 41 maintained source files without a direct test import and 11 test source files without a direct source import. These are structural signals, not test coverage. It found 0 broken local links in maintained documents and 2 in historical documents.

## Extraction and interpretation limits

AST extraction completed for all 137 selected current code files. Semantic LLM extraction of documents was not run; document relationships are local links, explicit path references, and source manifest references. The raw AST has 355 unresolved-endpoint edges and 22 self loops. Unresolved endpoints remain as AMBIGUOUS nodes in the final graph. Full physical inventory coverage does not mean full content analysis.

## Verification

- physical_file_parity: PASS
- edge_endpoints: PASS
- ast_edge_integration: PASS
- ast_source_completion: PASS
- sensitive_css_content_excluded: PASS
- working_tree_outside_archive: PASS
- semantic_extraction: NOT RUN
- runtime_or_trading_tests: NOT RUN
