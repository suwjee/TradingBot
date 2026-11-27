# CP406 — Independent local prepared Order audit and parent ownership

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA66–OA71 lines 2291–2461. B05-23. Source-only; no algorithm execution.

## OA66-A — lines 2291–2299

Return a four-element tuple of mapping get results in exact order: parentType, parentFamily, eventTime, parentSourceTime. Each absent key gives None with a native dict; an explicitly stored None is equivalent for this key. No kind, source index, reaction identity, conversion, normalization, or validation. Tuple construction alone does not require hashable contents; later owner-map use does. Missing fields can collapse distinct malformed causes into the same key; unhashable components or failing get can raise. Native equality and hash apply.

## OA67-A — lines 2300–2308

Allocate fresh combined list; only s_detector is None returns it immediately. Falsey non-None detector is still dereferenced. Traverse order_audit.values in native mapping insertion order; original ledger keys are not used to establish identity here.

## OA67-B — lines 2309–2316

Read entry.get(a_causes) and test truthiness. A truthy value is used as supplied; otherwise create one fallback pair by required key access a_source_time then a_stop_event_time. No missing-key guard or non-null validation. If accepted_a_sources is not None, construct a fresh list retaining causes with slot 0 in that supplied collection; no conversion, source index or timestamp equality tolerance. Empty native accepted set excludes all well-formed causes; malformed indexing or membership may raise before filtering completes. A falsey explicit a_causes collection does not suppress the fallback.

## OA67-C — lines 2317–2331

Skip if resulting a_causes falsey. Otherwise iterate in supplied order, unpack each cause into exactly two values source_time and stop_time; build fresh parent-stop dictionaries with literal parentType A and parentFamily None, eventTime=stop_time, parentSourceTime=source_time. No null-pair rejection, deduplication, sorting, or stop validation. Append original entry reference with fresh cause list only after comprehension completes; a truthy empty iterator can yield an empty appended list when no filter materializes it. Return accumulated list; malformed pair or key access propagates without local recovery.

## OA68-A — lines 2332–2347

Required detector (no None guard); optional accepted A set defaults None. Traverse detector.order_audit.values in mapping order. For each row access required causes, sort entire collection by native str before filtering; stable sort preserves iteration order for equal string keys, which does not establish a universal deterministic tie order for unordered input. Construct fresh parent-stop dicts from tuple positions 1 through 4, preserving raw label, family, event and source; no new StopAll label or source-time normalization. Missing causes key, noniterable or failing str can raise.

## OA68-B — lines 2348–2354

First require slot 0 exactly parent-stop; then exclude only if slot 1 exactly A, accepted_a_sources is not None, and slot 4 absent from that collection. Short-circuit order matters: a non-parent kind needs no later slot access, non-A skips A membership but selected dict still reads all four slots. No S/E/StopAll acceptance filter or cause-length/type guard; extra positions ignored, short parent tuples may raise, explicit None fields otherwise preserved. Filtering is by source time alone; it does not prove upstream acceptance.

## OA68-C — lines 2355–2360

Extend freshly constructed parent list with entry.get(order_b_causes, empty tuple) in supplied iterable order. Missing B key defaults empty, explicit None can raise; no B type/kind filter, deduplication, deep copy, or A-source filter. B dictionaries/objects retained by reference. Append original entry with the combined list only if truthy, so B-only rows can enter. Return collection in original mapping traversal order.

## OA69-A — lines 2361–2379

Allocate fresh identity map and output list. Iterate supplied entry/cause pairs in sequence order, require reaction key, convert reaction first_idx using int, then canonical order_identity converts First again and Break via int. Identity derives from reaction, not original ledger key. Apply inclusive First window start_index <= First <= end_index; if outside, require exact normalized physical identity membership in supplied required set, with native equality/hash. No Break window check or chronology check; required identities bypass only this window, not cause eligibility or later owner selection. No range normalization or reversed-window rejection; missing/malformed attributes/conversions or comparisons can raise.

## OA69-B — lines 2380–2387

Look up identity in local merge map. Existing non-None prepared row wins entry, reaction and crossed completely; retrieve its cause list and extend with each supplied cause only if not currently equal to an item in the growing list. Generator membership is evaluated as extension proceeds, so duplicates within later list can be suppressed after first append; full native equality, not parent key. Duplicates already in first list survive. No crossing lookup or geometry replacement for later rows. Malformed equality/iteration may fail after some appends.

## OA69-C — lines 2388–2403

For new identity read entry.get(stop_cross), then check key presence independently. Present key, including None or other falsey value, is authoritative and bypasses crossing lookup. Only absent key invokes supplied detector.cross_order with required confirmation_time and stop_level unchanged (even for S entry). No normalization or write-back to original entry by this function; dynamic callee may mutate caches. Build fresh prepared mapping entry/reaction as original aliases, causes as shallow list preserving duplicates and element aliases, crossed as supplied/computed value. Publish into local merge map before appending output; return output in first eligible identity encounter order, with no sort. Failure can propagate after earlier calls/mutations; no rollback.

## OA70-A — lines 2404–2416

Allocate parent_owner and parent_rank maps. First pass over all prepared rows computes rank eagerly for every row, including those with no parent causes: raw entry confirmation_time then int reaction First then int Break. Native lexicographic comparison (no confirmation conversion); incompatible values can fail when compared. No global accepted parent universe, source validation or price comparison; the candidates are only prepared rows surviving collection and window/required filtering.

## OA70-B — lines 2417–2426

For each cause call get(kind); skip unless exactly parent-stop. Derive OA66 key; read prior rank with get. If absent (None) or current rank strictly smaller, publish rank then owner row reference. Equal rank leaves first owner; no kind in key beyond the outer parent guard, no unique source index, no additional tie breaker. Dict keys require hashable components and native equality. Any malformed mapping/access, hash or incompatible comparison can raise; no local catch.

## OA70-C — lines 2427–2435

Second pass over original prepared order. Allocate fresh accepted cause list per item; keep non-parent kinds (including missing kind in native dict) without parent-key checks. Parent-stop retained only when owner map get for exact key is the same item object, not equal row or equal physical identity. Preserve original cause order, duplicates and element references, including all duplicated winner causes. No fallback to a different owner for a malformed or later-dropped row.

## OA70-D — lines 2436–2441

Only if accepted list truthy, replace prepared item's causes field with that fresh list and append the same item reference to deduped output. Omitted rows are not changed by this second pass; retained rows mutate in place, not original entry causes under ordinary prepared schema. If failure later, earlier replacements remain. Return retained rows in input order. Required identity is not exempt from empty cause suppression; no guarantee every requested identity is returned.

## OA71-A — lines 2442–2451

Public preparation accepts detector, inclusive First window, optional s_detector=None, accepted_a_sources=None, required_identities=None. Create a fresh native set from required_identities or a fresh empty set by truthiness. No individual pair normalization; unhashable members or failing truthiness/iteration can raise before collecting. Input accepted A collection passed unchanged to each collector; no independent validation of its authority.

## OA71-B — lines 2452–2461

Eagerly collect S entries first, then E entries, expanding both results into fresh combined list. S precedes E for shared physical identity; S does not always win if excluded/absent. Invoke merge with supplied detector and exact start/end/required set, then return single-owner result directly. No final sorting, serialization, public numbering, or additional validation. A failure at any stage prevents later stages; dynamic provider side effects and partial earlier mutable state not rolled back. Local source contract is direction-invariant except delegated crossing geometry.

## Consumer boundaries

- `engine/pipeline/core_utils.py` (51–66): Canonical order_identity converts First and Break via int; reaction_identity uses the same int pair. OA69 converts First before invoking helper. Decimal normalizer exists but OA69 does not call it on stored price.
- `engine/pipeline/order_audit_engine.py` (1167–1199, 1403–1433, 1459–1484, 2622–2654): Order B provider creates reset-leg dict including string levels and physical identity, dedups by full equality and sorts by postBehaviorStopTime/resetTime/strictBreakTime/physicalOrderIdentity. Parent registration uses raw parent label, E numbering, sequence reset override StopAllN and empty family; OA68 projects stored tuple without relabelling. S provider first stores reaction, confirmation, stop geometry, first A source/stop and a_causes then appends unique source/stop pair. Public cross_order delegates _cross_order; base cache key start/level includes cached None, strict lower search with left=max(start,range_start), right exclusive range_end and direction less unless bearish.
- `engine/pipeline/e_zone_detector.py` (537–557): E override delegates base when live continuation None; otherwise key start/level, cached path calls dirty-time then returns cached value, miss invokes live first_stop with clamped start and direction less flag, maps event to index/time and caches result including None. OA69's missing-key crossing path cannot assert uniform base implementation or runtime equivalence.
- `engine/pipeline/lifecycle_engine.py` (19–19): Imports prepare_order_audit from Order audit owner, rather than independently reconstructing the helper.
- `engine/bridge/trading_pipeline.py` (1611–1718, 3040–3050, 3074–3098, 3417–3457, 3485–3499): Visibility derives full-history accepted A source times by excluding invalid source pairs, independently gathers normalized required physical pairs from visible S/E/StopAll with both fields non-None. Calls preparation when full E detector exists, then bridge validates missing referenced identities and duplicate exact parent keys across distinct physical identities (raises; does not choose owner). Serializer consumes prepared row and emits parent-stop/reset-leg branches, not arbitrary retained non-parent kinds. Primary stage prepares both owners over full main index range, refreshes after registration, reconciles primary labels then prepares visible range preserving prior prepared identities as required; later bridge invariant checked again. Required identity exemption does not bypass OA70; accepted A times discard index. These are source-visible boundaries, not guaranteed final coherence.
- `engine/pipeline/PL_PH_detector.py` (645–680): NativePrimaryOrders reads prepared reaction, entry, crossed and cause kinds, recalculates reaction confirmation via chronology, applies gate, non-primary reaction number restriction and direct/reset-leg selection, rejects absent or non-later crossing, creates StructureOrder with Decimal conversion and deep-copied audit causes. This consumer imposes its own eligibility; OA70 rank is not a primary structure acceptance proof.

## Exact structural reconciliation

Seven-category counts: branches 33, comparisons 17, arithmetic 7, calls 41, accesses 399, effects 29, exits 12. 538 total (98 W1, 440 Additional), 7 separate historical supplements. All 7107 prior rows (1656 W1, 5451 Additional) and 134 prior supplements revalidated; exact disjoint local union 7645/8318; 673 later rows. All 1892 CP316 links reconciled. Three filter IDs resolved: 2315:19:Compare:filter => AST 9403, branch row 486; 2348:15:BoolOp:filter => AST 9522, branch row 491; 2385:19:Compare:filter => AST 9702, branch row 501. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP406_W3_B05_Prepared_Order_Audit_Parent_Ownership_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP406_Completion.json).

- Source-first local review by GPT, not independently staffed. Owner selection is limited to collected/window-eligible/required candidates, not a proof of globally accepted parent provenance or every public required identity surviving. Native protocols, malformed values, dynamic dispatch and ordering ties in unordered source collections remain conditional.
- Prepared entries and reactions are aliases; parent dictionaries newly constructed, B elements shared, and later cause-list mutations are not transactional. Missing-key crossing calls may alter detector caches. No new cross-owner acceptance, runtime equality, or production defect asserted.
- No RAW payload, runtime, ZIP, production changes, performance measurements, fresh AST generator, or independent SHA-256 claim. Git blob identities and full recursive tree/readback are publication evidence.
