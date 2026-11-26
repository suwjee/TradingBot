# Phase 02 — Deep Static Analysis

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70` (latest TradingBot/main resolved at phase start). **Structural inventory: VERIFIED. Semantic and dynamic closure: PARTIAL.**

- [Completion report](Phase_02_Completion_Report.md)
- [Methodology and interpretation](Methodology.md)
- [Static analysis summary](Static_Analysis_Summary.json)
- [Function and class inventory](Function_Inventory.json)
- [Decision and control-event inventory index](Branch_Inventory.json)
- [Dependency graph](Dependency_Graph.md), [Call graph](Call_Graph.md), [Data flow and side effects](Data_Flow.md), [Reachability review](Dead_Code_Review.md)
- [Validation report](Validation_Report.json), [artifact hashes](SHA256SUMS.txt)

Per-module reports contain AST location metadata, scope IDs, branch outcomes, call sites and candidates, import references, access and mutation sites, class fields, operator kinds, return/raise/break/continue/yield events, scope-grouped def/use, conservative reaching writes, statement-level CFG and independently derived compiled block graph. No source bodies or executable tooling are included.

| Module report | Functions | Classes | Decision/control sites | Calls |
|---|---:|---:|---:|---:|
| [engine/__init__.py](__init__.json) | 0 | 0 | 0 | 0 |
| [engine/bridge/__init__.py](bridge____init__.json) | 0 | 0 | 0 | 0 |
| [engine/bridge/live_pipeline.py](bridge__live_pipeline.json) | 13 | 4 | 50 | 97 |
| [engine/bridge/trading_pipeline.py](bridge__trading_pipeline.json) | 102 | 10 | 552 | 1229 |
| [engine/pipeline/PL_PH_detector.py](pipeline__PL_PH_detector.json) | 46 | 15 | 214 | 267 |
| [engine/pipeline/__init__.py](pipeline____init__.json) | 0 | 0 | 1 | 4 |
| [engine/pipeline/a_zone_detector.py](pipeline__a_zone_detector.json) | 39 | 6 | 180 | 324 |
| [engine/pipeline/blue_line_detector.py](pipeline__blue_line_detector.json) | 18 | 4 | 106 | 196 |
| [engine/pipeline/core_utils.py](pipeline__core_utils.json) | 6 | 1 | 13 | 21 |
| [engine/pipeline/direction_policy.py](pipeline__direction_policy.json) | 6 | 1 | 7 | 6 |
| [engine/pipeline/e_zone_detector.py](pipeline__e_zone_detector.json) | 54 | 7 | 334 | 453 |
| [engine/pipeline/lifecycle_engine.py](pipeline__lifecycle_engine.json) | 46 | 5 | 286 | 595 |
| [engine/pipeline/order_audit_engine.py](pipeline__order_audit_engine.json) | 82 | 6 | 551 | 844 |
| [engine/pipeline/reaction_engine.py](pipeline__reaction_engine.json) | 107 | 22 | 555 | 590 |
| [engine/pipeline/s_zone_detector.py](pipeline__s_zone_detector.json) | 50 | 3 | 238 | 453 |
| [engine/pipeline/true_false.py](pipeline__true_false.json) | 7 | 1 | 46 | 41 |

Use Audit metadata for traceability, not as a dependency of standalone algorithms. Re-resolve main before Phase 03.
