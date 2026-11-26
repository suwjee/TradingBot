# Phase 07 — Checkpoint 214 / W1 B09-53

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB71–TB72, lines 2069–2126; 13 original rows; cumulative B09 1262/2276.

[Site evidence](Semantic_Closure_B09_53.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L68). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## E detector construction and delegated direct geometry

- B09-53-F01: Full range is zero through len(candles)−1, even if caller supplies a narrower display range. Opposite direction delegated to chronology; direct geometry closes over supplied detector map. Only non-null continuation adds both live keyword arguments; default E exceptions immutable empty frozenset, blocked/invalid sets nullable. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2069-L2126) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L68).
- B09-53-F02: Provided order_geometry is checked by exact non-null, not truthiness or callable validation. It receives detector selected by requested geometry direction and same gate/bounds; otherwise delegate that detector's native method. Exceptions propagate. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2069-L2126) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L71).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
