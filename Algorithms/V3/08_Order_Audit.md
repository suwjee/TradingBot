# Order audit — canonical ledger, reuse and accepted provenance (V3)

**Conventions:** B = bullish, R = bearish. Parent directional extreme is Low for B and High for R; strict parent stop/improvement means lower for B and higher for R. An opposite Order has its own direction and strict predicate, not the parent predicate. Use Decimal normalization and native arithmetic order; preserve source/main versus exact-event times, physical identity, original order, and nulls. Use [record interfaces](../../Contracts/Declared_Record_Schemas.md) and [chronology/index services](20_Indexes_And_Caching.md). Procedure labels name semantic operations, not required implementation symbols.


## OL-M01 — State model

One direction's ledger is keyed by physical opposite (First index,Break index). Entry retains canonical reaction/number/confirmation, stop level/source, strict crossing triple or null, set of parent-stop tuples and separate reset-leg dictionaries. Parent-stop tuple identity includes label/family/exact stop/source. Initial A audit uses A source/stop pairs. Order_A and Order_B are independent creation routes; carried-live and accepted-live are consumption labels only. Geometry-only evidence cannot create except explicit S-side independent A route. Never assign consumption parent as creation parent. Initialize caches and confirmation-sorted index, track actual ledger changes; mutable ledger and derived indexes are owned by detector.

## OL-M02 — Candidate availability

| Candidate path | Gates |
|---|---|
| Direct parent-stop | [Order A](06_Order_A.md), canonical owner and strict stop |
| Reset-leg | [Order B](07_Order_B.md), accepted exact reset provenance |
| Unconsumed S Blue Order | S Blue with Order confirmation/stop, actual crossing >= new parent stop, copy its physical geometry |
| Gate-owned initial A | First main exactly gate, confirmation >= parent stop and stop >= parent stop; earliest crossing then First |
| Carried accepted Order | Creation strictly in (parent lifecycle decision,parent stop); own confirmation <= parent stop; strict crossing >= parent stop. Initial A uses First in inclusive lifecycle..stop as separate eligibility path |
| Post-stop accepted | Confirmation > parent stop and crossing > both; no sequence reset in (parent stop,cross]; deduplicate physical identity |

Carried creation event from earliest parent-stop cause (when multiple) plus every reset-leg physical confirmation. Sort carried crossing then later First. Post-stop fallback materializes and sorts, optimized native stream merges initial and ledger runs, same crossing/confirmation tie keeps later First and initial exact tie. Validate exact native types/timezone, finite Decimal level and crossing shape under local context; invalid/unverifiable data falls back to legacy scan. Never use speculative cache results as accepted evidence. Scope/key and invalidation details below.

## OL-M03 — Rebuild and primary reparenting

Rebuild from actual accepted E plus accepted S roots, retained initial A causes and reset legs; filter S parent cause when invalid or occupied by E. Preserve valid historical physical entries even if unused by current E; retain independently valid causes, do not synthesize an Order without cause. Reconstructed E-consumed geometry may use recorded Order fields if canonical identity missing; only create ledger row if valid recovered/explicit parent causes exist. Ensure audit preserves prior independently valid B/history entries. Register primary PH on bearish owner / PL on bullish owner only. Find first strict stop strictly after decision; require direct physical Order confirmation > stop. Reparent same-source obsolete StopAll cause only when exact stop matches and after primary decision; transfer to direct identity, revoke other matching cause, remove identity only if no parent/reset cause left. Relabel B stop and anchor provenance with exact source/stop and anchor First gates; reconcile finalized primary labels without changing identity or prices.

## OL-M04 — Public audit preparation and invariants

Collect accepted S/A ledger (filter accepted A set) then E ledger; preserve first geometry for physical identity and append distinct causes. Retain First within visible inclusive range OR explicitly required identity from visible S/E/StopAll. Keep one physical owner per exact parent-stop tuple: earliest confirmation,First,Break. Remove owner-losing causes only, drop entry only when no causes. Final bridge invariant requires every displayed S/E/StopAll with both physical indexes reference retained identity, and one exact parent-stop cannot name multiple identities. Audit export sorts First time,Break time. Exact stop, main owner and optional nulls remain intact. Invalidity/visibility ownership is [Lifecycle](10_Lifecycle.md), not ledger geometry.

## Detailed ledger procedures

### OA01 — relabel_primary_causes
Deep-copy each input cause; for parentType/postBehaviorType/anchorBehaviorType paired with corresponding source-time key, string-convert the current label (default empty) and test PH/PL prefix first; only then read associated source (default null) and test membership in labels before replacement. Retain first equal dict, preserve order; no original mutation.

### OA13 — OrderAuditEngineMixin._initialize_order_audit
Initialize empty cross/canonical stop, candidate/carried/post-stop/direct caches, empty ledger and confirmation index, pending list, lazy initial records/indexes null or empty. Materialize trend/opposite First times and confirmations via owner callbacks. Stable trend confirmation sort, times list. Group opposite reset times by int from First in input order; opposite-by-First dictionary last wins. Physical identity-to-canonical position first wins with setdefault. Fresh containers replace prior named values: initial record cache, initial First/confirmation times and by-First index are null; initial confirmation records empty tuple; ledger confirmation index and pending empty lists, sorted audit null, trend-leg positions empty dict. Four separate callback passes preserve input order, First times from main index and exact confirmations from chronology using trend/Order directions respectively. Only trend triples are stable-sorted by confirmation alone after ordinary zip (shortest-input termination); opposite arrays are not sorted locally. Reset grouping retains all returned times in supplied order; E owner sorts opposite resets beforehand. Physical identity is int First/Break, first duplicate wins; by-First last duplicate wins. No local validation of alignment/sortedness, no Order creation.

### OA25 — _has_sequence_reset_between
Upper bound start in sorted reset times; true next exists and <=end, interval (start,end].

### OA26 — _index_order_audit_identity
Insert (confirmation,First,Break) right of equal into confirmation index. If sorted audit is dict append pending; otherwise reset sorted audit null.

### OA27 — _clear_order_audit
Clear authoritative ledger and confirmation index; invalidate carried and post-stop caches.

### OA28 — _invalidate_carried_order_caches
Clear carried results; set creation index and pending append null. Does not invalidate post-stop results.

### OA29 — _invalidate_post_stop_order_cache
Clear post-stop result cache, null sorted audit and clear pending.

### OA31 — _reparent_primary_high_causes
Label kind+number and source identity. For each ledger parent-stop cause replacing StopAll role, require same parent source time, non-null equal stop and stop>primary decision. Keep replacement only on direct physical identity, family empty; other matching roles revoked. B causes: relabel postBehavior StopAll when exact source and stop match and stop>decision; relabel anchor StopAll on exact source when reset identity exists and its First main time>=decision. Delete entries with neither parent nor B causes; remove indexes of revoked identities and invalidate post-stop. Invalidate carried if changes/revocations. Historical sequence reset map not removed.

### OA32 — register_primary_high
Only bearish owner and parent.kind PH; otherwise ValueError. OA36.

### OA33 — register_primary_low
Only bullish owner and kind PL; otherwise ValueError. OA36.

### OA34 — _primary_parent_order
Search lower (decision,range_end) using first_cross_position, less iff bullish owner. If stop found call OA19 with stop,null,false, confirmation_after=stop; return stop,direct (null possible).

### OA35 — primary_order_dependency
OA34; no direct => stop,null. Else stop,repr(direct),str(level),source index/time,cross of confirmation and stop level.

### OA36 — _register_primary_point
OA34 then OA31 even when no direct (direct identity null). Null direct => null. Else ensure physical ledger row with stop/cross and empty cause set/index if new. Add cause (parent-stop,kind+number,empty family,exact stop,source time) if absent; invalidate carried; return identity.

### OA37 — reconcile_primary_high_labels
OA39 with PH.

### OA38 — reconcile_primary_low_labels
OA39 with PL.

### OA39 — _reconcile_primary_labels
Map source to prefix+number (last duplicate wins). For each ledger cause tuple relabel only prefix-matching label at known source; B causes OA01; update only changed collections, invalidate carried if changed.

### OA44 — _unconsumed_s_orders
Require S color exact blue, non-null order confirmation/stop level. Crossing exists and >=parent_stop. Construct SimpleNamespace from parent's Order mode/First/Break/box top/bottom and their source indexes; return singleton match with parent Order number/source/confirmation/level/cross, carried-live label and null parent creation time. Otherwise empty.

## Reuse and indexing

### OA45 — _initial_order_records
Lazy materialize initial audit values as (First time,confirmation,int number,reaction,Decimal stop,int source,source time,cross). Sort by First,confirmation,First index,Break index. Cache tuple and First times, group records by First as tuples, separate confirmation-sorted view by confirmation,First time,First index,Break; return same tuple.

### OA46 — _initial_record_match
Convert record to OrderMatch dropping First time; supplied causes, null parent cause time.

### OA47 — _initial_order_match
Convert entry to OrderMatch, normalize number/level/source index, calculate crossing, supplied causes and null parent cause time.

### OA48 — _gate_owned_initial_order
Initial records at gate main First; confirmation>=parent stop, crossing exists and >=parent stop. Convert carried-live; min crossing,First time or null.

### OA49 — _carried_creation_events
Earliest parent-stop cause event only if >1 (single preserved), plus every B physical confirmation. No dedup here.

### OA50 — _validated_carried_creation_index
Under local Decimal context validate native rows (exact dict; allowed cause containers, nonempty exact tuples, B exact dicts). No creation => skip. Exact datetime values and same tzinfo object for creation,confirmation,source time,cross dates; non-null crossing exact tuple length>=3 and int index. Exact int reaction number/source/First/Break; stop level exact Decimal,str,int,float and normalized finite. Build sorted unique creation events per row with original ordinal. Return events,tzinfo; any validation failure or exception => null, preserving caller Decimal flags/traps and legacy evaluation fallback.

### OA51 — _extend_carried_creation_index
Consume pending append (set null immediately). Require matching ledger identity and expected size. Validate appended rows OA50; compatible tzinfo if both have events; if old empty adopt new timezone. Insert new events with ordinal offset using insort_right; extend entries. Return ledger,entries,(events,timezone) or null.

### OA52 — _carried_orders_for_parent
Null lifecycle decision => empty. Cache key decision,parent_stop; copy on hit. If creation index missing or cache empty, try OA51 else materialize ledger values with OA50. Use native index only when query datetimes exact and tzinfo identity matches: events strictly between lifecycle start and parent stop; dedup ordinals sorted insertion order. Else legacy scan OA49 per entry. Require creation event in strict interval (when not indexed), confirmation<=parent_stop, crossing non-null and >=parent_stop. Convert matches carried-live. Add initial records with First in inclusive [lifecycle_start,parent_stop] and same confirmation/cross conditions. Sort crossing, negative First index (later First wins ties); cache tuple.

### OA53 — _post_stop_accepted_orders_for_parent
Ignore parent. Cache key parent_stop and confirmation-index length. First initial records confirmation strictly after parent stop, add OA54; then ledger index entries after (parent_stop,2^63-1,2^63-1). Skip missing entry/reaction, non-datetime confirmation or missing level/source fields. If crossed not tuple len>=3 with datetime event recompute cross. Normalize and add accepted-live. Sort identity winners (cross event,confirmation,-First index), cache list, return copy.

### OA54 — _post_stop_accepted_orders_for_parent.add_match
Reject null cross or cross<=parent_stop or <=own confirmation or sequence reset in (parent_stop,cross]. Per identity replace only strictly earlier (cross,confirmation,First index). Insertion order retained.

### OA55 — _iter_post_stop_accepted_orders
Lazy merge with fallback to OA53 for non-native query or data. Key (cross,confirmation,-First). Validate initial geometry eagerly under local Decimal context, sorted crossed after confirmation; conflicting events for same identity invalidate optimized stream. Persist initial view and times/geometry or false. For audit build/append from confirmation index or pending; exact native times/ints/dict/price types, normalized finite price and matching indexed confirmation required; null crossing must have known-null cache; include only cross>confirmation; conflicting initial identity event pair triggers fallback. Sort new audit rows by key+First+Break, merge equal bit_length tiers into immutable runs, clear pending; exceptions mark audit false. Determine first sequence reset strictly after parent stop. Return OA59 generator, using OA58 for eligibility. Initial materialization before audit maintains eager exception precedence.

### OA56 — _iter_post_stop_accepted_orders.native_time
Exact datetime type and tzinfo same object as range_start.

### OA57 — _iter_post_stop_accepted_orders.native_match
Exact ints number/source/First/Break; native confirmation/source time; exact finite Decimal level; cross null or exact tuple len>=3 with int index and native main/exact time.

### OA58 — _iter_post_stop_accepted_orders.eligible
Start upper_bound cross times parent_stop; unwrap audit row if flagged; stop iteration at cross>=first reset; yield only confirmation>parent_stop. Preserves row form.

### OA59 — _iter_post_stop_accepted_orders.accepted
Merge eligible audit runs by full audit key, extract matches; merge eligible initial and audit by main key; yield first per physical identity, initial wins equal merge key.

### OA60 — _order_created_only_by_disowned_s
False if entry missing, no parent causes, B causes exist or initial ledger identity. Else true only if every cause parent-stop S, len>4, source in disowned source times or equals prospective source.

### OA61 — _blocked_by_gate_owned_order
Require parent-stop cause label in E; gate-owned initial OA48 at E parent stop; block if exists and its confirmation<zone Order First time.

## Accepted ledger reconstruction and export

### OA62 — _rebuild_accepted_order_audit
Set accepted E physical source identities. Invalid S times = explicit invalid roots plus accepted E occupied sources. Snapshot previous ledger with parent causes filtered OA63; clear ledger/index/caches; register B legs. For all S and numbered E (StopAll label where sequence reset source) resolve parent stop and OA40 register if stop. For each numbered E whose physical Order absent: find canonical opposite by First, require matching Break else SimpleNamespace with Order geometry, internal false. Recover valid prior parent-stop causes; initial A audit causes (skip null source/stop); if none and carried-live with S parent, find exact S across original+supplemental matching parent source/index and Order identity and recover A creation. If explicit Order parent cause time non-null, add parent-stop using E parent number if found or StopAll override, family empty at reset otherwise zone family, zone parent stop event/source. Filter OA63; skip if none. Compute exact cross, insert reconstructed ledger row/index. Finally preserve all previous valid parent-stop physical identities even not consumed by final E: merge causes into existing or restore prior entry with causes and index. Return numbered sorted source time,index.

### OA63 — _rebuild_accepted_order_audit.valid_parent_stop_cause
Require nonempty parent-stop cause. Reject S len>4 and source time invalid/occupied; otherwise valid.

### OA64 — rebuild_accepted_order_audit
OA62 with copy of zones and supplemental S.

### OA65 — ensure_accepted_order_audit
Snapshot prior ledger with copied cause sets; OA62 on supplied zones. Invalid S source times from invalid roots union new accepted E identities. For prior identities absent in rebuild filter S causes at those times; skip if no causes and no B causes. Restore row and confirmation index. Invalidate carried, return rebuilt zones. Preserves pre-existing StopAll/history orders.

### OA66 — _parent_stop_cause_key
Tuple parentType,parentFamily,eventTime,parentSourceTime via get.

### OA67 — _collect_s_ledger_entries
Null detector => empty. Per S ledger entry use a_causes or fallback source/stop pair; optional accepted A filter; skip empty. Pair original entry with list of parent-stop cause dicts (A,null family,event,source).

### OA68 — _collect_e_ledger_entries
Per E ledger entry sort causes by str; convert parent-stop tuples to dict, excluding A sources not accepted if filter present. Extend B causes, append pair if nonempty.

### OA69 — _merge_prepared_identities
Combine entries in input order; filter First index to inclusive window unless required identity. First entry wins geometry; later identity extends distinct causes. Use entry stop_cross if key exists (including null), otherwise detector.cross_order. Output dict entry/reaction/causes/crossed, preserve first encounter order.

### OA70 — _single_owner_parent_stop_causes
For each exact parent cause key select physical row min (confirmation,First,Break), first tie. Retain all non-parent causes; parent causes only when row object is selected owner. Mutate retained rows' causes, drop rows with no cause.

### OA71 — prepare_order_audit
Normalize required identities set; collect S then E entries; OA69 and OA70. Return prepared rows.

### OA72 — accepted_audit_entry
Use a_causes or fallback; filter by accepted source set. No accepted => null. First accepted selected. If original selected source/stop and full list unchanged return original object; else shallow copy, replace selected source/stop and accepted causes.

### OA73 — accepted_audit_entries
Map physical identities to non-null OA72 results.

### OA74 — order_identity_is_internal
Both order First/Break required; check normalized identity in internal identities, else false.

## S-side physical Order_A
