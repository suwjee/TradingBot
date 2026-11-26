# Phase 07 — Checkpoint 42 / W1 B04-05

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `e727bfd89a86cd9aef171701bc8a74b69cbf02ed`. **Local review PASS; B04 INCOMPLETE; Phase 08 BLOCKED.** S29–S36, lines 696–869; 116 original rows, 9 supplemental items, 4 resolved local documentation omissions/clarifications. S cumulative 576/962.

[Individual evidence](Semantic_Closure_B04_05.json) preserves original category IDs, spans, interpretations and historical navigation. Compared with [S contract](../../Algorithms/V3/05_S_Zone.md), [S state model](../../Algorithms/V3/State_Machines/03_S_Zone.md) and [shared chronology](../../Algorithms/V3/20_Indexes_And_Caching.md). Historical references retained; active edits preserve stable IDs and line counts.

## Verified local behavior

Legacy price classification before exact-time refinement; nested trend protects after classification. S30 computes full-main candidate first, then lower remainder if present, later strictly better main wins, ties keep stop main. Candidate event equality scan and unbounded fallback are distinct from observed event. S33 explicit formation first, nonreset S04 or source fallback, Reset first strict lower crossing with per-row normalization. S34 Reset Blue qualification includes internal; S35 strict-after confirmation through event inclusive.

## Findings

- B04-05-F01: Preserve fallback provenance in pre/post timing.
- B04-05-F02: Explicit unclamped lower remainder start and fallback.
- B04-05-F03: Preserve per-row conversion order and explicit/fallback time provenance.
- B04-05-F04: Align state transition with timing fallback.

## Open dependencies

- W2 compare S31 fallback use in Type4, S37 and lifecycle; verify S33 and A10 time flag differences and caller Blue ordering/identity.
- W1 S37 race and S39/S40 arbitration remain; W3 separate review pending.

No RAW read, runtime execution, production change or main modification.
