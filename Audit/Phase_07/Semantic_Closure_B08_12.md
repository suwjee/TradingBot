# Phase 07 — Checkpoint 149 / W1 B08-12

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `a50bf552cc758c65791cd31db2d03386f00bc38b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P16 lines 326–349; 27 original rows, 2 supplemental items, one resolved local clarification. Primary cumulative 242/670.

[Site evidence](Semantic_Closure_B08_12.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L93), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact category IDs, spans and procedures matched.

## Retained Primary steps, ownership replay and MBL refresh

- B08-12-S01: Allocate empty physical promoted-source set. Read confirm_high attribute once with null fallback; no callable validation. Replay only when run exists. Traverse retained steps in returned order. Null cycle index skips checkpoint/point work after restoring activation count. Equality with checkpoint count appends, otherwise replaces by index. Append retained checkpoint at next sequential index. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L326-L340).
- B08-12-S02: Null point skips publication and callback; restored checkpoint remains. Route exact PH to highs, all other kinds to lows; append original point. Only exact PH participates in primary ownership. Record raw physical source index/time pair. Callback gate is non-null rather than truthiness. Replay primary confirmation to native Order owner. Refresh MBL for every restored checkpoint in list order after callbacks. Compute first bullish reversal only if aggregate highs is truthy. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L341-L349).

## Finding

- B08-12-F01: Read optional confirm_high once; the gate is non-null, not callable validation. Every retained step restores the activation count before its null-cycle skip. A null point retains the restored checkpoint but emits no point or callback. MBL refresh follows all retained primary callbacks; reversal is computed only for a nonempty aggregate high list. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L93).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
