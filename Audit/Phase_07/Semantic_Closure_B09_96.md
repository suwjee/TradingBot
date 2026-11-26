# Phase 07 — Checkpoint 257 / W1 B09-96

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `fc39d697b5807ac621dddb80138f4f8ff3b013c7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB96/TB97, lines 3648–3669; 25 original category rows; cumulative B09 2215/2276.

[Site evidence](Semantic_Closure_B09_96.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L122). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## True/False repair horizon and closed confirmation boundary

Repair through equals visible end main open plus chronology timeframe minus one second. Build repair finder with lower index, local_datetime, epoch and inclusive through parameter. raw_timeframe defaults to 1 only if attribute absent. closed_through is lesser of epoch(through)+1 and last available seconds candle epoch+raw_timeframe. StopAll callback compares decisionTime+args.timeframe<=closed_through; equality closed. Iterate directions and each calculationSegments or absent singleton tuple, call apply_true_false with shared finder and callback. Merged rows may share references; this local path does not separately rebuild aggregate arrays. Phase timings rounded to two decimals; total measured as elapsed perf_counter seconds times 1000 then rounded, not price rounding. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3648-L3669).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
