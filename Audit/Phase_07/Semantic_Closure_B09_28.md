# Phase 07 — Checkpoint 189 / W1 B09-28

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `9658be2dda143e889bb770fa9c249866bb8dadb7`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB51–TB52, lines 1133–1180; 26 original rows; cumulative B09 712/2276.

[Site evidence](Semantic_Closure_B09_28.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L137). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Blue output and stable full-history ordinal map

- B09-28-F01: Formation kind is string/lowercase; only scale/reset map to labels, only reset adds brokenLevel. Stop price is retained source extreme but both stop times are always null because standalone Blue stop evidence is not retained; no new detector is created. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1133-L1180) · [Contract](../../Algorithms/V3/19_Serialization.md#L137).
- B09-28-F02: Sort is stable for exact equal keys; the kind key is string conversion without lowercasing, unlike output formation mapping. Ordinal enumeration starts at one and retains original line references. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1133-L1180) · [Contract](../../Algorithms/V3/19_Serialization.md#L140).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
