# Phase 07 — Checkpoint 198 / W1 B09-37

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB60, lines 1562–1609; 16 original rows; cumulative B09 944/2276.

[Site evidence](Semantic_Closure_B09_37.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L164). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Eight additive output arrays from shared selections

- B09-37-F01: Each of the eight output arrays is independently constructed in its supplied selection order, with exactly one projection invocation per selected item or pair; no local sorting/filtering. Raw reactions remain full directional reactions for Blue and A. A projection failure propagates rather than returning a shortened array. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1562-L1609) · [Contract](../../Algorithms/V3/19_Serialization.md#L164).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
