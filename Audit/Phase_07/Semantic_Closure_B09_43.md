# Phase 07 — Checkpoint 204 / W1 B09-43

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB63, lines 1755–1777; 39 original rows; cumulative B09 1087/2276.

[Site evidence](Semantic_Closure_B09_43.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L70). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Independent market segment and half-open RAW slicing

- B09-43-F01: Require valid nonempty main interval before indexing. The lower interval is bisect-left at both ends, excluding the boundary even when multiple equal-time rows exist. New local records and chronology use original dynamic type and integer total seconds. Visible bounds may express no overlap; this helper does not enforce visible nonemptiness. Explicit non-null trend overrides are retained independently, otherwise original flags only at start zero. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1755-L1777) · [Contract](../../Algorithms/V3/21_RAW_Aggregation_Contract.md#L70).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
