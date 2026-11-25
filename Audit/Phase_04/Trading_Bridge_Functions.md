# Trading Bridge — function contracts

Pinned production source: engine/bridge/trading_pipeline.py, main 466eb875070f02cd0dbfb105033422bbe2fd8c70, blob 7b28fa7e93c8980c082cb277fb75556959b1abcf. Pipeline version 1.15.0, implementation 1.21.0. Source-only: this document describes observed implementation, including orchestration and presentation, not new trading rules. Times are Tehran-local naive datetimes internally; legacy times are integer epoch seconds, projected times are local strings. Prices use Decimal and string serialization. Optional values remain null unless the function explicitly chooses another fallback. Errors propagate unless explicitly caught. Module record fields are covered by Phase 03. IDs below are in AST inventory order, including nested functions.

## Input, progress and market data

### TB01 — progress_events_to (55–60)
Context manager: set context-local progress sink, yield control, restore previous token in finally even on exception. No result payload.

### TB02 — emit_progress (63–72)
Construct status/label/details event; optional durationMs rounded to two decimals. If sink exists call it; otherwise emit QG_PROGRESS prefix and compact JSON to stderr, flushed. Sink/encoding errors propagate. No market change.

### TB03 — timed (75–84)
Read performance counter, emit start, invoke work and return its result. Finally accumulate elapsed milliseconds by label in supplied timings and emit completion even on work error. Telemetry only.

### TB04 — load_module (87–94)
Create import specification from name/path; missing spec/loader raises RuntimeError. Create module, register in sys.modules, execute loader, return module. Dynamic external implementation conditional on supplied path.

### TB05 — load_engine (97–98)
Delegate TB04 with fixed reaction_engine module name.

### TB06 — local_datetime (104–110)
Epoch-keyed cache; miss converts epoch in Asia/Tehran then removes timezone marker, stores and returns naive datetime.

### TB07 — epoch (116–122)
Datetime-keyed cache; miss attaches Tehran timezone and truncates timestamp with int; stores and returns.

### TB08 — display_epoch (128–137)
Datetime directly delegates TB07. Otherwise cache by input string, parse year-month-day hour:minute:second, convert and cache. Parse failures propagate.

### TB09 — _aggregate_candle_buckets (140–184)
Start lower/main lists with optional existing tail dicts. Iterate rows in supplied order, convert time to int and OHLC with supplied decimal callback. Consecutive equal raw timestamp merges into lower bucket: original Open, max High, min Low, latest Close. Otherwise append new bucket. Unless lower_only, repeat aggregation at epoch-aligned floor time (timeframe 1 uses raw timestamp). Return lower and main buckets; modifies supplied tail dicts, does not sort or enforce chronology itself.

### TB10 — build_candle_buckets (187–202)
Initialize per-call normalization cache, delegate TB09 with TB11 and lower_only flag.

### TB11 — cached_decimal (192–200)
Key by (type,value); first normalized representation retained. On missing key normalize using as_decimal, store, return. Cache is local to TB10; invalid value propagates.

### TB12 — LiveMarketBuckets.__init__ (216–223)
Require timeframe of exact int type >=1. Lower buckets empty, main aliases lower at timeframe1, otherwise separate list. Last raw timestamp null and persistent price cache empty.

### TB13 — LiveMarketBuckets.append (225–227)
Enter transactional stage_append context, return its yielded delta, exit context normally.

### TB14 — LiveMarketBuckets.stage_append (230–295)
Initial dirty indices are current lengths. Empty rows yield delta without change. Otherwise int first timestamp, floor main bucket. If first timestamp equals last raw timestamp, dirty lower is last bucket and copy it as tail; similarly copy last main if same bucket, except timeframe1 shares lower. Aggregate checked rows using TB15 and TB16. Snapshot old suffixes and last time before replacing suffixes, inserting new price keys, updating last time. Yield TB17 delta. If BaseException during consumer body, restore old suffixes/time and delete newly inserted price keys, then rethrow. Pre-yield validation/aggregation uses copies and local price additions, no committed mutation. Do not silently accept decreasing RAW time.

### TB15 — checked_rows (255–264)
Generator converts time to int, requires equal original numeric value and >0, rejects decreasing time relative to previous including prior append. Updates captured previous timestamp and yields original row. Equal timestamps permitted.

### TB16 — cached_decimal (266–272)
Consult persistent price cache by type/value then local additions. On miss normalize and add locally; return preserved first value.

### TB17 — LiveMarketBuckets._delta (297–303)
Construct BucketAppend with dirty lower/main indices and exclusive settled counts max(0,length-1), last bucket provisional.

### TB18 — build_candle_objects (306–333)
Enumerate bucket dicts from supplied start index; convert time to Tehran naive datetime and formatted display string; classify color with engine callback, construct engine.Candle with OHLC unchanged. Return list.

### TB19 — LiveMarketViews.__init__ (339–343)
Initialize lower/main candle arrays and corresponding indexes to empty/null.

### TB20 — LiveMarketViews._update_series (346–352)
Rebuild mutable candle suffix from dirty if existing index else zero; replace suffix. If no index or new length exceeds capacity, construct LowerTimeframeIndex with retained crossings; otherwise refresh_suffix in existing index. Return index.

### TB21 — LiveMarketViews.update (354–363)
Timed update of lower series; timeframe1 main and index alias lower, otherwise timed separate main update. Mutates object in place.

## Legacy and projected serialization

### TB22 — _index_selected (365–370)
If either range bound null accept; otherwise inclusive start <= int(index) <= end.

### TB23 — select_reaction_serialization_items (373–393)
Keep resets by reset index and reactions by First index, original order. Pair each selected native reaction with optional transformed public item, otherwise itself. Return pairs and resets; no mutation.

### TB24 — serialize (396–437)
Use supplied selection when present or TB23. Reset fields: index,time,secondTime nullable,brokenLevel string,fromFirstIndex. Reaction fields: firstIndex/Time, boxTop/Bottom and corresponding SourceIndex/Time, breakIndex/Time,mode. Times via TB08, prices strings; preserve order; return reaction and reset arrays.

### TB25 — serialize_blue_lines (440–457)
Filter via TB22 on source index. Per row direction,kind,reactionNumber,previousStrikeCount,strikeCount,fibonacciLevel nullable string,sourceIndex/Time,sourceExtreme string,brokenLevel nullable string,linePrice string,startTime,endTime. Epoch timestamps; order preserved.

### TB26 — serialize_a_zones (460–484)
Each row: direction; blue1/2Ordinal,SourceTime,StopTime,StopLevel; continuationLevel,SourceIndex,SourceTime; triggerIndex,Time,EventTime; reactionNumber,FirstTime,BreakTime; sourceIndex,Time,price; calculationValid true. Times epoch, levels/prices strings. No extra filtering.

### TB27 — serialize_s_zones (487–549)
Each row direction,color,formationType; aOrdinal,aSourceIndex/Time,aPrice,aStopIndex/Time/EventTime; orderDirection,orderReactionNumber,orderMode,orderFirstIndex/Time,orderBreakIndex/Time,orderConfirmationTime,orderBoxTop/Bottom and their SourceIndex/Time,orderStopLevel/SourceIndex/SourceTime; resetReactionNumber,resetTime; sourceIndex/Time,price,decisionIndex/Time/EventTime,calculationValid true. Optional order/reset times and prices preserve null, otherwise epoch/string. Original order.

### TB28 — serialize_e_zones (552–592)
Each row direction,family,number,parentType,parentSourceIndex/Time,parentPrice,parentStopIndex/Time/EventTime; orderDirection,ReactionNumber,Mode,Causes list,ParentStopCauseTime optional; orderFirst/BreakIndex/Time,ConfirmationTime,BoxTop/Bottom and SourceIndex/Time,StopLevel/SourceIndex/Time; sourceIndex/Time,price,decisionIndex/Time/EventTime. Convert prices to strings and time to epoch, optional as declared. No calculationValid addition.

### TB29 — serialize_stopalls (595–659)
Each row direction,number,sourceIndex/Time,price,decisionIndex/Time/EventTime,gateType/EventTime,stoppedBehaviorType/Key/Count,underlyingEFamily/Number; nullable order fields including causes, parent stop cause, full geometry; stopIndex/Time/EventTime. Epoch and price string conversions guarded for nullable data. No donor fields in legacy row.

### TB30 — bridge_datetime (662–673)
Null -> null; string unchanged; non-datetime -> null; datetime formatted as local year-month-day hour:minute:second.

### TB31 — bridge_direction (676–677)
Return title-case string representation of direction.

### TB32 — bridge_mode (680–681)
A -> Leg Start; B -> Normal; else null.

### TB33 — bridge_color (684–687)
Null or empty string -> null; otherwise title-case string.

### TB34 — _bridge_horizon (690–694)
Last visible main candle timestamp plus chronology timeframe.

### TB35 — _bridge_in_horizon (697–698)
Non-null event strictly before TB34.

### TB36 — _bridge_proven_strict_event (701–738)
Reject absent event/level or event outside horizon. Normalize level. Obtain lower timestamps from chronology or build fallback list. Bisect left at event and examine only equal timestamp rows. Bearish strict High>level; otherwise strict Low<level. Return exact event on first proof, else null. Never select a different time or infer intrabar order.

### TB37 — _bridge_stop_view (741–758)
Absent/out-of-horizon stop time yields both time/eventTime null. Otherwise format main time and TB36-proven event separately.

### TB38 — _bridge_reaction_confirmation (761–782)
Invoke chronology.reaction_confirmation with use_intrabar_start option. Catch AttributeError/IndexError/TypeError/ValueError and return null; use boxTop for bullish, boxBottom for bearish; prove exact crossing via TB36 with opposite direction.

### TB39 — _bridge_order_identity (785–790)
Return physical First/Break int identity if both non-null; else null.

### TB40 — BridgeProjection.__init__ (801–818)
Store direction, market and Order direction. Build audit map by physical reaction identity; later duplicate wins.

### TB41 — BridgeProjection.physical_order (820–863)
Null record or invalid First/Break bounds -> null. Obtain physical entry/reaction and optional crossed main/exact times. Return firstCandle.time, breakoutCandle.time/eventTime (verified confirmation), stop.price/time/eventTime (TB37); no new Order.

### TB42 — BridgeProjection.parent_order (865–870)
Find matching audit by behavior's physical Order identity TB39; pass to TB41, otherwise null.

### TB43 — BridgeProjection.current_order (872–925)
Require strict stop event and source time. Find audit causes: parent-stop requires exact label/source/event and matching family (requested null accepts null or empty); reset-leg requires exact post type or E/StopAll base type matching numbered prefix plus exact source/stop. Collect by distinct physical identity. Exactly one -> TB41, else null. Does not use mere time proximity.

### TB44 — BridgeProjection.order_audit (927–984)
Require TB41 non-null else RuntimeError. Return type Order Audit, formatted direction/mode, First index/time, structure top/bottom time/price, breakout index/time/event, stop level/sourceTime/stoppedAt, causes. Parent-stop family formatted, times local; reset-leg datetime values local, other values unchanged; skip unknown cause kind.

### TB45 — _bridge_parent_stop (987–1005)
No detector or caught AttributeError/TypeError/ValueError -> null pair. Call detector.parent_stop(type,item); null result or out-of-range index -> null pair; return main time and exact event.

### TB46 — _bridge_a_stop (1008–1026)
No S detector or caught AttributeError/IndexError/TypeError/ValueError -> null pair. Obtain first_a_stop with normalized price and A confirmation helper; null result -> null pair; otherwise main/exact times.

### TB47 — _bridge_behavior_stop (1029–1041)
Combine TB37 stop fields and string price.

### TB48 — _bridge_blue_formation (1044–1064)
Non-scale: source_time,null. Scale requires ordinal 1..reaction count and valid Break index, else null pair. Return Break main time and TB38 proof with intrabar start disabled.

### TB49 — _bridge_project_reaction (1067–1107)
Type Reaction; format direction/mode; First color/time from raw candle; public geometry top/bottom source time and price; Break main time and proven confirmation from raw reaction.

### TB50 — _bridge_project_reset (1110–1130)
Type Reset, direction, occurredAt main display/second time, previousReaction firstCandle time if previous First index valid else null, brokenLevel string.

### TB51 — _bridge_project_blue (1133–1166)
Type Blue Line; formation Scale/Reset/null, formedAt TB48, line price/sourceExtreme. Stop price equals source extreme but stop time/event always null. Only reset includes brokenLevel.

### TB52 — _bridge_full_lines_by_ordinal (1169–1178)
Stable sort by int reaction number,source time,string kind, map 1-based ordinal to object.

### TB53 — _bridge_project_a (1181–1268)
Resolve each recorded Blue ordinal in full map and formation time, A stop via TB46 and TB36. Reaction lookup 1-based if valid. Return A type/direction, formation ordinary->Type-1/double-stop->Type-2/else null, formedAt source/price; two Blue entries formedAt time/stoppedAt proof/stopLevel; reaction startedAt and confirmedAt main plus proof without intrabar start; parent null; currentOrder exact A cause; own stop. Missing associations preserve null.

### TB54 — _bridge_project_s (1271–1324)
Read S parent_stop from E detector and prove it. Type S, formatted color; blue formation simple/advanced/type3/type4 -> Type-1/2/3/4, else null (red null). formedAt source/price; parent A behavior recorded formation and stop, parent Order from audit; currentOrder exact S/color cause; own stop.

### TB55 — _bridge_source_index (1327–1332)
Both source index/time required; return int index,time or null.

### TB56 — _bridge_parent_behavior_for_e (1335–1376)
Match parent by recorded type and exact source identity in corresponding S/E/StopAll map. Color from S color or E family; number E/StopAll; missing object leaves metadata null but retains recorded source/price/stop. Return parent behavior projection.

### TB57 — _bridge_project_e (1379–1423)
E type/direction/family color/int number/formedAt, parent behavior TB56 and parentOrder, currentOrder exact numbered E label/family/proven stop, own stop.

### TB58 — _bridge_project_stopall (1426–1492)
Type StopAll/direction/number. Gate sequence-group-stop->Type-1, stopall-stop->Type-2, opposite-s-group-stop->Type-3, else null. FormedAt source/price. Parent donor type,color,number,source/nullable price and independent recorded donor stop; parentOrder. CurrentOrder exact numbered StopAll label with null family and own proven stop. Do not substitute stopped group's gate for donor stop.

### TB59 — _bridge_audit_order_key (1495–1502)
Return pair of epoch times of physical First and Break main candles.

### TB60 — build_bridge_output (1505–1607)
Use exact selected legacy arrays and state detectors. Opposite direction fallback if no E detector; build BridgeProjection from final audit. Ordinal map from full Blue; parent lookup from pre-range S/E/StopAll with selected E/StopAll overriding duplicate identities. Map TB49–58 and TB44 over respective arrays; preserve order and lengths. Returns eight arrays, no independent filtering.

### TB61 — validate_order_audit_bridge (1610–1675)
Build audit physical identity set. Public S/E/StopAll with both Order indexes must reference accepted identity; collect missing and raise RuntimeError. For parent-stop causes require unique physical owner per exact tuple of label/family/event/source; repeated same owner allowed, multiple owners raise RuntimeError. No ranking.

### TB62 — serialize_order_audit (1678–1728)
Legacy direction; public reactionNumber truthy override otherwise native; mode, First/time, box top/bottom/source indexes/times, Break/time, stop level/source and nullable crossed index/main/event, causes. Convert parent cause timestamps to epochs, reset-leg datetime values to epochs; preserve other values. Sort firstTime,breakTime.

## Market preparation and orchestration

### TB63 — market_segment (1755–1775)
Require nonempty valid [start,stop). Slice main and lower by main boundary times (end exclusive, last+timeframe if full tail). Replace candles with local enumerated indexes; construct fresh chronology same type and lower index. Offset increased by start; visible range clamped/adjusted; initial trend flags inherited only if start=0 unless explicitly supplied.

### TB64 — absolute_payload_indexes (1778–1789)
Recursively copy lists/dicts. Exact nonnegative int values under key index or suffix Index increased by offset. PhysicalOrderIdentity/resetReactionIdentity list/tuple become list with exact nonnegative ints offset; otherwise recurse. Other scalar unchanged. Does not change time or price.

### TB65 — serialize_trend_transition (1792–1812)
Publish target direction (default bullish) and opposite previous direction, source main/absolute index, event, level string, PH3/PL3 source identity; id direction:trend:source epoch. Icon candle index source+49 if exists, corresponding time and High for bullish target/Low otherwise, else null.

### TB66 — parse_arguments (1815–1889)
Require reaction,Blue,A,S engine paths (aliases accepted), data path,timeframe,from/to,direction bullish/bearish/both. E and lifecycle paths optional. Blue/A/S/PLPH flags enabled/disabled default enabled; bridge-output switch; raw-timeframe default1. Require timeframe and raw-timeframe >=1. argparse failures propagate. Return namespace.

### TB67 — load_engines (1892–1927)
Time and dynamically load configured Reaction,Blue,A,S and optional E paths with expected module names. Lifecycle default pipeline/lifecycle_engine.py always loaded; primary module PL_PH_detector.py loaded if flag enabled (missing attr defaults disabled). Return EngineBundle.

### TB68 — prepare_market_context (1930–1945)
Timed read input bytes; remove UTF-8 BOM prefix; parse JSON using Decimal parse_float; delegate rows to TB69.

### TB69 — _prepare_market_context_from_rows (1948–1970)
Use full file rows for calculation; empty raises ValueError. Timed bucket normalization, lower_only at tf1. Delegate TB70, never slice raw to visible range.

### TB70 — _prepare_market_context_from_buckets (1973–2029)
Batch: build lower candles, shared lower index, main candles or tf1 alias, chronology. Live: require delta, update views, register prepared lower/main indexes, chronology. Determine requested visible bucket epochs (floor for tf>1); bisect start and end+tf minus one. Empty range raises, end clamped to last. Return full context with visible bounds.

### TB71 — create_e_detector (2069–2124)
Construct E detector with full market bounds, trend/opposite reactions and resets, S zones, initial audit, blocked First times, exceptions, invalid S identities, Order_B legs, lifecycle.sequence_priority, direct geometry TB72. Only pass live continuation/scope when supplied.

### TB72 — direct_geometry (2091–2104)
Invoke provided live order_geometry callback with direction's detector and requested geometry bounds/gate if present; otherwise call detector.first_order_reaction_after_gate.

### TB73 — calculate_full_direction_state (2127–2482)
Compute full direction state. If no shared stages, timed Blue then A, create full-range S detector with opposite resets and initial Order geometry; run S (live callbacks where provided), retain initial S copy. Else reuse shared Blue/A/S detector and initial S, not the previous E. Snapshot S candidates. Filter S audit by eligible A source; create initial E with feedback scope and detect. Apply lifecycle S eligibility; if size changed identify blocked S source times (set membership or TypeError fallback list); recreate E with valid S and blocked sources and detect.
Execute A visibility helpers, then split ALL S-eligible A by dominant S/E stops with original S candidates and no StopAll; callbacks E parent stop and S A-stop from confirmation; collect stage-invalid A. Derive invalid A and S identities and stage-invalid S descendants; remove stage-invalid S from active S. Accepted A excludes invalid; resolve Order context with S audit, previous E blocked times, invalid A, pending S A sources, opposite reactions, A first stop from source, accepted E stops, opposite confirmation, mutable exceptions. Recreate final E using accepted orders, blocked/exceptions/invalid S/legs; detect.
Reconcile shared Order stops using accepted initial audit and E ledger; if S rows change, replace candidates by (a source, source) identity, recreate shared-order E and detect once. Filter calculation S candidates by stage-invalid; find consumed S evidence after larger E stop; for each evidence/owner find current E owner by physical source/time; if present build continuation_chain_from_s with independent accepted A identities and replace_with_earlier_continuation. Rebuild accepted E audit with supplemental S evidence. Remove all invalid S from active list. Return FullDirectionState incl full Blue/A, E detector/results, S detector, invalid sets, candidates and initial S. Callback errors propagate; this orchestrates existing engine rules rather than inventing them.

### TB74 — calculate_direction_with_order_b_feedback (2485–2549)
Start empty B legs/seen signatures/shared stages; at most eight passes. Run TB73 with current legs and pass scope; save initial shared stages. For optional StopAll reconcile lifecycle, else copy E and empty StopAll. Restore independent S roots and ensure accepted audit. Discover accepted reset legs from full reactions/resets, eligible/invalid A, S/E/StopAll, detectors and priority, optional live finder. Compare old/new order_b_leg_identity; equal returns original state of pass (temporary local E list is not assigned to state.e_zones). Repeated new identity raises nonconvergence; otherwise remember and repeat. After eight raise.

### TB75 — prepare_pipeline_state (2552–2703)
Requested directions from args; any Blue/A/S enabled requires both reaction directions. Reusable full context iff E exists and S enabled. Initialize state maps. Full: create both geometry UnifiedReactionDetector for full history with matching initial trend flag; batch detect timed or live reactions; derive internal ownership; report if callback. Initial Order geometry closures capture specific opposite direction and delegate live or detector. Calculate both full directions if primary exists else requested; TB74 each, explicit lifecycle path controls StopAll; store all outputs/maps and report. Nonfull: create initial geometry finder for both, detect required directions full independently; internal ownership if behavior enabled else empty identity sets. Return PipelineState with retained optional live stages.

### TB76 — calculate_direction_range_state (2738–2837)
Need Blue if Blue/A/S enabled; reuse full Blue clipped by source range or detect from full reactions/chronology; else empty. Need A if A/S enabled; reuse clipped full A or detect from Blue; else empty. If S enabled, full-context uses full candidates/accepted S and eligible A (not clipped); otherwise construct full-range S detector with opposite data and initial geometry, detect and store detector, S candidates accepted and A replaced by eligible. Return range state including full E copy and invalid sets from maps (empty defaults). No final display filtering here.

### TB77 — finalize_direction_visibility (2840–3076)
Filter A by accepted S and S stops. Copy E. If E detector, restore independent S roots for potential StopAll donors; supplement only missing physical sources, keep accepted E objects. StopAll enabled iff explicit lifecycle path, E engine and S flag; reconcile if detector exists. If E detector exists restore independent roots for final visibility, ensure accepted audit, set visibility stop callback based on S-like attribute. Discover final accepted Order_B legs, require identity equality with converged detector legs or RuntimeError; register legs. Else visibility stop callback uses S detector first_a_stop from decision event.
Capture pre-display S/E/StopAll references for projection joins. Run lifecycle.finalize_behavior_visibility with initial visible A, full S candidates, E/StopAll, invalid S, stop and candidate event callbacks, full candles/all A. Build primary groups from full valid A and returned S/E/StopAll BEFORE clipping. Clip A/S/E/StopAll by inclusive source range; remove invalid A/S identities. Order audit A sources remain full S-eligible noninvalid A. Flatten all behavior reactions, mark internal Blue, filter internal behavior outputs. Required Order identities from complete First/Break on displayed S/E/StopAll; prepare audit with range plus required identities, validate TB61 if E detector. Return public Blue, displayed behavior, audit, projection references and primary groups.

### TB78 — serialize_direction_payload (3079–3217)
Legacy-only: timed serialize selected reactions/reset with published_reaction_candidate transform, timed TB79. Bridge enabled: create single transform/selection via TB80; select enabled/ranged Blue, enabled A, existing S/E/StopAll, audit sorted by TB59 if detector else empty; timed TB81. No trading decisions; identical selections used for additive bridge.

### TB79 — build_legacy_payload (3106–3129)
Return reactions,resets, enabled Blue and A (disabled empty), S,E,StopAll, and serialized audit if E detector otherwise empty. Blue range passed through.

### TB80 — serialize_reactions_from_one_selection (3138–3146)
TB23 once then TB24 with selection, return reactions,resets,selection triple.

### TB81 — build_payload (3179–3213)
Legacy arrays from selected objects; append bridgeOutput from TB60 with same selections. Return payload.

### TB82 — serialize_primary_order (3220–3246)
Preserve ownerDirection distinct from physical direction. reactionNumber/Mode, types in fixed parent-stop->Order_A then reset-leg->Order_B order if causes present; auditCauses values TB83; First/Break index/time, exact confirmation, stopLevel/source/hit index/time/event, causes list, nullable boxTop/Bottom string. Main times from market candle positions.

### TB83 — value (3223–3228)
Datetime -> epoch, Decimal -> string, else unchanged. Used for primary audit cause values.

### TB84 — serialize_primary_structures (3249–3368)
Dynamically import primary resolution/label/leg functions. Default direction bearish; select finalized primary lows (bullish) or highs through visible end. Cycles fallback [primary]. TB85 and TB86 generate stable absolute identity strings while row indexes local. Selected points require source in visible inclusive range and decision <=end. Visible cycles need MBL and trigger<=end. Form matching legs from formed_matching_legs through end; rows include reference/second indexes, trigger/confirmation exact and main times, source/price, capTime at source+400 or extrapolate using last candle/timeframe, stop fields only if stop index<=end, optional cycleId. No additional source clipping for legs. Highs/lows choose finalized primary side and native opposite points. On main-side rows add deduplicated cycleIds for matching source/index and decided points. Per visible cycle with id publish trigger, reference, second, highCount, main-side highIds/lowIds dedup by physical source, lowCount (bullish selected lows, bearish counts rows matching cycleId). Post-primary3 orders from visible cycles with stop<=end, relabeled and serialized with opposite conceptual owner, optional cycleId. Status last visible cycle or waiting-for-stopall-break if qualification<horizon, else waiting-for-matching-behaviors. Return high/low/MBL/status/cycles and postPH3Orders bullish or postPL3Orders bearish.

### TB85 — cycle_identity (3260–3265)
If nonempty id and nonzero offset, split colon string; exactly four parts and second cycle -> offset last two int parts. Else unchanged.

### TB86 — point (3266–3289)
Relabel order against finalized primary. Origin identity_source or item; id direction:origin kind:number:trigger+offset:decision+offset; append origin cycle suffix only if non-null and different from first cycle. Return source/time/price, kind/number, trigger/decision local indexes with main/exact times, serialized order owner bearish for PH else bullish; optional offset cycleId.

### TB87 — calculate_primary_structures (3371–3424)
Finalize opposite direction and obtain both full primary groups. For each owner prepare full-range audit from accepted noninvalid A. Build NativePrimaryOrders with TB88 on_high and direction. Detect appropriate primary via live callback or engine with S/E/StopAll/resolver. Resolve final primary side through visible end, reconcile detector primary labels. Preserve existing visibility audit identities as required; rebuild visibility audit with visible bounds. Return primary; mutates detector and visibility audit.

### TB88 — commit_high (3394–3402)
Register low for bullish or high for bearish on E detector, then refresh that direction's full-range audit in groups using accepted A. Closure mutates groups.

### TB89 — build_direction_output (3427–3467)
TB76 then TB77. Primary owner bearish for both else requested direction. Calculate primary only if direction matches owner, primary module exists, E detector exists and explicit lifecycle path. Save state.primary_result; resolve StopAll ownership through end; validate audit. Serialize TB78; append primary structures if present.

### TB90 — merge_regime_outputs (3469–3495)
Group regime segments by direction preserving encounter order. Single segment unchanged. Multiple: copy final segment, concatenate all list-valued keys from all segments, merge bridge arrays in encounter order, remove aggregate calculationEndTime, attach original segments as calculationSegments. No reconstruction.

### TB91 — build_reversed_trend_outputs (3498–3591)
Begin opposite target direction with full current context, incoming null. While transition exists: require 0<boundary<len current else RuntimeError. Independently calculate closed prefix via TB94 or live closed-regime callback; require confirmed Primary3 matching transition source time and level else RuntimeError. If no visible history empty arrays recursively via TB95. Publish stopped prefix with TB93. Serialize incoming transition and slice fresh regime from boundary including boundary candle; initialize only target trend. Calculate TB92 with optional live active regime, release indexes in finally (fallback live release). If next transition missing or beyond current end publish active segment and break; otherwise repeat. Merge TB90. No state carried across independent regimes except explicit transition metadata and live cache interface.

### TB92 — calculate (3506–3514)
Shallow copy args, set direction, prepare state for supplied context with optional continuation, build direction output; return group/state.

### TB93 — publish (3516–3531)
Convert local indexes to absolute via TB64; add calculationStartTime/Index only for noninitial offset; attach incoming transition if present. For stopped segment set calculationEndTime to reversal main timestamp, status reversed-to-target, all cycle statuses stopped-on-trend-reversal, cap matching legs at end. Return projected group.

### TB94 — calculate_closed (3538–3554)
Capture current context/boundary/direction as defaults. Slice [0,boundary), check visible history; if none use whole prefix for internal calculation. Calculate TB92; resolve confirmed primary through prefix final index; return offset,first time,history flag,group,confirmed. Finally release indexes or live fallback.

### TB95 — empty_lists (3564–3569)
Recursively replace any list with empty list; copy dict recursively; retain other scalars.

### TB96 — build_response_payload (3594–3667)
Build version/enable/timeframe/actualFrom/To metadata, directions dict; E enabled iff engine and S; StopAll also explicit lifecycle path. Build requested direction outputs in order. If primary transition <=visible end replace direction groups with reversed regimes; activeDirection from max (calculationStartIndex default -1,direction) over segments, fallback target. Repair search through visible main end minus one second; closed_through=min(epoch(through)+1,last lower epoch+raw_timeframe(default1)). Apply True/False to every segment using repair finder and TB97; aggregate direction arrays share row references as constructed. Add rounded phase and bridge total timings. Return payload.

### TB97 — stopall_confirmation_closed (3654–3655)
True iff row decisionTime+args.timeframe <= captured closed_through.

### TB98 — _market_calculation_scope (3671–3685)
Clear three timestamp caches and optional engine clear_market_indexes before yield; clear engine indexes and timestamp caches again in finally. Each calculation independent.

### TB99 — calculate_live_from_raw (3688–3692)
Delegate TB101 with rows preparer and one-element input tuple.

### TB100 — calculate_live_from_buckets (3695–3703)
Delegate TB101 with bucket preparer, lower/main bucket arrays, optional live views/delta and report callback.

### TB101 — _run_live_calculation (3706–3714)
Start performance counter, empty timings; enter TB98, prepare market from injected function/inputs, optional report Market chronology ready, prepare pipeline state with report_stage (no live argument supplied on this path), return response payload. Context cleanup on exception.

### TB102 — main (3717–3748)
Start pipeline and validation counters; progress start, parse, store validation duration and completion. Load engines; enter market scope; prepare market/state and response. Emit total calculation completion. Compact JSON encode, emit encoding completion, print encoded payload, return 0. Module entry catches Exception, prints error JSON and exits 1; otherwise SystemExit main status. Does not catch BaseException generally.

## Phase boundary

All 102 named function declarations described. Nested lambdas, comprehensions, exact access expressions and conditional receiver targets are indexed separately in the scope traceability ledger; downstream stage implementations are specified in their owning module documents. This source-only description does not assert numerical equivalence of a future implementation.
