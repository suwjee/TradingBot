# Phase 07 — Checkpoint 243 / W1 B09-82

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `2dda09909aae83e73299ac587d313f7a24f5d7e9`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB84/TB85/TB86, lines 3249–3289; 45 original category rows; cumulative B09 1844/2276.

[Site evidence](Semantic_Closure_B09_82.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L195). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Primary direction resolution, cycle and physical point identity

Direction defaults only for absent attribute; exact bullish resolves lows, all other values resolve highs through the requested end. Falsy cycles fall back to a singleton primary, and the first cycle id is read from its first item. Cycle identity transformation is short-circuited by truthy id then truthy offset, then exact four-part length and literal cycle token; integer conversion errors propagate. Point relabeling uses finalized primary points, while identity origin uses truthy identity_source or the item itself; origin trigger/decision offsets affect the id, not local row indexes. Origin cycle suffix is present only for non-null origin cycle differing from first cycle; row cycleId independently follows the actual item's non-null cycle. Exact PH yields bearish conceptual Order owner, otherwise bullish. Main trigger and decision stamps directly index market candles, whereas exact event times and source time use the native supplied values. No price rounding or local repair. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3249-L3289) · [Primary owner](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L128-L195).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
