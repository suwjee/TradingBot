# Phase 07 — Checkpoint 40 / W1 B04-03

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `248b8c3b5d1061d4a5f04123f0fd08b5825dff40`. **Local review PASS; B04 INCOMPLETE; Phase 08 BLOCKED.** S20–S23, lines 403–586; 80 original rows, 8 supplemental items, 5 resolved local documentation omissions/clarifications. S cumulative 364/962.

[Individual evidence](Semantic_Closure_B04_03.json) preserves original category IDs, spans, interpretations and historical navigation. Compared with [S contract](../../Algorithms/V3/05_S_Zone.md), [S state model](../../Algorithms/V3/State_Machines/03_S_Zone.md) and [shared chronology](../../Algorithms/V3/20_Indexes_And_Caching.md). Historical references retained; active edits preserve IDs and line counts.

## Verified local behavior

Type3 scans stable sorted Reset events strictly inside the A-stop/deadline interval. Eligibility uses owner confirmation and first owner Reset; geometry is independent. First hit only, no recross on failed trend qualification. Earliest successful crossing wins; equality retains prior Reset. Type4 processes sorted filtered aligned reactions, rebuilds last-equal candidate geometry, uses next filtered confirmation as exclusive horizon, skips empty windows. First hit only must qualify against public Blue from source main open; first successful aligned row returns. Both call lower index directly; no coarse fallback. Type4 record discards aligned ordinal, sets Order/Reset fields null, preserves parent/source/decision provenance. S40 cross-route priority not yet audited here.

## Findings

- B04-03-F01: First-hit qualification and direct index dependency.
- B04-03-F02: Filtered successor and equal-time window behavior.
- B04-03-F03: First-hit Blue qualification and direct index dependency.
- B04-03-F04: Type3 transition first-hit-only qualification.
- B04-03-F05: Type4 transition filtered successor and first-hit-only qualification.

## Open dependencies

- W1 S31 candidate event-time service and S40 actual route arbitration remain to review.
- W2 verify lower-index presence, owner map consistency, valid source indexes and actual Blue/Reaction chronology including fallback.
- W3 separate source-first forensic review pending.

No RAW read, runtime execution, production change or main modification.
