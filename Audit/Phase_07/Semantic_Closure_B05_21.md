# Phase 07 — Checkpoint 67 / W1 B05-21

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `b2b4d65268c4497cb879416eb1dbf662befbf9f7`. **Local review PASS; B05 INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** OA62, OA63, lines 2046–2233; 141 original rows, 8 supplemental items, 7 resolved local clarifications. Order Audit cumulative 1626/1892.

[Individual evidence](Semantic_Closure_B05_21.json) matches exact category IDs and AST spans in [immutable AST crosswalk](Decision_Site_Crosswalk_04.json) and [context ledger](Semantic_Context_Order_Audit.json). Pinned source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de` confirmed directly; no direct full Phase 02 inventory re-read claimed. Active contracts [Order Audit](../../Algorithms/V3/08_Order_Audit.md), [Order Ledger state model](../../Algorithms/V3/State_Machines/04_Order_Ledger.md).

## Verified local behavior

- Accepted E source pairs normalized only index; invalid S cause filter projects source times alone (discards index). OA63 rejects falsey or non-parent-stop; excludes exact S label only when len>4 and source invalid; label accessed before len guard. No complete cause validation.
- Shallow copy every old row with fresh filtered parent cause set. Clear ledger, confirmation index and carried/post-stop cache groups (OA27), then register B legs, then S list followed by numbered list labelled StopAll by reset source or E. Stop resolver ignores label, reads decision and normalized price; skip None, OA40 receives stop[1]. No rollback.
- Recovery only for numbered identities absent from current ledger; skip existing even if causes differ. Normalize zone pair; opposite lookup raw First key, require int Break equals raw zone Break, else construct recorded geometry namespace with source indices/times and internal false. Recover filtered prior parent causes.
- Recover A pairs from truthy initial a_causes else optional singleton fallback; skip null source/stop. If still no causes and carried-live S parent, choose first original S then supplemental matching int source index/raw source time and raw Order pair; add A cause from required S attrs without null filtering. Supplemental S not part of initial parent registration.
- Explicit order_parent_stop_cause_time non-null enables cause, but actual event is zone.parent_stop_event_time. E parent label from first exact raw index/time numbered match, reset source overrides label and family empty regardless type; otherwise zone.family. Filter all causes via OA63, skip empty.
- Normalize stop level for crossing only; ledger stores original zone level and geometry fields unchanged. Null crossing permitted; publish row then index; no local rollback.
- Repeat filter of prior parent causes even for unused physical identities. Skip prior row without valid parent causes even if prior B causes; if current exists merge only parent cause set, assert isinstance set, preserve current geometry/B. Otherwise restore shallow prior mapping with copied cause set (retains other fields including old B references), index original confirmation; no crossing recomputation.
- Stable sorted numbered return by raw source time,index. No final cache invalidation in OA62 beyond delegated calls; cause-only merge coherence is owner dependency, not locally established.

## Findings

- B05-21-F01: Clarify time-only invalid S filter and partial cause shape guard. Active contract amended at line 140 and related clauses; rechecked against pinned source.
- B05-21-F02: Specify shallow snapshot, registration order, owner stop delegation and invalidation scope. Active contract amended at line 140 and related clauses; rechecked against pinned source.
- B05-21-F03: Specify existing identity skip, recorded geometry fallback, initial vs carried S null asymmetry. Active contract amended at line 140 and related clauses; rechecked against pinned source.
- B05-21-F04: Specify explicit cause gate vs actual event, label/family precedence, price representation and row/index ordering. Active contract amended at line 140 and related clauses; rechecked against pinned source.
- B05-21-F05: Clarify retained parent-only criterion, existing vs restored B/geometry behavior, no extra cache invalidation. Active contract amended at line 140 and related clauses; rechecked against pinned source.
- B05-21-F06: Clarify short-circuit and partial shape validation. Active contract amended at line 143 and related clauses; rechecked against pinned source.
- B05-21-F07: Refine OLC03 exact reconstruction and retention conditions. Active contract amended at line 83 and related clauses; rechecked against pinned source.

## Open dependencies

- W2: E accepted source owner, invalid S time projection, original/supplemental S contracts, B registration, canonical/recorded geometry, parent stop chronology, cache freshness after historical cause merge. No assertion all recovered data valid or no errors.
- W3 separate source-first forensic review pending. No RAW, runtime, differential or benchmark.

No RAW read, trading execution, benchmark, production change or main modification.
