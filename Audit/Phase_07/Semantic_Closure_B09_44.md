# Phase 07 — Checkpoint 205 / W1 B09-44

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB64, lines 1778–1791; 29 original rows; cumulative B09 1116/2276.

[Site evidence](Semantic_Closure_B09_44.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L175). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Absolute payload index projection and recursive identity fields

- B09-44-F01: Scalar offset requires exact int type (excluding bool and subclasses), nonnegative and key index or suffix Index. Identity sequences under the two exact names become lists and offset eligible parts only; other parts are retained without recursion inside that special route. Ordinary tuples outside the special route are returned unchanged. Dict and list instances are copied recursively. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1778-L1791) · [Contract](../../Algorithms/V3/19_Serialization.md#L175).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
