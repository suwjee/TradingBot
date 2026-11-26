# Phase 07 — Checkpoint 207 / W1 B09-46

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4d07e075f1fb57f03663eba1c6af5af0b8fea85b`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB66, lines 1815–1891; 25 original rows; cumulative B09 1167/2276.

[Site evidence](Semantic_Closure_B09_46.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L62). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## CLI argument contract, aliases, flags and validation

- B09-46-F01: Analysis timeframe check precedes RAW timeframe check; both are native integers from parser, require >=1. The parser does not independently check from/to ordering or positivity of timestamps. Required paths are Path conversions; E/lifecycle optional; bridge-output store_true; primary and three behavior flags default enabled. Native parser failures propagate. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1815-L1891) · [Contract](../../Algorithms/V3/17_Trading_Bridge.md#L62).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
