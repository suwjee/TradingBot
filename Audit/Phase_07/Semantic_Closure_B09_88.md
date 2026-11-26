# Phase 07 — Checkpoint 249 / W1 B09-88

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `22f1df1a1df592fb1b4911d5057f6cf80940b7f4`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** TB89, lines 3427–3468; 21 original category rows; cumulative B09 2023/2276.

[Site evidence](Semantic_Closure_B09_88.json), [immutable crosswalk](Decision_Site_Crosswalk_01.json), [context ledger](Semantic_Context_Trading_Pipeline.json), [active contract](../../Algorithms/V3/17_Trading_Bridge.md#L101). Pinned blob `7b28fa7e93c8980c082cb277fb75556959b1abcf`; exact IDs, spans, procedures and operations validated.

## Direction output primary activation and StopAll ownership gate

Always calculate direction range then finalize visibility before primary gating. Start local primary at None. Missing args.direction defaults to both for equality test; exact both chooses bearish primary owner, otherwise read args.direction. Gate short-circuits left to right: requested direction equals primary owner, primary engine non-null, requested E detector key present, explicit lifecycle_engine non-null. Only then timed PH/PL computation, assign state.primary_result, replace visible StopAll list via primary ownership resolution through visible end, then validate prepared audit against visible S/E/StopAll. Serialize direction payload regardless of primary gate; only non-null primary adds primary serialization via update, with no independent rerun. StopAll ownership helper removes matching physical source identity only for primary points decided by requested horizon; historical collection not mutated by helper. No local exception suppression. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3427-L3468).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
