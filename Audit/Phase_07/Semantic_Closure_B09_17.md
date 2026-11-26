# Phase 07 — Checkpoint 178 / W1 B09-17

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9658be2dda143e889bb770fa9c249866bb8dadb7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB34–TB35, lines 690–700; 7 original rows; cumulative B09 394/2276.

[Site evidence](Semantic_Closure_B09_17.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L86). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Exclusive projection horizon and temporal membership

- B09-17-F01: The horizon uses the selected last visible main candle's timestamp and chronology timeframe; no independent fallback, bounds correction or RAW extension. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L690-L700) · [Contract](../../Algorithms/V3/19_Serialization.md#L86).
- B09-17-F02: Null is rejected before horizon computation; equality with horizon fails. There is no lower-bound test in this helper. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L690-L700) · [Contract](../../Algorithms/V3/19_Serialization.md#L89).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
