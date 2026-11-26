# Phase 07 — Checkpoint 64 / W1 B05-18

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `798159d64a58d795077606047d75f65e019a5492`. **Local review PASS; B05 INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** OA53, OA54, lines 1798–1878; 78 original rows, 7 supplemental items, 5 resolved local clarifications. Order Audit cumulative 1285/1892.

[Individual evidence](Semantic_Closure_B05_18.json) matches exact category IDs and AST spans in [immutable AST crosswalk](Decision_Site_Crosswalk_04.json) and [context ledger](Semantic_Context_Order_Audit.json). Pinned source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de` confirmed directly; no direct full Phase 02 inventory re-read claimed. Active contracts [Order Audit](../../Algorithms/V3/08_Order_Audit.md), [Order Ledger state model](../../Algorithms/V3/State_Machines/04_Order_Ledger.md).

## Verified local behavior

- Parent ignored, cache key exact parent_stop and confirmation-index length; cached non-null list incl empty copied. No cause count/parent identity in key; invalidation owned elsewhere.
- Nested gate rejects null cross, cross<=stop then <=confirmation, reset in (stop,cross]. Int physical pair; absent inserts, otherwise strictly earlier (cross,confirmation,positive First) replaces whole match, equal retains first insertion. No extra confirmation>stop test here.
- Materialize initial geometry before ledger, assert confirmation-time list, upper bound excludes equal confirmations; initial records enter accepted-live first.
- Ledger upper bound full tuple (stop,2^63-1,2^63-1), not unconditional strict confirmation for arbitrary indices. Discard indexed confirmation, use current entry. Missing row/reaction, non-datetime confirmation, any null level/source fields skip. isinstance allows subclasses; no confirmation>stop recheck.
- Stored crossing accepted if isinstance tuple, length>=3 and slot2 datetime isinstance only. Otherwise normalize level and recompute, do not write back to ledger. Convert number default0, normalize level again, int source; gate after conversion. Malformed selected inputs may raise, no local catch.
- Stable final sort by cross,confirmation,-First, unlike positive First selection rank. Dict insertion order survives replacement; cache original list and return shallow copy on hit and miss.
- Eager path is source-established fallback, not asserted identical to later lazy optimized stream; index/actual confirmation coherence and sentinel bounds remain W2.

## Findings

- B05-18-F01: Specify cache list copying and strict nested rejection/identity replacement. Active contract amended at line 111 and related clauses; rechecked against pinned source.
- B05-18-F02: Clarify full tuple sentinel, actual entry confirmation and absence of final strict confirmation check. Active contract amended at line 111 and related clauses; rechecked against pinned source.
- B05-18-F03: Specify partial crossing shape checks, recomputation without writeback, conversion order. Active contract amended at line 111 and related clauses; rechecked against pinned source.
- B05-18-F04: Clarify positive First replacement versus negative final sort and stable ties. Active contract amended at line 114 and related clauses; rechecked against pinned source.
- B05-18-F05: Correct broad OLR08 strict confirmation guarantee to index selection plus actual crossing gates, conditional coherence. Active contract amended at line 73 and related clauses; rechecked against pinned source.

## Open dependencies

- W2: index/actual confirmation coherence, integer sentinel range, sequence reset synchronization, cache lifetime and OA55 optimized-stream comparison. No unconditional strict confirmation guarantee on malformed/inconsistent entries.
- W3 separate source-first forensic review pending. No RAW, runtime, differential or benchmark.

No RAW read, trading execution, benchmark, production change or main modification.
