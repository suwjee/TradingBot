# Order audit — canonical ledger, reuse and accepted provenance (V3)

**Conventions:** B = bullish, R = bearish. Parent directional extreme is Low for B and High for R; strict parent stop/improvement means lower for B and higher for R. An opposite Order has its own direction and strict predicate, not the parent predicate. Use Decimal normalization and native arithmetic order; preserve source/main versus exact-event times, physical identity, original order, and nulls. Use [record interfaces](../../Contracts/Declared_Record_Schemas.md) and [chronology/index services](20_Indexes_And_Caching.md). Procedure labels name semantic operations, not required implementation symbols.


## OL-M01 — State model

One direction's ledger is keyed by physical opposite (First index,Break index). Entry retains canonical reaction/number/confirmation, stop level/source, strict crossing triple or null, set of parent-stop tuples and separate reset-leg dictionaries. Parent-stop tuple identity includes label/family/exact stop/source. Initial A audit uses A source/stop pairs. Order_A and Order_B are independent creation routes; carried-live and accepted-live are consumption labels only. Geometry-only evidence cannot create except explicit S-side independent A route. Never assign consumption parent as creation parent. Initialize caches and confirmation-sorted index, track actual ledger changes; mutable ledger and derived indexes are owned by detector.

## OL-M02 — Candidate availability

| Candidate path | Gates |
|---|---|
| Direct parent-stop | [Order A](06_Order_A.md), canonical owner and stop geometry; actual Order crossing can be null at creation, whereas E consumption requires a qualifying crossing |
| Reset-leg | [Order B](07_Order_B.md), accepted exact reset provenance |
| Unconsumed S Blue Order | S Blue with Order confirmation/stop, actual crossing >= new parent stop, copy its physical geometry |
| Gate-owned initial A | First main exactly gate, confirmation >= parent stop and stop >= parent stop; earliest crossing then First |
| Carried accepted Order | Creation strictly in (parent lifecycle decision,parent stop); own confirmation <= parent stop; strict crossing >= parent stop. Initial A uses First in inclusive lifecycle..stop as separate eligibility path |
| Post-stop accepted | Native stream: confirmation > parent stop and crossing > both; no sequence reset in (parent stop,cross]; deduplicate physical identity. Eager legacy scan uses its confirmation index tuple bound and current row without an additional confirmation > parent stop recheck (OA53/54). |

Carried creation event from earliest parent-stop cause (when multiple) plus every reset-leg physical confirmation. Sort carried crossing then later First. Post-stop fallback materializes and sorts, optimized native stream merges initial and ledger runs, same crossing/confirmation tie keeps later First and initial exact tie. Validate exact native types/timezone, finite Decimal level and crossing shape under local context; invalid/unverifiable data falls back to legacy scan. Never use speculative cache results as accepted evidence. Scope/key and invalidation details below.

## OL-M03 — Rebuild and primary reparenting

Rebuild from actual accepted E plus accepted S roots, retained initial A causes and reset legs; filter S parent cause when invalid or occupied by E. Preserve valid historical physical entries even if unused by current E; retain independently valid causes, do not synthesize an Order without cause. Reconstructed E-consumed geometry may use recorded Order fields if canonical identity missing; only create ledger row if valid recovered/explicit parent causes exist. Ensure audit preserves prior independently valid B/history entries. Register primary PH on bearish owner / PL on bullish owner only. Find first strict stop strictly after decision; request direct physical Order with confirmation_after=stop (OA34; no independent final recheck and OA20 sequential-skip caveat). Reparent same-source obsolete StopAll cause only when exact stop matches and after primary decision; transfer to direct identity, revoke other matching cause, remove identity only if no parent/reset cause left. Relabel B stop and anchor provenance with exact source/stop and anchor First gates; reconcile finalized primary labels without changing identity or prices.

## OL-M04 — Public audit preparation and invariants

Collect accepted S/A ledger (filter accepted A set) then E ledger; preserve first geometry for physical identity and append distinct causes. Retain First within visible inclusive range OR explicitly required identity from visible S/E/StopAll. Keep one physical owner per exact parent-stop tuple: earliest confirmation,First,Break. Remove owner-losing causes only, drop entry only when no causes. Final bridge invariant requires every displayed S/E/StopAll with both physical indexes reference retained identity, and one exact parent-stop cannot name multiple identities. Audit export sorts First time,Break time. Exact stop, main owner and optional nulls remain intact. Invalidity/visibility ownership is [Lifecycle](10_Lifecycle.md), not ledger geometry.

## Detailed ledger procedures

### OA01 — relabel_primary_causes
Deep-copy each input cause; for parentType/postBehaviorType/anchorBehaviorType paired with corresponding source-time key, string-convert the current label (default empty) and test PH/PL prefix first; only then read associated source (default null) and test membership in labels before replacement. Retain first equal dict, preserve order; no original mutation.

### OA13 — OrderAuditEngineMixin._initialize_order_audit
Initialize empty cross/canonical stop, candidate/carried/post-stop/direct caches, empty ledger and confirmation index, pending list, lazy initial records/indexes null or empty. Materialize trend/opposite First times and confirmations via owner callbacks. Stable trend confirmation sort, times list. Group opposite reset times by int from First in input order; opposite-by-First dictionary last wins. Physical identity-to-canonical position first wins with setdefault. Fresh containers replace prior named values: initial record cache, initial First/confirmation times and by-First index are null; initial confirmation records empty tuple; ledger confirmation index and pending empty lists, sorted audit null, trend-leg positions empty dict. Four separate callback passes preserve input order, First times from main index and exact confirmations from chronology using trend/Order directions respectively. Only trend triples are stable-sorted by confirmation alone after ordinary zip (shortest-input termination); opposite arrays are not sorted locally. Reset grouping retains all returned times in supplied order; E owner sorts opposite resets beforehand. Physical identity is int First/Break, first duplicate wins; by-First last duplicate wins. No local validation of alignment/sortedness, no Order creation.

### OA25 — _has_sequence_reset_between
Upper bound start in sorted reset times; true next exists and <=end, interval (start,end]. Upper bound excludes all equal starts; bounds test short-circuits before array access, end inclusive. Owner setter copies reset mapping and sorts keys; query assumes synchronized sorted comparable timestamps, does not normalize interval.

### OA26 — _index_order_audit_identity
Insert (confirmation,First,Break) right of equal into confirmation index. If sorted audit is dict append pending; otherwise reset sorted audit null. No duplicate suppression; isinstance(dict) includes subclass, append same tuple to pending; non-dict sets sorted audit null without clearing pending. Index assumed sorted.

### OA27 — _clear_order_audit
Clear authoritative ledger and confirmation index; invalidate carried and post-stop caches. Clear existing ledger/index containers in place in that order, then carried then post-stop invalidation; unrelated geometry/direct/candidate caches not reset here; no rollback.

### OA28 — _invalidate_carried_order_caches
Clear carried results; set creation index and pending append null. Does not invalidate post-stop results. Clear carried dictionary in place; assign creation index and append state None. Leave post-stop state untouched.

### OA29 — _invalidate_post_stop_order_cache
Clear post-stop result cache, null sorted audit and clear pending. Clear result dictionary in place, assign sorted audit None, then clear pending list in place; does not clear carried state.

### OA31 — _reparent_primary_high_causes
Label kind+number and source identity. For each ledger parent-stop cause replacing StopAll role, require same parent source time, non-null equal stop and stop>primary decision. Keep replacement only on direct physical identity, family empty; other matching roles revoked. B causes: relabel postBehavior StopAll when exact source and stop match and stop>decision; relabel anchor StopAll on exact source when reset identity exists and its First main time>=decision. Delete entries with neither parent nor B causes; remove indexes of revoked identities and invalidate post-stop. Invalidate carried if changes/revocations. Historical sequence reset map not removed. Parent-stop tuple matching uses only parent source time (not source index); ordered short-circuit requires StopAll prefix, non-null equal stop and strict event>decision. Nonmatching cause retained unchanged, matching cause only retained as replacement on direct identity (null direct revokes matches). B post-stop uses exact source pair, stop equality and strict bound without direct-identity gate; anchor independently uses exact pair, truthy reset identity and inclusive First main>=decision, no stop/direct gate. In-place B dictionary changes are not sorted/deduped here. Any causeless entry including already causeless marked for deferred removal; filter every matching confirmation tuple via slice, preserve list identity. Post-stop invalidation only on revoked, carried if changed or revoked; no rollback.

### OA32 — register_primary_high
Only bearish owner and parent.kind PH; otherwise ValueError. OA36. Direction mismatch short-circuits kind lookup (default None); invalid raises before OA36, valid returns its result.

### OA33 — register_primary_low
Only bullish owner and kind PL; otherwise ValueError. OA36. Direction mismatch short-circuits kind lookup (default None); invalid raises before OA36, valid returns its result.

### OA34 — _primary_parent_order
Search lower (decision,range_end) using first_cross_position, less iff bullish owner. If stop found call OA19 with stop,null,false, confirmation_after=stop; return stop,direct (null possible). No local range_start clamp or returned-position validation; indexed/scan strict crossing service owns proof. Request OA19 with deadline null, bounded false, E flag default false, confirmation_after=stop; OA34 does not recheck returned confirmation. OA20 initial threshold loop is not re-run after blocked-First skips, so do not claim unconditional strict confirmation on arbitrary streams.

### OA35 — primary_order_dependency
OA34; no direct => stop,null. Else stop,repr(direct),str(level),source index/time,cross of confirmation and stop level. Two-element tuple on null direct, six-element otherwise; native repr and str evaluated before crossing; no direct registration, delegated calls may populate caches.

### OA36 — _register_primary_point
OA34 then OA31 even when no direct (direct identity null). Null direct => null. Else ensure physical ledger row with stop/cross and empty cause set/index if new. Add cause (parent-stop,kind+number,empty family,exact stop,source time) if absent; invalidate carried; return identity. Use OA31 before null-direct return and lookup (which sees possible revocation); same helper for both primary kinds. Existing row geometry retained; new row published then indexed. Cause tuple dedup exact; carried invalidation on addition, besides OA31 effects. No rollback.

### OA37 — reconcile_primary_high_labels
OA39 with PH. Fixed PH prefix; no direction/kind gate, implicit None.

### OA38 — reconcile_primary_low_labels
OA39 with PL. Fixed PL prefix; no direction/kind gate, implicit None.

### OA39 — _reconcile_primary_labels
Map source to prefix+number (last duplicate wins). For each ledger cause tuple relabel only prefix-matching label at known source; B causes OA01; update only changed collections, invalidate carried if changed. Parent tuples rebuilt as set (may dedup after relabel), prefix test via str, original label fallback. OA01 B relabel independently matches either PH/PL prefix with supplied source map, not only wrapper prefix; deep-copy/equality dedup. Compare set/list by equality, preserve original collections when equal. Carried invalidation only on change, no post-stop invalidation or index/geometry mutation.

### OA44 — _unconsumed_s_orders
Require S color exact blue, non-null order confirmation/stop level. Crossing exists and >=parent_stop. Construct SimpleNamespace from parent's Order mode/First/Break/box top/bottom and their source indexes; return singleton match with parent Order number/source/confirmation/level/cross, carried-live label and null parent creation time. Otherwise empty. Required color via str, optional confirmation then stop-level None guards in order; read confirmation and normalize level again after guards. Reject crossing null or exact event<parent_stop, no separate confirmation gate. Namespace geometry attributes copied without conversion or canonical lookup; int only reaction number and stop source index. No direct ledger mutation.

## Reuse and indexing

### OA45 — _initial_order_records
Lazy materialize initial audit values as (First time,confirmation,int number,reaction,Decimal stop,int source,source time,cross). Sort by First,confirmation,First index,Break index. Cache tuple and First times, group records by First as tuples, separate confirmation-sorted view by confirmation,First time,First index,Break; return same tuple. Non-null cache incl empty returned immediately without secondary rebuild. Traverse initial audit values in input order, normalize level and compute cross before int ordinal/source. Stable sort; publish primary tuple before First time projection, bucket tuples, then separate stable confirmation-sorted tuple and times. Same record/reaction objects reused; owner retains nonempty initial mapping by reference, immutability assumed not enforced, no rollback if secondary publication fails.

### OA46 — _initial_record_match
Convert record to OrderMatch dropping First time; supplied causes, null parent cause time. Static unpack exact eight-field record, preserve all seven remaining fields, supplied cause tuple and null creation time; no recompute/copy.

### OA47 — _initial_order_match
Convert entry to OrderMatch, normalize number/level/source index, calculate crossing, supplied causes and null parent cause time. Read reaction/confirmation then normalize stop and compute crossing before integer conversions; preserve reaction and source time, no new geometry.

### OA48 — _gate_owned_initial_order
Initial records at gate main First; confirmation>=parent stop, crossing exists and >=parent stop. Convert carried-live; min crossing,First time or null. Use clamped main self.times, force materialization, assert by-First dictionary non-null. Exact bucket lookup default empty; strict earlier rejection means confirmation and crossing equality allowed. Stable min on exact crossing then recomputed reaction First, first equal wins, empty None. No ledger mutation.

### OA49 — _carried_creation_events
Earliest parent-stop cause event only if >1 (single preserved), plus every B physical confirmation. No dedup here. Collect exact parent-stop causes in native iteration order, only reduce when count>1; append every B physical confirmation in input order including duplicate/equal times. No cross-category dedup, time normalization or local validation/catch.

### OA50 — _validated_carried_creation_index
Under local Decimal context validate native rows (exact dict; allowed cause containers, nonempty exact tuples, B exact dicts). No creation => skip. Exact datetime values and same tzinfo object for creation,confirmation,source time,cross dates; non-null crossing exact tuple length>=3 and int index. Exact int reaction number/source/First/Break; stop level exact Decimal,str,int,float and normalized finite. Build sorted unique creation events per row with original ordinal. Return events,tzinfo; any validation failure or exception => null, preserving caller Decimal flags/traps and legacy evaluation fallback. Validate cause containers and element shapes before no-creation skip; original ordinal counts skipped rows. Nonempty parent tuples not length-validated here; OA49 exceptions fall back. Date groups created then confirmation/source then optional crossing slots 1:3; exact datetime and same tzinfo object across rows, first date seeds even None. Crossing extra fields ignored, no positivity/index bounds validation. Eager four-int field tuple, exact level type gate then finite normalization. Dedup per row only, sort pairs inside context; catch Exception including context management, restore caller context; no partial index returned.

### OA51 — _extend_carried_creation_index
Consume pending append (set null immediately). Require matching ledger identity and expected size. Validate appended rows OA50; compatible tzinfo if both have events; if old empty adopt new timezone. Insert new events with ordinal offset using insort_right; extend entries. Return ledger,entries,(events,timezone) or null. Pending consumed before null check/unpack; malformed pending outside OA50 catch. Validate new rows only, old prefix depends on owner invalidation. Empty old adopts new timezone, mismatch only both event lists nonempty. Offset old entry count including skipped rows; mutate old events then old entries in place, no rollback/catch.

### OA52 — _carried_orders_for_parent
Null lifecycle decision => empty. Cache key decision,parent_stop; copy on hit. If creation index missing or cache empty, try OA51 else materialize ledger values with OA50. Use native index only when query datetimes exact and tzinfo identity matches: events strictly between lifecycle start and parent stop; dedup ordinals sorted insertion order. Else legacy scan OA49 per entry. Require creation event in strict interval (when not indexed), confirmation<=parent_stop, crossing non-null and >=parent_stop. Convert matches carried-live. Add initial records with First in inclusive [lifecycle_start,parent_stop] and same confirmation/cross conditions. Sort crossing, negative First index (later First wins ties); cache tuple. Hit non-null tuple including empty; return shallow list. Refresh missing index OR empty carried cache; store full tuple even when OA50 payload null. Native upper bound (start,len(entries)), lower bound (stop,-1), ordinal dedup/sort; selected None marker bypasses creation scan. Legacy generator lazy OA49; skip empty creation before reading confirmation/cross. Ordered rejection legacy no strict hit, confirmation>stop, crossing null, exact crossing<stop; stored crossing not recomputed, normalize only selected. Initial records after accepted pass, inclusive First slice with same confirmation/cross guards, no creation check or cross-route dedup. Stable equal sort keys preserve accepted-before-initial/traversal order; tuple cache, original list on miss. Ordinary reuse depends on owner invalidation, no local catch for legacy errors.

### OA53 — _post_stop_accepted_orders_for_parent
Ignore parent. Cache key parent_stop and confirmation-index length. First initial records confirmation strictly after parent stop, add OA54; then ledger index entries after (parent_stop,2^63-1,2^63-1). Skip missing entry/reaction, non-datetime confirmation or missing level/source fields. If crossed not tuple len>=3 with datetime event recompute cross. Normalize and add accepted-live. Sort identity winners (cross event,confirmation,-First index), cache list, return copy. Non-null cache list incl empty, copy on hit and miss. Initial materialized before ledger and asserted confirmation index. Full tuple upper-bound sentinel is exact integer 2^63−1 for both identity fields, not a universal strict confirmation filter for arbitrary indexes; use current entry confirmation, discard indexed value, no local recheck >parent_stop. Legacy isinstance(datetime/tuple) accepts subclasses; only slot2 crossing date checked, len>=3, other slots not validated. Recompute malformed/null crossing using normalized level, no ledger writeback. Convert number default0, normalize level again and int source before nested gate. Native errors propagate. Final stable key (cross,confirmation,-int First).

### OA54 — _post_stop_accepted_orders_for_parent.add_match
Reject null cross or cross<=parent_stop or <=own confirmation or sequence reset in (parent_stop,cross]. Per identity replace only strictly earlier (cross,confirmation,First index). Insertion order retained. Ordered null, crossing<=parent stop, crossing<=own confirmation, sequence reset rejection; no confirmation>parent stop recheck. Int physical pair; absent insert without rank, otherwise strict lexicographic positive First rank, equal retains first. Final sort OA53 uses negative First; replacement retains dictionary insertion order.

### OA55 — _iter_post_stop_accepted_orders
Lazy merge with fallback to OA53 for non-native query or data. Key (cross,confirmation,-First). Validate initial geometry eagerly under local Decimal context, sorted crossed after confirmation; conflicting events for same identity invalidate optimized stream. Persist initial view and times/geometry or false. For audit build/append from confirmation index or pending; exact native times/ints/dict/price types, normalized finite price and matching indexed confirmation required; null crossing must have known-null cache; include only cross>confirmation; conflicting initial identity event pair triggers fallback. Sort new audit rows by key+First+Break, merge equal bit_length tiers into immutable runs, clear pending; exceptions mark audit false. Determine first sequence reset strictly after parent stop. Return OA59 generator, using OA58 for eligibility. Initial materialization before audit maintains eager exception precedence. Outer method eagerly captures timezone, validates/builds views and captures next Reset before returning OA59 generator; eager OA53 fallback called before iter. Initial OA45 materialization outside try; native conversion/validation/sort under local context; validate all before filtering cross non-null and >confirmation. Initial geometry pair agreement only (cross,confirmation), same identity equal pair allowed; no price/source equality check. Initial None builds, False caches failure. Audit refresh None or pending; full index only None, otherwise pending. Require indexed native confirmation and exact int pair, exact dict/price, normalized level, native match and confirmation equality; no indexed pair vs reaction identity check. Null cross requires existing known-null cache and omitted; non-null cross<=confirmation omitted. Compare event pair only against initial identity, no audit-audit conflict check. Full row key uses indexed First/Break after main key. Shallow copy mapping, not mutate older run lists; tier is bit_length, not equal size, merge older first on ties, fresh list and time projection. Pending cleared on success or caught failure before state assignment. False with empty pending falls back; with pending attempts build but False.copy fails if reached and caught. Build exceptions caught, initial materialization and generator-consumption exceptions not covered. No claim of runtime parity.

### OA56 — _iter_post_stop_accepted_orders.native_time
Exact datetime type and tzinfo same object as range_start. Exact type before tzinfo identity check, no conversion or value-equality comparison.

### OA57 — _iter_post_stop_accepted_orders.native_match
Exact ints number/source/First/Break; native confirmation/source time; exact finite Decimal level; cross null or exact tuple len>=3 with int index and native main/exact time. Four fields evaluated eagerly before all exact-int checks, then native confirmation/source, exact Decimal finite, then optional crossing in ordered short circuit. Exact tuple length>=3 (extra fields ignored), no positivity or range validation.

### OA58 — _iter_post_stop_accepted_orders.eligible
Start upper_bound cross times parent_stop; unwrap audit row if flagged; stop iteration at cross>=first reset; yield only confirmation>parent_stop. Preserves row form. Reset captured once before generator returned, upper bound crossing strictly > parent stop, break run on crossing>=reset including equality, strict confirmation>stop; yield original keyed row/match, not copy. No extra cross>confirmation check at consumption.

### OA59 — _iter_post_stop_accepted_orders.accepted
Merge eligible audit runs by full audit key, extract matches; merge eligible initial and audit by main key; yield first per physical identity, initial wins equal merge key. Generator creates audit run iterators in mapping insertion order on consumption, merge by full key then unwrap; merge initial first and audit second by main key, equal main key initial first. Fresh seen set per generator, add before yield, no repeated arbitration or mutation. Published runs reused by reference, not frozen.

### OA60 — _order_created_only_by_disowned_s
False if entry missing, no parent causes, B causes exist or initial ledger identity. Else true only if every cause parent-stop S, len>4, source in disowned source times or equals prospective source. Ordered OR entry None, falsey parent causes, truthy B causes, mere initial identity membership. All causes must pass exact kind then S label then len>4 then source membership or prospective equality; source None may equal default prospective None. Malformed short cause can raise before len guard; no local catch or normalization.

### OA61 — _blocked_by_gate_owned_order
Require parent-stop cause label in E; gate-owned initial OA48 at E parent stop; block if exists and its confirmation<zone Order First time. Absent label returns before OA48. Non-null gate-owned match and strict confirmation<zone Order First only; equality not blocked, no identity comparison or independent crossing recheck.

## Accepted ledger reconstruction and export

### OA62 — _rebuild_accepted_order_audit
Set accepted E physical source identities. Invalid S times = explicit invalid roots plus accepted E occupied sources. Snapshot previous ledger with parent causes filtered OA63; clear ledger/index/caches; register B legs. For all S and numbered E (StopAll label where sequence reset source) resolve parent stop and OA40 register if stop. For each numbered E whose physical Order absent: find canonical opposite by First, require matching Break else SimpleNamespace with Order geometry, internal false. Recover valid prior parent-stop causes; initial A audit causes (skip null source/stop); if none and carried-live with S parent, find exact S across original+supplemental matching parent source/index and Order identity and recover A creation. If explicit Order parent cause time non-null, add parent-stop using E parent number if found or StopAll override, family empty at reset otherwise zone family, zone parent stop event/source. Filter OA63; skip if none. Compute exact cross, insert reconstructed ledger row/index. Finally preserve all previous valid parent-stop physical identities even not consumed by final E: merge causes into existing or restore prior entry with causes and index. Return numbered sorted source time,index. Accepted source pair indices int-normalized; invalid S filtering projects time only. Snapshot shallow mapping with fresh filtered parent set; clear specific OA27 caches then register B then original S and numbered parents, supplemental not in registration list. Owner stop uses decision and normalized price, skip None. Existing identity skips recovery entirely. Opposite lookup raw First, normalized Break compared to raw zone Break; namespace copies recorded geometry incl source times and internal false. Initial A truthy list or optional fallback, skip null pair; carried-live S fallback only no causes, first original then supplemental match, int source index/raw other fields; required A attrs added without null check. Non-null explicit cause time only enables cause, actual event zone.parent_stop_event_time; first raw matching E parent, reset label/family override. Repeat OA63 filter; normalize price only for crossing, store original zone level; publish then index. Prior retention requires valid parent causes even if B exists; current row merges only parent set (assert isinstance set), absent row restores shallow prior fields incl B reference with new parent set and index. No final cache invalidation or rollback here; stable raw source time/index sort.

### OA63 — _rebuild_accepted_order_audit.valid_parent_stop_cause
Require nonempty parent-stop cause. Reject S len>4 and source time invalid/occupied; otherwise valid. Ordered falsey/kind rejection; label accessed before len guard; shorter S tuples with accessible label can pass, malformed may raise. No full tuple shape validation or source-index check.

### OA64 — rebuild_accepted_order_audit
OA62 with copy of zones and supplemental S. Shallow list(zones), supplemental sequence passed unchanged; return directly.

### OA65 — ensure_accepted_order_audit
Snapshot prior ledger with copied cause sets; OA62 on supplied zones. Invalid S source times from invalid roots union new accepted E identities. For prior identities absent in rebuild filter S causes at those times; skip if no causes and no B causes. Restore row and confirmation index. Invalidate carried, return rebuilt zones. Preserves pre-existing StopAll/history orders. Snapshot shallow row and new parent set (B/geometry shared). After OA62 union actual invalid/accepted source pairs then project times; skip current identity without merging. Filter absent preserved causes only exact S label len>4 and invalid source, no kind check (unlike OA63). B-only may restore. Publish then index original confirmation; no cross recompute. Unconditional carried invalidation on normal completion, no extra post-stop flush; return rebuilt sorted zones.

### OA66 — _parent_stop_cause_key
Tuple parentType,parentFamily,eventTime,parentSourceTime via get. All get defaults None; no kind component or normalization; mapping use requires hashable values.

### OA67 — _collect_s_ledger_entries
Null detector => empty. Per S ledger entry use a_causes or fallback source/stop pair; optional accepted A filter; skip empty. Pair original entry with list of parent-stop cause dicts (A,null family,event,source). Truthiness fallback uses required source/stop keys; filter only non-null accepted set (empty excludes all). No null pair rejection or dedup; original entry reference and fresh dictionaries in supplied order.

### OA68 — _collect_e_ledger_entries
Per E ledger entry sort causes by str; convert parent-stop tuples to dict, excluding A sources not accepted if filter present. Extend B causes, append pair if nonempty. Stable native str sort before filtering; exact kind parent-stop, A exclusion only if filter non-null and source absent. B extend in input order by reference, no filter/dedup; original entry retained.

### OA69 — _merge_prepared_identities
Combine entries in input order; filter First index to inclusive window unless required identity. First entry wins geometry; later identity extends distinct causes. Use entry stop_cross if key exists (including null), otherwise detector.cross_order. Output dict entry/reaction/causes/crossed, preserve first encounter order. Normalize reaction physical indices; window chained inclusive and required override only outside. First list shallow copy preserves its duplicates; later generator extends against growing list by full equality, no recomputation for existing identity. Explicit null crossing retained; missing key calls detector.cross_order with unchanged level/confirmation. Original entry/reaction refs retained.

### OA70 — _single_owner_parent_stop_causes
For each exact parent cause key select physical row min (confirmation,First,Break), first tie. Retain all non-parent causes; parent causes only when row object is selected owner. Mutate retained rows' causes, drop rows with no cause. Rank computed even no parent causes; absent or strict smaller replaces, equal first. Second pass owner tested by object identity; retain non-parent unconditionally, duplicate winning causes retained. Replace list only when nonempty; omitted row untouched by second pass. Preserve row order.

### OA71 — prepare_order_audit
Normalize required identities set; collect S then E entries; OA69 and OA70. Return prepared rows. Set(required identities or empty) without per-pair normalization; S collector then E, merge then ownership, no final sort/serialization.

### OA72 — accepted_audit_entry
Use a_causes or fallback; filter by accepted source set. No accepted => null. First accepted selected. If original selected source/stop and full list unchanged return original object; else shallow copy, replace selected source/stop and accepted causes. Truthy a_causes else required singleton pair; preserve accepted pair order/duplicates, source membership only (no null/stop test). Compare selected source then stop via get default None, then list(causes) equality, short-circuit; all equal returns exact original row. Otherwise shallow copy and replace only three A fields; reiterability assumed.

### OA73 — accepted_audit_entries
Map physical identities to non-null OA72 results. Input mapping order, OA72 once per row, retain non-null under original key (no key normalization).

### OA74 — order_identity_is_internal
Both order First/Break required; check normalized identity in internal identities, else false. Read both optional attributes before ordered None guard; zero allowed, int conversion then supplied membership, no bounds validation.

## S-side physical Order_A

## CP384 — W3 OA01 independent local qualification

Full-record equality after relabeling is not physical Order identity. A missing source key defaults to None, which can match a supplied None mapping key. Native copy, string, membership and mapping failures propagate. See [independent foundations review](Chronology/CP384_W3_B05_Order_Audit_Foundations.md). This is not caller or ledger acceptance.
