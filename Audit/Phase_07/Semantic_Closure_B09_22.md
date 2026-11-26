# Phase 07 — Checkpoint 183 / W1 B09-22

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9658be2dda143e889bb770fa9c249866bb8dadb7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB41–TB42, lines 820–871; 36 original rows; cumulative B09 498/2276.

[Site evidence](Semantic_Closure_B09_22.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L107). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Physical Order projection, range guards and parent lookup

- B09-22-F01: Bounds are against the full main array, not the visible slice; both First and Break are integer-converted before bounds checks. An exactly non-null crossed record is indexed for main/exact stop separately; no shape fallback. Confirmation uses physical Order direction and default intrabar-start. Stop price is a string even when stop times are suppressed by horizon. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L820-L871) · [Contract](../../Algorithms/V3/19_Serialization.md#L107).
- B09-22-F02: Only a non-null identity performs the audit lookup, but the physical formatter is always invoked, including with null. No formation-Order reconstruction or alternate-key search. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L820-L871) · [Contract](../../Algorithms/V3/19_Serialization.md#L110).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
