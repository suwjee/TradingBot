# Phase 07 — Checkpoint 209 / W1 B09-48

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB68, lines 1930–1947; 6 original rows; cumulative B09 1195/2276.

[Site evidence](Semantic_Closure_B09_48.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L73). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Full RAW file read, BOM removal and exact JSON parsing

- B09-48-F01: Read complete bytes, remove one leading UTF-8 BOM prefix only, and use native JSON parser with Decimal for floating lexemes; integer parsing remains native default. No pre-filter of requested timestamps or numeric conversion through binary float. Parse and file failures propagate. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1930-L1947) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L73).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
