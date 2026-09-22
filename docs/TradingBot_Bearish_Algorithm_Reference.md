# TradingBot Bearish Algorithm Reference

Source audit: 2026-09-18. Scope: the current working tree in `D:\My-Projects\TradingBot`, including uncommitted maintained Python files. This document describes executable behavior; it does not approve trading outcomes or claim an independent Bearish oracle pass. Source analysis was read-only.

## Authority and current versions

The executable source in `engine/pipeline/` and `engine/bridge/trading_pipeline.py` is authoritative for this reference. The older `engine/algorithms/TradingBot_Bearish_Algorithm_Reference_V4.0.1.md` and its Bullish counterpart are **historical documents**, not the current runtime contract. The longer `engine/TradingBot_Bearish_Algorithm_Reference.md` is useful background but also contains superseded version, selected-range, fixed-point and ownership statements. Resolve disagreements by inspecting the functions named here.

| Component | Source | Declared version |
| --- | --- | --- |
| Orchestration and JSON | `engine/bridge/trading_pipeline.py` | `1.2.2` |
| Reaction, Reset, chronology, shared Order geometry | `engine/pipeline/reaction_engine.py` | `9.5.2` |
| Blue Line | `engine/pipeline/blue_line_detector.py` | `2.3.0` |
| A | `engine/pipeline/a_zone_detector.py` | `1.6.3` |
| S | `engine/pipeline/s_zone_detector.py` | `4.13.1` |
| E | `engine/pipeline/e_zone_detector.py` | `6.6.2` |
| StopAll and lifecycle | `engine/pipeline/lifecycle_engine.py` | `1.10.1` |
| Direction policy | `engine/pipeline/direction_policy.py` | `1.0.0` |
| Numeric utilities | `engine/pipeline/core_utils.py` | `1.0.0` |

Versions identify constants, not immutable source snapshots. In particular the current lifecycle implementation differs from historical fixed-point documentation despite retaining `1.10.1`. Current A is `1.6.3`, not the `1.6.2` quoted by the older maintained reference.

## Input, time and full-RAW semantics

`prepare_market_context()` reads the complete supplied JSON input, strips an optional UTF-8 BOM, parses with `orjson`, and gives **all supplied rows** to `build_candle_buckets()`. Inside the bridge, requested `from_time` and `to_time` remain presentation bounds. The application now owns range isolation before the bridge starts: a full-chart request supplies the original RAW path, while a partial request streams only source rows in the inclusive selected chart-candle buckets through a Windows named pipe. The partial calculation therefore starts with empty state at the selected `from` candle and has no chronology after the selected `to` candle.

Required row fields consumed here are `time`, `open`, `high`, `low`, `close`. Time is integer Unix seconds. Prices become `Decimal` through shared conversion; the normalization cache keys both Python type and value so `10` and `10.0` are not silently conflated. The bridge walks input order: it is not a general sorting, gap-filling or arbitrary duplicate-repair routine. Chronological, valid OHLC input remains an upstream contract.

Consecutive equal-second rows aggregate to first Open, maximum High, minimum Low and last Close. Main buckets are aligned by `time // timeframe * timeframe`, with the same OHLC aggregation. Lower candles are the actual available timestamp buckets; the variable name `seconds` does not prove complete one-second coverage. No missing candles are synthesized.

Main candle indexes refer to the complete supplied input. For `/api/reactions` partial requests, that input is the selected range and indexes are therefore range-local; direct bridge calls with a full RAW file retain full-file indexes. Requested bounds are floored to bucket opens; binary search selects through the bucket containing `to_time`, inclusive. The application passes the final available source-row time as the effective bridge end bound so analysis timeframes finer than the chart remain visible through the complete selected `to` candle. `actualFrom` and `actualTo` report selected main-candle opens. Display strings use `Asia/Tehran`; public JSON times are epoch seconds. Time, source index, source candle time and exact event time are separate provenance fields and must not be substituted for one another.

The calculation path is `Reaction/Reset -> Blue -> A -> S -> E -> StopAll -> final ownership/visibility -> serialization`. Opposite-direction Reactions and Resets are dependencies of Bearish S/E even when only Bearish output is requested. Disabling a visible lower-stage collection does not necessarily remove that stage from downstream calculation.

### Process and application contracts

`parse_arguments()` requires Reaction/Blue/A/S engine paths, `--data`, integer `--timeframe`, `--from-time`, `--to-time`, and `--direction bullish|bearish|both`. The engine-path flags retain `--engine`, `--blue-engine`, `--a-engine`, `--s-engine`, `--e-engine`, and `--stopall-engine` aliases. E and lifecycle paths are optional; Blue/A/S switches default to enabled. Positive timeframe is explicitly checked. Loading shared lifecycle helpers without an explicit lifecycle path does not enable public StopAll: that requires the explicit path, E and enabled S.

The bridge writes compact JSON on stdout and `QG_PROGRESS:` JSON on stderr. Runtime errors inside guarded execution yield an `error` JSON object and exit 1; success exits 0. Argument parsing uses normal argparse failure behavior/exit 2. A dependency-import failure before guarded execution can bypass JSON error handling. `timed()` emits a completed progress phase in `finally`, so that word alone is not evidence that a phase succeeded.

The current caller is `apps/chart/vite.config.js:runDetector`, using a fresh `TRADINGBOT_PYTHON || "python"` process and all six explicit engine paths. `POST /api/reactions` accepts `{id,timeframe,chartTimeframe,from,to,direction,blueLines,requestId?}`, supports one requested direction, enables A/S and supplies E/lifecycle. `chartTimeframe` determines the exact inclusive source buckets streamed for a partial request and participates in the durable calculation-cache identity. Progress is available at `/api/reactions/progress`; endpoint failures become HTTP 400. This application contract is narrower than the bridge's `both` option.

Full E execution is staged rather than one detector call: initial Blue/A/S/E; possible E rerun after S eligibility changes; dominant-stop A/S and blocked-Order arbitration; unconditional final-audit E rebuild; possible E rebuild after shared-Order S reconciliation; then consumed-S continuation replacement. Normal execution therefore runs E two to four times per requested direction before possible continuation construction. The later single-pass StopAll contract does not mean that E itself runs once. Reduced execution without E or with S disabled returns empty E/StopAll/OrderAudit collections.

## Direction and exact comparisons

Market color is `GREEN` for `Close >= Open` and `RED` otherwise. A doji therefore remains GREEN in public market semantics. Bearish trend geometry uses High/max/strict `>` for stops and adverse boundaries; its Reaction confirmation is strict `Low < BoxBottom`. Its opposite Order is Bullish, whose stop is strict `Low < OrderStopLevel`. Equality never constitutes one of these strict breaks.

`BearishDetector` executes the Bullish reference state machine through a read-only coordinate adapter: `(O,H,L,C) -> (-O,-L,-H,-C)`. Decimal `copy_negate()` avoids context-rounding during reflection. It swaps private GREEN/RED roles, including the role of a GREEN market doji, and mirrors price/source fields back afterward. This internal role transformation does not recolor market candles. Time, indexes, chronology, modes, family labels, counts and parent identities remain invariant. The production unified detector also has explicit directional branches; therefore a reference-adapter equivalence alone is insufficient to prove the entire public pipeline equivalent.

Lower-timeframe indexed queries resolve first strict crossings and exact extrema. At a true tie inside the finest available candle, Reaction invalidation/Reset precedes confirmation; an S candidate-cross/Order-stop tie rejects the S decision. Different modules deliberately use different equal-extreme ownership rules, described below.

`as_decimal()` preserves Decimal input or uses `Decimal(str(value))`; ordinary JSON decimal-number lexemes first pass through `orjson` Python numeric conversion. Thus Decimal calculations do not guarantee preservation of every original JSON floating-point lexeme. No explicit Decimal precision/context is configured here. `MarketChronology` lower windows are `[start,end)`. Its unresolved Reaction confirmation fallback is Break main-candle open; A explicitly ignores a private intrabar start in that lookup while S/E can use it.

## Reaction and Reset

Source: `reaction_engine.py`, `BullishDetector`, `BearishDetector`, `UnifiedReactionDetector`, `MarketChronology` and `published_reaction_candidate`.

### Mode A: Leg-Start

The Bearish initial candidate is the exact reflected reference pattern. A GREEN First follows a RED candle/run. When a GREEN anchor exists, the prospective First High must be no greater than the anchor High; without that anchor it can pass by being no greater than the preceding candle High or frozen leg-opening High. The preceding contiguous RED run contributes its minimum Low. The smaller of that minimum and First Low establishes BoxBottom; equality preserves the prior run owner. First High initializes BoxTop. Later strictly greater High updates BoxTop while waiting.

The candidate's anchor/leg ceiling is frozen. A strict High above that boundary before strict Low below BoxBottom invalidates the candidate. If both occur on one main candle, finest-event order decides; equal finest-event position is invalidation-first. Internal BoxTop updates do not themselves redefine the frozen owner boundary. An invalidated candidate is not revived by a later break; search resumes from an eligible later First with the appropriate restart/anchor context.

The reference scanner explicitly handles leg-opening GREEN anchors, RED Reset context followed by a qualifying GREEN, and anchor cleanup after invalidation. `UnifiedReactionDetector` applies additional gate ownership to bounded/direct searches; a generic two-candle pattern is not a substitute for that state machine.

### Mode B: Normal continuation

After an accepted Bearish Reaction, the running bottom tracks the minimum Low from the Break candle onward. A subsequent eligible GREEN becomes First. BoxBottom is the lower of running bottom and First Low, retaining the prior owner on equality. BoxTop is the maximum High from immediately after an earlier bottom owner through First, or from First itself when First owns the bottom. Further strict High updates BoxTop until Low strictly crosses BoxBottom.

The confirmation helper locates the first strict lower-timeframe breakdown. Its opposite-edge maximum includes the confirmation event, not later finest candles. A remaining part of the same Break candle can supply a successor only through `_candidate_from_confirmation_remainder()` and its ownership checks.

### Reset and same-candle ownership

A confirmed Bearish Reaction resets at strict `High > confirmed BoxTop`. If a pending Reaction also confirms on that main candle, exact lower events determine whether Reset or breakdown happens first, with Reset winning an exact tie. Reset records the broken level, containing main index/time, owning First index and, where resolved, exact `secondTime`.

After confirmation, only the remaining portion of the same Break candle is inspected for a strict opposite-edge Reset. When such a Reset exists, the Break candle belongs to that completed/reset transition and cannot also seed the next Normal FirstGreen. The next search is a new Mode-A leg. The unified detector's ordinary post-Reset route is `_first_direct_same_direction_after_reset`; structural/bounded cross-direction search helpers have separate gates and must not relabel ordinary history indiscriminately.

`_owner_boundary_before_confirmation()` also protects direct recovery and Order geometry: breaking a frozen owner boundary first kills the geometry. Gate outcomes, blocked First times and canonical identities are calculation state, not UI filters.

### Public Reaction geometry

The serializer calls `published_reaction_candidate()` on a clone. If Break owns the Bearish BoxTop, the published BoxTop is recomputed from eligible earlier main candles plus lower candles through the first strict breakdown, inclusive. Equal maxima retain the earliest main owner. If no strict lower confirmation can be resolved, the detector geometry is retained. This presentation clone does **not** rewrite the internal geometry used by downstream engines.

## Blue Line

Source: `blue_line_detector.py`; formation/stop timing is resolved by A's `_formation()` and `_build_blue_states()`.

For Bearish, the Fibonacci threshold is `BoxBottom + 0.618 * (reference - BoxBottom)`, using exact `Decimal("0.618")`. Mode A takes reference from its anchor or leg boundary and resets the previous strike-count comparison. Mode B takes the previous Reaction's BoxTop. Missing required Mode-A boundary or a Normal Reaction without a preceding Leg-Start is an error.

A new strike requires High strictly above the threshold for the first strike, or strictly above the previous confirmed strike High. A pending strike retains the strictly larger High. A RED main candle confirms pending evidence. A final pending strike can be resolved intrabar through the Reaction Break, requiring strict penetration and then a strict Reaction breakdown; the decisive maximum maps back to its main source candle.

A scale Blue requires a current strike count strictly greater than the previous Reaction's count. The first Blue is permitted directly; later Blues require at least one intervening healthy Reaction. A non-emitted scale candidate still advances the comparison to the current count. Reset Blue obeys the same spacing state, and resets are associated by their owning First index.

| Kind | Bearish drawn price | Stop/reference extreme | Timing |
| --- | --- | --- | --- |
| Scale | `High - (High-Low)/3` of decisive source main candle | Decisive strike High | Forms at exact owner Reaction confirmation; stop search starts there |
| Reset | `High - (High-Low)/5` of Reset main candle | Reset main High | Forms at exact Reset; its own stop search starts at next main-candle open |

Both draw from one timeframe before source through one timeframe after source. Drawn `linePrice` is not the stop level. A Reset Blue is calculation-invalid when the prior Blue already stopped before the Reset candle and the Reset candle also strictly crosses that prior source extreme. Such double-stop evidence is retained for A's dedicated path; invalid Blues do not enter ordinary valid Blue states. Public filtering also removes internal Blues. Full calculation ordinals can consequently have gaps.

## A

Source: `a_zone_detector.py`, especially `_pair_trigger`, `_inherited_stop`, `_a_source`, `_double_stop_a_candidates`, `_detect_ordinary_a`, `_filter_special_a`.

A uses adjacent eligible Blue states in their existing ordinal order. A prospective pair expires when the following Blue forms. The first Blue must have a strict stop within the pair's life. Ordinary triggers are resolved in this order:

1. **Inherited continuation:** an eligible same-direction Reaction between prior Blue formation/stop and current formation establishes the carried level. After an ordinary valid Blue has stopped, scan from its stop main candle through the next eligible Bearish Reaction's complete Break main candle, inclusive, and freeze maximum High. The current Blue must subsequently cross this level strictly. This applies to every ordinal, not only a named Blue-1/Blue-2 fixture.
2. **Prior Blue stopped before current formation:** freeze maximum High from the exact prior stop through the main candle preceding current formation. A strict crossing during current formation can trigger immediately; otherwise current must stop and the frozen continuation level must then be crossed, before expiry.
3. **Coexisting Blues:** both must stop. Sort stops by `(exactStopEvent, stopLevel)` for Bearish, so lower stop level is first when exact events tie. The first stop's event extreme is the continuation threshold; different events require a strict cross from the second event onward. A same-event double stop uses that event directly as the trigger.

The validating Bearish Reaction must confirm at or after the trigger and have First no earlier than the effective Blue stop boundary required by the pair. A source is maximum eligible High from **trigger main-candle open through exact validating Reaction confirmation**, inclusive; subsequent prices in the same Break candle cannot relocate it. A first equal maximum keeps its earlier owner.

The special double-stop path takes a calculation-invalid Reset Blue plus its preceding valid Blue, requires that predecessor's strict crossing on the Reset source candle, and validates with an eligible same-direction Reaction. It uses the same exact-confirmation A source function and then passes special-candidate filtering against ordinary results.

Accepted A advances the cycle through its validating Break. Current `1.6.3` includes a narrowly gated adjacent Blue reuse: after A's strict stop, if the next Blue forms at or after that event, the previous pair's second ordinal can bridge into the next pair. Otherwise Blues already consumed through the cycle are skipped. This is not unrestricted Blue-pair reuse.

Native A validity is provisional until lifecycle arbitration. A that overlaps an accepted handoff/closed dominant transition can be calculation-invalid even though its pair geometry formed. Final serializers emit accepted A with `calculationValid: true`.

## S

Source: `s_zone_detector.py`; shared stop geometry in `MarketChronology.canonical_order_stop()`.

An A stops strictly at `High > A.price`. S selects eligible Bullish opposite geometry after that exact event. A canonical opposite Reaction can share the main A-stop candle if its exact confirmation is later. Bounded search cannot skip an earlier canonical identity; matching First/Break geometry must be canonicalized before computing Mode-dependent stop provenance. Stopped-A Order audit is collected separately from whether an S eventually publishes.

For a Bullish Order, Mode A stop is minimum Low over its true anchor/context through Break inclusive, extending through the preceding relevant RED context. Mode B stop inherits the previous healthy Bullish Reaction's BoxBottom and source. Mode B without a previous owner raises an error. Its strict stop condition is `Low < stopLevel`.

### Simple and Advanced branches

The initial Bearish price classifier calls the candidate post-Order when `Order.BoxTop >= AStopMain.High`; equality is post-Order. A valid nested Advanced owner preserves this classification. Otherwise exact candidate formation can override it to pre-Order only when that event is strictly before the Order First main timestamp.

* **Simple pre-Order:** maximum High from the exact A-stop remainder through Order First, retaining first equal maximum. Its own exact formation event is resolved. The decision race starts at Order confirmation; an unqualified candidate crossing can return an internal fallback status and transfer selection to the ordinary later branch.
* **Advanced:** a Bearish Reaction must begin strictly after Bullish Order First, finish no later than Order Break/confirmation and remain geometrically inside the Order box. Candidate source is the Order BoxTop source main candle and price is that main candle High. Candidate crossing is gated by nested Reaction confirmation.
* **Simple post-Order:** use the first eligible Bearish Reaction after Order confirmation. Candidate is maximum High over Order Break through Bearish Break inclusive, using the **last** equal maximum. Other source helpers deliberately use first equality; these policies are not interchangeable.

### Red/Blue decision

Scan exact lower events from Order confirmation with the branch-specific candidate gate. If both `High > candidate` and `Low < OrderStop` occur in the same finest event, reject the decision. Order stop first yields **S Red**. Candidate cross first yields **S Blue** only with qualifying Blue evidence or an ordinary aligned Reaction in the required behavior interval. Unqualified crossing can invoke only the explicit pre-Order fallback path. If lower events exist but none decide, do not invent a main-candle result; a main-candle fallback is used only when that lower window is empty.

For Red, preserve an accepted pre-Order candidate when applicable; otherwise recompute maximum High from Order Break through the decision main candle, inclusive, with first-equality ownership. Red/Blue describe behavior families and never swap under price reflection.

### Type 3: Reset-leg S without an Order

An eligible opposite Bullish Reaction is already confirmed at/before A stop and has not reset by then. Its own Reset occurs strictly after A stop and before the new-Order deadline. Freeze maximum High over its complete Break-to-Reset main-candle interval, taking the last equal source. After that Reset, a strict High crossing before the deadline plus a Bearish confirmation in `(AStop, crossing]` completes Type 3. Choose the earliest decision. Type 3 is always Blue and carries Reset owner/time; Order-specific fields are null. It is not an inferred Order_B.

An unresolved S can later be resolved by the strict stop of another accepted physical Order in the same lifecycle through `reconcile_shared_order_stops()`. Arbitrary opposite Reactions are not Orders. The first accepted S-parent-stop Order establishes the continuation terminal boundary, preventing later independent-lifecycle Orders from retroactively changing the older S.

## E and physical Order ownership

Source: `e_zone_detector.py`, `reaction_engine.py` geometry helpers and `lifecycle_engine.py` accepted-audit preparation.

E starts at a strict S/E parent stop (`High > parent.price`). A stopped accepted S opens E1 in its family; recursive E continuation advances its family/number subject to dominance, ancestry, source-reuse guards and lifecycle reset boundaries. Parent, source and decision are separate identities.

**Direct Order_A:** `_direct_parent_stop_order()` compares canonical Bullish Reaction availability with healthy bounded post-gate geometry. Published geometry remains canonical when it supplies the accepted strict stop. Earlier bounded geometry can qualify in the explicit no-canonical-stop fallback, S continuous/restart/continue branches, and the narrow E trend-leg exception. In that E exception a newly confirmed ordinary non-internal Bearish leg supplies a fresh direct gate; allowed bounded Bullish Mode-A continuation retains true anchor provenance and reaction number `0`. These conditions are not a blanket permission to manufacture Orders.

**Reset-leg Order_B:** use the owning Bullish Reaction's full Break-to-own-Reset interval to freeze maximum High, require an actual Reset and subsequent strict High boundary crossing, and require ordinary Bearish evidence in the gate window. Only that opposite owner's Reset releases its ownership; a Bearish Reset does not. Local bounded geometry is a search aid: an exact published `(FirstIndex, BreakIndex)` identity is required for the accepted Reset-leg Order. Blocked Firsts, owner lifetime and deadline checks remain in force. Noncanonical geometry already open in the gate main candle is pre-gate and search advances.

`order_candidates()` merges identical First/Break geometry and its independent `parent-stop`/`reset-leg` causes. Candidate confirmations are bounded by earliest known eligible Order-stop time and any explicit continuous deadline. Direct, inherited unconsumed-S and carried-live paths each provide their representative to the final race. E chooses earliest exact Order stop; in that final cross-path race an equal stop event prefers the **later First index**. Candidate-pool sorting elsewhere uses different chronological keys; do not globally substitute one tie policy.

The E decision is `max(parentStopEvent, orderStopEvent)`. E source is the maximum High over **complete main candles** containing parent stop through decision, inclusive; the first equal maximum retains ownership. This intentionally differs from A's exact-confirmation-truncated endpoint. E copies complete parent/Order geometry, cause timestamps, source owners and decision provenance.

Reconciliation rejects invalid/blocked parent paths, prevents recursive reuse of source in an ancestry chain, and rebuilds audit from accepted lineages. A consumed S can continue a dominant E family instead of opening an unrelated E1. An independent accepted S can retain its E1 root, but an S whose physical source already belongs to accepted E cannot be restored as a competing parent.

At one physical `(sourceIndex, sourceTime)`, exactly one E wins: Red before Blue regardless of number, then higher number within one family. Exact family/number ties preserve already accepted provenance. This dominance is applied early enough that slightly earlier lower-priority confirmation cannot discard a competing Red branch. An invalid S cannot open a cross-family root over a native E continuation already occupying that exact source; this is not a blanket deletion of all invalid-S evidence.

## StopAll and final lifecycle

Source: `lifecycle_engine.py`, `StopAllDetector`, `reconcile_stopall_lifecycle`, `split_a_zones_by_dominant_stops`, `finalize_behavior_visibility`.

Behavior priority is `StopAll > E Red > S Red > E Blue > S Blue > A`. Family priority is invariant under reflection. The current `dominant_module()` selects by priority, then number, source time and index within the set supplied by surrounding chronology filters. Do not describe that helper as globally chronology-first.

StopAll processes accepted E sequence plus eligible S sources strictly earlier than each E source. Same-source S that lost ownership to E is excluded. An S group needs at least two matching-family S events; an E group needs at least two matching `(family, number)` E events. Higher priority can replace a current group; a higher same-family E number can advance it. Lower-priority events may remain valid outputs but do not replace or split the dominant group.

Once the latest relevant group parent strictly stops, an eligible later E whose decision is at/after the gate produces StopAll1. That E supplies winning Order/geometry and need not match the stopped group's family/number. StopAll copies the decisive E price/source/Order provenance, plus stopped-group key/count and gate. If active StopAlls have strictly stopped by a later E decision, the new StopAll number is one plus the highest stopped active number. New StopAll clears group state. Bearish StopAll itself stops only at strict High above its price; equality is non-stop.

**Current reconciliation is a single historical pass, not a global fixed point.** `reconcile_stopall_lifecycle()` runs StopAll from already reconciled accepted E, freezes those boundaries, stores `{sourceTime: number}` on E for downstream audit and returns the same E list. Its explicit intent is to prevent future reset maps from deleting/recreating an already decided StopAll prefix. Historical instructions to rerun E until a fixed point or raise a fixed-point convergence error do not describe this source.

The lifecycle layer invalidates equal/lower re-entry into a stopped dominant transition and tracks consumed boundaries/invalid leg heads. For A-to-A overlap, a new trigger at/before the prior exact A stop remains in the handoff; a later trigger can be a new leg but still faces larger-module ownership. Invalid live leg-head intervals block associated Order Firsts. Native detector evidence, accepted calculation objects and visible objects must be kept distinct.

Final presentation is accepted lineage closure: retain historical S referenced by final E and historical A referenced by final S where allowed, then apply physical-source collision priority. StopAll occupies its source before E; E/StopAll occupied sources remove competing A/S. Explicit invalid-S identities remain excluded. Internal geometry is not broadly forbidden: the remaining scoped E/StopAll prohibition concerns an internal **Mode-B Reset-leg Order_B**. A Mode-A Order with Reset provenance or a valid direct/carried Order is not automatically removed for being internal.

## OrderAudit and serialization

`prepare_order_audit()` merges S/A-stop and E ledgers by physical `(FirstIndex, BreakIndex)` identity, combines accepted causes, filters by Order First in the visible range, and resolves strict stops. A causes survive only for accepted A sources. One exact parent-stop tuple `(parentType, parentFamily, eventTime, parentSourceTime)` is spent once: earliest confirmation, then First and Break, wins. A later physical Order can remain only with another independent accepted cause. Internal Mode-B audit whose accepted causes are exclusively Reset-leg is rejected after cause merging, preserving any valid independent parent-stop cause.

`serialize_order_audit()` sorts by `(firstTime, breakTime)`. Audit stop hits can be null and audit-only Orders do not imply a synthetic E, StopAll or stop line. `reactionNumber: 0` is meaningful for permitted unpublished bounded direct geometry; never coerce it into a normal ordinal.

The response envelope includes `engine`, engine `version`, `pipelineVersion`, `blueLineVersion`, `aVersion`, `sVersion`, `eVersion`, `stopAllVersion`, enabled flags, `timeframe`, `actualFrom`, `actualTo`, `directions` and `timings`. Each direction contains exactly the collection names `reactions`, `resets`, `blueLines`, `aZones`, `sZones`, `eZones`, `stopAlls`, `orderAudit`.

| Collection | Required provenance groups and public contract |
| --- | --- |
| Reaction | First, semantic BoxTop/BoxBottom values and their source index/time, Break, Mode; filter by First index; public geometry clone |
| Reset | `index`, `time`, nullable `secondTime`, `brokenLevel`, `fromFirstIndex`; filter by Reset index |
| Blue | Direction/kind, owner number/counts, nullable Fibonacci/broken level, source/extreme, drawn line/start/end; filter by source index |
| A | Blue ordinals/sources/stops/levels, continuation owner, trigger main/exact event, validating Reaction, source/price, `calculationValid: true` |
| S | Color/formation type, A parent/stop, nullable complete Order geometry, optional Reset owner/time, source/price, decision main/exact event, `calculationValid: true` |
| E | Family/number, parent/stop, Order identity/geometry/stop owner and all cause timestamps, source/price, decision main/exact event |
| StopAll | Number/source/price/decision, gate type/event, stopped group/count, underlying E family/number, complete Order provenance, nullable own stop |
| OrderAudit | Order direction/number/mode, First/Break/box geometry, stop level/source and nullable hit, accepted cause objects |

Prices serialize with `str(Decimal)`, not floating-point rounding. Times are integer epoch seconds; absent optional values are JSON `null`, not zero or omitted substitutes. BoxTop and BoxBottom always keep semantic upper/lower meanings. Indexes and numbers retain full-context provenance, not display-window renumbering. Stage serializers do formatting; accepted ownership is resolved before them. `timings` is observational and nondeterministic, so exact semantic regression comparisons may normalize timing fields only.

## Invariants, asymmetries and remaining limits

* Strictness is local and explicit: equality is non-break, while containment, selected intervals and several confirmation bounds are intentionally inclusive.
* Event order is limited by the finest available RAW. A field named `secondTime` or a lower array named `seconds` does not create missing chronological evidence. A same-finest tie is governed by code, not an assumed intrabar path.
* Public doji GREEN is invariant; private reference-role swapping is necessary for the Bearish adapter and cannot be copied into chart colors.
* Exact-confirmation public Reaction/A geometry differs intentionally from complete-boundary-candle E geometry. A public Reaction box can differ from internal detector geometry; changing one to match the other can change ownership.
* Full-RAW calculation can change an earlier displayed object's resolution when the physical RAW is extended. It is not a causal live-prefix backtest guarantee. The frozen StopAll reconciliation rule prevents one specific retrospective feedback loop; it does not convert every stage into streaming-prefix semantics.
* Verified directional asymmetry: unified initial/post-Reset Bullish same-Break Reset uses `analysis.extreme`, while Bearish uses stored `box_top` in those branches. Ordinary Bearish refines before selecting its Reset level. Both directions' confirmation-remainder helper rejects reuse when the remainder crosses `analysis.extreme`. The source is therefore not reducible to a blanket assertion that all branches are literal mirrors. Exact field-level comparisons are necessary.
* Source extraction found no basis to claim a new executable full-file regression or an independently approved Bearish trading validation in this documentation task. Documentation inspection is diagnostic evidence only.
* Historical regression claims and dated fixture examples in older references are not proof for the current dirty working tree. Declared version numbers alone cannot establish byte-for-byte parity.
* Source ordering, valid OHLC, timezone availability, available lower coverage and canonical Reaction provenance are prerequisites. The bridge's bucket builder does not itself validate every one of these contracts.
* Never add timestamp, symbol, OHLC fingerprint or fixture-specific branches to make examples match. Verify the integrated `Reaction -> Blue -> A -> S -> E -> StopAll -> OrderAudit` objects, including parents, causes, nulls, exact event times and ordering, not only counts or screenshots.

For maintenance, inspect the named source functions first, preserve the other direction, and compare exact serialized protected collections on the explicitly requested RAW/range. Any proposed rule correction remains separate from this record of current executable behavior until implemented and verified.

### Additional findings from the completed source audit

The companion audit artifact `docs/graphify/engine-audit-evidence.md` records the following concrete defects or risks. They are not silently repaired or promoted into approved trading rules here.

| Finding | Evidence and implication |
| --- | --- |
| Package entry point fails | Audit reproduced `ImportError` because `engine/pipeline/__init__.py` imports `run_blue_line`, absent from `blue_line_detector.py`; production dynamic loading bypasses that entry point. |
| Cache dependency coverage | Vite `calculationSources` fingerprints bridge and six engines but omits `direction_policy.py` and `core_utils.py`; changing shared calculation dependencies can leave cached output stale. |
| Sparse initial data | Reaction `DetectorBase` infers interval from the first two main timestamps, while downstream chronology uses requested timeframe. Early gaps or a single main candle can produce inconsistent windows; a single candle defaults the Reaction interval to one second. |
| A visibility event mapping | `visible_a_zones_after_s_stops()` uses `bisect_left` on S decision event, mapping an intrabar event to the next main candle, and uses S decision rather than a separately resolved S stop. Intended behavior requires a focused fixture. |
| StopAll reset-map derived state | Single-pass reconciliation changes `sequence_resets` after E detection but does not refresh `_sequence_reset_times` or rebuild accepted audit; downstream audit-reset semantics may not reflect the new map fully. |
| Mixed-cause internal ownership | Public E/StopAll filtering rejects an internal Mode-B with Reset-leg provenance even if another cause exists; audit rejects it only when all merged causes are Reset-leg. The two output layers can disagree in a mixed-cause case. |
| Partial lower-data coverage | Empty-window A/S fallbacks do not detect partially missing data; E/StopAll generally require a witnessed lower cross, while confirmation may default to Break open. Missing observations can change resolution without a uniform error. |
| Cache retention/misses | `_geometry_after_reset_cache` is checked but not populated by its current helper; some E `.get(...) is not None` caches recompute misses. Module-level caches retain source sequences for process lifetime, acceptable for the fresh subprocess but a memory-growth risk in long-lived embedding. |

These are static/source-audit findings except the explicitly reproduced package import failure. No new timings, engine regression or independent market-oracle checks were performed for this reference. Full-file allocation, both Reaction directions, nested post-Reset geometry search, containment classification, repeated E passes and recursive lineage work are performance candidates; no fixed short display-window lookback limits their work.
