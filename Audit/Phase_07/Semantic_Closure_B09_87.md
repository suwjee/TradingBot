# Phase 07 — Checkpoint 248 / W1 B09-87

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `22f1df1a1df592fb1b4911d5057f6cf80940b7f4`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB87, lines 3404–3426; 16 original category rows; cumulative B09 2002/2276.

[Site evidence](Semantic_Closure_B09_87.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L95). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Native Primary dispatch, label reconciliation and retained audit identities

Construct one NativePrimaryOrders resolver from chronology, both groups, callback and requested direction. Select detect_bullish only for exact bullish, otherwise detect_bearish; if live_stages is non-null call its primary service with direction, groups, resolver and requested E detector instead of the batch detector. Batch consumes requested S/E/StopAll groups and same resolver. After obtaining primary result select low resolution and low-label reconciliation for bullish, otherwise high counterparts; invoke resolution through market.end_index before reconciliation. Capture required identities from every existing visibility.prepared_order_audit reaction's first_idx and break_idx using order_identity; set deduplicates. Rebuild only the visibility audit using visible start/end, requested detectors, retained accepted A set and required identities. Return primary; failures propagate; callback and reconciliation effects are not locally undone. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3404-L3426).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
