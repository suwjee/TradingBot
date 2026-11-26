# Phase 07 — Checkpoint 237 / W1 B09-76

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9867049120fdd0b558150bfb73b642fa4bee4b3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB77, lines 2942–2972; 14 original rows; cumulative B09 1651/2276.

[Site evidence](Semantic_Closure_B09_76.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L89). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Pre-range projection snapshots and full primary groups

- B09-76-F01: Capture pre-display accepted S/E/StopAll lists before final lifecycle visibility. The primary groups are built after that call but before range clipping/internal filtering: A from full noninvalid A, S/E from returned visible calculation lists, StopAll from current list. Candidate-event callback uses recorded source index, price and source time. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2942-L2972) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L89).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
