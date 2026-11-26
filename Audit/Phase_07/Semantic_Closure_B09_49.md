# Phase 07 — Checkpoint 210 / W1 B09-49

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB69, lines 1948–1972; 8 original rows; cumulative B09 1203/2276.

[Site evidence](Semantic_Closure_B09_49.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L76). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Full-context rows and lower-only aggregation

- B09-49-F01: Full rows are returned unchanged by timed pass-through; only falsiness rejects empty input. Timeframe one selects lower_only, all other timeframes build both arrays. from/to do not truncate the calculation context, and this wrapper does not sort or repair rows. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1948-L1972) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L76).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
