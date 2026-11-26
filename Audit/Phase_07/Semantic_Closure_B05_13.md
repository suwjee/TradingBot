# Phase 07 — Checkpoint 59 / W1 B05-13

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `7b88b81db3998117e6c4b39fe1d154deb99ab791`. **Local review PASS; B05 INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** OA40, lines 1339–1435; 84 original rows, 7 supplemental items, 5 resolved local clarifications. Order Audit cumulative 914/1892.

[Individual evidence](Semantic_Closure_B05_13.json) matches exact category IDs and AST spans in [immutable AST crosswalk](Decision_Site_Crosswalk_04.json) and [context ledger](Semantic_Context_Order_Audit.json). Pinned source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de` confirmed directly; no direct full Phase 02 inventory re-read claimed. Active contracts [Order A](../../Algorithms/V3/06_Order_A.md), [Order Audit](../../Algorithms/V3/08_Order_Audit.md), [Order Ledger state model](../../Algorithms/V3/State_Machines/04_Order_Ledger.md).

## Verified local behavior

- S-only invalid/E-occupied identity veto, then sequence reset (source,parent_stop]; OA23 first and separate OA19 second with exact type flags, both deadline None.
- Supplement direct only when every existing match has different physical identity, even if matching existing identity carries only reset-leg; empty list passes. No rerun of OA23 single-owner or deadline gate after append. Later register only parent-stop matches; do not assert one registration per call unconditionally.
- Capture previous index only exact dict and truthy carried cache. Existing row geometry retained. New row published, indexed, referenced in new_entries, then cause-set assertion. No rollback.
- Nested family fallback evaluated eagerly even if color present; str of selected value, E number non-null incl zero; exact source-time reset mapping overrides label for any parent type and family empty. Use parent_stop from function, not match slot eight.
- Unique cause min of previous parent-stop events (default None) and strict earlier comparison inside try; Exception conservative earlier true. Actual add outside catch. Equal/later cause retained without earlier-existing flag.
- Invalidate carried only if new rows or earlier existing creation; if no earlier-existing flag and captured index matches ledger object, payload non-null, old size+new size=current size, store pending pair of original index and new-entry list. Validation deferred; no post-stop flush beyond OA26 effects.
- Registration does not locally validate acceptance beyond S/Reset gates, and does not undo partially published state on errors. W2 owner acceptance, direct arbitration and append consumers remain open.

## Findings

- B05-13-F01: Clarify identity-only supplemental-direct gate, reset-leg-only collision and no repeated candidate bound/single-owner check. Active contract amended at line 60 and related clauses; rechecked against pinned source.
- B05-13-F02: Document exact dict capture, cause assertion and publication ordering. Active contract amended at line 60 and related clauses; rechecked against pinned source.
- B05-13-F03: Document eager nested default, exact label overrides and function-owned cause time. Active contract amended at line 60 and related clauses; rechecked against pinned source.
- B05-13-F04: Specify catch boundary, strict earlier flag and exact append preconditions. Active contract amended at line 60 and related clauses; rechecked against pinned source.
- B05-13-F05: Reconcile OAP11/12 registration and cache invalidation with actual supplemental-direct and deferred append path. Active contract amended at line 35 and related clauses; rechecked against pinned source.

## Open dependencies

- W2: S/E source acceptance, sequence reset setter synchronization, OA19/OA23 direct supplementation and possible multiple parent registrations, ledger provenance, OA51 append validation and dependent caches. Do not infer one registered physical row per call solely from OA23.
- W3 separate source-first forensic review pending. No RAW, runtime, differential or benchmark.

No RAW read, trading execution, benchmark, production change or main modification.
