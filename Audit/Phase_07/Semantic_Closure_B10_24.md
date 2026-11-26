# Phase 07 — Checkpoint 284 / W1 B10-24

**Local PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry `1ba6affbff3bfa2dd2c7f36849007a04d9735da9`; engine/bridge/live_pipeline.py lines 184–197; 31 original rows.

[Site evidence](Semantic_Closure_B10_24.json) · [Crosswalk](Decision_Site_Crosswalk_01.json) · [Context ledger](Semantic_Context_Batch_01.json) · [Contract](../../Algorithms/V3/23_Live_Transport_Contract.md#L69) · [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/live_pipeline.py#L184-L197).

## Binary header validation and progress scope

Read at most 256 bytes, bind truthy header; EOF terminates normally. Require newline, parse JSON, extract bytes/digest/base. Exact positive int size, string digest length64; no hex validation. Read declared size and require exact length. Exact True progress chooses sink else no-op. Enter progress context.

W2/W3/W4 open. No runtime, RAW payload or production changes.
