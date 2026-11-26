# Phase 07 — Checkpoint 143 / W1 B08-06

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `f270019e27cceaf6122cf03aafe7003de6755f9b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P09, lines 181–197; 17 original rows, 1 supplemental items, 1 resolved local clarification groups. Primary cumulative 106/670.

[Site evidence](Semantic_Closure_B08_06.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md), [chronology](../../Algorithms/V3/Chronology/04_Lifecycle_Primary.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; site IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Public MBL formation and confirmation horizon

- B08-06-S01: Lazy cycle fallback on any falsy cycles; absent or future MBL skipped. Aggregate direction selects cycle points; min exact decision among eligible points, first tie, yield original objects only after confirmed point. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L187-L195).

## Findings

- B08-06-F01: Clarify aggregate direction and falsy-cycle fallback. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L64).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
