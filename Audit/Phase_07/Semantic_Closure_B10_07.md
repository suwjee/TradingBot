# Phase 07 — Checkpoint 267 / W1 B10-07

**Local PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry `6e27afc8970c649ab433fff75d0d9f25c29369fe`; engine/pipeline/true_false.py lines 86–96; 15 original rows.

[Site evidence](Semantic_Closure_B10_07.json) · [Crosswalk](Decision_Site_Crosswalk_04.json) · [Context ledger](Semantic_Context_Batch_01.json) · [Contract](../../Algorithms/V3/22_True_False_Exact_Contract.md#L43) · [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/true_false.py#L86-L96).

## Independent repeat counters and F repair

Counters start one. Accumulate independently only same-rank same-verdict. F removes earlier repair >= current time, missing default -1 not null fallback; repair current. Replace repeat, no final sweep.

W2/W3/W4 open. No runtime, RAW payload or production changes.
