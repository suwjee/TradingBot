# Shared services, directional adapters and auxiliary lifecycle transitions (V3)

Source-derived service state complements the [indexes and chronology](../20_Indexes_And_Caching.md), [primary](../12_Primary_Structures.md), [ledger](../08_Order_Audit.md) and [projection](../19_Serialization.md) contracts. These are auxiliary operational states rather than new trading states. Each row applies only to its indicated service; do not infer a universal state transition ordering across unrelated services. Procedure IDs refer to the [V3 registry](../README.md).

## CI — Containment index, identity and direction primitives

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| CI01 | INIT | Input interval iterable | Start empty runs and three working lists; traverse in caller order | BUILD | C01 |
| CI02 | BUILD | Nonempty run and incoming start or end strictly decreases | Seal old run before current triple, start new lists | BUILD | C01 |
| CI03 | BUILD | Any incoming triple | Append start,end and original payload reference; equal times do not split | BUILD | C01 |
| CI04 | BUILD | End of input | Seal final nonempty run; retain caller order, no validation or sort | READY | C01 |
| CI05 | READY | Enclosing query | Lazy traversal of each run; stop=lower_bound(start), first=lower_bound(end) restricted before stop; yield original references at first..stop exclusive | READY | C02 |
| CI06 | READY | Ordered naive timestamp optimization test | Exact datetime type, no tzinfo, nondecreasing sequence (equal allowed); empty eligible; otherwise choose caller's legacy path where defined | READY | C03 |
| CI07 | READY | Conversion/identity | Decimal instance returned unchanged, else native string then Decimal; physical pair integer-convert First then Break, no independent validation | READY | C04,C05,C06 |
| CI08 | READY | Direction selection or directional predicate | Exact bullish/bearish select frozen shared policy else ValueError; individual policy methods branch bullish vs else; stop/improve strict, confirmation opposite-side strict, min/max preserves ordinary first equality | READY or ERROR | D01,D02,D03,D04,D05,D06,RE01,RE02 |

## MC — Market chronology and detector service lifetimes

Registers shared sequence time/reflected-view/index associations, detector helpers, per-chronology confirmation/Reset caches and E main extent cache. All are scoped to original data identity and the calculation lifetime, not trading decisions.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| MC01 | INIT | Base detector | Retain source arrays/bounds, get identity-shared timestamp lists and lower index; infer TF from first two main times else1 second, require positive | READY or ERROR | RE03,RE04 |
| MC02 | INIT | MarketChronology | Require TF>=1; reuse supplied index times else create lists, choose supplied lower index or shared source index; fresh confirmation/Reset/E geometry maps | READY or ERROR | RE53 |
| MC03 | READY | Exact event -> main | Chronology upper_bound−1, clamp only negative when requested; DetectorBase additionally requires selected bounds and event before next actual main (last nominal end) | READY | RE06,RE54,RE55 |
| MC04 | READY | Lower interval request | lower_bound(start), lower_bound(end) or length when end null; half-open original sequence | READY | RE05,RE56,RE57 |
| MC05 | READY | Reset time key hit/miss | Key index,owner First,second/display/native time,broken price string; return cache or parse truthy second then display else timestamp, save | READY | RE58,RE60 |
| MC06 | READY | Confirmation key hit/miss | Key direction,flag,First/Break,box price strings,optional intrabar start; invalid start clamps to Break open; first strict lower confirmation else Break open; save without implying exact proof | READY | RE59,RE61 |
| MC07 | READY | First strict lower/range extreme | Invoke segment index query with appropriate strict predicate or nonempty range; reflected index swaps min/max and sign-negates thresholds/values, position invariant | READY | RE35,RE36,RE37,RE38,RE39,RE46,RE47,RE48,RE49,RE50 |
| MC08 | READY | Unified detector constructed | Empty both-direction reaction/reset arrays, null helpers and cursors, empty gate/geometry caches, retain initial flags | READY | RE73 |
| MC09 | READY | Bull/bear helper property queried | Construct only if absent and retain object; each uses source chronology | READY | RE74,RE75 |
| MC10 | READY | Reaction Break-index query | Return cached list iff same stream length; else rebuild in stream order; assumes native append-only stream | READY | RE87 |
| MC11 | READY | Public detector entry | Invoke corresponding first-only or unified scan; initial bullish trend helper selects native trend-start route | READY | RE14,RE81,RE96 |

## RD — Reflected Reaction and independent A-stop finder services

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| RD01 | INIT | Native candle mirror | Exact Decimal sign-copy; swap High/Low and color roles; preserve index/time; candidate and analysis mirror with source ownership swapped | READY | RE16,RE17,RE18 |
| RD02 | READY | Reflected sequence requested | Identity cache lookup; if absent allocate lazy view with null per-index cache; slices materialize requested positions, scalar first access mirrors and stores, repeat returns same object | READY | RE19,RE20,RE21,RE22 |
| RD03 | READY | Bearish detector | Build bullish reference with native time arrays, replace price views and reflected lower index; map context/invalidation/breakout/post-reset results back | READY | RE23,RE24,RE25,RE26,RE27,RE28,RE29 |
| RD04 | INIT | Non-full pipeline independent A-stop finder | Validate trend direction; derive opposite tags; initialize gate result and bounded detection caches | FIND | RE71 |
| RD05 | FIND | Gate key (gate index,end index) cached | Return saved candidate/null; exact gate event argument not part of this finder cache or local selection | FIND | RE72 |
| RD06 | FIND | No eligible adjacent First from max(1,gate) through end | Cache null | FIND | RE72 |
| RD07 | FIND | Eligible First exists | Walk backwards contiguous context tag; inspect cached bounded results by(context,end); if no First>=gate, run new Unified bounded detection with stop_after_first_at_or_after gate, save tuple | FIND | RE72 |
| RD08 | FIND | Return first bounded result with First>=gate or null | Cache selected result; caller OA76 independently checks exact confirmation>stop; no fabricated public Reaction | FIND | RE72,OA76 |

## PR — Reflected Primary adapters

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| PR01 | INIT | Bullish primary request | Build reflected chronology/rows/index; exact price sign-copy, time/index invariant; primary/secondary roles swapped | REFERENCE | P26,P27,P28,P29,P30,P31,P32,P33,P34,P35,P37 |
| PR02 | REFERENCE | Request core PH or PL Orders | Swap actual requested kind to PL or PH; call original service, reflect physical price fields and direction; preserve identity/causes | REFERENCE | P23,P36,P42 |
| PR03 | REFERENCE | Core commits PH | Wrapper confirm_high exists even if native callback absent; if underlying callback exists pass projected original-market primary point; scheduler clears pending proposals according to wrapper presence | REFERENCE | P16,P37,P43 |
| PR04 | REFERENCE | Project point | Cache by object identity; reuse previous run projected point only if original object identical; swap kind, sign-copy price, reflect Order, recursively project identity source, replace cycle prefix | PROJECT | P38,P39 |
| PR05 | PROJECT | Project result | Swap high/low arrays, reflect MBL and transition level, map transition target/status and recursive cycles, reflect post-secondary3 Orders | RETURN | P37,P40,P41 |
| PR06 | RETURN | Read live result or transition point | Return native projected result reference / point property as defined; no further mutation | RETURN | P01,P45 |

Core bearish scheduler sees a callable confirm_high method on the reflected wrapper. The underlying original callback can still be absent. This is a source-level adapter behavior, not a new independent bullish algorithm.

## ES — E initialization and auxiliary stop services

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| ES01 | INIT | Invalid direction or absent sequence-priority resolver | ValueError | ERROR | E08 |
| ES02 | INIT | Valid inputs | Copy invalid-root set, initialize accepted identities and sequence resets; sort S by source,index and opposite resets by exact Reset time; retain bounded chronology | READY | E08,E09,E11,E12 |
| ES03 | READY | No live service and prepared main index owns exact candles | Use matching directional range query (TF1 may use lower index); else initialize shared extent arrays/sparse table | READY | E08,E15,E16 |
| ES04 | READY | Sparse range request | Use inclusive window two overlapping blocks, strict better else earlier position; length<=0 returns left in extent position helper | READY | E17,E29 |
| ES05 | READY | Parent/Order strict stop search | Use lower index when available else original lower scan; no invented main fallback. Live Order crossing cache checks chronology identity; save hit triple or null | READY | E13,E14,E20,E21,E22,E23,E24,E25,E27 |
| ES06 | READY | Public E detection wrapper | Create detector with supplied native parameters and run discovery/reconciliation; no alternate formation | RETURN | E54 |

## LS — Ledger auxiliary state and projection stop guards

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| LS01 | READY | Ledger clear requested | Clear physical map and confirmation index; clear carried/post-stop caches and pending index evidence | READY | OA27,OA28,OA29 |
| LS02 | READY | Carried creation cause changed | Drop carried result/index/append evidence; cause-only change does not automatically clear post-stop cache | READY | OA28,OA40 |
| LS03 | READY | New indexed identity or explicit post-stop reset | Insert confirmation/First/Break in sorted position; append pending to native sorted index when maintained; explicit invalidation clears sorted and pending | READY | OA26,OA29 |
| LS04 | READY | Primary dependency query | Resolve current primary stop/direct match; no match returns stop,null, else native signature includes repr(direct),price string,source,strict stop | READY | OA35 |
| LS05 | READY | Visual lifecycle query | First opposite native record with First and confirmation>=start, return canonical stop/cross and false flag, or empty | READY | OA41 |
| LS06 | READY | Public stop helpers | Use canonical stop/cross/first-match and initial record adapters, preserve own direction and explicit null | READY | OA15,OA24,OA43,OA46,OA47,OA54,OA81 |
| LS07 | READY | S for StopAll | Apply S module eligibility then exclude exact physical source occupied by accepted E; no duplicate sequence occurrence | READY | LC35,LC37 |
| LS08 | READY | Dominance/internal helper requested | Use exact shared sequence priority/key and module identity; internal Reaction lookup/containment are predicate helpers, not extra current display filtering | READY | LC01,LC02,LC04,LC31,LC42,LC43,OA74 |
| LS09 | READY | Projection parent stop read | E detector null or expected attribute/type/value error => null pair; valid returned index must lie in market; A helper catches additionally IndexError; no new arbitrary stop selector | READY | TB45,TB46 |
| LS10 | READY | Projection formation/stop | Blue non-Scale returns source time and null exact event; Scale uses valid ordinal/Break and confirmation with intrabar disabled; behavior stop maps exact price string and horizon proof | READY | TB47,TB48,TB59 |
| LS11 | READY | Projection formatting | Native timestamp string or datetime formatting, other values null; title-case direction/color; Mode A/B mapping or null; optional int/Decimal conversions only as specified | READY | TB30,TB31,TB32,TB33,LC10,LC11 |
| LS12 | READY | Initial visible A selection | Remove A sharing S source; subsequent S-decision main suppression is separate | READY | LC46,LC26 |
| LS13 | READY | Read-only result wrapper | Return copied list or recorded result as owning operation specifies; no inferred deep copy | READY | A23,A38,S41,S50,LC24 |

## IO — Batch/Live adapters, aggregation cache and progress

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| IO01 | INIT | Enter progress sink context | Save token, install sink; restore token in finally even on failure | READY | TB01 |
| IO02 | READY | Timing starts | Emit start before protected work; on exit accumulate duration and emit completion even if work failed | READY | TB02,TB03 |
| IO03 | READY | Batch price normalization | Local key exact type and value; first normalized representation retained on equal key; no added rounding | READY | TB10,TB11,C04 |
| IO04 | READY | Public bucket append wrapper | Enter stage_append context, return delta after exit | READY | TB13,TB14 |
| IO05 | READY | Raw-list Live calculation entry | Fresh market context using raw rows; same run scope and full replay as bucket entry | READY | TB99,TB101 |

## Supporting procedure boundaries

These operations are pure/accessor/search utilities or state-machine subexpressions, not independent trading transitions. Their own exact inputs/outputs and native failures remain normative in the V3 procedure descriptions. A stateful caller invokes them at the applicable guard/effect; do not silently infer a separate lifecycle for each primitive.

| Owner | Supporting procedures | Contract |
|---|---|---|
| A | A02,A03,A04,A05,A06,A14,A32 | Direction, bounds, confirmation and cache-key helpers |
| Blue | BL01,BL02 | Color normalization and indexed main lookup |
| S | S02,S03,S04,S05,S06,S08,S09,S11,S13,S14,S31,S32,S33,S34,S35,S36 | Bounds, time, source extrema (earliest vs last), candidate proof and strict qualification |
| Primary | P13 | First strict cross from provided lower position, main owner result |
| Reaction | RE09,RE10 | Context-run source and exact breakout refinement; used in RXI/RXU |
| Lifecycle | LC07,LC20,LC29 | Strict stop and recorded/derived event, used in SA/LC |

The support table is not a substitute for branch-level transition proof. Native callback bindings and data-dependent aliases remain explicit. Package initialization has only import-path and export-surface behavior documented in the V3 registry; top engine empty, bridge package descriptive only, pipeline compatibility path inserts resolved directory if absent and exposes five named Blue items in order. No trading state is initialized by those package files.
