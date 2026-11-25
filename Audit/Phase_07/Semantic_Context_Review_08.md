# Phase 07 — S chronology direct review, checkpoint 08

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. **INCOMPLETE.** Continuation of [checkpoint 07](Semantic_Context_Review_07.md).

[S Zone direct context ledger](Semantic_Context_S.json) partitions the entire pinned source file and connects all inventoried site IDs to explicit reviewed context, compared against the [S procedure contract](../../Algorithms/V3/05_S_Zone.md). This retains native comparisons, arithmetic operators, branch outcomes, call sites and source references.

## Important distinctions

- A strict stop search with any lower rows does not fall back to main candles on a miss. The S decision fallback applies only to an empty lower decision interval and uses the containing main, unlike the A-stop fallback.
- Source selection deliberately differs: earliest equal for ordinary candidate range, latest equal for simple candidate and Type3/4, stop-main owner for equal pre-Order clipped candidate, earlier containing-main owner on equal post-confirmation remainder.
- Type3 considers opposite Reset events in (A stop, deadline), requires owner confirmation <= A stop and first owner Reset > A stop. Its candidate crossing can occur on the Reset event. Type4 considers aligned confirmations in (A stop, deadline), clips search to next aligned confirmation and requires a valid public Blue formation within the inclusive source-to-cross interval. Exact Type3/4 decision tie goes Type3.
- Order-backed lower race compares actual lower positions, not only displayed main times. Same non-null position yields no decision. Main fallback both-predicate ambiguity is evaluated before candidate qualification.
- Shared Order reconciliation accepts a stop at frozen source main time (inclusive lower bound, despite the descriptive docstring's “after”), strictly before current decision, with own confirmation strictly before stop. No additional condition requires Order confirmation after S source. A identity/source price and formation type remain unchanged.
- Live decisions are reusable only through the strictly settled frontier; dependency changes may rewind it; main-only decisions are not cached. CH96 update context includes final commit after detection.

## Coverage

| Metric | S newly reviewed | Cumulative | Pending |
|---|---:|---:|---:|
| Source files | 1 | 11 | 5 |
| Contexts | 69 | 302 | — |
| Branch sites | 238 | 855 | 2278 |
| Comparisons | 171 | 605 | 1572 |
| Arithmetic | 100 | 302 | 772 |
| Calls | 453 | 1409 | 3711 |

[Machine-readable cumulative progress](Semantic_Context_Progress_08.json).

The five remaining direct-review modules are Reaction, Order Audit, E, Lifecycle and Trading Pipeline. Prior rule/procedure/state-machine coverage is retained but not treated as fresh semantic closure. Phase 08 remains blocked. No RAW reads, execution, benchmarks or production changes.
