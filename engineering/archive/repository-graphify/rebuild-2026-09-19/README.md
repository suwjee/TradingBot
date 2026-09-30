# Graphify Rebuild (2026-09-19)

This snapshot was generated from the current worktree with Graphify `0.9.63` and the installed Python package `graphifyy 0.9.42`.

## Recorded command sequence

```text
graphify update . --no-cluster
graphify cluster-only . --no-label
graphify diagnose multigraph --graph graphify-out/graph.json --json
```

These commands show the original working-directory invocation. The resulting intermediate directory was subsequently moved to `raw-run/` under this snapshot.

The final directed graph was rebuilt through the installed Graphify Python API because this CLI version does not accept `--directed` on `graphify update`. The structural pass covered code plus detected documents; semantic extraction was skipped, so "code-focused" means that the graph's relationships come from AST/source structure rather than LLM document semantics. No application source was changed.

## Coverage and limitations

- 108 files detected: 88 code files and 20 documents.
- One file was classified as sensitive and excluded: `apps/chart/src/styles/tokens.css`. This is a detector limitation to verify manually; it is still covered by the UI source review.
- Semantic extraction was not run because no Gemini key was configured and this snapshot is primarily a code graph.
- The graph contains 1,240 nodes, 2,774 directed links, and 54 communities.
- Diagnostics report zero dangling endpoints, self-loops, duplicate directed pairs, and unverified nodes.
- Graphify relationships are navigation evidence. Source files remain authoritative, especially where generated documentation or inferred edges differ.
- The raw CLI/API intermediates used for this run are preserved under `raw-run/` in this snapshot because deletion was not required for verification and preserving recoverability is safer in the dirty worktree.

## Representative query result

Queries for module dependencies, UI-to-bridge communication, pipeline execution, engine calculations, Bullish logic, Bearish logic, and result propagation returned source-linked nodes. `application initialization` returned no matching node, which is recorded as an unresolved vocabulary/coverage limitation rather than a claim that initialization is absent.
