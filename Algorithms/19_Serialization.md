# Serialization and API

Projection must not recalculate trading decisions. Preserve Decimal strings, identity, direction, native versus public geometry, exact source and event timestamps, order/provenance and stable arrays. Non-deterministic runtime timings are not trading results. No complete schema certification.

Supplementary material below is the English semantic prose of the existing synchronized references, pinned to 466eb875070f02cd0dbfb105033422bbe2fd8c70. It is not a fresh branch-level proof. Exact production-source appendices are excluded. Historical acceptance examples remain historical.
## 13. Serialization / API contract

### 13.1 Projection rule

Legacy serialization contains no trading recalculation. Decimal prices are stringified; native local datetimes are converted through the existing Tehran-local epoch contract. Stable source ordering is preserved. Presentation range filtering is applied after full calculation, and OrderAudit may retain a pre-range physical identity when an in-range public behavior references it. `calculationValid` is emitted as `true` for public A/S because invalid calculation objects have already been removed by the calculation/visibility owner.

### 13.2 Legacy JSON fields

- **Reaction:** `firstIndex`, `firstTime`, `boxTopSourceIndex`, `boxTopSourceTime`, `boxTop`, `boxBottomSourceIndex`, `boxBottomSourceTime`, `boxBottom`, `breakIndex`, `breakTime`, `mode`.
- **Reset:** `index`, `time`, `secondTime`, `brokenLevel`, `fromFirstIndex`.
- **BlueLine:** `direction`, `kind`, `reactionNumber`, `previousStrikeCount`, `strikeCount`, `fibonacciLevel`, `sourceIndex`, `sourceTime`, `sourceExtreme`, `brokenLevel`, `linePrice`, `startTime`, `endTime`.
- **A:** `direction`, `blue1Ordinal`, `blue2Ordinal`, `blue1SourceTime`, `blue2SourceTime`, `blue1StopTime`, `blue2StopTime`, `blue1StopLevel`, `blue2StopLevel`, `continuationLevel`, `continuationSourceIndex`, `continuationSourceTime`, `triggerIndex`, `triggerTime`, `triggerEventTime`, `reactionNumber`, `reactionFirstTime`, `reactionBreakTime`, `sourceIndex`, `sourceTime`, `price`, `calculationValid`.
- **S:** `direction`, `color`, `formationType`, `aOrdinal`, `aSourceIndex`, `aSourceTime`, `aPrice`, `aStopIndex`, `aStopTime`, `aStopEventTime`, `orderDirection`, `orderReactionNumber`, `orderMode`, `orderFirstIndex`, `orderFirstTime`, `orderBreakIndex`, `orderBreakTime`, `orderConfirmationTime`, `orderBoxTop`, `orderBoxTopSourceIndex`, `orderBoxTopSourceTime`, `orderBoxBottom`, `orderBoxBottomSourceIndex`, `orderBoxBottomSourceTime`, `orderStopLevel`, `orderStopSourceIndex`, `orderStopSourceTime`, `resetReactionNumber`, `resetTime`, `sourceIndex`, `sourceTime`, `price`, `decisionIndex`, `decisionTime`, `decisionEventTime`, `calculationValid`.
- **E:** `direction`, `family`, `number`, `parentType`, `parentSourceIndex`, `parentSourceTime`, `parentPrice`, `parentStopIndex`, `parentStopTime`, `parentStopEventTime`, `orderDirection`, `orderReactionNumber`, `orderMode`, `orderCauses`, `orderParentStopCauseTime`, `orderFirstIndex`, `orderFirstTime`, `orderBreakIndex`, `orderBreakTime`, `orderConfirmationTime`, `orderBoxTop`, `orderBoxTopSourceIndex`, `orderBoxTopSourceTime`, `orderBoxBottom`, `orderBoxBottomSourceIndex`, `orderBoxBottomSourceTime`, `orderStopLevel`, `orderStopSourceIndex`, `orderStopSourceTime`, `sourceIndex`, `sourceTime`, `price`, `decisionIndex`, `decisionTime`, `decisionEventTime`.
- **StopAll:** `direction`, `number`, `sourceIndex`, `sourceTime`, `price`, `decisionIndex`, `decisionTime`, `decisionEventTime`, `gateType`, `gateEventTime`, `stoppedBehaviorType`, `stoppedBehaviorKey`, `stoppedBehaviorCount`, `underlyingEFamily`, `underlyingENumber`, `orderDirection`, `orderReactionNumber`, `orderMode`, `orderCauses`, `orderParentStopCauseTime`, `orderFirstIndex`, `orderFirstTime`, `orderBreakIndex`, `orderBreakTime`, `orderConfirmationTime`, `orderBoxTop`, `orderBoxTopSourceIndex`, `orderBoxTopSourceTime`, `orderBoxBottom`, `orderBoxBottomSourceIndex`, `orderBoxBottomSourceTime`, `orderStopLevel`, `orderStopSourceIndex`, `orderStopSourceTime`, `stopIndex`, `stopTime`, `stopEventTime`.
- **OrderAudit:** `direction`, `reactionNumber`, `reactionMode`, `firstIndex`, `firstTime`, `boxTopSourceIndex`, `boxTopSourceTime`, `boxTop`, `boxBottomSourceIndex`, `boxBottomSourceTime`, `boxBottom`, `breakIndex`, `breakTime`, `stopLevel`, `stopSourceIndex`, `stopSourceTime`, `stopHitIndex`, `stopHitTime`, `stopHitEventTime`, `causes`.

### 13.3 Response envelope

The envelope contains `engine`, `version`, `pipelineVersion`, nullable `primaryVersion`, `blueLineVersion`, `aVersion`, `sVersion`, nullable `eVersion` and `stopAllVersion`, enablement booleans, `timeframe`, `actualFrom`, `actualTo`, and `directions`. The runtime telemetry is `timings.phasesMs` and `timings.bridgeTotalMs`. `activeDirection` is added only when a reversal is published within the request horizon. Each calculated direction owns its finalized Reaction/Reset/Blue/A/S/E/StopAll/OrderAudit arrays. Section 13.10 specifies the subsequent verdict annotations.

### 13.4 Optional Bridge Output

`--bridge-output` adds a read-only projection built only from finalized calculation selections and canonical OrderAudit. It may validate a recorded strict event, but it must not search for a substitute trading event or mutate detector/lifecycle state. Physical Order joins use `(FirstIndex, BreakIndex)` and exact accepted causes, never list position.

### 13.4a Bearish primary structures — approved current extension
<!-- PRIMARY-STRUCTURES-BEGIN -->

#### Scope, ownership and terminology

`pipeline/PL_PH_detector.py` owns the newly taught **bearish** Primary-High (`PH`), Primary-Low (`PL`) and **matching behavior leg (`MBL`)** state. `MBLL` / `matching_behavior_leg_low` are superseded training names; a bearish MBL still represents the original leg's minimum Low. The new module consumes finalized calculation-accepted behavior state and the existing accepted physical OrderAudit. It does not repair Reaction/Reset/Order eligibility, invent additional physical Orders, or delegate trading decisions to the Chart or serializer.

**The earlier bullish deferral is superseded by the user's explicit mirror approval.** This subsection retains the bearish specification; Section 13.4b defines its approved bullish counterpart and symmetric fresh regime restart. Both directional References independently contain the same complete current shared Source. The upstream engines and native physical OrderAudit retain their original ownership.

#### Matching setup and first PH gate

1. For a new matching pair, use the latest accepted StopAll as its reference only if its number is at least 3. Every new StopAll clears incomplete matching. A latest StopAll below 3 prevents a new qualification until an eligible reference arrives.
2. At or after that boundary, accept at least two **exact dominant** S/E occurrences under `lifecycle_engine.advance_dominant_behavior`, the same owner/count resolver used by StopAll. S identity is `(S, color)`; E identity is `(E, family, number)`. Shared priority is S Blue < E Blue < S Red < E Red, with the existing higher-E-number rule within one family. A lower-priority intervening occurrence does not replace the owner; a higher-priority owner replacement restarts its count. Use accepted final events: an E/S source belonging to StopAll is not simultaneously an independent matching occurrence, and an invalid calculation event does not count.
3. Freeze the qualifying leg's preceding reference, the second accepted matching occurrence's main source candle and the latest of the three exact decisions (reference and both occurrences). A retrospective source timestamp does not substitute for qualification. A subsequent StopAll does not by itself invalidate an already qualified pair. Keep that pair pending while also evaluating newly qualified legs; an earlier unbroken reference must not block later valid setups.
4. For each pending qualified leg, find its first authoritative RAW `High > reference StopAll main-candle High` strictly after its exact qualification time. A crossing at the same timestamp as qualification does not activate the leg. Equality does not open PH space. **Every activated qualified leg starts an independent cycle**, even while older cycles remain active or their MBLs remain unbroken. An eligible activation freezes an internal candidate leg; it does not yet form a public MBL. Earlier qualification does not block a later setup that crosses first. Its owning calculation candle is the initial PH trigger candle. Activation order follows exact break time, then qualification time, reference source index and second-behavior source index for deterministic ties.
5. Resolve only eligible accepted conceptual Bearish Orders of creation type Order_A or Order_B. The first eligible exact Order stop confirms PH-1; its source and its later confirmation are separate events.

#### Independent cycle ownership and exact shared chronology

The user explicitly superseded the one-global-cycle interpretation. Each qualifying historical reference StopAll and its first exact dominant matching pair can start its own PH-1/PL sequence and immutable MBL. Do not wait for an older MBL to break or an older cycle to finish. New-cycle activation does not cancel, reset or overwrite earlier cycles. PH/PL logical confirmation counters and PH-reset flags remain local to each cycle. Final physical PH numbering is reconciled across these roles by the higher-number precedence rule below. Additional repetitions under the same already-qualified reference do not create extra cycles. Duplicate physical accepted input records cannot manufacture matching counts or duplicate cycle activations.

Accepted historical StopAll/S/E state remains causal evidence and is not retroactively rebuilt. However, a historical StopAll already promoted to a confirmed PH cannot be reused as the reference of a new independent cycle. At the pending strict activation event, reject the entire setup if the reference's exact source index/time is already PH-owned. It must create no checkpoint, PH, PL, MBL or native PH-parent callback. Continue existing valid cycles and unrelated later setups. Final candle ownership remains PH over StopAll. Logical cycles may consume the same canonical physical Order; the native Order ledger remains shared and physically deduplicated. A newly accepted PH-parent cause from one context can legitimately make a physical Order eligible in another context. Sharing does not merge local confirmation states or MBLs; final physical PH names follow the precedence below.

Process activation and confirmed PH/PL transitions in global exact RAW chronology. Prospective per-cycle checkpoints may evaluate future seek/cancellation routes but cannot commit native PH ownership. Commit only the globally earliest confirmed point, then update the shared native audit. A PH commit invalidates every pending prospective decision, including cycles currently waiting without an accepted Order, so a new valid physical Order can wake an older context before its previously projected future cancellation. Never run one cycle through its entire future before beginning another against that future-mutated ledger. Exact activation/decision ties activate contexts first; decision ties retain deterministic activation order. There is no arbitrary cycle count or feedback-loop cap.

`PrimaryPoint.cycle_id` and each cycle's `PrimaryResult.cycle_id` identify the logical context. Aggregate `PrimaryResult.cycles` retains all separate results; internal aggregate highs/lows retain all logical roles in global decision order. Final physical PH ownership is resolved by the primary Engine before Bridge projection. The old aggregate `.mbl` is only an internal first-cycle candidate compatibility view. `formed_matching_legs` owns the complete confirmed MBL collection for the requested horizon. Earliest exact qualification provenance is retained independently of source ordering, including qualified-but-unbroken setups.

#### Final physical PH number precedence

The user's later correction supersedes publishing each local PH counter as a
separate chart label. `PL_PH_detector.resolve_primary_highs` first filters out
roles confirmed after the requested horizon, groups exact physical source
candles, and chooses the largest local number for each candle. Ties use exact
confirmation chronology and deterministic cycle activation order. Confirmed
physical groups follow global decision chronology, including retrospective
source candles; source-candle position cannot reorder a later confirmation.

For a distinct next physical PH whose Decimal High is **strictly greater**
than the preceding finalized PH-n, its final number is at least n+1. Keep a
larger already-qualified local number. Thus a qualifying/reset PH-1 above the
previous PH-n continues as PH-(n+1), while an equal/lower new PH may retain its
local reset number. Coincident roles use one larger number without incrementing
again for each duplicate role. This is an Engine ownership rule, not a Chart
overlap workaround. Keep independent MBLs, PL state, strict crossings, native
Order selection, confirmation events and logical reset eligibility unchanged.

Final PH aliases in native parent-stop and reset-leg provenance use the same
source-to-number mapping. `OrderAuditEngineMixin.reconcile_primary_high_labels`
only reconciles names and duplicate aliases; it cannot move/recreate Orders or
change their physical identity, geometry or chronology. Frozen structure Order
snapshots receive the same alias mapping without mutating their source data.
Final numbering is calculated before the presentation start filter, so hiding
earlier candles cannot restart the visible sequence.


#### MBL formation requires a confirmed PH

The approved prerequisites are cumulative: an accepted StopAll sequence at or
beyond StopAll3, two exact dominant matching behaviors, an eligible strict
reference break, and at least one confirmed PH belonging to that valid cycle.
Qualification and activation alone cannot form an MBL. Another cycle's PH or
a future PH outside the requested horizon cannot confirm this cycle's leg.

The frozen minimum boundary is retained internally as a candidate for existing
Order/cancellation chronology. `PL_PH_detector.formed_matching_legs` promotes
that candidate to the formed output only when the owning cycle's earliest PH
confirmation is within the requested end horizon. Source, price, strict break
and 400-candle cap stay unchanged; PH resets do not generate another MBL.
An already-broken candidate is not made unbroken by later PH confirmation.

PH ownership is committed before any strictly later reference breakout. If a
proposed reference broke earlier, that higher candle would lie in the inclusive
PH-maximum interval and the old reference could not remain its PH extreme
source. Thus activation-time rejection preserves exact chronology without
letting an invalid reference cycle create native Order side effects.

#### Immutable MBL

The MBL is the minimum main-candle Low from the **second matching behavior's source candle through the reference-StopAll breakout candle, inclusive**. Equal minimum values retain the earliest candle in that closed range. Preserve its source identity, Decimal price, reference StopAll, second matching behavior and exact breakout provenance.

There is one immutable candidate **per valid independent cycle**; a cycle exposes its MBL only after its own first PH confirms. Several valid confirmed cycles can expose several MBLs at once. **PH reset does not create another MBL and never recomputes its price or source.** The former training sentence describing a new MBL after PH reset is superseded. Its first subsequent authoritative RAW `Low < MBL.price` is its strict break; equality is not a break.

#### Native Order direction, creation and eligibility

Distinguish **conceptual owner direction** from the native Order's **opposite physical Reaction direction**:

| Structure being confirmed | Conceptual owner / audit group | Native physical `direction` | Native strict Order stop |
|---|---|---|---|
| PH in this bearish market algorithm | `bearish` | `bullish` | `Low < stopLevel` |
| PL in this bearish market algorithm | `bullish` | `bearish` | `High > stopLevel` |

This is the existing native Order contract, not a changed price comparator. The PL teaching's Bullish Reset / LL / opposite Bearish physical Reaction belongs to the **Bullish owner** path. Never reinterpret its conceptual name by swapping its already resolved stop.

- Reuse full-history `prepare_order_audit(detector, 0, final_index, s_detector, accepted_a_sources)`. It merges accepted S/E ledgers, removes rejected A creation causes, deduplicates exact physical `(FirstIndex, BreakIndex)` and applies the established one-physical-Order_A-per-parent-stop cause rule.
- **Order_A** is accepted `parent-stop` provenance. **Order_B** is accepted `reset-leg` provenance. Native physical Reaction **Mode A/B is independent of creation type**; a Mode-B physical Reaction carrying only `parent-stop` is Order_A.
- An unconfirmed structure crossing does **not** manufacture a physical Order or Order_B. The strict stop of an already confirmed PH is a genuine parent-stop event and creates native bearish-owner Order_A through the existing OrderAudit owner, as specified below. Order_B must already satisfy accepted A/S/E/StopAll lifecycle stop ownership, the correct directional Reset, the accepted geometric anchor and strictly extending LL/HH boundary, strict post-Reset boundary break, accepted-A expiry, canonical opposite physical Reaction, confirmation and native strict Order stop.
- Logical initial PH-1 and logical PH-1 following a reset admit accepted Order_A and Order_B. Logical PH-2 and PH-3 admit accepted Order_A. An accepted Order_B can also confirm either point when its physical BoxTop is strictly above the preceding confirmed PH High. Final physical renumbering does not change this Order eligibility or replay the race.
- **Every specified PL, including PL-1, admits both conceptual Bullish Order_A and Order_B.** This supersedes earlier B-only PL-1 teaching. For PL Order_A, the first eligible accepted canonical Bearish physical Reaction after the trigger supplies the direct candidate, even if its Order is still open; a later stopped Order_A must not replace this first valid candidate. Do not substitute an arbitrary unaccepted canonical Reaction; do not label noncanonical order-only geometry as a canonical PL candidate. Continue evaluating all eligible accepted Order_B candidates in the same race.
- **PH consumption gate:** an already accepted native Order is eligible when its exact confirmation is **at or after** the structure crossing. Its physical First may precede that crossing. A joint confirmation/crossing in one finest RAW timestamp is eligible; do not invent an ordering between these compatible same-direction events. An Order confirmed strictly before the new crossing is not admitted by this rule. This applies to initial/reset PH-1 and subsequent PH with their existing creation-type restrictions. **PL keeps its existing gate:** First belongs to the trigger main candle or later, and confirmation is strictly after the crossing. The selected exact Order stop remains strictly after confirmation and the crossing. This consumption gate does not loosen the separate native creation rule for a new Order_A caused by stopping a confirmed PH.
- Choose the earliest eligible **exact stop event**, regardless of creation time, proximity, public Reaction number or A/B type. Retain all accepted creation types on a shared physical identity. Exact Order-stop ties prefer the larger physical First index, then the smaller Break index. Order type gives no tie preference. For the secondary direct-A lock, select the canonical candidate by lower physical First index, earlier confirmation, then lower Break index before testing whether it has stopped. A shared identity with accepted B provenance can still compete on the B route.

#### PH replaces StopAll and owns its subsequent Order_A

Once PH is confirmed, its exact `(source_index, source_time)` candle has final behavior **PH**, not StopAll. Remove that candle from the final accepted/public StopAll collection, including the optional Bridge output, before serialization. A PH confirmed after the requested presentation horizon does not erase a StopAll from an earlier window. Preserve historical StopAll boundaries, identities and sequence-reset evidence used before PH confirmation; final classification does not retroactively rebuild that accepted prefix or renumber historical identities.

Each PH is committed to native OrderAudit immediately after confirmation and before selecting a later structure Order. Its first strictly later authoritative RAW `High > PH.price` is the PH stop. Equality is not a stop. That event creates conceptual bearish **Order_A** from existing native canonical physical Bullish Reaction rules, with First in the stop's main candle or later and confirmation strictly after the exact stop. Skip canonical candidates confirmed at or before the stop and continue to the first eligible canonical candidate. Keep native stop geometry, physical identity, blocked-First eligibility, Decimal values and full creation provenance. An open native Order_A is retained; it does not confirm a new PH until its own strict stop occurs. There is one physical Order_A owner per PH parent-stop cause.

Record `parent-stop` creation with parent `PHn`, its source and exact stop event. Historical StopAll reset maps cannot veto this PH parent or rename it back to StopAll. If an obsolete StopAll cause belongs to the same actual PH stop, only the eligible native PH direct identity can own the transferred cause. Remove that obsolete cause from an ineligible former identity; retain its independent creation causes if any. A fully cause-less physical identity is removed from the native ledger and confirmation index, and affected accepted-order/reuse caches are invalidated.

Independent valid Reset routes retain creation type **Order_B**. Their post-stop owner is PH only when the same source's actual PH stop occurred after PH confirmation. Their geometric anchor owner is PH only when PH was already confirmed at the Reset Reaction's First main timestamp. Earlier roles retain historical StopAll provenance. Reparenting does not change Reset geometry or convert a Reset cause into Order_A. Re-prepare accepted audits after each PH commitment, and revalidate final public behavior references after PH/StopAll ownership resolution.

#### PH continuation through PH3

After confirming PH-1 or PH-2, wait for the first strict `High > PH-n.price`. That main candle opens PH-(n+1). Use the earliest eligible exact Order stop after that gate. The ordinary Order_A path remains eligible. The additional Order_B path requires a strictly higher BoxTop than the previous PH High, with equality excluded. The new PH price is the maximum High from the breakout main candle through the selected Order-stop main candle, including both whole candles; earliest equality owns the source. Source and exact later confirmation remain distinct.

The approved directional regime changes on the first strict stop of a confirmed final physical PH-3. This bounds the normal local progression. Public physical numbering is reconciled across independent cycles and can retain or produce a higher final number. Reversal selection tests final number 3 rather than imposing a blanket numeric cap on the serializer.

#### PH3 stop and bullish regime start

The first authoritative strict `High > confirmed PH3.price` across all independent cycle owners ends the entire bearish regime. Equality does not reverse. The exact selected lower-timeframe event orders this transition against all pending activations and decisions; reversal wins a joint boundary before a later bearish point can commit.

All bearish cycles stop at that transition. Their finalized prefix objects remain historical on the Chart, including stable physical identity and provenance. No later bearish calculation result or active continuation is exposed.

The bridge constructs independent calculation inputs: the bearish prefix ends before the crossing main candle; the bullish suffix includes that complete candle and all subsequent supplied candles. Earlier candles and previous detector/lifecycle/Order state cannot enter the new bullish calculation. Public indexes are translated back to the original supplied-input coordinates. A discovery event must be supported by a freshly calculated historical prefix. A transition beyond the requested presentation horizon cannot replace the current outputs.

Only the first bullish Reaction uses the explicit new-regime bootstrap. The first RED candle from the boundary is eligible without an earlier GREEN; its BoxTop uses the initial GREEN run and FirstRed, or FirstRed alone when the boundary is RED. Its BoxBottom evolves through exact confirmation without applying an earlier-leg/Reset boundary. The new leg-head Low remains available to native Blue calculation. After first confirmation, ordinary same-direction Reset, Blue, A, S, E, StopAll and physical Order rules resume. Section 13.4b now explicitly authorizes the bullish primary calculation and its symmetric bearish restart; that later teaching supersedes the earlier one-direction scope limit.

#### PL-1, PL-2 and PL-3

| PL stage | Required strict trigger | Eligible conceptual Bullish Orders |
|---|---|---|
| PL-1 | first `Low < MBL.price` | accepted Order_A and Order_B |
| PL-2 | after PL-1 confirmation, first `Low < PL-1.price` | accepted Order_A and Order_B |
| PL-3 | after PL-2 confirmation, first `Low < PL-2.price` | accepted Order_A and Order_B |

The strict break of an existing PL is its stop and opens the next PL stage. Each PL price is the minimum Low from **its own trigger main candle through its selected Order-stop main candle, inclusive**. Select the earliest equal-minimum candle. The selected stop confirms the structure; source, trigger and confirmation identities/times remain distinct.

After PH reset and a new PH-1, the next PL remains **previous PL number + 1**. Its trigger is the strict break of the **last PL's Low**, not another break of the already fixed MBL. In particular `PH-1 → PL-1 → new PH-1 → PL-2` is the taught sequence. Do not reset the PL counter when resetting PH.

#### Cancellation and PH reset

1. Before a pending PH is confirmed, a strict MBL break cancels that pending PH and enters the PL path. This applies to PH-1, PH-2, PH-3 and the shared later-PH continuation. A later stop of the cancelled PH's old Order cannot confirm it.
2. A subsequent PL still requires its own previous-PL-Low break; cancellation must not invent that price break when price has only crossed MBL.
3. If PL is pending but no new PL has confirmed since the latest PH, a strict break above that PH's High cancels pending PL and resumes the same PH cycle at the next PH number.
4. Once a PL has confirmed, the next eligible upward PH gate restarts the local confirmation state at **PH-1**, with accepted conceptual Bearish A/B Orders. Its final public number is still subject to higher-number precedence, including strict-price continuation. This applies after an existing PH-1, PH-2 or later PH. The PH range again starts at that new upward breakout, while the MBL remains unchanged and PL numbering survives.
5. Use the finest supplied RAW chronology for competing boundaries and Order stops. If opposing events occupy exactly the same authoritative RAW timestamp and their order is unresolvable, report `ambiguous-raw-boundary-order` rather than inventing an intrabar OHLC path or type priority.

#### After strict break of PL-3

The latest supplied formal algorithm defines another native conceptual Bullish Order_A search from the first valid Bearish physical Reaction and continued eligible Order_B evaluation after strict `Low < PL-3.price`. **It does not define PL-4 formation.** Preserve these eligible orders as post-PL3 evidence, but do not create a fourth PL from them. An eligible subsequent upward PH reset remains a separate taught transition. Earlier generic counting language must not override this later explicit PL-4 boundary.

#### Full-history calculation and additive public contract

The complete supplied RAW means the authoritative input stream: the existing selected-range HTTP route can supply only the selected candle buckets, while the complete-source route supplies the original file. This feature preserves that transport scope. Calculate accepted matching, MBL, structure state and native Order candidates on that complete supplied stream; apply the presentation window only after calculation. Calculation Source identity includes the new module so a stale cached result cannot silently omit its output. Existing reaction, reset, Blue, A, S, E, StopAll and OrderAudit arrays retain their original ownership and serialization.

The bearish group adds `primaryHighs`, `primaryLows`, `matchingBehaviorLegs`, `primaryStatus`, `primaryCycles` and `postPL3Orders`; the envelope adds `primaryVersion`. Prices remain Decimal strings; public times use the existing Tehran-local epoch conversion.

- **Primary point:** stable `id`, owning `cycleId`, market `direction`, `kind`, final `number`, `sourceIndex/sourceTime/price`, `triggerIndex/triggerTime/triggerEventTime`, `decisionIndex/decisionTime/decisionEventTime`, and the selected native `order`.
- **Selected Order / post-PL3 Order:** conceptual `ownerDirection` and opposite physical `direction`; `reactionNumber`, physical `firstIndex/firstTime`, `breakIndex/breakTime`, `confirmationEventTime`, `stopLevel`, `stopSourceIndex/stopSourceTime`, `stopHitIndex/stopHitTime/stopHitEventTime`, accepted creation-kind `causes`, readable creation `types`, native `reactionMode`, isolated complete `auditCauses`, and box geometry. Stable physical identity and the creation-type/Reaction-Mode distinction must survive projection.
- **MBL:** stable `id`, additive `cycleId`, `direction`, `sourceIndex/sourceTime/price`, `referenceStopAllIndex`, `secondBehaviorIndex`, `triggerIndex/triggerTime/triggerEventTime`, earliest owning-PH `confirmationIndex/confirmationTime/confirmationEventTime`, nullable `stopIndex/stopTime/stopEventTime`, and `capTime` for 400 subsequent analysis candles. A future confirmation or crossing beyond the presentation horizon must not be presented as already confirmed inside the window.
- **Status:** explicit waiting state, unresolved authoritative RAW ordering, or `post-pl3-orders-only`. A missing valid Order cannot be replaced with a provisional point.

The Section 13.5 AST index and Section 16 exact Source provide complete current dataclass fields, function contracts and serializer implementation; they are regenerated after Source edits.


`primaryCycles` contains each activated context's stable `id`, direction, final supplied-stream status, reference/second-behavior source indexes, trigger index/times, and presentation-selected logical high/low counts. `highIds` joins each context to its final physical PH objects; a PH shared by several contexts is published once and exposes all participating `cycleIds`. Cycles activated beyond the requested end are omitted. Top-level `primaryStatus` belongs to the latest visible cycle; before any visible activation, exact qualification provenance determines waiting-for-matching-behaviors versus waiting-for-stopall-break. Per-cycle statuses describe the complete supplied calculation, not reconstructed snapshots of every earlier lifecycle instant.

A physical PH keeps the ID of its earliest confirmed logical role, with deterministic activation-order ties; first-cycle legacy IDs are preserved. An additional-cycle origin includes its cycle identity. A later winning role or final number change must not change that ID and lose Hide/Appearance settings. `PrimaryPoint.identity_source` separates physical identity provenance from the winning semantic role. Logical cycle memberships remain available even though coincident PH roles no longer create overprinted labels. MBL IDs retain reference/second-source identity and all legs are serialized. Post-PL3 logical Order uses include cycleId; shared physical identity is not manufactured a second time.

#### Chart presentation and settings

The Chart receives final calculation truth. It never reconstructs matching, crossings, Orders or structure numbering.

| Market direction | PH marker / label | PL marker / label |
|---|---|---|
| Bearish | downward double chevron above candle; label above marker | filled circle below candle; label below marker |
| Bullish | green filled circle above candle; label above marker | pink upward double chevron below candle; label below marker |

Default arrow extent and label font are `12px`. Colors follow point kind: PH is green `#056656`; PL is pink `#ec407a`. Both bearish PL and bullish PH circles default to radius `4px` (diameter `8px`) and opacity `100%`; circle label font is `12px` in the point's color. Explicit marker/radius/appearance customization remains supported. Candle-to-nearest-marker-edge gap is `12px`; marker-to-visible-label-edge gap is `10px`. Text is `PH-n` / `PL-n` using the finalized number; repeated PH-1 after reset retains a distinct stable object identity.

MBL uses the finalized source/price and strict end event, dotted line size `2`, color `#b22833`, and centered `MBL` text at `9px`, with a label gap in the line. Display at most 400 subsequent actual analysis candles. An earlier strict break ends the line at that candle. The cap applies equally to the latest and all earlier MBLs; no later break extends a line beyond the cap. At a bearish-to-bullish handoff, historical drawing is bounded by the explicit calculation end. A PH reset does not itself create such a newer MBL. Source `capTime` is the timestamp at source index + 400 when that actual candle is available. For shorter supplied input, extrapolate the remaining analysis slots from the last available main candle. A stopped regime clamps the cap to its exclusive calculation boundary. Chart uses the supplied end or the legacy time-based display fallback when an older payload lacks it. Chart does not search raw prices for a substitute end.

Configure contains a PH/PL section with marker/label visibility switches for PH, PL and MBL. Appearance exposes colors, marker/label sizes, circle opacity/radius, gaps and line style/width using the same persistence and reset patterns as existing controls. Per-object hide/unhide uses the existing object tree and stable IDs. All stated appearance values are defaults, not fixed calculation rules.

The Info panel reports finalized PH, PL and MBL counts and the Engine's current primary status. A zero count remains a valid result and its waiting state is shown explicitly. Before reusing an in-browser result for appearance changes, the Chart checks the current opaque calculation-Source fingerprint through the local server. Missing, failed or changed Source identity requires the normal calculation request. This identity check does not independently validate RAW bytes or infer trading state.

#### Directional transition presentation

Draw a green dashed vertical line across the full plot height at the finalized bullish-start main candle, irrespective of that candle's market color. Render a clean green upward zigzag arrow at the actual 50th calculation candle counting the start as candle 1 (offset 49). The icon is 28 by 28 CSS pixels with a stronger stroke and a filled arrowhead; its bottom edge is exactly 100 CSS pixels above that candle's High, horizontally centered on that candle. Pan/zoom changes anchors while preserving screen-pixel dimensions and clearance. If the 50th actual candle is absent, retain the boundary line and omit the icon.

At a bearish start, draw the symmetric red dashed full-height boundary and a red downward zigzag at the actual 50th calculation candle counting the start as 1. Its size is `28 × 28` CSS pixels; its top edge is exactly `100px` below that candle's Low, horizontally centered on it. Preserve pixel dimensions and clearance during pan/zoom; omit the icon when the target actual candle is absent.

The Engine supplies `trendTransitions` on the incoming direction with stable identity, direction/previousDirection, source and exact event time, stopped PH3 or PL3 provenance, and nullable target-candle High or Low. The Chart does not search OHLC for a trend event. Historical paint, hit testing and selection all respect the owning segment's end bound; new segment anchors come from fresh finalized input and user presentation offsets may move drawings; Section 13.4b specifies the complete repeated-regime contract.

A historical full-October USOIL 5s RAW acceptance run at 30s recorded bearish PH1 at `2026-10-07 00:13:30`, PH2 at `03:55:30` and PH3 at `04:47:00`, with PH3 High `90.573`. Its strict stop starts the bullish context at `16:57:30`. FirstRed/BoxTop are `16:57:30`, BoxBottom is `16:59:30` and Break is `17:00:30`. The 50th candle is `17:22:00`. These are bounded acceptance anchors, never production special cases.

#### Bounded authoritative-RAW acceptance example

The user-provided XAUUSD 5s RAW example, calculated at 30 seconds, has reference StopAll6 at `2026-09-29 17:52:00`, High `4175.180`, and matching S Red sources `18:28:00` and `20:06:30`. Its first strict reference breakout belongs to main candle `22:09:00`. The MBL is main source `21:28:00`, price `4142.445`.

The earliest accepted eligible bearish-owner Order stop is physical Bullish identity `(3045, 3046)`, First `23:07:00`, confirmation `23:07:50`, stop level `4170.765`, exact stop `23:12:15` in main candle `23:12:00`. This physical Reaction has Mode B but accepted parent-stop creation provenance, hence creation type Order_A. Its A cause source is `22:59:30`, stopped at `23:05:50`. The inclusive PH range `22:09:00 .. 23:12:00` has maximum `4175.755`, main source `22:10:00`. Physical Bullish Order First `22:23:30` is accepted but stops later and does not win this race.

This is bounded acceptance evidence of the general accepted-audit, chronological race and inclusive-extrema rules. None of these timestamps, indices, prices or RAW names is a production branch or universal market rule.

#### Historical USOIL joint-confirmation acceptance example

On the user-selected USOIL RAW chart identity `107aa8c4-ca51-47b7-925f-401df4200f0c`, supplied from October 1 through October 23 and calculated bearish at 30 seconds, reference StopAll5 is `2026-10-06 08:21:00`, High `90.028`. The first two matching S Red sources after it are `11:45:30` and `14:37:00`; repeating the same source in a written list does not create a second physical behavior. The immutable MBL remains `2026-10-06 15:50:30`, price `86.867`.

The reference breaks strictly at `2026-10-07 00:13:45`, belonging to main candle `00:13:30`. The accepted bearish-owner physical Bullish Order has First `00:10:30`, exact confirmation `00:13:45`, native stop `89.803`, and exact stop `01:31:00`. It has physical Reaction Mode B but accepted creation type Order_A. The user explicitly confirmed that this older-First, jointly confirmed Order validates PH-1. The inclusive whole-candle range has maximum `90.034` on `00:13:30`, so that candle owns PH-1; `01:31:00` is its confirmation, not its source. That older run recorded an unbroken-display cap at `16:40:30` under the superseded 100-candle setting. Current display uses the 400-candle rule above.

The previous gate required First at or after the crossing candle and confirmation strictly later than the crossing; it wrongly excluded this accepted Order and selected `03:55:30` as the first PH source. The general PH confirmation gate above corrects that earliest divergence. These timestamps, prices and the chart identity are bounded acceptance evidence only; production contains no corresponding special case.

#### Historical later-cycle acceptance examples

The following examples predate the approved global PH3 reversal. They retain historical evidence of local-cycle/ownership behavior; later October cycles and PH4+ are not current full-month acceptance expectations once the October 7 PH3 stops.

#### Historical independent USOIL October 22 example

In the **same full** USOIL107AA8C4 calculation, reference StopAll9 is `2026-10-22 12:05:30`, High `100.068`; matching S Red sources are `13:20:00` and `15:42:00`. Their qualified leg strictly breaks at `21:20:35`, belonging to main candle `21:20:30`. Its independent PH-1 source is `21:20:30`, High `100.149`, confirmed at `21:47:25`. Its own immutable MBL is `18:56:30`, price `97.883`.

This cycle must coexist with the October6/7 cycle above, whose MBL remains unbroken and whose numbering continues locally. The October22 PH source is no longer a public StopAll10. Both independent PH-1 objects and both MBLs must have distinct object identities and support independent hide/unhide. MBL remains dotted red, with a 100-analysis-candle unbroken cap and 9px default label; older legs use their capped presentation when newer cycles exist. None of these bounded fixture dates/prices/chart identities participates in production conditionals.


#### Historical USOIL PH number-priority example

The later explicit invalid-cycle rule supersedes the previous PH-5 example
at October8 11:25:30: that point depended on a PH-owned StopAll reference and
its whole cycle is invalid. After recalculation, October7 17:09 remains PH-4;
October8 12:30 is PH-5 and14:21 is PH-6. The general physical number-precedence
rule remains unchanged; invalid cycle roles no longer participate in it.

#### Historical USOIL rejected MBL examples

Reject the candidate MBL source `2026-10-07 11:51:30`: reference index8894 is
the PH-3 source at04:47, confirmed04:55:05 before its would-be activation.
Reject candidate source `2026-10-08 18:01:00`: reference index12832 is an
already-confirmed PH source at14:41:30. Neither historical StopAll may seed a
new independent cycle. These identities are test evidence only, not production
conditions. The original acceptance run retained the October 6 leg at 15:50:30 and a separately confirmed October 22 leg at 18:56:30 under its then-active regime boundaries. The October 22 object is historical evidence and is not a current full-range expectation after a prior regime reversal.

<!-- PRIMARY-STRUCTURES-END -->

### 13.4b Bullish primary mirror and alternating regimes — approved current extension
<!-- PRIMARY-BULLISH-MIRROR-BEGIN -->

#### Scope and exact transformation

The user has approved the bullish PL/PH/MBL mirror and subsequent bearish restart. This section extends, rather than removes, the bearish rules in Section 13.4a. `detect_bullish` executes that shared primary state machine with exact Decimal sign/High-Low reflection, then restores real market prices, kinds and directions. Reflection never reverses time or changes market candle colors, S/E Red/Blue families, dominant-owner priority, canonical physical Order identity, accepted cause structure or chronological tie rules. Native Order selection and parent callbacks see the original market coordinates. Exact Decimal negation preserves long input lexemes without context rounding.

| Primary contract | Bullish regime | Bearish regime |
|---|---|---|
| Main confirmed structure | PL | PH |
| Activated reference break | strict `Low < reference StopAll Low` | strict `High > reference StopAll High` |
| Immutable MBL extreme | maximum main-candle High | minimum main-candle Low |
| MBL break | strict `High > MBL.price` | strict `Low < MBL.price` |
| Main continuation / stop | strict `Low < confirmed PL.price` | strict `High > confirmed PH.price` |
| Opposite confirmed structure | PH | PL |
| Regime reversal | first strict stop of a confirmed final PL3 | first strict stop of a confirmed final PH3 |

#### Matching, independent cycles and frozen MBL

1. Require StopAll3 or later and the same exact dominant matching S/E pair, with the same accepted-event exclusions, decision-time qualification, causal historical reference, duplicate suppression and deterministic activation ordering as Section 13.4a. Do not swap behavior families or aggregate unlike identities.
2. The first strict authoritative RAW `Low < reference StopAll main-candle Low` activates a separate bullish cycle. Equality does not activate it. A reference already promoted to a confirmed PL is ineligible to seed another cycle; reject that whole pending setup without native parent side effects.
3. Freeze the MBL candidate at the maximum main-candle High from the second matching behavior source through the reference-break main candle, both inclusive. Earliest equal maximum owns the source. Publish that cycle's candidate only after its own first PL confirmation within the requested horizon. No other cycle or future point can confirm it.
4. Keep the frozen source, price and provenance for the cycle's entire lifetime. A PL reset does not create a new MBL. Its first later strict `High > MBL.price` remains its break even if it occurred before the first PL confirmation. Distinct qualified cycles remain independent and may share one accepted physical Order without duplicating that Order.
5. Globally interleave activations and confirmed points in exact RAW chronology. A committed primary PL updates the shared native audit and invalidates pending prospective decisions. Reversal wins a joint boundary; activation ties precede point commitment and remaining point ties retain deterministic activation order. Opposing RAW events with no resolvable ordering report `ambiguous-raw-boundary-order`.

#### Bullish Order gates, confirmation and extrema

| Bullish point | Conceptual Order owner | Opposite physical Reaction | Accepted creation types | Structure consumption gate |
|---|---|---|---|---|
| Initial/reset local PL1 | `bullish` | `bearish` | Order_A and Order_B | confirmation at or after crossing; older First allowed |
| Local PL2 / PL3 | `bullish` | `bearish` | Order_A, or Order_B with BoxBottom strictly below the previous PL Low | confirmation at or after crossing; older First allowed |
| PH1 / PH2 / PH3 | `bearish` | `bullish` | Order_A and Order_B | First in trigger main candle or later; confirmation strictly after crossing |

Conceptual bullish Orders use native physical bearish `High > stopLevel`; conceptual bearish Orders use native physical bullish `Low < stopLevel`. Creation type is accepted parent-stop/reset-leg provenance, independent of physical Reaction Mode A/B. An Order stop must be strictly after both its confirmation and the structure crossing. The earliest exact eligible stop wins; exact stop ties prefer larger FirstIndex, then BreakIndex, with no A/B preference. For opposite PH, preserve canonical Reaction eligibility and the first valid direct Order_A lock: an open first eligible direct A cannot be replaced by a later direct A, while accepted B candidates still race normally.

Confirm each PL at the minimum Low over the whole trigger main candle through the whole winning Order-stop main candle, inclusive. Confirm each PH at the maximum High over its own corresponding inclusive interval. Earliest equal extrema retain the source. Trigger, source and exact later confirmation remain distinct. No unconfirmed crossing manufactures a native Order.

#### Continuation, cancellation and final physical PL ownership

After confirmed PL1 or PL2, the first strict break of that PL Low opens the next local PL stage. The ordinary Order_A path and each qualifying Order_B compete by earliest exact stop. An Order_B whose BoxBottom equals the previous PL Low does not qualify. Before a pending PL confirms, an MBL High break cancels it and enters the PH path. If an earlier PH exists, a later PH still requires its own preceding PH High break; cancellation alone cannot invent that crossing.

PH1 opens at the first strict `High > MBL.price`; subsequent PH stages require the first strict break above the last PH High after its confirmation. PH numbering survives a PL reset. If PH is pending and no new PH has confirmed since the latest PL, strict loss of that PL Low cancels the pending PH and resumes the next local PL. A confirmed PH resets local PL confirmation to PL1 at the next valid downward gate with A/B eligibility; the original MBL and PH counter persist.

`resolve_primary_lows` reconciles final physical PL roles before presentation filtering. Coincident roles publish one greatest local number; chronological ties retain the same deterministic identity-source rule as PH. A distinct next confirmed physical PL strictly lower than the preceding final PL-n takes at least n+1, retaining a larger qualified local number. Equal/higher price does not force that continuation. Final renumbering preserves native Order eligibility, exact events, logical cycle membership and stable object IDs. Native PL aliases and frozen selected-Order causes use that same final source-to-number map without rediscovering Orders.

The first strict stop of any confirmed final physical PL-3 ends all bullish cycles, as described below. Separate this local continuation/reversal boundary from final public numbering across independent cycles, which can reconcile a higher displayed number. Opposite PH stops after PH3 retain eligible conceptual bearish Order_A/B evidence as `postPH3Orders`, without forming PH4. This evidence does not override a PL3 regime reversal.

#### Confirmed PL parent and StopAll ownership

A confirmed primary PL owns its exact source candle in final output and replaces that candle's public StopAll, including optional Bridge output. Preserve the historical StopAll boundaries required before PL confirmation; a future PL cannot erase an earlier presentation horizon.

Commit each primary PL immediately to native `register_primary_low`. Its first strictly later authoritative RAW `Low < PL.price` is a genuine bullish-owner parent stop. It creates native Order_A from the first eligible canonical physical bearish Reaction, with First in the stop-owning main candle or later and confirmation strictly after the exact stop. Preserve one physical owner per parent-stop cause, native stop geometry and identity. Open Orders remain in the accepted ledger without provisionally confirming a point.

Use `PLn` for the parent-stop cause and eligible Reset-leg post-stop/anchor aliases under the same exact confirmation-time checks as PH. Transfer an obsolete StopAll direct cause only to the eligible native identity; retain other independent causes, remove cause-less identities and their confirmation-index entries, and invalidate affected reuse caches. A Reset-leg remains Order_B. Final PL relabeling changes aliases only, never physical geometry or chronology.

#### Fresh alternating directional regimes

The first authoritative strict `Low < confirmed final PL3.price` begins bearish calculation; equality does not reverse. The existing PH3 High stop begins bullish calculation. Across each regime's independent cycles select the earliest exact eligible primary-3 stop. All cycles in the stopped direction end there, with no later active continuation.

Recalculate the stopped regime from its physically independent prefix ending before the crossing main candle. That prefix must independently support the confirmed stopped final primary-3 source and level; otherwise fail rather than publish an unsupported transition. Start the opposite direction from the complete crossing main candle, with new normalized candles, lower chronology, detectors, lifecycle and Order state. Carry no earlier candle or previous regime state. Repeat this fresh prefix/suffix process whenever the new regime subsequently reverses. Time always advances and public indexes translate back to the original supplied-input coordinates.

Only the first Reaction of each newly started direction uses the bootstrap exception. Bullish accepts FirstRed without earlier GREEN and confirms strict `High > BoxTop`; bearish accepts FirstGreen, including a market Doji, without earlier RED and confirms strict `Low < BoxBottom`. The fixed confirmation edge spans the initial context run and First, or First alone when it starts at the boundary; its opposite edge evolves through exact confirmation. No prior-leg/Reset boundary invalidates that first search. Preserve the boundary leg-head Low/High for downstream native calculation. Ordinary Reset and all downstream rules resume immediately after first confirmation.

An explicit bullish request starts bullish primary calculation; `both` retains the existing initial bearish precedence. Repeated transitions alternate from that initial regime. Disabling primary calculation preserves the existing directional behavior. A transition after the requested presentation horizon does not replace current output.

#### Additive public contract and historical presentation

Both directions expose finalized `primaryHighs`, `primaryLows`, `matchingBehaviorLegs`, `primaryStatus` and `primaryCycles`. Bearish retains `postPL3Orders`; bullish exposes `postPH3Orders` with conceptual bearish owner and physical bullish direction. Primary prices remain Decimal strings. Bullish primary PL objects expose participating `cycleIds`; each bullish cycle joins them through `lowIds`, matching bearish `highIds`. Absolute input offsets participate in stable point/cycle/MBL identities, so a later same-direction regime cannot reuse an earlier regime's IDs.

Each incoming direction receives Engine-finalized `trendTransitions` with stable `id`, `direction`, `previousDirection`, boundary `sourceIndex/sourceTime`, exact `eventTime` and stopped `level`. Bullish-start provenance uses `phNumber/phSourceIndex/phSourceTime`; bearish-start provenance uses the corresponding `pl*` fields. `iconCandleIndex/iconCandleTime` target the actual 50th calculation candle counting the boundary as 1. Bullish exposes `iconCandleHigh`; bearish exposes `iconCandleLow`. Target fields are null when that actual candle does not exist. When a reversal is published within the requested horizon, the envelope's `activeDirection` identifies the latest published regime. Without a published reversal the field is absent.

Both trend-start icons remain `28 × 28` CSS pixels. The bullish icon's bottom edge is exactly `100px` above its target candle's High; the bearish icon's top edge is exactly `100px` below its target candle's Low. These are screen-pixel clearances during pan/zoom and do not change the actual-candle-50 target. The latest explicit user instruction restores `100px` clearance and supersedes the earlier `500px` clarification. Current automatic calculation remains unchanged; Auto/Manual controls are not part of this approved change. Historical verification retains the geometry tested at that time.

Historical groups carry `calculationEndTime`; later groups carry `calculationStartTime/calculationStartIndex`. A direction occurring more than once exposes flat chronological `calculationSegments`, each a complete same-direction finalized payload without nested segments. Aggregate list fields concatenate those finalized collections for counts/object inspection, optional Bridge lists concatenate likewise, and scalar state follows the latest same-direction segment. A single segment retains the legacy group shape. Chart renders each segment independently and applies each historical segment's end bound consistently to paint, hit testing and selection. New segment anchors come from fresh finalized input; user presentation offsets may move drawings. The Chart cannot infer a crossing from OHLC. Stable IDs preserve per-object Hide/Appearance state.

MBL retains the red dotted line, fixed source/price, 9px label and maximum 400 actual analysis candles after its source, ending earlier at its strict break or historical regime end. `capTime` and explicit regime bounds own presentation; Chart cannot calculate a replacement trading end. The actual-bar target/cap chronology survives data gaps.

<!-- PRIMARY-BULLISH-MIRROR-END -->
