# CP401 — Independent local post-stop accepted Order query

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA53–OA54 lines 1798–1878. B05-18. Source-only, no execution.

## OA53-A — lines 1798–1810

Delete local parent binding without inspecting parent fields. Key is native (parent_stop, current confirmation-index length), not ledger identity, actual geometry, reset version, direction, Decimal context or parent identity. Evaluate index length before cache lookup. Non-None cached list including empty is a hit; return a fresh shallow list without any initial materialization or eligibility checks. Cache correctness depends on detector-local ownership, geometry coherence and invalidation; length alone cannot detect same-size replacement. Native hash/equality errors propagate. Allocate local identity dictionary only on miss.

## OA54-A — lines 1812–1820

Nested add_match receives an already constructed nine-slot match. Read crossing slot 6; None returns before reading crossing event. Read slot 2 of crossing, reject crossing<=parent_stop first, then crossing<=match confirmation by short-circuit OR. Both equalities rejected. Only then call dynamic reset predicate on (parent_stop,crossing); native helper uses right bisect at start and checks earliest later reset<=end, hence reset equal stop excluded and reset equal crossing included. No confirmation>parent_stop, cause, price or direction check in this helper. Exceptions propagate; no local catch.

## OA54-B — lines 1821–1829

Read reaction then int First and Break via getattr in that order. Identity is physical pair, not reaction number, object equality, index tuple or cause. Lookup current winner. Absent inserts without evaluating rank; otherwise compute new (crossing,confirmation,+int First) then existing (crossing,confirmation,+int First), replace whole match only on strict lexicographic less. Equal retains earlier candidate, even different level/source. Replacing existing dict key preserves its insertion position. Positive First is the comparison key here, not final descending First. Dynamic properties can be read again; no revalidation or catch. No provenance union or ledger writes.

## OA53-B — lines 1831–1836

Force dynamic initial geometry materialization before reading accepted ledger. Assert confirmation-time array is not None, not nonempty; read confirmation-record view; right bisect time array at parent_stop, excluding all equal confirmations under sorted/coherent view. Slice suffix eagerly, then convert each record via dynamic OA46 with accepted-live singleton and call OA54. Initial candidates enter dictionary before ledger candidates. OA45 may compute all initial geometry/crossings including unselected rows, cache intermediate state or raise before any ledger scan; OA53 does not undo these effects.

## OA53-C — lines 1838–1847

Right bisect full ordered confirmation-index tuple using (parent_stop,2^63-1,2^63-1); both sentinels computed by exponent/subtraction. Under coherent index and identity bounds this excludes confirmations equal stop; arbitrary larger identity fields can admit equal-time tuples. Slice suffix, unpack each indexed confirmation/First/Break; indexed time is discarded, lookup ledger by unconverted pair, skip only None row. No sort/shape validation or fallback for bad index, no recheck that entry's actual confirmation is after stop or matches indexed confirmation. Lookup and unpack errors propagate.

## OA53-D — lines 1848–1856

Read reaction then actual confirmation via get before gate; reject reaction None or confirmation not isinstance(datetime), allowing subclasses. Read level, source index, source time in order before rejecting any None, short-circuit None checks. Zero/false/empty non-None values are not automatically rejected; no exact native type, timezone, finite level, index bounds or source-time type check. Missing keys default None. Nonmapping entry or custom access may raise.

## OA53-E — lines 1857–1868

Read stored crossing; reuse if isinstance(tuple), length>=3, slot2 isinstance(datetime), in that order; subclass accepted, no slot0/1 check, extra slots retained. Otherwise invoke dynamic crossing with actual confirmation and as_decimal(level); no writeback into ledger. Base OA43 may use its own cross cache and returns exact lower event. Build match before nested eligibility: int number from get default 0 (explicit None still errors), original reaction, actual confirmation, as_decimal(level) again if fallback, int source index, original source time, crossing, accepted-live singleton, None parent-stop creation time. Decimal instance retained else Decimal(str(value)), caller context, no imposed rounding/finite check. Even if crossing None or rejected later, conversion happens first. Fallback conversion/crossing may fail before number conversion; valid stored crossing bypasses first conversion/call. No local catch, no implicit skip on malformed conversion.

## OA53-F — lines 1870–1877

Sort identity dictionary values stably ascending by exact crossing slot2, confirmation, negative int First (later First wins only when first two keys equal). Dict first insertion order breaks equal complete keys, including after replacement. No Break or reaction number tie key. Compute keys and complete sorting before cache assignment. Store original result list, return a fresh shallow list on miss as on hit; nested match objects remain shared. Failed conversion, sort, reset or comparison prevents final cache publication; initial/cross caches may already have changed. If copy after assignment fails, cache already published. No ledger registration in this query.

## Consumer boundaries

- engine/pipeline/order_audit_engine.py [[590,607],[1089,1132],[1140,1166],[1240,1248],[1371,1433],[2190,2224]]: Run-local post-stop result cache. Reset predicate uses sorted times, first reset strictly after start and <=end. New physical identity inserts confirmation tuple by right bisect, length changes, stream pending append if active. Clear/revocation invalidates post-stop caches, cause-only update normally invalidates carried but not post-stop. New registration and restoration insert index rows. Length key not a version; relies on owner invalidation and coherent immutable geometry.
- engine/pipeline/order_audit_engine.py [[1459,1477],[1524,1596],[1879,1934],[1990,2017]]: Cross helper caches (start,level), lower range [max(start,range_start),range_end), direction-sensitive first strict crossing, returns mapped main index/time and exact lower event or None. Initial materialization reuses immutable geometry, primary sort First/confirmation/FirstIndex/BreakIndex, secondary confirmation/First/FirstIndex/BreakIndex. OA46 preserves record fields. OA55 eager fallback for non-native parent, invalid initial or audit view; later native stream uses same output key but stronger gates, own reset and identity dedup, full parity not claimed.
- engine/pipeline/core_utils.py [[51,53],[60,66]]: Decimal instance unchanged, otherwise Decimal(str(value)); actual conversion caller context. Physical identity is integer First/Break pair, same geometry convention as OA54, no use of ledger number or object identity.
- engine/pipeline/e_zone_detector.py [[395,411],[608,668]]: Reset setter copies mapping, sorts times and clears post-stop result cache among others. _zone registers current parent after carried query and before invoking OA55; accepted stream is grouped by exact crossing then re-sorted by negative First for global E adjudication across direct,inherited,carried,accepted. Disowned-S-only filter uses physical identity and prospective source. OA53 output key includes confirmation unlike E choice. Final E ownership is not OA53 responsibility.

## Verification

288 category rows: 78 W1, 210 additional; 7 historical supplements. All 5470 prior rows (1207 W1,4263 additional), 104 supplements and 1892 CP316 links reconciled; exact disjoint local union 5758/8318. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP401_W3_B05_Post_Stop_Accepted_Order_Query_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP401_Completion.json).

Separate source-first GPT pass, not independently staffed. Local source contracts only. Conditional on immutable initial records, coherent confirmation index and bounded identities, cache invalidation, native comparability and caller Decimal context; no runtime equivalence asserted. Eager versus lazy parity is not asserted and OA55–OA59 closure is deferred to CP402.

No RAW payload, runtime, ZIP or production changes. Counts from pinned canonical source-backed inventory, not newly executed AST generator. CP396 read through pinned path. Git blob identities used; no independent SHA-256 claimed.
