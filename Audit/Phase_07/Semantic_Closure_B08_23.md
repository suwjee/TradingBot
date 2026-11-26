# Phase 07 — Checkpoint 160 / W1 B08-23

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `5b8fc97ab572038ab288cb9d51bb47b22efa3b16`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P40–P43/P37, lines 770–799; 36 original rows, 2 supplemental items, 3 resolved local clarification groups. Primary cumulative 645/670.

[Site evidence](Semantic_Closure_B08_23.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L208), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact IDs, spans, procedures and operations matched.

## Bullish result projection and native Order callback adapter

- B08-23-S01: Apply four chained global case-sensitive replacements in sequence: ph to placeholder, pl to ph, placeholder to pl, reversal target text swap; not token-aware. Replace result direction bullish; map original lows to projected highs in order. Map original highs to projected lows in order. Truthy MBL replaced with sign-copied price, else null; other MBL fields retained. Project cycle id and status. Reflect each post-PL3 Order snapshot, preserve iteration order. Recursively project each nested cycle with shared point cache. Truthy transition replaced with sign-copied level. Project transition's high through same point cache, set target bearish. Falsy transition becomes null. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L770-L784).
- B08-23-S02: Native request kind PL only when reflected core asks PH, else PH. Call original Orders with native kind and unchanged number/gate/event; reflect each returned snapshot in order. Read original confirm_high attribute with null fallback on each callback. Invoke only non-null callback; no truthiness or callable validation. Pass native projected point; ignore callback return. Run bearish core with reflected chronology, unchanged native S/E/StopAll, then project result. Create new adapter instance and pass same run object in reflected coordinates. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L785-L799).

## Findings

- B08-23-F01: The four replacements are global, case-sensitive and order-dependent, including any preexisting placeholder text; they are not a general directional token parser. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L204).
- B08-23-F02: All nested cycles and transition points use the same point cache; MBL and transition use truthiness gates, whereas their non-null box fields use exact null gates elsewhere. The result replacement preserves unrelated fields. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L208).
- B08-23-F03: The adapter always exposes confirm_high to the bearish core; therefore its scheduler treats that callback as present and clears pending after a successful adapter invocation even if the native callback is absent. The native callback sees the projected point and no reflected chronology. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L216).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
