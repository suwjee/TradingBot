# Phase 07 — Checkpoint 252 / W1 B09-91

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `fc39d697b5807ac621dddb80138f4f8ff3b013c7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB91/TB94, lines 3534–3559; 31 original category rows; cumulative B09 2109/2276.

[Site evidence](Semantic_Closure_B09_91.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L116). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Reversal advance guard, independent prefix and cleanup

Loop is unconditional; transition.index must satisfy strictly 0<boundary<len(current.candles), independent of visible start. Otherwise raise RuntimeError. Closure captures current context, boundary and direction via default arguments. Slice [0,boundary), excluding transition candle. has_history tests visible start<=end; if false replace visible bounds by full prefix [0,len-1] for internal proof while preserving false flag. Calculate prefix without continuation, resolve highs only for exact bearish, otherwise lows, through full prefix final index, not visible end. Return offset, first candle timestamp, original history flag, payload, confirmed points. Finally call release_indexes when non-null, else live fallback only when live non-null; prefix construction and replacement are before try. Non-null live delegates to closed_regime with closure instead of directly invoking it. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3534-L3559).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
