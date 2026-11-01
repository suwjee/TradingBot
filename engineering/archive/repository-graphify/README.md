---
title: TradingBot Graphify Archive Navigation
document_role: reference
lifecycle: maintained
owner: generated-evidence-navigation
last_modified_at: 2026-10-28T18:08:26+03:30
---

# TradingBot Graphify artifacts

The latest preserved whole-repository graph is [the 2026-10-04 dated snapshot](snapshots/rebuild-2026-10-04_032629/). It describes that execution, not the current checkout. The top-level `graph.json`, `graph.html`, reports, health files, inventory, and manifest are compatibility mirrors of that snapshot. The dated snapshot owns the reproducible `tools/` scripts and is the provenance anchor for those mirrors.

## Recorded snapshot scope

- The recorded Graphify 0.9.63 execution extracted the code then present in Chart, Engine, and project scripts. The graph also inventories that physical repository tree, including archived, verification, generated, dependency, and local-state paths as classified metadata.
- The generating snapshot and Git internals are excluded from the physical inventory to avoid self-reference. Local-state, dependency, archive, and verification contents were not semantically indexed. The detector-sensitive `apps/chart/src/styles/tokens.css` is path-only.
- Maintained Markdown contributes structural local links and explicit path references. Semantic LLM extraction of documents was not run. Inferred and ambiguous relationships remain labeled in the graph and do not establish trading semantics or runtime correctness.
- Read [GRAPH_REPORT.md](GRAPH_REPORT.md) for counts and coverage, [GRAPH_HEALTH.md](GRAPH_HEALTH.md) for integrity results, and [manifest.json](manifest.json) for output hashes. Paths in the manifest are relative to the dated snapshot.

## Historical evidence

The earlier `rebuild-2026-09-19/`, `rebuild-2026-09-23/`, and `snapshots/` entries remain historical evidence. The root `.graphify_labels.json` and `cost.json` are historical sidecars from the prior Graphify build; no new community labeling or semantic token accounting was performed for the recorded structural rebuild. These generated artifacts support navigation only. Root [`AGENTS.md`](../../../AGENTS.md), maintained documentation, accepted references, and live Source retain their respective authority. Validate important relationships directly against current Source. Every new Graphify execution requires explicit user approval for that execution.
