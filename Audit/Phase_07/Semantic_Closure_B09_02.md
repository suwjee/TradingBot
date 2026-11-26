# Phase 07 — Checkpoint 163 / W1 B09-02

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `866184b604be85951ceab86ea65b738a04575a36`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB01–TB03, lines 54–85; 24 original rows; cumulative B09 33/2276.

[Site evidence](Semantic_Closure_B09_02.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L44). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Context progress, failure ordering and timing telemetry

- B09-02-F01: Details are merged after status and label, and a supplied non-null duration overwrites durationMs with a two-decimal rounded telemetry value. Exact null selects compact stderr JSON with flush; non-null sink is called directly. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L54-L85) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L41).
- B09-02-F02: The start emission is outside the try; on its failure work is not called. Completion telemetry runs in finally after work return or error, with unrounded accumulated duration in the timings map. A failure in finally can supersede the work result or exception. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L54-L85) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L44).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
