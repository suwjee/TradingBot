# Phase 07 — Checkpoint 202 / W1 B09-41

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB62, lines 1701–1730; 35 original rows; cumulative B09 1043/2276.

[Site evidence](Semantic_Closure_B09_41.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L170). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Legacy Order Audit fields, nullable crossing and stable sorting

- B09-41-F01: Truthy public number overrides entry number before int conversion; zero/falsy falls back. Crossed is tested by exact non-null separately for each field, no shape or horizon fallback. First/Break use detector main candles; box source times use display_epoch. Stable final sort by firstTime,breakTime retains encounter order for exact ties. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1701-L1730) · [Contract](../../Algorithms/V3/19_Serialization.md#L170).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
