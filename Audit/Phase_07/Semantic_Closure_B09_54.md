# Phase 07 — Checkpoint 215 / W1 B09-54

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB73, lines 2127–2199; 33 original rows; cumulative B09 1295/2276.

[Site evidence](Semantic_Closure_B09_54.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L74). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Full-direction initial Blue/A/S and reusable stage ownership

- B09-54-F01: Fresh stages require null shared_stages and assert non-null E engine. Blue/A use live callbacks only with non-null live; initial S constructed full-range, then native detect or live S. Save initial S as a shallow list copy. Reuse shares Blue/A/detector references and original initial_s_zones, but creates fresh current S list from that initial snapshot; candidate list independently copied. Live E/geometry attributes read only when live non-null. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2127-L2199) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L74).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
