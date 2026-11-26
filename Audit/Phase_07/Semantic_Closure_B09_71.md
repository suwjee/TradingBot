# Phase 07 — Checkpoint 232 / W1 B09-71

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9867049120fdd0b558150bfb73b642fa4bee4b3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** Declarations, lines 2706–2737; 3 original rows; cumulative B09 1543/2276.

[Site evidence](Semantic_Closure_B09_71.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L89). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Range and visibility state records

- B09-71-F01: DirectionRangeState and DirectionVisibilityState are mutable slotted records of references. Projection lists serve parent joins, not independent public output or feedback. primary_groups has fresh dict default per instance and is keyword-only. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2706-L2737) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L89).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
