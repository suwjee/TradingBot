# Primary structures — concurrent MBL cycles, native Orders and reconciliation (V3)

**Conventions:** B = bullish, R = bearish. A strict trend stop means Low < level for B, High > level for R; improvement uses the same predicate. Main source identity and exact event chronology are separate. Preserve Decimal representation, operation order and stable ordering. Required record fields/defaults are in [record interfaces](../../Contracts/Declared_Record_Schemas.md); shared searches in [Index and cache contracts](20_Indexes_And_Caching.md). Procedure labels identify semantic operations, not required implementation symbols.


## PS-M01 — Coordinate system and module contract

Primary core operates in BEARISH coordinates. Bullish path reflects price signs with Decimal sign-copy, High/Low, strict greater/less and swaps PH/PL roles. Native chronology, Order physical identities, causes, S/E family and market colors remain invariant; native Order direction reflected in/out as specified. Input accepted S/E/StopAll and chronological lower/main services, callable native Order resolver. Output logical cycles, matching legs, confirmed high/low roles, status, post-secondary3 Orders, optional reversal. Public physical numbering resolved separately from logical cycle counters. See [Primary high/low roles](13_Primary_High.md), [MBL](14_Matching_Behavior_Leg.md) and [Reversal](15_Trend_Reversal.md).

## PS-M02 — Global scheduling

Discover qualified matching seeds; reference StopAll number>=3, dominant exact-key repeated behaviors after it, maximum relevant exact decision qualification. Dedup pair source indexes. Find first strict above-reference High after qualification (below original Low when B); schedule activation by (exact activation,qualification,reference index,second index). Track earliest qualification even without activation. Initialize each activated cycle with floor main minimum from second source through gate and own strict later floor stop. Replay settled checkpoints in live mode; callbacks for retained primary points restore ledger effects.

At each iteration generate prospective next point per cycle without committing. Choose next decision by (exact event,cycle index), next activation by schedule. If earliest eligible Primary3 reversal event <= both, reversal wins and terminate. Otherwise activation wins decision tie; skip activation whose reference physical source already promoted; otherwise create cycle and repeat. If no decision or activation, stop. Commit earliest point to cycle and global result, checkpoint; on primary PH in bearish coordinates invoke native on_high callback, invalidate all pending proposals if callback present, recompute earliest reversal. Secondary PL does not invalidate proposals alone. No arbitrary pass cap. Preserve pending-proposal cycle status at end. Aggregate first MBL, last cycle status or reversed status, deduplicated post-secondary3 Orders by physical direction/First/Break, sorted exact stop,-First,Break.

## PS-M03 — Per-cycle prospect (bearish reference)

State phase PH/PL/seek, gate main/exact cursor, reference High, floor MBL, previous PH/PL, reset_high flag. PH number=1 if reset or no highs, else previous+1; PL increments from 1. Seek next strict higher than high-level or lower than low-level strictly after cursor; neither -> waiting; same exact event -> ambiguous, no point. PH gate allows confirmation >= cursor independent First; PL requires First >= gate main and confirmation > cursor. Continuing PH >1 requires parent-stop cause or reset-leg plus non-null boxTop strictly > previous PH. All Orders require actual stop strictly after own confirmation; native resolver also requires stop > gate. Winner earliest stop, later First, earlier Break. Cancellation = first lower than MBL floor for PH, first higher than high-level for PL. If earlier cancellation (or post-PL3 phase), inspect same RAW row for opposing strict cross; both => ambiguous. Same stop and cancel event => ambiguous for ordinary stage. If cancellation wins, advance cursor; PL switches PH; PH with existing lows switches PL only if row Low strictly below prior low, else seek; no lows switches PL. Post-PL3 stores candidates before cancellation (no PL4); if cancel absent wait post-pl3-orders-only, else restart PH. Winner with no earlier cancellation -> freeze main extreme on gate..Order stop inclusive (highest for PH, lowest PL, earliest tie); record exact trigger and decision. Move cursor to Order stop, seek, reset PH count if PL committed.

## PS-M04 — Native Order services and physical projection

Resolve owner ledger by requested kind PH/PL, gate and actual physical direction; secondary only canonical positive reaction number and reset-leg or earliest direct parent-stop identity; require exact crossing > confirmation and gate. Preserve full copied cause provenance. Primary commitment can reparent obsolete StopAll causes and rebuild native ledger; [Order Audit](08_Order_Audit.md) owns actual edits. Final primary points group by physical (source index,time), filter decision<=horizon, order groups by earliest decision/source; winner highest logical number then role order; identity from earliest role, geometry/order from winner. Strict progressive price may increase final number beyond local winner. No mutation of logical cycles. Resolve StopAll ownership by confirmed physical primary source at horizon, and MBL public only once primary confirmation exists in its cycle. Projection/serialization is separate.

## PS-M05 — Live cache and failure modes

Retain run steps strictly before dirty exact event, rewound to first changed activation; dirty main containing exact event may rewind to its open. Cache strict searches and projected object identities with native original identity check. Replay retained primary callbacks, refresh MBL stops. On failure wrapper does not commit new state but external callbacks may already have changed ledger. Status distinguishes awaiting matching, awaiting break, ambiguous RAW, waiting Order, post-secondary3 only, reversal. No synthetic confirmation or tie order. Full per-operation contracts follow.

## Detailed primary procedures

### P01 — TrendTransition.point

Property returns high field, unchanged, including original reference. Direction-neutral alias, not a second point. StructureOrder, PrimaryPoint, MatchingBehaviorLeg and TrendTransition are frozen/slotted, not recursive deep freezes; PrimaryResult is slotted but mutable. List default factories create independent lists per field and instance. PrimaryPoint cycle_id and identity_source are keyword-only optional fields defaulting to None. MatchingBehaviorLeg stop_index and stop_event_time are required nullable fields, not omitted defaults. Type union declarations are not runtime numerical operations.

### P02 — first_bullish_transition

Resolve physical PHs with P04 through last main position len(candles)−1. For each point number exactly 3, invoke supplied truthy cross or P12 with chronology, point decision event, price, above=true. For non-null crossing (index,time) create TrendTransition with point price and original point, default target bullish. Return minimum by (event_time, high.source_index, high.cycle_id or empty string), first tie, default null. The callback selection is truthiness-based for PH3 only; an explicit non-null hit is expanded directly without independent local timestamp or index validation. The full-history resolver uses len(main candles)-1 even if empty. Cycle ID fallback uses truthiness and key source index is raw.

### P03 — first_bearish_transition

Resolve physical PLs with P05 through last main position. For every number 3 call P12 below price strictly after decision, no custom callback. Create transition target bearish for non-null hit. Same sort/min tie key as P02, null absent. The lower transition always uses the native search, and expands the non-null hit without an additional local gate; full horizon is len(main candles)-1.

### P04 — resolve_primary_highs

Delegate P06 with primary.highs, cycles attribute default empty tuple, through_index, above=true. No in-place edits. The default applies only to an absent cycles attribute; explicit None is passed through and would fail enumeration in P06.

### P05 — resolve_primary_lows

Same delegation on lows, above=false. Same absent-only default and no local repair.

### P06 — _resolve_primary_points

Inputs points, cycles, inclusive decision-index horizon, keyword above. Map cycle_id to enumeration position (later duplicates overwrite). Traverse original points, retain decision_index<=horizon, group by (source_index,source_time) preserving encounter order. Sort group lists by (minimum decision_event_time across group, first row source time,index). Per group, identity=min by P07; winner=min by (negative number, expanded P07 tuple). Start number=winner.number. If prior reconciled result exists and winner.price strictly exceeds prior price when above or strictly below otherwise, number=max(winner number, prior final number+1); equality does not extend. Append new replaced winner with final number and identity_source=identity.identity_source if truthy else identity. Never mutate local cycle points or original identities; final point's geometry/order from winner but identity from earliest role. The horizon compares decision_index only, with no source-time filter. Physical keys are raw index/time. Stable group sorting precedes role selection. Both identity and winner minima retain first exact ties; number progression consults only the immediately preceding reconciled result and raw prices. The replacement takes the earliest role's existing identity_source when truthy, otherwise the role itself, without recursive traversal.

### P07 — _resolve_primary_points.role_order

Captured cycle order. Return tuple (decision exact event, cycle position or map length if missing, cycle_id or empty string, trigger_index,number). Called in both identity and winner selection; no mutation. The default len(cycle_order) is evaluated eagerly even when key exists. Cycle ID fallback is truthiness-based.

### P08 — relabel_primary_order

Build mapping source_time -> concatenated kind and number from supplied highs/points (later entries overwrite). Call order-audit relabel_primary_causes on original audit causes and labels; replace order.audit_causes with tuple of returned entries. Other fields unchanged. Delegate actual relabel logic to order owner, do not alter native identity. Source time alone is the label key; tuple materialization precedes replacement, and the helper does not directly mutate the native ledger.

### P09 — formed_matching_legs

Lazy generator. Iterate primary.cycles if truthy, otherwise singleton primary. Skip cycle with null mbl or trigger_index>through_index. Select cycle.lows for parent primary.direction exactly bullish (attribute default bearish), else highs. Choose earliest decision_event_time among points decision_index<=horizon; first tie retained, null absent. Yield (cycle,confirmation) only with non-null confirmation. Activation alone not enough; does not mutate hidden candidate. The direction belongs to aggregate primary, not each cycle; missing direction alone defaults to bearish. Any falsy cycles value uses singleton primary. The generator yields original references only when confirmation is not None.

### P10 — resolve_stopall_ownership

Select primary lows if direction bullish else highs (default bearish). Build set (point.source_index,point.source_time) confirmed by horizon inclusive. Return original StopAll records in input order except matching (integer item.source_index,item.source_time). No change to historical collection or physical points. Primary point key is raw; only StopAll index is int-converted before comparison. No number, price or family condition; retained objects and input order preserved.

### P11 — order_meets_structure_gate

If kind exactly PH, confirmation>=event (First position irrelevant). Other kind: first_index>=gate_index AND confirmation>event. Exact PH same-event allowance versus secondary PL strict confirmation is source behavior, not symmetrical comparisons within reflected coordinate system. Other-kind gate uses left-to-right short circuit; confirmation is not compared when First fails.

### P12 — strict_cross

Find upper bound (first timestamp strictly after event) in second_times. Delegate P13 with left,level,above; no same-event recross or main fallback. Upper bound excludes every lower timestamp equal to event; level is passed unchanged.

### P13 — _cross_from

Select lower_index.first_greater if above truthy, else first_less. Search [left,len(seconds)), strict by index contract. Null if no position, else obtain timestamp at position and map to main index with clamp=true; return (index,instant). No sorting or fallback if lower index absent. The exclusive upper bound is len(seconds), not len(second_times). Non-null zero is a valid position. The returned exact instant is from second_times, with clamp=True on mapping.

### P14 — _extreme

Use main candles across inclusive integer positions [left,right]. Attribute High and max when high truthy; else Low and min. Key normalized Decimal; native first candidate on ties. Re-read normalized selected extreme and return (position,value). Empty range raises native min/max exception; full main candle included, not clipped lower event. Attribute choice and chooser choice are separate truthiness tests. No local clipping, negative-index repair or bounds validation. Normalize selected attribute once again after min/max selection.

### P15 — _matching_seeds

Lazy generator. Occupied set of integer StopAll source indexes (ignores time for this filter). Create event tuples (source_time,priority,kind,item): StopAll 0 always, S 1 and E 2 only if integer index not occupied and calculation_valid is NOT exact false. Sort stably by (source_time,priority,item.source_index). Dedup on (kind,integer source index,source_time) before processing. StopAll sets reference=item if integer number>=3 else null, clears dominant owner and confirmation list, sets qualified=false. Other events ignored until reference exists and current segment not already qualified. Family = lowercased string color for S, family for E; number null for S else integer E number. Update owner via advance_dominant_behavior(previous,kind,family,number,item). If same object as previous skip; otherwise if previous null or new count=1 clear confirmations; append item.decision_event_time. If new owner armed, set qualified=true, yield reference, current behavior, maximum of reference decision and collected confirmations. No MBL activation until later strict break. Dominance dependency is lifecycle owner and must preserve object identity signaling. StopAll events are materialized first, then extend S then E; occupied-index exclusion short-circuits the validity getter. Exact False identity does not exclude None or numeric zero. Sort uses raw source_index but dedup int-converts it. Mark seen before later skips, including ignored events. Every StopAll clears the registers even when number<3. Owner identity comparison is not equality; previous None short-circuits count read. Set qualified before computing max/yield; no local rollback if max fails.

### P16 — detect_bearish

Inputs chronology,S/E/StopAll collections, callable native orders, optional keyword _run null. Create PrimaryResult, choose cross=_run.cross if present else P12; activated list, qualified flag false, seen identities. For each P15 seed set qualified, track minimum qualification_event_time. Dedup by integer reference and second source index (not time). Level=normalized reference main High; find strictly later above cross after qualification. If hit append activation (hit,reference,second,qualification). Stable sort by (hit event,qualification,reference index,second index). If run set schedule to P17 identities. If none activated, status waiting-for-stopall-break if qualified else default; return.
Initialize checkpoints, pending map, promoted_sources set, activation_index=0. Obtain optional orders.confirm_high callback. With run, replay P18 retained steps: set activation count each step; skip steps with null cycle index; append checkpoint if index equals length else replace. For non-null point append to result highs if PH else lows; on PH record physical source and invoke callback if present. Refresh each retained MBL via P20. Determine transition via P02 if any highs.
Loop:
- For every checkpoint absent in pending, compute P22 proposal with current transition boundary (before_event) and cross; pending includes proposals with null point. Determine earliest decision by min(event,index) among non-null proposals; next activation event if available.
- Transition wins ties against both decision and activation: if transition exists and its event<= each non-null next event, set result.transition and terminate.
- Otherwise activation wins decision tie. Consume next activation; if reference physical source already promoted, record run step with no cycle and continue. Else create P21 checkpoint, append run step before adding checkpoint, then append; continue so all same-time activations precede committing points.
- If no decision terminate. Else remove proposal at selected index, set committed checkpoint, append point to checkpoint result and overall result according to kind. Record run step. For PH, add promoted source; if callback exists invoke then clear ALL pending (including null proposals); recompute earliest reversal P02 regardless of callback presence. PL does not invalidate pending by itself.
At end result.cycles = pending proposal result when entry exists, otherwise committed result, in checkpoint order. result.mbl first cycle mbl; status last cycle status overridden to reversed-to-bullish when transition. Dedup post_pl3_orders across cycles by (direction,first_index,break_index), first wins; sort by (stop_event_time,negative first_index,break_index). Return aggregate. No rollback of external callbacks or run state on exceptions; no arbitrary iteration cap.

### P17 — _activation_identity

Input activation tuple. Return (hit exact time,hit index,integer reference source index,reference source time,integer second source index,second source time,qualification). Price absent; used in live schedule comparison.

### P18 — _PrimaryRun.retained_steps

No previous -> return current steps list itself. Else start frontier=dirty_event; find common prefix of prior/current schedule exact tuple equality. For each schedule with differing suffix, frontier=min(frontier,first changed activation event). Traverse prior steps in order; stop at step.event_time>=frontier; append original earlier step references to current list. Return current list. Requires meaningful non-null frontier when previous exists; not a general deduplication routine.

### P19 — _PrimaryRun.cross

Key=(event,string level,above). Current hit (including null) returned. Compute left=upper_bound(second_times,event). If previous key exists, reuse old non-null hit strictly before dirty event; else left=max(left,lower_bound(second_times,dirty_event)). Query P13, store result and return. No previous entry => full strict-after-event scan. Does not validate market identity beyond supplied run/dirty contract.

### P20 — _refresh_cycle_mbl

Read checkpoint.result.mbl, find first below-price cross after MBL trigger via passed cross. Null/falsy stop becomes (null,null). If stop pair unchanged return same checkpoint. Else replace mbl stop fields and replace result then checkpoint (shallow record replacements). No mutation of original record, other lists remain shared.

### P21 — _activate_cycle

Input chronology, activation, cross default P12. Build PrimaryResult with cycle_id formatted bearish:cycle:reference.source_index:second.source_index and qualification. Reference price normalized main High. Gate index/cursor=activation crossing. P14 minimum Low across second source index through gate index inclusive; cross below that floor after cursor. Set result.mbl using source/time/floor, integer reference/second source indexes, gate/cursor, optional broken index/event; return checkpoint with reference price/gate/cursor/default PH phase.

### P22 — _next_point

Inputs chronology, committed checkpoint, orders callback, optional before_event null and cross P12. Make replaced result with fresh copies highs/lows/post_pl3_orders, keep other result fields; local phase/reset_high/gate/cursor, reference price and MBL floor. Prospective checkpoint replaced with result, not committed. Loop, with no arbitrary cap:
1. high_level=last PH price or reference; low_level=last PL price or floor. high number=1 if reset_high or no highs, else prior+1. Low number=prior+1 or 1.
2. phase seek: find up above high_level and down below low_level after cursor; neither => status waiting-for-structure-break, return (prospective,null); equal exact events => ambiguous-raw-boundary-order, return null proposal. Otherwise earliest direction chooses PH or PL and gate/cursor from hit.
3. before_event exists and cursor>=boundary => waiting-for-trend-reversal, null proposal. Set number for phase; continues_primary iff PH and number>1.
4. Call orders(phase,number,gate_index,cursor). Candidates satisfy P11 gate, AND if continuing primary either parent-stop cause OR reset-leg cause plus non-null box_top strictly above prior high_level, AND stop_event_time>confirmation_event_time. Pick min by (stop_event_time,negative First index,Break index), default null.
5. Cancellation cross = below floor for PH; above high_level for PL, strictly after cursor. cancel_is_next truthy iff cancellation exists AND (PL number>3 OR no winner OR cancel strictly earlier than winner stop). When true inspect RAW row at upper_bound(second_times,cancel event)−1: for PH opposing High>high_level, for PL Low<floor. If opposing also true => ambiguous-raw-boundary-order; null proposal. No invented within-row order.
6. PL number>3: post_pl3_orders becomes candidate list restricted to stop strictly before cancellation if any. No cancellation => post-pl3-orders-only, null proposal. Else update gate/cursor to cancel, phase=PH, continue; never PL4.
7. Cancellation and winner same stop event => ambiguous-raw-boundary-order, null proposal. Earlier cancellation or no winner: advance gate/cursor. If PL switch to PH; if PH and existing lows, inspect exact cancellation row Low and switch to PL iff Low<low_level else seek; if no lows switch PL. Continue.
8. No winner => status waiting-for-{lowercase phase}-order-stop; null proposal. Else choose source with P14 over gate through winner.stop_index inclusive, maximum High for PH/minimum Low for PL. Create PrimaryPoint with phase,number,source main time/price, gate/cursor, winner stop index/exact event, winner snapshot, cycle_id. Set prospective.gate_index=gate, cursor=winner stop, phase=seek, reset_high=(prior phase PL); return (prospective,point).
Null proposal returns prospective whose checkpoint phase/cursor are original unless updated in step 8; result.status/post-PL3 list may be revised. No native ledger write here. before_event checks gate cursor only; global loop resolves exact decision vs transition.

### P23 — NativePrimaryOrders.__init__

Retain chronology and groups references, optional on_high null, direction default bearish. No validation or copy.

### P24 — NativePrimaryOrders.confirm_high

Call on_high(point) only if non-null; ignore return. No other mutation in wrapper.

### P25 — NativePrimaryOrders.__call__

Inputs kind,number (unused),gate_index,event. Owner bucket bearish for PH else bullish. is_primary iff kind equals PL when stored direction bullish, otherwise PH. Physical direction=chronology.opposite_direction(owner). Traverse groups[owner].get(OrderAudit,empty tuple). Each prepared entry exposes reaction,entry,crossed,causes; convert First/Break indexes; exact confirmation using physical direction; cause-kind tuple deduplicated preserving encounter order. Require P11 with PH gate for is_primary else PL. Non-primary additionally integer native reaction number>0. Collect eligible records before stop filtering. Among parent-stop cause records find first_direct=min(First,confirmation,Break), first tie. Iterate records in input order: for non-primary, require reset-leg OR record identity is first_direct. Require crossed non-null and crossed[2]>max(confirmation,event). Emit StructureOrder with original physical direction, integer native reaction number, First/Break, confirmation, normalized stop level, integer stop source index, integer crossed main index, crossed exact event, causes, normalized box top/bottom, string reaction mode and tuple of deep-copied audit cause dicts. Return list; no geometry synthesis, sort or callback in this method.

### P26 — _negate_price

Normalize Decimal via as_decimal, then native copy_negate (no arithmetic unary minus/context rounding). Return reflected value. Preserve signed zero/exponent semantics of native operation.

### P27 — _ReflectedRow.high

Return P26(original.low); reads lazily, no storage.

### P28 — _ReflectedRow.low

Return P26(original.high).

### P29 — _ReflectedRows.__init__

Snapshot sequence as tuple of original row references. No per-row copy or reflection until access.

### P30 — _ReflectedRows.__len__

Return retained tuple length.

### P31 — _ReflectedRows.__getitem__

Use native tuple indexing, wrap selected item in new _ReflectedRow. No explicit slice handling or bound guard; type annotation not validation.

### P32 — _ReflectedPriceIndex.__init__

Retain original index reference.

### P33 — _ReflectedPriceIndex.first_greater

Delegate original.first_less(left,right,P26(level)); same bounds and original positions.

### P34 — _ReflectedPriceIndex.first_less

Delegate original.first_greater(left,right,P26(level)).

### P35 — _ReflectedChronology.__init__

Wrap original candles and seconds with P29; retain original times and second_times references; lower_index=P32 adapter; main_index=original bound callable. No time reflection or timeframe reconstruction.

### P36 — _reflect_structure_order

Return replaced order: direction bearish if original exactly bullish else bullish; stop level negated; box_top=negated original bottom if non-null, else null; bottom=negated original top if non-null, else null. All other fields retained including cause tuples, times, physical indexes, reaction mode.

### P37 — detect_bullish

Inputs same market collections/orders, optional _run null. Fresh local point_cache keyed by object identity. Define P38–P43 helpers/adapters. Call P16 with reflected chronology P35, original S/E/StopAll collections, new ReflectedOrders adapter, same _run. Project returned result via P41. Source run remains in reflected coordinates; callbacks get native projected points. Does not reflect tags, S/E families, causes or time.

### P38 — detect_bullish.cycle_id

If value truthy replace first occurrence of bearish:cycle: with bullish:cycle: (not restricted to prefix); else return as supplied.

### P39 — detect_bullish.point

If id(item) absent local cache: consult _run.previous.projected_points by id only when run and previous truthy. Reuse projection iff old pair non-null and old original is item. Otherwise replace item: kind PL if PH else PH, negated price, P36 order, P38 cycle_id, recursively project truthy identity_source else null. Store local cache. If run non-null save (original,projection) under id. Return local projection; shared identities preserved within invocation; no cycle detection on recursive identity_source.

### P40 — detect_bullish.status

Sequential string replacements globally: ph -> __primary_high__; pl -> ph; placeholder -> pl; reversed-to-bullish -> reversed-to-bearish. No general uppercase transformation.

### P41 — detect_bullish.result

Return replacement with direction bullish, highs projected from original lows, lows from original highs, mbl replaced with negated price if truthy else null, projected cycle id/status, each post_pl3 order reflected, recursively project cycles, transition if truthy replaced with negated level/projected high/target_direction bearish; else null. Other result fields preserved. Fresh lists, original source state unmodified.

### P42 — ReflectedOrders.__call__

Nested adapter. Map requested PH -> native PL, else native PH. Invoke original orders(actual_kind,number,gate,event), reflect each returned snapshot P36 in iterable order. Return list. No price changes to native callback inputs beyond reflected-kind mapping.

### P43 — ReflectedOrders.confirm_high

Read original orders.confirm_high default null. If non-null invoke on P39-projected item. Ignore returned value. Adapter method itself exists even when original callback missing.

### P44 — LivePrimaryContinuation.__init__

Validate direction exact bearish/bullish, else ValueError. Select P37 if bullish else P16; retain timeframe and chronology.times; create default _PrimaryRun, detect with run, retain result.

### P45 — LivePrimaryContinuation.result

Return retained result object itself (not copy). External mutation is not prevented by wrapper.

### P46 — LivePrimaryContinuation.update

Require timeframe equal original; else ValueError. Require first_dirty_event isinstance datetime (subclass allowed), else TypeError. Frontier initially dirty event; for each old/new main times compute upper_bound(event)−1; if nonnegative and event strictly before containing main end, rewind frontier=min(frontier,main start). New _PrimaryRun(previous current run,frontier); detect with new inputs/orders; on success clear run.previous, replace retained run/result, then retained times; return result. No update of wrapper if detect fails, but callbacks may already have mutated external ledger. Schedule comparison can rewind further in P18.
