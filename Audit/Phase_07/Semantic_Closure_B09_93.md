# Phase 07 — Checkpoint 254 / W1 B09-93

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `fc39d697b5807ac621dddb80138f4f8ff3b013c7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB91, lines 3571–3593; 26 original category rows; cumulative B09 2154/2276.

[Site evidence](Semantic_Closure_B09_93.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L107). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Boundary-inclusive fresh regime, live cleanup and continuation

Append stopped published prefix first. Read target and serialize incoming transition in old current context before replacing it with market_segment(boundary,len(current.candles)); boundary candle belongs to new regime. Initial bullish and bearish flags are independent exact target comparisons, not complementary defaults. Set current direction to target. Try covers optional live.active_regime and calculate; finally native release has priority, otherwise live fallback. Then read optional next transition from new primary result. If None or index strictly greater than current visible end, publish active regime with first candle timestamp and offset, append and break; equality repeats. Merge all accumulated regimes in encounter order. No runtime proof of delegated live or segment behavior. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3571-L3593).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
