# Phase 07 — Checkpoint 206 / W1 B09-45

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB65, lines 1792–1814; 26 original rows; cumulative B09 1142/2276.

[Site evidence](Semantic_Closure_B09_45.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L178). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Trend transition absolute identity and actual fiftieth candle

- B09-45-F01: Target icon is actual full-history candle at source index+49, not an extrapolated time or a visible-end-clamped candle. Target lookup uses only upper bound. Direction defaults bullish if attribute absent; exact bullish selects ph fields, previous bearish and icon High, all other values select pl/previous bullish/Low. Absolute source and icon indexes add market offset; prices are stringified, not rounded. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1792-L1814) · [Contract](../../Algorithms/V3/19_Serialization.md#L178).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
