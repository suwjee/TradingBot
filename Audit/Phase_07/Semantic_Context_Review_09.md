# Phase 07 — E direct context review, checkpoint 09

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. **INCOMPLETE.** Continuation of [checkpoint 08](Semantic_Context_Review_08.md).

[E Zone direct context ledger](Semantic_Context_E.json) partitions the pinned source and joins its original site IDs to reviewed semantic contexts, compared against the [E procedure contract](../../Algorithms/V3/09_E_Zone.md).

## Important distinctions

- Parent stop starts at exact decision event, inclusive; strict directional lower crossing with exclusive range end; no main fallback.
- Source extrema include complete boundary main candles, not clipped lower-timeframe portions. Equal extrema retain earliest main position.
- Carried Order query precedes parent audit registration; post-stop accepted query follows it. Gate-owned query is evaluated even though its local return is unused. All crossed routes compete on exact Order stop and later First, preserving route order for equal keys.
- E decision is max(parent exact stop,Order exact crossing). Invalid S without independent creation cause is excluded; discovery and acceptance are separate.
- Reconciliation first checks parent ownership and Order validity; the winning candidate is ranked by parent priority before chronology. A strict later decision and strict price improvement are both required to stop an active E. Exact same-source ties retain incumbent.
- Reopened disowned Order races force full checkpoint restart; hard sequence resets clear active E and are projected to StopAll only after native reconciliation. Independent S roots are restored with a separate heap/rerace, not by arbitrary renumbering.
- Previous live results require explicitly settled events and matched evidence; checkpoint rewind is derived from changed candidate/parent/reset dependencies.

| Metric | E newly reviewed | Cumulative | Pending |
|---|---:|---:|---:|
| Source files | 1 | 12 | 4 |
| Contexts | 71 | 373 | — |
| branches | 334 | 1189 | 1944 |
| comparisons | 218 | 823 | 1354 |
| arithmetic | 104 | 406 | 668 |
| calls | 453 | 1862 | 3258 |

[Machine-readable cumulative progress](Semantic_Context_Progress_09.json).

Reaction, Order Audit, Lifecycle and Trading Pipeline remain pending direct review. Shared contexts do not independently certify every nested expression or dynamic dispatch. Phase 08 blocked. No RAW reads, engine execution, benchmark or production edits.
