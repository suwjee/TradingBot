# Phase 07 — Checkpoint 80 / W1 B06-08

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `8ae2c90b2b4b92be2c74dd7abacd176b4845923f`. **Local review PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E16–E17, lines 458–506; 51 original rows, 2 supplemental items, 1 resolved local clarifications. E cumulative 352/1109.

[Individual evidence](Semantic_Closure_B06_08.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [chronology](../../Algorithms/V3/Chronology/03_Order_E.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Sparse table construction, inclusive query and earliest ties

- B06-08-S01: Level zero retains positions; each subsequent level combines two previous half-span positions. Exact power-of-two widths included. If neither strict directional comparison wins, smaller position selected; no separate equality test. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L461-L485). Conditional boundary: Decimal comparison errors propagate.
- B06-08-S02: Nonpositive interval returns left before table lookup; positive queries use overlapping left/right power-of-two blocks, strict left then strict right then smaller index. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L489-L504). Conditional boundary: No local validation of endpoints; W2 callers ensure valid bounds.

## Findings

- B06-08-F01: Clarify neither strict comparison wins, rather than adding an equality test; nonpositive range returns left before table read. Active E contract line 92 amended; rechecked pinned source.

W2/W3/W4 open. No RAW read, Engine execution, benchmark, or production change.
