# CP353 — W3 lower-timeframe index local forensic review

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`; Reaction source blob `9adffb832ffa231ba0cb01de507a30fbe62be0b0`, lines 886–1131. Separate same-assistant source-first pass, not an independently staffed or blind audit.

## Local disposition

PASS_SCOPED for RE31–RE52: 229 W1 rows, 780 additional category rows, 11 historical supplemental items, 80 source contract groups. Exact category/row/node/span joins plus source-group semantics and row roles are recorded. Overlapping category records are not distinct rules or runtime paths.

- Constructor retains source reference; optional crossing history, timestamp materialization in input order, power-of-two capacity, null value arrays and -1 position arrays. Low and High normalized separately. Parent aggregation chooses left on ordinary equality; query returns earliest equal sequence position, not candle.index.
- Suffix refresh rejects invalid chained range, allows no-op only at equal new length, clears history only when changed position precedes old final row. Timestamp list identity is retained. History clear, timestamps, length, leaves and parents mutate in order; no local rollback or arbitrary input protection.
- Extrema query rejects invalid half-open bounds; strict crossing clips and returns None for empty. Root/segment exclusion is directional and strict. Search uses positions, not timestamp sorting; inner node null behavior and descent rely on valid tree and native comparator assumptions.
- Crossing history stores only settled rows before last position; actual latest hit can be returned without remembering as settled. Key uses native equality/hash of level and callable, not string price representation or right bound. FIFO insertion eviction at 16384; no LRU promotion.
- Identity registry prepared path validates exact source object, not concrete class or freshness. Reflected wrapper aliases time array and reverses price queries via copy_negate. Global clear/release removes registrations, not objects retained elsewhere.

## Findings

CP353-F01: clarify native equality-based cache key and insertion FIFO in RE41/42, distinct from RE59 representation key.

CP353-F02: clarify positional firstness, inner-node null assumptions and right-child descent in RE43/44.

CP353-F03: keep full dirty frontier, lifetime and failure/rollback review open. Bounded Bridge and live routes confirm source-specific mutation boundaries, not all callers or external-reference recovery.

## Evidence

- [Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP353_W3_Lower_Index_Local_Forensic_Register.json)
- [Consumer boundary register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP353_W3_Index_Consumer_Boundaries.json)
- [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP353_Completion.json)

W3 INCOMPLETE; W4 NOT RUN. B02 reviewed 886–1369; complement 1–885 and 1370–2908. Continue from 1–234 (record declarations and DetectorBase), then remaining source regions. No RAW payload, project runtime, ZIP, production or main change.
