# Phase 07 — Checkpoint 172 / W1 B09-11

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `866184b604be85951ceab86ea65b738a04575a36`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB19–TB22, lines 335–372; 24 original rows; cumulative B09 206/2276.

[Site evidence](Semantic_Closure_B09_11.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L62). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Live view refresh, index capacity and visible index predicate

- B09-11-F01: The retained candle list is changed before index construction or suffix refresh; there is no local rollback. Equal length to capacity reuses the index. An absent index forces rebuild from zero, even if caller supplies a later dirty boundary. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L335-L372) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L62).
- B09-11-F02: Lower update is published first. TF1 aliases both candle and index objects; nonshared main is updated separately and may fail after the lower update. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L335-L372) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L65).
- B09-11-F03: The OR guard short-circuits on either null bound without converting index. Only when both bounds exist is index int-converted and checked with inclusive endpoints; no bound normalization. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L365-L372) · [Contract](../../Algorithms/V3/19_Serialization.md#L50).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
