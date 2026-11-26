# Phase 07 — Reaction direct context review, checkpoint 11

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. **INCOMPLETE.** Continuation of [checkpoint 10](Semantic_Context_Review_10.md).

[Reaction direct context ledger](Semantic_Context_Reaction.json) partitions the pinned source and links original site IDs to semantic contexts, compared with [Reaction](../../Algorithms/V3/01_Reaction_Engine.md), [Indexes and caching](../../Algorithms/V3/20_Indexes_And_Caching.md), and [Live Bridge](../../Algorithms/V3/18_Live_Bridge.md).

## Important distinctions

- Directional invalidation/Reset wins an exact lower-position tie. Post-confirmation Reset starts strictly after the hit (+1us), whereas lower extrema through confirmation include the hit row.
- The directional reference may seed a Mode B candidate from a RED Break using full main geometry. Unified same-candle reuse additionally requires exact analysis, no outward strict stop in the remainder, and uses lower extrema across the entire Break interval.
- A direct Reset search can return a later confirmed First while an earlier First remains pending; live checkpoints preserve that possibility of replacement. Geometry-only search bypasses owner invalidation.
- Order gate restart wins equal lower positions. Earliest geometry chooses the first main with confirmation and smallest First index within it, not minimum exact lower confirmation across its candidates.
- MarketChronology confirms from valid intrabar start or Break open and falls back to Break open. A calls with intrabar disabled. The detector's analysis uses a different window that can begin before Break.
- Canonical Mode A Order stop uses contextual main extremes through Break inclusive. Other modes inherit prior opposite Reaction edge.
- Live crossing history excludes the unsettled last lower candle. Exact source identity governs shared index reuse. Preview does not commit the live Reaction cursor.
- Actual source distinctions override descriptive intent; the geometry-only cache has a lookup but no write in that method, gate_event is unused in the A-stop finder, and _append_reaction returns true despite a caller retaining a false-result branch.

| Metric | Newly reviewed | Cumulative | Pending |
|---|---:|---:|---:|
| Source files | 1 | 14 | 2 |
| Contexts | 96 | 539 | — |
| branches | 555 | 2030 | 1103 |
| comparisons | 453 | 1470 | 707 |
| arithmetic | 279 | 789 | 285 |
| calls | 590 | 3047 | 2073 |

[Machine-readable cumulative progress](Semantic_Context_Progress_11.json).

Order Audit and Trading Pipeline remain pending direct review. Shared semantic contexts are not independent nested-expression certification. Phase 08 blocked. No RAW reads, engine execution, benchmark or production edits.
