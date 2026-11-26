# Phase 07 — Checkpoint 93 / W1 B06-21

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `0b5f1b42706bff08a26b3644d4995cfefc345fe6`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E44 heap replay and preliminary eligibility, lines 1294–1327; 35 original rows, 3 supplemental items, 2 resolved local clarifications. E cumulative 946/1109.

[Individual evidence](Semantic_Closure_B06_21.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original category IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Heap replay, reopen and initial Order eligibility

- B06-21-S01: Pop and remove scheduled, snapshot before group processing; steps empty is valid. Group aliases by_source list. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1294-L1299).
- B06-21-S02: Rerace iterates live group (same-source append visible). Disowned then parent eligibility then parent lookup; missing skip. Checkpoint raises before flag; otherwise mark reopened then call E30 with original stop. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1302-L1318).
- B06-21-S03: Filter valid_order first, parent_active second; empty skips source. No local rollback of earlier rerace effects. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1319-L1324).

## Findings

- B06-21-F01: Clarify live group iteration and precise checkpoint/parent ordering. Active E contract line 176 amended; rechecked pinned source.
- B06-21-F02: Clarify snapshot and scheduled.remove, preliminary filter order. Active E contract line 175 amended; rechecked pinned source.

W2/W3/W4 open. No RAW payload read, Engine execution, benchmark or production change. Permanent RAW protocol remains unchanged.
