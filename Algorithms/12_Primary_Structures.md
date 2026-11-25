# PS — Primary structures (PL, PH and MBL)

Qualify StopAll >=3 by at least two matching dominant S/E exact identities; qualification time is maximum decision. Independent qualified seeds may activate on strict crossing reference High (bearish) or Low (bullish). MBL is immutable min Low (bearish) or max High (bullish) over complete main interval second matching source through gate inclusive; visible only after the first confirmed primary in the same cycle, extension cap 400 main candles. Globally interleave independent cycles by exact decisions. A committed primary updates shared native ledger and clears pending proposals. Primary gate permits confirmation >= event even with older First; secondary requires First >= gate main and confirmation > event, canonical positive geometry. Stop after confirmation and event. Continuing primary uses parent-stop or strict reset-leg extension. Order race earliest stop, later First then Break. Respect cancellation/ambiguous exact RAW tie. No secondary number 4. After 3 only eligible Orders. Highest physical local number wins, strict extension at least previous+1, horizon filter; promote same-source StopAll only after confirmed. Primary3 strict stop triggers a fresh opposite regime from the entire boundary candle. Bullish reflection preserves native families, time and price representation. This is not a complete branch-level reconstruction.

Supplementary material below is the English semantic prose of the existing synchronized references, pinned to 466eb875070f02cd0dbfb105033422bbe2fd8c70. It is not a fresh branch-level proof. Exact production-source appendices are excluded. Historical acceptance examples remain historical.

## 2. Execution, ownership and time model

### 2.1 Calculation stages and inputs

The bridge constructs ordered lower-timeframe RAW candles and analysis-timeframe main candles. It runs the normal Reaction/Reset, Blue, A, S, E, StopAll and physical OrderAudit owners. It passes full-history accepted S/E/StopAll candidates and the accepted native audit from both conceptual directions to the primary detector. The directional primary owner is the requested calculation direction. A `both` request seeds the primary calculation on the bearish direction under the current bridge dispatch rule. The normal directional setup requires the primary module, an enabled S/E pipeline and a lifecycle Engine.

The successive boundaries are calculation acceptance, primary cycle formation, final source ownership, serialization, independent verdict annotation, and rendering. An owning component can change its own result. Chart renders the finalized price, time, number, provenance and verdict supplied by Engine. Vite passes the actual RAW duration and the analysis timeframe to Bridge. FARAZ supplies input candles and is not the owner of trading behavior.

### 2.2 Representations and chronological comparisons

| Item | Representation and rule |
|---|---|
| RAW row | JSON object with epoch seconds in `time` and `open`, `high`, `low`, `close`. Supply chronological rows and the actual RAW duration. Prices use the decimal lexemes in JSON. |
| Main candle | Analysis-timeframe bucket. Retain the first Open, maximum High, minimum Low and last Close. The bucket start is its candle timestamp. Main-candle position refers to the actual sequence of available buckets. |
| Lower event | Exact available RAW time. Price crossings use the lower event, even when multiple events fall inside one main candle. A main timestamp labels the containing bucket. |
| Trigger | Main candle and exact RAW event that open a structure candidate. |
| Source | Main candle holding the chosen extreme in its full allowed interval. Its position can precede the exact decision. |
| Decision | Exact stop of the winning accepted Order and its containing main candle. Qualification and final visibility use their own decision requirements. |
| Level | Internally Decimal. Serialize price and box/stop levels as strings. Thresholds use strict comparisons except for the explicitly inclusive confirmation and interval boundaries. |
| Time serialization | Public input/output seconds are Unix epochs. Bridge converts internal Tehran-local times using the Tehran timezone database. |

References to `sourceTime` in the verdict algorithm mean chronological source-candle time. References to the Order race, reversal, or competing crossings mean exact decision or lower RAW time. If the finest available RAW timestamp contains two opposing actions whose order would determine the structure, the primary detector can report `ambiguous-raw-boundary-order`. It does not use an invented order within that RAW candle. Where one exact timestamp is explicitly eligible for compatible actions, use the specified tie rule.

### 2.3 Direction mapping

| Rule | Bullish market | Bearish market |
|---|---|---|
| Directional primary point | PL | PH |
| Initial StopAll reference threshold | First eligible `Low < StopAll-candle Low` | First eligible `High > StopAll-candle High` |
| Immutable MBL | Maximum High | Minimum Low |
| Strict MBL break | `High > MBL.price` | `Low < MBL.price` |
| Main point stop | `Low < confirmed PL.price` | `High > confirmed PH.price` |
| Main continuation Order_B gate | `BoxBottom < preceding PL.price` | `BoxTop > preceding PH.price` |
| Opposite structure in that cycle | PH | PL |
| Conceptual Order owner for the directional point | bullish | bearish |
| Physical native Order reaction for the directional point | bearish | bullish |
| Native Order stop for the directional point | `High > Order.stopLevel` | `Low < Order.stopLevel` |
| Regime change | First eligible strict stop of finalized PL-3 starts bearish | First eligible strict stop of finalized PH-3 starts bullish |

`detect_bullish` uses the shared primary calculation with exact Decimal reflection `M(O,H,L,C)=(-O,-L,-H,-C)`. The reflected views swap High and Low, and swap first-greater and first-less index queries. Reflect the Order stop level and the box edges with `reflected_top = -original_bottom` and `reflected_bottom = -original_top`. Restore physical price, point kind, direction and projected cycle identity at the output boundary. Use exact sign changes, such as Decimal `copy_negate`, even when the active Decimal context has limited precision.

Timestamps, chronology, indexes, identity/provenance and already accepted native Order causes keep their meaning across reflection. Red and Blue in S/E are behavior families in both directions. The native Order resolver and the primary-registration callback run in original market coordinates. Market candle color uses the normal Open/Close classification, including doji.

## 3. Matching qualification and independent primary cycles

### 3.1 Exact accepted matching behavior

1. Build the event stream from accepted native StopAll and eligible S/E rows in source order. On one source candle, a StopAll donor cannot supply another independent S/E occurrence. Rows with `calculation_valid=False` are excluded from the S/E matching input. Duplicate physical events cannot supply a second occurrence.
2. A published native StopAll with number at least 3 replaces the current potential reference. A subsequent native StopAll below 3 clears that reference for the next matching setup. An already-qualified pair remains pending on its frozen reference.
3. For each candidate reference, use the first two accepted occurrences of the current exact dominant owner. An S identity is kind and color. An E identity is kind, family and number. Dominance is `S Blue < E Blue < S Red < E Red`, with larger E numbers winning within the same E family. A smaller intervening S/E leaves the owner intact. A larger replacement becomes the new owner at count 1. Count exactly matching identities and apply the same native owner reducer as StopAll. Primary matching consumes native behavior identities. It does not consult T/F verdicts.
4. Freeze the reference StopAll, the second matching behavior's source, and the exact qualification time. Qualification time is the maximum of the reference decision and both selected matching decisions. The native source candle of the second behavior can be earlier than qualification. Additional matching occurrences under the same already-qualified reference do not start extra cycles.
5. Scan from the first RAW event strictly after qualification for the strict reference threshold in the direction matrix. Use the reference candle's actual directional extreme, with equality excluded. No reference crossing means the seed remains waiting.

### 3.2 Activation and global ordering

Each qualifying reference and exact second behavior identify one independent cycle. A later seed may activate first if its crossing occurs first. No established or pending cycle blocks another valid seed by merely existing. Order activations by exact crossing, then exact qualification, reference source index, and second-behavior source index. Deduplicate the physical pair. Before accepting a pending activation, check whether its reference source index/time is already owned by an earlier confirmed directional primary. Reject such a seed and leave the existing cycles intact.

The detector maintains committed checkpoints plus prospective next-point proposals for active cycles. Compare the next activation, the earliest proposed decision, and the earliest confirmed reversal across the entire direction:

1. An eligible reversal at or before competing exact events wins and closes that regime.
2. At a shared activation/decision time, process activation first. Exact decision ties keep deterministic activation order.
3. Commit the earliest point. A directional primary commitment registers native OrderAudit ownership and invalidates outstanding proposals, including proposals waiting without a candidate. Reconsider the remaining cycles with the now-current shared native audit.

Cycles can consume the same accepted physical Order. Native audit identity remains physically deduplicated. Their local primary/opposite counters and MBLs remain independent. A physical candle can accumulate multiple logical roles before the final directional primary ownership pass.

## 4. MBL formation, break and display horizon

1. At cycle activation, measure the interval of whole main candles from the second matching behavior's source through the reference-break candle, including both endpoints. Take maximum High in bullish and minimum Low in bearish. If the winning extreme occurs on more than one candle, use the earliest candle. Freeze the time, level, reference, second source, and exact activation event.
2. This is initially a candidate leg. A leg becomes part of public output once its own first directional primary confirms within the requested end horizon. An opposite point, another cycle's primary, or a future confirmation does not publish the leg.
3. Starting strictly after activation, track the first strict MBL break using RAW. Keep the first exact event and its main index. An MBL can already be broken by the time it becomes public. A local primary reset or further matching leaves the frozen MBL in that cycle unchanged.
4. Public `stopIndex`, `stopTime` and `stopEventTime` are null until the requested main-candle horizon contains the break. Bridge supplies `capTime` from the actual main candle at source index + 400 when available. When that index does not yet exist, it extrapolates from the last main timestamp by the remaining number of analysis periods. A stopped regime clamps the cap at the reversal boundary. Chart ends the line at the earliest applicable end and does not search for a replacement price crossing.
5. Several formed legs may coexist. IDs use direction plus the reference and second source indexes. First-cycle compatibility access through the internal aggregate `.mbl` is not a substitute for the formed-leg collection.

## 5. Native Order selection and point confirmation

### 5.1 Native ownership, creation and eligibility

The Order owner for PH is conceptual bearish. The Order owner for PL is conceptual bullish. The opposite physical Reaction direction is serialized separately. `Order_A` carries accepted `parent-stop` provenance. `Order_B` carries accepted `reset-leg` provenance. A physical reaction can be Mode A or Mode B independently of these causes. An accepted physical identity can carry both types. The full native audit rules in Appendix A and the embedded native owners determine creation and acceptance. A structure threshold crossing does not create a new arbitrary physical Order.

| Point being confirmed | Eligible creation routes | Consumption gate at the structure crossing |
|---|---|---|
| Initial or reset directional PL-1/PH-1 | Native A and B | Native confirmation at or after the exact crossing. An earlier physical First is eligible if the Order meets this gate. |
| Same-cycle directional PL-2/3 or PH-2/3 | Native parent-stop A, or accepted reset-leg B whose directional box edge strictly extends the previous confirmed primary price | Same directional confirmation gate as local 1. In bullish compare physical BoxBottom with previous PL Low. In bearish compare physical BoxTop with previous PH High. Equality does not qualify the added B route. |
| Opposite PH in bullish or PL in bearish | Native A and B | Physical First index at or after the trigger main index, native confirmation strictly after the exact crossing, and canonical accepted Reaction identity. |

For the opposite structure, find the first acceptable direct A by physical First index, exact confirmation and Break index. An open first direct A remains the direct candidate. A later direct-only A cannot supersede it simply because the later A has stopped. All accepted eligible B candidates still compete, including an identity carrying both types. For the directional continuation, the ordinary accepted parent-stop route and each qualifying reset-leg route are in the same race. An already stopped or open accepted Order is represented by its actual native audit state, with all independent causes.

### 5.2 Race and extrema

A winning Order has an actual native stop strictly after its confirmation and the point's exact trigger. Among eligible stops choose the earliest exact time. Exact stop ties prefer the larger physical First index, then the smaller Break index. A/B creation type does not determine a tie winner. Capture the exact order identity, stop, geometry, mode, and accepted causes on the point.

For PH use maximum High. For PL use minimum Low. Evaluate every whole main candle between trigger index and Order stop index, inclusive. Earliest equal maximum or minimum supplies the source. A point's label price and source time come from that candle. Its decision time is the Order stop, even if the selected extreme was earlier. An open qualifying Order is not a confirmed point.

### 5.3 Point commitment and StopAll source ownership

A confirmed directional PL/PH owns its exact physical source in the final result. At a horizon where it has confirmed, omit the public StopAll at that matching source in both the native result and its optional Bridge projection. Preserve accepted historical StopAll evidence that led to the point. Native StopAll boundary/numbering and the independent T/F series must keep their separate roles. The final source-ownership rule does not retroactively rebuild the accepted historical prefix or assign new physical StopAll identifiers. A confirmation beyond the requested horizon cannot remove an earlier public StopAll.

Commit directional primary stops to native audit. The first strictly later strict price stop of the point is a real parent-stop eligible to create native Order_A. The accepted canonical physical reaction's First belongs to the stop candle or later, and native confirmation is strictly after the stop. A canonical candidate confirmed at or before the stop is skipped in favor of the first eligible canonical candidate. Preserve one physical identity per such cause. Transfer an obsolete same-stop StopAll cause only to the eligible primary direct identity. Retain independent causes on the former order, remove cause-less identities and indexes, and refresh accepted-audit and reused-query state as required. A valid Reset route remains Order_B. Its anchor or post-stop owner is the directional primary only when the native temporal ownership tests are satisfied. Final relabeling updates accepted aliases and serialized frozen order causes without changing geometry or native eligibility.

## 6. Local state, cancellation and final labels

### 6.1 Local continuation

After a directional point has confirmed, seek the next eligible break beginning strictly after its decision. A new directional point seeks the last confirmed primary's level, or the reference threshold before the first primary. After local 1 and local 2, a strict new break in the same directional space opens the next local number if the counter has not reset. The opposite path first breaks the frozen MBL. Later opposite points require the strict break of their own last confirmed level. Opposite numbering survives a local primary reset. After an opposite point confirms, the next directional candidate uses local number 1 with A/B eligibility and still needs a valid new directional crossing. It keeps the existing MBL and opposite count.

### 6.2 Competing boundaries and cancellation

- When seeking, choose the earlier exact eligible opposing break. If both new direction choices are present in the same finest RAW event, report ambiguity and do not assume an intrabar order.
- While a directional primary is pending, a strictly earlier MBL break cancels that candidate and allows the opposite path. If an opposite point already exists, the cancellation alone cannot create a subsequent opposite point. Its prior confirmed level must also break.
- While an opposite point is pending, a strictly earlier break of the current directional threshold cancels the pending opposite point and resumes evaluation of the directional path. A canceled candidate's later old Order stop cannot revive the abandoned proposal.
- When a cancellation and proposed Order stop have the same exact time, the implementation can report `ambiguous-raw-boundary-order` and withhold the disputed proposal. An ambiguous proposal does not erase already confirmed points.
- After the third opposite point, a further opposite break retains eligible accepted Orders as post-third order evidence and forms no fourth opposite point. A newer directional break can end that wait. The bridge publishes the evidence as `postPL3Orders` in bearish and `postPH3Orders` in bullish.
- The directional regime ends on the first strict stop of a confirmed **final physical** directional point numbered 3. This limits normal local continuation. Final numbering is a separate physical reconciliation across cycles. A historical or concurrent physical public number greater than 3 must not be treated as a newly taught local continuation number or as a T/F primary label.

### 6.3 Final physical label resolution

1. Filter logical roles by decision horizon before assigning a public directional primary number. Group by the physical source index and time. Within a source choose the largest local number. Resolve equal numbers by exact decision, deterministic cycle order, cycle identity, trigger index and local number. The earliest eligible logical role supplies the stable physical identity.
2. Process physical groups by their earliest confirmation, then source time and index. A distinct lower PL following PL-n forces a final number of at least n+1. A distinct higher PH following PH-n does the same. Preserve a larger already-qualified local number. An equal or shallower extreme does not force a continuation. Coincident roles have one final marker and do not each increment the counter.
3. Resolve before applying the visible start filter. Use the final number everywhere in public primary labels and applicable OrderAudit parent/source aliases. A later role or a different winning final number does not replace the stable ID for that candle. Keep all participating visible cycle IDs.
4. This final physical ownership/reconciliation applies to the **directional** primary rows. Opposite logical rows are projected through their own visibility contract.

## 7. Trend change and isolated regimes

Find the earliest strict RAW stop strictly after confirmation of any visible, resolved directional number 3 across current independent cycles. Resolve ties by the existing chronological identity ordering. Exact equality is not a reversal. On the winning event, stop all cycles in that trend. The boundary belongs to the incoming trend's complete main candle.

Bridge recalculates a prefix that ends before the boundary. That independent prefix must contain a confirmed final directional number 3 matching the reversal's price and source. Without this evidence the bridge rejects the inconsistent result. It then constructs a fresh suffix from the boundary candle, without the old Reaction, lifecycle, primary or Order state. Use the authorized opening rule for the new direction. Translate local indexes back to coordinates of the input, preserving the physical identity of finalized historical output. A later reversal beyond the selected presentation horizon does not replace that horizon's outputs.

Return each independent segment with its own start/end bound as applicable and attach the transition to the incoming segment. When a direction recurs, aggregate its rows in segment order. The segment arrays remain available for historical clipping, selections and renderer ownership. An MBL's end and the old cycle statuses are bounded by the stopped regime. No automated position selection is inferred from a trend reversal.

The separate T/F repair lookup searches the existing original RAW horizon using a carried reference's original direction. The new regime's trading state and new verdict series still start fresh.

## 8. True/False evaluation

### 8.1 Scope, ordering and output ownership

Evaluate Basic S/E, StopAll, and the directional primary numbers independently. This step annotates the already-serialized final behavior rows. Within a published segment, clear previously added verdict, repair and repeat fields on the four input collections. For each source time choose the first valid row by this collection priority:

1. Directional primary collection, `primaryLows` for bullish or `primaryHighs` for bearish.
2. `stopAlls`.
3. `eZones`.
4. `sZones`.

The winner is the first eligible row within the selected collection. A row with `calculationValid: false` cannot win. After choosing owners, order rows by complete source epoch. The opposite primary collection is outside this pass. A donor suppressed at the same source cannot also produce an independent Basic verdict. The optional nested `bridgeOutput` projection is separate from the native arrays and does not receive these annotations. Its projected StopAll source is `formedAt.time` in Tehran display form, while the native row uses epoch `sourceTime`. Aggregate arrays and their owning segment arrays share the same final row objects.

The native calculation can have access to accepted history before the display start. The verdict evaluator sees only the source rows included in the published segment. Cropping earlier source rows can change its available Basic parents and StopAll baseline. Re-evaluation after a live append uses the new published result and exact close evidence for the current horizon. No separate client-side label history is authoritative.

### 8.2 Basic classification and engulf reset

Maintain a lookup of already assigned verdicts by source time and an active record per exact rank. The active record holds the latest occurrence, a verdict repetition count, and a separately maintained repair count. Rank is kind/family priority and, for E, its integer continuation number.

1. Before the first admitted S in that segment, an admitted E has no Basic classification and retains a neutral null verdict.
2. Every admitted S is T. A later E normally alternates from its already-assessed published parent, T to F or F to T. If the parent has no assigned published Basic verdict at that point, fall back to E number parity, odd F and even T. Therefore a simple S → E1 → E2 → E3 chain is T, F, T, F.
3. Before counting the new occurrence, check lower-rank records. If at least one lower rank has at least two qualifying occurrences of the same exact rank and same T/F label, the incoming larger behavior is an engulf. Assign that new behavior T even if its ordinary E parent alternation would yield F.
4. An occurrence of higher rank displaces lower-rank records. A lower-rank intervening behavior normally leaves a higher-rank repeat intact. If the intervening behavior itself starts an engulf, its global verdict restart applies. A same-rank occurrence with a different label starts a new repeat count.
5. On an engulf clear all surviving verdict repetition counts. The incoming behavior seeds its own new count of 1. Keep earlier assigned labels available for parent lookup. Keep separate F repair history. The new T marks the incoming behavior and does not rewrite the earlier displayed labels.

Thus two smaller S Blue objects can cause an S Red or E1 Blue to be the first T of a fresh count. An older S Red from before that reset cannot combine with the new S Red for the next repetition even if the two are of the same type and label.

### 8.3 Basic F repair

Use the finest available RAW and a strict crossing of the reference level. In bullish a lower Low repairs the reference. In bearish a higher High repairs the reference. Equality does not qualify, and the RAW Close need not cross. The reference's original market direction governs its test even after a reversal.

- For a repeated same-rank F record, the latest occurrence supplies the active reference. Look for the first strict crossing at or after that occurrence's source time. A crossing belonging to an older occurrence strictly before the new source may remain historical evidence. If the older occurrence's repair was at or after the new source, remove that attribution when the new reference supersedes it.
- When a larger Basic behavior displaces a singleton lower-rank F, the larger behavior's source time supplies the singleton's earliest search time. An already-classified F can be repaired even when the newer behavior has its own T verdict.
- Search through the end of the last visible main bucket, inclusive, using RAW rows actually supplied in that window. The bridge computes an inclusive horizon of visible bucket start + analysis duration - 1 second. Lower RAW from within that bucket is allowed. Re-evaluate as the horizon advances.
- Publish the first eligible crossing as `trueFalseRepairTime` on the owner row. The original Basic T/F label remains as assessed. A prior segment can supply a historical reference only if its source row is in the published result.
- Each eligible F reference is searched independently. The Engine does not wait for one F to be repaired before evaluating another, and no global newest-first or oldest-first queue exists. If a single RAW event strictly crosses several separately eligible references after their own search starts, each may receive that same epoch in `trueFalseRepairTime`. The rule that the latest occurrence represents a repeated F group still applies within that group.

### 8.4 StopAll series, shorter series and confirmation close

Reset the StopAll verdict state at the source of each finalized directional primary, at the calculation start, and with a new independent regime. Partition published StopAlls within that history at an equal or decreasing native number. The first published number in a new segment or series is its starting number. An ordinary series alternates T/F by the distance from that number, with an even offset producing T. Native object numbering belongs to the owner stages and is separate from the verdict calculation.

1. Keep two comparison endpoints for the current group. The first is the last number of the immediately preceding published series. The second is the largest last number among all earlier series in the same history. A shorter group supplies the first endpoint for the next group and leaves the historical maximum intact.
2. Begin the group at T, alternating by native number distance from its first published number. A group that ends below the first endpoint has ordinary T/F and carries no N/A. Neither comparison qualifies if its exact endpoint is absent. Intermediate earlier endpoints below the historical maximum do not supply additional matches.
3. When a StopAll exactly reaches either endpoint and its confirmation main candle has closed, flag the current prefix through it as repeated and assign the group's original alternating T/F to that prefix. Previous groups retain their own verdicts. If both endpoints are equal, one confirmed match flags the prefix once.
4. After any confirmed match, the first higher published number in the same group starts a fresh count at T. Continue alternating by distance from that number. When the current group later confirms its larger historical endpoint, extend N/A through it and recalculate the newly covered rows from the group's original start. The first higher number after the larger endpoint starts another fresh count at T. Any native restart or directional primary boundary applies before counting a row as part of the current series.
5. In the live/manual Bridge, a matching StopAll satisfies the close gate when its `decisionTime + analysisDuration` is at or before the lesser of `lastVisibleMainStart + analysisDuration` and `lastSuppliedRawStart + rawDuration`. Use the confirmation candle's `decisionTime`. Vite supplies the selected RAW duration in seconds. The direct CLI accepts `--raw-timeframe` and defaults to 1 second. Direct calls on finalized row sets can omit the closure callback.

The corrected A–G schematic in one primary-delimited history yields the following after each applicable endpoint confirms and closes. A bracketed entry carries both N/A and its T/F.

| Group | Prior group endpoint | Largest prior endpoint | Current display |
|---|---:|---:|---|
| A | None | None | T, F, T |
| B | 3 | 3 | [N/A + T], [N/A + F], [N/A + T] |
| C | 3 | 3 | T, F |
| D | 2 | 3 | [N/A + T], [N/A + F], [N/A + T], T |
| E | 4 | 4 | T |
| F | 1 | 4 | [N/A + T], T |
| G | 2 | 4 | [N/A + T], [N/A + F], [N/A + T], [N/A + F], T |

In F, number 2 starts a fresh count. In G, number 2 belongs to the repeated prefix and is F. When G reaches 4, it covers all four numbers from the D endpoint, including the two already marked after matching F. Beyond an even matched endpoint, the first new odd number is T. Beyond an odd matched endpoint, the first new even number is T.

For lengths 1 → 2 → 2, the middle series' second StopAll is T and the final series' second StopAll is N/A + F. If the preceding and largest endpoint is 3 and the published numbers are 1, 2, 4, 5, the labels remain T, F, F, T. The published prefix cannot match a missing exact endpoint.

### 8.5 Directional primary verdicts and nullability

Only the final PL in bullish and final PH in bearish participate in this track. Final number 1 is T. Final numbers 2 and 3 are F. A valid admitted directional point at another native number is neutral. Each admitted directional primary still resets the StopAll verdict history. The opposite primary does not reset that history.

| Public field | Meaning |
|---|---|
| `trueFalse: "T"` or `"F"` | Final verdict on the assessed source owner. |
| `trueFalse: null` | Assessed source owner with no assigned T/F, such as a directional primary outside 1–3 or an E before the first admitted S. |
| absent `trueFalse` | Row outside the verdict projection, suppressed/noneligible source owner, or a legacy payload. |
| `trueFalseRepeated: true` | StopAll's repeated prefix flag. The same row retains its T/F. Non-repeated rows omit this flag. |
| `trueFalseRepairTime` | Exact first recognized repair RAW event time in Unix seconds. Its absence means no published repair evidence. |

## 9. Public payload and runtime interfaces

### 9.1 Main response and per-direction groups

Manual and live requests share the output builder. The JSON envelope includes native module versions, nullable `primaryVersion`, feature switches, `timeframe`, actual visible bucket bounds and `directions`. For a published trend reversal, `activeDirection` identifies the most recently activated visible regime. Before a published reversal the field is absent and the request direction supplies context. Keep `timings.phasesMs` and `timings.bridgeTotalMs` as measured telemetry separate from deterministic semantic comparisons.

The primary projection within each calculated direction has `primaryHighs`, `primaryLows`, `matchingBehaviorLegs`, `primaryStatus`, `primaryCycles`, and either `postPL3Orders` (bearish) or `postPH3Orders` (bullish). The bridge adds these only when that primary path ran. Source rows and MBLs at a previously confirmed horizon have different visibility filters as specified below. A direction can also have `trendTransitions` for its incoming segments and `calculationSegments` when the direction recurs.

### 9.2 Field inventory

| Row or collection | Required fields in the current published shape |
|---|---|
| PH or PL | `id`, `direction`, `kind`, `number`, `sourceIndex`, `sourceTime`, `price`, `triggerIndex`, `triggerTime`, `triggerEventTime`, `decisionIndex`, `decisionTime`, `decisionEventTime`, `order`. Add `cycleId` when associated with a cycle. Directional rows also expose `cycleIds`, in deterministic order. Apply verdict fields per section 8. |
| Selected Order | `ownerDirection`, physical `direction`, `reactionNumber`, nullable `reactionMode`, `types`, `auditCauses`, `firstIndex`, `firstTime`, `breakIndex`, `breakTime`, `confirmationEventTime`, `stopLevel`, `stopSourceIndex`, `stopSourceTime`, `stopHitIndex`, `stopHitTime`, `stopHitEventTime`, `causes`, nullable `boxTop` and `boxBottom`. `types` lists A before B when both are present. |
| MBL | `id`, `direction`, `sourceIndex`, `sourceTime`, `price`, `referenceStopAllIndex`, `secondBehaviorIndex`, `capTime`, `triggerIndex`, `triggerTime`, `triggerEventTime`, `confirmationIndex`, `confirmationTime`, `confirmationEventTime`, nullable `stopIndex`, `stopTime` and `stopEventTime`, and `cycleId` when applicable. |
| Primary cycle | `id`, `direction`, `status`, `referenceStopAllIndex`, `secondBehaviorIndex`, `triggerIndex`, `triggerTime`, `triggerEventTime`, `highCount`, `lowCount`, and directional joins `lowIds` in bullish or `highIds` in bearish. Counts describe the selected underlying logical rows as implemented by the serializer. Directional joins reference the final displayed physical IDs. The two are different kinds of collection. |
| Post-third Order | Selected Order shape, plus `cycleId` when supplied. Omit candidates whose native stop main candle is beyond the horizon. |
| Trend transition | `id`, new `direction`, `previousDirection`, `sourceIndex`, `sourceTime`, `eventTime`, `level`, stopped `phNumber`/`plNumber` and associated source index/time, nullable `iconCandleIndex`, `iconCandleTime` and directional `iconCandleHigh`/`iconCandleLow`. |
| Regime bounds | `calculationStartTime` and `calculationStartIndex` for a derived segment. `calculationEndTime` is the exclusive cutoff on the historical segment. The original calculation can omit a start marker. |

Epoch times and indexes are integers, primary levels and stop prices are exact Decimal strings, and cause payloads preserve native fields and order. When native provenance contains datetimes or Decimal values, project them with the corresponding epoch/price conversion. Time and index fields are independently meaningful. A confirmation horizon is not inferred from a source time.

### 9.3 Visibility filters and identities

- For a point, require main source within the display interval and main decision at or before its end. Resolve directional numbers and source owners before applying the start filter.
- For a cycle, require activation by the end. For a formed leg, require that the same cycle's first directional point has confirmed by the end. A visible MBL or active cycle can carry source information earlier than the visible start.
- A main point ID uses the earliest confirmed identity-producing role, including its trigger/decision and, for later origin cycles, its cycle key. A final label-number change does not change that stable ID. MBL identity is independent of its current break or cap.
- If no cycle is activated by the horizon, distinguish waiting for matching behavior from a qualified pending reference break. Use qualification before the end candle's exclusive boundary to choose the waiting state. With activated cycles, the latest visible cycle provides the top-level status. Per-cycle status records the calculated state, not a replay of every intermediate historical UI state. A stopped historical segment is tagged with its reversal status.
- Actual index offsets are restored after isolated regime calculation. Concatenate arrays in segment order. When an aggregate contains multiple segments, segment bounds govern historical paint, hit tests and selection.

### 9.4 Manual CLI and managed live worker

The CLI receives an input RAW JSON path, source duration, analysis timeframe, epoch start/end bounds, requested direction and explicit module paths. Module loading preserves the established import names in the `engine/bridge` and `engine/pipeline` layout. Pass an explicit lifecycle Engine and E module to enable the full primary path. The complete CLI and live worker commands are in section 13.

The live worker reads the seed input and the trusted original RAW path from `TRADINGBOT_LIVE_RAW_SOURCE`. The worker emits a ready seed and uses a private JSON-lines header for each framed update. Header fields include positive byte count `bytes`, `sha256`, optional append base hash `baseSha256` and optional `progress`. The following payload contains exactly the declared byte count. A delta is validated against the committed RAW identity. Full replacement input must preserve the previous prefix for this worker. The selected seed must be an exact contiguous slice of original decoded RAW. Retain the original suffix after the seed for catch-up on the next append. Byte deltas begin with the array comma, validate against the original prefix hash and preserve strict candle order. Output envelopes are newline-delimited JSON with `type` equal to seed, update, progress or error. Invalid/incomplete framing raises an error, an unverified delta returns `RAW_DELTA_MISMATCH`, and changed history requires recovery or a fresh calculation.

The current production worker stages incremental normalized RAW buckets and index views transactionally. It replays trading stages for the supplied history when constructing a new result. On failure the RAW append rolls back and the derived market views are rebuilt on retry. The embedded `LivePrimaryContinuation` is a supported Engine primitive with its own dirty-event/schedule rewind and native callback replay tests. The current production worker does not use that primitive to retain primary stage checkpoints. In both entry points verdicts are recomputed from final output and the same confirmation-close rules.
