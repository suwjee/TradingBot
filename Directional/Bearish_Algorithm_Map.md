# Bearish algorithm map

Strict stop High > level; confirmation Low < bottom; max High; First GREEN, context RED, native doji GREEN. Opposite Order bullish. S exact race tie no decision, E earliest stop then later First. PH primary, PL secondary; strict PH3 stop starts fresh bullish entire boundary main candle. T/F per final regime. This is a map, not complete executable proof.

Supplementary material below is the English semantic prose of the existing synchronized references, pinned to 466eb875070f02cd0dbfb105033422bbe2fd8c70. It is not a fresh branch-level proof. Exact production-source appendices are excluded. Historical acceptance examples remain historical.
## 4. Reaction / Reset — ACTIVE Bearish specification

### 4.1 Data and color contract

`Candle` carries `index`, native `timestamp`, display time, immutable market `tag`, and Decimal OHLC. `Candidate` carries First/box sources, Mode A/B, optional anchor and leg boundary, Break, intrabar start, cross-direction gate metadata, public box/number metadata and internal/public ownership flags. `ResetEvent` records main index/time, optional exact lower-TF second, broken level, and the owning Reaction First index.

### 4.2 Canonical directional geometry

For Bearish, the canonical First candle role is **FirstGreen** (`GREEN`) following the opposite context color `RED`. Confirmation is the first strict breakdown satisfying `Low < BoxBottom`. The confirmation edge is `BoxBottom`. The opposite box edge `BoxTop` may evolve only through chronology available up to the exact confirmation event.

The source does not maintain an independent hand-written Bearish state machine: Bearish geometry executes the Bullish reference state machine through exact Decimal sign/High-Low/color-role reflection. Therefore the initial leg, Mode-A invalidation, breakout/breakdown priority, Reset priority, post-confirmation handling, and lower-timeframe tie rules share one mechanical geometry contract. The reflected color role is internal coordinate machinery only; market Doji remains GREEN.

### 4.3 Mode A / leg-start ownership

Mode A is the first Reaction of a leg. The detector establishes the contiguous context run, builds the directional First candidate, preserves any qualifying adjacent anchor, and freezes the outer leg boundary. Before confirmation, strict outer-boundary invalidation owns the candidate ahead of confirmation when lower-TF chronology proves it first. In the standalone initial Mode-A WAITING state, an invalidated owner releases search and nested geometry cannot confirm while its selected structural owner remains unresolved. The bounded Unified post-Reset search has the separate completion-selection contract in Section 4.7.

### 4.4 Mode B / normal ownership

After a confirmed Reaction, normal search uses the running directional context and the required First color. A confirmation main candle may itself seed the next Mode-B First only when the post-confirmation remainder does not first Reset the just-confirmed structure. The confirmation candle can be the next First when its market color has the required role. First check strictly later RAW within that same candle for an immediate Reset against the confirmed opposite edge. A strict Reset there disqualifies reuse. With no such Reset and with RAW rows available, use the entire confirmation candle from its main open through its exclusive end to build the successor box. BoxTop is its maximum RAW High and BoxBottom is its minimum RAW Low, with the earliest RAW occurrence on equality. Both edge source indexes and times name the main candle. Mode B starts its intrabar search at that main open. The full-candle geometry rule and the later-only Reset check apply after the initial and later confirmed Reactions in both directions.

This handoff applies identically to the **initial confirmed Reaction** and to every later confirmed Reaction. Initial-confirmation status is not a reason to discard an otherwise eligible same-candle continuation; a same-remainder Reset still owns precedence exactly as before.

### 4.5 Exact confirmation and published box

If the Break main candle owns the full-main-candle opposite extreme, only lower-TF prices at or before the first strict confirmation may define the published opposite edge. Later prices in that same main candle cannot retroactively alter Reaction/Order geometry. If lower-TF chronology cannot prove a refinement, detector geometry is retained rather than guessed. Equal eligible extremes retain the earliest main-candle owner.

### 4.6 Reset

A confirmed Bearish Reaction resets only on the first strict `High > confirmed BoxTop` event. Equality is not Reset. When Reset and confirmation/break activity share a main candle, selected lower-TF ordering decides which event owns the state transition. Reset reopens **same-direction** Reaction ownership; opposite-direction patterns do not gate that search. A Reset event with an exact lower-TF second exposes that exact second; otherwise the owning main-candle start is the fallback representation.

### 4.7 Post-Reset structural owner vs geometry-only evidence

After Reset, `_first_direct_same_direction_after_reset` scans eligible First candidates in chronological First-index order within the configured end index. It returns a candidate only if confirmation wins before strict loss of its frozen owning boundary. If invalidation wins first, candidates with First indexes at or before that invalidation main index are blocked. A candidate unfinished at the bounded end is skipped, so a later eligible candidate that completes healthily may be returned. The standalone initial Mode-A WAITING state retains its selected unfinished structural owner. The returned healthy result joins the canonical same-direction Reaction stream. `_first_geometry_after_reset` separately returns complete geometry without lifecycle acceptance; generic geometry alone cannot create Order_A. An unfinished or invalidated bounded geometry alone cannot create Order_A. The **special complete post-A-stop physical Order_A** is an explicit exception: it is independently confirmed, after the parent stop, and recorded by S OrderAudit without appending a new public canonical Reaction.

### 4.8 Internal Reaction ownership

Cross-direction internal protection is determined after both directions exist. A candidate is internal only when its temporal/box structure is contained by a healthy opposite Reaction and the complete lower-timeframe physical path through its confirmation remains inside the protecting box. Internal identity affects behavior/public ownership; it does not delete historical calculation evidence or renumber the canonical Reaction stream.

## 5. Blue — ACTIVE Bearish specification

### 5.1 Inputs and reference level

Blue consumes canonical Bearish Reactions and Bearish Resets. For each Reaction, the scale reference is the Mode-A boundary when present; otherwise it is the previous Reaction opposite edge. The 0.618 level is `BoxBottom + 0.618 × (reference − BoxBottom)`.

### 5.2 Scale strikes

Within Reaction First..Break inclusive, a new strike requires a strictly higher `High` than the previous confirmed strike (or than the Fibonacci level for the first strike). Pending strikes confirm on a `RED` main candle. A Break main candle is eligible only with its lower-TF extreme through the strict Reaction confirmation row, inclusive; later main-candle extremes are excluded. A pending strike reaching the Break candle may confirm intrabar only from lower-TF chronology through that exact confirmation row, inclusive; the decisive extreme is the most directional eligible lower-TF extreme.

A Scale Blue is emitted when strike count increases and spacing ownership permits it (first Blue, or at least one healthy Reaction since the previous Blue). Its source is the decisive strike; line price is `High − (High − Low) / 3` and its drawing interval is one timeframe before/after the source time.

### 5.3 Reset Blue and double-stop calculation validity

A Reset Blue is sourced by the Reset main candle, with source extreme `High`, broken level from Reset, and line price `High − (High − Low) / 5`. If the prior Blue first strict-stops on that same Reset candle and the Reset source extends strictly farther in the Bearish direction than the prior Blue source extreme, the new Reset Blue is marked `calculation_valid=False`. That invalid line remains calculation evidence for the A double-stop route but is excluded from public Blue output.

### 5.4 Internal/public Blue

A Blue becomes behavior-internal when its owning Reaction is internal, or when both the source extreme and rendered line price lie strictly inside the same protected healthy Reaction. Drawing offset alone does not create internal ownership. Public Blue is exactly `calculation_valid and not behavior_internal`.

## 6. A — ACTIVE Bearish specification

### 6.1 Blue state and strict stops

A builds an immutable `BlueState` ledger from all Blue calculation state. Blue formation is exact: Scale Blue forms at its Reaction confirmation; Reset Blue uses the first strict lower-TF crossing of its broken level when available. Each Blue stop is the first strict Bearish crossing of its `source_extreme`; equality does not stop a Blue.

### 6.2 Ordinary adjacent-Blue route

Ordinary A evaluates adjacent calculation-valid Blue states. A pair may trigger through the established direct or inherited-stop route. When the first Blue stopped before the second formed, continuation geometry is frozen over the owning interval; inherited-stop ownership uses the complete stop-candle through the aligned Reaction Break candle. Directional source selection is the maximum High and strict comparisons preserve chronology. Exact equal-event ties use deterministic ordering; the second/current Blue may be reused for the next adjacent pair only when the current A's first strict stop and the next Blue formation satisfy the source lifecycle gate.

### 6.3 Double-stop route

A Reset Blue marked calculation-invalid by the Blue double-stop rule can create the special A route with the previous valid Blue only when the previous Blue's first strict stop belongs to the invalid Reset Blue source candle. The route then requires the first qualifying same-direction canonical Reaction after the trigger chronology. A special route cannot duplicate a Reaction already owned by ordinary A, and earlier ordinary A lifecycle may suppress the special route when its first stop already completed before the special Reaction.

### 6.4 Reaction confirmation and A source freeze

After a valid Blue-pair trigger, the first qualifying canonical Bearish Reaction confirms A. The A source/price is the maximum High from the trigger main-candle open through the exact lower-TF Reaction confirmation, inclusive. Prices later in the same Break candle are outside A ownership and cannot move the source retroactively. Ties retain the earliest source unless the owning helper explicitly states otherwise.

### 6.5 A stop and lifecycle handoff

A itself stops on the first strict Bearish crossing after its confirming Reaction. A historical stop before a route's `not_before` boundary belongs to the previous cycle; a later recross of the same level cannot be reinterpreted as the new cycle's first stop. The stop event opens S space.

## 7. S — ACTIVE Bearish specification

### 7.1 General A→S gate

Only A candidates outside an already-owned S continuation are eligible. S begins at A's first strict Bearish stop. If the next A confirmation is already reached at/before that handoff, the stale A does not open S. The detector audits the stopped A's first physical Order_A independently before choosing the S route.

A decided S normally owns subsequent A continuation. A newly built Reset-Blue/Reset-Blue pair may preempt that ownership only when both Blue sources are born after the S handoff, Blue-1 stops before Blue-2 forms, the A source is Blue-2's stop candle, and the pair is actually Reset/Reset. A trigger that begins strictly after the exact S ownership handoff is independently eligible.

A detection remains provisional until S ownership is resolved. If a detected A is consumed by an already-owned S continuation and therefore is not in the accepted A set, its later strict price stop cannot create or retain A-owned `parent-stop` Order_A provenance. This rule changes Order eligibility only; A geometry/detection and S ownership rules are unchanged.

### 7.2 Order-free Type-3 S Blue

Type-3 is an opposite-Reset-leg route available after A stop and before the first Order deadline. The opposite Reaction owning the Reset must have confirmed by the A-stop event and must not already have Reset before that A stop. Candidate geometry spans the **complete opposite Reaction Break main candle through the Reset main candle**, inclusive, and selects the maximum High with **last-candle ownership on equality**. After Reset, the first strict Bearish cross of that candidate wins only if at least one ordinary same-direction Reaction confirms after A stop and no later than the cross. Earliest valid Type-3 decision wins.

### 7.3 Order-free Type-4 S Blue

Type-4 is the same-direction Reaction continuation available after A stop only while no opposite Order has formed. For every aligned Bearish Reaction confirmed before the Order deadline, candidate geometry spans the A-stop main candle through that Reaction Break main candle, inclusive, selects the maximum High and assigns equality to the **last** candidate candle. Search begins at the maximum of A-stop event, aligned Reaction confirmation and candidate formation event. That lower-timeframe start is inclusive. The next aligned Reaction confirmation and Order deadline are exclusive upper bounds. The first strict Bearish cross creates S Blue only when a public calculation-valid Blue formed from the candidate source through that cross. If a candidate crosses without qualifying Blue, no S is created from it; the next aligned Reaction rebuilds a fresh candidate from the same A-stop origin.

Type-3 and Type-4 are independent. Earlier exact decision event wins; Type-3 owns only a true exact-event tie.

### 7.4 Order-backed Simple and Advanced routes

**First post-A-stop opposite Order_A gate:** independently confirmed opposite geometry is eligible when its First belongs to the stop-owning or later main candle and its exact confirmation is strictly after the A stop. An earlier continuously owned opposite Reaction must not suppress this physical Order. Use the existing canonical Reaction for an identical physical identity; otherwise emit a geometry-only OrderAudit identity with `reactionNumber=0` while keeping public canonical Reaction numbering untouched. The first eligible post-stop First/confirmation pair owns the immutable Order_A. Ordinary same-direction nested Reaction geometry may qualify this Order for Advanced/Type-2 without being independently published as an opposite Reaction.

The first physical opposite Order_A owned by the stopped A is immutable for that A; later native Reactions do not refresh it merely because they are newer. Candidate timing first applies established price geometry. Exact event chronology may reclassify an apparent after-Order Simple candidate as pre-Order only when its candidate event is strictly before Order First; equality belongs to after-Order. A valid nested same-direction Reaction wholly contained in the physical opposite Order, with aligned confirmation at or before Order confirmation, owns the **Advanced** path and cannot be stolen by the pre-Order Simple chronology optimization.

For pre-Order Simple, candidate geometry spans A-stop through Order First with the A-stop candle restricted to lower-TF prices at/after the exact A-stop event. For post-Order Simple, the first aligned Reaction after Order confirmation is used and candidate geometry spans Order Break through aligned Reaction Break inclusive with last-on-equality ownership. Advanced uses the directionally relevant opposite Order box source after a nested aligned Reaction confirms.

### 7.5 S decision race

After Order confirmation, two strict lower-TF events compete:

- physical Order stop: `Low < OrderStop` → **S Red**;
- S candidate strict Bearish cross → **S Blue** only after an aligned Reset Blue formation or an ordinary aligned Reaction completion qualifies the candidate.

An exact same lower-TF position for both crossings produces no decision. Otherwise the earlier event wins. The legacy pre-Order Simple fallback may initially observe an unqualified candidate cross; if later qualification exists by that exact event it becomes Blue, otherwise the fallback path is rebuilt through normal ownership rather than inventing a family.

When a Red decision wins, Red source geometry is recalculated from Order Break through the Red decision main candle unless the accepted pre-Order source is itself authoritative.

### 7.6 Shared accepted-Order stop reconciliation

After E/OrderAudit accepts physical Orders, an open S may be converted to Red by **any** accepted physical Order whose strict stop occurs at or after the frozen S source main-candle start and strictly before S's current decision; the Order confirmation must be strictly earlier than its stop. Parent identity is irrelevant to use; physical identity is authoritative. Candidates are deduplicated by `(FirstIndex, BreakIndex)`, ordered by `(stopCrossEvent, confirmation, FirstIndex, BreakIndex)`, and provenance remains attached to the Order that created it.

## 8. E — ACTIVE Bearish specification

### 8.1 Parent stop and E-space opening

Every E cycle starts only after the first strict Bearish stop of an accepted S/E parent. For an E parent, a stop search begins at its decision event, so E cannot stop before the Order-stop event that confirmed it. Sequence/StopAll boundaries may later reinterpret parent type, but do not invent a different price event.

### 8.2 Physical Order choices

At each parent stop, E considers physical Orders from these routes: direct parent-stop Order_A, an S-carried unconsumed Order, a gate-owned initial A Order, carried-live accepted identity, post-stop accepted-live identity, and accepted Order_B reset-leg identities. `parent-stop` and `reset-leg` are creation causes; `carried-live` / `accepted-live` are use routes only. A candidate must possess an exact strict Order stop. Winner is earliest stop event; for an exact same stop event the larger Order First index wins (`-FirstIndex` tie key). Sequence reset boundaries may invalidate an Order crossing that would span a hard reset.

E performs this comparison over one complete eligible candidate set spanning all direct, inherited, carried and post-stop accepted routes. No route may reduce to a single candidate before the global `(exact stop event, -FirstIndex)` adjudication. This E-consumption tie rule does not change physical Order creation ordering.

### 8.3 E source and decision

`decision_event = max(parent_stop_event, order_stop_event)`. The E source is the maximum High across the **complete main candle containing the parent stop through the complete main candle containing the Order stop**, inclusive. Lower-TF chronology decides whether stops occurred; it does not truncate either E boundary candle's OHLC. Strict-better replacement retains the earliest equal source.

### 8.4 Recursive family/number lifecycle

Every fully formed accepted S starts a provisional E1 chain in S color. Recursive children are built after the preceding E's strict stop. Reconciliation is chronological: a stopped E leaves the active set but remains historical output. Family follows the accepted stopped parent. Red family outranks Blue at a shared physical source; within equal behavioral priority exact decision chronology is the tie-breaker. When stopped members of the same accepted family exist, the next number is `max(stopped family number)+1`; otherwise the family starts at 1. An active Red E cannot be superseded by S; a Red S may supersede a Blue E under the source lifecycle rules, while Blue S cannot steal an active E continuation.

### 8.5 Consumed S evidence and independent roots

A suppressed/non-public S can remain calculation evidence for continuation of a stopped larger E when lifecycle ownership proves it belongs to that continuation. Its first E inherits the stopped larger E's reconciled family and next number, then recursive children are rebuilt natively. Separately, each accepted stopped S may retain an independent direct E1 root. A same-source accepted E owns that physical source and prevents a provisional S at that source from manufacturing a competing later root. Explicitly invalid S evidence cannot create cross-family competing root provenance when native E continuation already owns the source. A provisional S at an E-owned source also loses Order creation rights. Every E route selects from the complete remaining native Order set; an invalid first choice does not discard a later valid alternative. An E source cannot qualify itself by invalidating its Order's only creator.

### 8.6 Same-source reconciliation and OrderAudit rebuild

At one physical E source, Red E outranks Blue E; within the same family higher number wins; exact remaining ties preserve the earlier accepted object. After reconciliation, the canonical Order ledger is rebuilt from the accepted E state. Valid parent-stop Order_A identities are retained even if later visibility changes their consuming owner. External restoration/continuation replacement must resynchronize OrderAudit before serialization.

## 9. Order_A — ACTIVE canonical physical parent-stop rule

### 9.1 Creation gate

Order_A is the physical `parent-stop` route opened by an accepted strict behavior stop. Ordinarily a bounded/direct Order candidate must match a canonical opposite-direction (Bullish) Reaction identity `(FirstIndex, BreakIndex)`. **Approved 5.4.30 exception:** after an accepted A stop, independently confirmed complete physical opposite Order geometry may enter S OrderAudit even when it is absent from the public opposite Reaction stream. It receives `reactionNumber=0`, not a synthetic canonical Reaction, and retains its real physical First/Break identity and exact confirmation. An incomplete, unconfirmed, or otherwise invalid geometry cannot enter the accepted audit.

After a stopped A, the first eligible physically confirmed opposite Order is immutable for that A. For S/E parent stops, direct bounded geometry may be evaluated subject to the existing canonical acceptance contract. One exact parent-stop cause may own at most one physical Order_A; when multiple candidates compete, earliest canonical confirmation, then FirstIndex, then BreakIndex owns the cause.

For an A parent, “accepted” means the A survives S ownership and current invalid-A lifecycle filtering into the finalized A behavior set. A provisional/detected A that is S-owned, consumed, filtered or invalid cannot open an A-owned Order_A and cannot be retained as an A `parent-stop` cause in the final OrderAudit. Other independently valid creation causes on the same physical Order identity remain valid.

A shared accepted physical Order stop that changes S Blue to S Red must preserve its opposite `order_direction`, identity, First/Break, confirmation, and exact stop provenance.

### 9.2 Canonical stop

Order stop provenance comes from `MarketChronology.canonical_order_stop`. For Mode A it uses the canonical leg-head/floor context required by that opposite Reaction; for Mode B it uses the previous healthy opposite Reaction's outer edge under the established chronology. The Order's exact strict stop uses the **opposite direction** predicate; for this Bearish calculation that is `Low < OrderStop`. Equality does not stop an Order.

### 9.3 Parent validity and retention

An S explicitly identified in invalid_s_root_identities is calculation evidence, not an accepted S parent, and cannot create or retain a `parent-stop` Order_A cause. An E derived from that S may be accepted only when its chosen physical Order has a valid creating cause independent of the invalid S. This applies to ordinary chain reconciliation, consumed-S continuation, and independent-root restoration; provisional geometry alone cannot publish an E or StopAll. Ordinary E/lifecycle reconciliation can change who uses a valid accepted physical Order_A while retaining its valid causes and identity. Confirmed directional primary ownership has the explicit exception in Sections 13.4a–13.4b: revoke or transfer an obsolete same-stop StopAll parent cause and remove the identity only if no independently valid cause remains. A shared Order_B identity retains its independently accepted reset-leg provenance.

The same acceptance rule applies during every OrderAudit rebuild/reconciliation pass: nonaccepted A causes are removed before a physical identity is retained on A provenance. This prevents a provisional A cause from being reintroduced after downstream E reconciliation while preserving independent valid S/E or reset-leg provenance for the same physical Order.

## 10. Order_B — ACTIVE Bearish reset-leg rule

### 10.1 Eligibility and post-stop owner

Order_B is eligible only after an accepted lifecycle stop (`A`, `S`, `E`, or `StopAll`) selected by the accepted lifecycle owner of the stopped main candle. The stop opens eligibility; it is **not** the geometric HH anchor.

### 10.2 Geometric behavior anchor

For each reset Bearish Reaction, choose the latest accepted behavior source that exists strictly before the Reaction FirstGreen candle, independent of current dominance. Valid anchor families are A/S/E/StopAll. When several lifecycle projections share exactly one source candle, lifecycle priority and number resolve only that exact-source tie.

### 10.3 HH construction and extension

Use the closed main-candle range from anchor behavior source through reset Reaction FirstGreen, inclusive:

`HH = maximum High(anchor candle .. reset Reaction FirstGreen)`

Only a strict better High replaces the current source, so equal extremes retain the earliest source. The HH source must be strictly before the reset Reaction FirstGreen. It must also extend beyond the anchor itself: the HH must be strictly above the anchor behavior `High`; equality invalidates the setup.

### 10.4 Reset and calculation-timeframe strict-break candle

The reset Reaction must first produce its canonical Reset. A strict `High > HH` must occur after that Reset. The **configured calculation candle containing the first valid post-Reset strict crossing** is the Order_B break candle. Equality is not a break.

Lower-timeframe RAW is consulted only when exact intrabar chronology is required: to prove that a crossing in the Reset candle happened after the exact Reset, to retain the exact crossing timestamp as `strict_break_time`, and to prove any same-candle confirmation occurs strictly after that crossing. The exact lower-timeframe timestamp does **not** postpone the Order_B First-candle gate beyond its owning calculation candle.

### 10.5 Accepted-A expiry

Let the next accepted A formation after the reset Reaction First be `A_next`. Compare `A_next` and the strict break by their owning calculation-timeframe candles. If the A candle is at or before the strict-break candle, the pending reset leg expires. A is upstream of Order_B feedback, so this hard expiry prevents a stale S/E/StopAll setup from firing inside a newer A lifecycle.

### 10.6 Physical canonical opposite Reaction

Let `BreakCandleIndex` be the main calculation-candle index containing `strict_break_time`. Choose the first canonical Bullish Reaction satisfying both:

`FirstIndex >= BreakCandleIndex`

`strict_break_time < ConfirmationTime`

Therefore a Bullish Reaction whose First is the **same main candle** as the strict HH break is eligible even if its candle opened before the exact lower-timeframe crossing. Exact lower-TF chronology remains relevant only to the strict confirmation-after-crossing condition. Canonical-Reaction membership is mandatory; geometry-only evidence cannot become Order_B.

### 10.7 Provenance and identity

Order_B records post-stop behavior, geometric anchor type/source/extreme, reset Reaction identity/confirmation, Reset index/broken level/time, frozen HH boundary/source, exact strict break, and final physical opposite Reaction identity/confirmation. Physical Order identity remains `(FirstIndex, BreakIndex)`. Multiple reset-leg causes may merge into one identity; they do not create duplicate physical Orders.

## 11. Order / OrderAudit architecture

1. The identity-keyed Order ledger is canonical; parent labels are provenance, not identity.
2. Creation causes are exactly `parent-stop` (Order_A) and `reset-leg` (Order_B). `carried-live` and `accepted-live` are consumption/use routes.
3. One exact parent-stop event has one physical Order_A owner. Cause deduplication ranks by confirmation, FirstIndex, BreakIndex.
4. `prepare_order_audit` merges S-stage and E-stage accepted ledgers, retains identities outside the presentation range when required by a visible behavior, deduplicates causes, and computes a strict stop only when it was not already authoritative.
5. `accepted_audit_entry` filters an A-owned identity to accepted A provenance without discarding the complete physical cause set used for presentation.
6. OrderAudit must not fabricate parentage: invalid/suppressed parents lose creation rights; valid historical parent-stop provenance survives later consumer reconciliation.
7. The active physical Order routes are Order_A and Order_B.

## 12. Lifecycle / StopAll — ACTIVE specification

### 12.1 Exact S/E dominance priority

The complete dominance priority for S/E behavior is `S Blue < E Blue < S Red < E Red`. `A` is not a member of this ranking and cannot become its highest behavior, increment its count, or arm its StopAll rule. StopAll is a hard lifecycle boundary, not a competing S/E behavior. Separate A/S/E/StopAll visibility and Order_B ownership rules retain their own scopes.

This priority and exact-identity rule are identical in Bullish and Bearish. Only the strict price stop is directional: Bullish uses `Low < owner price` and Bearish uses `High > owner price`; equality is not a stop.

### 12.2 Highest existing behavior and armed owner

The first accepted S/E occurrence immediately becomes the highest existing exact behavior with count `1`. It is not armed. A repeated occurrence increments only the same exact identity: `S Blue`, `S Red`, or an E identity with the same family and number such as `E1 Blue` or `E1 Red`. Different E numbers and colors never combine. The current exact owner is armed for StopAll at count `>= 2`; its latest accepted occurrence supplies the strict stop level and search start. A third or later exact occurrence remains armed while it still owns the highest state.

An accepted unrelated higher-priority behavior replaces the owner at its source time and starts at count `1`. A direct E child first resolves the strict stop of its exact armed parent, even when its retrospectively chosen source candle begins at or before that stop. An accepted independent E sourced from a different S parent may also donate the currently armed owner stop when the first strict crossing belongs to that very E source candle and its directional source extreme strictly penetrates the owner price. A larger number within the same E family advances the E owner; a smaller number does not. Lower-priority accepted objects may remain valid calculation/output objects, but cannot count, remain armed, or trigger StopAll behind the current owner. There is one active exact owner and no independent Blue repetition ledger.

### 12.3 Chronological strict stop and E donor

The armed owner's stop is the first strict 5-second crossing at or after its latest occurrence's decision event. A stop must precede replacement by an unrelated higher-priority behavior to belong to the former owner; an E directly caused by that stop is resolved as a donor before it replaces its parent. A completed earlier stop is frozen as pending historical evidence if no eligible donor exists at that transition; later replacement cannot cancel it. This pending completed gate is not a second occurrence counter and cannot re-arm a displaced behavior.

At an incoming E, a completed owner stop strictly before the E source time creates `StopAll1` through `sequence-group-stop`; the incoming E supplies physical geometry and Order provenance regardless of family. Two causal exceptions also admit an owner stop at/after retrospective E source time **and no later than E's decision**: (1) exact direct child of the armed owner, whose `parentStopEventTime` equals its first strict stop and whose parent type/source identity/price exactly match the owner's latest occurrence; or (2) an independently accepted E at a new physical source whose directional source extreme strictly penetrates the armed owner's price, and the owner's **first** strict stop belongs to that exact 30s (or configured) E source candle `[sourceTime, sourceTime + timeframe)`. The second route does not depend on E ancestry or require the parent S to postdate the dominant E: independent E parents can predate the owner. An unrelated E cannot consume a stop in a *later* main candle merely because its E decision is later. No earlier displaced owner is revived and no parallel Blue counter is introduced. Bridge includes only otherwise-omitted accepted independent S-root E identities as extra StopAll donor candidates, preserving the preexisting E candidate and Order provenance at every already-admitted physical source. An existing active StopAll that strictly stops at or before the incoming E decision continues to create the next numbered StopAll through `stopall-stop` under its separate historical contract. Its gate precedes the S/E owner gate.

**Superseded by V5.4.33:** the V5.4.32 sentence limiting *all* retrospective E donor exceptions to exact direct children alone. That direct-child rule remains active; the same-source-candle independent-E route is the additional narrowly bounded general exception.

### 12.4 S Red donor and legacy gate name

**ACTIVE (5.4.31 direct accepted-S Red rule):** When the currently dominant exact S/E behavior is Blue, its count is `>= 2`, and its latest accepted occurrence was confirmed **strictly before** the decision event of an accepted `S Red`, the **first eligible S Red itself** immediately produces `StopAll1`. No strict Blue price stop is required. Either Order Mode A or Mode B is valid. Formation must be checked at the incoming S **decision event**, not merely its retrospective source candle. The new `gateEventTime` is exactly the S decision event, and `stoppedBehaviorKey` preserves `S blue` or the precise `E(n) blue` owner and its count. The S is the donor; the StopAll resets the current dominant owner and pending stop state. This direct accepted-S Red gate has precedence inside S handling over the older completed-stop-only path. A previously displaced lower-priority Blue cannot trigger it.

**HISTORICAL LEGACY ROUTE (still executable as fallback):** When the direct gate is not eligible, an accepted S Red of Mode B may still consume an already-completed strict stop of an earlier armed Blue owner using the existing pending-stop rule. This fallback gate event is the earlier physical stop; Mode A does not consume that fallback. The two routes reuse the legacy serialized name `opposite-s-group-stop` but differ in gate chronology. Neither fallback nor other StopAll/E donor paths is removed.



**HISTORICAL / SUPERSEDED (`5.4.22` and earlier):** accepted Blue occurrences were counted in a parallel ledger independent of dominant-owner transitions. That ledger could promote a lower-priority Blue group after a higher-priority Red owner had formed, or promote without a strict stop. It is not an active rule.

### 12.5 Hard StopAll boundary

Materializing StopAll resets the active exact owner, its count/armed state, and any pending completed stop. Historical S/E and StopAll objects remain available as calculation and output evidence. E receives the accepted StopAll source map through the existing atomic sequence-reset publication; its dependent candidate/carried context caches refresh while immutable physical stop/cross caches and historical accepted causes remain retained. A later lifecycle cannot inherit an earlier count or resurrect a displaced owner.

### 12.6 Cross-stage A/S/E visibility ownership

A, S and E calculations continue to retain internal historical evidence. Public ownership is resolved from exact strict stops, source chronology and shared priority. A source that strictly extends beyond the newest stopped owner can be consumed as the closed owner's next leg head instead of re-entering as equal/smaller behavior; equality stays with the earlier owner. S under a stopped larger owner obeys analogous chronology-first ownership; a higher-priority Red S may supersede a stopped Blue S, while equal/lower candidates remain owned by the prior lifecycle. Final E/StopAll source occupancy removes duplicate A/S labels on the same physical source, while referenced historical parents are retained for lineage closure.
