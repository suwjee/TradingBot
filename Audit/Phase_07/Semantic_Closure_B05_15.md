# Phase 07 — Checkpoint 61 / W1 B05-15

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `7b88b81db3998117e6c4b39fe1d154deb99ab791`. **Local review PASS; B05 INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** OA45, OA46, OA47, OA48, OA49, lines 1524–1643; 66 original rows, 7 supplemental items, 5 resolved local clarifications. Order Audit cumulative 1036/1892.

[Individual evidence](Semantic_Closure_B05_15.json) matches exact category IDs and AST spans in [immutable AST crosswalk](Decision_Site_Crosswalk_04.json) and [context ledger](Semantic_Context_Order_Audit.json). Pinned source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de` confirmed directly; no direct full Phase 02 inventory re-read claimed. Active contracts [Order A](../../Algorithms/V3/06_Order_A.md), [Order Audit](../../Algorithms/V3/08_Order_Audit.md), [Order Ledger state model](../../Algorithms/V3/State_Machines/04_Order_Ledger.md).

## Verified local behavior

- Non-null tuple cache hit includes empty, no secondary rebuild. Iterate initial ledger values in insertion order, normalize level and compute crossing before int ordinal/source conversion; stable First/confirmation/First-index/Break-index sort; publish primary tuple first.
- Project First times, group same record references by First, tuple buckets, stable independent confirmation sort (confirmation,First time,First index,Break index), publish tuple then confirmation times. No local rollback or validation of immutable initial ledger premise.
- Static OA46 unpacks eight-field record, drops First, preserves all remaining fields and supplied causes, null parent cause time. No stop/cross recomputation; tuple shape assumed.
- OA47 entry path reads reaction, confirmation, normalizes level, computes crossing before int ordinal/source conversions, retains source time, supplied cause labels, null parent cause time. No geometry copy.
- Clamped gate main from self.times, force materialization, assert by-First non-null; exact bucket, confirmation>=stop, crossing non-null and >=stop. Convert carried-live; min crossing then recomputed First; first tie, empty None.
- Collect parent-stop event only; if multiple reduce to minimum, otherwise preserve zero/one; append every B physical confirmation in input order, including duplicates. No sort/dedup across categories or validation/fallback here.
- Run-local initial immutability is conditional: owner retains nonempty initial audit mapping by reference; no automatic mutation detection in these helpers. Cache may be partially published if secondary indexing fails. Cross-owner lifecycle and native validation OA50 remain open.

## Findings

- B05-15-F01: Clarify lazy tuple/cache publication order, same record identities, stability and conditional immutability. Active contract amended at line 87 and related clauses; rechecked against pinned source.
- B05-15-F02: Specify OA46 no recompute and OA47 eager crossing before integer conversions. Active contract amended at line 90 and related clauses; rechecked against pinned source.
- B05-15-F03: Specify exact gate bucket, assertion, inclusive confirmation/cross and min tie. Active contract amended at line 96 and related clauses; rechecked against pinned source.
- B05-15-F04: Specify native iteration, parent minimum only and B duplicate preservation. Active contract amended at line 99 and related clauses; rechecked against pinned source.
- B05-15-F05: Clarify initial gate ownership and lazy index dependence. Active contract amended at line 70 and related clauses; rechecked against pinned source.

## Open dependencies

- W2: initial ledger immutability and alias lifetime, chronological alignment, cached secondary publication, recorded A owner and OA50/OA51 native index validation; OA49 malformed provenance behavior remains conditional.
- W3 separate source-first forensic review pending. No RAW, runtime, differential or benchmark.

No RAW read, trading execution, benchmark, production change or main modification.
