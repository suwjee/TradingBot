# TradingBot Graphify Artifacts

Generated: 2026-09-18  
Mode: directed, repository-wide, with project source, documentation, RAW data metadata, generated state, images, and vendored dependencies included

## Coverage

No file was excluded as sensitive. Graphify detection reported `skipped_sensitive=0`. The final inventory records every non-Git file present at finalization time, with path, byte size, role, and SHA-256. The inventory file records its own hash as `null` because a file cannot contain a stable hash of itself.

Credential/session container files were included in structural inspection and inventory. Secret values are intentionally not reproduced in prose or reports.

## Final Outputs

| File | Purpose |
|---|---|
| `graph.json` | Directed graph with 31,165 nodes, 72,134 links, and community assignments |
| `graph.html` | Aggregated interactive visualization with 721 community nodes and 2,140 cross-community connections |
| `GRAPH_REPORT.md` | Community, hub, relationship, and suggested-question report |
| `GRAPH_HEALTH.md` / `graph-health.json` | Diagnostics from the raw extraction before graph build |
| `.graphify_labels.json` | Deterministic descriptive labels for all 721 communities |
| `full-file-inventory.json` | Final complete non-Git file inventory and SHA-256 evidence |
| `manifest.json` | Graph build identity, output hashes, and inventory reference |
| `cost.json` | Available usage accounting and limitation note |
| `engine-audit-evidence.md` | Read-only engine findings supplied by the parallel source audit |

## Health Interpretation

The raw extraction contained 807 dangling endpoint edges, 17 self-loops, 4,349 directed same-endpoint collapses, and 4,733 undirected same-endpoint collapses. These diagnostics describe extraction quality before `build_from_json` normalization. The exported `graph.json` has complete node/link endpoints; post-build diagnostics cannot reconstruct edges discarded or collapsed during build.

The graph includes vendored/minified packages because the user explicitly requested every project file. This makes the graph comprehensive but shifts many large communities toward Playwright, Vite, Lightweight Charts, Rolldown, and Lightning CSS. Project-owned architecture should be interpreted together with `TradingBot_Technical_Architecture.md` and `TradingBot_Project_Audit.md`.

Community labels are deterministic heuristics derived from dominant paths and representative symbols. They are navigation aids, not semantic proof.

## Snapshot Versus Final Inventory

Graph extraction was built from a 620-file checkpoint that included task-owned intermediate JSON, scripts, marker files, and caches. After the final graph and health artifacts were verified, those temporary files were removed. The final inventory therefore contains 619 files at the review checkpoint, while `graph.json` intentionally retains 19 file-hierarchy nodes that refer to deleted task artifacts from the extraction snapshot. Those nodes preserve build provenance; they do not assert that the temporary paths still exist. `full-file-inventory.json`, not the graph's file-hierarchy snapshot, is authoritative for final filesystem presence.

## Current directed rebuild

The current-turn code-focused directed rebuild is preserved at `rebuild-2026-09-19/`. It was generated with Graphify `0.9.63` / `graphifyy 0.9.42` from the current worktree and reports 1,240 nodes, 2,774 directed links, and zero dangling endpoints in its diagnostic. The dated README records its command sequence and limitations, including the detector-classified skip of `apps/chart/src/styles/tokens.css`. This older repository-wide snapshot remains preserved as historical/supporting evidence rather than silently overwritten.
