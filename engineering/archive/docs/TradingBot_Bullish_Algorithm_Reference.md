# TradingBot Bullish Algorithm Reference

Evidence date: 2026-09-18  
Authority: current working-tree implementation under `engine/bridge` and `engine/pipeline`  
Direction: Bullish market semantics, with opposite-direction Orders where required

## 1. Status and Version Set

This reference describes the active implementation, not only the committed `HEAD`. The current launcher and Vite backend point to untracked replacement engine modules while tracked legacy modules are deleted. Until those user-owned changes are committed, a fresh checkout does not reproduce the runtime documented here.

| Component | File | Version |
|---|---|---:|
| Pipeline bridge | `engine/bridge/trading_pipeline.py` | `1.2.2` |
| Reaction | `engine/pipeline/reaction_engine.py` | `9.5.2` |
| Blue Line | `engine/pipeline/blue_line_detector.py` | `2.3.0` |
| A | `engine/pipeline/a_zone_detector.py` | `1.6.3` |
| S | `engine/pipeline/s_zone_detector.py` | `4.13.1` |
| E | `engine/pipeline/e_zone_detector.py` | `6.6.2` |
| StopAll/lifecycle | `engine/pipeline/lifecycle_engine.py` | `1.10.1` |
| Direction policy | `engine/pipeline/direction_policy.py` | `1.0.0` |
| Shared utilities | `engine/pipeline/core_utils.py` | `1.0.0` |

The older documents under `engine/algorithms/*V4.0.1.md` are historical snapshots. They describe older versions and removed range-isolation helpers, so they are not a standalone specification of the current runtime.

## 2. Runtime Contract

The public entry point is `engine/bridge/trading_pipeline.py`. Its required inputs are the engine module paths, RAW candle JSON, positive integer timeframe, `from`/`to` epochs, and direction. The Vite endpoint `/api/reactions` always supplies the current Reaction, Blue, A, S, E, and lifecycle modules. A full-chart request supplies the original RAW path. A partial request supplies only source rows in the inclusive selected chart-candle buckets through a Windows named pipe, without writing another RAW file.

The RAW JSON must be an array whose rows contain `time`, `open`, `high`, `low`, and `close`. The bridge:

1. reads the complete supplied input (original RAW file or an in-memory range stream);
2. removes an optional UTF-8 BOM;
3. aggregates consecutive identical timestamps into lower candles;
4. aggregates main candles into epoch-aligned `floor(timestamp / timeframe) * timeframe` buckets;
5. calculates against the entire supplied input; for a partial application request, that input contains no data outside the selected chart-candle range;
6. applies `from`/`to` only when deciding which public objects are visible.

The bridge does not sort rows, fill missing intervals, globally deduplicate timestamps, or independently validate OHLC relationships. Those integrity guarantees belong to the RAW storage boundary and validation tooling.

All public indexes and ordinals retain identity relative to the complete supplied input. Through `/api/reactions`, a partial request supplies only the selected source rows, so its identities restart inside that range and its results cannot depend on observations outside it. A direct bridge caller that supplies a full file while using narrower `from`/`to` presentation bounds retains the bridge's full-input identity and dependency behavior.

## 3. Shared Numerical and Time Semantics

- Price calculations use `Decimal(str(value))` after JSON parsing.
- Timezone interpretation is `Asia/Tehran`; public epochs are integer seconds.
- Public prices are strings. Indexes and times are integers. Unavailable metadata is `null`.
- A market candle is `GREEN` when `Open <= Close`, including doji; otherwise it is `RED`.
- Bullish strict crossings use `Low < level` for stops and `High > level` for upward confirmations. Equality does not stop or confirm.
- Lower-timeframe windows are half-open `[start, end)` unless a stage explicitly includes an aligned boundary.
- If no strict lower-timeframe confirmation is found, chronology can fall back to the Break candle open.
- Equal extrema normally retain the earliest lower position. Some S source-selection paths explicitly assign equality to the latest main candle.

`MarketChronology` is the shared authority for lower windows, exact confirmation/reset events, main-index mapping, and canonical Order stops. The production bridge normally computes both market directions because Bullish S/E decisions require Bearish Reaction and Reset geometry.

## 4. Pipeline Order

The effective Bullish calculation flow is:

```text
complete supplied input
  -> Bullish + Bearish Reaction/Reset context
  -> Bullish Blue Lines
  -> Bullish A zones
  -> Bullish S zones
  -> Bullish E initial detection
  -> S eligibility and A/S ownership reconciliation
  -> E final-audit rebuild
  -> shared Order-stop reconciliation
  -> optional E continuation reconstruction
  -> single lifecycle/StopAll reconciliation
  -> visibility, lineage closure, internal filtering, serialization
```

E detection can execute two to four times for one requested direction. StopAll reconciliation is a single pass; there is no current E/StopAll fixed-point loop.

## 5. Bullish Reaction and Reset

### 5.1 Initial Mode A candidate

`BullishDetector.detect` establishes the initial Bullish geometry from a GREEN context followed by a RED First candle. It freezes the Bullish leg floor/anchor, derives `BoxTop` from the context/First maximum, evolves `BoxBottom`, and confirms only on a strict `High > BoxTop` breakout.

Before confirmation, a strict owner invalidation rejects the candidate. When invalidation and confirmation occur on the same lower candle, invalidation wins for unresolved direct candidates.

### 5.2 Normal Mode B discovery

After a confirmed Reaction, Mode B searches from the running Bullish peak for a new RED First. The new candidate retains the relevant outer boundary and must strictly confirm upward. `_append_reaction` records the opposite edge from the complete First-through-Break main-candle span.

Calculation geometry and published geometry are distinct. `published_reaction_candidate` can truncate a displayed edge at the first exact lower-timeframe confirmation when the Break candle owns that edge; downstream calculations continue to use the authoritative calculation geometry.

### 5.3 Bullish Reset

A Bullish Reset is a strict `Low` break of the prior confirmed Bullish bottom. Equality is not a Reset. Post-Reset direct discovery searches the same requested direction; an opposite-direction candidate alone does not unlock ordinary Bullish post-Reset discovery.

`_first_direct_same_direction_after_reset`, `_build_direct_candidate`, and `_scan_direct_candidate` preserve the Reset-to-First outer boundary and enforce the context/First color and local-floor alignment rules. Direct Order discovery is a separate geometry path: overlapping candidates may exist, and the earliest confirmation wins, then earliest First for a tie.

In initial and post-Reset same-Break branches, the Bullish path uses the analyzed extreme as its Reset reference. This differs from the corresponding Bearish path and must not be normalized without a specification change and regression evidence.

## 6. Bullish Blue Lines

`detect_blue_lines` and `count_scale_strikes` use an exact Fibonacci ratio of `0.618`.

For a Bullish Reaction:

```text
Blue level = top - 0.618 * (top - reference)
```

- Mode A uses its anchor/leg boundary and resets the prior strike count.
- Mode B references the preceding Reaction's opposite box edge.
- New directional extremes create pending strikes.
- A GREEN candle confirms a Bullish pending strike.
- A pending final strike can use lower chronology through the Break candle.
- A Scale Blue requires a strike count strictly greater than the preceding Reaction and at least one intervening healthy Reaction after an earlier Blue.
- Scale drawing price is `Low + candle_range / 3`.
- Reset drawing price is `Low + candle_range / 5`.
- The rendered span is source time plus/minus one main timeframe.

A same-index double-stop Reset Blue can remain as special A evidence while carrying `calculation_valid=False`. `mark_internal_blue_lines` marks Blue geometry owned by an internal Reaction or whose semantic source extreme and rendered line are strictly inside a healthy Reaction. `public_blue_lines` removes invalid/internal display lines, but calculation dependencies can remain.

## 7. Bullish A Zones

`AZoneDetector` constructs chronologically formed Blue states. The Blue `source_extreme`, not its rendered line, is the stop level.

- Scale Blue stop scanning begins at the exact Reaction confirmation.
- Reset Blue stop scanning begins after the complete source candle.
- A Blue pair expires when the next Blue forms.
- `_pair_trigger` resolves inherited-stop geometry, stops before current formation, and simultaneous stops.
- `_inherited_stop` can freeze the full stop-candle through aligned Break-candle Bullish extreme.
- `_a_source` freezes the Bullish extreme from trigger-candle open through the exact confirming Reaction event, inclusive. Later Break-candle values cannot move the A source.
- `_double_stop_a_candidates` consumes special invalid Reset Blue evidence.
- `_filter_special_a` resolves conflicts and Blue-pair consumption.

Equal extrema normally belong to the earliest event. Same-event Blue stops are ordered by their directional stop levels. Under explicit reuse conditions, an ordinary cycle may reuse adjacent Blue provenance after the first strict A stop.

## 8. Bullish S Zones

`SZoneDetector` audits stopped A independently before deciding S ownership.

### 8.1 Opposite Order selection

For a Bullish parent, `_first_order_after` selects a Bearish canonical Order whose First is at or after the main candle containing the A stop and whose confirmation is strictly after the A stop. Ranking is confirmation event, First index, then Break index.

The Simple pre-Order window runs from the A-stop remainder through Order First. Equality with Order First remains chronologically after the pre-Order window. Advanced ownership requires a nested Bullish Reaction inside the Bearish Order; this prevents Simple chronology from stealing an already established nested owner.

### 8.2 S source and decision

- Simple post-Order source spans the Order Break through the aligned Bullish Reaction Break, inclusive.
- Ordinary `_candidate_source` keeps the earliest equal Bullish extreme.
- `_candidate_source_last` assigns equal extrema to the latest candle for Simple Blue and Type3 Reset-leg geometry.
- If the Bearish Order strictly stops first, S is Red.
- If the qualified Bullish candidate crosses first, S is Blue.
- A same-finest-candle dual crossing produces no decision.
- A Blue decision requires aligned Reset Blue evidence or ordinary Bullish trend confirmation; pre-Order discovery may fall back to post-Order discovery.

Type3 is an Order-free Blue S. It requires an active pre-A-stop Bearish Reaction, a later Bearish Reset, a strict Break-to-Reset boundary cross, aligned Bullish trend confirmation, and completion before the next Order confirmation deadline.

`_a_owned_by_s` implements lineage handoff plus fresh-trigger and fresh Reset/Reset pair exceptions. `reconcile_shared_order_stops` may convert an existing S to Red when a later accepted physical Order stops earlier than its previous decision. The S source remains frozen.

## 9. Bullish E and Order Lifecycle

`EZoneDetector` separates native chain detection, reconciliation, and accepted audit rebuilding.

### 9.1 Order creation and identity

Orders arise from `parent-stop`, `reset-leg`, or `carried-live` paths. Physical identity is `(FirstIndex, BreakIndex)`; causes sharing that geometry merge.

- Mode A Order stop is the complete anchor/context-through-Break directional outer extreme.
- Mode B inherits the preceding healthy opposite Reaction edge through `MarketChronology.canonical_order_stop`.
- A Reset-leg Order_B requires actual Bearish Reset context, the inclusive Break-to-Reset boundary, a strict boundary cross, noninternal aligned Bullish trend evidence, the first structurally owned Bearish geometry, and an exact published Bearish Reaction identity.
- A Bullish trend Reset does not release an opposite owner.
- Deadlines are bounded by the next nonnested outer Reset and current stop/decision chronology.

Narrow direct Order_A exceptions are allowed only for bounded `continue` geometry: S-to-E continuation and E continuation after a newly confirmed noninternal trend leg. A noncanonical accepted geometry uses Reaction number `0`; it does not relax Reset-leg canonicality.

### 9.2 E construction and reconciliation

`_zone` selects one representative for each direct/inherited/carried path and then the earliest Order stop; a tie favors the later Order First. E source uses the complete main candles containing the parent stop through the Order stop and keeps the earliest equal Bullish extreme.

An E chain ends when there is no next Order/stop or a source index repeats. There is no configured numeric recursion depth.

Reconciliation gives priority to accepted parent ownership and chronology. For the same physical E source, Red outranks Blue, then the higher number within one family; an exact rank tie preserves existing provenance. An invalid S cannot open a competing cross-family root when that S source already owns a native E continuation. `restore_independent_s_roots` can restore an eligible direct E1 after dominant StopAll arbitration, except when the S source is already E-owned.

## 10. StopAll and Visibility

Lifecycle priority is direction-independent:

```text
StopAll > E Red > S Red > E Blue > S Blue
```

`StopAllDetector.detect` groups repeated dominant S color or repeated E `(family, number)`. StopAll1 requires at least two group members, a strict group stop, and a qualifying later E decision. When an active StopAll strictly stops and a qualifying E follows, the next StopAll number is the highest stopped number plus one.

Lower-priority events at distinct sources can remain visible but do not split the dominant group. StopAll inherits the decisive E geometry and Order. Final public E is removed at the same source as the StopAll.

Final visibility then:

1. removes A sources occupied by S and applies S-transition filtering;
2. reconciles StopAll once;
3. restores eligible independent S-owned E1 roots;
4. restores required historical A/S lineage;
5. applies source-index display windows;
6. removes invalid A/S;
7. marks nonpublic Blue geometry;
8. blocks internal Reset-leg Mode-B E/StopAll ownership;
9. serializes merged accepted OrderAudit identities.

Internal geometry is not universally discarded. The explicit public prohibition concerns internal Mode-B Reset-leg ownership. Mixed-cause OrderAudit and public E filtering currently use unequal predicates and should be treated as a known risk.

## 11. Public Bullish Payload

The envelope identifies all engine versions, enable flags, timeframe, actual visible bounds, direction objects, and timing phases. `directions.bullish` always contains:

`reactions`, `resets`, `blueLines`, `aZones`, `sZones`, `eZones`, `stopAlls`, and `orderAudit`.

Important identity fields include Reaction First/Break indexes, Blue source index, A Blue provenance, S parent A and complete Order provenance, E parent and Order cause, StopAll gate/stopped behavior, and OrderAudit physical geometry plus merged causes. These fields are the stable basis for comparison; equal result counts alone do not establish parity.

Private calculation fields such as `behavior_internal`, internal anchors, native invalid-state flags, and some gate-decision objects are not generally serialized.

## 12. Invariants for Future Changes

- Keep Python authoritative; do not reproduce decisions in browser code.
- Preserve full-RAW identities and apply ranges only to presentation.
- Do not hardcode timestamps, OHLC values, file identities, fixtures, or expected outputs into runtime logic.
- Preserve strict crossing semantics; equality changes are behavioral changes.
- Preserve independent Bullish/Bearish decisions and the lifecycle priority ordering.
- Preserve source, parent, Order, cause, ordinal, version, and `orderAudit` provenance.
- Validate protected arrays, ordering, version fields, and stable hashes; counts are insufficient.
- Treat missing lower chronology separately from an algorithm failure.
- Do not infer exact Bullish/Bearish mirroring where the source contains explicit asymmetry.

## 13. Current Known Risks

1. `engine.pipeline` package import fails because `__init__.py` exports absent `run_blue_line`; production dynamic loading bypasses it.
2. the Vite calculation fingerprint omits `direction_policy.py` and `core_utils.py`, allowing stale cache reuse after changes there;
3. Reaction infers timeframe from early main timestamps while downstream chronology uses the requested timeframe, which can diverge on sparse early data;
4. a lifecycle helper maps intrabar decision events with `bisect_left`, potentially choosing the next main candle;
5. StopAll updates `sequence_resets` without fully rebuilding all derived reset-time/audit state;
6. partially missing lower data can be trusted by some stages while other stages emit no event;
7. most searches use lifecycle boundaries or the full RAW end, so shortening the display range does not proportionally reduce calculation cost.

These are source-derived findings, not authorization to change the engine. Any correction requires a focused specification, deterministic fixtures, direction-specific validation, and zero-drift comparison outside the intended change.
