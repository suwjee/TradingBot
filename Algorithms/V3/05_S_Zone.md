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

Once E supplies accepted ledger, deduplicate physical entries by First/Break (replace missing-cross entry only when new has crossing), require own confirmation < stop. Sort by (stop,confirmation,First,Break); for each S choose earliest stop >= frozen source main and strictly earlier than its current decision. Convert to Red and replace Order/decision provenance, retain source/price, A identity and formation type; clear Reset provenance. No new Order creation here. Live S caches resolved non-null decisions only if actual lower evidence and dependency frontier are settled; dirty includes changes in trend/opposite geometry, reset/Blue events and scope. Full details below.

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
For sorted opposite Reset events in (A-stop,deadline), require owner confirmation exists and <=A-stop; if owner Reset list exists and earliest <=A-stop skip. Resolve S18 leg; skip null. Search lower index strict trend crossing of leg boundary in [reset event,deadline). Skip absent or S19 false. Map decision exact event to main; owner number from mixin map. Candidate tuple (source index,time,boundary,decision index,main time,owner number,reset exact time,crossing). Winner strictly earliest crossing, ties retain first Reset traversal. Return null if none. No lower-data fallback.

### S21 — _type4_has_blue
Window start=main timestamp at candidate source index. lower_bound sorted public Blue formation times; return true iff first >=start exists and <=crossing. Inclusive endpoints.

### S22 — _first_type4
Inputs A stop tuple, deadline. Aligned trend sorted rows confirmation strictly after A stop and strictly before deadline, Break index>=A-stop index. For each aligned row in order, S14 over A-stop index through its Break inclusive. Candidate exact formation via S31 with not_before=A stop. Search start=max(confirmation,candidate event,A stop), end=min(deadline,next aligned confirmation or deadline); skip start>=end. Search lower first strict trend crossing in [start,end); skip absent or no S21 Blue from candidate source main time through crossing. First qualifying returns (source index,time,price,decision index,main time,trend reaction number,exact event). Failed candidate is replaced by next aligned reaction; no Order yet, no coarse fallback.

### S23 — _build_type4_zone
Return SZone direction stored, color blue, formation_type type4, A ordinal/source index/time/price and stop tuple from parent inputs; all Order fields and both Reset fields null. Source and decision from type4 tuple; aligned reaction number unused. No price recalculation.

### S24 — _candidate_after_order
First index integer. Start=max(detector start,min(lower_bound(main times,Order confirmation),First)). If anchor_idx non-null and integer>=start, return anchor index/main timestamp/normalized anchor_value (no upper-bound or null-value guard). Otherwise S13 inclusive start..First. Map containing confirmation main index; if containing<start, scan lower remainder [confirmation,containing main end); replace candidate whenever strict trend improvement OR equal price, assigning containing main index/time and lower price. This gives earlier containing main candle on equal candidate price; no pre-confirmation data.

### S25 — _a_source_event_time
Read A source main time and normalized price. First lower row in [source,source+timeframe) whose trend extreme equals price yields timestamp; else source main time.

### S26 — _a_owned_by_s
Calculate source event via S25. Iterate windows in insertion order. Consider first with start<=event and (end null OR event<end). If zone.trigger_event_time exists and >start, return false immediately (independent). Else read both Blue source times, both stop main times and A source time with null defaults. Return false if window closed (end non-null), all five times non-null, start<Blue1 source, Blue1 stop<Blue2 source, A source==Blue2 stop, AND S27 reset-reset. Otherwise return true. No matching window => false. Does not continue to later overlapping window after exception. Trigger exception is evaluated before reset-reset exception.

### S27 — _a_pair_is_reset_reset
Convert Blue ordinal attrs default 0 to integers then subtract one. If either outside Blue list return false. Both referenced kind strings (default empty) must equal reset.

### S28 — eligible_a_zones
Property returns fresh list of sorted A inputs for which S26 false, no public display filter.

### S29 — _candidate_timing
Read stop main trend extreme and normalized opposite Order box_bottom B/box_top R. Legacy after if boundary<=stop extreme B or >= R, else before. Before returns immediately. If after and S16 nested trend match exists, preserve after. Else default A stop event to stop main timestamp if null; compute S30 then S31; return before iff candidate exact event<main Order First timestamp, else after (equality after).

### S30 — _candidate_before_order
Default A stop event to stop main timestamp. First index integer; initial candidate S13 inclusive stop..First (reversed fails). Query lower remainder [exact A stop,stop main end); empty returns initial full-main candidate. Nonempty seed first lower row, strict trend improvement only. If First>stop index compute later S13 on stop+1..First. Return later only if strictly better than lower remainder extreme; ties choose stop main. Otherwise return (A-stop index,A-stop main time,lower extreme). Local lower source reference not output.

### S31 — _candidate_event_time
Source main timestamp; scan [max(source,not_before),source+timeframe) first row trend extreme==level. Return exact timestamp or max(source,not_before) fallback, even if gate after candle end.

### S32 — candidate_event_time
Public delegate S31(source index,price,fallback used as not_before).

### S33 — _blue_formation_time
If explicit formation_time non-null return as supplied. Else integer source index and main timestamp. For kind string !=reset: if valid 1-based trend reaction number, return S04; else source time. Reset: if broken_level null return source; otherwise scan [source,source+timeframe), first strict directional normalized price crossing of normalized broken level; return timestamp or source fallback.

### S34 — _candidate_cross_has_blue
Reject reaction number outside 1..trend count. Lookup first Reset Blue formation by number; true iff non-null and <=candidate crossing event. No same-candle requirement, no internal filter here.

### S35 — _has_ordinary_trend_reaction
Same temporal predicate as S19 but generic behavior_start/event: first sorted confirmation strictly after start and <=event.

### S36 — _candidate_crossed
Return S09 of S08(candle) and level.

### S37 — _decision
Inputs candidate level, Order stop level, start, trend reaction number, behavior_start, optional candidate_start null, fallback_on_unqualified_cross false. Output null or (family,main index,main time,exact event).
Lower route when [lower_bound(max(start,range_start)),lower_bound(range_end)) nonempty:
1. Find opposite Order stop independently using first_greater if order_direction bearish else first_less across entire window.
2. Candidate gate=max(scan_start,candidate_start or scan_start). Fallback enabled: qualified start=gate, candidate family fallback. Otherwise obtain aligned Reset Blue time only if ordinal valid; first trend confirmation strictly after behavior_start; if neither exists candidate position null. If any qualifier, qualified start=max(gate,min(non-null times)), family blue; query first strict trend cross from lower_bound(qualified start,lo=left,hi=right) through right exclusive. When fallback enabled do same query from gate.
3. Both null => null; identical non-null position => null (ambiguous). Earlier Order stop or only Order => red. Otherwise candidate exists (assert); if fallback enabled and S34 or S35 true at event, upgrade family blue; return family and mapped time/index.
No-lower route: scan main positions max(start_index,upper_bound(main times,start)−1) through end_index inclusive. Candidate crossing strict plus candidate_start absent or main timestamp>=candidate_start. Order crossing via mixin. Both => null regardless of qualification. Order only => red; candidate plus S34/S35 => blue; candidate plus fallback enabled => fallback; else continue. Main fallback event=main timestamp. No fallback when nonempty lower route merely lacks crossings. Exact equality never strict crossing.

### S38 — _build_type3_zone
Same field mapping as S23 but formation_type type3 and Reset owner number/time from type3 tuple; Order fields null. Source/decision from supplied tuple.

### S39 — _build_order_backed_zone
Inputs parent A/ordinal/price/stop, Order match (ordinal,reaction,confirmation). Obtain Order stop geometry via mixin; S29 timing. If timing before, S30 pre-order candidate else null. Initialize behavior start=A-stop, decision null, use_pre=false.
- Pre-order exists: simple, initial source and red_source=pre-order, aligned number=0. Find exact candidate event S31; behavior start=candidate event. S37 race starting Order confirmation with candidate gate at candidate event and fallback enabled. Null => return null; non-fallback => use_pre=true; fallback => clear decision and reconsider aligned geometry.
- If not use_pre, reset behavior start=A-stop and seek S16 nested match. If found advanced: source index=Order box_bottom_source_idx B/box_top_source_idx R; main source time/trend extreme; candidate start=nested confirmation, aligned number from nested; red_source null. Else simple: require S15 first later trend reaction, absent => null; source S17 inclusive Order Break..aligned Break last tie; red_source=pre-order if exists else S24 (computed even though final non-pre Red uses S13); candidate start=aligned confirmation.
- If decision still null call S37 normal (fallback false) with source price, Order stop, confirmation, aligned number, behavior start and candidate start. Null => null.
- Unpack decision. Red: if use_pre and red_source non-null retain it; else S13 inclusive Order Break through decision main index earliest tie. Blue retains selected candidate.
- Build SZone with direction, decision family/color and chosen formation_type, full parent A identity/stop; Order direction stored, reaction number/mode, First/Break integer indexes and main times, exact confirmation, normalized box bounds and integer source indexes/main times, stop level/source from mixin. Reset fields null. Source/decision tuple as selected. No second physical Order search.

### S40 — _resolve_candidate
Deadline=Order confirmation if match exists else range_end. Compute BOTH S20 Type3 and S22 Type4 before arbitration. If Type3 exists and Type4 absent or Type3 exact event<=Type4 exact event, S38. Else if Type4 exists S23. Else Order match exists S12. Else null. Tie precedence Type3; independent of main timeframe color.

### S41 — detect
Delegate S42 with bound S40 resolver.

### S42 — _detect
Fresh output; clear ownership windows and audit map. First audit stopped A for every sorted A through mixin, even later excluded. Cycle start=range_start. Iterate A in order with 1-based ordinal. Skip S26-owned; skip source<cycle start or equal when output nonempty. Compute next A exact confirmation if next exists (even if later ineligible). Normalize A price, find first A stop after its own confirmation. No stop skip. Compute first Order after stop via mixin. If next A confirmation exists and stop event>=it skip. Append open ownership (stop event,null); invoke resolver. Null result leaves window open and continues. Success append S, cycle start=S.source_time, replace last window with (stop,max(stop,S.decision_event_time+1 microsecond)); includes exact decision. Return stable sorted output by (source_time,decision_event_time). Mutates audit and ownership in-place; failures can leave partial state.

### S43 — reconcile_shared_order_stops
Inputs S records and accepted Order entry dicts. Dedup by (integer reaction First,Break); skip absent reaction; first wins unless retained stop_cross null and new non-null, then replace. For each retained entry require confirmation isinstance datetime; normalize stop level. If supplied stop_cross not tuple len>=3 with datetime element 2, compute mixin shared stop cross. Require crossing exists and confirmation<exact crossing. Build candidates (cross event,confirmation,First,Break,entry,cross tuple), stable sort first four; store cross times. For each S, lower_bound cross times at S.source_time (inclusive), choose first if its event<S.decision_event_time (strict). No candidate => retain original zone. Winner => replace S color red, full Order provenance from winner entry/reaction (stored order direction, integer reaction number default 0, mode, First/Break, box prices/source times, exact confirmation, stop price/index/time), Reset fields null, decision tuple from crossing; retain original S formation type, A provenance and frozen source/price. Output in input order. Does not reassign Order parent cause or compare winner confirmation to S start beyond own confirmation<cross.

### S44 — _s_reaction_inputs
Return tuple of First, Break, mode, intrabar_start default null, box top source index/string top, bottom source index/string bottom, anchor_idx default null/string anchor_value default null. No numeric normalization.

### S45 — LiveSZoneContinuation.__init__
Scope null, fresh dependencies set and decisions map.

### S46 — LiveSZoneContinuation._current_dependencies
Static: build set for each trend/opposite reaction: (Break main time,side literal,0-based enumeration,S44 tuple). Add (exact opposite reset event,reset,integer owner First), (event,reset-blue,reaction number) from map, (event,public-blue) from times. Set deduplicates; no source mutation. Return set.

### S47 — LiveSZoneContinuation._settled_through
Static. through=S decision event. Type3/4 => through directly. Other types assert Order match. Find lower_bound(max(Order confirmation,range start)); if no lower row or first lower time>through return null (main-only decision not reusable). Set through=max(through,Order Break main time). If S15 aligned match exists, max with aligned Break main time and exact confirmation. Return frontier.

### S48 — LiveSZoneContinuation.update
Input fresh detector, required dirty main index. Validate 0<=dirty<=candle count. Scope=(direction,timeframe,start_index,range_start). Dirty time=main timestamp at index or range_end at end. Compute S46 dependencies. If same scope, dirty=min(dirty,min(event times in symmetric difference of old/new deps,default dirty)); prior decisions=current stored. Else empty prior. Fresh current map; define S49. Invoke detector S42 with resolver. On success replace scope/dependencies/decisions, return sorted detector output. Detector may mutate even when wrapper not committed.

### S49 — LiveSZoneContinuation.update.resolve
Key=(A ordinal,source index,source time,string price,stop tuple,Order key). Order key null or (number,S44 reaction tuple,confirmation). If previous decision exists and stored through<dirty, copy pair to current and return stored S. Else call detector S40; if result non-null compute S47 and cache only non-null through. Return nullable result. Null not cached. No in-place S edits.

### S50 — detect_s_zones
Construct SZoneDetector forwarding all arguments in signature order/defaults S01, call detect, return. No persistent wrapper state.
