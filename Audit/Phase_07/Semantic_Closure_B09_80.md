# Phase 07 — Checkpoint 241 / W1 B09-80

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9867049120fdd0b558150bfb73b642fa4bee4b3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB78/TB80/TB81, lines 3135–3219; 29 original rows; cumulative B09 1771/2276.

[Site evidence](Semantic_Closure_B09_80.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L92). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Single selection and additive bridge serialization

- B09-80-F01: Bridge mode calls selection once and reuses exact pairs/reset objects. Blue is filtered once by visible index, then serializer called without explicit bounds; A flag exact enabled, S/E/StopAll retained from visibility. Audit stable sorted via TB59 only for non-null detector. Legacy and additive outputs use same selections; legacy audit serializer may sort again by its own key. No fresh trading decision. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3135-L3219) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L92).
- B09-80-F02: The native/public selection is constructed once and passed as selected_items to TB24, preventing reselection and reapplication of transform. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3135-L3219) · [Contract](../../Algorithms/V3/19_Serialization.md#L184).
- B09-80-F03: Additive output receives the exact selections used by legacy serialization, with selected Blue already range-filtered and audit sorted by native main First/Break key. No separate trading calculation. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3135-L3219) · [Contract](../../Algorithms/V3/19_Serialization.md#L187).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
