# Phase 07 — Checkpoint 231 / W1 B09-70

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9867049120fdd0b558150bfb73b642fa4bee4b3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB75, lines 2659–2705; 20 original rows; cumulative B09 1540/2276.

[Site evidence](Semantic_Closure_B09_70.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L82). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Nonreusable geometry, required Reaction directions and state return

- B09-70-F01: Nonreusable path still creates both independent A-stop geometry finders, but runs native Reaction only for required directions; it does not use live.reactions here. Ownership calls native behavior views only when any behavior module enabled, otherwise two separate empty sets. Return requested directions, full maps and supplied live reference. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2659-L2705) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L82).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
