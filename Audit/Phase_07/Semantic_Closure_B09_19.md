# Phase 07 — Checkpoint 180 / W1 B09-19

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9658be2dda143e889bb770fa9c249866bb8dadb7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB37, lines 741–760; 11 original rows; cumulative B09 437/2276.

[Site evidence](Semantic_Closure_B09_19.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L95). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Stop projection and horizon null handling

- B09-19-F01: The main stop-time guard is evaluated before exact-event proof. A valid main time remains visible even when proof is null; an absent or out-of-horizon main time suppresses both fields without checking the event. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L741-L760) · [Contract](../../Algorithms/V3/19_Serialization.md#L95).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
