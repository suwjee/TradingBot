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
Null analysis => null before any time/index access. Otherwise lower-bound bisect at confirmation event timestamp +1 microsecond and nominal Break end, search strict Low<supplied box_bottom in that half-open positional range; excludes all equal-event timestamps, not only the crossing row. Return exact selected self.seconds row (possibly reflected) or null; no fallback, local clamp, sorting or rollback. Requires coherent time/row/index alignment.

### RE14 — BullishDetector.detect
Forward first_only unchanged to RE15 with default initial and retain_initial; no additional filtering.

### RE15 — BullishDetector._scan
Initialize new empty result arrays, mode A, SCANNING, null last confirmed/running peak/leg floor/anchor/reset context/candidate; leg just started true. Read detector start and clear instance _initial_cursor. Optional non-null initial cursor restores index,state,leg floor,flag,anchor/origin and shallow copy of non-null candidate; no prior confirmed state, mode, peak or reset context restored. Traverse selected positions through detector end inclusive, without local clamp:
1. Non-null last confirmed bottom and strict Low<bottom signals Reset; only when WAITING use RE12 race. Reset event uses main index/display, second_time null even if lower race evidence exists, previous bottom and First; clear candidate/confirmed/peak, mode A SCANNING, null floor, just_started, anchor=current RED if so (origin reset), reset_context=current; continue.
2. WAITING: require non-null candidate by native assertion (when enabled). Mode A and RE11 => discard candidate, SCANNING, RED anchor origin candidate_invalidation or null; continue, no Reset and no other leg register reset. Update bottom/source on strict lower before strict High>BoxTop; set Break before RE10; refine price/source unconditionally only when current main owns bottom and analysis exists. Append shallow replacement candidate. first_only => immediate bullish result with original bounds, no post-break state/reset/cursor retention. Else update last confirmed bottom/First, peak=current High/index, mode B SCANNING, candidate null. RE13 with confirmed bottom => record exact lower display, clear state as step1 and continue. Otherwise RED Break seeds next B on same main with top running peak and full main Low, regardless of analysis availability. Continue after WAITING regardless; no B scan peak update.
3. Mode A first candle of leg: freeze leg_open_low=current Low, clear just_started, take/reset prior reset context. If RED immediately after GREEN reset and Low>=reset Low, choose greater of preceding GREEN run peak vs current High (GREEN wins equal), build A candidate with leg boundary and default null anchor fields, WAITING. Else RED anchors with origin leg_open; non-RED preserves existing anchor/origin. Continue.
4. Later A scanning: read previous positional row index-1. Require GREEN predecessor and RED First. If non-null anchor origin candidate_invalidation and both previous Low and First Low strictly below anchor Low, clear anchor. With remaining anchor require First Low>=anchor Low, no alternate fallback; without anchor require First Low>=previous Low OR >=leg_open_low in order. On pass choose top max GREEN run/current with run winning tie; assert non-null top/source when enabled; A candidate bottom First Low, anchor fields by truthiness, leg boundary frozen, WAITING. On fail RED replaces anchor/origin scan; explicit DOJI/NEUTRAL tag clears; otherwise unchanged (native equal open/close remains GREEN).
5. Non-A scanning: RED creates B candidate top=max running peak/current High (running wins equal), bottom minimum from candle after top source if earlier, otherwise current, through First inclusive; WAITING. After possible candidate construction, initialize a null running peak or update it only on strict higher; equality retains existing source. At normal exhaustion only, if retain_initial save cursor next=end+1,state/floor/flag/anchor/origin and pending candidate reference (no copy at save); no confirmed/peak/reset_context history. Return literal bullish result with original bounds and confirmed lists only. Native index/type/assertion failures propagate; no local transactional rollback.

## Reflection and publication

### RE16 — mirror_candle
Create a new Candle preserving index/time/display, swap GREEN/RED only, leave other tags unchanged. Negate open/close, mirrored High=-original Low, Low=-original High using Decimal copy_negate in OHLC argument order; no price reclassification or context rounding. This is role adaptation, not market doji reclassification.

### RE17 — mirror_candidate
Null=>null. Shallow replacement, swap and sign-copy top/bottom and paired source index/display fields; optional non-null anchor/leg boundary sign-copied (zero included). Preserve all unlisted fields, including First/Break, anchor index, mode, intrabar start, cross-direction/gate flags and behavior_public_* geometry/number/time/internal metadata without additional reflection. Separate object, not a deep copy.

### RE18 — mirror_analysis
Null=>null. Construct new IntrabarAnalysis by mirroring event Candle, sign-copying extreme, then mirroring source Candle separately in that order. Distinct new Candle objects even if original event/source alias; preserve stored index/time, not reference identity.

### RE19 — _ReflectedCandles.__init__
Retain original source and allocate null mirror cache to initial source length; current length queries use source, and no automatic cache resize, mutation detection or freshness check is implemented.

### RE20 — _ReflectedCandles.__len__
Return current source length, not fixed cache capacity.

### RE21 — _ReflectedCandles.__getitem__
Slice materializes a list via indices normalized against current source length, preserving requested order; repeated scalar reads may fill earlier slots before a later failure. Scalar lookup indexes the fixed cache first (including negative indexes), mirrors source[index] only on a null slot, stores and returns exact cached object. Source mutation/resizing can leave stale values, mismatched negative positions or out-of-bounds slots; no local refresh or rollback.

### RE22 — _reflected_view
Process-local cache by id and exact source identity; cached pair retains source and view. Allocate view before publishing pair on miss; return exact cached view on hit. No local eviction or freshness check. The clear/release helpers remove registry entries, not external references.

### RE23 — BearishDetector.__init__
Base init, then Bullish reference on original sequences, then replace reference candles, seconds and lower index in that order using reflected views and adapter over original lower index. Time arrays remain original. Constructor/registry effects before failure are not locally rolled back.

### RE24 — red_run_bottom_before
Reference RE09 with unchanged positional argument, then sign-copy returned value and mirror source into a new candle; physical fields preserved, object identity not restored.

### RE25 — breakdown_analysis
Mirror candidate and candle, call reference RE10, mirror returned analysis. Nullable mirror helper does not independently validate delegate input.

### RE26 — invalidation_high_break_before_breakdown
Mirror candidate/candle, return reference RE11 result; wrapper does not recheck caller admission.

### RE27 — confirmed_reset_before_breakdown
Mirror candidate/candle and sign-copy confirmed top; return RE12 result; wrapper adds no main breach test.

### RE28 — post_breakdown_reset
Mirror analysis, sign-copy top, mirror candle in that order before calling RE13, even if analysis is null; mirror non-null hit into new candle, otherwise return null. No wrapper shortcut or local recovery.

### RE29 — BearishDetector.detect
Reference detect with unchanged first_only; return new R result and ordered new lists with mirrored candidates and replaced resets (only broken_level sign-copied); original start/end retained, no renumbering.

### RE30 — published_reaction_candidate
Read chronology main/lower sequences before shallow cloning input. Missing Break returns clone before integer conversion or direction validation. Convert First then Break; negative First, reversed Break or Break outside full main array returns clone; conversion/access failures propagate. Read Break row and timeframe before exact direction dispatch. For B only if integer bottom source==Break, initialize min Low from full First then complete main candles strictly before Break; threshold top. For R only if integer top source==Break, max High and threshold bottom. Unsupported direction raises after bounds check and chronology attribute reads. Scan full Break lower interval [open, open+timeframe), not intrabar_start, in supplied order; update opposite extreme first, then strict confirmation check on same row. Lower extreme source is Break main, not lower row. Equality retains earlier selected owner. If confirmation found update only opposite price, source stored index and display time on clone; if absent leave clone unchanged even after temporary extrema changes. Bounds allow First==Break: initialization then uses full First/Break main extreme before lower scan, so scan does not guarantee removal of a later extreme in that case. Do not impose a First<Break guard or reset initial extreme. Does not mutate detection; no reclassification of ledger or behavior visibility.

## Segment indexes

### RE63 — _BehaviorReactionSpan.from_reaction
Compute published clone RE30 first, then integer-convert original First and Break; construct frozen slotted span with original physical pair, First main positional timestamp and RE61 confirmation evaluated on original reaction with default intrabar flag (including main-open fallback), followed by normalization of published top then bottom. These are separate provenance sources; no local failure fallback.

### RE64 — may_contain
Evaluate in order with short circuit: outer First strictly earlier; outer confirmation>=inner; outer top>=inner and bottom<=inner. Equal First excludes; other equalities admit.

### RE65 — path_extremes
Lower inclusive First through RE61 confirmation via bisect_left/bisect_right, including all boundary-equal rows under aligned ordered times. Empty/reversed positional interval returns null without price queries; otherwise min Low then max High from index, discard positions. Nonempty observed path required, but no gap-free coverage proof.

### RE66 — contains_path
Require non-null extremes, then bottom<=minimum and top>=maximum in order with short circuit; inclusive edges.

### RE67 — _apply_behavior_reaction_views
For bullish then bearish, enumerate zip of full reactions/spans from one (shorter input truncates without explicit length validation), assign metadata in order: behavior public number, published top/bottom, confirmation/First times, internal flag by span physical identity membership. Return full native objects (not cloned/filtered), identity number maps for all full reactions regardless of zip length, original blocked mapping and sets of First main timestamps (dedup by timestamp, not physical pair). Unprocessed tail may retain prior metadata. Mutates Candidate metadata without internal rollback; partial writes on failure possible.

### RE68 — build_behavior_reaction_views
Build all spans before owner search, bullish then bearish, preserve input order. Index only if all First/confirmation exact naive datetime (empty all true); no global ordering requirement, provider partitions on decreasing start or end to preserve caller order. Otherwise full opposite scan. Per inner reset lazy extrema; index enclosing is strict outer First/inclusive end candidate filter, not verdict. Check outer may_contain before path; compute lower path once on first eligible outer; null path stops owner search, first containing path adds inner physical identity then breaks. Blocked sets do not record owner pairs. Apply RE67 after both direction sets built.

### RE69 — LiveBehaviorReactionViews.__init__
Frozen slotted live entry holds geometry/span/nullable extrema (not deep immutability). Initialize separate empty entries and match sets, bullish then bearish; perform actual update dirty0. Constructor ignores returned tuple, but update mutates supplied Candidate metadata; no local constructor rollback.

### RE70 — LiveBehaviorReactionViews.update
Validate chained inclusive 0<=dirty<=len(main), short circuit (negative avoids length read), no integer-type or dataset-generation check. Key ordered First/Break/intrabar,str top and source,str bottom and source; price strings preserve representation distinctions, other fields use native equality, no object identity or generation. Same ordinal reuse exact old entry iff old non-null, geometry equal and Break<dirty; equality to dirty rebuilds. Else compute span then eagerly path extrema even without owners; mark changed only on full entry inequality (geometry, span, extrema), append rebuilt entry even if equal. Retain prior pairs when inner survives and unchanged then outer survives and unchanged; native ordinals nonnegative, upper bounds tested. Changed inner checks all current outer positions; unchanged inner checks changed outer set only, no chronological rank. RE64 before RE66, retain every passing ordinal pair, blocked physical identities deduplicate across owners; removal of one owner does not release an identity with another surviving match. Build span lists and apply RE67 on original full Candidate objects before replacing retained entries/matches. Failure before commit leaves old maps but can leave partial metadata or chronology/index side effects; no local transaction, clone, or proof of caller dirty correctness.

### RE71 — directional_a_stop_order_finder
Validate exact supported direction before cache allocation; choose opposite Order direction (bearish: GREEN First, RED context; bullish: RED First, GREEN context). Create two closure-local caches; capture sources by reference and return RE72 closure, no generation or eviction.

### RE72 — directional_a_stop_order_finder.find
Key (gate_index,end_index), gate_event unused. Membership hit returns stored Candidate reference or None before any candle reads. Lazy ascending First scan from max(1,gate) through end inclusive, current tag then preceding context tag; no upper clamp. Missing pair caches null. Extend contiguous preceding context backward to zero if eligible. Detection key (context,end); lookup tuple or empty, select first in stored order with int(required First)>=gate; no Break or exact confirmation-time check. If absent run Unified from context to end in opposite direction with default trend flags, stop after First>=gate; materialize and replace detection tuple before selecting again. Failure during reselection can leave detection cache replaced while outer key absent. Cache and return candidate or null by reference, not clone; no local invalidation, canonical Order creation or exact gate-event acceptance; caller owns admission.

## Unified Reaction ownership

### RE73 — UnifiedReactionDetector.__init__
Run Base init first, then store output direction and both initial trend flags as supplied, no local validation of direction/flags. Lazy B/R helpers null; separate fresh direction reaction/reset lists, separate empty geometry-after-reset and Order gate caches; live checkpoint and initial cursor null. Comments on immutable chronology do not establish caller lifetime.

### RE74 — bull
On null only construct bullish detector using current original arrays and bounds, assign after construction succeeds; return retained exact helper, no automatic refresh if fields later change.

### RE75 — bear
On null only construct independent bearish detector using current original arrays and bounds, assign after construction succeeds; return retained exact helper, no automatic refresh/rollback of earlier registry effects.

### RE76 — _append_reaction
Ordered short-circuit gate: non-null Break, non-null anchor, anchor+1==First, truthy direction Reset list. Use last inserted Reset index, construct opposite reference (exact bearish selects BullishDetector, otherwise BearishDetector) through candidate First; any opposite reaction Break==anchor confirms. If confirmed, read anchor/First rows; exact bearish and anchor High<=First High replaces bottom with anchor Low/source; otherwise nonbearish anchor Low>=First Low replaces top with anchor High/source. No independent comparison to existing edge or monotonic extension predicate. If Break non-null, convert First then Break to int, read Break row, canonical opposite edge recalculated inclusive First..Break by minimum Low for exact bullish, maximum High otherwise. Overwrite price/source; if stored source.index equals converted Break position and exact analysis non-null, overwrite with analysis extreme and source through confirming lower row inclusive. Otherwise retain recomputed full-main extreme; no improvement retest, new admission, or local bounds validation. Null Break skips recomputation but does not prevent append. Mutate supplied candidate then append shallow replacement to requested direction list, return literal true if successful; no rejection false path, dedup or rollback. Caller owns valid confirmation/direction.

### RE77 — _append_reset
Append new ResetEvent using supplied candle stored index/display, optional second display (default null), broken level and prior First. No local dedup, exact-event validation, normalization or rollback; caller owns admission.

### RE78 — _refine
Choose helper exact bullish else bearish, then invoke exact bullish breakout_analysis otherwise breakdown_analysis. Null returns before candidate writes. Separate exact bullish and exact bearish guards refine respective opposite edge only when source index equals current candle.index; overwrite price/source without improvement retest. Unsupported direction can dispatch breakdown without either mutation. Return nonnull analysis even if no refinement.

### RE79 — _candidate_from_confirmation_remainder
Exact bullish requires RED, otherwise GREEN; test tag mismatch first then null analysis. confirmed argument unused. Remainder bounds bisect_left at exact event+1 microsecond (all equal timestamps excluded) and current main open+timeframe exclusive. Strict first_less on analysis.extreme for bullish, first_greater otherwise; any nonnull hit including position zero rejects, no Reset emitted. Otherwise materialize full Break lower interval (not remainder only); empty=>null, nonempty not proof of complete coverage. Max key (High, negative native timestamp.timestamp() epoch float), min key (Low, datetime), first equal full key retained; bullish top then bottom, otherwise bottom then top. Native epoch precision/timezone governs top tie behavior, not another exact datetime comparison; no price conversion. Return new mode B candidate with First and both source identities/display current main, levels selected lower, intrabar_start main open, Break/default fields unset. No mutation of confirmed, no ledger append here.

### RE80 — _first_initial
Retention takes precedence: select bullish trend flag for exact bullish, otherwise bearish flag. Truthy flag asserts nullable trend cursor and delegates trend search; otherwise assert nullable ordinary cursor, use bull or reflected bear.reference scan with first_only and retention, assign helper cursor reference before testing reaction list; return first shallow copy for bullish or one mirror for reflected route, else null. Assertions depend on native configuration. Without retention ignore supplied cursor; check exact bullish trend then exact bearish trend, else native directional detect first_only and shallow-copy first result if present (bear result already mirrored). No explicit cursor clearing or ledger append in wrapper.

### RE81 — _first_bullish_trend_reaction
Delegate exact bullish trend bootstrap to RE82 with default nonretaining search.

### RE82 — _first_trend_reaction
Start>end returns null before source/cursor access or cursor save. Restore fixed source reference and optional shallow pending candidate copy from cursor, resume next_index without clamp; else fixed source selected start and start position. Iterate through end inclusive. Before First, update fixed confirmation-side High B/Low otherwise strictly including current row, equality retains source. On required RED B/GREEN otherwise create mode A using fixed confirmation edge/current opposite edge, boundary original selected main start Low B/High otherwise. Consume First by continue, no same-First confirmation. Strict opposite edge update before strict confirmation; First, improved opposite source and Break use loop positions, initial box source indices stored Candle.index. Refine after Break, ignore analysis return; return candidate without new cursor save or append. Normal exhaustion with retention alone saves next=end+1, fixed source and pending candidate references; null. No owner-boundary invalidation here.

### RE83 — _first_direct_same_direction_after_reset
Return first tuple element from RE84, discard earlier-pending flag; docstring does not prohibit later Firsts when an earlier candidate remains unresolved.

### RE84 — _direct_reset_search
First positions strictly after Reset through end inclusive; read row before blocked guard, skip First<=blocked_through. Require current First tag then predecessor context tag. Build RE92, skip null, scan RE93 through detector end. First confirmed in First traversal order returns candidate and sticky earlier_pending, even if an earlier candidate remains unresolved. Unconfirmed with null invalidation sets earlier_pending true, continues; nonnull invalidation sets blocked_through inclusive without clearing prior flag. Exhaustion returns literal null,true even without a specific pending candidate. No global earliest exact confirmation selection.

### RE85 — _first_geometry_after_reset
Limit end or min(request,end), key direction/reset/limit, membership hit returns shallow replacement or null. Miss recomputes limit, scans adjacent tags after reset, uses RE92 (local alignment still enforced), scans First+1..limit, updates opposite extreme strictly then tests strict confirmation (exact bullish else bearish); improved source and Break use stored Candle.index/display. Refine, ignore analysis result, return first complete geometry in First traversal order; null on exhaustion. No owner-boundary invalidation, no local cache write, no canonical ledger append or accepted Order claim.

### RE86 — first_geometry_after_reset
Public wrapper forwards direction/reset/end unchanged to RE85, no additional admission.

### RE87 — _reaction_break_indices
Inherited cache direction and stored ledger length: if nonnull cache entry and length unchanged return exact cached list reference, no content or identity freshness check. Else convert each Break to int in existing stream order, store length/list and return same list. No sort, duplicate check, or automatic invalidation for equal-length mutations; ascending stream is a caller invariant.

### RE88 — first_order_reaction_after_gate
Bound limit; reject gate<start or gate>=limit before cache access. Key direction/gate/limit/exact event (nullable), membership hit returns shallow copy or null. Read ledger and RE87 indices; bisect_left gives prior owner cut-1, only first equal Break tested by RE90, no duplicate scan or local sort. Default search gate+1. No owner: RE91, tag no-history if result, cache RE89, no crossing search. Owner: inclusive outer min Low otherwise max High for exact bearish from owner First through max(First,gate-1); gate High otherwise Low for exact bearish. Truthy exact event or gate open through limit main end exclusive, no local clamp. Empty interval => cached null. Evaluate both strict lower queries in order outer then gate, exact bearish greater/less, otherwise less/greater. Neither=>cached null; restart iff outward exists and gate absent or outward position<=gate position (physical-position tie, not equal timestamp alone); else continue. Read decision time for either, restart maps to main via RE06 and starts int(source.index)+1; null unmappable. Continue retains gate+1 even if gate hit later. Reject start>limit, equality allowed. RE91 returns geometry, tag decision. Continue with missing anchor index OR value: numeric max prior Reset index strictly before result First; min Low B/max High otherwise over Reset..First-1, overwrite all anchor index/value/leg boundary fields (even individually populated); complete anchor untouched even if leg boundary absent. No prior Reset leaves incomplete anchor. Cache and return; no accepted Order creation or source-generation validation.

### RE89 — first_order_reaction_after_gate.cache_result
If cache size>=32768 delete oldest insertion before copying/storing (FIFO, not LRU); store shallow copy or null under captured key and return original result. Copy/store failure after eviction is not rolled back; hits do not refresh order.

### RE90 — first_order_reaction_after_gate.confirmed_no_later_than_gate
Convert Break to int. Earlier Break or exact gate time null => Break<=gate; remaining later Break false. Equal main with exact event: truthy intrabar_start or Break main open through Break end exclusive without RE61 start clamp. Exact bearish uses strict Low<bottom, otherwise High>top. First strict lower crossing in supplied order determines <=gate event, equality allowed; no crossing compares Break open<=gate (fallback, not observed crossing).

### RE91 — _earliest_confirmed_geometry
Exact bullish tags RED First/GREEN context else GREEN/RED; bound limit, reset=max(detector start,start-1). Scan main positions inclusive. On ordered scan>reset, current First tag, prior context tag, build RE92 and append nonnull candidate before active scan. Each main traverses active in insertion order, retain scan<=First unchanged; drop RE94 invalidation before writes. Strict opposite edge update then strict confirmation sets stored Candle.index/display Break, refines (ignore analysis return), collects confirmed; others survive. After full current-main candidate loop, first main with confirmations returns minimum First, first encountered for equal key; no cross-candidate exact lower confirmation sort. Null on exhaustion, no canonical ledger append.

### RE92 — _build_direct_candidate
Exact bullish context GREEN/First RED, else reversed. Read First candle before ordered rejection First<=reset, current tag, predecessor tag; no local clamping. Extend contiguous context run backward inclusive reset, then immediately preceding contiguous First-color run bounded reset. B local floor min Low local_start..First-1, reject First Low<floor (equality allowed); top max High context_start..First, bottom First Low; outer leg floor/source min Low reset..First-1. Nonbullish mirror ceiling/max, bottom min Low, top First High, outer max High. Mode A First and initial opposite edge source are positional First; confirmation edge and anchor use stored Candle.index/display. Anchor and leg boundary equal independent outer extreme.

### RE93 — _scan_direct_candidate
For each later main through stop inclusive calculate strict confirmation before calling RE94; invalidation result true returns null,scan before mutation. Separate exact bullish and exact bearish guards update the opposite edge strictly. On saved confirmation set Break to loop scan (source updates use Candle.index), refine, return candidate,null. End null,null.

### RE94 — _owner_boundary_before_confirmation
Read leg boundary; null false before price comparisons. Compute both main strict outward and confirmation predicates (exact bullish else bearish); no outward false, outward without confirmation true. Both: scan full main lower window without intrabar-start clamp; outward checked first each physical row, wins same-row tie, then strict confirmation. No resolving row including empty window => true. Equality alone does not satisfy strict predicates.

### RE95 — _result
Construct DetectionResult for output_direction with actual existing direction reaction/reset list references and start/end window; no clone, sort, or validation.

### RE96 — UnifiedReactionDetector.detect
Public keyword-only optional stop_after_first_at_or_after forwarded to RE97 with retain_cursor=False.

### RE97 — _detect
Retention selects RE80 with supplied initial cursor and retain_initial true; otherwise RE80 without these arguments. Null initial returns fresh empty lists, not internal ledger aliases. Append RE76 (ignore return), optional inclusive First gate returns RE95 before remainder analysis or checkpoint. Previous aliases canonicalized initial, next=Break+1, running peak/trough and source from Break, candidate null. Reanalyze canonical Break; exact extreme or opposite box reset level. Post-confirmation reset RE13/28: append exact event and pending Break; otherwise seed RE79. Invoke RE98 with cursor and requested stop/retention.

### RE98 — _scan_normal
Restore cursor previous/candidate/running/next/pending without copying; earliest_open null. On each positional main, pending nonnull short circuits strict previous-edge Reset predicate; independent candidate strict confirmation evaluated. If both true, RE12/27 recalculates Reset against current main even when pending existed. On Reset choose pending or current index and read candle, then if retention and earliest_open absent snapshot cursor with shallow previous/candidate copies and actual list counts. Clear pending; append unless last Reset.from_first_idx equals previous First (no earlier search, time or price comparison). Snapshot route RE84: true still_open saves earliest_open; otherwise ordinary RE83. Missing structural or Break breaks loop. Set mode A and both cross-direction flags false; append RE76 (source includes false branch clearing candidate and advancing to Break+1/pending, though native RE76 returns true). Inclusive First gate early return before cursor/remainder. Previous aliases canonicalized structural, next Break+1,running Break extreme/source; analyze after append, reset level analysis extreme or box; hit appends exact Reset and clears candidate/sets pending Break, otherwise seed RE79. Continue directly without normal increment.
Existing candidate: exact bullish updates bottom strict and confirms High>top, else updates top strict and confirms Low<bottom. Set stored Break, refine, compute reset level and post-reset BEFORE append. Append then inclusive First gate may return before emitting already-detected Reset or saving cursor; otherwise previous shallow copy after append, running=current edge/stored source, exact hit append/clear/pending else RE79. No candidate: exact B RED or exact R GREEN only, max/min before source choice, running source wins equality; opposite range from after earlier source or current stored index through current inclusive; mode B First uses stored identity. After normal path (including unresolved candidate), separate exact B/R running guards initialize null or strictly improve; advance positional index once. Loop exit retention chooses earliest_open or current cursor references/counts, without new copies; early returns bypass checkpoint publication. Return RE95 aliases. No unconditional rollback or cross-direction admission.

## Committed continuation
