# RX — Complete Reaction module composition (V3)

## RX-M01 — Authority, input and output

Consume indexed main candles, ordered lower candles, inclusive main calculation bounds and requested direction. Native tag is GREEN when Open <= Close, RED otherwise. First is RED for B, GREEN for R; context is opposite. A physical Reaction is (First index, Break index) with both box prices and their source ownership, mode, optional anchor/leg boundary and intrabar start. Only confirmed native geometry goes into the canonical stream. Reset and public clipping are separate operations; neither visibility nor Order creation is owned by this module.

**Contract conventions.** B = bullish, R = bearish. Directional extreme X is Low for B and High for R; a strict improvement or stop is X < level for B and X > level for R. Confirmation uses High > top for B and Low < bottom for R. Main position/time, exact lower event, physical identity and ordinal are different fields. Preserve Decimal representation, original arithmetic order, stable traversal, and native failures unless an explicit fallback is specified. Use [declared record interfaces](../../Contracts/Declared_Record_Schemas.md) and [index/chronology services](20_Indexes_And_Caching.md). Procedure labels below name semantic operations, not required implementation symbols.


## RX-M02 — Reference geometry and regime bootstrap

There are three entry routes; do not conflate them:

| Route | Initial First | Invalidating boundary | Completion selection |
|---|---|---|---|
| Normal initial leg | Required color following context, anchored by initial/scan/invalidation RED in B coordinates | Anchor or frozen leg boundary | Selected WAITING candidate owns search until confirmation or invalidation |
| Isolated trend start | First correct-color candle may be at boundary; confirmation edge tracks extreme until First | No previous regime boundary invalidation | First later strict confirmation |
| Post-Reset bounded structural search | Eligible color transition strictly after Reset and last blocking invalidation | Frozen extreme from Reset through candle before First | Scan in First order; skip unfinished candidates, block through actual invalidation |

Use the bullish reference state for ordinary initial leg; reflect R exactly using sign-copy on Decimal and swap High/Low and GREEN/RED roles, not native color recomputation. Retain timestamps and identities. For B, initial leg records opening Low; the GREEN run peak sets top unless First High is strictly greater. On rejected candidate First, maintain anchor rules and do not allow nested geometry to displace the selected initial WAITING owner. In isolated trend bootstrap choose strict highest High B/lowest Low R from regime start before First; freeze confirmation edge once First exists; opposite edge evolves until a later confirming candle. The first candidate returns from its entry route, then Unified appends canonical geometry.

## RX-M03 — Unified normal continuation

1. Commit the initial candidate by canonicalization: possible adjacent confirmed opposite anchor supplies confirmation edge only under the explicit inequalities in RE76. Always recompute the opposite edge across First..Break; if Break owns it, refine to the first exact confirmation using RE10/25. Store a copy.
2. Derive running peak/trough from Break. Check the strictly later lower remainder for Reset at exact analyzed extreme, otherwise native edge. If Reset exists record it and carry pending Break reset; else allow the Break candle to seed next mode B only if its First color matches, exact analysis exists, and no outward strict remainder crossing. Its two edges come from the **entire** Break lower interval, not only the remainder.
3. During ordinary scan a pending/strict confirmed-edge Reset is evaluated before candidate confirmation, but a candidate that confirms within that main candle can win when lower evidence places confirmation first. Reset clears current search and reopens same direction; apply [Reset module](02_Reset_Algorithm.md) then commit the resulting mode A structure if any. If no new structure, stop.
4. Without Reset: waiting mode B updates opposite edge on strict improvement, then tests strict confirmation. On confirmation refine, compute later reset, append canonical Reaction, then reset or seed as in step 2. In scanning state open mode B on First color, with confirmation edge the better of running extreme/current candle (running wins equality); opposite edge from after the confirmation-edge source if earlier than First, through First. Update running edge strictly. Do not append an unfinished candidate.
5. End result carries native chronological lists and original calculation bounds. Snapshot/preview operations in [Live Bridge](18_Live_Bridge.md) do not redefine the batch path.

## RX-M04 — Independent Order geometry and internal ownership

Independent Order search uses the gate main index, optional exact event, bounded horizon and latest confirmed owner including same-main owner only if exact confirmation no later than gate. No owner: search from gate+1. Owner exists: compare first strict outward break of First..gate−1 boundary against first strict confirmation-side break of gate candle's edge over [gate event or main open, end main+TF). No evidence => no result; outward wins same-row tie. Restart searches from crossing main+1, continuation from gate+1. Among concurrently active valid candidates, first main candle with confirmation wins and earliest First within it wins (not a separate exact-event sort). Preserve valid anchor; reconstruct from last earlier Reset only if continue and anchor incomplete. This geometry is not automatically a canonical Reaction or Order.

After both directions exist, make published geometry clones; outer First strictly earlier, outer confirmation >= inner confirmation and outer box inclusively contains inner box. Require a nonempty available lower path through inner confirmation (no independent completeness or gap check), with min Low >= outer bottom and max High <= outer top. Empty path does not qualify. First valid containing opposite span marks internal. Keep all native records and ordinals; assign metadata rather than deleting. Chronological containment optimization may fall back to original scan; [Blue](03_Blue_Line.md) and [Lifecycle](10_Lifecycle.md) own subsequent visibility.

## RX-M05 — Failure and boundary rules

Equality does not confirm, invalidate or reset finite prices. No fabricated lower order inside a row: the invalidation checks use outward predicate first; confirmation analysis includes crossing row. Missing exact confirmation may retain native geometry or use Break main fallback in chronology service; these are not proof of exact event. No new rounding. Empty initial result yields empty canonical lists; malformed indexes or prices fail natively. Full per-operation sequence follows below; Reset and indexes are specified separately.

## Detailed Reaction procedures (RE01–RE30, RE63–RE98)

### RE01 — classify_candle_color
GREEN iff open<=close (including equality), RED otherwise.

### RE02 — opposite_direction
Return direction policy opposite; invalid direction follows policy exception.

### RE03 — DetectorBase.__init__
Retain candles, lower, start/end as supplied references and bounds. Obtain shared main times, lower times, then lower segment index; initialize empty instance reaction-break index cache. Timeframe difference first two main timestamps or 1s for <=1 row; require positive. Registry publication may already have occurred before timeframe validation; no local rollback or all-grid validation.

### RE04 — DetectorBase._shared_time_index
Global cache by id and exact object identity; on miss build timestamp list in source order and retain source/list. Cache hit returns the same list, with no mutation freshness check or sorting.

### RE05 — seconds_between
Compute both lower bounds eagerly; return generator with fixed increasing position range [lower_bound(start),lower_bound(end)). Element lookup is lazy against the retained lower sequence; no synthetic gap fill.

### RE06 — main_source_for_time
Main position upper_bound(timestamp)-1; require selected index range; end next actual main timestamp or current+timeframe; return candle if timestamp<end else null.

### RE07 — minimum_low
Inclusive main index range; when end-start>=16 (17 inclusive rows) use shared range index, reflected view queries original maximum then copy-negates. Index leaves normalize via the shared Decimal helper; the linear route reads stored prices directly, initializes source at start even for a reversed interval, then scans strict lower, first equal owner. No local interval validation on linear route. Return value and corresponding (possibly reflected) candle; equivalent results require valid aligned native input, not arbitrary malformed inputs.

### RE08 — maximum_high
Mirror of RE07: strict higher, reflected queries original minimum then copy-negates. Same threshold, tie and validity qualifications; stored-price linear route versus normalized indexed route.

### RE09 — BullishDetector.green_run_peak_before
Previous main index must be >=start and GREEN, else ValueError. Extend contiguous GREEN run backward to start; RE08 inclusive peak.

### RE10 — breakout_analysis
Start index = top source+1 if top source<First, else top source; this is evaluated even when a truthy candidate.intrabar_start supplies the start. Otherwise use derived main time. End supplied Break main+nominal timeframe, half-open lower window; no local clamp of start to Break or main-crossing admission check. First lower High>BoxTop; null absent. Min Low through crossing inclusive, map minimum timestamp (not crossing timestamp) to selected main candle; null if unmappable. Return analysis(event lower candle,extreme,main source); no candidate mutation.

### RE11 — mode_a_invalidation_before_breakout
Caller admits Mode A; helper does not test mode or emit Reset. Level anchor_value if non-null else leg_boundary. Missing or main Low>=level false; main High<=top with strict low breach true. If both, query exact lower first Low<level then High>top across current main open to open+nominal timeframe, end exclusive, regardless of intrabar_start. Both queries precede arbitration. No invalidation => true only if no breakout either; invalidation present/no breakout true; both => invalidation_position<=breakout_position (same lower position invalidates first; duplicate timestamps at different positions do not establish a tie).

### RE12 — confirmed_reset_before_breakout
Caller supplies reset context; helper does not test main Low or emit Reset. Null candidate or main High<=top true. Else query Low<confirmed bottom then High>candidate top across full nominal current main interval, with same no-event and positional tie logic RE11.

### RE13 — post_breakout_reset
Null analysis =>null. Search lower Low<box_bottom strictly after confirmation (event+1us) through Break end exclusive. Return lower candle or null.

### RE14 — BullishDetector.detect
RE15 first_only flag.

### RE15 — BullishDetector._scan
Initialize empty results, mode A, SCANNING, null last confirmed/running peak/leg floor/anchor/reset context/candidate; leg just started true. Optional initial cursor restores index,state,leg floor,flag,anchor/origin,copy candidate; no prior confirmed state. For each main:
1. Strict Low<last confirmed bottom signals Reset; if WAITING use RE12 race. Reset event uses main display, second_time null, previous bottom and First; clear candidate/confirmed/peak, mode A SCANNING, null floor, just_started, anchor=current RED if so (origin reset), reset_context=current; continue.
2. WAITING: mode A and RE11 => discard candidate, SCANNING, RED anchor origin candidate_invalidation or null; continue. Update box bottom on strict lower. If High>BoxTop set Break; RE10; refine bottom only when current main owns it and analysis exists. Append replacement candidate. first_only => immediate result. Else update last confirmed bottom/First, peak=current High, mode B SCANNING, candidate null. RE13 same-Break post-reset => record exact second display, clear state as in step1 and continue. Otherwise RED Break seeds next B candidate on same candle with top running peak and bottom current Low, WAITING. Continue after waiting regardless.
3. Mode A first candle of leg: freeze leg_open_low=current Low, clear just_started, take/reset prior reset context. If RED immediately after GREEN reset and Low>=reset Low, choose greater of preceding GREEN run peak vs current High (GREEN wins equal), build A candidate with leg boundary, WAITING. Else RED anchors with origin leg_open. Continue.
4. Later A scanning: require GREEN predecessor and RED First. If anchor origin candidate_invalidation and both previous Low and First Low strictly below anchor Low, clear anchor. With anchor require First Low>=anchor Low; without anchor require First Low>=previous Low OR >=leg_open_low. On pass choose top max GREEN run/current with run winning tie; A candidate bottom First Low, anchor fields if present, leg boundary frozen, WAITING. On fail RED replaces anchor/origin scan; DOJI/NEUTRAL clears; otherwise unchanged.
5. B scanning: RED creates candidate top=max running peak/current High (running wins equal), bottom minimum from candle after top source if earlier, otherwise current, through First inclusive; WAITING. After possible candidate construction, initialize a null running peak or update it only on strict higher; equality retains the existing source. End: if retain_initial save cursor next=end+1,state/floor/flag/anchor/origin/candidate. Return B direction result with original window. Direct state assignments preserve full chronological branch order.

## Reflection and publication

### RE16 — mirror_candle
Preserve index/time/display, swap GREEN/RED only, leave other tags unchanged. Negate open/close, mirrored High=-original Low, Low=-original High using copy_negate. This is role adaptation, not doji reclassification.

### RE17 — mirror_candidate
Null=>null. Replace top/bottom and their source fields swapped and sign-reflected; optional anchor/leg boundary negated; all other fields including gate flags unchanged.

### RE18 — mirror_analysis
Null=>null; mirror event/source candle and negate extreme.

### RE19 — _ReflectedCandles.__init__
Retain source and allocate null mirror cache to its initial length; current length queries use the source, and no automatic cache resize or freshness check is implemented.

### RE20 — _ReflectedCandles.__len__
Source length.

### RE21 — _ReflectedCandles.__getitem__
Slice materializes list via normalized slice indices; single index cache miss mirrors and saves candle; return cached object.

### RE22 — _reflected_view
Global cache by id and exact source identity; allocate view on miss.

### RE23 — BearishDetector.__init__
Base init, bullish reference on original sequences, then replace reference candles/seconds with reflected views and lower index with reflected adapter. Times remain original.

### RE24 — red_run_bottom_before
Reference RE09 then negate value and mirror source back.

### RE25 — breakdown_analysis
Mirror inputs, reference RE10, mirror analysis back.

### RE26 — invalidation_high_break_before_breakdown
Mirror candidate/candle, reference RE11.

### RE27 — confirmed_reset_before_breakdown
Mirror candidate/candle and negate confirmed top; RE12.

### RE28 — post_breakdown_reset
Mirror analysis/candle, negate top, RE13; mirror non-null result back.

### RE29 — BearishDetector.detect
Reference detect first_only; return R with mirrored candidates, reset broken levels sign-reflected, original start/end.

### RE30 — published_reaction_candidate
Clone input. Missing Break or invalid First/Break bounds returns clone unchanged. For B only if bottom source==Break, initialize min Low from First then complete main candles strictly before Break; threshold top. For R only if top source==Break, max High and threshold bottom. Unsupported direction raises after bounds check. Scan lower within Break main; update opposite extreme first, then strict confirmation check on same row; if confirmation found freeze price/source (Break main for lower extreme), earliest equal main source. If no confirmation leave clone unchanged. Bounds allow First==Break: initialization then uses the full First/Break main extreme before the lower scan, so the lower scan does not guarantee removal of a later extreme in that case. Do not impose a First<Break guard or reset the initial extreme. Does not mutate detection.

## Segment indexes

### RE63 — _BehaviorReactionSpan.from_reaction
Published clone RE30 supplies normalized top/bottom; physical First/Break and First main time come from original reaction, and RE61 confirmation is evaluated on original reaction with default intrabar flag (including its main-open fallback).

### RE64 — may_contain
Outer First strictly earlier; outer confirmation>=inner; outer top>=inner and bottom<=inner.

### RE65 — path_extremes
Lower inclusive First through RE61 confirmation time via lower/upper bound. Empty null; else min Low then max High from index. Nonempty observed path is required, but this helper does not validate gap-free coverage.

### RE66 — contains_path
Non-null extremes and bottom<=minimum and top>=maximum.

### RE67 — _apply_behavior_reaction_views
For bullish then bearish, zip full reactions/spans (shorter input truncates without explicit length validation), assign 1-based behavior public number, published box, confirmation/First times, internal flag by blocked physical identity. Return full objects (not filtered), identity number maps for all full reactions, blocked sets and blocked First main-time sets. Mutates Candidate metadata without internal rollback.

### RE68 — build_behavior_reaction_views
Build spans both directions. Containment index only if all First/confirmation exact naive datetime; otherwise scan all opposite spans. For each inner, check outer may_contain; compute lower path once on first candidate; null path stops search; add blocked identity on first containing path. RE67.

### RE69 — LiveBehaviorReactionViews.__init__
Empty entries/matches per direction, update dirty0.

### RE70 — LiveBehaviorReactionViews.update
Validate dirty main index. Geometry key First/Break/intrabar,str top and source,str bottom and source. At same ordinal reuse old entry when key equal and Break<dirty; else compute span/extremes and mark position changed only if new entry differs. Retain successful old inner/outer pairs when in bounds and neither changed. For changed inner compare all opposite; unchanged inner compare changed opposite only. Add pairs meeting RE64/66; blocked identities from all pairs. RE67 mutates full native Candidate metadata, then replace entries/matches and return; no local rollback or clone of full results. Dirty bound is inclusive 0..len(main); retain all successful position pairs, not a single selected owner.

### RE71 — directional_a_stop_order_finder
Validate direction; choose opposite Order direction and tags, create gate and detection caches; return RE72 closure.

### RE72 — directional_a_stop_order_finder.find
Key gate index,end (gate_event unused). First opposite First tag with preceding context tag from max(1,gate) through end. None cache null. Extend context run backward to0. Lookup cached detection tuple by context,end; first reaction First>=gate. If absent run Unified from context to end in opposite direction stopping first at/after gate, cache tuple and select. Cache and return order (including null) by reference, not a clone; no automatic cache invalidation or exact gate-event acceptance inside this closure.

## Unified Reaction ownership

### RE73 — UnifiedReactionDetector.__init__
Base init, store output direction and initial trend flags. Lazy B/R helpers null, reaction/reset lists per direction, empty geometry-after-reset and Order gate caches; live checkpoint and initial cursor null.

### RE74 — bull
Lazy bullish detector same window/sequences.

### RE75 — bear
Lazy bearish detector same window/sequences.

### RE76 — _append_reaction
If Break, adjacent anchor (anchor+1==First) and prior Reset exists, run opposite reference from last reset through First; detect whether opposite reaction Break==anchor. If so bearish and anchor High<=First High: replace bottom with anchor Low/source; bullish and anchor Low>=First Low: replace top with anchor High/source. If Break exists canonical opposite edge recalculated inclusive First..Break by minimum Low B/max High R; if Break owns extreme and exact analysis available refine through the confirming lower row inclusive, otherwise keep full-main extreme. A null Break skips canonical recomputation but does not prevent append. Append replace(candidate) to direction list, return true. Mutates supplied candidate before copy; caller owns confirmation validity.

### RE77 — _append_reset
Append ResetEvent main index/display, optional exact second display, level and prior First.

### RE78 — _refine
Directional analysis RE10/25 (exact bullish selects breakout, otherwise breakdown). Null =>null. Separate exact bullish/bearish guards refine the corresponding opposite edge only if its source equals current candle.index; nonbullish/nonbearish input can dispatch breakdown without mutating either edge. Return nonnull analysis even if no refinement.

### RE79 — _candidate_from_confirmation_remainder
Require Break correct First color (RED B/GREEN R) and analysis. Reject if exact lower after confirmation through Break end strictly crosses analysis.extreme outward. Collect entire Break lower interval; absent=>null. Choose max key (High, negative native timestamp.timestamp() epoch float) and min key (Low, datetime); equal full keys retain first encountered row. Bullish evaluates top then bottom, otherwise bottom then top. Native epoch conversion and precision govern top tie behavior, not an additional exact datetime comparison. Return mode B candidate with First and both sources current main, levels from lower, intrabar_start main open. No partial-remainder-only levels. confirmed argument unused.

### RE80 — _first_initial
With retain_initial, trend flag routes RE82 and asserts cursor type; otherwise reference B or reflected R _scan first_only with initial cursor, retain its cursor, return first clone or mirror or null. Without retain flag ignore supplied cursor; check exact bullish trend then exact bearish trend, else directional detect first_only, clone first or null. Retaining ordinary bearish route scans reflected reference then mirrors candidate once; cursor type assertions depend on native assertion configuration.

### RE81 — _first_bullish_trend_reaction
RE82 bullish.

### RE82 — _first_trend_reaction
Empty window null. Fixed source from cursor or first main; restore candidate clone and next index. Before candidate update fixed peak High B/trough Low R strictly; on required First color create mode A using fixed confirmation edge and current opposite edge, leg boundary initial main Low B/High R; continue (cannot confirm same First). After candidate update opposite edge strictly; First, improved opposite source and Break use loop positions, whereas initial box source indices come from Candle.index. Strict directional confirmation sets Break and refines, returns without saving a new cursor. Only normal exhaustion with retention saves next=end+1,fixed source,candidate reference; null. Empty window returns before cursor save. No initial boundary invalidation.

### RE83 — _first_direct_same_direction_after_reset
First element RE84.

### RE84 — _direct_reset_search
First candidates strictly after Reset, beyond blocked_through, proper color and predecessor. RE92 build then RE93 scan to end. Confirmed=>return candidate and flag of earlier pending. Unconfirmed with null invalidation sets earlier_pending true and permits later candidates; invalidated blocks through that index. Exhaustion returns null,true.

### RE85 — _first_geometry_after_reset
Limit min requested/end, cache lookup key direction/reset/limit; clone non-null hit. Iterate First tag after reset with context predecessor, RE92. Scan later candles, update opposite extreme and strict confirm, refine and return first completed candidate in First traversal order, else null. Does not enforce invalidation; source contains lookup but no cache writes in this method.

### RE86 — first_geometry_after_reset
RE85 public wrapper.

### RE87 — _reaction_break_indices
Cache direction and list length; if cached entry nonnull and length unchanged return same list reference; else rebuild int Break values in current stream order. No local sort, duplicate check or freshness check; ascending append-only stream is a caller invariant.

### RE88 — first_order_reaction_after_gate
Bound limit; reject gate<start or gate>=limit. Cache key direction/gate/limit/exact gate, return copy on hit. Latest prior confirmed owner via lower_bound Break; same-main Break qualifies only RE90. Default search gate+1. No owner: RE91, set gate no-history if result, cache RE89. Owner: outer boundary min Low B/max High R from owner First through max(First,gate-1); gate boundary gate High B/Low R. Search lower [exact gate or gate main,limit main end). Empty or neither strict crossing => cached null. Restart when outward crosses before or equal gate boundary crossing; continuation otherwise. Restart maps event to selected main, search from that index+1, null unmappable. Reject start>limit. RE91 first complete geometry, assign decision. Continue with missing anchor index or value: latest prior reset index strictly before result First, reconstruct outer extreme reset..First-1 and assign all anchor index/value/leg boundary fields, even if one anchor component was already populated; existing complete anchor never overwritten. Without a prior Reset leave the incomplete anchor unchanged. Cache and return.

### RE89 — first_order_reaction_after_gate.cache_result
If cache >=32768 delete oldest insertion; store shallow copy or null, return original.

### RE90 — first_order_reaction_after_gate.confirmed_no_later_than_gate
Break<gate or no exact gate => Break<=gate; Break>gate false. Equal main: scan from truthy intrabar_start or Break main open to Break end exclusive without RE61's start clamp; first strict directional confirmation <=gate event; absent => compare Break main open to gate (fallback, not observed confirmation).

### RE91 — _earliest_confirmed_geometry
Scan main from start to bounded end. reset_index=max(detector start,start-1). Each eligible color transition strictly after reset adds RE92 candidate. For all active candidates skip scan<=First; reject RE94 invalidation; update opposite edge strictly; strict confirmation sets Break/refines and collects confirmed. Keep survivors. First main with confirmations returns min First index among confirmed (does not sort exact lower confirmation times among same-main candidates). Null if none.

### RE92 — _build_direct_candidate
Require First>reset, correct tag and prior context. Find contiguous context run backward inclusive reset, then contiguous preceding First-color run also bounded reset. B local floor min Low local_start..First-1; reject First Low<floor. Top max High context_start..First, bottom First Low. Outer leg floor/source min Low reset..First-1. R mirror local ceiling/max, bottom min Low, top First High, outer max High. Return mode A with anchor and leg boundary equal outer extreme.

### RE93 — _scan_direct_candidate
For each later main through stop inclusive calculate strict confirmation before calling RE94; invalidation result true returns null,scan before mutation. Separate exact bullish and exact bearish guards update the opposite edge strictly. On saved confirmation set Break to loop scan (source updates use Candle.index), refine, return candidate,null. End null,null.

### RE94 — _owner_boundary_before_confirmation
Missing leg boundary false. Main no strict outer breach false; breach without confirmation true. Both: scan lower main window, outward check first each row (wins same-row tie), then strict confirm; return accordingly. No resolution =>true. Equality preserves structure.

### RE95 — _result
Return DetectionResult with output direction, actual direction reaction/reset lists, window.

### RE96 — UnifiedReactionDetector.detect
RE97 retain_cursor false.

### RE97 — _detect
Initial RE80 with optional retained cursor; absent return empty result. Append RE76; if requested First gate satisfied return. Initialize previous initial, next=Break+1, running peak/trough from Break, source Break, candidate null. Analyze Break; exact analysis extreme or opposite box as reset level. Post-confirmation reset RE13/28 => append exact event and pending Break index; otherwise seed RE79. RE98 with cursor and requested stop flag.

### RE98 — _scan_normal
Restore cursor previous/candidate/running/next/pending. For each main, reset if pending or strict crossing previous opposite edge; if reset and candidate strict confirms, use directional RE12/27 race. On Reset choose pending or current main; if retain and earliest_open absent snapshot cursor + counts before recording. Clear pending; append reset unless last reset already from previous First. With snapshot run RE84; if earlier pending or unresolved save earliest_open; else RE83. Missing structural or Break =>break. Set mode A and both cross-direction flags false; append RE76 (source has false-return branch advancing to Break+1/pending, though RE76 returns true). Stop early if requested First gate. Set previous structural,next Break+1,running Break extreme/source; analyze exact confirmation, reset level from analysis or box; post-reset append exact event, clear candidate/set pending Break; otherwise RE79. Continue without increment.
When candidate exists, B updates bottom strict and confirms High>top; R updates top strict and confirms Low<bottom. Set Break, refine, compute reset level and post-reset BEFORE append; append, early stop if First gate; previous clone, running=current High/Low/source; if post-reset append, clear candidate/set pending; else seed RE79. When no candidate, B RED opens mode B top=max running/current High (running source wins equal), bottom min from after top source if earlier else current through First; R GREEN mirror bottom=min running/current Low and top max. After the normal path, initialize null running directional peak/trough or replace it only on strict improvement, with separate exact bullish and bearish guards; increment index. On finish retain earliest_open checkpoint if any, otherwise current cursor/counts. Return RE95. This normal path owns actual same-direction restart, not cross-direction unlocking.

## Committed continuation
