# Phase 03 — Fundamental computational contracts (V3.0)

**Status: IN PROGRESS — checkpoint 01.** Main baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Previous algorithm checkpoint: `74191a2c58f3960fbec12ffdbc786808a0cf37e3`.

## Phase 02 entry decision

Latest main and algorithm heads match the Phase 02 handoff. The Phase 02 structural inventory and conservative handoff are accepted for this phase. This does not close semantic dispatch, transitive aliasing or all-path feasibility. Preserve the prior 596 name-only candidate rows and other unresolved semantic dependencies for per-function review. No new runtime gate is introduced. See [Phase 02 closure](../Phase_02/Source_Only_Closure/README.md) and [active scope](../Source_Only_Scope.md).

## Checkpoint 01 deliverables

| Foundation | Evidence / status |
|---|---|
| Numerical and price representation | [N01–N06](../../Specification/02_Numerical_Precision.md), expanded; module arithmetic enumeration open |
| Time and chronology | [T01–T05](../../Specification/03_Chronology_And_Time_Model.md), expanded; event-order paths open |
| Candle, input and aggregation | [C01–C06](../../Specification/07_Candles_And_Market_Input.md), expanded |
| Index and cache primitives | [I01–I05](../../Specification/08_Range_Indexes_And_Caches.md), expanded; module-specific caches open |
| Core utilities | [existing source-derived contract](../../Specification/05_Core_Utilities.md), source rechecked |
| Direction primitives | [existing source-derived contract](../../Specification/06_Direction_Policy.md), source rechecked |
| Physical identity, provenance and numbering | Partial; detailed identity matrix pending |
| Model defaults, optionality, visibility and ownership | Partial; complete common field/schema matrix pending |
| Tie, fallback and error contracts | Partial; per-module shared-rule exceptions pending |

## Source traceability

The sole implementation authority is the pinned main source. File paths and lines are audit metadata, not implementation dependencies. Numeric-context screening used lexical matches, not proof against arbitrary alias/dynamic runtime effects.

| Rule IDs | Main source path and lines |
|---|---|
| N01 | engine/bridge/trading_pipeline.py:1930–1972; engine/bridge/live_pipeline.py:81–86; engine/pipeline/core_utils.py:51–54 |
| N02, C02, C05 | engine/bridge/trading_pipeline.py:140–205, 213–304 |
| N03 | engine/pipeline/direction_policy.py:31–54; engine/pipeline/reaction_engine.py:909–938, 973–1010; engine/bridge/trading_pipeline.py:140–185 |
| N04 | engine/pipeline/blue_line_detector.py:21–22, 77–84; engine/pipeline/reaction_engine.py:642–688, 1095–1118 |
| N05 | engine/pipeline/order_audit_engine.py:1644–1668, 1902–1958, 1989–1995 |
| N06 | engine/bridge/trading_pipeline.py:63–74, 396–438, 460–486, 1678–1730, 3661–3666 |
| T01 | engine/bridge/trading_pipeline.py:41–51, 100–138 |
| T02, T03 | engine/bridge/trading_pipeline.py:1815–1890, 1948–2030; engine/pipeline/reaction_engine.py:155–225, 1132–1199 |
| T04 | engine/pipeline/reaction_engine.py:1200–1308 |
| T05 | engine/bridge/trading_pipeline.py:1755–1777, 3594–3670; engine/pipeline/true_false.py:17–29 |
| C01, C03, C04, C06 | engine/bridge/trading_pipeline.py:140–205, 206–365, 1743–1754; engine/pipeline/reaction_engine.py:35–45, 140–145, 642–662 |
| I01–I03 | engine/pipeline/reaction_engine.py:884–1069 (cache cap at 32–33) |
| I04 | engine/pipeline/reaction_engine.py:172–183, 692–729, 1070–1167; engine/bridge/trading_pipeline.py:3671–3685 |
| I05 | engine/pipeline/core_utils.py:17–49; engine/pipeline/reaction_engine.py:203–229 |

## Remaining checkpoint work

Finish the shared identity and provenance rules; common data model fields/defaults and null/error semantics; module-specific foundational cache keys and ownership; visibility, tie and boundary matrix. Reconcile cross-document claims against the exact source and record remaining module-specific work under Phase 04 onward. No complete Phase 03 claim until those foundation gates are reviewed.

No RAW data was opened, no source module executed, no test or benchmark run. No production code changes. New documents are English. Prior historical analysis and verification evidence remains unchanged.
