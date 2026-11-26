# Phase 07 — Checkpoint 89 / W1 B06-17

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `d85e99fd7f813c0729740fadefc6b34773beed8b`. **Local review PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E42–E43, lines 1031–1131; 67 original rows, 5 supplemental items, 3 resolved local clarifications. E cumulative 767/1109.

[Individual evidence](Semantic_Closure_B06_17.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original category IDs, spans and procedure links matched. No full Phase 02 inventory reread claimed.

## Two-pass provisional discovery, root-chain pruning and reconciliation dispatch

- B06-17-S01: All S strict stops queried in detector order. Invoke registration before any chain discovery, then retain stopped parent even if owner registration declines. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1043-L1049).
- B06-17-S02: Inherited registration rejects S identity in invalid/accepted E set or intervening reset. Return None does not mean caller may discard stopped parent. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L1339-L1349).
- B06-17-S03: Each stopped S gets independent chain, own seen source indices and owned times. Append chain/global candidate, mark source, switch parent before next E stop, increment only when stopped. No direct E41 or reset gate in E42 loop. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1051-L1084).
- B06-17-S04: Early returns retain original candidate list; only exact E-parent continuation families at same physical root identity count. Any differing family blocks entire invalid root chain. Flatten unblocked chains in input order; no ledger rollback here. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1086-L1122).
- B06-17-S05: Live continuation dispatch returns live list directly; nonlive returns only numbered component of native compute; no local fallback. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1124-L1130).

## Findings

- B06-17-F01: Distinguish owner registration rejection from stopped-parent collection and preserve exact append/parent switch order. Active E contract line 167 amended; rechecked pinned source.
- B06-17-F02: Clarify any differing family (not assumed mirror), whole-chain pruning and lack of local provenance rollback. Active E contract line 167 amended; rechecked pinned source.
- B06-17-F03: Clarify non-null dispatch, native first component and no alternate path. Active E contract line 170 amended; rechecked pinned source.

W2/W3/W4 open. No RAW payload read, Engine execution, benchmark or production change. Permanent RAW verification policy remains unchanged.
