# Phase 07 — Checkpoint 173 / W1 B09-12

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `866184b604be85951ceab86ea65b738a04575a36`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB23–TB24, lines 373–439; 28 original rows; cumulative B09 234/2276.

[Site evidence](Semantic_Closure_B09_12.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/19_Serialization.md#L56). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations matched.

## Legacy Reaction and Reset selection and serialization

- B09-12-F01: Select resets by reset index and native reactions by First before invoking a non-null transform. Preserve native/public pair identities and encounter order; no validation of transform result. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L373-L439) · [Contract](../../Algorithms/V3/19_Serialization.md#L53).
- B09-12-F02: An explicitly supplied non-null selection bypasses selection and transformation even when empty. Reset secondTime uses an exact null gate. Only public reaction object fields are serialized from each pair; native item is retained for other views. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L373-L439) · [Contract](../../Algorithms/V3/19_Serialization.md#L56).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
