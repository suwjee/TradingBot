# Phase 07 — Checkpoint 105 / W1 B07-08

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `454f48cc40b7d2065675075e39fddfc37f837aec`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** LC19, LC15 dispatch, lines 475–524; 49 original rows, 3 supplemental items, 3 resolved local clarifications. Lifecycle cumulative 316/1179.

[Site evidence](Semantic_Closure_B07_08.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_Lifecycle.json), [StopAll](../../Algorithms/V3/11_StopAll.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `2885dcbd3af108baadde7510ffd7968ad735c57e`; site IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Repeated StopAll, E promotion and checkpoint capture

- B07-08-S01: Query every active StopAll from own decision and raw price. Stop<=E decision inclusive. Max number and min exact event independent; count entries; remove by object id, emit then extend active, clear owner/pending. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L475-L496).
- B07-08-S02: No stopped active: fresh armed search even if pending, truthy pending prevails; completed emits number1 and appends active (not singleton). Ordinary E accept normalizes family and int number. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L498-L515).
- B07-08-S03: Exact S tag otherwise E; process supplied event order, capture optional post-event checkpoint with output length; no local catch, no stop resolve. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L517-L523).

## Findings

- B07-08-F01: Specify object identity removal, independent extrema and mutation order. [Active contract](../../Algorithms/V3/11_StopAll.md#L73).
- B07-08-F02: Clarify eager gate search, active append and fallback. [Active contract](../../Algorithms/V3/11_StopAll.md#L73).
- B07-08-F03: Clarify dispatch and snapshot timing. [Active contract](../../Algorithms/V3/11_StopAll.md#L61).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
