# CP326 — W2 E reconciliation

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`. Static scoped review; no runtime/RAW execution. 147 prior transitions retained, 36 new transitions; overlaps/duplicate IDs zero.

## CP326-S01 — E records

Source: `engine/pipeline/e_zone_detector.py:35–100`.

Frozen EZone and live progress/reconciliation records retain physical parent and Order identity, exact event times versus main timestamps, frozen source price, cause and route. Frozen wrapper does not recursively freeze nested objects. Internal reopen signal distinct from public result.

## CP326-S02 — Live init/advance

Source: `engine/pipeline/e_zone_detector.py:112–146`.

Require nonempty times and dirty main index in 0..len. Market scope is first main timestamp and timeframe; dirty time is indexed main or last+timeframe. Same scope moves current stop, extreme, zone, reconciliation and scoped caches to previous; new scope discards them. Current caches and main index reset, chronology reference replaced.

## CP326-S03 — Live parent stop cache

Source: `engine/pipeline/e_zone_detector.py:148–174`.

Chronology identity required. Stop key is direction predicate, start and numeric Decimal level. Prior null or hit >= dirty reopens progress at min(scanned_until,dirty); prior retained hit returned only before range_end. Resume from max(start,scanned_until), return null if start>=end; fresh callback result stored as event or range_end coverage. Caller maintains coherent search contract.

## CP326-S04 — Live main extreme

Source: `engine/pipeline/e_zone_detector.py:176–194`.

Key direction/start/end; reuse previous only when end main time < dirty. Lazily index main candles; use range minimum for bullish and maximum for bearish over [start,end+1); earliest equal extreme. Store actual candle index, main timestamp and price.

## CP326-S05 — Live E object cache

Source: `engine/pipeline/e_zone_detector.py:196–218`.

Key includes parent, Order physical identity and geometry, route, cause, stop, confirmation, crossing and source; price strings preserve representation in this key. Prior object reused only when max(parent stop, crossing, confirmation)<dirty; current hit has no additional cutoff. No independent First/Break or source timestamps in key; coherent chronology is required. Native race determines arguments before cache lookup.

## CP326-S06 — Live reconciliation dependency

Source: `engine/pipeline/e_zone_detector.py:220–265`.

Empty candidates delegate to native reconciliation. Evidence includes ordered candidate identities and repr, ledger presence/initial/B/parent causes, blocked query, both family priorities, source and parent indexes, S source/A/decision/color, resets and invalid/visual starts. Key retains candidate object identities and grouped insertion order; scope direction/live_scope. Exact cache hit restores candidate list, accepted identities and visual starts and returns list of numbered records.

## CP326-S07 — Live reconciliation replay

Source: `engine/pipeline/e_zone_detector.py:267–309`.

For compatible prior validity, frontier is min(dirty main, changed candidate source and parent indexes, changed S groups, mapped reset symmetric difference). Bisect previous steps; restore preceding steps and checkpoint, or last step with last retained step removed. Replay catches only internal reopened-race signal and restarts without checkpoint. Save only non-reopened reconciliation; retain original candidates, native and numbered results and evidence. No universal arbitrary-input guarantee.

## CP326-S08 — E detector initialization

Source: `engine/pipeline/e_zone_detector.py:313–392`.

Validate direction and required priority. Copy invalid identity set; sequence reset setter copies mapping. Stable S sort by source_time,int index; resets exact sorted. Retain chronology references and inclusive main bounds/exclusive end. Native shared main index only with candle object identity; one-second lower index fallback if main absent, else sparse extrema. Live uses continuation. Truthy blocked/initial maps retained; B legs tuple; initialize mixin ledger and consumed/visual/candidate state.

## CP326-S09 — Sequence reset state

Source: `engine/pipeline/e_zone_detector.py:394–411`.

Getter returns actual mapping; setter copies and sorts and clears order_candidates, carried, post_stop and direct_parent_stop caches only. In-place mutation bypasses setter; no additional rollback/invalidation implied.

## CP326-S10 — Chronology and strict lower crossing

Source: `engine/pipeline/e_zone_detector.py:413–438`.

Reset and main-index accessors delegate, main lookup clamped. Search first strict lower low/high via prepared index or linear predicate; no main fallback and no retry on index miss. Normalize policy extreme.

## CP326-S11 — Native sparse main extrema

Source: `engine/pipeline/e_zone_detector.py:440–504`.

Per-chronology direction cache shares sparse index/pairs. Compare strict lows/highs, retain earliest position on equality. Inclusive query uses two overlapping blocks; nonpositive length returns left. No separate bounds validation in sparse helper.

## CP326-S12 — Parent/Order stop provider

Source: `engine/pipeline/e_zone_detector.py:507–557`.

Parent search starts max(start,range_start), lower interval half-open, strict directional penetration. Live progress or native mixin for Order; live per-detector raw start/Decimal key includes null, dirty validation on hit; live tuple main time from chronology.times, native from candle timestamp. Consistency requires coherent prepared chronology.

## CP326-S13 — Parent confirmation and stop

Source: `engine/pipeline/e_zone_detector.py:559–578`.

Reaction confirmation delegates with Order direction; First timestamp from main index. Parent type is not used to select predicate. Start at exact decision, normalized price, return (index,event) or null; no lower-to-main substitute.

## CP326-S14 — E price freeze

Source: `engine/pipeline/e_zone_detector.py:581–606`.

Main range includes complete OHLC of both stop and decision candles. Start max(detector start,mapped start), end min(detector end,mapped end), raise end to start if inverted. Native shared query when valid, else sparse; live separate index. Strict extreme wins, earliest equal. Extreme may occur later than exact decision within its main candle; do not intrabar-truncate.

## CP326-S15 — Global Order-route race

Source: `engine/pipeline/e_zone_detector.py:608–675`.

Inherited S only for S parent; evaluate gate-owned query even though local result unused. Carried before registration, register, accepted iterator, then direct. S without carried uses earliest inherited crossing or range_end deadline. Direct S bounded, E trend/parent flag. Merge crossed direct/inherited/carried and accepted equal-cross groups by (exact crossing,-First), stable route order. Prospective full-main source used to skip disowned-only S creator; first remaining wins, optional live cache. Ledger presentation order is not this race.

## CP326-S16 — E immutable construction

Source: `engine/pipeline/e_zone_detector.py:677–733`.

Decision max(parent stop,Order crossing); supplied frozen source unchanged. Record normalized parent index/price, exact physical Order direction/number/mode/cause/stop, Order and source geometry, main and exact events. Construction does not mutate accepted collection.

## CP326-S17 — Consumed S evidence application

Source: `engine/pipeline/e_zone_detector.py:735–763`.

Normalize owner physical pair; iterate evidence and first currently matching owner. Rebuild continuation then replace sequentially. Internal helper does not explicitly pass independent A Order identities, unlike Bridge caller; preserve default behavior.

## CP326-S18 — Continuation from consumed S

Source: `engine/pipeline/e_zone_detector.py:765–822`.

Reject same owner source or already E-owned S source. Require strict stop, inherit owner family/next number. Owned source times include accepted and owner. Reject null/repeated source index, invalid S unless independent A identity, or sequence reset in (parent source,zone source]. Append and continue only after strict E stop; increment number.

## CP326-S19 — Replacement by earlier continuation

Source: `engine/pipeline/e_zone_detector.py:824–869`.

Empty continuation returns copy. Last-wins source map; descend only through E parent chain with cycle guard. Earliest direct child by decision/source; replace only when first new decision strictly earlier, or no child. Remove descendants, keep unrelated/owner, resolve conflicts and refresh accepted identities.

## CP326-S20 — Physical source conflict

Source: `engine/pipeline/e_zone_detector.py:871–913`.

Group by (int source index,time). Higher callback E-family priority wins; same family then higher number; exact tie retains first object. Final stable order source_time,index,decision; no price-only identity.

## CP326-S21 — Independent E roots

Source: `engine/pipeline/e_zone_detector.py:915–1005`.

Mask dominant physical pairs. Eligible E1/S roots not invalid without Order; heap source time,index,original ordinal with equality set. Skip newly occupied parent. Disowned-only reraces parent and queues unseen result. Replace earliest same-parent existing root by independent root without earlier-decision gate, else add if five-field identity distinct. Mark root source even if not appended; resolve and update accepted.

## CP326-S22 — Invalid S gate

Source: `engine/pipeline/e_zone_detector.py:1007–1029`.

Only S parent with exact invalid source pair is tested. Initial A or B cause suffices independently; missing ledger invalid. Otherwise require parent-stop cause other than S at invalid source time. This is a gate, not removal of all suppressed geometry.

## CP326-S23 — Stopped-S discovery and candidate chain

Source: `engine/pipeline/e_zone_detector.py:1031–1084`.

Pre-register all stopped S before individual chain generation. Each chain starts parent color and number 1. Null candidate/repeated source index ends chain. Add source times to owned set; next E requires strict stop. No fixed recursion depth in source.

## CP326-S24 — Invalid root cross-family suppression

Source: `engine/pipeline/e_zone_detector.py:1086–1122`.

Map E-parent continuations by source geometry. For an invalid S root whose source also belongs to an E continuation of different family, remove entire chain. Prior ledger registration is not rolled back.

## CP326-S25 — Reconciliation dispatch

Source: `engine/pipeline/e_zone_detector.py:1124–1130`.

Optional live continuation delegates; native path returns first result of computation. No live execution required for static reconciliation.

## CP326-S26 — Reconciliation initialization

Source: `engine/pipeline/e_zone_detector.py:1132–1173`.

Group all candidates by source index. Heap includes groups >=frontier, each key independent minima source time/decision; known set. Restore checkpoint native numbered prefix, active, accepted sets and sequence_start. Candidate map last-wins, S map first-wins, physical pairs retained.

## CP326-S27 — Reconciliation helper indexes

Source: `engine/pipeline/e_zone_detector.py:1175–1218`.

Numbered index first physical/time; unique sorted times and used S parent time. Child max decision indexes all inputs and generated candidates. Enqueue null/known skip; copy input only at first mutation; update maps and group. Schedule different current source not already scheduled; no frontier guard or heap-key refresh for already queued group.

## CP326-S28 — Order validity and parent activation

Source: `engine/pipeline/e_zone_detector.py:1220–1285`.

Order gate order: disowned, gate-owned veto, invalid S. S requires parent present/not E-owned; post-reset source>sequence_start and A source>=start. Prior numbered time strictly earlier; absent or <=sequence start accepts; else rebuilt S or unused earlier Red S vs Blue prior. Non-S boundary equality/physical active parent, else recursively trace skipped invalid Order parent that is not invalid-without-cause. Shared seen set no pop; preliminary eligibility not final active check.

## CP326-S29 — Stop and reopened race

Source: `engine/pipeline/e_zone_detector.py:1287–1324`.

Candidate decision strictly after prior and price strict directional penetration; no new market scan. For disowned-only current candidate with active parent rerace actual parent; checkpoint raises internal reopen. Native rerace derives family/number from candidate S or actual E parent, enqueue. Filter valid Order and active parent, skip empty.

## CP326-S30 — Competing families

Source: `engine/pipeline/e_zone_detector.py:1325–1364`.

Suppress S that strictly stops active E if owner Red or S Blue and owner's max child decision>=candidate decision. Prefer subset not blocked by unaccepted later Red S with source>parent source and decision<parent stop against E-parent Blue; if subset empty retain eligible.

## CP326-S31 — Ranking and final parent gate

Source: `engine/pipeline/e_zone_detector.py:1365–1404`.

For E use first active parent matching source TIME, else own family. Rank min(-priority,decision,parent_stop), stable tie. Gather stopped family before final physical parent active/boundary gate; if selected fails skip whole group without runner-up.

## CP326-S32 — Family numbering and reset

Source: `engine/pipeline/e_zone_detector.py:1406–1453`.

Actual E parent family first active time match. Branch order Red parent, stopped Red, Blue parent, stopped Blue, original. Number max stopped same family+1 or 1. Remove stopped physical pairs, replace family/number only, update accepted. Reset source clears active and updates sequence_start, historical numbered stays.

## CP326-S33 — Regenerated child

Source: `engine/pipeline/e_zone_detector.py:1454–1464`.

Only regenerated winner triggers next stop and child race; mark reopened. Enqueue only child strictly later source index. No local rollback of rejected race side effects.

## CP326-S34 — Lineage and returned projection

Source: `engine/pipeline/e_zone_detector.py:1465–1492`.

Shared seen source pair; add parent stop to visual lifecycle starts, terminate S else follow candidate parent. Optional terminal step at candle count. Native tuple before projection; parent_type E becomes StopAll where parent source reset, no geometry change. Publish accepted identities and last candidates.

## CP326-S35 — Native detect pipeline

Source: `engine/pipeline/e_zone_detector.py:1495–1506`.

Clear accepted and ledger; register B; clear visual starts; discover and copy candidates; reconcile; apply consumed S, resolve conflicts; rebuild accepted Order ledger. No catch or runtime parity assertion.

## CP326-S36 — Public E wrapper

Source: `engine/pipeline/e_zone_detector.py:1509–1538`.

Forward positional chronology and source arguments and explicit keyword options; priority default null but constructor requires it. Other advanced live/reset/geometry options not universally forwarded.

## Cross-owner boundaries

- `engine/bridge/trading_pipeline.py:2153–2208`: Bridge constructs E with owner-specific priority, sequence resets, geometry/index inputs; prior CP323 rows retained.
- `engine/bridge/trading_pipeline.py:2293–2413`: Feedback, S invalidation and E recreation handoff; prior transition records not recounted.
- `engine/bridge/trading_pipeline.py:2508–2567`: Consumed evidence/continuation replacement and independent-root integration; Bridge supplies independent A physical identities.
- `engine/pipeline/lifecycle_engine.py:29–39`: Sequence priority is S Blue 1, E Blue 2, S Red 3, E Red 4; distinct module priority includes StopAll; unknown key errors.
- `engine/pipeline/lifecycle_engine.py:996–1136`: Consumed S evidence selection is lifecycle-owned; strict Close extension and owner stop/rank precede E continuation; detailed lifecycle rows reserved for CP327.
- `engine/pipeline/reaction_engine.py:1153–1192`: Main times may derive from supplied prepared index; per-chronology E extrema cache; clamp underflow and coherent chronology dependency.

## Remaining

CP327 / W2 lifecycle and StopAll: priority/identity, exact stops, ownership filters, consumption, final visibility, StopAll state/feedback; then Primary, projection/live and W3/W4.
