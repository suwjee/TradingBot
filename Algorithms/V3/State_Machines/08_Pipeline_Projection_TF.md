# Pipeline orchestration, visibility and final True/False — state and lifecycle contract (V3)

Source-derived extended-state models complement [Trading Bridge](../17_Trading_Bridge.md), [Serialization](../19_Serialization.md), [True/False](../16_True_False.md), [exact T/F](../22_True_False_Exact_Contract.md). Labels are analytical unless explicitly native; tables are ordered within each decision stage, not an instruction to persist new fields. Use exact time and Decimal representation, stable ordering, and source-specific guards. Procedure IDs refer to the [V3 registry](../README.md). No runtime results or general mutation-safety guarantee are asserted.

## BF — Batch and full live replay orchestration

Batch and active Live both use fresh calculation scope, full market context, native directional geometry and final output pipeline. Source clipping is presentation. These are ordered phase transitions of the orchestrator, not new trading state.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| BF01 | INIT | Batch CLI or live request | Parse/validate config, resolve configured engine modules; optional features conditional; positive timeframes | MARKET or ERROR | TB04,TB05,TB66,TB67,TB102,L01 |
| BF02 | MARKET | Begin calculation scope | Clear time and market caches; normalize full RAW rows/buckets and derive visible bounds; prepare lower/main market context | GEOMETRY | TB09,TB10,TB68,TB69,TB70,TB98 |
| BF03 | GEOMETRY | Full E path enabled (E module and S enabled) | Prepare full direction geometry and both native streams needed for ownership; if primary loaded calculate both behavior directions; retain native results and behavior views separately | STAGES | TB75 |
| BF04 | GEOMETRY | Non-full path | Prepare requested/native supporting directions and independent A-stop geometry; no full E detector | STAGES | TB75 |
| BF05 | STAGES | Full direction | Shared Blue/A/S, initial S candidate/audit state, then E provisional acceptance and lifecycle invalid A/S, blocked context, accepted E rebuild; reconcile S and E, consumed S evidence, rebuild ledger | FEEDBACK | TB71,TB72,TB73 |
| BF06 | FEEDBACK | Feedback signature stable | Return accepted full direction state per OF machine | RANGE | TB74 |
| BF07 | STAGES | Non-full/range path | Compute necessary upstream dependencies even if hidden, use available full-state ranges where provided | RANGE | TB76 |
| BF08 | RANGE | Direction visibility finalization | Preserve full historical donor groups; apply StopAll optional lifecycle, independent root restoration and audit; verify final reset-leg signature; accepted ledger before view clipping | VISIBILITY | TB77 |
| BF09 | VISIBILITY | Final source selection | Finalize A/S/E/StopAll, clip visible source indexes, filter invalid A/S, mark internal Blue, public Blue filter; prepare audit retaining required out-of-range identities, validate | PRIMARY | TB77,TB61 |
| BF10 | PRIMARY | Enabled primary with E/lifecycle and matching direction | Full primary groups and native audit services, primary commit callback, physical label reconciliation and StopAll ownership; reprepare audit and validate | SERIALIZE | TB87,TB88,TB89 |
| BF11 | PRIMARY | Primary not enabled/eligible | No primary calculation | SERIALIZE | TB87,TB89 |
| BF12 | SERIALIZE | Build output group | Legacy rows and optional additive bridge from same selection; serialize primary when available | REGIME | TB78,TB79,TB80,TB81,TB84,TB89 |
| BF13 | REGIME | Visible confirmed Primary3 transition | Independent closed and new regime replay, aggregate per direction and activeDirection | ANNOTATE | TB90,TB91,TB96 |
| BF14 | REGIME | No visible transition | Keep direction groups | ANNOTATE | TB96 |
| BF15 | ANNOTATE | Final groups | T/F within final segment, bounded lower repair and closed-confirmation gate; build response metadata/timings | RETURN | TF01,TF07,TB96,TB97 |
| BF16 | RETURN | Normal batch CLI | Compact JSON stdout, success exit0; optional progress/timing outputs | EXIT | TB02,TB03,TB102 |
| BF17 | MARKET or GEOMETRY or STAGES or FEEDBACK or RANGE or VISIBILITY or PRIMARY or SERIALIZE or REGIME or ANNOTATE | Failure | Scope finally clears indexes/time caches; ordinary batch outer entry catches Exception and emits error JSON, live uses LT/LX; no universal native rollback | ERROR | TB98,TB102,L02,L13 |

Batch full computation is not truncated at view end. Feature flags can affect detection dependencies and presentation separately. The timing wrapper's completion event in finally is not proof that calculation succeeded.

## OF — Order_B feedback (bounded orchestration, not generic E recursion)

Registers current reset legs (empty first), seen semantic signatures (empty first), shared upstream stages (null first), pass index 0..7.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| OF01 | INIT | First pass | Calculate full direction with current legs, set shared state only first pass | RECONCILE | TB73,TB74 |
| OF02 | RECONCILE | StopAll enabled | Reconcile StopAll with same flag as final visibility; otherwise E copy and empty StopAll | REDISCOVER | TB74,LC40 |
| OF03 | REDISCOVER | Accepted state | Restore independent roots and ensure audit; discover reset legs using eligible A, invalid A set, accepted S/E/StopAll, native trend/opposite streams | COMPARE | OA11,OA65,TB74 |
| OF04 | COMPARE | New semantic signature == old | Return the current full-direction state (not arbitrary replacement with local E list) | RETURN | OA12,TB74 |
| OF05 | COMPARE | Unequal signature already seen | RuntimeError nonconvergence | ERROR | TB74 |
| OF06 | COMPARE | Unequal unseen signature and more passes remain | Add signature to seen, replace legs, reuse shared stages, increment pass | INIT | TB74 |
| OF07 | COMPARE | Eighth pass ends unequal and not repeated | RuntimeError exceeded eight passes | ERROR | TB74 |
| OF08 | RETURN | Final visibility rediscovery | Require same converged semantic signature; mismatch raises; register accepted legs on matching state | RETURN or ERROR | TB77,OA30 |

No other stage inherits this eight-pass cap. Stable signature includes complete semantic fields described by OA12, not just number of Orders.

## PJ — Native calculation versus public projection lifecycle

Registers full native objects, accepted calculation eligibility, public selection, optional additive projection, final audit. Public price strings and time formatting do not change geometry.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| PJ01 | NATIVE | Select view | Reaction First/Reset own/Blue source inclusive index filters; Reaction transform returns separate published geometry; preserve original order | SELECTED | TB22,TB23,RE30 |
| PJ02 | SELECTED | Legacy mapping | Native Decimal string and Tehran-local epoch; optional fields null as specified, flags control Blue/A output | LEGACY | TB06,TB07,TB08,TB24,TB25,TB26,TB27,TB28,TB29,TB62 |
| PJ03 | SELECTED | Optional bridge enabled | Build fresh nested mappings from identical selections; joins by physical identity and full Blue ordinal, including invalid lines where referenced | BRIDGE | TB40,TB49,TB50,TB51,TB52,TB53,TB54,TB55,TB56,TB57,TB58,TB60,TB78 |
| PJ04 | BRIDGE | Recorded stop/confirmation event | If stop main outside exclusive horizon, null both; otherwise exact recorded lower timestamp must prove strict predicate (all rows at same timestamp considered); do not select substitute crossing | BRIDGE | TB34,TB35,TB36,TB37,TB38 |
| PJ05 | BRIDGE | Parent Order requested | Resolve accepted physical First/Break identity; missing -> null | BRIDGE | TB39,TB41,TB42 |
| PJ06 | BRIDGE | Current Order requested | Exactly one distinct accepted audit identity with matching parent source and exact strict stop/cause type/family (or compatible reset-leg post-behavior); missing/conflict -> null; never infer from formation Order | BRIDGE | TB43 |
| PJ07 | BRIDGE | Project Blue standalone stop | Keep null time/eventTime and semantic price, no second detector calculation | BRIDGE | TB51 |
| PJ08 | LEGACY or BRIDGE | Prepared ledger invalid identity/cause owner invariant | RuntimeError rather than fabricate missing audit | ERROR | TB44,TB61 |
| PJ09 | LEGACY or BRIDGE | Primary/regime output | Serialize logical/physical identities, exact time and price, optional fields; offset only designated nonnegative integer index fields/identity elements, not price/number/time | FINAL | TB64,TB65,TB82,TB83,TB84,TB85,TB86 |
| PJ10 | FINAL | T/F presentation | Annotation operates only on final legacy selected rows, not trading objects; no new ownership | RETURN | TF07,TB96 |

## TFC — Published row collection and ownership

Registers selected mapping by sourceTime, basic events buffer, StopAll buffer. Direction primary key primaryLows B else primaryHighs. Remove annotation keys from all visited records, including excluded donors.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| TFC01 | INIT | Direction group | Visit primary,stopAlls,eZones,sZones in order, remove three keys; if calculationValid is not exact false retain first row per sourceTime | SORT | TF07 |
| TFC02 | SORT | Selected rows sorted sourceTime | Traverse selected rows by sourceTime; set current row verdict null immediately before processing that row; non-winning rows not annotated | EVENT | TF07 |
| TFC03 | EVENT | Primary row | Flush StopAll recurrence and clear buffer; number1 T,2/3 F, else null | EVENT | TF06,TF07 |
| TFC04 | EVENT | StopAll row | Append to stop buffer | EVENT | TF07 |
| TFC05 | EVENT | S or E row | Append to basic buffer; primary does not reset basic | EVENT | TF07 |
| TFC06 | EVENT | Exhausted | Run basic recurrence, then remaining StopAll recurrence | RETURN | TF04,TF06,TF07 |

## TFB — Basic S/E verdict and repair recurrence

Registers started=false, repeats map rank→(latest reference,repair_count,verdict_count), known source time→verdict. Rank lexicographic S Blue(1,0),E Blue(2,n),S Red(3,0),E Red(4,n).

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| TFB01 | INIT | No S yet; E arrives | Skip | INIT | TF04 |
| TFB02 | INIT | First S | started=true, evaluate row | ROW | TF04 |
| TFB03 | ROW | S or any lower rank verdict_count>=2 (engulf) | Verdict T | MUTATE | TF03,TF04 |
| TFB04 | ROW | Otherwise known parent verdict | Invert T->F, else T | MUTATE | TF04 |
| TFB05 | ROW | Otherwise | F if number odd, T if even | MUTATE | TF04 |
| TFB06 | MUTATE | Current verdict selected | Write row and known[sourceTime]; remove lower repeat ranks; if removed latest F with repair_count=1 attempt repair at current time | REPEAT | TF04,TF05 |
| TFB07 | REPEAT | Engulf | Zero verdict_count on surviving repeats, preserve repair_count | REPEAT | TF04 |
| TFB08 | REPEAT | Prior same rank and same verdict | New counters prior+1; for F remove prior repair if >=current time, attempt current repair at current time | ROW | TF04,TF05 |
| TFB09 | REPEAT | No same-verdict prior | Counters=1 | ROW | TF04 |
| TFB10 | ROW | Store current rank state after counters computed | Replace latest reference; next row; no final sweep on exhaustion | ROW or RETURN | TF04 |
| TFB11 | MUTATE or REPEAT | Repair callback exists AND key absent | Search original RAW inclusive start/through with row direction strict predicate; store epoch iff hit; present null counts as existing key | MUTATE or REPEAT | TF01,TF02,TF05 |

Row mutations can affect prior references. A callback failure propagates without undoing earlier annotations. No verdict on E preceding first S.

## TFS — StopAll repeated-prefix recurrence

Registers previous_number, previous_series_end, largest_prior_end initially 0; group_start/verdict_start null; repeated_prefix empty; restart=false. Called on ordered StopAll buffer per TFC.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| TFS01 | INIT or SERIES | First row or n<=previous_number | prior_end=previous_number; largest=max(old,prior_end); group_start=verdict_start=n; clear prefix,restart=false | SERIES | TF06 |
| TFS02 | SERIES | Increasing n and restart=true | verdict_start=n, clear restart | SERIES | TF06 |
| TFS03 | SERIES | Each row after start checks | previous=n, T iff (n−verdict_start) even | MATCH | TF06 |
| TFS04 | MATCH | n<=largest_prior_end | Append original row to prefix | MATCH | TF06 |
| TFS05 | MATCH | n in {previous_series_end,largest_prior_end} AND n<=largest AND confirmation callback absent or true | Retroactively mark all retained prefix repeated=true, parity relative group_start; restart=true | SERIES | TF06 |
| TFS06 | MATCH | No matching boundary/closed gate | Preserve current verdict and prefix | SERIES | TF06 |
| TFS07 | SERIES | Exhaustion | Return in-place annotations; no repair, prefix ends with buffer | RETURN | TF06 |
| TFS08 | MATCH | Bridge closure callback supplied | Closed iff decision main epoch+TF<=minimum(visible main end,last raw epoch+raw TF) under exact supplied horizon | MATCH | TB96,TB97 |

A later larger boundary can overwrite earlier temporary verdicts. T/F is not a new trading confirmation or formation algorithm. No transfer of verdict history across independently serialized regimes.
