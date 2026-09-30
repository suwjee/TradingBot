# Graphify Rebuild — 2026-09-23

This is the current directed structural snapshot. Rebuild it from the repository root with:

```powershell
python docs/graphify/rebuild-2026-09-23/build_graph.py
```

Snapshot size: 2,691 nodes, 4,526 directed links, and 147 communities.

The script refreshes the detector manifest, AST/Markdown extraction, normalized graph, report, HTML view, diagnostics, cost record, and top-level `docs/graphify/` mirrors. It excludes `docs/graphify/` from source input to avoid indexing its own generated outputs.

## Coverage and limits

- Graphify detected 111 files (92 code, 17 Markdown documents, and 2 HTML entry pages; approximately 339,970 words). HTML contributes literal local script/style references.
- Eleven additional unclassified paths are represented as path-only nodes. `apps/chart/src/styles/tokens.css` is detector-classified as sensitive; a redacted scan found no private-key/JWT/credential-assignment pattern. Only 177 CSS custom-property names are indexed, never values.
- The launcher’s RAW/runtime directories are represented by directory-scope nodes only. Their contents were not read or copied; `runtime/cache/secret` is not traversed.
- A bounded host-agent inline layer adds 10 source-located concepts, 44 evidence links, and 2 documented hyperedges from explicit maintained text. It covers calculation boundaries, numerical/directional contracts, RAW storage, and documented security risks without credential/session values.
- Graphify-inferred code edges remain labeled `INFERRED`; manually resolved module-basename links are also marked inferred. Relationship variants and source evidence survive endpoint canonicalization in `edge_evidence`.
- No semantic LLM call was made. Graphify’s structural code/Markdown extraction is supplemented by the bounded, source-grounded inline layer; this must not be mistaken for an LLM extraction or a fresh security audit.

See `GRAPH_HEALTH.md` for raw extractor limitations and the clean normalized/serialized integrity checks. The graph is navigation evidence, not a substitute for direct source tracing.
