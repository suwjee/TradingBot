# Phase 07 — Checkpoint 95 / W1 B06-23

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `0b5f1b42706bff08a26b3644d4995cfefc345fe6`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E44 winner, family, number and reset, lines 1372–1456; 59 original rows, 3 supplemental items, 2 resolved local clarifications. E cumulative 1050/1109.

[Individual evidence](Semantic_Closure_B06_23.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original category IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Winner selection, family/number and active-state commit

- B06-23-S01: Min key negative priority, exact decision, exact parent stop, stable first tie. Scan stopped owners before hard parent gate; literal red/blue dictionary. If selected winner fails hard gate skip whole source, no runner-up. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1380-L1404).
- B06-23-S02: Owner by time only for E, non-null test; numbering branch order red parent, stopped red, blue parent, stopped blue, fallback. Parent color branch without stopped same family yields 1. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1406-L1435).
- B06-23-S03: Remove all stopped physical identities then replace family/number, append/index/add sets. Reset membership of original source time clears active and sets boundary; numbered history retained. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1436-L1453).

## Findings

- B06-23-F01: Correct operation order and explicitly prohibit runner-up fallback. Active E contract line 179 amended; rechecked pinned source.
- B06-23-F02: Clarify time-only owner, non-null gate and exact commit order. Active E contract line 180 amended; rechecked pinned source.

W2/W3/W4 open. No RAW payload read, Engine execution, benchmark or production change. Permanent RAW protocol remains unchanged.
