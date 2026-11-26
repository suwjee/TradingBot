# Phase 07 — Checkpoint 98 / W1 B07-01

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `81b9ac43ec79fa5032d15d8a99c5010f73793a3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** LC01–LC04 and declarations, lines 1–120; 50 original rows, 3 supplemental items, 2 resolved local clarifications. Lifecycle cumulative 50/1179.

[Site evidence](Semantic_Closure_B07_01.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_Lifecycle.json), [Lifecycle](../../Algorithms/V3/10_Lifecycle.md), [StopAll](../../Algorithms/V3/11_StopAll.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned source blob `2885dcbd3af108baadde7510ffd7968ad735c57e`; site ID/span/procedure links matched. No full Phase 02 inventory reread claimed.

## Shared sequence priority and immutable StopAll/owner records

- B07-01-S01: Version strings are metadata. Exact table S blue1/E blue2/S red3/E red4. Convert kind then family via str/lower; no trimming or default. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L24-L39).
- B07-01-S02: StopAll record separates own source/decision, supplied gate and stopped group, underlying E/Order, own stop and eight keyword-only nullable donor fields. Record frozen/slotted, no constructor selection performed by declaration. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L42-L94).
- B07-01-S03: Dominant owner stores exact kind/family/number, count and latest reference. Priority property recomputes normalized table lookup, armed count>=2 inclusive; key uses exact E kind else S label. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L95-L118).

## Findings

- B07-01-F01: Specify normalization order and absence of fallback. [Active contract](../../Algorithms/V3/10_Lifecycle.md#L45).
- B07-01-F02: Clarify shallow immutable record and exact key metadata versus lookup normalization. [Active contract](../../Algorithms/V3/10_Lifecycle.md#L48).

W2/W3/W4 open. No RAW payload read, runtime, benchmark, or production change.
