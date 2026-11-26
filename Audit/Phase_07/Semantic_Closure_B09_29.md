# Phase 07 — Checkpoint 190 / W1 B09-29

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9658be2dda143e889bb770fa9c249866bb8dadb7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB53, lines 1181–1270; 55 original rows; cumulative B09 767/2276.

[Site evidence](Semantic_Closure_B09_29.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L143). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## A Zone projection, Blue associations and exact current Order

- B09-29-F01: Both Blue ordinals are integer-converted and looked up independently in the full map; null associations yield null formation pairs, but recorded Blue stop fields are still projected. Only each formation main time is emitted, not its resolved formation event. Reaction ordinal uses inclusive one-based bounds; missing association suppresses exact confirmation but leaves recorded First/Break times. Confirmation uses intrabar-start false. Parent is constant null; currentOrder requires exact A cause with null family and proven stop. Own stop projection is separate. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1181-L1270) · [Contract](../../Algorithms/V3/19_Serialization.md#L143).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
