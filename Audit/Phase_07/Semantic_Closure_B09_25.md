# Phase 07 — Checkpoint 186 / W1 B09-25

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9658be2dda143e889bb770fa9c249866bb8dadb7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB45–TB47, lines 987–1043; 35 original rows; cumulative B09 623/2276.

[Site evidence](Semantic_Closure_B09_25.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L119). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Parent and A stop retrieval, exception scopes and stop price

- B09-25-F01: Only the detector call is in the catch; IndexError is not included. Unpacking, integer conversion, bound checks and final timestamp access occur outside it. Exact null detector/result yields null pair; valid index uses full main history and recorded event unchanged. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L987-L1043) · [Contract](../../Algorithms/V3/19_Serialization.md#L119).
- B09-25-F02: The catch includes input price normalization, A confirmation lookup and stop call. Non-null result is unpacked outside the catch; its index is ignored and returned main/event times are used directly. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L987-L1043) · [Contract](../../Algorithms/V3/19_Serialization.md#L122).
- B09-25-F03: Price is stringified independently of whether stop main or exact event is visible. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L987-L1043) · [Contract](../../Algorithms/V3/19_Serialization.md#L125).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
