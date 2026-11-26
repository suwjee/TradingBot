# Phase 07 — Checkpoint 246 / W1 B09-85

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `2dda09909aae83e73299ac587d313f7a24f5d7e9`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB84, lines 3350–3370; 21 original category rows; cumulative B09 1969/2276.

[Site evidence](Semantic_Closure_B09_85.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L195). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Post-primary orders and strict qualification status horizon

Post-primary orders traverse visible cycles then their post_pl3_orders in encounter order for both directions. A stop index strictly greater than end skips the order; equal is retained and no local missing-stop fallback exists. Accepted orders are relabeled against the same finalized primary and serialized with opposite conceptual owner (bearish if bullish, otherwise bullish); non-null cycle id optionally adds transformed cycleId. Qualification defaults None only for absent attribute. Horizon is end candle timestamp plus timeframe. If visible cycles exist, last encounter's status wins unconditionally; otherwise non-null qualification strictly earlier than horizon yields waiting-for-stopall-break, while equality, later or absent qualification yields waiting-for-matching-behaviors. Return key postPH3Orders only for exact bullish flag, otherwise postPL3Orders; no sort or requalification. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3350-L3370) · [Primary owner](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L128-L195).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
