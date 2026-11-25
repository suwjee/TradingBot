# Serialization — legacy and additive Bridge Output (V3)

**Conventions:** B = bullish, R = bearish. Preserve Decimal representation, evaluation order, native failures, exact versus main-candle time, original array order and nulls. Record interfaces: [Declared schemas](../../Contracts/Declared_Record_Schemas.md). Operation IDs designate semantic procedures, not required implementation symbols. This contract does not claim runtime equivalence.


## SER-M01 — Selection, conversions and stable identity

Consume final visibility objects, physical Order audit and calculation context. Select native Reaction by First index, Reset by own index, Blue by source index; inclusive range when both bounds supplied. Transform selected Reaction into published clipped box; never alter native geometry. A/S/E/StopAll already selected by lifecycle/range. Legacy-only path and bridge-enabled path must use identical selection and order; bridge-enabled computes selection once, then maps two views. Blue/A display flags suppress only their respective arrays. Order audit sorted by (First main epoch,Break main epoch). Legacy time = Tehran-local naive datetime with Tehran zone attached, integer epoch seconds; legacy display strings parsed with year-month-day hour:minute:second. Decimal serialized as native string, not float; nullable fields stay null where explicitly guarded. No new quantization, no schema inference from price value. Preserve array order and record key spelling.

## SER-M02 — Legacy field groups

The following names are exact (common notation expands repeated prefixed fields with capitalization as shown in the individual procedure contracts).

| Array | Core field sequence and distinctions |
|---|---|
| reactions | firstIndex, firstTime, boxTopSourceIndex, boxTopSourceTime, boxTop, boxBottomSourceIndex, boxBottomSourceTime, boxBottom, breakIndex, breakTime, mode |
| resets | index, time, secondTime, brokenLevel, fromFirstIndex |
| blueLines | direction, kind, reactionNumber, previousStrikeCount, strikeCount, fibonacciLevel, sourceIndex, sourceTime, sourceExtreme, brokenLevel, linePrice, startTime, endTime |
| aZones | direction, blue1Ordinal, blue2Ordinal, blue1SourceTime, blue2SourceTime, blue1StopTime, blue2StopTime, blue1StopLevel, blue2StopLevel, continuationLevel, continuationSourceIndex, continuationSourceTime, triggerIndex, triggerTime, triggerEventTime, reactionNumber, reactionFirstTime, reactionBreakTime, sourceIndex, sourceTime, price, calculationValid (true) |
| sZones | direction, color, formationType, aOrdinal, aSourceIndex, aSourceTime, aPrice, aStopIndex, aStopTime, aStopEventTime, common Order fields without orderCauses/orderParentStopCauseTime, resetReactionNumber, resetTime, sourceIndex, sourceTime, price, decisionIndex, decisionTime, decisionEventTime, calculationValid (true) |
| eZones | direction, family, number, parentType, parentSourceIndex, parentSourceTime, parentPrice, parentStopIndex, parentStopTime, parentStopEventTime, common Order fields including causes, sourceIndex, sourceTime, price, decisionIndex, decisionTime, decisionEventTime |
| stopAlls | direction, number, sourceIndex, sourceTime, price, decisionIndex, decisionTime, decisionEventTime, gateType, gateEventTime, stoppedBehaviorType, stoppedBehaviorKey, stoppedBehaviorCount, underlyingEFamily, underlyingENumber, common Order fields including causes, stopIndex, stopTime, stopEventTime |

Common Order fields in order: orderDirection, orderReactionNumber, orderMode, optionally orderCauses, orderParentStopCauseTime, then orderFirstIndex, orderFirstTime, orderBreakIndex, orderBreakTime, orderConfirmationTime, orderBoxTop, orderBoxTopSourceIndex, orderBoxTopSourceTime, orderBoxBottom, orderBoxBottomSourceIndex, orderBoxBottomSourceTime, orderStopLevel, orderStopSourceIndex, orderStopSourceTime. S/StopAll nullable provenance is explicitly guarded; E required geometry is not. StopAll donor metadata is not added to the legacy row. Legacy OrderAudit retains exact physical geometry, public ordinal if truthy else native, strict stop fields or null, accepted parent-stop and reset-leg causes. See detailed operations for conversions. Do not promote any geometry from display.

## SER-M03 — Additive nested projection

All eight legacy arrays have corresponding Bridge Output arrays. Use fresh mappings, title-case direction/color, Mode A -> Leg Start, B -> Normal, other -> null. Local datetime display string or already-string unchanged; other types -> null. View horizon = last visible main open + timeframe. A recorded stop main time outside horizon becomes both time and eventTime null. Otherwise eventTime appears only when that exact recorded lower timestamp proves the strict predicate; scan rows with equal timestamp only, never substitute a later crossing. Reaction confirmation proof uses opposite stop predicate. Reset occurrence uses recorded display/second string. Parent geometry joins by exact physical (index,time) or Blue ordinal from full sorted Blue including invalid; do not infer from output row position.

| Type | Nested contract |
|---|---|
| Reaction | type, direction, mode, firstCandle(color,time), structure(boxTop(time,price), boxBottom(time,price), breakoutCandle(time,eventTime)) |
| Reset | type,direction,occurredAt(time,eventTime),previousReaction(firstCandle(time)),brokenLevel |
| Blue Line | type,direction,formation(Scale/Reset/null),formedAt(time,eventTime),line(price,sourceExtreme),stop(time=null,eventTime=null,price=sourceExtreme); brokenLevel only for reset |
| A | type,direction,formation(Type-1 ordinary/Type-2 double-stop/null),formedAt(time,price),blueLines(first,second each formedAt(time),stoppedAt(time,eventTime),stopLevel),reaction(startedAt(time),confirmedAt(time,eventTime)),parent=null,currentOrder,stop |
| S | type,direction,color,formation(Blue simple/advanced/type3/type4 -> Type-1/2/3/4; Red null),formedAt(time,price),parent(behavior(type=A,formedAt,stoppedAt),order),currentOrder,stop |
| E | type,direction,color,number,formedAt,parent(behavior(type,color,number,formedAt,stoppedAt),order),currentOrder,stop |
| StopAll | type,direction,number,formation(sequence-group-stop/stopall-stop/opposite-s-group-stop -> Type-1/2/3),formedAt,parent(behavior from retained donor type/color/number/price/time/actual donor stop,order),currentOrder,stop |
| Order Audit | type,direction,mode,firstCandle(index,time),structure(boxTop,boxBottom,breakoutCandle(index,time,eventTime)),stop(level,sourceTime,stoppedAt(time,eventTime)),causes |

For behavior stop mapping use time,eventTime,price. Physical parentOrder is accepted audit identity's firstCandle(time), breakoutCandle(time,eventTime), stop(price,time,eventTime); no identity match => null. currentOrder is not formation Order: require exactly one distinct physical audit identity with exact source/stop and matching parent-stop label/family or compatible reset-leg post-behavior type. Null family accepts null or empty only; E/StopAll numbered labels can match corresponding base reset-leg types. Zero or multiple identities => null. Historical accepted E/S/StopAll references may support nested projection but are not added as public independent rows.

## SER-M04 — Primary and regimes

Physical primary IDs use identity source if retained, direction/kind/number/absolute trigger/decision; later cycle origins add cycle suffix. Row indexes local until absolute projection; include cycleId when present and dedup cycleIds on physical primary. Primary point selection requires source in visible range and decision<=end; MBL requires formed activation and primary confirmation through horizon, not source clipping; optional stop fields clipped at end. Serialize primary Orders with conceptual ownerDirection separate from physical direction, causes/types and copied audit provenance. Directional post-secondary3 key postPL3Orders (R) or postPH3Orders (B). Reversal source/PH3/PL3 and icon index are absolute, index transformation recurses only through list/dict, applies exact nonnegative int to index or suffix Index, and physicalOrderIdentity/resetReactionIdentity components. Do not shift timestamps, numbers or prices. See [Primary](12_Primary_Structures.md), [Trend reversal](15_Trend_Reversal.md).

## Detailed serialization procedures

### TB22 — _index_selected
If either range bound null accept; otherwise inclusive start <= int(index) <= end.

### TB23 — select_reaction_serialization_items
Keep resets by reset index and reactions by First index, original order. Pair each selected native reaction with optional transformed public item, otherwise itself. Return pairs and resets; no mutation.

### TB24 — serialize
Use supplied selection when present or TB23. Reset fields: index,time,secondTime nullable,brokenLevel string,fromFirstIndex. Reaction fields: firstIndex/Time, boxTop/Bottom and corresponding SourceIndex/Time, breakIndex/Time,mode. Times via TB08, prices strings; preserve order; return reaction and reset arrays.

### TB25 — serialize_blue_lines
Filter via TB22 on source index. Per row direction,kind,reactionNumber,previousStrikeCount,strikeCount,fibonacciLevel nullable string,sourceIndex/Time,sourceExtreme string,brokenLevel nullable string,linePrice string,startTime,endTime. Epoch timestamps; order preserved.

### TB26 — serialize_a_zones
Each row: direction; blue1/2Ordinal,SourceTime,StopTime,StopLevel; continuationLevel,SourceIndex,SourceTime; triggerIndex,Time,EventTime; reactionNumber,FirstTime,BreakTime; sourceIndex,Time,price; calculationValid true. Times epoch, levels/prices strings. No extra filtering.

### TB27 — serialize_s_zones
Each row direction,color,formationType; aOrdinal,aSourceIndex/Time,aPrice,aStopIndex/Time/EventTime; orderDirection,orderReactionNumber,orderMode,orderFirstIndex/Time,orderBreakIndex/Time,orderConfirmationTime,orderBoxTop/Bottom and their SourceIndex/Time,orderStopLevel/SourceIndex/SourceTime; resetReactionNumber,resetTime; sourceIndex/Time,price,decisionIndex/Time/EventTime,calculationValid true. Optional order/reset times and prices preserve null, otherwise epoch/string. Original order.

### TB28 — serialize_e_zones
Each row direction,family,number,parentType,parentSourceIndex/Time,parentPrice,parentStopIndex/Time/EventTime; orderDirection,ReactionNumber,Mode,Causes list,ParentStopCauseTime optional; orderFirst/BreakIndex/Time,ConfirmationTime,BoxTop/Bottom and SourceIndex/Time,StopLevel/SourceIndex/Time; sourceIndex/Time,price,decisionIndex/Time/EventTime. Convert prices to strings and time to epoch, optional as declared. No calculationValid addition.

### TB29 — serialize_stopalls
Each row direction,number,sourceIndex/Time,price,decisionIndex/Time/EventTime,gateType/EventTime,stoppedBehaviorType/Key/Count,underlyingEFamily/Number; nullable order fields including causes, parent stop cause, full geometry; stopIndex/Time/EventTime. Epoch and price string conversions guarded for nullable data. No donor fields in legacy row.

### TB30 — bridge_datetime
Null -> null; string unchanged; non-datetime -> null; datetime formatted as local year-month-day hour:minute:second.

### TB31 — bridge_direction
Return title-case string representation of direction.

### TB32 — bridge_mode
A -> Leg Start; B -> Normal; else null.

### TB33 — bridge_color
Null or empty string -> null; otherwise title-case string.

### TB34 — _bridge_horizon
Last visible main candle timestamp plus chronology timeframe.

### TB35 — _bridge_in_horizon
Non-null event strictly before TB34.

### TB36 — _bridge_proven_strict_event
Reject absent event/level or event outside horizon. Normalize level. Obtain lower timestamps from chronology or build fallback list. Bisect left at event and examine only equal timestamp rows. Bearish strict High>level; otherwise strict Low<level. Return exact event on first proof, else null. Never select a different time or infer intrabar order.

### TB37 — _bridge_stop_view
Absent/out-of-horizon stop time yields both time/eventTime null. Otherwise format main time and TB36-proven event separately.

### TB38 — _bridge_reaction_confirmation
Invoke chronology.reaction_confirmation with use_intrabar_start option. Catch AttributeError/IndexError/TypeError/ValueError and return null; use boxTop for bullish, boxBottom for bearish; prove exact crossing via TB36 with opposite direction.

### TB39 — _bridge_order_identity
Return physical First/Break int identity if both non-null; else null.

### TB40 — BridgeProjection.__init__
Store direction, market and Order direction. Build audit map by physical reaction identity; later duplicate wins.

### TB41 — BridgeProjection.physical_order
Null record or invalid First/Break bounds -> null. Obtain physical entry/reaction and optional crossed main/exact times. Return firstCandle.time, breakoutCandle.time/eventTime (verified confirmation), stop.price/time/eventTime (TB37); no new Order.

### TB42 — BridgeProjection.parent_order
Find matching audit by behavior's physical Order identity TB39; pass to TB41, otherwise null.

### TB43 — BridgeProjection.current_order
Require strict stop event and source time. Find audit causes: parent-stop requires exact label/source/event and matching family (requested null accepts null or empty); reset-leg requires exact post type or E/StopAll base type matching numbered prefix plus exact source/stop. Collect by distinct physical identity. Exactly one -> TB41, else null. Does not use mere time proximity.

### TB44 — BridgeProjection.order_audit
Require TB41 non-null else RuntimeError. Return type Order Audit, formatted direction/mode, First index/time, structure top/bottom time/price, breakout index/time/event, stop level/sourceTime/stoppedAt, causes. Parent-stop family formatted, times local; reset-leg datetime values local, other values unchanged; skip unknown cause kind.

### TB45 — _bridge_parent_stop
No detector or caught AttributeError/TypeError/ValueError -> null pair. Call detector.parent_stop(type,item); null result or out-of-range index -> null pair; return main time and exact event.

### TB46 — _bridge_a_stop
No S detector or caught AttributeError/IndexError/TypeError/ValueError -> null pair. Obtain first_a_stop with normalized price and A confirmation helper; null result -> null pair; otherwise main/exact times.

### TB47 — _bridge_behavior_stop
Combine TB37 stop fields and string price.

### TB48 — _bridge_blue_formation
Non-scale: source_time,null. Scale requires ordinal 1..reaction count and valid Break index, else null pair. Return Break main time and TB38 proof with intrabar start disabled.

### TB49 — _bridge_project_reaction
Type Reaction; format direction/mode; First color/time from raw candle; public geometry top/bottom source time and price; Break main time and proven confirmation from raw reaction.

### TB50 — _bridge_project_reset
Type Reset, direction, occurredAt main display/second time, previousReaction firstCandle time if previous First index valid else null, brokenLevel string.

### TB51 — _bridge_project_blue
Type Blue Line; formation Scale/Reset/null, formedAt TB48, line price/sourceExtreme. Stop price equals source extreme but stop time/event always null. Only reset includes brokenLevel.

### TB52 — _bridge_full_lines_by_ordinal
Stable sort by int reaction number,source time,string kind, map 1-based ordinal to object.

### TB53 — _bridge_project_a
Resolve each recorded Blue ordinal in full map and formation time, A stop via TB46 and TB36. Reaction lookup 1-based if valid. Return A type/direction, formation ordinary->Type-1/double-stop->Type-2/else null, formedAt source/price; two Blue entries formedAt time/stoppedAt proof/stopLevel; reaction startedAt and confirmedAt main plus proof without intrabar start; parent null; currentOrder exact A cause; own stop. Missing associations preserve null.

### TB54 — _bridge_project_s
Read S parent_stop from E detector and prove it. Type S, formatted color; blue formation simple/advanced/type3/type4 -> Type-1/2/3/4, else null (red null). formedAt source/price; parent A behavior recorded formation and stop, parent Order from audit; currentOrder exact S/color cause; own stop.

### TB55 — _bridge_source_index
Both source index/time required; return int index,time or null.

### TB56 — _bridge_parent_behavior_for_e
Match parent by recorded type and exact source identity in corresponding S/E/StopAll map. Color from S color or E family; number E/StopAll; missing object leaves metadata null but retains recorded source/price/stop. Return parent behavior projection.

### TB57 — _bridge_project_e
E type/direction/family color/int number/formedAt, parent behavior TB56 and parentOrder, currentOrder exact numbered E label/family/proven stop, own stop.

### TB58 — _bridge_project_stopall
Type StopAll/direction/number. Gate sequence-group-stop->Type-1, stopall-stop->Type-2, opposite-s-group-stop->Type-3, else null. FormedAt source/price. Parent donor type,color,number,source/nullable price and independent recorded donor stop; parentOrder. CurrentOrder exact numbered StopAll label with null family and own proven stop. Do not substitute stopped group's gate for donor stop.

### TB59 — _bridge_audit_order_key
Return pair of epoch times of physical First and Break main candles.

### TB60 — build_bridge_output
Use exact selected legacy arrays and state detectors. Opposite direction fallback if no E detector; build BridgeProjection from final audit. Ordinal map from full Blue; parent lookup from pre-range S/E/StopAll with selected E/StopAll overriding duplicate identities. Map TB49–58 and TB44 over respective arrays; preserve order and lengths. Returns eight arrays, no independent filtering.

### TB61 — validate_order_audit_bridge
Build audit physical identity set. Public S/E/StopAll with both Order indexes must reference accepted identity; collect missing and raise RuntimeError. For parent-stop causes require unique physical owner per exact tuple of label/family/event/source; repeated same owner allowed, multiple owners raise RuntimeError. No ranking.

### TB62 — serialize_order_audit
Legacy direction; public reactionNumber truthy override otherwise native; mode, First/time, box top/bottom/source indexes/times, Break/time, stop level/source and nullable crossed index/main/event, causes. Convert parent cause timestamps to epochs, reset-leg datetime values to epochs; preserve other values. Sort firstTime,breakTime.

## Market preparation and orchestration

### TB64 — absolute_payload_indexes
Recursively copy lists/dicts. Exact nonnegative int values under key index or suffix Index increased by offset. PhysicalOrderIdentity/resetReactionIdentity list/tuple become list with exact nonnegative ints offset; otherwise recurse. Other scalar unchanged. Does not change time or price.

### TB65 — serialize_trend_transition
Publish target direction (default bullish) and opposite previous direction, source main/absolute index, event, level string, PH3/PL3 source identity; id direction:trend:source epoch. Icon candle index source+49 if exists, corresponding time and High for bullish target/Low otherwise, else null.

### TB79 — build_legacy_payload
Return reactions,resets, enabled Blue and A (disabled empty), S,E,StopAll, and serialized audit if E detector otherwise empty. Blue range passed through.

### TB80 — serialize_reactions_from_one_selection
TB23 once then TB24 with selection, return reactions,resets,selection triple.

### TB81 — build_payload
Legacy arrays from selected objects; append bridgeOutput from TB60 with same selections. Return payload.

### TB82 — serialize_primary_order
Preserve ownerDirection distinct from physical direction. reactionNumber/Mode, types in fixed parent-stop->Order_A then reset-leg->Order_B order if causes present; auditCauses values TB83; First/Break index/time, exact confirmation, stopLevel/source/hit index/time/event, causes list, nullable boxTop/Bottom string. Main times from market candle positions.

### TB83 — value
Datetime -> epoch, Decimal -> string, else unchanged. Used for primary audit cause values.

### TB84 — serialize_primary_structures
Dynamically import primary resolution/label/leg functions. Default direction bearish; select finalized primary lows (bullish) or highs through visible end. Cycles fallback [primary]. TB85 and TB86 generate stable absolute identity strings while row indexes local. Selected points require source in visible inclusive range and decision <=end. Visible cycles need MBL and trigger<=end. Form matching legs from formed_matching_legs through end; rows include reference/second indexes, trigger/confirmation exact and main times, source/price, capTime at source+400 or extrapolate using last candle/timeframe, stop fields only if stop index<=end, optional cycleId. No additional source clipping for legs. Highs/lows choose finalized primary side and native opposite points. On main-side rows add deduplicated cycleIds for matching source/index and decided points. Per visible cycle with id publish trigger, reference, second, highCount, main-side highIds/lowIds dedup by physical source, lowCount (bullish selected lows, bearish counts rows matching cycleId). Post-primary3 orders from visible cycles with stop<=end, relabeled and serialized with opposite conceptual owner, optional cycleId. Status last visible cycle or waiting-for-stopall-break if qualification<horizon, else waiting-for-matching-behaviors. Return high/low/MBL/status/cycles and postPH3Orders bullish or postPL3Orders bearish.

### TB85 — cycle_identity
If nonempty id and nonzero offset, split colon string; exactly four parts and second cycle -> offset last two int parts. Else unchanged.

### TB86 — point
Relabel order against finalized primary. Origin identity_source or item; id direction:origin kind:number:trigger+offset:decision+offset; append origin cycle suffix only if non-null and different from first cycle. Return source/time/price, kind/number, trigger/decision local indexes with main/exact times, serialized order owner bearish for PH else bullish; optional offset cycleId.
