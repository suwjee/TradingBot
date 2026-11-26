# Phase 07 — Checkpoint 166 / W1 B09-05

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `866184b604be85951ceab86ea65b738a04575a36`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB09, lines 140–186; 31 original rows; cumulative B09 93/2276.

[Site evidence](Semantic_Closure_B09_05.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L29). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Ordered RAW aggregation and exact bucket boundaries

- B09-05-F01: The output lists contain supplied non-null tail dictionaries by reference, including the main tail even when lower_only is true. Lower-only bypasses main-key calculation after each lower update. Same-key extrema use previous value first in native min/max; no discontiguous-key merge, time validation or sort. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L140-L186) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L29).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
