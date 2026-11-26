# Phase 07 — Checkpoint 101 / W1 B07-04

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `81b9ac43ec79fa5032d15d8a99c5010f73793a3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** LC12, lines 262–349; 39 original rows, 3 supplemental items, 1 resolved local clarifications. Lifecycle cumulative 166/1179.

[Site evidence](Semantic_Closure_B07_04.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_Lifecycle.json), [Lifecycle](../../Algorithms/V3/10_Lifecycle.md), [StopAll](../../Algorithms/V3/11_StopAll.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned source blob `2885dcbd3af108baadde7510ffd7968ad735c57e`; site ID/span/procedure links matched. No full Phase 02 inventory reread claimed.

## S-donor StopAll construction and Order provenance

- B07-04-S01: StopAll number1, fixed opposite-s-group-stop label, supplied gate/owner. Underlying E tuple independently indexed only when non-None; no length check or conversion. Order direction/mode nullable unchanged; causes empty; parent cause sourced from A-stop event. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L272-L300).
- B07-04-S02: Optional Order fields via getattr None default; index/number int and box/stop prices Decimal only when non-None; timestamps unchanged. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L301-L338).
- B07-04-S03: Own stops all None; S donor metadata separately reads source index/time, raw string color and normalized price, donor number None, donor-stop defaults None. No stop computation or owner validation in constructor. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L339-L348).

## Findings

- B07-04-F01: Clarify exact S optional fields, raw underlying tuple and no selection in constructor. [Active contract](../../Algorithms/V3/11_StopAll.md#L52).

W2/W3/W4 open. No RAW payload read, runtime, benchmark, or production change.
