# Phase 07 — Checkpoint 63 / W1 B05-17

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `798159d64a58d795077606047d75f65e019a5492`. **Local review PASS; B05 INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** OA52, lines 1722–1797; 77 original rows, 6 supplemental items, 4 resolved local clarifications. Order Audit cumulative 1207/1892.

[Individual evidence](Semantic_Closure_B05_17.json) matches exact category IDs and AST spans in [immutable AST crosswalk](Decision_Site_Crosswalk_04.json) and [context ledger](Semantic_Context_Order_Audit.json). Pinned source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de` confirmed directly; no direct full Phase 02 inventory re-read claimed. Active contracts [Order Audit](../../Algorithms/V3/08_Order_Audit.md), [Order Ledger state model](../../Algorithms/V3/State_Machines/04_Order_Ledger.md).

## Verified local behavior

- Null parent decision returns empty before caches. Non-null cache tuple hit incl empty => shallow list. Refresh missing index or empty carried cache; try OA51 then snapshot ledger values and OA50, store tuple even null validation payload. Native query exact datetime and tzinfo object match.
- Native upper bound (start,len(entries)), lower bound (stop,-1) implement strict interval for valid ordinals; sorted set of ordinals recovers ledger insertion order and dedup per row. None creation marker means already proven. Legacy lazily evaluates OA49 in ledger order.
- Skip empty legacy creations first; then read confirmation and stored cross; rejection OR in exact order (legacy no strict hit, confirmation>stop, cross null, cross event<stop). Confirmation and crossing equality allowed. Accepted ledger crossing not recomputed, normalization after eligibility.
- Initial records materialized after accepted traversal; assert First index present. First slice inclusive [lifecycle start,stop]; same confirmation/cross gates, no creation-event test. No cross-route identity dedup.
- Stable sort exact crossing then -int First; equal key preserves accepted-before-initial/traversal order. Cache tuple, return original list on miss, copy on hit. No registration or ledger mutation from eligibility query except dependent cache effects.
- Ordinary index reuse relies on owner lifecycle/invalidation; no repeated prefix validation. Native validation fallback does not swallow errors from actual legacy scan or conversion.

## Findings

- B05-17-F01: Specify cache hit/refresh, null payload, exact query type, sentinel bounds and lazy fallback. Active contract amended at line 108 and related clauses; rechecked against pinned source.
- B05-17-F02: Specify ordered gates, None sentinel, equality and stored crossing without recomputation. Active contract amended at line 108 and related clauses; rechecked against pinned source.
- B05-17-F03: Specify separate inclusive initial route, no cross-route dedup, stable tie and cache publication. Active contract amended at line 108 and related clauses; rechecked against pinned source.
- B05-17-F04: Clarify OLR06/07/09/10 native/legacy and distinct initial path. Active contract amended at line 71 and related clauses; rechecked against pinned source.

## Open dependencies

- W2: reconcile ledger creation ownership, native index freshness, initial-record lifetime and consumer ordering. No cross-route physical dedup assumed.
- W3 separate source-first forensic review pending. No RAW, runtime, differential or benchmark.

No RAW read, trading execution, benchmark, production change or main modification.
