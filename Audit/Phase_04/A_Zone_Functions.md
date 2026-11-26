# Phase 04 — A Zone function contracts (checkpoint 02)

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Source engine/pipeline/a_zone_detector.py, blob `431934d2fb597238d5281a769c29fdb51747868b`. A_ZONE_VERSION 1.7.0, implementation 1.8.1, last modified date 2026-11-19. All 39 named declarations described. Owner: A formation, adjacent Blue pair, double-stop route, trigger and frozen source, not S/E/lifecycle projection.

## Conventions and records

B = bullish, R = bearish. Directional Low/minimum/strict less for B, High/maximum/strict greater for R. Shared normalization as_decimal returns existing Decimal unchanged or converts its string. All arithmetic/context and chronology dependency semantics remain native. Unless explicitly handled, missing attributes, malformed input, conversion, range, comparison and dependency errors propagate. No hidden fallback. Record declarations are in [record catalog](../../Contracts/Declared_Record_Schemas.md): BlueState frozen/slotted (ordinal, original line, formation index/time, nullable stop index/time/event time, stop level and nullable event extreme); AZone frozen/slotted with required geometry and provenance fields; optional keyword-only presentation provenance formation_route, blue_1_stop_event_time, blue_2_stop_event_time defaults null. _AHistory mutable/slotted with nine independently allocated dictionary factories: confirmations, reset_formations, crossings, extremes, matches, inherited_stops, triggers, sources, zones. Internal aliases: MarketEvent = (integer main index, event datetime, Decimal), EventKey = variadic tuple. None of those type annotations validates input at runtime.

## A01 — AZoneDetector.__init__ (69–109)

Inputs direction, reactions, Blue lines, chronology. Reject any direction outside exact bullish/bearish with ValueError. Store policy, shallow list of reactions in supplied order; stable sort Blue lines by (integer reaction_number, source_time, string kind) ascending. Store chronology and references to its candles, seconds, timeframe, main times, second times and lower index. Construct three lists in reaction order: First main time by integer first_idx; Break main time by integer break_idx; exact confirmation via A14 (virtual dispatch, so live subclass override may be called). Record three booleans via ordered_naive_datetimes independently for those lists. No reaction sorting. Input object references remain shared.

## A02 — AZoneDetector.extreme_name (112–113)

Property returns stored policy.extreme_attr; no mutation.

## A03 — AZoneDetector._strict_cross (115–116)

Delegate value/level to stored policy.strict_cross, return Boolean (strict Low<level B, High>level R); native errors propagate.

## A04 — AZoneDetector._better (118–119)

Delegate value/current to policy.better_extreme; strict improvement, equal does not replace.

## A05 — AZoneDetector._main_index (121–122)

Return chronology.main_index(timestamp); delegate mapping, no alternate fallback.

## A06 — AZoneDetector._lower_window (124–127)

Return chronology.lower_window(start,end), end nullable; no copying imposed by wrapper.

## A07 — AZoneDetector._first_crossing (129–169)

Inputs level, start, nullable end. Lower slice indices: lower bound(start); end lower bound(end) or lower length. If nonempty and lower index exists, select directional first_less/first_greater, query [left,right), return null if no position (no coarse fallback); otherwise fetch lower row, normalize directional price, map timestamp to main position and return (main position,event time,value). Else scan lower slice in caller order; first strict crossing returns same shape. If any lower rows but no crossing, return null. Only if no lower rows, scan main candles: start=max(0,lower_bound(main_times,start)); exclusive end = main length or max(start_index,lower_bound(main_times,end)); first strict directional price returns (integer candle.index,candle.timestamp,value). Else null. Start included, end excluded; main fallback selects candle opens at/after start, not containing candle before start. Does not mutate.

## A08 — AZoneDetector._range_extreme (171–214)

Reject end<start with ValueError. Convert inclusive end to exclusive by adding one microsecond. Obtain lower bounds. Nonempty with index: select range_minimum B / range_maximum R; get (value,lower position), map lower time to main position; return (value,position,main timestamp). Otherwise call lower window; nonempty: seed first row, replace only on strict improvement, map selected lower time to main, return directional price and main position/time. Empty lower fallback: start position=max(0,upper_bound(main_times,start)−1); end position=min(main length−1,max(start,upper_bound(main_times,end)−1)); seed start candle then scan inclusive rest, strict improvement retains earliest tie. Return normalized price, integer source candle.index and timestamp. Main fallback includes containing candles, unlike A07. Missing candle errors propagate.

## A09 — AZoneDetector._formation (216–231)

Require 1<=integer reaction_number<=reaction count, otherwise ValueError even for Reset. If string kind is scale: resolve reaction by ordinal, index=integer break_idx; event=A14, stop-scan start=event. Otherwise index=integer line.source_index; main source timestamp, event=A10, stop-scan start=source timestamp+timeframe. Read candles[index] before return (even if unused). Return (index,event,scan start). No special rejection of unknown kind.

## A10 — AZoneDetector._reset_formation_time (233–243)

Input line/source index; read main source timestamp and exclusive end=start+timeframe. Normalize broken_level. Traverse A06 window; first strict crossing directional extreme returns exact lower timestamp. If none, return source main start, even if lower rows exist. No index optimization here.

## A11 — AZoneDetector._build_blue_states (245–272)

Enumerate sorted Blue lines starting at 1 (ordinal counts invalid lines too). Skip if bool(calculation_valid default true) false. Obtain formation via A09; normalize source_extreme as stop level; A07 from stop-scan start unbounded end. Return list of BlueState for valid lines in order, with original line reference; on hit set stop index, main timestamp, exact event timestamp, stop event extreme; otherwise those fields null. Internal lines are not filtered here.

## A12 — AZoneDetector._double_stop_a_candidates (274–335)

Traverse sorted Blue lines with ordinal including invalid. On valid line set previous=(ordinal,line) and continue. Invalid without previous => skip. Otherwise formation index from invalid line.source_index; formation time from invalid line.source_time; source main time from candles[index]. Find A07 crossing of previous source_extreme from formation time to source main time+timeframe exclusive; skip if absent or crossing main index differs. Find A15 first aligned reaction with confirmation >= trigger event and First >= formation time; skip if none. A17 chooses A source; skip if none. Emit via A21 record:
- Blue ordinals/times from previous and invalid lines, both stop main times = invalid source main time, stop levels = respective normalized source_extremes.
- continuation level/source index/time = previous Blue semantic source; trigger index, main timestamp and exact event from crossing.
- reaction number, First and Break main timestamps; A source index/time/price from A17; direction; route double-stop. Optional exact Blue stop event provenance remains null.
After successful emission clear previous. Failed attempts retain previous. Return list.

## A13 — AZoneDetector._pair_trigger (337–495)

Inputs previous/current BlueState, nullable expires_at. Return null if previous exact or main stop time absent, or previous exact stop > expires_at. Otherwise return 8-tuple (continuation level,index,time,trigger index,trigger main time,trigger exact time, effective previous stop main time,effective current stop main time) using FIRST applicable route:

1. A16 inherited stop non-null: unpack level/index/time and unused inherited Break time. Search A07 from current formation through expires_at exclusive. If no crossing return null, not fallback. On hit effective previous stop time = inherited level source time, current = trigger main time.
2. No inherited stop, previous exact stop < current formation: compute A08 over previous exact stop through current formation main open−1 microsecond inclusive (invalid reversed interval propagates). Search crossing from current formation to min(formation main end,expires_at) if expiry exists, else main end. Hit returns previous actual stop main time and effective current trigger main time. If no hit require current stop times non-null and current exact stop <= expiry when supplied; A07 from current exact stop to expiry exclusive, return null if absent; on hit use both actual stop main times.
3. Otherwise require current stop times non-null and exact stop <= expiry. Stable sort previous/current by (stop_event_time, stop_level for R or negated stop_level for B), so same-event higher previous-level priority B / lower level R, original order on equal key. Assert first/second exact times and exact event extremes non-null. Continuation level is first.stop_event_extreme; source index integer first.stop_index and corresponding main timestamp. If same exact stop event time, return second.stop_index and second event immediately (no extra strict crossing required). Otherwise A07 from second exact stop to expiry exclusive; null if absent. Both effective stop main times remain original previous/current, irrespective of sort order.
Expiry comparisons for recorded stops allow equality; search windows exclude expiry. The immediate same-time route can therefore return an event exactly at expiry. No price rounding or alternative route after a selected route fails.

## A14 — AZoneDetector._reaction_confirmation_time (497–500)

Delegate chronology.reaction_confirmation(direction,reaction,use_intrabar_start=false). Explicitly disables intrabar start behavior. Return exact datetime; no alternative.

## A15 — AZoneDetector._first_reaction_after (502–531)

Input trigger time, keyword-only not_before default null, start_position default 0. If nonnegative start_position, ordered confirmations, trigger exact naive datetime and either no not_before or ordered firsts with exact naive not_before, use position=max(start_position,lower_bound(confirmations,trigger)); if not_before set, max with lower_bound(first_times,not_before). Return (position+1,reaction) if in range else null. Fallback traverse range(start_position,reaction count), first confirmation>=trigger AND (not_before null OR First>=not_before). Return 1-based ordinal and original reaction or null. Inclusive both; no strict greater change. Negative start positions are not normalized in fallback; native indexing semantics apply.

## A16 — AZoneDetector._inherited_stop (533–590)

Require previous formation strictly before current formation. chained iff previous main/exact stop times exist, exact stop strictly before current formation, and neither original line marked internal (truthiness default false). If not chained and previous kind string is scale return null. Otherwise start window=previous main stop time if chained else previous formation time. Candidate reactions in original order; if first times ordered and start exact naive datetime, begin upper_bound(first_times,start); otherwise begin 0. Skip First<=window_start. Break must be strictly before current formation; if Break>=formation and breaks ordered with exact naive current formation, terminate, else skip. First eligible reaction yields A08 extreme from window_start through Break main time+timeframe−1 microsecond inclusive when chained (complete Break candle), otherwise Break main timestamp inclusive. Return (level,index,time,Break main time). If none null. Non-chained Reset may inherit while live; Scale may not. No direction-specific lifecycle differences.

## A17 — AZoneDetector._a_source (592–611)

Start = trigger main candle timestamp, end = exact A14 reaction confirmation. End<start => null. A08 inclusive range returns price/source; reorder output as (source index, source main timestamp, price). Freeze at confirmation, not full Break OHLC when lower chronology available.

## A18 — AZoneDetector._detect_ordinary_a (613–732)

Inputs valid states list. Output empty; cycle_after_index=-1, bridge_reuse_ordinal=null, index=0. While adjacent pair exists:
- previous=states[i], current=states[i+1]; bridge_pair iff previous ordinal matches non-null reuse. Skip and increment if current formation index<=cycle_after_index OR previous formation index<=cycle_after_index and not bridge_pair. Clear reuse only on such skipped bridge_pair.
- expiry = next state's formation time if present, else null. Call A13; null -> increment and continue. On hit call A15 with trigger event and not_before=max(effective Blue stop main times). No matching reaction -> break entire loop. Call A17; null -> increment and continue.
- Emit A21 with direction, pair ordinals/source times, effective stop main times from A13, actual respective stop levels, continuation tuple, trigger tuple, selected reaction number and First/Break main timestamps, A source tuple, formation_route ordinary; exact stop provenance for each Blue included only if its actual stop main time equals corresponding effective stop time, else null.
- Set cycle_after_index to matched reaction break index. Compute confirmation via A14 and first strict stop of A price via A07 from confirmation unbounded. Permit adjacent reuse iff stop exists, next-next state exists and its formation time >= exact first stop. If permitted set bridge_reuse_ordinal=current.ordinal and increment i by 1. Else clear reuse and advance i while state formation_index<=cycle_after_index.
Return output in detection order. Exact confirmation and stop-time tests are invariant; geometry mirrored by policy.

## A19 — AZoneDetector._filter_special_a (734–796)

Inputs special double-stop candidates, ordinary candidates. Remove special candidates whose reaction_number occurs in ordinary non-null reaction numbers. For each retained special find latest ordinary with source_time strictly less (stable first on equal maximum), null if none. If prior exists and A22 reports stopped before special reaction_first_time with not_before=special blue_1_source_time, discard special. Build list (set of two integer Blue ordinals,trigger event) for remaining special. If nonempty, remove ordinary whose trigger is strictly later than any special trigger and whose two-ordinal set intersects that special pair. Equality of trigger not consumed. Return (filtered ordinary,filtered special), preserves each input relative order, does not alter original zone records.

## A20 — AZoneDetector.detect (798–808)

A11 then A18. Generate A12 candidates, resolve with A19. Combine ordinary then special, stable sort ascending (source_time,trigger_event_time). Return list, no separate public/internal filter.

## A21 — AZoneDetector._zone (810–811)

Pass provided named fields to AZone constructor; return newly allocated record. Missing/extra constructor fields raise native errors; no normalization.

## A22 — AZoneDetector._a_was_stopped_before (813–836)

Input zone,end_time,keyword-only not_before null default. Start position=integer candles[zone.source_index].index+1. If >= candle count return false. A07 first crossing of zone.price from start candle timestamp to end exclusive. Absent => false. Otherwise return true iff not_before absent OR exact first stop>=not_before. Do not rescan for recross after lower gate.

## A23 — detect_a_zones (839–845)

Construct AZoneDetector with supplied direction/reactions/Blue/chronology and call detect; return result. No persistent state.

## Live A continuation

Virtual dispatch: live overrides A14/A10/A07/A08/A15/A16/A13/A17/A21. Other methods are inherited. Each live detector owns fresh current history and references previous history during computation; wrapper clears previous after successful detection. Current market and reaction objects remain external dependencies. Settled means strictly before dirty time, not at it.

## A24 — _LiveAZoneDetector.__init__ (868–888)

Initialize history fresh, previous history from prior detector if non-null else fresh, dirty_time; then call base constructor A01 (may dispatch A27 before current reaction comparison is built; confirmations only require initialized fields). Build list of zipped first/break/confirmation times. Old list prior.reaction_inputs or empty. same_reactions initially lengths equal; common prefix=0; zip in order until first inequality, set same=false on mismatch, increment prefix on each equal. changed_reaction_time = minimum Break timestamp (tuple index 1) across both suffixes after common prefix, default null. No whole-record comparison beyond timestamp triples.

## A25 — _LiveAZoneDetector._settled (890–891)

True iff dirty time exists AND event_time<dirty_time; false when null dirty. No equal-boundary reuse.

## A26 — _LiveAZoneDetector._settled_reaction_window (893–896)

A25(end) AND (changed_reaction_time absent OR end<=changed time). Short-circuit.

## A27 — _LiveAZoneDetector._reaction_confirmation_time (898–908)

Key=(integer break_idx,string of confirmation-side box_top B / box_bottom R). If absent current confirmations: use previous if main timestamp at index settled and key present, else base A14. Store current and return. String representation preserves Decimal spelling distinctions; no cross-run global cache.

## A28 — _LiveAZoneDetector._reset_formation_time (910–917)

Key=(source index,string broken level). Use prior reset_formations if source main timestamp settled and key present, else base A10. Write current history and return, does not first consult current cache.

## A29 — _LiveAZoneDetector._first_crossing (919–949)

Key=(string level,start,end). Current hit returns stored tuple element 0 (including null). Otherwise lower bounds, has_lower=left<right; retrieve prior cached pair (hit or null, old_has_lower), dirty time. Default scan_start=start. If prior entry exists and dirty non-null and start<dirty:
- reuse whole pair if bounded end<=dirty OR old hit exists before dirty AND old_has_lower equals current has_lower.
- else dirty_position=min(right,lower_bound(lower_times,dirty)). If old_has_lower AND left<dirty_position, unchanged lower row suppresses coarse fallback: if dirty_position==right store (null,true), return null; else scan_start=dirty.
- else if no old lower and no current lower, scan_start=dirty.
Run base A07(level,scan_start,end); store (result,has_lower) and return. If old hit crosses dirty or lower availability changed, reuse only where above explicit condition allows; no broad cache fallback. Original query key retained even if scan narrowed.

## A30 — _LiveAZoneDetector._range_extreme (951–960)

Key=(start,end). First prefer previous if end settled and key present; else current hit returns immediately; else base A08. Store selected result in current unless immediate current return.

## A31 — _LiveAZoneDetector._first_reaction_after (962–979)

Key=(trigger,not_before); read prior match number or null. Use current key if present; else prior non-null ordinal <= common prefix; else if prior key present, prior null and same_reactions, retain null. Otherwise call base A15 with start_position=common prefix if prior key existed else 0, cache returned ordinal or null. Return (ordinal,current reactions[ordinal−1]) if non-null; never return old object reference.

## A32 — _LiveAZoneDetector._blue_key (982–988)

Static: tuple (formation_index,formation_time,stop_index,stop_time,stop_event_time,string stop_level,string stop_event_extreme, original line.kind, bool original line.behavior_internal default false). Omits ordinal, line identity, rendered price. Null event extreme string becomes native string representation. No mutation.

## A33 — _LiveAZoneDetector._inherited_stop (990–997)

Key=(A32(previous),A32(current)). If A26(current formation time) and previous key exists reuse (including null), else base A16. Save to current inherited_stops and return.

## A34 — _LiveAZoneDetector._pair_trigger (999–1012)

Key=(A32(previous),A32(current),expires_at). Reuse previous trigger only if expiry non-null, current formation A26 settled, all non-null values among expiry, previous formation, previous stop event, current stop event are A25 settled, and prior key exists. Otherwise base A13. Store current result (nullable), return.

## A35 — _LiveAZoneDetector._a_source (1014–1025)

End=A27 confirmation; key=(trigger index,end). If end and trigger main timestamp settled and previous key exists, reuse; else base A17. Store current source (nullable) and return.

## A36 — _LiveAZoneDetector._zone (1027–1036)

Key is tuple of (field name,value) in supplied keyword insertion order, with every Decimal value replaced by its native representation tuple (sign,digits,exponent), not equality-normalized. If previous zones key yields non-null, return same record object; otherwise base A21 allocates. Store current result. Unhashable value fails natively; no implicit sorting.

## A37 — LiveAZoneContinuation.__init__ (1042–1046)

Store direction. Construct live detector with previous=null, dirty=null; calculate result and retain detector. No separate return.

## A38 — LiveAZoneContinuation.result (1049–1050)

Property returns fresh list of retained records; objects shared.

## A39 — LiveAZoneContinuation.update (1052–1069)

Require revised timeframe equal previous, else ValueError; require 0<=first_dirty_main<=min(old count,new count), else ValueError. Dirty time = min available timestamp at that position across old and new time arrays; default = new last timestamp+timeframe if new times nonempty else null (default expression evaluated even when candidates exist). Construct fresh live detector with prior and dirty; detect; replace its previous history with fresh _AHistory to release old history; commit detector and result to wrapper only after successful calculation. Return A38 copy. No explicit exception catch or change to original source rows.

## Coverage boundary

39/39 named declarations described; six class declarations accounted for. Anonymous lambdas, list/dict/set comprehensions and generators described at their owning operations. The explicit calls to chronology, lower index and shared policy are conditional dependency contracts, not claims of proven binding or implementation coverage in those modules. Reconcile all detailed Phase 02 call, control, effect and exit IDs in closure pass. No execution.