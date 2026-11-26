# Phase 07 — Checkpoint 212 / W1 B09-51

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB70, lines 1999–2030; 24 original rows; cumulative B09 1245/2276.

[Site evidence](Semantic_Closure_B09_51.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L79). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Visible aligned bucket bounds and full MarketContext

- B09-51-F01: Both visible boundaries use integer floor alignment except timeframe one unchanged. Bisect left on bucket time yields inclusive start and exclusive end+timeframe, then subtract one. Reject start beyond candle length or end before start before clamping end to last actual candle. Returned market keeps full calculation arrays and default zero offset/trend flags. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1999-L2030) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L79).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
