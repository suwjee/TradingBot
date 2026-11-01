---
title: Bullish primary mirror implementation plan
document_role: evidence
lifecycle: historical
owner: engine-and-chart
created_at: 2026-11-01T17:42:36+03:30
last_modified_at: 2026-11-01T19:27:33+03:30
---

# Bullish primary mirror implementation plan

> Execute with the subagent-driven-development skill for independent primary/Chart tasks, with root integration and independent review. Do not stage, commit, push, release, or run Graphify.

**Goal:** Implement the user's approved bullish PL/PH/MBL mirror, PL3 reversal, isolated alternating regimes and mirrored Chart markers while preserving existing bearish rules.

**Architecture:** Reuse the existing exact primary state machine through a price-reflection adapter, preserving chronological decisions and native physical Order identity/provenance. Native OrderAudit adds symmetric confirmed-PL parent handling. The existing bridge owns fresh regime inputs and serialization; the Chart consumes finalized regime metadata and clips each historical regime independently.

**Tech stack:** Python Decimal and MarketChronology, existing Canvas Chart, pytest, Node test runner, Playwright/Chrome.

**Spec:** Current user teaching and the confirmed clarifications in this chat, summarized below; accepted References will receive this approved delta and exact current Source.

## Global constraints and spec

- In bullish primary calculation, StopAll3+ and the same exact dominant matching S/E pair precede strict Low below reference StopAll Low. MBL is maximum High from second behavior source through break main candle inclusive, frozen and exposed after the owning first PL confirmation.
- Primary bullish PL1/reset PL1 accepts conceptual bullish A/B Orders (physical bearish Reaction); PL2/3 accepts A. Opposite bullish PH1..3 accepts conceptual bearish A/B Orders (physical bullish Reaction). Preserve all mirrored native eligibility, timing gates, direct-A locking, tie, cancellation, ownership and independent-cycle rules.
- PL uses minimum inclusive main-candle Low through the winning Order stop; PH uses maximum High. Earliest equal extreme owns the source. Exact RAW event order and Decimal remain authoritative.
- Pending PL is cancelled by MBL break. Pending PH without a new confirmed PH since the latest PL is cancelled by breaking that PL Low. Confirmed PH resets local PL counting, while PH counting and MBL persist. No PH4. Post-PH3 Orders remain evidence.
- Final physical PL precedence mirrors PH: a strictly lower next confirmed physical PL continues at least the prior final number+1, even after local reset. Coincident roles retain the greater number. Stable identities and provenance survive relabeling.
- First strict stop of any confirmed final PL3 ends all bullish cycles and begins bearish calculation at the complete crossing main candle. No earlier input/state is carried. PH3 does the existing opposite transition. Repeated transitions use fresh contexts.
- Only the first Reaction of each newly started direction bypasses prior-leg/Reset context: bearish FirstGreen/BoxBottom mirrors bullish FirstRed/BoxTop. Ordinary Reset and downstream rules resume immediately after confirmation. Market Doji remains GREEN; S/E Blue/Red families do not swap.
- Bullish PL is a pink upward double chevron below Low, label below; bullish PH is a green circle above High, label above. Existing sizes/gaps: arrow12px, circle radius4px, label12px, candle-edge gap12px, marker-label gap10px. Preserve explicit appearance settings.
- MBL keeps the existing red dotted styling and max400 actual calculation candles, earlier strict break, fixed source/price, and per-regime historical end.
- Both trend-start icons remain 28x28 CSS pixels. Bearish start uses a red dashed full-height vertical line and red downward zigzag at actual candle50 counting start1, icon top500px below its Low. Bullish start retains the green boundary and upward zigzag, icon bottom500px above High. Actual bar count survives gaps; absent target omits icon.
- Preserve dirty user work; baseline byte snapshots are under ignored task scratch. No RAW mutation. No timestamp/fixture-specific production branches. English developer-facing content; Persian conversation.
- Keep standalone PH/PL/MBL concepts excluded from the Vault. Existing upstream retrieval remains bounded and does not override the new explicit teaching.

## Interfaces

- Primary: `detect_bullish(chronology,s_zones,e_zones,stopalls,orders)` returns `PrimaryResult(direction="bullish")` with real `.lows` PL and `.highs` PH; existing bearish APIs remain compatible. `resolve_primary_lows` mirrors `resolve_primary_highs`. `NativePrimaryOrders(..., direction="bullish", on_high=callback)` consumes real point kinds and calls the callback for the primary PL. Transition has target direction metadata; old positional construction remains supported.
- Audit: `register_primary_low` and `reconcile_primary_low_labels` mirror the existing high APIs without changing bearish behavior.
- Bridge: directional primary serialization with the same public arrays, `postPH3Orders` for bullish; existing bearish field retained. Transition emits direction/previousDirection, ph/pl provenance and target High/Low as appropriate.
- Regimes: each direction's aggregate payload may expose `calculationSegments`, a chronological list of complete same-direction payloads without nested segments. Chart renders each segment independently; aggregate arrays serve counts/object tree. A single segment keeps legacy shape. Initial `both` retains bearish precedence; explicit bullish starts bullish. Primary-disabled behavior stays unchanged.

## Review focus

1. Equality, earliest extrema, older-First compatible confirmation, opposite-event ties and direct-A locking.
2. Repeated regime boundaries, missing fifty candles, no prior-state leakage, stable absolute indexes/IDs and historical hit/selection clipping.
3. Bidirectional native parent causes, StopAll promotion, canonical physical membership, cause aliases and shared Order deduplication.
4. Fresh first bearish Reaction on GREEN/Doji and ordinary Reset immediately afterward.
5. Existing USOIL bearish anchors before its first reversal and independent direct bullish real-data evidence.

## Tasks

### 1. Primary and native OrderAudit mirror

Owners: `engine/pipeline/PL_PH_detector.py`, `engine/pipeline/order_audit_engine.py`, focused new/updated unit tests.

- [x] Write and witness failing bullish primary/native PL tests, then implement exact reflected behavior.
- [x] Verify mirrored extrema, eligibility, cycle/reset numbering, PH3 cap, PL3 transition, parent provenance and deterministic source ownership.
- [x] Run affected and existing primary/audit tests; self-review.

### 2. Chart mirrored symbols and regime rendering

Owners: `apps/chart/src/chart/primary-structure.js`, relevant portions of `apps/chart/src/main.js`, Chart unit tests.

- [x] Write failing marker/color/geometry/segment tests, then implement the approved shapes and both directional transition markers.
- [x] Render `calculationSegments` independently and preserve object settings, paint/hit/selection bounds and aggregate counts.
- [x] Run Chart suite/build and support browser verification.

### 3. Fresh bearish bootstrap and bridge regimes

Owners: `engine/pipeline/reaction_engine.py`, `engine/bridge/trading_pipeline.py`, context/bootstrap/serialization tests.

- [x] Write failing first bearish Reaction, bullish serialization and repeated isolation tests.
- [x] Wire directional primary/native parents; orchestrate fresh prefix/suffix regimes with independently supported transition provenance.
- [x] Verify disabled-primary compatibility, presentation horizons, offsets, unique stable IDs and additive output.

### 4. Integrated verification and synchronization

Owners: accepted References, task report and controlled delivery.

- [x] Run complete Engine/Chart suites, representative/full authoritative RAW, independent prefix/suffix comparisons, determinism and performance evidence.
- [x] Independently review changes and fix actionable findings with regression tests.
- [x] Synchronize both exact-source References and applicable maintained owner docs; check links/anti-drift.
- [x] Transfer only verified task files to live checkout with original-byte guards; confirm unchanged protected user files and live service source.

## Pre-flight ledger

| Tasks | Shared contract | Resolution |
|---|---|---|
| 1 / 3 | Directional primary result, callback, low resolver and native low APIs | Interfaces above; preserve bearish defaults and old positional construction. |
| 2 / 3 | `calculationSegments`, directional transition metadata, aggregate arrays | Flat chronological segments; Chart must never calculate a crossing. |
| 1 / 4 | Native source and reflected semantics in References | Regenerate Source blocks after owners finish; do not edit old evidence. |
| 2 / 4 | User-approved symbols and screen geometry | Defaults reflect samples, preserve explicit overrides; real browser verification. |
| 3 / 4 | Independent market/regime evidence | Fresh recomputation, historical output only as before-change evidence. |
| 1 | Tests vs implementation | No duplicate strategy; test general rules, strict limits and native causes. |
| 2 | Tests vs implementation | Shape/color depends on point kind, directional shape, same established controls. |
| 3 | Tests vs implementation | Fresh state per direction, complete boundary candle and absolute public indexes. |
| 4 | Evidence vs scope | Distinguish mirror parity from independent market validation. |

Ruling: `both` preserves the existing initial bearish precedence rather than choosing a new initial direction from prices. Explicit bullish requests start bullish. Repeated transitions alternate that initial regime; time never reverses.

Ruling: approved images change bullish PH circle to green and bullish PL chevrons to pink; colors follow point kind. Preserve existing named appearance controls and explicit per-object customization.

Ruling: use the maintained Engineering UI/UX Reference and accepted References as existing design context rather than introduce a duplicate root design document for these focused chart markers.

Baseline snapshots: `apps/chart/state/tmp/bullish-primary-mirror/before/`, `before.json`, `baseline-source/`, `live-before.json`. All pre-existing task changes remain intact; no Git mutation is required.

## Completion evidence

Engine242, Chart260, documentation31, build, both exact References, full anti-drift, complete RAW CLI/HTTP, independent fresh bullish/bearish input checks and Chrome geometry: PASS. Independent reviewers found two Chart/report regressions, both fixed with failing tests. Current user clarification is500px clearance and28px icon size. Guarded live transfer and current served28px/500px renderer verified; see delivery.json and live-acceptance.json.
