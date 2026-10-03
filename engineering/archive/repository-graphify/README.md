# TradingBot Graphify Artifacts

Generated from commit `822c5ce1c1e7f464d2e08085fd6d991ee1d5d8ed` on 2026-09-23 with Graphify `0.9.63` / `graphifyy 0.9.42`. The graph has 2,691 nodes, 4,526 directed links, and 147 communities. The top-level files mirror the verified dated build in [`rebuild-2026-09-23/`](rebuild-2026-09-23/).

## Scope and confidentiality

- The corpus contains 111 classified files: 92 code files, 17 Markdown documents, and 2 HTML entry pages (340,018 words). The HTML pages contribute their literal local script/style references.
- Eleven detector-unclassified paths are included as file nodes only. The detector-sensitive `apps/chart/src/styles/tokens.css` is represented by its file node and 177 CSS custom-property identifiers only; values are omitted. A redacted scan found no private-key, JWT, or credential-assignment pattern.
- `data/raw/`, `runtime/cache/`, and launcher-declared runtime directories appear as directory-scope markers. Their contents were not traversed; candles, drawings, cache data, credentials, and session values are not included.
- `docs/graphify/` outputs, vendored dependencies, build products, and cache trees are excluded from source input to avoid self-reference and generated noise. The historical 2026-09-18 inventory remains unchanged and is not the coverage manifest for this build.
- No semantic LLM call was made. A bounded host-agent inline layer adds 10 source-located concepts, 44 evidence links, and 2 documented hyperedges from explicit maintained text. It records calculation boundaries and documented security risks without indexing credential/session values. Graphify-inferred edges remain labeled `INFERRED`.

## Outputs

| File | Purpose |
|---|---|
| `graph.json` | Directed, source-linked project graph with community assignments and retained edge-evidence variants |
| `graph.html` | Interactive graph visualization |
| `GRAPH_REPORT.md` | Community hubs, God Nodes, surprising connections, and suggested questions |
| `GRAPH_HEALTH.md` / `graph-health.json` | Raw-extractor diagnostics and verified normalized/serialized graph health |
| `.graphify_labels.json` | Descriptive labels for detected communities |
| `manifest.json` | Build identity, coverage, graph counts, and output hashes |
| `cost.json` | LLM token accounting (zero; inline semantic evidence uses no model tokens) |
| `rebuild-2026-09-23/build_graph.py` | Reproducible rebuild command |
| `rebuild-2026-09-23/raw-run/` | Detection, raw/normalized extraction, diagnostics, and analysis sidecars |

## Health and interpretation

The raw AST extractor initially produced unresolved import endpoints and parallel edges. The rebuild resolves direct imports to in-repository file nodes or explicit external-module nodes, then canonicalizes parallel links while retaining their relations, confidence, source locations, contexts, and occurrence counts in `edge_evidence`. The inline semantic layer is source-located and marked extracted; it does not replace source verification. See `GRAPH_HEALTH.md` for raw and normalized diagnostics; source files remain authoritative, especially for inferred relationships and documented risk findings.

`full-file-inventory.json`, `engine-audit-evidence.md`, and `rebuild-2026-09-19/` are preserved historical/supporting evidence. The 2026-09-19 snapshot was not overwritten.
