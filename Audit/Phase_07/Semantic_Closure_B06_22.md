# Phase 07 — Checkpoint 94 / W1 B06-22

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `0b5f1b42706bff08a26b3644d4995cfefc345fe6`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E44 ownership filters, E51, lines 1328–1371; 45 original rows, 3 supplemental items, 2 resolved local clarifications. E cumulative 991/1109.

[Individual evidence](Semantic_Closure_B06_22.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original category IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Active-owner suppression and ownership priority

- B06-22-S01: Suppress S if any active owner meets strict stop, red-owner or blue-candidate, existing max child decision >= candidate decision. Child lookup happens only after previous gates. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1328-L1345).
- B06-22-S02: Prefer excluding E-blue when any still-unaccepted red S has strictly later source than parent and strictly earlier decision than parent stop. If preferred subset empty retain original. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1346-L1364).
- B06-22-S03: Priority owner lookup is first active record by source time only for E parent, uses truthy parent; injected sequence_priority determines rank. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1365-L1370).

## Findings

- B06-22-F01: Specify ordered short circuit and child decision assignment. Active E contract line 177 amended; rechecked pinned source.
- B06-22-F02: Emphasize time-only owner lookup and truthiness distinct from later owner gate. Active E contract line 203 amended; rechecked pinned source.

W2/W3/W4 open. No RAW payload read, Engine execution, benchmark or production change. Permanent RAW protocol remains unchanged.
