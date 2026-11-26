# Phase 07 — Checkpoint 45 / W1 B04-08

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `948de60fc391ad6bf2aa608372edd3755b54df4c`. **Local review PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** S40–S43, lines 1225–1423; 143 original rows, 8 supplemental items, 4 resolved local documentation omissions/clarifications. S cumulative 886/962.

[Individual evidence](Semantic_Closure_B04_08.json) preserves original category IDs, spans, interpretations and historical navigation. Compared with [S contract](../../Algorithms/V3/05_S_Zone.md), [S state model](../../Algorithms/V3/State_Machines/03_S_Zone.md), [continuation](../../Algorithms/V3/State_Machines/07_Continuation.md) and [shared chronology](../../Algorithms/V3/20_Indexes_And_Caching.md). Historical references retained; active edits preserve IDs and line counts.

## Verified local behavior

S40 evaluates both independent routes before comparing exact decision timestamps; Type3 wins equality. S42 audits all sorted A before eligibility, selects physical Order before next-A gate, leaves unresolved ownership open, closes successful window with max(stop,decision+1us). S43 deduplicates physical First/Break by presence of crossing before validating it, accepts supplied crossing shape without independent strict price proof, recomputes only malformed shape, strict confirmation<cross and source<=cross<old decision. Replace only specified fields, preserve original source/price, formation and A provenance; preserve input order.

## Findings

- B04-08-F01: Preserve native confirmation fallback at next-A expiry.
- B04-08-F02: Distinguish presence-only dedup from later crossing validation.
- B04-08-F03: State exact trust boundary for accepted ledger crossing.
- B04-08-F04: Align state machine with presence-only preference and later shape gate.

## Open dependencies

- B05 verify OA lookup/audit/shared-cross contracts; W2 actual accepted ledger shape, physical identity dedup semantics, source index and time compatibility.
- W2 verify next-A confirmation fallback and ownership closure propagation; W3 separate forensic review pending.

No RAW read, runtime execution, production change or main modification.
