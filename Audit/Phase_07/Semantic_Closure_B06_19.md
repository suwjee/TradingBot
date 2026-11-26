# Phase 07 — Checkpoint 91 / W1 B06-19

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `a4e4555e9fe0a0953041c036d354148c527d5ee3`. **Local partition PASS; E44 outer procedure INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E47–E48 (nested in E44), lines 1204–1228; 27 original rows, 3 supplemental items, 2 resolved local clarifications. E cumulative 845/1109.

[Individual evidence](Semantic_Closure_B06_19.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original category IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Generated candidate enqueue, heap scheduling and Order validation

- B06-19-S01: Skip null/known full record; first successful enqueue shallow copies captured input list; append updates candidate list/map, child max and shared source group in fixed order. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1204-L1215).
- B06-19-S02: Do not schedule current or already pending source; no lower-bound frontier test or reheap of already scheduled source. Generated heap key uses new candidate times, not group minima; may schedule earlier source. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1216-L1218).
- B06-19-S03: Order gate order: only-disowned cause first; then gate-owned block; then invalid S cause; short circuit at each failed gate. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1220-L1227).

## Findings

- B06-19-F01: Clarify full record dedup, same-source mutation and no reprioritization/frontier guard. Active E contract line 191 amended; rechecked pinned source.
- B06-19-F02: Make explicit gate evaluation sequence and lack of local rollback. Active E contract line 194 amended; rechecked pinned source.

Remaining E44 body, W2/W3/W4 open. No RAW payload read, Engine execution, benchmark or production change. Permanent RAW protocol remains unchanged.
