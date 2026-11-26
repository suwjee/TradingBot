# Phase 07 — Checkpoint 102 / W1 B07-05

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `81b9ac43ec79fa5032d15d8a99c5010f73793a3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** LC13–LC14, lines 350–360; 9 original rows, 2 supplemental items, 2 resolved local clarifications. Lifecycle cumulative 175/1179.

[Site evidence](Semantic_Closure_B07_05.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_Lifecycle.json), [Lifecycle](../../Algorithms/V3/10_Lifecycle.md), [StopAll](../../Algorithms/V3/11_StopAll.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned source blob `2885dcbd3af108baadde7510ffd7968ad735c57e`; site ID/span/procedure links matched. No full Phase 02 inventory reread claimed.

## Event ordering and detection entry point

- B07-05-S01: Build S list then E list; stable sorting uses raw (source_time,kind,source_index) not exact decision. E before S at equal source time, same-key order retained. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L350-L354).
- B07-05-S02: Allocate output, evaluate events then default checkpoint, run full event detection, then resolve each own stop in emission order into fresh list; no local exception recovery. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L356-L359).

## Findings

- B07-05-F01: Clarify raw index and source-time sorting, not decision-time sorting. [Active contract](../../Algorithms/V3/11_StopAll.md#L55).
- B07-05-F02: Clarify evaluation and post-traversal stop resolution order. [Active contract](../../Algorithms/V3/11_StopAll.md#L58).

W2/W3/W4 open. No RAW payload read, runtime, benchmark, or production change.
