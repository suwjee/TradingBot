# Phase 07 — Checkpoint 107 / W1 B07-10

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `454f48cc40b7d2065675075e39fddfc37f837aec`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** LC23–LC24, lines 550–605; 52 original rows, 3 supplemental items, 3 resolved local clarifications. Lifecycle cumulative 380/1179.

[Site evidence](Semantic_Closure_B07_10.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_Lifecycle.json), [StopAll](../../Algorithms/V3/11_StopAll.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `2885dcbd3af108baadde7510ffd7968ad735c57e`; site IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Live dirty prefix replay and public StopAll wrapper

- B07-10-S01: Inclusive dirty index validation; terminal None; clamp back to earlier prior coverage. New detector and repr keys. Zip to shortest, break on mismatch or max(source,decision)>=dirty; equality invalidates. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L551-L567).
- B07-10-S02: Restore checkpoint and slices; replay suffix. Retained output old hit reused only if non-null and before dirty or dirty absent. Missing hit rescanned from max(decision,dirty); new output resolved from decision. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L568-L581).
- B07-10-S03: Assign checkpoints,keys,unresolved output,result in order, then coverage last lower timestamp+1 microsecond or None, return shallow copy. Wrapper constructs detector then detect. No rollback on exception. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L582-L599).

## Findings

- B07-10-F01: Clarify inclusive index, zip shortest and mismatch short circuit. [Active contract](../../Algorithms/V3/11_StopAll.md#L85).
- B07-10-F02: Clarify output prefix reuse, update order and microsecond coverage not candle end. [Active contract](../../Algorithms/V3/11_StopAll.md#L85).
- B07-10-F03: Clarify supplied arguments and no wrapper recovery. [Active contract](../../Algorithms/V3/11_StopAll.md#L88).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
