# Phase 07 — Checkpoint 250 / W1 B09-89

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `22f1df1a1df592fb1b4911d5057f6cf80940b7f4`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB90, lines 3469–3497; 31 original category rows; cumulative B09 2054/2276.

[Site evidence](Semantic_Closure_B09_89.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L104). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Independent regime aggregation and array ordering

Group segments by direction in first-encounter order; segment order is preserved. Exactly one segment returns its original object unchanged. Multiple segments shallow-copy last segment for scalar metadata, then collect every key with a list-valued occurrence in a set (key iteration order is not explicitly stabilized). For each collected key concatenate rows in segment then row order, using [] only for absent key; present non-iterable values can fail, and rows are reused, not recalculated. For bridgeOutput collect each segment mapping or absent default {}, test any truthy mapping; when true, derive bridge keys with dict.fromkeys in first occurrence order and concatenate each key's rows in mapping encounter order. When all mappings are falsy, no separate merged bridge mapping is installed. Remove aggregate calculationEndTime with absent default None, attach original segment list as calculationSegments. No deduplication of public rows, no recomputation of trades or global sort. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3469-L3497).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
