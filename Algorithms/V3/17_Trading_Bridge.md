# Trading Bridge — request-to-final-output algorithm (V3)

**Conventions:** B = bullish, R = bearish. Preserve Decimal representation and arithmetic order, native exception behavior, main time versus exact lower event, order and nulls. Record definitions are in [declared interfaces](../../Contracts/Declared_Record_Schemas.md). Procedure IDs designate semantic operations, not required implementation symbols. No runtime equivalence asserted.


## TB-M01 — Entry, dependency selection and input scope

Require reaction/Blue/A/S engine paths, data, timeframe, from/to and direction; E/lifecycle optional paths, Blue/A/S/primary flags default enabled, bridge-output optional, raw timeframe default1. Positive timeframe/raw timeframe required. Load engine modules once with configured names and optional primary. Lifecycle module loads by default path even when explicit StopAll flag is absent. StopAll enabled only explicit lifecycle path AND E AND S enabled. E enabled iff E engine present and S enabled. Dynamic configured modules/callbacks must satisfy referenced contracts; the source does not establish semantics of arbitrary externally supplied replacements.

Read full RAW bytes, strip BOM, decode Decimal floats, aggregate full history, establish visible range by epoch-aligned bucket bounds. Never truncate calculation at visible end. See [RAW](21_RAW_Aggregation_Contract.md). Context scope clears timestamp and market index caches before/after calculation even on error. Timed wrappers preserve result and emit progress with finally on work failure (start outside try).

## TB-M02 — Calculation stage composition

Direction request both -> B then R. If any Blue/A/S enabled, calculate both native Reaction directions for ownership. Full reusable mode iff E engine exists and S enabled; construct both full-history geometry detectors, native results and ownership. If primary present, calculate full behavior for both even single-direction request. Other mode uses independent directional initial A-stop geometry finder, native results for required directions and optional ownership; no E full state.

For each full direction:
1. Detect Blue including invalid/internal, A from full Blue, S with opposite native geometry/reset. Keep original S candidates and initial S copy.
2. Filter initial S audit by S-eligible A source. Detect initial E from accepted S. If S eligibility changes by module ownership, derive blocked S times and repeat E with valid S. Do not use provisional invalid A creation.
3. Determine invalid A by lifecycle from all S-eligible A and provisional S candidates/E. Derive invalid S and stage-specific S invalidation; remove stage-invalid S only for this next calculation. Resolve accepted Order context (including exact E exceptions); recreate E with accepted A ledger, blocked First, invalid S, Order_B legs.
4. Reconcile S decisions against shared accepted strict Order stops. If S changes, update candidate identities, rebuild E once. Find consumed-S evidence after larger E stops, re-open continuation via E detector preserving independent accepted A identities. Rebuild accepted ledger from final E plus evidence. Remove invalid S from accepted list.
5. Order_B feedback: keep step1 shared stages, repeat remaining state with legs; optional StopAll reconcile, independent S root restoration, ensure ledger, rediscover legs. Equal semantic leg signature -> return original direction state of pass; repeated non-equal signature -> error; maximum eight passes. No guessed convergence.

## TB-M03 — Requested-range selection and final visibility

Collect range Blue/A by source where reusable; if nonreusable compute full geometry with appropriate flags, S requires A requires Blue regardless of display flags. Full S uses full eligible A and accepted/candidate S. E full state retained. Apply initial A/S display collision rules. Supplement missing independent E donors only for StopAll (do not replace already accepted donor identity). Optional StopAll reconcile; restore independent S roots, ensure audit; rediscover final Order_B and require exact signature equals converged state. Register legs. Capture pre-range accepted references for bridge joins. Apply lifecycle final visibility to full candidates and collect primary groups before range clipping. Clip A/S/E/StopAll by source range inclusive; filter invalid A/S. Mark Blue internal using all behavior reactions then public Blue filter. Internal behavior helper currently copies lists. Prepare OrderAudit with all calculation-accepted A, visible range plus required physical identities, validate physical/cause invariant.

## TB-M04 — Primary, projection and reversal

Primary owner = bearish for both, otherwise requested direction. Only if primary loaded, full E detector exists and explicit lifecycle path: finalize opposite direction, build full primary groups and full audits for both; NativePrimaryOrders callback registers confirmed primary and refreshes its audit. Detect in native primary coordinates, reconcile final labels through visible end, reprepare visible audit preserving previously required identities. Resolve StopAll physical ownership and validate. Serialize legacy and optional additive bridge from SAME selections; append primary arrays if computed. If primary transition index <= visible end, replace direction groups with [independent regimes](15_Trend_Reversal.md), derive activeDirection. Then apply bounded True/False per segment. Final envelope carries versions, enable flags, requested timeframe and actual visible bucket epochs, directions and telemetry. No price rounding; timings rounded to two decimals only. CLI success prints compact JSON/exit0; ordinary exceptions print error JSON/exit1.

## TB-M05 — Dependencies and failure handling

Feedback is the only bounded eight-pass loop here, not a general E/Reaction/primary limit. Geometry and business acceptance remain owner modules. Full stage output maps and partial detector state are mutable; no blanket transaction in batch. Live transport wraps input append transaction, not an empirical equivalence guarantee. Stage callback may fail; no silent catch except explicitly described fallback. See [Live](18_Live_Bridge.md), [Serialization](19_Serialization.md), [RAW](21_RAW_Aggregation_Contract.md) and [T/F](22_True_False_Exact_Contract.md) for exact interface behavior.

## Detailed orchestration procedures

### TB01 — progress_events_to
Context manager: set context-local progress sink, yield control, restore previous token in finally even on exception. No result payload.

### TB02 — emit_progress
Construct status/label/details event; optional durationMs rounded to two decimals. If sink exists call it; otherwise emit QG_PROGRESS prefix and compact JSON to stderr, flushed. Sink/encoding errors propagate. No market change.

### TB03 — timed
Read performance counter, emit start, invoke work and return its result. Finally accumulate elapsed milliseconds by label in supplied timings and emit completion even on work error. Telemetry only.

### TB04 — load_module
Create import specification from name/path; missing spec/loader raises RuntimeError. Create module, register in sys.modules, execute loader, return module. Dynamic external implementation conditional on supplied path.

### TB05 — load_engine
Delegate TB04 with fixed reaction_engine module name.

### TB06 — local_datetime
Epoch-keyed cache; miss converts epoch in Asia/Tehran then removes timezone marker, stores and returns naive datetime.

### TB07 — epoch
Datetime-keyed cache; miss attaches Tehran timezone and truncates timestamp with int; stores and returns.

### TB08 — display_epoch
Datetime directly delegates TB07. Otherwise cache by input string, parse year-month-day hour:minute:second, convert and cache. Parse failures propagate.

### TB66 — parse_arguments
Require reaction,Blue,A,S engine paths (aliases accepted), data path,timeframe,from/to,direction bullish/bearish/both. E and lifecycle paths optional. Blue/A/S/PLPH flags enabled/disabled default enabled; bridge-output switch; raw-timeframe default1. Require timeframe and raw-timeframe >=1. argparse failures propagate. Return namespace.

### TB67 — load_engines
Time and dynamically load configured Reaction,Blue,A,S and optional E paths with expected module names. Lifecycle default pipeline/lifecycle_engine.py always loaded; primary module PL_PH_detector.py loaded if flag enabled (missing attr defaults disabled). Return EngineBundle.

### TB71 — create_e_detector
Construct E detector with full market bounds, trend/opposite reactions and resets, S zones, initial audit, blocked First times, exceptions, invalid S identities, Order_B legs, lifecycle.sequence_priority, direct geometry TB72. Only pass live continuation/scope when supplied.

### TB72 — direct_geometry
Invoke provided live order_geometry callback with direction's detector and requested geometry bounds/gate if present; otherwise call detector.first_order_reaction_after_gate.

### TB73 — calculate_full_direction_state
Compute full direction state. If no shared stages, timed Blue then A, create full-range S detector with opposite resets and initial Order geometry; run S (live callbacks where provided), retain initial S copy. Else reuse shared Blue/A/S detector and initial S, not the previous E. Snapshot S candidates. Filter S audit by eligible A source; create initial E with feedback scope and detect. Apply lifecycle S eligibility; if size changed identify blocked S source times (set membership or TypeError fallback list); recreate E with valid S and blocked sources and detect.
Execute A visibility helpers, then split ALL S-eligible A by dominant S/E stops with original S candidates and no StopAll; callbacks E parent stop and S A-stop from confirmation; collect stage-invalid A. Derive invalid A and S identities and stage-invalid S descendants; remove stage-invalid S from active S. Accepted A excludes invalid; resolve Order context with S audit, previous E blocked times, invalid A, pending S A sources, opposite reactions, A first stop from source, accepted E stops, opposite confirmation, mutable exceptions. Recreate final E using accepted orders, blocked/exceptions/invalid S/legs; detect.
Reconcile shared Order stops using accepted initial audit and E ledger; if S rows change, replace candidates by (a source, source) identity, recreate shared-order E and detect once. Filter calculation S candidates by stage-invalid; find consumed S evidence after larger E stop; for each evidence/owner find current E owner by physical source/time; if present build continuation_chain_from_s with independent accepted A identities and replace_with_earlier_continuation. Rebuild accepted E audit with supplemental S evidence. Remove all invalid S from active list. Return FullDirectionState incl full Blue/A, E detector/results, S detector, invalid sets, candidates and initial S. Callback errors propagate; this orchestrates existing engine rules rather than inventing them.

### TB74 — calculate_direction_with_order_b_feedback
Start empty B legs/seen signatures/shared stages; at most eight passes. Run TB73 with current legs and pass scope; save initial shared stages. For optional StopAll reconcile lifecycle, else copy E and empty StopAll. Restore independent S roots and ensure accepted audit. Discover accepted reset legs from full reactions/resets, eligible/invalid A, S/E/StopAll, detectors and priority, optional live finder. Compare old/new order_b_leg_identity; equal returns original state of pass (temporary local E list is not assigned to state.e_zones). Repeated new identity raises nonconvergence; otherwise remember and repeat. After eight raise.

### TB75 — prepare_pipeline_state
Requested directions from args; any Blue/A/S enabled requires both reaction directions. Reusable full context iff E exists and S enabled. Initialize state maps. Full: create both geometry UnifiedReactionDetector for full history with matching initial trend flag; batch detect timed or live reactions; derive internal ownership; report if callback. Initial Order geometry closures capture specific opposite direction and delegate live or detector. Calculate both full directions if primary exists else requested; TB74 each, explicit lifecycle path controls StopAll; store all outputs/maps and report. Nonfull: create initial geometry finder for both, detect required directions full independently; internal ownership if behavior enabled else empty identity sets. Return PipelineState with retained optional live stages.

### TB76 — calculate_direction_range_state
Need Blue if Blue/A/S enabled; reuse full Blue clipped by source range or detect from full reactions/chronology; else empty. Need A if A/S enabled; reuse clipped full A or detect from Blue; else empty. If S enabled, full-context uses full candidates/accepted S and eligible A (not clipped); otherwise construct full-range S detector with opposite data and initial geometry, detect and store detector, S candidates accepted and A replaced by eligible. Return range state including full E copy and invalid sets from maps (empty defaults). No final display filtering here.

### TB77 — finalize_direction_visibility
Filter A by accepted S and S stops. Copy E. If E detector, restore independent S roots for potential StopAll donors; supplement only missing physical sources, keep accepted E objects. StopAll enabled iff explicit lifecycle path, E engine and S flag; reconcile if detector exists. If E detector exists restore independent roots for final visibility, ensure accepted audit, set visibility stop callback based on S-like attribute. Discover final accepted Order_B legs, require identity equality with converged detector legs or RuntimeError; register legs. Else visibility stop callback uses S detector first_a_stop from decision event.
Capture pre-display S/E/StopAll references for projection joins. Run lifecycle.finalize_behavior_visibility with initial visible A, full S candidates, E/StopAll, invalid S, stop and candidate event callbacks, full candles/all A. Build primary groups from full valid A and returned S/E/StopAll BEFORE clipping. Clip A/S/E/StopAll by inclusive source range; remove invalid A/S identities. Order audit A sources remain full S-eligible noninvalid A. Flatten all behavior reactions, mark internal Blue, filter internal behavior outputs. Required Order identities from complete First/Break on displayed S/E/StopAll; prepare audit with range plus required identities, validate TB61 if E detector. Return public Blue, displayed behavior, audit, projection references and primary groups.

### TB78 — serialize_direction_payload
Legacy-only: timed serialize selected reactions/reset with published_reaction_candidate transform, timed TB79. Bridge enabled: create single transform/selection via TB80; select enabled/ranged Blue, enabled A, existing S/E/StopAll, audit sorted by TB59 if detector else empty; timed TB81. No trading decisions; identical selections used for additive bridge.

### TB87 — calculate_primary_structures
Finalize opposite direction and obtain both full primary groups. For each owner prepare full-range audit from accepted noninvalid A. Build NativePrimaryOrders with TB88 on_high and direction. Detect appropriate primary via live callback or engine with S/E/StopAll/resolver. Resolve final primary side through visible end, reconcile detector primary labels. Preserve existing visibility audit identities as required; rebuild visibility audit with visible bounds. Return primary; mutates detector and visibility audit.

### TB88 — commit_high
Register low for bullish or high for bearish on E detector, then refresh that direction's full-range audit in groups using accepted A. Closure mutates groups.

### TB89 — build_direction_output
TB76 then TB77. Primary owner bearish for both else requested direction. Calculate primary only if direction matches owner, primary module exists, E detector exists and explicit lifecycle path. Save state.primary_result; resolve StopAll ownership through end; validate audit. Serialize TB78; append primary structures if present.

### TB90 — merge_regime_outputs
Group regime segments by direction preserving encounter order. Single segment unchanged. Multiple: copy final segment, concatenate all list-valued keys from all segments, merge bridge arrays in encounter order, remove aggregate calculationEndTime, attach original segments as calculationSegments. No reconstruction.

### TB91 — build_reversed_trend_outputs
Begin opposite target direction with full current context, incoming null. While transition exists: require 0<boundary<len current else RuntimeError. Independently calculate closed prefix via TB94 or live closed-regime callback; require confirmed Primary3 matching transition source time and level else RuntimeError. If no visible history empty arrays recursively via TB95. Publish stopped prefix with TB93. Serialize incoming transition and slice fresh regime from boundary including boundary candle; initialize only target trend. Calculate TB92 with optional live active regime, release indexes in finally (fallback live release). If next transition missing or beyond current end publish active segment and break; otherwise repeat. Merge TB90. No state carried across independent regimes except explicit transition metadata and live cache interface.

### TB92 — calculate
Shallow copy args, set direction, prepare state for supplied context with optional continuation, build direction output; return group/state.

### TB93 — publish
Convert local indexes to absolute via TB64; add calculationStartTime/Index only for noninitial offset; attach incoming transition if present. For stopped segment set calculationEndTime to reversal main timestamp, status reversed-to-target, all cycle statuses stopped-on-trend-reversal, cap matching legs at end. Return projected group.

### TB94 — calculate_closed
Capture current context/boundary/direction as defaults. Slice [0,boundary), check visible history; if none use whole prefix for internal calculation. Calculate TB92; resolve confirmed primary through prefix final index; return offset,first time,history flag,group,confirmed. Finally release indexes or live fallback.

### TB95 — empty_lists
Recursively replace any list with empty list; copy dict recursively; retain other scalars.

### TB96 — build_response_payload
Build version/enable/timeframe/actualFrom/To metadata, directions dict; E enabled iff engine and S; StopAll also explicit lifecycle path. Build requested direction outputs in order. If primary transition <=visible end replace direction groups with reversed regimes; activeDirection from max (calculationStartIndex default -1,direction) over segments, fallback target. Repair search through visible main end minus one second; closed_through=min(epoch(through)+1,last lower epoch+raw_timeframe(default1)). Apply True/False to every segment using repair finder and TB97; aggregate direction arrays share row references as constructed. Add rounded phase and bridge total timings. Return payload.

### TB97 — stopall_confirmation_closed
True iff row decisionTime+args.timeframe <= captured closed_through.

### TB98 — _market_calculation_scope
Clear three timestamp caches and optional engine clear_market_indexes before yield; clear engine indexes and timestamp caches again in finally. Each calculation independent.

### TB99 — calculate_live_from_raw
Delegate TB101 with rows preparer and one-element input tuple.

### TB100 — calculate_live_from_buckets
Delegate TB101 with bucket preparer, lower/main bucket arrays, optional live views/delta and report callback.

### TB101 — _run_live_calculation
Start performance counter, empty timings; enter TB98, prepare market from injected function/inputs, optional report Market chronology ready, prepare pipeline state with report_stage (no live argument supplied on this path), return response payload. Context cleanup on exception.

### TB102 — main
Start pipeline and validation counters; progress start, parse, store validation duration and completion. Load engines; enter market scope; prepare market/state and response. Emit total calculation completion. Compact JSON encode, emit encoding completion, print encoded payload, return 0. Module entry catches Exception, prints error JSON and exits 1; otherwise SystemExit main status. Does not catch BaseException generally.
