# Phase 07 — Checkpoint 260 / W1 B09-99

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `fc39d697b5807ac621dddb80138f4f8ff3b013c7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB102/module entry, lines 3717–3757; 35 original category rows; cumulative B09 2276/2276.

[Site evidence](Semantic_Closure_B09_99.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L140). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## CLI timing, compact JSON and exception exit semantics

Capture pipeline and validation performance counters separately, emit validation started before parse, store elapsed validation ms and emit completed. Load engines outside scope, then scope market preparation, state and payload. After scope success emit total calculation completion in ms, start encoding counter, json.dumps with separators comma/colon, emit encoding completion, print encoded payload and return 0. Module guard exact __main__ invokes main and raises SystemExit(result); catches ordinary Exception only, prints JSON error with str(exc), raises SystemExit(1). SystemExit and other non-Exception BaseException are not intercepted. Timings concern telemetry only. No runtime execution in this review. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3717-L3757).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
