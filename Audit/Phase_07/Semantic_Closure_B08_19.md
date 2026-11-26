# Phase 07 — Checkpoint 156 / W1 B08-19

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `5b8fc97ab572038ab288cb9d51bb47b22efa3b16`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P22, lines 583–622; 34 original rows, 3 supplemental items, 3 resolved local clarification groups. Primary cumulative 504/670.

[Site evidence](Semantic_Closure_B08_19.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L129), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact IDs, spans, procedures and operations matched.

## Post-secondary3, cancellation transitions and point publication

- B08-19-S01: Special post-PL3 branch requires exact PL and number>3; precedes normal equal-time race. Replace post-PL3 list with candidate objects in original order, not winner-only or accumulated. Retain all if cancel null, otherwise only stop strictly earlier than cancellation. Exact null cancel returns post-pl3-orders-only, no new PL point. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L583-L593).
- B08-19-S02: Both truthy and equal exact stop times -> ambiguous null proposal. Cancellation truthy and winner null or strictly later -> cancellation wins. Exact PL switches to PH after setting cancellation gate/cursor. Other phase with truthy existing lows requires prior-low penetration check. Read RAW row at upper bound of cursor minus1, normalize Low, require strict below prior low; otherwise seek. Winner exactly null returns waiting status. Status uses lowercase current phase text. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L594-L613).
- B08-19-S03: Find inclusive gate-to-winner-stop main extreme; High only exact PH, otherwise Low. Construct point with phase/number, source/time/price, gate/cursor, winner stop and exact Order reference, cycle id. Reset high flag true iff previous phase exact PL; prospective cursor now winner stop, phase seek. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L614-L622).

## Findings

- B08-19-F01: This branch replaces rather than extends the post-secondary3 list, preserving eligible candidate encounter order. It precedes the normal equal-stop ambiguity test; a candidate equal to cancellation is excluded. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L129).
- B08-19-F02: On cancellation, the phase and gate/cursor changes are local speculative registers. Existing secondary lows require an actual strict penetration of the previous low, not merely the MBL floor. The last RAW timestamp at or before cursor is read directly. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L130).
- B08-19-F03: The winner snapshot is passed directly into the logical point. Only a point-producing return updates the prospective gate, cursor, phase and reset flag; the global scheduler owns commitment. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L131).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
