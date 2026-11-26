# Phase 07 — Checkpoint 236 / W1 B09-75

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9867049120fdd0b558150bfb73b642fa4bee4b3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB77, lines 2900–2941; 22 original rows; cumulative B09 1637/2276.

[Site evidence](Semantic_Closure_B09_75.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L88). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Final E restoration and Order_B equality invariant

- B09-75-F01: E-map membership controls final root restoration and audit ensure. Stop callback uses S-like attribute presence. Discover final B legs, compare exact signature to converged detector legs before registration; inequality raises, no feedback rerun. Without E, callback uses S first_a_stop from decision_event_time, not source or confirmation. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2900-L2941) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L88).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
