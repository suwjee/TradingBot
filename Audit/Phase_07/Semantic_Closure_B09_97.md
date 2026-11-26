# Phase 07 — Checkpoint 258 / W1 B09-97

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `fc39d697b5807ac621dddb80138f4f8ff3b013c7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB98/TB99/TB100, lines 3670–3705; 17 original category rows; cumulative B09 2232/2276.

[Site evidence](Semantic_Closure_B09_97.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L128). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Calculation cache scope and live input entry points

Scope captures three timestamp caches in order local datetime, epoch, display epoch; clears each before optional reaction.clear_market_indexes call. Setup precedes try/yield; after yield finally clears optional indexes first then all timestamp caches in same order. If setup fails no yield/finally; if index cleanup raises, subsequent cache loop not reached. Both live entry points delegate common runner; RAW uses row preparer and singleton tuple (rows,), bucket path uses second/main buckets then live_views and bucket_delta, preserving optional None values. Union annotations are type expressions, not trading arithmetic. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3670-L3705).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
