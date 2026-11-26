# Phase 07 — Checkpoint 71 / W1 B05-25

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `0fb58e1845ec0002f75d9ddc7d149d11ebc98081`. **Local review PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** OA75, OA76, OA77, lines 2517–2621; 56 original rows, 7 supplemental items, 5 resolved local clarifications. Order Audit cumulative 1841/1892.

[Individual evidence](Semantic_Closure_B05_25.json) matches exact category IDs and AST spans in [immutable AST crosswalk](Decision_Site_Crosswalk_04.json) and [context ledger](Semantic_Context_Order_Audit.json). Pinned source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de` confirmed directly; no direct full Phase 02 inventory re-read claimed. Active contracts [Order Audit](../../Algorithms/V3/08_Order_Audit.md), [Order A](../../Algorithms/V3/06_Order_A.md), [Order Ledger state model](../../Algorithms/V3/State_Machines/04_Order_Ledger.md).

## Verified local behavior

- First lookup int key and one-based input ordinal, last duplicate First wins. Separate one-based enumeration resolves exact confirmations and normalizes First/Break; sort complete tuples, ordinal before reaction object resolves ties. Project confirmation array and initialize empty cache. Owner chronology assumed immutable.
- Evaluate native OA77 eagerly first even when callback absent. Only None callback disables; map exact stop then call with gate/stop/end. Reject missing geometry or missing/null Break; other malformed data may raise.
- Independent First int>=gate (no upper-bound recheck) and confirmation strictly >stop, equality rejected. Owner callback owns geometry and exact chronology.
- Map by normalized First and require full normalized pair match to last-wins entry; mapped number/object used and confirmation recomputed without repeating strict gate, otherwise number zero; no invented native Reaction.
- Native absent => independent; else strict rank (original independent First,current confirmation) vs (native int First,native confirmation), equality retains native. Confirmation can be recomputed after mapping.
- Exact A stop membership cache incl None before main map; miss upper bound excludes equal confirmations; scan confirmation-sorted rows for First>=gate, first hit breaks; store match or None. No stop-crossing gate.
- Source-first local contract, not proof callback chronology or independent/native consistency. S owner main-index wrapper passes no explicit clamp (unlike E wrapper).

## Findings

- B05-25-F01: Specify separate enumeration, stable tuple keys and first lookup duplicates. Active contract amended at line 72 and related clauses; rechecked against pinned source.
- B05-25-F02: Specify eager native query and precise independent rejection/owner mapping. Active contract amended at line 75 and related clauses; rechecked against pinned source.
- B05-25-F03: Clarify recomputed confirmation without final strict check and native tie. Active contract amended at line 75 and related clauses; rechecked against pinned source.
- B05-25-F04: Specify exact membership cache, strict confirmation and inclusive First. Active contract amended at line 78 and related clauses; rechecked against pinned source.
- B05-25-F05: Clarify remap/no-recheck and original First rank. Active contract amended at line 13 and related clauses; rechecked against pinned source.

## Open dependencies

- W2: S owner chronology, native/independent geometry callback and canonical map consistency, remapped confirmation no-recheck, cache lifetime and pipeline consumer. No claim malformed data occurs.
- W3 separate source-first forensic review pending. No RAW, runtime, differential or benchmark.

No RAW read, trading execution, benchmark, production change or main modification.
