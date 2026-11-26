# Phase 07 — Checkpoint 197 / W1 B09-36

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB60, lines 1540–1561; 18 original rows; cumulative B09 928/2276.

[Site evidence](Semantic_Closure_B09_36.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L164). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Pre-range source associations and duplicate precedence

- B09-36-F01: Projection attribute fallback applies only when absent, not when empty or null. S map uses full S alone, while E and StopAll maps iterate pre-range rows followed by selected rows so later selected duplicates win. Each source pair is computed once; only non-null pairs retained. Raw reactions are taken from full directional result. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1540-L1561) · [Contract](../../Algorithms/V3/19_Serialization.md#L164).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
