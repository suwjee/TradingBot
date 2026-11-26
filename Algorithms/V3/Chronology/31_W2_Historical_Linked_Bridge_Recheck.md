# CP346 — historical matrix-linked Trading Pipeline review

25/25 Bridge records reviewed from pinned source; cumulative 44/131 historical linked records. W2 NOT_ACCEPTED.

### CP323-P26 · engine/bridge/trading_pipeline.py:2211–2282

Fresh Blue→A→S uses full native inputs, opposite resets and initial geometry. Initial S is shallow copied, feedback reuses original Blue/A/S detector and initial S but copies current S and candidates. Live callbacks only on nonnull live.

Handoff: Shared first pass does not freeze E or feedback results; no proof of active incremental dispatch.

### CP323-P28 · engine/bridge/trading_pipeline.py:3531–3630

Reversal boundary strictly inside current candles; prefix excludes boundary and recalculates without live, including full prefix if no visible overlap. Requires Primary3 same source time and level (not index). Resolver precedence and indexed mode are independent. Next regime includes boundary, target trend flags exact; release in finally after segment construction. Publish copies indexes; incoming transition already absolute; stopped main timestamp controls status and cap.

Handoff: Cache hit still needs proof; no arbitrary reversal limit or geometry carry. Prefix construction is outside protected cleanup; optional live active resolver and cleanup not active-worker proof.

### CP323-S26 · engine/bridge/trading_pipeline.py:2153–2208

E constructed over full main indices with trend/opposite native reactions/resets, accepted audit, blocked times, exceptions, invalid S and B legs. Direct callback uses specified direction's geometry detector, optional geometry service checked nonnull. Live keywords only when continuation nonnull.

Handoff: Priority, geometry and ledger are owner services, not Bridge reconstruction; callback failure propagates.

### CP323-S27 · engine/bridge/trading_pipeline.py:2284–2469

Filter accepted A audit by S eligible sources; rerun E with reconciled S only if length differs, with TypeError fallback for membership. Preliminary A visibility helpers execute but their output is not split input. Split all eligible A with S candidates/current E and empty StopAll. A stop callback uses confirmation ordinal in split, but source time in order-context resolution. Stage-invalid and all-invalid identities distinct; exact E exceptions and opposite default-true confirmation forwarded to rebuilt E.

Handoff: Source-time collapse for A sources is deliberate, not physical pair equivalence. Callback selection differs by operation; no local ordinal guard.

### CP323-S28 · engine/bridge/trading_pipeline.py:2470–2645

Concatenate accepted audit values without dedup; changed S list triggers one rebuild and replacement by (A source,source) last duplicate. Consumed evidence excludes stage-invalid only; match current owner by int index and time, preserve independent A keys, rebuild audit with all supplemental S; final S excludes all invalid. Feedback 0–7, fixed original occupied E set, restored donors, StopAll conditional, ensure audit then discover B legs. Exact 17-field sorted signature retains multiplicity, not whole object (omits post-stop behavior_source_time). Equal signature registers; repeated unequal signature or eight-pass exhaustion raises.

Handoff: No new visibility rediscovery; accepted ledger rebuilt after continuation and ensured before B discovery. No general E or Primary eight-pass limit.

### CP323-S29 · engine/bridge/trading_pipeline.py:2648–2802

Requested both ordered bullish then bearish; enabled B/A/S requires both native reaction directions. Reusable iff E nonnull and S enabled, full geometry both. Independent geometry closures bind opposite direction; full lifecycle both only if primary present. Explicit lifecycle path selects StopAll. Report before storing maps. Fallback constructs both geometry finders, native detection for required directions, no live reaction/ownership calls.

Handoff: Conditional live reference retained without establishing dispatch. Stage callback failure propagates.

### CP323-S30 · engine/bridge/trading_pipeline.py:2915–2936

Nonreusable S full-range detector stored, detected candidates aliased as accepted, eligible A replaces earlier A. E list copied; invalid sets retained or default.

Handoff: No final display clipping here; detector ownership independent of visible range.

### CP323-S31 · engine/bridge/trading_pipeline.py:2939–3108

A visibility then converged E/StopAll copies. Existing E parent stop by a_source_time presence; fallback S stop starts at decision event. Capture projection lists before final visibility; primary groups before range clipping, A full noninvalid. Clip inclusive then exact invalid pair removal. Audit full accepted A sources, internal Blue marking, internal behavior filter currently copies. Required identity complete pair, audit preparation/validation gated by E-map membership not nonnull callback gate.

Handoff: Full S detector directly indexed even absent E; projection snapshots are joins not republication; required identity bypasses range not eligibility.

### CP323-S33 · engine/bridge/trading_pipeline.py:3405–3448

Finalize opposite range/visibility, alias primary groups, full audits for each owner using accepted A sources. Committed callback registers low for bullish else high, then refreshes that owner's audit. Native detect or conditional live primary service.

Handoff: Mutation only at committed Primary callback; no rollback of group/detector changes if callback fails.

### CP328-S28 · engine/bridge/trading_pipeline.py:3449–3458

Resolve directional primary labels through visible end, reconcile native detector, collect required identities from prior prepared visible audit and reprepare at visible bounds.

Handoff: Preserve identity not invalid cause; native numbering and relabeling delegated.

### CP328-S29 · engine/bridge/trading_pipeline.py:3461–3500

Primary direction bearish if both else requested; requires primary nonnull, E map key and explicit lifecycle path. Resolve StopAll physical ownership through horizon, validate audit then serialize; add Primary arrays if computed.

Handoff: No extra trading decision by serializer; visibility audit and StopAll ownership distinct.

### CP328-S30 · engine/bridge/trading_pipeline.py:3502–3528

Group regimes by direction encounter order; single segment original; multiple shallow-copy last metadata, list keys set iteration not stabilized, concatenate shared row refs, bridge keys first occurrence order, remove end time and retain original calculationSegments.

Handoff: No dedup, sort, recalculation or global T/F pass.

### CP329-S07 · engine/bridge/trading_pipeline.py:691–739

Exclusive upper horizon only; reject null event/level, normalize Decimal, lower time fallback only None; bisect and inspect equal timestamps only, bearish High> else Low<. Return exact event or null.

Handoff: Proof checks returned timestamp not native scan firstness; CP342 qualifies fallback proof.

### CP329-S08 · engine/bridge/trading_pipeline.py:742–759

Absent or late main stop nulls both fields. Otherwise main time formatted and exact proof independent; null proof does not erase main.

Handoff: Main stop is not exact lower proof.

### CP329-S09 · engine/bridge/trading_pipeline.py:786–819

Physical order pair requires both indexes nonnull; int normalization no local bounds validation. Prepared final audit indexed by pair, duplicate last wins.

Handoff: No alternate order geometry search or ledger mutation.

### CP329-S13 · engine/bridge/trading_pipeline.py:988–1042

Existing E parent stop catches AttributeError/TypeError/ValueError only around call; unpack/conversion/bounds afterward. S A stop catches those plus IndexError; unpack outside. Stop mapping uses proof plus independent string price.

Handoff: Owner method may execute native lookup/cache; no independent new stop selection or detector reconstruction.

### CP329-S16 · engine/bridge/trading_pipeline.py:1170–1179

Full Blue lines sorted stably by integer reaction number, source time, string kind; enumerate from one.

Handoff: Ordinal not visible-array position; invalid/internal full records retained for joins.

### CP329-S17 · engine/bridge/trading_pipeline.py:1182–1269

Independent full Blue ordinal lookups; emit main formation only; retain recorded stop fields. A stop via native S and proof. Optional one-based Reaction lookup, stored A First/Break main, exact confirmation flag false. Route mapping, null parent, current exact A cause (null family), own stop separate.

Handoff: Missing association cannot select substitute; provenance does not create Order.

### CP329-S24 · engine/bridge/trading_pipeline.py:1611–1676

Complete physical identity public S/E/StopAll must exist in prepared audit; collect missing and raise before cause test. Only parent-stop exact tuple type/family/event/source; same identity allowed, differing owner conflict collected and raised.

Handoff: No ranking, repair, alternate cause or bounds validation by invariant.

### CP330-S02 · engine/bridge/trading_pipeline.py:87–98

Load spec guard None/missing loader; register module before exec, fixed reaction name; no rollback.

Handoff: Configured module semantics conditional, not proved by loader.

### CP330-S08 · engine/bridge/trading_pipeline.py:255–277

Checked row int conversion equality, positive and nondecreasing (not exact int type); private price additions keyed type/value, validate and aggregate before published suffix mutation.

Handoff: Numeric equality distinct from byte lexeme and exact type; rollback boundary as CP345.

### CP330-S13 · engine/bridge/trading_pipeline.py:1788–1823

MarketIndexWindow flattens nested offsets, retains candles and slices times. First clamps bounds, empty null, translates nonnull hit including zero; extrema invalid bounds raise, translate position.

Handoff: Base index owns strict predicates, earliest tie and Decimal value; no extra normalization.

### CP330-S14 · engine/bridge/trading_pipeline.py:1826–1857

Require nonempty existing main segment; lower half-open first to next main or final+duration. Independent reindex unless indexed mode with corresponding zero offset. Register lower/main prepared windows in order, same chronology type and integer duration; local visible interval can be empty, accumulate offset; trend flags independently override or inherit at zero.

Handoff: New local chronology and optional shared index windows distinct; no price/time transformation.

### CP330-S16 · engine/bridge/trading_pipeline.py:1974–2009

Load order Reaction/Blue/A/S, optional E exact nonnull, lifecycle truthy configured/default always, primary fixed module if enabled (absent flag disabled) not timed separately.

Handoff: Lifecycle load not StopAll enablement; external configured semantics conditional.

### CP330-S19 · engine/bridge/trading_pipeline.py:2055–2079

Batch lower and shared index then main (TF1 alias), fresh chronology. Live asserts delta, updates views, registers both prepared sequences, fresh chronology with both indexes.

Handoff: No live trading stages implied; view/index refresh failures propagate to protected append.

CP345 continuation count typo corrected by exact IDs (25 not 26). CH37 and TR-M02 qualified. No production, runtime or RAW change. F05/R01/R02 remain open.
