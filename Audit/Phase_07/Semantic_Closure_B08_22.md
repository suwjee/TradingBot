# Phase 07 — Checkpoint 159 / W1 B08-22

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `5b8fc97ab572038ab288cb9d51bb47b22efa3b16`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P37–P39, lines 743–769; 26 original rows, 2 supplemental items, 2 resolved local clarification groups. Primary cumulative 609/670.

[Site evidence](Semantic_Closure_B08_22.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L200), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact IDs, spans, procedures and operations matched.

## Bullish projection identity, recursive point cache and replay

- B08-22-S01: Truthy cycle id replaces first occurrence anywhere; falsy value returned unchanged. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L743-L754).
- B08-22-S02: Local cache keyed by object id; only absent keys project. Consult previous run projection only if run and previous truthy; lookup by id. Reuse previous pair only if non-null and stored original is identical, not value-equal. Otherwise create replacement of point with mirrored fields. Exact PH becomes PL, other kind becomes PH; price sign copied. Reflect order snapshot and project cycle id. Recursively project truthy identity_source, else null; no cycle guard before recursion. Store projected point in local id cache after recursion. Only non-null run receives projection pair. Store original and projected object pair by id, including reused projection. Return cached projected point; existing cache avoids recomputation. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L755-L769).

## Findings

- B08-22-F01: The projection cache is per invocation, and a live run retains original/projected object pairs; it is not a numeric or source-index cache. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L192).
- B08-22-F02: Previous-run reuse requires original object identity in addition to id-key lookup. Recursion completes before local cache insertion; a cyclic identity_source is not locally guarded. Even a reused prior projection is stored in the current run when non-null. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L200).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
