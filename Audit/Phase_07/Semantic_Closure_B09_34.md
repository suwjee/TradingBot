# Phase 07 — Checkpoint 195 / W1 B09-34

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB59, lines 1495–1504; 6 original rows; cumulative B09 898/2276.

[Site evidence](Semantic_Closure_B09_34.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L161). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Physical audit sort key and main-time identity

- B09-34-F01: Both indexes are converted to int and used directly against detector candles, with no local bounds guard or fallback. The key uses main timestamps, not exact confirmation or stop event. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1495-L1504) · [Contract](../../Algorithms/V3/19_Serialization.md#L161).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
