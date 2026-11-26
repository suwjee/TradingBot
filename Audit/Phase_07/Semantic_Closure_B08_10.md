# Phase 07 — Checkpoint 147 / W1 B08-10

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `f270019e27cceaf6122cf03aafe7003de6755f9b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P15, lines 248–286; 45 original rows, 3 supplemental items, 1 resolved local clarification groups. Primary cumulative 184/670.

[Site evidence](Semantic_Closure_B08_10.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md), [chronology](../../Algorithms/V3/Chronology/04_Lifecycle_Primary.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; site IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Matching Behavior Leg seed, StopAll and dominant qualification

- B08-10-S01: StopAll occupies integer index only; all StopAll emitted, S then E excluded by occupied index or exact Boolean False; validity read after occupancy gate. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L250-L256).
- B08-10-S02: Sort exact source time, rank, raw index; normalize dedup index, add before any skip. Every StopAll clears owner/confirmations/qualified and number>=3 determines reference. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L257-L272).
- B08-10-S03: Normalize family and conditional number then invoke LC05. Identity-equal owner skips; reset confirmations on first/new count1. Append current decision and set qualified before max/yield, no activation break search. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L273-L284).

## Findings

- B08-10-F01: Clarify exact False, raw sort versus normalized dedup, owner identity and mutation order. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L88).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
