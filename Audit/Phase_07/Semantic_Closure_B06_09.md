# Phase 07 — Checkpoint 81 / W1 B06-09

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `8ae2c90b2b4b92be2c74dd7abacd176b4845923f`. **Local review PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E18–E27, lines 507–580; 47 original rows, 4 supplemental items, 2 resolved local clarifications. E cumulative 399/1109.

[Individual evidence](Semantic_Closure_B06_09.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [chronology](../../Algorithms/V3/Chronology/03_Order_E.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Parent and Order exact stop, live cache, confirmation delegation

- B06-09-S01: Parent and Order choose distinct less predicates; lower timestamp returned from lower_times. Start inclusive and end exclusive through bisect_left; no row timestamp access. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L510-L535). Conditional boundary: W2 chronology/index contracts.
- B06-09-S02: Nonlive delegates mixin; live raw (start,level) key preserves cached None, validates chronology on hit, clamps only search start on miss, maps main time from times[index]. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L540-L557). Conditional boundary: W2 equivalence of times[index] and candle.timestamp.
- B06-09-S03: Inherited mixin nonlive path also caches None by membership but returns main timestamp from candle.timestamp; direct source read of pinned Order Audit owner. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L1459-L1476). Conditional boundary: Owner path engine/pipeline/order_audit_engine.py.
- B06-09-S04: Confirmation delegation supplies two positional arguments only, First maps int(first_idx), exact decision time and normalized parent price used for S/E stop; parent_type ignored locally. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L559-L578). Conditional boundary: W2 chronology defaults, time/index coherence.

## Findings

- B06-09-F01: Distinguish raw cache key from clamped search start, and live main time from inherited candle timestamp. Active E contract line 107 amended; rechecked pinned source.
- B06-09-F02: Specify exact delegation; default intrabar behavior belongs to chronology owner, not E. Active E contract line 110 amended; rechecked pinned source.

W2/W3/W4 open. No RAW read, Engine execution, benchmark, or production change.
