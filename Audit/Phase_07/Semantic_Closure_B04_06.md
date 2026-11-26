# Phase 07 — Checkpoint 43 / W1 B04-06

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `b06351ea69da4a656d3a671d07bf8ec751974e71`. **Local review PASS; B04 INCOMPLETE; Phase 08 BLOCKED.** S37, S38, lines 870–1053; 98 original rows, 7 supplemental items, 3 resolved local documentation omissions/clarifications. S cumulative 674/962.

[Individual evidence](Semantic_Closure_B04_06.json) preserves original category IDs, spans, interpretations and historical navigation. Compared with [S contract](../../Algorithms/V3/05_S_Zone.md), [S state model](../../Algorithms/V3/State_Machines/03_S_Zone.md) and [shared chronology](../../Algorithms/V3/20_Indexes_And_Caching.md). Historical references retained; active edits preserve IDs and line counts.

## Verified local behavior

Nonempty lower route queries Order stop independently before candidate qualifiers; no local lower-index null guard. Candidate gate uses truthiness and bounded lower lookup. Normal mode gates by earliest nonnull matching Reset Blue or next trend confirmation, not both. Fallback mode tests qualification only on winning first candidate. Neither or same position null; strict earlier Order red. Empty lower route uses containing main and checks both price/time predicates before any qualifier; unqualified candidate may continue. Type3 emits no Order fields.

## Findings

- B04-06-F01: Explicit lower index dependency and evaluation order.
- B04-06-F02: Distinguish raw position ambiguity from qualification or timestamp equality.
- B04-06-F03: Remove implication that candidate must be Blue-qualified before ambiguity.

## Open dependencies

- B05 verify Order crossing predicate and canonical stop geometry; W2 actual lower-index availability, position mapping and fallback reachability.
- W3 separate forensic review pending.

No RAW read, runtime execution, production change or main modification.
