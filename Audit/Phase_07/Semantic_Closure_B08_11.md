# Phase 07 — Checkpoint 148 / W1 B08-11

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `a50bf552cc758c65791cd31db2d03386f00bc38b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P16 lines 287–325; 31 original rows, 2 supplemental items, one resolved local clarification. Primary cumulative 215/670.

[Site evidence](Semantic_Closure_B08_11.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L92), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact category IDs, spans and procedures matched.

## Matching-leg activation schedule and qualification deduplication

- B08-11-S01: Create fresh default Primary aggregate. Choose run crossing if run is non-null, otherwise native strict crossing. Allocate empty seen-pair set. Enumerate qualifying seeds in generator order. Update earliest qualification before dedup; null short-circuits strict earlier comparison. Normalize both reference and second indexes for identity; omit times. Skip already seen pair even if first seed had no crossing. Mark pair seen before price read/crossing. Read reference main High at integer index and normalize Decimal. Request strictly later upward crossing after qualification. Only non-null hit creates activation. Append hit, reference, second and qualification preserving identity. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L300-L316).
- B08-11-S02: Stable sort by hit time, qualification, raw reference index and raw second index. Only non-null run receives schedule. Materialize sorted activation identities, including empty schedule. Empty activation returns without retained-step replay. Qualified but no crossing sets waiting-for-stopall-break; otherwise keep default. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L317-L325).

## Finding

- B08-11-F01: Qualification minimum includes duplicates and seeds without crossing because it precedes dedup. Mark pair seen before crossing so a later duplicate cannot retry a missing hit. Schedule publication precedes empty-activation return, including an empty schedule; no retained steps are replayed on that return. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L92).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
