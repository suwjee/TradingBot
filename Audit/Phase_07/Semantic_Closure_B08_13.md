# Phase 07 — Checkpoint 150 / W1 B08-13

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `a50bf552cc758c65791cd31db2d03386f00bc38b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P16 lines 350–385; 46 original rows, 3 supplemental items, one resolved local clarification. Primary cumulative 288/670.

[Site evidence](Semantic_Closure_B08_13.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L95), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact category IDs, spans and procedures matched.

## Global reversal and activation race, pending proposal ownership

- B08-13-S01: Unbounded scheduler loop, exits via explicit branches. Enumerate checkpoints in stable cycle-index order. Compute only missing pending entries; null-point entries occupy map. Request prospective point with selected crossing and reversal bound. Pass event if transition truthy else null; arbitration separately tests non-null. Retain only non-null points in decision list. Minimum (decision event,cycle index), null if no decision. Next activation only if index strictly below schedule length. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L350-L359).
- B08-13-S02: Reversal requires non-null transition; conjunction short-circuits. Absent decision unbounded; otherwise reversal <= earliest decision. Absent activation unbounded; otherwise reversal <= next activation. Activation considered only when index in bounds; tie favors activation. Absent decision bypasses comparison; otherwise activation <= earliest decision. Increment count on consuming activation before promoted ownership check. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L360-L372).
- B08-13-S03: Match integer reference index and exact time against promoted physical sources. Only run records skipped activation. Record skipped activation time/count without cycle/point. Create independent cycle only for unpromoted reference using selected cross. Only run records activated cycle. Record step before committed checkpoint append. Use current checkpoint length as new cycle index. Append activated checkpoint; restart before committing point. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L373-L385).

## Finding

- B08-13-F01: The prospective cutoff uses transition truthiness, while reversal arbitration requires non-null transition. Pending membership, not point existence, suppresses recomputation. Consume activation index before checking promoted ownership; skipped activation is a live step with null cycle/point. New-cycle step records current list length before append. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L95).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
