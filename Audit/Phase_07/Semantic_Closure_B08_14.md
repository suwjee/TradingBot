# Phase 07 — Checkpoint 151 / W1 B08-14

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `a50bf552cc758c65791cd31db2d03386f00bc38b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P16 lines 386–420; 34 original rows, 3 supplemental items, one resolved local clarification. Primary cumulative 322/670.

[Site evidence](Semantic_Closure_B08_14.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L98), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact category IDs, spans and procedures matched.

## Global point commitment, native Order invalidation and aggregate publication

- B08-14-S01: Stop if no selected decision after activation arbitration. Pop selected cycle proposal; take prospective checkpoint and point. Select cycle highs for exact PH, otherwise lows. Append selected point to committed cycle list. Append same point to aggregate highs for exact PH, otherwise lows. Only non-null run records commitment. Record exact decision event, activation count, cycle index, checkpoint and point. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L386-L397).
- B08-14-S02: Only exact PH promotes identity and recomputes reversal. Add raw physical index/time pair to promoted set. Only non-null callback causes native confirmation and clearing pending. Invoke callback before invalidation; exception propagates before clear. Clear all pending including null-point proposals after callback returns. Recompute reversal after PH even without callback. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L398-L403).
- B08-14-S03: Use pending prospective result if index exists, else committed result. Traverse checkpoints in stable index order. Select last cycle status with negative-one index; not price arithmetic. Override status only for non-null transition. Traverse published cycles including pending prospective results. Traverse each cycle post-PL3 Orders in order. First physical Order per direction/First/Break wins, preserving object. Sort physical Orders by exact stop, descending First, ascending Break. Negate First for descending tie order; no price conversion. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L405-L418).

## Finding

- B08-14-F01: Remove pending and append same point to committed and aggregate arrays before optional run-step recording. PH callback must return before pending clear; absent callback means no invalidation, but reversal is still recomputed. Final pending prospective cycle results including null-point states can contribute status and post-PL3 Orders. First and last cycle are indexed directly without empty-cycle fallback; first physical duplicate wins before stable sort. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L98).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
