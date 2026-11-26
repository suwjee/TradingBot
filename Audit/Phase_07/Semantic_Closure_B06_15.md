# Phase 07 — Checkpoint 87 / W1 B06-15

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `d85e99fd7f813c0729740fadefc6b34773beed8b`. **Local review PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E40, lines 915–1006; 75 original rows, 4 supplemental items, 2 resolved local clarifications. E cumulative 678/1109.

[Individual evidence](Semantic_Closure_B06_15.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original category IDs, spans and procedure links matched. No full Phase 02 inventory reread claimed.

## Independent S root restoration and heap ownership

- B06-15-S01: Initial dominant and accepted S identities normalize index; candidate parent key is raw. Four filters short-circuit in written order; no new S stop search. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L933-L949).
- B06-15-S02: Heap keys time, raw source index, unique ordinal; full-record known set. E rerace uses original stop and current dominant time set; missing S parent propagates next() failure. Rerace branch always continues, even if no replacement. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L950-L978).
- B06-15-S03: Replace earliest existing same-S-parent object unconditionally, not by comparing new root decision. Remove all references identical to winner, retain equal but distinct objects. Otherwise five-field duplicate gate. Dominant sources only grows; add raw root pair even when not appended. Final E38 conflicts and accepted set. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L979-L1005).
- B06-15-S04: Owner disowned-only guard checked directly; missing/empty causes, initial ledger or Order_B cause makes predicate false. Full cross-owner proof remains W2. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L2020-L2033).

## Findings

- B06-15-F01: Clarify initial normalized vs raw evolving identities, rerace always continues and full-record membership. Active E contract line 161 amended; rechecked pinned source.
- B06-15-F02: Explicitly rule out a new-versus-existing decision comparison; document object-identity removal and monotone dominant set. Active E contract line 161 amended; rechecked pinned source.

W2/W3/W4 open. No RAW payload read, Engine execution, benchmark or production change. Permanent RAW verification policy remains unchanged.
