# TradingBot Bullish Algorithm Reference — Current Standalone Specification

**Document Version:** `5.4.24`  
**Last Modified:** `2026-10-04 21:40:18 +03:30`  
**Status:** `ACTIVE — behavioral StopAll correction, byte-exact Current Source`  
**Target Direction:** `bullish`  
**Opposite Direction:** `bearish`  
**Production Source Behavioral Change:** `YES — unified exact-owner StopAll eligibility`  
**Mirror Contract:** Current shared Production Source defines both directional paths. Price geometry is reflected; time, identity, provenance, Doji, behavior-family names and lifecycle ordering remain invariant.

> Current Production Source defines executable behavior. This canonical Reference specifies the audited implementation and its exact Bullish↔Bearish mirror contract. Section 16 embeds every current live production Python Source file, byte-synchronized.

## 0. Revision scope

Reference `5.4.24` corrects a causal E-donor edge case in the exact-owner StopAll rule. An E source is retrospective geometry across complete main candles; it can equal or precede the strict stop of its own accepted parent even though its decision follows that stop. The completed stop of the currently armed exact S/E parent must materialize StopAll when the incoming E proves that same physical parent-stop event. An unrelated higher-priority E cannot use this exception. All other `5.4.23` dominance, identity, mirror and hard-reset rules remain active.

Only `pipeline/lifecycle_engine.py` changes production behavior. The Source manifest and exact embedded Source below are regenerated from live `engine/`; the original `engine.zip` and the `5.4.23` Reference snapshot remain historical inputs.

## 1. Source manifest

| Module | Owner | Version | Lines | Bytes | SHA-256 |
|---|---|---:|---:|---:|---|
| `__init__.py` | Package marker | `unversioned` | 0 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `bridge/__init__.py` | Package marker | `unversioned` | 1 | 64 | `2bc59770b9d4313c0e6306287d074487b9e1672dbaf3ada9a8be381e7123f0b8` |
| `bridge/trading_pipeline.py` | Pipeline / Serialization | `1.8.0 (impl 1.9.0)` | 2957 | 108158 | `edc657fa8322d0e6a08617a23dcf20f88d8e08407e1f74ebf01b7b0d123d345e` |
| `pipeline/__init__.py` | Legacy / unsupported package wrapper | `unversioned` | 19 | 348 | `ca549e4cf5d9a070227498d0d210279e0f7edae66d62dadab7981cddaa1db5c3` |
| `pipeline/a_zone_detector.py` | A | `1.7.0` | 804 | 31373 | `83f08b06556eb59c6d1b3afd22b51c280315bd80f3a31bc3044ada349251a115` |
| `pipeline/blue_line_detector.py` | Blue | `2.4.0` | 458 | 15802 | `b0426cddc49c2fface77b00ba713beaa469ffa4f33f0291d34e51827825f283a` |
| `pipeline/core_utils.py` | Core Utilities | `1.0.0` | 26 | 832 | `007e5329e14ab9695e555c630527badc84dd35a239dea1cf685141e4278265eb` |
| `pipeline/direction_policy.py` | Direction Policy | `1.0.0` | 70 | 2282 | `a27ac63c2f066311c9381e2ead6fb44f0789f423a37b465da65c80e6329397ea` |
| `pipeline/e_zone_detector.py` | E | `6.16.1 (impl 6.18.2)` | 1140 | 48698 | `9047cfbe0beba2b91d36a136c9b6033563bc5ac1ebd7a54af6b698c962f80aef` |
| `pipeline/lifecycle_engine.py` | Lifecycle / StopAll | `1.18.2 (impl 1.20.2)` | 1439 | 58761 | `e17f85cc6a14d40539f487b9c083a218da1ee3809d0f0c911fd9a8e71adc8558` |
| `pipeline/order_audit_engine.py` | Order / OrderAudit | `1.5.3` | 1947 | 78465 | `c791ef427ee2d5c5d0f5f1cc8261e413c768ee475b8b835cdfa0769cfee65ea6` |
| `pipeline/reaction_engine.py` | Reaction / Reset | `9.8.0 (impl 9.9.0)` | 2431 | 104599 | `9bc697bdb3d1e421b7700a94bbd52a7407f7891215031b271ced4523d7d6c8ca` |
| `pipeline/s_zone_detector.py` | S | `4.20.0 (impl 4.21.0)` | 1444 | 60888 | `ef71a2e4176caaabc25d1ef0c1f0f24efb54ed3110982cdb7cf52d2449cca2ee` |

This manifest is generated from current live Engine Source, including the zero-byte root package marker. The `5.4.22` claim that `__init__.py` was absent from the supplied archive was incorrect: the inspected archive contains that entry. Exact Source bytes and newline structure are checked against Section 16.

## 2. Authoritative pipeline and ownership

The production execution contract is:

`Complete supplied input normalization → both directional Reaction/Reset contexts → cross-direction Internal Reaction classification → Blue → A → initial S → provisional E → S validity/rebuild and accepted A/Order context → final E/OrderAudit → shared physical Order stop reconciliation → consumed-S native continuation → accepted Order_B feedback → lifecycle/StopAll → visibility/lineage closure → final OrderAudit synchronization → serialization`

Order_B feedback may repeat S/E context construction up to eight passes, using exact reset-leg identities. A repeated non-convergent identity or pass overflow is an error. This feedback does not recalculate Reaction/Blue/A geometry. StopAll is reconciled once from accepted chronology; downstream boundary publication does not reinterpret historical E.

The bridge calculates the complete input it actually receives. The full-chart HTTP route supplies the original RAW file. A selected-range HTTP route supplies an in-memory stream filtered by inclusive chart-candle buckets; that calculation begins with empty state at the selected start and cannot use rows outside the supplied stream. Within that supplied input, CLI from/to bounds filter presentation after calculation. Neither frontend nor serialization independently implements trading rules.

Ownership boundaries are strict: Reaction/Reset is owned by `reaction_engine.py`; Blue by `blue_line_detector.py`; A by `a_zone_detector.py`; S by `s_zone_detector.py`; E by `e_zone_detector.py`; physical Order discovery/reuse/provenance by `order_audit_engine.py`; lifecycle/StopAll/visibility by `lifecycle_engine.py`; request/range orchestration and serialization by `bridge/trading_pipeline.py`. Serialization is a projection of finalized state and is not a second trading algorithm.

## 3. Global invariants

1. **Decimal:** every price-sensitive input is normalized with `Decimal(str(value))`; no binary-float decision is authoritative.
2. **Candle color:** `GREEN` iff `close >= open`; `RED` iff `close < open`; a Doji is always GREEN in both market directions.
3. **Strict crossing:** equality never satisfies a strict price crossing. For Bullish behavior-space stops the directional primitive is `Low < Level`; the Bearish mirror uses the opposite strict comparator.
4. **Chronology:** exact event ordering comes from the finest selected lower timeframe. Range windows are half-open unless a component explicitly includes a complete main boundary candle. Time is never mirrored.
5. **Reaction identity:** physical Reaction/Order identity is `(FirstIndex, BreakIndex)`. Identity, provenance structure, stable ordering, lifecycle priority, behavior-family names and public schemas are direction-invariant.
6. **Determinism:** candidate ordering and tie-breaking are explicit. Equal main-candle extremes keep the earliest source unless the owning rule explicitly requests last-on-equality (S Type-3/Type-4 candidate construction).
7. **Canonical mirror:** the Bearish Reaction path mechanically reflects the shared Bullish coordinate state machine. Independently inspect explicit directional branches and policies. Reflect prices/roles; preserve time, state ownership, canonical identity, cause structure and lifecycle families.
8. **Calculation vs presentation:** internal/historical objects may remain necessary for later calculation even when they are not independently visible. Final filters cannot rewrite upstream truth.

## 4. Reaction / Reset — ACTIVE Bullish specification

### 4.1 Data and color contract

`Candle` carries `index`, native `timestamp`, display time, immutable market `tag`, and Decimal OHLC. `Candidate` carries First/box sources, Mode A/B, optional anchor and leg boundary, Break, intrabar start, cross-direction gate metadata, public box/number metadata and internal/public ownership flags. `ResetEvent` records main index/time, optional exact lower-TF second, broken level, and the owning Reaction First index.

### 4.2 Canonical directional geometry

For Bullish, the canonical First candle role is **FirstRed** (`RED`) following the opposite context color `GREEN`. Confirmation is the first strict breakout satisfying `High > BoxTop`. The confirmation edge is `BoxTop`. The opposite box edge `BoxBottom` may evolve only through chronology available up to the exact confirmation event.

The source does not maintain an independent hand-written Bearish state machine: Bearish geometry executes the Bullish reference state machine through exact Decimal sign/High-Low/color-role reflection. Therefore the initial leg, Mode-A invalidation, breakout/breakdown priority, Reset priority, post-confirmation handling, and lower-timeframe tie rules share one mechanical geometry contract. The reflected color role is internal coordinate machinery only; market Doji remains GREEN.

### 4.3 Mode A / leg-start ownership

Mode A is the first Reaction of a leg. The detector establishes the contiguous context run, builds the directional First candidate, preserves any qualifying adjacent anchor, and freezes the outer leg boundary. Before confirmation, strict outer-boundary invalidation owns the candidate ahead of confirmation when lower-TF chronology proves it first. In the standalone initial Mode-A WAITING state, an invalidated owner releases search and nested geometry cannot confirm while its selected structural owner remains unresolved. The bounded Unified post-Reset search has the separate completion-selection contract in Section 4.7.

### 4.4 Mode B / normal ownership

After a confirmed Reaction, normal search uses the running directional context and the required First color. A confirmation main candle may itself seed the next Mode-B First only when the post-confirmation remainder does not first Reset the just-confirmed structure. The complete confirmation candle can be the next First when its market color has the required role; post-event chronology still controls which prices are eligible for the new boundary.

### 4.5 Exact confirmation and published box

If the Break main candle owns the full-main-candle opposite extreme, only lower-TF prices at or before the first strict confirmation may define the published opposite edge. Later prices in that same main candle cannot retroactively alter Reaction/Order geometry. If lower-TF chronology cannot prove a refinement, detector geometry is retained rather than guessed. Equal eligible extremes retain the earliest main-candle owner.

### 4.6 Reset

A confirmed Bullish Reaction resets only on the first strict `Low < confirmed BoxBottom` event. Equality is not Reset. When Reset and confirmation/break activity share a main candle, selected lower-TF ordering decides which event owns the state transition. Reset reopens **same-direction** Reaction ownership; opposite-direction patterns do not gate that search. A Reset event with an exact lower-TF second exposes that exact second; otherwise the owning main-candle start is the fallback representation.

### 4.7 Post-Reset structural owner vs geometry-only evidence

After Reset, `_first_direct_same_direction_after_reset` scans eligible First candidates in chronological First-index order within the configured end index. It returns a candidate only if confirmation wins before strict loss of its frozen owning boundary. If invalidation wins first, candidates with First indexes at or before that invalidation main index are blocked. A candidate unfinished at the bounded end is skipped, so a later eligible candidate that completes healthily may be returned. The standalone initial Mode-A WAITING state retains its selected unfinished structural owner. The returned healthy result joins the canonical same-direction Reaction stream. `_first_geometry_after_reset` separately returns complete geometry without lifecycle acceptance; geometry alone cannot create Order_A.

### 4.8 Internal Reaction ownership

Cross-direction internal protection is determined after both directions exist. A candidate is internal only when its temporal/box structure is contained by a healthy opposite Reaction and the complete lower-timeframe physical path through its confirmation remains inside the protecting box. Internal identity affects behavior/public ownership; it does not delete historical calculation evidence or renumber the canonical Reaction stream.

## 5. Blue — ACTIVE Bullish specification

### 5.1 Inputs and reference level

Blue consumes canonical Bullish Reactions and Bullish Resets. For each Reaction, the scale reference is the Mode-A boundary when present; otherwise it is the previous Reaction opposite edge. The 0.618 level is `BoxTop − 0.618 × (BoxTop − reference)`.

### 5.2 Scale strikes

Within Reaction First..Break inclusive, a new strike requires a strictly lower `Low` than the previous confirmed strike (or than the Fibonacci level for the first strike). Pending strikes confirm on a `GREEN` main candle. A pending strike reaching the Break candle may confirm intrabar only from lower-TF chronology through the strict Reaction confirmation lower-timeframe row, inclusive; the decisive extreme is the most directional eligible lower-TF extreme.

A Scale Blue is emitted when strike count increases and spacing ownership permits it (first Blue, or at least one healthy Reaction since the previous Blue). Its source is the decisive strike; line price is `Low + (High − Low) / 3` and its drawing interval is one timeframe before/after the source time.

### 5.3 Reset Blue and double-stop calculation validity

A Reset Blue is sourced by the Reset main candle, with source extreme `Low`, broken level from Reset, and line price `Low + (High − Low) / 5`. If the prior Blue first strict-stops on that same Reset candle and the Reset source extends strictly farther in the Bullish direction than the prior Blue source extreme, the new Reset Blue is marked `calculation_valid=False`. That invalid line remains calculation evidence for the A double-stop route but is excluded from public Blue output.

### 5.4 Internal/public Blue

A Blue becomes behavior-internal when its owning Reaction is internal, or when both the source extreme and rendered line price lie strictly inside the same protected healthy Reaction. Drawing offset alone does not create internal ownership. Public Blue is exactly `calculation_valid and not behavior_internal`.

## 6. A — ACTIVE Bullish specification

### 6.1 Blue state and strict stops

A builds an immutable `BlueState` ledger from all Blue calculation state. Blue formation is exact: Scale Blue forms at its Reaction confirmation; Reset Blue uses the first strict lower-TF crossing of its broken level when available. Each Blue stop is the first strict Bullish crossing of its `source_extreme`; equality does not stop a Blue.

### 6.2 Ordinary adjacent-Blue route

Ordinary A evaluates adjacent calculation-valid Blue states. A pair may trigger through the established direct or inherited-stop route. When the first Blue stopped before the second formed, continuation geometry is frozen over the owning interval; inherited-stop ownership uses the complete stop-candle through the aligned Reaction Break candle. Directional source selection is the minimum Low and strict comparisons preserve chronology. Exact equal-event ties use deterministic ordering; the second/current Blue may be reused for the next adjacent pair only when the current A's first strict stop and the next Blue formation satisfy the source lifecycle gate.

### 6.3 Double-stop route

A Reset Blue marked calculation-invalid by the Blue double-stop rule can create the special A route with the previous valid Blue only when the previous Blue's first strict stop belongs to the invalid Reset Blue source candle. The route then requires the first qualifying same-direction canonical Reaction after the trigger chronology. A special route cannot duplicate a Reaction already owned by ordinary A, and earlier ordinary A lifecycle may suppress the special route when its first stop already completed before the special Reaction.

### 6.4 Reaction confirmation and A source freeze

After a valid Blue-pair trigger, the first qualifying canonical Bullish Reaction confirms A. The A source/price is the minimum Low from the trigger main-candle open through the exact lower-TF Reaction confirmation, inclusive. Prices later in the same Break candle are outside A ownership and cannot move the source retroactively. Ties retain the earliest source unless the owning helper explicitly states otherwise.

### 6.5 A stop and lifecycle handoff

A itself stops on the first strict Bullish crossing after its confirming Reaction. A historical stop before a route's `not_before` boundary belongs to the previous cycle; a later recross of the same level cannot be reinterpreted as the new cycle's first stop. The stop event opens S space.

## 7. S — ACTIVE Bullish specification

### 7.1 General A→S gate

Only A candidates outside an already-owned S continuation are eligible. S begins at A's first strict Bullish stop. If the next A confirmation is already reached at/before that handoff, the stale A does not open S. The detector audits the stopped A's first physical Order_A independently before choosing the S route.

A decided S normally owns subsequent A continuation. A newly built Reset-Blue/Reset-Blue pair may preempt that ownership only when both Blue sources are born after the S handoff, Blue-1 stops before Blue-2 forms, the A source is Blue-2's stop candle, and the pair is actually Reset/Reset. A trigger that begins strictly after the exact S ownership handoff is independently eligible.

### 7.2 Order-free Type-3 S Blue

Type-3 is an opposite-Reset-leg route available after A stop and before the first Order deadline. The opposite Reaction owning the Reset must have confirmed by the A-stop event and must not already have Reset before that A stop. Candidate geometry spans the **complete opposite Reaction Break main candle through the Reset main candle**, inclusive, and selects the minimum Low with **last-candle ownership on equality**. After Reset, the first strict Bullish cross of that candidate wins only if at least one ordinary same-direction Reaction confirms after A stop and no later than the cross. Earliest valid Type-3 decision wins.

### 7.3 Order-free Type-4 S Blue

Type-4 is the same-direction Reaction continuation available after A stop only while no opposite Order has formed. For every aligned Bullish Reaction confirmed before the Order deadline, candidate geometry spans the A-stop main candle through that Reaction Break main candle, inclusive, selects the minimum Low and assigns equality to the **last** candidate candle. Search begins at the maximum of A-stop event, aligned Reaction confirmation and candidate formation event. That lower-timeframe start is inclusive. The next aligned Reaction confirmation and Order deadline are exclusive upper bounds. The first strict Bullish cross creates S Blue only when a public calculation-valid Blue formed from the candidate source through that cross. If a candidate crosses without qualifying Blue, no S is created from it; the next aligned Reaction rebuilds a fresh candidate from the same A-stop origin.

Type-3 and Type-4 are independent. Earlier exact decision event wins; Type-3 owns only a true exact-event tie.

### 7.4 Order-backed Simple and Advanced routes

The first physical opposite Order_A owned by the stopped A is immutable for that A; later native Reactions do not refresh it merely because they are newer. Candidate timing first applies established price geometry. Exact event chronology may reclassify an apparent after-Order Simple candidate as pre-Order only when its candidate event is strictly before Order First; equality belongs to after-Order. A valid nested same-direction Reaction wholly contained in the physical opposite Order, with aligned confirmation at or before Order confirmation, owns the **Advanced** path and cannot be stolen by the pre-Order Simple chronology optimization.

For pre-Order Simple, candidate geometry spans A-stop through Order First with the A-stop candle restricted to lower-TF prices at/after the exact A-stop event. For post-Order Simple, the first aligned Reaction after Order confirmation is used and candidate geometry spans Order Break through aligned Reaction Break inclusive with last-on-equality ownership. Advanced uses the directionally relevant opposite Order box source after a nested aligned Reaction confirms.

### 7.5 S decision race

After Order confirmation, two strict lower-TF events compete:

- physical Order stop: `High > OrderStop` → **S Red**;
- S candidate strict Bullish cross → **S Blue** only after an aligned Reset Blue formation or an ordinary aligned Reaction completion qualifies the candidate.

An exact same lower-TF position for both crossings produces no decision. Otherwise the earlier event wins. The legacy pre-Order Simple fallback may initially observe an unqualified candidate cross; if later qualification exists by that exact event it becomes Blue, otherwise the fallback path is rebuilt through normal ownership rather than inventing a family.

When a Red decision wins, Red source geometry is recalculated from Order Break through the Red decision main candle unless the accepted pre-Order source is itself authoritative.

### 7.6 Shared accepted-Order stop reconciliation

After E/OrderAudit accepts physical Orders, an open S may be converted to Red by **any** accepted physical Order whose strict stop occurs at or after the frozen S source main-candle start and strictly before S's current decision; the Order confirmation must be strictly earlier than its stop. Parent identity is irrelevant to use; physical identity is authoritative. Candidates are deduplicated by `(FirstIndex, BreakIndex)`, ordered by `(stopCrossEvent, confirmation, FirstIndex, BreakIndex)`, and provenance remains attached to the Order that created it.

## 8. E — ACTIVE Bullish specification

### 8.1 Parent stop and E-space opening

Every E cycle starts only after the first strict Bullish stop of an accepted S/E parent. For an E parent, a stop search begins at its decision event, so E cannot stop before the Order-stop event that confirmed it. Sequence/StopAll boundaries may later reinterpret parent type, but do not invent a different price event.

### 8.2 Physical Order choices

At each parent stop, E considers physical Orders from these routes: direct parent-stop Order_A, an S-carried unconsumed Order, a gate-owned initial A Order, carried-live accepted identity, post-stop accepted-live identity, and accepted Order_B reset-leg identities. `parent-stop` and `reset-leg` are creation causes; `carried-live` / `accepted-live` are use routes only. A candidate must possess an exact strict Order stop. Winner is earliest stop event; for an exact same stop event the larger Order First index wins (`-FirstIndex` tie key). Sequence reset boundaries may invalidate an Order crossing that would span a hard reset.

### 8.3 E source and decision

`decision_event = max(parent_stop_event, order_stop_event)`. The E source is the minimum Low across the **complete main candle containing the parent stop through the complete main candle containing the Order stop**, inclusive. Lower-TF chronology decides whether stops occurred; it does not truncate either E boundary candle's OHLC. Strict-better replacement retains the earliest equal source.

### 8.4 Recursive family/number lifecycle

Every fully formed accepted S starts a provisional E1 chain in S color. Recursive children are built after the preceding E's strict stop. Reconciliation is chronological: a stopped E leaves the active set but remains historical output. Family follows the accepted stopped parent. Red family outranks Blue at a shared physical source; within equal behavioral priority exact decision chronology is the tie-breaker. When stopped members of the same accepted family exist, the next number is `max(stopped family number)+1`; otherwise the family starts at 1. An active Red E cannot be superseded by S; a Red S may supersede a Blue E under the source lifecycle rules, while Blue S cannot steal an active E continuation.

### 8.5 Consumed S evidence and independent roots

A suppressed/non-public S can remain calculation evidence for continuation of a stopped larger E when lifecycle ownership proves it belongs to that continuation. Its first E inherits the stopped larger E's reconciled family and next number, then recursive children are rebuilt natively. Separately, each accepted stopped S may retain an independent direct E1 root. A same-source accepted E owns that physical source and prevents a provisional S at that source from manufacturing a competing later root. Explicitly invalid S evidence cannot create cross-family competing root provenance when native E continuation already owns the source.

### 8.6 Same-source reconciliation and OrderAudit rebuild

At one physical E source, Red E outranks Blue E; within the same family higher number wins; exact remaining ties preserve the earlier accepted object. After reconciliation, the canonical Order ledger is rebuilt from the accepted E state. Valid parent-stop Order_A identities are retained even if later visibility changes their consuming owner. External restoration/continuation replacement must resynchronize OrderAudit before serialization.

## 9. Order_A — ACTIVE canonical physical parent-stop rule

### 9.1 Creation gate

Order_A is the physical `parent-stop` route opened by an accepted strict behavior stop. A bounded/direct geometry candidate may create Order_A **only** when its `(FirstIndex, BreakIndex)` exists in the canonical opposite-direction (Bearish) Reaction stream. Geometry absent from that canonical registry remains internal evidence and cannot enter OrderAudit as Order_A or receive a synthetic reaction number.

After a stopped A, the first canonical opposite Order is immutable for that A. For S/E parent stops, direct bounded geometry may be evaluated, but canonical membership remains mandatory. One exact parent-stop cause may own at most one physical Order_A; when multiple candidates compete, earliest canonical confirmation, then FirstIndex, then BreakIndex owns the cause.

### 9.2 Canonical stop

Order stop provenance comes from `MarketChronology.canonical_order_stop`. For Mode A it uses the canonical leg-head/floor context required by that opposite Reaction; for Mode B it uses the previous healthy opposite Reaction's outer edge under the established chronology. The Order's exact strict stop uses the **opposite direction** predicate; for this Bullish calculation that is `High > OrderStop`. Equality does not stop an Order.

### 9.3 Parent validity and retention

An S explicitly identified in invalid_s_root_identities is calculation evidence, not an accepted S parent, and cannot create or retain a `parent-stop` Order_A cause. An E derived from that S may be accepted only when its chosen physical Order has a valid creating cause independent of the invalid S. This applies to ordinary chain reconciliation, consumed-S continuation, and independent-root restoration; provisional geometry alone cannot publish an E or StopAll. Once a valid canonical Order_A enters the identity-keyed ledger, later E/lifecycle reconciliation may change who uses it but cannot delete that physical identity/provenance. A shared Order_B identity may add reset-leg provenance without erasing valid parent-stop provenance.

## 10. Order_B — ACTIVE Bullish reset-leg rule

### 10.1 Eligibility and post-stop owner

Order_B is eligible only after an accepted lifecycle stop (`A`, `S`, `E`, or `StopAll`) selected by the accepted lifecycle owner of the stopped main candle. The stop opens eligibility; it is **not** the geometric LL anchor.

### 10.2 Geometric behavior anchor

For each reset Bullish Reaction, choose the latest accepted behavior source that exists strictly before the Reaction FirstRed candle, independent of current dominance. Valid anchor families are A/S/E/StopAll. When several lifecycle projections share exactly one source candle, lifecycle priority and number resolve only that exact-source tie.

### 10.3 LL construction and extension

Use the closed main-candle range from anchor behavior source through reset Reaction FirstRed, inclusive:

`LL = minimum Low(anchor candle .. reset Reaction FirstRed)`

Only a strict better Low replaces the current source, so equal extremes retain the earliest source. The LL source must be strictly before the reset Reaction FirstRed. It must also extend beyond the anchor itself: the LL must be strictly below the anchor behavior `Low`; equality invalidates the setup.

### 10.4 Reset and strict break

The reset Reaction must first produce its canonical Reset. Search **strictly after** that exact Reset event for the first lower-TF `Low < LL`. Equality is not a break. This exact lower-TF timestamp is `strict_break_time`.

### 10.5 Accepted-A expiry

Let the next accepted A formation after the reset Reaction First be `A_next`. If `A_next <= strict_break_time`, the pending reset leg expires. A is upstream of Order_B feedback, so this hard expiry prevents a stale S/E/StopAll setup from firing inside a newer A lifecycle.

### 10.6 Physical canonical opposite Reaction

After the strict break, choose the first canonical Bearish Reaction satisfying both:

`strict_break_time <= FirstTime`

`strict_break_time < ConfirmationTime`

Thus **FirstTime equality is valid**, while the price break and confirmation remain strict. Canonical-Reaction membership is mandatory; geometry-only evidence cannot become Order_B.

### 10.7 Provenance and identity

Order_B records post-stop behavior, geometric anchor type/source/extreme, reset Reaction identity/confirmation, Reset index/broken level/time, frozen LL boundary/source, exact strict break, and final physical opposite Reaction identity/confirmation. Physical Order identity remains `(FirstIndex, BreakIndex)`. Multiple reset-leg causes may merge into one identity; they do not create duplicate physical Orders.

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

An accepted unrelated higher-priority behavior replaces the owner at its source time and starts at count `1`. A direct E child first resolves the strict stop of its exact armed parent, even when its retrospectively chosen source candle begins at or before that stop. A larger number within the same E family advances the E owner; a smaller number does not. Lower-priority accepted objects may remain valid calculation/output objects, but cannot count, remain armed, or trigger StopAll behind the current owner. There is one active exact owner and no independent Blue repetition ledger.

### 12.3 Chronological strict stop and E donor

The armed owner's stop is the first strict 5-second crossing at or after its latest occurrence's decision event. A stop must precede replacement by an unrelated higher-priority behavior to belong to the former owner; an E directly caused by that stop is resolved as a donor before it replaces its parent. A completed earlier stop is frozen as pending historical evidence if no eligible donor exists at that transition; later replacement cannot cancel it. This pending completed gate is not a second occurrence counter and cannot re-arm a displaced behavior.

At an incoming E, a completed owner stop strictly before the E source time creates `StopAll1` through `sequence-group-stop`; the incoming E supplies physical geometry and Order provenance regardless of family. There is one narrow causal exception: the E may be the direct child of the armed current owner whose first strict stop is its exact `parentStopEventTime`, even when that stop is at or after the E's retrospective `sourceTime`. The match requires parent type, source index/time and price to identify the owner's latest occurrence exactly, and the stop must be no later than the E decision event. An E descended from a different parent cannot revive a displaced owner or use a later unrelated stop. An existing active StopAll that strictly stops at or before the incoming E decision continues to create the next numbered StopAll through `stopall-stop` under its separate historical contract. Its gate precedes the S/E owner gate.

### 12.4 S Red donor and legacy gate name

An accepted S Red whose final accepted `order_mode` is `B` may donate fresh `StopAll1` through the serialized `opposite-s-group-stop` gate only for a completed strict stop of a Blue behavior that was the armed current owner when it stopped. The gate event is the actual lower-timeframe stop, not the S Red decision. If the earlier stopped owner is E, its family and number remain exact in `stoppedBehaviorKey`. A Mode-A S Red cannot use this S-donor gate; the completed stop remains pending for an eligible later donor. The S Red donor's own validity and the stopped owner's eligibility are separate questions.

**HISTORICAL / SUPERSEDED (`5.4.22` and earlier):** accepted Blue occurrences were counted in a parallel ledger independent of dominant-owner transitions. That ledger could promote a lower-priority Blue group after a higher-priority Red owner had formed, or promote without a strict stop. It is not an active rule.

### 12.5 Hard StopAll boundary

Materializing StopAll resets the active exact owner, its count/armed state, and any pending completed stop. Historical S/E and StopAll objects remain available as calculation and output evidence. E receives the accepted StopAll source map through the existing atomic sequence-reset publication; its dependent candidate/carried context caches refresh while immutable physical stop/cross caches and historical accepted causes remain retained. A later lifecycle cannot inherit an earlier count or resurrect a displaced owner.

### 12.6 Cross-stage A/S/E visibility ownership

A, S and E calculations continue to retain internal historical evidence. Public ownership is resolved from exact strict stops, source chronology and shared priority. A source that strictly extends beyond the newest stopped owner can be consumed as the closed owner's next leg head instead of re-entering as equal/smaller behavior; equality stays with the earlier owner. S under a stopped larger owner obeys analogous chronology-first ownership; a higher-priority Red S may supersede a stopped Blue S, while equal/lower candidates remain owned by the prior lifecycle. Final E/StopAll source occupancy removes duplicate A/S labels on the same physical source, while referenced historical parents are retained for lineage closure.

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

The envelope contains `engine`, `version`, `pipelineVersion`, `blueLineVersion`, `aVersion`, `sVersion`, `eVersion`, `stopAllVersion`, enablement booleans, `timeframe`, `actualFrom`, `actualTo`, `directions`, and runtime `timings`. Each requested direction owns its own Reaction/Reset/Blue/A/S/E/StopAll/OrderAudit arrays.

### 13.4 Optional Bridge Output

`--bridge-output` adds a read-only projection built only from finalized calculation selections and canonical OrderAudit. It may validate a recorded strict event, but it must not search for a substitute trading event or mutate detector/lifecycle state. Physical Order joins use `(FirstIndex, BreakIndex)` and exact accepted causes, never list position.

### 13.5 Complete module/class symbol and schema coverage

This index is regenerated mechanically from the exact Current Source AST for this Reference revision. Its coverage contract is explicit: it enumerates every module-level assignment/type alias/cache/index, every module-level function, every class, every annotated class/dataclass field, every class method/property implementation, and every nested implementation function/closure. Imported names and local variables are not separately enumerated because they are not Source-defined module/class symbols; they remain byte-exact in Section 16.

The index is descriptive only. It does not create algorithm behavior and does not supersede the semantic stage rules above.

#### `__init__.py`
- **Module-level symbols/assignments:** _none_
- **Top-level functions:** _none_
- **Classes / schemas:** _none_
- **Nested implementation functions/closures:** _none_

#### `bridge/__init__.py`
- **Module-level symbols/assignments:** _none_
- **Top-level functions:** _none_
- **Classes / schemas:** _none_
- **Nested implementation functions/closures:** _none_

#### `bridge/trading_pipeline.py`
- **Module-level symbols/assignments:** `_ENGINE_ROOT` (L31), `_PIPELINE_DIR` (L32), `_pipeline_dir_text` (L33), `_DTFMT` (L40), `TRADING_PIPELINE_VERSION` (L43), `TRADING_PIPELINE_IMPLEMENTATION_VERSION` (L44), `TRADING_PIPELINE_LAST_MODIFIED` (L45), `TEHRAN` (L47), `_local_dt_cache` (L84), `_epoch_cache` (L96), `_display_epoch_cache` (L108)
- **Top-level functions:** `emit_progress` (L50), `timed` (L58), `load_module` (L70), `load_engine` (L80), `local_datetime` (L87), `epoch` (L99), `display_epoch` (L111), `build_candle_buckets` (L123), `build_candle_objects` (L181), `_index_selected` (L211), `select_reaction_serialization_items` (L219), `serialize` (L242), `serialize_blue_lines` (L286), `serialize_a_zones` (L306), `serialize_s_zones` (L333), `serialize_e_zones` (L398), `serialize_stopalls` (L441), `bridge_datetime` (L508), `bridge_direction` (L522), `bridge_mode` (L526), `bridge_color` (L530), `_bridge_horizon` (L536), `_bridge_in_horizon` (L543), `_bridge_proven_strict_event` (L547), `_bridge_stop_view` (L587), `_bridge_reaction_confirmation` (L607), `_bridge_order_identity` (L631), `_bridge_parent_stop` (L833), `_bridge_a_stop` (L854), `_bridge_behavior_stop` (L875), `_bridge_blue_formation` (L890), `_bridge_project_reaction` (L913), `_bridge_project_reset` (L956), `_bridge_project_blue` (L979), `_bridge_full_lines_by_ordinal` (L1015), `_bridge_project_a` (L1027), `_bridge_project_s` (L1117), `_bridge_source_index` (L1173), `_bridge_parent_behavior_for_e` (L1181), `_bridge_project_e` (L1225), `_bridge_project_stopall` (L1272), `_bridge_audit_order_key` (L1341), `build_bridge_output` (L1351), `validate_order_audit_bridge` (L1456), `serialize_order_audit` (L1524), `parse_arguments` (L1597), `load_engines` (L1669), `prepare_market_context` (L1703), `create_e_detector` (L1819), `calculate_full_direction_state` (L1865), `calculate_direction_with_order_b_feedback` (L2181), `prepare_pipeline_state` (L2235), `calculate_direction_range_state` (L2382), `finalize_direction_visibility` (L2484), `serialize_direction_payload` (L2700), `build_direction_output` (L2841), `build_response_payload` (L2866), `main` (L2919)
- **Classes / schemas:**
  - **`BridgeProjection`** (L639)
    - fields: _none_
    - methods/properties: `__init__` (L647), `physical_order` (L666), `parent_order` (L711), `current_order` (L718), `order_audit` (L773)
  - **`EngineBundle`** (L1578)
    - fields: `reaction` (L1579), `blue_line` (L1580), `a_zone` (L1581), `s_zone` (L1582), `e_zone` (L1583), `lifecycle` (L1584)
    - methods/properties: _none_
  - **`MarketContext`** (L1588)
    - fields: `seconds` (L1589), `candles` (L1590), `lower_index` (L1591), `chronology` (L1592), `start_index` (L1593), `end_index` (L1594)
    - methods/properties: _none_
  - **`PipelineState`** (L1784)
    - fields: `directions` (L1787), `results` (L1788), `reusable_full_context` (L1789), `initial_order_geometry` (L1790), `internal_reaction_identities` (L1791), `full_e_zones` (L1792), `full_e_detectors` (L1793), `full_s_detectors` (L1794), `full_lines_by_direction` (L1795), `full_a_by_direction` (L1796), `invalid_a_identities_by_direction` (L1797), `invalid_s_identities_by_direction` (L1798), `full_s_by_direction` (L1799), `full_s_candidates_by_direction` (L1800)
    - methods/properties: _none_
  - **`FullDirectionState`** (L1804)
    - fields: `e_zones` (L1807), `e_detector` (L1808), `s_detector` (L1809), `blue_lines` (L1810), `a_zones` (L1811), `invalid_a_identities` (L1812), `invalid_s_identities` (L1813), `s_zones` (L1814), `s_candidates` (L1815), `initial_s_zones` (L1816)
    - methods/properties: _none_
  - **`DirectionRangeState`** (L2352)
    - fields: `blue_lines` (L2355), `a_zones` (L2356), `s_candidates` (L2357), `accepted_s_zones` (L2358), `e_zones` (L2359), `invalid_a_identities` (L2360), `invalid_s_identities` (L2361)
    - methods/properties: _none_
  - **`DirectionVisibilityState`** (L2365)
    - fields: `blue_lines` (L2368), `a_zones` (L2369), `s_zones` (L2370), `e_zones` (L2371), `stopalls` (L2372), `prepared_order_audit` (L2373), `projection_s_zones` (L2377), `projection_e_zones` (L2378), `projection_stopalls` (L2379)
    - methods/properties: _none_
- **Nested implementation functions/closures:** `build_candle_buckets.<locals>.cached_decimal` (L132), `create_e_detector.<locals>.direct_geometry` (L1837), `serialize_direction_payload.<locals>.serialize_reactions_from_one_selection` (L2759), `serialize_direction_payload.<locals>.build_payload` (L2800)

#### `pipeline/__init__.py`
- **Module-level symbols/assignments:** `__all__` (L12)
- **Top-level functions:** _none_
- **Classes / schemas:** _none_
- **Nested implementation functions/closures:** _none_

#### `pipeline/a_zone_detector.py`
- **Module-level symbols/assignments:** `A_ZONE_VERSION` (L20), `A_ZONE_LAST_MODIFIED_DATE` (L21)
- **Top-level functions:** `detect_a_zones` (L798)
- **Classes / schemas:**
  - **`BlueState`** (L25)
    - fields: `ordinal` (L26), `line` (L27), `formation_index` (L28), `formation_time` (L29), `stop_index` (L30), `stop_time` (L31), `stop_event_time` (L32), `stop_level` (L33), `stop_event_extreme` (L34)
    - methods/properties: _none_
  - **`AZone`** (L38)
    - fields: `direction` (L39), `blue_1_ordinal` (L40), `blue_2_ordinal` (L41), `blue_1_source_time` (L42), `blue_2_source_time` (L43), `blue_1_stop_time` (L44), `blue_2_stop_time` (L45), `blue_1_stop_level` (L46), `blue_2_stop_level` (L47), `continuation_level` (L48), `continuation_source_index` (L49), `continuation_source_time` (L50), `trigger_index` (L51), `trigger_time` (L52), `trigger_event_time` (L53), `reaction_number` (L54), `reaction_first_time` (L55), `reaction_break_time` (L56), `source_index` (L57), `source_time` (L58), `price` (L59), `formation_route` (L62), `blue_1_stop_event_time` (L63), `blue_2_stop_event_time` (L64)
    - methods/properties: _none_
  - **`AZoneDetector`** (L67)
    - fields: _none_
    - methods/properties: `__init__` (L68), `extreme_name` (L108), `_strict_cross` (L111), `_better` (L114), `_main_index` (L117), `_lower_window` (L120), `_first_crossing` (L125), `_range_extreme` (L167), `_formation` (L201), `_reset_formation_time` (L218), `_build_blue_states` (L230), `_double_stop_a_candidates` (L259), `_pair_trigger` (L322), `_reaction_confirmation_time` (L482), `_first_reaction_after` (L487), `_inherited_stop` (L504), `_a_source` (L554), `_detect_ordinary_a` (L575), `_filter_special_a` (L696), `detect` (L760), `_a_was_stopped_before` (L772)
- **Nested implementation functions/closures:** _none_

#### `pipeline/blue_line_detector.py`
- **Module-level symbols/assignments:** `BLUE_LINE_VERSION` (L18), `FIBONACCI_RATIO` (L19)
- **Top-level functions:** `_is_color` (L48), `_main_candle` (L52), `_stops_on_index` (L59), `fibonacci_level` (L75), `_intrabar_pending_confirmation` (L84), `count_scale_strikes` (L139), `_build_scale_blue_line` (L207), `_build_reset_blue_line` (L245), `detect_blue_lines` (L299), `public_blue_lines` (L407), `mark_internal_blue_lines` (L416)
- **Classes / schemas:**
  - **`ScaleStrike`** (L23)
    - fields: `source_index` (L24), `source_time` (L25), `extreme` (L26)
    - methods/properties: _none_
  - **`BlueLine`** (L30)
    - fields: `direction` (L31), `kind` (L32), `reaction_number` (L33), `previous_strike_count` (L34), `strike_count` (L35), `fibonacci_level` (L36), `source_index` (L37), `source_time` (L38), `source_extreme` (L39), `broken_level` (L40), `line_price` (L41), `start_time` (L42), `end_time` (L43), `calculation_valid` (L44), `behavior_internal` (L45)
    - methods/properties: _none_
- **Nested implementation functions/closures:** `mark_internal_blue_lines.<locals>.owner_is_internal` (L429), `mark_internal_blue_lines.<locals>.geometry_is_internal` (L435)

#### `pipeline/core_utils.py`
- **Module-level symbols/assignments:** `CORE_UTILS_VERSION` (L5), `OrderIdentity` (L16)
- **Top-level functions:** `as_decimal` (L11), `order_identity` (L19), `reaction_identity` (L24)
- **Classes / schemas:** _none_
- **Nested implementation functions/closures:** _none_

#### `pipeline/direction_policy.py`
- **Module-level symbols/assignments:** `DIRECTION_POLICY_VERSION` (L11), `Direction` (L17), `BULLISH` (L57), `BEARISH` (L64)
- **Top-level functions:** `policy_for` (L49)
- **Classes / schemas:**
  - **`DirectionPolicy`** (L21)
    - fields: `direction` (L22), `extreme_attr` (L23), `opposite_extreme_attr` (L24), `first_reaction_tag` (L25), `context_tag` (L26)
    - methods/properties: `opposite_direction` (L29), `strict_cross` (L32), `better_extreme` (L35), `choose_extreme` (L38), `confirmation_cross` (L41)
- **Nested implementation functions/closures:** _none_

#### `pipeline/e_zone_detector.py`
- **Module-level symbols/assignments:** `E_ZONE_VERSION` (L25), `E_ZONE_IMPLEMENTATION_VERSION` (L26), `E_ZONE_LAST_MODIFIED` (L27)
- **Top-level functions:** `detect_e_zones` (L1111)
- **Classes / schemas:**
  - **`EZone`** (L31)
    - fields: `direction` (L32), `family` (L33), `number` (L34), `parent_type` (L35), `parent_source_index` (L36), `parent_source_time` (L37), `parent_price` (L38), `parent_stop_index` (L39), `parent_stop_time` (L40), `parent_stop_event_time` (L41), `order_direction` (L42), `order_reaction_number` (L43), `order_mode` (L44), `order_causes` (L45), `order_parent_stop_cause_time` (L46), `order_first_index` (L47), `order_first_time` (L48), `order_break_index` (L49), `order_break_time` (L50), `order_confirmation_time` (L51), `order_box_top` (L52), `order_box_top_source_index` (L53), `order_box_top_source_time` (L54), `order_box_bottom` (L55), `order_box_bottom_source_index` (L56), `order_box_bottom_source_time` (L57), `order_stop_level` (L58), `order_stop_source_index` (L59), `order_stop_source_time` (L60), `source_index` (L61), `source_time` (L62), `price` (L63), `decision_index` (L64), `decision_time` (L65), `decision_event_time` (L66)
    - methods/properties: _none_
  - **`EZoneDetector`** (L69)
    - fields: _none_
    - methods/properties: `__init__` (L70), `sequence_resets` (L226), `sequence_resets` (L230), `_reset_time` (L244), `_main_index` (L247), `_first_cross_position` (L251), `_stop_value` (L268), `_build_extreme_sparse` (L271), `_extreme_position` (L300), `_first_parent_stop` (L320), `_confirmation_for` (L333), `_confirmation` (L336), `_reaction_first_time` (L339), `_parent_stop` (L343), `parent_stop` (L351), `_extreme_between` (L358), `_zone` (L374), `set_consumed_s_evidence` (L477), `_apply_consumed_s_evidence` (L489), `continuation_chain_from_s` (L507), `replace_with_earlier_continuation` (L557), `resolve_same_source_conflicts` (L600), `restore_independent_s_roots` (L644), `_invalid_s_without_order_cause` (L705), `_discover_candidate_chains` (L729), `_reconcile_candidate_chains` (L821), `detect` (L1098)
- **Nested implementation functions/closures:** `EZoneDetector.replace_with_earlier_continuation.<locals>.descends_from_owner` (L566), `EZoneDetector.resolve_same_source_conflicts.<locals>.outranks` (L618), `EZoneDetector._reconcile_candidate_chains.<locals>.valid_order` (L852), `EZoneDetector._reconcile_candidate_chains.<locals>.parent_active` (L858), `EZoneDetector._reconcile_candidate_chains.<locals>.stopped_by` (L931), `EZoneDetector._reconcile_candidate_chains.<locals>.collect_lineage` (L1073)

#### `pipeline/lifecycle_engine.py`
- **Module-level symbols/assignments:** `STOP_ALL_VERSION` (L24), `STOP_ALL_IMPLEMENTATION_VERSION` (L25), `STOP_ALL_LAST_MODIFIED` (L26), `SEQUENCE_PRIORITY` (L29)
- **Top-level functions:** `sequence_priority` (L37), `detect_stopalls` (L478), `resolve_order_context` (L491), `visible_a_zones_after_s_stops` (L543), `module_priority` (L559), `module_identity` (L573), `module_stop_event` (L582), `strictly_beyond_boundary` (L596), `dominant_module` (L601), `split_a_zones_by_dominant_stops` (L613), `blocked_orders_while_invalid_leg_heads_are_live` (L816), `consumed_s_evidence_after_larger_stop` (L839), `s_zones_for_module_engines` (L981), `s_zones_for_stopall` (L1011), `visible_s_zones_after_module_resets` (L1030), `reconcile_stopall_lifecycle` (L1208), `visible_a_zones_after_module_boundaries` (L1241), `reaction_number_is_internal` (L1288), `point_is_inside_healthy_reaction` (L1302), `filter_internal_behavior_outputs` (L1325), `finalize_behavior_visibility` (L1338), `visible_a_zones` (L1433)
- **Classes / schemas:**
  - **`StopAll`** (L43)
    - fields: `direction` (L44), `number` (L45), `source_index` (L46), `source_time` (L47), `price` (L48), `decision_index` (L49), `decision_time` (L50), `decision_event_time` (L51), `gate_type` (L52), `gate_event_time` (L53), `stopped_behavior_type` (L54), `stopped_behavior_key` (L55), `stopped_behavior_count` (L56), `underlying_e_family` (L57), `underlying_e_number` (L58), `order_direction` (L59), `order_reaction_number` (L60), `order_mode` (L61), `order_causes` (L62), `order_parent_stop_cause_time` (L63), `order_first_index` (L64), `order_first_time` (L65), `order_break_index` (L66), `order_break_time` (L67), `order_confirmation_time` (L68), `order_box_top` (L69), `order_box_top_source_index` (L70), `order_box_top_source_time` (L71), `order_box_bottom` (L72), `order_box_bottom_source_index` (L73), `order_box_bottom_source_time` (L74), `order_stop_level` (L75), `order_stop_source_index` (L76), `order_stop_source_time` (L77), `stop_index` (L78), `stop_time` (L79), `stop_event_time` (L80), `donor_type` (L85), `donor_source_index` (L86), `donor_source_time` (L87), `donor_color` (L88), `donor_number` (L89), `donor_price` (L90), `donor_stop_time` (L91), `donor_stop_event_time` (L92)
    - methods/properties: _none_
  - **`_DominantBehavior`** (L96)
    - fields: `kind` (L99), `family` (L100), `number` (L101), `count` (L102), `latest` (L103)
    - methods/properties: `priority` (L106), `armed` (L110), `key` (L114)
  - **`StopAllDetector`** (L121)
    - fields: _none_
    - methods/properties: `__init__` (L122), `_strict_stop` (L143), `_dominates_e` (L160), `_stopall_from_e` (L169), `_optional_int` (L228), `_optional_decimal` (L232), `_stopall_from_s` (L235), `detect` (L323)
- **Nested implementation functions/closures:** `StopAllDetector.detect.<locals>.armed_stop_before` (L335), `StopAllDetector.detect.<locals>.accept` (L367), `StopAllDetector.detect.<locals>.process_s_event` (L381), `visible_s_zones_after_module_resets.<locals>.cached_stop_event` (L1059)

#### `pipeline/order_audit_engine.py`
- **Module-level symbols/assignments:** `ORDER_AUDIT_ENGINE_VERSION` (L14), `ORDER_AUDIT_ENGINE_LAST_MODIFIED` (L15), `OrderMatch` (L406)
- **Top-level functions:** `dominant_post_behavior_stops` (L55), `order_b_reset_event_time` (L101), `discover_order_b_reset_legs` (L132), `discover_accepted_order_b_reset_legs` (L328), `order_b_leg_identity` (L413), `_parent_stop_cause_key` (L1614), `_collect_s_ledger_entries` (L1623), `_collect_e_ledger_entries` (L1655), `_merge_prepared_identities` (L1678), `_single_owner_parent_stop_causes` (L1721), `prepare_order_audit` (L1759), `accepted_audit_entry` (L1779), `order_identity_is_internal` (L1809)
- **Classes / schemas:**
  - **`PostBehaviorStop`** (L18)
    - fields: `behavior_type` (L19), `behavior_source_index` (L20), `behavior_source_time` (L21), `event_time` (L22)
    - methods/properties: _none_
  - **`OrderBBehaviorAnchor`** (L26)
    - fields: `behavior_type` (L27), `behavior_source_index` (L28), `behavior_source_time` (L29), `priority` (L30), `number` (L31)
    - methods/properties: _none_
  - **`OrderBResetLeg`** (L35)
    - fields: `post_stop` (L36), `anchor_behavior_type` (L37), `anchor_behavior_source_index` (L38), `anchor_behavior_source_time` (L39), `anchor_behavior_extreme` (L40), `reset_reaction` (L41), `reset_confirmation_time` (L42), `reset_source_index` (L43), `reset_broken_level` (L44), `reset_time` (L45), `leg_boundary` (L46), `leg_source_index` (L47), `leg_source_time` (L48), `strict_break_time` (L49), `reaction_number` (L50), `physical_reaction` (L51), `physical_confirmation_time` (L52)
    - methods/properties: _none_
  - **`OrderAuditEngineMixin`** (L437)
    - fields: _none_
    - methods/properties: `_order_stop` (L440), `order_stop` (L469), `_first_healthy_direct_geometry` (L476), `_trend_leg_direct_order` (L551), `_direct_parent_stop_order` (L603), `_compute_direct_parent_stop_order` (L620), `_merge_order_candidate` (L693), `_enforce_single_parent_stop_owner` (L727), `order_candidates` (L754), `_first_order` (L843), `_has_sequence_reset_between` (L859), `_index_order_audit_identity` (L870), `_clear_order_audit` (L880), `_invalidate_carried_order_caches` (L886), `_invalidate_post_stop_order_cache` (L893), `register_order_b_reset_legs` (L897), `_register_order_audit` (L964), `visual_order_lifecycle` (L1037), `_cross_order` (L1059), `cross_order` (L1080), `_unconsumed_s_orders` (L1087), `_initial_order_records` (L1124), `_initial_record_match` (L1183), `_initial_order_match` (L1197), `_gate_owned_initial_order` (L1212), `_carried_orders_for_parent` (L1235), `_post_stop_accepted_orders_for_parent` (L1296), `_blocked_by_gate_owned_order` (L1378), `_rebuild_accepted_order_audit` (L1389), `rebuild_accepted_order_audit` (L1575), `ensure_accepted_order_audit` (L1590)
  - **`SOrderAuditMixin`** (L1818)
    - fields: _none_
    - methods/properties: `_first_order_after` (L1821), `_order_matches_after` (L1834), `_record_a_order_audit` (L1856), `_audit_stopped_a` (L1891), `_order_stop` (L1904), `_order_stop_crossed` (L1916), `_shared_order_stop_cross` (L1922)
- **Nested implementation functions/closures:** `OrderAuditEngineMixin._post_stop_accepted_orders_for_parent.<locals>.add_match` (L1310), `OrderAuditEngineMixin._rebuild_accepted_order_audit.<locals>.valid_parent_stop_cause` (L1400)

#### `pipeline/reaction_engine.py`
- **Module-level symbols/assignments:** `REACTION_ENGINE_VERSION` (L21), `REACTION_ENGINE_IMPLEMENTATION_VERSION` (L22), `REACTION_ENGINE_LAST_MODIFIED` (L23), `_ORDER_GATE_CACHE_MAX_ENTRIES` (L25), `_SEQUENCE_TIME_INDEXES` (L27), `_REFLECTED_VIEWS` (L636), `_LOWER_TIMEFRAME_INDEXES` (L932)
- **Top-level functions:** `classify_candle_color` (L94), `opposite_direction` (L99), `mirror_candle` (L563), `mirror_candidate` (L583), `mirror_analysis` (L602), `_reflected_view` (L639), `published_reaction_candidate` (L709), `_decimal_value` (L807), `shared_lower_timeframe_index` (L937), `build_behavior_reaction_views` (L1205), `directional_a_stop_order_finder` (L1316)
- **Classes / schemas:**
  - **`Candle`** (L30)
    - fields: `index` (L31), `timestamp` (L32), `display_time` (L33), `tag` (L34), `open` (L35), `high` (L36), `low` (L37), `close` (L38)
    - methods/properties: _none_
  - **`Candidate`** (L42)
    - fields: `first_idx` (L43), `first_time` (L44), `box_top_source_idx` (L45), `box_top_source_time` (L46), `box_top` (L47), `box_bottom_source_idx` (L48), `box_bottom_source_time` (L49), `box_bottom` (L50), `mode` (L51), `anchor_idx` (L52), `anchor_value` (L53), `leg_boundary_value` (L54), `break_idx` (L55), `break_time` (L56), `intrabar_start` (L57), `cross_direction_origin` (L58), `cross_direction_chain_owner` (L59), `order_gate_decision` (L60), `behavior_public_number` (L61), `behavior_public_box_top` (L62), `behavior_public_box_bottom` (L63), `behavior_confirmation_time` (L64), `behavior_first_time` (L65), `behavior_internal` (L66)
    - methods/properties: _none_
  - **`ResetEvent`** (L70)
    - fields: `index` (L71), `display_time` (L72), `second_time` (L73), `broken_level` (L74), `from_first_idx` (L75)
    - methods/properties: _none_
  - **`IntrabarAnalysis`** (L79)
    - fields: `event_second` (L80), `extreme` (L81), `extreme_source` (L82)
    - methods/properties: _none_
  - **`DetectionResult`** (L86)
    - fields: `direction` (L87), `reactions` (L88), `resets` (L89), `start_index` (L90), `end_index` (L91)
    - methods/properties: _none_
  - **`DetectorBase`** (L104)
    - fields: _none_
    - methods/properties: `__init__` (L105), `_shared_time_index` (L130), `seconds_between` (L140), `main_source_for_time` (L145), `minimum_low` (L158), `maximum_high` (L167)
  - **`BullishDetector`** (L177)
    - fields: _none_
    - methods/properties: `green_run_peak_before` (L178), `breakout_analysis` (L188), `mode_a_invalidation_before_breakout` (L214), `confirmed_reset_before_breakout` (L250), `post_breakout_reset` (L270), `detect` (L285)
  - **`_ReflectedCandles`** (L611)
    - fields: _none_
    - methods/properties: `__init__` (L619), `__len__` (L623), `__getitem__` (L626)
  - **`BearishDetector`** (L649)
    - fields: _none_
    - methods/properties: `__init__` (L657), `red_run_bottom_before` (L671), `breakdown_analysis` (L675), `invalidation_high_break_before_breakdown` (L680), `confirmed_reset_before_breakdown` (L685), `post_breakdown_reset` (L691), `detect` (L698)
  - **`LowerTimeframeIndex`** (L812)
    - fields: _none_
    - methods/properties: `__init__` (L819), `first_less` (L860), `first_greater` (L863), `range_minimum` (L866), `range_maximum` (L870), `_range_query` (L874), `_first` (L912)
  - **`ReflectedLowerTimeframeIndex`** (L950)
    - fields: _none_
    - methods/properties: `__init__` (L955), `first_less` (L959), `first_greater` (L962), `range_minimum` (L965), `range_maximum` (L969)
  - **`MarketChronology`** (L974)
    - fields: _none_
    - methods/properties: `__init__` (L993), `opposite_direction` (L1016), `main_index` (L1020), `lower_bounds` (L1029), `lower_window` (L1040), `_reset_cache_key` (L1047), `_reaction_cache_key` (L1059), `reset_time` (L1073), `reaction_confirmation` (L1092), `canonical_order_stop` (L1140)
  - **`UnifiedReactionDetector`** (L1379)
    - fields: _none_
    - methods/properties: `__init__` (L1389), `bull` (L1421), `bear` (L1429), `_append_reaction` (L1436), `_append_reset` (L1518), `_refine` (L1536), `_candidate_from_confirmation_remainder` (L1557), `_first_initial` (L1642), `_first_direct_same_direction_after_reset` (L1655), `_first_geometry_after_reset` (L1693), `first_geometry_after_reset` (L1746), `_reaction_break_indices` (L1753), `first_order_reaction_after_gate` (L1768), `_earliest_confirmed_geometry` (L1917), `_build_direct_candidate` (L1991), `_scan_direct_candidate` (L2049), `_owner_boundary_before_confirmation` (L2079), `_result` (L2120), `detect` (L2129)
- **Nested implementation functions/closures:** `build_behavior_reaction_views.<locals>.path_is_contained` (L1225), `directional_a_stop_order_finder.<locals>.find` (L1330), `UnifiedReactionDetector.first_order_reaction_after_gate.<locals>.cache_result` (L1784), `UnifiedReactionDetector.first_order_reaction_after_gate.<locals>.confirmed_no_later_than_gate` (L1795)

#### `pipeline/s_zone_detector.py`
- **Module-level symbols/assignments:** `S_ZONE_VERSION` (L22), `S_ZONE_IMPLEMENTATION_VERSION` (L23), `S_ZONE_LAST_MODIFIED` (L24)
- **Top-level functions:** `detect_s_zones` (L1421)
- **Classes / schemas:**
  - **`SZone`** (L28)
    - fields: `direction` (L29), `color` (L30), `formation_type` (L31), `a_ordinal` (L32), `a_source_index` (L33), `a_source_time` (L34), `a_price` (L35), `a_stop_index` (L36), `a_stop_time` (L37), `a_stop_event_time` (L38), `order_direction` (L39), `order_reaction_number` (L40), `order_mode` (L41), `order_first_index` (L42), `order_first_time` (L43), `order_break_index` (L44), `order_break_time` (L45), `order_confirmation_time` (L46), `order_box_top` (L47), `order_box_top_source_index` (L48), `order_box_top_source_time` (L49), `order_box_bottom` (L50), `order_box_bottom_source_index` (L51), `order_box_bottom_source_time` (L52), `order_stop_level` (L53), `order_stop_source_index` (L54), `order_stop_source_time` (L55), `reset_reaction_number` (L56), `reset_time` (L57), `source_index` (L58), `source_time` (L59), `price` (L60), `decision_index` (L61), `decision_time` (L62), `decision_event_time` (L63)
    - methods/properties: _none_
  - **`SZoneDetector`** (L66)
    - fields: _none_
    - methods/properties: `__init__` (L67), `_main_index` (L194), `_lower_window` (L197), `_reaction_confirmation_time` (L202), `reaction_confirmation_time` (L207), `_reset_time` (L214), `_a_confirmation_time` (L217), `_trend_extreme` (L225), `_a_stopped` (L230), `_first_a_stop` (L233), `first_a_stop` (L269), `_resolved_order_backed_zone` (L276), `_candidate_source` (L295), `_candidate_source_last` (L310), `_first_trend_reaction_after_order` (L330), `_nested_trend_reaction` (L342), `_simple_candidate` (L372), `_type3_reset_leg` (L381), `_type3_has_trend_reaction` (L397), `_first_type3` (L406), `_type4_has_blue` (L456), `_first_type4` (L467), `_build_type4_zone` (L537), `_candidate_after_order` (L590), `_a_source_event_time` (L631), `_a_owned_by_s` (L640), `_a_pair_is_reset_reset` (L681), `eligible_a_zones` (L695), `_candidate_timing` (L699), `_candidate_before_order` (L744), `_candidate_event_time` (L788), `candidate_event_time` (L803), `_blue_formation_time` (L810), `_candidate_cross_has_blue` (L840), `_has_ordinary_trend_reaction` (L857), `_candidate_crossed` (L868), `_decision` (L873), `_build_type3_zone` (L999), `_build_order_backed_zone` (L1057), `detect` (L1228), `reconcile_shared_order_stops` (L1305)
- **Nested implementation functions/closures:** _none_

### 13.6 Master Bullish ↔ Bearish directional mirror matrix

This matrix is normative for directional transformation. Bullish is the canonical geometry; Bearish is derived mechanically. A row marked **directional** must transform exactly as shown. A concept listed in Section 13.7 is invariant and must not be direction-flipped.

| Rule / primitive | Bullish | Bearish | Classification |
|---|---|---|---|
| Direction name | `bullish` | `bearish` | directional |
| Directional extreme field | `Low` / `low` | `High` / `high` | directional |
| Opposite extreme field | `High` / `high` | `Low` / `low` | directional |
| Better directional extreme | lower (`<`) | higher (`>`) | directional |
| Directional aggregate | `minimum` / `min` | `maximum` / `max` | directional |
| First Reaction role | `FirstRed` / `RED` | `FirstGreen` / `GREEN` | directional |
| Pre-First context role | `GREEN` | `RED` | directional |
| Reaction confirmation | first strict `High > BoxTop` | first strict `Low < BoxBottom` | directional |
| Reaction confirmation edge | `BoxTop` | `BoxBottom` | directional |
| Opposite evolving box edge | `BoxBottom` | `BoxTop` | directional |
| Reaction Reset | first strict `Low < confirmed BoxBottom` | first strict `High > confirmed BoxTop` | directional |
| Blue Fibonacci level | `BoxTop − 0.618 × (BoxTop − reference)` | `BoxBottom + 0.618 × (reference − BoxBottom)` | directional |
| New Scale strike | strictly lower `Low` | strictly higher `High` | directional |
| Scale-strike confirmation color | `GREEN` | `RED` | directional |
| Scale Blue source extreme | decisive `Low` | decisive `High` | directional |
| Scale Blue line price | `Low + (High − Low) / 3` | `High − (High − Low) / 3` | directional |
| Reset Blue source extreme | Reset-candle `Low` | Reset-candle `High` | directional |
| Reset Blue line price | `Low + (High − Low) / 5` | `High − (High − Low) / 5` | directional |
| Blue strict stop | first directional `Low < source_extreme` | first directional `High > source_extreme` | directional |
| Ordinary A source selection | minimum `Low` | maximum `High` | directional |
| A frozen source after trigger | minimum `Low` through exact confirmation | maximum `High` through exact confirmation | directional |
| A strict stop | directional strict lower penetration | directional strict upper penetration | directional |
| S Type-3 source | minimum `Low`, last owner on equality | maximum `High`, last owner on equality | directional |
| S Type-4 source | minimum `Low`, last owner on equality | maximum `High`, last owner on equality | directional |
| S Blue candidate crossing | strict lower directional cross | strict upper directional cross | directional |
| Physical opposite Order direction used by current behavior | Bearish Reaction/Order | Bullish Reaction/Order | directional |
| Physical Order strict stop in current calculation | `High > OrderStop` | `Low < OrderStop` | directional |
| S Red race event | physical Order `High > OrderStop` | physical Order `Low < OrderStop` | directional |
| E parent/behavior strict stop | lower directional penetration | upper directional penetration | directional |
| Armed S/E owner strict stop | first lower-TF `Low < owner price` | first lower-TF `High > owner price` | directional |
| Direct E-child donor | exact owner identity and parent-stop provenance | exact owner identity and parent-stop provenance | invariant |
| E source | minimum `Low` across complete boundary candles | maximum `High` across complete boundary candles | directional |
| Order_B reset Reaction role | Bullish reset Reaction / `FirstRed` | Bearish reset Reaction / `FirstGreen` | directional |
| Order_B frozen boundary | `LL = minimum Low(...)` | `HH = maximum High(...)` | directional |
| Order_B anchor extension | `LL < anchor Low` | `HH > anchor High` | directional |
| Order_B strict break after Reset | first lower-TF `Low < LL` | first lower-TF `High > HH` | directional |
| Order_B canonical opposite Reaction | first canonical Bearish Reaction | first canonical Bullish Reaction | directional |
| DirectionPolicy `strict_cross` | `<` | `>` | directional |
| DirectionPolicy `better_extreme` | `<` | `>` | directional |
| DirectionPolicy `choose_extreme` | `min` | `max` | directional |
| DirectionPolicy `confirmation_cross` | `>` | `<` | directional |
| Reaction mechanical reflection used internally | `O,H,L,C` canonical coordinates | `O'=-O, H'=-L, L'=-H, C'=-C` plus role reflection | implementation mirror |

All strict rows remain strict. Equality is not converted into a crossing in either direction.

### 13.7 Direction-invariant contract matrix

The following semantics are intentionally identical in Bullish and Bearish. Mirroring any of these merely because price direction changes is an error.

| Invariant | Exact contract |
|---|---|
| Time / chronology | timestamps, event order, lower-TF windows and boundary inclusion rules are not mirrored |
| Doji | `close == open` is always `GREEN` |
| Decimal | price-sensitive decisions use Decimal semantics; direction does not change numeric representation |
| Strict equality | equality never satisfies a strict crossing |
| Exact StopAll owner | one exact S/E identity; count `1` is highest but unarmed; count `>=2` arms the latest occurrence |
| Replacement and chronology | unrelated higher formation disarms lower future eligibility; a completed earlier strict stop remains valid |
| Retrospective E source | direct child may reuse the armed owner's exact completed parent-stop event through its decision; unrelated E cannot |
| Physical identity | canonical Reaction/Order identity is `(FirstIndex, BreakIndex)` |
| Provenance concepts | `parent-stop`, `reset-leg`, `carried-live`, `accepted-live` retain the same meanings |
| Stage ownership | Reaction, Blue, A, S, E, OrderAudit, Lifecycle/StopAll owners remain the same modules |
| Behavior-family names | `S Blue`, `S Red`, `E Blue`, `E Red`, and `StopAll` names are not color-swapped |
| S/E dominance priority | `S Blue < E Blue < S Red < E Red`; A is excluded and StopAll is a boundary |
| Numbering | Reaction, E and StopAll numbering rules remain structurally identical |
| Stable ordering | deterministic tie keys retain the same semantic ordering contract |
| Public/internal meaning | visibility/internal-state semantics do not reverse with market direction |
| Serialization schema | public field names and response shape are identical across directions |
| Hard StopAll boundary | historical boundary/reset semantics are identical |
| Calculation vs presentation | internal historical evidence may survive even when not public |
| Canonical membership | geometry-only evidence cannot become a physical canonical Order in either direction |
| Invalid S parentage | an explicitly invalid S cannot create/retain `parent-stop` cause in either direction |
| Order cause merge | multiple causes may attach to one physical identity without duplicating the Order |
| E same-source priority | Red E outranks Blue E; within family, higher number wins; remaining exact ties preserve earlier accepted object |
| S Type-3/Type-4 tie | earlier exact decision event wins; Type-3 owns only a true exact-event tie |
| S decision same-position race | exact same lower-TF position for Order stop and candidate cross produces no S decision |

### 13.8 Reconstruction-quality stage contract

This table makes the stage chain reconstructable without relying on examples. The detailed prose in Sections 4–12 remains normative; this table is a compact cross-stage contract and must agree with it.

| Stage | Authoritative inputs / prior state | Opening trigger / gate | Source or selection rule | Chronology / tie rule | Stop / terminal rule | Downstream ownership |
|---|---|---|---|---|---|---|
| Reaction / Reset | normalized main candles, selected lower-TF chronology, directional state | required First role after opposite context; strict confirmation | directional box geometry; opposite edge may evolve only through chronology available by confirmation | lower-TF order resolves confirmation vs invalidation/reset; equal eligible opposite extremes retain earliest owner | confirmed Reaction resets only on first strict directional break of confirmed opposite edge | publishes canonical Reaction/Reset stream; cross-direction internal classification occurs after both directions exist |
| Blue | canonical same-direction Reactions and Resets | scale strike growth or Reset event | Fibonacci reference from Mode-A boundary or previous opposite edge; decisive directional strike/source | Break-candle intrabar confirmation only through exact Reaction-confirmation lower-TF row inclusive | first strict directional crossing of `source_extreme`; double-stop Reset Blue may remain calculation-invalid evidence | calculation Blue ledger feeds A; public Blue requires `calculation_valid and not behavior_internal` |
| A | immutable Blue calculation ledger + canonical Reactions | ordinary adjacent valid Blue pair or approved double-stop route | directional extreme from trigger main-candle open through exact confirming Reaction event | exact chronology and deterministic tie ownership; equal source retains earliest unless helper explicitly differs | first strict directional A stop after confirming Reaction; stale pre-`not_before` stop cannot be reused | stop opens S space |
| S | accepted A, A stop, canonical physical Order context, Reactions/Resets/Blue | post-A-stop eligibility; choose order-free Type-3/4 or order-backed route | Type-3/4 and Simple/Advanced source rules in Section 7 | exact event race; Type-3 vs Type-4 earlier event wins, Type-3 only on exact tie; Order-stop/candidate same-position race gives no decision | S Blue on qualified candidate strict cross; S Red on accepted physical Order strict stop; accepted-Order reconciliation may convert open S to Red | accepted S begins provisional E1 chain; historical/invalid evidence may remain calculation context but not fabricate parentage |
| E | accepted S/E parent, exact parent stop, canonical Order ledger | first strict parent stop + physical Order with exact strict stop | directional extreme over complete main candles containing parent stop through Order stop | winner Order is earliest stop; same stop uses larger FirstIndex; `decision_event=max(parent_stop,order_stop)` | recursive child starts only after preceding E strict stop; sequence reset may invalidate crossings spanning hard boundary | reconciled E feeds lifecycle/StopAll and canonical OrderAudit rebuild |
| Order_A | accepted strict behavior stop + canonical opposite-direction Reaction registry | parent-stop direct/bounded geometry that is canonically registered | canonical Reaction identity; canonical Order stop from `MarketChronology` | competing parent-stop candidates: earliest confirmation, then FirstIndex, then BreakIndex | exact opposite-direction strict Order stop | identity-keyed physical Order with `parent-stop` provenance |
| Order_B | accepted lifecycle stop + later reset same-direction Reaction + canonical Reset | eligible post-stop reset leg with accepted behavior anchor strictly before reset Reaction First | LL/HH from closed anchor-source .. reset-First range; strict extension beyond anchor | strict break must occur after exact Reset; next accepted A at/before break expires setup; final opposite Reaction permits FirstTime equality but requires strict later confirmation | physical Order then follows canonical opposite Order stop rules | adds `reset-leg` provenance to canonical physical identity; may merge with Order_A identity |
| Lifecycle / StopAll | accepted S/E chronology and lower-TF strict stops | one exact highest owner; count `>=2` arms it; an E or qualified S Red donates StopAll after a completed stop | priority, exact identity and direct E-parent proof are direction-invariant; only strict price comparison mirrors | prior stop survives unrelated replacement; direct E child may share or precede its retrospective source timestamp | StopAll hard boundary clears owner/count/pending completed stop but retains history | final visibility/lineage closure and StopAll source map |
| OrderAudit | physical identity ledger + accepted S/E/A causes + lifecycle results | merge accepted ledgers and reconcile current accepted causes | dedupe by `(FirstIndex, BreakIndex)`; provenance is attached to identity | stable cause/order sorting; retain pre-range identity when a visible behavior references it | strict stop computed only when not already authoritative; invalid parent cannot fabricate cause | canonical serialized physical Order history |
| Serialization | finalized calculation state only | requested direction/presentation range | projection only; Decimal values stringified under existing contract | stable source ordering; presentation filtering occurs after calculation | never recalculates trading decisions | response envelope + optional read-only Bridge Output |

### 13.9 Package/source integrity notes

1. The current live Engine tree contains the root zero-byte `__init__.py` and the other production Source paths in Section 1. The pre-correction `engine.zip` remains unchanged.
2. Section 16 embeds each current live production Python file byte-for-byte, including the root package marker.
3. The pre-existing unsupported `pipeline/__init__.py` wrapper import of missing `run_blue_line` remains outside this lifecycle correction. The production Bridge path is the supported calculation entry.
4. Unit and RAW regression evidence for this revision is recorded in Section 14. Prior `5.4.23` and `5.4.22` verification claims are retained there only as historical evidence.

## 14. Verification scope for Reference `5.4.24`

### 14.1 Current verification

- **PASS — syntax, unit and mirror contracts:** current Engine tests completed with `91 passed, 2 xfailed`. Direct E-child acceptance, mismatched-parent rejection and unarmed count-1 rejection run for both S colors in Bullish and Bearish; the prior exact-count, replacement, strict-boundary, historical-stop, reset and valid StopAll-chain contracts remain passing.
- **PASS — target RAW and first difference:** 93,533 five-second rows were calculated at 30 seconds in both directions. Bearish `S Red` at `2026-09-25 02:12:00 +03:30` and `06:05:30 +03:30` arms the exact owner. Its price is `93.184`; first strict five-second High above it is `93.194` at `08:51:00 +03:30`. Incoming `E1 Red` has the second S as its exact parent and `parentStopEventTime=08:51:00`; `StopAll1` now occupies that E source (`08:51:00`), with `stoppedBehaviorKey=S red`, count `2`, and gate time `08:51:00`. The following `08:51:30` five-second High is `93.157`, not a fresh strict stop.
- **PASS — unrelated target chain preserved:** Bearish `2026-10-02 09:24:30 +03:30` and `18:05:00 +03:30` remain `S Red`; `E1 Red` count `2` first strictly stops at `19:57:05 +03:30` and yields `StopAll1` at the `20:20:00 +03:30` E donor.
- **PASS — previous-revision differential on target RAW:** all Bullish arrays, including S/E/StopAll/OrderAudit/Bridge Output, are exactly unchanged from `5.4.23`. Bearish Reaction, Reset, Blue, A and S arrays are exactly unchanged; all `40` common E objects have identical payloads. The corrected earlier StopAll boundary changes later E/StopAll visibility and OrderAudit as intended.
- **PASS — historical RAW anchors:** both-direction 30-second calculations completed on the `2026-09-11` FXCM:USOIL and `2026-09-28` FOREXCOM:XAUUSD inputs. Every Reaction, Reset, Blue, A, S, E, StopAll and OrderAudit array is exactly equal to `5.4.23` on both anchors and both directions.
- **PASS — continuous RAW differential:** the `2026-08-21` to `2026-10-02` FXCM:USOIL calculation completed in both directions. Reaction, Reset, Blue, A and S arrays are exactly equal to `5.4.23` in both directions; every common E payload is identical (`251` Bullish and `222` Bearish). The newly materialized StopAll sources exactly match the E sources removed from public E output (`89` Bullish and `41` Bearish); no prior StopAll source is removed. Later StopAll numbering, OrderAudit and Bridge Output may change through the corrected hard boundaries. Observed wall time was `557.62 s` versus `344.993 s` for the earlier revision on this RAW; changed downstream work and runtime conditions prevent treating this as a controlled performance benchmark.
- **NOT RUN — independent global market correctness proof:** finite RAW and synthetic cases cannot prove all possible histories.

### 14.2 Prior `5.4.23` verification — HISTORICAL / SUPERSEDED

The `5.4.23` Source required the owner stop to be strictly before every incoming E `sourceTime`. This was incorrect for an E directly caused by that owner's stop because E source geometry is selected retrospectively from complete main candles. Its earlier RAW checks remain historical evidence; its conclusion that every gate at or after donor source is invalid is superseded by the exact direct-parent rule above. The prior `5.4.23` delivery ZIP retains that Reference as historical evidence; it is not a current live Reference.

### 14.3 Prior `5.4.22` verification — HISTORICAL EVIDENCE

The following `PASS` labels reproduce historical documentation claims; they are not current validation results. Direct inspection of the unchanged `engine.zip` for this correction found **13** Python Source entries, including the zero-byte root `__init__.py`, plus two References and cached bytecode. Thus the prior `14 files total / 12 Python Source` inventory claim below is incorrect and must not be used as a current Source boundary. The current `5.4.24` manifest and exact recovery checks use all 13 live production Source files.

#### Verification performed for the historical documentation-only synchronization

- **PASS — complete archive inventory:** the supplied authoritative `engine.zip` was recursively extracted and contains 14 files total: 12 Python Source files and the two prior `5.4.21` Algorithm References.
- **PASS — exact Source manifest:** every actual Python file was hashed from archive bytes and the Section 1 manifest was regenerated from those bytes.
- **PASS — Source compilation:** all 12 Python files compile successfully with the current Python parser/compiler.
- **PASS — production Bridge import:** `bridge.trading_pipeline` imports successfully from the extracted archive.
- **FAIL — legacy `pipeline` package-wrapper import (pre-existing Source defect):** `pipeline/__init__.py` imports missing `run_blue_line` from `pipeline/blue_line_detector.py`. This is not introduced by Reference `5.4.22`; no production Source is changed by this documentation release.
- **PASS — dual-direction production smoke execution:** the Current Bridge completed a full 30-second calculation in `both` directions on `RAW FXCM_USOIL 5S FROM 2026-09-11 02-53-30 TO 2026-09-15 11-03-45.json`, including Reaction, Reset, Blue, A, S, E, StopAll, OrderAudit and Bridge Output.
  - Bullish counts: `reactions=551`, `resets=263`, `blueLines=235`, `aZones=53`, `sZones=26`, `eZones=11`, `stopAlls=20`, `orderAudit=96`, `bridgeOutput=8`.
  - Bearish counts: `reactions=519`, `resets=285`, `blueLines=230`, `aZones=49`, `sZones=24`, `eZones=17`, `stopAlls=19`, `orderAudit=116`, `bridgeOutput=8`.
- **PASS — AST symbol coverage regeneration:** Section 13.5 was generated from the complete Current Source AST and includes module-level assignments/caches, top-level functions, classes, annotated fields, methods/properties and nested implementation closures.
- **PASS — directional documentation audit:** the target-direction semantic sections remain paired and Section 13.6 records the complete canonical transformation set used by the Current Source; Section 13.7 explicitly protects direction-invariant semantics from false mirroring.
- **PASS — exact embedded Source recovery:** every file embedded in Section 16 of each `5.4.22` Reference is recovered byte-for-byte equal to the corresponding Current Source file, including final-newline structure.
- **PASS — Bullish/Bearish embedded Source identity:** the two References embed exactly the same Current Source bytes and manifest hashes.
- **NOT RUN — historical unit suite (`49 passed, 2 xfailed`):** those tests are not present in the supplied `engine.zip`; therefore the historical result is not claimed as a new `5.4.22` execution.
- **NOT RUN — exhaustive-input correctness proof:** no finite regression set constitutes proof for every possible market history.
- **NOT APPLICABLE — trading-output before/after regression for this Reference revision:** `5.4.22` changes documentation only; Production Source bytes are unchanged.

### 14.4 Carried-forward `5.4.21` Source verification — HISTORICAL EVIDENCE

The preceding Source-synchronized Reference recorded these results on `2026-10-03`. They remain historical evidence for the unchanged Source snapshot, but this `5.4.22` documentation release does not relabel them as newly rerun tests:

- `49 passed, 2 xfailed` Engine unit contracts.
- Successful pre-refactor parity on four complete `FXCM:USOIL` / `FOREXCOM:XAUUSD` RAW inputs in both directions.
- Complete requested USOIL RAW execution through `2026-10-02 16:35:20` with the accepted OrderAudit invariant repair.
- Full-RAW Bullish old/new payload equality was not applicable because the old pre-refactor Bullish Engine terminated at its OrderAudit invariant.

## 15. Current revision record

### `5.4.24` direct E-child StopAll correction — ACTIVE / BEHAVIORAL BUG FIX

- **Document version:** `5.4.24`
- **Previous Reference:** `5.4.23`
- **Modified:** `2026-10-04 21:40:18 +03:30`
- **Production Source behavioral change:** `pipeline/lifecycle_engine.py` only, `1.18.1 → 1.18.2` and implementation `1.20.1 → 1.20.2`.
- **Serialization/API shape:** unchanged; the causal E donor still uses `sequence-group-stop` and existing provenance fields.
- **Trading-output change:** a direct E child materializes a completed strict stop of its armed exact parent even when its retrospective source timestamp equals or precedes the parent stop. Unrelated higher E replacements retain the strict source-time cutoff.
- **Mirror impact:** identical parent identity, chronology and donor checks; only Bullish `Low < price` versus Bearish `High > price` differs.

### `5.4.23` exact-owner StopAll correction — HISTORICAL / SUPERSEDED

- **Document version:** `5.4.23`
- **Previous Reference:** `5.4.22`
- **Modified:** `2026-10-04 21:01:35 +03:30`
- **Production Source behavioral change:** `pipeline/lifecycle_engine.py` only, `1.18.0 → 1.18.1` and implementation `1.20.0 → 1.20.1`.
- **Serialization/API shape:** unchanged; legacy `opposite-s-group-stop` name is retained only for semantically valid transitions.
- **Trading-output change:** invalid lower-priority or unstopped Blue promotions are removed; valid completed owner stops use the existing donor contracts. Downstream S/E/StopAll/OrderAudit may change after the first corrected boundary.
- **Mirror impact:** identical identity, priority, arming, replacement, chronology, donor and reset rules; Bullish `Low < price` mirrors Bearish `High > price`.
- **Manifest correction:** include the zero-byte root `__init__.py` present in both the inspected archive and live Engine tree.

### `5.4.22` documentation completeness synchronization — HISTORICAL / SUPERSEDED

- **Document version:** `5.4.22`
- **Previous Reference:** `5.4.21`
- **Modified:** `2026-10-04 13:12:49 +00:00`
- **Production Source behavioral changes:** `NONE`
- **Production Source module version changes:** `NONE`
- **Serialization/API changes:** `NONE`
- **Trading-output changes caused by this revision:** `NONE`
- **Mirror impact:** semantic mirror is unchanged; documentation now exposes it explicitly and exhaustively in one master matrix.
- **Corrections:** remove the nonexistent zero-byte root `__init__.py` from the manifest/snapshot; regenerate symbol coverage so `_invalid_s_without_order_cause` and the previously omitted Reaction module caches/indexes are represented.
- **Completeness additions:** mechanical AST symbol/schema index, Master Bullish↔Bearish Mirror Matrix, direction-invariant matrix, reconstruction-quality cross-stage contract, archive/source-integrity notes, explicit current verification status, and known wrapper defect disclosure.
- **Known unresolved Source issue:** the unsupported legacy `pipeline/__init__.py` wrapper imports missing `run_blue_line`; this documentation-only revision does not change that API/package Source.
- **Verification limitation:** the standalone unit suite is absent from the supplied package, so the historical `49 passed, 2 xfailed` result is not re-executed here.

### `5.4.21` Source behavior baseline — HISTORICAL

This was the executable calculation baseline for `5.4.22`. Reference `5.4.23` supersedes its StopAll eligibility behavior while retaining the unrelated accepted OrderAudit invariant repair.

### Earlier `5.4.20` / intermediate `5.4.21` calculation changes — HISTORICAL / SUPERSEDED

The later Blue-consumption feedback, Blue publication suppression, and dominant S-Red continuation exception that changed results relative to the supplied pre-refactor Engine are not active in this Source snapshot. Historical records remain evidence only.

