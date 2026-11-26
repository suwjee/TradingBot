# CP328 — W2 Primary, MBL and reversal

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`. 213 prior rows retained, 30 new scoped transitions. No runtime or RAW execution.

## CP328-S01 — Primary records

Source: `engine/pipeline/PL_PH_detector.py:25–99`.

Frozen StructureOrder, PrimaryPoint, MBL and TrendTransition separate physical Order identity, gate/trigger, decision, source, optional stop and cycle identity; identity_source keyword-only; point aliases high for compatibility. PrimaryResult is mutable slotted with independent list factories, optional MBL/transition and default bearish direction.

## CP328-S02 — P02–03

Source: `engine/pipeline/PL_PH_detector.py:101–125`.

Resolve physical primary points through full main horizon. Exactly number3 only; first strict later crossing above PH for bearish or below PL for bullish; choose min exact event,source index,cycle id or empty. No hit null; bearish-to-bullish helper supports optional cross callback.

## CP328-S03 — P04–07

Source: `engine/pipeline/PL_PH_detector.py:128–172`.

Filter decision_index<=through_index before grouping by raw physical index/time. Sort groups by min decision, source time/index. Earliest role identity by decision,cycle list index (unknown uses len),cycle id,trigger index,number; winner highest number then same role order. Strict progressive price vs previous final point advances number to max(local,previous+1); equality not advance. identity_source earliest role's existing truthy identity or role; logical states unchanged.

## CP328-S04 — P08–09

Source: `engine/pipeline/PL_PH_detector.py:175–195`.

Last source-time label wins; replace Order audit_causes using relabel helper, preserve Order geometry. MBL public only if activation index within horizon and at least one actual primary decision within horizon; iterate cycles or root fallback, choose earliest qualifying decision. Direction selects lows for bullish, highs otherwise.

## CP328-S05 — P10–11

Source: `engine/pipeline/PL_PH_detector.py:198–219`.

StopAll public ownership removed only at physical index/time of confirmed primary through horizon; historical collection unchanged. PH reference gate confirmation>=event, no First constraint; other role requires First>=gate main and confirmation>event.

## CP328-S06 — P12–14

Source: `engine/pipeline/PL_PH_detector.py:222–245`.

Strict later crossing starts bisect_right(exact event), uses lower index first greater/less through len(seconds); no main fallback. Map exact hit to clamped main. Main extreme inclusive both endpoints, min/max normalized Decimal, first tie; return actual selected index/price.

## CP328-S07 — P15 matching seeds

Source: `engine/pipeline/PL_PH_detector.py:248–284`.

StopAll index occupancy excludes coincident S/E; exclude only calculation_valid is False (not general falsiness). Stable sort source,StopAll/S/E rank,raw index; dedup kind,int index,time. Every StopAll resets owner/confirmation/qualified and sets reference iff number>=3. Accept via exact sequence owner, skip same object; clear confirmations on absent/new count1. Armed yields once per reference, qualification max(reference decision,all accepted owner confirmations).

## CP328-S08 — P16 seed activation

Source: `engine/pipeline/PL_PH_detector.py:287–325`.

Earliest qualification retained even if no activation. Dedup reference/second int source indexes; level reference main High; strict later cross after qualification; sort activation exact,qualification,reference/second indexes. Store optional run schedule. None activated returns initial status or waiting-for-stopall-break.

## CP328-S09 — P16 retained schedule

Source: `engine/pipeline/PL_PH_detector.py:326–349`.

Restore retained step activation counter and cycle checkpoints, append prior points, record promoted PH physical sources and replay callback before fresh proposal. Refresh MBL own stops, compute initial reversal from retained confirmed points.

## CP328-S10 — P16 global race

Source: `engine/pipeline/PL_PH_detector.py:350–385`.

Generate pending prospective for every cycle without existing entry, including null proposals. Earliest decision tuple(exact event,cycle index). Reversal <= both next decision and activation wins; otherwise activation <= decision wins. Consume activation, skip already promoted physical reference, optionally record skip step. Other activation builds checkpoint and records step.

## CP328-S11 — P16 commit and aggregate

Source: `engine/pipeline/PL_PH_detector.py:386–418`.

No decision ends loop. Commit selected proposal into cycle and aggregate lists, capture step. Only PH marks promoted source and invokes callback; if callback exists clear ALL pending proposals; recompute reversal after PH. Aggregate cycles from pending prospective state if present else committed; first MBL,last status or reversed; dedup post-PL3 Orders by direction/First/Break first encountered, sort stop,-First,Break.

## CP328-S12 — P17 run records

Source: `engine/pipeline/PL_PH_detector.py:421–455`.

Cycle checkpoint phase PH and reset_high False, reference price/gate/cursor. Activation identity exact cross/main, reference/second index/time and qualification (not price). Step frozen wrapper may reference mutable checkpoint; run retains previous, dirty event, schedule, steps, crossing cache, point projection map.

## CP328-S13 — P18–19 replay boundary

Source: `engine/pipeline/PL_PH_detector.py:457–487`.

Rewind frontier to earliest differing old/new activation time after equal schedule prefix; retain previous steps strictly before frontier. Strict crossing cache key exact event,str(level),above; current hit returned; previous hit strictly before dirty reused; otherwise search from max(strict original left,dirty lower bound). Prior null still constrains left; caller supplies valid dirty.

## CP328-S14 — P20–21 MBL freeze

Source: `engine/pipeline/PL_PH_detector.py:490–515`.

Refresh only MBL stop via strict later crossing from original trigger; preserve same checkpoint if unchanged. Activate cycle id reference/second source indexes, reference main High, freeze min main Low second..gate inclusive, first tie; own stop later below floor; initial phase PH. MBL source time from selected main.

## CP328-S15 — P22 seek

Source: `engine/pipeline/PL_PH_detector.py:518–553`.

Prospective result copies highs/lows/post-PL3 lists, no commitment. Levels last PH or reference, last PL or floor; PH resets to1 on reset_high/no highs, PL increments. Seek strict crossings after cursor; none waiting, equal exact ambiguous, earlier sets PH/PL gate. If cursor>=before_event transition boundary wait.

## CP328-S16 — P22 Order race

Source: `engine/pipeline/PL_PH_detector.py:554–574`.

Request role/number/gate/cursor. Enforce role gate, continuing PH>1 parent-stop OR reset-leg with non-null boxTop strictly > high level; actual stop>confirmation. Winner min stop,-First,Break. Cancellation PH floor Low, PL high-level High; next if PL>3 or absent winner or earlier cancellation.

## CP328-S17 — P22 ambiguity/post-secondary

Source: `engine/pipeline/PL_PH_detector.py:575–596`.

When cancellation next, inspect lower row selected by bisect_right(cancel exact)-1, opposing High>high_level for PH or Low<floor for PL => ambiguous. PL number>3 retains all eligible Orders stopping before cancel (or all absent cancel); no PL4, absent cancel returns post-pl3-orders-only else switch PH and advance. Ordinary equal cancel/winner stop ambiguous.

## CP328-S18 — P22 cancel/confirm

Source: `engine/pipeline/PL_PH_detector.py:597–621`.

Earlier cancel advances gate/cursor; PL->PH; PH with prior lows switches PL only if cancel row Low<prior low else seek, without prior lows PL. No winner waits role Order stop. Winner freezes full inclusive main gate..stop extreme (PH high/PL low), first tie. Point exact trigger/decision and physical Order; prospective cursor=winner stop, phase seek, reset_high only if PL. Commit globally later.

## CP328-S19 — P23–24 native owner callback

Source: `engine/pipeline/PL_PH_detector.py:624–642`.

Native service retains chronology/groups/direction, optional confirm_high invokes callback only when non-null. Creation through confirmed primary parent registration, not speculative crossing.

## CP328-S20 — P25 native gate

Source: `engine/pipeline/PL_PH_detector.py:644–662`.

Owner bearish for requested PH else bullish; primary iff requested role matches active direction's PL or PH. Physical direction opposite owner. Read prepared accepted ledger, int First/Break, native confirmation, crossed and cause kinds dedup encounter order. Gate as primary PH or secondary PL; secondary requires reaction_number>0.

## CP328-S21 — P25 native selection

Source: `engine/pipeline/PL_PH_detector.py:663–680`.

Earliest direct parent-stop record by First,confirmation,Break, before stop eligibility filtering. Secondary permits reset-leg or exact selected direct record object. Require crossed nonnull and exact stop>max(confirmation,event). Build StructureOrder with Decimal stop and box prices, int identity/source/stop, reaction mode, deep-copied audit causes. No new Order creation by query.

## CP328-S22 — P26–34 mirror primitives

Source: `engine/pipeline/PL_PH_detector.py:683–732`.

Decimal copy_negate exact sign without context rounding; lazy reflected high=-original Low, low=-original High, snapshot tuple row refs. Reuse original lower index with first_greater->first_less and negated level, converse for less. Times, second_times, main_index shared. No reverse time.

## CP328-S23 — P35 reflect Order

Source: `engine/pipeline/PL_PH_detector.py:735–740`.

Replace direction bullish->bearish else bullish, negate stop level, swap/negate nullable box edges. Preserve physical First/Break, confirmation, stop event, source indexes and causes.

## CP328-S24 — P36–37 point projection

Source: `engine/pipeline/PL_PH_detector.py:743–768`.

Cache by object id; prior projected pair reused only when original object is same. Swap PH/PL, exact sign price/Order reflection, replace cycle prefix once, recursively reflect identity_source. Save projection pair for live run.

## CP328-S25 — P38–41 bullish dispatch

Source: `engine/pipeline/PL_PH_detector.py:770–797`.

Swap status ph/pl with temporary placeholder and reversal target. Project bullish result highs from core lows, lows from highs, negate MBL price and transition level, reflect cycles and post-secondary Orders, target bearish. Native resolver receives original requested swapped kind, unchanged gate/time; callback receives projected point. S/E families and market colors unchanged.

## CP328-S26 — P42 live initialization

Source: `engine/pipeline/PL_PH_detector.py:800–814`.

Validate direction; choose detector, retain timeframe and times, run initial detection with run state. Result returns same mutable object, not copy.

## CP328-S27 — P43 live update

Source: `engine/pipeline/PL_PH_detector.py:816–839`.

Reject timeframe changes and non-datetime dirty event. Rewind frontier to containing main open in both old/new times when event within bucket, since full candle extrema can change from later lower row. New run(previous,frontier), detect using fresh Orders and replay callbacks; detach previous then publish run/result/times. No independent proof of immutable prefix.

## CP328-S28 — TB88 final label/audit

Source: `engine/bridge/trading_pipeline.py:3449–3458`.

Resolve final physical primary labels through selected market.end_index; direction selects low/high reconcile. Rebuild range OrderAudit after label reconciliation, retain all identities previously prepared via required set.

## CP328-S29 — TB89 direction dispatch

Source: `engine/bridge/trading_pipeline.py:3461–3500`.

Calculate and finalize visibility, primary only selected primary direction (both defaults bearish), primary engine/E/lifecycle present. Save primary_result; remove public StopAll at confirmed primary ownership through end; validate prepared audit against final S/E/StopAll. Serialize direction then update with primary structures.

## CP328-S30 — TB90 regime merge

Source: `engine/bridge/trading_pipeline.py:3502–3528`.

Group segments by direction. Single segment unchanged; multiple use shallow last segment copy, concatenate list-valued fields from all segments and bridgeOutput lists with first key encounter order. Remove aggregate calculationEndTime; retain calculationSegments. No geometry recalculation.

## Cross-owner boundaries

- `engine/bridge/trading_pipeline.py:3405–3448`: Full-history owner groups, accepted A source causes, exact physical ledger, callback registers primary and refreshes owner audit before further proposals. Optional live protocol only if state.live_stages present; CP323-S33 retained.
- `engine/bridge/trading_pipeline.py:3531–3630`: Validate advancing boundary inside current candles; independent prefix [0,boundary) requires number3 same source time and Decimal price before publication even if cached. If no visible history clear public arrays recursively after proof. Publish historical status/end, cap MBL; new regime boundary inclusive with target bootstrap and fresh state; release segment indexes in finally. Live closed resolver precedes explicit closed callback. Continue only while next transition within selected end. CP323-P28 retained.
- `engine/pipeline/order_audit_engine.py:1202–1337`: Primary confirmed parent reparent/revocation and ledger label reconciliation preserve physical identity; CP325-S21–23 retained.
- `engine/pipeline/lifecycle_engine.py:121–139`: Exact dominant owner transition shared by MBL and StopAll; CP327-S03 retained.

## Remaining

CP329 / W2 Bridge projection, serialization and final horizon/identity rules; then live/RAW aggregation boundary reconciliation, W2 closure and W3/W4.
