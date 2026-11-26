# Phase 07 — Checkpoint 171 / W1 B09-10

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `866184b604be85951ceab86ea65b738a04575a36`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB18, lines 306–334; 7 original rows; cumulative B09 182/2276.

[Site evidence](Semantic_Closure_B09_10.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L56). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Engine candle creation and stable positional indexes

- B09-10-F01: Enumerate from caller-specified start index, retain bucket order; format six local wall-clock components and invoke the engine classifier with original Open/Close. OHLC objects are supplied without a further normalization step. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L306-L334) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L56).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
