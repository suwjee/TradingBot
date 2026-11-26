# Phase 07 — Checkpoint 54 / W1 B05-08

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `8b4c74cb5e4126cfb55af8f60fa106d8fbf126c2`. **Local review PASS; B05 INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** OA21, OA22, OA23, OA24, lines 921–1088; 93 original rows, 7 supplemental items, 4 resolved local clarifications. Order Audit cumulative 653/1892.

[Individual evidence](Semantic_Closure_B05_08.json) matches exact category IDs and AST spans in [immutable AST crosswalk](Decision_Site_Crosswalk_04.json) and [context ledger](Semantic_Context_Order_Audit.json). Pinned source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de` confirmed directly; prior partitions checked for overlap. Active contracts [Order A](../../Algorithms/V3/06_Order_A.md) and [Order Ledger state model](../../Algorithms/V3/State_Machines/04_Order_Ledger.md). No direct full Phase 02 inventory re-read claimed.

## Verified local behavior

Eager stop/cross, deterministic identity merge, single parent-stop cause, independent Order_B causes, stable deadlines and shallow cache publication.

- Resolve stop and crossing before prior identity read; strict rank comparison replaces entire match, not merged causes. Existing equal rank retains first.
- At most one parent-stop owner (zero valid). Choose minimum rank; iterate snapshot; remove all parent-stop labels only from losing records, preserve other order/duplicates and clear parent cause time; delete if none.
- Candidate cache five-field native key, non-null tuple incl empty hit returns shallow list. Direct merge precedes optional trend merge, both exact start cause.
- Order_B legs traverse input order; physical First strictly later than start. Existing identity preserves geometry, confirmation, stop, crossing and parent cause time, ordered dedup labels; new identity uses leg number/confirmation, stop/cross, reset-leg and null parent cause.
- Enforce parent ownership before deadline. Earliest exact crossing among surviving records, range_end only if none; optionally min supplied deadline. Include confirmation equal deadline, even unstopped; sort crossing-or-range_end, First, stable tie insertion order.
- Tuple cache snapshot and original fresh list on miss; shallow list on hit. OA24 calls OA23 with E flag default false then filters non-null crossing only, returns first; no second deadline test.
- No local Decimal rounding, price conversion, change to physical geometry or runtime assertion; stop/cross and First/identity services define conditional inputs.

## Findings

- B05-08-F01: Clarify eager stop/cross and whole-record replacement on strict earlier rank. Active source contract corrected at line 48; detailed behavior rechecked against pinned source.
- B05-08-F02: Clarify at-most-one semantics, snapshot and stable remaining cause tuple. Active source contract corrected at line 51; detailed behavior rechecked against pinned source.
- B05-08-F03: Clarify exact cache hit, route order, existing Order_B geometry preservation and ordered cause dedup. Active source contract corrected at line 54; detailed behavior rechecked against pinned source.
- B05-08-F04: Clarify deadline without unconditional range_end cap, stable ties, shallow cache and OA24 default E flag. Active source contract corrected at line 57; detailed behavior rechecked against pinned source.

## Open dependencies

- W2: reconcile accepted B legs, E consumption, cache invalidation and deadline/crossing ownership with OA40/OA42 and downstream E state.
- W3 separate forensic source-first review pending. No RAW, runtime or benchmark.

No RAW read, trading execution, benchmark, production or main modification.
