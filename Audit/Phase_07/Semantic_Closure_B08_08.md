# Phase 07 — Checkpoint 145 / W1 B08-08

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `f270019e27cceaf6122cf03aafe7003de6755f9b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P11–P13, lines 211–237; 14 original rows, 2 supplemental items, 1 resolved local clarification groups. Primary cumulative 130/670.

[Site evidence](Semantic_Closure_B08_08.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md), [chronology](../../Algorithms/V3/Chronology/04_Lifecycle_Primary.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; site IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Asymmetric PH/PL Order gate and strictly later RAW crossing

- B08-08-S01: Exact uppercase PH uses only confirmation>=event; any other kind tests First>=gate before strict confirmation>event. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L217-L219).
- B08-08-S02: Upper bound excludes all equal RAW times; truthy above selects strict greater, exclusive right=len(seconds), no local fallback. Position zero valid, map exact timestamp clamp=True. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L224-L236).

## Findings

- B08-08-F01: Clarify exact-kind dispatch, short-circuit and lower-array bounds. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L72).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
