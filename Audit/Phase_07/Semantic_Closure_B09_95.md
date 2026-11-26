# Phase 07 — Checkpoint 256 / W1 B09-95

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `fc39d697b5807ac621dddb80138f4f8ff3b013c7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB96, lines 3639–3647; 15 original category rows; cumulative B09 2190/2276.

[Site evidence](Semantic_Closure_B09_95.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L122). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Visible reversal replacement and active direction tie rule

Read transition from primary result with None default. Only non-null transition whose index<=visible end replaces entire directions mapping via reversed regime builder with state.live_stages supplied. Candidates enumerate resulting mapping and each group's calculationSegments (absent fallback singleton group, not falsy fallback); tuple uses calculationStartIndex absent default -1 and direction. max compares tuples lexicographically, so ties choose greatest direction string, not last encountered. Default (-1,target with absent bullish fallback) is used only for empty candidates; target lookup is still evaluated for default argument. Extract second tuple element. No activeDirection added on non-reversal path. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3639-L3647).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
