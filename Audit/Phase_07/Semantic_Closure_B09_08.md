# Phase 07 — Checkpoint 169 / W1 B09-08

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `866184b604be85951ceab86ea65b738a04575a36`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB14–TB16, lines 250–277; 22 original rows; cumulative B09 156/2276.

[Site evidence](Semantic_Closure_B09_08.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L47). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Live RAW checks and staged Decimal cache

- B09-08-F01: Original numeric equality after conversion is not an exact-type test: an integer-equivalent positive value can pass, subject to native conversion/equality; decreasing times fail, equal times pass. The original row is yielded only after updating the captured previous time. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L250-L277) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L47).
- B09-08-F02: Persistent membership is checked first, including values equal under the typed key. Local cache additions remain private until aggregation succeeds; the checked iterator validates lazily during aggregation. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L250-L277) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L50).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
