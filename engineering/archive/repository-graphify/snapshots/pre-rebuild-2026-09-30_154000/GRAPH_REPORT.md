# Graph Report - TradingBot  (2026-09-23)

## Corpus Check
- 111 files · ~340,018 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2691 nodes · 4526 edges · 147 communities (139 shown, 8 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 70 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `822c5ce1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Styles Tokens
- Chart Main
- Complete Project Engineering Audit
- Engine Pipeline A Zone Detector
- Engine Pipeline S Zone Detector
- Trading Bot Master Prompt For
- Engine Bridge Trading Pipeline
- Manual Review Render
- Trading Bot High Performance Zero
- Trading Bot Ui Ux Technical
- Trading Bot Technical Architecture
- Algorithm Page
- Complete Project Engineering Audit 2
- Chart Vite Config
- Trading Bot Project Audit
- Chart Main 2
- Chart Main 3
- Chart Faraz Candle Api
- Engine Pipeline E Zone Detector
- Chart Main 4
- Engine Algorithms Trading Bot Bearish
- Engine Algorithms Trading Bot Bullish
- Engine Pipeline E Zone Detector 2
- Agen
- Chart Screenshot Overlay Test
- Complete Project Engineering Audit 3
- Engine Pipeline Reaction
- Features Candle Update
- Chart Main 5
- Engine Pipeline Reaction 2
- Chart Raw Resource Store
- Engine Pipeline Reaction 3
- Chart Update Contract Test
- Engine Algorithms Trading Bot Bearish 2
- Engine Algorithms Trading Bot Bullish 2
- Algorithm Page 2
- Chart Main 6
- Features Candle Export
- Engine Pipeline Reaction 4
- Trading Bot Bearish Algorithm Reference
- Trading Bot Bullish Algorithm Reference
- Engine Pipeline Lifecycle
- Chart Package
- Chart View Transform
- Engine Pipeline E Zone Detector 3
- Engine Pipeline Reaction 5
- Engine Pipeline Lifecycle 2
- 2026 09 21 Complete Project
- Engine Pipeline E Zone Detector 4
- Engine Pipeline Lifecycle 3
- Agents
- Chart Main 7
- Ui Workspace State
- Features Indicator Cache
- Chart Main 8
- 2026 09 17 Tradingbot V2
- Project Scripts Start
- Engine Algorithms Trading Bot Bearish 3
- Engine Algorithms Trading Bot Bullish 3
- Engine Pipeline E Zone Detector 5
- Agents 2
- Content Bridge
- Content
- Algorithm Mirror
- Engine Algorithms Trading Bot Bearish 4
- Engine Algorithms Trading Bot Bearish 5
- Engine Algorithms Trading Bot Bullish 4
- Engine Algorithms Trading Bot Bullish 5
- Chart Transfer
- Chart Indicator Range Input
- Ui Feedback
- Complete Project Engineering Audit 4
- Engine Algorithms Trading Bot Bearish 6
- Engine Algorithms Trading Bot Bullish 6
- Content Object Catalog
- Chart Main 9
- Trading Bot High Performance Zero 2
- Trading Bot Repository Baseline
- Engine Algorithms Trading Bot Bearish 7
- Engine Algorithms Trading Bot Bearish 8
- Engine Algorithms Trading Bot Bullish 7
- Engine Algorithms Trading Bot Bullish 8
- Trading Bot High Performance Zero 3
- Trading Bot Validation Report
- Engine Algorithms Trading Bot Bearish 9
- Engine Algorithms Trading Bot Bearish 10
- Engine Algorithms Trading Bot Bearish 11
- Engine Algorithms Trading Bot Bullish 9
- Engine Algorithms Trading Bot Bullish 10
- Engine Algorithms Trading Bot Bullish 11
- Engine Pipeline Lifecycle 4
- Agen 2
- Complete Project Engineering Audit 5
- Engine Algorithms Trading Bot Bearish 12
- Engine Algorithms Trading Bot Bullish 12
- Chart Vite Config 2
- Trading Bot Cleanup Report
- Engine Algorithms Trading Bot Bearish 13
- Engine Algorithms Trading Bot Bearish 14
- Engine Algorithms Trading Bot Bearish 15
- Engine Algorithms Trading Bot Bullish 13
- Engine Algorithms Trading Bot Bullish 14
- Engine Algorithms Trading Bot Bullish 15
- Agen 3
- Trading Bot Ui Ux Technical 2
- Trading Bot Ui Ux Technical 3
- Trading Bot Ui Ux Technical 4
- Engine Algorithms Trading Bot Bearish 16
- Engine Algorithms Trading Bot Bullish 16
- Content Glossary
- Agen 4
- Trading Bot Ui Ux Technical 5
- Engine Algorithms Trading Bot Bearish 17
- Engine Algorithms Trading Bot Bearish 18
- Engine Algorithms Trading Bot Bearish 19
- Engine Algorithms Trading Bot Bullish 17
- Engine Algorithms Trading Bot Bullish 18
- Engine Algorithms Trading Bot Bullish 19
- Engine Pipeline E Zone Detector 6
- Chart Candle File Response
- Content Calculation Guides
- Agen 5
- Trading Bot High Performance Zero 4
- Trading Bot Master Prompt For 2
- Engine Algorithms Trading Bot Bearish 20
- Engine Algorithms Trading Bot Bearish 21
- Engine Algorithms Trading Bot Bearish 22
- Engine Algorithms Trading Bot Bullish 20
- Engine Algorithms Trading Bot Bullish 21
- Engine Algorithms Trading Bot Bullish 22
- Engine Pipeline Lifecycle 5
- Features Screenshot Overlay
- Agen 6
- Trading Bot High Performance Zero 5
- Trading Bot High Performance Zero 6
- Trading Bot Master Prompt For 3
- Agen 7
- Agen 8
- Trading Bot High Performance Zero 7
- Trading Bot Master Prompt For 4
- Engine Bridge Init
- Engine Init
- Sensitive Runtime Content Excluded

## God Nodes (most connected - your core abstractions)
1. `EZoneDetector` - 62 edges
2. `TradingBot UI/UX Technical Reference` - 50 edges
3. `SZoneDetector` - 47 edges
4. `TradingBot Technical Architecture Reference` - 45 edges
5. `TradingBot Bearish Algorithm Reference — Comprehensive Standalone Rebuild & Exact Implementation Specification` - 42 edges
6. `TradingBot Bullish Algorithm Reference — Comprehensive Standalone Rebuild & Exact Implementation Specification` - 42 edges
7. ``<Page Name> — Frontend Technical Reference`` - 41 edges
8. `as_decimal()` - 36 edges
9. `AGENT.md — TradingBot / TRADE | Unified AI Operating Contract` - 35 edges
10. `Stage 33 — Mandatory Per-Page Analysis` - 28 edges

## Surprising Connections (you probably didn't know these)
- `build_candle_buckets()` --indirect_call--> `as_decimal()`  [INFERRED]
  engine/bridge/trading_pipeline.py → engine/pipeline/core_utils.py
- `validate_order_audit_bridge()` --calls--> `order_identity()`  [INFERRED]
  engine/bridge/trading_pipeline.py → engine/pipeline/core_utils.py
- `finalize_direction_visibility()` --calls--> `order_identity()`  [INFERRED]
  engine/bridge/trading_pipeline.py → engine/pipeline/core_utils.py
- `prepare_order_audit()` --calls--> `order_identity()`  [INFERRED]
  engine/pipeline/lifecycle_engine.py → engine/pipeline/core_utils.py
- `strictly_beyond_boundary()` --calls--> `policy_for()`  [INFERRED]
  engine/pipeline/lifecycle_engine.py → engine/pipeline/direction_policy.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Documented browser-to-Python request and response path** — agents_http_sse_python_runtime_boundary, apps_chart_src_main, apps_chart_vite_config, engine_bridge_trading_pipeline [EXTRACTED 1.00]
- **Documented calculation stage sequence and lifecycle output** — agents_calculation_stage_ownership, engine_bridge_trading_pipeline, engine_pipeline_reaction_engine, engine_pipeline_blue_line_detector, engine_pipeline_a_zone_detector, engine_pipeline_s_zone_detector, engine_pipeline_e_zone_detector, engine_pipeline_lifecycle_engine [EXTRACTED 1.00]

## Communities (147 total, 8 thin omitted)

### Community 0 - "Styles Tokens"
Cohesion: 0.01
Nodes (177): --accent-blue, --accent-blue-hover, --algorithm-a, --algorithm-a-soft, --algorithm-blue-line, --algorithm-blue-line-soft, --algorithm-bridge, --algorithm-bridge-soft (+169 more)

### Community 1 - "Chart Main"
Cohesion: 0.02
Nodes (77): appRoot, calculationStageDescriptions, canvas, captureFeedback, chart, chartElement, chartSettingInputs, chartSettings (+69 more)

### Community 2 - "Complete Project Engineering Audit"
Cohesion: 0.02
Nodes (84): Audit Evidence Standard, Audit Modification Policy, Complete Project Engineering Audit, Architecture Reconstruction, UI/UX Technical Reference, Security Review, and AI Operational Documentation, Documentation Language Requirement, Final Quality Standard, Final Writing Rule, Fundamental Rule, Mandatory Codex Desktop Plugin Requirement (+76 more)

### Community 3 - "Engine Pipeline A Zone Detector"
Cohesion: 0.06
Nodes (51): Numerical, temporal, and provenance invariants, core_utils import alias, Python stdlib: dataclasses, Direction, direction_policy import alias, AZone, AZoneDetector, BlueState (+43 more)

### Community 4 - "Engine Pipeline S Zone Detector"
Cohesion: 0.07
Nodes (36): as_decimal(), Preserve Decimal values and normalize other numeric inputs losslessly., detect_s_zones(), datetime, Decimal, S-zone calculation from authoritative A, Reaction, Blue, and Order state. Owns…, Build the order-free Blue Type-3 continuation for one stopped A., Resolve Simple/Advanced S ownership after a stopped A finds an Order. (+28 more)

### Community 5 - "Trading Bot Master Prompt For"
Cohesion: 0.03
Nodes (76): 10. Bullish and Bearish Must Both Be Fully Standalone, 11. Canonical Directional Mirror, 12. Mandatory Direction-Invariant Section, 13. Other Mandatory Direction-Invariant Rules, 14. Strict Crossing, 15. Exact Decimal Contract, 16. Candle Color Contract, 17. Full Physical RAW Authority (+68 more)

### Community 6 - "Engine Bridge Trading Pipeline"
Cohesion: 0.05
Nodes (72): Python stdlib: argparse, Python stdlib: decimal, HumanReportSerializationTests, build_candle_buckets(), build_candle_objects(), build_direction_output(), build_response_payload(), calculate_direction_range_state() (+64 more)

### Community 7 - "Manual Review Render"
Cohesion: 0.08
Nodes (52): app, fail(), loadCalculationReport(), loading, renderReview(), buildInfoPayload(), buildLegacyReviewBody(), buildReviewBody() (+44 more)

### Community 8 - "Trading Bot High Performance Zero"
Cohesion: 0.04
Nodes (47): 11. STRICT CROSSING, 12. PHYSICAL ORDER IDENTITY, 14. CACHE SCOPE, 15. REACTION OPTIMIZATION, 16. BLUE OPTIMIZATION, 17. A OPTIMIZATION, 18. S OPTIMIZATION, 19. S-AFTER-A RULE (+39 more)

### Community 9 - "Trading Bot Ui Ux Technical"
Cohesion: 0.04
Nodes (46): 10. Sidebar and Navigation Rail, 11. Footer and Status Bar, 12. Toolbars and Controls, 13. Design Tokens, 14. Chart Color System, 15. Algorithm Color System, 16. Typography, 17. Spacing and Geometry (+38 more)

### Community 10 - "Trading Bot Technical Architecture"
Cohesion: 0.04
Nodes (45): 10. Dependency Architecture, 11. Startup and Runtime, 12. System Architecture, 13. Backend Architecture, 14. Frontend Architecture, 15. End-to-End Data Flow, 16. HTTP and Communication Interfaces, 17. Core Data Structures (+37 more)

### Community 11 - "Algorithm Page"
Cohesion: 0.07
Nodes (36): ALGORITHM_COPY, eCarried, eDirect, eRecursive, eResetLeg, FAMILY_SUMMARIES_FA, STOP_RULES_FA, TYPE_STEPS_FA (+28 more)

### Community 12 - "Complete Project Engineering Audit 2"
Cohesion: 0.05
Nodes (42): Accessibility, Animation, Backend Dependencies, Charts / Visualization, Color Usage, Component Tree, Controls, Data Flow (+34 more)

### Community 13 - "Chart Vite Config"
Cohesion: 0.05
Nodes (28): aEnginePath, blueEnginePath, bridgePath, calculationId(), calculationMetadata(), calculationsDir, calculationSources, chartRoot (+20 more)

### Community 14 - "Trading Bot Project Audit"
Cohesion: 0.05
Nodes (39): 10. Documentation Drift, 11. Cleanup Decision, 12. Validation Limits, 13. Current-turn corroboration (2026-09-19), 13. Recommended Remediation Backlog, 1. Executive Assessment, 2. Scope and Evidence, 3.1 Deterministic calculation authority (+31 more)

### Community 15 - "Chart Main 2"
Cohesion: 0.08
Nodes (36): CHART_TIMEFRAME_KEY, drawingArray(), indicatorControlId(), normalizeHistorySnapshot(), restoredTimeframe(), appearancePopup(), beginColorDrawingHistory(), changeStyle() (+28 more)

### Community 16 - "Chart Main 3"
Cohesion: 0.09
Nodes (35): chartTabUrl(), resolveChartTabState(), resolveWorkspaceRefreshState(), WORKSPACES, aggregate(), applyChartSettings(), fmt(), formatChartAxisTime() (+27 more)

### Community 17 - "Chart Faraz Candle Api"
Cohesion: 0.11
Nodes (25): ALLOWED_HOSTS, browserExecutable(), buildCandleFilename(), buildCoverageRecoveryChunks(), chunkRange(), clearTextCredentials(), createFarazCandleApi(), findCandleCoverageGaps() (+17 more)

### Community 18 - "Engine Pipeline E Zone Detector"
Cohesion: 0.16
Nodes (12): datetime, Return every Blue-S Order whose stop did not decide the S itself., Materialize immutable initial OrderAudit geometry once per run. Algorithm…, Keep an A-owned order that starts in the parent-stop candle., Return every Order formed and left live inside this parent lifecycle., Return accepted physical Orders confirmed after this parent stopped., Return one final Reset-leg candidate per physical Order after start., Return the first healthy geometry after an A/S/E strict stop. A candidate… (+4 more)

### Community 19 - "Chart Main 4"
Cohesion: 0.09
Nodes (29): calculateMeasureStats(), calculatePositionLevels(), durationLabel(), canonicalCoordinateAtTime(), canonicalTimeAtCoordinate(), constrainLinePoint(), dash(), distSeg() (+21 more)

### Community 20 - "Engine Algorithms Trading Bot Bearish"
Cohesion: 0.06
Nodes (31): 20.10 Dataclass/object schemas present in the source snapshot, 20.1 `reaction_engine.py`, 20.2 `blue_line_detector.py`, 20.3 `a_zone_detector.py`, 20.4 `s_zone_detector.py`, 20.5 `e_zone_detector.py`, 20.6 `lifecycle_engine.py`, 20.7 `trading_pipeline.py` (+23 more)

### Community 21 - "Engine Algorithms Trading Bot Bullish"
Cohesion: 0.06
Nodes (31): 20.10 Dataclass/object schemas present in the source snapshot, 20.1 `reaction_engine.py`, 20.2 `blue_line_detector.py`, 20.3 `a_zone_detector.py`, 20.4 `s_zone_detector.py`, 20.5 `e_zone_detector.py`, 20.6 `lifecycle_engine.py`, 20.7 `trading_pipeline.py` (+23 more)

### Community 22 - "Engine Pipeline E Zone Detector 2"
Cohesion: 0.13
Nodes (15): detect_e_zones(), EZone, EZoneDetector, Return whether a known hard reset lies in ``(start, end]``., Public lifecycle API for the first strict parent stop., Reject only a nested Order_A, while preserving its child lineage., Register non-public S evidence that continues a stopped larger E., Build the E continuation opened by one S consumed by a stopped E. The S remains… (+7 more)

### Community 23 - "Agen"
Cohesion: 0.07
Nodes (28): 10. A: ordinary pair, double-stop, trigger, validating Reaction, 11. S: A-stop handoff, Order ownership and all valid routes, 12. Physical Order_A, Order_B, identity and provenance, 13. Recursive E calculation and reconciliation, 14. Lifecycle priority, repeated Blue groups and StopAll, 15. Cross-stage reconciliation, ownership and visibility, 16. Reproduction and first-difference forensic procedure, 17. Source/Reference and directional audit procedure (+20 more)

### Community 24 - "Chart Screenshot Overlay Test"
Cohesion: 0.10
Nodes (8): resolveCanonicalChartPoint(), MIN_SAFE_BAR_SPACING, zoomOutCapacityGain(), buildIndicatorCalculationRequest(), numeric(), setAnchoredPopoverOpen(), Node.js built-in: node:assert/strict, Node.js built-in: node:test

### Community 25 - "Complete Project Engineering Audit 3"
Cohesion: 0.07
Nodes (28): Accessibility, Animation, Backend Dependencies, Change Map, Charts, Component Tree, Data Flow, Dialogs (+20 more)

### Community 26 - "Engine Pipeline Reaction"
Cohesion: 0.10
Nodes (18): build_behavior_reaction_views(), _decimal_value(), directional_a_stop_order_finder(), MarketChronology, published_reaction_candidate(), datetime, Expose the shared mirror-direction contract to downstream engines., Map an exact lower-timeframe timestamp to its owning main candle. (+10 more)

### Community 27 - "Features Candle Update"
Cohesion: 0.16
Nodes (22): buildChartUpdatePackets(), buildChartUpdateRanges(), buildChartVerificationRanges(), buildGapDetectionRanges(), buildLatestCandleRange(), buildUnverifiedChartUpdateRanges(), chunkCandleUpdates(), chunkCandleUpdatesByBytes() (+14 more)

### Community 28 - "Chart Main 5"
Cohesion: 0.10
Nodes (25): appliedContextMatches(), CONTEXT_KEYS, restoreIndicatorLifecycle(), applyVisualSettings(), calculateIndicator(), calculationKey(), captureIndicatorForm(), clampToolbarPosition() (+17 more)

### Community 29 - "Engine Pipeline Reaction 2"
Cohesion: 0.13
Nodes (13): Python stdlib: array, BearishDetector, DetectionResult, mirror_analysis(), mirror_candidate(), mirror_candle(), Authoritative Reaction geometry and shared market chronology. Owns candle…, Internal coordinate/role adapter; never reclassify a market candle here. Input… (+5 more)

### Community 30 - "Chart Raw Resource Store"
Cohesion: 0.20
Nodes (22): assertCandles(), atomicWrite(), CANDLE_KEYS, createRawResourceStore(), persistedMetadata(), readableCoverage(), readableRange(), runtimeCoverage() (+14 more)

### Community 31 - "Engine Pipeline Reaction 3"
Cohesion: 0.19
Nodes (10): Candidate, Unified v9 directional post-Reset engine. The proven directional detectors…, Return the first structurally owned reaction after Reset. The earliest eligible…, Return the first complete raw Reaction geometry after a boundary. This bounded…, Public lifecycle API for post-Reset geometry discovery., Cached ascending `break_idx` values mirroring `all_reactions[direction]`.…, Return direct Order_A geometry from continuous Reaction context., Return the geometry whose strict confirmation occurs first. Multiple First… (+2 more)

### Community 32 - "Chart Update Contract Test"
Cohesion: 0.12
Nodes (15): args, child, vite, legacyIdentity(), migrateFlatRawFiles(), candles, appCss, exporterSource (+7 more)

### Community 33 - "Engine Algorithms Trading Bot Bearish 2"
Cohesion: 0.08
Nodes (23): 11. OrderAudit contract, 13. StopAll engine, 14. Final visibility and lineage closure, 15. Direction-specific mirror table, 15A. Exact full-pipeline reconstruction sequence, 15F. StopAll exact state machine pseudocode, 17. Determinism, ordering and tie-breaking, 18. Forbidden shortcuts and hard requirements (+15 more)

### Community 34 - "Engine Algorithms Trading Bot Bullish 2"
Cohesion: 0.08
Nodes (23): 11. OrderAudit contract, 13. StopAll engine, 14. Final visibility and lineage closure, 15. Direction-specific mirror table, 15A. Exact full-pipeline reconstruction sequence, 15F. StopAll exact state machine pseudocode, 17. Determinism, ordering and tie-breaking, 18. Forbidden shortcuts and hard requirements (+15 more)

### Community 35 - "Algorithm Page 2"
Cohesion: 0.27
Nodes (23): calculationGuide(), codeSummary(), contractSequence(), definitionFor(), escapeHtml(), familySection(), fieldRows(), glossaryPage() (+15 more)

### Community 36 - "Chart Main 6"
Cohesion: 0.12
Nodes (21): moveIndicatorRange(), nearestIndex(), normalizeIndicatorRange(), applyIndicatorForm(), chartWorkspaceActive(), closeCutCandlesModal(), commitIndicatorRangeInputs(), cutCurrentFile() (+13 more)

### Community 37 - "Features Candle Export"
Cohesion: 0.20
Nodes (14): $id(), initCandleExport(), markup(), request(), timeframeLabel(), VALIDATION_CHECKS, isQualifiedFarazSymbol(), normalizeFarazSymbol() (+6 more)

### Community 38 - "Engine Pipeline Reaction 4"
Cohesion: 0.17
Nodes (9): BullishDetector, Candle, DetectorBase, IntrabarAnalysis, Build one immutable-source timestamp index per calculation process., Reuse a correctly colored confirmation candle for the next reaction., Reuse one immutable lower-timeframe index per source sequence., ResetEvent (+1 more)

### Community 39 - "Trading Bot Bearish Algorithm Reference"
Cohesion: 0.10
Nodes (21): A, Additional findings from the completed source audit, Authority and current versions, Blue Line, Direction and exact comparisons, E and physical Order ownership, Input, time and full-RAW semantics, Invariants, asymmetries and remaining limits (+13 more)

### Community 40 - "Trading Bot Bullish Algorithm Reference"
Cohesion: 0.10
Nodes (21): 10. StopAll and Visibility, 11. Public Bullish Payload, 12. Invariants for Future Changes, 13. Current Known Risks, 1. Status and Version Set, 2. Runtime Contract, 3. Shared Numerical and Time Semantics, 4. Pipeline Order (+13 more)

### Community 41 - "Engine Pipeline Lifecycle"
Cohesion: 0.17
Nodes (7): detect_stopalls(), Decimal, Promote the accepted opposite-color S into a fresh StopAll1. This is the…, Return the pending-reversal exact Blue behavior-group key. S Blue is one group…, Return Blue-repeat metadata when accepted S Red must become StopAll. Accepted…, StopAll, StopAllDetector

### Community 42 - "Chart Package"
Cohesion: 0.10
Nodes (19): dependencies, lightweight-charts, description, devDependencies, playwright-core, vite, keywords, name (+11 more)

### Community 43 - "Chart View Transform"
Cohesion: 0.16
Nodes (17): buildCandleLod(), chooseLodStride(), lowerBoundTime(), coordinateToRawTime(), createViewAnchorCache(), interpolate(), numericTime(), rawIndexAtTime() (+9 more)

### Community 44 - "Engine Pipeline E Zone Detector 3"
Cohesion: 0.12
Nodes (10): A confirmed later Red S closes an older Blue-E order lifecycle., Index one newly accepted physical Order by confirmation chronology., Attach canonical Order_B provenance to already relevant Orders. Order_B…, Return only orders admitted by the E lifecycle, including live ones. This is…, Public audit API for an Order stop crossing., Rebuild Order Audit from accepted S/E/StopAll state only., Rebuild the canonical Order ledger after external E reconciliation. The…, Add audit coverage for externally restored accepted E zones. Visibility may… (+2 more)

### Community 45 - "Engine Pipeline Reaction 5"
Cohesion: 0.17
Nodes (9): classify_candle_color(), LowerTimeframeIndex, Decimal, Immutable segment index for exact first strict High/Low crossings. The index is…, Return the minimum Low and earliest owning position in [left, right)., Return the maximum High and earliest owning position in [left, right)., Match Lightweight Charts: Open <= Close is an up/green candle., Price-reflected view over a lower-timeframe index without rebuilding it. (+1 more)

### Community 46 - "Engine Pipeline Lifecycle 2"
Cohesion: 0.12
Nodes (18): Python stdlib: bisect, filter_internal_behavior_outputs(), forbidden_internal_order_b(), order_identity_is_internal(), point_is_inside_healthy_reaction(), Cross-stage behavior lifecycle, visibility, priority, and StopAll ownership.…, Return whether a numbered Reaction resolves to a protected internal owner., Return whether a behavior's physical Order Reaction is internal. (+10 more)

### Community 47 - "2026 09 21 Complete Project"
Cohesion: 0.11
Nodes (18): Baseline, Completion Dashboard, Cross-Stage Dependencies, Execution Outcome, Execution Tasks, Global Constraints, Open Questions and Unverified Areas, Plan Self-Review (+10 more)

### Community 48 - "Engine Pipeline E Zone Detector 4"
Cohesion: 0.12
Nodes (12): order_identity(), Return the canonical physical Order/Reaction geometry identity., Return ``(FirstIndex, BreakIndex)`` for a Reaction-like object., reaction_identity(), Return raw opposite Reaction geometry inside the closed leg range. Reset…, Return the first canonical opposite Reaction after the Order_B gate., Build every Order_B from same-direction Reset-leg geometry. Bearish mirror:…, Return canonical Order_B Orders whose Reaction forms at/after start. (+4 more)

### Community 49 - "Engine Pipeline Lifecycle 3"
Cohesion: 0.16
Nodes (19): consumed_s_evidence_after_larger_stop(), dominant_module(), finalize_behavior_visibility(), module_identity(), module_priority(), module_stop_event(), Return the earliest suppressed S evidence that continues each stopped E. A…, Preserve the established S eligibility contract consumed by E/StopAll. (+11 more)

### Community 50 - "Agents"
Cohesion: 0.14
Nodes (10): Calculation stage order and lifecycle ownership, Bullish and Bearish are independent directional contracts, Graph index excludes sensitive data values and runtime contents, Browser, Vite, Python runtime boundary, Partial-range requests have bounded chronology, RAW candle integrity belongs to the storage boundary, Python engine is the calculation authority, Path reference alias: README.md (+2 more)

### Community 51 - "Chart Main 7"
Cohesion: 0.18
Nodes (17): updateStageAggregate(), calculationStageDescription(), calculationStageKey(), calculationStageTitle(), calculationTraceAggregates(), escapeHtml(), eventDetails(), formatDuration() (+9 more)

### Community 52 - "Ui Workspace State"
Cohesion: 0.14
Nodes (11): initAlgorithmPage(), storedDirection(), storedLanguage(), storedSidebarState(), applyWorkspaceState(), contracts, mountWorkspaceHeader(), restoreWorkspaceHeader() (+3 more)

### Community 53 - "Features Indicator Cache"
Cohesion: 0.24
Nodes (13): cacheClearLayers(), clearDrawingStorage(), clearIndicatorBrowserState(), clearIndicatorCacheStorage(), clearIndicatorIndexedDb(), clearIndicatorStorage(), deleteDatabase(), isDrawingStorageKey() (+5 more)

### Community 54 - "Chart Main 8"
Cohesion: 0.20
Nodes (17): applyPinnedPanelWidth(), cancelDrawingTool(), checkpoint(), closeSidePanel(), ensurePanelResizeHandle(), finishDraft(), panelWidthLimit(), restoreWorkspaceAfterRefresh() (+9 more)

### Community 55 - "2026 09 17 Tradingbot V2"
Cohesion: 0.12
Nodes (15): Global Constraints, Plan Self-Review, Task 10: Validate the unchanged implementation and generated artifacts, Task 11: Execute the verification-before-completion gate, Task 12: Create and publish the v2.0.0 stable checkpoint, Task 1: Capture the immutable repository baseline, Task 2: Dispatch independent read-only analysis workstreams, Task 3: Generate and verify the project Graphify (+7 more)

### Community 56 - "Project Scripts Start"
Cohesion: 0.21
Nodes (14): Data scope: data/raw (contents not indexed), Data scope: runtime/cache/drawings (contents not indexed), Data scope: runtime/cache/indicator-calculations (contents not indexed), Data scope: runtime/cache/indicator-templates (contents not indexed), Data scope: runtime/tmp/faraz-candle-exports (contents not indexed), Ensure-NpmDependencies(), Ensure-Path(), Ensure-ProjectFiles() (+6 more)

### Community 57 - "Engine Algorithms Trading Bot Bearish 3"
Cohesion: 0.13
Nodes (15): 6.10 Direct same-direction recovery after Reset, 6.11 Frozen owner boundary for direct/Order geometry, 6.12 Canonical Order stop geometry, 6.13 Bounded Order-gate search, 6.14 Internal Reaction classification, 6.1 Core Reaction object, 6.2 Initial Mode-A detection, 6.3 Same-main-candle race: Mode-A invalidation vs confirmation (+7 more)

### Community 58 - "Engine Algorithms Trading Bot Bullish 3"
Cohesion: 0.13
Nodes (15): 6.10 Direct same-direction recovery after Reset, 6.11 Frozen owner boundary for direct/Order geometry, 6.12 Canonical Order stop geometry, 6.13 Bounded Order-gate search, 6.14 Internal Reaction classification, 6.1 Core Reaction object, 6.2 Initial Mode-A detection, 6.3 Same-main-candle race: Mode-A invalidation vs confirmation (+7 more)

### Community 59 - "Engine Pipeline E Zone Detector 5"
Cohesion: 0.20
Nodes (6): Decimal, Return the first strict lower-timeframe crossing in [left, right)., Return the first candle owning the requested closed-range extreme., Return the same-direction Reset owner and its trigger extreme. Bearish: from…, Return the first exact strict break of the reset-leg trigger level. Bearish…, Return the other reset-leg edge on the closed trigger->break range.

### Community 60 - "Agents 2"
Cohesion: 0.15
Nodes (13): A. Project Identity, B. Repository Map, C. Architecture Overview, D. Runtime Execution Flow, E. Engine Knowledge, F. Bullish and Bearish Knowledge, G. Frontend Knowledge, H. Dependency and Data-Flow Map (+5 more)

### Community 61 - "Content Bridge"
Cohesion: 0.18
Nodes (10): branch(), BRIDGE_CALCULATION_GUIDE, BRIDGE_COPY, BRIDGE_ENVELOPE_CATALOG, BRIDGE_FAMILY_CONTRACT, BRIDGE_MODULE_SUMMARY, BRIDGE_TYPE_MODULE_SUMMARIES, normalizeBridgeBranch() (+2 more)

### Community 62 - "Content"
Cohesion: 0.15
Nodes (4): continuation, eContract, ENGINE_CONTRACTS, sContract

### Community 63 - "Algorithm Mirror"
Cohesion: 0.27
Nodes (12): BEARISH_MIRROR_FAMILIES, escapeRegExp(), isBearishMirrorFamily(), mirrorDirectionalLexemes(), mirrorDirectionalText(), mirrorPriceExtremaFunctions(), mirrorPriceOperators(), PRICE_OPERATORS (+4 more)

### Community 64 - "Engine Algorithms Trading Bot Bearish 4"
Cohesion: 0.15
Nodes (13): 15B. E Order creation and shared accepted-Order confirmation — function-level, Carried-live accepted Orders, Order_B Step 1 — same-direction Reset owner and trigger extreme, Order_B Step 2 — exact strict break, Order_B Step 3 — closed evidence interval and mirrored other edge, Order_B Step 4 — raw opposite Reaction geometry only, Order_B Step 5 — physical Order_B after the gate, Order_B Step 6 — cause ownership and latest-cause rule (+5 more)

### Community 65 - "Engine Algorithms Trading Bot Bearish 5"
Cohesion: 0.15
Nodes (13): 24.10 V5.4.3 Bearish XAUUSD 30s regression, 24.11 V5.4.4 cycle-wide Blue-repeat StopAll regression, 24.12 V5.4.5 historical Mode-B refresh regression (superseded by V5.4.8), 24.1 Bearish exact lower-timeframe Reaction confirmation and A ownership, 24.2 Bearish Order bounded Mode-A anchor, 24.3 Bearish chained Blue carried-stop mirror, 24.4 Exact-source E continuation ownership is direction-invariant, 24.5 Bearish validation of exact-key S-reversal StopAll ownership (+5 more)

### Community 66 - "Engine Algorithms Trading Bot Bullish 4"
Cohesion: 0.15
Nodes (13): 15B. E Order creation and shared accepted-Order confirmation — function-level, Carried-live accepted Orders, Order_B Step 1 — same-direction Reset owner and trigger extreme, Order_B Step 2 — exact strict break, Order_B Step 3 — closed evidence interval and mirrored other edge, Order_B Step 4 — raw opposite Reaction geometry only, Order_B Step 5 — physical Order_B after the gate, Order_B Step 6 — cause ownership and latest-cause rule (+5 more)

### Community 67 - "Engine Algorithms Trading Bot Bullish 5"
Cohesion: 0.15
Nodes (13): 24.10 V5.4.3 Bearish XAUUSD 30s regression, 24.11 V5.4.4 cycle-wide Blue-repeat StopAll regression, 24.12 V5.4.5 historical Mode-B refresh regression (superseded by V5.4.8), 24.1 Bullish same-Break confirmation/reset ownership, 24.2 Bullish Blue → A → S → Order → later A/S chain, 24.3 Exact-source E continuation ownership, 24.4 StopAll downstream consequence of correct E ownership, 24.5 Bullish S-reversal StopAll cycle (+5 more)

### Community 68 - "Chart Transfer"
Cohesion: 0.36
Nodes (11): CANDLE_KEYS, chartTransferConstants, createChartTransferBundle(), importChartTransferBundle(), invalid(), isPlainObject(), safeBundleFile(), safeSourceId() (+3 more)

### Community 69 - "Chart Indicator Range Input"
Cohesion: 0.27
Nodes (7): bucketTime(), prepareIndicatorRangeInput(), runIndicatorRangeCalculation(), withIndicatorRangePipe(), Node.js built-in: node:crypto, Node.js built-in: node:net, Node.js built-in: node:url

### Community 70 - "Ui Feedback"
Cohesion: 0.27
Nodes (8): createCaptureFeedback(), farazActivityNotice(), farazExtractionOutcome(), farazLoginWaitingDetail(), indicatorApplyProblem(), indicatorNotificationType(), notificationPresentation(), presentations

### Community 71 - "Complete Project Engineering Audit 4"
Cohesion: 0.17
Nodes (12): 1. Security Scan Scope, 2. Vulnerability Classes, 3. Security Findings Must Be Manually Validated, 4. Security Finding Evidence, 5. Dependency Security, 6. Sensitive Data Protection, 7. Security Reconciliation Pass, 8. Final Security Pass (+4 more)

### Community 72 - "Engine Algorithms Trading Bot Bearish 6"
Cohesion: 0.18
Nodes (11): 10.10 Invalid-A / invalid-S exact same-source cross-family root rule (E 6.6.2), 10.1 Parent strict stop, 10.2 Order routes, 10.3 Canonical Order_B Reset-leg formation — Bearish, 10.4 Canonical Order stop, 10.5 E source, shared accepted Order confirmation, and decision, 10.6 Recursive chains, 10.7 Family and number reconciliation (+3 more)

### Community 73 - "Engine Algorithms Trading Bot Bullish 6"
Cohesion: 0.18
Nodes (11): 10.10 Invalid-A / invalid-S exact same-source cross-family root rule (E 6.6.2), 10.1 Parent strict stop, 10.2 Order routes, 10.3 Canonical Order_B Reset-leg formation — Bullish, 10.4 Canonical Order stop, 10.5 E source, shared accepted Order confirmation, and decision, 10.6 Recursive chains, 10.7 Family and number reconciliation (+3 more)

### Community 74 - "Content Object Catalog"
Cohesion: 0.20
Nodes (6): BRIDGE_OBJECT_CATALOG, bridgeObjects, commonEvent, decisionFields, FIELD_TYPE_OVERRIDES, orderFields

### Community 75 - "Chart Main 9"
Cohesion: 0.22
Nodes (9): calculationInfoPath(), openManualReviewTab(), exportChartData(), focusObjectOnChart(), indicatorToast(), moveDrawingTool(), renderDrawingToolbar(), stitchDrawingIcon() (+1 more)

### Community 76 - "Trading Bot High Performance Zero 2"
Cohesion: 0.20
Nodes (10): 49. REQUIRED FINAL REPORT, Algorithm Changes, Behavioral Changes, Calculation Changes, Changed Files, Memory, New Production Files, Performance (+2 more)

### Community 77 - "Trading Bot Repository Baseline"
Cohesion: 0.20
Nodes (9): Baseline Interpretation, Current-turn baseline reconciliation (2026-09-19), Existing Tags, File Inventory, Git Identity, Pre-Existing Tracked Changes, Pre-Existing Untracked Changes, TradingBot Repository Baseline (+1 more)

### Community 78 - "Engine Algorithms Trading Bot Bearish 7"
Cohesion: 0.20
Nodes (10): 16. Public serialization contract, A, Blue Line, E, OrderAudit, Reaction, Reset, Response envelope (+2 more)

### Community 79 - "Engine Algorithms Trading Bot Bearish 8"
Cohesion: 0.20
Nodes (10): 26.1 `reaction_engine.py`, 26.2 `blue_line_detector.py`, 26.3 `a_zone_detector.py`, 26.4 `s_zone_detector.py`, 26.5 `e_zone_detector.py`, 26.6 `lifecycle_engine.py`, 26.7 `trading_pipeline.py`, 26.8 `direction_policy.py` (+2 more)

### Community 80 - "Engine Algorithms Trading Bot Bullish 7"
Cohesion: 0.20
Nodes (10): 16. Public serialization contract, A, Blue Line, E, OrderAudit, Reaction, Reset, Response envelope (+2 more)

### Community 81 - "Engine Algorithms Trading Bot Bullish 8"
Cohesion: 0.20
Nodes (10): 26.1 `reaction_engine.py`, 26.2 `blue_line_detector.py`, 26.3 `a_zone_detector.py`, 26.4 `s_zone_detector.py`, 26.5 `e_zone_detector.py`, 26.6 `lifecycle_engine.py`, 26.7 `trading_pipeline.py`, 26.8 `direction_policy.py` (+2 more)

### Community 82 - "Trading Bot High Performance Zero 3"
Cohesion: 0.22
Nodes (9): 4. ZERO-DIFFERENCE CONTRACT, A, Blue, E, Order / OrderAudit, Reaction, Reset, S (+1 more)

### Community 83 - "Trading Bot Validation Report"
Cohesion: 0.22
Nodes (8): Commands and Context, Final Integrity Gate, Graphify Evidence, Range/Cut/Identity Addendum, Release Gate Result, Safety and Limitations, Status Summary, TradingBot Validation Report

### Community 84 - "Engine Algorithms Trading Bot Bearish 9"
Cohesion: 0.22
Nodes (9): 15E. Lifecycle function-level reconstruction rules, `consumed_s_evidence_after_larger_stop`, Final lineage closure, Invalid leg-head Order block, `s_zones_for_module_engines`, `s_zones_for_stopall`, `split_a_zones_by_dominant_stops`, `visible_a_zones_after_module_boundaries` (+1 more)

### Community 85 - "Engine Algorithms Trading Bot Bearish 10"
Cohesion: 0.22
Nodes (9): 22.1 Market chronology terms, 22.2 Reaction modes, 22.3 Blue Line types, 22.4 A behavior types, 22.5 S behavior formation families, 22.6 E behavior concepts, 22.7 StopAll, 22.8 OrderAudit (+1 more)

### Community 86 - "Engine Algorithms Trading Bot Bearish 11"
Cohesion: 0.22
Nodes (9): 9.1 Immutable first opposite Order_A after A stop, 9.2 Type-3 S (no new Order before decision), 9.3 Type-4 S Blue — aligned-Reaction candidate before any Order, 9.4 Pre-Order versus post-Order candidate ownership, 9.5 Candidate geometry, 9.6 S decision race, 9.7 A-to-S ownership windows, 9.8 Shared accepted Order-stop reconciliation (+1 more)

### Community 87 - "Engine Algorithms Trading Bot Bullish 9"
Cohesion: 0.22
Nodes (9): 15E. Lifecycle function-level reconstruction rules, `consumed_s_evidence_after_larger_stop`, Final lineage closure, Invalid leg-head Order block, `s_zones_for_module_engines`, `s_zones_for_stopall`, `split_a_zones_by_dominant_stops`, `visible_a_zones_after_module_boundaries` (+1 more)

### Community 88 - "Engine Algorithms Trading Bot Bullish 10"
Cohesion: 0.22
Nodes (9): 22.1 Market chronology terms, 22.2 Reaction modes, 22.3 Blue Line types, 22.4 A behavior types, 22.5 S behavior formation families, 22.6 E behavior concepts, 22.7 StopAll, 22.8 OrderAudit (+1 more)

### Community 89 - "Engine Algorithms Trading Bot Bullish 11"
Cohesion: 0.22
Nodes (9): 9.1 Immutable first opposite Order_A after A stop, 9.2 Type-3 S (no new Order before decision), 9.3 Type-4 S Blue — aligned-Reaction candidate before any Order, 9.4 Pre-Order versus post-Order candidate ownership, 9.5 Candidate geometry, 9.6 S decision race, 9.7 A-to-S ownership windows, 9.8 Shared accepted Order-stop reconciliation (+1 more)

### Community 90 - "Engine Pipeline Lifecycle 4"
Cohesion: 0.22
Nodes (9): accepted_audit_entry(), blocked_orders_while_invalid_leg_heads_are_live(), prepare_order_audit(), datetime, Return order First times owned by a still-live invalid leg head. A strict…, Resolve calculation-valid Order Audit identities before serialization. Multiple…, Return an E-facing A audit entry for one accepted A provenance. A physical…, Resolve accepted stopped-A Orders against provisional Order blocks. Calculation… (+1 more)

### Community 91 - "Agen 2"
Cohesion: 0.25
Nodes (8): Appendix D — Full historic correct/incorrect Behavior and Order registry, D.1 XAUUSD historical 1s (canonical census A) — Bearish 30s, D.2 USOIL 5s 11–15 September (canonical census D) — Bearish 30s, D.3 USOIL 5s 8–12 September (canonical census C) — Bullish 30s, D.4 XAUUSD broad 5s (canonical census B) — Bearish 30s, D.5 Versioned StopAll, dominant-key, native Mode-B and E-recursion anchors, D.6 Pending extended-XAUUSD A-stop→S investigation (NOT yet a passed baseline), D.7 Additional historical datasets and expectation availability

### Community 92 - "Complete Project Engineering Audit 5"
Cohesion: 0.25
Nodes (8): 1. Build the Audit Execution Plan, 2. Maintain a Completion Checklist, 3. Prevent Large-Repository Coverage Gaps, 4. Track Cross-Stage Dependencies, 5. Track Open Questions and Unverified Areas, 6. Perform Audit Checkpoints, 7. Perform Final Completeness Review, Mandatory Superpowers Responsibilities

### Community 93 - "Engine Algorithms Trading Bot Bearish 12"
Cohesion: 0.25
Nodes (8): 15D. E reconciliation — exact ownership rules, Assign accepted family/number, Candidate Order validity, Choose winner at one physical source, Does candidate stop an active E?, Final same-source conflict resolver, Parent active, Prevent lower-priority S stealing active continuation

### Community 94 - "Engine Algorithms Trading Bot Bullish 12"
Cohesion: 0.25
Nodes (8): 15D. E reconciliation — exact ownership rules, Assign accepted family/number, Candidate Order validity, Choose winner at one physical source, Does candidate stop an active E?, Final same-source conflict resolver, Parent active, Prevent lower-priority S stealing active continuation

### Community 95 - "Chart Vite Config 2"
Cohesion: 0.52
Nodes (7): cacheSegment(), calculationPath(), drawingPath(), identityDigest(), legacyDrawingPath(), removeChartArtifacts(), resolveDrawingPath()

### Community 96 - "Trading Bot Cleanup Report"
Cohesion: 0.29
Nodes (6): Current-turn update (2026-09-19), Decision, Reviewed Candidate Classes, Safe Future Cleanup Procedure, Task-Generated Temporary Files, TradingBot Cleanup Report

### Community 97 - "Engine Algorithms Trading Bot Bearish 13"
Cohesion: 0.29
Nodes (7): 3.1 Input rows, 3.2 Price normalization, 3.3 Duplicate raw timestamps, 3.4 Main timeframe buckets, 3.5 Timezone, 3.6 Candle color, 3. Raw data, Decimal, time and candle construction

### Community 98 - "Engine Algorithms Trading Bot Bearish 14"
Cohesion: 0.29
Nodes (7): 7.1 Fibonacci level, 7.2 Scale strikes, 7.3 Scale Blue emission, 7.4 Reset Blue, 7.5 Reset Blue double-stop validity, 7.6 Internal Blue, 7. Blue Line engine — Bearish

### Community 99 - "Engine Algorithms Trading Bot Bearish 15"
Cohesion: 0.29
Nodes (7): 8.1 Blue state and stop, 8.2 Ordinary adjacent-Blue pair, 8.3 Inherited/chained Blue stop, 8.4 A exact-confirmation source ownership, 8.5 Cycle and adjacent reuse, 8.6 Special double-stop A, 8. A engine — Bearish

### Community 100 - "Engine Algorithms Trading Bot Bullish 13"
Cohesion: 0.29
Nodes (7): 3.1 Input rows, 3.2 Price normalization, 3.3 Duplicate raw timestamps, 3.4 Main timeframe buckets, 3.5 Timezone, 3.6 Candle color, 3. Raw data, Decimal, time and candle construction

### Community 101 - "Engine Algorithms Trading Bot Bullish 14"
Cohesion: 0.29
Nodes (7): 7.1 Fibonacci level, 7.2 Scale strikes, 7.3 Scale Blue emission, 7.4 Reset Blue, 7.5 Reset Blue double-stop validity, 7.6 Internal Blue, 7. Blue Line engine — Bullish

### Community 102 - "Engine Algorithms Trading Bot Bullish 15"
Cohesion: 0.29
Nodes (7): 8.1 Blue state and stop, 8.2 Ordinary adjacent-Blue pair, 8.3 Inherited/chained Blue stop, 8.4 A exact-confirmation source ownership, 8.5 Cycle and adjacent reuse, 8.6 Special double-stop A, 8. A engine — Bullish

### Community 103 - "Agen 3"
Cohesion: 0.33
Nodes (6): Appendix E — Complete transferred memory rule and edge-case preservation, E.1 A, Blue and post-stop correctness, E.2 S Red, Type-4, shared Order-stop and same-source owner, E.3 Physical Order provenance, Mode distinctions and lineage, E.4 E recursion, StopAll and historical rescue, E.5 Earlier refactor and performance evidence — historical, not fresh test results

### Community 104 - "Trading Bot Ui Ux Technical 2"
Cohesion: 0.33
Nodes (6): 31. Workstation — Frontend Technical Reference, Layout and States, Modification Guide and Regression Risk, Overview, Source Map and Component Tree, User Workflow

### Community 105 - "Trading Bot Ui Ux Technical 3"
Cohesion: 0.33
Nodes (6): 32. FARAZ Exporter — Frontend Technical Reference, Component Tree and Data Flow, Modification Guide and Regression Risk, Overview, States, Responsive, Accessibility and Security, User Workflow

### Community 106 - "Trading Bot Ui Ux Technical 4"
Cohesion: 0.33
Nodes (6): 33. Algorithm Reference — Frontend Technical Reference, Controls and State, Layout, Responsive and Accessibility, Overview, Route Map, Security and Accuracy

### Community 107 - "Engine Algorithms Trading Bot Bearish 16"
Cohesion: 0.33
Nodes (6): 15C. E zone construction and recursive chain contract, Direct / inherited / carried / accepted-live representatives, E decision/source, Invalid-S-root collision (current E 6.13.0; behavior preserved from the earlier implementation), Provisional chains, Provisional chains

### Community 108 - "Engine Algorithms Trading Bot Bullish 16"
Cohesion: 0.33
Nodes (6): 15C. E zone construction and recursive chain contract, Direct / inherited / carried / accepted-live representatives, E decision/source, Invalid-S-root collision (current E 6.13.0; behavior preserved from the earlier implementation), Provisional chains, Provisional chains

### Community 109 - "Content Glossary"
Cohesion: 0.50
Nodes (4): entry(), GLOSSARY_ENTRIES, normalizeGlossaryEntry(), REACTION_GEOMETRY_REFERENCE

### Community 110 - "Agen 4"
Cohesion: 0.40
Nodes (5): 21.1 XAUUSD historical/Bearish and Source snapshot, 21.2 USOIL Bullish, 21.3 USOIL Bearish, 21.4 Historical memory-only additional checks, 21. Protected historical regression anchors (not production rules)

### Community 111 - "Trading Bot Ui Ux Technical 5"
Cohesion: 0.40
Nodes (5): 34. Manual Review — Frontend Technical Reference, Layout and States, Overview, Security and Regression Risk, Workflow and Dependencies

### Community 112 - "Engine Algorithms Trading Bot Bearish 17"
Cohesion: 0.40
Nodes (5): 21.1 No external project-source dependency, 21.2 Runtime dependencies that are not project-owned source, 21.3 Production command-line/Public API, 21.4 Global mutable state and cache safety, 21. Standalone reconstruction boundary, dependencies, Public API, and cache scope

### Community 113 - "Engine Algorithms Trading Bot Bearish 18"
Cohesion: 0.40
Nodes (5): 25.1 Recommended implementation order, 25.2 Common reconstruction mistakes that change output, 25.3 Observable-equivalence rule, 25.4 HPZR1 performance implementation notes, 25. Reconstruction procedure and implementation traps

### Community 114 - "Engine Algorithms Trading Bot Bearish 19"
Cohesion: 0.40
Nodes (5): 5.1 Main-index mapping, 5.2 Lower windows, 5.3 Reaction confirmation time, 5.4 Reset time, 5. Shared chronology contract

### Community 115 - "Engine Algorithms Trading Bot Bullish 17"
Cohesion: 0.40
Nodes (5): 21.1 No external project-source dependency, 21.2 Runtime dependencies that are not project-owned source, 21.3 Production command-line/Public API, 21.4 Global mutable state and cache safety, 21. Standalone reconstruction boundary, dependencies, Public API, and cache scope

### Community 116 - "Engine Algorithms Trading Bot Bullish 18"
Cohesion: 0.40
Nodes (5): 25.1 Recommended implementation order, 25.2 Common reconstruction mistakes that change output, 25.3 Observable-equivalence rule, 25.4 HPZR1 performance implementation notes, 25. Reconstruction procedure and implementation traps

### Community 117 - "Engine Algorithms Trading Bot Bullish 19"
Cohesion: 0.40
Nodes (5): 5.1 Main-index mapping, 5.2 Lower windows, 5.3 Reaction confirmation time, 5.4 Reset time, 5. Shared chronology contract

### Community 118 - "Engine Pipeline E Zone Detector 6"
Cohesion: 0.40
Nodes (4): OrderBFormation, Recursive E-zone and Order calculation from authoritative S/Reaction state.…, One complete reset-leg Order_B setup under the canonical mirror rule., Python stdlib: types

### Community 119 - "Chart Candle File Response"
Cohesion: 0.83
Nodes (3): entityTag(), matchesEntityTag(), sendCandleFile()

### Community 120 - "Content Calculation Guides"
Cohesion: 0.67
Nodes (3): CALCULATION_GUIDES, guide(), normalizePhase()

### Community 121 - "Agen 5"
Cohesion: 0.50
Nodes (4): 2.1 Different authorities for different questions, 2.2 Per-file two-slot revision policy, 2.3 Required inventory before a substantive task, 2. Authoritative inputs and conflict resolution

### Community 122 - "Trading Bot High Performance Zero 4"
Cohesion: 0.50
Nodes (4): 37. PERFORMANCE OPTIMIZATION STRATEGY, E, Reaction, S

### Community 123 - "Trading Bot Master Prompt For 2"
Cohesion: 0.50
Nodes (4): 8. Mandatory Three-Layer Structure, Layer 1 — Semantic Algorithm Specification, Layer 2 — Reconstruction / Function-Level Specification, Layer 3 — Embedded Production Implementation

### Community 124 - "Engine Algorithms Trading Bot Bearish 20"
Cohesion: 0.50
Nodes (4): 0.1 What counts as a "behavior", 0.2 Hard invariants that apply everywhere, 0.3 Complete module inventory in this snapshot, 0. How to use this document / reconstruction guarantee

### Community 125 - "Engine Algorithms Trading Bot Bearish 21"
Cohesion: 0.50
Nodes (4): 12.1 A after stopped behavior and stage-order ownership, 12.2 S after larger-module stops, 12.3 Same-source S versus E for module engines and StopAll, 12. Lifecycle hierarchy and calculation eligibility

### Community 126 - "Engine Algorithms Trading Bot Bearish 22"
Cohesion: 0.50
Nodes (4): 23.1 Mechanical directional map, 23.2 Invariant rules that must not be directionally swapped, 23.3 End-to-end Bearish behavior flow, 23. Directional rule matrix and full behavior transition catalog — Bearish

### Community 127 - "Engine Algorithms Trading Bot Bullish 20"
Cohesion: 0.50
Nodes (4): 0.1 What counts as a "behavior", 0.2 Hard invariants that apply everywhere, 0.3 Complete module inventory in this snapshot, 0. How to use this document / reconstruction guarantee

### Community 128 - "Engine Algorithms Trading Bot Bullish 21"
Cohesion: 0.50
Nodes (4): 12.1 A after stopped behavior and stage-order ownership, 12.2 S after larger-module stops, 12.3 Same-source S versus E for module engines and StopAll, 12. Lifecycle hierarchy and calculation eligibility

### Community 129 - "Engine Algorithms Trading Bot Bullish 22"
Cohesion: 0.50
Nodes (4): 23.1 Mechanical directional map, 23.2 Invariant rules that must not be directionally swapped, 23.3 End-to-end Bullish behavior flow, 23. Directional rule matrix and full behavior transition catalog — Bullish

### Community 130 - "Engine Pipeline Lifecycle 5"
Cohesion: 0.50
Nodes (4): Return accepted S state that may participate in StopAll grouping. E…, Freeze StopAll boundaries from the accepted chronological E state. StopAll is a…, reconcile_stopall_lifecycle(), s_zones_for_stopall()

### Community 132 - "Agen 6"
Cohesion: 0.67
Nodes (3): 22.1 First-diff comparison is mandatory, 22.2 Suggested regression report fields, 22. Mandatory tests and equivalence criteria

### Community 133 - "Trading Bot High Performance Zero 5"
Cohesion: 0.67
Nodes (3): 10. DIRECTION MIRROR, Bearish, Bullish

### Community 134 - "Trading Bot High Performance Zero 6"
Cohesion: 0.67
Nodes (3): 13. AUTHORITATIVE VS ACCELERATOR DATA, Authoritative, Non-authoritative

### Community 135 - "Trading Bot Master Prompt For 3"
Cohesion: 0.67
Nodes (3): 1. Core Requirement, Requirement A — Exact Synchronization With Current Production Source, Requirement B — Full Standalone Reconstructability

## Knowledge Gaps
- **1303 isolated node(s):** `name`, `version`, `description`, `private`, `dev` (+1298 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TradingBot Bullish Algorithm Reference — Comprehensive Standalone Rebuild & Exact Implementation Specification` connect `Engine Algorithms Trading Bot Bullish 2` to `Engine Algorithms Trading Bot Bullish 21`, `Engine Algorithms Trading Bot Bullish 22`, `Engine Algorithms Trading Bot Bullish`, `Engine Algorithms Trading Bot Bullish 3`, `Engine Algorithms Trading Bot Bullish 4`, `Engine Algorithms Trading Bot Bullish 5`, `Engine Algorithms Trading Bot Bullish 6`, `Engine Algorithms Trading Bot Bullish 7`, `Engine Algorithms Trading Bot Bullish 8`, `Engine Algorithms Trading Bot Bullish 9`, `Engine Algorithms Trading Bot Bullish 10`, `Engine Algorithms Trading Bot Bullish 11`, `Engine Algorithms Trading Bot Bullish 12`, `Engine Algorithms Trading Bot Bullish 13`, `Engine Algorithms Trading Bot Bullish 14`, `Engine Algorithms Trading Bot Bullish 15`, `Engine Algorithms Trading Bot Bullish 16`, `Engine Algorithms Trading Bot Bullish 17`, `Engine Algorithms Trading Bot Bullish 18`, `Engine Algorithms Trading Bot Bullish 19`, `Engine Algorithms Trading Bot Bullish 20`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **Why does `EZoneDetector` connect `Engine Pipeline E Zone Detector 2` to `Engine Pipeline E Zone Detector 4`, `Engine Pipeline E Zone Detector`, `Engine Pipeline E Zone Detector 5`, `Engine Pipeline E Zone Detector 3`?**
  _High betweenness centrality (0.000) - this node is a cross-community bridge._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _1303 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Styles Tokens` be split into smaller, more focused modules?**
  _Cohesion score 0.011235955056179775 - nodes in this community are weakly interconnected._
- **Should `Chart Main` be split into smaller, more focused modules?**
  _Cohesion score 0.022256201155283723 - nodes in this community are weakly interconnected._
- **Should `Complete Project Engineering Audit` be split into smaller, more focused modules?**
  _Cohesion score 0.023529411764705882 - nodes in this community are weakly interconnected._
- **Should `Engine Pipeline A Zone Detector` be split into smaller, more focused modules?**
  _Cohesion score 0.05600722673893405 - nodes in this community are weakly interconnected._

## Corpus scope and sensitive-content handling

- Structural extraction: 92 code files and 17 Markdown documents; 2 HTML entry pages contribute only literal local script/style references.
- Detector classified 111 files (340,018 words). 11 unclassified paths are represented only as file nodes.
- Detector-sensitive `apps/chart/src/styles/tokens.css` was checked with a redacted pattern scan; risk flags={'private_key_marker': False, 'jwt_like_value': False, 'credential_assignment': False, 'long_high_entropy_literals': 0}. Only 177 custom-property names are indexed; values are omitted.
- RAW/runtime directories are scope markers from literal launcher configuration; their contents were not traversed. Credential/session values and `runtime/cache/secret` contents were not accessed or emitted.
- `docs/graphify/` and prior generated Graphify outputs were excluded to avoid self-reference. The detector pruned vendored/build/cache trees and reported no walk errors.
- Semantic LLM extraction was not run. A bounded host-agent inline layer adds 10 concepts, 44 source-located evidence links, and 2 documented hyperedges; it uses explicit maintained text only, with confidence labels and no private-value indexing. Graphify-generated `INFERRED` edges remain labeled as inferred.
- Parallel endpoint links were canonicalized into one directed link each; relation, confidence, source location, context, and occurrence variants are retained in `edge_evidence`.
