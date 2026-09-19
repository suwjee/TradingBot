# Graph Report - TradingBot  (2026-09-19)

## Corpus Check
- Large corpus: 108 files · ~2,951,716 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 1240 nodes · 2774 edges · 54 communities (47 shown, 7 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 70 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0d084590`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 50
- Community 51
- Community 52
- Community 53

## God Nodes (most connected - your core abstractions)
1. `EZoneDetector` - 54 edges
2. `SZoneDetector` - 41 edges
3. `as_decimal()` - 30 edges
4. `drawAll()` - 25 edges
5. `Candle` - 25 edges
6. `AZoneDetector` - 23 edges
7. `calculateIndicator()` - 22 edges
8. `runChartUpdate()` - 22 edges
9. `UnifiedReactionDetector` - 22 edges
10. `createFarazCandleApi()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `build_candle_buckets()` --indirect_call--> `as_decimal()`  [INFERRED]
  engine/bridge/trading_pipeline.py → engine/pipeline/core_utils.py
- `prepare_order_audit()` --calls--> `order_identity()`  [INFERRED]
  engine/pipeline/lifecycle_engine.py → engine/pipeline/core_utils.py
- `strictly_beyond_boundary()` --calls--> `policy_for()`  [INFERRED]
  engine/pipeline/lifecycle_engine.py → engine/pipeline/direction_policy.py
- `reaction_number_is_internal()` --calls--> `order_identity()`  [INFERRED]
  engine/pipeline/lifecycle_engine.py → engine/pipeline/core_utils.py
- `order_identity_is_internal()` --calls--> `order_identity()`  [INFERRED]
  engine/pipeline/lifecycle_engine.py → engine/pipeline/core_utils.py

## Import Cycles
- None detected.

## Communities (54 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (42): detect_e_zones(), EZone, EZoneDetector, datetime, Decimal, Recursive E-zone and Order calculation from authoritative S/Reaction state.…, Return every valid E-space Order formed before this E decision., Return whether a known hard reset lies in ``(start, end]``. (+34 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (63): appRoot, calculationStageDescriptions, canvas, captureFeedback, chart, chartElement, chartSettingInputs, chartSettings (+55 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (37): as_decimal(), order_identity(), Decimal, Small behavior-neutral primitives shared by calculation engines., Preserve Decimal values and normalize other numeric inputs losslessly., Return the canonical physical Order/Reaction geometry identity., Return ``(FirstIndex, BreakIndex)`` for a Reaction-like object., reaction_identity() (+29 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (53): accepted_audit_entry(), blocked_orders_while_invalid_leg_heads_are_live(), consumed_s_evidence_after_larger_stop(), detect_stopalls(), dominant_module(), filter_internal_behavior_outputs(), finalize_behavior_visibility(), forbidden_internal_order_b() (+45 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (59): build_candle_buckets(), build_candle_objects(), build_direction_output(), build_response_payload(), calculate_direction_range_state(), calculate_full_direction_state(), create_e_detector(), DirectionRangeState (+51 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (42): app, fail(), loadCalculationReport(), loading, renderReview(), buildInfoPayload(), buildReviewBody(), causeObject() (+34 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (36): ALGORITHM_COPY, eCarried, eDirect, eRecursive, eResetLeg, FAMILY_SUMMARIES_FA, STOP_RULES_FA, TYPE_STEPS_FA (+28 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (29): aEnginePath, blueEnginePath, bridgePath, cacheSegment(), calculationId(), calculationMetadata(), calculationPath(), calculationsDir (+21 more)

### Community 8 - "Community 8"
Cohesion: 0.10
Nodes (31): Direction, BlueLine, _build_reset_blue_line(), _build_scale_blue_line(), count_scale_strikes(), detect_blue_lines(), fibonacci_level(), _intrabar_pending_confirmation() (+23 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (33): appliedContextMatches(), CONTEXT_KEYS, restoreIndicatorLifecycle(), resolveWorkspaceRefreshState(), WORKSPACES, aggregate(), applyChartSettings(), fmt() (+25 more)

### Community 10 - "Community 10"
Cohesion: 0.16
Nodes (13): AZone, AZoneDetector, BlueState, detect_a_zones(), datetime, Decimal, A-zone calculation from authoritative Reaction and Blue state. Owns Blue-…, Return the exact strict Reset event that makes a Reset Blue exist. (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (23): ALLOWED_HOSTS, browserExecutable(), buildCandleFilename(), buildCoverageRecoveryChunks(), chunkRange(), clearTextCredentials(), createFarazCandleApi(), findCandleCoverageGaps() (+15 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (31): CHART_TIMEFRAME_KEY, drawingArray(), indicatorControlId(), normalizeHistorySnapshot(), restoredTimeframe(), changeStyle(), checkpoint(), closeUniversalColorPicker() (+23 more)

### Community 13 - "Community 13"
Cohesion: 0.14
Nodes (21): $id(), initCandleExport(), markup(), request(), timeframeLabel(), VALIDATION_CHECKS, isQualifiedFarazSymbol(), normalizeFarazSymbol() (+13 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (28): resolveCanonicalChartPoint(), canonicalCoordinateAtTime(), canonicalTimeAtCoordinate(), chartViewAnchors(), constrainLinePoint(), dash(), distSeg(), drawIndicator() (+20 more)

### Community 15 - "Community 15"
Cohesion: 0.16
Nodes (12): Candidate, Unified v9 directional post-Reset engine. The proven directional detectors…, Reuse a correctly colored confirmation candle for the next reaction., Return the first structurally owned reaction after Reset. The earliest eligible…, Return the first complete same-direction geometry after Reset. This search…, Public lifecycle API for post-Reset geometry discovery., Find the first E Order_B geometry from its actual Reset context. The Order_B…, Cached ascending `break_idx` values mirroring `all_reactions[direction]`.… (+4 more)

### Community 16 - "Community 16"
Cohesion: 0.10
Nodes (18): build_behavior_reaction_views(), _decimal_value(), directional_a_stop_order_finder(), MarketChronology, published_reaction_candidate(), datetime, Expose the shared mirror-direction contract to downstream engines., Map an exact lower-timeframe timestamp to its owning main candle. (+10 more)

### Community 17 - "Community 17"
Cohesion: 0.16
Nodes (22): buildChartUpdatePackets(), buildChartUpdateRanges(), buildChartVerificationRanges(), buildGapDetectionRanges(), buildLatestCandleRange(), buildUnverifiedChartUpdateRanges(), chunkCandleUpdates(), chunkCandleUpdatesByBytes() (+14 more)

### Community 18 - "Community 18"
Cohesion: 0.11
Nodes (27): applyVisualSettings(), calculateIndicator(), calculationKey(), cancelDrawingTool(), captureIndicatorForm(), clampToolbarPosition(), clearActiveIndicatorCalculation(), clearIndicatorCache() (+19 more)

### Community 19 - "Community 19"
Cohesion: 0.13
Nodes (13): BearishDetector, DetectionResult, IntrabarAnalysis, mirror_analysis(), mirror_candidate(), mirror_candle(), Authoritative Reaction geometry and shared market chronology. Owns candle…, Internal coordinate/role adapter; never reclassify a market candle here. Input… (+5 more)

### Community 20 - "Community 20"
Cohesion: 0.27
Nodes (23): calculationGuide(), codeSummary(), contractSequence(), definitionFor(), escapeHtml(), familySection(), fieldRows(), glossaryPage() (+15 more)

### Community 21 - "Community 21"
Cohesion: 0.14
Nodes (20): updateStageAggregate(), calculationStageDescription(), calculationStageKey(), calculationStageTitle(), calculationTraceAggregates(), errorLogText(), escapeHtml(), eventDetails() (+12 more)

### Community 22 - "Community 22"
Cohesion: 0.10
Nodes (19): dependencies, lightweight-charts, description, devDependencies, playwright-core, vite, keywords, name (+11 more)

### Community 23 - "Community 23"
Cohesion: 0.17
Nodes (9): classify_candle_color(), LowerTimeframeIndex, Decimal, Immutable segment index for exact first strict High/Low crossings. The index is…, Return the minimum Low and earliest owning position in [left, right)., Return the maximum High and earliest owning position in [left, right)., Match Lightweight Charts: Open <= Close is an up/green candle., Price-reflected view over a lower-timeframe index without rebuilding it. (+1 more)

### Community 24 - "Community 24"
Cohesion: 0.18
Nodes (16): buildCandleLod(), chooseLodStride(), lowerBoundTime(), coordinateToRawTime(), createViewAnchorCache(), interpolate(), numericTime(), rawIndexAtTime() (+8 more)

### Community 25 - "Community 25"
Cohesion: 0.20
Nodes (7): BullishDetector, Candle, DetectorBase, Build one immutable-source timestamp index per calculation process., Reuse one immutable lower-timeframe index per source sequence., ResetEvent, shared_lower_timeframe_index()

### Community 26 - "Community 26"
Cohesion: 0.14
Nodes (11): initAlgorithmPage(), storedDirection(), storedLanguage(), storedSidebarState(), applyWorkspaceState(), contracts, mountWorkspaceHeader(), restoreWorkspaceHeader() (+3 more)

### Community 27 - "Community 27"
Cohesion: 0.24
Nodes (13): cacheClearLayers(), clearDrawingStorage(), clearIndicatorBrowserState(), clearIndicatorCacheStorage(), clearIndicatorIndexedDb(), clearIndicatorStorage(), deleteDatabase(), isDrawingStorageKey() (+5 more)

### Community 28 - "Community 28"
Cohesion: 0.30
Nodes (15): assertCandles(), atomicWrite(), CANDLE_KEYS, createRawResourceStore(), persistedMetadata(), readableCoverage(), readableRange(), runtimeCoverage() (+7 more)

### Community 29 - "Community 29"
Cohesion: 0.16
Nodes (16): applyIndicatorForm(), beginColorDrawingHistory(), chartWorkspaceActive(), commitIndicatorRangeInputs(), displayPickerValue(), indicatorStateKey(), inputFromTehran(), openIndicator() (+8 more)

### Community 30 - "Community 30"
Cohesion: 0.18
Nodes (10): branch(), BRIDGE_CALCULATION_GUIDE, BRIDGE_COPY, BRIDGE_ENVELOPE_CATALOG, BRIDGE_FAMILY_CONTRACT, BRIDGE_MODULE_SUMMARY, BRIDGE_TYPE_MODULE_SUMMARIES, normalizeBridgeBranch() (+2 more)

### Community 31 - "Community 31"
Cohesion: 0.15
Nodes (4): continuation, eContract, ENGINE_CONTRACTS, sContract

### Community 32 - "Community 32"
Cohesion: 0.27
Nodes (12): BEARISH_MIRROR_FAMILIES, escapeRegExp(), isBearishMirrorFamily(), mirrorDirectionalLexemes(), mirrorDirectionalText(), mirrorPriceExtremaFunctions(), mirrorPriceOperators(), PRICE_OPERATORS (+4 more)

### Community 33 - "Community 33"
Cohesion: 0.30
Nodes (12): applyPinnedPanelWidth(), closeSidePanel(), ensurePanelResizeHandle(), panelWidthLimit(), restoreWorkspaceAfterRefresh(), selectWorkspaceNavigation(), setDrawingToolsActive(), setPanelPinned() (+4 more)

### Community 34 - "Community 34"
Cohesion: 0.17
Nodes (11): built_at_commit, directed, generated_at, graph, communities, links, nodes, inventory (+3 more)

### Community 35 - "Community 35"
Cohesion: 0.36
Nodes (9): Ensure-NpmDependencies(), Ensure-Path(), Ensure-ProjectFiles(), Ensure-Runtimes(), Find-Command(), Install-Winget(), Refresh-Path(), Start-DevServer() (+1 more)

### Community 36 - "Community 36"
Cohesion: 0.20
Nodes (6): BRIDGE_OBJECT_CATALOG, bridgeObjects, commonEvent, decisionFields, FIELD_TYPE_OVERRIDES, orderFields

### Community 38 - "Community 38"
Cohesion: 0.46
Nodes (6): buildRawFilename(), formatTehranFileTime(), parseRawFilename(), partsAt(), safePart(), tehranParts

### Community 39 - "Community 39"
Cohesion: 0.25
Nodes (6): badEndpoints, graph, ids, rawFiles, rawRoot, root

### Community 40 - "Community 40"
Cohesion: 0.50
Nodes (3): legacyIdentity(), migrateFlatRawFiles(), localDataApi()

### Community 41 - "Community 41"
Cohesion: 0.50
Nodes (4): entry(), GLOSSARY_ENTRIES, normalizeGlossaryEntry(), REACTION_GEOMETRY_REFERENCE

### Community 42 - "Community 42"
Cohesion: 0.40
Nodes (4): appearancePopup(), styleModule(), icon(), paths

### Community 44 - "Community 44"
Cohesion: 0.40
Nodes (4): appCss, exporterSource, mainSource, viteSource

### Community 45 - "Community 45"
Cohesion: 0.50
Nodes (3): args, child, vite

### Community 46 - "Community 46"
Cohesion: 0.67
Nodes (3): CALCULATION_GUIDES, guide(), normalizePhase()

### Community 48 - "Community 48"
Cohesion: 0.67
Nodes (3): calculationInfoPath(), openManualReviewTab(), exportChartData()

## Knowledge Gaps
- **149 isolated node(s):** `type`, `name`, `version`, `description`, `private` (+144 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `drawAll()` connect `Community 18` to `Community 29`, `Community 14`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **Why does `setDrawingToolsActive()` connect `Community 33` to `Community 18`, `Community 12`?**
  _High betweenness centrality (0.000) - this node is a cross-community bridge._
- **What connects `type`, `name`, `version` to the rest of the system?**
  _149 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06248600223964166 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.026302349336057202 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.07492507492507493 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.05658381808566896 - nodes in this community are weakly interconnected._