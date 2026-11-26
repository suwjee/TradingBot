# CP403 — Independent local disowned-S and gate-owned Order eligibility

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA60–OA61 lines 2020–2045. B05-20. Source-only; no algorithm execution.

## OA60-A — lines 2020–2024

Inputs are a supplied physical identity pair, a supplied collection of source times, and optional prospective source time (default None). Annotations describe intended types but perform no runtime conversion or shape validation. The annotation union is not trading arithmetic. Output is a predicate for exclusion due solely to disowned S creators, not positive proof of Order validity or a ledger mutation.

## OA60-B — lines 2025–2028

Lookup current ledger using the exact supplied identity, without int conversion or identity reconstruction. Return False at the first successful guard in order: entry is None (not general falsey entry); no truthy causes from get without explicit default; truthy order_b_causes; identity membership in initial_order_audit. Earlier successful guard suppresses later reads/membership. Missing/empty/None causes return False, not vacuous True for ordinary empty sets. A truthy B-cause collection or mere initial key presence protects against this exclusion without validating B provenance, initial record value, crossing, or geometry. Absence of current row takes precedence over initial membership evaluation. False only means this predicate does not exclude, not that any creator is independently proven valid.

## OA60-C — lines 2029–2033

If all four guards fail, read required entry causes again by subscription and iterate as supplied with universal all. For each cause, test in order: slot 0 equals literal parent-stop; slot 1 equals literal S; length strictly greater than 4; slot 4 belongs to source_times or equals prospective_source_time. Each AND and the inner OR short-circuits; on membership success no prospective equality read is required; on membership failure read slot 4 again. No tuple/exact type check, no casing/label or datetime normalization, no identity/source-index comparison, no inspection of family slot 2 or parent-stop event slot 3, no check of extra slots. Native source membership/equality includes None matching prospective default None; an unhashable source in a native set raises before the equality fallback. Empty tuple raises at slot 0; a one-slot matching parent-stop tuple raises at slot 1; matching kind/label but length 2–4 returns False before slot 4. Nonmatching earlier fields suppress later access. all stops at first false predicate; every cause must pass for True. Ordinary empty collection was rejected by the guard; a custom truthy empty iterator or changing collection can still yield vacuous True. No snapshot, sorting or local catch; membership, comparison, truthiness, indexing, length, iteration and dynamic mapping errors propagate if reached. For native sets iteration order is not specified; malformed-input error timing may depend on it. No ledger/cache writes, cause filtering, price calculation or market-direction branch in this method.

## OA61-A — lines 2034–2038

Input is EZone-like object; inspect zone.order_causes membership of literal parent-stop use label, not a physical ledger cause tuple, parent_type, or parent_stop creation field. If absent return False before reading parent_stop_event_time or querying OA48. No exact container/type check or normalization; membership and attribute exceptions propagate. Carried/accepted labels alone do not enable this veto; mixed labels containing parent-stop do.

## OA61-B — lines 2039–2045

If label exists, synchronously call dynamic OA48 with exact zone.parent_stop_event_time, not its mapped candle time or the Order's creation time. Return the short-circuit AND: match is not None, and its actual confirmation (slot 2) is strictly earlier than zone.order_first_time. When match is None, skip both match indexing and zone First read. Equal confirmation and zone First does not block; later confirmation does not block. No identity-equality check, no new crossing/price/reset check, no parent-type check and no comparison of zone decision event or own confirmation. The less-than operator is chronological and direction-invariant, not a bearish/bullish price mirror. OA48 itself may materialize/cache initial records and raise; no local catch or fallback, no direct ledger mutation. For native inputs result is boolean; dynamic comparisons are not coerced beyond the source AND semantics. True is veto for this rule only; False is not final eligibility.

## Decision boundaries (source-derived, not runtime tests)

| Condition, under ordinary native input contracts | OA60 result / effect |
|---|---|
| Current row missing, causes empty, B causes truthy, or initial key present | False; first successful guard short-circuits |
| Every cause is parent-stop S with source in owned set or equal prospective source | True; exclusion solely by this predicate |
| Any cause has different kind/label, matching first fields but length at most four, or unmatched source | False; later causes not inspected |
| Empty cause tuple or one-slot matching kind, if reached | Indexing exception; no local catch |
| Matching kind/label and source None, prospective default None, membership false | Source comparison succeeds; other cause and guard conditions still apply |

| Condition | OA61 result / effect |
|---|---|
| Parent-stop label absent | False; no gate query |
| Gate query returns None | False; no First read |
| Gate confirmation earlier than zone Order First | True |
| Gate confirmation equal to or later than zone Order First | False |

## Consumer boundaries

- engine/pipeline/order_audit_engine.py [[1135,1198],[1371,1433],[1524,1594],[1612,1632]] (blob 6ddb93ba097ef137af2405ef15356b6f6bcf97de): Order B reset-leg registration writes truthy order_b_causes independently of parent-stop cause set; parent-stop registration constructs kind, parent label (S/E number or StopAll override), family, exact event and parent source time. Initial geometry materialization converts level, computes crossing and builds First-time buckets. OA48 maps exact parent stop to a main candle time, selects records in that First bucket with confirmation >= stop and non-null crossing event >= stop, projects carried-live and selects stable minimum (cross event, reaction First time), default None. OA61 compares that winner's confirmation, not crossing, to zone Order First. OA48 does not independently require crossing > confirmation or reset absence. The gate lookup can populate caches; no new cause registration in OA60/61.
- engine/pipeline/e_zone_detector.py [[220,242],[380,389],[416,417],[608,675],[677,733]] (blob 240369edf3352006082efe094eb68ac027d6689f): Constructor uses supplied truthy initial ledger else empty dict; _main_index delegates chronology main_index clamp=True. Live reconciliation dependency signature includes physical ledger presence, initial membership, B truthiness, frozen causes and gate veto, so OA61 can execute before full reconciliation. _zone computes inherited/gate/carried, registers parent, merges all eligible route streams by crossing and negative First, computes prospective source from stop through max(stop,cross), then invokes OA60 with int reaction First/Break, supplied owned source set (explicit empty set respected) or accepted E source-time projection, and prospective source slot 1. True continues choice race, first False is selected subject to other caller rules; no match returns None. The local gate_owned computed at line 620 is not subsequently used in _zone selection, but evaluation may affect cache/exception timing. Native _build_zone stores exact parent stop event, mapped order First candle timestamp and supplied use labels; these are OA61 inputs, not synonymous with parent-stop creation cause.
- engine/pipeline/e_zone_detector.py [[940,978],[995,1029],[1159,1159],[1220,1227],[1294,1324],[1448,1448]] (blob 240369edf3352006082efe094eb68ac027d6689f): Root restoration skips a parent already dominated; OA60 True triggers full _zone replacement race with dominant source-time projection and root source, enqueues unseen replacement and continues (original root not retained on this route). Distinct _invalid_s_without_order_cause checks invalid root identities and alternative creator; it is not OA60's complement. Reconciliation valid_order rejects OA60 first, then OA61, then invalid-S-without-cause; eligibility also requires parent_active. Reopening loop tests OA60 and parent_active, finds parent, can raise _ReopenedERace for checkpointed reconciliation, otherwise enqueues renewed race with accepted_source_times. Source-time set initialized from numbered E and grows on acceptance; not full source index/time identity. Cross-owner reconciliation and final selection are owned by E, not these local predicates.
- engine/pipeline/order_audit_engine.py [[2050,2072]] (blob 6ddb93ba097ef137af2405ef15356b6f6bcf97de): Adjacent accepted-ledger reconstruction has a distinct parent-stop cause filter, projects invalid S and accepted E source times, and prunes causes; OA60 is a read predicate, not this pruning operation. OA62/63 forensic closure belongs to CP404; this range is read only as a boundary dependency.

## Verification

84 category rows: 25 W1, 59 additional; 3 historical supplements. Branches 7, comparisons 10, arithmetic 2, calls 6, accesses 52, effects 3, exits 4. All 6362 prior rows (1460 W1, 4902 additional), 119 supplements and 1892 CP316 links reconciled; exact disjoint local union 6446/8318. Historical and canonical seven-category arrays and AST nodes match exactly. No current filter IDs; prior filter suffix mapping retained. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP403_W3_B05_Disowned_S_And_Gate_Owned_Order_Eligibility_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP403_Completion.json).

- Source-first local review by GPT, not independently staffed. OA60 and OA61 are exclusion predicates, not positive validity certificates; all caller ownership and runtime behavior are conditional on coherent ledgers, geometry and caller input state. No cross-owner acceptance or runtime equivalence asserted.
- Native collection truthiness, membership, indexing, comparison and iteration are not universal guarantees for dynamically supplied malformed objects; no local recovery or normalization. The source does not prove malformed values occur in production. No price rounding or trading-direction change introduced.
- No RAW payload, runtime, ZIP, production changes, performance measurements, fresh AST generator, or independent SHA-256 claim. Pinned old/current canonical AST arrays, CP316, historical W1 crosswalk and prior registers were directly reconciled.
