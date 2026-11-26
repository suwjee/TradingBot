# Phase 07 — Checkpoint 170 / W1 B09-09

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `866184b604be85951ceab86ea65b738a04575a36`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB14/TB17, lines 278–305; 19 original rows; cumulative B09 175/2276.

[Site evidence](Semantic_Closure_B09_09.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L53). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Live append commit, rollback and settled boundaries

- B09-09-F01: The rollback try begins after new cache keys, suffixes and last timestamp are published; it covers delta construction and the consumer's yield body, not earlier commit assignments. Restore lower suffix, nonshared main suffix, timestamp and delete newly inserted keys, then rethrow BaseException. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L278-L305) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L44).
- B09-09-F02: Settled lower and main counts are independent exclusive boundaries derived from actual list lengths; no estimate of missing RAW slots. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L278-L305) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L53).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
