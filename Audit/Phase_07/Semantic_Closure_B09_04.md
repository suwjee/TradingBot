# Phase 07 — Checkpoint 165 / W1 B09-04

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `866184b604be85951ceab86ea65b738a04575a36`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB06–TB08, lines 101–139; 20 original rows; cumulative B09 62/2276.

[Site evidence](Semantic_Closure_B09_04.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L53). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Tehran-local conversion and three timestamp caches

- B09-04-F01: A non-null cache hit returns the same stored object. Conversion strips timezone metadata without converting the Tehran wall clock to UTC. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L101-L139) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L53).
- B09-04-F02: Timezone attachment replaces any existing tzinfo rather than converting the input instant; timestamp conversion uses native int truncation toward zero. Zero is a valid cached result. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L101-L139) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L56).
- B09-04-F03: The datetime branch includes subclasses and bypasses the display cache. The other branch uses its input key as supplied and exact native parse format; no error fallback. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L101-L139) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L59).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
