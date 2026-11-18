# Domain assessment and position contract audit

Audit scope: current source at the start of the 2026-11-17 task. This is task evidence, not normative trading authority. Root `AGENTS.md` was read; Git status initially contained no tracked changes. No Graphify execution was used.

## Feature boundary

- `engine/pipeline/bullish_setup_engine.py` is an independent downstream stage. Its full 503-line source was read. It consumes accepted bullish S/E, StopAll and primary-low events, generates movement/parity T/F assessments, reference breaks and automatic entry/stop/target schematics, and owns its live rewind state. It does not provide native Reaction, physical Order, OrderAudit, StopAll or primary formation.
- `engine/bridge/trading_pipeline.py` owns `serialize_setup_annotations` and calls the stage after native primary calculation. The six added direction fields are `setupVersion`, `setupPhase`, `positionSetups`, `stopAllAssessments`, `behaviorAssessments` and `setupReferenceBreaks`. No live `primaryLowAssessments` field was found. Fields must disappear from aggregate and `calculationSegments` payloads, without changing native arrays, identities or primary/Order provenance.
- `engine/bridge/live_pipeline.py` was read fully. Its setup-only ownership is `_setup` plus `bullish_setups`; native continuation and RAW handling are independent.
- `apps/chart/src/chart/setup-annotations.js` is wholly automatic-position/T/F presentation. `main.js` integrates settings/defaults, presentation caching, object reconciliation/serialization, overlay labels/positions, position selection/editing and timing-stage labels. Preserve independent manual Long/Short tooling pending explicit scope clarification.
- `apps/chart/vite.config.js` includes the setup module in calculation fingerprints. Remove that dependency together with the module so runtime source discovery does not access a missing file. The changed source set invalidates stale calculation caches.

## Historical evidence

Git commit `3d82da4933dd1a5aa7c3a98906242488c9353e48` first tracked the setup Engine and automatic Chart annotation module. Its parent `afb586b` already contains manual Long/Short drawing tools and `calculatePositionLevels`; those date back to `dd6b72b` in the inspected history. Therefore restoring an old revision wholesale would discard newer unrelated behavior and does not define the requested removal boundary.

Manual Review True/False/Unselected selections are a separate human review workflow. They are not calculated setup assessments. Ordinary Boolean validity/ownership flags, physical Order/OrderAudit and primary structures are also outside the automatic setup stage.

## Consumers and synchronization

- Dedicated Engine tests: `test_bullish_setup_engine.py`, `test_live_bullish_setups.py`, `test_setup_serialization.py`; Chart: `setup-annotations.test.mjs`. Their former positive feature expectations should be retired and replaced with absence/retained-contract checks.
- Both accepted directional References embed the complete setup Engine and bridge sources, manifest entries, symbol indexes and active section 14A describing the six fields. They require full synchronization with live source, not only deletion of the embedded setup section.
- Maintained documentation: `technical-architecture.md` includes setup event state/assessment ownership; `testing.md` describes the former setup regression as maintained; `ui-ux-reference.md` includes setup Configure/Appearance and automatic-position workflows.
- The 2026-11-02 verification directory is historical evidence and should remain historical. Its `verify_setup_raw.py` already identifies the six added fields as a baseline-exclusion set.
- Tracked `engine/engine.zip` contains the setup module. It is an archive input/evidence artifact rather than runtime authority; decide separately whether its current packaging contract requires regeneration.

## Verification requirements

1. Capture a failing runtime contract test before removal: complete manual and live bullish/bearish output contains none of the six setup fields, recursively including independent regimes.
2. Check native fields and representative ordinary Boolean flags remain, and native arrays/identities/provenance match the original baseline after excluding only the six intentionally removed fields and documented non-stable telemetry.
3. Remove setup imports, execution and live state, not merely serializer fields. A missing setup module must not break supported Engine initialization or Vite source fingerprinting.
4. Run current Engine and Chart suites, build/static checks, live continuation parity, representative RAW equivalence and browser Configure/Appearance/indicator-object smoke tests. Manual drawings and Manual Review remain subject to the user's scope decision.

## Performance observations

Full `lifecycle_engine.py` (1594 lines) and `order_audit_engine.py` (2306 lines) were read.

- `s_zones_for_module_engines` repeatedly allocates/scans every E and accepted S per S candidate. Ordered strict-source prefix lookup can reduce the work. Preserve `max` first-match ties: equal-time E precedes S, and the first stable equal-source item wins.
- `blocked_orders_while_invalid_leg_heads_are_live` rescans every opposite Reaction per invalid A. A First-time interval index can preserve `[source_time, stop_event)` semantics.
- `dominant_post_behavior_stops` scans all lifetimes at every finite stop. A sweep can reduce quadratic work, but must preserve inclusive starts/ends, stable first-match rank ties, object identity ownership and same-main-candle selection.
- Accepted audit rebuilding repeatedly finds physical parent S/E by linear search. Per-invocation `setdefault` maps can preserve first-match selection and reduce repeated scans without persistent cache invalidation risk.
- Main-candle Order_B boundary scans could use a shared range index only after confirming earliest-equal-extreme and exact Decimal representation behavior.

These observations are optimization candidates, not benchmark results or proof of equivalence.

## Approved removal and implementation evidence

The user subsequently clarified that the removal includes manual Long/Short tools and Manual Review True/False workflows as well as automatic setup assessments. This supersedes the provisional boundary above.

- Deleted the standalone setup Engine, its bridge projection/execution and live continuation state, and its dedicated positive tests. Added real manual/live complete-pipeline tests verifying recursive absence of the six fields while native Reaction discovery, native arrays and primary fields remain active and live output equals manual output. RED: one expected failing bullish case and one unaffected passing bearish case. GREEN: two passing cases.
- Removed automatic Chart objects, labels, settings, appearance controls and editing paths, plus manual Long/Short drawing tools and price/geometry calculations. Retained Measure and ordinary drawing behavior. Legacy saved long/short drawings are omitted at the existing `drawingArray` boundary; old undo snapshots omit automatic positions/status labels while retaining unrelated drawings/objects. Original saved inputs are not mutated by normalization. RED: three failing state-contract tests; GREEN: three passing tests.
- Removed the setup source from the Vite calculation fingerprint. Removed Manual Review verdict controls, filters, bulk operations, storage, styling and export verdict column. Existing report data, category/date filtering, grouping, Bridge YAML, copy and download remain. New text exports contain timestamp and native event label. Historical local verdict keys remain inert rather than being erased.
- Current verification executed during this implementation: `python -m pytest engine/tests/unit -q --tb=short`: PASS, 464 tests; `npm test` from `apps/chart`: PASS, 329 tests; `npm run build`: PASS, with Vite's existing large-chunk warning. These are task-time results, not permanent suite totals.
- Browser verification: PASS using installed Edge and `playwright-core` because the Browser plugin is absent. An isolated fresh Vite process at `http://localhost:5191` served current source; the existing 5173 process was left untouched because its disabled watcher retained old transformed modules. The owned 5191 process was stopped afterward. At 1440x1000 and 390x844, Chart loaded without page/console errors or framework overlay. Long/Short toolbar and setup Configure/Appearance controls were absent; native S visibility and appearance remained usable; a legacy line survived while a legacy Long drawing was omitted; new Measure drawing, undo, redo and intercepted save preserved only line/measure drawings. Screenshots and the reusable smoke script are under the task visualization directory. Manual Review desktop/mobile checks also passed with a synthetic intercepted report, no verdict controls, working filters/Bridge YAML and no console errors.

## Complete Bridge source review

The entire current `trading_pipeline.py` was read jointly: delegated reviewer read lines 1-1750; contracts reviewer read lines 1751-3583 after removal. `live_pipeline.py`, `bullish_setup_engine.py` before deletion, `lifecycle_engine.py` and `order_audit_engine.py` were read completely by the contracts reviewer.

Retained contracts and cache risks:

- Native A/S `calculationValid: true` is ordinary validity metadata and remains. Decimal lexical values, Tehran epoch conversion, nullable provenance and exact event horizons remain independent of the removed assessments.
- Native Reaction/Reset and Bridge projection consume one finalized ordered selection. Do not independently filter/reorder projection arrays. `currentOrder` must have one exact accepted cause; ambiguity remains null. Strict event projection verifies the recorded event and does not scan for a substitute.
- Projection source maps use last-match dictionary semantics. Native parent lookup optimizations elsewhere may use first-match semantics. They are not interchangeable.
- `primary_groups` is pre-clipping native primary input, not a removable setup-stage relic. Primary registration updates physical Order causes before final serialization and remains required.
- Module-global datetime/epoch conversion caches hold pure timezone conversions and are unbounded. They contain no market state; retained live-worker memory can grow with new timestamps. This was observed statically, not memory-profiled here.
- `LiveMarketBuckets._prices` is per continuation and preserves first normalized Decimal representation. New cached prices commit only after successful input aggregation. Invalid input must not partially mutate this state.
- Full pipeline state is run-local. Feedback reuses only Reaction/Blue/A/initial-S dependencies within that invocation. Live E/StopAll/Order_B continuation scopes include stage/feedback identities; a cache must never cross these boundaries without equivalent invalidation.
- Source input remains full physical RAW for manual calculation while from/to are presentation bounds. Reversed regimes require independent prefix calculation, strict Primary3 support, absolute identity projection and indexed cleanup of temporary chronology views.
