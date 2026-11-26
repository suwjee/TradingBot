# Phase 07 — Checkpoint 127 / W1 B07-30

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `0910f7afc39a1c79f07a28eb07b5a797215b958c`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** LC38 dominant final acceptance, lines 1324–1376; 36 original rows, 2 supplemental items, 1 resolved local clarification groups. Lifecycle cumulative 1018/1179.

[Site evidence](Semantic_Closure_B07_30.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_Lifecycle.json), [Lifecycle](../../Algorithms/V3/10_Lifecycle.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `2885dcbd3af108baadde7510ffd7968ad735c57e`; site IDs, spans and procedure links matched. No full Phase 02 inventory reread claimed.

## Exact stop dominance, S priority override and consumption

- B07-30-S01: Dominant uses exact stop before priority, number, source,index; higher-priority S/S by attribute presence bypasses price. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L1328-L1350).
- B07-30-S02: No strict price crossing retains candidate; otherwise consume rank<=dominant. Cached stop read retained in loop although result unused; no extra gate. Fallback append. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L1354-L1375).

## Findings

- B07-30-F01: Clarify exact stop key vs stop-main index, marker gates and unused cached read. [Active contract](../../Algorithms/V3/10_Lifecycle.md#L102).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
