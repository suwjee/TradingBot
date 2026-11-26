# Phase 07 — Checkpoint 196 / W1 B09-35

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB60, lines 1505–1539; 12 original rows; cumulative B09 910/2276.

[Site evidence](Semantic_Closure_B09_35.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L164). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Bridge output detector selection and full Blue ordinals

- B09-35-F01: A non-null E detector supplies its physical order_direction as a string; absent detector uses exact bullish-to-bearish/otherwise-bullish fallback. Full Blue uses dictionary get fallback only for missing key, not a falsy stored list. The full line iterable is materialized before stable ordinal mapping. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1505-L1539) · [Contract](../../Algorithms/V3/19_Serialization.md#L164).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
