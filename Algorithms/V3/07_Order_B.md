# Order_B — Reset-leg creation and feedback (V3)

**Conventions:** B = bullish, R = bearish. Parent directional extreme is Low for B and High for R; strict parent stop/improvement means lower for B and higher for R. An opposite Order has its own direction and strict predicate, not the parent predicate. Use Decimal normalization and native arithmetic order; preserve source/main versus exact-event times, physical identity, original order, and nulls. Use [record interfaces](../../Contracts/Declared_Record_Schemas.md) and [chronology/index services](20_Indexes_And_Caching.md). Procedure labels name semantic operations, not required implementation symbols.


## OB-M01 — Dominant stop and independent anchor

Inputs accepted A/S/E/StopAll, exact stop callbacks, trend Reaction/Reset stream and opposite canonical stream. Evaluate accepted lifetime stops. At each distinct stop event activate lifetimes whose trigger/decision/source <= event; lifetimes include both activation and stop boundary. Dominant rank = priority,number,source time,index (earlier original ordinal on equal). Keep stop only if lifetime object owns dominance at exact event. Map to containing main and choose best rank (then event) for same main. Produce chronological stops. Independently pick latest accepted behavior anchor before reset Reaction First; same source/time deduplicated by priority,number,type. Do not use dominant stop as automatic geometric anchor.

## OB-M02 — Reset-leg procedure

For each exact Reset event sorted by (event,owner First,ordinal):
1. Resolve last same-direction Reaction of same First with confirmation strictly before Reset. Latest dominant stop and latest anchor must both be strictly before Reaction First main open; anchor index <= First.
2. Scan inclusive anchor..First main interval, starting at anchor directional extreme. Freeze LL (B=min Low) or HH (R=max High), earliest equal owner. Require strict extension beyond anchor and boundary source strictly before First.
3. Exact Reset: explicit truthy second uses chronology; else prove strict broken-level crossing within Reset main, no main fallback. Find first strict boundary crossing strictly AFTER Reset over lower history. No crossing => skip. Map containing main with clamp. If next accepted A formation strictly after reset Reaction First maps to main <= crossing main, expire.
4. Choose first opposite canonical Reaction ordered by confirmation/First/Break/ordinal satisfying First >= crossing main and confirmation > exact crossing. Same crossing main First is permitted, same event confirmation is not. No geometry-only opposite candidate.
5. Persist independent stop, anchor, reset, frozen boundary, exact break, physical opposite geometry and confirmation. Several valid causes may share one physical identity; register without replacing geometry.

## OB-M03 — Feedback and continuation

Only accepted behavior stop/anchor evidence enters discovery, excluding invalid A. Feedback runs initial Blue/A/S once then recomputes E with changed legs, reconciles optional StopAll and restores independent S roots, ensures accepted audit, rediscovers legs. Compare sorted semantic leg signatures (explicit fields in OA12), return unchanged state when equal; detect repeated non-equal signature or exceed eight passes => RuntimeError. Final visibility rediscovers and requires exact same signature. Live boundary cache only for ranges ending before dirty main; crossing cache resumes unexamined lower suffix, retains hit if before dirty and within current data. See [Trading Bridge](17_Trading_Bridge.md).

## Detailed reset-leg procedures

### OA02 — dominant_post_behavior_stops
Rank lifetimes by (priority callback, int number default0, source time,index), first equal rank wins via negative original ordinal. Sort activations by trigger event or decision event or source. Sweep distinct non-null stop events sorted; activate starts <= event; heap chooses highest rank, lazily discard expired end<event. Both boundaries inclusive. For each lifetime with stop whose owner at exact event is the identical behavior object (not tuple identity or equality), map stop to clamped main candle; invoke priority callback again and choose max (priority,number,source time,index,event time) per candle, first tie. Return PostBehaviorStop records sorted event,index. Records carry behavior type/source index/time/event.

### OA03 — order_b_reset_event_time
Truthy reset.second_time => return chronology.reset_time(reset) directly, including null. Otherwise normalize broken_level; within reset main [start,start+timeframe) search first strict low for exact bullish, high otherwise, via non-null lower index or sequential normalized prices only if index absent. Null on miss, no indexed-miss retry or main-candle timestamp fallback; local helper does not validate direction.

### OA04 — _order_b_boundary
Anchor normalized extreme at first candle. Scan inclusive first..last; strictly lower for low, strictly higher otherwise. Return anchor, extreme boundary, first index attaining boundary (ties unchanged). Anchor is read even for last<first (empty remainder); no local bounds validation.

### OA05 — _order_b_crossing
Search from supplied lower left to end; null if left>=length, no local lower clamp. Non-null lower index selects first_less for exact low, first_greater otherwise; only absent index uses sequential first strict crossing of selected attribute. Return exact lower timestamp or null; indexed miss does not retry.

### OA06 — discover_order_b_reset_legs
Validate direction, require post stops and anchors. Low for B, high R. Optional boundary/crossing callbacks or OA04/05 with crossing strictly after reset (upper bound). Sort trend confirmations (confirmation,First, Break, original ordinal, reaction), group by First; opposite analogous with 1-based ordinal. Sort valid reset events (exact reset time,from First,ordinal,reset); stops by (event,source time,index,type); anchors by (source time,index,priority,number,type); sort A formations. For each reset choose last same-direction candidate matching from First with confirmation<reset. Require latest stop event strictly before its First main time and latest anchor source strictly before that time; anchor index<=First. Compute boundary anchor..First inclusive. Boundary must extend anchor strictly and its source index<First. Find first strict crossing after reset; absent => skip. Map crossing to main. Reject if first A formation strictly after current First maps to main <= crossing main. Choose first opposite sorted candidate with First index>=crossing main AND confirmation>exact crossing. Return legs in reset traversal order, carrying stop, anchor type/index/time/extreme, reset reaction/confirmation/index/broken level/exact reset, leg boundary/index/time, exact strict break, physical opposite number/reaction/confirmation. No equality crossing or invented Reaction.

### OA07 — LiveOrderBResetLegs.__init__
Validate direction; store extreme attribute; initialize boundary/crossing caches and last lower time null.

### OA08 — LiveOrderBResetLegs.update
Validate dirty main index inclusive 0..len; map dirty or null at end; get latest lower time, dirty lower bound or len; previous coverage via upper_bound of last lower time or 0. New per-call caches; pass OA09/10 closures to OA06. Replace caches with queried entries and last lower time; return legs.

### OA09 — update.boundary
Key first,last; current cache first, prior cache only if last<first_dirty_main; else calculate OA04. Cache and return tuple.

### OA10 — update.crossing
Key reset time,level; current hit including null returned. Reuse old non-null crossing if before dirty (or dirty null), latest lower exists and crossing<=latest. Otherwise start upper_bound(reset); if prior key existed advance left to max(left,min(old coverage,dirty lower)); search OA05. Cache including null.

### OA11 — discover_accepted_order_b_reset_legs
Exclude invalid A (source time,int index). For accepted A use trend reaction ordinal-1 confirmation, S detector first_a_stop, exact stop triple[2]; for S/E use E detector parent_stop and element1; StopAll explicit stop. Obtain dominant stops OA02. Build anchor records for all accepted A/S/E/StopAll, priority and number default0; per exact source time/index choose greater (priority,number,type). Use finder callback or OA06 with dominant stops, accepted A trigger times and tuple of anchor values. Dominance does not suppress later lower-priority anchor.

### OA12 — order_b_leg_identity
Sorted tuple of legs' stop type/source index/event; anchor type/index/time/extreme; reset reaction First/Break, reset source index/broken level/time; leg boundary/source index; strict break; physical First/Break. Does not include all presentation fields.

## Canonical Order selection

### OA30 — register_order_b_reset_legs
If legs invalidate carried cache. Per physical reaction insert new ledger row with canonical stop, exact crossing, empty parent cause set and confirmation index; otherwise reuse existing. Build reset-leg cause dict with postBehaviorType/StopTime/SourceIndex/SourceTime, anchorBehaviorType/SourceIndex/SourceTime/Extreme string, resetReactionIdentity, BreakoutTime and ConfirmationTime, resetIndex/BrokenLevel string/Time, legBoundary string/SourceIndex/SourceTime, strictBreakTime, physicalOrderIdentity and ConfirmationTime. Deduplicate equality; sort B causes by post stop,reset,break,physical identity; invalidate carried on addition.

## Primary and parent registration
