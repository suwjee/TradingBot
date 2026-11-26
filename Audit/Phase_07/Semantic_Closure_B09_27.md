# Phase 07 — Checkpoint 188 / W1 B09-27

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9658be2dda143e889bb770fa9c249866bb8dadb7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB49–TB50, lines 1067–1132; 38 original rows; cumulative B09 686/2276.

[Site evidence](Semantic_Closure_B09_27.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L131). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Reaction and Reset projections, raw/public ownership

- B09-27-F01: The native raw First/Break indexes are integer-converted and indexed directly without a local bounds guard; First tag/time and Break main time come from raw market candles, while mode and box geometry come from public reaction. Confirmation uses raw reaction and default intrabar-start. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1067-L1132) · [Contract](../../Algorithms/V3/19_Serialization.md#L131).
- B09-27-F02: Only previous First timestamp is protected by explicit 0 <= index < full main length. Reset display and second time are formatted from recorded fields with null defaults; this does not independently prove reset crossing. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1067-L1132) · [Contract](../../Algorithms/V3/19_Serialization.md#L134).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
