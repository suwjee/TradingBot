# Phase 07 — Checkpoint 255 / W1 B09-94

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `fc39d697b5807ac621dddb80138f4f8ff3b013c7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB96, lines 3594–3638; 21 original category rows; cumulative B09 2175/2276.

[Site evidence](Semantic_Closure_B09_94.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L122). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Response envelope, exact feature gates and direction output

E enabled requires non-null E engine and exact enabled S option. StopAll additionally requires non-null explicit lifecycle_engine, evaluated first. Primary version uses non-null engine test, E version uses truthiness (distinct from E enable test), StopAll version uses explicit lifecycle option non-null independently of S/E enable gates. Blue/A/S flags compare exact enabled strings. actualFrom/To use visible start/end main candle timestamps converted with epoch. Initialize directions empty, assert dict, then build outputs in state.directions encounter order with shared state and timings; repeated direction overwrites its previous key. No price rounding in envelope. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3594-L3638).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
