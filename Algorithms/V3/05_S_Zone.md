# S — A ownership, order-free and Order-backed decisions (V3)

**Conventions:** B = bullish, R = bearish. Parent directional extreme is Low for B and High for R; strict parent stop/improvement means lower for B and higher for R. An opposite Order has its own direction and strict predicate, not the parent predicate. Use Decimal normalization and native arithmetic order; preserve source/main versus exact-event times, physical identity, original order, and nulls. Use [record interfaces](../../Contracts/Declared_Record_Schemas.md) and [chronology/index services](20_Indexes_And_Caching.md). Procedure labels name semantic operations, not required implementation symbols.


## S-M01 — Inputs and preprocessing

Input full parent-direction Reactions/Blue/A and opposite-direction Reactions/Resets, chronology, optional bounded main range and independent initial Order geometry. A records sorted by (Reaction Break main time, source index). Precompute S04 returned trend confirmation times (RE61 default intrabar flag, possible Break-open fallback) and First indexes; sorted-by-confirmation index is independent of original reaction ordinal. Reset Blue map retains first valid Reset formation per reaction number, even internal. Public Blue formation list excludes invalid/internal. Opposite reset events sorted by exact time, with owner confirmation map keyed physical First. Initialize S-owned A windows and physical Order audit.

## S-M02 — A-to-S ownership and provisional audit

First audit every stopped A, including candidates later excluded. Find strict A stop from its S07 returned Reaction confirmation (possible RE61 Break-open fallback), not source main open; if lower window nonempty, use first strict lower crossing, no fallback on a miss. If lower empty, scan main from lower_bound(start). The immutable first physical Order_A choice is shared with [Order A](06_Order_A.md).

For each sorted A, use exact source event reconstructed from first matching price in source main (main-time fallback). A is S-owned when first matching window contains source event (inclusive start, exclusive end or open). Escape if trigger is strictly after window start; also the closed-window reset-reset exception requires both Blue identity/time conditions of S26. Keep the first window decision. Skip A before cycle start or equal after output exists; skip if no strict stop, or stop >= next A confirmation. Open ownership at stop even when no S result. Resolve S candidate; if success, close window at max(stop, decision exact+1 microsecond), move cycle start to S source. No result leaves window open. Output sorted source time,decision event; exposed eligible A excludes owned A but native audit initially includes all stopped A. Final accepted A filtering belongs to lifecycle.

## S-M03 — Independent routes before first Order

Deadline = selected Order confirmation or range end; search both order-free routes before considering Order-backed branch.

| Route | Eligibility | Frozen candidate | Decision |
|---|---|---|---|
| Type3 Blue | Opposite Reset strictly after A stop and before deadline; owner confirmed no later than A stop; first owner Reset not already at/before A stop | Last equal directional extreme from opposite owner Break through Reset main | Strict candidate crossing from Reset to deadline exclusive; trend confirmation in (A stop,crossing] required |
| Type4 Blue | Trend confirmation in (A stop,deadline), Break main not before A stop main | Last equal extreme A-stop main through aligned Break | Strict candidate crossing from max(aligned confirmation, candidate event,A stop) until min(next aligned confirmation,deadline); a public valid Blue must form from candidate source main through crossing inclusive |
| Order-backed | No eligible Type3 or Type4; physical Order exists | Simple or advanced geometry below | Independent race |

Choose earliest exact Type3/Type4 event; true event tie goes Type3. Both routes output Blue and no Order provenance; only Type3 keeps Reset owner/time. If no route and no Order, no S.

## S-M04 — Order-backed geometry and race

Use canonical opposite Order stop. Legacy timing compares opposite Order box boundary to A-stop main directional extreme: B after iff Order bottom <= A-stop Low; R after iff Order top >= A-stop High. If after, nested aligned trend Reaction can preserve after; otherwise compare exact pre-order candidate event with Order First main and choose before only when strictly earlier. Pre-order geometry clips A-stop main lower rows from exact stop onward; compare later main extremes through Order First, retain stop-main on ties. No lower rows -> full-main candidate. Attempt pre-order race with fallback enabled; if neither event or tie -> null, if unqualified candidate wins -> abandon that candidate and resolve aligned geometry; if qualified or Order wins -> keep pre-order route.

Aligned advanced when a trend Reaction First is strictly later than Order First and before Order confirmation, Break <= Order Break, confirmation <= Order confirmation and contained box inclusively. Source is Order opposite edge's recorded main source (Low B / High R); candidate gate nested confirmation. Otherwise simple: first trend Reaction confirmation strictly after Order; source = last equal directional extreme Order Break..aligned Break inclusive. Gate at aligned confirmation.

Race starts at Order confirmation and uses lower data when any exists in range. Order strict crossing is independent. Candidate gate = max(scan start,candidate_start); normal candidate requires either aligned Reset Blue or ordinary trend confirmation strictly after behavior_start, earliest qualifier determines lower search start; fallback mode first searches unqualified and upgrades to Blue if a qualifier exists by crossing. Earliest lower position wins; same row with both eligible => no decision. Red = Order; Blue = qualified candidate; fallback is internal only. Main-only fallback scans containing main through range end; both raw main predicates on same candle => null even if candidate unqualified; Order first otherwise; candidate Blue requires qualification; unqualified fallback only when enabled. Never fallback just because lower search missed. Red source stays pre-order source only when that route won; otherwise earliest equal extreme Order Break..decision main. Blue keeps selected source. Populate full parent A and physical Order provenance, formation type simple/advanced, exact decision and owning main.

## S-M05 — Shared accepted Order reconciliation and continuation

Once E supplies accepted ledger, deduplicate physical entries by First/Break (replace missing-cross entry only when new has crossing), require own confirmation < stop. Sort by (stop,confirmation,First,Break); for each S choose earliest stop >= frozen source main and strictly earlier than its current decision. Convert to Red and replace Order/decision provenance, retain source/price, A identity and formation type; clear Reset provenance. No new Order creation here. Live S caches resolved non-null decisions only if the route-specific settled-through guard and dependency frontier permit reuse (Type3/4 directly use decision time; Order-backed guard tests lower-row presence, not a crossing proof); dirty includes changes in trend/opposite geometry, reset/Blue events and scope. Full details below.

## Detailed S procedures

### S01 — SZoneDetector.__init__

Inputs direction, trend/opposite Reactions, trend Blue lines, A zones, chronology, optional start/end indices null, opposite resets empty tuple, initial_order_geometry callback null. Validate exact direction else ValueError. Store policy, order_direction=chronology.opposite_direction(direction), shallow lists of Reactions/resets/Blue, callback. Stable sort A by (reaction_break_time,integer source_index). Store references to chronology, candles, seconds, timeframe, main/lower times and index. Default start=0/end=last, otherwise integer conversion. Require 0<=start<=end<candle count. Range [main start,main end+timeframe). Fresh order_audit map, a_ownership_windows list and reset-Blue formation map. Call mixin stopped-A lookup initializer.
For each calculation-valid line with string kind reset, record first encountered S33 returned formation time per integer reaction number, regardless of internal flag (returned time may be explicit or fallback). Build trend rows (confirmation via S04, integer First, integer Break, 1-based number, original reaction). Keep confirmation list in original order only if exact naive sorted; keep First index list only if valid 0<=First<=Break<candle count for every row and nondecreasing First. Sort trend tuples ascending, store sorted confirmation times. Build opposite confirmation map by integer First (later duplicate overwrites). Stable sort (exact reset event,reset) by event; save times and per-owner sorted lists keyed integer from_first_idx. Save sorted exact formation times of calculation-valid and non-internal trend Blue lines. Constructor has no standalone return. No reordering original inputs.

### S02 — _main_index
Return chronology.main_index(timestamp); mapping policy delegated.

### S03 — _lower_window
Return chronology.lower_window(start,nullable end).

### S04 — _reaction_confirmation_time
Return chronology.reaction_confirmation(direction,reaction), default intrabar behavior (RE61 first strict lower crossing or Break-open fallback). S04 adds no independent proof of a crossing; unlike A14 it does not disable intrabar start.

### S05 — reaction_confirmation_time
Public delegate to S04 with same inputs; no alternate chronology.

### S06 — _reset_time
Return chronology.reset_time(reset).

### S07 — _a_confirmation_time
Read integer zone.reaction_number; require 1..trend count, else ValueError. Return S04 for selected reaction with stored direction.

### S08 — _trend_extreme
Return normalized Decimal of candle attribute selected by policy.extreme_attr.

### S09 — _a_stopped
Return policy.strict_cross(value,level), equality false for ordinary finite prices.

### S10 — _first_a_stop
Scan start=max(input start,range_start). Lower bounds [lower_bound(scan start),lower_bound(range_end)). If nonempty and index exists, first_less B/first_greater R; no hit => null, no fallback. Hit maps exact time to main index and returns (index,main timestamp,event time). Otherwise scan lower slice first strict S09(S08); nonempty without hit => null. Only empty lower: main start=max(start_index,lower_bound(main times,input start)); scan through end_index inclusive, first strict returns integer candle.index and timestamp in both main/event slots. Null absent.

### S11 — first_a_stop
Public delegate to S10.

### S12 — _resolved_order_backed_zone
Delegate S39 with original stopped-A inputs and first physical Order match; never substitute later canonical reaction.

### S13 — _candidate_source
Inclusive main positional range; reject reversed with ValueError. Seed first candle, normalize trend extreme; replace only strict better via policy. Return (integer source candle.index,timestamp,price); earliest tie.

### S14 — _candidate_source_last
Same inclusive range with own reversed-range error; replace on <= for B, >= for R, so last tie. Native indexes, no clipping.

### S15 — _first_trend_reaction_after_order
Input exact Order confirmation. If original confirmation list valid and input exact naive datetime, upper_bound to first STRICTLY later confirmation, return 1-based position, original reaction, confirmation; null at end. Else iterate original order, recompute S04, first confirmation>input. No sorting fallback.

### S16 — _nested_trend_reaction
Inputs Order and confirmation. Read integer First/Break, main First timestamp, normalized box top/bottom. Candidate positions whole trend sequence or upper_bound(ordered First indexes,Order First) through upper_bound(Order Break,lo=left). In original order skip if First main time<=Order First time OR First index<=Order First OR Break>Order Break OR First time>=Order confirmation. Compute confirmation, then compute containment (box top<=Order top first, then bottom>=Order bottom only if top passes), even if confirmation is later than Order. Finally require confirmation<=Order confirmation and precomputed containment. Return (ordinal,reaction,confirmation) first eligible, else null. Equal geometry boundaries allowed, First strict.

### S17 — _simple_candidate
Return S14 on inclusive Order Break through aligned reaction Break.

### S18 — _type3_reset_leg
Resolve reset owner via mixin opposite_by_first_index integer from_first_idx; missing => null. Start=owner Break index, end=main mapping of exact reset time. Reversed => null; otherwise S14 inclusive Break-to-Reset.

### S19 — _type3_has_trend_reaction
Upper_bound sorted trend confirmations at A-stop event. True iff next exists and <=crossing. Window (A-stop,crossing].

### S20 — _first_type3
For sorted opposite Reset events in (A-stop,deadline), require owner confirmation exists and <=A-stop; if owner Reset list exists and earliest <=A-stop skip. Resolve S18 leg; skip null. Search lower index strict trend crossing of leg boundary in [reset event,deadline). Skip absent or S19 false for the first hit; no search for a later qualified recross in the same Reset interval. Direct lower_index call has no local null-index or empty-window guard; no coarse fallback. Map decision exact event to main; owner number from mixin map. Candidate tuple (source index,time,boundary,decision index,main time,owner number,reset exact time,crossing). Winner strictly earliest crossing, ties retain first Reset traversal. Return null if none. No lower-data fallback.

### S21 — _type4_has_blue
Window start=main timestamp at candidate source index. lower_bound sorted public Blue formation times; return true iff first >=start exists and <=crossing. Inclusive endpoints.

### S22 — _first_type4
Inputs A stop tuple, deadline. Aligned trend sorted rows confirmation strictly after A stop and strictly before deadline, Break index>=A-stop index. For each aligned row in order, S14 over A-stop index through its Break inclusive. Candidate exact formation via S31 with not_before=A stop. Search start=max(confirmation,candidate event,A stop), end=min(deadline,next filtered aligned confirmation or deadline); skip start>=end, including equal-confirmation windows. Do not merge equal-time aligned rows or use the next unfiltered trend row. Search lower first strict trend crossing in [start,end); skip absent or no S21 Blue from candidate source main time through the first crossing. No rescan for a later crossing within the same window; direct lower_index call has no local null-index guard. First qualifying returns (source index,time,price,decision index,main time,trend reaction number,exact event). Failed candidate is replaced by next aligned reaction; no Order yet, no coarse fallback.

### S23 — _build_type4_zone
Return SZone direction stored, color blue, formation_type type4, A ordinal/source index/time/price and stop tuple from parent inputs; all Order fields and both Reset fields null. Source and decision from type4 tuple; aligned reaction number unused. No price recalculation.

### S24 — _candidate_after_order
First index integer. Start=max(detector start,min(lower_bound(main times,Order confirmation),First)). If anchor_idx non-null and integer>=start, return anchor index/main timestamp/normalized anchor_value (no upper-bound or null-value guard). Otherwise S13 inclusive start..First. Map containing confirmation main index; if containing<start, scan lower remainder [confirmation,containing main end); replace candidate whenever strict trend improvement OR equal price, assigning containing main index/time and lower price. This gives earlier containing main candle on equal candidate price in the remainder branch. The anchor route tests only the clamped index lower bound, not its exact event time, and the min-with-First clamp can include a First main before the confirmation. The local helper does not universally prove absence of pre-confirmation data.

### S25 — _a_source_event_time
Read A source main time and normalized price. First lower row in [source,source+timeframe) whose trend extreme equals price yields timestamp; else source main time.

### S26 — _a_owned_by_s
Calculate source event via S25. Iterate windows in insertion order. Consider first with start<=event and (end null OR event<end). If zone.trigger_event_time exists and >start, return false immediately (independent). Else read both Blue source times, both stop main times and A source time with null defaults. Return false if window closed (end non-null), all five times non-null, start<Blue1 source, Blue1 stop<Blue2 source, A source==Blue2 stop, AND S27 reset-reset. Otherwise return true. No matching window => false. Does not continue to later overlapping window after exception. Trigger exception is evaluated before reset-reset exception.

### S27 — _a_pair_is_reset_reset
Convert both Blue ordinal attrs default 0 to integers then subtract one before either range guard. Test first range then second. Both referenced kind strings (default empty) must equal reset, checking first before second. Use the original supplied Blue list order, with no local validity/internal filter or identity check; caller ordinal alignment requires W2 verification.

### S28 — eligible_a_zones
Property returns fresh list of sorted A inputs for which S26 false, no public display filter.

### S29 — _candidate_timing
Read stop main trend extreme and normalized opposite Order box_bottom B/box_top R. Legacy after if boundary<=stop extreme B or >= R, else before. Before returns immediately. If after and S16 nested trend match exists, preserve after. Else default A stop event to stop main timestamp if null; compute S30 then S31; return before iff S31 returned candidate time<main Order First timestamp, else after (equality after). S31 may return a fallback, not proof of an observed price event.

### S30 — _candidate_before_order
Default A stop event to stop main timestamp. First index integer; initial candidate S13 inclusive stop..First (reversed fails). Query lower remainder [supplied or fallback A-stop time,stop main end), with no extra clamp to stop main open; empty returns the already-computed full-main candidate. Nonempty seed first lower row, strict trend improvement only. If First>stop index compute later S13 on stop+1..First. Return later only if strictly better than lower remainder extreme; ties choose stop main. Otherwise return (A-stop index,A-stop main time,lower extreme). Local lower source reference not output.

### S31 — _candidate_event_time
Source main timestamp; scan [max(source,not_before),source+timeframe) first row trend extreme==level. Return exact timestamp or max(source,not_before) fallback, even if gate after candle end.

### S32 — candidate_event_time
Public delegate S31(source index,price,fallback used as not_before).

### S33 — _blue_formation_time
If explicit formation_time non-null return as supplied. Else integer source index and main timestamp. For kind string !=reset: if valid 1-based trend reaction number, return S04; else source time. Reset: if broken_level null return source; otherwise scan [source,source+timeframe), normalize each selected lower price then normalize broken_level inside that row's selected strict comparison. Empty range never normalizes broken_level. Return first strict crossing timestamp or source fallback. Explicit formation and non-Reset S04 returns are not independent proof of observed crossing.

### S34 — _candidate_cross_has_blue
Reject reaction number outside 1..trend count. Lookup first Reset Blue formation by number; true iff non-null and <=candidate crossing event. No same-candle requirement, no internal filter here.

### S35 — _has_ordinary_trend_reaction
Same temporal predicate as S19 but generic behavior_start/event: first sorted confirmation strictly after start and <=event.

### S36 — _candidate_crossed
Return S09 of S08(candle) and level.

### S37 — _decision
Inputs candidate level, Order stop level, start, trend reaction number, behavior_start, optional candidate_start null, fallback_on_unqualified_cross false. Output null or (family,main index,main time,exact event).
Lower route when [lower_bound(max(start,range_start)),lower_bound(range_end)) nonempty:
1. Find opposite Order stop independently using first_greater if order_direction bearish else first_less across entire window, before candidate qualification. Nonempty lower route calls lower_index directly, without a local null-index guard.
2. Candidate gate=max(scan_start,candidate_start or scan_start). Fallback enabled: qualified start=gate, candidate family fallback. Otherwise obtain aligned Reset Blue time only if ordinal valid; first trend confirmation strictly after behavior_start; if neither exists candidate position null. If any qualifier, qualified start=max(gate,min(non-null times)), family blue; query first strict trend cross from lower_bound(qualified start,lo=left,hi=right) through right exclusive. When fallback enabled do same query from gate.
3. Both null => null; identical non-null position => null (ambiguous), before fallback candidate qualification; equal timestamps at distinct positions do not satisfy this guard. Earlier Order stop or only Order => red. Otherwise candidate exists (assert); if fallback enabled and S34 or S35 true at event, upgrade family blue; return family and mapped time/index.
No-lower route: scan main positions max(start_index,upper_bound(main times,start)−1) through end_index inclusive. Candidate crossing strict plus candidate_start absent or main timestamp>=candidate_start. Order crossing via mixin. Both => null regardless of qualification. Order only => red; candidate plus S34/S35 => blue; candidate plus fallback enabled => fallback; else continue. Main fallback event=main timestamp. No fallback when nonempty lower route merely lacks crossings. Exact equality never strict crossing.

### S38 — _build_type3_zone
Same field mapping as S23 but formation_type type3 and Reset owner number/time from type3 tuple; Order fields null. Source/decision from supplied tuple.

### S39 — _build_order_backed_zone
Inputs parent A/ordinal/price/stop, Order match (ordinal,reaction,confirmation). Obtain Order stop geometry via mixin; S29 timing. If timing before, S30 pre-order candidate else null. Initialize behavior start=A-stop, decision null, use_pre=false.
- Pre-order exists: simple, initial source and red_source=pre-order, aligned number=0. Find S31 returned candidate event time (including native fallback); behavior start=candidate event. S37 race starting Order confirmation with candidate gate at candidate event and fallback enabled. Null => return null; non-fallback => use_pre=true; fallback => clear decision and reconsider aligned geometry.
- If not use_pre, reset behavior start=A-stop and seek S16 nested match. If found advanced: source index=Order box_bottom_source_idx B/box_top_source_idx R; main source time/trend extreme; candidate start=nested confirmation, aligned number from nested; red_source null. Else simple: require S15 first later trend reaction, absent => null; source S17 inclusive Order Break..aligned Break last tie; red_source=pre-order if exists else S24 (computed even though final non-pre Red uses S13); candidate start=aligned confirmation.
- If decision still null call S37 normal (fallback false) with source price, Order stop, confirmation, aligned number, behavior start and candidate start. Null => null.
- Unpack decision. Red: if use_pre and red_source non-null retain it; else S13 inclusive Order Break through decision main index earliest tie. Blue retains selected candidate.
- Build SZone with direction, decision family/color and chosen formation_type, full parent A identity/stop; Order direction stored, reaction number/mode, First/Break integer indexes and main times, exact confirmation, normalized box bounds and integer source indexes/main times, stop level/source from mixin. Reset fields null. Source/decision tuple as selected. No second physical Order search.

### S40 — _resolve_candidate
Deadline=Order confirmation if match exists else range_end. Compute BOTH S20 Type3 and S22 Type4 before arbitration. If Type3 exists and Type4 absent or Type3 exact event<=Type4 exact event, S38. Else if Type4 exists S23. Else Order match exists S12. Else null. Tie precedence Type3; independent of main timeframe color.

### S41 — detect
Delegate S42 with bound S40 resolver.

### S42 — _detect
Fresh output; clear ownership windows and audit map. First audit stopped A for every sorted A through mixin, even later excluded. Cycle start=range_start. Iterate A in order with 1-based ordinal. Skip S26-owned; skip source<cycle start or equal when output nonempty. Compute next A S07 returned confirmation if next exists (even if later ineligible; RE61 may return Break-open fallback rather than observed crossing). Normalize A price, find first A stop after its own confirmation. No stop skip. Compute first Order after stop via mixin. If next A confirmation exists and stop event>=it skip. Append open ownership (stop event,null); invoke resolver. Null result leaves window open and continues. Success append S, cycle start=S.source_time, replace last window with (stop,max(stop,S.decision_event_time+1 microsecond)); includes exact decision. Return stable sorted output by (source_time,decision_event_time). Mutates audit and ownership in-place; failures can leave partial state.

### S43 — reconcile_shared_order_stops
Inputs S records and accepted Order entry dicts. Dedup by (integer reaction First,Break); skip absent reaction; first wins unless retained stop_cross null and new non-null, then replace; dedup preference tests presence, not shape, so a malformed non-null crossing can prevent later valid-entry preference. For each retained entry require confirmation isinstance datetime; normalize stop level. If supplied stop_cross not tuple len>=3 with datetime element 2, compute mixin shared stop cross. A supplied crossing passing that shape test is accepted without independent price-crossing proof or local validation of its first two elements. Require crossing exists and confirmation<exact crossing. Build candidates (cross event,confirmation,First,Break,entry,cross tuple), stable sort first four; store cross times. For each S, lower_bound cross times at S.source_time (inclusive), choose first if its event<S.decision_event_time (strict). No candidate => retain original zone. Winner => replace S color red, full Order provenance from winner entry/reaction (stored order direction, integer reaction number default 0, mode, First/Break, box prices/source times, exact confirmation, stop price/index/time), Reset fields null, decision tuple from crossing; retain original S formation type, A provenance and frozen source/price. Output in input order. Does not reassign Order parent cause or compare winner confirmation to S start beyond own confirmation<cross.

### S44 — _s_reaction_inputs
Return tuple of First, Break, mode, intrabar_start default null, box top source index/string top, bottom source index/string bottom, anchor_idx default null/string anchor_value default null. No numeric normalization.

### S45 — LiveSZoneContinuation.__init__
Scope null, fresh dependencies set and decisions map.

### S46 — LiveSZoneContinuation._current_dependencies
Static: build set for each trend/opposite reaction: (Break main time,side literal,0-based enumeration,S44 tuple). Add (exact opposite reset event,reset,integer owner First), (event,reset-blue,reaction number) from map, (event,public-blue) from times. Set deduplicates; no source mutation. Return set.

### S47 — LiveSZoneContinuation._settled_through
Static. through=S decision event. Type3/4 => through directly. Other types assert Order match. Find lower_bound(max(Order confirmation,range start)); if no lower row or first lower time>through return null. The guard proves only lower-row presence from clamped Order confirmation through decision, not an observed crossing or that the row is inside range_end. Set through=max(through,Order Break main time). If S15 aligned match exists, max with aligned Break main time and exact confirmation. Return frontier.

### S48 — LiveSZoneContinuation.update
Input fresh detector, required dirty main index. Validate 0<=dirty<=candle count. Scope=(direction,timeframe,start_index,range_start). Dirty time=main timestamp at index or range_end at end. Compute S46 dependencies. If same scope, dirty=min(dirty,min(event times in symmetric difference of old/new deps,default dirty)); prior decisions=current stored. Else empty prior. Fresh current map; define S49. Invoke detector S42 with resolver. On success replace scope/dependencies/decisions, return sorted detector output. Detector may mutate even when wrapper not committed.

### S49 — LiveSZoneContinuation.update.resolve
Key=(A ordinal,source index,source time,string price,stop tuple,Order key). Order key null or (number,S44 reaction tuple,confirmation). If previous decision exists and stored through<dirty, copy the same pair reference to current and return stored S. No current-map lookup; omitted A/Order fields depend on caller's frontier and signature sufficiency. Else call detector S40; if result non-null compute S47 and cache only non-null through. Return nullable result. Null not cached. No in-place S edits.

### S50 — detect_s_zones
Construct SZoneDetector forwarding all arguments in signature order/defaults S01, call detect, return. No persistent wrapper state.

### W3 CP375 — constructor and preprocessing forensic qualifications (S01)

The declared frozen/slotted S record separates parent A identity, optional Order/Reset provenance, source Decimal and exact versus main decision time; nullable annotations do not supply defaults or enforce normalization. Constructor copies input lists shallowly and sorts a new A list by Break main time then integer source index with stable ties, without eligibility filtering. Chronology arrays/index and initial geometry callback remain references; callback is not invoked by S01. Native integer conversion precedes the inclusive analysis-range gate; range end is nominal selected last open plus timeframe. No local timeframe positivity or array-coherence check is added.

Fresh A-window, audit and Reset Blue structures precede native mixin stopped-A initializer. That initializer creates its own opposite integer-First owner map, sorted Order tuples, confirmation projection and fresh canonical cache before S Blue/trend preprocessing. S01 builds a separate opposite confirmation map later, with later duplicate integer First overwriting; neither map is a complete physical identity proof. Provider confirmation may be queried more than once. Trend confirmation and First optimization gates are independent; empty all-tests are vacuously true, and sorted tuples preserve one-based original ordinal as a tie discriminator before object comparison.

First valid Reset Blue per integer ordinal is taken in input order without internal filtering. The separate public list filters validity then internal, accepts any kind and retains duplicate returned formation timestamps. S33 and S06/S04 may return explicit or fallback timestamps rather than observed exact crossings. Reset owner time lists use sorted returned events with stable equal-time order; native setdefault default allocation precedes append. No transactional rollback of external aliases is supplied by constructor failure. Full provider/creator/consumer and cache freshness proof remains independent W3 work.


### W3 CP376 — chronology, stop, source and Reaction alignment (S02–S19)

- **S02 (178–180)**: Delegate main index to chronology without clamp argument; native default rejects events before first main candle and maps by right bound minus one.
- **S03 (181–185)**: Delegate lower window with explicit start/end; provider half-open bounds and native slices; no extra validation.
- **S04 (186–190)**: Call provider reaction_confirmation(direction,reaction) with default intrabar enabled. Provider invalid intrabar start resets to Break open; first strict lower confirmation or Break-open fallback, including cached value.
- **S05 (191–197)**: Public API returns virtual S04 result unchanged; no independent timestamp or crossing validation.
- **S06 (198–200)**: Provider Reset time precedence cached nonnull, truthy second_time parse, truthy display_time parse, else timestamp; no new local normalization.
- **S07 (201–208)**: Convert reaction_number to int, reject below 1 or above trend count, then positional one-based trend Reaction lookup and S04 using S direction. Ordinal not independent physical identity.
- **S08 (209–213)**: Select policy extreme attribute and normalize via as_decimal; existing Decimal preserved, otherwise Decimal(str(value)).
- **S09 (214–216)**: Delegate strict directional crossing; bullish low < level, bearish high > level; equality excluded.
- **S10 (217–222)**: Clamp lower start using max(start,range_start); bisect left at clamped start and exclusive range_end; actual lower availability controls branch.
- **S10 (223–234)**: If nonempty indexed interval and index nonnull, use first_less bullish or first_greater otherwise. Indexed miss returns None directly, not main fallback; hit uses lower_times[position] and provider main position for candle timestamp.
- **S10 (235–240)**: Otherwise slice lower rows and traverse in existing order, returning first strict directional hit using row timestamp and mapped main position. Index and linear timestamp origins differ.
- **S10 (241–251)**: Nonempty linear miss returns None. Only empty slice scans main from max(selected start_index,bisect_left(candle_times,original start)) through end_index inclusive. No containing predecessor; return actual native candle.index int and same timestamp twice; exhaustion None.
- **S11 (253–259)**: Public first_a_stop forwards level,start unchanged through virtual S10.
- **S12 (260–278)**: Forward exactly supplied zone/ordinal/price/stop tuple and first physical Order match to S39. Wrapper does not select or substitute later Order; initial cause comment is not complete accepted-ledger proof.
- **S13 (279–293)**: Reject reversed range before seed; positional start access and inclusive subsequent slice without clipping to selected analysis range; strict policy improvement preserves first equal. Return actual source object's integer index and timestamp.
- **S14 (294–313)**: Separate reversed-range error; positional seed and inclusive slice; replace on <= bullish or >= otherwise, so last equal owns. Preserve source object's index/time and Decimal selected value.
- **S15 (314–324)**: Optimized path requires nonnull ordered confirmation list, exact datetime query type and naive tzinfo. bisect_right excludes equality; return one-based original position and cached timestamp or None without fallback.
- **S15 (325–333)**: Otherwise enumerate original trend order, recompute virtual S04 for each and choose first strict confirmation > query. No sorting or unconditional exact crossing proof.
- **S16 (334–345)**: Read integer Order First then Break, First candle timestamp, Decimal top then bottom; default all trend positions, narrow via two right bounds only if ordered First list exists. Upper bound inclusive Order Break.
- **S16 (346–357)**: Original positions traversed. Read candidate First, Break, First timestamp. Ordered short-circuit rejects First time <= Order First, First index <= Order First, Break > Order Break, or First time >= Order confirmation.
- **S16 (358–367)**: Compute confirmation after preliminary guards; compute containment eagerly even if confirmation too late, top <= Order top then bottom >= Order bottom if top passes. Final confirmation <= Order confirmation and containment; first qualifying original ordinal; None otherwise.
- **S17 (369–377)**: Call S14 with integer Order Break then aligned Reaction Break; inclusive last-equal geometry, no lower-event clipping.
- **S18 (378–393)**: Lookup integer Reset from_first_idx in mixin owner map, missing returns None. Use selected owner's Break position and main index of provider Reset time; reversed interval None; otherwise S14 inclusive last-equal whole main geometry. First-key map is not full physical identity.
- **S19 (394–402)**: bisect_right on sorted trend confirmation times at A-stop; guard position within length then <= crossing. Interval (A-stop,crossing]; only Boolean existence, no candidate source/geometry proof.

The local return values do not prove physical ownership, crossing-cache freshness, or arbitrary external callback equivalence. W3 cross-owner acceptance remains independent.


### W3 CP377 — order-free Type3/Type4 search and builder (S20–S23)

- **S20 (403–408)**: Type3 helper receives stopped-A event and deadline; no independent new Order search in this helper.
- **S20 (409–412)**: Winner initially None; strict Reset event window (A-stop,deadline) via right then left bounds, traverse stable time-sorted Reset pairs.
- **S20 (413–419)**: Convert owner First, get separate confirmation map; missing or > stop skips. Get owner Reset times default empty tuple; nonempty earliest <= stop skips current even if later.
- **S20 (420–425)**: Resolve S18 nullable whole-main last-equal leg, skip absent; unpack source and boundary. Lower query starts inclusive Reset time and ends exclusive deadline.
- **S20 (426–435)**: Direct lower_index directional strict query without local null-index/empty guard. None skip; first hit timestamp from lower_times. If no trend confirmation in (A-stop,crossing], reject this Reset without recross search.
- **S20 (436–447)**: Map crossing to main position; owner ordinal from mixin First map. Construct source index/time, Decimal boundary, decision main position/time, owner ordinal, Reset event and exact crossing tuple.
- **S20 (448–452)**: Replace winner only when None or candidate crossing strictly earlier; equality retains earlier traversal candidate. Scan all admitted Resets, then return winner or None.
- **S21 (453–463)**: Blue gate begins at candidate source main open (not A-stop or candidate event), uses sorted public-valid formation times and inclusive upper crossing bound. Existence only, no Blue identity/kind association.
- **S22 (464–478)**: Receives A-stop triple and deadline; docstring describes mirrored Type4 and candidate transfer, no new Order lookup here.
- **S22 (479–488)**: Select sorted confirmations strictly after A-stop and before deadline; filter Break index >= A-stop main position. Preserve original sorted tuple tie keys and ordinal; next aligned means filtered sequence.
- **S22 (489–496)**: Traverse aligned rows; reread integer Break; S14 whole main inclusive last-equal candidate from A-stop. S31 candidate event starts max(source open,A-stop), returns first matching lower extreme or fallback; not unconditional exact hit.
- **S22 (497–506)**: Search start max(confirmation,candidate_event,A-stop); end min(deadline,next filtered confirmation or deadline). Skip start>=end, including equal-confirmation earlier empty windows; no merging.
- **S22 (507–516)**: Lower-only strict index query on half-open bounds, no explicit null-index or main fallback. None advances; otherwise first crossing from lower_times.
- **S22 (517–521)**: First hit lacking S21 public Blue skips current aligned row; no retry at later crossing of same candidate. Next aligned row rebuilds from common A-stop origin.
- **S22 (522–533)**: First qualifying aligned candidate returns source index/time/level, mapped decision position/main timestamp, original Reaction ordinal and crossing event; exhaustion None. No scan-all winner comparison as Type3.
- **S23 (534–547)**: Unpack caller A-stop and Type4 tuple; trend ordinal intentionally unused, no extra geometry calculation.
- **S23 (548–558)**: Construct frozen slotted SZone, direction, blue/type4, caller A ordinal and price, native int parent source index and direct source/stop provenance.
- **S23 (559–577)**: All Order fields and Reset ordinal/time explicitly None; no physical Order creation or accepted ledger mutation in builder.
- **S23 (578–586)**: Retain Type4 source/price and separate decision main/index/event unchanged; record construction not lifecycle acceptance.

Direct index calls in S20/S22 have no local null-index guard or main fallback. This is a caller/provider proof obligation, not a demonstrated runtime defect. S40 resolver arbitration and accepted lifecycle remain independent.


### W3 CP378 — post-Order candidate and A ownership eligibility (S24–S28)

- **S24 (587–598)**: Signature/docstring describes post-Order candidate, but native gates below control; no standalone exact chronology proof.
- **S24 (599–603)**: Read integer First, bisect main opens at confirmation, clamp downward to First then upward to selected start. Read anchor index and value before anchor guard.
- **S24 (604–610)**: Anchor nonnull and int(anchor)>=start selects it; repeated native int conversion, positional candle lookup then Decimal anchor value. No explicit upper/First bound or exact anchor event check; native failures propagate.
- **S24 (611–619)**: Otherwise call S13 earliest-equal inclusive main candidate first; map confirmation containing main position. If containing<start, scan lower remainder [confirmation,containing open+timeframe), not preconfirmation extreme.
- **S24 (620–627)**: Replace candidate on strict directional improvement OR equality, using containing positional index and main timestamp rather than lower row timestamp or native Candle.index. Return selected tuple; no new stop proof.
- **S25 (628–636)**: Read A source and normalized price; search full source main lower half-open window; return first equal trend extreme timestamp, else source-open fallback. No A-stop lower gate or observed-event guarantee.
- **S26 (637–642)**: Resolve source event once; iterate ownership windows in insertion order, matching inclusive start and open/exclusive end. Skip nonmatches.
- **S26 (643–651)**: First matching window: nonnull trigger strictly after start returns False immediately, before Blue reads; equality does not preempt. No later window reconciliation.
- **S26 (652–661)**: Read five optional Blue/source fields even with open end, after trigger exception. Comment describes decided-S Reset-pair preemption, operative ordered predicate follows.
- **S26 (662–673)**: Require closed end, all five values present, start<Blue1 source, Blue1 stop<Blue2 source, source_time==Blue2 stop, then S27. No independent Blue2 source>start or validation of pair chronology beyond predicates.
- **S26 (674–677)**: Qualifying Reset-pair returns False; otherwise first matching window returns True. No matching window returns False. This is S eligibility, not global accepted lifecycle.
- **S27 (678–685)**: Convert both Blue ordinals (default 0, subtract 1) before first bounds guard; invalid position returns False, native conversion failures propagate. Original trend Blue list, not filtered public list.
- **S27 (686–690)**: Exact string kind reset for first then second, short circuit; no calculation_valid/internal gate or physical pair identity test.
- **S28 (691–695)**: Property constructs fresh list of original sorted A records not owned by S; no ownership mutation or final lifecycle acceptance.

The local predicates, not their comments, define the scoped source contract. Provider geometry and cross-owner accepted-ledger proof remain independent.


### W3 CP379 — candidate timing, source and Blue qualification (S29–S36)

- **S29 (696–710)**: Timing receives optional A-stop event; comment describes Advanced protection, operative price and event gates below.
- **S29 (711–721)**: Read stop main trend extreme, then normalized opposite Order box bottom bullish or top bearish. Legacy after when bottom<=low bullish or top>=high otherwise, equality after.
- **S29 (722–729)**: Legacy before returns immediately before nested query. Legacy after plus nonnull nested S16 keeps after, without simple candidate chronology.
- **S29 (730–739)**: Null stop event defaults to A-stop main open; S30 candidate, S31 returned event, then Order First main open. Strict event<First open yields before; equality after. S31 fallback not observed event.
- **S30 (741–750)**: Default only null stop event to stop main open, then integer Order First.
- **S30 (751–757)**: Eager S13 whole main inclusive candidate before lower query; reversed range fails even if lower could supply geometry. Query supplied stop event to nominal stop main end; no clamp to stop main open. Empty returns initial whole-main candidate.
- **S30 (758–769)**: Nonempty remainder seed first lower row then strict bullish low/bearish high improvement, retaining first equal. Lower source reference updated but not returned as exact event.
- **S30 (770–783)**: Later S13 range only when First>stop index; later strict improvement wins, equality or absence retains stop main positional index/time and remainder price. Distinguish native Candle.index of later candidate.
- **S31 (785–798)**: Read source main open; lower window [max(open,not_before),open+TF); return first equal normalized extreme timestamp; else max(open,not_before), even beyond nominal end. Price argument not independently normalized here.
- **S32 (800–806)**: Public fallback argument forwards as lower gate not independent replacement; virtual S31 result unchanged.
- **S33 (807–810)**: Explicit nonnull formation_time returned unchanged before source/ordinal reads, no local time validation.
- **S33 (811–819)**: Otherwise int source index and actual candle timestamp, exact string kind !=reset covers any other kind. Valid integer ordinal uses S04 provider default; invalid ordinal returns source open.
- **S33 (820–835)**: Reset broken_level None returns source; otherwise whole source main lower half-open scan. Select directional Low/High then normalize; broken_level normalized within chosen strict comparison per row, not if empty. First strict hit timestamp else source-open fallback.
- **S34 (837–852)**: Check ordinal bounds before map lookup; no native int conversion here. First calculation-valid Reset entry (may internal) from S01, not necessarily earliest. Nonnull time<=cross event; no source-main or behavior-start lower bound.
- **S35 (854–863)**: Upper bound sorted trend confirmation times at behavior start, then within length and <=event, interval (start,event]. Includes provider fallback times and no independent observed confirmation proof.
- **S36 (865–869)**: Read normalized trend extreme then delegate strict policy crossing; no rounding/equality relaxation.

Local returned-time provenance does not prove a physical event or cross-owner acceptance. No Runtime claim.


### W3 CP380 — S decision race and Type3 construction (S37–S38)

- **S37 (870–879)**: Decision receives independent candidate and Order stop levels, timing, ordinal, behavior start, optional candidate start and fallback flag.
- **S37 (880–889)**: Clamp lower start to range_start and exclude range_end via left bounds. Nonempty interval queries Order stop first, directly on lower index; exact bearish Order uses first_greater otherwise first_less. No null-index guard.
- **S37 (891–895)**: Candidate gate max(scan_start,candidate_start or scan_start) uses truthiness. Fallback mode sets gate and family fallback, defers qualification until after race.
- **S37 (896–911)**: Normal mode gets Reset Blue time only for valid ordinal and first sorted trend confirmation strictly after behavior_start. Keep nonnull qualifiers, not necessarily observed events.
- **S37 (912–926)**: No qualifiers means candidate_position None without query. Else earliest qualifier then max candidate gate; restricted lower bound and strict directional first index search, family blue.
- **S37 (927–934)**: Fallback mode performs first strict candidate query from qualified_start restricted to lower interval.
- **S37 (935–946)**: Both absent or same nonnull position returns None before fallback qualification. Equal timestamps at distinct positions are not same-position tie. Earlier Order position or absent candidate yields red mapped main position/time and event.
- **S37 (947–960)**: Assert surviving candidate nonnull; obtain lower timestamp. Fallback flag permits upgrade to blue via S34 then S35 short circuit, otherwise fallback family. Map main after qualification, return separate exact event.
- **S37 (962–972)**: Only empty lower interval enters main fallback. Start max(selected start, bisect_right(main times, original start)-1); inclusive selected end. Candidate strict predicate precedes optional gate event>=candidate_start. Order predicate evaluated independently.
- **S37 (973–978)**: Both main predicates true returns None before qualifier. Otherwise Order wins red with native Candle.index int and timestamp in both time slots.
- **S37 (979–988)**: Qualified candidate checks Reset Blue then ordinary confirmation after ambiguity/Order gates. Return blue on either, native Candle.index and main timestamp twice.
- **S37 (989–995)**: Unqualified candidate returns fallback only when flag; otherwise continue next main row, exhaustion None. Unlike normal lower qualifier gating, main ambiguity may be found before candidate qualified.
- **S38 (996–1015)**: Unpack caller A-stop and Type3 tuple; retain Reset owner ordinal/time; no recalculation.
- **S38 (1016–1026)**: Construct frozen slotted blue/type3 SZone with parent ordinal, native int parent index, parent source time, caller price and stop triple.
- **S38 (1027–1043)**: All Order provenance explicitly None, no physical Order creation.
- **S38 (1044–1053)**: Retain Reset ordinal/time and candidate/decision provenance unchanged, no extra price normalization or accepted lifecycle decision.

The native lower and main races have distinct admission and tie rules. This documents local source behavior, not runtime equivalence or accepted-ledger closure.


### W3 CP381 — Order-backed Simple/Advanced construction (S39)

- **S39 (1054–1064)**: Receive and unpack exact caller A stop and first supplied Order match; no second canonical Order lookup.
- **S39 (1065–1079)**: Resolve canonical Order stop triple first through mixin provider, then S29 timing. S30 called only if timing before; failure propagates before decision initialization.
- **S39 (1081–1092)**: Initialize behavior start at A stop, decision None, use_pre False. Pre candidate selects simple source/red reference and trend ordinal zero. S31 returned candidate time becomes behavior start and candidate gate.
- **S39 (1093–1107)**: Preliminary S37 race begins at Order confirmation with fallback flag true. None exits entire route; nonfallback sets use_pre; fallback clears decision but retains pre candidate. No unconditional second attempt.
- **S39 (1109–1116)**: If not use_pre reset behavior start to exact A-stop and call S16 again, even if timing previously queried. Advanced flag only nonnull nested match.
- **S39 (1117–1131)**: Advanced branch uses Order bottom source bullish or top source otherwise. Normalize full main trend extreme, not raw box edge; nested confirmation becomes gate, red_source None.
- **S39 (1132–1144)**: Non-pre, nonadvanced simple branch uses S15 first qualifying trend match; None exits. S17 inclusive last-equal main candidate geometry.
- **S39 (1145–1153)**: Evaluate red_source pre candidate if present else S24 post-order candidate even though later non-pre Red ignores it. Preserve native call/exception effects; gate aligned confirmation.
- **S39 (1154–1165)**: Only absent decision invokes S37 normal mode default fallback false. If None exit. No repeated race for retained pre decision.
- **S39 (1166–1174)**: Unpack color, decision position/main/event; convert Order Break even on Blue. Red uses pre source only when use_pre and red_source nonnull; otherwise S13 first-equal inclusive Break..decision. Blue retains prior selected source.
- **S39 (1176–1189)**: Convert First, top source, bottom source in order, then construct SZone; parent A source int/time, original supplied price and stop triple.
- **S39 (1190–1206)**: Preserve original Order direction/number and mode str, First/Break main times, supplied confirmation and normalized top plus source provenance in argument order.
- **S39 (1207–1216)**: Normalize bottom and its source time, carry canonical stop level/index/time; Reset fields null. No replacement Order or second stop proof.
- **S39 (1217–1224)**: Return selected source/price and separate decision main/index/event; frozen record not accepted ledger or lifecycle assertion.

Canonical Order stop is delegated to the provider, not independently recreated by S39. Supplied physical identity and accepted lifecycle remain independent cross-owner obligations.
