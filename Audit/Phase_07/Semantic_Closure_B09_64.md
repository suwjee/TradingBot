# Phase 07 — Checkpoint 225 / W1 B09-64

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9867049120fdd0b558150bfb73b642fa4bee4b3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB74, lines 2515–2540; 12 original rows; cumulative B09 1461/2276.

[Site evidence](Semantic_Closure_B09_64.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L79). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Feedback StopAll lifecycle and accepted reset-leg discovery

- B09-64-F01: Optional StopAll uses same enable contract as final visibility; absent flag copies state E and uses empty StopAll. Local E restoration and audit ensure precede reset-leg discovery. Live finders are obtained only if live is non-null, with feedback/pass scope; no local Order selection is reconstructed. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2515-L2540) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L79).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
