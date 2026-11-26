# Phase 07 — Checkpoint 90 / W1 B06-18

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `a4e4555e9fe0a0953041c036d354148c527d5ee3`. **Local partition PASS; E44 outer procedure INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E44 initialization (partial outer procedure), E45–E46, lines 1132–1203; 51 original rows, 3 supplemental items, 3 resolved local clarifications. E cumulative 818/1109.

[Individual evidence](Semantic_Closure_B06_18.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original category IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Reconciliation setup, replay prefix and source indexes

- B06-18-S01: Group all candidates by raw index; frontier gates initial heap only. Two group minima are independent, possibly different records. Known uses full record identity/equality, scheduled only initial heap keys. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1140-L1155).
- B06-18-S02: Checkpoint presence alone controls replay restore; previous required by dereference, count sliced without local validation; active copied independently. Detector accepted set aliases local accepted_sources. Candidate map last wins, S map first wins with integer index. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1156-L1173).
- B06-18-S03: Numbered indexes preserve first record per pair and time; sorted unique times, S-parent times. Child index includes all candidates and stores maximum exact decision per E-parent physical pair, not only accepted candidates. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1175-L1202).

## Findings

- B06-18-F01: Clarify frontier-only heap filtering, independent group minima, checkpoint preconditions and accepted-set alias. Active E contract line 173 amended; rechecked pinned source.
- B06-18-F02: Clarify first-wins pair/time and unique time insertion. Active E contract line 185 amended; rechecked pinned source.
- B06-18-F03: Clarify all-candidate child maximum including before frontier. Active E contract line 188 amended; rechecked pinned source.

Remaining E44 body, W2/W3/W4 open. No RAW payload read, Engine execution, benchmark or production change. Permanent RAW protocol remains unchanged.
