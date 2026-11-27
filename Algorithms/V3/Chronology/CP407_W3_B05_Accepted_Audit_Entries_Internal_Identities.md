# CP407 — Independent local accepted audit entries and internal identities

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA72–OA74 lines 2462–2516. B05-24. Source-only; no algorithm execution.

## OA72-A — lines 2462–2470

The helper receives an entry mapping and an accepted-source collection; returns a row mapping or None. Its E-facing purpose is to select one accepted A cause for the physical row while preserving all accepted causes for later use. The annotation is not a runtime shape check. It does not derive acceptance, physical identity, geometry, price or stop chronology.

## OA72-B — lines 2471–2473

Read a_causes via get, test native truthiness, and use that value unchanged if truthy; otherwise create a singleton list with a pair from required a_source_time and a_stop_event_time keys in that order. Missing, None, empty list/tuple or other falsey a_causes triggers fallback, not suppression. The fallback keys must exist even when accepted_sources is empty; malformed mapping or failing access propagates. Truthy iterable may be one-shot; no normalization, copy, sort or validation before traversal.

## OA72-C — lines 2474–2478

Eagerly build a fresh accepted list. Unpack each cause into exactly two elements, source time then stop time, before testing native membership of source time in accepted_sources. Selected elements are fresh two-element tuples holding original value references. Preserve iteration order and multiplicity, including repeated identical pairs and multiple stops for one source. No source-index, stop-time, null, ordering or chronological eligibility test; None may pass if membership allows. Empty accepted collection filters all well-formed causes; malformed arity/iterability still fails before membership, and unhashable source against a set or non-container accepted_sources may raise. No None-as-unrestricted sentinel (unlike optional filter OA67/OA68).

## OA72-D — lines 2479–2481

If accepted list is empty, return None without equality checks or copying. Otherwise select element zero, i.e. first surviving cause in traversal order. No min, sort, earliest stop/source-time test, or chronological tie-breaker; equal timestamps and equal pairs do not select by index or other ranking. Producer ordering controls the choice and is not independently validated.

## OA72-E — lines 2482–2487

Evaluate three conditions in exact short-circuit order: selected source equals entry.get(a_source_time); selected stop equals entry.get(a_stop_event_time); accepted list equals list(causes). Native get default is None, equality not identity, no normalization; last comparison materializes the original chosen iterable again only if first two succeeded. Return the exact input object if all true, not a shallow or deep copy. For a fallback singleton matching both original fields this may preserve missing or falsey a_causes as-is; it does not force materialization of that field. An original non-list iterable may also be retained if its list projection compares equal. One-shot iterators may have been consumed already, so this optimization is conditional on reiterability and native equality. Missing selected fields can compare equal to None for a truthy input iterable. Equality/iteration/get errors propagate.

## OA72-F — lines 2488–2494

Otherwise create a shallow dict from entry, then overwrite a_source_time with selected source, a_stop_event_time with selected stop and a_causes with the fresh accepted list, in that exact sequence. Return adjusted mapping. Other fields, including reaction, geometry, confirmation, stop level/index/time, stop_cross and nested objects, retain their original values/references; no Decimal conversion, deep copy, crossing recomputation, ledger publication or renumbering. Input row is not explicitly modified. External custom iterators/mappings can have side effects and exceptions are uncaught; no rollback of such effects. Original-row path and adjusted-row path have distinct aliasing.

## OA73-A — lines 2495–2502

Create a fresh output mapping by native items traversal of the supplied physical ledger in its iteration order. Unpack key/entry; original mapping keys are the output keys, without reaction-identity validation, int conversion, new normalization or cross-check. Empty input yields empty mapping. The dict annotation does not enforce key type; no sort or geometry access.

## OA73-B — lines 2503–2507

For each entry evaluate accepted_audit_entry exactly once by constructing the singleton iteration value and binding its result. Retain the result only when it is not None, rather than testing truthiness; insert the same returned row object under original key. Normal dict traversal preserves surviving key order and input mapping remains unmodified; no deep copy or mutation of accepted entry by this wrapper. Exceptions during inner helper, input iteration or key insertion propagate; no completed output returned if comprehension fails, and any external iteration side effects are not rolled back. No merge or dedup across different original keys; native dict insertion/equality semantics govern any custom repeated keys.

## OA74-A — lines 2508–2513

Read order_first_index and order_break_index via getattr with default None, First then Break, before testing either. Exact None guard returns False if either is None; zero and other falsey non-None values are not rejected. Even missing First does not avoid reading Break; attribute lookup errors other than defaultable AttributeError can propagate. None guard bypasses int conversion and membership.

## OA74-B — lines 2514–2516

For both present fields invoke canonical order_identity, which converts First then Break using int, and test membership of the resulting pair in supplied internal_identities. No conversion/normalization of the supplied membership collection, bounds/price/chronology/Reaction validation, direction selection, ownership check or mutation. Native membership equality/hash applies; malformed indexes or non-container/invalid membership protocol may raise; int conversions can collapse distinct raw representations. Return native membership boolean. The helper is an internal-identity query only, not a cause filter or authority to discard accepted provenance.

## Consumer boundaries

- `engine/pipeline/core_utils.py` (51–66): Physical identity helper returns int(First), int(Break) in order; reaction identity similarly converts stored attributes. OA74 uses this provider but never normalizes the internal collection. Decimal normalizer exists but OA72–74 do not invoke it or change prices.
- `engine/pipeline/order_audit_engine.py` (1539–1558, 2131–2142, 2309–2328, 2622–2654): Stopped-A audit producer derives normalized Reaction identity, stores first geometry/confirmation/stop and selected A fields in a new row when absent, then appends unique (source,stop) pairs in encounter order by native equality. OA72 first accepted order follows that list, not a time-sort. Initial records consumer traverses values, normalizes price in its own stage and calls crossing, then sorts by First, confirmation and integer indexes. Accepted rebuild uses initial entry causes/fallback but explicitly skips None source or stop, unlike OA72. OA67 also uses accepted-source membership but with optional None filter; not identical to OA72.
- `engine/pipeline/s_zone_detector.py` (78–119, 178–189, 201–207, 217–233, 1254–1256): S detector validates direction/range, sorts A by reaction_break_time then int source_index, initializes its physical ledger and invokes stopped-A audit in that A order after clearing ledger. Delegated reaction confirmation and A strict-stop finder govern producer chronology; OA72 does not infer a chronological minimum from it. Sorting source A by reaction-break time does not prove all appended stop times ascending.
- `engine/pipeline/lifecycle_engine.py` (17–20, 606–658, 660–692): Resolve Order context directly imports and calls OA72 once per original input entry via a comprehension, retaining non-None results under original keys. Starts a fresh inherited blocked-First set, adds provisional invalid-leg-head blocks, derives accepted initial First times from retained reaction.first_time (str values parsed by exact format), removes those from blocked set. Distinct conditional E-stop exceptions are derived and optionally emitted, not global unblocking. Returns accepted ledger and blocked times. Native failures can propagate; OA72 does not perform those subsequent lifecycle decisions.
- `engine/bridge/trading_pipeline.py` (2190–2208, 2284–2309, 2409–2438, 2439–2473, 3040–3050): Initial bridge acceptance derives source-time set from S eligible A, calls OA73 on S ledger, passes results as initial_order_audit into E detector. Later source-time set excludes invalid (source_time,int source_index) A pairs, passes to Lifecycle resolve_order_context; resulting accepted_orders/blocked times and distinct E exceptions feed final E detector. Shared reconciliation consumes accepted_orders and E ledger values; presentation A sources separately derived without clipping history. These call sites do not invoke OA74 directly. Time-only projection can collapse distinct source indexes, so OA72 membership does not prove full pair-level validity.
- `engine/pipeline/e_zone_detector.py` (382–389, 1008–1026): E detector retains truthy initial ledger mapping or substitutes a fresh empty mapping; references of its rows may be shared. Invalid-S root exclusion checks raw behavior physical pair against initial ledger before own B and parent causes; no call to OA74 in these inspected paths. Distinguish initial-order presence from internal identity membership.

## Exact structural reconciliation

Seven-category counts: branches 11, comparisons 8, arithmetic 2, calls 10, accesses 101, effects 7, exits 6. 145 total (31 W1, 114 Additional), 4 separate historical supplements. All 7645 prior rows (1754 W1, 5891 Additional) and 141 prior supplements revalidated; exact disjoint local union 7790/8318; 528 later rows. All 1892 CP316 links reconciled. Two filter IDs resolved: 2477:11:Compare:filter => AST 10048, branch row 516; 2504:11:Compare:filter => AST 10158, branch row 522. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP407_W3_B05_Accepted_Audit_Entries_Internal_Identities_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP407_Completion.json).

- Source-first local review by GPT, not independently staffed. OA72 consumes a caller-defined accepted-source collection; first surviving pair is iteration-order selection, not minimum event time, and source-time membership is not full A identity acceptance. Native container/attribute/equality and malformed input paths remain conditional.
- OA72 return can alias the original row or a shallow adjusted row; OA73 retains returned references under original keys. Reiterability is not validated; a one-shot iterable may be consumed. No global proof that all physical key/geometry pairs agree, no new cross-owner acceptance, runtime equality, or production defect asserted.
- No RAW payload, runtime, ZIP, production changes, performance measurements, fresh AST generator, or independent SHA-256 claim. Git blob identities and full recursive tree/readback are publication evidence.
