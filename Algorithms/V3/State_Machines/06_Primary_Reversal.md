# Primary structures, Matching Behavior Leg and reversal — state and lifecycle contract (V3)

Source-derived extended state machines complement [Primary](../12_Primary_Structures.md), [PH/PL](../13_Primary_High.md), [MBL](../14_Matching_Behavior_Leg.md), [Reversal](../15_Trend_Reversal.md). Labels are analytical unless identified as native. Evaluate guards in local table order; each machine has its own registers and traversal. A transition may be a substep of another; it is not a separate production event or a new field. B/R denote bullish/bearish; strict trend outward predicate Low < level / High > level respectively, and physical Order uses its own direction. Preserve exact Decimal representation, time and source identity. Null means no evidence unless a stated fallback exists. Procedure IDs are defined in the [V3 registry](../README.md); errors propagate except explicit recoverable branches.

## MB — Matching behavior qualification and activation

Reference core is bearish: primary PH, secondary PL. Bullish is reflected, primary PL/secondary PH, exact sign-copy, swap price axes and roles. Native timestamps, identities, accepted family, physical Order provenance unchanged. Registers reference StopAll, exact dominant owner, confirmation times, qualified flag, dedup event set, activation schedule.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| MB01 | INIT | Accepted S/E/StopAll | Exclude S/E at StopAll occupied source and exact Boolean False validity; sort source, StopAll/S/E rank,raw index; dedup(kind,int index,time) before later skips | EVENT | P15 |
| MB02 | EVENT | StopAll encountered | Reference=record only if number>=3; owner=null, confirmations empty, qualified=false | EVENT | P15 |
| MB03 | EVENT | No reference or already qualified | Skip non-StopAll event | EVENT | P15 |
| MB04 | EVENT | Accepted S/E | Advance exact owner via LC05; same owner object skipped; previous absent or new count1 clears confirmation list; append actual decision | EVENT | P15,LC05 |
| MB05 | EVENT | Owner armed | qualified=true; yield reference,decisive second, max(reference decision,matching decisions) | EVENT | P15 |
| MB06 | INIT | Qualified seeds enumerated | Dedup reference/second source indexes; preserve earliest qualification even without crossing | BREAK | P16 |
| MB07 | BREAK | No strict crossing of reference main High after qualification (B reflected Low) | No activation; if no other activated seed status waiting-for-stopall-break | RETURN or BREAK | P12,P16 |
| MB08 | BREAK | First strict crossing found | Schedule activation by exact event,qualification,reference index,second index | SCHEDULED | P16 |
| MB09 | SCHEDULED | Global activation selected, reference already promoted | Consume activation without new cycle | RETURN | P16 |
| MB10 | SCHEDULED | Reference not promoted | Freeze MBL min Low second..activation main inclusive (B max High), earliest tie, own strict later stop, cycle ID and initial phase/gate/cursor | ACTIVE | P14,P21 |
| MB11 | ACTIVE | Public horizon | Publish only when activation and at least one primary decision within horizon; retain earliest primary confirmation | RETURN | P09,TB84 |

## PP — Prospective per-cycle structure machine

Native phase = seek/PH/PL in bearish reference coordinates; prospective copies of committed result, phase, reset_high, gate_index,cursor,reference_price, MBL floor. Current high=last PH else reference; current low=last PL else floor. PH number=1 if reset_high or no PH else previous+1; PL=previous+1 or1. The prospect does not mutate committed ledger; proposed cancellation and status may be displaced after another cycle's commitment.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| PP01 | INIT | Committed checkpoint | Copy point and post-secondary3 arrays; local phase/gate/cursor; derive levels/numbers | seek or PH or PL | P22 |
| PP02 | seek | Neither strict high nor low break after cursor | status waiting-for-structure-break; no proposal | RETURN | P12,P22 |
| PP03 | seek | Both crossings same exact time | status ambiguous-raw-boundary-order; no proposal | RETURN | P22 |
| PP04 | seek | High break earlier or only high | gate,cursor=high crossing | PH | P22 |
| PP05 | seek | Low break earlier or only low | gate,cursor=low crossing | PL | P22 |
| PP06 | PH or PL | before_event exists and cursor>=transition | status waiting-for-trend-reversal; no proposal | RETURN | P22 |
| PP07 | PH or PL | Native Order service | PH confirmation>=gate (First not constrained by gate); PL First>=gate main and confirmation>gate; native actual stop>max(confirm,gate); secondary canonical ordinal>0, reset-leg or earliest direct parent-stop | RACE | P11,P25 |
| PP08 | RACE | Continuing PH number>1 | Require parent-stop OR reset-leg with nonnull boxTop>prior high; all candidates actual stop>confirmation; select min(stop,-First,Break) | RACE | P22 |
| PP09 | RACE | Cancellation next (earlier than winner or winner absent, or PL number>3) | Cancellation is Low<MBL floor for PH, High>current high for PL. Inspect exact cancel row; opposing High>current high for PH or Low<floor for PL => ambiguous, no proposal | CANCEL or RETURN | P22 |
| PP10 | RACE or CANCEL | PL number>3 | Retain candidate Orders whose stop<cancel or cancel absent; no PL4; absent cancel status post-pl3-orders-only, else gate,cursor=cancel and phase PH | RETURN or PH | P22 |
| PP11 | RACE | Normal stage cancel and winner same exact event | Ambiguous, no proposal | RETURN | P22 |
| PP12 | CANCEL | Earlier cancel wins, current PL | Advance gate/cursor to cancel, switch PH | PH | P22 |
| PP13 | CANCEL | Earlier cancel wins, PH and no existing PL | Advance gate/cursor, switch PL | PL | P22 |
| PP14 | CANCEL | Earlier cancel wins, PH and existing PL | Switch PL only if cancel row Low<previous PL, else seek; do not invent prior-low break | PL or seek | P22 |
| PP15 | RACE | No winner | status waiting-for-ph/pl-order-stop | RETURN | P22 |
| PP16 | RACE | Winner with no earlier cancel and no tie | Freeze main extreme gate..stop inclusive, earliest equality; build point with native physical Order, trigger and decision; prospective cursor=winner stop,phase=seek,reset_high=(old phase PL) | PROPOSED | P14,P22 |

PH/PL above are native bearish-core roles, not universal labels. In bullish reflection all inequalities/levels map exactly, including continuing-primary requirement original boxBottom<prior PL. Secondary number4 is not created (post-PH3 orders only for bullish). P22 local phase updates on cancellation need not become committed checkpoint; return is speculative until global scheduler decides.

## PG — Global exact-event scheduler

Registers ordered activation schedule, activation_index, cycle checkpoints, pending proposals, promoted primary physical sources, aggregated primary/secondary arrays, candidate reversal. Pending proposals include no-point states. Only global earliest confirmed decision commits ownership.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| PG01 | INIT | No activation | Return initial result; qualified but none activated -> waiting-for-stopall-break | RETURN | P16 |
| PG02 | INIT | Activated schedules exist | Restore retained live steps if applicable, replay primary callbacks, refresh MBL stops; compute earliest reversal from retained points | SCHEDULE | P16,P18,P20 |
| PG03 | SCHEDULE | Cycle lacks pending entry | Obtain prospective PP result bounded by current reversal | SCHEDULE | P16,P22 |
| PG04 | SCHEDULE | Reversal exists and <= earliest decision and <= next activation (absent treated unbounded) | Commit transition and stop scheduler | RETURN | P02,P16 |
| PG05 | SCHEDULE | Next activation <= earliest decision, or no decision | Consume activation; skip promoted reference else create independent checkpoint; activation wins equal-time decision | SCHEDULE | P16,P21 |
| PG06 | SCHEDULE | No activation selected and no decision | Stop scheduler | RETURN | P16 |
| PG07 | SCHEDULE | Earliest decision by (event,cycle index) | Pop pending, replace checkpoint, append point in cycle/global arrays; record optional retained step | COMMITTED | P16 |
| PG08 | COMMITTED | Primary PH in reference coordinates | Mark source promoted; invoke confirm_high if present; if callback present clear ALL pending proposals; recompute reversal | SCHEDULE | P16,P24,TB88 |
| PG09 | COMMITTED | Secondary PL | No primary callback/pending clear solely for secondary | SCHEDULE | P16 |
| PG10 | RETURN | Aggregate cycles | Use pending prospective status when present; first MBL,last cycle status or reversed; dedup post-secondary3 Orders by direction/First/Break, sort stop,-First,Break | RETURN | P16 |

Neither local cancellation nor pending proposal commits a primary point. Global transition beats both activation and point at equality; activation beats decision at equality; decision tie uses cycle index.

## PO — Physical ownership and numbering

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| PO01 | LOGICAL | Through horizon supplied | Keep points whose decision main <= horizon, group physical source index/time, order by first decision/source | PHYSICAL | P04,P05,P06 |
| PO02 | PHYSICAL | Group multiple logical points | Choose greatest logical number, then role-order tie; earliest role identity_source if truthy else earliest role, independently of winner geometry; strict progressive price can advance final number, equality cannot | PHYSICAL | P06,P07 |
| PO03 | PHYSICAL | Confirmed primary raw index/time matches StopAll (int index,time) at horizon | Remove StopAll from public ownership; keep historical donor/native evidence | PHYSICAL | P10 |
| PO04 | PHYSICAL | Primary label changed | Reconcile exact ledger parent/reset-leg provenance, preserve identity and prices | RETURN | P08,OA37,OA38,OA39 |
| PO05 | PHYSICAL | MBL presentation | Only formed leg with confirmed primary within horizon; own stop hidden beyond horizon; drawing extension source+400 actual candle or extrapolation, clip at regime end | RETURN | P09,TB84 |

## TR — Confirmed Primary3 reversal and independent regime handoff

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| TR01 | ACTIVE | Physical primary point number exactly3 | First strict High>PH3 or Low<PL3 after its decision; select earliest exact event,source index,cycle ID | TRANSITION or ACTIVE | P02,P03 |
| TR02 | TRANSITION | Transition index beyond visible horizon | Retain current output; no new visible regime | RETURN | TB91,TB96 |
| TR03 | TRANSITION | Index not strictly inside current main history | Error: no valid advancing regime boundary | ERROR | TB91 |
| TR04 | TRANSITION | Valid boundary | Calculate or reuse eligible independent prefix [0,index), then require matching confirmed Primary3 number/source time and price; clear nested public arrays if prefix outside view | CLOSED or ERROR | TB63,TB91,TB94,TB95 |
| TR05 | CLOSED | Prefix valid | Publish closed historical segment with reversal boundary main time, reversed status and clipped MBL caps; preserve exact transition metadata | RESTART | TB91,TB93 |
| TR06 | RESTART | New segment [index,end) | Slice local main/lower; reindex if no indexed support or nonzero origin, otherwise retain row identity; offset absolute identity, bootstrap target direction, fresh calculation (optional live continuation); release exact segment indexes in finally | ACTIVE | TB63,TB91,TB92 |
| TR07 | ACTIVE | No further visible transition | Publish active segment, group by direction, merge list fields and calculationSegments; activeDirection by greatest calculationStartIndex with lexical tie | RETURN | TB90,TB91,TB96 |

No fixed reversal count. Each valid reversal advances boundary. Do not carry historical geometry into new regime, and do not infer a transition from retrospective source position without actual strict crossing after confirmed point decision.

## v2.8.7 reversal integration

The boundary and Primary3 proof remain mandatory even when the explicit closed_regime resolver reuses a settled prefix. The optional resolver selects MarketIndexWindow-backed segment preparation; the live object's closed_regime takes precedence when present. Publication recursively copies cached row lists/dicts, even at offset zero, before adding segment metadata and recalculating final T/F. This is cached result reuse, not a transfer of active trading state. See [TB91 and TB94](../17_Trading_Bridge.md) and [TB103–112](../21_RAW_Aggregation_Contract.md). [Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3531-L3632).
