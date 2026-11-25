# Reaction Engine — function-level source contracts

Baseline main `466eb875070f02cd0dbfb105033422bbe2fd8c70`; engine/pipeline/reaction_engine.py blob `9adffb832ffa231ba0cb01de507a30fbe62be0b0`; semantic 9.9.1, implementation 9.13.4. Source-only. B= bullish, R=bearish. All prices are Decimal; price reflection uses copy_negate, not arithmetic unary minus. Main timestamps, exact lower events and display strings are separate. Candidate is mutable; Candle, ResetEvent, IntrabarAnalysis and DetectionResult frozen/slotted; cursors/checkpoints carry mutable candidate snapshots. No downstream visibility priority is owned here.

## Base chronology and bullish reference

### RE01 — classify_candle_color (138–140)
GREEN iff open<=close (including equality), RED otherwise.
### RE02 — opposite_direction (143–145)
Return direction policy opposite; invalid direction follows policy exception.
### RE03 — DetectorBase.__init__ (149–171)
Retain candles, lower, start/end. Shared time arrays by source identity and lower segment index. Empty reaction-break index cache. Timeframe difference first two main timestamps or 1s for <=1 row; require positive.
### RE04 — DetectorBase._shared_time_index (174–182)
Global cache by id and exact object identity; on miss build timestamp list and retain source/list.
### RE05 — seconds_between (184–187)
Lazy generator over lower [lower_bound(start),lower_bound(end)).
### RE06 — main_source_for_time (189–200)
Main position upper_bound(timestamp)-1; require selected index range; end next actual main timestamp or current+timeframe; return candle if timestamp<end else null.
### RE07 — minimum_low (202–216)
Inclusive main index range; when end-start>=16 use shared range index, reflected view queries original maximum then negates. Otherwise scan strict lower, first equal owner. Return value and corresponding (possibly reflected) candle.
### RE08 — maximum_high (218–232)
Mirror of RE07: strict higher, reflected queries original minimum. Same threshold and ties.
### RE09 — BullishDetector.green_run_peak_before (236–244)
Previous main index must be >=start and GREEN, else ValueError. Extend contiguous GREEN run backward to start; RE08 inclusive peak.
### RE10 — breakout_analysis (246–270)
Start index = top source+1 if top source<First, else top source. Start candidate.intrabar_start or main time there. End Break main+timeframe. First lower High>BoxTop; null absent. Min Low over lower interval through crossing inclusive, map min timestamp to selected main candle; null if unmappable. Return analysis(event lower candle,extreme,main source).
### RE11 — mode_a_invalidation_before_breakout (272–306)
Level anchor_value if non-null else leg_boundary. Missing or main Low>=level false; main High<=top with strict low breach true. If both, search exact lower first Low<level and High>top in current main. No invalidation => true only if no breakout either; invalidation present/no breakout true; both => invalidation<=breakout (same lower position invalidates first).
### RE12 — confirmed_reset_before_breakout (308–326)
Null candidate or main High<=top true. Else race Low<confirmed bottom vs High>candidate top with same no-event and tie logic RE11.
### RE13 — post_breakout_reset (328–341)
Null analysis =>null. Search lower Low<box_bottom strictly after confirmation (event+1us) through Break end exclusive. Return lower candle or null.
### RE14 — BullishDetector.detect (343–344)
RE15 first_only flag.
### RE15 — BullishDetector._scan (346–639)
Initialize empty results, mode A, SCANNING, null last confirmed/running peak/leg floor/anchor/reset context/candidate; leg just started true. Optional initial cursor restores index,state,leg floor,flag,anchor/origin,copy candidate; no prior confirmed state. For each main:
1. Strict Low<last confirmed bottom signals Reset; if WAITING use RE12 race. Reset event uses main display, second_time null, previous bottom and First; clear candidate/confirmed/peak, mode A SCANNING, null floor, just_started, anchor=current RED if so (origin reset), reset_context=current; continue.
2. WAITING: mode A and RE11 => discard candidate, SCANNING, RED anchor origin candidate_invalidation or null; continue. Update box bottom on strict lower. If High>BoxTop set Break; RE10; refine bottom only when current main owns it and analysis exists. Append replacement candidate. first_only => immediate result. Else update last confirmed bottom/First, peak=current High, mode B SCANNING, candidate null. RE13 same-Break post-reset => record exact second display, clear state as in step1 and continue. Otherwise RED Break seeds next B candidate on same candle with top running peak and bottom current Low, WAITING. Continue after waiting regardless.
3. Mode A first candle of leg: freeze leg_open_low=current Low, clear just_started, take/reset prior reset context. If RED immediately after GREEN reset and Low>=reset Low, choose greater of preceding GREEN run peak vs current High (GREEN wins equal), build A candidate with leg boundary, WAITING. Else RED anchors with origin leg_open. Continue.
4. Later A scanning: require GREEN predecessor and RED First. If anchor origin candidate_invalidation and both previous Low and First Low strictly below anchor Low, clear anchor. With anchor require First Low>=anchor Low; without anchor require First Low>=previous Low OR >=leg_open_low. On pass choose top max GREEN run/current with run winning tie; A candidate bottom First Low, anchor fields if present, leg boundary frozen, WAITING. On fail RED replaces anchor/origin scan; DOJI/NEUTRAL clears; otherwise unchanged.
5. B scanning: RED creates candidate top=max running peak/current High (running wins equal), bottom minimum from candle after top source if earlier, otherwise current, through First inclusive; WAITING. Update running peak only on strict higher. End: if retain_initial save cursor next=end+1,state/floor/flag/anchor/origin/candidate. Return B direction result with original window. Direct state assignments preserve full chronological branch order.

## Reflection and publication

### RE16 — mirror_candle (642–659)
Preserve index/time/display, swap GREEN/RED only, leave other tags unchanged. Negate open/close, mirrored High=-original Low, Low=-original High using copy_negate. This is role adaptation, not doji reclassification.
### RE17 — mirror_candidate (662–679)
Null=>null. Replace top/bottom and their source fields swapped and sign-reflected; optional anchor/leg boundary negated; all other fields including gate flags unchanged.
### RE18 — mirror_analysis (681–687)
Null=>null; mirror event/source candle and negate extreme.
### RE19 — _ReflectedCandles.__init__ (698–700)
Retain source and same-length null mirror cache.
### RE20 — _ReflectedCandles.__len__ (702–703)
Source length.
### RE21 — _ReflectedCandles.__getitem__ (705–712)
Slice materializes list via normalized slice indices; single index cache miss mirrors and saves candle; return cached object.
### RE22 — _reflected_view (718–725)
Global cache by id and exact source identity; allocate view on miss.
### RE23 — BearishDetector.__init__ (736–748)
Base init, bullish reference on original sequences, then replace reference candles/seconds with reflected views and lower index with reflected adapter. Times remain original.
### RE24 — red_run_bottom_before (750–752)
Reference RE09 then negate value and mirror source back.
### RE25 — breakdown_analysis (754–757)
Mirror inputs, reference RE10, mirror analysis back.
### RE26 — invalidation_high_break_before_breakdown (759–762)
Mirror candidate/candle, reference RE11.
### RE27 — confirmed_reset_before_breakdown (764–768)
Mirror candidate/candle and negate confirmed top; RE12.
### RE28 — post_breakdown_reset (770–775)
Mirror analysis/candle, negate top, RE13; mirror non-null result back.
### RE29 — BearishDetector.detect (777–785)
Reference detect first_only; return R with mirrored candidates, reset broken levels sign-reflected, original start/end.
### RE30 — published_reaction_candidate (788–883)
Clone input. Missing Break or invalid First/Break bounds returns clone unchanged. For B only if bottom source==Break, initialize min Low from First then complete main candles strictly before Break; threshold top. For R only if top source==Break, max High and threshold bottom. Unsupported direction raises after bounds check. Scan lower within Break main; update opposite extreme first, then strict confirmation check on same row; if confirmation found freeze price/source (Break main for lower extreme), earliest equal main source. If no confirmation leave clone unchanged. Does not mutate detection.

## Segment indexes

### RE31 — LowerTimeframeIndex.__init__ (893–907)
Store candles, optional OrderedDict crossing history, timestamp list; power-of-two size>=length starting1. Min/max arrays null, signed int positions -1 of size2*size. Fill leaves then parents.
### RE32 — _fill_leaves (909–916)
From first through length, normalized low/high and position at leaf size+position.
### RE33 — _update_parents (917–939)
Descending nodes last..before_first exclusive. Null left=>right, null right or left min<=right/max>=right=>left, otherwise right; copy corresponding position. Earliest tie.
### RE34 — refresh_suffix (941–957)
Require 0<=first<=old length<=new length<=size; if first==new length no-op. Clear history if dirty first<old length-1. Replace timestamp suffix, update length/leaves, recompute affected ancestor ranges bottom-up.
### RE35 — first_less (959–960)
RE40 minimum tree, exclude nodes with value>=level.
### RE36 — first_greater (962–963)
RE40 maximum tree, exclude nodes with value<=level.
### RE37 — range_minimum (965–967)
RE39 minimum=true.
### RE38 — range_maximum (969–971)
RE39 minimum=false.
### RE39 — _range_query (973–1009)
Require left>=0,right<=length,left<right. Standard half-open segment decomposition; consider non-null selected min/max values, strictly better or equal earlier position wins. Raise ValueError if no valid result; return value,position.
### RE40 — _first (1011–1017)
Clamp left>=0/right<=length; empty null. Dispatch history or direct RE43.
### RE41 — _first_with_history (1019–1035)
Key (left,level,excludes function). Cached crossing returned only if <right; examined>=right =>null. Search from examined. Settled excludes last candle (length-1); remember hit only if <settled, otherwise record no-hit coverage min(right,settled) when advanced. Return actual found crossing even latest unsettled.
### RE42 — _remember_crossing (1037–1040)
Assign history key; evict oldest FIFO when size>16384.
### RE43 — _search_first (1042–1062)
Root null or excluded =>null. Decompose interval; inspect left segments immediately, defer right segments and inspect reversed; first qualifying node descend RE44. Null none.
### RE44 — _descend_first (1064–1069)
Descend left child unless excluded then right; return leaf position.
### RE45 — shared_lower_timeframe_index (1077–1092)
If prepared supplied require its candles is source else ValueError; register and return. Otherwise reuse id+identity cached or construct/store.
### RE46 — ReflectedLowerTimeframeIndex.__init__ (1100–1102)
Retain base and same times.
### RE47 — reflected first_less (1104–1105)
Base first_greater with negated level.
### RE48 — reflected first_greater (1107–1108)
Base first_less with negated level.
### RE49 — reflected range_minimum (1110–1112)
Base maximum, negate value, preserve position.
### RE50 — reflected range_maximum (1114–1116)
Base minimum, negate value, preserve position.
### RE51 — clear_market_indexes (1119–1122)
Clear all three global time/range/reflected caches.
### RE52 — release_market_indexes (1125–1129)
For each supplied sequence remove id key from each global cache if present.

## MarketChronology and internal behavior

### RE53 — MarketChronology.__init__ (1153–1178)
Require timeframe_seconds>=1. Retain sequences; reuse prepared main/lower times when supplied, else build. Timeframe timedelta; lower index supplied or shared; store main range index. Empty confirmation/reset/E main extremes caches.
### RE54 — MarketChronology.opposite_direction (1181–1183)
RE02 wrapper.
### RE55 — main_index (1185–1192)
Upper_bound(main times,timestamp)-1; negative returns0 only if clamp else ValueError. No right-end guard.
### RE56 — lower_bounds (1194–1203)
Lower bounds start/end, end null=>len(seconds). Half-open interval.
### RE57 — lower_window (1205–1209)
Slice lower by RE56.
### RE58 — _reset_cache_key (1212–1221)
Tuple int index/from First defaults -1, second/display/timestamp defaults null, str broken level default empty.
### RE59 — _reaction_cache_key (1224–1236)
Direction,bool use_intrabar,int First/Break,str top/bottom, intrabar_start only if enabled else null.
### RE60 — reset_time (1238–1255)
Cache RE58; parse truthy second_time else truthy display_time using %Y-%m-%d %H:%M:%S, else timestamp attr. Cache result.
### RE61 — reaction_confirmation (1257–1302)
Cache RE59; Break main time. Start intrabar_start or candle_start if enabled, otherwise main start; invalid start outside Break resets to main start. Scan lower to Break end exclusive first strict High>top B or Low<bottom R, normalized. Cache/return exact event; absent => Break main start. A uses flag false; S/E/public usually true.
### RE62 — canonical_order_stop (1305–1367)
Mode A: scan_start=max(start_index,anchor_idx if non-null else First-1), extend backward while prior candle tag GREEN for bearish Order or RED for bullish. Inclusive through Break, max High bearish/min Low bullish, strict update first tie; return normalized price,source index,time. Other modes: reaction_number<=1 raises ValueError; previous opposite at number-2, use previous top/source bearish or bottom/source bullish. No new contextual extreme.
### RE63 — _BehaviorReactionSpan.from_reaction (1379–1386)
Published clone RE30; physical First/Break, First main time, exact RE61 confirmation, normalized published top/bottom.
### RE64 — may_contain (1388–1394)
Outer First strictly earlier; outer confirmation>=inner; outer top>=inner and bottom<=inner.
### RE65 — path_extremes (1396–1403)
Lower inclusive First through exact confirmation via lower/upper bound. Empty null; else min Low,max High from index.
### RE66 — contains_path (1405–1406)
Non-null extremes and bottom<=minimum and top>=maximum.
### RE67 — _apply_behavior_reaction_views (1409–1430)
For both directions zip full reactions/spans, assign 1-based behavior public number, published box, confirmation/First times, internal flag by blocked physical identity. Return full objects (not filtered), identity number maps, blocked sets and blocked First main times. Mutates Candidate metadata.
### RE68 — build_behavior_reaction_views (1433–1478)
Build spans both directions. Containment index only if all First/confirmation exact naive datetime; otherwise scan all opposite spans. For each inner, check outer may_contain; compute lower path once on first candidate; null path stops search; add blocked identity on first containing path. RE67.
### RE69 — LiveBehaviorReactionViews.__init__ (1496–1499)
Empty entries/matches per direction, update dirty0.
### RE70 — LiveBehaviorReactionViews.update (1501–1551)
Validate dirty main index. Geometry key First/Break/intrabar,str top and source,str bottom and source. At same ordinal reuse old entry when key equal and Break<dirty; else compute span/extremes and mark position changed only if new entry differs. Retain successful old inner/outer pairs when in bounds and neither changed. For changed inner compare all opposite; unchanged inner compare changed opposite only. Add pairs meeting RE64/66; blocked identities from all pairs. RE67, replace entries/matches, return.
### RE71 — directional_a_stop_order_finder (1554–1614)
Validate direction; choose opposite Order direction and tags, create gate and detection caches; return RE72 closure.
### RE72 — directional_a_stop_order_finder.find (1568–1612)
Key gate index,end (gate_event unused). First opposite First tag with preceding context tag from max(1,gate) through end. None cache null. Extend context run backward to0. Lookup cached detection tuple by context,end; first reaction First>=gate. If absent run Unified from context to end in opposite direction stopping first at/after gate, cache tuple and select. Cache order (including null).

## Unified Reaction ownership

### RE73 — UnifiedReactionDetector.__init__ (1627–1663)
Base init, store output direction and initial trend flags. Lazy B/R helpers null, reaction/reset lists per direction, empty geometry-after-reset and Order gate caches; live checkpoint and initial cursor null.
### RE74 — bull (1666–1671)
Lazy bullish detector same window/sequences.
### RE75 — bear (1674–1679)
Lazy bearish detector same window/sequences.
### RE76 — _append_reaction (1681–1761)
If Break, adjacent anchor (anchor+1==First) and prior Reset exists, run opposite reference from last reset through First; detect whether opposite reaction Break==anchor. If so bearish and anchor High<=First High: replace bottom with anchor Low/source; bullish and anchor Low>=First Low: replace top with anchor High/source. If Break exists canonical opposite edge recalculated inclusive First..Break by minimum Low B/max High R; if Break owns extreme and exact analysis available refine to pre-confirmation geometry. Append replace(candidate) to direction list, return true. Mutates supplied candidate before copy.
### RE77 — _append_reset (1763–1779)
Append ResetEvent main index/display, optional exact second display, level and prior First.
### RE78 — _refine (1781–1800)
Directional analysis RE10/25. Null =>null. Refine opposite edge only if candidate source index equals current candle.index; return analysis.
### RE79 — _candidate_from_confirmation_remainder (1802–1851)
Require Break correct First color (RED B/GREEN R) and analysis. Reject if exact lower after confirmation through Break end strictly crosses analysis.extreme outward. Collect entire Break lower interval; absent=>null. Choose max High earliest timestamp (key high,-epoch), min Low earliest timestamp. Return mode B candidate with First and both sources current main, levels from lower, intrabar_start main open. No partial-remainder-only levels. confirmed argument unused.
### RE80 — _first_initial (1853–1885)
With retain_initial, trend flag routes RE82 and asserts cursor type; otherwise reference B or reflected R _scan first_only with initial cursor, retain its cursor, return first clone or mirror or null. Without retain flag use trend bootstrap if relevant else directional detect first_only, clone first or null.
### RE81 — _first_bullish_trend_reaction (1887–1889)
RE82 bullish.
### RE82 — _first_trend_reaction (1891–1944)
Empty window null. Fixed source from cursor or first main; restore candidate clone and next index. Before candidate update fixed peak High B/trough Low R strictly; on required First color create mode A using fixed confirmation edge and current opposite edge, leg boundary initial main Low B/High R; continue (cannot confirm same First). After candidate update opposite edge strictly; strict directional confirmation sets Break and refines, returns. If unresolved and retaining cursor save next=end+1,fixed source,candidate; null. No initial boundary invalidation.
### RE83 — _first_direct_same_direction_after_reset (1947–1958)
First element RE84.
### RE84 — _direct_reset_search (1960–1991)
First candidates strictly after Reset, beyond blocked_through, proper color and predecessor. RE92 build then RE93 scan to end. Confirmed=>return candidate and flag of earlier pending. Unconfirmed with null invalidation sets earlier_pending true and permits later candidates; invalidated blocks through that index. Exhaustion returns null,true.
### RE85 — _first_geometry_after_reset (1993–2044)
Limit min requested/end, cache lookup key direction/reset/limit; clone non-null hit. Iterate First tag after reset with context predecessor, RE92. Scan later candles, update opposite extreme and strict confirm, refine and return first completed candidate in First traversal order, else null. Does not enforce invalidation; source contains lookup but no cache writes in this method.
### RE86 — first_geometry_after_reset (2046–2050)
RE85 public wrapper.
### RE87 — _reaction_break_indices (2053–2066)
Cache direction and list length; if length unchanged return cached ascending Break index list; else rebuild int values.
### RE88 — first_order_reaction_after_gate (2068–2215)
Bound limit; reject gate<start or gate>=limit. Cache key direction/gate/limit/exact gate, return copy on hit. Latest prior confirmed owner via lower_bound Break; same-main Break qualifies only RE90. Default search gate+1. No owner: RE91, set gate no-history if result, cache RE89. Owner: outer boundary min Low B/max High R from owner First through max(First,gate-1); gate boundary gate High B/Low R. Search lower [exact gate or gate main,limit main end). Empty or neither strict crossing => cached null. Restart when outward crosses before or equal gate boundary crossing; continuation otherwise. Restart maps event to selected main, search from that index+1, null unmappable. Reject start>limit. RE91 first complete geometry, assign decision. Continue with missing anchor index or value: latest prior reset index strictly before result First, reconstruct outer extreme reset..First-1 and assign anchor index/value/leg boundary; existing complete anchor never overwritten. Cache and return.
### RE89 — first_order_reaction_after_gate.cache_result (2084–2093)
If cache >=32768 delete oldest insertion; store shallow copy or null, return original.
### RE90 — first_order_reaction_after_gate.confirmed_no_later_than_gate (2095–2113)
Break<gate or no exact gate => Break<=gate; Break>gate false. Equal main: scan from intrabar_start or main through end; first strict directional confirmation <=gate event; absent => compare Break main time.
### RE91 — _earliest_confirmed_geometry (2217–2289)
Scan main from start to bounded end. reset_index=max(detector start,start-1). Each eligible color transition strictly after reset adds RE92 candidate. For all active candidates skip scan<=First; reject RE94 invalidation; update opposite edge strictly; strict confirmation sets Break/refines and collects confirmed. Keep survivors. First main with confirmations returns min First index among confirmed (does not sort exact lower confirmation times among same-main candidates). Null if none.
### RE92 — _build_direct_candidate (2291–2346)
Require First>reset, correct tag and prior context. Find contiguous context run backward inclusive reset, then contiguous preceding First-color run also bounded reset. B local floor min Low local_start..First-1; reject First Low<floor. Top max High context_start..First, bottom First Low. Outer leg floor/source min Low reset..First-1. R mirror local ceiling/max, bottom min Low, top First High, outer max High. Return mode A with anchor and leg boundary equal outer extreme.
### RE93 — _scan_direct_candidate (2349–2377)
For each later main through stop inclusive calculate strict confirmation, RE94 invalidation first =>null,index. Update opposite edge strictly; on confirmation set Break/refine, return candidate,null. End null,null.
### RE94 — _owner_boundary_before_confirmation (2379–2417)
Missing leg boundary false. Main no strict outer breach false; breach without confirmation true. Both: scan lower main window, outward check first each row (wins same-row tie), then strict confirm; return accordingly. No resolution =>true. Equality preserves structure.
### RE95 — _result (2420–2427)
Return DetectionResult with output direction, actual direction reaction/reset lists, window.
### RE96 — UnifiedReactionDetector.detect (2429–2432)
RE97 retain_cursor false.
### RE97 — _detect (2434–2515)
Initial RE80 with optional retained cursor; absent return empty result. Append RE76; if requested First gate satisfied return. Initialize previous initial, next=Break+1, running peak/trough from Break, source Break, candidate null. Analyze Break; exact analysis extreme or opposite box as reset level. Post-confirmation reset RE13/28 => append exact event and pending Break index; otherwise seed RE79. RE98 with cursor and requested stop flag.
### RE98 — _scan_normal (2517–2781)
Restore cursor previous/candidate/running/next/pending. For each main, reset if pending or strict crossing previous opposite edge; if reset and candidate strict confirms, use directional RE12/27 race. On Reset choose pending or current main; if retain and earliest_open absent snapshot cursor + counts before recording. Clear pending; append reset unless last reset already from previous First. With snapshot run RE84; if earlier pending or unresolved save earliest_open; else RE83. Missing structural or Break =>break. Set mode A and both cross-direction flags false; append RE76 (source has false-return branch advancing to Break+1/pending, though RE76 returns true). Stop early if requested First gate. Set previous structural,next Break+1,running Break extreme/source; analyze exact confirmation, reset level from analysis or box; post-reset append exact event, clear candidate/set pending Break; otherwise RE79. Continue without increment.
When candidate exists, B updates bottom strict and confirms High>top; R updates top strict and confirms Low<bottom. Set Break, refine, compute reset level and post-reset BEFORE append; append, early stop if First gate; previous clone, running=current High/Low/source; if post-reset append, clear candidate/set pending; else seed RE79. When no candidate, B RED opens mode B top=max running/current High (running source wins equal), bottom min from after top source if earlier else current through First; R GREEN mirror bottom=min running/current Low and top max. Update running directional peak/trough strictly, increment index. On finish retain earliest_open checkpoint if any, otherwise current cursor/counts. Return RE95. This normal path owns actual same-direction restart, not cross-direction unlocking.

## Committed continuation

### RE99 — LiveReactionContinuation.__init__ (2792–2819)
Validate direction via policy, require >=2 committed main else LiveReactionUnavailable. Copy candles/lower, options and timeframe. RE104 initial validation; construct RE102, RE97 retain cursor, always release indexes finally. Save result/checkpoint/initial cursor, processed_main_candles=0.
### RE100 — result (2822–2823)
RE101 snapshot.
### RE101 — _snapshot (2826–2831)
Replace result, clone each mutable candidate and copy reset list.
### RE102 — _detector (2833–2834)
New Unified on lists, full window 0..len-1, direction/options.
### RE103 — _release_indexes (2837–2838)
RE52.
### RE104 — _validate_extension (2840–2864)
Positive timeframe, both batches nonempty. Main index0 when no previous, else index previous+1, positive timestamp gap divisible by timeframe. Lower index0 or +1 with strictly increasing time. Lower first>=new main first, lower last<new main last+timeframe. Violations LiveReactionUnavailable with distinct messages.
### RE105 — advance (2866–2867)
RE107 commit true.
### RE106 — preview (2869–2871)
RE107 commit false.
### RE107 — _extend (2873–2905)
Both empty return snapshot. Validate against last committed main/lower; concatenate into new lists, new detector. No checkpoint: processed=len(new batch main), RE97 with initial cursor. Else copy prior reaction/reset prefixes at checkpoint counts, clone cursor previous/candidate, processed=len(full main)-cursor.next_index, RE98. Always release new sequence indexes finally. Only commit true updates owned lists/result/checkpoints/initial cursor and processed count. Return snapshot either way.

## Audit boundary
107 named declarations covered; all directional adapters, nested closures and live/segment index methods identified. Source behavior, including actual fallback paths and tie ordering, takes precedence over comments. No market data or engine execution was performed.
