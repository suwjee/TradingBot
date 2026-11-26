# Phase 07 — Checkpoint 228 / W1 B09-67

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9867049120fdd0b558150bfb73b642fa4bee4b3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB75, lines 2588–2618; 25 original rows; cumulative B09 1505/2276.

[Site evidence](Semantic_Closure_B09_67.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L82). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Full geometry detectors, native/live Reaction and ownership

- B09-67-F01: Full reusable branch constructs both full-history detectors regardless of requested output. Directional initial trend flags are gated by matching direction. Null live uses each detector.detect; non-null live uses shared live.reactions. Ownership is live callback or native tuple element 2. Non-null report callback runs after ownership, before subsequent lifecycle work. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2588-L2618) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L82).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
