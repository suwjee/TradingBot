# Phase 07 — Checkpoint 251 / W1 B09-90

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `fc39d697b5807ac621dddb80138f4f8ff3b013c7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB91/TB92/TB93, lines 3498–3533; 24 original category rows; cumulative B09 2078/2276.

[Site evidence](Semantic_Closure_B09_90.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L107). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Reversal initial direction, independent state and stopped publication

Initial current context is the original market; incoming is None. Exact target bullish (also absent default) selects initial bearish, otherwise bullish. Each calculation shallow-copies args and replaces direction, prepares state with no live argument when continuation is None and with explicit live otherwise; then builds direction output. Publish projects absolute indexes first; start metadata is added only when offset differs from original market offset, not merely when nonzero. Non-null incoming is attached as singleton trendTransitions. Stopped output uses transition candle in current context, not exact event time; overwrites primaryStatus and each existing cycle status, clamps each leg cap with min(old cap, end). Missing arrays default empty, existing values used as supplied. Optional release function is looked up once before loop. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3498-L3533).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
