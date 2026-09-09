# Graph Report - TradingBot  (2026-09-08)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1234 nodes · 2493 edges · 86 communities (53 shown, 33 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 71 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7d635cd1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app/Reaction-detection-new.py
- main.js
- EDetector
- SDetector
- test_e_rules.py
- reaction_bridge.py
- candle
- Bullish Indicator Algorithm
- manual-review.js
- Bullish Leg Review Amendment
- vite.config.js
- drawAll
- test_directional_symmetry.py
- ADetector
- loadFile
- indicator-interaction.test.mjs
- calculateIndicator
- ui-state.test.mjs
- drawIndicator
- package.json
- app/test_user_verified_ranges.py
- openIndicator
- Bearish indicator algorithm
- StopAllDetector
- test_stopall_rules.py
- TradingBot Agent Instructions
- test_bullish_leg_review.py
- Bullish Leg Continuation Handoff
- Start-TradingBot.ps1
- Current TradingBot handoff
- app/test_reaction_detection_new.py
- test_range_context_invariance.py
- candle-export.js
- manual-test-handoff.test.mjs
- Manual Review Presentation Test
- test_bearish_30s_bridge.py
- vite-dev.mjs
- chart-lod.js
- rebuildIndicatorObjects
- candle-export-ui.test.mjs
- User Working Rules
- test_xau_reset_window_a.py
- test_xau_two_stop_a.py
- test_fxcm_usoil_5s_integrated.py
- test_s_gate_order.py
- QG Chart Workstation
- clone
- calculation-cache.test.mjs
- candle-color.test.mjs
- Deterministic Output Equivalence
- One Writer Per Write Surface
- test_a_pipeline.py
- test_s_pipeline.py
- test_e_pipeline.py
- calculation-progress.js
- Learn Trading Rule Skill
- Chronological Dominant-Owner Selection
- TradingBot UI UX Design Rules
- browser-compat.test.mjs
- calculation-progress-info.test.mjs
- drawing-vertex-path.test.mjs
- Git Workflow
- Integrated Pipeline Order
- datetime
- Path
- Path
- ArgumentParser
- datetime
- Decimal
- Path
- Path
- ArgumentParser
- datetime
- Decimal
- datetime
- datetime
- skipif
- datetime
- Decimal
- OrderMatch
- Decimal
- OrderMatch
- datetime
- Decimal

## God Nodes (most connected - your core abstractions)
1. `EDetector` - 44 edges
2. `SDetector` - 38 edges
3. `candle()` - 29 edges
4. `UnifiedReactionDetector` - 28 edges
5. `Candle` - 27 edges
6. `Candidate` - 25 edges
7. `_decimal()` - 24 edges
8. `drawAll()` - 22 edges
9. `ADetector` - 21 edges
10. `calculateIndicator()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Output Equivalence` --semantically_similar_to--> `Parity Validation Requirements`  [INFERRED] [semantically similar]
  OPTIMIZATION_SUMMARY.md → docs/algorithms/BULLISH_INDICATOR_ALGORITHM.md
- `Range Contract` --semantically_similar_to--> `Isolated Virtual File Range`  [INFERRED] [semantically similar]
  OPTIMIZATION_SUMMARY.md → docs/algorithms/BULLISH_INDICATOR_ALGORITHM.md
- `Verification Artifacts Authority Boundary` --semantically_similar_to--> `Runtime Authority`  [INFERRED] [semantically similar]
  OPTIMIZATION_SUMMARY.md → docs/algorithms/BULLISH_INDICATOR_ALGORITHM.md
- `Lightweight Charts Workstation` --conceptually_related_to--> `Python Calculation Authority`  [INFERRED]
  AI-Directories/PROJECT_MAP.md → AGENTS.md
- `A and S Confirmation Lookup Cache` --conceptually_related_to--> `Bullish A Zone`  [INFERRED]
  OPTIMIZATION_SUMMARY.md → docs/algorithms/BULLISH_INDICATOR_ALGORITHM.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Bullish Pipeline Stages** — docs_algorithms_bullish_indicator_algorithm_reaction_and_reset_data_model, docs_algorithms_bullish_indicator_algorithm_bullish_blue_line, docs_algorithms_bullish_indicator_algorithm_bullish_a_zone, docs_algorithms_bullish_indicator_algorithm_bullish_s_zone, docs_algorithms_bullish_indicator_algorithm_bullish_stopall [EXTRACTED 1.00]
- **Order Lifecycle and Audit** — docs_algorithms_bullish_indicator_algorithm_bearish_order_authority, docs_algorithms_bullish_indicator_algorithm_bullish_s_zone, docs_algorithms_bullish_indicator_algorithm_accepted_order_ledger, docs_algorithms_bullish_indicator_algorithm_bullish_stopall, docs_algorithms_bullish_indicator_algorithm_order_audit [EXTRACTED 1.00]
- **Performance Optimization Mechanisms** — optimization_summary_bridge_geometry_reuse, optimization_summary_reaction_shared_indexes, optimization_summary_a_and_s_confirmation_lookup_cache, optimization_summary_e_shared_search_indexes, optimization_summary_verified_performance_result [EXTRACTED 1.00]
- **TradingBot Documentation Governance** — agents_overview, ai_directories_readme_overview, ai_directories_project_map_overview [EXTRACTED 1.00]
- **Application Entry Shells** — lightweight_charts_index_qg_chart_workstation, lightweight_charts_index_app_mount, lightweight_charts_index_main_module [INFERRED 0.85]
- **Manual Review Presentation Flow** — lightweight_charts_tests_manual_review_browser_reviewfixture, lightweight_charts_tests_manual_review_browser_rendermanualreview, lightweight_charts_tests_manual_review_browser_indicator_review_iframe [INFERRED 0.85]
- **Pipeline Governance** — ai_directories_bullish_leg_continuation_handoff_module_calculation_ownership, ai_directories_user_working_rules_formalize_before_source_change [INFERRED 0.85]
- **Chart and Candle Validation** — tradingbot_chart_workstation, tradingbot_raw_candle_inventory, tradingbot_asia_tehran_timezone, lightweight_charts_manual_test_overview [INFERRED 0.85]

## Communities (86 total, 33 thin omitted)

### Community 0 - "app/Reaction-detection-new.py"
Cohesion: 0.05
Nodes (63): ArgumentParser, BearishDetector, build_argument_parser(), build_report(), BullishDetector, Candidate, Candle, choose_range_interactively() (+55 more)

### Community 1 - "main.js"
Cohesion: 0.03
Nodes (62): calculationStageDescriptions, canvas, chart, chartElement, chartSettingInputs, chartSettings, chartSettingsDefaults, COLOR_OPACITY_TARGETS (+54 more)

### Community 2 - "EDetector"
Cohesion: 0.08
Nodes (32): Decimal, _CrossIndex, _d(), detect_e_zones(), EDetector, EZone, datetime, Recursive E detection over authoritative S and Reaction output. (+24 more)

### Community 3 - "SDetector"
Cohesion: 0.11
Nodes (21): _decimal(), detect_s_zones(), datetime, Exact S detection over authoritative Reaction and A output., Return A objects whose source candle is not occupied by a final S., Return the directional extreme, assigning equality to the last candle., Find the aligned reaction after the A stop. In the pre-order candidate case the…, Use the inclusive order-Break to aligned-Break interval. (+13 more)

### Community 4 - "test_e_rules.py"
Cohesion: 0.07
Nodes (54): parametrize, Isolated accepted-order inputs exercise E ownership, not Reaction discovery., scenario(), test_e_owns_joint_stop_over_later_same_family_s(), test_older_single_red_s_owns_joint_stop_over_nested_blue_e(), test_stopall_reset_preserves_order_child_but_restarts_e_numbering(), test_unstopped_red_s_does_not_recolor_nested_blue_e(), parametrize (+46 more)

### Community 5 - "reaction_bridge.py"
Cohesion: 0.07
Nodes (56): _a_zones_for_module_engines(), blocked_orders_while_invalid_leg_heads_are_live(), build_candle_buckets(), build_candle_objects(), build_candle_views(), build_candles(), bullish_a_stop_order_finder(), decimal() (+48 more)

### Community 6 - "candle"
Cohesion: 0.11
Nodes (34): BlueLine, count_scale_strikes(), detect_blue_lines(), fibonacci_level(), _intrabar_pending_confirmation(), _is_color(), _main_candle(), datetime (+26 more)

### Community 7 - "Bullish Indicator Algorithm"
Cohesion: 0.07
Nodes (48): A Ownership Window, Accepted Order Ledger, Bearish Order Authority, Blue Spacing Lock, Blue Stop Lifecycle, Browser Rendering Boundary, Bullish A Zone, Bullish Blue Line (+40 more)

### Community 8 - "manual-review.js"
Cohesion: 0.11
Nodes (42): buildInfoPayload(), buildReviewBody(), causeObject(), collections, colorSpec, detail(), escapeHtml(), eventCard() (+34 more)

### Community 9 - "Bullish Leg Review Amendment"
Cohesion: 0.05
Nodes (41): Same-candle A stop Order context, Chronological dominant owner, Bearish leg amendment, Inherited Order deadline, XAUUSD reflection verification, Bearish leg ownership, No independent Bearish historical reference, Inherited Order deadline and supersession (+33 more)

### Community 10 - "vite.config.js"
Cohesion: 0.06
Nodes (31): aEnginePath, blueEnginePath, bridgePath, cacheSegment(), calculationId(), calculationMetadata(), calculationPath(), calculationsDir (+23 more)

### Community 11 - "drawAll"
Cohesion: 0.11
Nodes (34): cancelDrawingTool(), changeStyle(), chartWorkspaceActive(), checkpoint(), clampToolbarPosition(), closeUniversalColorPicker(), colorControlTrigger(), drawAll() (+26 more)

### Community 12 - "test_directional_symmetry.py"
Cohesion: 0.16
Nodes (28): epoch(), Regression for the user-confirmed XAUUSD pre-order Blue S., run_bullish_window(), test_bullish_pre_order_candidate_becomes_blue_s(), test_full_file_preserves_verified_half_leg_behaviors(), test_isolated_range_does_not_inherit_the_prior_stopped_owner(), test_stopped_dominant_s_advances_lifecycle_without_hiding_half_leg_a(), test_stopped_s_parent_remains_visible_when_it_builds_e() (+20 more)

### Community 13 - "ADetector"
Cohesion: 0.22
Nodes (9): ADetector, AZone, BlueState, _decimal(), detect_a_zones(), datetime, Exact A detection over authoritative Reaction and Blue Line output., Return the exact strict Reset event that makes a Reset Blue exist. (+1 more)

### Community 14 - "loadFile"
Cohesion: 0.10
Nodes (27): aggregate(), applyChartSettings(), errorLogText(), exportChartData(), fmt(), focusObjectOnChart(), formatChartAxisTime(), formatSystemDateTime() (+19 more)

### Community 15 - "indicator-interaction.test.mjs"
Cohesion: 0.08
Nodes (3): section(), source, visibilityHarness()

### Community 16 - "calculateIndicator"
Cohesion: 0.12
Nodes (26): applyVisualSettings(), calculateIndicator(), calculationKey(), calculationStageDescription(), calculationStageKey(), calculationStageTitle(), calculationTraceAggregates(), captureIndicatorForm() (+18 more)

### Community 17 - "ui-state.test.mjs"
Cohesion: 0.13
Nodes (10): CHART_TIMEFRAME_KEY, drawingArray(), indicatorControlId(), normalizeHistorySnapshot(), restoredTimeframe(), drawing, harness(), indicator (+2 more)

### Community 18 - "drawIndicator"
Cohesion: 0.13
Nodes (21): constrainLinePoint(), dash(), distSeg(), drawIndicator(), drawOne(), handle(), hitTest(), indicatorHitTest() (+13 more)

### Community 19 - "package.json"
Cohesion: 0.10
Nodes (19): lightweight-charts, dependencies, lightweight-charts, description, devDependencies, playwright-core, vite, keywords (+11 more)

### Community 20 - "app/test_user_verified_ranges.py"
Cohesion: 0.29
Nodes (17): ACase, Case, final_visible_a_zones(), load_module(), main(), project_path(), Path, Candidate timing must mirror strictly around the order box boundary. (+9 more)

### Community 21 - "openIndicator"
Cohesion: 0.14
Nodes (18): applyIndicatorForm(), applyPinnedPanelWidth(), beginColorDrawingHistory(), closeSidePanel(), commitIndicatorRangeInputs(), displayPickerValue(), ensurePanelResizeHandle(), indicatorStateKey() (+10 more)

### Community 22 - "Bearish indicator algorithm"
Cohesion: 0.12
Nodes (16): Bearish A formation, XAUUSD logical reflection acceptance, Bearish Blue Line, Bridge ownership and fixed point, Decimal and temporal contract, Bearish indicator algorithm, Bearish E and accepted Order ledger, Exact directional mirror contract (+8 more)

### Community 23 - "StopAllDetector"
Cohesion: 0.28
Nodes (7): _d(), detect_stopalls(), datetime, Decimal, StopAll detection over authoritative S/E output., StopAll, StopAllDetector

### Community 24 - "test_stopall_rules.py"
Cohesion: 0.23
Nodes (15): load_bridge(), load_stopall(), Reusing the reconciled detector must not inherit its previous order ledger., run_strict_bullish_range(), test_clarified_range_continues_after_stopall_with_exclusive_labels_and_order_causes(), test_clarified_red_transition_requires_order_confirmation_inside_to(), test_full_file_dominant_e_blocks_early_s_and_preserves_stopall_lineage(), test_red_e_family_always_dominates_blue_regardless_of_number() (+7 more)

### Community 25 - "TradingBot Agent Instructions"
Cohesion: 0.17
Nodes (15): TradingBot Agent Instructions, Analyze TradingBot Chart Skill, Develop Chart Workstation Skill, Maintain Indicator Pipeline Skill, Validate Candle Data Skill, Data and Generated Output Policy, TradingBot Project Map, AI Routing Index (+7 more)

### Community 26 - "test_bullish_leg_review.py"
Cohesion: 0.26
Nodes (13): fixture, bullish(), epoch(), matching_rows(), parametrize, Acceptance requirements from the user's evolving bullish leg lesson. Historical…, Order_B is a formation cause, not merely Reaction mode B., Requested behaviors are valid; rejected candidates never reach output. (+5 more)

### Community 27 - "Bullish Leg Continuation Handoff"
Cohesion: 0.18
Nodes (10): Bullish Leg Continuation Handoff, Bullish-Only Implementation Scope, Completed continuation work, Confirmed user rules, Current acceptance state, Current implementation already present, Maintenance checks, Module Calculation Ownership (+2 more)

### Community 28 - "Start-TradingBot.ps1"
Cohesion: 0.36
Nodes (9): Ensure-NpmDependencies(), Ensure-Path(), Ensure-ProjectFiles(), Ensure-Runtimes(), Find-Command(), Install-Winget(), Refresh-Path(), Start-DevServer() (+1 more)

### Community 29 - "Current TradingBot handoff"
Cohesion: 0.20
Nodes (10): Accepted calculations only, Python calculation pipeline and chart workstation, Maintained Bullish source authority, Authorized complete Bearish mirror, Current TradingBot handoff, Graphify navigation not calculation input, Independent selected range universe, Bullish leg ownership rules (+2 more)

### Community 30 - "app/test_reaction_detection_new.py"
Cohesion: 0.28
Nodes (7): chart_doji_regression(), Independent test reflection; does not call production mirror helpers., Use real OHLC classification, including dojis, without historical input., Compare complete outputs and geometry, not only event counts., reference_mirror_candles(), reference_mirror_regression(), reflected_result()

### Community 31 - "test_range_context_invariance.py"
Cohesion: 0.48
Nodes (6): epoch(), Path, A selected calculation range behaves as an independent virtual file., run_bridge(), test_repeated_selected_range_is_deterministic(), test_selected_range_matches_a_physical_file_with_only_that_range()

### Community 32 - "candle-export.js"
Cohesion: 0.52
Nodes (6): $id(), initCandleExport(), markup(), request(), timeframeLabel(), VALIDATION_CHECKS

### Community 33 - "manual-test-handoff.test.mjs"
Cohesion: 0.43
Nodes (5): calculationInfoPath(), openManualReviewTab(), calculation, entrySource, viteSource

### Community 34 - "Manual Review Presentation Test"
Cohesion: 0.33
Nodes (7): Indicator Review Iframe, Presentation Test Inline Module, Manual Review Presentation Test, Presentation-Only Test Isolation, renderManualReview, reviewFixture, Synthetic Presentation Fixture

### Community 35 - "test_bearish_30s_bridge.py"
Cohesion: 0.53
Nodes (5): epoch(), skipif, User-approved A/S acceptance through the complete maintained bridge., test_confirmed_bearish_a_to_s_ownership(), test_xau_bullish_visual_blue_a_type3_and_red_s()

### Community 36 - "vite-dev.mjs"
Cohesion: 0.33
Nodes (5): args, child, debug, inputArgs, vite

### Community 37 - "chart-lod.js"
Cohesion: 0.53
Nodes (4): buildCandleLod(), chooseLodStride(), lowerBoundTime(), candles

### Community 38 - "rebuildIndicatorObjects"
Cohesion: 0.40
Nodes (6): indicatorOverrideKey(), readIndicatorOverrides(), rebuildIndicatorObjects(), removeInvalidIndicatorCalculations(), restoreChartIndicatorContext(), saveIndicatorObjectOverrides()

### Community 39 - "candle-export-ui.test.mjs"
Cohesion: 0.33
Nodes (5): api, appCss, main, ui, vite

### Community 40 - "User Working Rules"
Cohesion: 0.40
Nodes (5): No Historical Hardcoding Rule, Clarification Before Implementation, Exact Evidence Reporting, Formalize Before Source Change, User Working Rules

### Community 41 - "test_xau_reset_window_a.py"
Cohesion: 0.50
Nodes (4): epoch(), skipif, Bridge acceptance for the verified XAUUSD Reset-window A correction., test_bearish_reset_windows_remove_early_a()

### Community 42 - "test_xau_two_stop_a.py"
Cohesion: 0.50
Nodes (4): epoch(), skipif, Regression coverage for ordinary and special two-Blue-stop A ownership., test_bullish_two_stop_a_ownership_and_source_range()

### Community 43 - "test_fxcm_usoil_5s_integrated.py"
Cohesion: 0.50
Nodes (4): load(), main(), Path, Integrated Reaction -> Blue -> A -> S -> E smoke test for the supplied USOIL…

### Community 44 - "test_s_gate_order.py"
Cohesion: 0.40
Nodes (3): parametrize, S order ownership must follow exact events, not rounded candle timestamps., test_only_the_confirmation_that_stops_a_opens_the_new_order_context()

### Community 45 - "QG Chart Workstation"
Cohesion: 0.50
Nodes (5): Application Mount Element, Workstation Application Shell, Google Fonts Resources, Main Application Module, QG Chart Workstation

### Community 46 - "clone"
Cohesion: 0.40
Nodes (5): clone(), createUniqueId(), moveDrawing(), newDrawing(), shiftPoint()

### Community 47 - "calculation-cache.test.mjs"
Cohesion: 0.40
Nodes (3): config, files, request

### Community 48 - "candle-color.test.mjs"
Cohesion: 0.40
Nodes (4): end, library, select, start

### Community 50 - "Deterministic Output Equivalence"
Cohesion: 0.67
Nodes (3): Optimize Indicator Pipeline Skill, Speed Coding Rules, Deterministic Output Equivalence

### Community 51 - "One Writer Per Write Surface"
Cohesion: 0.67
Nodes (3): Native Agent Orchestration, Concurrent Codex Protocol, One Writer Per Write Surface

## Ambiguous Edges - Review These
- `Rejected Candidate Public-Payload Exclusion` → `Unresolved E Parent Lineage`  [AMBIGUOUS]
  docs/audits/2026-09-07-full-bullish-30s-raw-forexcom-audit.md · relation: conceptually_related_to

## Knowledge Gaps
- **172 isolated node(s):** `calculationStageDescriptions`, `canvas`, `chart`, `chartElement`, `chartSettingInputs` (+167 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Rejected Candidate Public-Payload Exclusion` and `Unresolved E Parent Lineage`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `candle()` connect `candle` to `app/test_user_verified_ranges.py`?**
  _High betweenness centrality (0.002) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `candle()` (e.g. with `synthetic_a_mirror_regression()` and `synthetic_owner_regression()`) actually correct?**
  _`candle()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `calculationStageDescriptions`, `canvas`, `chart` to the rest of the system?**
  _172 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app/Reaction-detection-new.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05225225225225225 - nodes in this community are weakly interconnected._
- **Should `main.js` be split into smaller, more focused modules?**
  _Cohesion score 0.0272654370489174 - nodes in this community are weakly interconnected._
- **Should `EDetector` be split into smaller, more focused modules?**
  _Cohesion score 0.0795196364816618 - nodes in this community are weakly interconnected._