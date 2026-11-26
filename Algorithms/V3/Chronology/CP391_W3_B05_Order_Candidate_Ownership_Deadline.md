# CP391 — Independent local Order candidate ownership and deadline review

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 921–1088. B05-08, OA21–OA24. Source-only, no execution.

## OA21-A — lines 921–932

Required keyword-only exact parent stop cause event. Resolve canonical stop triple from number and reaction, then crossing from supplied confirmation and unchanged Decimal level. Both calls precede identity calculation or existing match lookup, even for a losing duplicate; any exception propagates, earlier cache effects may survive.

## OA21-B — lines 933–945

Compute physical pair as integer First/Break via reaction_identity, then construct nine-slot match in order: number, reaction reference, confirmation, stop level, source index, source timestamp, crossing tuple or None, singleton parent-stop label tuple, exact parent stop cause event. Lookup current value by physical identity.

## OA21-C — lines 946–952

Absent or None existing value short-circuits rank evaluation. Otherwise compare lexicographic (confirmation, integer First, integer Break) strictly less, constructing full left tuple then right tuple. Replace whole record, not merge label sets; equal or later leaves original. Dictionary assignment to existing key retains insertion position. Return dictionary value by same identity; no copy.

## OA22-A — lines 955–963

Materialize parent-stop-labelled values in mapping iteration order; zero or one means immediate return without mutation. Not a guarantee at least one exists.

## OA22-B — lines 964–971

Minimum key is confirmation, integer First, integer Break; first equal key wins by traversal order. Derive winning physical identity from winning reaction reference, rather than selecting a cause timestamp.

## OA22-C — lines 972–979

Iterate shallow snapshot of dictionary items. Winner identity short-circuits label check; non-parent entries unchanged. Remove every parent-stop occurrence from losing labels, preserving order and duplicates of all other causes. If any remain, retain first seven fields, replace cause tuple, set parent cause event None. Else delete key. Mutates supplied map in sequence, no rollback if a later error. Identity consistency assumes keys match geometry.

## OA23-A — lines 982–1000

Five-field native tuple key ordered start, deadline, bounded, trend-leg, E flags; defaults None/false as declared. Cache get non-null includes empty tuple. Return new shallow list on hit, no geometry/callback revalidation; nested reaction references shared. Key omits run-specific state and assumes owner lifetime/invalidation.

## OA23-B — lines 1002–1011

Miss creates new insertion-ordered identity map. Direct OA19 called first with start/deadline/bounded/E (threshold defaults None). Only non-null result unpacked to OA21 with exact start as parent cause; no pre-filter by crossing or deadline.

## OA23-C — lines 1013–1020

If truthy trend-leg flag, resolve OA17(start); non-null tuple merges through same OA21 with exact start. Independent of whether direct candidate exists. Direct precedes trend merge, so equal rank retains direct.

## OA23-D — lines 1024–1029

Walk reset-leg input order; resolve physical reaction then First main time; reject First <= start (including equal). Only surviving leg computes identity and map lookup. No confirmation threshold at this step.

## OA23-E — lines 1030–1036

Existing non-null identity preserves first seven tuple fields and prior parent cause time, appends reset-leg to existing labels then deduplicates all labels by insertion order. No leg stop/cross call or use of new leg number/confirmation; continue, even if current prior crossing None.

## OA23-F — lines 1037–1045

New identity: resolve stop from leg number and physical reaction; use supplied leg confirmation, exact stop/source fields, crossing at leg confirmation with unchanged level, singleton reset-leg labels and None parent cause. Assignment only after tuple successfully evaluated; first encountered identity owns geometry absent later OA22 stripping.

## OA23-G — lines 1047–1057

Enforce parent-stop uniqueness before extracting stop evidence. Include only non-null crossing tuples and use exact lower event slot 2. Deadline is minimum surviving event or range_end if none; optional non-null continuous deadline clamps by min. No unconditional range_end cap when crossings exist, no prefilter by confirmation before deadline construction.

## OA23-H — lines 1058–1068

Keep all records with confirmation <= computed deadline, including equality and open crossing. Stable ascending sort key is exact crossing event if present else range_end, then reaction First main time. Key computed for each eligible element; no Break/number/cause third tie, so dictionary insertion order resolves equality. Crossing may lie after supplied deadline; filter tests confirmation only.

## OA23-I — lines 1069–1070

Cache tuple of sorted result only after complete successful generation; return original fresh list. Later list mutation does not alter tuple structure, but nested references shared. No outer rollback of delegated cache effects on failure.

## OA24-A — lines 1073–1085

Call OA23 with start, deadline and named bounded/trend flags; E argument omitted so false default. Materialize list filtered by crossing slot is not None, preserving sorted order; no new stop search, confirmation or crossing deadline check.

## OA24-B — lines 1086–1088

Return first filtered match if list truthy, else None; no additional tie-break, ownership reassignment or conversion.

## Consumer boundaries

- engine/pipeline/core_utils.py:59–66; order_audit_engine.py:653–688,1459–1477: Identity integer First/Break only, not confirmation, direction or cause. Direction is owner-local. Stop delegates canonical chronology, exact-object number cache; crossing uses unchanged Decimal level and half-open lower search [max(confirmation,range_start),range_end), strict directional comparator, with result cache. No local rounding in OA21–OA24.
- engine/pipeline/order_audit_engine.py:809–827,764–806; e_zone_detector.py:393–417,533–566: OA19 caches exact tuple or None; OA17 uses sorted trend-position cache including None; E sequence reset setter clears candidate/direct/carried/post-stop caches, not all other caches. E live override uses dirty-time and continuation search; run-local cache freshness, callback stability, exact lower chronology and physical input immutability remain conditional.
- engine/pipeline/order_audit_engine.py:1337–1379: Registration checks S root eligibility and hard reset first, calls OA23 with parent-specific flags then separately requests OA19 and appends direct match only if absent by physical identity. No repeat OA22/decision-deadline after supplement. Thus local at-most-one parent-stop candidate does not certify accepted ledger cardinality or downstream registration; separate source review needed.
- engine/pipeline/order_audit_engine.py:1134–1165: Accepted reset-leg registration separately invalidates carried caches and writes physical audit ledger/confirmation index; OA23 temporary candidate map is not that ledger. Its cause labels are not full accepted provenance records.

## Verification

421 category rows, 93 prior W1, 328 additional; seven supplements; 2646 prior rows revalidated without overlap. Local scoped acceptance only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP391_W3_B05_Order_Candidate_Ownership_Deadline_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP391_Completion.json).
