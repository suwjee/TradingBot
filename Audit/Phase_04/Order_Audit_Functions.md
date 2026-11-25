# Order Audit — function-level source contracts

Baseline main `466eb875070f02cd0dbfb105033422bbe2fd8c70`; engine/pipeline/order_audit_engine.py blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`. Contract version 1.8.2; implementation 1.9.5. Source-only. Physical identity is (First index, Break index), not consumer, public reaction number, or price. OrderMatch has nine positional fields: reaction number, reaction, confirmation, stop level, stop source index, stop source time, strict crossing triple or null, cause labels tuple, parent-stop cause time or null. B/R are bullish/bearish; direction of an Order is the opposite of its parent trend. Strict crossing is Low<level for bullish Order, High>level for bearish Order.

## Reset-leg geometry

### OA01 — relabel_primary_causes (25–37)
Deep-copy each input cause; for parentType/postBehaviorType/anchorBehaviorType paired with corresponding source-time key, change a PH/PL-prefixed label only if source in labels. Retain first equal dict, preserve order; no original mutation.

### OA02 — dominant_post_behavior_stops (77–136)
Rank lifetimes by (priority callback, int number default0, source time,index), first equal rank wins via negative original ordinal. Sort activations by trigger event or decision event or source. Sweep distinct non-null stop events sorted; activate starts <= event; heap chooses highest rank, lazily discard expired end<event. Both boundaries inclusive. For each lifetime with stop whose owner at exact event is same object, map stop to clamped main candle; choose max (priority,number,source time,index,event time) per candle, first tie. Return PostBehaviorStop records sorted event,index. Records carry behavior type/source index/time/event.

### OA03 — order_b_reset_event_time (139–167)
Truthy reset.second_time => chronology.reset_time(reset). Otherwise within reset main [start,start+timeframe) search first strict low/high crossing of broken_level via lower index or sequential normalized prices. Null absent; no main-candle timestamp fallback.

### OA04 — _order_b_boundary (170–177)
Anchor normalized extreme at first candle. Scan inclusive first..last; strictly lower for low, strictly higher otherwise. Return anchor, extreme boundary, first index attaining boundary (ties unchanged).

### OA05 — _order_b_crossing (180–195)
Search from supplied lower left to end; null empty. Lower index first_less/greater, otherwise loop first strict crossing of selected attribute. Return exact lower timestamp or null.

### OA06 — discover_order_b_reset_legs (198–375)
Validate direction, require post stops and anchors. Low for B, high R. Optional boundary/crossing callbacks or OA04/05 with crossing strictly after reset (upper bound). Sort trend confirmations (confirmation,First, Break, original ordinal, reaction), group by First; opposite analogous with 1-based ordinal. Sort valid reset events (exact reset time,from First,ordinal,reset); stops by (event,source time,index,type); anchors by (source time,index,priority,number,type); sort A formations. For each reset choose last same-direction candidate matching from First with confirmation<reset. Require latest stop event strictly before its First main time and latest anchor source strictly before that time; anchor index<=First. Compute boundary anchor..First inclusive. Boundary must extend anchor strictly and its source index<First. Find first strict crossing after reset; absent => skip. Map crossing to main. Reject if first A formation strictly after current First maps to main <= crossing main. Choose first opposite sorted candidate with First index>=crossing main AND confirmation>exact crossing. Return legs in reset traversal order, carrying stop, anchor type/index/time/extreme, reset reaction/confirmation/index/broken level/exact reset, leg boundary/index/time, exact strict break, physical opposite number/reaction/confirmation. No equality crossing or invented Reaction.

### OA07 — LiveOrderBResetLegs.__init__ (381–388)
Validate direction; store extreme attribute; initialize boundary/crossing caches and last lower time null.

### OA08 — LiveOrderBResetLegs.update (390–439)
Validate dirty main index inclusive 0..len; map dirty or null at end; get latest lower time, dirty lower bound or len; previous coverage via upper_bound of last lower time or 0. New per-call caches; pass OA09/10 closures to OA06. Replace caches with queried entries and last lower time; return legs.

### OA09 — update.boundary (406–414)
Key first,last; current cache first, prior cache only if last<first_dirty_main; else calculate OA04. Cache and return tuple.

### OA10 — update.crossing (416–429)
Key reset time,level; current hit including null returned. Reuse old non-null crossing if before dirty (or dirty null), latest lower exists and crossing<=latest. Otherwise start upper_bound(reset); if prior key existed advance left to max(left,min(old coverage,dirty lower)); search OA05. Cache including null.

### OA11 — discover_accepted_order_b_reset_legs (442–520)
Exclude invalid A (source time,int index). For accepted A use trend reaction ordinal-1 confirmation, S detector first_a_stop, exact stop triple[2]; for S/E use E detector parent_stop and element1; StopAll explicit stop. Obtain dominant stops OA02. Build anchor records for all accepted A/S/E/StopAll, priority and number default0; per exact source time/index choose greater (priority,number,type). Use finder callback or OA06 with dominant stops, accepted A trigger times and tuple of anchor values. Dominance does not suppress later lower-priority anchor.

### OA12 — order_b_leg_identity (530–550)
Sorted tuple of legs' stop type/source index/event; anchor type/index/time/extreme; reset reaction First/Break, reset source index/broken level/time; leg boundary/source index; strict break; physical First/Break. Does not include all presentation fields.

## Canonical Order selection

### OA13 — OrderAuditEngineMixin._initialize_order_audit (557–651)
Initialize empty cross/canonical stop, candidate/carried/post-stop/direct caches, empty ledger and confirmation index, pending list, lazy initial records/indexes null or empty. Materialize trend/opposite First times and confirmations via owner callbacks. Stable trend confirmation sort, times list. Group opposite reset times by int from First in input order; opposite-by-First dictionary last wins. Physical identity-to-canonical position first wins with setdefault.

### OA14 — _order_stop (653–679)
Ignore context_start. If number valid 1-based and exact object is canonical opposite at number-1, cache by number. Otherwise no cache. Both routes chronology.canonical_order_stop(order_direction,number,reaction,opposite_reactions,start_index). Return normalized level/source index/time from chronology, no synthetic contextual stop.

### OA15 — order_stop (682–686)
Public OA14 wrapper.

### OA16 — _first_healthy_direct_geometry (689–761)
No finder => null. Start containing main index and exact event; while index<=end call finder(order_direction,index,end,event). Null => null. If candidate First is blocked and equals original gate main time, advance to candidate First index+1, search_event=First. Otherwise get exact confirmation; prior owner via upper_bound(opposite confirmations,search_event)-1. First prior reset in stored order with search_event<reset<=confirmation restarts at reset main/exact time. Else require candidate identity canonical, otherwise null; return canonical number/object/confirmation. allow_bounded_continue is accepted but not used in function body; restarted assigned but not read. No extra mode gate.

### OA17 — _trend_leg_direct_order (764–792)
No finder null. Trend confirmation strictly > start via upper bound; skip trend First<=start. Per sorted trend position cache OA18 result (including null), return first canonical number/object/confirmation or null.

### OA18 — _trend_leg_order_position (794–806)
Reject internal trend. Finder opposite from trend Break through end at exact trend confirmation. Require candidate and gate decision continue; invoke confirmation callback; candidate First>trend confirmation required. Return canonical physical position or null.

### OA19 — _direct_parent_stop_order (809–827)
Cache by start,deadline,bounded flag,E flag,confirmation_after including null results; delegate OA20 on miss.

### OA20 — _compute_direct_parent_stop_order (829–918)
Gate main time from start. Geometric OA16; reject if confirmation_after given and confirmation<=it. Independent starts lower_bound(opposite First times,gate time), skip confirmation<=confirmation_after when specified; skip blocked First only when equal gate, unless E parent, pair (start,gate time) excepted and confirmation>start. Independent candidate if position valid. Prefer geometric when deadline exists, gate decision restart and deadline equals range_end or deadline<geometric confirmation. Else compute independent stop crossing if independent. Select geometric if not preferred already, independent crossing absent and independent absent or geometric First strictly earlier; otherwise independent if exists. Return min selected pool by First time,confirmation or null. No independent geometric fallback outside these clauses.

### OA21 — _merge_order_candidate (921–952)
Resolve canonical stop and crossing; construct OrderMatch cause parent-stop and supplied cause time. Per physical identity insert if absent or rank (confirmation,First,Break) strictly earlier. Return stored winner.

### OA22 — _enforce_single_parent_stop_owner (955–979)
If >1 parent-stop match, choose min confirmation,First,Break. For others with parent-stop strip that label; keep remaining causes with parent cause time null or delete identity. Mutates passed dict.

### OA23 — order_candidates (982–1070)
Cache key start,deadline,bounded/trend/E flags; return list copy on hit. Add OA19 and optionally OA17 via OA21. For each B leg whose physical First time>start, merge reset-leg label into same identity (ordered unique) or create match from leg confirmation and stop/cross. OA22. Deadline earliest non-null stop crossing among candidates or range_end; min continuous deadline when supplied. Keep confirmation<=deadline. Sort by crossing exact time (range_end for null), reaction First time; cache tuple, return list.

### OA24 — _first_order (1073–1086)
OA23 with flags, filter crossed not null, return first or null.

### OA25 — _has_sequence_reset_between (1089–1097)
Upper bound start in sorted reset times; true next exists and <=end, interval (start,end].

### OA26 — _index_order_audit_identity (1100–1111)
Insert (confirmation,First,Break) right of equal into confirmation index. If sorted audit is dict append pending; otherwise reset sorted audit null.

### OA27 — _clear_order_audit (1114–1118)
Clear authoritative ledger and confirmation index; invalidate carried and post-stop caches.

### OA28 — _invalidate_carried_order_caches (1120–1127)
Clear carried results; set creation index and pending append null. Does not invalidate post-stop results.

### OA29 — _invalidate_post_stop_order_cache (1129–1132)
Clear post-stop result cache, null sorted audit and clear pending.

### OA30 — register_order_b_reset_legs (1135–1199)
If legs invalidate carried cache. Per physical reaction insert new ledger row with canonical stop, exact crossing, empty parent cause set and confirmation index; otherwise reuse existing. Build reset-leg cause dict with postBehaviorType/StopTime/SourceIndex/SourceTime, anchorBehaviorType/SourceIndex/SourceTime/Extreme string, resetReactionIdentity, BreakoutTime and ConfirmationTime, resetIndex/BrokenLevel string/Time, legBoundary string/SourceIndex/SourceTime, strictBreakTime, physicalOrderIdentity and ConfirmationTime. Deduplicate equality; sort B causes by post stop,reset,break,physical identity; invalidate carried on addition.

## Primary and parent registration

### OA31 — _reparent_primary_high_causes (1202–1248)
Label kind+number and source identity. For each ledger parent-stop cause replacing StopAll role, require same parent source time, non-null equal stop and stop>primary decision. Keep replacement only on direct physical identity, family empty; other matching roles revoked. B causes: relabel postBehavior StopAll when exact source and stop match and stop>decision; relabel anchor StopAll on exact source when reset identity exists and its First main time>=decision. Delete entries with neither parent nor B causes; remove indexes of revoked identities and invalidate post-stop. Invalidate carried if changes/revocations. Historical sequence reset map not removed.

### OA32 — register_primary_high (1250–1258)
Only bearish owner and parent.kind PH; otherwise ValueError. OA36.

### OA33 — register_primary_low (1260–1264)
Only bullish owner and kind PL; otherwise ValueError. OA36.

### OA34 — _primary_parent_order (1266–1275)
Search lower (decision,range_end) using first_cross_position, less iff bullish owner. If stop found call OA19 with stop,null,false, confirmation_after=stop; return stop,direct (null possible).

### OA35 — primary_order_dependency (1277–1284)
OA34; no direct => stop,null. Else stop,repr(direct),str(level),source index/time,cross of confirmation and stop level.

### OA36 — _register_primary_point (1286–1310)
OA34 then OA31 even when no direct (direct identity null). Null direct => null. Else ensure physical ledger row with stop/cross and empty cause set/index if new. Add cause (parent-stop,kind+number,empty family,exact stop,source time) if absent; invalidate carried; return identity.

### OA37 — reconcile_primary_high_labels (1312–1314)
OA39 with PH.

### OA38 — reconcile_primary_low_labels (1316–1318)
OA39 with PL.

### OA39 — _reconcile_primary_labels (1320–1337)
Map source to prefix+number (last duplicate wins). For each ledger cause tuple relabel only prefix-matching label at known source; B causes OA01; update only changed collections, invalidate carried if changed.

### OA40 — _register_order_audit (1339–1433)
Skip S whose identity invalid or accepted E occupies it. Skip known sequence reset in (source,parent_stop]. OA23 with S bounded/E trend flags; also OA19 and append direct match if absent from candidates, even if no stop before decision. Register only matches with parent-stop cause. New physical row preserves geometry, adds index. Label parent type, E+number if present, override StopAll+sequence number at reset source and empty family; otherwise family from color/family. Add unique parent-stop cause with event/source. Determine earlier existing creation from minimum prior parent-stop event; exception => conservative earlier true. Invalidate carried if new row or earlier existing creation. When only appended rows and prior validated creation index refers to same exact dict and size agrees, retain pending index extension for next query. Later/equal additional cause does not change carried eligibility. No post-stop invalidation for cause-only additions.

### OA41 — visual_order_lifecycle (1437–1456)
Static method with explicit self argument. Start lower bound opposite First times; first candidate First>=start and confirmation>=start, compute stop/cross, return singleton eight-field tuple with final false; else empty.

### OA42 — _cross_order (1459–1477)
Cache (start,level) including null. Search strict crossing over lower [max(start,range_start),range_end), less unless order_direction bearish. Null absent; otherwise (main index, main timestamp, exact lower event). Cache result.

### OA43 — cross_order (1480–1484)
Public OA42 wrapper.

### OA44 — _unconsumed_s_orders (1487–1521)
Require S color exact blue, non-null order confirmation/stop level. Crossing exists and >=parent_stop. Construct SimpleNamespace from parent's Order mode/First/Break/box top/bottom and their source indexes; return singleton match with parent Order number/source/confirmation/level/cross, carried-live label and null parent creation time. Otherwise empty.

## Reuse and indexing

### OA45 — _initial_order_records (1524–1579)
Lazy materialize initial audit values as (First time,confirmation,int number,reaction,Decimal stop,int source,source time,cross). Sort by First,confirmation,First index,Break index. Cache tuple and First times, group records by First as tuples, separate confirmation-sorted view by confirmation,First time,First index,Break; return same tuple.

### OA46 — _initial_record_match (1583–1594)
Convert record to OrderMatch dropping First time; supplied causes, null parent cause time.

### OA47 — _initial_order_match (1597–1609)
Convert entry to OrderMatch, normalize number/level/source index, calculate crossing, supplied causes and null parent cause time.

### OA48 — _gate_owned_initial_order (1612–1632)
Initial records at gate main First; confirmation>=parent stop, crossing exists and >=parent stop. Convert carried-live; min crossing,First time or null.

### OA49 — _carried_creation_events (1636–1642)
Earliest parent-stop cause event only if >1 (single preserved), plus every B physical confirmation. No dedup here.

### OA50 — _validated_carried_creation_index (1644–1697)
Under local Decimal context validate native rows (exact dict; allowed cause containers, nonempty exact tuples, B exact dicts). No creation => skip. Exact datetime values and same tzinfo object for creation,confirmation,source time,cross dates; non-null crossing exact tuple length>=3 and int index. Exact int reaction number/source/First/Break; stop level exact Decimal,str,int,float and normalized finite. Build sorted unique creation events per row with original ordinal. Return events,tzinfo; any validation failure or exception => null, preserving caller Decimal flags/traps and legacy evaluation fallback.

### OA51 — _extend_carried_creation_index (1699–1720)
Consume pending append (set null immediately). Require matching ledger identity and expected size. Validate appended rows OA50; compatible tzinfo if both have events; if old empty adopt new timezone. Insert new events with ordinal offset using insort_right; extend entries. Return ledger,entries,(events,timezone) or null.

### OA52 — _carried_orders_for_parent (1722–1795)
Null lifecycle decision => empty. Cache key decision,parent_stop; copy on hit. If creation index missing or cache empty, try OA51 else materialize ledger values with OA50. Use native index only when query datetimes exact and tzinfo identity matches: events strictly between lifecycle start and parent stop; dedup ordinals sorted insertion order. Else legacy scan OA49 per entry. Require creation event in strict interval (when not indexed), confirmation<=parent_stop, crossing non-null and >=parent_stop. Convert matches carried-live. Add initial records with First in inclusive [lifecycle_start,parent_stop] and same confirmation/cross conditions. Sort crossing, negative First index (later First wins ties); cache tuple.

### OA53 — _post_stop_accepted_orders_for_parent (1798–1877)
Ignore parent. Cache key parent_stop and confirmation-index length. First initial records confirmation strictly after parent stop, add OA54; then ledger index entries after (parent_stop,2^63-1,2^63-1). Skip missing entry/reaction, non-datetime confirmation or missing level/source fields. If crossed not tuple len>=3 with datetime event recompute cross. Normalize and add accepted-live. Sort identity winners (cross event,confirmation,-First index), cache list, return copy.

### OA54 — _post_stop_accepted_orders_for_parent.add_match (1812–1829)
Reject null cross or cross<=parent_stop or <=own confirmation or sequence reset in (parent_stop,cross]. Per identity replace only strictly earlier (cross,confirmation,First index). Insertion order retained.

### OA55 — _iter_post_stop_accepted_orders (1879–2017)
Lazy merge with fallback to OA53 for non-native query or data. Key (cross,confirmation,-First). Validate initial geometry eagerly under local Decimal context, sorted crossed after confirmation; conflicting events for same identity invalidate optimized stream. Persist initial view and times/geometry or false. For audit build/append from confirmation index or pending; exact native times/ints/dict/price types, normalized finite price and matching indexed confirmation required; null crossing must have known-null cache; include only cross>confirmation; conflicting initial identity event pair triggers fallback. Sort new audit rows by key+First+Break, merge equal bit_length tiers into immutable runs, clear pending; exceptions mark audit false. Determine first sequence reset strictly after parent stop. Return OA59 generator, using OA58 for eligibility. Initial materialization before audit maintains eager exception precedence.

### OA56 — _iter_post_stop_accepted_orders.native_time (1890–1891)
Exact datetime type and tzinfo same object as range_start.

### OA57 — _iter_post_stop_accepted_orders.native_match (1893–1905)
Exact ints number/source/First/Break; native confirmation/source time; exact finite Decimal level; cross null or exact tuple len>=3 with int index and native main/exact time.

### OA58 — _iter_post_stop_accepted_orders.eligible (1998–2005)
Start upper_bound cross times parent_stop; unwrap audit row if flagged; stop iteration at cross>=first reset; yield only confirmation>parent_stop. Preserves row form.

### OA59 — _iter_post_stop_accepted_orders.accepted (2007–2015)
Merge eligible audit runs by full audit key, extract matches; merge eligible initial and audit by main key; yield first per physical identity, initial wins equal merge key.

### OA60 — _order_created_only_by_disowned_s (2020–2033)
False if entry missing, no parent causes, B causes exist or initial ledger identity. Else true only if every cause parent-stop S, len>4, source in disowned source times or equals prospective source.

### OA61 — _blocked_by_gate_owned_order (2035–2043)
Require parent-stop cause label in E; gate-owned initial OA48 at E parent stop; block if exists and its confirmation<zone Order First time.

## Accepted ledger reconstruction and export

### OA62 — _rebuild_accepted_order_audit (2046–2231)
Set accepted E physical source identities. Invalid S times = explicit invalid roots plus accepted E occupied sources. Snapshot previous ledger with parent causes filtered OA63; clear ledger/index/caches; register B legs. For all S and numbered E (StopAll label where sequence reset source) resolve parent stop and OA40 register if stop. For each numbered E whose physical Order absent: find canonical opposite by First, require matching Break else SimpleNamespace with Order geometry, internal false. Recover valid prior parent-stop causes; initial A audit causes (skip null source/stop); if none and carried-live with S parent, find exact S across original+supplemental matching parent source/index and Order identity and recover A creation. If explicit Order parent cause time non-null, add parent-stop using E parent number if found or StopAll override, family empty at reset otherwise zone family, zone parent stop event/source. Filter OA63; skip if none. Compute exact cross, insert reconstructed ledger row/index. Finally preserve all previous valid parent-stop physical identities even not consumed by final E: merge causes into existing or restore prior entry with causes and index. Return numbered sorted source time,index.

### OA63 — _rebuild_accepted_order_audit.valid_parent_stop_cause (2060–2072)
Require nonempty parent-stop cause. Reject S len>4 and source time invalid/occupied; otherwise valid.

### OA64 — rebuild_accepted_order_audit (2234–2246)
OA62 with copy of zones and supplemental S.

### OA65 — ensure_accepted_order_audit (2249–2288)
Snapshot prior ledger with copied cause sets; OA62 on supplied zones. Invalid S source times from invalid roots union new accepted E identities. For prior identities absent in rebuild filter S causes at those times; skip if no causes and no B causes. Restore row and confirmation index. Invalidate carried, return rebuilt zones. Preserves pre-existing StopAll/history orders.

### OA66 — _parent_stop_cause_key (2291–2297)
Tuple parentType,parentFamily,eventTime,parentSourceTime via get.

### OA67 — _collect_s_ledger_entries (2300–2329)
Null detector => empty. Per S ledger entry use a_causes or fallback source/stop pair; optional accepted A filter; skip empty. Pair original entry with list of parent-stop cause dicts (A,null family,event,source).

### OA68 — _collect_e_ledger_entries (2332–2358)
Per E ledger entry sort causes by str; convert parent-stop tuples to dict, excluding A sources not accepted if filter present. Extend B causes, append pair if nonempty.

### OA69 — _merge_prepared_identities (2361–2401)
Combine entries in input order; filter First index to inclusive window unless required identity. First entry wins geometry; later identity extends distinct causes. Use entry stop_cross if key exists (including null), otherwise detector.cross_order. Output dict entry/reaction/causes/crossed, preserve first encounter order.

### OA70 — _single_owner_parent_stop_causes (2404–2439)
For each exact parent cause key select physical row min (confirmation,First,Break), first tie. Retain all non-parent causes; parent causes only when row object is selected owner. Mutate retained rows' causes, drop rows with no cause.

### OA71 — prepare_order_audit (2442–2459)
Normalize required identities set; collect S then E entries; OA69 and OA70. Return prepared rows.

### OA72 — accepted_audit_entry (2462–2492)
Use a_causes or fallback; filter by accepted source set. No accepted => null. First accepted selected. If original selected source/stop and full list unchanged return original object; else shallow copy, replace selected source/stop and accepted causes.

### OA73 — accepted_audit_entries (2495–2505)
Map physical identities to non-null OA72 results.

### OA74 — order_identity_is_internal (2508–2514)
Both order First/Break required; check normalized identity in internal identities, else false.

## S-side physical Order_A

### OA75 — SOrderAuditMixin._initialize_stopped_a_order_lookup (2520–2544)
Opposite First map int->(1-based number,reaction), last duplicate wins. Sort native matches (confirmation,First,Break,number,reaction), confirmation times list; empty first-canonical cache.

### OA76 — _first_order_after (2546–2598)
Native OA77. If no initial geometry callback return native. Else call with gate main index,exact A stop,end. Null/incomplete physical, First<gate or confirmation<=stop => native. If physical identity matches mapped same First, use canonical number/object and recompute confirmation; else number0. Return independent if native absent or (First index,confirmation) strictly earlier than native; otherwise native. No public Reaction invented for order-only geometry.

### OA77 — _first_canonical_order_after (2601–2620)
Cache by exact A stop incl null; upper_bound confirmation stop; first sorted match whose First index>=gate main. Return number,reaction,confirmation or null.

### OA78 — _record_a_order_audit (2622–2654)
Compute stop via OA80, physical identity. If absent create row with reaction number/object/confirmation, stop geometry, A source/stop and empty a_causes. Append unique (A source,stop). Existing geometry and first selected cause preserved.

### OA79 — _audit_stopped_a (2657–2667)
Normalize A price; first A stop after its confirmation; absent => return. OA76 at exact event; if match OA78.

### OA80 — SOrderAuditMixin._order_stop (2670–2679)
Delegate chronology.canonical_order_stop with order_direction,number,reaction,opposite list,start_index. No local cache.

### OA81 — _order_stop_crossed (2682–2685)
Bearish Order normalized High>level; otherwise normalized Low<level.

### OA82 — _shared_order_stop_cross (2688–2712)
Lower range [max(confirmation,range_start),range_end). If nonempty and lower index exists, first_greater bearish/first_less otherwise, return null if none; else scan slice OA81. Return main index/timestamp/exact lower event at first crossing or null.

## Verification boundary
All 82 named declarations have individual descriptions, including nested helpers, with six classes (three immutable records and three owner classes). Runtime, RAW, benchmark and regression are outside this phase. Imported chronology, lifecycle and reaction dependencies require cross-module traceability review; source remains authoritative in case of documentation discrepancy.
