# Phase 07 — Checkpoint 240 / W1 B09-79

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9867049120fdd0b558150bfb73b642fa4bee4b3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB78–TB79, lines 3079–3134; 21 original rows; cumulative B09 1742/2276.

[Site evidence](Semantic_Closure_B09_79.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L92). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Direct legacy direction serialization

- B09-79-F01: Falsy or absent bridge_output selects direct legacy path. Reaction transformation occurs via serialize's selected native result; output builder includes Blue/A only on exact enabled flags, but S/E/StopAll are passed as already displayed. Blue receives visible bounds again. E audit membership selects serializer, otherwise empty. No additive projection. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3079-L3134) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L92).
- B09-79-F02: Direct legacy Blue receives visible bounds; A is enabled independently, S/E/StopAll are already displayed, and audit is selected by directional E-map membership. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3079-L3134) · [Contract](../../Algorithms/V3/19_Serialization.md#L181).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
