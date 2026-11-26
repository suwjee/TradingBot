# CP338 — W2 E Queue Semantic Reconciliation

**Status:** PASS_SCOPED after publication; W2 NOT_ACCEPTED.

Pinned source: `c99b4c957e932d9ee70c492ca03ce80711447fc1`, `240369edf3352006082efe094eb68ac027d6689f`. Entry `22d61f465da400bcf779b1f4ba423caca1bf9c8b`.

## CP326-S01 — E records

Source: `engine/pipeline/e_zone_detector.py:35–100`.

Frozen slotted EZone preserves parent/Order/decision/source geometry and separate event/main times; Order causes and parent-stop cause are independent fields. _ParentStopProgress, _EReconciliationStep and _ReconciledE retain native history, not recursively immutable evidence. _ReopenedERace is internal control only.

**Handoff:** OrderMatch supplies geometry/causes; E record is not creation ledger or proof of display eligibility.

B06 overlapping link occurrences: 7.

## CP326-S02 — E01–E03

Source: `engine/pipeline/e_zone_detector.py:112–146`.

advance validates nonempty times and inclusive dirty index 0..len, derives dirty time including last+TF terminal boundary; same (first time,TF) shifts five current maps to prior, otherwise discards. Fresh maps and main index; no proof of unchanged prefix by scope alone.

**Handoff:** Live caller must provide valid dirty frontier; _dirty_time requires exact chronology object identity.

B06 overlapping link occurrences: 22.

## CP326-S06 — E07

Source: `engine/pipeline/e_zone_detector.py:220–265`.

Empty candidates call native compute. For physical First/Break sorted identities, distinguish entry presence, initial membership, B cause and parent-cause set. Group ordered repr, gate veto, both priorities and affected parent index; retain S source/A/decision/color, resets, validity. Exact key uses object IDs and ordered groups; cache hit restores candidates/accepted set and unions visual starts.

**Handoff:** Ledger evidence precedes reuse; no broad independent runtime equivalence claim; cache key and scoped lookup distinct.

B06 overlapping link occurrences: 51.

## CP326-S07 — E07

Source: `engine/pipeline/e_zone_detector.py:267–309`.

Replay compatible validity: rewind from dirty for changed candidate/parent groups, S groups and reset difference; bisect steps, take boundary checkpoint or terminal fallback. Only _ReopenedERace caught, restart without checkpoint. Save only non-reopened result with original input/native/numbered/evidence.

**Handoff:** Dirty frontier is owner premise, not proof; checkpoint reuse is conditional, no general exception suppression.

B06 overlapping link occurrences: 51.

## CP326-S10 — E11–E14

Source: `engine/pipeline/e_zone_detector.py:413–438`.

Reset delegate unchanged; clamped main index delegates underflow clamp only. Lower index non-null selects strict first_less/greater and returns result even miss; otherwise linear half-open strict Decimal predicate. Policy extreme normalized.

**Handoff:** CP322-E11 provider fallback time is not independent strict lower proof. CP332-G42 index owner.

B06 overlapping link occurrences: 19.

## CP326-S14 — E28–E29

Source: `engine/pipeline/e_zone_detector.py:581–606`.

Map parent stop/end to main positions; lower bound start, upper bound end, promote reversed end to start with no reclamp. Live or shared native range includes both entire OHLC candles, else sparse earliest strict extreme. Source can use full main candle after exact decision tick.

**Handoff:** Geometry source differs from exact chronology; no intrabar truncation or later-source price renormalization.

B06 overlapping link occurrences: 25.

## CP326-S15 — E30–E31

Source: `engine/pipeline/e_zone_detector.py:608–675`.

Inherited S only; gate-owned query executed although result unused; carried before registration, register, accepted iterator then direct. S without carried uses earliest inherited crossing or range_end; S bounded/E trend flags. Merge crossed direct/inherited/carried and accepted equal-cross groups by exact event then later First; exact ties route order. Prospective full-main source fed to disowned-only S predicate; first survivor wins, then optional cache.

**Handoff:** CP337 distinguishes creators from consumers; no extra gate-owned route, no local rollback on rejected/exhausted race, presentation ordering not E ordering.

B06 overlapping link occurrences: 50.

## CP326-S16 — E32

Source: `engine/pipeline/e_zone_detector.py:677–733`.

Assert crossing, decision=max(parent stop,cross exact), map decision and parent stop to main. Store supplied frozen source tuple, normalized parent/box prices; retain match stop level/source and cause tuple unchanged, map First/Break/box indexes to detector times. No extra stop/source query.

**Handoff:** No new Order creation and no EZone separate Order-cross field; exact decision not inferred from main time.

B06 overlapping link occurrences: 25.

## CP326-S17 — E33–E34

Source: `engine/pipeline/e_zone_detector.py:735–763`.

Consumed S evidence retains original S and normalized owner pair; apply in encounter order to first matching owner in evolving result, skip absent, call continuation and replacement even empty.

**Handoff:** Internal path uses default empty independent-A identity set; Bridge can pass independent identities explicitly; consumed S is evidence, not public creator.

B06 overlapping link occurrences: 14.

## CP326-S18 — E35

Source: `engine/pipeline/e_zone_detector.py:765–822`.

Reject S same physical source as owner or already E owned. Strict stop required; inherit owner family/number+1. Iterate _zone with owned times including owner; null/repeated index stops, invalid S without cause needs independent A identity, reset (parent source,zone source] terminates. Append then next strict stop, increment after success.

**Handoff:** Creation effects from _zone precede rejection; no rollback in helper; no fixed depth cap.

B06 overlapping link occurrences: 38.

## CP326-S19 — E36–E37

Source: `engine/pipeline/e_zone_detector.py:824–869`.

Empty or non-earlier first continuation returns shallow copy and does not reset accepted IDs. Base identity map last wins; trace E-parent lineage with seen guard. Compare new first decision strictly against earliest direct child; replace descendants, conflict resolve and refresh accepted IDs only on replacement.

**Handoff:** Only earlier continuation wins here; do not confuse with independent E1 restoration E40, which has no new-vs-existing decision comparison.

B06 overlapping link occurrences: 32.

## CP326-S20 — E38–E39

Source: `engine/pipeline/e_zone_detector.py:871–913`.

Physical identity int index/time; first entry wins unless higher injected E priority, or same family/equal priority higher number. Equal priority different family retains incumbent. Stable final source time/raw index/decision ordering.

**Handoff:** No independent hardcoded priority policy, renumber or price-only identity; final public visibility remains lifecycle-owned.

B06 overlapping link occurrences: 20.

## CP326-S22 — E41

Source: `engine/pipeline/e_zone_detector.py:1007–1029`.

Invalid S gate applies only exact S parent pair in invalid set. Initial A identity or truthy B cause exempts, missing current entry rejects; otherwise require parent-stop cause other than S at invalid time, not invalid pair. No tuple-shape recovery.

**Handoff:** Independent physical creation permits geometry reuse, not an invalid S creation cause; cause source-time projection intentionally distinct.

B06 overlapping link occurrences: 22.

## CP326-S23 — E42 discovery

Source: `engine/pipeline/e_zone_detector.py:1031–1084`.

First pass strict stops and register all stopped S before any chains; registration may decline. Second pass independent chains start color/1, collect provisional _zone results, stop on null/repeated index or no strict E stop. Mark owned source times, no direct E41 or sequence reset gate in loop.

**Handoff:** Discovery is provisional, not public or accepted ledger; no artificial cap.

B06 overlapping link occurrences: 27.

## CP326-S24 — E42 pruning

Source: `engine/pipeline/e_zone_detector.py:1086–1122`.

If invalid set and candidates nonempty, map E-parent continuation physical time/index to families. Invalid root with any unequal family at its source blocks entire root chain; flatten unblocked in encounter order.

**Handoff:** Does not roll back earlier registration; cross-family geometry pruning not deletion of independent A/B creation.

B06 overlapping link occurrences: 36.

## CP326-S25 — E43

Source: `engine/pipeline/e_zone_detector.py:1124–1130`.

Non-null live continuation delegates reconcile; otherwise native compute element zero. No catch/fallback locally.

**Handoff:** Conditional callback existence is not evidence that live path executed.

B06 overlapping link occurrences: 4.

## CP326-S28 — E48–E49

Source: `engine/pipeline/e_zone_detector.py:1220–1285`.

Order validity evaluates disowned-only, gate veto, then invalid-S-without-cause. S parent exists and not occupied E; reset own source<=boundary or A source<boundary rejects. Prior numbered time strictly earlier; rebuilt S or unused earlier Red S vs Blue prior accepted. Non-S boundary/active physical parent else recursive trace skipped invalid Order but not invalid-without-cause; shared seen no pop.

**Handoff:** Preliminary parent eligibility is not final winner's active-parent check; source-time-only used-parent tracking preserved.

B06 overlapping link occurrences: 67.

## CP326-S29 — E44 loop/E50

Source: `engine/pipeline/e_zone_detector.py:1287–1324`.

Stop predicate requires decision strictly later plus strict directional penetration of prior price, not a rescan. Snapshot before group, disowned current candidate with active parent reraces real parent; checkpoint raises internal reopen before native rerace. Native sets reopened then enqueues. Filter valid and active; empty skips.

**Handoff:** Same-source enqueue can extend shared group; absent parent skips before reopen; no general monotone source claim.

B06 overlapping link occurrences: 41.

## CP326-S30 — E44 family gates

Source: `engine/pipeline/e_zone_detector.py:1325–1364`.

Suppress S candidate stopping active E if owner red or candidate blue and maximum indexed child decision>=candidate decision. Prefer subset excluding Blue E-parent with unaccepted later Red S source and decision<parent stop; if empty retain eligible. Red S preference does not independently test E41.

**Handoff:** Child index contains provisional as well as accepted candidates; no winner selection before gates.

B06 overlapping link occurrences: 38.

## CP326-S34 — E52/E44 projection

Source: `engine/pipeline/e_zone_detector.py:1465–1492`.

Walk candidate ancestry with shared seen pair; collect parent-stop event before terminating S. Optional terminal checkpoint at len(candles). Save native tuple first; project E parent to StopAll if parent source in reset map. Publish accepted set and copied candidates.

**Handoff:** Lineage evidence not final display, parent-type projection does not rewrite physical geometry.

B06 overlapping link occurrences: 28.

## CP326-S36 — E54

Source: `engine/pipeline/e_zone_detector.py:1509–1538`.

Wrapper forwards all nine caller positional values and four explicit keyword options, calls detect. Priority null default fails required constructor gate; advanced resets, exceptions, B legs/live scope omitted and use constructor defaults.

**Handoff:** Do not conflate wrapper and Bridge direct constructor or universal live execution.

B06 overlapping link occurrences: 9.

## Accessor CP322-E11

E11 passes reset unchanged. Provider cache key retains index/from_first, second/display/timestamp and broken-level string; priority truthy second_time parse, else truthy display_time parse, else timestamp. No strict Order_B reset reconstruction or separate exact lower proof. E constructor sorts by this delegate.

## Findings and scope

- CP338-F01 / DOCUMENTATION_CORRECTED: E-M05 earlier wording 'preserve earliest direct S-parent geometry selection' ambiguous: E40 chooses earliest existing only for removal and appends root without comparing its decision. Detailed E40 remains unchanged.
- CP338-F02 / QUALIFIED: Live cache/replay depends on caller dirty evidence, actual selected Order ledger, scope and identity; no runtime claim.
- CP338-F03 / OPEN_CROSS_OWNER: Lifecycle, Bridge and Live handoffs remain queued; F05 and CP333-R01/R02 not closed by local E rereview.

Queue: 116/185; remaining 69. Supplemental accessors: 6/9; remaining 3. W1 B06: 1109/1109 retained, 626 overlapping link occurrences. Runtime and RAW NOT_RUN. Historical evidence preserved. CP339 / W2 Lifecycle queue semantic reconciliation: directly rereview 17 queued Lifecycle records against W1/B07, active Lifecycle/StopAll/E/Order specs and pinned source; follow with 5 Primary, 45 Trading Pipeline, 2 Live records and CP322-E02/E03/E04. CP331-F05 and CP333-R01/R02 remain OPEN; W2 not accepted.
