# Phase 07 — Checkpoint 153 / W1 B08-16

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `5b8fc97ab572038ab288cb9d51bb47b22efa3b16`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P19–P21, lines 474–517; 34 original rows, 3 supplemental items, 3 resolved local clarification groups. Primary cumulative 389/670.

[Site evidence](Semantic_Closure_B08_16.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L111), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact IDs, spans, procedures and operations matched.

## Run crossing-cache reuse, MBL refresh and independent activation

- B08-16-S01: Cache key uses exact event, string representation of level and above argument. Return stored result on membership, including a stored null. Strict-after-event search starts at upper bound. Previous reuse only if previous non-null and key present; short-circuit. Old hit reused only if non-null and strictly earlier than dirty event; equality must re-search. When prior key exists but not reusable, resume at max(original strict start, lower bound of dirty event). Delegate crossing from computed left boundary; cache result including null. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L474-L489).
- B08-16-S02: Find below-floor crossing after original MBL trigger using provided crossing service. Falsy stop pair becomes null/null; no price mutation. Compare exact stop index/time pair; unchanged returns original checkpoint identity. Replace MBL only with new stop fields. Replace result and checkpoint shallowly, preserving unrelated fields and collections. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L490-L499).
- B08-16-S03: Fresh PrimaryResult with bearish cycle id formatted from raw donor indexes and qualification. Reference main High at integer reference index, normalized Decimal. Compute inclusive minimum Low from integer second index through activation gate main. Search below floor strictly after activation cursor. Construct MBL with selected source, main timestamp, floor, donor indexes and trigger. Integer-normalize reference donor index. Integer-normalize second donor index. Each broken-field selection uses truthiness of hit, otherwise null. Return new checkpoint with original reference price, gate and cursor; default PH. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L500-L517).

## Findings

- B08-16-F01: A stored null is a cache hit by membership. Prior key present with null result or hit at/after dirty time uses dirty lower bound; a missing prior key scans the full strict-after-event window. The string level key is not numerically normalized here. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L111).
- B08-16-F02: A falsy crossing result maps to null/null. Exact pair equality preserves checkpoint identity; otherwise replacements are shallow and preserve unrelated list references. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L115).
- B08-16-F03: The cycle identifier uses donor index formatting before integer normalization; the MBL stores integer donor indexes separately. Broken fields use hit truthiness, and the checkpoint takes its PH/reset defaults. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L119).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
