# E — Recursive candidate formation, ownership and numbering (V3)

**Conventions:** B = bullish, R = bearish. A strict trend stop means Low < level for B, High > level for R; improvement uses the same predicate. Main source identity and exact event chronology are separate. Preserve Decimal representation, operation order and stable ordering. Required record fields/defaults are in [record interfaces](../../Contracts/Declared_Record_Schemas.md); shared searches in [Index and cache contracts](20_Indexes_And_Caching.md). Procedure labels identify semantic operations, not required implementation symbols.


## E-M01 — Module boundary and initialization

Consume accepted/provisional S roots, trend/opposite native Reactions and Resets, chronology, initial accepted A Order ledger, blocked First gates, independent Order_B legs and explicit sequence-priority service. Invalid S identity set identifies calculation evidence without native creation rights. Construct full/bounded range, main directional extreme index or sparse table and independent physical audit state. Empty candidate collection returns empty numbered result. Do not use lifecycle display filtering as a substitute for E candidate acceptance.

## E-M02 — One global Order race per stopped parent

Parent (S or E) must strictly stop from its exact decision, searched over lower [max(decision,range_start),range_end). No main fallback. Collect unconsumed S Blue Orders (S only), gate-owned initial query (preserve dependency evaluation), carried-live before registering parent audit, register parent-stop cause, then query post-stop accepted stream and direct candidates. S without carried candidates bounds continuous direct selection by earliest inherited crossing or range end. E enables trend-leg continuation. These are creation/reuse contracts in [Order Audit](08_Order_Audit.md), not E-created geometry.

Merge crossed-only direct, inherited, carried and post-stop accepted by (exact strict Order stop, negative physical First index). Group post-stop stream by equal stop and reorder each group by this same key; do not reduce each route prematurely. Equal merge keys preserve route order. For each candidate, source = directional extreme over COMPLETE main candles containing parent stop through max(parent stop,Order stop), inclusive. Earliest equal main extreme wins. Reject Order whose only creating cause is disowned S or prospective same-source S under native ledger predicate. First remaining candidate wins. Source price is frozen; decision = max(parent stop, Order exact stop), main index mapped from that instant. Output E with parent identity/type/price/stop and full native Order identity/geometry/causes plus source and decision. If no accepted crossed Order, no E.

## E-M03 — Provisional discovery and candidate chains

First register stopped S parents in sorted source order before recursive discovery; then each stopped S opens independent chain of its family, number starting 1. Stop repeatedly at each E decision and run same race. Terminate when no stop/no child or duplicate source index in current chain (not a fixed depth cap). Retain every candidate, not just earliest root. If invalid S roots conflict with opposite-family E continuation at their source, discard whole affected chains. Reconciliation alone owns final family/number. Root continuation from consumed S evidence requires independent cause if invalid S and respects sequence reset between parent and child; see lifecycle.

## E-M04 — Reconciliation algorithm

Maintain min-heap of source groups ordered by earliest source time, earliest decision, source index; numbered sequence, accepted source identities/times, active E list, optional sequence_start. At each source:
1. Reopen parent Order race if a previously usable Order has become only-disowned-S and parent is eligible. In checkpoint replay this forces complete reconciliation restart; otherwise enqueue regenerated candidate with same physical ownership checks.
2. Reject invalid Order (disowned S, gate-owned earlier Order blocking, invalid S root with no independent cause) and inactive parent. S parent must exist and not itself be accepted E; cannot predate hard sequence boundary via own/A source. Against preceding numbered E, permit rebuilt S with own source later and A source not earlier, or an unused Red S dominating Blue E with earlier source. E parent eligible if boundary source, active physical parent, or specifically traced skipped invalid parent; actual winner still requires active physical parent or boundary.
3. Remove S candidate when it strictly stops an active E after that E decision, and owner is Red or candidate Blue, and an owner child decision at/after candidate decision exists. Prefer subset not blocked by a still-unaccepted later Red S before Blue E parent stop, if subset nonempty.
4. Choose highest parent ownership priority (S blue 1,E blue 2,S red 3,E red 4, actual active E family when present); ties earliest decision, then parent stop, then encounter. Reject if winner's E parent is not actually active or boundary.
5. Identify active E strictly stopped by winner price and strictly later decision. Number/family: actual Red parent -> Red, max stopped Red+1 or 1; otherwise any stopped Red -> Red max+1; otherwise Blue parent -> Blue max stopped Blue+1 or 1; otherwise stopped Blue -> Blue max+1; else original family/1. Remove all stopped active identities; append frozen replaced family/number. If source is sequence reset, clear active and set sequence_start instead of adding. Only regenerated winners discover additional descendants; enqueue later source only.
6. Collect accepted lineage stop evidence (seen identities). Preserve native numbered tuple for cache; project E parent type to StopAll only when parent source in sequence reset map. No rewriting physical Order or geometry.

## E-M05 — Final conflicts, restoration and audit

Same physical (source index,time) conflict: greater E family priority wins, same family higher number, equal keeps first. Final order source time,index,decision event. Consumed S evidence may replace descendants only when new direct continuation decision strictly earlier than existing earliest child; keep owner, remove descendants by ancestry walk, resolve same-source conflicts. Independent S root restoration considers only roots whose S parent still accepted and not dominant E source; use heap of roots, rerace when only-disowned cause, preserve earliest direct S-parent geometry selection and conflict resolve. Rebuild canonical accepted ledger after any branch replacement/restoration; historical valid cause retention is ledger-owned.

## E-M06 — Continuation contracts and errors

Live E history scoped by first main/timeframe and feedback scope; track dirty instant, stop progress, main extremes, zones, exact candidate evidence/steps, accepted identities. Reuse settled strict-before-dirty evidence only under keys; re-open forces full race restart. No fixed recursive cap; duplicate sources/cycle seen sets and strictly advancing event gates bound intended native paths. Unknown priorities/directions, missing records and invalid bounds follow explicit errors; no broad catch other than reopened reconciliation control. Exact cache procedures below.

## Detailed E procedures

### E01 — LiveEContinuation.__init__
Initialize chronology, scope, dirty time, main index null. Fresh current and previous dict pairs for stops, extremes, zones, reconciled results, scoped reconciliations. No external state.

### E02 — advance
Input chronology and keyword first_dirty_main. Require nonempty times and index 0..len inclusive else ValueError. Scope=(first main time,timeframe), dirty=time at index or last+timeframe. Same scope retains old current dicts as previous; changed scope uses empty previous dicts. All five current dicts fresh; clear main index; retain chronology and scope. No calculation. Scope equality alone is not proof of market prefix; caller supplies dirty evidence.

### E03 — _dirty_time
Require detector.chronology is retained chronology and dirty non-null, else ValueError. Return dirty.

### E04 — first_stop
Inputs detector,start,level,keyword less and search callback. Validate via E03. Key=(less,start,Decimal level) (numeric equality, not string). Use current progress else prior; prior with null event OR event>=dirty becomes new progress(min(old scanned_until,dirty),null). Store non-null progress in current. If event exists return only if event<range_end else null. Else resume start=max(start,scanned_until). Start>=range_end => null. Call search(start,range_end,level); store progress(event or range_end,event); return event. End exclusive through search; no coarse fallback.

### E05 — extreme
Validate E03; key=(direction,start index,end index). Current hit else prior only if main time at end<dirty. If absent, lazily build reaction_engine LowerTimeframeIndex over detector.candles once per advance; directional range_minimum/maximum on [start,end+1); result (integer candle.index,main time,price). Store current and return. Shared main index used for both directions.

### E06 — zone
Validate dirty. Match 9-tuple (Order number,object,confirmation,stop level/source index/source time,cross tuple,causes,cause time), assert cross non-null. Key includes detector direction,family,number,parent type,parent source index/time/string price,stop event,Order number/First/Break/mode/top source/string top/bottom source/string bottom,confirmation/string level/stop index/time/cross/causes/cause time,source index/time/string price. Use current else prior only if max(stop event,cross exact event,confirmation)<dirty. Else build E32. Store and return same selected object. Never reuse before native race selects same Order key.

### E07 — reconcile
Validate dirty. Empty candidates delegates E44 and returns numbered only. Else gather physical candidate Order identities sorted; ledger evidence per identity=(entry exists,in initial ledger,bool Order_B causes,frozenset causes or empty tuple). Group by candidate source_index, preserving candidate order, dependency tuple=(repr zone,ledger evidence,blocked-by-gate query result,sequence priority(parent_type,red),priority(parent_type,blue),parent_source_index for E else own source index). Group S parent evidence by source index with source_time,A source time,decision exact time,color. Resets frozenset items; validity=(invalid S identities frozenset,visual lifecycle starts frozenset). Evidence tuple=(groups,parents,resets,validity). Scope=(direction,live_scope); cache key=(candidate object IDs in order,groups tuple,parents tuple,resets,validity). Current or previous exact hit: save under current key/scope, restore last candidates list, accepted set and union lifecycle starts, return copied numbered list.
Otherwise previous scoped result if any; steps empty, frontier=0, checkpoint null. If prior and validity equal: frontier=main index of dirty; compare union old/new group keys, rewind to min(frontier,changed source,all affected parent-source indexes); rewind for changed S-parent groups, symmetric difference resets mapped to main. Find lower bound previous.steps by step.source; keep preceding steps; checkpoint=step at position else last step and remove last retained step. Call E44 with checkpoint arguments. Catch only _ReopenedERace, clear steps and restart E44 without checkpoint. If reconciliation did not dynamically reopen, save immutable _ReconciledE (original input candidates tuple,numbered tuple,accepted,lifecycle starts,evidence,steps,native tuple), both maps point same record. Return numbered list. No broad exception suppression.

## E detector

### E08 — EZoneDetector.__init__
Inputs direction,trend/opposite Reactions,S zones,opposite resets,chronology; start_index=0,end=null; direct_geometry_finder null; blocked_order_first_times null; e_parent_order_first_exceptions empty frozenset; initial_order_audit null; sequence_resets null; sequence_priority null (required at runtime); invalid_s_root_identities null; order_b_legs empty tuple; live_continuation null; live_scope empty tuple. Validate direction and non-null priority resolver separately. Store policy, priority; copy invalid identity set; fresh accepted identities; assign resets via E10 (copy and sort). Opposite direction via chronology. Shallow reaction lists; stable sort S by (source_time,integer source_index), resets by E11. Retain candles/lower/times/index/timeframe. Integer start and end or last; derive range [times[start],times[end]+timeframe), no explicit range check. Shared main-extreme callable initially null. Candidate index=chronology.main_range_index if present; if null and timeframe seconds==1 use lower index. Nonlive and candidate index.candles IS detector candles: take range_minimum B/range_maximum R or null. Nonlive with no callable initialize sparse E15. Store callback, blocked set or fresh empty, exceptions, initial ledger or fresh empty, tuple of legs, live continuation/scope. Invoke mixin initialize_order_audit, fresh visual lifecycle starts, consumed S evidence and last candidates lists.

### E09 — sequence_resets getter
Return stored dict itself.

### E10 — sequence_resets setter
Copy resets mapping, sort keys into _sequence_reset_times. For each existing non-null cache named _order_candidates_cache,_carried_orders_cache,_post_stop_orders_cache,_direct_parent_stop_cache clear it. Missing attrs tolerated. No broader state reset.

### E11 — _reset_time
Return chronology.reset_time(reset).

### E12 — _main_index
Return chronology.main_index(value,clamp=true).

### E13 — _first_cross_position
Inputs left/right positions, level, keyword less. Lower index present: delegate first_less or first_greater. Otherwise scan range [left,right), normalize Low if less else High, return first strictly < or >. Null absent. No main fallback.

### E14 — _stop_value
Normalize attribute from policy extreme_attr, return.

### E15 — _initialize_main_extremes
Read optional chronology._e_main_extremes dictionary; use direction cache if non-null. Otherwise build normalized main directional value list, integer candle code list, E16 sparse table; if chronology dict exists store triple. Cached hit assigns shared lists/table to detector. No new dict on chronology if absent.

### E16 — _build_extreme_sparse
Values length n, empty=>empty list. Level0 positions 0..n−1. For k starting 1 while 2^k<=n, compare previous level positions i and i+2^(k−1) over width n−2^k+1. Choose lower value B/higher R; if neither strict comparison wins choose smaller position (earliest tie). Append level; increment k. Return table. Uses exact normalized values, no price transform.

### E17 — _extreme_position
Inclusive [left,right], length=right−left+1; <=0 returns left. k=floor(log2 length) via bit_length−1; compare stored positions for intervals starting left and ending right of size 2^k. Directional strict extreme wins; equal choose smaller position. No bounds clamping here.

### E18 — _first_parent_stop
Start=max(source_time,range_start). Nonlive E19(start,range_end,level); live E04 with less=(direction B), search bound E19. Return (clamped main index,event) on non-null else null.

### E19 — _search_parent_stop
Delegate E21 with less=(direction B).

### E20 — _search_order_stop
Delegate E21 with less=(order_direction !=bearish).

### E21 — _search_strict_cross
Lower-bound start/end, E13 [left,right), return lower timestamp on non-null position else null.

### E22 — _cross_order
Nonlive call mixin superclass implementation. Live key=(start,level); cache hit validates live dirty then returns nullable result. Otherwise E04 from max(start,range_start), less=(order_direction !=bearish), search E20. Hit maps clamped main index and main time; result (index,time,event), else null. Cache current. Exact stop chronology not recomputed by caller.

### E23 — _confirmation_for
Return chronology.reaction_confirmation(direction,reaction), default intrabar behavior.

### E24 — _confirmation
Return E23(reaction,order_direction).

### E25 — _reaction_first_time
Return times[integer reaction.first_idx].

### E26 — _parent_stop
Parent type parameter unused. Start parent.decision_event_time, normalize parent.price; return E18. Includes exact confirmation event, not source main start.

### E27 — parent_stop
Public delegate E26.

### E28 — _extreme_between
Map start/end exact times to clamped main indexes. Start=max(detector start,mapped); end=min(detector end,mapped); if end<start set end=start. Include COMPLETE boundary main candles, even prices after exact stop. Live E05 else E29.

### E29 — _find_extreme
If shared callable and valid 0<=start<=end<count, query [start,end+1), return (integer candle.index,time,value). If shared callable but invalid bounds and sparse absent initialize E15. Otherwise E17 then return cached code/time/value. No additional clamping.

### E30 — _zone
Inputs family,number,parent type/object,stop event, optional keyword e_owned_source_times null. For S only get mixin unconsumed S orders else empty. Invoke gate-owned initial Order query (result local unused but preserve call). Get carried orders, register parent audit, obtain lazy post-stop accepted stream. If S and no carried: continuous deadline=min(exact stop of inherited crossed entries,default range_end); otherwise null. Get direct candidates from mixin order_candidates(stop_event,deadline,allow_bounded_continue=S,allow_trend_leg_continue=E,e_parent=E). Choice key=(exact crossing event,negative integer Order First). Sort crossed-only direct/inherited/carried independently by key; merge those streams with E31 post-stop stream in route order on exact ties. Owned sources = supplied set if non-null, else source times from accepted E identities. Iterate choices: prospective source E28 from stop to max(stop,Order cross event); skip if mixin says Order created only by disowned S for physical First/Break,owned times,prospective source time. First remaining match wins. Null if no match. Live E06 else E32 builder with selected match/source. No route-local reduction discards later First before global tie-break.

### E31 — _zone.post_stop_choices
Generator over post-stop accepted stream grouped by consecutive exact stop event; sort each group by choice key from E30 (later First first), yield entries. Upstream stream order must already group equal stop times. Does not materialize all groups at once.

### E32 — _build_zone
Unpack 9-field Order match, assert cross non-null. Decision exact=max(parent stop,Order cross event), main index/time clamped via E12. Source index/time/price supplied; parent stop main index/time mapped. Return EZone fields: stored direction, family/number/parent type, integer parent source index/time/normalized price, stop tuple; stored order_direction, order number/mode, causes and parent-stop cause time, integer First/Break and times, confirmation, normalized box top/bottom with integer source positions/times, match stop level/source index/time, source tuple, decision tuple. No extra stop or source query.

### E33 — set_consumed_s_evidence
Replace stored evidence with list of (original S object,(integer owner.source_index,owner.source_time)) in input order. No copy of S.

### E34 — _apply_consumed_s_evidence
Fresh result list; for each stored S/owner identity, choose first matching owner in current result, skip absent. Build E35 continuation, replace result via E36. Return final list.

### E35 — continuation_chain_from_s
Inputs stopped E owner,S evidence, optional independent_a_order_identities empty frozenset. S source identity=(time,integer index). If equals owner or already accepted E => empty. First strict S stop E26 absent => empty. Family string owner.family, number=int(owner.number)+1; parent initially S. Fresh chain, seen source-index set, owned times from accepted plus owner. Loop E30 with owned set; null or repeated source index stops. If E41 invalid S without other Order cause and physical Order not in independent A set, stop. If mixin sequence reset between parent source and child source, stop. Append zone, mark source/time; next E parent stop absent terminates; else update parent type E,parent,stop,number++. Return chain. No artificial depth cap.

### E36 — replace_with_earlier_continuation
Empty continuation => copy base. Owner ID=(index,time); map base by ID (last wins). Define E37 ancestry check. Direct E children of owner; if any choose earliest (decision exact,source time), and continuation first decision>=winner decision return unchanged copy. Else remove all descendants via E37, merge kept then continuation, E38 same-source resolve; replace accepted identities set from selected (time,integer index), return. Equality does not replace existing branch.

### E37 — replace_with_earlier_continuation.descends_from_owner
Walk current while parent_type E; parent ID==owner =>true; repeated parent ID=>false; add seen, follow base map if exists else false. Non-E parent=>false. Local seen each invocation.

### E38 — resolve_same_source_conflicts
Physical identity=(integer index,time). Traverse zones; first entry wins initially; replace only E39 says outranks. Keep original encounter order of identity keys; then stable sort selected objects by (source_time,source_index,decision_event_time). No renumbering or provenance rewrite beyond choosing object.

### E39 — resolve_same_source_conflicts.outranks
Compare shared priority("e",family): unequal higher wins. Same priority AND same family with unequal number =>higher number. Otherwise false, preserve incumbent. Uses injected priority resolver, no independent hardcoded table.

### E40 — restore_independent_s_roots
Dominant sources set(index,time); accepted S roots exclude same physical source. Select last candidate zones parent_type S, integer number=1, parent in accepted S, not E41 invalid. Result copy dominant zones. Heap root tuples(source time,index,ordinal,root), ordinal initial enumeration; known root set. While heap: pop; skip if parent ID now dominant. If native Order only by disowned S (owned times from dominant), locate first matching S via next (absence propagates), E30 replacement family/1/S/parent/old stop with current owned times; enqueue unique non-null replacement, increment ordinal; continue. Otherwise find same-S-parent zones in result. If any choose min(decision event,source time), remove by object identity, append root; else append only if no identical source/parent identity and parent type. Add root source to dominant even if not appended. Finally E38 conflicts and reset accepted identity set. No candidate-root creation from consumed S not in self.s_zones.

### E41 — _invalid_s_without_order_cause
False unless parent type S and (parent time,index) in invalid S set. Physical Order in initial audit =>false; missing current entry=>true; truthy Order_B causes=>false. Else collect invalid S times; return NOT any cause tuple with kind parent-stop AND not (parent type S and cause[4] invalid S time). Thus independent cause permits invalid root geometry, not new invalid-S cause.

### E42 — _discover_candidate_chains
First pass all sorted S: E26 strict stop; register S audit and save stopped parent for each hit BEFORE walking chains. Second pass each stopped S: family string color, number=1,parent S, fresh chain source set/list, owned times from accepted. Loop E30; absent or repeated source index breaks; append to chain and candidates, mark source/time, parent=E zone; next stop E26; absent break, else number++ and continue. Retain nonempty chain keyed original S. If no invalid identities or no candidates return candidates. Else map physical (time,integer index) of E-parent continuations to family set. Block invalid S root identities whose source has any continuation family != S color. If none blocked return candidates; else flatten only unblocked original chains in order. No sequence reset filter in this discovery loop; reconciliation owns hard gates.

### E43 — _reconcile_candidate_chains
Live E07 if available, else E44(candidates)[0].

### E44 — _compute_reconciliation
Inputs candidates, keyword steps/checkpoint/previous defaults null, frontier=0. Group by source_index; heap of (min source_time in group,min decision_event_time in group,source index) for sources>=frontier; scheduled set. known=set(candidates), regenerated empty; _reconciliation_reopened=false. If checkpoint supplied restore numbered prefix from previous.native_numbered up to count and active list from checkpoint; else empty. accepted_sources=(time,index) set, accepted_source_times, set detector accepted to same set; sequence_start from checkpoint or null. Map candidates by (index,time), last wins; S map by (integer index,time), first wins. Build indexes via E45 for retained numbered; child max decision per E parent via E46 for all candidates.
Heap loop:
1. Pop source, remove scheduled; if steps supplied append snapshot BEFORE source processing (source,count,active tuple,sequence_start). Get group (list shared with by_source).
2. For each group item whose Order is only created by disowned S and E49 parent_active, locate parent in S map or numbered map. Missing skip. If checkpoint supplied raise _ReopenedERace to restart. Else family/number from S item or numbered E parent family/number+1; mark reopened; regenerate via E30 with accepted source times, E47 enqueue.
3. Eligible items satisfy E48 valid_order and E49 parent_active. Empty skip. Remove S-parent item when it stops an active owner via E50, (owner red OR item blue), and max child decision for owner exists >= item decision. Empty skip.
4. Prefer current_owners subset excluding E-parent blue item if any still-unaccepted Red S has source strictly after its parent source and decision strictly before item parent stop. If subset nonempty replace eligible, else retain prior eligible.
5. Winner = min by (negative E51 ownership priority,decision exact time,parent stop exact time), first tie. Build stopped_by_family red/blue lists for active owners E50 says stopped. Require parent active: parent type S OR parent source time==sequence_start OR exact parent ID in active. If false skip; recursive ancestry eligibility alone does not bypass this hard check.
6. Actual parent family=first active E parent matching source time if exists, otherwise zone.family. If parent red: family red, number=max(stopped red numbers)+1 or 1. Else if stopped red nonempty: red,max+1. Else if parent blue: blue,max(stopped blue)+1 or 1. Else if stopped blue nonempty: blue,max+1. Otherwise original family,1. Remove all stopped active identities, replace winner family/number, append numbered, E45 index, add accepted identity/time. If original zone source time in sequence_resets clear active and set sequence_start; else append numbered zone.
7. Only regenerated original zone triggers new descendant query; if E26 next stop exists set reopened=true, E30 child with numbered family/number+1 and current owned times; enqueue only non-null child whose source_index>current source.
After heap, E52 collect lineage on each numbered with shared seen, add lifecycle starts. If steps present append terminal snapshot(source=len(candles),count,active,sequence_start). Save native tuple before projection. Replace each numbered parent_type E with StopAll if parent_source_time is a sequence reset key; other fields unchanged. Set accepted identity set and last candidate list (including regenerated). Return (projected numbered list,native tuple). No arbitrary iteration cap; heap ties use source index after two time fields. Dynamic regeneration copies original candidate list on first addition; may mutate detector audit through E30.

### E45 — _compute_reconciliation.index_numbered
First numbered wins (index,time) map and first at each source time. If new time, append if strictly after current last else sorted insertion. If parent_type S add parent time to numbered_s_parent_times. Mutates captured indexes only.

### E46 — _compute_reconciliation.index_child
If zone.parent_type E, map parent ID to maximum of old child decision (default zone's own) and current child decision. No mutation for other type.

### E47 — _compute_reconciliation.enqueue
Skip null or known zone (record equality/hash). If regenerated empty, shallow copy candidates before first addition; add to known/regenerated, append candidate, set candidate-by-ID map (overwrite), E46 index, append group. If different source than current and not scheduled, push (zone.source_time,decision event,source index), add scheduled. Current source group appended but not separately scheduled.

### E48 — _compute_reconciliation.valid_order
False if mixin only-disowned-S cause query for physical Order and accepted times/source time true. Otherwise true iff not blocked-by-gate AND not E41 invalid S without cause, short-circuit.

### E49 — _compute_reconciliation.parent_active
For S parent: retrieve exact parent ID; missing or parent source accepted as E =>false. If sequence_start exists and parent source<=sequence_start OR A source<sequence_start =>false. Position lower_bound(numbered_times,zone.source_time); no earlier=>true; prior time<=sequence_start when set=>true. Else prior=first numbered at immediately preceding time; return rebuilt_after_e (parent S source>prior source and A source>=prior source) OR dominant_s (S red, prior blue, S source<prior source, S parent not already used by numbered S root). For non-S: parent source==sequence_start=>true (hard gate not active family); exact parent in active=>true. Else use supplied seen or fresh, cycle=>false; add parent identity; find skipped candidate parent; return true iff exists, E48 false, E41 false, AND recursive E49 true. No recursion cap beyond seen.

### E50 — _compute_reconciliation.stopped_by
Return false if candidate decision<=prior decision. Else strict candidate.price<prior.price B or > R. Equality never stops. No direct market rescan in this predicate.

### E51 — _compute_reconciliation.ownership_priority
Find first active E parent by matching parent source time only if item.parent_type E. Family=parent.family if truthy parent else candidate.family. Return injected priority(item.parent_type,family).

### E52 — _compute_reconciliation.collect_lineage
If zone physical (index,time) seen return; add, add parent_stop_event_time to visual_lifecycle_starts. Stop if parent_type S. Otherwise lookup candidate parent by ID; recurse if exists. Shared seen across numbered traversal, no public visibility edits.

### E53 — detect
Clear accepted identities; mixin clear audit; register Order_B reset legs; clear visual lifecycle starts. E42 candidates; store shallow last candidates; E43 reconcile; E34 consumed S evidence; E38 same-source conflicts; return mixin rebuild_accepted_order_audit(numbered). Audit rebuild may return replaced records; do not claim direct list is final native accepted ledger without this step.

### E54 — detect_e_zones
Construct EZoneDetector with positional direction,trend/opposite reactions,S,opposite resets,chronology,start=0,end=null,direct callback null; keyword blocked first times,initial audit,priority,invalid S identities default null. Other constructor parameters defaults; call detect. Required priority at runtime even though wrapper default null.
