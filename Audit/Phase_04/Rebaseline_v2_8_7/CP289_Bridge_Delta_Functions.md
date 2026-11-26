# CP289 — engine/bridge/trading_pipeline.py current declaration delta

Pinned main: c99b4c957e932d9ee70c492ca03ce80711447fc1. Blob: e1e65ba960c5f726f9a05e2ab89e4457b65e5735. Scope: changed and added named declarations from CP287 structural delta; current source supersedes historical function descriptions for these scopes. The unaffected portions of historical TB/TF contracts remain navigation evidence, not proof of complete runtime equivalence. Native exceptions propagate unless an owning path explicitly catches them. No production execution.

## BD01 — LiveMarketViews

Current lines 336–364; changed; old lines 336–363.

Owns lower and main candle lists and indexes; now also owns a fresh LiveClosedRegimes instance. Existing update logic retains aliasing of lower/main for timeframe 1; no new runtime guarantee of immutable objects. See unchanged TB20/TB21.

## BD02 — LiveMarketViews.__init__

Current lines 339–344; changed; old lines 339–343.

No parameters other than receiver. Allocate separate empty seconds/candles lists, set both indexes null, instantiate one LiveClosedRegimes. Construction failures propagate; no result.

## BD03 — LiveClosedRegimes

Current lines 1756–1785; added; new declaration.

Per-view cache owner. Maintains preceding successfully published closed-prefix result map; stage and resolve below define exact lifetime.

## BD04 — LiveClosedRegimes.__init__

Current lines 1759–1760; added; new declaration.

Allocate empty published map; no other inputs, no output.

## BD05 — LiveClosedRegimes.stage

Current lines 1763–1785; added; new declaration.

Context-manager accepting first_dirty_main. Bind previous published mapping and new empty current mapping. Yield resolver closure. On normal resumption assign current as published; exception thrown through yield skips assignment. Does not catch callback exceptions or merge unused entries.

## BD06 — LiveClosedRegimes.stage.resolve

Current lines 1767–1781; added; new declaration.

Inputs direction, market, boundary, calculate callback. Form key in order: direction, market.index_offset, offset+boundary, boundary candle timestamp, market.start_index, min(market.end_index,boundary-1), initial bullish, initial bearish. Consult previous only if offset+boundary <= first_dirty_main, else null. Null/missing invokes calculate with no arguments. Store selected result in current by key, return it by reference. Invalid boundary/lookup/callback failures propagate; no mutation of original price.

## BD07 — MarketIndexWindow

Current lines 1788–1823; added; new declaration.

Adapter over retained range index, with local candle reference, timestamp slice, logical length and composed base offset; shares base query semantics rather than duplicating market data.

## BD08 — MarketIndexWindow.__init__

Current lines 1791–1798; added; new declaration.

Inputs index, candles, start, stop. Store candle reference, slice index.times[start:stop], store stop-start. If parent is a MarketIndexWindow, unwrap base and add start to parent's offset; otherwise base=index, offset=start. No explicit bounds/identity validation here.

## BD09 — MarketIndexWindow._first

Current lines 1800–1805; added; new declaration.

Inputs query, left,right,level. Clamp left at least zero, right at most length. If left>=right return null without base query. Otherwise invoke query(offset+left,offset+right,level); translate non-null position by subtracting offset. Propagate native errors.

## BD10 — MarketIndexWindow.first_less

Current lines 1807–1808; added; new declaration.

Delegate to _first with bound base.first_less; strict low crossing and local positions inherited from base.

## BD11 — MarketIndexWindow.first_greater

Current lines 1810–1811; added; new declaration.

Delegate to _first with bound base.first_greater; strict high crossing and local positions inherited from base.

## BD12 — MarketIndexWindow._extreme

Current lines 1813–1817; added; new declaration.

Inputs query,left,right. Require 0<=left<right<=length else ValueError (no lower-timeframe candles). Call base query at translated bounds, return its value unchanged and translated position. No Decimal conversion or new tie rule.

## BD13 — MarketIndexWindow.range_minimum

Current lines 1819–1820; added; new declaration.

Delegate to _extreme with base.range_minimum; base earliest tie preserved.

## BD14 — MarketIndexWindow.range_maximum

Current lines 1822–1823; added; new declaration.

Delegate to _extreme with base.range_maximum; base earliest tie preserved.

## BD15 — market_segment

Current lines 1826–1857; changed; old lines 1755–1775.

Inputs market,start,stop; optional initial flags and indexed_reaction. Reject unless 0<=start<stop<=main length. Determine first time and next main start or last+timeframe. Lower slice uses lower bounds at both times; main/lower list slices retain original order. Copy/reindex main when indexed_reaction is null or start nonzero, lower when null or left nonzero. With indexed support build lower and main windows, register against exact selected lists, pass both into runtime chronology constructor. Return MarketContext with visible start max(0,old start-start), visible end min(stop-start-1,old end-start), cumulative offset; inherit initial flags only at zero start unless explicitly supplied. Native exceptions propagate. Supersedes TB63.

## BD16 — PipelineState

Current lines 2114–2133; changed; old lines 2032–2050.

Mutable slotted shared direction state; new required full_stopalls_by_direction mapping is populated in prepare_pipeline_state. Per-direction values belong to accepted feedback, not a visibility-time reconstruction.

## BD17 — FullDirectionState

Current lines 2137–2150; changed; old lines 2054–2066.

Mutable slotted record of one direction's accepted detector state. New stopalls list has an independent empty list factory. Final feedback replaces e_zones and stopalls together; other fields are preserved by record replacement.

## BD18 — calculate_direction_with_order_b_feedback

Current lines 2569–2645; changed; old lines 2485–2549.

Inputs direction, engines, full market/results/geometry, timings, required stopall_enabled and optional live. Start empty legs and seen identities; shared stages null. For at most eight passes calculate full direction using current legs, first shared state retained. If enabled form accepted E physical pair set, restore independent S roots, append only absent-source donors after accepted list; reconcile lifecycle with optional pass-keyed live StopAll finder. Otherwise copy E and empty stops. Restore independent roots on result, ensure accepted audit. Discover reset legs using full reaction/reset, opposite reaction, eligible A, invalid A, S, accepted E/StopAll, detector and lifecycle priority; optional live finder keyed feedback/pass. If exact new identity equals old, register discovered legs and return replacement state with E and StopAll. If identity already seen raise RuntimeError; else record and continue. Exhaustion raises RuntimeError. No fabricated fallback. Supersedes TB74.

## BD19 — prepare_pipeline_state

Current lines 2648–2802; changed; old lines 2552–2703.

Retain args-derived directions, behavior enable and reusable E+S gate. Initialize full mappings including new StopAll map. In reusable path create both geometry detectors; use native detect or live.reactions, derive ownership via native or live route, optional stage callback. Create direction-specific opposite geometry callbacks; calculate both directions if primary supplied else requested directions. For each feedback result retain E, StopAll, detectors, Blue/A/S lists and validity sets in maps; report lifecycle ready if callback present. Non-reusable path creates independent A-stop finders, computes required reactions and ownership or empty identity sets; full maps remain empty. Return PipelineState with new StopAll map and live pointer. No scope-level exception suppression. Supersedes TB75.

## BD20 — finalize_direction_visibility

Current lines 2939–3110; changed; old lines 2840–3076.

Input current direction range and shared state; first choose visible A and remove A after S stops. Copy already accepted E and stored direction StopAll (default empty), without new StopAll reconciliation. Select parent-stop callback: E detector if non-null using S/E shape (a_source_time), otherwise S detector first_a_stop with Decimal(str(price)) and decision event. Snapshot accepted S/E/StopAll for projection. Finalize behavior visibility using S candidates, invalid S, stop and candidate callbacks, full A/candles. Capture primary groups before range filtering (valid full A, selected S/E, stops). Filter all public A/S/E/StopAll by inclusive source indexes; remove invalid A/S pairs. Obtain full-history eligible A source times, collect all reactions, mark internal Blue, filter internal behavior outputs. Build required physical Order pairs only with both indexes present; prepare audit if E detector key exists, else empty; validate audit when detector exists. Return DirectionVisibilityState with public Blue, display rows, audit, projection and primary groups. Supersedes TB77; detailed lifecycle selection remains owner-defined.

## BD21 — calculate_primary_structures

Current lines 3405–3458; changed; old lines 3371–3424.

Use provided direction visibility.primary_groups and compute opposite range and visibility using current no-reconciliation signature. Build accepted A sources per owner from full S detector eligible rows excluding invalid identity pairs; populate full-range OrderAudit for both. commit_high callback registers direction-specific primary point and refreshes that owner's audit. Construct NativePrimaryOrders, select bullish/bearish detector or live primary continuation, reconcile primary labels through visible end. Rebuild visible audit retaining required physical identities. Return primary result; updates group/audit state and propagates exceptions. Supersedes TB87; nested TB88 body unchanged.

## BD22 — build_direction_output

Current lines 3461–3500; changed; old lines 3427–3467.

Calculate range state, finalize visibility without old arguments. Primary direction is bearish when args direction is both, otherwise requested direction. Only calculate primary when current direction matches, primary engine present, direction has E detector and lifecycle argument non-null. Save primary result, reconcile StopAll ownership through end, validate audit. Serialize direction, update primary fields only when primary produced, return mapping. Supersedes TB89.

## BD23 — build_reversed_trend_outputs

Current lines 3531–3630; changed; old lines 3498–3591.

Copy local args per direction using nested calculate, project payload with absolute indexes using nested publish. Start direction opposite target, incoming null; indexed_reaction selected only if supplied closed_regime is non-null. Resolver prefers live.closed_regime when live present, otherwise supplied callback. Obtain optional reaction release method. Loop: require 0<boundary<current length or RuntimeError; obtain independent closed prefix result through resolver or calculate_closed. Require confirmed point number 3 with exact transition source time and price, else RuntimeError. If no visible history recursively empty list values. Publish stopped history (incoming transition, end time, stopped statuses, capped MBL), serialize incoming transition, segment remaining market from reversal candle inclusive with target initial flag and indexed support. Compute active direction using optional live.active_regime; always release selected indexes in finally via optional method or live fallback. If no next transition or transition beyond visible end publish final active group and break; otherwise continue. Merge regimes, preserve sequence. Supersedes TB91; nested calculate/publish/empty_lists retain historical logic.

## BD24 — build_reversed_trend_outputs.calculate_closed

Current lines 3576–3592; changed; old lines 3538–3554.

Closure defaults capture current,boundary,direction. Segment [0,boundary) with indexed support. If prefix visible range empty, replace range with full prefix for calculation, retaining has_history=false. Compute direction history and state, select primary high resolver for bearish else low, resolve through last prefix index. Return tuple (prefix offset, first timestamp, has_history, history payload, confirmed points). Finally release exact prefix lists via optional release method or live fallback. Cache stores tuple, not live state. Supersedes TB94.

## BD25 — build_response_payload

Current lines 3633–3710; changed; old lines 3594–3667.

Assemble version/enable flags, timeframe, actual bounds, requested direction payloads; use state.primary_result transition only if present and index<=visible end. Rebuild independent regimes with live stages and optional closed_regime; active direction from maximum (segment calculationStartIndex default -1,direction) with fallback target. Repair horizon = visible last main timestamp+timeframe-1 second. Confirmation closed boundary = min(epoch(through)+1,last lower epoch+raw_timeframe default1); closure checks decisionTime+args.timeframe<=boundary. Annotate each segment independently with shared original lower repair search. Round only timing telemetry to two decimals and return envelope. Supersedes TB96; no price rounding.

## BD26 — calculate_live_from_buckets

Current lines 3738–3753; changed; old lines 3695–3703.

Inputs args, engines, buckets and optional views, delta, report callback. Form inputs tuple from bucket lists and view/delta. No views: call _run_live_calculation directly with bucket preparation. Views: assert delta non-null, enter views.closed_regimes.stage(first_dirty_main), pass yielded resolver to run, return result through context exit. Failure propagates and stage assignment is skipped on exception. Supersedes TB100.

## BD27 — _run_live_calculation

Current lines 3756–3767; changed; old lines 3706–3714.

Capture start perf counter, fresh timings; enter market calculation scope, prepare market with supplied callable and arguments, optionally report chronology ready, prepare shared pipeline state, return build_response_payload with optional closed_regime passed through. Scope cleans caches on exit per unchanged TB98. Supersedes TB101.
