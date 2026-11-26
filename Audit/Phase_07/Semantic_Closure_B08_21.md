# Phase 07 — Checkpoint 158 / W1 B08-21

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `5b8fc97ab572038ab288cb9d51bb47b22efa3b16`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P26–P36, lines 683–742; 25 original rows, 3 supplemental items, 3 resolved local clarification groups. Primary cumulative 583/670.

[Site evidence](Semantic_Closure_B08_21.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L148), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact IDs, spans, procedures and operations matched.

## Exact Decimal reflection and immutable chronology adapters

- B08-21-S01: Normalize via as_decimal then copy_negate without arithmetic context rounding; sign flips even for signed zero. Frozen slotted wrapper retains original row reference. Reflected High is sign-copy of original Low, read lazily. Reflected Low is sign-copy of original High, read lazily. Snapshot row references into tuple; no deep copy. Return tuple length. Native tuple indexing then new reflected row wrapper, no explicit slice guard. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L683-L713).
- B08-21-S02: Reflected first_greater delegates original first_less with same bounds and sign-copied level. Reflected first_less delegates original first_greater with same bounds and sign-copied level. Wrap main candles in reflected row sequence. Wrap lower rows independently; original timestamps remain unchanged. Wrap original lower price index, reuse original main-index callable. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L714-L734).
- B08-21-S03: Shallow replace order, preserve untouched fields. Exact bullish direction becomes bearish, any other direction becomes bullish. Sign-copy normalized stop level. Reflected top from original bottom only if bottom non-null. Reflected bottom from original top only if top non-null. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L735-L742).

## Findings

- B08-21-F01: Reflection uses the Decimal sign-copy operation after normalization, preserving coefficient and exponent and reversing signed zero without context rounding. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L148).
- B08-21-F02: Row tuple snapshots contain original row references; the reflected index delegates to original strict opposite queries, and the original main-index callable remains bound to native chronology. No timestamps are transformed. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L184).
- B08-21-F03: Null tests are per opposite box field and do not use truthiness; zero is reflected. The replacement retains the exact audit-cause tuple and unchanged physical source indexes and event times. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L188).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
