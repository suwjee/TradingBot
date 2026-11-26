# Phase 07 — Checkpoint 181 / W1 B09-20

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9658be2dda143e889bb770fa9c249866bb8dadb7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB38, lines 761–784; 9 original rows; cumulative B09 446/2276.

[Site evidence](Semantic_Closure_B09_20.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L98). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Reaction confirmation proof and exception boundary

- B09-20-F01: The default intrabar-start flag is true. Only confirmation retrieval and level retrieval are inside the four-exception catch; opposite-direction lookup and strict proof happen outside it. Exact bullish selects boxTop, any other direction boxBottom. Neither fallback selection nor new event search is performed. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L761-L784) · [Contract](../../Algorithms/V3/19_Serialization.md#L98).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
