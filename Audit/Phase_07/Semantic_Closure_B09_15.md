# Phase 07 — Checkpoint 176 / W1 B09-15

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `866184b604be85951ceab86ea65b738a04575a36`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB28–TB29, lines 551–661; 63 original rows; cumulative B09 366/2276.

[Site evidence](Semantic_Closure_B09_15.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L68). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## E Zone and StopAll output field and null semantics

- B09-15-F01: Order causes are materialized as a list without a null fallback; only parent-stop cause time is optional in the E geometry mapping. All rows emitted in input order, without calculationValid. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L551-L661) · [Contract](../../Algorithms/V3/19_Serialization.md#L68).
- B09-15-F02: Order causes are unconditionally converted to list; order geometry/time guards are exact non-null. Final stopTime and stopEventTime alone use truthiness, unlike the optional Order fields. No independent filtering, donor fields or calculationValid flag. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L551-L661) · [Contract](../../Algorithms/V3/19_Serialization.md#L71).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
