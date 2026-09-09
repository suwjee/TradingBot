---
id: ALGORITHM-TRADINGBOT-BEARISH-20260908
type: algorithm
status: symmetric
direction: bearish
authority: user-approved-exact-mirror-of-bullish-2026-09-08
implementation_verification: full-xauusd-30s-logical-reflection-zero-differences
timezone: Asia/Tehran
---

# Bearish indicator algorithm: exact bullish mirror

## Authority and verification status

The user authorized the complete bearish mirror on 2026-09-08, including rules
previously documented as bullish-only. The maintained bullish calculations are
the reference and their behavior must remain unchanged. This document specifies
the approved mirror. Its symmetric status records exact full-file XAUUSD
30-second logical reflection with zero differing output fields, not independent
Bearish historical validation. Evidence is stored in
C:/Users/msadr/Desktop/NEW/verification/full_parity_evidence/.

Read this document with BULLISH_INDICATOR_ALGORITHM.md,
BULLISH_LEG_RULE_VERIFIED.md, and BULLISH_LEG_RULE_AMENDMENT_20260907.md.
The latter documents retain their historical scope and evidence. Their earlier
"bearish deferred" statements do not override the user's new authorization.
No bullish historical example, timestamp, price, or test count is reclassified
here as verified bearish evidence.

Source authority is D:/My-Projects/TradingBot:

- indicator/Modules/1_reaction-detector/app/Reaction-detection-new.py
- indicator/Modules/2_blue-line/app/blue_line.py
- indicator/Modules/3_A-zone/app/a_detector.py
- indicator/Modules/4_S-zones/app/s_detector.py
- indicator/Modules/5_E-zones/app/e_detector.py
- indicator/Modules/6_StopAll/app/stopall_detector.py
- indicator/indicator-settings/backend/reaction_bridge.py

The Obsidian Trading Vault provides navigation and governed knowledge, not
replacement calculations. Generated split files, Graphify, caches, and old
Prj-1 snapshots do not override maintained code and its approved reference.

## 1. Exact mirror contract

Use price reflection to define the mirror without changing event time:

    mirrored Open  = -Open
    mirrored High  = -Low
    mirrored Low   = -High
    mirrored Close = -Close

Decimal.copy_negate() expresses exact sign reflection without an intervening
binary float or precision-reducing arithmetic. A reflected BoxTop is the
negative original BoxBottom and carries that bottom's source provenance;
a reflected BoxBottom is the negative original BoxTop with its source.
Scalar price levels change sign; price distances remain positive distances.
Directional comparison is reversed, including non-strict eligibility tests:

    bullish High > upper level  <=> bearish Low < lower level
    bullish Low < lower level   <=> bearish High > upper level
    bullish Low >= floor        <=> bearish High <= ceiling
    bullish minimum Low         <=> bearish maximum High

Keep time order, exact seconds, indexes, source/decision relationships, window
inclusivity, tie-owner position, reset association, numbering, identifiers,
nullability, cause membership, and parent relationships unchanged by reflection.
Reverse price direction, never chronological order. Do not replace strict
crossings with equality or floating-point tolerances.

GREEN/RED market candle tags obey Open <= Close => GREEN, including every
market doji. Bearish Reaction uses the bullish reference in reflected
coordinates and swaps the internal GREEN/RED roles. Thus a market GREEN doji
can participate as bearish FirstGreen through the internal FirstRed role.
This internal role mapping does not recolor the source/chart doji RED.
A reflection oracle must carry the intended role swap; recomputing a doji tag
from reflected equal Open/Close loses that information.

The S/E family names red and blue are behavioral categories, not candle
direction. Preserve them exactly. Type 3 remains blue; red dominance and
family priorities are identical in both market directions.

Extrema ties preserve the owning helper's rule: an earliest bullish minimum
maps to an earliest bearish maximum; a latest minimum maps to a latest maximum.
There is no global replacement tie policy.

## 2. Input, numeric, and temporal contract

Validate a nonempty candle inventory with exactly time/open/high/low/close.
Times are positive safe integer Unix seconds, strictly increasing and unique.
OHLC values are finite; High bounds Open/Low/Close above, and Low bounds them
below. Convert decision prices through Decimal(str(value)); serialize prices
as strings.

For a requested timeframe and range, retain only:

    from <= raw.time < to + timeframe

Filter before any aggregation. Build one-second and main-timeframe buckets
using floor(time / bucket_width) * bucket_width; Open is first, Close last,
High the maximum, and Low the minimum. Index the resulting main candles from
zero. A partial first bucket contains only retained rows. No earlier/later
state may affect Reaction, owners, numbering, orders, or StopAll.

Convert epoch to Asia/Tehran local detector time and back consistently.
Main candle time and exact lower-second event time are distinct. Lower data
resolves intrabar races; equal main indexes cannot establish event order.
Selection changes can legitimately change output at shared clock times because
each selected range is an independent calculation universe.

## 3. Pipeline and opposite-order dependency

    raw range -> bearish Reaction/Reset -> bearish Blue -> bearish A
              -> bearish S -> bearish E -> StopAll -> accepted payload

Run bullish Reaction/Reset as the opposite Order authority for bearish S/E.
Do not remove this dependency or recreate its geometry in downstream modules.
StopAll boundaries feed back to E until a fixed point is reached.
Python owns all calculations; the browser consumes serialized results.

## 4. Bearish Reaction Mode A

Mode A initializes the first bearish Reaction without a previous Reaction.
Maintain a leg-open ceiling and, when available, a GREEN anchor.

FirstGreen is GREEN immediately after RED. With an anchor, require:

    FirstGreen.High <= anchor.High

Without an anchor, the mirrored eligibility accepts:

    FirstGreen.High <= previousRed.High
    or FirstGreen.High <= legOpenHigh

Mirror the anchor invalidation checks and state transitions of the reference.
Where both relevant consecutive highs exceed the anchor ceiling, discard that
anchor as the bullish reference discards the corresponding floor.

Find the continuous RED run immediately preceding FirstGreen. BoxBottom is the
minimum Low of that run and FirstGreen; an equal run low retains the earlier
RED source. Initialize BoxTop from FirstGreen.High. Store anchor/leg-ceiling
price and source with the candidate.

Before confirmation, higher High extends BoxTop. Confirm only with
Low < frozen BoxBottom. Low == BoxBottom is not confirmation. Invalidate the
owner only with High > its anchor/leg ceiling. When invalidation and breakdown
share a main candle, compare their first lower-second events in the same order
as the reference; an earlier invalidation rejects the candidate.

Within the confirmation scan, only highs eligible before the first strict
breakdown can refine the confirmed BoxTop. A later High cannot rewrite that
confirmed geometry. A subsequent lower candle with High > confirmed BoxTop
creates a same-main-candle Reset with its exact second time. Preserve the
reference's handling of conditions coincident in one finest candle.

## 5. Bearish Reaction Mode B and Reset recovery

After the first Reaction, track running Low and its source. A GREEN can open
Mode B. Freeze BoxBottom from the lower of running Low and FirstGreen.Low.
BoxTop is the maximum High in the mirrored eligible source window: if the
BoxBottom source precedes FirstGreen, begin after that boundary source;
otherwise begin at FirstGreen. Higher highs can refine BoxTop before confirmation;
only Low < frozen BoxBottom confirms.

If the confirmation candle is GREEN and no post-breakdown Reset occurred,
the reference's eligible remainder can seed the next Mode B. Do not force a
next-main-candle start or silently narrow reference extrema windows.

A confirmed bearish Reaction resets at the first High > confirmed BoxTop.
Equality does not reset. Store main time/index, exact second, broken level,
and from_first_idx. Reset clears ordinary candidate state and starts direct
same-direction recovery, preserving the broken owner's provenance.

Recovery seeks FirstGreen after RED in the post-reset context. Check adjacent
runs as in the reference. Reject a FirstGreen above the local ceiling.
BoxBottom is the context's minimum Low through First; the leg ceiling is the
maximum High from reset to before First. Before breakdown, High > leg boundary
invalidates; Low < BoxBottom confirms. Preserve intrabar event ordering and
blocked_through so an invalid candidate cannot seed premature nested recovery.

## 6. Bullish Order geometry APIs used by bearish S/E

Order_A uses first_order_reaction_after_gate. Reaction history may include only
confirmations eligible at the exact gate; future history cannot own it.
For an already active bullish order owner, the mirrored gate race is:

    Low < owner outer boundary => restart
    High > gate candle High    => continue

Select the first eligible complete geometry, resolving simultaneous confirmation
candidates by the reference's smallest first_idx rule.

Order_B uses first_simple_geometry_after_gate with reset-leg context preserved.
First is in/after its gate candle and the owner must survive to confirmation.
A geometric order can have reaction number zero without being a published
ordinary Reaction. Do not substitute a cached ordinary Reaction where the
bounded geometry API is required.

Dormant helpers do not become normative simply because they exist in source.

## 7. Bearish Blue Line

Use bearish Reactions/Resets and Decimal("0.618"). For initial Mode A, reference
anchor_value, falling back to leg_boundary. Otherwise reference the previous
bearish Reaction's BoxTop:

    fib = current.BoxBottom + 0.618 * (reference - current.BoxBottom)

Scan First through Break inclusively. A pending strike requires High > fib,
or High > last confirmed strike extreme when that reference exists. Equality
does not strike. Higher High updates pending state. The first eligible RED
after pending confirms it; doji remains market GREEN and is not a bearish RED
confirmation candle.

If pending remains at Reaction end, inspect lower confirmation candles.
Penetration must occur before or at the decisive Low < BoxBottom. Map the
decisive lower event to its main source candle.

A scale candidate requires an existing previous strike count and a strictly
larger current count. The first Reaction alone is not a scale. Update the
reference count even when spacing suppresses publication.

After a published Blue, at least one complete healthy Reaction without a Blue
must pass. A scale-bearing Reaction does not provide spacing for its own Reset.

    scale line price = High - (High - Low) / 3
    reset line price = reset.High - (reset.High - reset.Low) / 5
    start = source time - timeframe
    end   = source time + timeframe

Group Reset candidates by from_first_idx. Preserve broken-level provenance,
stateful spacing, source extreme, and calculation_valid decisions. Reflect
the invalid Reset-Blue case with a higher source extreme and the prior Blue
stopped at the relevant reset index. Invalid lines cannot enter an ordinary A
or public output; they may remain internal provenance for a special
double-stop A, in which case the A owns that candle. Ordinal gaps remain
possible because numbering precedes filtering.

Scale formation is the owning Reaction's exact confirmation. Reset formation
is its first strict lower-second broken-level crossing. Reset-Blue stop scans
start at source time + timeframe. A bearish Blue stops at first
High > sourceExtreme; equality is not a stop.

## 8. Bearish A formation

Consume valid Blue states in formation order, pairing adjacent eligible Blues.
A pair needs a stop trigger and a confirming bearish Reaction.

When the special double-stop route emits a valid A, both Blue lines that formed
that lifecycle are consumed and cannot be reused by a later ordinary pair. If
the A is sourced on the same candle as an invalid Blue, the A owns that candle;
the invalid Blue remains internal provenance only and is not published.

The three ordinary trigger paths are:

1. A bearish Reaction begins after previous-Blue formation and confirms before
   current-Blue formation. Freeze the maximum High from previous formation
   through that break; after current formation, High > that level triggers.
2. Previous Blue stopped before current formation. Freeze maximum High from
   exact prior stop to before current source. Inspect the current formation
   candle remainder for a strict break. If it does not trigger there, current
   Blue must also stop before the subsequent required strict higher high.
3. Both Blues coexisted. Use exact chronology to find first stop and its
   extreme; after second stop require High > first-stop extreme. Coincident
   exact stops retain the reference's immediate-trigger treatment.

A pair expires at the next eligible Blue formation. Select the first bearish
Reaction whose exact confirmation is not before trigger and whose First meets
the latest required stop-time bound. Do not infer this from main index alone.

A source is the maximum High over trigger_index through confirming break_idx,
inclusive. Earliest equal maximum wins. Advance the cycle through that break
after emission to prevent repeated ownership.

The special double-stop route may use an invalid intermediate Blue with a
prior valid Blue when its source/formation extreme strictly crosses the prior
source extreme. Apply the same confirmation/source logic and duplicate/lifecycle
suppression as the reference. Sort source time then trigger event time.

A stops at first High > A.price after exact A confirmation. If the next A
confirms before/equal to that stop, the earlier A cannot seed this S wait:
stop >= next confirmation is rejected. An accepted stopped A opens ownership
even if no Order/S is found. A successful S closes the window at its source
plus one timeframe; otherwise pending ownership remains.

## 9. Orders and bearish S

Bearish trend uses bullish Orders. Ordinary S order selection requires both
Order First main time and exact confirmation strictly after the exact A stop.

For bullish Order Mode A, stop is anchor_value, falling back to leg_boundary,
with the matching source. For Mode B, use the previous bullish Reaction's
BoxBottom and source; missing previous geometry is a structural error.

    bullish Order stop = first Low < orderStopLevel

For pre-order interpretation compare order.BoxTop to A-stop High:

    order boundary >= A-stop extreme => candidateAfter
    order boundary <  A-stop extreme => candidateBefore

The pre-order candidate is the maximum High from the exact A-stop remainder
through Order First, retaining the earlier tie source and exact lower event.

An advanced candidate needs a bearish Reaction nested in the bullish Order in
time and fully contained in its box in price; bearish order boundary is
order.BoxTop. Otherwise use the first bearish Reaction confirming after Order
confirmation. The simple candidate is maximum High from Order Break through
trend Reaction Break inclusive; this helper keeps the latest equal maximum.
The fallback after Order begins in the eligible exact-confirmation remainder,
retaining its temporal anchor before trend First.

After Order confirmation scan lower candles:

    candidateCross = High > candidatePrice, at/after candidate_start
    orderStop      = Low < orderStopLevel

If both occur in one finest candle, emit no S. If orderStop occurs first, emit
red S. If candidateCross occurs first, blue S needs aligned Reset-Blue evidence
available by the event, or a qualifying ordinary bearish Reaction confirmed
after behavior start and by the event. An unsupported pre-order fallback is
discarded and cannot later be reused as valid evidence; continue advanced/simple.

Retain A and Order provenance, candidate path, source time, and exact decision
time. Source and decision need not be the same timestamp.

## 10. Bearish S Type 3

Search after A-stop but before the first eligible bullish Order confirmation.
An eligible bullish owner confirmed before A-stop and was not reset by that
event. For a later bullish Reset, the leg spans that owner's Break through the
Reset main candle inclusively.

Boundary is maximum High of that leg; latest equal maximum wins. After Reset,
High > boundary must occur before the deadline. At least one bearish Reaction
must confirm after A-stop and no later than boundary crossing. Earliest eligible
decision wins. Output formation_type="type3", color="blue", and no invented
Order metadata or stop geometry.

## 11. Bearish E and accepted Order ledger

E requires a stopped accepted S/E parent and eligible healthy confirmed bullish
Order geometry. Parent strict stop is first High > parent.price after the
parent's exact decision. Order strict stop is
Low < orderStopLevel, because the Order direction is bullish.

Order causes are parent-stop (Order_A), reset-leg (Order_B), and carried-live.
Physical identity is (FirstIndex, BreakIndex). Multiple causes for one identity
merge; they never create duplicate geometry or independent votes.

Order_A starts after exact parent stop using the directional geometry API.
A First opened before the event cannot be reassigned to that stop. Preserve
same-candle initial-A ownership and its nested-direct blocking.
When the next published ordinary opposite Reaction has no strict Order stop in
the selected range, an earlier healthy geometry from the bounded directional
API is the direct Order_A fallback. Earlier pre-gate history may change its
Mode and stop provenance, but it must not hide the post-gate behavior. A
published Reaction that completes its Order lifecycle remains canonical.

Every strict stop of every final, calculation-valid A creates an independent
Order_A audit cause. An internal A candidate removed by final ownership or
visibility cannot create a public Order audit. Physical order identity remains
`(FirstIndex, BreakIndex)`; multiple visible stopped A zones targeting one
identity merge their accepted `parent-stop` causes without duplicating
geometry. E continues to consume only its accepted view.

For Order_B, use the bullish owner Break through bullish Reset inclusively.
Find maximum High of that leg. After Reset, High > this boundary opens the gate.
Require a bearish Reaction confirmation from leg start through boundary cross.
Construct bullish geometry with the reset context. An active bullish owner
blocks its nested Order_B until that owner's Reset; bearish trend Reset does
not release the opposite owner.

Apply blocked First times from live invalid heads to every relevant candidate
path, including direct geometry. An invalid head with a pending S owns the
window through its exact strict High stop. Firsts opened while it is live cannot
own the resumed outer E sequence. Heads without a pending S do not block.

Build direct/reset pools, merge equal identities/causes, compute order stop and
cross times, and impose the earliest valid decision deadline. A continuous
inherited-order deadline constrains both provisional and final pool deadlines.
A confirmation after the inherited order's strict stop cannot enter its
parent's audit.

Preserve pool ordering and final selection: the effective E zone key is
(stopEvent, -first_idx), so later First wins equal stop-event competition.
Do not replace it with a global earliest-First policy.

A blue S may carry an unused order whose stop is at/after S-stop. An accepted
ledger Order must meet the reference's parent-lifetime, confirmation, and live
stop eligibility. Carry reuses geometry and cannot manufacture another Order.
A superseded Blue-E parent cannot seed a later ledger after an eligible later
confirmed Red S owns that lifecycle. Keep red/blue categories unchanged.

E source is maximum High from the main candle containing exact parent stop
through the main candle containing Order stop, inclusive. Earliest tie wins.
Decision is max(exact parent stop, exact Order stop). Do not exclude the
parent-stop main candle simply because the event is intrabar.

Recursively build successors while parents stop and eligible Orders exist.
Reconcile all S-rooted chains using exact chronology and active state:

- E red priority 4, S red 3, E blue 2, S blue 1.
- Family follows accepted parent; red dominates blue.
- Number follows the same-family active stopped sequence, otherwise starts at 1.
- Stopped active objects leave active state but retain historical provenance.
- A dominating red S can survive nested blue E activity.
- StopAll sequence boundaries clear active E numbering at their source;
  downstream parent provenance may identify StopAll.

Rebuild audit from accepted parents after reconciliation. Retain the winning
Order of an accepted E and merge its legitimate causes. Rejected branches
cannot reopen audit after their deadline or supersession.

## 12. Bearish StopAll

StopAll consumes visible accepted S and accepted E; it does not discover
Reaction or Order geometry. It inherits the decisive E's source, Order,
cause, and underlying E family/number lineage. StopAll has no red/blue color.

Internal priorities remain S blue 1, E blue 2, S red 3, E red 4.
Group S by exact color and E by exact (family, number). Process E in source
order, incorporating only S with source strictly before the current E source;
equal source time does not count that S first.

Higher-priority events replace the active group; matching S count when no E
dominates; matching E family/number count together. Higher-number E advances
its same-family group. Red dominates blue independent of number. A nested
lower-priority historical event does not split the dominant group.

Before integrating current E, a group of at least two matching confirmed members
can yield StopAll1 when the eligible previous member's strict stop occurs no
later than the current E decision. Bearish member stop is High > price after
its own decision. The current E supplies StopAll geometry and Order; reset group
state afterward.

Check active StopAll continuation before ordinary group logic. If active
StopAlls strictly stop by current E decision:

    next number = max(stopped active StopAll numbers) + 1

Consume those stopped active objects, retain eligible other state according to
the reference, and reset grouping. Record the new StopAll's subsequent strict
stop metadata for recursion. Equality is never a stop.

## 13. Bridge ownership and fixed-point reconciliation

Apply all approved bullish leg rules directionally to bearish; see the paired
BEARISH_LEG_RULE_VERIFIED.md and BEARISH_LEG_RULE_AMENDMENT_20260908.md.

Owner selection is chronological first: latest stop-containing main candle,
then same-candle priority StopAll > E red > S red > E blue > S blue > A and
sequence number. An older high-number E cannot dominate a newer lifecycle.

A newly confirmed higher bearish Reaction head can preserve an interior A when
head precedes A, head.High > A.price, and head Reaction confirms before A source.
Preserve existing owner consumption. Resolve exact S source ownership with the
same lower event finder used by the bullish rule.

An accepted detected behavior can establish the next LegStart; an unlabelled
raw extreme alone cannot transfer ownership. Reflect strict lower boundaries
to strict higher boundaries. Equal highs do not count as a new strict break,
and reference tie ownership is retained.

A pending S is consumed by the resumed larger lifecycle when the dominant
owner has stopped by the candidate's exact source-extreme event and the S price
strictly exceeds its boundary. A higher-priority Red S remains visible over a
stopped Blue S when that strict break occurs. The A stop starts the S search; it
is not the later source-ownership cutoff. Without a supplied exact source-event
resolver, the helper uses source_time. Equality does not consume it. Rejected
A/S candidates may remain internal evidence but cannot supply public labels,
counts, or downstream Order geometry.

Reconcile initial E, filter stale S by accepted resets/ownership, and rerun E
with blocked Order provenance if needed. Rebuild S audit from accepted A, then
rebuild E audit from accepted parents.

Repeat visible-S filtering, StopAll detection, and E sequence reset mapping
{StopAll.source_time: StopAll.number}. Stop at identical reset state. If a reset
identity repeats without convergence, raise the reference error; do not silently
return a partial payload. Reruns use the same geometry/ledger inputs.

Suppress visible E represented by StopAll at the same source. Final collision
priority remains StopAll > E > S > A. Retain legitimate historical stopped
objects. Apply lineage closure for actual final E-to-S and S-to-A parents;
do not resurrect rejected candidates without a final child.

## 14. Serialization and presentation

Output under directions.bearish uses reactions, resets, blueLines, aZones,
sZones, eZones, stopAlls, and orderAudit, retaining the shared field schema.
Directional object fields say bearish; opposite Order direction says bullish.
BoxTop/BoxBottom stay actual upper/lower prices and retain their mapped sources.

Preserve First/Break/source/main/exact-event timestamps, indexes, ordinals,
family/number, mode, parent metadata, order stop/confirmation/causes, nulls, and
validity handling. Decimal prices serialize as strings; local times become epoch
seconds. actualFrom/actualTo describe retained main buckets, not extra raw data.

Order audit merges S audit and accepted E ledger by (FirstIndex, BreakIndex),
deduplicates causes, sorts First then Break, and respects the presentation range.
An accepted audit-only Order can display its box without inventing a stop line.
Order stop lines are supplied by attached S/E/StopAll geometry and deduplicated
with the same direction/First/stop-source identity as the reference.

Chart visibility, colors, manual positions, reset-label hiding, and other display
thresholds do not change calculations. Browser code must never recalculate
bearish facts. Cache identity includes engine content, dataset identity/mtime,
timeframe, range, direction, and options; changed engines invalidate old cache.

## 15. Acceptance requirements

Only the selected XAUUSD data is acceptance authority. Per the user's final
clarification, no independently validated Bearish example exists: verification
establishes logical reflection of Bullish, not independent trading correctness.
Other focused checks below are diagnostic, not alternative acceptance datasets.

Do not claim correctness from matching counts or chart appearance alone.
Compare every collection and field, including audit-only Orders, price strings,
extrema sources, exact times, parent lineage, causes, nulls, and ordering.

Required evidence for the implementation owner:

- Capture bullish baseline and prove it remains unchanged after bearish work.
- Compile changed source and run focused Reaction/Blue/A/S/E/StopAll tests.
- Run full directional reflection tests with correct internal candle roles,
  including doji, equal extrema, strict equality, intrabar races, deadlines,
  invalid-head ownership, and StopAll feedback.
- Exercise integrated bridge output and independent-range equivalence.
- Run the user-selected
  RAW_FOREXCOM_XAUUSD_1S_FROM_2026_08_18_04_44_40_TO_2026_09_05_00.json.
- Compare the split implementation in C:/Users/msadr/Desktop/NEW with the
  maintained source on identical inputs, including exact bullish regression.
- Record failures, skips, scope, command, and runtime evidence honestly.

The full-file maintained-source reflection comparison completed with zero
differences on 1,078,742 raw rows (38,234 main candles, 30 seconds).
Bullish output also exactly matches the pre-change HEAD and the unchanged
Bullish split. The evidence report separately records split-Bearish parity.
This document carries no fabricated Bearish historical examples. Universal
error-freedom is not established by any finite test suite.
