# CP354 — W3 Reaction records and DetectorBase forensic review

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`; Reaction source blob `9adffb832ffa231ba0cb01de507a30fbe62be0b0`, lines 1–234. Separate same-assistant source-first pass, not an independently staffed or blind audit.

## Local disposition

PASS_SCOPED for declarations and RE01–RE08: 106 W1 rows, 480 additional category rows, 7 historical supplemental items, 52 source contract groups. Exact category/row/node/span joins plus manually derived source-group semantics and row roles are recorded. Overlapping category records are not distinct rules or runtime paths.

- Candle, ResetEvent, IntrabarAnalysis and DetectionResult are frozen/slotted but referenced values are not deep-frozen. Candidate and cursors are mutable/slotted. Nullable required fields differ from default None fields. Record annotations do not validate or normalize prices, timestamps, modes, tags or indexes. Checkpoint record itself has no rollback.
- Candle color uses inclusive open<=close; ordinary equal values are GREEN. Opposite direction delegates policy selection and its exception behavior.
- DetectorBase retains input references and selected bounds. Global main/lower time indexes and shared lower index are obtained before positive timeframe check. Fresh per-detector break cache is distinct from shared caches. Timeframe inferred only from first pair, otherwise one second. No constructor rollback or freshness validation.
- Time cache uses exact identity and retains source/list; materialization follows input order. Lower window bounds eager, item lookup lazy. Main-source mapping uses last equal open, inclusive selected position range and next actual full-sequence open (or nominal final end); strict upper end. Not interchangeable with MarketChronology.main_index.
- Extrema route at end-start>=16 (17 inclusive rows). Native indexed leaf normalization versus direct stored-price linear scan; reflection swaps extrema with copy_negate. First equal owner retained under valid finite native inputs. Linear initializes start even for reversed range; no blanket invalid-input equivalence.

## Findings

CP354-F01: RE07/08 clarify exact threshold, normalization, invalid range and reflection distinctions.
CP354-F02: RE03–05 clarify preparation/validation ordering, identity/freshness, and eager bounds/lazy lookup.
CP354-F03: record mutation, shallow copies, candidate/checkpoint lifecycle and all consumers remain open. Five direct native handoffs inspected, not exhaustive.

## Evidence

- [Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP354_W3_Record_Base_Local_Forensic_Register.json)
- [Consumer boundary register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP354_W3_Record_Base_Consumer_Boundaries.json)
- [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP354_Completion.json)

W3 INCOMPLETE; W4 NOT RUN. B02 reviewed 1–234 and 886–1369; complement 235–885 and 1370–2908. Continue from 235–327 (green run, breakout and invalidation/confirmed-reset race helpers). No RAW payload, project runtime, ZIP, production or main change.
