# Phase 07 — Checkpoint 191 / W1 B09-30

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9658be2dda143e889bb770fa9c249866bb8dadb7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB54–TB55, lines 1271–1334; 42 original rows; cumulative B09 809/2276.

[Site evidence](Semantic_Closure_B09_30.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L146). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## S Zone projection, recorded parent A and source identity

- B09-30-F01: Only normalized blue enables formation mapping; emitted color is separately formatted from original color. The current Order cause uses the original color string, not the lowercased formation key. Parent A price/stop are recorded fields, and parent Order is looked up independently by physical identity; no replacement by current Order. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1271-L1334) · [Contract](../../Algorithms/V3/19_Serialization.md#L146).
- B09-30-F02: Both attributes are obtained before the null test; zero is allowed, source time is retained as supplied and integer index conversion is not a bounds check. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1271-L1334) · [Contract](../../Algorithms/V3/19_Serialization.md#L149).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
