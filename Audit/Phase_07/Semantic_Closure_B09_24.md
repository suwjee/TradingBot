# Phase 07 — Checkpoint 185 / W1 B09-24

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9658be2dda143e889bb770fa9c249866bb8dadb7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB44, lines 927–986; 36 original rows; cumulative B09 588/2276.

[Site evidence](Semantic_Closure_B09_24.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L116). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Final Order Audit projection, cause mapping and invalid records

- B09-24-F01: Invalid physical formatter result raises RuntimeError before cause mapping. Parent-stop accesses required cause keys; reset-leg maps each value and only datetime instances are formatted, other values unchanged. Unknown kinds are omitted. Missing box-source timestamps use null, whereas missing box prices are passed to native string conversion (not emitted as JSON null). The cause event time is formatted as recorded; stop proof is taken from the physical projection. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L927-L986) · [Contract](../../Algorithms/V3/19_Serialization.md#L116).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
