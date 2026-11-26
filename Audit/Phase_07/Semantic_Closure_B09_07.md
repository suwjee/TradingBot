# Phase 07 — Checkpoint 168 / W1 B09-07

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `866184b604be85951ceab86ea65b738a04575a36`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB12–TB14, lines 213–249; 35 original rows; cumulative B09 134/2276.

[Site evidence](Semantic_Closure_B09_07.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L44). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Live bucket construction and dirty tail selection

- B09-07-F01: Exact type excludes bool and int subclasses; invalid type short-circuits the positive test. TF1 main and lower are the same list object. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L213-L249) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L38).
- B09-07-F02: Initial dirty values are lengths; empty input yields without modifying state. First timestamp is int-converted before checked-row traversal. Tail copies are shallow and only selected on existing list plus equality of previous last raw time or aligned main key; nonshared main is checked separately. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L213-L249) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L44).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
