# Phase 07 — Checkpoint 83 / W1 B06-11

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `1f2a5f2c214be636e88a554baf72f11be227c4ef`. **Local review PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E30–E31, lines 608–676; 50 original rows, 6 supplemental items, 3 resolved local clarifications. E cumulative 474/1109.

[Individual evidence](Semantic_Closure_B06_11.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [chronology](../../Algorithms/V3/Chronology/03_Order_E.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original category IDs, spans and procedure links matched. No full Phase 02 inventory reread claimed.

## Global Order race, route ordering and prospective E source

- B06-11-S01: S-only inherited lookup, unused gate query, carried query, registration, post-stop iterable acquisition and direct query occur in that order. No local rollback if later candidate is rejected. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L615-L625).
- B06-11-S02: Deadline checks truthiness of entire carried collection, not crossed count. S with no carried uses earliest non-null inherited cross or range_end; flags are independent exact parent-type tests. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L626-L638).
- B06-11-S03: Direct, inherited and carried are each sorted eagerly (crossed only); accepted generator groups consecutive equal stop times lazily. Merge tie priority is direct, inherited, carried, accepted; stable within route. Upstream stream already ordered by stop is an owner dependency. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L642-L655).
- B06-11-S04: Explicit empty owned set retained by reference; compute prospective source before disowned-S predicate. Stop at first surviving physical match; E06/E32 receives same source. No local rollback on exhaustion. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L656-L675).
- B06-11-S05: Order owner disowned-S predicate: missing entry, empty causes, truthy Order_B causes or initial-audit identity returns false; otherwise every cause must be parent-stop/S, length>4, with cause time in owned times or equal prospective time. This is direct owner evidence, not W2 closure. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L2020-L2033).
- B06-11-S06: Accepted owner key is exact stop, confirmation, negative First; E reorders equal-stop groups by First. Owner may return a lazy iterator or fallback; cross-owner stream validity remains W2. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L1879-L1888).

## Findings

- B06-11-F01: Clarify eager owner call order, carried truthiness and retained side effects. Active E contract line 131 amended; rechecked pinned source.
- B06-11-F02: Specify consecutive-group requirement, three eagerly sorted routes and stable merge precedence. Active E contract line 134 amended; rechecked pinned source.
- B06-11-F03: Preserve explicitly empty owned set by reference and no local rollback. Active E contract line 131 amended; rechecked pinned source.

W2/W3/W4 open. No RAW payload read, Engine execution, benchmark or production change. Permanent RAW verification policy remains unchanged.
