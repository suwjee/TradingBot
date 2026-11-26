# CP398 — Independent local initial Order records, gate ownership and creation events

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA45–OA49 lines 1524–1643. B05-15. Source-only, no execution.

## OA45-A — lines 1524–1538

Return primary cache whenever non-None, including empty tuple, by reference before reading ledger or any secondary state. No validation, synchronization, invalidation or repair of missing secondary indexes on this path. Declared immutable run ledger is an owner premise, not a local enforcement.

## OA45-B — lines 1539–1548

On miss allocate local list, iterate initial_order_audit.values() in native mapping order; ignore mapping keys. Read required reaction, compute First via owner callback, read required confirmation, normalize required stop via as_decimal, then resolve crossing dynamically. No identity deduplication, range/acceptance filtering or local validation; crossing None retained. Existing Decimal instance preserved; other inputs converted from str, no quantization.

## OA45-C — lines 1549–1554

Append eight-field record only after all argument evaluations succeed: computed First, original confirmation, int reaction number, original reaction reference, normalized stop level, int source index, original stop source time, crossing. Number conversion precedes source index conversion and source time read; crossing lookup has already occurred. No fresh geometry, no canonical stop recomputation, no stored stop_cross lookup. Errors propagate; earlier delegated crossing/cache effects survive.

## OA45-D — lines 1555–1557

Stable in-place primary sort ascending lexicographic (stored First time, confirmation, int current reaction.first_idx, int current reaction.break_idx). Equal keys preserve ledger iteration order, no ordinal tie key. All key evaluations require both geometry fields. Convert list to tuple, publish primary before any secondary projection; record/reaction references retained.

## OA45-E — lines 1558–1568

Publish projected First-time list from sorted tuple, then build local grouping by exact native First key via setdefault and append each same record reference in primary order. Publish dictionary of tuple buckets only after full comprehension succeeds. No deduplication; equality/hash native. Partial primary/First publication survives group failure; later hit does not repair it.

## OA45-F — lines 1570–1581

Independently stable-sort primary tuple by (confirmation, stored First time, int current First index, int current Break index); tie order follows primary input. Reuse same records, do not recalculate crossing/First; index keys reread geometry. Publish confirmation-record tuple then confirmation-time list; return primary tuple. No atomic multi-index commit or rollback. After any late failure earlier published attributes remain, including primary non-None; reset setter does not clear these initial caches.

## OA46 — lines 1582–1596

Static converter accepts exactly eight iterable fields through unpacking, ignores first stored timestamp, returns nine-field OrderMatch (number,reaction,confirmation,level,source index,source time,crossing,supplied causes,None). No normalization, new reaction, cause copying, crossing validation or lookup. Wrong arity/noniterability propagates unpacking error; supplied causes not enforced as tuple at runtime.

## OA47-A — lines 1597–1604

Entry converter reads required reaction, confirmation, then normalizes required level and calls dynamic crossing before any number/source int conversion. No First callback, primary cache materialization, entry stop_cross read or filtering; same conditional base/live crossing contract as OA45.

## OA47-B — lines 1605–1611

Return nine fields in OrderMatch order, int number then int source index, original reaction/confirmation/source time, normalized level, crossing including None, supplied causes unchanged, None creation time. No ledger write or new geometry; missing keys/conversion failures propagate after possible crossing side effects.

## OA48-A — lines 1612–1619

Map parent_stop to owner clamped main index and read self.times at that index before materialization. Force OA45, then assert by-First dictionary is not None, not nonempty; no rebuild on cache hit. Allocate local matches. Mapping may fail before any materialization; assertion is native assertion, not fallback.

## OA48-B — lines 1620–1627

Exact gate_time dictionary bucket lookup (default empty tuple). Iterate primary stable bucket order, read confirmation and reject strictly earlier than parent_stop before reading crossing; reject None or exact crossing slot 2 strictly earlier. Both time equalities allowed; no separate crossing>confirmation, reset, owner acceptance or future deadline gate. Convert surviving record via OA46 with carried-live only; no direct registration.

## OA48-C — lines 1628–1634

Min over matches by (exact lower crossing event, recomputed owner reaction First time), earliest lexicographic, first equal key wins in bucket order; empty returns None without key evaluation. Recompute First rather than stored First; under immutable geometry all bucket First times equal. No descending First-index tie rule here; do not conflate E global winner. Malformed eligible fields propagate; local list not published.

## OA49-A — lines 1635–1639

Static helper obtains causes using missing-key default empty tuple (not None coercion), iterates native order; inspect cause slot 0, select exact parent-stop and then read slot 3 only for selected cause. No validation of tuple shape, owner type or time. Zero/one event preserved; if more than one, native min replaces list with singleton, not all tied minima. Comparison errors propagate before B iteration.

## OA49-B — lines 1640–1643

Iterate order_b_causes with missing-key default empty tuple, append every required physicalOrderConfirmationTime in native order, preserving duplicates and equal values; no earliest-only B reduction, global sorting, deduplication, timezone/Decimal conversion, or local catch. Return new list parent event first if any, then all B times. Missing key/None/malformed rows may raise; no ledger writes. Indexed consumer later validates/deduplicates conditionally, not this helper.

## Consumer boundaries

- engine/pipeline/order_audit_engine.py [[570,587],[1459,1477]]: Primary and First list/by-First/confirmation-time cache initialized None; confirmation record tuple initially empty. Base crossing caches exact (start,level), including None; exact lower event and candle timestamp; OA45/OA47 dispatch dynamically and preserve the returned object.
- engine/pipeline/e_zone_detector.py [[358,367],[385,411],[416,417],[537,566]]: Nonempty initial mapping retained by reference; falsey input replaced with new empty dict. Initialization after live state assignment. Sequence reset setter clears only four named query caches, not initial-record or crossing caches. First time via self.times[int(reaction.first_idx)]; main index clamped owner; live crossing may validate dirty chronology and use self.times[index], unlike base candle.timestamp. No runtime dispatch claim.
- engine/pipeline/reaction_engine.py [[1185,1192]]: Main index = right insertion bound minus one; if below zero clamp returns zero, otherwise native result. Equal main times map to last equal slot under ordered premise.
- engine/pipeline/core_utils.py [[51,53],[60,66]]: Existing Decimal instance returned unchanged else Decimal(str(value)); canonical physical geometry pair integer First/Break. Primary sorting uses both indexes but does not deduplicate by identity, and ignores original ledger key.
- engine/pipeline/e_zone_detector.py [[608,642],[651,675]]: _zone calls gate-owned initial helper before carried lookup and registration. Local gate_owned assignment is not used in that function's merged choice routes; evaluation still materializes/raises. E merge compares exact crossing then descending First int and disowned-S gate; no gate-local winner equivalence.
- engine/pipeline/order_audit_engine.py [[2035,2043]]: Separate _blocked_by_gate_owned_order only queries gate if zone causes include parent-stop; rejects when gate exists and its confirmation strictly precedes zone.order_first_time. Equal confirmation does not block; gate-local selection is not direct final E choice.
- engine/pipeline/order_audit_engine.py [[1644,1697],[1741,1795]]: OA50 native validation and index creation conditionally call OA49 and deduplicate events per entry, sorted by event/ordinal; fallback legacy scan calls same helper with strict lifecycle_start<creation<parent_stop, confirmation<=parent_stop and crossing>=parent_stop. Initial route uses First inclusive [lifecycle_start,parent_stop], confirmation<=parent_stop, crossing>=parent_stop; carried global sort exact event then descending First. OA50+ local closure is later.
- engine/pipeline/order_audit_engine.py [[1812,1836],[1910,1932]]: Eager post-stop initial route bisect_right confirmation times, then requires crossing>parent_stop and >confirmation, reset filter and physical identity selection. Stream materializes initial geometry before its localcontext/validation try; native geometry fallback separate. Initial-record cache failures before that try can propagate.

## Verification

407 category rows: 66 prior W1 and 341 additional; seven historical supplements; all 4465 prior rows structurally revalidated without overlap; all 85 prior supplemental IDs and spans match historical partitions. Local scoped only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP398_W3_B05_Initial_Order_Records_Gate_Creation_Events_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP398_Completion.json).

Separate source-first pass by GPT, not independently staffed. Local source review only; immutable input ledger/geometry, native chronology, dynamic base/live crossing, Decimal context and cross-owner ownership remain conditional. Partial cache publication is documented actual behavior, not an observed runtime defect.

No runtime, RAW payload, ZIP or production changes. Counts derived from pinned canonical source-backed inventory, not newly generated AST. Prior B05 row identity and all supplemental ID/span checks revalidated; unrelated historical artifacts not re-read.
