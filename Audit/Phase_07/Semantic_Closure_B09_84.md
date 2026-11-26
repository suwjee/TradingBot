# Phase 07 — Checkpoint 245 / W1 B09-84

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `2dda09909aae83e73299ac587d313f7a24f5d7e9`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB84, lines 3325–3349; 48 original category rows; cumulative B09 1948/2276.

[Site evidence](Semantic_Closure_B09_84.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L195). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Primary physical-source association and directional cycle counts

Select raw opposite points and final resolved main points: bullish highs native/lows final; otherwise highs final/lows native. Main row lookup keys are exact pairs (local source index, serialized source epoch); dictionary construction is last-row-wins for repeated keys. Main-row cycleIds use original main points, short-circuit exact source index, exact epoch, decision<=end and non-null cycle id; stable first-occurrence deduplication follows transformed ids. Cycle rows retain visible cycle order and require non-null id. highCount always invokes selected(cycle.highs); bullish lowCount similarly serializes selected lows, but nonbullish lowCount counts already-selected low rows by cycleId equality. Main-side lowIds/highIds use original cycle points with decision<=end and existing key membership; dedup by resulting row id in encounter order, not an independent sort. Trigger fields distinguish main timestamp and exact event. No new trading decision or implicit symmetry correction. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3325-L3349) · [Primary owner](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L128-L195).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
