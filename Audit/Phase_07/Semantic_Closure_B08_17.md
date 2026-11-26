# Phase 07 — Checkpoint 154 / W1 B08-17

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `5b8fc97ab572038ab288cb9d51bb47b22efa3b16`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P22, lines 518–553; 40 original rows, 3 supplemental items, 2 resolved local clarification groups. Primary cumulative 429/670.

[Site evidence](Semantic_Closure_B08_17.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L123), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact IDs, spans, procedures and operations matched.

## Prospective state copy, numbering and exact seek race

- B08-17-S01: Shallow-copy result with fresh highs list; retain original point references. Fresh lows list retaining original points. Fresh post-PL3 Order list; no mutation of committed list. Replace checkpoint with prospective result; phase and cursor initially unchanged. Unbounded prospective loop; explicit return or later-event progression. Last high price if list truthy, else reference; negative-one list index not price arithmetic. Last low price if list truthy, else MBL floor. PH number 1 when reset flag true or no highs (short circuit); otherwise last number+1. PL number last+1 if lows exist, else1. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L518-L538).
- B08-17-S02: Only exact seek phase enters dual crossing race. Query strict above current high after cursor. Query strict below current low after same cursor. Both hits exactly null -> waiting-for-structure-break; null proposal. Both truthy and exact hit times equal -> ambiguous; do not choose by price or index. Choose PH if up truthy and down null or strictly later; otherwise PL; short circuit. Select corresponding crossing tuple as gate index and cursor. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L539-L550).
- B08-17-S03: If cutoff non-null and cursor >= cutoff, wait for trend reversal; no point. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L551-L553).

## Findings

- B08-17-F01: Only the three named lists are copied; their contents and other result fields retain shallow identity. Prospective checkpoint registers are not updated by these local calculations until a point is actually proposed. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L123).
- B08-17-F02: Both absent means exact null tests; same-event ambiguity requires both hits truthy. PH selection uses a truthy upward hit and either null downward hit or strictly earlier upward time; the gate tuple is chosen after setting the phase. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L125).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
