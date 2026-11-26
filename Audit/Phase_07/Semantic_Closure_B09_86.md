# Phase 07 — Checkpoint 247 / W1 B09-86

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `22f1df1a1df592fb1b4911d5057f6cf80940b7f4`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB87/TB88, lines 3371–3403; 17 original category rows; cumulative B09 1986/2276.

[Site evidence](Semantic_Closure_B09_86.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L95). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Primary dual-owner groups and callback audit refresh

Opposite direction is obtained from chronology; current visibility primary_groups is retained by reference, opposite range and visibility are recomputed in that order, and both groups are then used directly. Owner iteration is fixed bullish then bearish. For each owner, accepted A is a set of source times from its S detector eligible A zones, excluding exact (source_time, int(source_index)) identities in that owner's invalid set; multiple accepted rows at one source time collapse. Full audit bounds are 0 and len(main candles)-1 inclusive, using the corresponding E detector, S detector and accepted set. Callback uses the requested primary direction, not the opposite or iterated owner; exact bullish selects register_primary_low, otherwise register_primary_high. Registration runs before refreshing that same group's full audit with the retained accepted set. No local exception handling, copying or rollback of group/detector mutations. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3371-L3403).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
