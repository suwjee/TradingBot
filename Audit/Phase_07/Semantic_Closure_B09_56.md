# Phase 07 — Checkpoint 217 / W1 B09-56

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9867049120fdd0b558150bfb73b642fa4bee4b3e`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB73, lines 2261–2293; 16 original rows; cumulative B09 1336/2276.

[Site evidence](Semantic_Closure_B09_56.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L75). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## A visibility and all-eligible dominant-stop validation

- B09-56-F01: The two candidate_a visibility calls are executed but their result is not passed to dominant-stop validation: that call receives a shallow list of ALL S-eligible A, original S candidates, current E and empty StopAll. Its mutable stage-invalid set is an output argument. The parent-stop label is selected by attribute presence; A-stop confirmation directly indexes trend_reactions at int(reaction_number)−1 without a local bounds guard. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2261-L2293) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L75).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
