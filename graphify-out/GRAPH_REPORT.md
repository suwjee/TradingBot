# Graph Report - TradingBot  (2026-09-07)

## Corpus Check
- 92 files · ~143,034 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1443 nodes · 3306 edges · 67 communities (58 shown, 9 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 65 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `aef5d854`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app/Reaction-detection-new.py
- __backup_20260904-010128/Reaction-detection-new.py
- candle
- main.js
- EDetector
- EDetector
- SDetector
- SDetector
- test_e_rules.py
- backend/reaction_bridge.py
- manual-review.js
- vite.config.js
- __backup_20260904-010128/reaction_bridge.py
- startCalculationProgress
- renderObjectTree
- ADetector
- ADetector
- indicator-interaction.test.mjs
- ui-state.test.mjs
- loadFile
- drawAll
- package.json
- Reaction Blue Line A S E StopAll Pipeline
- drawIndicator
- __backup_20260904-010128/blue_line.py
- StopAllDetector
- StopAllDetector
- test_stopall_rules.py
- test_directional_symmetry.py
- openIndicator
- Start-TradingBot.ps1
- test_xau_pre_order_blue_s.py
- renderChartViewport
- __backup_20260904-010128/test_reaction_detection_new.py
- app/test_reaction_detection_new.py
- candle-export.js
- manual-test-handoff.test.mjs
- Manual Review Presentation Test
- test_bearish_30s_bridge.py
- vite-dev.mjs
- candle-export-ui.test.mjs
- test_xau_reset_window_a.py
- test_xau_two_stop_a.py
- test_fxcm_usoil_5s_integrated.py
- QG Chart Workstation
- calculation-cache.test.mjs
- candle-color.test.mjs
- Deterministic Output Equivalence
- Explicit Rule Approval
- One Writer Per Write Surface
- test_a_pipeline.py
- test_s_pipeline.py
- test_e_pipeline.py
- TradingBot UI UX Design Rules
- browser-compat.test.mjs
- calculation-progress-info.test.mjs
- drawing-vertex-path.test.mjs
- Git Workflow
- __backup_20260904-010128/test_user_verified_ranges.py
- calculateIndicator
- test_bullish_leg_review.py
- Bullish leg continuation handoff
- Verified bullish leg ownership
- test_s_gate_order.py
- BULLISH_LEG_RULE_AMENDMENT_20260907.md

## God Nodes (most connected - your core abstractions)
1. `EDetector` - 44 edges
2. `EDetector` - 43 edges
3. `SDetector` - 38 edges
4. `SDetector` - 38 edges
5. `candle()` - 34 edges
6. `UnifiedReactionDetector` - 28 edges
7. `UnifiedReactionDetector` - 26 edges
8. `Candle` - 25 edges
9. `Candidate` - 25 edges
10. `Candle` - 25 edges

## Surprising Connections (you probably didn't know these)
- `Lightweight Charts Workstation` --conceptually_related_to--> `Python Calculation Authority`  [INFERRED]
  AI-Directories/PROJECT_MAP.md → AGENTS.md
- `Maintain Indicator Pipeline Skill` --implements--> `Reaction Blue Line A S E StopAll Pipeline`  [EXTRACTED]
  .agents/plugins/tradingbot-intelligence/skills/maintain-indicator-pipeline/SKILL.md → AGENTS.md
- `Optimization Summary` --references--> `Deterministic Output Equivalence`  [INFERRED]
  OPTIMIZATION_SUMMARY.md → SPEED_CODING_RULES.md
- `User Working Rules` --references--> `Explicit Rule Approval`  [INFERRED]
  AI-Directories/USER_WORKING_RULES.md → .agents/plugins/tradingbot-intelligence/skills/learn-trading-rule/SKILL.md
- `synthetic_owner_regression()` --calls--> `candle()`  [INFERRED]
  indicator/Modules/1_reaction-detector/app/__backup_20260904-010128/test_user_verified_ranges.py → indicator/Modules/4_S-zones/tests/test_s_ownership.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Deterministic Indicator Pipeline** — tradingbot_pipeline_reaction_blue_a_s_e_stopall, tradingbot_python_calculation_authority, tradingbot_decimal_strict_comparisons, docs_algorithms_bullish_indicator_algorithm_overview [EXTRACTED 1.00]
- **TradingBot Documentation Governance** — agents_overview, ai_directories_readme_overview, ai_directories_current_handoff_overview, ai_directories_project_map_overview [EXTRACTED 1.00]
- **Application Entry Shells** — lightweight_charts_index_qg_chart_workstation, lightweight_charts_index_app_mount, lightweight_charts_index_main_module [INFERRED 0.85]
- **Manual Review Presentation Flow** — lightweight_charts_tests_manual_review_browser_reviewfixture, lightweight_charts_tests_manual_review_browser_rendermanualreview, lightweight_charts_tests_manual_review_browser_indicator_review_iframe [INFERRED 0.85]
- **Chart and Candle Validation** — tradingbot_chart_workstation, tradingbot_raw_candle_inventory, tradingbot_asia_tehran_timezone, lightweight_charts_manual_test_overview [INFERRED 0.85]

## Communities (67 total, 9 thin omitted)

### Community 0 - "app/Reaction-detection-new.py"
Cohesion: 0.05
Nodes (61): BearishDetector, build_argument_parser(), build_report(), BullishDetector, Candidate, Candle, choose_range_interactively(), classify_candle_color() (+53 more)

### Community 1 - "__backup_20260904-010128/Reaction-detection-new.py"
Cohesion: 0.05
Nodes (61): BearishDetector, build_argument_parser(), build_report(), BullishDetector, Candidate, Candle, choose_range_interactively(), classify_candle_color() (+53 more)

### Community 2 - "candle"
Cohesion: 0.08
Nodes (51): ACase, Case, final_visible_a_zones(), load_module(), main(), project_path(), Path, Candidate timing must mirror strictly around the order box boundary. (+43 more)

### Community 3 - "main.js"
Cohesion: 0.03
Nodes (58): beginColorDrawingHistory(), calculationStageDescriptions, canvas, chart, chartElement, chartSettingInputs, chartSettings, chartSettingsDefaults (+50 more)

### Community 4 - "EDetector"
Cohesion: 0.09
Nodes (29): _CrossIndex, _d(), detect_e_zones(), EDetector, EZone, datetime, Decimal, OrderMatch (+21 more)

### Community 5 - "EDetector"
Cohesion: 0.08
Nodes (30): _CrossIndex, _d(), detect_e_zones(), EDetector, EZone, datetime, Decimal, OrderMatch (+22 more)

### Community 6 - "SDetector"
Cohesion: 0.11
Nodes (21): _decimal(), detect_s_zones(), datetime, Exact S detection over authoritative Reaction and A output., Return A objects whose source candle is not occupied by a final S., Return the directional extreme, assigning equality to the last candle., Find the aligned reaction after the A stop. In the pre-order candidate case the…, Use the inclusive order-Break to aligned-Break interval. (+13 more)

### Community 7 - "SDetector"
Cohesion: 0.11
Nodes (21): _decimal(), detect_s_zones(), datetime, Exact S detection over authoritative Reaction and A output., Return A objects whose source candle is not occupied by a final S., Return the directional extreme, assigning equality to the last candle., Find the aligned reaction after the A stop. In the pre-order candidate case the…, Use the inclusive order-Break to aligned-Break interval. (+13 more)

### Community 8 - "test_e_rules.py"
Cohesion: 0.07
Nodes (54): parametrize, Isolated accepted-order inputs exercise E ownership, not Reaction discovery., scenario(), test_e_owns_joint_stop_over_later_same_family_s(), test_older_single_red_s_owns_joint_stop_over_nested_blue_e(), test_stopall_reset_preserves_order_child_but_restarts_e_numbering(), test_unstopped_red_s_does_not_recolor_nested_blue_e(), parametrize (+46 more)

### Community 9 - "backend/reaction_bridge.py"
Cohesion: 0.07
Nodes (52): _a_zones_for_module_engines(), blocked_orders_while_invalid_leg_heads_are_live(), build_candle_buckets(), build_candle_objects(), build_candle_views(), build_candles(), bullish_a_stop_order_finder(), decimal() (+44 more)

### Community 10 - "manual-review.js"
Cohesion: 0.11
Nodes (42): buildInfoPayload(), buildReviewBody(), causeObject(), collections, colorSpec, detail(), escapeHtml(), eventCard() (+34 more)

### Community 11 - "vite.config.js"
Cohesion: 0.06
Nodes (31): aEnginePath, blueEnginePath, bridgePath, cacheSegment(), calculationId(), calculationMetadata(), calculationPath(), calculationsDir (+23 more)

### Community 12 - "__backup_20260904-010128/reaction_bridge.py"
Cohesion: 0.10
Nodes (36): build_candle_buckets(), build_candle_objects(), build_candle_views(), build_candles(), decimal(), emit_progress(), epoch(), load_engine() (+28 more)

### Community 13 - "startCalculationProgress"
Cohesion: 0.14
Nodes (20): updateStageAggregate(), calculationStageDescription(), calculationStageKey(), calculationStageTitle(), calculationTraceAggregates(), errorLogText(), escapeHtml(), eventDetails() (+12 more)

### Community 14 - "renderObjectTree"
Cohesion: 0.11
Nodes (29): drawingArray(), normalizeHistorySnapshot(), appearancePopup(), changeStyle(), closeUniversalColorPicker(), colorControlTrigger(), historySnapshot(), indicatorOverrideKey() (+21 more)

### Community 15 - "ADetector"
Cohesion: 0.22
Nodes (9): ADetector, AZone, BlueState, _decimal(), detect_a_zones(), datetime, Exact A detection over authoritative Reaction and Blue Line output., Return the exact strict Reset event that makes a Reset Blue exist. (+1 more)

### Community 16 - "ADetector"
Cohesion: 0.22
Nodes (9): ADetector, AZone, BlueState, _decimal(), detect_a_zones(), datetime, Exact A detection over authoritative Reaction and Blue Line output., Return the exact strict Reset event that makes a Reset Blue exist. (+1 more)

### Community 17 - "indicator-interaction.test.mjs"
Cohesion: 0.08
Nodes (3): section(), source, visibilityHarness()

### Community 18 - "ui-state.test.mjs"
Cohesion: 0.12
Nodes (8): CHART_TIMEFRAME_KEY, indicatorControlId(), restoredTimeframe(), drawing, harness(), indicator, section(), source

### Community 19 - "loadFile"
Cohesion: 0.13
Nodes (23): aggregate(), exportChartData(), fmt(), focusObjectOnChart(), inventorySignature(), loadFile(), loadInventory(), materialIcon() (+15 more)

### Community 20 - "drawAll"
Cohesion: 0.14
Nodes (18): applyChartSettings(), cancelDrawingTool(), checkpoint(), clampToolbarPosition(), drawAll(), drawIndicatorSelection(), finishDraft(), formatChartAxisTime() (+10 more)

### Community 21 - "package.json"
Cohesion: 0.10
Nodes (19): lightweight-charts, dependencies, lightweight-charts, description, devDependencies, playwright-core, vite, keywords (+11 more)

### Community 22 - "Reaction Blue Line A S E StopAll Pipeline"
Cohesion: 0.15
Nodes (19): TradingBot Agent Instructions, Analyze TradingBot Chart Skill, Develop Chart Workstation Skill, Maintain Indicator Pipeline Skill, Validate Candle Data Skill, Current Handoff, Data and Generated Output Policy, TradingBot Project Map (+11 more)

### Community 23 - "drawIndicator"
Cohesion: 0.13
Nodes (21): constrainLinePoint(), dash(), distSeg(), drawIndicator(), drawOne(), handle(), hitTest(), indicatorHitTest() (+13 more)

### Community 24 - "__backup_20260904-010128/blue_line.py"
Cohesion: 0.26
Nodes (15): BlueLine, count_scale_strikes(), detect_blue_lines(), fibonacci_level(), _intrabar_pending_confirmation(), _is_color(), _main_candle(), datetime (+7 more)

### Community 25 - "StopAllDetector"
Cohesion: 0.28
Nodes (7): _d(), detect_stopalls(), datetime, Decimal, StopAll detection over authoritative S/E output., StopAll, StopAllDetector

### Community 26 - "StopAllDetector"
Cohesion: 0.28
Nodes (7): _d(), detect_stopalls(), datetime, Decimal, StopAll detection over authoritative S/E output., StopAll, StopAllDetector

### Community 27 - "test_stopall_rules.py"
Cohesion: 0.23
Nodes (15): load_bridge(), load_stopall(), Reusing the reconciled detector must not inherit its previous order ledger., run_strict_bullish_range(), test_clarified_range_continues_after_stopall_with_exclusive_labels_and_order_causes(), test_clarified_red_transition_requires_order_confirmation_inside_to(), test_full_file_dominant_e_blocks_early_s_and_preserves_stopall_lineage(), test_red_e_family_always_dominates_blue_regardless_of_number() (+7 more)

### Community 28 - "test_directional_symmetry.py"
Cohesion: 0.28
Nodes (15): load(), pipeline(), plain(), parametrize, Cross-stage price/role reflection against the maintained bullish rules. Family…, reflect_candles(), reflect_payload(), reflected() (+7 more)

### Community 29 - "openIndicator"
Cohesion: 0.19
Nodes (15): applyIndicatorForm(), applyPinnedPanelWidth(), chartWorkspaceActive(), closeSidePanel(), commitIndicatorRangeInputs(), displayPickerValue(), ensurePanelResizeHandle(), inputFromTehran() (+7 more)

### Community 30 - "Start-TradingBot.ps1"
Cohesion: 0.36
Nodes (9): Ensure-NpmDependencies(), Ensure-Path(), Ensure-ProjectFiles(), Ensure-Runtimes(), Find-Command(), Install-Winget(), Refresh-Path(), Start-DevServer() (+1 more)

### Community 31 - "test_xau_pre_order_blue_s.py"
Cohesion: 0.53
Nodes (9): epoch(), skipif, Regression for the user-confirmed XAUUSD pre-order Blue S., run_bullish_window(), test_bullish_pre_order_candidate_becomes_blue_s(), test_full_file_preserves_verified_half_leg_behaviors(), test_stopped_dominant_s_advances_lifecycle_without_hiding_half_leg_a(), test_stopped_s_parent_remains_visible_when_it_builds_e() (+1 more)

### Community 32 - "renderChartViewport"
Cohesion: 0.31
Nodes (8): buildCandleLod(), chooseLodStride(), lowerBoundTime(), renderChartViewport(), scheduleChartViewport(), sourceCandleAt(), viewportIndexRange(), candles

### Community 33 - "__backup_20260904-010128/test_reaction_detection_new.py"
Cohesion: 0.28
Nodes (7): chart_doji_regression(), Independent test reflection; does not call production mirror helpers., Use real OHLC classification, including dojis, without historical input., Compare complete outputs and geometry, not only event counts., reference_mirror_candles(), reference_mirror_regression(), reflected_result()

### Community 34 - "app/test_reaction_detection_new.py"
Cohesion: 0.28
Nodes (7): chart_doji_regression(), Independent test reflection; does not call production mirror helpers., Use real OHLC classification, including dojis, without historical input., Compare complete outputs and geometry, not only event counts., reference_mirror_candles(), reference_mirror_regression(), reflected_result()

### Community 35 - "candle-export.js"
Cohesion: 0.52
Nodes (6): $id(), initCandleExport(), markup(), request(), timeframeLabel(), VALIDATION_CHECKS

### Community 36 - "manual-test-handoff.test.mjs"
Cohesion: 0.43
Nodes (5): calculationInfoPath(), openManualReviewTab(), calculation, entrySource, viteSource

### Community 37 - "Manual Review Presentation Test"
Cohesion: 0.33
Nodes (7): Indicator Review Iframe, Presentation Test Inline Module, Manual Review Presentation Test, Presentation-Only Test Isolation, renderManualReview, reviewFixture, Synthetic Presentation Fixture

### Community 38 - "test_bearish_30s_bridge.py"
Cohesion: 0.53
Nodes (5): epoch(), skipif, User-approved A/S acceptance through the complete maintained bridge., test_confirmed_bearish_a_to_s_ownership(), test_xau_bullish_visual_blue_a_type3_and_red_s()

### Community 39 - "vite-dev.mjs"
Cohesion: 0.33
Nodes (5): args, child, debug, inputArgs, vite

### Community 40 - "candle-export-ui.test.mjs"
Cohesion: 0.33
Nodes (5): api, appCss, main, ui, vite

### Community 41 - "test_xau_reset_window_a.py"
Cohesion: 0.50
Nodes (4): epoch(), skipif, Bridge acceptance for the verified XAUUSD Reset-window A correction., test_bearish_reset_windows_remove_early_a()

### Community 42 - "test_xau_two_stop_a.py"
Cohesion: 0.50
Nodes (4): epoch(), skipif, Regression coverage for ordinary and special two-Blue-stop A ownership., test_bullish_two_stop_a_ownership_and_source_range()

### Community 43 - "test_fxcm_usoil_5s_integrated.py"
Cohesion: 0.50
Nodes (4): load(), main(), Path, Integrated Reaction -> Blue -> A -> S -> E smoke test for the supplied USOIL…

### Community 44 - "QG Chart Workstation"
Cohesion: 0.50
Nodes (5): Application Mount Element, Workstation Application Shell, Google Fonts Resources, Main Application Module, QG Chart Workstation

### Community 45 - "calculation-cache.test.mjs"
Cohesion: 0.40
Nodes (3): config, files, request

### Community 46 - "candle-color.test.mjs"
Cohesion: 0.40
Nodes (4): end, library, select, start

### Community 47 - "Deterministic Output Equivalence"
Cohesion: 0.50
Nodes (4): Optimize Indicator Pipeline Skill, Optimization Summary, Speed Coding Rules, Deterministic Output Equivalence

### Community 49 - "Explicit Rule Approval"
Cohesion: 0.67
Nodes (3): Learn Trading Rule Skill, User Working Rules, Explicit Rule Approval

### Community 50 - "One Writer Per Write Surface"
Cohesion: 0.67
Nodes (3): Native Agent Orchestration, Concurrent Codex Protocol, One Writer Per Write Surface

### Community 59 - "__backup_20260904-010128/test_user_verified_ranges.py"
Cohesion: 0.29
Nodes (17): ACase, Case, final_visible_a_zones(), load_module(), main(), project_path(), Path, Candidate timing must mirror strictly around the order box boundary. (+9 more)

### Community 61 - "calculateIndicator"
Cohesion: 0.14
Nodes (17): applyVisualSettings(), calculateIndicator(), calculationKey(), captureIndicatorForm(), clone(), createUniqueId(), indicatorSettings(), indicatorStateKey() (+9 more)

### Community 62 - "test_bullish_leg_review.py"
Cohesion: 0.26
Nodes (13): fixture, bullish(), epoch(), matching_rows(), parametrize, Acceptance requirements from the user's evolving bullish leg lesson. Historical…, Order_B is a formation cause, not merely Reaction mode B., Requested behaviors are valid; rejected candidates never reach output. (+5 more)

### Community 63 - "Bullish leg continuation handoff"
Cohesion: 0.25
Nodes (7): Bullish leg continuation handoff, Completed continuation work, Confirmed user rules, Current acceptance state, Current implementation already present, Maintenance checks, Scope and authority

### Community 64 - "Verified bullish leg ownership"
Cohesion: 0.33
Nodes (5): Confirmed chronology, Ownership rules, Scope, Verification contract, Verified bullish leg ownership

### Community 65 - "test_s_gate_order.py"
Cohesion: 0.40
Nodes (3): parametrize, S order ownership must follow exact events, not rounded candle timestamps., test_only_the_confirmation_that_stops_a_opens_the_new_order_context()

## Knowledge Gaps
- **132 isolated node(s):** `name`, `version`, `description`, `private`, `test` (+127 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `drawAll()` connect `drawAll` to `openIndicator`, `drawIndicator`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _132 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app/Reaction-detection-new.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05261336102457598 - nodes in this community are weakly interconnected._
- **Should `__backup_20260904-010128/Reaction-detection-new.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05426774483378257 - nodes in this community are weakly interconnected._
- **Should `candle` be split into smaller, more focused modules?**
  _Cohesion score 0.07950310559006211 - nodes in this community are weakly interconnected._
- **Should `main.js` be split into smaller, more focused modules?**
  _Cohesion score 0.029860434923726063 - nodes in this community are weakly interconnected._
- **Should `EDetector` be split into smaller, more focused modules?**
  _Cohesion score 0.08504504504504505 - nodes in this community are weakly interconnected._