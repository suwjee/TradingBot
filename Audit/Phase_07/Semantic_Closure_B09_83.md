# Phase 07 — Checkpoint 244 / W1 B09-83

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `2dda09909aae83e73299ac587d313f7a24f5d7e9`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB84, lines 3290–3324; 56 original category rows; cumulative B09 1900/2276.

[Site evidence](Semantic_Closure_B09_83.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L195). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Primary visibility, formed MBL chronology and cap projection

Point selection evaluates inclusive source start/end first, then inclusive decision end; a failed source test skips the decision check and serialization. Visible cycle collection retains encounter order for cycles with an MBL and trigger no later than visible end; formed leg selection is separately delegated through end, requires a confirmed primary point, and does not clip source to visible start. MBL identity offsets reference and second indexes only in the id. Cap uses the actual full-history candle at source+400 if strictly below candle count, otherwise last candle timestamp plus timeframe times (source+400+1-count); no visible-end clamp. Trigger and confirmation main times and exact event times are separately sourced. Each stop field independently tests non-null stop index then <= end; zero and equality survive. Non-null cycle id adds transformed cycleId. Output legs retain generator order. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3290-L3324) · [Primary owner](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L128-L195).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
