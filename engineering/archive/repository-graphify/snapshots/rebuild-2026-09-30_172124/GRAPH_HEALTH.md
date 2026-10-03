<!-- created_at: 2026-09-30T17:56:06+03:30 -->
<!-- last_modified_at: 2026-09-30T17:56:06+03:30 -->

# Graph health

- Broken local relative references: 2 (see `graph-health.json` for path and line).
- Import strongly connected components: 0.
- Archive/current non-generic duplicate basename groups: 0. Generic `README.md` and `manifest.json` names are excluded from authority-risk counts.
- Exact-content readable-source groups: 0.
- Maintained source without direct test import: 29 (structural only).
- Tests without direct source import: 10 (structural only).
- Maintained/reference/test file nodes without a non-ownership relationship: 13.
- Dangling graph edges: 0.
- Raw Graphify AST dangling-endpoint edges: 354; unresolved endpoint nodes: 65; raw self loops: 17. These remain visible as AMBIGUOUS evidence.
- Missing ownership: 0.
- Architecture boundary review: browser filtering in `apps/chart/src/main.js:L2825-L2833,L5849` (INFERRED concern).
- Documentation drift: `engineering/docs/verification/repository-integrity.md:L388-L436` names two absent verification/CI paths (observed in live tree).
- Package import probe: FAIL. With `engine/pipeline` on `sys.path`, `import engine.pipeline` raises `ImportError` because `engine/pipeline/__init__.py:L9` exports missing `run_blue_line` from `blue_line_detector.py`.
- Import probe created two ignored Python bytecode files and refreshed existing bytecode cache entries under `engine/`. A narrowly scoped cleanup command was rejected by automatic approval review, so those cache files were left in place. Tracked production Source and chart local state were not edited by this run.
