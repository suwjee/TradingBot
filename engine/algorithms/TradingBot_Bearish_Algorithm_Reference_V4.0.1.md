# TradingBot Bearish Algorithm Reference

## 1. Metadata

Document-Name: TradingBot Bearish Algorithm Reference  
Document-Version: 4.0.1  
Filename: TradingBot_Bearish_Algorithm_Reference_V4.0.1.md  
Direction: Bearish  
Status: Canonical  
Language: English  
Source-Extraction-Authority: Production Python Source Code  
Specification-Type: Standalone Reimplementation Specification  
Price-Type: Decimal  
Main-Timeframe: Configurable integer seconds  
Lower-Timeframe-Authority: Original RAW Candles  
Timezone: Asia/Tehran  
Source-Baseline: trade_refactor_zero_diff_V4  

This document was reconstructed exclusively from the frozen production source files listed below. It does not depend on any older Algorithm Reference.

### Frozen source baseline

| Source file | Internal version | SHA-256 |
| --- | --- | --- |
| reaction_engine.py | 9.4.4 | `04699bda50ebeb7255053585046514ded90ceecaf88fe3530be95b06fc4a85bd` |
| direction_policy.py | 1.0.0 | `cd11e94fad148fba86da4661dd605dd673b129ca411830211df82abf325b0840` |
| blue_line_detector.py | 2.2.1 | `78f9a045852a4340f988adc239c2d85f4e4ded7c4ab2e8b151be5d95c7d61328` |
| a_zone_detector.py | 1.4.2 | `79af21f5236bd6da1027294593622e72f7c80ef1300a2f139fa0e8eaaa9cac1c` |
| s_zone_detector.py | 4.5.1 | `b891d22f98302cc5f07f238ae837c2565f6f28c216c28b7945f779d4c26c22b9` |
| e_zone_detector.py | 6.3.1 | `39e844cb5e25c2cbd27a089d373305fb56915b4852771b93badb0864b7bb5209` |
| lifecycle_engine.py | 1.3.1 | `3fe9e97c15de07f38c964a7f3a9dd0e7dfae7270c763ccd8ba47d7abd4bdeb16` |
| trading_pipeline.py | unversioned module; frozen by SHA-256 | `883f5f6fdcb9bc91c3f4075e8a78056cc21c9177fd7951ae98b5de78686e4b5e` |

### Normative status

This file is a standalone executable specification for the Bearish calculation engine. A correct reimplementation MUST be possible from this file alone. Source-origin labels are retained only for auditability; they are not external dependencies.


## 2. AI Interpretation Rules

1. MUST NOT infer an undocumented rule.
2. MUST NOT change any comparison operator.
3. MUST NOT invent a fallback, tie-break, or event order.
4. MUST use Original RAW Candles whenever exact chronology is required.
5. MUST NOT infer an intrabar OHLC path from a Main Candle.
6. MUST preserve exact source identifiers used in pseudocode.
7. MUST preserve control-flow order where the order changes results.
8. MUST treat documented exceptions as normative.
9. MUST report a contradiction instead of silently reconciling it.
10. Do not assume access to another Algorithm Reference. This requirement is mandatory.
11. Do not assume access to production source code. After this specification has been generated, source access MUST NOT be required for reimplementation.
12. MUST distinguish Calculation, Lifecycle, and Visibility.
13. MUST treat only A, S, E, and StopAll as behaviors.
14. MUST keep Doji GREEN in every direction and every adapter.
15. MUST preserve Decimal arithmetic for all calculation-sensitive price values.
16. MUST treat `Source-Origin` only as audit metadata; implementation MUST remain possible without source files.
17. MUST treat every `Rule-ID` block as normative, including its metadata contract and ordered body.
18. MUST use exact public/internal field semantics in Sections 19 and 28.1 when reconstructing state.


## 3. Specification Authority and Terminology

### 3.1 Extraction authority

The production Python source listed in Section 1 was the sole extraction authority for this document.

### 3.2 Reimplementation authority

After publication, this document itself contains the information required to reimplement the Bearish engine without source access.

### 3.3 Behavior terminology

The word **behavior** means only:

- A
- S
- E
- StopAll

The following are not behaviors:

- Reaction
- Reset
- Blue Line
- Order

### 3.4 Direction contract

The active `DirectionPolicy` for this document is:

| Field | Value |
| --- | --- |
| name | bearish |
| extreme_attr | high |
| opposite_extreme_attr | low |
| first_color | GREEN |
| context_color | RED |
| order_direction | bullish |
| is_bullish | False |

`DirectionPolicy.strict_cross(value, level)` is exactly:

```python
return value > level
```

`DirectionPolicy.improves(value, current)` is exactly:

```python
return value > current
```

Equality is therefore not a directional strict cross and does not improve an existing directional extreme.


## 4. Global Invariants

### INV-001 — Candle color

Status: Active  
Implementation-Class: Shared  
Source-Origin: `reaction_engine.classify_candle_color`

```python
return "GREEN" if open_price <= close_price else "RED"
```

A Doji (`open_price == close_price`) is always GREEN. Equivalently, `close == open` MUST classify as GREEN. Direction adapters MUST NOT rewrite `Candle.tag`.

### INV-002 — Decimal price arithmetic

All OHLC, Reaction boundaries, Fibonacci levels, Blue prices, A/S/E prices, Order stops, StopAll prices, and strict-cross levels are Decimal values. External numeric input is normalized with `Decimal(str(value))` or an equivalent exact decimal-string conversion. Binary floating-point arithmetic MUST NOT be introduced into price comparisons.

### INV-003 — Strict crossing

All directional stop/trigger rules use strict `<` or `>` as specified. Equality MUST NOT be treated as a crossing unless an explicit rule says so.

### INV-004 — Original RAW authority

A RAW Candle is one original row from the input file. Lower-timeframe chronology MUST use these original rows directly. A lower timeframe MUST NOT be synthesized from Main Candles.

### INV-005 — Main Candle versus RAW Candle

A Main Candle is an aggregation bucket at the requested `timeframe`. A RAW Candle is never replaced by a re-aggregated approximation when exact chronology is required.

### INV-006 — Determinism

Given the same RAW rows, timeframe, range, direction, and enable flags, iteration order and output order MUST remain deterministic.

### INV-007 — No fixture logic

No timestamp, price, symbol, filename, or dataset-specific exception participates in production decisions.


## 5. Input Model, Time, and Aggregation

### DATA-001 — RAW row model

Rule-ID: DATA-001  
Status: Active  
Phase: Input  
Source-Origin: `trading_pipeline.build_native_raw_candles`

Each RAW row MUST provide:

| Key | Type | Meaning |
| --- | --- | --- |
| `time` | integer epoch seconds | RAW Candle timestamp |
| `open` | numeric | RAW open |
| `high` | numeric | RAW high |
| `low` | numeric | RAW low |
| `close` | numeric | RAW close |

The production pipeline assumes rows are already ordered by `time` because `isolate_raw_range` uses `bisect_left`. It does not sort or deduplicate rows. Duplicate timestamps, if present, remain separate RAW rows in their original list order.

### DATA-002 — Time conversion

`local_datetime(epoch_value)` converts epoch seconds into Asia/Tehran and removes timezone metadata, leaving a naive project-local `datetime`. `epoch(local)` reattaches Asia/Tehran and converts back to integer epoch seconds.

### DATA-003 — Selected RAW range

`prepare_market_context` computes:

```python
range_end_exclusive = args.to_time + args.timeframe
rows = isolate_raw_range(source_rows, args.from_time, range_end_exclusive)
```

Therefore selected RAW rows satisfy the bisected interval `[from_time, to_time + timeframe)`.

### AGG-001 — Native RAW Candle construction

`build_native_raw_candles` creates exactly one `Candle` per selected RAW row. The index is the row position in the isolated range. `tag` is produced by `classify_candle_color`.

### AGG-002 — Main timeframe buckets

`build_timeframe_buckets(rows, raw_candles, timeframe)` computes:

```python
bucket_time = timestamp if timeframe == 1 else timestamp // timeframe * timeframe
```

For each bucket:

- `open` = open of the first RAW Candle in bucket order.
- `high` = maximum RAW high in the bucket.
- `low` = minimum RAW low in the bucket.
- `close` = close of the last RAW Candle in bucket order.
- incomplete edge buckets are retained; there is no completeness filter.

When `timeframe == 1`, `raw_candles` are also the Main Candles.

### DATA-004 — `Candle`

`Candle` fields are:

`index`, `timestamp`, `display_time`, `tag`, `open`, `high`, `low`, `close`.

`display_time` is formatted as `YYYY-MM-DD HH:MM:SS` in Asia/Tehran local project time.

### DATA-005 — Runtime configuration and module enablement

The production command-line contract is part of reproducibility. `parse_arguments` accepts the following behavior-affecting values:

| Argument | Required | Values / default | Calculation effect |
| --- | --- | --- | --- |
| `--reaction-engine` / `--engine` | Yes | path | Loads Reaction engine. |
| `--blue-line-engine` / `--blue-engine` | Yes | path | Loads Blue engine. |
| `--a-zone-engine` / `--a-engine` | Yes | path | Loads A engine. |
| `--s-zone-engine` / `--s-engine` | Yes | path | Loads S engine. |
| `--e-zone-engine` / `--e-engine` | No | path or absent | E is available only when supplied. |
| `--lifecycle-engine` / `--stopall-engine` | No | path or absent | If absent, `load_engines` still loads the local `lifecycle_engine.py`; however public `stopAllEnabled` is true only when the CLI path was explicitly supplied and E+S are enabled. |
| `--blue-lines` | No | `enabled` (default) / `disabled` | Public Blue output flag; Blue calculation is still required when A or S is enabled. |
| `--a-zones` | No | `enabled` (default) / `disabled` | Public A output flag; A calculation is still required when S is enabled. |
| `--s-zones` | No | `enabled` (default) / `disabled` | Enables S; E requires S enabled. |
| `--data` | Yes | RAW JSON path | Input source. |
| `--timeframe` | Yes | integer >= 1 | Main timeframe in seconds. |
| `--from-time` | Yes | integer epoch | Range lower bound. |
| `--to-time` | Yes | integer epoch | Requested upper range anchor; selection extends by one Main timeframe as DATA-003 specifies. |
| `--direction` | Yes | `bullish`, `bearish`, `both` | Requested public direction(s). |

`prepare_pipeline_state` calculates both Reaction directions whenever any behavior module (Blue/A/S) is enabled, even if only one direction is requested, because opposite-direction Reactions/Resets participate in downstream ownership.


## 6. Processing Pipeline

### PIPE-001 — Calculation order

Rule-ID: PIPE-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Pipeline  
Implementation-Class: Shared  
Requires-RAW: Conditional  
Produces: Ordered calculation state and/or public direction payload.  
Depends-On: DATA/AGG rules plus enabled detector/lifecycle phases.  

**Purpose:** Defines `Calculation order` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** EngineBundle, MarketContext, PipelineState, CLI enable flags, and detector outputs.  
**Trigger:** When the production pipeline enters this phase.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Ordered calculation state and/or public direction payload.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Conditional; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** See the symbolic examples relevant to this phase in Section 24.  
**Test Contract:** Reimplementation checklist and output-schema checks.  

With behavior modules enabled, the production calculation order is:

```text
RAW JSON
→ isolate_raw_range
→ build_native_raw_candles
→ build_timeframe_buckets / build_candle_objects
→ LowerTimeframeIndex + MarketChronology
→ UnifiedReactionDetector for required directions
→ build_behavior_reaction_views
→ detect_blue_lines
→ detect_a_zones
→ SZoneDetector.detect
→ EZoneDetector.detect
→ A/S/E lifecycle reconciliation
→ reconcile_stopall_lifecycle
→ finalize_behavior_visibility
→ mark_internal_blue_lines / filter_internal_behavior_outputs
→ prepare_order_audit
→ serialization
```

Even a single requested direction may require both directional Reaction streams because A/S/E ownership consumes opposite-direction Reactions and Resets.

### PIPE-002 — Lower-timeframe service

Rule-ID: PIPE-002  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Pipeline  
Implementation-Class: Shared  
Requires-RAW: Conditional  
Produces: Ordered calculation state and/or public direction payload.  
Depends-On: DATA/AGG rules plus enabled detector/lifecycle phases.  

**Purpose:** Defines `Lower-timeframe service` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** EngineBundle, MarketContext, PipelineState, CLI enable flags, and detector outputs.  
**Trigger:** When the production pipeline enters this phase.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Ordered calculation state and/or public direction payload.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Conditional; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** See the symbolic examples relevant to this phase in Section 24.  
**Test Contract:** Reimplementation checklist and output-schema checks.  

`LowerTimeframeIndex` indexes the original RAW Candle sequence. `first_less` returns the earliest RAW position whose Low is strictly `< level`; `first_greater` returns the earliest RAW position whose High is strictly `> level`. `range_minimum` and `range_maximum` return the extreme and earliest owning RAW position on equality.

### PIPE-003 — `MarketChronology`

Rule-ID: PIPE-003  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Pipeline  
Implementation-Class: Shared  
Requires-RAW: Conditional  
Produces: Ordered calculation state and/or public direction payload.  
Depends-On: DATA/AGG rules plus enabled detector/lifecycle phases.  

**Purpose:** Defines ``MarketChronology`` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** EngineBundle, MarketContext, PipelineState, CLI enable flags, and detector outputs.  
**Trigger:** When the production pipeline enters this phase.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Ordered calculation state and/or public direction payload.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Conditional; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** See the symbolic examples relevant to this phase in Section 24.  
**Test Contract:** Reimplementation checklist and output-schema checks.  

`MarketChronology.main_index(timestamp)` maps an exact RAW time to the owning Main Candle with `bisect_right(times, timestamp) - 1`.

`MarketChronology.lower_bounds(start, end)` uses `bisect_left`, making the window start-inclusive and end-exclusive.

`MarketChronology.reaction_confirmation` scans only the Break Main Candle from the allowed `start` through `candle_end` and returns the first RAW strict confirmation. If none is found, it falls back to the Break Main Candle start time rather than inventing an intrabar order.


#### LowerTimeframeIndex exact semantics

`LowerTimeframeIndex` is an immutable segment index over the Original RAW Candle sequence. `first_less(left, right, level)` and `first_greater(left, right, level)` search the half-open RAW-position range `[left, right)`. A segment is pruned when its extreme cannot satisfy the strict comparator. The first matching leaf in source order is returned.

`range_minimum(left, right)` and `range_maximum(left, right)` return `(Decimal extreme, earliest RAW position)`. Equality resolves to the earlier RAW position. An empty/out-of-range query raises `ValueError("Range contains no lower-timeframe candles.")`. `shared_lower_timeframe_index` caches one index per exact source sequence identity.

`MarketChronology.main_index(timestamp, clamp=False)` uses `bisect_right(self.times, timestamp) - 1`. If the event is before the first Main Candle it raises `ValueError("Lower-timeframe event precedes the main candles.")`; with `clamp=True` it returns zero.

`MarketChronology.reset_time(reset)` returns `second_time` when present, else `display_time`, else `timestamp`. String times are parsed with `%Y-%m-%d %H:%M:%S`.

`MarketChronology.reaction_confirmation(direction, reaction, use_intrabar_start=True)` uses `reaction.intrabar_start` only when requested and valid inside the Break Main Candle; otherwise it starts at the Break Main Candle open. A-engine calls use `use_intrabar_start=False`; S/E/public chronology use the default. If no strict RAW confirmation is found in the Break Main Candle, the function returns the Break Main Candle start.


## 7. Bearish Reaction Specification

### Reaction data model

`Candidate` is the authoritative internal Reaction object. Its behaviorally relevant fields are:

- `first_idx`, `first_time`
- `box_top_source_idx`, `box_top_source_time`, `box_top`
- `box_bottom_source_idx`, `box_bottom_source_time`, `box_bottom`
- `mode`
- `anchor_idx`, `anchor_value`, `leg_boundary_value`
- `break_idx`, `break_time`
- `intrabar_start`
- `cross_direction_origin`, `cross_direction_chain_owner`
- `order_gate_decision`
- behavior-public metadata populated by `build_behavior_reaction_views`
- `behavior_internal`

### REA-A-001 — Mode A role colors

Rule-ID: REA-A-001  
Status: Active  
Direction: Bearish  
Phase: Reaction  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: Candidate Reaction state or a confirmed Reaction.  
Depends-On: INV-001..INV-005, DATA/AGG, RAW-001..RAW-003.  

**Purpose:** Defines `Mode A role colors` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Main Candles, Original RAW Candles, MarketChronology, prior Reaction/Reset state.  
**Trigger:** When the Reaction state machine reaches the eligibility condition stated in the normative body.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Candidate Reaction state or a confirmed Reaction.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-REA-001  
**Test Contract:** T-RAW-CONF and T-REA-TIE.  

Source-Origin: `reaction_engine.BearishDetector` and `UnifiedReactionDetector`

- Context color: `RED`.
- First color: `GREEN`.
- Confirmation edge: `box_bottom`.
- Reset edge: `box_top`.
- Directional leg extreme: `high`.

A Mode-A candidate begins only from the current leg/reset ownership context. The first-color Main Candle must follow the required context-color sequence and must satisfy the outer leg-boundary acceptance logic.

For the source state machine, the exact direction-specific confirmation condition is:

```python
candle.low < candidate.box_bottom
```

The exact direction-specific Reset condition against the previously confirmed Reaction is:

```python
candle.high > previous.box_top
```

### REA-A-002 — Direct post-Reset owner

Rule-ID: REA-A-002  
Status: Active  
Direction: Bearish  
Phase: Reaction  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: Candidate Reaction state or a confirmed Reaction.  
Depends-On: INV-001..INV-005, DATA/AGG, RAW-001..RAW-003.  

**Purpose:** Defines `Direct post-Reset owner` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Main Candles, Original RAW Candles, MarketChronology, prior Reaction/Reset state.  
**Trigger:** When the Reaction state machine reaches the eligibility condition stated in the normative body.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Candidate Reaction state or a confirmed Reaction.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-REA-001  
**Test Contract:** T-RAW-CONF and T-REA-TIE.  

Source-Origin: `UnifiedReactionDetector._first_direct_same_direction_after_reset`, `_build_direct_candidate`, `_scan_direct_candidate`, `_owner_boundary_before_confirmation`.

After a Reset, scanning begins strictly after `reset_index`. The first eligible `GREEN` Main Candle whose immediately preceding Main Candle is `RED` may become the owner candidate.

`_build_direct_candidate` preserves the actual Reset context and freezes the outer leg boundary from the Reset region through the pre-First context. For this direction, strict loss of that boundary occurs when the directional `high` moves beyond the frozen boundary before confirmation.

If invalidation and confirmation are both possible inside one Main Candle, `_owner_boundary_before_confirmation` scans Original RAW Candles in chronological order. Invalidation wins only when its strict event occurs first; confirmation wins when its strict event occurs first. Equality does not invalidate.

If the earliest owner is invalidated, `_first_direct_same_direction_after_reset` blocks through the invalidation Main Candle and continues searching. A later nested pattern cannot confirm while an earlier owner remains unresolved.

### REA-B-001 — Mode B formation

Rule-ID: REA-B-001  
Status: Active  
Direction: Bearish  
Phase: Reaction  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: Candidate Reaction state or a confirmed Reaction.  
Depends-On: INV-001..INV-005, DATA/AGG, RAW-001..RAW-003.  

**Purpose:** Defines `Mode B formation` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Main Candles, Original RAW Candles, MarketChronology, prior Reaction/Reset state.  
**Trigger:** When the Reaction state machine reaches the eligibility condition stated in the normative body.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Candidate Reaction state or a confirmed Reaction.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-REA-001  
**Test Contract:** T-RAW-CONF and T-REA-TIE.  

After a confirmed Reaction without a post-confirmation Reset, normal search is active. A `GREEN` Main Candle can open a Mode-B candidate.

The running confirmation-side extreme is `low`. The candidate confirmation edge is derived from the running extreme and the First candle. The opposite edge is owned by the complete range from the confirmation-edge source forward through First.

While waiting:

- the opposite box edge may extend only in the directional adverse direction (`box_top` with comparator `>`),
- confirmation requires `candle.low < candidate.box_bottom`.

After confirmation, `UnifiedReactionDetector._append_reaction` normalizes the opposite edge to the complete confirmed `First..Break` Main-Candle geometry, inclusive.

### REA-CONF-001 — Exact RAW confirmation

Rule-ID: REA-CONF-001  
Status: Active  
Direction: Bearish  
Phase: Reaction  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: Candidate Reaction state or a confirmed Reaction.  
Depends-On: INV-001..INV-005, DATA/AGG, RAW-001..RAW-003.  

**Purpose:** Defines `Exact RAW confirmation` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Main Candles, Original RAW Candles, MarketChronology, prior Reaction/Reset state.  
**Trigger:** When the Reaction state machine reaches the eligibility condition stated in the normative body.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Candidate Reaction state or a confirmed Reaction.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-REA-001  
**Test Contract:** T-RAW-CONF and T-REA-TIE.  

Source-Origin: `MarketChronology.reaction_confirmation`, `BearishDetector.breakdown_analysis`.

The Break Main Candle is not itself the exact confirmation time. Exact confirmation is the first Original RAW Candle in the allowed Break window satisfying the strict confirmation edge:

```python
# Bearish
value = item.low
confirms = value < reaction.box_bottom
```

The public Reaction object does not serialize this exact confirmation timestamp, but S/E/Order chronology consumes it.

### REA-CONF-002 — Break-candle opposite-edge refinement

Rule-ID: REA-CONF-002  
Status: Active  
Direction: Bearish  
Phase: Reaction  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: Candidate Reaction state or a confirmed Reaction.  
Depends-On: INV-001..INV-005, DATA/AGG, RAW-001..RAW-003.  

**Purpose:** Defines `Break-candle opposite-edge refinement` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Main Candles, Original RAW Candles, MarketChronology, prior Reaction/Reset state.  
**Trigger:** When the Reaction state machine reaches the eligibility condition stated in the normative body.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Candidate Reaction state or a confirmed Reaction.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-REA-001  
**Test Contract:** T-RAW-CONF and T-REA-TIE.  

`BearishDetector.breakdown_analysis` locates the first strict RAW confirmation and the most extreme opposite edge up to and including that RAW event. If the Break Main Candle currently owns the candidate opposite edge, `_refine` replaces that edge with the pre-confirmation RAW extreme rather than a later extreme from the same Main Candle.

### RST-001 — Normal Reset

Rule-ID: RST-001  
Status: Active  
Direction: Bearish  
Phase: Reaction/Reset  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: ResetEvent or Reset ownership transition.  
Depends-On: REA rules and RAW-001..RAW-003.  

**Purpose:** Defines `Normal Reset` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Confirmed/waiting Reaction geometry, Main Candle, and Original RAW chronology.  
**Trigger:** When a strict Reset/invalidation condition stated below becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** ResetEvent or Reset ownership transition.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-RST-001  
**Test Contract:** T-REA-TIE.  

A confirmed Bearish Reaction resets when a later Main Candle strictly breaks `box_top` according to `candle.high > previous.box_top`. The Reset records the Main Candle index/time, `broken_level`, and the owning Reaction `from_first_idx`.

### RST-002 — Reset versus confirmation in the same Main Candle

Rule-ID: RST-002  
Status: Active  
Direction: Bearish  
Phase: Reaction/Reset  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: ResetEvent or Reset ownership transition.  
Depends-On: REA rules and RAW-001..RAW-003.  

**Purpose:** Defines `Reset versus confirmation in the same Main Candle` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Confirmed/waiting Reaction geometry, Main Candle, and Original RAW chronology.  
**Trigger:** When a strict Reset/invalidation condition stated below becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** ResetEvent or Reset ownership transition.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-RST-001  
**Test Contract:** T-REA-TIE.  

If a Reset of the prior confirmed Reaction and confirmation of a waiting candidate can both occur in one Main Candle, `BearishDetector.confirmed_reset_before_breakdown` uses Original RAW chronology.

The source uses the earliest strict RAW positions. A true same-RAW-position tie is resolved in favor of Reset because the implementation compares the positions with `<=`.

### RST-003 — Mode-A invalidation versus confirmation

Rule-ID: RST-003  
Status: Active  
Direction: Bearish  
Phase: Reaction/Reset  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: ResetEvent or Reset ownership transition.  
Depends-On: REA rules and RAW-001..RAW-003.  

**Purpose:** Defines `Mode-A invalidation versus confirmation` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Confirmed/waiting Reaction geometry, Main Candle, and Original RAW chronology.  
**Trigger:** When a strict Reset/invalidation condition stated below becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** ResetEvent or Reset ownership transition.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-RST-001  
**Test Contract:** T-REA-TIE.  

`BearishDetector.invalidation_high_break_before_breakdown` freezes the leg boundary. If the strict leg-boundary invalidation and candidate confirmation occur inside one Main Candle, Original RAW positions decide the order. A true same-position tie invalidates the candidate.

### RST-004 — Post-confirmation Reset inside the Break Main Candle

Rule-ID: RST-004  
Status: Active  
Direction: Bearish  
Phase: Reaction/Reset  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: ResetEvent or Reset ownership transition.  
Depends-On: REA rules and RAW-001..RAW-003.  

**Purpose:** Defines `Post-confirmation Reset inside the Break Main Candle` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Confirmed/waiting Reaction geometry, Main Candle, and Original RAW chronology.  
**Trigger:** When a strict Reset/invalidation condition stated below becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** ResetEvent or Reset ownership transition.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-RST-001  
**Test Contract:** T-REA-TIE.  

`BearishDetector.post_breakdown_reset` begins strictly after the exact confirmation event (`+ timedelta(microseconds=1)`) and scans to the end of the same Main Candle. A strict break of `box_top` creates a Reset with `second_time` equal to the exact RAW Reset time.

When this happens, the remainder of the Break Main Candle MUST NOT seed a normal successor. The next search restarts as a fresh Mode-A leg.

### REA-B-002 — Confirmation-candle reuse when no post-confirmation Reset exists

Rule-ID: REA-B-002  
Status: Active  
Direction: Bearish  
Phase: Reaction  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: Candidate Reaction state or a confirmed Reaction.  
Depends-On: INV-001..INV-005, DATA/AGG, RAW-001..RAW-003.  

**Purpose:** Defines `Confirmation-candle reuse when no post-confirmation Reset exists` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Main Candles, Original RAW Candles, MarketChronology, prior Reaction/Reset state.  
**Trigger:** When the Reaction state machine reaches the eligibility condition stated in the normative body.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Candidate Reaction state or a confirmed Reaction.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-REA-001  
**Test Contract:** T-RAW-CONF and T-REA-TIE.  

`UnifiedReactionDetector._candidate_from_confirmation_remainder` may reuse the entire confirmation Main Candle as the next Mode-B First only when its `Candle.tag` equals `GREEN` and intrabar analysis exists. In the current source, `whole_confirmation_candle = True`; therefore the candidate box uses the entire confirmation Main Candle RAW range rather than only the post-event remainder.

### REA-PUB-001 — Published Reaction geometry

Rule-ID: REA-PUB-001  
Status: Active  
Direction: Bearish  
Phase: Reaction  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: Candidate Reaction state or a confirmed Reaction.  
Depends-On: INV-001..INV-005, DATA/AGG, RAW-001..RAW-003.  

**Purpose:** Defines `Published Reaction geometry` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Main Candles, Original RAW Candles, MarketChronology, prior Reaction/Reset state.  
**Trigger:** When the Reaction state machine reaches the eligibility condition stated in the normative body.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Candidate Reaction state or a confirmed Reaction.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-REA-001  
**Test Contract:** T-RAW-CONF and T-REA-TIE.  

`published_reaction_candidate` protects public geometry from retroactive movement after exact confirmation. If the Break Main Candle owns the opposite box edge, only RAW extremes up to and including the first strict confirmation are eligible. If exact RAW confirmation cannot be resolved, detector geometry is preserved rather than guessed.

Equal extremes retain the earliest Main-Candle owner.

### REA-GATE-001 — Direct Order geometry after an exact stop gate

Rule-ID: REA-GATE-001  
Status: Active  
Direction: Bearish  
Phase: Reaction  
Implementation-Class: Mirrored  
Requires-RAW: Yes  
Produces: Candidate Reaction state or a confirmed Reaction.  
Depends-On: INV-001..INV-005, DATA/AGG, RAW-001..RAW-003.  

**Purpose:** Defines `Direct Order geometry after an exact stop gate` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Main Candles, Original RAW Candles, MarketChronology, prior Reaction/Reset state.  
**Trigger:** When the Reaction state machine reaches the eligibility condition stated in the normative body.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Candidate Reaction state or a confirmed Reaction.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-REA-001  
**Test Contract:** T-RAW-CONF and T-REA-TIE.  

`UnifiedReactionDetector.first_order_reaction_after_gate` treats `gate_event_time` as exact RAW chronology. A Reaction whose Break is in the gate Main Candle counts as history only if its exact confirmation is no later than the gate event.

With history, the method compares the active outer boundary against the gate-candle boundary using RAW events. The first strict event determines `order_gate_decision`:

- `"restart"`: the outer owner boundary breaks first; search resumes after the Main Candle containing that event.
- `"continue"`: the gate boundary breaks first; search continues in the already-open post-Reset leg and may restore true anchor provenance.
- `"no-history"`: no prior confirmed Reaction exists by the gate.

The returned geometry is produced by `_earliest_confirmed_geometry`; overlapping First candidates compete by earliest strict confirmation, then the earliest `first_idx` among candidates confirming on that scan.


## 8. Internal Reaction Ownership

### INT-REA-001 — Cross-direction interior classification

Rule-ID: INT-REA-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Internal-Reaction  
Implementation-Class: Shared  
Requires-RAW: Yes  
Produces: behavior_internal/public-Reaction metadata and physical internal identities.  
Depends-On: Published Reaction geometry, exact confirmation, RAW-001.  

**Purpose:** Defines `Cross-direction interior classification` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Both directional Reaction collections and MarketChronology.  
**Trigger:** After both directional Reaction streams have published geometry and exact confirmation metadata.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** behavior_internal/public-Reaction metadata and physical internal identities.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-INT-001  
**Test Contract:** T-INTERNAL.  

Source-Origin: `build_behavior_reaction_views`.

Before A/S/E visibility decisions, both directional Reaction streams are converted to published geometry and exact confirmation times.

A Bearish Reaction is marked `behavior_internal = True` only when an opposite-direction outer Reaction satisfies all of the following:

1. the inner `behavior_first_time` is strictly later than the outer First time;
2. the inner confirmation is no later than the outer confirmation;
3. the inner published `box_top` is `<=` outer published `box_top`;
4. the inner published `box_bottom` is `>=` outer published `box_bottom`;
5. every Original RAW Candle from the inner First through inner exact confirmation, inclusive, stays inside the outer published box (`low >= outer_bottom` and `high <= outer_top`).

The physical Reaction identity used by this subsystem is:

```python
(int(reaction.first_idx), int(reaction.break_idx))
```

`behavior_public_number`, `behavior_public_box_top`, `behavior_public_box_bottom`, `behavior_confirmation_time`, and `behavior_first_time` are populated on every Reaction before downstream ownership filters run.


## 9. Blue Line Specification

### BLU-001 — Reaction reference and Fibonacci level

Rule-ID: BLU-001  
Status: Active  
Direction: Bearish  
Phase: Blue  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: BlueLine objects or Blue validity/visibility state.  
Depends-On: Confirmed Reactions/Resets, DirectionPolicy, MarketChronology.  

**Purpose:** Defines `Reaction reference and Fibonacci level` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Resets, MarketChronology, and prior Blue state.  
**Trigger:** For each confirmed current-direction Reaction and its owned Reset events.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** BlueLine objects or Blue validity/visibility state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-BLU-001  
**Test Contract:** T-BLUE-SCALE and T-INTERNAL.  

Source-Origin: `detect_blue_lines`, `fibonacci_level`, `count_scale_strikes`.

`FIBONACCI_RATIO = Decimal("0.618")`.

For a Mode-A Reaction, `reference` is `anchor_value`; if absent, `leg_boundary_value`. Missing both is an error.

For a Mode-B Reaction, `reference` is the previous Reaction's `box_top`.

The exact Bearish formula is:

```python
bottom + FIBONACCI_RATIO * (reference - bottom)
```

### BLU-SCALE-001 — Scale strikes

Rule-ID: BLU-SCALE-001  
Status: Active  
Direction: Bearish  
Phase: Blue  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: BlueLine objects or Blue validity/visibility state.  
Depends-On: Confirmed Reactions/Resets, DirectionPolicy, MarketChronology.  

**Purpose:** Defines `Scale strikes` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Resets, MarketChronology, and prior Blue state.  
**Trigger:** For each confirmed current-direction Reaction and its owned Reset events.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** BlueLine objects or Blue validity/visibility state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-BLU-001  
**Test Contract:** T-BLUE-SCALE and T-INTERNAL.  

`count_scale_strikes` scans Main Candles from `first_idx` through `break_idx`, inclusive.

- The strike extreme field is `high`.
- A new pending strike requires `DirectionPolicy.improves(candle_extreme, last_extreme)`.
- A more extreme pending strike replaces the previous pending strike.
- A pending strike is confirmed when a Main Candle has `tag == "RED"`.

If a pending strike survives to the end of the Reaction, `_intrabar_pending_confirmation` scans Original RAW Candles from the pending source through the Break Main Candle. It collects RAW candles that strictly improve the comparison extreme. Once a RAW candle also strictly confirms the owning Reaction, the decisive extreme among eligible RAW candles is selected and mapped back to its owning Main Candle.

### BLU-SCALE-002 — Scale Blue emission and spacing

Rule-ID: BLU-SCALE-002  
Status: Active  
Direction: Bearish  
Phase: Blue  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: BlueLine objects or Blue validity/visibility state.  
Depends-On: Confirmed Reactions/Resets, DirectionPolicy, MarketChronology.  

**Purpose:** Defines `Scale Blue emission and spacing` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Resets, MarketChronology, and prior Blue state.  
**Trigger:** For each confirmed current-direction Reaction and its owned Reset events.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** BlueLine objects or Blue validity/visibility state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-BLU-001  
**Test Contract:** T-BLUE-SCALE and T-INTERNAL.  

A Scale Blue candidate exists only when the current strike count is strictly greater than the previous Reaction strike count:

```python
scale_candidate = previous_count is not None and len(strikes) > previous_count
```

It is emitted only if no Blue has yet been emitted or at least one healthy Reaction has occurred since the previous Blue. A new Blue resets `healthy_reactions_since_blue` to zero.

The decisive Scale Blue source is the final confirmed strike. The rendered line price is:

```python
line_price = high - (high - low) / Decimal(3)
```

`start_time = source_time - chronology.timeframe` and `end_time = source_time + chronology.timeframe`.

### BLU-RESET-001 — Reset Blue

Rule-ID: BLU-RESET-001  
Status: Active  
Direction: Bearish  
Phase: Blue  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: BlueLine objects or Blue validity/visibility state.  
Depends-On: Confirmed Reactions/Resets, DirectionPolicy, MarketChronology.  

**Purpose:** Defines `Reset Blue` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Resets, MarketChronology, and prior Blue state.  
**Trigger:** For each confirmed current-direction Reaction and its owned Reset events.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** BlueLine objects or Blue validity/visibility state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-BLU-001  
**Test Contract:** T-BLUE-SCALE and T-INTERNAL.  

Resets are indexed by `from_first_idx` and processed under their owner Reaction. Reset Blue source is the Reset Main Candle.

The exact line-price formula is:

```python
line_price = high - (high - low) / Decimal(5)
```

For this direction, `source_extreme` is the Reset Main Candle `high` and `broken_level` is the Reset's `broken_level`.

A Reset Blue is skipped when a Blue already exists and fewer than one healthy Reaction has occurred since the previous Blue.

### BLU-RESET-002 — Double-stop calculation validity

Rule-ID: BLU-RESET-002  
Status: Active  
Direction: Bearish  
Phase: Blue  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: BlueLine objects or Blue validity/visibility state.  
Depends-On: Confirmed Reactions/Resets, DirectionPolicy, MarketChronology.  

**Purpose:** Defines `Double-stop calculation validity` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Resets, MarketChronology, and prior Blue state.  
**Trigger:** For each confirmed current-direction Reaction and its owned Reset events.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** BlueLine objects or Blue validity/visibility state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-BLU-001  
**Test Contract:** T-BLUE-SCALE and T-INTERNAL.  

`_build_reset_blue_line` sets `calculation_valid = False` only when all of the following are true:

1. `previous_line` exists;
2. `_stops_on_index` proves the first strict stop of the previous line occurs exactly at the current Reset index;
3. the current Reset source extends strictly beyond the previous line `source_extreme` in the Bearish direction.

A calculation-invalid Blue remains available to the special double-stop A path but is excluded from ordinary `BlueState` construction and public Blue serialization.

### BLU-INT-001 — Internal Blue

Rule-ID: BLU-INT-001  
Status: Active  
Direction: Bearish  
Phase: Blue  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: BlueLine objects or Blue validity/visibility state.  
Depends-On: Confirmed Reactions/Resets, DirectionPolicy, MarketChronology.  

**Purpose:** Defines `Internal Blue` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Resets, MarketChronology, and prior Blue state.  
**Trigger:** For each confirmed current-direction Reaction and its owned Reset events.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** BlueLine objects or Blue validity/visibility state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-BLU-001  
**Test Contract:** T-BLUE-SCALE and T-INTERNAL.  

`mark_internal_blue_lines` marks a Blue internal when either:

- its owner Reaction is `behavior_internal`, or
- both `source_extreme` and `line_price` are strictly inside the same healthy Reaction interior at a `source_time` strictly after that Reaction First and no later than its confirmation.

`public_blue_lines` returns only lines with `calculation_valid == True` and `behavior_internal == False`.


## 10. A Behavior Specification

### A-STATE-001 — `BlueState`

Rule-ID: A-STATE-001  
Status: Active  
Direction: Bearish  
Phase: A  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: AZone objects or A lifecycle state.  
Depends-On: BLU rules, confirmed trend Reactions, MarketChronology.  

**Purpose:** Defines ``BlueState`` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Blue Lines, Main Candles, and MarketChronology.  
**Trigger:** When the required Blue lifecycle/pair state becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** AZone objects or A lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-A-001  
**Test Contract:** T-A-STRICT.  

`AZoneDetector._build_blue_states` enumerates Blue Lines in sorted order `(reaction_number, source_time, kind)` using 1-based ordinals. Calculation-invalid Blue Lines are skipped here.

For Scale Blue, formation index is the owner Reaction Break and exact formation time is `MarketChronology.reaction_confirmation(self.direction, reaction, use_intrabar_start=False)`. For Reset Blue, formation index is `source_index` and `_reset_formation_time` scans the source Main Candle for the exact strict RAW break of `broken_level`.

The first future strict crossing of each Blue `source_extreme` becomes its stop.

### A-ORD-001 — Ordinary adjacent-Blue pair

Rule-ID: A-ORD-001  
Status: Active  
Direction: Bearish  
Phase: A  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: AZone objects or A lifecycle state.  
Depends-On: BLU rules, confirmed trend Reactions, MarketChronology.  

**Purpose:** Defines `Ordinary adjacent-Blue pair` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Blue Lines, Main Candles, and MarketChronology.  
**Trigger:** When the required Blue lifecycle/pair state becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** AZone objects or A lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-A-001  
**Test Contract:** T-A-STRICT.  

`_detect_ordinary_a` evaluates adjacent valid `BlueState` objects. The pair expires at the next Blue formation time when a third Blue exists.

`_pair_trigger` rejects the pair if the previous Blue has no stop or its stop is after `expires_at`.

The pair trigger has three source-faithful cases:

1. **Inherited stop geometry** — `_inherited_stop(previous, current)` finds the first trend Reaction fully between previous and current Blue formation. `continuation_level` becomes the directional extreme from `previous.formation_time` through that Reaction Break. The first strict crossing from `current.formation_time` to `expires_at` triggers A.
2. **Previous Blue stopped before current Blue formation** — `continuation_level` becomes `_range_extreme(previous.stop_event_time, current_source_time - 1 microsecond)`. The current formation Main Candle is checked first from exact current formation through its Main Candle end. If that fails, current Blue must itself stop and the level must then be strictly crossed after the current stop.
3. **Overlapping/same-cycle stops** — previous/current states are sorted by exact `stop_event_time` and a direction-specific tie key. The first stop's `stop_event_extreme` becomes `continuation_level`. If both stops share the exact event time, the second stop event is the trigger; otherwise the level must be strictly crossed after the second stop.

### A-ORD-002 — Validating trend Reaction

Rule-ID: A-ORD-002  
Status: Active  
Direction: Bearish  
Phase: A  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: AZone objects or A lifecycle state.  
Depends-On: BLU rules, confirmed trend Reactions, MarketChronology.  

**Purpose:** Defines `Validating trend Reaction` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Blue Lines, Main Candles, and MarketChronology.  
**Trigger:** When the required Blue lifecycle/pair state becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** AZone objects or A lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-A-001  
**Test Contract:** T-A-STRICT.  

After `_pair_trigger` returns, `_first_reaction_after` selects the first trend Reaction satisfying:

```python
self._reaction_confirmation_time(reaction) >= trigger_event_time
```

and, when `not_before` is supplied, the Reaction First Main time must be `>= not_before`.

For ordinary A, `not_before = max(blue_1_stop_time, blue_2_stop_time)`.

### A-SRC-001 — A source and price

Rule-ID: A-SRC-001  
Status: Active  
Direction: Bearish  
Phase: A  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: AZone objects or A lifecycle state.  
Depends-On: BLU rules, confirmed trend Reactions, MarketChronology.  

**Purpose:** Defines `A source and price` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Blue Lines, Main Candles, and MarketChronology.  
**Trigger:** When the required Blue lifecycle/pair state becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** AZone objects or A lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-A-001  
**Test Contract:** T-A-STRICT.  

`_a_source(trigger_index, reaction)` scans complete Main Candles from `trigger_index` through the validating Reaction `break_idx`, inclusive. The source is the strict directional extreme using `DirectionPolicy.improves`; equality preserves the earlier source.

For Bearish, A `price` is therefore the maximum High in that inclusive Main-Candle range.

### A-REUSE-001 — Adjacent Blue reuse

Rule-ID: A-REUSE-001  
Status: Active  
Direction: Bearish  
Phase: A  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: AZone objects or A lifecycle state.  
Depends-On: BLU rules, confirmed trend Reactions, MarketChronology.  

**Purpose:** Defines `Adjacent Blue reuse` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Blue Lines, Main Candles, and MarketChronology.  
**Trigger:** When the required Blue lifecycle/pair state becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** AZone objects or A lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-A-001  
**Test Contract:** T-A-STRICT.  

After an ordinary A is created, the first strict A stop is searched from the validating Reaction exact confirmation. The second Blue may be reused as the first Blue of the adjacent pair only when a third Blue exists and its formation time is no earlier than that A stop event. Otherwise all Blue states whose formation index is `<=` the validating Break index are consumed before the next pair search.

### A-DOUBLE-001 — Special double-stop A

Rule-ID: A-DOUBLE-001  
Status: Active  
Direction: Bearish  
Phase: A  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: AZone objects or A lifecycle state.  
Depends-On: BLU rules, confirmed trend Reactions, MarketChronology.  

**Purpose:** Defines `Special double-stop A` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Blue Lines, Main Candles, and MarketChronology.  
**Trigger:** When the required Blue lifecycle/pair state becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** AZone objects or A lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-A-001  
**Test Contract:** T-A-STRICT.  

`_double_stop_a_candidates` processes a calculation-invalid Blue only when a previous valid Blue exists. The previous valid Blue `source_extreme` must be strictly crossed between the invalid Blue `formation_time` and the end of its source Main Candle, and that crossing must map to the invalid Blue's `source_index`.

The first trend Reaction after that trigger validates the special A. A source uses `_a_source` exactly as ordinary A.

### A-DOUBLE-002 — Special/ordinary ownership filtering

Rule-ID: A-DOUBLE-002  
Status: Active  
Direction: Bearish  
Phase: A  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: AZone objects or A lifecycle state.  
Depends-On: BLU rules, confirmed trend Reactions, MarketChronology.  

**Purpose:** Defines `Special/ordinary ownership filtering` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Blue Lines, Main Candles, and MarketChronology.  
**Trigger:** When the required Blue lifecycle/pair state becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** AZone objects or A lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-A-001  
**Test Contract:** T-A-STRICT.  

`_filter_special_a` applies the following rules in order:

1. A special A is removed if an ordinary A uses the same `reaction_number`.
2. A special A is removed when the latest earlier ordinary A had already experienced its first strict stop before the special Reaction First, with the stop lifecycle constrained by `blue_1_source_time`.
3. Accepted special A objects consume later ordinary A objects whose Blue ordinals overlap the special pair and whose `trigger_event_time` is later.

### A-OWN-001 — A stop semantics

Rule-ID: A-OWN-001  
Status: Active  
Direction: Bearish  
Phase: A  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: AZone objects or A lifecycle state.  
Depends-On: BLU rules, confirmed trend Reactions, MarketChronology.  

**Purpose:** Defines `A stop semantics` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Current-direction Reactions, Blue Lines, Main Candles, and MarketChronology.  
**Trigger:** When the required Blue lifecycle/pair state becomes eligible.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** AZone objects or A lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-A-001  
**Test Contract:** T-A-STRICT.  

The A strict stop uses `value > level` against A `price`. Exact stop event comes from Original RAW Candles. The Main stop time is the owning Main Candle start.


## 11. S Behavior Specification

### S-STOP-001 — Exact A stop

Rule-ID: S-STOP-001  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `Exact A stop` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

`SZoneDetector._first_a_stop` scans Original RAW Candles from the A confirmation/lifecycle start. The first strict `high` crossing of A `price` is the A stop. It returns `(index, Main time, exact RAW event time)`.

### ORD-AINIT-001 — Initial Order from a stopped A

Rule-ID: ORD-AINIT-001  
Status: Active  
Direction: Bearish  
Phase: Order  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: One physical Order identity with canonical stop/provenance, or no Order.  
Depends-On: Canonical Reaction identity, MarketChronology.canonical_order_stop, exact stop chronology.  

**Purpose:** Defines `Initial Order from a stopped A` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Canonical opposite Reaction geometry, MarketChronology, parent/reset provenance, and Order ledger state.  
**Trigger:** When a parent stop or reset-leg gate requests an opposite canonical Order.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** One physical Order identity with canonical stop/provenance, or no Order.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-ORD-001  
**Test Contract:** T-E-ID plus canonical-Order rules.  

`_first_order_after(a_stop_event_time)` searches the opposite-direction (`Bullish`) Reaction stream.

A canonical opposite Reaction whose First belongs to the same Main Candle as the exact A stop is eligible only when its exact confirmation is strictly later than the A stop.

`initial_order_geometry` is a local/bounded search aid only. Its physical `(first_idx, break_idx)` identity MUST match a published opposite Reaction before it can become an Order. An unmatched local geometry MUST NOT manufacture an Order.

`_audit_stopped_a` merges multiple stopped-A causes into one `order_audit` entry keyed by physical Order identity.

### S-T3-001 — Type3 eligibility

Rule-ID: S-T3-001  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `Type3 eligibility` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

Type3 is evaluated before an order-backed S and is limited by the direct-order confirmation deadline when such an Order exists.

`_first_type3`:

1. builds reset times by opposite Reaction owner;
2. marks opposite Reactions eligible only when their exact confirmation is no later than the A stop and they were not Reset by/before the A stop;
3. examines opposite Resets strictly after the A stop and strictly before `deadline`;
4. `_type3_reset_leg` computes inclusive owner-Break-to-Reset geometry using the trend directional extreme (`highest High`);
5. Original RAW Candles are scanned for the first strict crossing of that boundary before `deadline`;
6. `_type3_has_trend_reaction` requires at least one trend Reaction exact confirmation strictly after A stop and no later than the boundary crossing;
7. the earliest qualifying crossing wins.

Type3 always creates:

- `color = "blue"`
- `formation_type = "type3"`
- all Order fields = `None`
- `reset_reaction_number` and exact `reset_time` populated.

### S-ORD-001 — Canonical Order stop

Rule-ID: S-ORD-001  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `Canonical Order stop` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

`_order_stop` delegates exclusively to `MarketChronology.canonical_order_stop`. No S-specific synthetic stop is allowed.

### S-TIM-001 — Candidate timing relative to Order

Rule-ID: S-TIM-001  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `Candidate timing relative to Order` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

`_candidate_timing` compares the A-stop Main Candle directional extreme with the Order outer edge. Equality belongs to the `"after"` case.

For this Bearish trend, the Order edge is `box_top`.

### S-SIMPLE-001 — Pre-order Simple candidate

Rule-ID: S-SIMPLE-001  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `Pre-order Simple candidate` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

When `_candidate_timing(a_stop_index, order, order_confirmation_time) == "before"`, `_candidate_before_order` computes the directional extreme from the A-stop Main Candle through Order First. The A-stop Main Candle's pre-stop portion is not allowed to overwrite exact chronology: the RAW remainder beginning at `a_stop_event_time` is evaluated, then later complete Main Candles through First compete with it.

This candidate is passed to `_decision` with `fallback_on_unqualified_cross=True`. A qualified Blue/Red decision owns the result; an unqualified candidate cross returns `"fallback"` and forces later order-backed resolution instead of creating S.

### S-ADV-001 — Advanced candidate

Rule-ID: S-ADV-001  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `Advanced candidate` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

If the pre-order path does not own the decision, `_nested_trend_reaction` searches for a trend Reaction wholly inside the opposite Order box and within Order chronology:

- trend First is strictly after Order First;
- trend Break index is no later than Order Break;
- trend First time is before Order confirmation;
- trend exact confirmation is no later than Order confirmation;
- trend `box_top <= order.box_top` and `box_bottom >= order.box_bottom`.

When found:

- `formation_type = "advanced"`;
- source index is Order `box_top_source_idx`;
- price is the trend directional extreme of that source Main Candle;
- candidate is not eligible before nested trend exact confirmation.

### S-SIMPLE-002 — Post-order Simple candidate

Rule-ID: S-SIMPLE-002  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `Post-order Simple candidate` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

If no Advanced nested Reaction exists, `_first_trend_reaction_after_order` selects the first trend Reaction whose exact confirmation is strictly after Order confirmation.

`_simple_candidate` uses `_candidate_source_last(order.break_idx, trend_reaction.break_idx)`. Equality is deliberately assigned to the **last** Main Candle in this interval.

`_candidate_after_order` supplies the red-side source path. A valid Reaction anchor is authoritative only when `anchor_idx >= start_index`; otherwise the earliest directional extreme after exact Order confirmation through Reaction First is used, including the valid RAW remainder of an intrabar confirmation candle.

### S-DEC-001 — Blue/Red decision race

Rule-ID: S-DEC-001  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `Blue/Red decision race` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

`_decision` scans Original RAW Candles from `max(start, range_start)`.

For every RAW Candle:

```python
candidate_cross = self._candidate_crossed(item, candidate_level)
order_cross = self._order_stop_crossed(item, order_stop_level)
```

The exact Order-stop condition for the opposite `bullish` Order is:

```python
low < order_stop_level
```

Decision order is normative:

1. if `candidate_cross and order_cross`: return `None` because same RAW Candle OHLC cannot reveal the internal order;
2. else if `order_cross`: map `event_time` with `_main_index(event_time)` and return `("red", index, candles[index].timestamp, event_time)`;
3. else if `candidate_cross` and either `_candidate_cross_has_blue(trend_reaction_number, event_time)` or `_has_ordinary_trend_reaction(behavior_start, event_time)`: return `("blue", index, candles[index].timestamp, event_time)`;
4. else, only when `fallback_on_unqualified_cross=True`, return `("fallback", index, candles[index].timestamp, event_time)`.

A candidate cross is ignored before `candidate_start` when that gate is supplied.

### S-BLUE-001 — Blue evidence

Rule-ID: S-BLUE-001  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `Blue evidence` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

`_candidate_cross_has_blue` accepts the aligned Reset Blue when its exact formation time is no later than the candidate crossing. The Blue does not need to be drawn on the candidate or crossing Main Candle.

`_has_ordinary_trend_reaction` independently accepts any ordinary trend Reaction whose exact confirmation is strictly after `behavior_start` and no later than the candidate crossing.

### S-RED-001 — Red source

Rule-ID: S-RED-001  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `Red source` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

If Order stop wins, the S family is Red. For a qualified pre-order candidate, that pre-order source is retained. Otherwise `_candidate_source(order_break_index, decision_index)` supplies the directional extreme through the Red decision Main Candle.

### S-OWN-001 — A ownership window

Rule-ID: S-OWN-001  
Status: Active  
Direction: Bearish  
Phase: S  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: SZone objects or S ownership/decision state.  
Depends-On: A rules, opposite canonical Reactions, Blue evidence, MarketChronology, Order stop rules.  

**Purpose:** Defines `A ownership window` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** A zones, current/opposite Reactions, Blue Lines, opposite Resets, MarketChronology, and initial_order_geometry.  
**Trigger:** After an A has an exact strict stop and this rule's chronology gates are satisfied.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** SZone objects or S ownership/decision state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-S-001  
**Test Contract:** T-S-AMBIG.  

A strict A stop opens an `a_ownership_windows` interval. A decided S closes that interval at `max(a_stop_event_time, decision_event_time + 1 microsecond)`.

A later A inside that ownership window is normally owned by the active S. It may preempt only when all conditions in `_a_owned_by_s` are met: the ownership window is closed, both defining Blues are Reset Blues, the entire pair was born after the S ownership start, Blue-1 stopped before Blue-2 formed, and the A source time equals Blue-2 stop time.


## 12. Order Specification

### ORD-ID-001 — Physical identity

Rule-ID: ORD-ID-001  
Status: Active  
Direction: Bearish  
Phase: Order  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: One physical Order identity with canonical stop/provenance, or no Order.  
Depends-On: Canonical Reaction identity, MarketChronology.canonical_order_stop, exact stop chronology.  

**Purpose:** Defines `Physical identity` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Canonical opposite Reaction geometry, MarketChronology, parent/reset provenance, and Order ledger state.  
**Trigger:** When a parent stop or reset-leg gate requests an opposite canonical Order.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** One physical Order identity with canonical stop/provenance, or no Order.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-ORD-001  
**Test Contract:** T-E-ID plus canonical-Order rules.  

A physical Order identity is:

```python
(int(reaction.first_idx), int(reaction.break_idx))
```

Multiple accepted causes are merged into that one identity. Cause order is deduplicated while preserving insertion order in `_merge_order_candidate`.

### ORD-STOP-A-001 — Mode-A canonical stop

Rule-ID: ORD-STOP-A-001  
Status: Active  
Direction: Bearish  
Phase: Order  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: One physical Order identity with canonical stop/provenance, or no Order.  
Depends-On: Canonical Reaction identity, MarketChronology.canonical_order_stop, exact stop chronology.  

**Purpose:** Defines `Mode-A canonical stop` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Canonical opposite Reaction geometry, MarketChronology, parent/reset provenance, and Order ledger state.  
**Trigger:** When a parent stop or reset-leg gate requests an opposite canonical Order.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** One physical Order identity with canonical stop/provenance, or no Order.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-ORD-001  
**Test Contract:** T-E-ID plus canonical-Order rules.  

Source-Origin: `MarketChronology.canonical_order_stop`.

For an opposite `bullish` Order Reaction in Mode A:

- `scan_start` begins at `anchor_idx` when present, otherwise `max(start_index, first_idx - 1)`;
- scan extends backward through contiguous Main Candles with `tag == "RED"`;
- stop attribute is `low`;
- scan runs from `scan_start` through Order `break_idx`, inclusive;
- the strict outer extreme becomes `(stop_level, stop_source_index, stop_source_time)`.

### ORD-STOP-B-001 — Mode-B canonical stop

Rule-ID: ORD-STOP-B-001  
Status: Active  
Direction: Bearish  
Phase: Order  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: One physical Order identity with canonical stop/provenance, or no Order.  
Depends-On: Canonical Reaction identity, MarketChronology.canonical_order_stop, exact stop chronology.  

**Purpose:** Defines `Mode-B canonical stop` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Canonical opposite Reaction geometry, MarketChronology, parent/reset provenance, and Order ledger state.  
**Trigger:** When a parent stop or reset-leg gate requests an opposite canonical Order.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** One physical Order identity with canonical stop/provenance, or no Order.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-ORD-001  
**Test Contract:** T-E-ID plus canonical-Order rules.  

For Mode B, `reaction_number` MUST be greater than 1. The stop is inherited from the immediately previous healthy opposite Reaction.

For the opposite `bullish` Order direction, the inherited semantic edge is `box_bottom` and its matching source index/time.

### ORD-PARENT-001 — Parent-stop cause

Rule-ID: ORD-PARENT-001  
Status: Active  
Direction: Bearish  
Phase: Order  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: One physical Order identity with canonical stop/provenance, or no Order.  
Depends-On: Canonical Reaction identity, MarketChronology.canonical_order_stop, exact stop chronology.  

**Purpose:** Defines `Parent-stop cause` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Canonical opposite Reaction geometry, MarketChronology, parent/reset provenance, and Order ledger state.  
**Trigger:** When a parent stop or reset-leg gate requests an opposite canonical Order.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** One physical Order identity with canonical stop/provenance, or no Order.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-ORD-001  
**Test Contract:** T-E-ID plus canonical-Order rules.  

In E space, `_direct_parent_stop_order` searches for the first valid Order opened by an exact parent stop. Local geometry is canonicalized whenever required. A noncanonical bounded geometry can be retained only in the explicitly supported `allow_bounded_continue` path and only when `order_gate_decision == "continue"`.

### ORD-RESET-001 — Reset-leg cause

Rule-ID: ORD-RESET-001  
Status: Active  
Direction: Bearish  
Phase: Order  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: One physical Order identity with canonical stop/provenance, or no Order.  
Depends-On: Canonical Reaction identity, MarketChronology.canonical_order_stop, exact stop chronology.  

**Purpose:** Defines `Reset-leg cause` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Canonical opposite Reaction geometry, MarketChronology, parent/reset provenance, and Order ledger state.  
**Trigger:** When a parent stop or reset-leg gate requests an opposite canonical Order.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** One physical Order identity with canonical stop/provenance, or no Order.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-ORD-001  
**Test Contract:** T-E-ID plus canonical-Order rules.  

A reset-leg Order requires all of the following source conditions:

1. an opposite Reaction Reset at or after the current E lifecycle `context_start`;
2. `_reset_leg_geometry` from the owner Reaction Break through Reset Main Candle, inclusive;
3. the first strict directional boundary crossing after Reset;
4. crossing before the next non-nested opposite Reset;
5. `_reset_leg_has_simple_trend_reaction(leg_start, crossing)` — at least one non-internal trend Reaction confirmation in the leg;
6. `_first_order_b_geometry` resolves the first structurally owned post-gate geometry;
7. the geometry must resolve to a published opposite Reaction identity; local geometry alone cannot create an Order.

`_reset_leg_evidence` returns `(reset_time, crossing)` only when the selected canonical Reaction is the first owned Order_B after the gate.

### ORD-CARRIED-001 — Carried-live and inherited S Orders

Rule-ID: ORD-CARRIED-001  
Status: Active  
Direction: Bearish  
Phase: Order  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: One physical Order identity with canonical stop/provenance, or no Order.  
Depends-On: Canonical Reaction identity, MarketChronology.canonical_order_stop, exact stop chronology.  

**Purpose:** Defines `Carried-live and inherited S Orders` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Canonical opposite Reaction geometry, MarketChronology, parent/reset provenance, and Order ledger state.  
**Trigger:** When a parent stop or reset-leg gate requests an opposite canonical Order.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** One physical Order identity with canonical stop/provenance, or no Order.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-ORD-001  
**Test Contract:** T-E-ID plus canonical-Order rules.  

A Blue S may pass its own Order forward only when that Order stop did not already decide the S and the stop remains live at the S parent stop (`_unconsumed_s_orders`).

`_carried_orders_for_parent` also retains Orders created and confirmed inside an earlier parent lifecycle when their stop is still live at the current parent stop. These matches use cause `"carried-live"`; retained Reset evidence adds `"reset-leg"` as a secondary cause.

### ORD-RACE-001 — Candidate ordering

Rule-ID: ORD-RACE-001  
Status: Active  
Direction: Bearish  
Phase: Order  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: One physical Order identity with canonical stop/provenance, or no Order.  
Depends-On: Canonical Reaction identity, MarketChronology.canonical_order_stop, exact stop chronology.  

**Purpose:** Defines `Candidate ordering` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Canonical opposite Reaction geometry, MarketChronology, parent/reset provenance, and Order ledger state.  
**Trigger:** When a parent stop or reset-leg gate requests an opposite canonical Order.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** One physical Order identity with canonical stop/provenance, or no Order.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-ORD-001  
**Test Contract:** T-E-ID plus canonical-Order rules.  

`order_candidates` merges direct parent-stop, synthetic bounded reset-leg, and canonical reset-leg evidence by physical identity. The decision deadline is the earliest known Order stop, further limited by any `continuous_deadline`.

Eligible Orders must confirm no later than that deadline. Final ordering is:

1. earliest Order stop exact event (`range_end` for still-live orders),
2. earlier Reaction First time.


## 13. E Behavior Specification

### E-PARENT-001 — Parent types and strict parent stop

Rule-ID: E-PARENT-001  
Status: Active  
Direction: Bearish  
Phase: E  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: EZone objects, accepted E chain state, and E Order audit state.  
Depends-On: Accepted S state, ORD rules, lifecycle ownership, MarketChronology.  

**Purpose:** Defines `Parent types and strict parent stop` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S/E/StopAll parent state, opposite Reactions/Resets, Order candidates, MarketChronology, and lifecycle context.  
**Trigger:** After an accepted parent behavior and Order satisfy this rule's stop/decision gates.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** EZone objects, accepted E chain state, and E Order audit state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-E-001  
**Test Contract:** T-E-ID.  

E parents are accepted S, E, or a StopAll boundary reattached during reconciliation. `_parent_stop` calls `_first_parent_stop` from the parent's `decision_event_time` against parent `price`.

For Bearish, the parent stop is the first Original RAW Candle satisfying `value > level` against the parent price.

### E-ZONE-001 — Creating one E candidate

Rule-ID: E-ZONE-001  
Status: Active  
Direction: Bearish  
Phase: E  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: EZone objects, accepted E chain state, and E Order audit state.  
Depends-On: Accepted S state, ORD rules, lifecycle ownership, MarketChronology.  

**Purpose:** Defines `Creating one E candidate` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S/E/StopAll parent state, opposite Reactions/Resets, Order candidates, MarketChronology, and lifecycle context.  
**Trigger:** After an accepted parent behavior and Order satisfy this rule's stop/decision gates.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** EZone objects, accepted E chain state, and E Order audit state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-E-001  
**Test Contract:** T-E-ID.  

`_zone(family, number, parent_type, parent, stop_event)` performs the E-space Order race.

It constructs up to one representative from each applicable creation path:

- inherited unconsumed S Order,
- gate-owned initial A Order,
- carried-live Order,
- direct/reset-leg result returned by `_first_order`.

Only choices with a proven Order stop crossing participate. The winner is:

```python
min(choices, key=lambda item: (item[6][2], -int(getattr(item[1], "first_idx"))))
```

Therefore earliest exact Order-stop event wins; on the same event, the later/larger `first_idx` wins.

`decision_event_time = max(parent_stop_event_time, order_stop_event_time)`.

### E-SRC-001 — E source and price

Rule-ID: E-SRC-001  
Status: Active  
Direction: Bearish  
Phase: E  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: EZone objects, accepted E chain state, and E Order audit state.  
Depends-On: Accepted S state, ORD rules, lifecycle ownership, MarketChronology.  

**Purpose:** Defines `E source and price` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S/E/StopAll parent state, opposite Reactions/Resets, Order candidates, MarketChronology, and lifecycle context.  
**Trigger:** After an accepted parent behavior and Order satisfy this rule's stop/decision gates.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** EZone objects, accepted E chain state, and E Order audit state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-E-001  
**Test Contract:** T-E-ID.  

`_extreme_between` uses complete Main Candles from the Main Candle containing parent stop through the Main Candle containing Order stop, inclusive. RAW chronology decides whether stop events happened, but neither boundary Main Candle is truncated.

For Bearish, E `price` is the maximum High in this inclusive Main-Candle interval. Equality preserves the earlier source because `DirectionPolicy.improves` is strict.

### E-CHAIN-001 — Recursive provisional chains

Rule-ID: E-CHAIN-001  
Status: Active  
Direction: Bearish  
Phase: E  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: EZone objects, accepted E chain state, and E Order audit state.  
Depends-On: Accepted S state, ORD rules, lifecycle ownership, MarketChronology.  

**Purpose:** Defines `Recursive provisional chains` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S/E/StopAll parent state, opposite Reactions/Resets, Order candidates, MarketChronology, and lifecycle context.  
**Trigger:** After an accepted parent behavior and Order satisfy this rule's stop/decision gates.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** EZone objects, accepted E chain state, and E Order audit state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-E-001  
**Test Contract:** T-E-ID.  

`_discover_candidate_chains` first registers S-owned Order audit entries, then starts an independent E chain from every stopped S.

Initial provisional family equals `s_zone.color`; provisional number starts at 1. After each E candidate, that E becomes the next parent. The chain advances only when the immediately prior E has a strict parent stop. Provisional number increments by one per recursive stop. Duplicate `source_index` inside one chain terminates the loop.

### E-RECON-001 — Competing-chain reconciliation

Rule-ID: E-RECON-001  
Status: Active  
Direction: Bearish  
Phase: E  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: EZone objects, accepted E chain state, and E Order audit state.  
Depends-On: Accepted S state, ORD rules, lifecycle ownership, MarketChronology.  

**Purpose:** Defines `Competing-chain reconciliation` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S/E/StopAll parent state, opposite Reactions/Resets, Order candidates, MarketChronology, and lifecycle context.  
**Trigger:** After an accepted parent behavior and Order satisfy this rule's stop/decision gates.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** EZone objects, accepted E chain state, and E Order audit state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-E-001  
**Test Contract:** T-E-ID.  

`_reconcile_candidate_chains` groups candidates by `source_index`, processes groups chronologically, validates Order/parent ownership, and maintains an active accepted E set.

A candidate E stops an active prior E only when its decision is later and:

```python
zone.price > prior.price
```

Family/number are then reconciled from the accepted stopped parent state:

1. if accepted parent family is Red, new family is Red;
2. else if any stopped Red E exists, new family is Red;
3. else if accepted parent family is Blue, new family is Blue;
4. else if any stopped Blue E exists, new family is Blue;
5. otherwise retain provisional family.

Within a family, number becomes one greater than the maximum stopped E number of that family when such a stopped E exists; otherwise number is 1.

Red is dominant over Blue in cross-family ownership. A lower-priority S cannot steal an active E continuation. A Red S may supersede Blue E, but no S supersedes Red E under the documented reconciliation checks.

### E-RESET-001 — StopAll sequence reset integration

Rule-ID: E-RESET-001  
Status: Active  
Direction: Bearish  
Phase: E  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: EZone objects, accepted E chain state, and E Order audit state.  
Depends-On: Accepted S state, ORD rules, lifecycle ownership, MarketChronology.  

**Purpose:** Defines `StopAll sequence reset integration` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S/E/StopAll parent state, opposite Reactions/Resets, Order candidates, MarketChronology, and lifecycle context.  
**Trigger:** After an accepted parent behavior and Order satisfy this rule's stop/decision gates.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** EZone objects, accepted E chain state, and E Order audit state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-E-001  
**Test Contract:** T-E-ID.  

When an accepted E source time appears in `sequence_resets`, the active E set is cleared and `sequence_start` is moved to that source. A later candidate whose parent source equals a StopAll boundary is re-labeled with `parent_type = "StopAll"` so pre-boundary family/number state does not leak across the hard lifecycle reset.

### E-AUD-001 — Accepted Order Audit

Rule-ID: E-AUD-001  
Status: Active  
Direction: Bearish  
Phase: E  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: EZone objects, accepted E chain state, and E Order audit state.  
Depends-On: Accepted S state, ORD rules, lifecycle ownership, MarketChronology.  

**Purpose:** Defines `Accepted Order Audit` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S/E/StopAll parent state, opposite Reactions/Resets, Order candidates, MarketChronology, and lifecycle context.  
**Trigger:** After an accepted parent behavior and Order satisfy this rule's stop/decision gates.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** EZone objects, accepted E chain state, and E Order audit state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-E-001  
**Test Contract:** T-E-ID.  

`_rebuild_accepted_order_audit` clears provisional audit state and rebuilds it only from accepted S/E/StopAll parents and accepted E objects.

Every Order embedded in an accepted E is effective by definition and is reinserted into the ledger if not already present, provided its physical Reaction identity resolves to a canonical opposite Reaction.

Reset-leg evidence may be retained as a secondary cause without changing Order selection.


## 14. StopAll Specification

### LIF-PRIO-001 — Sequence priority

Rule-ID: LIF-PRIO-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Lifecycle  
Implementation-Class: Shared  
Requires-RAW: Conditional  
Produces: Accepted/invalid ownership partitions and lifecycle state.  
Depends-On: Calculated behavior collections and exact stop provenance.  

**Purpose:** Defines `Sequence priority` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Calculated A/S/E/StopAll objects, exact stop finders, Main Candles, and ownership state.  
**Trigger:** During post-calculation ownership reconciliation.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Accepted/invalid ownership partitions and lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Conditional; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-INT-001  
**Test Contract:** T-STOPALL and T-INTERNAL.  

`SEQUENCE_PRIORITY` is exactly:

| Sequence | Priority |
| --- | ---: |
| S Blue | 1 |
| E Blue | 2 |
| S Red | 3 |
| E Red | 4 |

Higher numeric value is higher sequence priority.

`module_priority` used by visibility is:

| Module | Priority |
| --- | ---: |
| S Blue | 1 |
| E Blue | 2 |
| S Red | 3 |
| E Red | 4 |
| StopAll | 5 |

### STP-001 — Strict StopAll stop

Rule-ID: STP-001  
Status: Active  
Direction: Bearish  
Phase: StopAll  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: StopAll objects and exact StopAll stop state.  
Depends-On: Accepted S/E state, sequence priority, exact strict-stop chronology.  

**Purpose:** Defines `Strict StopAll stop` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S zones, reconciled E zones, MarketChronology, and active StopAll state.  
**Trigger:** While accepted E decisions are processed against active sequence/StopAll state.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** StopAll objects and exact StopAll stop state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-STP-001  
**Test Contract:** T-STOPALL.  

`StopAllDetector._strict_stop` scans Original RAW Candles from StopAll `decision_event_time`. The current direction's `DirectionPolicy` determines strict `<` or `>` against StopAll `price`. The exact RAW event and owning Main Candle are stored.

### STP-SEQ-001 — `sequence-group-stop`

Rule-ID: STP-SEQ-001  
Status: Active  
Direction: Bearish  
Phase: StopAll  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: StopAll objects and exact StopAll stop state.  
Depends-On: Accepted S/E state, sequence priority, exact strict-stop chronology.  

**Purpose:** Defines ``sequence-group-stop`` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S zones, reconciled E zones, MarketChronology, and active StopAll state.  
**Trigger:** While accepted E decisions are processed against active sequence/StopAll state.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** StopAll objects and exact StopAll stop state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-STP-001  
**Test Contract:** T-STOPALL.  

Before each accepted E decision, S events with earlier `source_time` update the active sequence group according to `SEQUENCE_PRIORITY`.

A sequence qualifies only when:

- active E group count is at least 2, or
- no E group owns the sequence and active same-color S count is at least 2.

The latest member of that qualifying group is checked for a strict stop. If its exact stop occurs no later than the current E decision, the current E is converted to `StopAll1` with `gate_type = "sequence-group-stop"`. The current E supplies the winning Order fields even if its family/number differs from the stopped group.

### STP-CHAIN-001 — `stopall-stop`

Rule-ID: STP-CHAIN-001  
Status: Active  
Direction: Bearish  
Phase: StopAll  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: StopAll objects and exact StopAll stop state.  
Depends-On: Accepted S/E state, sequence priority, exact strict-stop chronology.  

**Purpose:** Defines ``stopall-stop`` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S zones, reconciled E zones, MarketChronology, and active StopAll state.  
**Trigger:** While accepted E decisions are processed against active sequence/StopAll state.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** StopAll objects and exact StopAll stop state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-STP-001  
**Test Contract:** T-STOPALL.  

Every active StopAll is checked for a strict stop before each E decision. If one or more active StopAll objects have stopped, the current E creates the next StopAll:

- number = highest stopped StopAll number + 1;
- `gate_type = "stopall-stop"`;
- `gate_event_time` = earliest exact stop among the stopped active StopAll objects;
- sequence S/E group counters are reset.

### STP-OUT-001 — StopAll own stop fields

Rule-ID: STP-OUT-001  
Status: Active  
Direction: Bearish  
Phase: StopAll  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: StopAll objects and exact StopAll stop state.  
Depends-On: Accepted S/E state, sequence priority, exact strict-stop chronology.  

**Purpose:** Defines `StopAll own stop fields` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S zones, reconciled E zones, MarketChronology, and active StopAll state.  
**Trigger:** While accepted E decisions are processed against active sequence/StopAll state.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** StopAll objects and exact StopAll stop state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-STP-001  
**Test Contract:** T-STOPALL.  

After StopAll creation finishes, each emitted StopAll is independently scanned for its first future strict stop. `stopIndex`, `stopTime`, and `stopEventTime` are null when no strict stop exists in the available RAW range.

### STP-RECON-001 — E/StopAll fixed-point reconciliation

Rule-ID: STP-RECON-001  
Status: Active  
Direction: Bearish  
Phase: StopAll  
Implementation-Class: Shared direction-parameterized  
Requires-RAW: Yes  
Produces: StopAll objects and exact StopAll stop state.  
Depends-On: Accepted S/E state, sequence priority, exact strict-stop chronology.  

**Purpose:** Defines `E/StopAll fixed-point reconciliation` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Accepted S zones, reconciled E zones, MarketChronology, and active StopAll state.  
**Trigger:** While accepted E decisions are processed against active sequence/StopAll state.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** StopAll objects and exact StopAll stop state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-STP-001  
**Test Contract:** T-STOPALL.  

`reconcile_stopall_lifecycle` repeatedly:

1. computes S objects eligible for module engines,
2. detects StopAll,
3. converts StopAll source times to `sequence_resets`,
4. reruns E when this mapping changed.

The loop terminates only when `sequence_resets` is unchanged. Repeating a previously seen mapping is an error (`E/StopAll lifecycle reconciliation did not converge`).

StopAll is a hard lifecycle boundary. Accepted family/number ownership from before the boundary MUST NOT propagate into the next sequence.


## 15. Lifecycle, Calculation, and Visibility

### LIF-001 — Separation of concerns

Rule-ID: LIF-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Lifecycle  
Implementation-Class: Shared  
Requires-RAW: Conditional  
Produces: Accepted/invalid ownership partitions and lifecycle state.  
Depends-On: Calculated behavior collections and exact stop provenance.  

**Purpose:** Defines `Separation of concerns` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Calculated A/S/E/StopAll objects, exact stop finders, Main Candles, and ownership state.  
**Trigger:** During post-calculation ownership reconciliation.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Accepted/invalid ownership partitions and lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Conditional; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-INT-001  
**Test Contract:** T-STOPALL and T-INTERNAL.  

The detector stages first calculate candidates. Lifecycle functions then reconcile ownership. Visibility functions finally decide what is serialized. An object may therefore be calculated yet not public.

### LIF-A-001 — Dominant-stop A ownership

Rule-ID: LIF-A-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Lifecycle  
Implementation-Class: Shared  
Requires-RAW: Conditional  
Produces: Accepted/invalid ownership partitions and lifecycle state.  
Depends-On: Calculated behavior collections and exact stop provenance.  

**Purpose:** Defines `Dominant-stop A ownership` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Calculated A/S/E/StopAll objects, exact stop finders, Main Candles, and ownership state.  
**Trigger:** During post-calculation ownership reconciliation.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Accepted/invalid ownership partitions and lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Conditional; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-INT-001  
**Test Contract:** T-STOPALL and T-INTERNAL.  

`split_a_zones_by_dominant_stops` evaluates accepted S/E/StopAll strict stop events chronologically by their containing Main Candle. The newest stopped Main Candle owns the transition; priority/number resolve owners stopped in the same Main Candle.

An A whose price does not strictly move beyond the dominant stopped owner remains valid. An A that strictly moves beyond it becomes an invalid leg-head candidate and is not public, while consuming lower/equal stopped owners for later half-leg discovery. Equality remains valid.

There is one source-derived provenance exception: a confirmed trend Reaction may establish an interior directional leg head between the owner stop and A First. In that case the A may remain valid even though its price is beyond the old owner boundary, provided the exact Reaction/index conditions in `split_a_zones_by_dominant_stops` are satisfied.

### LIF-ORD-001 — Invalid leg-head Order blocking

Rule-ID: LIF-ORD-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Lifecycle  
Implementation-Class: Shared  
Requires-RAW: Conditional  
Produces: Accepted/invalid ownership partitions and lifecycle state.  
Depends-On: Calculated behavior collections and exact stop provenance.  

**Purpose:** Defines `Invalid leg-head Order blocking` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Calculated A/S/E/StopAll objects, exact stop finders, Main Candles, and ownership state.  
**Trigger:** During post-calculation ownership reconciliation.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Accepted/invalid ownership partitions and lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Conditional; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-INT-001  
**Test Contract:** T-STOPALL and T-INTERNAL.  

`blocked_orders_while_invalid_leg_heads_are_live` blocks opposite Reaction First times from an invalid A `source_time` until that invalid A itself experiences its strict stop. Accepted stopped-A Order identities override this provisional block through `resolve_order_context`.

### LIF-S-001 — S eligibility for E/StopAll engines

Rule-ID: LIF-S-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Lifecycle  
Implementation-Class: Shared  
Requires-RAW: Conditional  
Produces: Accepted/invalid ownership partitions and lifecycle state.  
Depends-On: Calculated behavior collections and exact stop provenance.  

**Purpose:** Defines `S eligibility for E/StopAll engines` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Calculated A/S/E/StopAll objects, exact stop finders, Main Candles, and ownership state.  
**Trigger:** During post-calculation ownership reconciliation.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Accepted/invalid ownership partitions and lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Conditional; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-INT-001  
**Test Contract:** T-STOPALL and T-INTERNAL.  

`s_zones_for_module_engines` keeps S independent inside the current half-leg but prevents an S from crossing back through the most recent E/S module boundary using either its parent `a_price` or its own `price`.

### LIF-S-002 — Final S visibility after larger-module stops

Rule-ID: LIF-S-002  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Lifecycle  
Implementation-Class: Shared  
Requires-RAW: Conditional  
Produces: Accepted/invalid ownership partitions and lifecycle state.  
Depends-On: Calculated behavior collections and exact stop provenance.  

**Purpose:** Defines `Final S visibility after larger-module stops` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Calculated A/S/E/StopAll objects, exact stop finders, Main Candles, and ownership state.  
**Trigger:** During post-calculation ownership reconciliation.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Accepted/invalid ownership partitions and lifecycle state.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Conditional; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-INT-001  
**Test Contract:** T-STOPALL and T-INTERNAL.  

`visible_s_zones_after_module_resets` processes S chronologically against accepted E/StopAll and earlier visible S. The most recent stopped larger-module lifecycle is authoritative; old higher-priority historical objects do not own every later leg forever.

A newly confirmed higher-priority S can supersede a stopped lower-priority S owner. Otherwise a would-be S is consumed only when its own directional price is strictly beyond the dominant stopped owner according to `DirectionPolicy.strict_cross`. Equality stays with the earlier owner.

### VIS-A-001 — A occupied-source rules

Rule-ID: VIS-A-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Visibility  
Implementation-Class: Shared  
Requires-RAW: No  
Produces: Final public A/S/E/StopAll collections.  
Depends-On: LIF rules plus accepted lineage.  

**Purpose:** Defines `A occupied-source rules` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Calculated/reconciled behaviors and occupied-source/lineage state.  
**Trigger:** During final public visibility reconciliation.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Final public A/S/E/StopAll collections.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** No; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-INT-001  
**Test Contract:** T-INTERNAL.  

`visible_a_zones` removes A labels whose `source_index` is occupied by a final S. `visible_a_zones_after_s_stops` also removes the A label on a Main Candle that contains an already-confirmed S stop.

`visible_a_zones_after_module_boundaries` removes an A whose provenance (`blue_1_source_time`, `blue_2_source_time`, `continuation_source_time`, `reaction_first_time`) straddles the latest dominant stopped S/E/StopAll boundary.

### VIS-FINAL-001 — Final lineage closure

Rule-ID: VIS-FINAL-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Visibility  
Implementation-Class: Shared  
Requires-RAW: No  
Produces: Final public A/S/E/StopAll collections.  
Depends-On: LIF rules plus accepted lineage.  

**Purpose:** Defines `Final lineage closure` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Calculated/reconciled behaviors and occupied-source/lineage state.  
**Trigger:** During final public visibility reconciliation.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Final public A/S/E/StopAll collections.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** No; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-INT-001  
**Test Contract:** T-INTERNAL.  

`finalize_behavior_visibility`:

1. removes E objects whose source index is occupied by StopAll;
2. resolves final S visibility against accepted E/StopAll;
3. re-adds historical S parents referenced by accepted E lineage;
4. resolves A after module boundaries;
5. re-adds historical A parents referenced by accepted S lineage;
6. removes A/S whose source index is occupied by final E or StopAll;
7. removes S identities classified invalid during calculation reconciliation.

### INT-BEH-001 — Final Internal-Reaction veto

Rule-ID: INT-BEH-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: Internal-Reaction Visibility  
Implementation-Class: Shared  
Requires-RAW: Conditional  
Produces: Internal-Reaction-filtered public behavior collections.  
Depends-On: INT-REA-001, accepted behavior lineage, Order provenance.  

**Purpose:** Defines `Final Internal-Reaction veto` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Visible behavior candidates, healthy Reaction interiors, internal Reaction identities, and Order provenance.  
**Trigger:** After ordinary lifecycle visibility and internal-Reaction metadata are available.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Internal-Reaction-filtered public behavior collections.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Conditional; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-INT-001  
**Test Contract:** T-INTERNAL.  

`filter_internal_behavior_outputs` removes:

- A whose `(source_time, price)` is strictly inside any healthy Reaction interior;
- S with the same interior condition, except `color == "blue" and formation_type == "advanced"`;
- S whose `reset_reaction_number` resolves to an internal opposite Reaction;
- E/StopAll inside a healthy Reaction interior;
- E/StopAll whose physical Order Reaction is internal **only when** the Order carries reset-leg provenance (`forbidden_internal_order_b`).

Direct parent-stop and carried-live Orders are not rejected merely because the same physical Reaction is internal to this specific reset-leg veto.


## 16. RAW Chronology and Ambiguity Rules

### RAW-001 — Exact event authority

Rule-ID: RAW-001  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: RAW Chronology  
Implementation-Class: Shared  
Requires-RAW: Yes  
Produces: Exact RAW event position/time/extreme or an explicit no-event/ambiguity result.  
Depends-On: INV-002, INV-003, INV-004, Main/RAW timestamp indexes.  

**Purpose:** Defines `Exact event authority` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Original RAW Candle sequence, exact event timestamps, strict levels, and Main Candle time index.  
**Trigger:** When an exact event or tie must be resolved below Main-Candle granularity.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Exact RAW event position/time/extreme or an explicit no-event/ambiguity result.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-RST-001 / EX-S-001  
**Test Contract:** T-RAW-CONF, T-REA-TIE, and T-S-AMBIG.  

Exact event chronology MUST use Original RAW Candles for:

- Reaction confirmation;
- Reset versus Reaction confirmation competition;
- Mode-A owner invalidation versus confirmation;
- post-confirmation Reset;
- Blue Reset formation;
- Blue pending strike confirmation;
- Blue stops used by A;
- A pair trigger crossings;
- A stop;
- S candidate crossing;
- S Order-stop crossing;
- E parent stop;
- E Order stop;
- Reset-leg boundary crossing;
- StopAll stop.

### RAW-002 — Same RAW Candle ambiguity

Rule-ID: RAW-002  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: RAW Chronology  
Implementation-Class: Shared  
Requires-RAW: Yes  
Produces: Exact RAW event position/time/extreme or an explicit no-event/ambiguity result.  
Depends-On: INV-002, INV-003, INV-004, Main/RAW timestamp indexes.  

**Purpose:** Defines `Same RAW Candle ambiguity` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Original RAW Candle sequence, exact event timestamps, strict levels, and Main Candle time index.  
**Trigger:** When an exact event or tie must be resolved below Main-Candle granularity.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Exact RAW event position/time/extreme or an explicit no-event/ambiguity result.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-RST-001 / EX-S-001  
**Test Contract:** T-RAW-CONF, T-REA-TIE, and T-S-AMBIG.  

When two competing strict events can both be true from one RAW Candle's OHLC and the source cannot determine their internal order, the implementation MUST follow the explicit source branch rather than invent a path.

The clearest example is `SZoneDetector._decision`: simultaneous `candidate_cross` and `order_cross` returns `None`.

Reaction competition has its own explicit tie rule: Reset/invalidation wins a true equal RAW position because those methods compare positions with `<=`.

### RAW-003 — No Main Candle path assumption

Rule-ID: RAW-003  
Status: Active  
Direction: Shared; reproduced inside the Bearish standalone specification  
Phase: RAW Chronology  
Implementation-Class: Shared  
Requires-RAW: Yes  
Produces: Exact RAW event position/time/extreme or an explicit no-event/ambiguity result.  
Depends-On: INV-002, INV-003, INV-004, Main/RAW timestamp indexes.  

**Purpose:** Defines `No Main Candle path assumption` exactly as implemented by the frozen production baseline.  
**Preconditions:** Every predecessor object and guard explicitly stated in the normative body below MUST exist or pass; otherwise this rule produces no result.  
**Inputs:** Original RAW Candle sequence, exact event timestamps, strict levels, and Main Candle time index.  
**Trigger:** When an exact event or tie must be resolved below Main-Candle granularity.  
**Calculation:** The body below is normative and MUST be applied in the written/source decision order.  
**Validation:** Every strict comparator, index/time gate, canonical-identity check, and early-exit condition stated below is mandatory.  
**Output:** Exact RAW event position/time/extreme or an explicit no-event/ambiguity result.  
**State Effect:** Only state changes explicitly stated below are permitted; no additional ownership or visibility effect may be inferred.  
**Invalid If:** Any mandatory guard below fails, a required canonical object is missing, or a required exact event cannot be established under the stated source rule.  
**Exceptions:** Only exceptions explicitly stated in this rule or a referenced Rule-ID apply.  
**Priority:** Branch/order precedence in the body below is normative.  
**RAW Chronology:** Yes; when exact chronology is required, Original RAW Candles are authoritative.  
**Pseudocode:** Inline code plus Section 23 use production identifiers; no teaching aliases are authoritative.  
**Worked Example:** EX-RST-001 / EX-S-001  
**Test Contract:** T-RAW-CONF, T-REA-TIE, and T-S-AMBIG.  

A Main Candle MUST NOT be interpreted as Open→High→Low→Close or Open→Low→High→Close. Only RAW row order can resolve intrabar chronology.


## 17. Tie and Equality Rules

1. Doji equality (`open == close`) is GREEN.
2. Directional strict stop equality is not a stop.
3. `DirectionPolicy.improves` equality does not move the source; earliest owner is preserved unless a method explicitly uses a better-or-equal rule.
4. `LowerTimeframeIndex.range_minimum` and `range_maximum` retain the earliest RAW position on equal extrema.
5. `SZoneDetector._candidate_source_last` is an explicit exception: equal candidate extrema move ownership to the last Main Candle.
6. `_candidate_timing` assigns equality to the `after` case.
7. Reaction Reset/invalidation versus confirmation at the same RAW position resolves to Reset/invalidation.
8. S candidate cross and Order stop true in the same RAW Candle produce no S decision.
9. E Order winner ties on exact Order-stop event are resolved by larger `first_idx` because `_zone` sorts with `-first_idx`.
10. Output Order Audit is sorted by `(firstTime, breakTime)`.


## 18. Invalid and Non-Producing Cases

The following source conditions produce no public object or terminate the current candidate path:

- no initial Reaction can be confirmed;
- a Mode-A Reaction owner boundary strictly invalidates before confirmation;
- a post-Reset direct owner never confirms;
- Scale Blue strike count does not increase versus prior Reaction;
- Blue spacing does not permit a new Blue;
- Reset Blue double-stop rule sets `calculation_valid=False` for ordinary use;
- A pair lacks required Blue stops, trigger crossing, or validating Reaction;
- special double-stop A local crossing does not occur on the invalid Blue source Main Candle;
- A is consumed by active S ownership without the Reset-Reset preemption exception;
- A stop never occurs;
- Type3 lacks eligible Reset, boundary crossing, or trend-Reaction evidence;
- Order local geometry cannot canonicalize where canonical identity is required;
- S candidate and Order stop are ambiguous in the same RAW Candle;
- S decision never obtains Blue evidence or Order-stop Red decision;
- E parent never stops;
- E has no stopped Order candidate;
- recursive E repeats a source index within the same provisional chain;
- lifecycle reconciliation rejects parent ownership or an invalid Order;
- Internal-Reaction final veto removes public output;
- StopAll sequence group is shorter than two or its dominant parent never strictly stops;
- E/StopAll reconciliation enters a previously seen sequence-reset mapping, which is an error rather than partial output.


## 19. Public Output Schema

All serialized prices are decimal strings. All serialized timestamps are integer epoch seconds produced by reattaching Asia/Tehran to project-local datetimes.

The exact public field names are normative.


### Reaction

| Field | Type | Meaning |
| --- | --- | --- |
| firstIndex | int | Main Candle index of First. |
| firstTime | epoch int | Main Candle start time of First. |
| boxTopSourceIndex | int | Main Candle index owning boxTop. |
| boxTopSourceTime | epoch int | Main Candle start time owning boxTop. |
| boxTop | decimal string | Published Reaction upper boundary. |
| boxBottomSourceIndex | int | Main Candle index owning boxBottom. |
| boxBottomSourceTime | epoch int | Main Candle start time owning boxBottom. |
| boxBottom | decimal string | Published Reaction lower boundary. |
| breakIndex | int | Main Candle index that strictly confirms the Reaction. |
| breakTime | epoch int | Main Candle start time of breakIndex. |
| mode | string | "A" or "B". |

### Reset

| Field | Type | Meaning |
| --- | --- | --- |
| index | int | Main Candle index containing the Reset. |
| time | epoch int | Main Candle start time. |
| secondTime | epoch int | null | Exact RAW Reset time when explicitly recorded after confirmation; otherwise null. |
| brokenLevel | decimal string | Strictly broken Reaction boundary. |
| fromFirstIndex | int | First index of the Reaction being reset. |

### BlueLine

| Field | Type | Meaning |
| --- | --- | --- |
| direction | string | Trend direction. |
| kind | string | "scale" or "reset". |
| reactionNumber | int | 1-based owner Reaction number. |
| previousStrikeCount | int | null | Prior Reaction strike count for Scale Blue. |
| strikeCount | int | null | Current strike count for Scale Blue. |
| fibonacciLevel | decimal string | null | 0.618 level for Scale Blue. |
| sourceIndex | int | Main Candle index of decisive source. |
| sourceTime | epoch int | Main source time. |
| sourceExtreme | decimal string | Calculation-owned directional extreme. |
| brokenLevel | decimal string | null | Reset level for Reset Blue. |
| linePrice | decimal string | Rendered Blue line price. |
| startTime | epoch int | sourceTime minus one Main timeframe. |
| endTime | epoch int | sourceTime plus one Main timeframe. |

### AZone

| Field | Type | Meaning |
| --- | --- | --- |
| direction | string | Trend direction. |
| blue1Ordinal | int | 1-based first Blue ordinal. |
| blue2Ordinal | int | 1-based second Blue ordinal. |
| blue1SourceTime | epoch int | First Blue source time. |
| blue2SourceTime | epoch int | Second Blue source time. |
| blue1StopTime | epoch int | Effective first Blue stop Main time. |
| blue2StopTime | epoch int | Effective second Blue stop Main time. |
| blue1StopLevel | decimal string | First Blue sourceExtreme. |
| blue2StopLevel | decimal string | Second Blue sourceExtreme. |
| continuationLevel | decimal string | A continuation boundary used by pair trigger. |
| continuationSourceIndex | int | Main Candle owning continuationLevel. |
| continuationSourceTime | epoch int | Main time owning continuationLevel. |
| triggerIndex | int | Main Candle containing exact trigger event. |
| triggerTime | epoch int | Main Candle start time containing trigger. |
| triggerEventTime | epoch int | Exact RAW trigger time. |
| reactionNumber | int | 1-based validating trend Reaction. |
| reactionFirstTime | epoch int | Validating Reaction First Main time. |
| reactionBreakTime | epoch int | Validating Reaction Break Main time. |
| sourceIndex | int | Main Candle owning A price. |
| sourceTime | epoch int | A source Main time. |
| price | decimal string | A directional extreme. |
| calculationValid | bool | Always true for serialized accepted A objects. |

### SZone

| Field | Type | Meaning |
| --- | --- | --- |
| direction | string | Trend direction. |
| color | string | "blue" or "red". |
| formationType | string | "simple", "advanced", or "type3". |
| aOrdinal | int | 1-based A ordinal. |
| aSourceIndex | int | Parent A source index. |
| aSourceTime | epoch int | Parent A source time. |
| aPrice | decimal string | Parent A price. |
| aStopIndex | int | Main Candle containing strict A stop. |
| aStopTime | epoch int | Main start time containing strict A stop. |
| aStopEventTime | epoch int | Exact RAW A stop time. |
| orderDirection | string | null | Opposite Order direction; null for Type3. |
| orderReactionNumber | int | null | 1-based opposite Reaction number; null for Type3. |
| orderMode | string | null | Order Reaction mode; null for Type3. |
| orderFirstIndex | int | null | Order First index. |
| orderFirstTime | epoch int | null | Order First Main time. |
| orderBreakIndex | int | null | Order Break index. |
| orderBreakTime | epoch int | null | Order Break Main time. |
| orderConfirmationTime | epoch int | null | Exact RAW order confirmation. |
| orderBoxTop | decimal string | null | Order boxTop. |
| orderBoxTopSourceIndex | int | null | Order boxTop source index. |
| orderBoxTopSourceTime | epoch int | null | Order boxTop source Main time. |
| orderBoxBottom | decimal string | null | Order boxBottom. |
| orderBoxBottomSourceIndex | int | null | Order boxBottom source index. |
| orderBoxBottomSourceTime | epoch int | null | Order boxBottom source Main time. |
| orderStopLevel | decimal string | null | Canonical Order stop. |
| orderStopSourceIndex | int | null | Main Candle owning Order stop. |
| orderStopSourceTime | epoch int | null | Order stop source Main time. |
| resetReactionNumber | int | null | Type3 Reset owner Reaction number. |
| resetTime | epoch int | null | Exact Reset time for Type3. |
| sourceIndex | int | S source Main index. |
| sourceTime | epoch int | S source Main time. |
| price | decimal string | S directional extreme. |
| decisionIndex | int | Main Candle containing S decision event. |
| decisionTime | epoch int | Decision Main time. |
| decisionEventTime | epoch int | Exact RAW decision event. |
| calculationValid | bool | Always true for serialized accepted S objects. |

### EZone

| Field | Type | Meaning |
| --- | --- | --- |
| direction | string | Trend direction. |
| family | string | "blue" or "red". |
| number | int | Reconciled E number. |
| parentType | string | "S", "E", or "StopAll" after reconciliation. |
| parentSourceIndex | int | Parent source index. |
| parentSourceTime | epoch int | Parent source time. |
| parentPrice | decimal string | Parent behavior price. |
| parentStopIndex | int | Main Candle containing parent stop. |
| parentStopTime | epoch int | Parent-stop Main time. |
| parentStopEventTime | epoch int | Exact RAW parent stop. |
| orderDirection | string | Opposite Order direction. |
| orderReactionNumber | int | 1-based canonical Reaction number, or zero only for bounded continue geometry admitted by E. |
| orderMode | string | Order mode. |
| orderCauses | array[string] | Physical Order provenance such as parent-stop, reset-leg, carried-live. |
| orderParentStopCauseTime | epoch int | null | Parent-stop creation event when retained. |
| orderResetLegResetTime | epoch int | null | Reset-leg reset event. |
| orderResetLegBreakTime | epoch int | null | Strict reset-leg boundary break event. |
| orderFirstIndex | int | Order First index. |
| orderFirstTime | epoch int | Order First Main time. |
| orderBreakIndex | int | Order Break index. |
| orderBreakTime | epoch int | Order Break Main time. |
| orderConfirmationTime | epoch int | Exact RAW Order confirmation. |
| orderBoxTop | decimal string | Order boxTop. |
| orderBoxTopSourceIndex | int | Order boxTop source index. |
| orderBoxTopSourceTime | epoch int | Order boxTop source Main time. |
| orderBoxBottom | decimal string | Order boxBottom. |
| orderBoxBottomSourceIndex | int | Order boxBottom source index. |
| orderBoxBottomSourceTime | epoch int | Order boxBottom source Main time. |
| orderStopLevel | decimal string | Canonical Order stop. |
| orderStopSourceIndex | int | Order stop source index. |
| orderStopSourceTime | epoch int | Order stop source Main time. |
| sourceIndex | int | E source Main index. |
| sourceTime | epoch int | E source Main time. |
| price | decimal string | E directional extreme. |
| decisionIndex | int | Main decision index. |
| decisionTime | epoch int | Decision Main time. |
| decisionEventTime | epoch int | Exact RAW decision event. |

### StopAll

| Field | Type | Meaning |
| --- | --- | --- |
| direction | string | Trend direction. |
| number | int | StopAll sequence number. |
| sourceIndex | int | Underlying accepted E source index. |
| sourceTime | epoch int | Underlying accepted E source time. |
| price | decimal string | StopAll price copied from underlying E. |
| decisionIndex | int | Decision Main index. |
| decisionTime | epoch int | Decision Main time. |
| decisionEventTime | epoch int | Exact RAW E decision event. |
| gateType | string | "sequence-group-stop" or "stopall-stop". |
| gateEventTime | epoch int | Exact RAW gate stop event. |
| stoppedBehaviorType | string | "S", "E", or "StopAll". |
| stoppedBehaviorKey | string | Human-readable stopped sequence key. |
| stoppedBehaviorCount | int | Count of stopped members represented by gate. |
| underlyingEFamily | string | Family of E used to create StopAll. |
| underlyingENumber | int | E number used to create StopAll. |
| orderDirection | string | Underlying E Order direction. |
| orderReactionNumber | int | Underlying E Order Reaction number. |
| orderMode | string | Underlying E Order mode. |
| orderCauses | array[string] | Underlying E Order causes. |
| orderParentStopCauseTime | epoch int | null | Underlying E parent-stop cause. |
| orderResetLegResetTime | epoch int | null | Underlying E reset-leg Reset. |
| orderResetLegBreakTime | epoch int | null | Underlying E reset-leg boundary break. |
| orderFirstIndex | int | Underlying Order First index. |
| orderFirstTime | epoch int | Underlying Order First time. |
| orderBreakIndex | int | Underlying Order Break index. |
| orderBreakTime | epoch int | Underlying Order Break time. |
| orderConfirmationTime | epoch int | Underlying exact Order confirmation. |
| orderBoxTop | decimal string | Underlying Order boxTop. |
| orderBoxTopSourceIndex | int | Underlying Order boxTop source index. |
| orderBoxTopSourceTime | epoch int | Underlying Order boxTop source Main time. |
| orderBoxBottom | decimal string | Underlying Order boxBottom. |
| orderBoxBottomSourceIndex | int | Underlying Order boxBottom source index. |
| orderBoxBottomSourceTime | epoch int | Underlying Order boxBottom source Main time. |
| orderStopLevel | decimal string | Underlying canonical Order stop. |
| orderStopSourceIndex | int | Underlying Order stop source index. |
| orderStopSourceTime | epoch int | Underlying Order stop source Main time. |
| stopIndex | int | null | Main Candle containing StopAll strict stop. |
| stopTime | epoch int | null | StopAll stop Main time. |
| stopEventTime | epoch int | null | Exact RAW StopAll stop time. |

### OrderAudit

| Field | Type | Meaning |
| --- | --- | --- |
| direction | string | Order direction. |
| reactionNumber | int | Public Reaction number when available, else audit reaction number. |
| reactionMode | string | Order Reaction mode. |
| firstIndex | int | Order First index. |
| firstTime | epoch int | Order First Main time. |
| boxTopSourceIndex | int | Order boxTop source index. |
| boxTopSourceTime | epoch int | Order boxTop source Main time. |
| boxTop | decimal string | Order boxTop. |
| boxBottomSourceIndex | int | Order boxBottom source index. |
| boxBottomSourceTime | epoch int | Order boxBottom source Main time. |
| boxBottom | decimal string | Order boxBottom. |
| breakIndex | int | Order Break index. |
| breakTime | epoch int | Order Break Main time. |
| stopLevel | decimal string | Canonical Order stop. |
| stopSourceIndex | int | Canonical stop source index. |
| stopSourceTime | epoch int | Canonical stop source Main time. |
| stopHitIndex | int | null | Main Candle containing strict stop crossing. |
| stopHitTime | epoch int | null | Stop hit Main time. |
| stopHitEventTime | epoch int | null | Exact RAW stop hit event. |
| causes | array[object] | Merged creation causes; parent-stop or reset-leg. |

`causes` is serialized in source order from `prepared["causes"]`. Each cause object uses one of these exact schemas:

**parent-stop cause**

| Field | Type | Meaning |
| --- | --- | --- |
| kind | string | Exact cause discriminator; value is `parent-stop`. |
| parentType | string | Parent behavior type recorded by the Order resolver. |
| parentFamily | string | Parent family recorded by the Order resolver. |
| eventTime | epoch int | Exact cause event time serialized from `cause["eventTime"]`. |
| parentSourceTime | epoch int | Parent source time serialized from `cause["parentSourceTime"]`. |

**reset-leg cause**

| Field | Type | Meaning |
| --- | --- | --- |
| kind | string | Exact cause discriminator; value is `reset-leg`. |
| resetTime | epoch int | Reset time serialized from `cause["resetTime"]`. |
| boundaryBreakTime | epoch int | Exact reset-leg boundary break time serialized from `cause["boundaryBreakTime"]`. |


### Public response envelope

The response contains engine/module version fields, enable flags, requested timeframe, `actualFrom`, `actualTo`, a `directions` object keyed by requested trend direction, and timing telemetry. Each direction payload contains:

```text
reactions
resets
blueLines
aZones
sZones
eZones
stopAlls
orderAudit
```

`reactions` and `resets` are always serialized from Reaction results. Blue/A/S can be disabled by configuration. E requires an E engine and S enabled. StopAll requires lifecycle + E + S.


## 20. State Machines

### Reaction

```text
Mode A SCANNING
→ Mode A WAITING candidate
→ strict confirmation
→ Mode B SCANNING
→ Mode B WAITING candidate
→ strict confirmation
→ ...

Any confirmed-Reaction Reset
→ new Mode A ownership search

Post-confirmation same-Main-Candle Reset
→ fresh Mode A search; Break Candle remainder cannot seed successor
```

### A

```text
Blue formation
→ Blue strict stop state
→ adjacent valid Blue pair / special double-stop pair
→ pair trigger
→ validating trend Reaction
→ A source selection
→ A active
→ first strict A stop
```

### S

```text
A exact stop
→ Type3 attempt before Order deadline
→ otherwise opposite Order
→ pre-order Simple OR Advanced nested OR post-order Simple
→ RAW candidate/Order-stop race
→ S Blue or S Red
```

### E

```text
Accepted S strict stop
→ E Order race
→ E1
→ E1 strict stop
→ E2
→ ... En
→ reconciliation across competing chains and families
```

### StopAll

```text
Dominant S/E sequence count >= 2 + strict group stop
→ StopAll1

StopAllN strict stop + later accepted E
→ StopAll(N+1)

StopAll source
→ hard E-family/number sequence reset
```


## 21. Direction-Specific Summary

This Bearish file is complete by itself. The current direction's core price/color contract is:

| Concept | Bearish rule |
| --- | --- |
| Trend directional extreme | high |
| Trend improvement | value > current |
| Trend strict stop/cross | value > level |
| Reaction context color | RED |
| Reaction First color | GREEN |
| Reaction confirmation | candle.low < candidate.box_bottom |
| Reaction Reset | candle.high > previous.box_top |
| Opposite Order direction | bullish |
| Opposite Order strict stop | low < order_stop_level |
| Scale Blue Fibonacci | bottom + FIBONACCI_RATIO * (reference - bottom) |
| Scale Blue linePrice | high - (high - low) / Decimal(3) |
| Reset Blue linePrice | high - (high - low) / Decimal(5) |
| E/StopAll source extreme | high |

Doji remains GREEN and is not color-reflected.


## 22. Mirror Contract for Audit Only

This section is an audit correspondence table, not an implementation dependency. All Bearish rules are already fully defined above.

| Bearish concept | Opposite-direction correspondence |
| --- | --- |
| `high` | `low` |
| `>` strict directional crossing | `<` |
| `RED` context | `GREEN` context in the opposite direction |
| `GREEN` First | `RED` First in the opposite direction |
| `Low < box_bottom` confirmation | `High > box_top` confirmation |
| `High > box_top` Reset | `Low < box_bottom` Reset |
| Doji GREEN | Doji GREEN |

Shared non-directional semantics such as Decimal conversion, timestamps, RAW chronology, physical Order identity, lifecycle iteration, and serialization are not color- or price-reflected.


## 23. Source-Faithful Pseudocode Contracts

These blocks intentionally use production identifiers. They are concise contracts, not renamed teaching aliases.

### Candle color

```python
def classify_candle_color(open_price, close_price):
    return "GREEN" if open_price <= close_price else "RED"
```

### Directional strict cross

```python
policy = get_direction_policy(direction)
crossed = policy.strict_cross(value, level)
```

### Exact Reaction confirmation

```python
confirmation = chronology.reaction_confirmation(direction, reaction)
```

### Blue calculation

```python
blue_lines = detect_blue_lines(
    direction,
    full_results[direction].reactions,
    chronology,
    full_results[direction].resets,
)
```

### A calculation

```python
a_zones = detect_a_zones(
    direction,
    full_results[direction].reactions,
    blue_lines,
    chronology,
)
```

### S calculation

```python
s_detector = SZoneDetector(
    direction,
    full_results[direction].reactions,
    full_results[opposite].reactions,
    blue_lines,
    a_zones,
    chronology,
    0,
    len(candles) - 1,
    full_results[opposite].resets,
    initial_order_geometry=initial_order_geometry[direction],
)
s_zones = s_detector.detect()
```

### E calculation

```python
e_detector = create_e_detector(
    direction,
    e_engine,
    full_results,
    s_zones,
    chronology,
    geometry_detectors,
    s_detector.order_audit,
    lifecycle_engine,
)
e_zones = e_detector.detect()
```

### StopAll reconciliation

```python
e_zones, stopalls = reconcile_stopall_lifecycle(
    detector,
    s_zones,
    e_zones,
    chronology,
    direction,
    timed_step,
)
```

### Final Internal-Reaction filtering

```python
display_a_zones, display_s_zones, e_zones, stopalls = (
    filter_internal_behavior_outputs(
        display_a_zones,
        display_s_zones,
        e_zones,
        stopalls,
        opposite_reactions,
        opposite_internal_identities,
        all_behavior_reactions,
    )
)
```

### 23.1 `UnifiedReactionDetector.detect` main-loop contract

The following branch-specific pseudocode preserves the production control order and identifiers. Helper internals are specified by the Reaction/Reset rules above.

```python
direction = self.output_direction
initial = self._first_initial(direction)
if initial is None:
    return DetectionResult(direction=direction, reactions=[], resets=[], start_index=self.start_index, end_index=self.end_index)
self._append_reaction(direction, initial)
previous = initial
index = initial.break_idx + 1
running_value = self.candles[initial.break_idx].low
running_source = initial.break_idx
candidate = None

while index <= self.end_index:
    candle = self.candles[index]
    reset = pending_reset_index is not None or (candle.high > previous.box_top)
    candidate_break = candidate is not None and (candle.low < candidate.box_bottom)

    if reset and candidate_break:
        reset = self.bear.confirmed_reset_before_breakdown(candidate, candle, previous.box_top)

    if reset:
        reset_index = pending_reset_index if pending_reset_index is not None else index
        reset_candle = self.candles[reset_index]
        pending_reset_index = None
        level = previous.box_bottom if direction == "bullish" else previous.box_top
        already_recorded = (
            self.all_resets[direction]
            and self.all_resets[direction][-1].from_first_idx == previous.first_idx
        )
        if not already_recorded:
            self._append_reset(direction, reset_candle, level, previous.first_idx)
        direct_candidate = self._first_direct_same_direction_after_reset(direction, reset_index)
        if direct_candidate is None or direct_candidate.break_idx is None:
            break
        direct_candidate.mode = "A"
        direct_candidate.cross_direction_origin = False
        direct_candidate.cross_direction_chain_owner = False
        if not self._append_reaction(direction, direct_candidate):
            candidate = None
            index = direct_candidate.break_idx + 1
            pending_reset_index = direct_candidate.break_idx
            continue
        previous = direct_candidate
        index = direct_candidate.break_idx + 1
        continue

    if candidate is not None:
        if candle.high > candidate.box_top:
            candidate.box_top = candle.high
            candidate.box_top_source_idx = candle.index
            candidate.box_top_source_time = candle.display_time
        if candle.low < candidate.box_bottom:
            candidate.break_idx = candle.index
            candidate.break_time = candle.display_time
            analysis = self._refine(direction, candidate, candle)
            post_reset_second = self.bear.post_breakdown_reset(analysis, candidate.box_top, candle)
            self._append_reaction(direction, candidate)
            previous = replace(candidate)
            running_value = candle.low
            running_source = candle.index
            if post_reset_second is not None:
                self._append_reset(
                    direction,
                    candle,
                    previous.box_bottom if direction == "bullish" else previous.box_top,
                    previous.first_idx,
                    post_reset_second.display_time,
                )
                candidate = None
                pending_reset_index = candle.index
            else:
                candidate = self._candidate_from_confirmation_remainder(direction, previous, candle, analysis)
    elif candle.tag == "GREEN":
        bottom = min(running_value, candle.low)
        bottom_source = running_source if running_value <= candle.low else candle.index
        top_start = bottom_source + 1 if bottom_source < candle.index else candle.index
        top, top_source = self.maximum_high(top_start, candle.index)
        candidate = Candidate(candle.index, candle.display_time, top_source.index, top_source.display_time, top, bottom_source, self.candles[bottom_source].display_time, bottom, mode="B")

    if candle.low < running_value: running_value, running_source = candle.low, candle.index
    index += 1

return self._result()
```

`stop_after_first_at_or_after` is an optional early-return control used by callers; when supplied, detection returns after appending a Reaction whose `first_idx` is at or beyond that threshold.

### 23.2 `detect_blue_lines` execution order

```python
policy = get_direction_policy(direction)
output = []
previous_reaction = None
previous_count = None
has_blue_line = False
healthy_reactions_since_blue = 0

for reaction_number, reaction in enumerate(reactions, start=1):
    behavior_internal = bool(getattr(reaction, "behavior_internal", False))
    if str(getattr(reaction, "mode")) == "A":
        reference = getattr(reaction, "anchor_value", None)
        if reference is None:
            reference = getattr(reaction, "leg_boundary_value", None)
        if reference is None:
            raise ValueError("Leg-Start reaction is missing its leg-head boundary.")
        previous_count = None
    else:
        if previous_reaction is None:
            raise ValueError("A Normal reaction cannot precede the Leg-Start reaction.")
        reference = Decimal(getattr(previous_reaction, "box_top"))

    level, strikes = count_scale_strikes(direction, reaction, chronology, reference, candles_by_index)
    scale_candidate = previous_count is not None and len(strikes) > previous_count
    scale_emitted = False
    if scale_candidate and (not has_blue_line or healthy_reactions_since_blue >= 1):
        output.append(
            _build_scale_blue_line(
                direction, reaction_number, previous_count, level, strikes,
                candles_by_index, chronology, behavior_internal,
            )
        )
        has_blue_line = True
        healthy_reactions_since_blue = 0
        scale_emitted = True
    if has_blue_line and not scale_emitted:
        healthy_reactions_since_blue += 1

    for reset in resets_by_first.get(int(getattr(reaction, "first_idx")), []):
        if has_blue_line and healthy_reactions_since_blue < 1:
            continue
        output.append(
            _build_reset_blue_line(
                direction, reaction_number, reset,
                output[-1] if output else None,
                candles, candles_by_index, chronology, behavior_internal,
            )
        )
        has_blue_line = True
        healthy_reactions_since_blue = 0

    previous_reaction = reaction
    previous_count = len(strikes)
return output
```

### 23.3 `AZoneDetector.detect` and ordinary-A ownership order

```python
states = self._build_blue_states()
ordinary = self._detect_ordinary_a(states)
ordinary, special = self._filter_special_a(self._double_stop_a_candidates(), ordinary)
return sorted(ordinary + special, key=lambda item: (item.source_time, item.trigger_event_time))
```

`_detect_ordinary_a` processes adjacent `BlueState` objects in list order, honors `cycle_after_index` and `bridge_reuse_ordinal`, sets `expires_at` to the third Blue formation when present, calls `_pair_trigger`, then `_first_reaction_after`, then `_a_source`. After creating an A it computes the first strict A stop from validating-Reaction confirmation and either permits adjacent second-Blue reuse or consumes Blue states through the validating `break_idx`.

### 23.4 `SZoneDetector.detect` execution order

```python
output = []
self.a_ownership_windows.clear()
self.order_audit.clear()
for zone in self.a_zones:
    self._audit_stopped_a(zone)

cycle_start_time = self.range_start
for zone_offset, zone in enumerate(self.a_zones):
    a_ordinal = zone_offset + 1
    if self._a_owned_by_s(zone):
        continue
    source_time = getattr(zone, "source_time")
    if source_time < cycle_start_time or (source_time == cycle_start_time and output):
        continue
    next_a_confirmation = self._a_confirmation_time(self.a_zones[zone_offset + 1]) if zone_offset + 1 < len(self.a_zones) else None
    a_price = _decimal(getattr(zone, "price"))
    a_stop = self._first_a_stop(a_price, self._a_confirmation_time(zone))
    if a_stop is None:
        continue
    _, _, a_stop_event_time = a_stop
    order_match = self._first_order_after(a_stop_event_time)
    if next_a_confirmation is not None and a_stop_event_time >= next_a_confirmation:
        continue
    self.a_ownership_windows.append((a_stop_event_time, None))
    type3_deadline = order_match[2] if order_match is not None else self.range_end
    type3 = self._first_type3(a_stop_event_time, type3_deadline)
    if type3 is not None:
        s_zone = self._build_type3_zone(zone, a_ordinal, a_price, a_stop, type3)
    elif order_match is not None:
        s_zone = self._build_order_backed_zone(zone, a_ordinal, a_price, a_stop, order_match)
        if s_zone is None:
            continue
    else:
        continue
    output.append(s_zone)
    cycle_start_time = s_zone.source_time
    self.a_ownership_windows[-1] = (a_stop_event_time, max(a_stop_event_time, s_zone.decision_event_time + timedelta(microseconds=1)))
return sorted(output, key=lambda item: (item.source_time, item.decision_event_time))
```

### 23.5 E execution order

`EZoneDetector.detect` is exactly a two-stage calculation/reconciliation entry point:

```python
def detect(self):
    self.order_audit.clear()
    self.visual_lifecycle_starts.clear()
    candidates = self._discover_candidate_chains()
    numbered = self._reconcile_candidate_chains(candidates)
    return self._rebuild_accepted_order_audit(numbered)
```

`_discover_candidate_chains` starts a provisional chain from every stopped S. Each provisional chain repeatedly calls `_zone(parent_type, parent)`; the newly created E becomes the next parent. A chain ends when the parent has no strict stop, `_zone` cannot produce a candidate, or a duplicate `source_index` would occur. Global ownership is not decided here. `_reconcile_candidate_chains` performs the chronological global acceptance described by E-RECON-001, including parent validity, Order validity, stopped-E family inheritance, Red-over-Blue dominance, numbering, and StopAll sequence resets.

### 23.6 StopAll and fixed-point lifecycle execution order

```python
# StopAllDetector.detect
s_events = sorted(
    self.s_zones,
    key=lambda item: (item.source_time, item.source_index),
)
s_position = 0
s_key = None
s_count = 0
e_key = None
e_count = 0
active = []
output = []

for e_item in self.e_zones:
    while s_position < len(s_events) and s_events[s_position].source_time < e_item.source_time:
        s_item = s_events[s_position]
        color = str(s_item.color)
        incoming_priority = self._sequence_priority("s", color)
        active_priority = self._active_sequence_priority(s_key, e_key)
        if e_key is None and s_key == color:
            s_count += 1
        elif incoming_priority > active_priority:
            s_key, s_count = color, 1
            e_key, e_count = None, 0
        s_position += 1

    e_decision = e_item.decision_event_time
    stopped_active = []
    for item in active:
        stop = self._strict_stop(item.decision_event_time, item.price)
        if stop is not None and stop[2] <= e_decision:
            stopped_active.append((item, stop))

    if stopped_active:
        highest = max(item.number for item, _ in stopped_active)
        gate_event = min(stop[2] for _, stop in stopped_active)
        zone = self._stopall_from_e(
            e_item,
            highest + 1,
            "stopall-stop",
            gate_event,
            "StopAll",
            f"StopAll{highest}",
            len(stopped_active),
        )
        stopped_ids = {id(item) for item, _ in stopped_active}
        active = [item for item in active if id(item) not in stopped_ids]
        output.append(zone)
        active.append(zone)
        s_key = e_key = None
        s_count = e_count = 0
        continue

    new_key = self._e_key(e_item)
    qualifies_e = e_key is not None and e_count >= 2
    qualifies_s = e_key is None and s_key is not None and s_count >= 2
    if qualifies_e or qualifies_s:
        parent = max(
            (
                item
                for item in (self.e_zones if qualifies_e else self.s_zones)
                if item.source_time < e_item.source_time
                and (
                    self._e_key(item) == e_key
                    if qualifies_e
                    else str(item.color) == s_key
                )
            ),
            key=lambda item: item.source_time,
        )
        gate = self._strict_stop(
            parent.decision_event_time,
            _decimal(parent.price),
        )
        if gate is not None and gate[2] <= e_decision:
            zone = self._stopall_from_e(
                e_item,
                1,
                "sequence-group-stop",
                gate[2],
                "E" if qualifies_e else "S",
                (
                    f"E{e_key[1]} {e_key[0]}"
                    if qualifies_e
                    else f"S {s_key}"
                ),
                e_count if qualifies_e else s_count,
            )
            output.append(zone)
            active.append(zone)
            s_key = e_key = None
            s_count = e_count = 0
            continue

    if e_key == new_key:
        e_count += 1
    else:
        incoming_priority = self._sequence_priority("e", new_key[0])
        active_priority = self._active_sequence_priority(s_key, e_key)
        replaces_active = incoming_priority > active_priority
        advances_e = (
            e_key is not None
            and incoming_priority == active_priority
            and self._dominates_e(new_key, e_key)
        )
        if replaces_active or advances_e:
            e_key, e_count = new_key, 1
            s_key, s_count = None, 0

completed = []
for item in output:
    stop = self._strict_stop(item.decision_event_time, item.price)
    completed.append(
        replace(
            item,
            stop_index=stop[0] if stop else None,
            stop_time=stop[1] if stop else None,
            stop_event_time=stop[2] if stop else None,
        )
    )
return completed
```

`reconcile_stopall_lifecycle` is a fixed-point loop with this exact state transition contract:

```python
seen = set()
pass_number = 1
measure = timed_step or (lambda _label, work: work())
while True:
    visible_s = measure(
        f"Reconcile S visibility - {direction.title()} - pass {pass_number}",
        lambda: s_zones_for_module_engines(s_zones, e_zones, direction),
    )
    stopalls = measure(
        f"StopAll - {direction.title()} - pass {pass_number}",
        lambda: detect_stopalls(direction, visible_s, e_zones, chronology),
    )
    resets = {item.source_time: item.number for item in stopalls}
    if resets == detector.sequence_resets:
        return e_zones, stopalls
    identity = tuple(sorted(resets.items()))
    if identity in seen:
        raise ValueError("E/StopAll lifecycle reconciliation did not converge")
    seen.add(identity)
    detector.sequence_resets = resets
    e_zones = measure(
        f"E - {direction.title()} - StopAll reconciliation {pass_number}",
        detector.detect,
    )
    pass_number += 1
```

The exact implementation also preserves the optional `timed_step` wrapper around `detector.detect()` and `detect_stopalls`; that wrapper changes telemetry only, not calculation order or outputs.

## 24. Worked Symbolic Examples

These examples contain no fixture-specific project timestamps or prices. They demonstrate source rules only.

### EX-REA-001 — Strict Bearish Reaction confirmation

Given a waiting Bearish Reaction with confirmation boundary `box_bottom = 100` and Original RAW values inside the Break Main Candle that touch 100 and later strictly cross it, the touch is not confirmation. The first RAW event satisfying the source comparator is the exact confirmation.

### EX-RST-001 — Competing confirmation and Reset

If one Main Candle contains both the prior-Reaction Reset condition and the waiting-candidate confirmation condition, compare the first RAW positions. If both conditions are true at the same RAW position, Reset/invalidation owns the tie under the Reaction source implementation.

### EX-S-001 — S same-RAW ambiguity

If one RAW Candle simultaneously satisfies the S `candidate_cross` and the opposite Order `order_cross`, `_decision` returns `None`. No assumed High/Low path is allowed.

### EX-E-001 — Recursive E

An accepted S stops strictly, an opposite Order later stops, and E1 is formed. If E1 later stops strictly and a new valid E-space Order stops, E2 may be formed. The chain continues recursively until `_parent_stop` or `_zone` returns no next candidate, then global reconciliation decides which provisional chain remains accepted.

### EX-BLU-001 — Scale Blue spacing

Given consecutive healthy Reactions with equal strike counts, no Scale Blue is emitted. When a later Reaction has a strictly larger strike count, a Scale Blue is emitted only if either no prior Blue exists or `healthy_reactions_since_blue >= 1`. A Reset Blue resets that spacing counter exactly like a Scale Blue.

### EX-A-001 — Equality does not trigger A continuation

If the candidate continuation level is touched exactly but never strictly crossed under `DirectionPolicy.strict_cross`, `_pair_trigger` produces no trigger from that touch. The later validating Reaction cannot create A until a strict trigger event exists.

### EX-ORD-001 — Two causes, one physical Order

If parent-stop evidence and reset-leg evidence resolve to the same canonical `(first_idx, break_idx)`, the system keeps one physical Order identity and merges both causes. A second Order object MUST NOT be created.

### EX-STP-001 — Sequence-group StopAll

When the currently dominant same-family S/E sequence contains at least two qualifying active members and its latest qualifying member has a strict RAW stop no later than a later accepted E decision, that later E supplies `StopAll1` with `gate_type = "sequence-group-stop"`.

### EX-INT-001 — Calculated but not visible

A mathematically calculated ordinary A/S/E/StopAll point can remain in detector/lifecycle state yet be removed from public output when it lies strictly inside a protected healthy Reaction interior. The Advanced Blue S exception remains eligible exactly as INT-BEH-001 defines.


## 25. Test Contracts

### T-INV-DOJI

Given `open == close`, `classify_candle_color` MUST return GREEN.

Forbidden: converting Doji to RED in any directional adapter.

### T-RAW-CONF

Given a Main Break Candle containing multiple RAW Candles, exact Reaction confirmation MUST equal the first RAW strict confirmation, not the Main Candle start unless no strict RAW confirmation can be resolved.

### T-REA-TIE

Given Reset/invalidation and confirmation at the same RAW position, the Reset/invalidation branch MUST win where the source uses `<=`.

### T-BLUE-SCALE

Given equal strike count versus the prior Reaction, Scale Blue MUST NOT be emitted. It requires a strict increase.

### T-A-STRICT

Given price exactly equal to A/Blue continuation level, no strict A stop/trigger is created.

### T-S-AMBIG

Given `candidate_cross and order_cross` in the same RAW Candle, `_decision` MUST return no S decision.

### T-E-ID

Multiple Order causes mapping to one `(first_idx, break_idx)` MUST serialize as one physical Order identity with merged causes.

### T-STOPALL

A sequence-group StopAll requires at least two active members of the dominant S or E sequence and a strict stop of the qualifying latest group member before/equal to the current E decision event.

### T-INTERNAL

An ordinary A/S/E/StopAll point strictly inside a protected healthy Reaction interior MUST be filtered according to `filter_internal_behavior_outputs`; the Advanced Blue S exception MUST remain visible.


## 26. Reimplementation Checklist

A reimplementation is incomplete until every item below is YES:

- RAW JSON rows can be isolated without sorting or deduplication changes.
- Original RAW Candles and Main Candles are distinct representations.
- Asia/Tehran conversion matches `local_datetime` / `epoch` semantics.
- Doji is always GREEN.
- Decimal comparisons are preserved.
- `LowerTimeframeIndex` strict first-cross semantics are reproduced.
- Mode A and Mode B Reaction formation are reproduced.
- Reset-before-confirmation and post-confirmation Reset are reproduced.
- published Reaction geometry is frozen at exact confirmation.
- cross-direction Internal Reaction ownership is reproduced.
- Scale and Reset Blue, strike spacing, and calculation validity are reproduced.
- ordinary A, inherited continuation, Blue reuse, and double-stop A are reproduced.
- exact A stop and stopped-A Order audit are reproduced.
- S Simple, Advanced, Type3, Blue, Red, ownership windows, and same-RAW ambiguity are reproduced.
- Mode-A and Mode-B canonical Order stops are reproduced.
- parent-stop, reset-leg, carried-live, and inherited S Order paths are reproduced.
- recursive E candidate chains and global reconciliation are reproduced.
- E family/number dominance is reproduced.
- StopAll sequence-group-stop and stopall-stop are reproduced.
- E/StopAll fixed-point reconciliation is reproduced.
- A/S/E/StopAll lifecycle and visibility filters are reproduced.
- Internal-Reaction final output veto and Advanced Blue S exception are reproduced.
- public schemas and output ordering are reproduced exactly.


## 27. Rule Coverage Matrix

| Rule group | Subsystem | Key source identifiers | RAW required |
| --- | --- | --- | --- |
| INV / DATA / AGG | Input | `classify_candle_color`, `build_native_raw_candles`, `build_timeframe_buckets` | Yes |
| REA / RST | Reaction | `UnifiedReactionDetector.detect`, `_first_direct_same_direction_after_reset`, `_owner_boundary_before_confirmation`, `reaction_confirmation` | Yes |
| INT-REA | Internal Reaction | `build_behavior_reaction_views`, `published_reaction_candidate` | Yes |
| BLU | Blue | `detect_blue_lines`, `count_scale_strikes`, `_intrabar_pending_confirmation`, `mark_internal_blue_lines` | Yes |
| A | A | `AZoneDetector.detect`, `_pair_trigger`, `_double_stop_a_candidates`, `_a_source` | Yes |
| S | S | `SZoneDetector.detect`, `_first_type3`, `_build_order_backed_zone`, `_decision` | Yes |
| ORD | Order | `canonical_order_stop`, `order_candidates`, `_reset_leg_evidence`, `_merge_order_candidate` | Yes |
| E | E | `EZoneDetector.detect`, `_zone`, `_discover_candidate_chains`, `_reconcile_candidate_chains` | Yes |
| STP | StopAll | `StopAllDetector.detect`, `reconcile_stopall_lifecycle` | Yes |
| LIF / VIS | Lifecycle | `split_a_zones_by_dominant_stops`, `visible_s_zones_after_module_resets`, `finalize_behavior_visibility`, `filter_internal_behavior_outputs` | Yes |
| OUT | Serialization | `serialize*`, `build_response_payload` | No |


## 28. Source Coverage Inventory

The following calculation-source identifiers were reviewed while generating this standalone specification. The list is informational audit metadata; the algorithm rules above remain self-contained.


### `a_zone_detector.py`

Covered by: Section 10


| Kind | Identifier | Source line |
| --- | --- | --- |
| class | `BlueState` | 23 |
| class | `AZone` | 36 |
| function | `_decimal` | 60 |
| class | `AZoneDetector` | 64 |
| method | `AZoneDetector.__init__` | 65 |
| method | `AZoneDetector.extreme_name` | 93 |
| method | `AZoneDetector._strict_cross` | 96 |
| method | `AZoneDetector._better` | 99 |
| method | `AZoneDetector._main_index` | 102 |
| method | `AZoneDetector._lower_window` | 105 |
| method | `AZoneDetector._first_crossing` | 110 |
| method | `AZoneDetector._range_extreme` | 152 |
| method | `AZoneDetector._formation` | 186 |
| method | `AZoneDetector._reset_formation_time` | 203 |
| method | `AZoneDetector._build_blue_states` | 215 |
| method | `AZoneDetector._double_stop_a_candidates` | 244 |
| method | `AZoneDetector._pair_trigger` | 306 |
| method | `AZoneDetector._reaction_confirmation_time` | 466 |
| method | `AZoneDetector._first_reaction_after` | 471 |
| method | `AZoneDetector._inherited_stop` | 489 |
| method | `AZoneDetector._a_source` | 516 |
| method | `AZoneDetector._detect_ordinary_a` | 537 |
| method | `AZoneDetector._filter_special_a` | 647 |
| method | `AZoneDetector.detect` | 711 |
| method | `AZoneDetector._a_was_stopped_before` | 723 |
| function | `detect_a_zones` | 749 |

### `blue_line_detector.py`

Covered by: Section 9


| Kind | Identifier | Source line |
| --- | --- | --- |
| class | `ScaleStrike` | 23 |
| class | `BlueLine` | 30 |
| function | `_is_color` | 48 |
| function | `_main_candle` | 52 |
| function | `_stops_on_index` | 59 |
| function | `fibonacci_level` | 75 |
| function | `_intrabar_pending_confirmation` | 84 |
| function | `count_scale_strikes` | 135 |
| function | `_build_scale_blue_line` | 196 |
| function | `_build_reset_blue_line` | 235 |
| function | `detect_blue_lines` | 290 |
| function | `public_blue_lines` | 397 |
| function | `mark_internal_blue_lines` | 406 |

### `direction_policy.py`

Covered by: Sections 3–4, 21–23


| Kind | Identifier | Source line |
| --- | --- | --- |
| class | `DirectionPolicy` | 13 |
| method | `DirectionPolicy.strict_cross` | 22 |
| method | `DirectionPolicy.improves` | 26 |
| function | `get_direction_policy` | 52 |

### `e_zone_detector.py`

Covered by: Sections 12–13


| Kind | Identifier | Source line |
| --- | --- | --- |
| class | `EZone` | 24 |
| function | `_decimal` | 71 |
| class | `EZoneDetector` | 75 |
| method | `EZoneDetector.__init__` | 76 |
| method | `EZoneDetector._reset_time` | 194 |
| method | `EZoneDetector._main_index` | 197 |
| method | `EZoneDetector._first_cross_position` | 201 |
| method | `EZoneDetector._stop_value` | 218 |
| method | `EZoneDetector._first_parent_stop` | 222 |
| method | `EZoneDetector._confirmation_for` | 235 |
| method | `EZoneDetector._confirmation` | 238 |
| method | `EZoneDetector._reaction_first_time` | 241 |
| method | `EZoneDetector._strict_trigger_cross` | 244 |
| method | `EZoneDetector._reset_leg_geometry` | 258 |
| method | `EZoneDetector._reset_leg_has_simple_trend_reaction` | 287 |
| method | `EZoneDetector._first_order_b_geometry` | 303 |
| method | `EZoneDetector._next_outer_reset_time` | 439 |
| method | `EZoneDetector._replacement_order` | 461 |
| method | `EZoneDetector._reset_leg_evidence` | 511 |
| method | `EZoneDetector._legacy_reset_leg_evidence` | 554 |
| method | `EZoneDetector._order_stop` | 595 |
| method | `EZoneDetector.order_stop` | 607 |
| method | `EZoneDetector._first_healthy_direct_geometry` | 614 |
| method | `EZoneDetector._synthetic_reset_leg_orders` | 699 |
| method | `EZoneDetector._direct_parent_stop_order` | 790 |
| method | `EZoneDetector._merge_order_candidate` | 875 |
| method | `EZoneDetector._add_canonical_reset_leg_orders` | 921 |
| method | `EZoneDetector.order_candidates` | 958 |
| method | `EZoneDetector._first_order` | 1043 |
| method | `EZoneDetector._blue_parent_superseded` | 1056 |
| method | `EZoneDetector._register_order_audit` | 1065 |
| method | `EZoneDetector._reset_by_proven_order` | 1194 |
| method | `EZoneDetector._enrich_order_audit_reset_causes` | 1220 |
| method | `EZoneDetector.visual_order_lifecycle` | 1252 |
| method | `EZoneDetector._parent_stop` | 1294 |
| method | `EZoneDetector.parent_stop` | 1302 |
| method | `EZoneDetector._cross_order` | 1309 |
| method | `EZoneDetector.cross_order` | 1329 |
| method | `EZoneDetector._unconsumed_s_orders` | 1336 |
| method | `EZoneDetector._initial_order_match` | 1373 |
| method | `EZoneDetector._gate_owned_initial_order` | 1386 |
| method | `EZoneDetector._carried_orders_for_parent` | 1414 |
| method | `EZoneDetector._blocked_by_gate_owned_order` | 1482 |
| method | `EZoneDetector._reset_evidence_for_order` | 1492 |
| method | `EZoneDetector._extreme_between` | 1505 |
| method | `EZoneDetector._zone` | 1521 |
| method | `EZoneDetector._discover_candidate_chains` | 1623 |
| method | `EZoneDetector._reconcile_candidate_chains` | 1665 |
| method | `EZoneDetector._rebuild_accepted_order_audit` | 1993 |
| method | `EZoneDetector.detect` | 2100 |
| function | `detect_e_zones` | 2109 |

### `lifecycle_engine.py`

Covered by: Sections 14–18


| Kind | Identifier | Source line |
| --- | --- | --- |
| function | `sequence_priority` | 31 |
| function | `_decimal` | 36 |
| class | `StopAll` | 41 |
| class | `StopAllDetector` | 83 |
| method | `StopAllDetector.__init__` | 84 |
| method | `StopAllDetector._strict_stop` | 105 |
| method | `StopAllDetector._e_key` | 122 |
| method | `StopAllDetector._dominates_e` | 126 |
| method | `StopAllDetector._sequence_priority` | 136 |
| method | `StopAllDetector._active_sequence_priority` | 140 |
| method | `StopAllDetector._stopall_from_e` | 149 |
| method | `StopAllDetector.detect` | 207 |
| function | `detect_stopalls` | 326 |
| function | `prepare_order_audit` | 338 |
| function | `accepted_audit_entry` | 431 |
| function | `resolve_order_context` | 460 |
| function | `visible_a_zones_after_s_stops` | 512 |
| function | `module_priority` | 528 |
| function | `module_identity` | 542 |
| function | `module_stop_event` | 551 |
| function | `strictly_beyond_boundary` | 565 |
| function | `dominant_module` | 568 |
| function | `split_a_zones_by_dominant_stops` | 579 |
| function | `blocked_orders_while_invalid_leg_heads_are_live` | 730 |
| function | `s_zones_for_module_engines` | 752 |
| function | `visible_s_zones_after_module_resets` | 777 |
| function | `reconcile_stopall_lifecycle` | 946 |
| function | `visible_a_zones_after_module_boundaries` | 980 |
| function | `reaction_number_is_internal` | 1027 |
| function | `order_identity_is_internal` | 1042 |
| function | `point_is_inside_healthy_reaction` | 1051 |
| function | `forbidden_internal_order_b` | 1074 |
| function | `_is_advanced_blue_s` | 1088 |
| function | `filter_internal_behavior_outputs` | 1095 |
| function | `finalize_behavior_visibility` | 1154 |
| function | `visible_a_zones` | 1249 |

### `reaction_engine.py`

Covered by: Sections 4, 6–8, 12, 16, 23


| Kind | Identifier | Source line |
| --- | --- | --- |
| class | `Candle` | 25 |
| class | `Candidate` | 37 |
| class | `ResetEvent` | 65 |
| class | `IntrabarAnalysis` | 74 |
| class | `DetectionResult` | 81 |
| function | `classify_candle_color` | 89 |
| function | `opposite_direction` | 94 |
| class | `DetectorBase` | 103 |
| method | `DetectorBase.__init__` | 104 |
| method | `DetectorBase._shared_time_index` | 129 |
| method | `DetectorBase.raw_between` | 139 |
| method | `DetectorBase.main_source_for_time` | 144 |
| method | `DetectorBase.minimum_low` | 157 |
| method | `DetectorBase.maximum_high` | 166 |
| class | `BullishDetector` | 176 |
| method | `BullishDetector._is_context_color` | 185 |
| method | `BullishDetector._is_first_color` | 188 |
| method | `BullishDetector.green_run_peak_before` | 191 |
| method | `BullishDetector.breakout_analysis` | 204 |
| method | `BullishDetector.mode_a_invalidation_before_breakout` | 230 |
| method | `BullishDetector.confirmed_reset_before_breakout` | 266 |
| method | `BullishDetector.post_breakout_reset` | 286 |
| method | `BullishDetector.detect` | 301 |
| function | `mirror_candle` | 579 |
| function | `mirror_candidate` | 599 |
| function | `mirror_analysis` | 618 |
| class | `_ReflectedCandles` | 627 |
| method | `_ReflectedCandles.__init__` | 635 |
| method | `_ReflectedCandles.__len__` | 639 |
| method | `_ReflectedCandles.__getitem__` | 642 |
| function | `_reflected_view` | 655 |
| class | `BearishDetector` | 665 |
| method | `BearishDetector.__init__` | 673 |
| method | `BearishDetector.red_run_bottom_before` | 693 |
| method | `BearishDetector.breakdown_analysis` | 697 |
| method | `BearishDetector.invalidation_high_break_before_breakdown` | 702 |
| method | `BearishDetector.confirmed_reset_before_breakdown` | 707 |
| method | `BearishDetector.post_breakdown_reset` | 713 |
| method | `BearishDetector.detect` | 720 |
| function | `published_reaction_candidate` | 731 |
| function | `_decimal_value` | 829 |
| class | `LowerTimeframeIndex` | 834 |
| method | `LowerTimeframeIndex.__init__` | 841 |
| method | `LowerTimeframeIndex.first_less` | 882 |
| method | `LowerTimeframeIndex.first_greater` | 885 |
| method | `LowerTimeframeIndex.range_minimum` | 888 |
| method | `LowerTimeframeIndex.range_maximum` | 892 |
| method | `LowerTimeframeIndex._range_query` | 896 |
| method | `LowerTimeframeIndex._first` | 934 |
| function | `shared_lower_timeframe_index` | 959 |
| class | `ReflectedLowerTimeframeIndex` | 972 |
| method | `ReflectedLowerTimeframeIndex.__init__` | 977 |
| method | `ReflectedLowerTimeframeIndex.first_less` | 981 |
| method | `ReflectedLowerTimeframeIndex.first_greater` | 984 |
| method | `ReflectedLowerTimeframeIndex.range_minimum` | 987 |
| method | `ReflectedLowerTimeframeIndex.range_maximum` | 991 |
| class | `MarketChronology` | 996 |
| method | `MarketChronology.__init__` | 1015 |
| method | `MarketChronology.opposite_direction` | 1038 |
| method | `MarketChronology.main_index` | 1042 |
| method | `MarketChronology.lower_bounds` | 1051 |
| method | `MarketChronology.lower_window` | 1062 |
| method | `MarketChronology._reset_cache_key` | 1069 |
| method | `MarketChronology._reaction_cache_key` | 1081 |
| method | `MarketChronology.reset_time` | 1095 |
| method | `MarketChronology.reaction_confirmation` | 1114 |
| method | `MarketChronology.canonical_order_stop` | 1162 |
| function | `build_behavior_reaction_views` | 1227 |
| function | `directional_a_stop_order_finder` | 1335 |
| class | `UnifiedReactionDetector` | 1398 |
| method | `UnifiedReactionDetector.__init__` | 1408 |
| method | `UnifiedReactionDetector.bull` | 1434 |
| method | `UnifiedReactionDetector.bear` | 1442 |
| method | `UnifiedReactionDetector._append_reaction` | 1449 |
| method | `UnifiedReactionDetector._append_reset` | 1515 |
| method | `UnifiedReactionDetector._refine` | 1533 |
| method | `UnifiedReactionDetector._candidate_from_confirmation_remainder` | 1554 |
| method | `UnifiedReactionDetector._first_initial` | 1623 |
| method | `UnifiedReactionDetector._first_direct_same_direction_after_reset` | 1636 |
| method | `UnifiedReactionDetector._first_geometry_after_reset` | 1674 |
| method | `UnifiedReactionDetector.first_geometry_after_reset` | 1726 |
| method | `UnifiedReactionDetector.first_simple_geometry_after_gate` | 1733 |
| method | `UnifiedReactionDetector._reaction_break_indices` | 1781 |
| method | `UnifiedReactionDetector.first_order_reaction_after_gate` | 1796 |
| method | `UnifiedReactionDetector._earliest_confirmed_geometry` | 1916 |
| method | `UnifiedReactionDetector._build_direct_candidate` | 1971 |
| method | `UnifiedReactionDetector._scan_direct_candidate` | 2029 |
| method | `UnifiedReactionDetector._owner_boundary_before_confirmation` | 2059 |
| method | `UnifiedReactionDetector._result` | 2100 |
| method | `UnifiedReactionDetector.detect` | 2109 |

### `s_zone_detector.py`

Covered by: Sections 11–12


| Kind | Identifier | Source line |
| --- | --- | --- |
| class | `SZone` | 23 |
| function | `_decimal` | 61 |
| class | `SZoneDetector` | 65 |
| method | `SZoneDetector.__init__` | 66 |
| method | `SZoneDetector._main_index` | 132 |
| method | `SZoneDetector._lower_window` | 135 |
| method | `SZoneDetector._reaction_confirmation_time` | 140 |
| method | `SZoneDetector.reaction_confirmation_time` | 145 |
| method | `SZoneDetector._reset_time` | 152 |
| method | `SZoneDetector._a_confirmation_time` | 155 |
| method | `SZoneDetector._trend_extreme` | 163 |
| method | `SZoneDetector._a_stopped` | 168 |
| method | `SZoneDetector._first_a_stop` | 171 |
| method | `SZoneDetector.first_a_stop` | 207 |
| method | `SZoneDetector._first_order_after` | 214 |
| method | `SZoneDetector._audit_stopped_a` | 294 |
| method | `SZoneDetector._candidate_source` | 336 |
| method | `SZoneDetector._candidate_source_last` | 353 |
| method | `SZoneDetector._first_trend_reaction_after_order` | 371 |
| method | `SZoneDetector._nested_trend_reaction` | 383 |
| method | `SZoneDetector._simple_candidate` | 413 |
| method | `SZoneDetector._type3_reset_leg` | 422 |
| method | `SZoneDetector._type3_has_trend_reaction` | 438 |
| method | `SZoneDetector._first_type3` | 448 |
| method | `SZoneDetector._candidate_after_order` | 519 |
| method | `SZoneDetector._a_source_event_time` | 560 |
| method | `SZoneDetector._a_owned_by_s` | 569 |
| method | `SZoneDetector._a_pair_is_reset_reset` | 601 |
| method | `SZoneDetector.eligible_a_zones` | 615 |
| method | `SZoneDetector._candidate_timing` | 619 |
| method | `SZoneDetector._candidate_before_order` | 642 |
| method | `SZoneDetector._candidate_event_time` | 682 |
| method | `SZoneDetector.candidate_event_time` | 697 |
| method | `SZoneDetector._blue_formation_time` | 704 |
| method | `SZoneDetector._candidate_cross_has_blue` | 734 |
| method | `SZoneDetector._has_ordinary_trend_reaction` | 751 |
| method | `SZoneDetector._order_stop` | 771 |
| method | `SZoneDetector._candidate_crossed` | 782 |
| method | `SZoneDetector._order_stop_crossed` | 786 |
| method | `SZoneDetector._decision` | 791 |
| method | `SZoneDetector._build_type3_zone` | 885 |
| method | `SZoneDetector._build_order_backed_zone` | 943 |
| method | `SZoneDetector.detect` | 1114 |
| function | `detect_s_zones` | 1183 |

### `trading_pipeline.py`

Covered by: Sections 5–6, 15, 19, 23


| Kind | Identifier | Source line |
| --- | --- | --- |
| function | `emit_progress` | 29 |
| function | `timed` | 37 |
| function | `load_module` | 49 |
| function | `load_engine` | 59 |
| function | `decimal` | 63 |
| function | `local_datetime` | 67 |
| function | `epoch` | 72 |
| function | `isolate_raw_range` | 77 |
| function | `_price_normalizer` | 87 |
| function | `build_native_raw_candles` | 103 |
| function | `build_timeframe_buckets` | 134 |
| function | `build_candle_objects` | 161 |
| function | `serialize` | 191 |
| function | `serialize_blue_lines` | 239 |
| function | `serialize_a_zones` | 264 |
| function | `serialize_s_zones` | 291 |
| function | `serialize_e_zones` | 356 |
| function | `serialize_stopalls` | 407 |
| function | `serialize_order_audit` | 460 |
| class | `EngineBundle` | 519 |
| class | `MarketContext` | 529 |
| function | `parse_arguments` | 538 |
| function | `load_engines` | 605 |
| function | `prepare_market_context` | 639 |
| class | `PipelineState` | 693 |
| class | `FullDirectionState` | 713 |
| function | `create_e_detector` | 727 |
| function | `calculate_full_direction_state` | 789 |
| function | `prepare_pipeline_state` | 969 |
| class | `DirectionRangeState` | 1086 |
| class | `DirectionVisibilityState` | 1099 |
| function | `calculate_direction_range_state` | 1110 |
| function | `finalize_direction_visibility` | 1212 |
| function | `serialize_direction_payload` | 1361 |
| function | `build_direction_output` | 1415 |
| function | `build_response_payload` | 1440 |
| function | `main` | 1492 |
### 28.1 Exact internal dataclass contracts

These internal schemas are included because a standalone reimplementation must preserve ownership/provenance fields even when a field is not public. Names and annotations are copied from the frozen source baseline.

#### `BlueState` — `a_zone_detector.py`

| Field | Annotation | Default |
| --- | --- | --- |
| ordinal | int | required |
| line | object | required |
| formation_index | int | required |
| formation_time | datetime | required |
| stop_index | int | None | required |
| stop_time | datetime | None | required |
| stop_event_time | datetime | None | required |
| stop_level | Decimal | required |
| stop_event_extreme | Decimal | None | required |

#### `AZone` — `a_zone_detector.py`

| Field | Annotation | Default |
| --- | --- | --- |
| direction | str | required |
| blue_1_ordinal | int | required |
| blue_2_ordinal | int | required |
| blue_1_source_time | datetime | required |
| blue_2_source_time | datetime | required |
| blue_1_stop_time | datetime | required |
| blue_2_stop_time | datetime | required |
| blue_1_stop_level | Decimal | required |
| blue_2_stop_level | Decimal | required |
| continuation_level | Decimal | required |
| continuation_source_index | int | required |
| continuation_source_time | datetime | required |
| trigger_index | int | required |
| trigger_time | datetime | required |
| trigger_event_time | datetime | required |
| reaction_number | int | required |
| reaction_first_time | datetime | required |
| reaction_break_time | datetime | required |
| source_index | int | required |
| source_time | datetime | required |
| price | Decimal | required |

#### `ScaleStrike` — `blue_line_detector.py`

| Field | Annotation | Default |
| --- | --- | --- |
| source_index | int | required |
| source_time | datetime | required |
| extreme | Decimal | required |

#### `BlueLine` — `blue_line_detector.py`

| Field | Annotation | Default |
| --- | --- | --- |
| direction | str | required |
| kind | str | required |
| reaction_number | int | required |
| previous_strike_count | int | None | required |
| strike_count | int | None | required |
| fibonacci_level | Decimal | None | required |
| source_index | int | required |
| source_time | datetime | required |
| source_extreme | Decimal | required |
| broken_level | Decimal | None | required |
| line_price | Decimal | required |
| start_time | datetime | required |
| end_time | datetime | required |
| calculation_valid | bool | True |
| behavior_internal | bool | False |

#### `DirectionPolicy` — `direction_policy.py`

| Field | Annotation | Default |
| --- | --- | --- |
| name | str | required |
| extreme_attr | str | required |
| opposite_extreme_attr | str | required |
| first_color | str | required |
| context_color | str | required |
| order_direction | str | required |
| is_bullish | bool | required |

#### `EZone` — `e_zone_detector.py`

| Field | Annotation | Default |
| --- | --- | --- |
| direction | str | required |
| family | str | required |
| number | int | required |
| parent_type | str | required |
| parent_source_index | int | required |
| parent_source_time | datetime | required |
| parent_price | Decimal | required |
| parent_stop_index | int | required |
| parent_stop_time | datetime | required |
| parent_stop_event_time | datetime | required |
| order_direction | str | required |
| order_reaction_number | int | required |
| order_mode | str | required |
| order_causes | tuple[str, ...] | required |
| order_parent_stop_cause_time | datetime | None | required |
| order_reset_leg_reset_time | datetime | None | required |
| order_reset_leg_break_time | datetime | None | required |
| order_first_index | int | required |
| order_first_time | datetime | required |
| order_break_index | int | required |
| order_break_time | datetime | required |
| order_confirmation_time | datetime | required |
| order_box_top | Decimal | required |
| order_box_top_source_index | int | required |
| order_box_top_source_time | datetime | required |
| order_box_bottom | Decimal | required |
| order_box_bottom_source_index | int | required |
| order_box_bottom_source_time | datetime | required |
| order_stop_level | Decimal | required |
| order_stop_source_index | int | required |
| order_stop_source_time | datetime | required |
| source_index | int | required |
| source_time | datetime | required |
| price | Decimal | required |
| decision_index | int | required |
| decision_time | datetime | required |
| decision_event_time | datetime | required |

#### `StopAll` — `lifecycle_engine.py`

| Field | Annotation | Default |
| --- | --- | --- |
| direction | str | required |
| number | int | required |
| source_index | int | required |
| source_time | datetime | required |
| price | Decimal | required |
| decision_index | int | required |
| decision_time | datetime | required |
| decision_event_time | datetime | required |
| gate_type | str | required |
| gate_event_time | datetime | required |
| stopped_behavior_type | str | required |
| stopped_behavior_key | str | required |
| stopped_behavior_count | int | required |
| underlying_e_family | str | required |
| underlying_e_number | int | required |
| order_direction | str | required |
| order_reaction_number | int | required |
| order_mode | str | required |
| order_causes | tuple[str, ...] | required |
| order_parent_stop_cause_time | datetime | None | required |
| order_reset_leg_reset_time | datetime | None | required |
| order_reset_leg_break_time | datetime | None | required |
| order_first_index | int | required |
| order_first_time | datetime | required |
| order_break_index | int | required |
| order_break_time | datetime | required |
| order_confirmation_time | datetime | required |
| order_box_top | Decimal | required |
| order_box_top_source_index | int | required |
| order_box_top_source_time | datetime | required |
| order_box_bottom | Decimal | required |
| order_box_bottom_source_index | int | required |
| order_box_bottom_source_time | datetime | required |
| order_stop_level | Decimal | required |
| order_stop_source_index | int | required |
| order_stop_source_time | datetime | required |
| stop_index | int | None | required |
| stop_time | datetime | None | required |
| stop_event_time | datetime | None | required |

#### `Candle` — `reaction_engine.py`

| Field | Annotation | Default |
| --- | --- | --- |
| index | int | required |
| timestamp | datetime | required |
| display_time | str | required |
| tag | str | required |
| open | Decimal | required |
| high | Decimal | required |
| low | Decimal | required |
| close | Decimal | required |

#### `Candidate` — `reaction_engine.py`

| Field | Annotation | Default |
| --- | --- | --- |
| first_idx | int | required |
| first_time | str | required |
| box_top_source_idx | int | required |
| box_top_source_time | str | required |
| box_top | Decimal | required |
| box_bottom_source_idx | int | required |
| box_bottom_source_time | str | required |
| box_bottom | Decimal | required |
| mode | str | required |
| anchor_idx | int | None | None |
| anchor_value | Decimal | None | None |
| leg_boundary_value | Decimal | None | None |
| break_idx | int | None | None |
| break_time | str | None | None |
| intrabar_start | datetime | None | None |
| cross_direction_origin | bool | False |
| cross_direction_chain_owner | bool | False |
| order_gate_decision | str | None | None |
| behavior_public_number | int | None | None |
| behavior_public_box_top | Decimal | None | None |
| behavior_public_box_bottom | Decimal | None | None |
| behavior_confirmation_time | datetime | None | None |
| behavior_first_time | datetime | None | None |
| behavior_internal | bool | False |

#### `ResetEvent` — `reaction_engine.py`

| Field | Annotation | Default |
| --- | --- | --- |
| index | int | required |
| display_time | str | required |
| second_time | str | None | required |
| broken_level | Decimal | required |
| from_first_idx | int | required |

#### `IntrabarAnalysis` — `reaction_engine.py`

| Field | Annotation | Default |
| --- | --- | --- |
| event_second | Candle | required |
| extreme | Decimal | required |
| extreme_source | Candle | required |

#### `DetectionResult` — `reaction_engine.py`

| Field | Annotation | Default |
| --- | --- | --- |
| direction | str | required |
| reactions | list[Candidate] | required |
| resets | list[ResetEvent] | required |
| start_index | int | required |
| end_index | int | required |

#### `SZone` — `s_zone_detector.py`

| Field | Annotation | Default |
| --- | --- | --- |
| direction | str | required |
| color | str | required |
| formation_type | str | required |
| a_ordinal | int | required |
| a_source_index | int | required |
| a_source_time | datetime | required |
| a_price | Decimal | required |
| a_stop_index | int | required |
| a_stop_time | datetime | required |
| a_stop_event_time | datetime | required |
| order_direction | str | None | required |
| order_reaction_number | int | None | required |
| order_mode | str | None | required |
| order_first_index | int | None | required |
| order_first_time | datetime | None | required |
| order_break_index | int | None | required |
| order_break_time | datetime | None | required |
| order_confirmation_time | datetime | None | required |
| order_box_top | Decimal | None | required |
| order_box_top_source_index | int | None | required |
| order_box_top_source_time | datetime | None | required |
| order_box_bottom | Decimal | None | required |
| order_box_bottom_source_index | int | None | required |
| order_box_bottom_source_time | datetime | None | required |
| order_stop_level | Decimal | None | required |
| order_stop_source_index | int | None | required |
| order_stop_source_time | datetime | None | required |
| reset_reaction_number | int | None | required |
| reset_time | datetime | None | required |
| source_index | int | required |
| source_time | datetime | required |
| price | Decimal | required |
| decision_index | int | required |
| decision_time | datetime | required |
| decision_event_time | datetime | required |

#### `EngineBundle` — `trading_pipeline.py`

| Field | Annotation | Default |
| --- | --- | --- |
| reaction | object | required |
| blue_line | object | required |
| a_zone | object | required |
| s_zone | object | required |
| e_zone | object | None | required |
| lifecycle | object | None | required |

#### `MarketContext` — `trading_pipeline.py`

| Field | Annotation | Default |
| --- | --- | --- |
| raw_candles | list[object] | required |
| candles | list[object] | required |
| lower_index | object | required |
| chronology | object | required |
| start_index | int | required |
| end_index | int | required |

#### `PipelineState` — `trading_pipeline.py`

| Field | Annotation | Default |
| --- | --- | --- |
| directions | tuple[str, ...] | required |
| results | dict[str, object] | required |
| reusable_full_context | bool | required |
| initial_order_geometry | dict[str, object] | required |
| internal_reaction_identities | dict[str, set[tuple[int, int]]] | required |
| full_e_zones | dict[str, list[object]] | required |
| full_e_detectors | dict[str, object] | required |
| full_s_detectors | dict[str, object] | required |
| full_lines_by_direction | dict[str, list[object]] | required |
| full_a_by_direction | dict[str, list[object]] | required |
| invalid_a_identities_by_direction | dict[str, set[tuple[datetime, int]]] | required |
| invalid_s_identities_by_direction | dict[str, set[tuple[datetime, int]]] | required |
| full_s_by_direction | dict[str, list[object]] | required |
| full_s_candidates_by_direction | dict[str, list[object]] | required |

#### `FullDirectionState` — `trading_pipeline.py`

| Field | Annotation | Default |
| --- | --- | --- |
| e_zones | list[object] | required |
| e_detector | object | required |
| s_detector | object | required |
| blue_lines | list[object] | required |
| a_zones | list[object] | required |
| invalid_a_identities | set[tuple[datetime, int]] | required |
| invalid_s_identities | set[tuple[datetime, int]] | required |
| s_zones | list[object] | required |
| s_candidates | list[object] | required |

#### `DirectionRangeState` — `trading_pipeline.py`

| Field | Annotation | Default |
| --- | --- | --- |
| blue_lines | list[object] | required |
| a_zones | list[object] | required |
| s_candidates | list[object] | required |
| accepted_s_zones | list[object] | required |
| e_zones | list[object] | required |
| invalid_a_identities | set[tuple[datetime, int]] | required |
| invalid_s_identities | set[tuple[datetime, int]] | required |

#### `DirectionVisibilityState` — `trading_pipeline.py`

| Field | Annotation | Default |
| --- | --- | --- |
| blue_lines | list[object] | required |
| a_zones | list[object] | required |
| s_zones | list[object] | required |
| e_zones | list[object] | required |
| stopalls | list[object] | required |
| prepared_order_audit | list[object] | required |

### 28.2 Calculation-affecting module constants and type aliases

| Source file | Identifier | Frozen value/expression |
| --- | --- | --- |
| a_zone_detector.py | A_ZONE_VERSION | '1.4.2' |
| blue_line_detector.py | BLUE_LINE_VERSION | '2.2.1' |
| blue_line_detector.py | FIBONACCI_RATIO | Decimal('0.618') |
| direction_policy.py | DIRECTION_POLICY_VERSION | '1.0.0' |
| direction_policy.py | _BULLISH | DirectionPolicy(name='bullish', extreme_attr='low', opposite_extreme_attr='high', first_color='RED', context_color='GREEN', order_direction='bearish', is_bullish=True) |
| direction_policy.py | _BEARISH | DirectionPolicy(name='bearish', extreme_attr='high', opposite_extreme_attr='low', first_color='GREEN', context_color='RED', order_direction='bullish', is_bullish=False) |
| e_zone_detector.py | E_ZONE_VERSION | '6.3.1' |
| e_zone_detector.py | OrderMatch | tuple[int, object, datetime, Decimal, int, datetime, tuple[int, datetime, datetime] | None, tuple[str, ...], datetime | None, datetime | None, datetime | None] |
| lifecycle_engine.py | STOP_ALL_VERSION | '1.3.1' |
| lifecycle_engine.py | SEQUENCE_PRIORITY | {('s', 'blue'): 1, ('e', 'blue'): 2, ('s', 'red'): 3, ('e', 'red'): 4} |
| reaction_engine.py | REACTION_ENGINE_VERSION | '9.4.4' |
| reaction_engine.py | _SEQUENCE_TIME_INDEXES | {} |
| reaction_engine.py | _REFLECTED_VIEWS | {} |
| reaction_engine.py | _LOWER_TIMEFRAME_INDEXES | {} |
| s_zone_detector.py | S_ZONE_VERSION | '4.5.1' |
| trading_pipeline.py | _DTFMT | '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}' |
| trading_pipeline.py | TEHRAN | ZoneInfo('Asia/Tehran') |

### 28.3 Exact production function/method signatures

This interface inventory is audit metadata and a naming contract for pseudocode. It is not a requirement to reproduce the same file layout, but any identifier used in pseudocode MUST retain this spelling and semantics.

| File | Identifier | Signature | Return annotation | Line |
| --- | --- | --- | --- | --- |
| a_zone_detector.py | `_decimal` | `_decimal(value: object)` | `Decimal` | 60 |
| a_zone_detector.py | `AZoneDetector.__init__` | `AZoneDetector.__init__(self, direction: str, reactions: Sequence[object], blue_lines: Sequence[object], chronology: object)` | `None` | 65 |
| a_zone_detector.py | `AZoneDetector.extreme_name` | `AZoneDetector.extreme_name(self)` | `str` | 93 |
| a_zone_detector.py | `AZoneDetector._strict_cross` | `AZoneDetector._strict_cross(self, value: Decimal, level: Decimal)` | `bool` | 96 |
| a_zone_detector.py | `AZoneDetector._better` | `AZoneDetector._better(self, value: Decimal, current: Decimal)` | `bool` | 99 |
| a_zone_detector.py | `AZoneDetector._main_index` | `AZoneDetector._main_index(self, timestamp: datetime)` | `int` | 102 |
| a_zone_detector.py | `AZoneDetector._lower_window` | `AZoneDetector._lower_window(self, start: datetime, end: datetime | None)` | `Sequence[object]` | 105 |
| a_zone_detector.py | `AZoneDetector._first_crossing` | `AZoneDetector._first_crossing(self, level: Decimal, start: datetime, end: datetime | None)` | `tuple[int, datetime, Decimal] | None` | 110 |
| a_zone_detector.py | `AZoneDetector._range_extreme` | `AZoneDetector._range_extreme(self, start: datetime, end: datetime)` | `tuple[Decimal, int, datetime]` | 152 |
| a_zone_detector.py | `AZoneDetector._formation` | `AZoneDetector._formation(self, line: object)` | `tuple[int, datetime, datetime]` | 186 |
| a_zone_detector.py | `AZoneDetector._reset_formation_time` | `AZoneDetector._reset_formation_time(self, line: object, source_index: int)` | `datetime` | 203 |
| a_zone_detector.py | `AZoneDetector._build_blue_states` | `AZoneDetector._build_blue_states(self)` | `list[BlueState]` | 215 |
| a_zone_detector.py | `AZoneDetector._double_stop_a_candidates` | `AZoneDetector._double_stop_a_candidates(self)` | `list[AZone]` | 244 |
| a_zone_detector.py | `AZoneDetector._pair_trigger` | `AZoneDetector._pair_trigger(self, previous: BlueState, current: BlueState, expires_at: datetime | None)` | `tuple[Decimal, int, datetime, int, datetime, datetime, datetime, datetime] | None` | 306 |
| a_zone_detector.py | `AZoneDetector._reaction_confirmation_time` | `AZoneDetector._reaction_confirmation_time(self, reaction: object)` | `datetime` | 466 |
| a_zone_detector.py | `AZoneDetector._first_reaction_after` | `AZoneDetector._first_reaction_after(self, trigger_event_time: datetime, *, not_before: datetime | None=None)` | `tuple[int, object] | None` | 471 |
| a_zone_detector.py | `AZoneDetector._inherited_stop` | `AZoneDetector._inherited_stop(self, previous: BlueState, current: BlueState)` | `tuple[Decimal, int, datetime, datetime] | None` | 489 |
| a_zone_detector.py | `AZoneDetector._a_source` | `AZoneDetector._a_source(self, trigger_index: int, reaction: object)` | `tuple[int, datetime, Decimal] | None` | 516 |
| a_zone_detector.py | `AZoneDetector._detect_ordinary_a` | `AZoneDetector._detect_ordinary_a(self, states: list[BlueState])` | `list[AZone]` | 537 |
| a_zone_detector.py | `AZoneDetector._filter_special_a` | `AZoneDetector._filter_special_a(self, special: list[AZone], ordinary: list[AZone])` | `tuple[list[AZone], list[AZone]]` | 647 |
| a_zone_detector.py | `AZoneDetector.detect` | `AZoneDetector.detect(self)` | `list[AZone]` | 711 |
| a_zone_detector.py | `AZoneDetector._a_was_stopped_before` | `AZoneDetector._a_was_stopped_before(self, zone: AZone, end_time: datetime, *, not_before: datetime | None=None)` | `bool` | 723 |
| a_zone_detector.py | `detect_a_zones` | `detect_a_zones(direction: str, reactions: Sequence[object], blue_lines: Sequence[object], chronology: object)` | `list[AZone]` | 749 |
| blue_line_detector.py | `_is_color` | `_is_color(candle: object, color: str)` | `bool` | 48 |
| blue_line_detector.py | `_main_candle` | `_main_candle(candles_by_index: dict[int, object], index: int)` | `object` | 52 |
| blue_line_detector.py | `_stops_on_index` | `_stops_on_index(direction: str, line: object, candles: Sequence[object], start_index: int, end_index: int)` | `bool` | 59 |
| blue_line_detector.py | `fibonacci_level` | `fibonacci_level(direction: str, reaction: object, reference: Decimal)` | `Decimal` | 75 |
| blue_line_detector.py | `_intrabar_pending_confirmation` | `_intrabar_pending_confirmation(direction: str, chronology: object, reaction: object, comparison_extreme: Decimal, start_time: datetime, break_time: datetime, candles_by_index: dict[int, object])` | `ScaleStrike | None` | 84 |
| blue_line_detector.py | `count_scale_strikes` | `count_scale_strikes(direction: str, reaction: object, chronology: object, reference: Decimal, candles_by_index: dict[int, object] | None=None)` | `tuple[Decimal, list[ScaleStrike]]` | 135 |
| blue_line_detector.py | `_build_scale_blue_line` | `_build_scale_blue_line(direction: str, reaction_number: int, previous_count: int, level: Decimal, strikes: Sequence[ScaleStrike], candles_by_index: dict[int, object], chronology: object, behavior_internal: bool)` | `BlueLine` | 196 |
| blue_line_detector.py | `_build_reset_blue_line` | `_build_reset_blue_line(direction: str, reaction_number: int, reset: object, previous_line: BlueLine | None, candles: Sequence[object], candles_by_index: dict[int, object], chronology: object, behavior_internal: bool)` | `BlueLine` | 235 |
| blue_line_detector.py | `detect_blue_lines` | `detect_blue_lines(direction: str, reactions: Sequence[object], chronology: object, resets: Sequence[object]=())` | `list[BlueLine]` | 290 |
| blue_line_detector.py | `public_blue_lines` | `public_blue_lines(lines: Sequence[BlueLine])` | `list[BlueLine]` | 397 |
| blue_line_detector.py | `mark_internal_blue_lines` | `mark_internal_blue_lines(lines: Sequence[BlueLine], owner_reactions: Sequence[object], all_behavior_reactions: Sequence[object])` | `None` | 406 |
| direction_policy.py | `DirectionPolicy.strict_cross` | `DirectionPolicy.strict_cross(self, value: Decimal, level: Decimal)` | `bool` | 22 |
| direction_policy.py | `DirectionPolicy.improves` | `DirectionPolicy.improves(self, value: Decimal, current: Decimal)` | `bool` | 26 |
| direction_policy.py | `get_direction_policy` | `get_direction_policy(direction: str)` | `DirectionPolicy` | 52 |
| e_zone_detector.py | `_decimal` | `_decimal(value: object)` | `Decimal` | 71 |
| e_zone_detector.py | `EZoneDetector.__init__` | `EZoneDetector.__init__(self, direction: str, trend_reactions: Sequence[object], opposite_reactions: Sequence[object], s_zones: Sequence[object], trend_resets: Sequence[object], opposite_resets: Sequence[object], chronology: object, start_index: int=0, end_index: int | None=None, geometry_finder: Callable[[str, int, int], object | None] | None=None, direct_geometry_finder: Callable[[str, int, int, datetime], object | None] | None=None, blocked_order_first_times: set[datetime] | None=None, initial_order_audit: dict[tuple[int, int], dict[str, object]] | None=None, reset_geometry_finder: Callable[[str, int, int, int], object | None] | None=None, sequence_resets: dict[datetime, int] | None=None, sequence_priority: Callable[[str, str], int] | None=None)` | `None` | 76 |
| e_zone_detector.py | `EZoneDetector._reset_time` | `EZoneDetector._reset_time(self, reset: object)` | `datetime` | 194 |
| e_zone_detector.py | `EZoneDetector._main_index` | `EZoneDetector._main_index(self, value: datetime)` | `int` | 197 |
| e_zone_detector.py | `EZoneDetector._first_cross_position` | `EZoneDetector._first_cross_position(self, left: int, right: int, level: Decimal, *, less: bool)` | `int | None` | 201 |
| e_zone_detector.py | `EZoneDetector._stop_value` | `EZoneDetector._stop_value(self, item: object)` | `Decimal` | 218 |
| e_zone_detector.py | `EZoneDetector._first_parent_stop` | `EZoneDetector._first_parent_stop(self, source_time: datetime, level: Decimal)` | `tuple[int, datetime] | None` | 222 |
| e_zone_detector.py | `EZoneDetector._confirmation_for` | `EZoneDetector._confirmation_for(self, reaction: object, direction: str)` | `datetime` | 235 |
| e_zone_detector.py | `EZoneDetector._confirmation` | `EZoneDetector._confirmation(self, reaction: object)` | `datetime` | 238 |
| e_zone_detector.py | `EZoneDetector._reaction_first_time` | `EZoneDetector._reaction_first_time(self, reaction: object)` | `datetime` | 241 |
| e_zone_detector.py | `EZoneDetector._strict_trigger_cross` | `EZoneDetector._strict_trigger_cross(self, start: datetime, level: Decimal)` | `datetime | None` | 244 |
| e_zone_detector.py | `EZoneDetector._reset_leg_geometry` | `EZoneDetector._reset_leg_geometry(self, reset: object, reset_time: datetime)` | `tuple[datetime, Decimal] | None` | 258 |
| e_zone_detector.py | `EZoneDetector._reset_leg_has_simple_trend_reaction` | `EZoneDetector._reset_leg_has_simple_trend_reaction(self, leg_start: datetime, boundary_cross: datetime)` | `bool` | 287 |
| e_zone_detector.py | `EZoneDetector._first_order_b_geometry` | `EZoneDetector._first_order_b_geometry(self, reset_time: datetime, boundary_cross: datetime, deadline: datetime)` | `tuple[int, object, datetime] | None` | 303 |
| e_zone_detector.py | `EZoneDetector._next_outer_reset_time` | `EZoneDetector._next_outer_reset_time(self, reset_position: int, fallback: datetime)` | `datetime` | 439 |
| e_zone_detector.py | `EZoneDetector._replacement_order` | `EZoneDetector._replacement_order(self, owner: object, owner_confirmation: datetime, owner_stop_event: datetime)` | `tuple[int, object, datetime, datetime] | None` | 461 |
| e_zone_detector.py | `EZoneDetector._reset_leg_evidence` | `EZoneDetector._reset_leg_evidence(self, reaction: object, context_start: datetime)` | `tuple[datetime, datetime] | None` | 511 |
| e_zone_detector.py | `EZoneDetector._legacy_reset_leg_evidence` | `EZoneDetector._legacy_reset_leg_evidence(self, reaction: object, context_start: datetime)` | `tuple[datetime, datetime] | None` | 554 |
| e_zone_detector.py | `EZoneDetector._order_stop` | `EZoneDetector._order_stop(self, number: int, reaction: object, context_start: datetime | None=None)` | `tuple[Decimal, int, datetime]` | 595 |
| e_zone_detector.py | `EZoneDetector.order_stop` | `EZoneDetector.order_stop(self, reaction_number: int, reaction: object)` | `tuple[Decimal, int, datetime]` | 607 |
| e_zone_detector.py | `EZoneDetector._first_healthy_direct_geometry` | `EZoneDetector._first_healthy_direct_geometry(self, start: datetime, allow_bounded_continue: bool=False)` | `tuple[int, object, datetime] | None` | 614 |
| e_zone_detector.py | `EZoneDetector._synthetic_reset_leg_orders` | `EZoneDetector._synthetic_reset_leg_orders(self, start: datetime, audit_legacy: bool)` | `list[tuple[int, object, datetime, datetime, datetime]]` | 699 |
| e_zone_detector.py | `EZoneDetector._direct_parent_stop_order` | `EZoneDetector._direct_parent_stop_order(self, start: datetime, continuous_deadline: datetime | None, allow_bounded_continue: bool)` | `tuple[int, object, datetime] | None` | 790 |
| e_zone_detector.py | `EZoneDetector._merge_order_candidate` | `EZoneDetector._merge_order_candidate(self, by_geometry: dict[tuple[int, int], OrderMatch], number: int, reaction: object, confirmation: datetime, cause: str, *, parent_stop_cause_time: datetime | None=None, reset_time: datetime | None=None, reset_break: datetime | None=None)` | `OrderMatch` | 875 |
| e_zone_detector.py | `EZoneDetector._add_canonical_reset_leg_orders` | `EZoneDetector._add_canonical_reset_leg_orders(self, by_geometry: dict[tuple[int, int], OrderMatch], start: datetime, provisional_deadline: datetime, audit_legacy: bool)` | `datetime` | 921 |
| e_zone_detector.py | `EZoneDetector.order_candidates` | `EZoneDetector.order_candidates(self, start: datetime, continuous_deadline: datetime | None=None, audit_legacy: bool=False, allow_bounded_continue: bool=False)` | `list[OrderMatch]` | 958 |
| e_zone_detector.py | `EZoneDetector._first_order` | `EZoneDetector._first_order(self, start: datetime, continuous_deadline: datetime | None=None, allow_bounded_continue: bool=False)` | `OrderMatch | None` | 1043 |
| e_zone_detector.py | `EZoneDetector._blue_parent_superseded` | `EZoneDetector._blue_parent_superseded(self, parent: object, parent_stop: datetime)` | `bool` | 1056 |
| e_zone_detector.py | `EZoneDetector._register_order_audit` | `EZoneDetector._register_order_audit(self, parent_type: str, parent: object, parent_stop: datetime)` | `None` | 1065 |
| e_zone_detector.py | `EZoneDetector._reset_by_proven_order` | `EZoneDetector._reset_by_proven_order(self, reaction: object, confirmation: datetime)` | `bool` | 1194 |
| e_zone_detector.py | `EZoneDetector._enrich_order_audit_reset_causes` | `EZoneDetector._enrich_order_audit_reset_causes(self)` | `None` | 1220 |
| e_zone_detector.py | `EZoneDetector.visual_order_lifecycle` | `EZoneDetector.visual_order_lifecycle(self, start: datetime)` | `list[tuple[int, object, datetime, Decimal, int, datetime, tuple[int, datetime, datetime] | None, bool]]` | 1252 |
| e_zone_detector.py | `EZoneDetector._parent_stop` | `EZoneDetector._parent_stop(self, parent_type: str, parent: object)` | `tuple[int, datetime] | None` | 1294 |
| e_zone_detector.py | `EZoneDetector.parent_stop` | `EZoneDetector.parent_stop(self, parent_type: str, parent: object)` | `tuple[int, datetime] | None` | 1302 |
| e_zone_detector.py | `EZoneDetector._cross_order` | `EZoneDetector._cross_order(self, start: datetime, level: Decimal)` | `tuple[int, datetime, datetime] | None` | 1309 |
| e_zone_detector.py | `EZoneDetector.cross_order` | `EZoneDetector.cross_order(self, confirmation_time: datetime, stop_level: Decimal)` | `tuple[int, datetime, datetime] | None` | 1329 |
| e_zone_detector.py | `EZoneDetector._unconsumed_s_orders` | `EZoneDetector._unconsumed_s_orders(self, parent: object, parent_stop: datetime)` | `list[OrderMatch]` | 1336 |
| e_zone_detector.py | `EZoneDetector._initial_order_match` | `EZoneDetector._initial_order_match(self, entry: dict[str, object], causes: tuple[str, ...])` | `OrderMatch` | 1373 |
| e_zone_detector.py | `EZoneDetector._gate_owned_initial_order` | `EZoneDetector._gate_owned_initial_order(self, parent_stop: datetime)` | `OrderMatch | None` | 1386 |
| e_zone_detector.py | `EZoneDetector._carried_orders_for_parent` | `EZoneDetector._carried_orders_for_parent(self, parent: object, parent_stop: datetime)` | `list[OrderMatch]` | 1414 |
| e_zone_detector.py | `EZoneDetector._blocked_by_gate_owned_order` | `EZoneDetector._blocked_by_gate_owned_order(self, zone: EZone)` | `bool` | 1482 |
| e_zone_detector.py | `EZoneDetector._reset_evidence_for_order` | `EZoneDetector._reset_evidence_for_order(self, first_index: int, break_index: int)` | `tuple[datetime, datetime] | None` | 1492 |
| e_zone_detector.py | `EZoneDetector._extreme_between` | `EZoneDetector._extreme_between(self, start: datetime, end: datetime)` | `tuple[int, datetime, Decimal]` | 1505 |
| e_zone_detector.py | `EZoneDetector._zone` | `EZoneDetector._zone(self, family: str, number: int, parent_type: str, parent: object, stop_event: datetime)` | `EZone | None` | 1521 |
| e_zone_detector.py | `EZoneDetector._discover_candidate_chains` | `EZoneDetector._discover_candidate_chains(self)` | `list[EZone]` | 1623 |
| e_zone_detector.py | `EZoneDetector._reconcile_candidate_chains` | `EZoneDetector._reconcile_candidate_chains(self, candidates: list[EZone])` | `list[EZone]` | 1665 |
| e_zone_detector.py | `EZoneDetector._rebuild_accepted_order_audit` | `EZoneDetector._rebuild_accepted_order_audit(self, numbered: list[EZone])` | `list[EZone]` | 1993 |
| e_zone_detector.py | `EZoneDetector.detect` | `EZoneDetector.detect(self)` | `list[EZone]` | 2100 |
| e_zone_detector.py | `detect_e_zones` | `detect_e_zones(direction: str, trend_reactions: Sequence[object], opposite_reactions: Sequence[object], s_zones: Sequence[object], trend_resets: Sequence[object], opposite_resets: Sequence[object], chronology: object, start_index: int=0, end_index: int | None=None, geometry_finder: Callable[[str, int, int], object | None] | None=None, direct_geometry_finder: Callable[[str, int, int, datetime], object | None] | None=None, blocked_order_first_times: set[datetime] | None=None, initial_order_audit: dict[tuple[int, int], dict[str, object]] | None=None, reset_geometry_finder: Callable[[str, int, int, int], object | None] | None=None, sequence_priority: Callable[[str, str], int] | None=None)` | `list[EZone]` | 2109 |
| lifecycle_engine.py | `sequence_priority` | `sequence_priority(kind: str, family: str)` | `int` | 31 |
| lifecycle_engine.py | `_decimal` | `_decimal(value: object)` | `Decimal` | 36 |
| lifecycle_engine.py | `StopAllDetector.__init__` | `StopAllDetector.__init__(self, direction: str, s_zones: Sequence[object], e_zones: Sequence[object], chronology: object)` | `None` | 84 |
| lifecycle_engine.py | `StopAllDetector._strict_stop` | `StopAllDetector._strict_stop(self, start: datetime, level: Decimal)` | `tuple[int, datetime, datetime] | None` | 105 |
| lifecycle_engine.py | `StopAllDetector._e_key` | `StopAllDetector._e_key(item: object)` | `tuple[str, int]` | 122 |
| lifecycle_engine.py | `StopAllDetector._dominates_e` | `StopAllDetector._dominates_e(new: tuple[str, int], old: tuple[str, int])` | `bool` | 126 |
| lifecycle_engine.py | `StopAllDetector._sequence_priority` | `StopAllDetector._sequence_priority(cls, kind: str, family: str)` | `int` | 136 |
| lifecycle_engine.py | `StopAllDetector._active_sequence_priority` | `StopAllDetector._active_sequence_priority(cls, s_key: str | None, e_key: tuple[str, int] | None)` | `int` | 140 |
| lifecycle_engine.py | `StopAllDetector._stopall_from_e` | `StopAllDetector._stopall_from_e(self, item: object, number: int, gate_type: str, gate_event: datetime, behavior_type: str, behavior_key: str, behavior_count: int)` | `StopAll` | 149 |
| lifecycle_engine.py | `StopAllDetector.detect` | `StopAllDetector.detect(self)` | `list[StopAll]` | 207 |
| lifecycle_engine.py | `detect_stopalls` | `detect_stopalls(direction: str, s_zones: Sequence[object], e_zones: Sequence[object], chronology: object)` | `list[StopAll]` | 326 |
| lifecycle_engine.py | `prepare_order_audit` | `prepare_order_audit(detector, start_index: int, end_index: int, s_detector=None, accepted_a_sources: set[datetime] | None=None)` |  | 338 |
| lifecycle_engine.py | `accepted_audit_entry` | `accepted_audit_entry(entry: dict[str, object], accepted_sources: set)` | `dict[str, object] | None` | 431 |
| lifecycle_engine.py | `resolve_order_context` | `resolve_order_context(order_audit: dict, accepted_a_sources: set[datetime], inherited_blocked_first_times: set[datetime], invalid_a_zones: Sequence[object], pending_s_a_sources: set[datetime], opposite_reactions: Sequence[object], candles: Sequence[object], direction: str, stop_finder)` | `tuple[dict, set[datetime]]` | 460 |
| lifecycle_engine.py | `visible_a_zones_after_s_stops` | `visible_a_zones_after_s_stops(a_zones, s_zones, candles)` |  | 512 |
| lifecycle_engine.py | `module_priority` | `module_priority(item)` |  | 528 |
| lifecycle_engine.py | `module_identity` | `module_identity(item)` |  | 542 |
| lifecycle_engine.py | `module_stop_event` | `module_stop_event(item, stop_event_finder=None)` |  | 551 |
| lifecycle_engine.py | `strictly_beyond_boundary` | `strictly_beyond_boundary(price, boundary, direction)` |  | 565 |
| lifecycle_engine.py | `dominant_module` | `dominant_module(modules)` |  | 568 |
| lifecycle_engine.py | `split_a_zones_by_dominant_stops` | `split_a_zones_by_dominant_stops(a_zones, s_zones, e_zones, stopalls, candles, direction, stop_event_finder=None, trend_reactions=None, confirmation_finder=None)` |  | 579 |
| lifecycle_engine.py | `blocked_orders_while_invalid_leg_heads_are_live` | `blocked_orders_while_invalid_leg_heads_are_live(invalid_a_zones, opposite_reactions, candles, direction, stop_finder)` |  | 730 |
| lifecycle_engine.py | `s_zones_for_module_engines` | `s_zones_for_module_engines(s_zones, e_zones, direction)` |  | 752 |
| lifecycle_engine.py | `visible_s_zones_after_module_resets` | `visible_s_zones_after_module_resets(s_zones, e_zones, direction, stop_event_finder=None, source_event_finder=None, candles=None)` |  | 777 |
| lifecycle_engine.py | `reconcile_stopall_lifecycle` | `reconcile_stopall_lifecycle(detector, s_zones, e_zones, chronology, direction, timed_step=None)` |  | 946 |
| lifecycle_engine.py | `visible_a_zones_after_module_boundaries` | `visible_a_zones_after_module_boundaries(a_zones, s_zones, e_zones, direction, stop_event_finder=None)` |  | 980 |
| lifecycle_engine.py | `reaction_number_is_internal` | `reaction_number_is_internal(items, number, identities)` |  | 1027 |
| lifecycle_engine.py | `order_identity_is_internal` | `order_identity_is_internal(item, internal_identities)` |  | 1042 |
| lifecycle_engine.py | `point_is_inside_healthy_reaction` | `point_is_inside_healthy_reaction(source_time, price, reactions)` |  | 1051 |
| lifecycle_engine.py | `forbidden_internal_order_b` | `forbidden_internal_order_b(item, internal_identities)` |  | 1074 |
| lifecycle_engine.py | `_is_advanced_blue_s` | `_is_advanced_blue_s(item)` |  | 1088 |
| lifecycle_engine.py | `filter_internal_behavior_outputs` | `filter_internal_behavior_outputs(a_zones, s_zones, e_zones, stopalls, opposite_reactions, opposite_internal_identities, all_behavior_reactions)` |  | 1095 |
| lifecycle_engine.py | `finalize_behavior_visibility` | `finalize_behavior_visibility(a_zones, s_zones, e_zones, stopalls, direction, invalid_s_identities, stop_event_finder, source_event_finder, candles, *, all_a_zones=None)` |  | 1154 |
| lifecycle_engine.py | `visible_a_zones` | `visible_a_zones(a_zones: Sequence[object], s_zones: Sequence[object])` | `list[object]` | 1249 |
| reaction_engine.py | `classify_candle_color` | `classify_candle_color(open_price: Decimal, close_price: Decimal)` | `str` | 89 |
| reaction_engine.py | `opposite_direction` | `opposite_direction(direction: str)` | `str` | 94 |
| reaction_engine.py | `DetectorBase.__init__` | `DetectorBase.__init__(self, candles: Sequence[Candle], raw_candles: Sequence[Candle], start_index: int, end_index: int)` | `None` | 104 |
| reaction_engine.py | `DetectorBase._shared_time_index` | `DetectorBase._shared_time_index(candles: Sequence[Candle])` | `list[datetime]` | 129 |
| reaction_engine.py | `DetectorBase.raw_between` | `DetectorBase.raw_between(self, start: datetime, end: datetime)` | `Iterable[Candle]` | 139 |
| reaction_engine.py | `DetectorBase.main_source_for_time` | `DetectorBase.main_source_for_time(self, timestamp: datetime)` | `Candle | None` | 144 |
| reaction_engine.py | `DetectorBase.minimum_low` | `DetectorBase.minimum_low(self, start_index: int, end_index: int)` | `tuple[Decimal, Candle]` | 157 |
| reaction_engine.py | `DetectorBase.maximum_high` | `DetectorBase.maximum_high(self, start_index: int, end_index: int)` | `tuple[Decimal, Candle]` | 166 |
| reaction_engine.py | `BullishDetector._is_context_color` | `BullishDetector._is_context_color(self, candle: Candle)` | `bool` | 185 |
| reaction_engine.py | `BullishDetector._is_first_color` | `BullishDetector._is_first_color(self, candle: Candle)` | `bool` | 188 |
| reaction_engine.py | `BullishDetector.green_run_peak_before` | `BullishDetector.green_run_peak_before(self, first_red_index: int)` | `tuple[Decimal, Candle]` | 191 |
| reaction_engine.py | `BullishDetector.breakout_analysis` | `BullishDetector.breakout_analysis(self, candidate: Candidate, breakout_candle: Candle)` | `IntrabarAnalysis | None` | 204 |
| reaction_engine.py | `BullishDetector.mode_a_invalidation_before_breakout` | `BullishDetector.mode_a_invalidation_before_breakout(self, candidate: Candidate, candle: Candle)` | `bool` | 230 |
| reaction_engine.py | `BullishDetector.confirmed_reset_before_breakout` | `BullishDetector.confirmed_reset_before_breakout(self, candidate: Candidate | None, candle: Candle, confirmed_bottom: Decimal)` | `bool` | 266 |
| reaction_engine.py | `BullishDetector.post_breakout_reset` | `BullishDetector.post_breakout_reset(self, analysis: IntrabarAnalysis | None, box_bottom: Decimal, breakout_candle: Candle)` | `Candle | None` | 286 |
| reaction_engine.py | `BullishDetector.detect` | `BullishDetector.detect(self, *, first_only: bool=False)` | `DetectionResult` | 301 |
| reaction_engine.py | `mirror_candle` | `mirror_candle(candle: Candle)` | `Candle` | 579 |
| reaction_engine.py | `mirror_candidate` | `mirror_candidate(candidate: Candidate | None)` | `Candidate | None` | 599 |
| reaction_engine.py | `mirror_analysis` | `mirror_analysis(analysis: IntrabarAnalysis | None)` | `IntrabarAnalysis | None` | 618 |
| reaction_engine.py | `_ReflectedCandles.__init__` | `_ReflectedCandles.__init__(self, source: Sequence[Candle])` | `None` | 635 |
| reaction_engine.py | `_ReflectedCandles.__len__` | `_ReflectedCandles.__len__(self)` | `int` | 639 |
| reaction_engine.py | `_ReflectedCandles.__getitem__` | `_ReflectedCandles.__getitem__(self, index)` |  | 642 |
| reaction_engine.py | `_reflected_view` | `_reflected_view(source: Sequence[Candle])` | `_ReflectedCandles` | 655 |
| reaction_engine.py | `BearishDetector.__init__` | `BearishDetector.__init__(self, candles, raw_candles, start_index, end_index)` |  | 673 |
| reaction_engine.py | `BearishDetector.red_run_bottom_before` | `BearishDetector.red_run_bottom_before(self, first_green_index)` |  | 693 |
| reaction_engine.py | `BearishDetector.breakdown_analysis` | `BearishDetector.breakdown_analysis(self, candidate, breakdown_candle)` |  | 697 |
| reaction_engine.py | `BearishDetector.invalidation_high_break_before_breakdown` | `BearishDetector.invalidation_high_break_before_breakdown(self, candidate, candle)` |  | 702 |
| reaction_engine.py | `BearishDetector.confirmed_reset_before_breakdown` | `BearishDetector.confirmed_reset_before_breakdown(self, candidate, candle, confirmed_top)` |  | 707 |
| reaction_engine.py | `BearishDetector.post_breakdown_reset` | `BearishDetector.post_breakdown_reset(self, analysis, box_top, breakdown_candle)` |  | 713 |
| reaction_engine.py | `BearishDetector.detect` | `BearishDetector.detect(self, *, first_only: bool=False)` | `DetectionResult` | 720 |
| reaction_engine.py | `published_reaction_candidate` | `published_reaction_candidate(direction: str, candidate: Candidate, chronology: object)` | `Candidate` | 731 |
| reaction_engine.py | `_decimal_value` | `_decimal_value(value: object)` | `Decimal` | 829 |
| reaction_engine.py | `LowerTimeframeIndex.__init__` | `LowerTimeframeIndex.__init__(self, candles: Sequence[Candle])` | `None` | 841 |
| reaction_engine.py | `LowerTimeframeIndex.first_less` | `LowerTimeframeIndex.first_less(self, left: int, right: int, level: Decimal)` | `int | None` | 882 |
| reaction_engine.py | `LowerTimeframeIndex.first_greater` | `LowerTimeframeIndex.first_greater(self, left: int, right: int, level: Decimal)` | `int | None` | 885 |
| reaction_engine.py | `LowerTimeframeIndex.range_minimum` | `LowerTimeframeIndex.range_minimum(self, left: int, right: int)` | `tuple[Decimal, int]` | 888 |
| reaction_engine.py | `LowerTimeframeIndex.range_maximum` | `LowerTimeframeIndex.range_maximum(self, left: int, right: int)` | `tuple[Decimal, int]` | 892 |
| reaction_engine.py | `LowerTimeframeIndex._range_query` | `LowerTimeframeIndex._range_query(self, left: int, right: int, *, minimum: bool)` | `tuple[Decimal, int]` | 896 |
| reaction_engine.py | `LowerTimeframeIndex._first` | `LowerTimeframeIndex._first(self, node: int, start: int, end: int, left: int, right: int, level: Decimal, less: bool)` | `int | None` | 934 |
| reaction_engine.py | `shared_lower_timeframe_index` | `shared_lower_timeframe_index(candles: Sequence[Candle])` | `LowerTimeframeIndex` | 959 |
| reaction_engine.py | `ReflectedLowerTimeframeIndex.__init__` | `ReflectedLowerTimeframeIndex.__init__(self, base: LowerTimeframeIndex)` | `None` | 977 |
| reaction_engine.py | `ReflectedLowerTimeframeIndex.first_less` | `ReflectedLowerTimeframeIndex.first_less(self, left: int, right: int, level: Decimal)` | `int | None` | 981 |
| reaction_engine.py | `ReflectedLowerTimeframeIndex.first_greater` | `ReflectedLowerTimeframeIndex.first_greater(self, left: int, right: int, level: Decimal)` | `int | None` | 984 |
| reaction_engine.py | `ReflectedLowerTimeframeIndex.range_minimum` | `ReflectedLowerTimeframeIndex.range_minimum(self, left: int, right: int)` | `tuple[Decimal, int]` | 987 |
| reaction_engine.py | `ReflectedLowerTimeframeIndex.range_maximum` | `ReflectedLowerTimeframeIndex.range_maximum(self, left: int, right: int)` | `tuple[Decimal, int]` | 991 |
| reaction_engine.py | `MarketChronology.__init__` | `MarketChronology.__init__(self, candles: Sequence[Candle], raw_candles: Sequence[Candle], timeframe_seconds: int, lower_index: LowerTimeframeIndex | None=None)` | `None` | 1015 |
| reaction_engine.py | `MarketChronology.opposite_direction` | `MarketChronology.opposite_direction(direction: str)` | `str` | 1038 |
| reaction_engine.py | `MarketChronology.main_index` | `MarketChronology.main_index(self, timestamp: datetime, *, clamp: bool=False)` | `int` | 1042 |
| reaction_engine.py | `MarketChronology.lower_bounds` | `MarketChronology.lower_bounds(self, start: datetime, end: datetime | None=None)` | `tuple[int, int]` | 1051 |
| reaction_engine.py | `MarketChronology.lower_window` | `MarketChronology.lower_window(self, start: datetime, end: datetime | None=None)` | `Sequence[Candle]` | 1062 |
| reaction_engine.py | `MarketChronology._reset_cache_key` | `MarketChronology._reset_cache_key(reset: object)` | `tuple[object, ...]` | 1069 |
| reaction_engine.py | `MarketChronology._reaction_cache_key` | `MarketChronology._reaction_cache_key(reaction: object, direction: str, use_intrabar_start: bool)` | `tuple[object, ...]` | 1081 |
| reaction_engine.py | `MarketChronology.reset_time` | `MarketChronology.reset_time(self, reset: object)` | `datetime` | 1095 |
| reaction_engine.py | `MarketChronology.reaction_confirmation` | `MarketChronology.reaction_confirmation(self, direction: str, reaction: object, *, use_intrabar_start: bool=True)` | `datetime` | 1114 |
| reaction_engine.py | `MarketChronology.canonical_order_stop` | `MarketChronology.canonical_order_stop(self, order_direction: str, reaction_number: int, reaction: object, opposite_reactions: Sequence[object], *, start_index: int=0)` | `tuple[Decimal, int, datetime]` | 1162 |
| reaction_engine.py | `build_behavior_reaction_views` | `build_behavior_reaction_views(full_results: dict[str, object], chronology: MarketChronology)` |  | 1227 |
| reaction_engine.py | `directional_a_stop_order_finder` | `directional_a_stop_order_finder(candles: Sequence[Candle], raw_candles: Sequence[Candle], direction: str)` |  | 1335 |
| reaction_engine.py | `UnifiedReactionDetector.__init__` | `UnifiedReactionDetector.__init__(self, candles: Sequence[Candle], raw_candles: Sequence[Candle], start_index: int, end_index: int, output_direction: str)` | `None` | 1408 |
| reaction_engine.py | `UnifiedReactionDetector.bull` | `UnifiedReactionDetector.bull(self)` | `BullishDetector` | 1434 |
| reaction_engine.py | `UnifiedReactionDetector.bear` | `UnifiedReactionDetector.bear(self)` | `BearishDetector` | 1442 |
| reaction_engine.py | `UnifiedReactionDetector._append_reaction` | `UnifiedReactionDetector._append_reaction(self, direction: str, candidate: Candidate)` | `bool` | 1449 |
| reaction_engine.py | `UnifiedReactionDetector._append_reset` | `UnifiedReactionDetector._append_reset(self, direction: str, candle: Candle, level: Decimal, first_idx: int, second_time: str | None=None)` | `None` | 1515 |
| reaction_engine.py | `UnifiedReactionDetector._refine` | `UnifiedReactionDetector._refine(self, direction: str, candidate: Candidate, candle: Candle)` | `IntrabarAnalysis | None` | 1533 |
| reaction_engine.py | `UnifiedReactionDetector._candidate_from_confirmation_remainder` | `UnifiedReactionDetector._candidate_from_confirmation_remainder(self, direction: str, confirmed: Candidate, candle: Candle, analysis: IntrabarAnalysis | None)` | `Candidate | None` | 1554 |
| reaction_engine.py | `UnifiedReactionDetector._first_initial` | `UnifiedReactionDetector._first_initial(self, direction: str)` | `Candidate | None` | 1623 |
| reaction_engine.py | `UnifiedReactionDetector._first_direct_same_direction_after_reset` | `UnifiedReactionDetector._first_direct_same_direction_after_reset(self, direction: str, reset_index: int)` | `Candidate | None` | 1636 |
| reaction_engine.py | `UnifiedReactionDetector._first_geometry_after_reset` | `UnifiedReactionDetector._first_geometry_after_reset(self, direction: str, reset_index: int, end_index: int | None=None)` | `Candidate | None` | 1674 |
| reaction_engine.py | `UnifiedReactionDetector.first_geometry_after_reset` | `UnifiedReactionDetector.first_geometry_after_reset(self, direction: str, reset_index: int, end_index: int)` | `Candidate | None` | 1726 |
| reaction_engine.py | `UnifiedReactionDetector.first_simple_geometry_after_gate` | `UnifiedReactionDetector.first_simple_geometry_after_gate(self, direction: str, reset_index: int, gate_index: int, end_index: int | None=None)` | `Candidate | None` | 1733 |
| reaction_engine.py | `UnifiedReactionDetector._reaction_break_indices` | `UnifiedReactionDetector._reaction_break_indices(self, direction: str)` | `list[int]` | 1781 |
| reaction_engine.py | `UnifiedReactionDetector.first_order_reaction_after_gate` | `UnifiedReactionDetector.first_order_reaction_after_gate(self, direction: str, gate_index: int, end_index: int | None=None, gate_event_time: datetime | None=None)` | `Candidate | None` | 1796 |
| reaction_engine.py | `UnifiedReactionDetector._earliest_confirmed_geometry` | `UnifiedReactionDetector._earliest_confirmed_geometry(self, direction: str, start_index: int, end_index: int | None=None)` | `Candidate | None` | 1916 |
| reaction_engine.py | `UnifiedReactionDetector._build_direct_candidate` | `UnifiedReactionDetector._build_direct_candidate(self, direction: str, reset_index: int, first_index: int)` | `Candidate | None` | 1971 |
| reaction_engine.py | `UnifiedReactionDetector._scan_direct_candidate` | `UnifiedReactionDetector._scan_direct_candidate(self, direction: str, candidate: Candidate, stop_index: int)` | `tuple[Candidate | None, int | None]` | 2029 |
| reaction_engine.py | `UnifiedReactionDetector._owner_boundary_before_confirmation` | `UnifiedReactionDetector._owner_boundary_before_confirmation(self, direction: str, candidate: Candidate, candle: Candle)` | `bool` | 2059 |
| reaction_engine.py | `UnifiedReactionDetector._result` | `UnifiedReactionDetector._result(self)` | `DetectionResult` | 2100 |
| reaction_engine.py | `UnifiedReactionDetector.detect` | `UnifiedReactionDetector.detect(self, *, stop_after_first_at_or_after: int | None=None)` | `DetectionResult` | 2109 |
| s_zone_detector.py | `_decimal` | `_decimal(value: object)` | `Decimal` | 61 |
| s_zone_detector.py | `SZoneDetector.__init__` | `SZoneDetector.__init__(self, direction: str, trend_reactions: Sequence[object], opposite_reactions: Sequence[object], trend_blue_lines: Sequence[object], a_zones: Sequence[object], chronology: object, start_index: int | None=None, end_index: int | None=None, opposite_resets: Sequence[object]=(), initial_order_geometry: Callable[[int, datetime, int], object | None] | None=None)` | `None` | 66 |
| s_zone_detector.py | `SZoneDetector._main_index` | `SZoneDetector._main_index(self, timestamp: datetime)` | `int` | 132 |
| s_zone_detector.py | `SZoneDetector._lower_window` | `SZoneDetector._lower_window(self, start: datetime, end: datetime | None)` | `Sequence[object]` | 135 |
| s_zone_detector.py | `SZoneDetector._reaction_confirmation_time` | `SZoneDetector._reaction_confirmation_time(self, reaction: object, direction: str)` | `datetime` | 140 |
| s_zone_detector.py | `SZoneDetector.reaction_confirmation_time` | `SZoneDetector.reaction_confirmation_time(self, reaction: object, direction: str)` | `datetime` | 145 |
| s_zone_detector.py | `SZoneDetector._reset_time` | `SZoneDetector._reset_time(self, reset: object)` | `datetime` | 152 |
| s_zone_detector.py | `SZoneDetector._a_confirmation_time` | `SZoneDetector._a_confirmation_time(self, zone: object)` | `datetime` | 155 |
| s_zone_detector.py | `SZoneDetector._trend_extreme` | `SZoneDetector._trend_extreme(self, candle: object)` | `Decimal` | 163 |
| s_zone_detector.py | `SZoneDetector._a_stopped` | `SZoneDetector._a_stopped(self, value: Decimal, level: Decimal)` | `bool` | 168 |
| s_zone_detector.py | `SZoneDetector._first_a_stop` | `SZoneDetector._first_a_stop(self, level: Decimal, start: datetime)` | `tuple[int, datetime, datetime] | None` | 171 |
| s_zone_detector.py | `SZoneDetector.first_a_stop` | `SZoneDetector.first_a_stop(self, level: Decimal, start: datetime)` | `tuple[int, datetime, datetime] | None` | 207 |
| s_zone_detector.py | `SZoneDetector._first_order_after` | `SZoneDetector._first_order_after(self, a_stop_event_time: datetime)` | `tuple[int, object, datetime] | None` | 214 |
| s_zone_detector.py | `SZoneDetector._audit_stopped_a` | `SZoneDetector._audit_stopped_a(self, zone: object)` | `None` | 294 |
| s_zone_detector.py | `SZoneDetector._candidate_source` | `SZoneDetector._candidate_source(self, start_index: int, end_index: int)` | `tuple[int, datetime, Decimal]` | 336 |
| s_zone_detector.py | `SZoneDetector._candidate_source_last` | `SZoneDetector._candidate_source_last(self, start_index: int, end_index: int)` | `tuple[int, datetime, Decimal]` | 353 |
| s_zone_detector.py | `SZoneDetector._first_trend_reaction_after_order` | `SZoneDetector._first_trend_reaction_after_order(self, order_confirmation_time: datetime)` | `tuple[int, object, datetime] | None` | 371 |
| s_zone_detector.py | `SZoneDetector._nested_trend_reaction` | `SZoneDetector._nested_trend_reaction(self, order: object, order_confirmation_time: datetime)` | `tuple[int, object, datetime] | None` | 383 |
| s_zone_detector.py | `SZoneDetector._simple_candidate` | `SZoneDetector._simple_candidate(self, order: object, reaction: object)` | `tuple[int, datetime, Decimal]` | 413 |
| s_zone_detector.py | `SZoneDetector._type3_reset_leg` | `SZoneDetector._type3_reset_leg(self, reset: object)` | `tuple[int, datetime, Decimal] | None` | 422 |
| s_zone_detector.py | `SZoneDetector._type3_has_trend_reaction` | `SZoneDetector._type3_has_trend_reaction(self, a_stop_event: datetime, crossing: datetime)` | `bool` | 438 |
| s_zone_detector.py | `SZoneDetector._first_type3` | `SZoneDetector._first_type3(self, a_stop_event: datetime, deadline: datetime)` | `tuple[int, datetime, Decimal, int, datetime, int, datetime, datetime] | None` | 448 |
| s_zone_detector.py | `SZoneDetector._candidate_after_order` | `SZoneDetector._candidate_after_order(self, order_confirmation_time: datetime, reaction: object)` | `tuple[int, datetime, Decimal]` | 519 |
| s_zone_detector.py | `SZoneDetector._a_source_event_time` | `SZoneDetector._a_source_event_time(self, zone: object)` | `datetime` | 560 |
| s_zone_detector.py | `SZoneDetector._a_owned_by_s` | `SZoneDetector._a_owned_by_s(self, zone: object)` | `bool` | 569 |
| s_zone_detector.py | `SZoneDetector._a_pair_is_reset_reset` | `SZoneDetector._a_pair_is_reset_reset(self, zone: object)` | `bool` | 601 |
| s_zone_detector.py | `SZoneDetector.eligible_a_zones` | `SZoneDetector.eligible_a_zones(self)` | `list[object]` | 615 |
| s_zone_detector.py | `SZoneDetector._candidate_timing` | `SZoneDetector._candidate_timing(self, a_stop_index: int, order: object, order_confirmation_time: datetime)` | `str` | 619 |
| s_zone_detector.py | `SZoneDetector._candidate_before_order` | `SZoneDetector._candidate_before_order(self, a_stop_index: int, order: object, a_stop_event_time: datetime | None=None)` | `tuple[int, datetime, Decimal]` | 642 |
| s_zone_detector.py | `SZoneDetector._candidate_event_time` | `SZoneDetector._candidate_event_time(self, source_index: int, level: Decimal, not_before: datetime)` | `datetime` | 682 |
| s_zone_detector.py | `SZoneDetector.candidate_event_time` | `SZoneDetector.candidate_event_time(self, source_index: int, price: Decimal, fallback: datetime)` | `datetime` | 697 |
| s_zone_detector.py | `SZoneDetector._blue_formation_time` | `SZoneDetector._blue_formation_time(self, line: object)` | `datetime` | 704 |
| s_zone_detector.py | `SZoneDetector._candidate_cross_has_blue` | `SZoneDetector._candidate_cross_has_blue(self, reaction_number: int, event_time: datetime)` | `bool` | 734 |
| s_zone_detector.py | `SZoneDetector._has_ordinary_trend_reaction` | `SZoneDetector._has_ordinary_trend_reaction(self, behavior_start: datetime, event_time: datetime)` | `bool` | 751 |
| s_zone_detector.py | `SZoneDetector._order_stop` | `SZoneDetector._order_stop(self, order_number: int, reaction: object)` | `tuple[Decimal, int, datetime]` | 771 |
| s_zone_detector.py | `SZoneDetector._candidate_crossed` | `SZoneDetector._candidate_crossed(self, candle: object, level: Decimal)` | `bool` | 782 |
| s_zone_detector.py | `SZoneDetector._order_stop_crossed` | `SZoneDetector._order_stop_crossed(self, candle: object, level: Decimal)` | `bool` | 786 |
| s_zone_detector.py | `SZoneDetector._decision` | `SZoneDetector._decision(self, candidate_level: Decimal, order_stop_level: Decimal, start: datetime, trend_reaction_number: int, behavior_start: datetime, candidate_start: datetime | None=None, fallback_on_unqualified_cross: bool=False)` | `tuple[str, int, datetime, datetime] | None` | 791 |
| s_zone_detector.py | `SZoneDetector._build_type3_zone` | `SZoneDetector._build_type3_zone(self, zone: object, a_ordinal: int, a_price: Decimal, a_stop: tuple[int, datetime, datetime], type3: tuple[int, datetime, Decimal, int, datetime, int, datetime, datetime])` | `SZone` | 885 |
| s_zone_detector.py | `SZoneDetector._build_order_backed_zone` | `SZoneDetector._build_order_backed_zone(self, zone: object, a_ordinal: int, a_price: Decimal, a_stop: tuple[int, datetime, datetime], order_match: tuple[int, object, datetime])` | `SZone | None` | 943 |
| s_zone_detector.py | `SZoneDetector.detect` | `SZoneDetector.detect(self)` | `list[SZone]` | 1114 |
| s_zone_detector.py | `detect_s_zones` | `detect_s_zones(direction: str, trend_reactions: Sequence[object], opposite_reactions: Sequence[object], trend_blue_lines: Sequence[object], a_zones: Sequence[object], chronology: object, start_index: int | None=None, end_index: int | None=None, opposite_resets: Sequence[object]=(), initial_order_geometry: Callable[[int, datetime, int], object | None] | None=None)` | `list[SZone]` | 1183 |
| trading_pipeline.py | `emit_progress` | `emit_progress(status: str, label: str, duration_ms: float | None=None)` |  | 29 |
| trading_pipeline.py | `timed` | `timed(timings: dict[str, float], label: str, work)` |  | 37 |
| trading_pipeline.py | `load_module` | `load_module(name: str, path: Path)` |  | 49 |
| trading_pipeline.py | `load_engine` | `load_engine(path: Path)` |  | 59 |
| trading_pipeline.py | `decimal` | `decimal(value: object)` | `Decimal` | 63 |
| trading_pipeline.py | `local_datetime` | `local_datetime(epoch_value: int)` | `datetime` | 67 |
| trading_pipeline.py | `epoch` | `epoch(local: datetime)` | `int` | 72 |
| trading_pipeline.py | `isolate_raw_range` | `isolate_raw_range(source_rows: list[dict], from_time: int, end_exclusive: int)` | `list[dict]` | 77 |
| trading_pipeline.py | `_price_normalizer` | `_price_normalizer()` |  | 87 |
| trading_pipeline.py | `build_native_raw_candles` | `build_native_raw_candles(engine, rows: list[dict])` | `list[object]` | 103 |
| trading_pipeline.py | `build_timeframe_buckets` | `build_timeframe_buckets(rows: list[dict], raw_candles: list[object], timeframe: int)` | `list[dict]` | 134 |
| trading_pipeline.py | `build_candle_objects` | `build_candle_objects(engine, buckets: list[dict])` |  | 161 |
| trading_pipeline.py | `serialize` | `serialize(result, start_index=None, end_index=None, reaction_transform=None)` |  | 191 |
| trading_pipeline.py | `serialize_blue_lines` | `serialize_blue_lines(items, start_index=None, end_index=None)` |  | 239 |
| trading_pipeline.py | `serialize_a_zones` | `serialize_a_zones(items)` |  | 264 |
| trading_pipeline.py | `serialize_s_zones` | `serialize_s_zones(items)` |  | 291 |
| trading_pipeline.py | `serialize_e_zones` | `serialize_e_zones(items)` |  | 356 |
| trading_pipeline.py | `serialize_stopalls` | `serialize_stopalls(items)` |  | 407 |
| trading_pipeline.py | `serialize_order_audit` | `serialize_order_audit(prepared_items, detector)` |  | 460 |
| trading_pipeline.py | `parse_arguments` | `parse_arguments(argv=None)` |  | 538 |
| trading_pipeline.py | `load_engines` | `load_engines(args, timings: dict[str, float])` | `EngineBundle` | 605 |
| trading_pipeline.py | `prepare_market_context` | `prepare_market_context(args, engines: EngineBundle, timings: dict[str, float])` | `MarketContext` | 639 |
| trading_pipeline.py | `create_e_detector` | `create_e_detector(direction: str, e_engine, full_results: dict[str, object], s_zones: list[object], chronology, geometry_detectors: dict[str, object], initial_order_audit, lifecycle_engine, *, blocked_order_first_times: set[datetime] | None=None)` |  | 727 |
| trading_pipeline.py | `calculate_full_direction_state` | `calculate_full_direction_state(direction: str, engines: EngineBundle, market: MarketContext, full_results: dict[str, object], geometry_detectors: dict[str, object], initial_order_geometry: dict[str, object], timings: dict[str, float])` | `FullDirectionState` | 789 |
| trading_pipeline.py | `prepare_pipeline_state` | `prepare_pipeline_state(args, engines: EngineBundle, market: MarketContext, timings: dict[str, float])` | `PipelineState` | 969 |
| trading_pipeline.py | `calculate_direction_range_state` | `calculate_direction_range_state(direction: str, args, engines: EngineBundle, market: MarketContext, state: PipelineState, timings: dict[str, float])` | `DirectionRangeState` | 1110 |
| trading_pipeline.py | `finalize_direction_visibility` | `finalize_direction_visibility(direction: str, args, engines: EngineBundle, market: MarketContext, state: PipelineState, direction_state: DirectionRangeState, timings: dict[str, float])` | `DirectionVisibilityState` | 1212 |
| trading_pipeline.py | `serialize_direction_payload` | `serialize_direction_payload(direction: str, args, engines: EngineBundle, market: MarketContext, state: PipelineState, visibility: DirectionVisibilityState, timings: dict[str, float])` |  | 1361 |
| trading_pipeline.py | `build_direction_output` | `build_direction_output(direction: str, args, engines: EngineBundle, market: MarketContext, state: PipelineState, timings: dict[str, float])` |  | 1415 |
| trading_pipeline.py | `build_response_payload` | `build_response_payload(args, engines: EngineBundle, market: MarketContext, state: PipelineState, timings: dict[str, float], pipeline_started: float)` | `dict[str, object]` | 1440 |
| trading_pipeline.py | `main` | `main()` | `int` | 1492 |

## 29. Complete Function Reconstruction Contracts

This appendix is normative and closes function-level reconstruction ambiguity. Every production function and method from the eight frozen source modules is reproduced below as a source-faithful executable pseudocode contract. The blocks use the exact production identifiers, comparison operators, branch order, loop order, cache semantics, exceptions, and return behavior. A reimplementation MAY be reorganized internally, but its observable behavior MUST remain equivalent to these contracts.

The purpose of this appendix is precision, not external source dependency: all required implementation logic is present inside this document. The source files named in `Source-Origin` are provenance labels only.

### FUN-A-001 — `_decimal`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:_decimal`  
Source-Lines: 60-61  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _decimal(value: object) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))
```

### FUN-A-002 — `AZoneDetector.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector.__init__`  
Source-Lines: 65-90  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(
        self,
        direction: str,
        reactions: Sequence[object],
        blue_lines: Sequence[object],
        chronology: object,
    ) -> None:
        self.policy = get_direction_policy(direction)
        self.direction = self.policy.name
        self._is_bullish = self.policy.is_bullish
        self.reactions = list(reactions)
        self.blue_lines = sorted(
            blue_lines,
            key=lambda item: (
                int(getattr(item, "reaction_number")),
                getattr(item, "source_time"),
                str(getattr(item, "kind")),
            ),
        )
        self.chronology = chronology
        self.candles = chronology.candles
        self.lower = chronology.raw_candles
        self.timeframe = chronology.timeframe
        self.candle_times = chronology.times
        self.lower_times = chronology.raw_times
        self.lower_index = chronology.lower_index
```

### FUN-A-003 — `AZoneDetector.extreme_name`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector.extreme_name`  
Source-Lines: 93-94  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def extreme_name(self) -> str:
        return self.policy.extreme_attr
```

### FUN-A-004 — `AZoneDetector._strict_cross`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._strict_cross`  
Source-Lines: 96-97  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _strict_cross(self, value: Decimal, level: Decimal) -> bool:
        return self.policy.strict_cross(value, level)
```

### FUN-A-005 — `AZoneDetector._better`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._better`  
Source-Lines: 99-100  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _better(self, value: Decimal, current: Decimal) -> bool:
        return self.policy.improves(value, current)
```

### FUN-A-006 — `AZoneDetector._main_index`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._main_index`  
Source-Lines: 102-103  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _main_index(self, timestamp: datetime) -> int:
        return self.chronology.main_index(timestamp)
```

### FUN-A-007 — `AZoneDetector._lower_window`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._lower_window`  
Source-Lines: 105-108  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _lower_window(
        self, start: datetime, end: datetime | None
    ) -> Sequence[object]:
        return self.chronology.lower_window(start, end)
```

### FUN-A-008 — `AZoneDetector._first_crossing`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._first_crossing`  
Source-Lines: 110-150  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_crossing(
        self,
        level: Decimal,
        start: datetime,
        end: datetime | None,
    ) -> tuple[int, datetime, Decimal] | None:
        left = bisect_left(self.lower_times, start)
        right = len(self.lower) if end is None else bisect_left(self.lower_times, end)
        if right > left and self.lower_index is not None:
            position = (
                self.lower_index.first_less(left, right, level)
                if self._is_bullish
                else self.lower_index.first_greater(left, right, level)
            )
            if position is None:
                return None
            item = self.lower[position]
            event_time = getattr(item, "timestamp")
            value = _decimal(getattr(item, self.extreme_name))
            return self._main_index(event_time), event_time, value

        lower_items = self.lower[left:right]
        for item in lower_items:
            value = _decimal(getattr(item, self.extreme_name))
            if self._strict_cross(value, level):
                event_time = getattr(item, "timestamp")
                return self._main_index(event_time), event_time, value
        if lower_items:
            return None

        start_index = max(0, bisect_left(self.candle_times, start))
        end_index = (
            len(self.candles)
            if end is None
            else max(start_index, bisect_left(self.candle_times, end))
        )
        for item in self.candles[start_index:end_index]:
            value = _decimal(getattr(item, self.extreme_name))
            if self._strict_cross(value, level):
                return int(getattr(item, "index")), getattr(item, "timestamp"), value
        return None
```

### FUN-A-009 — `AZoneDetector._range_extreme`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._range_extreme`  
Source-Lines: 152-184  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _range_extreme(
        self, start: datetime, end: datetime
    ) -> tuple[Decimal, int, datetime]:
        if end < start:
            raise ValueError("Extreme range end precedes its start.")
        lower_items = self._lower_window(start, end + timedelta(microseconds=1))
        if lower_items:
            source = lower_items[0]
            value = _decimal(getattr(source, self.extreme_name))
            for item in lower_items[1:]:
                candidate = _decimal(getattr(item, self.extreme_name))
                if self._better(candidate, value):
                    source = item
                    value = candidate
            source_index = self._main_index(getattr(source, "timestamp"))
            return (
                value,
                source_index,
                getattr(self.candles[source_index], "timestamp"),
            )
        start_index = max(0, bisect_right(self.candle_times, start) - 1)
        end_index = min(
            len(self.candles) - 1,
            max(start_index, bisect_right(self.candle_times, end) - 1),
        )
        source = self.candles[start_index]
        value = _decimal(getattr(source, self.extreme_name))
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = _decimal(getattr(item, self.extreme_name))
            if self._better(candidate, value):
                source = item
                value = candidate
        return value, int(getattr(source, "index")), getattr(source, "timestamp")
```

### FUN-A-010 — `AZoneDetector._formation`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._formation`  
Source-Lines: 186-201  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _formation(self, line: object) -> tuple[int, datetime, datetime]:
        reaction_number = int(getattr(line, "reaction_number"))
        if reaction_number < 1 or reaction_number > len(self.reactions):
            raise ValueError("Blue Line refers to a missing reaction.")
        if str(getattr(line, "kind")) == "scale":
            reaction = self.reactions[reaction_number - 1]
            index = int(getattr(reaction, "break_idx"))
            event_time = self._reaction_confirmation_time(reaction)
            stop_scan_time = event_time
        else:
            index = int(getattr(line, "source_index"))
            source_time = getattr(self.candles[index], "timestamp")
            event_time = self._reset_formation_time(line, index)
            stop_scan_time = source_time + self.timeframe
        candle = self.candles[index]
        return index, event_time, stop_scan_time
```

### FUN-A-011 — `AZoneDetector._reset_formation_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._reset_formation_time`  
Source-Lines: 203-213  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reset_formation_time(self, line: object, source_index: int) -> datetime:
        """Return the exact strict Reset event that makes a Reset Blue exist."""
        source = self.candles[source_index]
        start = getattr(source, "timestamp")
        end = start + self.timeframe
        broken_level = _decimal(getattr(line, "broken_level"))
        for item in self._lower_window(start, end):
            value = _decimal(getattr(item, self.extreme_name))
            if self._strict_cross(value, broken_level):
                return getattr(item, "timestamp")
        return start
```

### FUN-A-012 — `AZoneDetector._build_blue_states`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._build_blue_states`  
Source-Lines: 215-242  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _build_blue_states(self) -> list[BlueState]:
        states: list[BlueState] = []
        for ordinal, line in enumerate(self.blue_lines, start=1):
            if not bool(getattr(line, "calculation_valid", True)):
                continue
            formation_index, formation_time, stop_scan_time = self._formation(line)
            stop_level = _decimal(getattr(line, "source_extreme"))
            stop = self._first_crossing(
                stop_level,
                stop_scan_time,
                None,
            )
            states.append(
                BlueState(
                    ordinal=ordinal,
                    line=line,
                    formation_index=formation_index,
                    formation_time=formation_time,
                    stop_index=stop[0] if stop else None,
                    stop_time=(
                        getattr(self.candles[stop[0]], "timestamp") if stop else None
                    ),
                    stop_event_time=stop[1] if stop else None,
                    stop_level=stop_level,
                    stop_event_extreme=stop[2] if stop else None,
                )
            )
        return states
```

### FUN-A-013 — `AZoneDetector._double_stop_a_candidates`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._double_stop_a_candidates`  
Source-Lines: 244-304  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _double_stop_a_candidates(self) -> list[AZone]:
        result: list[AZone] = []
        previous: tuple[int, object] | None = None
        for ordinal, line in enumerate(self.blue_lines, start=1):
            if bool(getattr(line, "calculation_valid", True)):
                previous = (ordinal, line)
                continue
            if previous is None:
                continue
            previous_ordinal, previous_line = previous
            formation_index = int(getattr(line, "source_index"))
            formation_time = getattr(line, "source_time")
            source_time = getattr(self.candles[formation_index], "timestamp")
            crossing = self._first_crossing(
                _decimal(getattr(previous_line, "source_extreme")),
                formation_time,
                source_time + self.timeframe,
            )
            if crossing is None or crossing[0] != formation_index:
                continue
            trigger_index, trigger_event_time, _ = crossing
            match = self._first_reaction_after(
                trigger_event_time,
                not_before=formation_time,
            )
            if match is None:
                continue
            reaction_number, reaction = match
            first_index = int(getattr(reaction, "first_idx"))
            break_index = int(getattr(reaction, "break_idx"))
            source = self._a_source(trigger_index, reaction)
            if source is None:
                continue
            source_index, a_source_time, price = source
            result.append(
                AZone(
                    direction=self.direction,
                    blue_1_ordinal=previous_ordinal,
                    blue_2_ordinal=ordinal,
                    blue_1_source_time=getattr(previous_line, "source_time"),
                    blue_2_source_time=getattr(line, "source_time"),
                    blue_1_stop_time=source_time,
                    blue_2_stop_time=source_time,
                    blue_1_stop_level=_decimal(getattr(previous_line, "source_extreme")),
                    blue_2_stop_level=_decimal(getattr(line, "source_extreme")),
                    continuation_level=_decimal(getattr(previous_line, "source_extreme")),
                    continuation_source_index=int(getattr(previous_line, "source_index")),
                    continuation_source_time=getattr(previous_line, "source_time"),
                    trigger_index=trigger_index,
                    trigger_time=getattr(self.candles[trigger_index], "timestamp"),
                    trigger_event_time=trigger_event_time,
                    reaction_number=reaction_number,
                    reaction_first_time=getattr(self.candles[first_index], "timestamp"),
                    reaction_break_time=getattr(self.candles[break_index], "timestamp"),
                    source_index=source_index,
                    source_time=a_source_time,
                    price=price,
                )
            )
            previous = None
        return result
```

### FUN-A-014 — `AZoneDetector._pair_trigger`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._pair_trigger`  
Source-Lines: 306-464  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _pair_trigger(
        self,
        previous: BlueState,
        current: BlueState,
        expires_at: datetime | None,
    ) -> tuple[
        Decimal,
        int,
        datetime,
        int,
        datetime,
        datetime,
        datetime,
        datetime,
    ] | None:
        if previous.stop_event_time is None or previous.stop_time is None:
            return None
        if (
            expires_at is not None
            and previous.stop_event_time > expires_at
        ):
            return None

        # A following Blue Line inherits the stop level established by the
        # previous line's first aligned Reaction.  The level is the
        # directional extreme from the previous Blue candle through that
        # Reaction breakout, not the following line's own source extreme.
        inherited = self._inherited_stop(previous, current)
        if inherited is not None:
            level, level_index, level_time, reaction_break_time = inherited
            crossing = self._first_crossing(
                level,
                current.formation_time,
                expires_at,
            )
            if crossing is None:
                return None
            trigger_index, trigger_event_time, _ = crossing
            return (
                level,
                level_index,
                level_time,
                trigger_index,
                getattr(self.candles[trigger_index], "timestamp"),
                trigger_event_time,
                level_time,
                getattr(self.candles[trigger_index], "timestamp"),
            )

        if previous.stop_event_time < current.formation_time:
            current_source_time = getattr(
                self.candles[current.formation_index], "timestamp"
            )
            level, level_index, level_time = self._range_extreme(
                previous.stop_event_time,
                current_source_time - timedelta(microseconds=1),
            )
            formation_candle_end = (
                getattr(self.candles[current.formation_index], "timestamp")
                + self.timeframe
            )
            formation_window_end = (
                min(formation_candle_end, expires_at)
                if expires_at is not None
                else formation_candle_end
            )
            formation_crossing = self._first_crossing(
                level,
                current.formation_time,
                formation_window_end,
            )
            if formation_crossing is not None:
                trigger_index, trigger_event_time, _ = formation_crossing
                effective_stop_time = getattr(
                    self.candles[trigger_index], "timestamp"
                )
                return (
                    level,
                    level_index,
                    level_time,
                    trigger_index,
                    effective_stop_time,
                    trigger_event_time,
                    previous.stop_time,
                    effective_stop_time,
                )

            if current.stop_event_time is None or current.stop_time is None:
                return None
            if (
                expires_at is not None
                and current.stop_event_time > expires_at
            ):
                return None
            search_start = current.stop_event_time
            crossing = self._first_crossing(level, search_start, expires_at)
            if crossing is None:
                return None
            trigger_index, trigger_event_time, _ = crossing
            return (
                level,
                level_index,
                level_time,
                trigger_index,
                getattr(self.candles[trigger_index], "timestamp"),
                trigger_event_time,
                previous.stop_time,
                current.stop_time,
            )

        if current.stop_event_time is None or current.stop_time is None:
            return None
        if (
            expires_at is not None
            and current.stop_event_time > expires_at
        ):
            return None
        first, second = sorted(
            (previous, current),
            key=lambda item: (
                item.stop_event_time,
                -item.stop_level if self._is_bullish else item.stop_level,
            ),
        )
        assert first.stop_event_time is not None
        assert second.stop_event_time is not None
        assert first.stop_event_extreme is not None
        assert second.stop_event_extreme is not None
        first_index = int(first.stop_index)
        level = first.stop_event_extreme
        level_time = getattr(self.candles[first_index], "timestamp")

        if first.stop_event_time == second.stop_event_time:
            trigger_index = int(second.stop_index)
            return (
                level,
                first_index,
                level_time,
                trigger_index,
                getattr(self.candles[trigger_index], "timestamp"),
                second.stop_event_time,
                previous.stop_time,
                current.stop_time,
            )

        crossing = self._first_crossing(level, second.stop_event_time, expires_at)
        if crossing is None:
            return None
        trigger_index, trigger_event_time, _ = crossing
        return (
            level,
            first_index,
            level_time,
            trigger_index,
            getattr(self.candles[trigger_index], "timestamp"),
            trigger_event_time,
            previous.stop_time,
            current.stop_time,
        )
```

### FUN-A-015 — `AZoneDetector._reaction_confirmation_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._reaction_confirmation_time`  
Source-Lines: 466-469  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reaction_confirmation_time(self, reaction: object) -> datetime:
        return self.chronology.reaction_confirmation(
            self.direction, reaction, use_intrabar_start=False
        )
```

### FUN-A-016 — `AZoneDetector._first_reaction_after`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._first_reaction_after`  
Source-Lines: 471-487  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_reaction_after(
        self,
        trigger_event_time: datetime,
        *,
        not_before: datetime | None = None,
    ) -> tuple[int, object] | None:
        for number, reaction in enumerate(self.reactions, start=1):
            first_time = getattr(
                self.candles[int(getattr(reaction, "first_idx"))],
                "timestamp",
            )
            if (
                self._reaction_confirmation_time(reaction) >= trigger_event_time
                and (not_before is None or first_time >= not_before)
            ):
                return number, reaction
        return None
```

### FUN-A-017 — `AZoneDetector._inherited_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._inherited_stop`  
Source-Lines: 489-514  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _inherited_stop(
        self,
        previous: BlueState,
        current: BlueState,
    ) -> tuple[Decimal, int, datetime, datetime] | None:
        if previous.formation_time >= current.formation_time:
            return None
        for reaction in self.reactions:
            first_time = getattr(
                self.candles[int(getattr(reaction, "first_idx"))],
                "timestamp",
            )
            break_time = getattr(
                self.candles[int(getattr(reaction, "break_idx"))],
                "timestamp",
            )
            if first_time <= previous.formation_time:
                continue
            if break_time >= current.formation_time:
                continue
            level, level_index, level_time = self._range_extreme(
                previous.formation_time,
                break_time,
            )
            return level, level_index, level_time, break_time
        return None
```

### FUN-A-018 — `AZoneDetector._a_source`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._a_source`  
Source-Lines: 516-535  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _a_source(
        self,
        trigger_index: int,
        reaction: object,
    ) -> tuple[int, datetime, Decimal] | None:
        # The A candle is the directional extreme from the candle that stops
        # the required Blue Lines through the confirming Reaction breakout
        # candle, inclusive.
        end_index = int(getattr(reaction, "break_idx"))
        start_index = trigger_index
        if start_index > end_index:
            return None
        source = self.candles[start_index]
        value = _decimal(getattr(source, self.extreme_name))
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = _decimal(getattr(item, self.extreme_name))
            if self._better(candidate, value):
                source = item
                value = candidate
        return int(getattr(source, "index")), getattr(source, "timestamp"), value
```

### FUN-A-019 — `AZoneDetector._detect_ordinary_a`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._detect_ordinary_a`  
Source-Lines: 537-645  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _detect_ordinary_a(self, states: list[BlueState]) -> list[AZone]:
        """Resolve the ordinary adjacent-Blue A lifecycle."""
        output: list[AZone] = []
        cycle_after_index = -1
        bridge_reuse_ordinal: int | None = None
        index = 0

        while index + 1 < len(states):
            previous = states[index]
            current = states[index + 1]
            bridge_pair = (
                bridge_reuse_ordinal is not None
                and previous.ordinal == bridge_reuse_ordinal
            )
            if (
                current.formation_index <= cycle_after_index
                or (
                    previous.formation_index <= cycle_after_index
                    and not bridge_pair
                )
            ):
                if bridge_pair:
                    bridge_reuse_ordinal = None
                index += 1
                continue

            expires_at = (
                states[index + 2].formation_time
                if index + 2 < len(states)
                else None
            )
            trigger = self._pair_trigger(previous, current, expires_at)
            if trigger is None:
                index += 1
                continue

            (
                continuation_level,
                continuation_source_index,
                continuation_source_time,
                trigger_index,
                trigger_time,
                trigger_event_time,
                blue_1_stop_time,
                blue_2_stop_time,
            ) = trigger
            match = self._first_reaction_after(
                trigger_event_time,
                not_before=max(blue_1_stop_time, blue_2_stop_time),
            )
            if match is None:
                break
            reaction_number, reaction = match
            source = self._a_source(trigger_index, reaction)
            if source is None:
                index += 1
                continue
            source_index, source_time, price = source
            break_index = int(getattr(reaction, "break_idx"))
            output.append(
                AZone(
                    direction=self.direction,
                    blue_1_ordinal=previous.ordinal,
                    blue_2_ordinal=current.ordinal,
                    blue_1_source_time=getattr(previous.line, "source_time"),
                    blue_2_source_time=getattr(current.line, "source_time"),
                    blue_1_stop_time=blue_1_stop_time,
                    blue_2_stop_time=blue_2_stop_time,
                    blue_1_stop_level=previous.stop_level,
                    blue_2_stop_level=current.stop_level,
                    continuation_level=continuation_level,
                    continuation_source_index=continuation_source_index,
                    continuation_source_time=continuation_source_time,
                    trigger_index=trigger_index,
                    trigger_time=trigger_time,
                    trigger_event_time=trigger_event_time,
                    reaction_number=reaction_number,
                    reaction_first_time=getattr(
                        self.candles[int(getattr(reaction, "first_idx"))],
                        "timestamp",
                    ),
                    reaction_break_time=getattr(
                        self.candles[break_index], "timestamp"
                    ),
                    source_index=source_index,
                    source_time=source_time,
                    price=price,
                )
            )
            cycle_after_index = break_index

            confirmation_time = self._reaction_confirmation_time(reaction)
            first_stop = self._first_crossing(price, confirmation_time, None)
            allow_adjacent_reuse = (
                first_stop is not None
                and index + 2 < len(states)
                and states[index + 2].formation_time >= first_stop[1]
            )
            if allow_adjacent_reuse:
                bridge_reuse_ordinal = current.ordinal
                index += 1
            else:
                bridge_reuse_ordinal = None
                while (
                    index < len(states)
                    and states[index].formation_index <= cycle_after_index
                ):
                    index += 1
        return output
```

### FUN-A-020 — `AZoneDetector._filter_special_a`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._filter_special_a`  
Source-Lines: 647-709  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _filter_special_a(
        self,
        special: list[AZone],
        ordinary: list[AZone],
    ) -> tuple[list[AZone], list[AZone]]:
        """Resolve special double-stop A ownership against ordinary A state."""
        ordinary_reactions = {
            item.reaction_number
            for item in ordinary
            if item.reaction_number is not None
        }
        special = [
            item
            for item in special
            if item.reaction_number not in ordinary_reactions
        ]

        filtered_special: list[AZone] = []
        for item in special:
            prior_candidates = [
                prior
                for prior in ordinary
                if prior.source_time < item.source_time
            ]
            prior = max(
                prior_candidates,
                key=lambda zone: zone.source_time,
                default=None,
            )
            if prior is not None and self._a_was_stopped_before(
                prior,
                item.reaction_first_time,
                not_before=item.blue_1_source_time,
            ):
                continue
            filtered_special.append(item)
        special = filtered_special

        consumed_special = [
            (
                {
                    int(getattr(item, "blue_1_ordinal")),
                    int(getattr(item, "blue_2_ordinal")),
                },
                getattr(item, "trigger_event_time"),
            )
            for item in special
        ]
        if consumed_special:
            ordinary = [
                item
                for item in ordinary
                if not any(
                    getattr(item, "trigger_event_time") > trigger_event_time
                    and {
                        int(getattr(item, "blue_1_ordinal")),
                        int(getattr(item, "blue_2_ordinal")),
                    }
                    & consumed_ordinals
                    for consumed_ordinals, trigger_event_time in consumed_special
                )
            ]
        return ordinary, special
```

### FUN-A-021 — `AZoneDetector.detect`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector.detect`  
Source-Lines: 711-721  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect(self) -> list[AZone]:
        """Return ordinary and special A zones after one ownership resolution."""
        states = self._build_blue_states()
        ordinary = self._detect_ordinary_a(states)
        ordinary, special = self._filter_special_a(
            self._double_stop_a_candidates(), ordinary
        )
        return sorted(
            ordinary + special,
            key=lambda item: (item.source_time, item.trigger_event_time),
        )
```

### FUN-A-022 — `AZoneDetector._a_was_stopped_before`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:AZoneDetector._a_was_stopped_before`  
Source-Lines: 723-746  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _a_was_stopped_before(
        self,
        zone: AZone,
        end_time: datetime,
        *,
        not_before: datetime | None = None,
    ) -> bool:
        """Return whether A's *first* strict stop belongs to this lifecycle.

        A stop that happened before ``not_before`` completed the prior cycle.
        A later recross of the same price must not be mistaken for a new stop
        owned by the current Blue pair.
        """
        start = int(getattr(self.candles[zone.source_index], "index")) + 1
        if start >= len(self.candles):
            return False
        first_stop = self._first_crossing(
            zone.price,
            getattr(self.candles[start], "timestamp"),
            end_time,
        )
        if first_stop is None:
            return False
        return not_before is None or first_stop[1] >= not_before
```

### FUN-A-023 — `detect_a_zones`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `a_zone_detector.py:detect_a_zones`  
Source-Lines: 749-755  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect_a_zones(
    direction: str,
    reactions: Sequence[object],
    blue_lines: Sequence[object],
    chronology: object,
) -> list[AZone]:
    return AZoneDetector(direction, reactions, blue_lines, chronology).detect()
```

### FUN-BLU-001 — `_is_color`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:_is_color`  
Source-Lines: 48-49  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _is_color(candle: object, color: str) -> bool:
    return str(getattr(candle, "tag")).upper() == color
```

### FUN-BLU-002 — `_main_candle`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:_main_candle`  
Source-Lines: 52-56  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _main_candle(candles_by_index: dict[int, object], index: int) -> object:
    try:
        return candles_by_index[index]
    except KeyError as exc:
        raise ValueError(f"Missing main candle index {index}.") from exc
```

### FUN-BLU-003 — `_stops_on_index`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:_stops_on_index`  
Source-Lines: 59-72  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _stops_on_index(
    direction: str,
    line: object,
    candles: Sequence[object],
    start_index: int,
    end_index: int,
) -> bool:
    policy = get_direction_policy(direction)
    level = Decimal(getattr(line, "source_extreme"))
    for candle in candles[max(0, start_index) : end_index + 1]:
        extreme = Decimal(getattr(candle, policy.extreme_attr))
        if policy.strict_cross(extreme, level):
            return int(getattr(candle, "index")) == end_index
    return False
```

### FUN-BLU-004 — `fibonacci_level`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:fibonacci_level`  
Source-Lines: 75-81  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def fibonacci_level(direction: str, reaction: object, reference: Decimal) -> Decimal:
    policy = get_direction_policy(direction)
    if policy.is_bullish:
        top = Decimal(getattr(reaction, "box_top"))
        return top - FIBONACCI_RATIO * (top - reference)
    bottom = Decimal(getattr(reaction, "box_bottom"))
    return bottom + FIBONACCI_RATIO * (reference - bottom)
```

### FUN-BLU-005 — `_intrabar_pending_confirmation`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:_intrabar_pending_confirmation`  
Source-Lines: 84-132  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _intrabar_pending_confirmation(
    direction: str,
    chronology: object,
    reaction: object,
    comparison_extreme: Decimal,
    start_time: datetime,
    break_time: datetime,
    candles_by_index: dict[int, object],
) -> ScaleStrike | None:
    policy = get_direction_policy(direction)
    end_time = break_time + chronology.timeframe
    left, right = chronology.lower_bounds(start_time, end_time)
    relevant = chronology.raw_candles[left:right]
    if not relevant:
        return None

    break_level = Decimal(
        getattr(reaction, "box_top" if policy.is_bullish else "box_bottom")
    )
    eligible: list[object] = []
    for second in relevant:
        extreme = Decimal(getattr(second, policy.extreme_attr))
        penetrates = policy.strict_cross(extreme, comparison_extreme)
        if penetrates:
            eligible.append(second)
        breaks = (
            Decimal(getattr(second, "high")) > break_level
            if policy.is_bullish
            else Decimal(getattr(second, "low")) < break_level
        )
        if breaks and eligible:
            decisive = (
                min(eligible, key=lambda item: Decimal(getattr(item, "low")))
                if policy.is_bullish
                else max(eligible, key=lambda item: Decimal(getattr(item, "high")))
            )
            decisive_time = getattr(decisive, "timestamp")
            source_position = chronology.main_index(decisive_time)
            source = candles_by_index.get(source_position)
            if source is None:
                raise ValueError("Cannot map decisive native RAW candle to a main candle.")
            return ScaleStrike(
                source_index=int(getattr(source, "index")),
                source_time=getattr(source, "timestamp"),
                extreme=Decimal(
                    getattr(decisive, policy.extreme_attr)
                ),
            )
    return None
```

### FUN-BLU-006 — `count_scale_strikes`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:count_scale_strikes`  
Source-Lines: 135-193  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def count_scale_strikes(
    direction: str,
    reaction: object,
    chronology: object,
    reference: Decimal,
    candles_by_index: dict[int, object] | None = None,
) -> tuple[Decimal, list[ScaleStrike]]:
    """Return the exact 0.618 level and confirmed strikes for one reaction."""
    policy = get_direction_policy(direction)
    level = fibonacci_level(direction, reaction, reference)
    if candles_by_index is None:
        candles_by_index = {
            int(getattr(candle, "index")): candle for candle in chronology.candles
        }
    first_index = int(getattr(reaction, "first_idx"))
    break_index = int(getattr(reaction, "break_idx"))
    reaction_candles = [
        _main_candle(candles_by_index, index)
        for index in range(first_index, break_index + 1)
    ]
    confirming_color = policy.context_color
    strikes: list[ScaleStrike] = []
    pending: ScaleStrike | None = None

    for candle in reaction_candles:
        last_extreme = strikes[-1].extreme if strikes else level
        candle_extreme = Decimal(
            getattr(candle, policy.extreme_attr)
        )
        is_new = policy.improves(candle_extreme, last_extreme)
        if is_new and (
            pending is None
            or policy.improves(candle_extreme, pending.extreme)
        ):
            pending = ScaleStrike(
                source_index=int(getattr(candle, "index")),
                source_time=getattr(candle, "timestamp"),
                extreme=candle_extreme,
            )

        if pending is not None and _is_color(candle, confirming_color):
            strikes.append(pending)
            pending = None

    if pending is not None:
        break_candle = reaction_candles[-1]
        intrabar = _intrabar_pending_confirmation(
            direction=direction,
            chronology=chronology,
            reaction=reaction,
            comparison_extreme=strikes[-1].extreme if strikes else level,
            start_time=pending.source_time,
            break_time=getattr(break_candle, "timestamp"),
            candles_by_index=candles_by_index,
        )
        if intrabar is not None:
            strikes.append(intrabar)

    return level, strikes
```

### FUN-BLU-007 — `_build_scale_blue_line`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:_build_scale_blue_line`  
Source-Lines: 196-232  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _build_scale_blue_line(
    direction: str,
    reaction_number: int,
    previous_count: int,
    level: Decimal,
    strikes: Sequence[ScaleStrike],
    candles_by_index: dict[int, object],
    chronology: object,
    behavior_internal: bool,
) -> BlueLine:
    """Build one scale Blue from its decisive confirmed strike."""
    policy = get_direction_policy(direction)
    decisive = strikes[-1]
    source = _main_candle(candles_by_index, decisive.source_index)
    high = Decimal(getattr(source, "high"))
    low = Decimal(getattr(source, "low"))
    line_price = (
        low + (high - low) / Decimal(3)
        if policy.is_bullish
        else high - (high - low) / Decimal(3)
    )
    return BlueLine(
        direction=direction,
        kind="scale",
        reaction_number=reaction_number,
        previous_strike_count=previous_count,
        strike_count=len(strikes),
        fibonacci_level=level,
        source_index=decisive.source_index,
        source_time=decisive.source_time,
        source_extreme=decisive.extreme,
        broken_level=None,
        line_price=line_price,
        start_time=decisive.source_time - chronology.timeframe,
        end_time=decisive.source_time + chronology.timeframe,
        behavior_internal=behavior_internal,
    )
```

### FUN-BLU-008 — `_build_reset_blue_line`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:_build_reset_blue_line`  
Source-Lines: 235-288  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _build_reset_blue_line(
    direction: str,
    reaction_number: int,
    reset: object,
    previous_line: BlueLine | None,
    candles: Sequence[object],
    candles_by_index: dict[int, object],
    chronology: object,
    behavior_internal: bool,
) -> BlueLine:
    """Build one Reset Blue while preserving the established double-stop rule."""
    policy = get_direction_policy(direction)
    reset_index = int(getattr(reset, "index"))
    source = _main_candle(candles_by_index, reset_index)
    high = Decimal(getattr(source, "high"))
    low = Decimal(getattr(source, "low"))
    line_price = (
        low + (high - low) / Decimal(5)
        if policy.is_bullish
        else high - (high - low) / Decimal(5)
    )
    source_time = getattr(source, "timestamp")
    calculation_valid = not (
        previous_line is not None
        and _stops_on_index(
            direction,
            previous_line,
            candles,
            int(getattr(previous_line, "source_index")) + 1,
            reset_index,
        )
        and (
            low < Decimal(getattr(previous_line, "source_extreme"))
            if policy.is_bullish
            else high > Decimal(getattr(previous_line, "source_extreme"))
        )
    )
    return BlueLine(
        direction=direction,
        kind="reset",
        reaction_number=reaction_number,
        previous_strike_count=None,
        strike_count=None,
        fibonacci_level=None,
        source_index=reset_index,
        source_time=source_time,
        source_extreme=low if policy.is_bullish else high,
        broken_level=Decimal(getattr(reset, "broken_level")),
        line_price=line_price,
        start_time=source_time - chronology.timeframe,
        end_time=source_time + chronology.timeframe,
        calculation_valid=calculation_valid,
        behavior_internal=behavior_internal,
    )
```

### FUN-BLU-009 — `detect_blue_lines`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:detect_blue_lines`  
Source-Lines: 290-394  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect_blue_lines(
    direction: str,
    reactions: Sequence[object],
    chronology: object,
    resets: Sequence[object] = (),
) -> list[BlueLine]:
    """Detect scale and Reset Blue Lines over authoritative engine events."""
    policy = get_direction_policy(direction)
    candles = chronology.candles
    candles_by_index = {
        int(getattr(candle, "index")): candle for candle in candles
    }
    resets_by_first: dict[int, list[object]] = {}
    for reset in resets:
        resets_by_first.setdefault(
            int(getattr(reset, "from_first_idx")), []
        ).append(reset)

    output: list[BlueLine] = []
    previous_reaction: object | None = None
    previous_count: int | None = None
    has_blue_line = False
    healthy_reactions_since_blue = 0

    for reaction_number, reaction in enumerate(reactions, start=1):
        behavior_internal = bool(getattr(reaction, "behavior_internal", False))
        if str(getattr(reaction, "mode")) == "A":
            boundary = getattr(reaction, "anchor_value", None)
            if boundary is None:
                boundary = getattr(reaction, "leg_boundary_value", None)
            if boundary is None:
                raise ValueError(
                    "Leg-Start reaction is missing its leg-head boundary."
                )
            reference = Decimal(boundary)
            previous_count = None
        else:
            if previous_reaction is None:
                raise ValueError(
                    "A Normal reaction cannot precede the Leg-Start reaction."
                )
            reference = Decimal(
                getattr(
                    previous_reaction,
                    "box_bottom" if policy.is_bullish else "box_top",
                )
            )

        level, strikes = count_scale_strikes(
            direction,
            reaction,
            chronology,
            reference,
            candles_by_index,
        )
        scale_candidate = (
            previous_count is not None and len(strikes) > previous_count
        )
        scale_emitted = False
        if scale_candidate and (
            not has_blue_line or healthy_reactions_since_blue >= 1
        ):
            output.append(
                _build_scale_blue_line(
                    direction,
                    reaction_number,
                    previous_count,
                    level,
                    strikes,
                    candles_by_index,
                    chronology,
                    behavior_internal,
                )
            )
            has_blue_line = True
            healthy_reactions_since_blue = 0
            scale_emitted = True

        if has_blue_line and not scale_emitted:
            healthy_reactions_since_blue += 1

        for reset in resets_by_first.get(
            int(getattr(reaction, "first_idx")), []
        ):
            if has_blue_line and healthy_reactions_since_blue < 1:
                continue
            output.append(
                _build_reset_blue_line(
                    direction,
                    reaction_number,
                    reset,
                    output[-1] if output else None,
                    candles,
                    candles_by_index,
                    chronology,
                    behavior_internal,
                )
            )
            has_blue_line = True
            healthy_reactions_since_blue = 0

        previous_reaction = reaction
        previous_count = len(strikes)

    return output
```

### FUN-BLU-010 — `public_blue_lines`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:public_blue_lines`  
Source-Lines: 397-404  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def public_blue_lines(lines: Sequence[BlueLine]) -> list[BlueLine]:
    """Return only calculation-valid, public Blue Lines for serialization."""
    return [
        line
        for line in lines
        if bool(getattr(line, "calculation_valid", True))
        and not bool(getattr(line, "behavior_internal", False))
    ]
```

### FUN-BLU-011 — `mark_internal_blue_lines`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `blue_line_detector.py:mark_internal_blue_lines`  
Source-Lines: 406-448  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def mark_internal_blue_lines(
    lines: Sequence[BlueLine],
    owner_reactions: Sequence[object],
    all_behavior_reactions: Sequence[object],
) -> None:
    """Mark Blue Lines that are private to protected Reaction interiors.

    A Blue is internal when its owning Reaction is behavior-internal, or when
    both its calculation-owned ``source_extreme`` and rendered ``line_price``
    fall strictly inside the same healthy Reaction interior.  The drawing
    offset alone never changes ownership.
    """

    def owner_is_internal(line: BlueLine) -> bool:
        number = int(getattr(line, "reaction_number", 0) or 0)
        if number < 1 or number > len(owner_reactions):
            return False
        return bool(getattr(owner_reactions[number - 1], "behavior_internal", False))

    def geometry_is_internal(line: BlueLine) -> bool:
        source_time = getattr(line, "source_time", None)
        line_price = getattr(line, "line_price", None)
        source_extreme = getattr(line, "source_extreme", None)
        if source_time is None or line_price is None or source_extreme is None:
            return False
        rendered = Decimal(str(line_price))
        semantic = Decimal(str(source_extreme))
        for reaction in all_behavior_reactions:
            first = getattr(reaction, "behavior_first_time", None)
            confirmed = getattr(reaction, "behavior_confirmation_time", None)
            if first is None or confirmed is None:
                continue
            if source_time <= first or source_time > confirmed:
                continue
            bottom = Decimal(str(getattr(reaction, "behavior_public_box_bottom")))
            top = Decimal(str(getattr(reaction, "behavior_public_box_top")))
            if bottom < semantic < top and bottom < rendered < top:
                return True
        return False

    for line in lines:
        if owner_is_internal(line) or geometry_is_internal(line):
            object.__setattr__(line, "behavior_internal", True)
```

### FUN-DIR-001 — `DirectionPolicy.strict_cross`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `direction_policy.py:DirectionPolicy.strict_cross`  
Source-Lines: 22-24  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def strict_cross(self, value: Decimal, level: Decimal) -> bool:
        """Return True only for a strict directional cross; equality is never a cross."""
        return value < level if self.is_bullish else value > level
```

### FUN-DIR-002 — `DirectionPolicy.improves`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `direction_policy.py:DirectionPolicy.improves`  
Source-Lines: 26-28  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def improves(self, value: Decimal, current: Decimal) -> bool:
        """Return True when *value* extends the directional extreme."""
        return value < current if self.is_bullish else value > current
```

### FUN-DIR-003 — `get_direction_policy`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `direction_policy.py:get_direction_policy`  
Source-Lines: 52-58  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def get_direction_policy(direction: str) -> DirectionPolicy:
    """Return the immutable directional contract used by all calculation engines."""
    if direction == "bullish":
        return _BULLISH
    if direction == "bearish":
        return _BEARISH
    raise ValueError("Direction must be 'bullish' or 'bearish'.")
```

### FUN-E-001 — `_decimal`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:_decimal`  
Source-Lines: 71-72  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _decimal(value: object) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))
```

### FUN-E-002 — `EZoneDetector.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector.__init__`  
Source-Lines: 76-192  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(
        self,
        direction: str,
        trend_reactions: Sequence[object],
        opposite_reactions: Sequence[object],
        s_zones: Sequence[object],
        trend_resets: Sequence[object],
        opposite_resets: Sequence[object],
        chronology: object,
        start_index: int = 0,
        end_index: int | None = None,
        geometry_finder: Callable[[str, int, int], object | None] | None = None,
        direct_geometry_finder: Callable[
            [str, int, int, datetime], object | None
        ] | None = None,
        blocked_order_first_times: set[datetime] | None = None,
        initial_order_audit: dict[tuple[int, int], dict[str, object]] | None = None,
        reset_geometry_finder: Callable[
            [str, int, int, int], object | None
        ] | None = None,
        sequence_resets: dict[datetime, int] | None = None,
        sequence_priority: Callable[[str, str], int] | None = None,
    ) -> None:
        self.policy = get_direction_policy(direction)
        self.direction = self.policy.name
        self._is_bullish = self.policy.is_bullish
        self._stop_value_name = self.policy.extreme_attr
        if sequence_priority is None:
            raise ValueError("EZoneDetector requires the shared sequence-priority resolver.")
        self.sequence_priority = sequence_priority
        self.sequence_resets = dict(sequence_resets or {})
        self.order_direction = chronology.opposite_direction(direction)
        self.chronology = chronology
        self.trend_reactions = list(trend_reactions)
        self.opposite_reactions = list(opposite_reactions)
        self.s_zones = sorted(
            s_zones,
            key=lambda item: (
                getattr(item, "source_time"),
                int(getattr(item, "source_index")),
            ),
        )
        self.opposite_resets = sorted(opposite_resets, key=self._reset_time)
        self.candles = chronology.candles
        self.lower = chronology.raw_candles
        self.lower_times = chronology.raw_times
        self.lower_index = chronology.lower_index
        self.timeframe = chronology.timeframe
        self.times = chronology.times
        self.start_index = int(start_index)
        self.end_index = len(self.candles) - 1 if end_index is None else int(end_index)
        self.range_start = self.times[self.start_index]
        self.range_end = self.times[self.end_index] + self.timeframe
        self.geometry_finder = geometry_finder
        self.direct_geometry_finder = direct_geometry_finder or geometry_finder
        self.reset_geometry_finder = reset_geometry_finder
        self.blocked_order_first_times = blocked_order_first_times or set()
        self.initial_order_audit = initial_order_audit or {}
        self._geometry_evidence_cache: dict[tuple[datetime, datetime], bool] = {}
        self._order_b_geometry_cache: dict[
            tuple[datetime, datetime, datetime],
            tuple[int, object, datetime] | None,
        ] = {}
        self._next_outer_reset_cache: dict[int, datetime | None] = {}
        self._cross_order_cache: dict[
            tuple[datetime, Decimal], tuple[int, datetime, datetime] | None
        ] = {}
        self._trigger_cross_cache: dict[tuple[datetime, Decimal], datetime | None] = {}
        self._reset_leg_geometry_cache: dict[
            tuple[int, datetime], tuple[datetime, Decimal] | None
        ] = {}
        self._order_candidates_cache: dict[
            tuple[datetime, datetime | None, bool], tuple[OrderMatch, ...]
        ] = {}
        self.order_audit: dict[tuple[int, int], dict[str, object]] = {}
        self._synthetic_order_cache: list[
            tuple[int, object, datetime, datetime, datetime]
        ] | None = None
        self._audit_synthetic_order_cache: list[
            tuple[int, object, datetime, datetime, datetime]
        ] | None = None
        self._trend_first_times = [
            self._reaction_first_time(item) for item in self.trend_reactions
        ]
        self._trend_confirmations = [
            self._confirmation_for(item, self.direction)
            for item in self.trend_reactions
        ]
        self._opposite_first_times = [
            self._reaction_first_time(item) for item in self.opposite_reactions
        ]
        self._opposite_confirmations = [
            self._confirmation(item) for item in self.opposite_reactions
        ]
        self._trend_by_confirmation = sorted(
            zip(
                self._trend_confirmations,
                self._trend_first_times,
                self.trend_reactions,
            ),
            key=lambda item: item[0],
        )
        self._trend_confirmation_times = [item[0] for item in self._trend_by_confirmation]
        self._opposite_reset_times_by_first: dict[int, list[datetime]] = {}
        for reset in self.opposite_resets:
            self._opposite_reset_times_by_first.setdefault(
                int(getattr(reset, "from_first_idx")), []
            ).append(self._reset_time(reset))
        self._opposite_reset_events = [
            (self._reset_time(item), item) for item in self.opposite_resets
        ]
        self._opposite_reset_times = [item[0] for item in self._opposite_reset_events]
        self._opposite_by_first_index = {
            int(getattr(item, "first_idx")): item
            for item in self.opposite_reactions
        }
        self.visual_lifecycle_starts: set[datetime] = set()
```

### FUN-E-003 — `EZoneDetector._reset_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._reset_time`  
Source-Lines: 194-195  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reset_time(self, reset: object) -> datetime:
        return self.chronology.reset_time(reset)
```

### FUN-E-004 — `EZoneDetector._main_index`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._main_index`  
Source-Lines: 197-198  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _main_index(self, value: datetime) -> int:
        return self.chronology.main_index(value, clamp=True)
```

### FUN-E-005 — `EZoneDetector._first_cross_position`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._first_cross_position`  
Source-Lines: 201-216  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_cross_position(
        self, left: int, right: int, level: Decimal, *, less: bool
    ) -> int | None:
        """Return the first strict lower-timeframe crossing in [left, right)."""
        if self.lower_index is not None:
            return (
                self.lower_index.first_less(left, right, level)
                if less
                else self.lower_index.first_greater(left, right, level)
            )
        field = "low" if less else "high"
        for position in range(left, right):
            value = _decimal(getattr(self.lower[position], field))
            if value < level if less else value > level:
                return position
        return None
```

### FUN-E-006 — `EZoneDetector._stop_value`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._stop_value`  
Source-Lines: 218-219  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _stop_value(self, item: object) -> Decimal:
        return _decimal(getattr(item, self._stop_value_name))
```

### FUN-E-007 — `EZoneDetector._first_parent_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._first_parent_stop`  
Source-Lines: 222-233  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_parent_stop(
        self, source_time: datetime, level: Decimal
    ) -> tuple[int, datetime] | None:
        left = bisect_left(self.lower_times, max(source_time, self.range_start))
        right = bisect_left(self.lower_times, self.range_end)
        position = self._first_cross_position(
            left, right, level, less=self._is_bullish
        )
        if position is None:
            return None
        event = self.lower_times[position]
        return self._main_index(event), event
```

### FUN-E-008 — `EZoneDetector._confirmation_for`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._confirmation_for`  
Source-Lines: 235-236  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _confirmation_for(self, reaction: object, direction: str) -> datetime:
        return self.chronology.reaction_confirmation(direction, reaction)
```

### FUN-E-009 — `EZoneDetector._confirmation`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._confirmation`  
Source-Lines: 238-239  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _confirmation(self, reaction: object) -> datetime:
        return self._confirmation_for(reaction, self.order_direction)
```

### FUN-E-010 — `EZoneDetector._reaction_first_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._reaction_first_time`  
Source-Lines: 241-242  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reaction_first_time(self, reaction: object) -> datetime:
        return getattr(self.candles[int(getattr(reaction, "first_idx"))], "timestamp")
```

### FUN-E-011 — `EZoneDetector._strict_trigger_cross`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._strict_trigger_cross`  
Source-Lines: 244-256  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _strict_trigger_cross(self, start: datetime, level: Decimal) -> datetime | None:
        cache_key = (start, level)
        cached = self._trigger_cross_cache.get(cache_key)
        if cached is not None:
            return cached
        left = bisect_left(self.lower_times, start)
        right = bisect_left(self.lower_times, self.range_end)
        position = self._first_cross_position(
            left, right, level, less=self._is_bullish
        )
        result = None if position is None else self.lower_times[position]
        self._trigger_cross_cache[cache_key] = result
        return result
```

### FUN-E-012 — `EZoneDetector._reset_leg_geometry`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._reset_leg_geometry`  
Source-Lines: 258-285  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reset_leg_geometry(
        self, reset: object, reset_time: datetime,
    ) -> tuple[datetime, Decimal] | None:
        """Return the inclusive Break-to-Reset leg start and outer boundary."""
        cache_key = (int(getattr(reset, "from_first_idx")), reset_time)
        cached = self._reset_leg_geometry_cache.get(cache_key)
        if cached is not None:
            return cached
        owner = self._opposite_by_first_index.get(
            int(getattr(reset, "from_first_idx"))
        )
        if owner is None:
            self._reset_leg_geometry_cache[cache_key] = None
            return None
        start_index = int(getattr(owner, "break_idx"))
        end_index = self._main_index(reset_time)
        if end_index < start_index:
            self._reset_leg_geometry_cache[cache_key] = None
            return None
        boundary = self._stop_value(self.candles[start_index])
        for candle in self.candles[start_index + 1 : end_index + 1]:
            value = self._stop_value(candle)
            better = self.policy.improves(value, boundary)
            if better:
                boundary = value
        result = self.times[start_index], boundary
        self._reset_leg_geometry_cache[cache_key] = result
        return result
```

### FUN-E-013 — `EZoneDetector._reset_leg_has_simple_trend_reaction`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._reset_leg_has_simple_trend_reaction`  
Source-Lines: 287-301  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reset_leg_has_simple_trend_reaction(
        self, leg_start: datetime, boundary_cross: datetime,
    ) -> bool:
        key = (leg_start, boundary_cross)
        cached = self._geometry_evidence_cache.get(key)
        if cached is not None:
            return cached
        left = bisect_left(self._trend_confirmation_times, leg_start)
        right = bisect_right(self._trend_confirmation_times, boundary_cross)
        result = any(
            not bool(getattr(self._trend_by_confirmation[position][2], "behavior_internal", False))
            for position in range(left, right)
        )
        self._geometry_evidence_cache[key] = result
        return result
```

### FUN-E-014 — `EZoneDetector._first_order_b_geometry`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._first_order_b_geometry`  
Source-Lines: 303-437  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_order_b_geometry(
        self, reset_time: datetime, boundary_cross: datetime, deadline: datetime,
    ) -> tuple[int, object, datetime] | None:
        """Return the first structurally owned Order_B geometry after its gate."""
        cache_key = (reset_time, boundary_cross, deadline)
        if cache_key in self._order_b_geometry_cache:
            return self._order_b_geometry_cache[cache_key]
        end_index = min(self.end_index, bisect_left(self.times, deadline) - 1)
        if self.geometry_finder is None:
            self._order_b_geometry_cache[cache_key] = None
            return None

        def find_geometry(gate_index: int) -> object | None:
            if gate_index > end_index:
                return None
            if self.reset_geometry_finder is not None:
                reset_index = self._main_index(reset_time)
                gate_time = self.times[gate_index]
                gate_owner = self._opposite_by_first_index.get(gate_index)
                # A non-canonical First that is already open in the main
                # candle containing the lower-timeframe gate belongs to the
                # pre-gate leg.  Canonical ownership may start on that candle;
                # otherwise the bounded Reset search begins on the next one.
                reset_gate_index = (
                    gate_index
                    if gate_owner is not None
                    and self._reaction_first_time(gate_owner) == gate_time
                    else gate_index + 1
                )
                return self.reset_geometry_finder(
                    self.order_direction,
                    reset_index,
                    reset_gate_index,
                    end_index,
                )
            assert self.geometry_finder is not None
            return self.geometry_finder(
                self.order_direction, gate_index, end_index
            )

        gate_event = boundary_cross
        while gate_event < deadline:
            gate_index = self._main_index(gate_event)
            geometry = find_geometry(gate_index)
            if geometry is None:
                break
            gate_time = self.times[gate_index]
            if self._reaction_first_time(geometry) == gate_time:
                matching = self._opposite_by_first_index.get(
                    int(getattr(geometry, "first_idx"))
                )
                if (
                    matching is None
                    or int(getattr(matching, "break_idx"))
                    != int(getattr(geometry, "break_idx"))
                ):
                    geometry = find_geometry(gate_index + 1)
                    if geometry is None:
                        break
            confirmation = self._confirmation_for(
                geometry, self.order_direction
            )
            if confirmation >= deadline:
                break

            geometry_first = self._reaction_first_time(geometry)
            if geometry_first in self.blocked_order_first_times:
                # The leg context may keep an internal head alive after the
                # Reset boundary has crossed. Geometry whose First opens in
                # that closed interval cannot own the resumed outer E space.
                next_index = max(
                    gate_index, int(getattr(geometry, "first_idx"))
                ) + 1
                if next_index > end_index:
                    break
                gate_event = self.times[next_index]
                continue
            owner_position = bisect_right(
                self._opposite_first_times, geometry_first
            ) - 1
            owner = (
                self.opposite_reactions[owner_position]
                if owner_position >= 0 else None
            )
            if owner is not None:
                owner_first = self._reaction_first_time(owner)
                owner_resets = self._opposite_reset_times_by_first.get(
                    int(getattr(owner, "first_idx")), []
                )
                owner_reset = next(
                    (value for value in owner_resets if value > geometry_first),
                    None,
                )
                owner_already_reset = any(
                    value <= geometry_first for value in owner_resets
                )
                # Opposite-Reaction ownership is directionally independent.
                # A trend-side Reset cannot release or invalidate this owner;
                # only a Reset belonging to that owner can do so.
                active_owner = not owner_already_reset
                if active_owner:
                    owner_confirmation = self._confirmation(owner)
                    if owner_first >= gate_time:
                        if owner_confirmation >= deadline:
                            break
                        result = owner_position + 1, owner, owner_confirmation
                        self._order_b_geometry_cache[cache_key] = result
                        return result
                    if owner_reset is None or owner_reset >= deadline:
                        break
                    gate_event = owner_reset
                    continue

            existing = self._opposite_by_first_index.get(
                int(getattr(geometry, "first_idx"))
            )
            if (
                existing is not None
                and int(getattr(existing, "break_idx"))
                == int(getattr(geometry, "break_idx"))
            ):
                result = owner_position + 1, existing, confirmation
                self._order_b_geometry_cache[cache_key] = result
                return result

            # Reset-leg local geometry is only a search aid; without an exact
            # published Reaction identity it cannot create an Order.
            next_index = int(getattr(geometry, "first_idx")) + 1
            if next_index > end_index:
                break
            gate_event = self.times[next_index]
            continue

        self._order_b_geometry_cache[cache_key] = None
        return None
```

### FUN-E-015 — `EZoneDetector._next_outer_reset_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._next_outer_reset_time`  
Source-Lines: 439-458  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _next_outer_reset_time(
        self, reset_position: int, fallback: datetime,
    ) -> datetime:
        """Return the next non-nested Reset boundary.

        A reaction that starts after the current Reset belongs to a nested leg
        and cannot close the outer ResetLeg owner.
        """
        if reset_position in self._next_outer_reset_cache:
            cached = self._next_outer_reset_cache[reset_position]
            return fallback if cached is None else cached
        reset_time, _ = self._opposite_reset_events[reset_position]
        result = None
        for next_time, next_reset in self._opposite_reset_events[reset_position + 1:]:
            owner_first = self.times[int(getattr(next_reset, "from_first_idx"))]
            if owner_first <= reset_time:
                result = next_time
                break
        self._next_outer_reset_cache[reset_position] = result
        return fallback if result is None else result
```

### FUN-E-016 — `EZoneDetector._replacement_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._replacement_order`  
Source-Lines: 461-509  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _replacement_order(
        self,
        owner: object,
        owner_confirmation: datetime,
        owner_stop_event: datetime,
    ) -> tuple[int, object, datetime, datetime] | None:
        """Find the first order created by a complete behavioral-reset cycle."""
        reset_left = bisect_right(self._opposite_reset_times, owner_confirmation)
        reset_right = bisect_left(self._opposite_reset_times, owner_stop_event)
        reset_events = self._opposite_reset_events[reset_left:reset_right]
        owner_first_index = int(getattr(owner, "first_idx"))
        for position, (reset_time, reset) in enumerate(reset_events):
            reset_owner_index = int(getattr(reset, "from_first_idx"))
            reset_owner_first = self.times[reset_owner_index]
            if (
                reset_owner_index != owner_first_index
                and reset_owner_first < owner_confirmation
            ):
                continue
            # A Reset of the provisional order, or of a later opposite
            # reaction in its still-open lifecycle, can originate the
            # replacement leg. Stale reactions from before that lifecycle
            # cannot take ownership.
            absolute_position = bisect_left(self._opposite_reset_times, reset_time)
            next_opposite_reset = self._next_outer_reset_time(
                absolute_position, owner_stop_event
            )
            leg = self._reset_leg_geometry(reset, reset_time)
            if leg is None:
                continue
            leg_start, trigger = leg
            crossing = self._strict_trigger_cross(reset_time, trigger)
            if crossing is None or crossing >= min(next_opposite_reset, owner_stop_event):
                continue
            if not self._reset_leg_has_simple_trend_reaction(leg_start, crossing):
                continue
            gate_time = self.times[self._main_index(crossing)]
            order_start = bisect_left(self._opposite_first_times, gate_time)
            for order_position in range(order_start, len(self.opposite_reactions)):
                reaction = self.opposite_reactions[order_position]
                first = self._opposite_first_times[order_position]
                confirmation = self._opposite_confirmations[order_position]
                if (
                    first >= gate_time
                    and confirmation >= crossing
                    and confirmation < owner_stop_event
                ):
                    return order_position + 1, reaction, confirmation, reset_time
        return None
```

### FUN-E-017 — `EZoneDetector._reset_leg_evidence`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._reset_leg_evidence`  
Source-Lines: 511-551  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reset_leg_evidence(
        self, reaction: object, context_start: datetime
    ) -> tuple[datetime, datetime] | None:
        """Return the Reset and strict-break events that created ``reaction``."""
        order_first = self._reaction_first_time(reaction)
        order_confirmation = self._confirmation(reaction)
        # Mode-B ownership starts with the current E-space lifecycle. A Reset
        # that occurred before the parent stop belongs to an older lifecycle
        # and cannot create an order for this parent.
        reset_left = bisect_left(self._opposite_reset_times, context_start)
        reset_right = bisect_right(
            self._opposite_reset_times, order_confirmation
        )
        reaction_first_index = int(getattr(reaction, "first_idx"))
        for reset_position in range(reset_left, reset_right):
            reset_time, reset = self._opposite_reset_events[reset_position]
            next_reset = self._next_outer_reset_time(
                reset_position, self.range_end
            )
            if order_confirmation >= next_reset:
                continue
            leg = self._reset_leg_geometry(reset, reset_time)
            if leg is None:
                continue
            leg_start, boundary = leg
            crossing = self._strict_trigger_cross(reset_time, boundary)
            if crossing is None or crossing > order_confirmation:
                continue
            if not self._reset_leg_has_simple_trend_reaction(leg_start, crossing):
                continue
            first_after_crossing = self._first_order_b_geometry(
                reset_time, crossing, next_reset
            )
            if (
                order_confirmation >= crossing
                and first_after_crossing is not None
                and int(getattr(first_after_crossing[1], "first_idx"))
                == reaction_first_index
            ):
                return reset_time, crossing
        return None
```

### FUN-E-018 — `EZoneDetector._legacy_reset_leg_evidence`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._legacy_reset_leg_evidence`  
Source-Lines: 554-592  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _legacy_reset_leg_evidence(
        self, reaction: object, context_start: datetime,
    ) -> tuple[datetime, datetime] | None:
        """Return the established audit cause without changing E eligibility."""
        order_first = self._reaction_first_time(reaction)
        order_confirmation = self._confirmation(reaction)
        reset_left = bisect_left(self._opposite_reset_times, context_start)
        reset_right = bisect_right(self._opposite_reset_times, order_confirmation)
        reaction_first_index = int(getattr(reaction, "first_idx"))
        for reset_position in range(reset_left, reset_right):
            reset_time, reset = self._opposite_reset_events[reset_position]
            next_reset = self._next_outer_reset_time(reset_position, self.range_end)
            if order_confirmation >= next_reset:
                continue
            leg = self._reset_leg_geometry(reset, reset_time)
            if leg is None:
                continue
            leg_start, boundary = leg
            crossing = self._strict_trigger_cross(reset_time, boundary)
            if crossing is None or crossing > order_confirmation:
                continue
            # Audit and calculation use the same Reset-leg evidence contract.
            # A behavior-internal trend Reaction cannot unlock Order_B merely
            # because local geometry can rediscover it.
            aligned = self._reset_leg_has_simple_trend_reaction(
                leg_start, crossing
            )
            if not aligned:
                continue
            gate_time = self.times[self._main_index(crossing)]
            first_after = bisect_left(self._opposite_first_times, gate_time)
            if (
                order_first >= gate_time
                and first_after < len(self.opposite_reactions)
                and int(getattr(self.opposite_reactions[first_after], "first_idx"))
                == reaction_first_index
            ):
                return reset_time, crossing
        return None
```

### FUN-E-019 — `EZoneDetector._order_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._order_stop`  
Source-Lines: 595-605  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _order_stop(
        self, number: int, reaction: object, context_start: datetime | None = None,
    ) -> tuple[Decimal, int, datetime]:
        del context_start  # Provenance never manufactures a context-only stop.
        return self.chronology.canonical_order_stop(
            self.order_direction,
            number,
            reaction,
            self.opposite_reactions,
            start_index=self.start_index,
        )
```

### FUN-E-020 — `EZoneDetector.order_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector.order_stop`  
Source-Lines: 607-611  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def order_stop(
        self, reaction_number: int, reaction: object
    ) -> tuple[Decimal, int, datetime]:
        """Public audit API for canonical Order stop provenance."""
        return self._order_stop(reaction_number, reaction)
```

### FUN-E-021 — `EZoneDetector._first_healthy_direct_geometry`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._first_healthy_direct_geometry`  
Source-Lines: 614-697  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_healthy_direct_geometry(
        self, start: datetime, allow_bounded_continue: bool = False,
    ) -> tuple[int, object, datetime] | None:
        """Return the first healthy geometry after an A/S/E strict stop.

        A candidate completes normally when the active prior reaction is not
        Reset before its confirmation. If that prior reaction is Reset first,
        the search restarts strictly after the Reset candle and the first
        complete geometry owns the new leg.
        """
        if self.direct_geometry_finder is None:
            return None
        # Geometry needs its complete context candle at or after the exact
        # stop event. A First candle that already opened before the lower-time-
        # frame stop cannot be attributed to that stop.
        search_index = self._main_index(start)
        search_event = start
        restarted = False
        while search_index <= self.end_index:
            candidate = self.direct_geometry_finder(
                self.order_direction, search_index, self.end_index, search_event
            )
            if candidate is None:
                return None
            first = self._reaction_first_time(candidate)
            if (
                first in self.blocked_order_first_times
                and first == self.times[self._main_index(start)]
            ):
                search_index = int(getattr(candidate, "first_idx")) + 1
                search_event = first
                continue
            confirmation = self._confirmation_for(
                candidate, self.order_direction
            )
            owner_position = bisect_right(
                self._opposite_confirmations, search_event
            ) - 1
            prior = (
                self.opposite_reactions[owner_position]
                if owner_position >= 0 else None
            )
            reset_before_confirmation = None
            if prior is not None:
                for reset_time in self._opposite_reset_times_by_first.get(
                    int(getattr(prior, "first_idx")), []
                ):
                    if search_event < reset_time <= confirmation:
                        reset_before_confirmation = reset_time
                        break
            if reset_before_confirmation is not None:
                search_index = self._main_index(reset_before_confirmation)
                search_event = reset_before_confirmation
                restarted = True
                continue

            identity = (
                int(getattr(candidate, "first_idx")),
                int(getattr(candidate, "break_idx")),
            )
            canonical_position = next((
                pos for pos, item in enumerate(self.opposite_reactions)
                if (
                    int(getattr(item, "first_idx")),
                    int(getattr(item, "break_idx")),
                ) == identity
            ), None)
            if canonical_position is None:
                # Only the S->E parent-stop path may admit a noncanonical
                # bounded Reaction, and only when exact gate chronology proves
                # continuation of the already-open post-Reset leg.
                if (
                    allow_bounded_continue
                    and getattr(candidate, "order_gate_decision", None) == "continue"
                ):
                    return 0, candidate, confirmation
                search_index = int(getattr(candidate, "first_idx")) + 1
                search_event = first
                continue
            candidate = self.opposite_reactions[canonical_position]
            number = canonical_position + 1
            confirmation = self._opposite_confirmations[canonical_position]
            return number, candidate, confirmation
        return None
```

### FUN-E-022 — `EZoneDetector._synthetic_reset_leg_orders`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._synthetic_reset_leg_orders`  
Source-Lines: 699-788  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _synthetic_reset_leg_orders(
        self, start: datetime, audit_legacy: bool
    ) -> list[tuple[int, object, datetime, datetime, datetime]]:
        """Return Reset-leg orders discovered from bounded post-Reset geometry."""
        selected_cache = (
            self._audit_synthetic_order_cache
            if audit_legacy
            else self._synthetic_order_cache
        )
        if selected_cache is not None:
            return [item for item in selected_cache if item[3] >= start]
        if self.geometry_finder is None:
            return []

        all_synthetic: list[
            tuple[int, object, datetime, datetime, datetime]
        ] = []
        for reset_position, (reset_time, reset) in enumerate(
            self._opposite_reset_events
        ):
            reset_owner = self._opposite_by_first_index.get(
                int(getattr(reset, "from_first_idx"))
            )
            if reset_owner is None:
                continue
            leg = self._reset_leg_geometry(reset, reset_time)
            if leg is None:
                continue
            leg_start, boundary = leg
            crossing = self._strict_trigger_cross(reset_time, boundary)
            if crossing is None:
                continue
            next_reset = self._next_outer_reset_time(
                reset_position, self.range_end
            )
            if crossing >= next_reset:
                continue

            if audit_legacy:
                if self.geometry_finder(
                    self.direction,
                    bisect_left(self.times, leg_start),
                    self._main_index(crossing),
                ) is None:
                    continue
                first_index = self._main_index(crossing)
                end_index = min(
                    self.end_index,
                    max(first_index, bisect_left(self.times, next_reset) - 1),
                )
                geometry = self.geometry_finder(
                    self.order_direction, first_index, end_index
                )
                if geometry is None:
                    continue
                existing = self._opposite_by_first_index.get(
                    int(getattr(geometry, "first_idx"))
                )
                if (
                    existing is None
                    or int(getattr(existing, "break_idx"))
                    != int(getattr(geometry, "break_idx"))
                ):
                    continue
                geometry = existing
                number = self.opposite_reactions.index(existing) + 1
                confirmation = self._confirmation_for(
                    geometry, self.order_direction
                )
            else:
                if not self._reset_leg_has_simple_trend_reaction(
                    leg_start, crossing
                ):
                    continue
                order_b = self._first_order_b_geometry(
                    reset_time, crossing, next_reset
                )
                if order_b is None:
                    continue
                number, geometry, confirmation = order_b

            all_synthetic.append(
                (number, geometry, confirmation, reset_time, crossing)
            )

        if audit_legacy:
            self._audit_synthetic_order_cache = all_synthetic
        else:
            self._synthetic_order_cache = all_synthetic
        return [item for item in all_synthetic if item[3] >= start]
```

### FUN-E-023 — `EZoneDetector._direct_parent_stop_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._direct_parent_stop_order`  
Source-Lines: 790-873  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _direct_parent_stop_order(
        self,
        start: datetime,
        continuous_deadline: datetime | None,
        allow_bounded_continue: bool,
    ) -> tuple[int, object, datetime] | None:
        """Select the direct parent-stop Order without Reset-leg evidence."""
        gate_time = self.times[self._main_index(start)]
        geometric_direct = self._first_healthy_direct_geometry(
            start, allow_bounded_continue
        )
        direct_position = bisect_left(self._opposite_first_times, gate_time)
        while (
            direct_position < len(self.opposite_reactions)
            and self._opposite_first_times[direct_position]
            in self.blocked_order_first_times
            and self._opposite_first_times[direct_position] == gate_time
        ):
            direct_position += 1

        independent = None
        if direct_position < len(self.opposite_reactions):
            independent = (
                direct_position + 1,
                self.opposite_reactions[direct_position],
                self._opposite_confirmations[direct_position],
            )
        geometric_gate_decision = (
            getattr(geometric_direct[1], "order_gate_decision", None)
            if geometric_direct is not None
            else None
        )
        prefer_geometric = (
            continuous_deadline is not None
            and geometric_direct is not None
            and geometric_gate_decision == "restart"
            and (
                continuous_deadline == self.range_end
                or continuous_deadline < geometric_direct[2]
            )
        )
        independent_cross = None
        if independent is not None:
            independent_level, _, _ = self._order_stop(
                independent[0], independent[1]
            )
            independent_cross = self._cross_order(
                independent[2], independent_level
            )

        direct_pool: list[tuple[int, object, datetime]] = []
        if prefer_geometric:
            direct_pool.append(geometric_direct)
        elif (
            allow_bounded_continue
            and geometric_direct is not None
            and geometric_direct[0] == 0
            and geometric_gate_decision == "continue"
            and (
                independent is None
                or self._reaction_first_time(geometric_direct[1])
                < self._reaction_first_time(independent[1])
            )
        ):
            direct_pool.append(geometric_direct)
        elif (
            geometric_direct is not None
            and independent_cross is None
            and (
                independent is None
                or self._reaction_first_time(geometric_direct[1])
                < self._reaction_first_time(independent[1])
            )
        ):
            direct_pool.append(geometric_direct)
        elif independent is not None:
            direct_pool.append(independent)

        if not direct_pool:
            return None
        return min(
            direct_pool,
            key=lambda item: (self._reaction_first_time(item[1]), item[2]),
        )
```

### FUN-E-024 — `EZoneDetector._merge_order_candidate`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._merge_order_candidate`  
Source-Lines: 875-919  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _merge_order_candidate(
        self,
        by_geometry: dict[tuple[int, int], OrderMatch],
        number: int,
        reaction: object,
        confirmation: datetime,
        cause: str,
        *,
        parent_stop_cause_time: datetime | None = None,
        reset_time: datetime | None = None,
        reset_break: datetime | None = None,
    ) -> OrderMatch:
        """Merge one provenance cause into a single physical Order identity."""
        level, source, source_time = self._order_stop(number, reaction)
        crossed = self._cross_order(confirmation, level)
        key = (
            int(getattr(reaction, "first_idx")),
            int(getattr(reaction, "break_idx")),
        )
        existing = by_geometry.get(key)
        existing_causes = existing[7] if existing is not None else ()
        causes = tuple(dict.fromkeys((*existing_causes, cause)))
        if cause == "parent-stop":
            parent_cause = parent_stop_cause_time
            reset_cause_time = existing[9] if existing is not None else None
            reset_cause_break = existing[10] if existing is not None else None
        else:
            parent_cause = existing[8] if existing is not None else None
            reset_cause_time = reset_time
            reset_cause_break = reset_break
        match: OrderMatch = (
            number,
            reaction,
            confirmation,
            level,
            source,
            source_time,
            crossed,
            causes,
            parent_cause,
            reset_cause_time,
            reset_cause_break,
        )
        by_geometry[key] = match
        return match
```

### FUN-E-025 — `EZoneDetector._add_canonical_reset_leg_orders`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._add_canonical_reset_leg_orders`  
Source-Lines: 921-956  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _add_canonical_reset_leg_orders(
        self,
        by_geometry: dict[tuple[int, int], OrderMatch],
        start: datetime,
        provisional_deadline: datetime,
        audit_legacy: bool,
    ) -> datetime:
        """Merge canonical Reset-leg evidence up to the current decision bound."""
        for position, reaction in enumerate(self.opposite_reactions):
            confirmation = self._opposite_confirmations[position]
            if confirmation < start:
                continue
            if confirmation > provisional_deadline:
                break
            evidence = (
                self._legacy_reset_leg_evidence(reaction, start)
                if audit_legacy
                else self._reset_leg_evidence(reaction, start)
            )
            if evidence is None:
                continue
            reset_time, reset_break = evidence
            match = self._merge_order_candidate(
                by_geometry,
                position + 1,
                reaction,
                confirmation,
                "reset-leg",
                reset_time=reset_time,
                reset_break=reset_break,
            )
            if match[6] is not None:
                provisional_deadline = min(
                    provisional_deadline, match[6][2]
                )
        return provisional_deadline
```

### FUN-E-026 — `EZoneDetector.order_candidates`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector.order_candidates`  
Source-Lines: 958-1041  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def order_candidates(
        self,
        start: datetime,
        continuous_deadline: datetime | None = None,
        audit_legacy: bool = False,
        allow_bounded_continue: bool = False,
    ) -> list[OrderMatch]:
        """Return every valid E-space Order formed before this E decision."""
        cache_key = (
            start,
            continuous_deadline,
            audit_legacy,
            allow_bounded_continue,
        )
        cached = self._order_candidates_cache.get(cache_key)
        if cached is not None:
            return list(cached)

        by_geometry: dict[tuple[int, int], OrderMatch] = {}
        direct = self._direct_parent_stop_order(
            start, continuous_deadline, allow_bounded_continue
        )
        if direct is not None:
            self._merge_order_candidate(
                by_geometry,
                *direct,
                "parent-stop",
                parent_stop_cause_time=start,
            )

        for number, reaction, confirmation, reset_time, reset_break in (
            self._synthetic_reset_leg_orders(start, audit_legacy)
        ):
            if confirmation < start:
                continue
            self._merge_order_candidate(
                by_geometry,
                number,
                reaction,
                confirmation,
                "reset-leg",
                reset_time=reset_time,
                reset_break=reset_break,
            )

        known_stops = [
            item[6][2]
            for item in by_geometry.values()
            if item[6] is not None
        ]
        provisional_deadline = min(known_stops) if known_stops else self.range_end
        if continuous_deadline is not None:
            provisional_deadline = min(
                provisional_deadline, continuous_deadline
            )
        provisional_deadline = self._add_canonical_reset_leg_orders(
            by_geometry,
            start,
            provisional_deadline,
            audit_legacy,
        )

        stopped = [
            item[6][2]
            for item in by_geometry.values()
            if item[6] is not None
        ]
        decision_deadline = min(stopped) if stopped else self.range_end
        if continuous_deadline is not None:
            decision_deadline = min(decision_deadline, continuous_deadline)
        eligible = [
            item
            for item in by_geometry.values()
            if item[2] <= decision_deadline
        ]
        result = sorted(
            eligible,
            key=lambda item: (
                item[6][2] if item[6] is not None else self.range_end,
                self._reaction_first_time(item[1]),
            ),
        )
        self._order_candidates_cache[cache_key] = tuple(result)
        return result
```

### FUN-E-027 — `EZoneDetector._first_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._first_order`  
Source-Lines: 1043-1054  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_order(
        self, start: datetime, continuous_deadline: datetime | None = None,
        allow_bounded_continue: bool = False,
    ) -> OrderMatch | None:
        candidates = [
            item for item in self.order_candidates(
                start, continuous_deadline,
                allow_bounded_continue=allow_bounded_continue,
            )
            if item[6] is not None
        ]
        return candidates[0] if candidates else None
```

### FUN-E-028 — `EZoneDetector._blue_parent_superseded`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._blue_parent_superseded`  
Source-Lines: 1056-1063  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _blue_parent_superseded(self, parent: object, parent_stop: datetime) -> bool:
        """A confirmed later Red S closes an older Blue-E order lifecycle."""
        return str(getattr(parent, "family")) == "blue" and any(
            str(getattr(item, "color")) == "red"
            and getattr(item, "source_time") > getattr(parent, "source_time")
            and getattr(item, "decision_event_time") < parent_stop
            for item in self.s_zones
        )
```

### FUN-E-029 — `EZoneDetector._register_order_audit`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._register_order_audit`  
Source-Lines: 1065-1192  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _register_order_audit(
        self, parent_type: str, parent: object, parent_stop: datetime,
    ) -> None:
        if any(parent.source_time < reset <= parent_stop
               for reset in self.sequence_resets):
            return
        if (
            parent_type == "E"
            and self._blue_parent_superseded(parent, parent_stop)
        ):
            # Enforce the same ownership rule during provisional discovery
            # and final audit. Otherwise a closed branch can seed a carried
            # order into another parent before final reconciliation.
            return
        inherited_owners: list[OrderMatch] = []
        if parent_type == "S":
            inherited_owners = self._unconsumed_s_orders(parent, parent_stop)
        carried_owners = self._carried_orders_for_parent(parent, parent_stop)
        # Exact mirror contract: Bullish and Bearish use the same lifecycle
        # representative/deadline rule; only underlying price comparisons flip.
        inherited_owner = inherited_owners[0] if inherited_owners else None
        carried_owner = carried_owners[0] if carried_owners else None
        continuous_deadline = None
        if parent_type == "S" and carried_owner is None:
            continuous_deadline = (
                inherited_owner[6][2]
                if inherited_owner is not None and inherited_owner[6] is not None
                else self.range_end
            )
        order_search_start = parent_stop
        if (
            parent_type == "S"
            and carried_owner is not None
            and carried_owner[6] is not None
        ):
            order_search_start = max(parent_stop, carried_owner[6][2])
        matches = self.order_candidates(
            order_search_start, continuous_deadline,
            allow_bounded_continue=(parent_type == "S"),
        )
        gate_owned = self._gate_owned_initial_order(parent_stop)
        if gate_owned is not None:
            gate_confirmation = gate_owned[2]
            matches = [
                item for item in matches
                if (
                    "reset-leg" in item[7]
                    or self._reaction_first_time(item[1]) <= gate_confirmation
                )
            ]
        gate_time = self.times[self._main_index(parent_stop)]
        ledger_gate = [
            entry for entry in self.order_audit.values()
            if self._reaction_first_time(entry["reaction"]) == gate_time
            and entry.get("stop_cross") is not None
            and entry["stop_cross"][2] >= parent_stop
        ]
        if ledger_gate:
            owner_confirmation = min(
                entry["confirmation_time"] for entry in ledger_gate
            )
            matches = [
                item for item in matches
                if (
                    "reset-leg" in item[7]
                    or self._reaction_first_time(item[1]) <= owner_confirmation
                )
            ]
        for match in matches:
            number, reaction, confirmation, level, source, source_time = match[:6]
            crossed, causes = match[6], match[7]
            reset_evidence = None
            if "reset-leg" in causes:
                if number == 0:
                    reset_evidence = (
                        None
                        if self._reset_by_proven_order(reaction, confirmation)
                        else (
                            (match[9], match[10])
                            if match[9] is not None and match[10] is not None
                            else None
                        )
                    )
                else:
                    reset_evidence = self._legacy_reset_leg_evidence(
                        reaction, parent_stop
                    )
            # Audit is an eligibility ledger, not a provisional-candidate log.
            # A geometric Order_B may legitimately have reaction number zero,
            # while a canonical reaction may still fail Reset ownership.  Admit
            # either only after at least one creation cause is proven.
            if "parent-stop" not in causes and reset_evidence is None:
                continue
            key = (
                int(getattr(reaction, "first_idx")),
                int(getattr(reaction, "break_idx")),
            )
            entry = self.order_audit.setdefault(key, {
                "reaction_number": number,
                "reaction": reaction,
                "confirmation_time": confirmation,
                "stop_level": level,
                "stop_source_index": source,
                "stop_source_time": source_time,
                "stop_cross": crossed,
                "causes": set(),
            })
            audit_causes = entry["causes"]
            assert isinstance(audit_causes, set)
            if "parent-stop" in causes:
                family = str(getattr(parent, "color", getattr(parent, "family", "")))
                number_value = getattr(parent, "number", None)
                parent_label = parent_type
                if parent_type == "E" and number_value is not None:
                    parent_label = f"E{number_value}"
                if parent.source_time in self.sequence_resets:
                    parent_label = f"StopAll{self.sequence_resets[parent.source_time]}"
                    family = ""
                audit_causes.add(
                    (
                        "parent-stop", parent_label, family, parent_stop,
                        getattr(parent, "source_time"),
                    )
                )
            if reset_evidence is not None:
                audit_causes.add((
                    "reset-leg", reset_evidence[0], reset_evidence[1],
                ))
```

### FUN-E-030 — `EZoneDetector._reset_by_proven_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._reset_by_proven_order`  
Source-Lines: 1194-1218  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reset_by_proven_order(
        self, reaction: object, confirmation: datetime,
    ) -> bool:
        """Whether a provisional geometry is Reset by a proven live order."""
        proven = set(self.initial_order_audit)
        proven.update(
            identity for identity, entry in self.order_audit.items()
            if entry.get("causes")
        )
        first = self._reaction_first_time(reaction)
        left = bisect_left(self._opposite_reset_times, first)
        right = bisect_right(self._opposite_reset_times, confirmation)
        for _, reset in self._opposite_reset_events[left:right]:
            owner = self._opposite_by_first_index.get(
                int(getattr(reset, "from_first_idx"))
            )
            if owner is None:
                continue
            identity = (
                int(getattr(owner, "first_idx")),
                int(getattr(owner, "break_idx")),
            )
            if identity in proven:
                return True
        return False
```

### FUN-E-031 — `EZoneDetector._enrich_order_audit_reset_causes`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._enrich_order_audit_reset_causes`  
Source-Lines: 1220-1250  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _enrich_order_audit_reset_causes(self) -> None:
        """Attach established Reset evidence without changing E eligibility."""
        if not self.s_zones or not self.order_audit:
            return
        lifecycle_start = min(
            getattr(item, "decision_event_time") for item in self.s_zones
        )
        if self._audit_synthetic_order_cache is None:
            self.order_candidates(
                lifecycle_start, audit_legacy=True
            )
        reset_evidence: dict[tuple[int, int], tuple[datetime, datetime]] = {}
        for _, reaction, _, reset_time, reset_break in (
            self._audit_synthetic_order_cache or []
        ):
            if reset_time < lifecycle_start:
                continue
            identity = (
                int(getattr(reaction, "first_idx")),
                int(getattr(reaction, "break_idx")),
            )
            current = reset_evidence.get(identity)
            if current is None or reset_time < current[0]:
                reset_evidence[identity] = (reset_time, reset_break)
        for identity, (reset_time, reset_break) in reset_evidence.items():
            entry = self.order_audit.get(identity)
            if entry is None:
                continue
            causes = entry["causes"]
            assert isinstance(causes, set)
            causes.add(("reset-leg", reset_time, reset_break))
```

### FUN-E-032 — `EZoneDetector.visual_order_lifecycle`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector.visual_order_lifecycle`  
Source-Lines: 1252-1292  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def visual_order_lifecycle(
        self, start: datetime,
    ) -> list[tuple[int, object, datetime, Decimal, int, datetime,
                    tuple[int, datetime, datetime] | None, bool]]:
        """Return only orders admitted by the E lifecycle, including live ones.

        This is presentation/audit output.  It follows the same direct and
        Reset-leg replacement gates as ``_first_order`` but does not require a
        stop crossing, so a valid still-live order can be drawn without
        changing E calculation.
        """
        position = bisect_left(self._opposite_first_times, start)
        owner = None
        for order_position in range(position, len(self.opposite_reactions)):
            reaction = self.opposite_reactions[order_position]
            first = self._opposite_first_times[order_position]
            confirmation = self._opposite_confirmations[order_position]
            if first >= start and confirmation >= start:
                owner = (order_position + 1, reaction, confirmation, start)
                break
        if owner is None:
            return []

        lifecycle = []
        is_replacement = False
        while owner is not None:
            number, reaction, confirmation, context = owner
            level, source, source_time = self._order_stop(
                number, reaction, context
            )
            crossed = self._cross_order(confirmation, level)
            lifecycle.append(
                (
                    number, reaction, confirmation, level, source,
                    source_time, crossed, is_replacement,
                )
            )
            deadline = crossed[2] if crossed is not None else self.range_end
            owner = self._replacement_order(reaction, confirmation, deadline)
            is_replacement = True
        return lifecycle
```

### FUN-E-033 — `EZoneDetector._parent_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._parent_stop`  
Source-Lines: 1294-1300  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _parent_stop(self, parent_type: str, parent: object) -> tuple[int, datetime] | None:
        if parent_type == "S":
            start = getattr(parent, "decision_event_time")
        else:
            # An E can only stop after the order-stop event that confirms it.
            start = getattr(parent, "decision_event_time")
        return self._first_parent_stop(start, _decimal(getattr(parent, "price")))
```

### FUN-E-034 — `EZoneDetector.parent_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector.parent_stop`  
Source-Lines: 1302-1306  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def parent_stop(
        self, parent_type: str, parent: object
    ) -> tuple[int, datetime] | None:
        """Public lifecycle API for the first strict parent stop."""
        return self._parent_stop(parent_type, parent)
```

### FUN-E-035 — `EZoneDetector._cross_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._cross_order`  
Source-Lines: 1309-1327  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _cross_order(
        self, start: datetime, level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        cache_key = (start, level)
        if cache_key in self._cross_order_cache:
            return self._cross_order_cache[cache_key]
        left = bisect_left(self.lower_times, max(start, self.range_start))
        right = bisect_left(self.lower_times, self.range_end)
        position = self._first_cross_position(
            left, right, level, less=self.order_direction != "bearish"
        )
        if position is None:
            self._cross_order_cache[cache_key] = None
            return None
        event = self.lower_times[position]
        index = self._main_index(event)
        result = index, getattr(self.candles[index], "timestamp"), event
        self._cross_order_cache[cache_key] = result
        return result
```

### FUN-E-036 — `EZoneDetector.cross_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector.cross_order`  
Source-Lines: 1329-1333  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def cross_order(
        self, confirmation_time: datetime, stop_level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        """Public audit API for an Order stop crossing."""
        return self._cross_order(confirmation_time, stop_level)
```

### FUN-E-037 — `EZoneDetector._unconsumed_s_orders`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._unconsumed_s_orders`  
Source-Lines: 1336-1369  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _unconsumed_s_orders(
        self, parent: object, parent_stop: datetime
    ) -> list[OrderMatch]:
        """Return every Blue-S Order whose stop did not decide the S itself."""
        if (
            str(getattr(parent, "color")) != "blue"
            or getattr(parent, "order_confirmation_time", None) is None
            or getattr(parent, "order_stop_level", None) is None
        ):
            return []
        confirmation = getattr(parent, "order_confirmation_time")
        stop_level = _decimal(getattr(parent, "order_stop_level"))
        crossed = self._cross_order(confirmation, stop_level)
        if crossed is None or crossed[2] < parent_stop:
            return []
        reaction = SimpleNamespace(
            mode=getattr(parent, "order_mode"),
            first_idx=getattr(parent, "order_first_index"),
            break_idx=getattr(parent, "order_break_index"),
            box_top=getattr(parent, "order_box_top"),
            box_top_source_idx=getattr(parent, "order_box_top_source_index"),
            box_bottom=getattr(parent, "order_box_bottom"),
            box_bottom_source_idx=getattr(parent, "order_box_bottom_source_index"),
        )
        return [(
            int(getattr(parent, "order_reaction_number")),
            reaction,
            confirmation,
            stop_level,
            int(getattr(parent, "order_stop_source_index")),
            getattr(parent, "order_stop_source_time"),
            crossed,
            ("carried-live",), None, None, None,
        )]
```

### FUN-E-038 — `EZoneDetector._initial_order_match`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._initial_order_match`  
Source-Lines: 1373-1384  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _initial_order_match(
        self, entry: dict[str, object], causes: tuple[str, ...],
    ) -> OrderMatch:
        reaction = entry["reaction"]
        confirmation = entry["confirmation_time"]
        level = _decimal(entry["stop_level"])
        crossed = self._cross_order(confirmation, level)
        return (
            int(entry["reaction_number"]), reaction, confirmation, level,
            int(entry["stop_source_index"]), entry["stop_source_time"],
            crossed, causes, None, None, None,
        )
```

### FUN-E-039 — `EZoneDetector._gate_owned_initial_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._gate_owned_initial_order`  
Source-Lines: 1386-1412  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _gate_owned_initial_order(
        self, parent_stop: datetime,
    ) -> OrderMatch | None:
        """Keep an A-owned order that starts in the parent-stop candle.

        The already-open A lifecycle owns that candle.  A later ordinary
        Reaction cannot be relabeled as a new Order_A merely because the S/E
        parent stopped while the earlier order was still forming or live.
        """
        gate_time = self.times[self._main_index(parent_stop)]
        matches: list[OrderMatch] = []
        for entry in self.initial_order_audit.values():
            reaction = entry["reaction"]
            first = self._reaction_first_time(reaction)
            confirmation = entry["confirmation_time"]
            if first != gate_time or confirmation < parent_stop:
                continue
            match = self._initial_order_match(entry, ("carried-live",))
            crossed = match[6]
            if crossed is None or crossed[2] < parent_stop:
                continue
            matches.append(match)
        return min(
            matches,
            key=lambda item: (item[6][2], self._reaction_first_time(item[1])),
            default=None,
        )
```

### FUN-E-040 — `EZoneDetector._carried_orders_for_parent`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._carried_orders_for_parent`  
Source-Lines: 1414-1479  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _carried_orders_for_parent(
        self, parent: object, parent_stop: datetime,
    ) -> list[OrderMatch]:
        """Return every Order formed and left live inside this parent lifecycle."""
        lifecycle_start = getattr(parent, "decision_event_time", None)
        if lifecycle_start is None:
            # Lightweight compatibility callers may provide only the fields
            # needed to identify a parent.  Without an exact lifecycle event
            # there is no carried-live window to evaluate.
            return []
        matches: list[OrderMatch] = []
        for entry in self.order_audit.values():
            created_events: list[datetime] = []
            reset_evidence: tuple[datetime, datetime] | None = None
            for cause in entry.get("causes", set()):
                if cause[0] == "parent-stop":
                    created_events.append(cause[3])
                elif cause[0] == "reset-leg":
                    created_events.append(cause[1])
                    reset_evidence = (cause[1], cause[2])
            if not created_events:
                continue
            created = min(created_events)
            confirmation = entry["confirmation_time"]
            crossed = entry.get("stop_cross")
            if (
                created <= lifecycle_start
                or created >= parent_stop
                or confirmation > parent_stop
                or crossed is None
                or crossed[2] < parent_stop
            ):
                continue
            causes = (
                ("carried-live", "reset-leg")
                if reset_evidence is not None
                else ("carried-live",)
            )
            reaction = entry["reaction"]
            matches.append((
                int(entry["reaction_number"]), reaction, confirmation,
                _decimal(entry["stop_level"]), int(entry["stop_source_index"]),
                entry["stop_source_time"], crossed, causes, None,
                reset_evidence[0] if reset_evidence is not None else None,
                reset_evidence[1] if reset_evidence is not None else None,
            ))

        # Orders created by stopped A zones arrive through the initial audit
        # ledger.  They can become live during a later S lifecycle even when
        # their creation cause predates that S's decision event.  Formation,
        # confirmation and strict-stop chronology determine ownership here.
        for entry in self.initial_order_audit.values():
            reaction = entry["reaction"]
            first = self._reaction_first_time(reaction)
            confirmation = entry["confirmation_time"]
            if first < lifecycle_start or confirmation > parent_stop:
                continue
            match = self._initial_order_match(entry, ("carried-live",))
            crossed = match[6]
            if crossed is None or crossed[2] < parent_stop:
                continue
            matches.append(match)
        return sorted(
            matches,
            key=lambda item: (item[6][2], -int(getattr(item[1], "first_idx"))),
        )
```

### FUN-E-041 — `EZoneDetector._blocked_by_gate_owned_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._blocked_by_gate_owned_order`  
Source-Lines: 1482-1490  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _blocked_by_gate_owned_order(self, zone: EZone) -> bool:
        """Reject only a nested Order_A, while preserving its child lineage."""
        if "parent-stop" not in zone.order_causes or "reset-leg" in zone.order_causes:
            return False
        gate_owned = self._gate_owned_initial_order(zone.parent_stop_event_time)
        return (
            gate_owned is not None
            and gate_owned[2] < zone.order_first_time
        )
```

### FUN-E-042 — `EZoneDetector._reset_evidence_for_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._reset_evidence_for_order`  
Source-Lines: 1492-1503  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reset_evidence_for_order(
        self, first_index: int, break_index: int,
    ) -> tuple[datetime, datetime] | None:
        for _, reaction, _, reset_time, reset_break in (
            self._synthetic_order_cache or []
        ):
            if (
                int(getattr(reaction, "first_idx")) == first_index
                and int(getattr(reaction, "break_idx")) == break_index
            ):
                return reset_time, reset_break
        return None
```

### FUN-E-043 — `EZoneDetector._extreme_between`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._extreme_between`  
Source-Lines: 1505-1519  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _extreme_between(self, start: datetime, end: datetime) -> tuple[int, datetime, Decimal]:
        # E source ownership is candle-based: include the complete main candle
        # containing the parent stop and the complete main candle containing
        # the order stop. Lower-timeframe chronology decides whether each stop
        # happened, but it must not truncate either boundary candle's OHLC.
        start_index = max(self.start_index, self._main_index(start))
        end_index = min(self.end_index, self._main_index(end))
        source = self.candles[start_index]
        value = self._stop_value(source)
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = self._stop_value(item)
            better = self.policy.improves(candidate, value)
            if better:
                source, value = item, candidate
        return int(getattr(source, "index")), getattr(source, "timestamp"), value
```

### FUN-E-044 — `EZoneDetector._zone`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._zone`  
Source-Lines: 1521-1621  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _zone(
        self, family: str, number: int, parent_type: str,
        parent: object, stop_event: datetime,
    ) -> EZone | None:
        # Every E-space cycle starts at the strict parent stop. The order First
        # must itself strictly cross the active parent/reset boundary.
        inherited = (
            self._unconsumed_s_orders(parent, stop_event)
            if parent_type == "S"
            else []
        )
        gate_owned = self._gate_owned_initial_order(stop_event)
        carried = self._carried_orders_for_parent(parent, stop_event)
        self._register_order_audit(parent_type, parent, stop_event)
        # A stopped E opens a new direct search at its own stop candle. An
        # older order formed before that event cannot replace the first valid
        # post-stop order. S may still pass its explicitly unconsumed Blue
        # order through the dedicated inheritance rule above.
        # Exact mirror contract: one representative per creation path in both
        # directions, followed by the shared final stop-event race.
        inherited_one = inherited[0] if inherited else None
        carried_one = carried[0] if carried else None
        direct = self._first_order(
            stop_event,
            (
                inherited_one[6][2]
                if parent_type == "S" and carried_one is None
                and inherited_one is not None and inherited_one[6] is not None
                else self.range_end
                if parent_type == "S" and carried_one is None
                else None
            ),
            allow_bounded_continue=(parent_type == "S"),
        )
        choices = [
            item for item in (direct, inherited_one, carried_one)
            if item is not None and item[6] is not None
        ]
        order_match = min(
            choices,
            key=lambda item: (item[6][2], -int(getattr(item[1], "first_idx"))),
            default=None,
        )
        if order_match is None:
            return None
        (
            order_number, order, order_confirmation, order_stop,
            stop_source, stop_source_time, crossed, order_causes,
            order_parent_stop_cause_time, order_reset_leg_reset_time,
            order_reset_leg_break_time,
        ) = order_match
        if crossed is None:
            return None
        order_decision_index, order_decision_time, order_decision_event = crossed
        decision_event = max(stop_event, order_decision_event)
        decision_index = self._main_index(decision_event)
        decision_time = getattr(self.candles[decision_index], "timestamp")
        source_index, source_time, price = self._extreme_between(stop_event, decision_event)
        parent_stop_index = self._main_index(stop_event)
        order_first_index = int(getattr(order, "first_idx"))
        top_source = int(getattr(order, "box_top_source_idx"))
        bottom_source = int(getattr(order, "box_bottom_source_idx"))
        return EZone(
            direction=self.direction,
            family=family,
            number=number,
            parent_type=parent_type,
            parent_source_index=int(getattr(parent, "source_index")),
            parent_source_time=getattr(parent, "source_time"),
            parent_price=_decimal(getattr(parent, "price")),
            parent_stop_index=parent_stop_index,
            parent_stop_time=getattr(self.candles[parent_stop_index], "timestamp"),
            parent_stop_event_time=stop_event,
            order_direction=self.order_direction,
            order_reaction_number=order_number,
            order_mode=str(getattr(order, "mode")),
            order_causes=order_causes,
            order_parent_stop_cause_time=order_parent_stop_cause_time,
            order_reset_leg_reset_time=order_reset_leg_reset_time,
            order_reset_leg_break_time=order_reset_leg_break_time,
            order_first_index=order_first_index,
            order_first_time=getattr(self.candles[order_first_index], "timestamp"),
            order_break_index=int(getattr(order, "break_idx")),
            order_break_time=getattr(self.candles[int(getattr(order, "break_idx"))], "timestamp"),
            order_confirmation_time=order_confirmation,
            order_box_top=_decimal(getattr(order, "box_top")),
            order_box_top_source_index=top_source,
            order_box_top_source_time=getattr(self.candles[top_source], "timestamp"),
            order_box_bottom=_decimal(getattr(order, "box_bottom")),
            order_box_bottom_source_index=bottom_source,
            order_box_bottom_source_time=getattr(self.candles[bottom_source], "timestamp"),
            order_stop_level=order_stop,
            order_stop_source_index=stop_source,
            order_stop_source_time=stop_source_time,
            source_index=source_index,
            source_time=source_time,
            price=price,
            decision_index=decision_index,
            decision_time=decision_time,
            decision_event_time=decision_event,
        )
```

### FUN-E-045 — `EZoneDetector._discover_candidate_chains`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._discover_candidate_chains`  
Source-Lines: 1623-1663  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _discover_candidate_chains(self) -> list[EZone]:
        """Build provisional recursive E chains from every stopped S parent."""
        candidates: list[EZone] = []
        # Discover S-owned orders before walking recursive E chains.  A valid
        # order formed inside an E parent's lifetime must remain available even
        # when that S branch is reconciled later than the E branch.
        for s_zone in self.s_zones:
            stop = self._parent_stop("S", s_zone)
            if stop is not None:
                self._register_order_audit("S", s_zone, stop[1])

        for s_zone in self.s_zones:
            stop = self._parent_stop("S", s_zone)
            if stop is None:
                continue
            _, stop_event = stop

            # Every fully formed S starts an independent E chain. E1 remains
            # visible when E2 is later formed; numbering is advanced only by
            # a strict stop of the immediately previous E in that chain.
            family = str(getattr(s_zone, "color"))
            number = 1

            parent_type: str = "S"
            parent: object = s_zone
            chain_sources: set[int] = set()
            while True:
                zone = self._zone(family, number, parent_type, parent, stop_event)
                if zone is None:
                    break
                if zone.source_index in chain_sources:
                    break
                candidates.append(zone)
                chain_sources.add(zone.source_index)
                parent_type, parent = "E", zone
                next_stop = self._parent_stop("E", zone)
                if next_stop is None:
                    break
                _, stop_event = next_stop
                number += 1
        return candidates
```

### FUN-E-046 — `EZoneDetector._reconcile_candidate_chains`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._reconcile_candidate_chains`  
Source-Lines: 1665-1991  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reconcile_candidate_chains(
        self, candidates: list[EZone]
    ) -> list[EZone]:
        """Resolve competing E chains into the accepted chronological lifecycle."""
        # Resolve competing chains chronologically.  A stopped E is removed
        # from the active set immediately; it remains only as historical
        # output and cannot affect a later family or number.
        by_source: dict[int, list[EZone]] = {}
        for zone in candidates:
            by_source.setdefault(zone.source_index, []).append(zone)
        # A later E continuation can supersede a provisional E that was
        # started directly from an S before the continuation was confirmed.
        # Keep the later, deeper (bullish) / higher (bearish) structure.  This
        # This prevents a provisional S-owned object from consuming the active
        # chain before the later confirmed continuation.
        pending = sorted(
            by_source.values(),
            key=lambda item: (
                min(zone.source_time for zone in item),
                min(zone.decision_event_time for zone in item),
            ),
        )
        numbered: list[EZone] = []
        active: list[EZone] = []
        sequence_start: datetime | None = None

        candidates_by_source_time = {
            (item.source_index, item.source_time): item
            for item in candidates
        }

        children_by_parent: dict[tuple[int, object], list[EZone]] = {}
        s_children_by_source: dict[tuple[int, object], list[EZone]] = {}
        for item in candidates:
            if item.parent_type == "E":
                children_by_parent.setdefault(
                    (item.parent_source_index, item.parent_source_time), []
                ).append(item)
            elif item.parent_type == "S":
                s_children_by_source.setdefault(
                    (item.source_index, item.source_time), []
                ).append(item)

        def valid_order(zone: EZone) -> bool:
            if self._blocked_by_gate_owned_order(zone):
                return False
            if (
                zone.parent_type == "S"
                or zone.order_mode != "B"
                or zone.family != "blue"
            ):
                return True
            children = children_by_parent.get(
                (zone.source_index, zone.source_time), []
            )
            for child in children:
                for competing in s_children_by_source.get(
                    (child.source_index, child.source_time), []
                ):
                    if competing.decision_event_time <= child.decision_event_time:
                        return False
            return True

        def invalidated_only_by_future_s(zone: EZone) -> bool:
            if valid_order(zone) or zone.parent_type != "E":
                return False
            children = children_by_parent.get(
                (zone.source_index, zone.source_time), []
            )
            parent_times = {
                competing.parent_source_time
                for child in children
                for competing in s_children_by_source.get(
                    (child.source_index, child.source_time), []
                )
                if competing.decision_event_time <= child.decision_event_time
            }
            return any(value > zone.source_time for value in parent_times)

        def parent_active(zone: EZone, seen: set[tuple[int, datetime]] | None = None) -> bool:
            if zone.parent_type == "S":
                parent_s = next(
                    (
                        item for item in self.s_zones
                        if int(getattr(item, "source_index"))
                        == zone.parent_source_index
                        and getattr(item, "source_time")
                        == zone.parent_source_time
                    ),
                    None,
                )
                if parent_s is None:
                    return False
                if sequence_start is not None and (
                    parent_s.source_time <= sequence_start
                    or parent_s.a_source_time < sequence_start
                ):
                    return False
                prior_e = [
                    item for item in numbered
                    if getattr(item, "source_time")
                    < zone.source_time
                    and (sequence_start is None or item.source_time > sequence_start)
                ]
                if not prior_e:
                    return True
                prior = max(
                    prior_e, key=lambda item: getattr(item, "source_time")
                )
                rebuilt_after_e = (
                    getattr(parent_s, "source_time")
                    > getattr(prior, "source_time")
                    and getattr(parent_s, "a_source_time")
                    >= getattr(prior, "source_time")
                )
                # A still-unconsumed Red S is not invalidated by a nested
                # Blue E. Its later strict stop owns the Red transition.
                dominant_s = (
                    str(getattr(parent_s, "color")) == "red"
                    and prior.family == "blue"
                    and parent_s.source_time < prior.source_time
                    and not any(
                        item.parent_type == "S"
                        and item.parent_source_time == zone.parent_source_time
                        for item in numbered
                    )
                )
                return rebuilt_after_e or dominant_s
            if zone.parent_source_time == sequence_start:
                # The StopAll source is a valid order gate, but never an
                # active E whose family/number could leak across the reset.
                return True
            if any(
                item.source_index == zone.parent_source_index
                and item.source_time == zone.parent_source_time
                for item in active
            ):
                return True
            identity = (zone.parent_source_index, zone.parent_source_time)
            if seen is None:
                seen = set()
            if identity in seen:
                return False
            seen.add(identity)
            skipped_parent = candidates_by_source_time.get(identity)
            return (
                skipped_parent is not None
                and not valid_order(skipped_parent)
                and parent_active(skipped_parent, seen)
            )

        def stopped_by(zone: EZone, prior: EZone) -> bool:
            if zone.decision_event_time <= prior.decision_event_time:
                return False
            if self.direction == "bullish":
                return zone.price < prior.price
            return zone.price > prior.price

        for group in pending:
            eligible = [
                item for item in group
                if valid_order(item) and parent_active(item)
            ]
            if not eligible:
                continue
            # A lower-priority S cannot steal an active E continuation.
            # Red S may supersede Blue E, but no S supersedes Red E.
            # Color follows the accepted stopped parent's reconciled family.
            eligible = [
                item
                for item in eligible
                if not (
                    item.parent_type == "S"
                    and any(
                        stopped_by(item, owner)
                        and (owner.family == "red" or item.family == "blue")
                        and any(
                            child.parent_type == "E"
                            and child.parent_source_index == owner.source_index
                            and child.parent_source_time == owner.source_time
                            and child.decision_event_time
                            >= item.decision_event_time
                            for child in candidates
                        )
                        for owner in active
                    )
                )
            ]
            if not eligible:
                continue
            current_owners = [
                item for item in eligible
                if not (
                    item.parent_type == "E"
                    and item.family == "blue"
                    and any(
                        str(getattr(s_zone, "color")) == "red"
                        and getattr(s_zone, "source_time")
                        > item.parent_source_time
                        and getattr(s_zone, "decision_event_time")
                        < item.parent_stop_event_time
                        for s_zone in self.s_zones
                    )
                )
            ]
            if current_owners:
                eligible = current_owners
            def ownership_priority(item: EZone) -> int:
                parent = next((prior for prior in active
                    if item.parent_type == "E"
                    and prior.source_time == item.parent_source_time), None)
                parent_family = parent.family if parent else item.family
                return self.sequence_priority(item.parent_type, parent_family)

            zone = min(
                eligible,
                key=lambda item: (
                    item.decision_event_time,
                    -ownership_priority(item),
                    item.parent_stop_event_time,
                ),
            )
            stopped_by_family: dict[str, list[EZone]] = {"red": [], "blue": []}
            for prior in active:
                if stopped_by(zone, prior):
                    stopped_by_family[prior.family].append(prior)

            parent_identity = (zone.parent_source_index, zone.parent_source_time)
            parent_is_active = (
                zone.parent_type == "S"
                or zone.parent_source_time == sequence_start
            ) or any(
                (item.source_index, item.source_time) == parent_identity
                for item in active
            )
            if not parent_is_active:
                reset_evidence = self._reset_evidence_for_order(
                    zone.order_first_index, zone.order_break_index
                )
                if reset_evidence is not None:
                    zone = replace(
                        zone,
                        order_causes=("reset-leg",),
                        order_parent_stop_cause_time=None,
                        order_reset_leg_reset_time=reset_evidence[0],
                        order_reset_leg_break_time=reset_evidence[1],
                    )

            owner = next((item for item in active
                          if zone.parent_type == "E"
                          and item.source_time == zone.parent_source_time), None)
            # Color follows the accepted stopped parent, not merely the most
            # recent S. A still-unbroken Red S does not recolor a nested E.
            parent_family = owner.family if owner is not None else zone.family

            if parent_family == "red":
                family = "red"
                number = (
                    max(item.number for item in stopped_by_family["red"]) + 1
                    if stopped_by_family["red"]
                    else 1
                )
            elif stopped_by_family["red"]:
                family = "red"
                number = max(item.number for item in stopped_by_family["red"]) + 1
            elif parent_family == "blue":
                family = "blue"
                number = (
                    max(item.number for item in stopped_by_family["blue"]) + 1
                    if stopped_by_family["blue"]
                    else 1
                )
            elif stopped_by_family["blue"]:
                family = "blue"
                number = max(item.number for item in stopped_by_family["blue"]) + 1
            else:
                family = zone.family
                number = 1
            stopped_ids = {
                (item.source_index, item.source_time)
                for values in stopped_by_family.values() for item in values
            }
            active = [
                item for item in active
                if (item.source_index, item.source_time) not in stopped_ids
            ]
            numbered_zone = replace(zone, family=family, number=number)
            numbered.append(numbered_zone)
            if zone.source_time in self.sequence_resets:
                active.clear()
                sequence_start = zone.source_time
            else:
                active.append(numbered_zone)
        def collect_lineage(zone: EZone, seen: set[tuple[int, datetime]]) -> None:
            identity = (zone.source_index, zone.source_time)
            if identity in seen:
                return
            seen.add(identity)
            self.visual_lifecycle_starts.add(zone.parent_stop_event_time)
            if zone.parent_type == "S":
                return
            parent = candidates_by_source_time.get(
                (zone.parent_source_index, zone.parent_source_time)
            )
            if parent is not None:
                collect_lineage(parent, seen)

        numbered_ids = {
            (item.source_index, item.source_time) for item in numbered
        }
        numbered.extend(
            item for item in candidates
            if invalidated_only_by_future_s(item)
            and (item.source_index, item.source_time) not in numbered_ids
            and not any(item.parent_source_time < reset <= item.source_time
                        for reset in self.sequence_resets)
        )

        lineage_seen: set[tuple[int, datetime]] = set()
        for zone in numbered:
            collect_lineage(zone, lineage_seen)

        numbered = [replace(item, parent_type="StopAll")
                    if item.parent_type == "E"
                    and item.parent_source_time in self.sequence_resets
                    else item for item in numbered]
        return numbered
```

### FUN-E-047 — `EZoneDetector._rebuild_accepted_order_audit`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector._rebuild_accepted_order_audit`  
Source-Lines: 1993-2098  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _rebuild_accepted_order_audit(
        self, numbered: list[EZone]
    ) -> list[EZone]:
        """Rebuild Order Audit from accepted S/E/StopAll state only."""
        # Audit only accepted S/E state. Provisional candidate chains must not
        # create visible or reported order genders.
        self.order_audit.clear()
        accepted_parents: list[tuple[str, object]] = [
            ("S", item) for item in self.s_zones
        ] + [("StopAll" if item.source_time in self.sequence_resets else "E", item)
             for item in numbered]
        for parent_type, parent in accepted_parents:
            stop = self._parent_stop(parent_type, parent)
            if stop is None:
                continue
            if parent_type == "E":
                # A later accepted Red S owns the behavioral color and closes
                # older Blue-E continuation state. The historical E remains
                # visible, but its later price crossing cannot open an order.
                if self._blue_parent_superseded(parent, stop[1]):
                    continue
            self._register_order_audit(parent_type, parent, stop[1])

        # Every order embedded in an accepted E is effective by definition.
        # Keep it in audit even when its provisional parent was skipped and
        # the child was reattached to the nearest active ancestor.
        for zone in numbered:
            identity = (zone.order_first_index, zone.order_break_index)
            if identity in self.order_audit:
                continue
            reaction = self._opposite_by_first_index.get(zone.order_first_index)
            if (
                reaction is None
                or int(getattr(reaction, "break_idx")) != zone.order_break_index
            ):
                continue
            causes: set[tuple[object, ...]] = set()
            if zone.order_parent_stop_cause_time is not None:
                parent_label = zone.parent_type
                if zone.parent_type == "E":
                    parent_zone = next(
                        (
                            item for item in numbered
                            if item.source_index == zone.parent_source_index
                            and item.source_time == zone.parent_source_time
                        ),
                        None,
                    )
                    if parent_zone is not None:
                        parent_label = f"E{parent_zone.number}"
                if zone.parent_source_time in self.sequence_resets:
                    parent_label = f"StopAll{self.sequence_resets[zone.parent_source_time]}"
                causes.add((
                    "parent-stop",
                    parent_label,
                    "" if zone.parent_source_time in self.sequence_resets else zone.family,
                    zone.parent_stop_event_time,
                    zone.parent_source_time,
                ))
            if (
                zone.order_reset_leg_reset_time is not None
                and zone.order_reset_leg_break_time is not None
            ):
                causes.add((
                    "reset-leg",
                    zone.order_reset_leg_reset_time,
                    zone.order_reset_leg_break_time,
                ))
            self.order_audit[identity] = {
                "reaction_number": zone.order_reaction_number,
                "reaction": reaction,
                "confirmation_time": zone.order_confirmation_time,
                "stop_level": zone.order_stop_level,
                "stop_source_index": zone.order_stop_source_index,
                "stop_source_time": zone.order_stop_source_time,
                "stop_cross": (
                    zone.decision_index,
                    zone.decision_time,
                    zone.decision_event_time,
                ),
                "causes": causes,
            }

        self._enrich_order_audit_reset_causes()

        # A retained order can have Reset-leg evidence predating its new
        # StopAll gate. Preserve that proven secondary cause in the emitted
        # object as well as the ledger; it never changes selection or weight.
        for index, zone in enumerate(numbered):
            if zone.parent_type != "StopAll":
                continue
            entry = self.order_audit.get((zone.order_first_index, zone.order_break_index))
            reset_causes = sorted(cause for cause in entry["causes"]
                                  if cause[0] == "reset-leg") if entry else []
            if reset_causes and "reset-leg" not in zone.order_causes:
                cause = reset_causes[0]
                numbered[index] = replace(
                    zone, order_causes=(*zone.order_causes, "reset-leg"),
                    order_reset_leg_reset_time=cause[1],
                    order_reset_leg_break_time=cause[2],
                )

        return sorted(
            numbered,
            key=lambda item: (item.source_time, item.source_index),
        )
```

### FUN-E-048 — `EZoneDetector.detect`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:EZoneDetector.detect`  
Source-Lines: 2100-2106  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect(self) -> list[EZone]:
        """Discover, reconcile and audit recursive E lifecycles."""
        self.order_audit.clear()
        self.visual_lifecycle_starts.clear()
        candidates = self._discover_candidate_chains()
        numbered = self._reconcile_candidate_chains(candidates)
        return self._rebuild_accepted_order_audit(numbered)
```

### FUN-E-049 — `detect_e_zones`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `e_zone_detector.py:detect_e_zones`  
Source-Lines: 2109-2142  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect_e_zones(
    direction: str,
    trend_reactions: Sequence[object],
    opposite_reactions: Sequence[object],
    s_zones: Sequence[object],
    trend_resets: Sequence[object],
    opposite_resets: Sequence[object],
    chronology: object,
    start_index: int = 0,
    end_index: int | None = None,
    geometry_finder: Callable[[str, int, int], object | None] | None = None,
    direct_geometry_finder: Callable[[str, int, int, datetime], object | None] | None = None,
    blocked_order_first_times: set[datetime] | None = None,
    initial_order_audit: dict[tuple[int, int], dict[str, object]] | None = None,
    reset_geometry_finder: Callable[[str, int, int, int], object | None] | None = None,
    sequence_priority: Callable[[str, str], int] | None = None,
) -> list[EZone]:
    return EZoneDetector(
        direction,
        trend_reactions,
        opposite_reactions,
        s_zones,
        trend_resets,
        opposite_resets,
        chronology,
        start_index,
        end_index,
        geometry_finder,
        direct_geometry_finder,
        blocked_order_first_times,
        initial_order_audit,
        reset_geometry_finder,
        sequence_priority=sequence_priority,
    ).detect()
```

### FUN-LIF-001 — `sequence_priority`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:sequence_priority`  
Source-Lines: 31-33  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def sequence_priority(kind: str, family: str) -> int:
    """Return the single authoritative cross-stage behavior priority."""
    return SEQUENCE_PRIORITY[(str(kind).lower(), str(family).lower())]
```

### FUN-LIF-002 — `_decimal`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:_decimal`  
Source-Lines: 36-37  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _decimal(value: object) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))
```

### FUN-LIF-003 — `StopAllDetector.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:StopAllDetector.__init__`  
Source-Lines: 84-103  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(
        self,
        direction: str,
        s_zones: Sequence[object],
        e_zones: Sequence[object],
        chronology: object,
    ) -> None:
        self.policy = get_direction_policy(direction)
        self.direction = self.policy.name
        self._is_bullish = self.policy.is_bullish
        self.s_zones = list(s_zones)
        self.e_zones = sorted(
            e_zones, key=lambda item: (item.source_time, item.source_index)
        )
        self.chronology = chronology
        self.candles = chronology.candles
        self.lower = chronology.raw_candles
        self.lower_times = chronology.raw_times
        self.lower_index = chronology.lower_index
        self.times = chronology.times
```

### FUN-LIF-004 — `StopAllDetector._strict_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:StopAllDetector._strict_stop`  
Source-Lines: 105-119  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _strict_stop(
        self, start: datetime, level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        left = bisect_left(self.lower_times, start)
        right = len(self.lower)
        position = (
            self.lower_index.first_less(left, right, level)
            if self._is_bullish
            else self.lower_index.first_greater(left, right, level)
        )
        if position is None:
            return None
        event = self.lower_times[position]
        index = self.chronology.main_index(event, clamp=True)
        return index, self.times[index], event
```

### FUN-LIF-005 — `StopAllDetector._e_key`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:StopAllDetector._e_key`  
Source-Lines: 122-123  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _e_key(item: object) -> tuple[str, int]:
        return str(item.family), int(item.number)
```

### FUN-LIF-006 — `StopAllDetector._dominates_e`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:StopAllDetector._dominates_e`  
Source-Lines: 126-133  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _dominates_e(new: tuple[str, int], old: tuple[str, int]) -> bool:
        new_family, new_number = new
        old_family, old_number = old
        if new_family == old_family:
            return new_number > old_number
        # Red is always the dominant E family. A higher-numbered Blue E must
        # not separate or replace an active Red group.
        return new_family == "red" and old_family == "blue"
```

### FUN-LIF-007 — `StopAllDetector._sequence_priority`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:StopAllDetector._sequence_priority`  
Source-Lines: 136-137  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _sequence_priority(cls, kind: str, family: str) -> int:
        return sequence_priority(kind, family)
```

### FUN-LIF-008 — `StopAllDetector._active_sequence_priority`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:StopAllDetector._active_sequence_priority`  
Source-Lines: 140-147  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _active_sequence_priority(
        cls, s_key: str | None, e_key: tuple[str, int] | None,
    ) -> int:
        if e_key is not None:
            return cls._sequence_priority("e", e_key[0])
        if s_key is not None:
            return cls._sequence_priority("s", s_key)
        return 0
```

### FUN-LIF-009 — `StopAllDetector._stopall_from_e`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:StopAllDetector._stopall_from_e`  
Source-Lines: 149-205  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _stopall_from_e(
        self,
        item: object,
        number: int,
        gate_type: str,
        gate_event: datetime,
        behavior_type: str,
        behavior_key: str,
        behavior_count: int,
    ) -> StopAll:
        return StopAll(
            direction=self.direction,
            number=number,
            source_index=int(item.source_index),
            source_time=item.source_time,
            price=_decimal(item.price),
            decision_index=int(item.decision_index),
            decision_time=item.decision_time,
            decision_event_time=item.decision_event_time,
            gate_type=gate_type,
            gate_event_time=gate_event,
            stopped_behavior_type=behavior_type,
            stopped_behavior_key=behavior_key,
            stopped_behavior_count=behavior_count,
            underlying_e_family=str(item.family),
            underlying_e_number=int(item.number),
            order_direction=str(item.order_direction),
            order_reaction_number=int(item.order_reaction_number),
            order_mode=str(item.order_mode),
            order_causes=tuple(getattr(item, "order_causes", ())),
            order_parent_stop_cause_time=getattr(
                item, "order_parent_stop_cause_time", None
            ),
            order_reset_leg_reset_time=getattr(
                item, "order_reset_leg_reset_time", None
            ),
            order_reset_leg_break_time=getattr(
                item, "order_reset_leg_break_time", None
            ),
            order_first_index=int(item.order_first_index),
            order_first_time=item.order_first_time,
            order_break_index=int(item.order_break_index),
            order_break_time=item.order_break_time,
            order_confirmation_time=item.order_confirmation_time,
            order_box_top=_decimal(item.order_box_top),
            order_box_top_source_index=int(item.order_box_top_source_index),
            order_box_top_source_time=item.order_box_top_source_time,
            order_box_bottom=_decimal(item.order_box_bottom),
            order_box_bottom_source_index=int(item.order_box_bottom_source_index),
            order_box_bottom_source_time=item.order_box_bottom_source_time,
            order_stop_level=_decimal(item.order_stop_level),
            order_stop_source_index=int(item.order_stop_source_index),
            order_stop_source_time=item.order_stop_source_time,
            stop_index=None,
            stop_time=None,
            stop_event_time=None,
        )
```

### FUN-LIF-010 — `StopAllDetector.detect`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:StopAllDetector.detect`  
Source-Lines: 207-323  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect(self) -> list[StopAll]:
        s_events = sorted(
            self.s_zones, key=lambda item: (item.source_time, item.source_index)
        )
        s_position = 0
        s_key: str | None = None
        s_count = 0
        e_key: tuple[str, int] | None = None
        e_count = 0
        active: list[StopAll] = []
        output: list[StopAll] = []

        for e_item in self.e_zones:
            while s_position < len(s_events) and (
                s_events[s_position].source_time < e_item.source_time
            ):
                s_item = s_events[s_position]
                color = str(s_item.color)
                incoming_priority = self._sequence_priority("s", color)
                active_priority = self._active_sequence_priority(s_key, e_key)
                if e_key is None and s_key == color:
                    s_count += 1
                elif incoming_priority > active_priority:
                    s_key, s_count = color, 1
                    e_key, e_count = None, 0
                s_position += 1

            e_decision = e_item.decision_event_time
            stopped_active = []
            for item in active:
                stop = self._strict_stop(item.decision_event_time, item.price)
                if stop is not None and stop[2] <= e_decision:
                    stopped_active.append((item, stop))
            if stopped_active:
                highest = max(item.number for item, _ in stopped_active)
                gate_event = min(stop[2] for _, stop in stopped_active)
                zone = self._stopall_from_e(
                    e_item, highest + 1, "stopall-stop", gate_event,
                    "StopAll", f"StopAll{highest}", len(stopped_active),
                )
                stopped_ids = {id(item) for item, _ in stopped_active}
                active = [item for item in active if id(item) not in stopped_ids]
                output.append(zone)
                active.append(zone)
                s_key = e_key = None
                s_count = e_count = 0
                continue

            new_key = self._e_key(e_item)
            # Once a dominant group has stopped, this E supplies the winning
            # order only. Its family/number need not match the stopped group.
            qualifies_e = e_key is not None and e_count >= 2
            qualifies_s = (
                e_key is None
                and s_key is not None
                and s_count >= 2
            )
            if qualifies_e or qualifies_s:
                parent = max(
                    (
                        item for item in (
                            self.e_zones if qualifies_e else self.s_zones
                        )
                        if item.source_time < e_item.source_time
                        and (
                            self._e_key(item) == e_key if qualifies_e
                            else str(item.color) == s_key
                        )
                    ),
                    key=lambda item: item.source_time,
                )
                gate = self._strict_stop(parent.decision_event_time, _decimal(parent.price))
                if gate is not None and gate[2] <= e_decision:
                    zone = self._stopall_from_e(
                        e_item, 1, "sequence-group-stop", gate[2],
                        "E" if qualifies_e else "S",
                        (
                            f"E{e_key[1]} {e_key[0]}" if qualifies_e
                            else f"S {s_key}"
                        ),
                        e_count if qualifies_e else s_count,
                    )
                    output.append(zone)
                    active.append(zone)
                    s_key = e_key = None
                    s_count = e_count = 0
                    continue

            if e_key == new_key:
                e_count += 1
            else:
                incoming_priority = self._sequence_priority("e", new_key[0])
                active_priority = self._active_sequence_priority(s_key, e_key)
                replaces_active = incoming_priority > active_priority
                advances_e = (
                    e_key is not None
                    and incoming_priority == active_priority
                    and self._dominates_e(new_key, e_key)
                )
                if replaces_active or advances_e:
                    e_key, e_count = new_key, 1
                    s_key, s_count = None, 0
            # A lower-priority Sequence event remains valid output but cannot
            # replace or separate the active dominant group.

        completed = []
        for item in output:
            stop = self._strict_stop(item.decision_event_time, item.price)
            completed.append(
                replace(
                    item,
                    stop_index=stop[0] if stop else None,
                    stop_time=stop[1] if stop else None,
                    stop_event_time=stop[2] if stop else None,
                )
            )
        return completed
```

### FUN-LIF-011 — `detect_stopalls`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:detect_stopalls`  
Source-Lines: 326-332  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect_stopalls(
    direction: str,
    s_zones: Sequence[object],
    e_zones: Sequence[object],
    chronology: object,
) -> list[StopAll]:
    return StopAllDetector(direction, s_zones, e_zones, chronology).detect()
```

### FUN-LIF-012 — `prepare_order_audit`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:prepare_order_audit`  
Source-Lines: 338-428  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def prepare_order_audit(
    detector,
    start_index: int,
    end_index: int,
    s_detector=None,
    accepted_a_sources: set[datetime] | None = None,
):
    """Resolve calculation-valid Order Audit identities before serialization.

    Multiple causes may own the same physical ``(FirstIndex, BreakIndex)``
    Order.  This function keeps one identity, merges all accepted provenance,
    applies calculation eligibility, and resolves the canonical stop crossing.
    It intentionally returns native datetimes/prices; JSON formatting remains
    the pipeline serializer's responsibility.
    """
    combined: list[tuple[dict[str, object], list[dict[str, object]]]] = []

    if s_detector is not None:
        for entry in s_detector.order_audit.values():
            a_causes = entry.get("a_causes") or [(
                entry["a_source_time"], entry["a_stop_event_time"]
            )]
            if accepted_a_sources is not None:
                a_causes = [
                    cause for cause in a_causes
                    if cause[0] in accepted_a_sources
                ]
            if not a_causes:
                continue
            combined.append((entry, [
                {
                    "kind": "parent-stop",
                    "parentType": "A",
                    "parentFamily": None,
                    "eventTime": stop_time,
                    "parentSourceTime": source_time,
                }
                for source_time, stop_time in a_causes
            ]))

    for entry in detector.order_audit.values():
        causes: list[dict[str, object]] = []
        for cause in sorted(entry["causes"], key=str):
            if cause[0] == "parent-stop":
                causes.append({
                    "kind": cause[0],
                    "parentType": cause[1],
                    "parentFamily": cause[2],
                    "eventTime": cause[3],
                    "parentSourceTime": cause[4],
                })
            else:
                causes.append({
                    "kind": cause[0],
                    "resetTime": cause[1],
                    "boundaryBreakTime": cause[2],
                })
        combined.append((entry, causes))

    merged: dict[tuple[int, int], dict[str, object]] = {}
    output: list[dict[str, object]] = []
    for entry, supplied_causes in combined:
        reaction = entry["reaction"]
        if bool(getattr(reaction, "behavior_internal", False)):
            continue
        first_index = int(getattr(reaction, "first_idx"))
        if not start_index <= first_index <= end_index:
            continue
        identity = (first_index, int(getattr(reaction, "break_idx")))
        existing = merged.get(identity)
        if existing is not None:
            existing_causes = existing["causes"]
            existing_causes.extend(
                cause for cause in supplied_causes
                if cause not in existing_causes
            )
            continue
        crossed = entry.get("stop_cross")
        if "stop_cross" not in entry:
            crossed = detector.cross_order(
                entry["confirmation_time"], entry["stop_level"]
            )
        prepared = {
            "entry": entry,
            "reaction": reaction,
            "causes": list(supplied_causes),
            "crossed": crossed,
        }
        merged[identity] = prepared
        output.append(prepared)
    return output
```

### FUN-LIF-013 — `accepted_audit_entry`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:accepted_audit_entry`  
Source-Lines: 431-458  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def accepted_audit_entry(
    entry: dict[str, object], accepted_sources: set
) -> dict[str, object] | None:
    """Return an E-facing A audit entry for one accepted A provenance.

    A physical order may be opened by more than one stopped A.  E still
    consumes one identity-keyed entry, so select the first accepted cause
    while retaining the complete cause list for presentation serialization.
    """
    causes = entry.get("a_causes") or [
        (entry["a_source_time"], entry["a_stop_event_time"])
    ]
    selected = next(
        ((source_time, stop_time) for source_time, stop_time in causes
         if source_time in accepted_sources),
        None,
    )
    if selected is None:
        return None
    if (
        selected[0] == entry.get("a_source_time")
        and selected[1] == entry.get("a_stop_event_time")
    ):
        return entry
    adjusted = dict(entry)
    adjusted["a_source_time"] = selected[0]
    adjusted["a_stop_event_time"] = selected[1]
    return adjusted
```

### FUN-LIF-014 — `resolve_order_context`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:resolve_order_context`  
Source-Lines: 460-509  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def resolve_order_context(
    order_audit: dict,
    accepted_a_sources: set[datetime],
    inherited_blocked_first_times: set[datetime],
    invalid_a_zones: Sequence[object],
    pending_s_a_sources: set[datetime],
    opposite_reactions: Sequence[object],
    candles: Sequence[object],
    direction: str,
    stop_finder,
) -> tuple[dict, set[datetime]]:
    """Resolve accepted stopped-A Orders against provisional Order blocks.

    Calculation ownership is authoritative: a canonical Order already accepted
    from stopped-A audit provenance cannot also be vetoed by the provisional
    invalid-leg-head block.  Keep the complete identity-keyed audit entries
    while filtering causes to A sources that remain calculation-eligible.
    """
    accepted_orders = {
        key: accepted
        for key, value in order_audit.items()
        for accepted in [accepted_audit_entry(value, accepted_a_sources)]
        if accepted is not None
    }

    blocked_order_first_times = set(inherited_blocked_first_times)
    blocked_order_first_times.update(
        blocked_orders_while_invalid_leg_heads_are_live(
            [
                item for item in invalid_a_zones
                if getattr(item, "source_time") in pending_s_a_sources
            ],
            opposite_reactions,
            candles,
            direction,
            stop_finder,
        )
    )

    accepted_initial_first_times = {
        getattr(entry["reaction"], "first_time")
        for entry in accepted_orders.values()
    }
    accepted_initial_first_times = {
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        if isinstance(value, str) else value
        for value in accepted_initial_first_times
    }
    blocked_order_first_times.difference_update(accepted_initial_first_times)
    return accepted_orders, blocked_order_first_times
```

### FUN-LIF-015 — `visible_a_zones_after_s_stops`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:visible_a_zones_after_s_stops`  
Source-Lines: 512-526  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def visible_a_zones_after_s_stops(a_zones, s_zones, candles):
    """Suppress the A candle that contains an already-confirmed S stop.

    That candle is the S-stop/E transition candle. It may still carry the
    order box's BoxBottom, but it cannot receive a new A label.
    """
    times = [getattr(item, "timestamp") for item in candles]
    stop_indices = {
        bisect_left(times, getattr(item, "decision_event_time"))
        for item in s_zones
    }
    return [
        item for item in a_zones
        if int(getattr(item, "source_index")) not in stop_indices
    ]
```

### FUN-LIF-016 — `module_priority`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:module_priority`  
Source-Lines: 528-540  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def module_priority(item):
    """Return the confirmed behavioral ownership priority.

    StopAll > E red > S red > E blue > S blue.  A is intentionally absent:
    this helper is used only after A has become an S candidate.
    """
    if hasattr(item, "stopped_behavior_type"):
        return 5
    if hasattr(item, "family"):
        return 4 if str(getattr(item, "family")).lower() == "red" else 2
    if hasattr(item, "a_source_time"):
        return 3 if str(getattr(item, "color")).lower() == "red" else 1
    return 0
```

### FUN-LIF-017 — `module_identity`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:module_identity`  
Source-Lines: 542-549  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def module_identity(item):
    return (
        type(item).__name__,
        getattr(item, "family", getattr(item, "color", None)),
        getattr(item, "number", None),
        getattr(item, "source_time"),
        getattr(item, "source_index", None),
    )
```

### FUN-LIF-018 — `module_stop_event`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:module_stop_event`  
Source-Lines: 551-563  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def module_stop_event(item, stop_event_finder=None):
    """Resolve the strict native RAW stop event of an S/E/StopAll object."""
    explicit = getattr(item, "stop_event_time", None)
    if explicit is not None:
        return explicit
    if stop_event_finder is None:
        return None
    found = stop_event_finder(item)
    if found is None:
        return None
    if isinstance(found, tuple):
        return found[-1]
    return found
```

### FUN-LIF-019 — `strictly_beyond_boundary`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:strictly_beyond_boundary`  
Source-Lines: 565-566  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def strictly_beyond_boundary(price, boundary, direction):
    return get_direction_policy(direction).strict_cross(price, boundary)
```

### FUN-LIF-020 — `dominant_module`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:dominant_module`  
Source-Lines: 568-577  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def dominant_module(modules):
    return max(
        modules,
        key=lambda item: (
            module_priority(item),
            int(getattr(item, "number", 0)),
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    )
```

### FUN-LIF-021 — `split_a_zones_by_dominant_stops`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:split_a_zones_by_dominant_stops`  
Source-Lines: 579-728  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def split_a_zones_by_dominant_stops(
    a_zones, s_zones, e_zones, stopalls, candles, direction,
    stop_event_finder=None, trend_reactions=None, confirmation_finder=None,
):
    """Separate visible A labels from A objects allowed into downstream math.

    A/Reaction/Blue discovery remains independent inside every half-leg.  Once
    an accepted S/E/StopAll is strictly stopped, however, the main candle that
    contains that stop begins the next leg comparison.  An A whose source
    extreme is strictly beyond the highest-priority stopped owner is the
    leg-start candidate, but it cannot re-enter calculation as an equal or
    smaller behavior. That candidate consumes the closed owner for subsequent
    half-leg A discovery while remaining absent from the public output.

    Equality is deliberately valid.  Stop chronology is exact at native RAW interval,
    while leg ownership is assigned to the containing main candle.
    """
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    candle_times = [getattr(item, "timestamp") for item in candles]
    modules = sorted(
        [*s_zones, *e_zones, *stopalls],
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    )
    stopped = []
    for module in modules:
        stop_event = module_stop_event(module, stop_event_finder)
        if stop_event is None:
            continue
        stop_index = bisect_right(candle_times, stop_event) - 1
        if stop_index < 0:
            continue
        stopped.append((module, stop_index, stop_event))
    stop_indices = {
        module_identity(module): stop_index
        for module, stop_index, _stop_event in stopped
    }

    valid = []
    invalid = []
    consumed = set()
    for a_zone in sorted(
        a_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ),
    ):
        source_index = int(getattr(a_zone, "source_index"))
        eligible = [
            module for module, stop_index, _stop_event in stopped
            if getattr(module, "source_time") < getattr(a_zone, "source_time")
            and stop_index <= source_index
            and module_identity(module) not in consumed
        ]
        if not eligible:
            valid.append(a_zone)
            continue
        # A historical high-priority E cannot own every later leg forever.
        # The newest main candle containing a strict stop owns the transition;
        # priority and numbering resolve only owners stopped in that candle.
        dominant = max(
            eligible,
            key=lambda item: (
                stop_indices[module_identity(item)],
                module_priority(item),
                int(getattr(item, "number", 0)),
                getattr(item, "source_time"),
                int(getattr(item, "source_index", -1)),
            ),
        )
        crosses_dominant = strictly_beyond_boundary(
            Decimal(str(getattr(a_zone, "price"))),
            Decimal(str(getattr(dominant, "price"))),
            direction,
        )
        if not crosses_dominant:
            valid.append(a_zone)
            continue

        # A confirmed trend Reaction may establish a directional leg head
        # inside the closed owner's range before this A. Preserve that A as an
        # interior-leg behavior, while retaining the existing owner
        # consumption below. This is provenance-based and uses no fixture data.
        interior = False
        if (
            trend_reactions is not None
            and confirmation_finder is not None
            and source_index > 0
            and getattr(a_zone, "reaction_first_time", None) is not None
        ):
            owner_stop = next(
                stop_event for module, stop_index, stop_event in stopped
                if module_identity(module) == module_identity(dominant)
            )
            owner_stop_index = bisect_right(candle_times, owner_stop) - 1
            first_trend_index = bisect_right(
                candle_times, getattr(a_zone, "reaction_first_time")
            ) - 1
            if 0 <= owner_stop_index <= first_trend_index < len(candles):
                extreme_name = "low" if direction == "bullish" else "high"
                head = (
                    min(
                        candles[owner_stop_index:first_trend_index + 1],
                        key=lambda candle: Decimal(str(getattr(candle, extreme_name))),
                    )
                    if direction == "bullish"
                    else max(
                        candles[owner_stop_index:first_trend_index + 1],
                        key=lambda candle: Decimal(str(getattr(candle, extreme_name))),
                    )
                )
                head_extreme = Decimal(str(getattr(head, extreme_name)))
                a_extreme = Decimal(str(getattr(a_zone, "price")))
                if (
                    int(getattr(head, "index", -1)) < source_index
                    and (
                        head_extreme < a_extreme
                        if direction == "bullish"
                        else head_extreme > a_extreme
                    )
                ):
                    interior = any(
                        int(getattr(reaction, "first_idx"))
                        >= int(getattr(head, "index"))
                        and int(getattr(reaction, "first_idx"))
                        <= first_trend_index
                        and int(getattr(reaction, "break_idx")) < source_index
                        and confirmation_finder(reaction, direction)
                        < getattr(a_zone, "source_time")
                        for reaction in trend_reactions
                    )
        if interior:
            valid.append(a_zone)
            # Continue into the common consumption logic below.
            dominant_priority = module_priority(dominant)
            for module in eligible:
                if module_priority(module) <= dominant_priority:
                    consumed.add(module_identity(module))
            continue

        invalid.append(a_zone)
        dominant_priority = module_priority(dominant)
        for module in eligible:
            if module_priority(module) <= dominant_priority:
                consumed.add(module_identity(module))
    return valid, invalid
```

### FUN-LIF-022 — `blocked_orders_while_invalid_leg_heads_are_live`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:blocked_orders_while_invalid_leg_heads_are_live`  
Source-Lines: 730-750  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def blocked_orders_while_invalid_leg_heads_are_live(
    invalid_a_zones, opposite_reactions, candles, direction, stop_finder,
):
    """Return order First times owned by a still-live invalid leg head.

    A strict dominant-boundary crossing can expose a new leg head without
    making its A calculation-valid. Until that head itself stops, an internal
    opposite Reaction cannot take over the larger owner's resumed E space.
    """
    blocked = set()
    for a_zone in invalid_a_zones:
        stop = stop_finder(a_zone)
        if stop is None:
            continue
        stop_event = stop[2]
        source_time = getattr(a_zone, "source_time")
        for reaction in opposite_reactions:
            first_time = getattr(candles[int(getattr(reaction, "first_idx"))], "timestamp")
            if source_time <= first_time < stop_event:
                blocked.add(first_time)
    return blocked
```

### FUN-LIF-023 — `s_zones_for_module_engines`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:s_zones_for_module_engines`  
Source-Lines: 752-775  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def s_zones_for_module_engines(s_zones, e_zones, direction):
    """Preserve the established S eligibility contract consumed by E/StopAll."""
    ordered_e = sorted(e_zones, key=lambda item: getattr(item, "source_time"))
    visible = []
    for s_zone in sorted(s_zones, key=lambda item: getattr(item, "source_time")):
        prior_modules = [
            item for item in [*ordered_e, *visible]
            if getattr(item, "source_time") < getattr(s_zone, "source_time")
        ]
        if prior_modules:
            prior = max(prior_modules, key=lambda item: getattr(item, "source_time"))
            if getattr(s_zone, "a_source_time") < getattr(prior, "source_time"):
                continue
            boundary = Decimal(str(getattr(prior, "price")))
            if strictly_beyond_boundary(
                Decimal(str(getattr(s_zone, "a_price"))), boundary, direction
            ):
                continue
            if strictly_beyond_boundary(
                Decimal(str(getattr(s_zone, "price"))), boundary, direction
            ):
                continue
        visible.append(s_zone)
    return visible
```

### FUN-LIF-024 — `visible_s_zones_after_module_resets`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:visible_s_zones_after_module_resets`  
Source-Lines: 777-944  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def visible_s_zones_after_module_resets(
    s_zones, e_zones, direction, stop_event_finder=None, source_event_finder=None,
    candles=None,
):
    """Apply dominant-behavior ownership to successive S candidates.

    Bullish/bearish half-leg calculations remain active under a larger
    behavior.  But once the currently dominant S/E/StopAll and the candidate
    S's parent A have both stopped, that A belongs to the next larger module
    lifecycle.  The would-be S is therefore consumed, while its historical
    inputs remain available for chart rendering and audits.
    """
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    ordered_external = sorted(
        e_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    )
    visible = []
    consumed = set()
    for s_zone in sorted(
        s_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    ):
        a_stop_event = getattr(s_zone, "a_stop_event_time", None)
        ownership_event = a_stop_event
        if direction in {"bullish", "bearish"}:
            # The larger head may stop while the internal S search is open,
            # after A stops but before the candidate's own extreme forms.
            # A later stop after that extreme must not rewrite its ownership.
            ownership_event = (
                source_event_finder(s_zone) if source_event_finder is not None
                else getattr(s_zone, "source_time")
            )
        prior_modules = [
            item for item in [*ordered_external, *visible]
            if getattr(item, "source_time") < getattr(s_zone, "source_time")
            and module_identity(item) not in consumed
        ]
        # A newer E/StopAll source begins the current larger-module lifecycle.
        # Stops belonging to modules sourced before that owner are historical
        # and cannot suppress nested S candidates in the newer lifecycle.
        prior_external = [
            item for item in ordered_external
            if getattr(item, "source_time") < getattr(s_zone, "source_time")
        ]
        if prior_external:
            current_external = max(
                prior_external,
                key=lambda item: (
                    getattr(item, "source_time"),
                    int(getattr(item, "source_index", -1)),
                ),
            )
            lifecycle_start = getattr(current_external, "source_time")
            prior_modules = [
                item for item in prior_modules
                if getattr(item, "source_time") >= lifecycle_start
            ]
        if prior_modules and ownership_event is not None:
            stopped_prior = [
                module for module in prior_modules
                if (
                    module_stop := module_stop_event(module, stop_event_finder)
                ) is not None
                and module_stop <= ownership_event
            ]
            if stopped_prior:
                # A lower-priority S may not re-form inside the next lifecycle
                # of the most recent stopped larger module.  Use the latest
                # stopped E/StopAll owner for this continuation-boundary test;
                # do not let an older, higher-priority historical module steal
                # ownership from the current lifecycle.
                stopped_external = [
                    module for module in stopped_prior
                    if not hasattr(module, "a_source_time")
                ]
                if candles is not None and stopped_external:
                    latest_external = max(
                        stopped_external,
                        key=lambda item: (
                            getattr(item, "source_time"),
                            int(getattr(item, "source_index", -1)),
                        ),
                    )
                    if module_priority(s_zone) < module_priority(latest_external):
                        larger_stop = module_stop_event(
                            latest_external, stop_event_finder
                        )
                        if larger_stop is not None:
                            candle_times = [
                                getattr(candle, "timestamp") for candle in candles
                            ]
                            stop_index = bisect_right(candle_times, larger_stop) - 1
                            source_index = int(getattr(s_zone, "source_index"))
                            if (
                                0 <= stop_index < len(candles)
                                and 0 <= source_index < len(candles)
                            ):
                                stop_close = Decimal(str(
                                    getattr(candles[stop_index], "close")
                                ))
                                source_close = Decimal(str(
                                    getattr(candles[source_index], "close")
                                ))
                                if strictly_beyond_boundary(
                                    source_close, stop_close, direction
                                ):
                                    continue

                # Lifecycle ownership is chronological first.  An old
                # high-priority StopAll/E must not steal the transition from
                # the behavior that stopped most recently before this source.
                # Priority/number only resolve a true same-stop-event tie.
                dominant = max(
                    stopped_prior,
                    key=lambda item: (
                        module_stop_event(item, stop_event_finder),
                        module_priority(item),
                        int(getattr(item, "number", 0)),
                        getattr(item, "source_time"),
                        int(getattr(item, "source_index", -1)),
                    ),
                )
                # A newly confirmed higher-priority S family supersedes a
                # stopped lower-priority owner.  In particular, a Red S must
                # remain visible after a stopped Blue S when its own strict
                # directional extreme is reached.  The existing price/stop
                # consumption rule still applies when the candidate priority
                # is equal or lower, preserving the established lifecycle.
                if (
                    hasattr(s_zone, "a_source_time")
                    and hasattr(dominant, "a_source_time")
                    and module_priority(s_zone) > module_priority(dominant)
                ):
                    visible.append(s_zone)
                    continue
                # A stopped owner advances the lifecycle only when the new S
                # is itself the strict directional extreme of that leg.
                # Equality belongs to the earlier owner and remains valid.
                if not strictly_beyond_boundary(
                    Decimal(str(getattr(s_zone, "price"))),
                    Decimal(str(getattr(dominant, "price"))),
                    direction,
                ):
                    visible.append(s_zone)
                    continue
                # All lower/equal stopped owners involved in this transition
                # leave subsequent calculation ownership together.  The
                # highest-priority object determines the next module number.
                dominant_priority = module_priority(dominant)
                for module in stopped_prior:
                    module_stop = module_stop_event(module, stop_event_finder)
                    if (
                        module_priority(module) <= dominant_priority
                    ):
                        consumed.add(module_identity(module))
                continue
        # An active larger behavior does not disable the independent A/S
        # lifecycle inside the current half-leg.
        visible.append(s_zone)
    return visible
```

### FUN-LIF-025 — `reconcile_stopall_lifecycle`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:reconcile_stopall_lifecycle`  
Source-Lines: 946-978  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def reconcile_stopall_lifecycle(
    detector, s_zones, e_zones, chronology, direction, timed_step=None
):
    """Feed accepted reset boundaries back into authoritative E ownership.

    Geometry and eligible orders remain owned by E. Reconcile until both
    stages agree; a cycle is an error, never a partially corrected payload.
    """
    seen = set()
    pass_number = 1
    measure = timed_step or (lambda _label, work: work())
    while True:
        visible_s = measure(
            f"Reconcile S visibility - {direction.title()} - pass {pass_number}",
            lambda: s_zones_for_module_engines(s_zones, e_zones, direction),
        )
        stopalls = measure(
            f"StopAll - {direction.title()} - pass {pass_number}",
            lambda: detect_stopalls(direction, visible_s, e_zones, chronology),
        )
        resets = {item.source_time: item.number for item in stopalls}
        if resets == detector.sequence_resets:
            return e_zones, stopalls
        identity = tuple(sorted(resets.items()))
        if identity in seen:
            raise ValueError("E/StopAll lifecycle reconciliation did not converge")
        seen.add(identity)
        detector.sequence_resets = resets
        e_zones = measure(
            f"E - {direction.title()} - StopAll reconciliation {pass_number}",
            detector.detect,
        )
        pass_number += 1
```

### FUN-LIF-026 — `visible_a_zones_after_module_boundaries`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:visible_a_zones_after_module_boundaries`  
Source-Lines: 980-1025  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def visible_a_zones_after_module_boundaries(
    a_zones, s_zones, e_zones, direction, stop_event_finder=None,
):
    """Require A provenance to rebuild after the dominant strict stop.

    A price is deliberately not compared with the old module price.  Reactions
    and Blue Lines remain valid inside every half-leg; only provenance that
    straddles the dominant stop belongs to the closed lifecycle.
    """
    del direction  # Exact-stop ownership is directionally mirrored.
    modules = sorted(
        [*s_zones, *e_zones],
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ),
    )
    valid = []
    for a_zone in sorted(
        a_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ),
    ):
        stopped_prior = [
            module for module in modules
            if getattr(module, "source_time") <= getattr(a_zone, "source_time")
            and (
                stop_event := module_stop_event(module, stop_event_finder)
            ) is not None
            and stop_event <= getattr(a_zone, "source_time")
        ]
        if stopped_prior:
            dominant = dominant_module(stopped_prior)
            boundary_event = module_stop_event(dominant, stop_event_finder)
            provenance_times = (
                getattr(a_zone, "blue_1_source_time"),
                getattr(a_zone, "blue_2_source_time"),
                getattr(a_zone, "continuation_source_time"),
                getattr(a_zone, "reaction_first_time"),
            )
            if min(provenance_times) < boundary_event:
                continue
        valid.append(a_zone)
    return valid
```

### FUN-LIF-027 — `reaction_number_is_internal`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:reaction_number_is_internal`  
Source-Lines: 1027-1039  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def reaction_number_is_internal(items, number, identities):
    """Return whether a numbered Reaction resolves to a protected internal owner."""
    if number is None:
        return False
    number = int(number)
    if number < 1 or number > len(items):
        return False
    reaction = items[number - 1]
    identity = (
        int(getattr(reaction, "first_idx")),
        int(getattr(reaction, "break_idx")),
    )
    return identity in identities
```

### FUN-LIF-028 — `order_identity_is_internal`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:order_identity_is_internal`  
Source-Lines: 1042-1048  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def order_identity_is_internal(item, internal_identities):
    """Return whether a behavior's physical Order Reaction is internal."""
    first_index = getattr(item, "order_first_index", None)
    break_index = getattr(item, "order_break_index", None)
    if first_index is None or break_index is None:
        return False
    return (int(first_index), int(break_index)) in internal_identities
```

### FUN-LIF-029 — `point_is_inside_healthy_reaction`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:point_is_inside_healthy_reaction`  
Source-Lines: 1051-1071  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def point_is_inside_healthy_reaction(source_time, price, reactions):
    """Return True only for a strict protected Reaction interior.

    First and published box edges are ownership boundaries, so equality and
    the First timestamp itself remain eligible.
    """
    if source_time is None or price is None:
        return False
    value = _decimal(price)
    for reaction in reactions:
        first = getattr(reaction, "behavior_first_time", None)
        confirmed = getattr(reaction, "behavior_confirmation_time", None)
        if first is None or confirmed is None:
            continue
        if source_time <= first or source_time > confirmed:
            continue
        bottom = _decimal(getattr(reaction, "behavior_public_box_bottom"))
        top = _decimal(getattr(reaction, "behavior_public_box_top"))
        if bottom < value < top:
            return True
    return False
```

### FUN-LIF-030 — `forbidden_internal_order_b`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:forbidden_internal_order_b`  
Source-Lines: 1074-1085  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def forbidden_internal_order_b(item, internal_identities):
    """Reject only an internal Reset-leg Order_B owner.

    Direct parent-stop and carried-live Orders keep their own lifecycle rules.
    """
    if not order_identity_is_internal(item, internal_identities):
        return False
    causes = {str(value) for value in getattr(item, "order_causes", ())}
    return (
        "reset-leg" in causes
        or getattr(item, "order_reset_leg_reset_time", None) is not None
    )
```

### FUN-LIF-031 — `_is_advanced_blue_s`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:_is_advanced_blue_s`  
Source-Lines: 1088-1092  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _is_advanced_blue_s(item):
    return (
        str(getattr(item, "color", "")).lower() == "blue"
        and str(getattr(item, "formation_type", "")).lower() == "advanced"
    )
```

### FUN-LIF-032 — `filter_internal_behavior_outputs`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:filter_internal_behavior_outputs`  
Source-Lines: 1095-1152  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def filter_internal_behavior_outputs(
    a_zones,
    s_zones,
    e_zones,
    stopalls,
    opposite_reactions,
    opposite_internal_identities,
    all_behavior_reactions,
):
    """Apply the final non-fallback Internal-Reaction ownership veto.

    Detector state is preserved. Only public/calculation outputs that violate
    the protected-interior contract are removed, with the established
    S-Blue-Advanced evidence exception kept intact.
    """
    visible_a = [
        item for item in a_zones
        if not point_is_inside_healthy_reaction(
            getattr(item, "source_time", None),
            getattr(item, "price", None),
            all_behavior_reactions,
        )
    ]
    visible_s = [
        item for item in s_zones
        if (
            _is_advanced_blue_s(item)
            or not point_is_inside_healthy_reaction(
                getattr(item, "source_time", None),
                getattr(item, "price", None),
                all_behavior_reactions,
            )
        )
        and not reaction_number_is_internal(
            opposite_reactions,
            getattr(item, "reset_reaction_number", None),
            opposite_internal_identities,
        )
    ]
    visible_e = [
        item for item in e_zones
        if not point_is_inside_healthy_reaction(
            getattr(item, "source_time", None),
            getattr(item, "price", None),
            all_behavior_reactions,
        )
        and not forbidden_internal_order_b(item, opposite_internal_identities)
    ]
    visible_stopalls = [
        item for item in stopalls
        if not point_is_inside_healthy_reaction(
            getattr(item, "source_time", None),
            getattr(item, "price", None),
            all_behavior_reactions,
        )
        and not forbidden_internal_order_b(item, opposite_internal_identities)
    ]
    return visible_a, visible_s, visible_e, visible_stopalls
```

### FUN-LIF-033 — `finalize_behavior_visibility`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:finalize_behavior_visibility`  
Source-Lines: 1154-1246  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def finalize_behavior_visibility(
    a_zones,
    s_zones,
    e_zones,
    stopalls,
    direction,
    invalid_s_identities,
    stop_event_finder,
    source_event_finder,
    candles,
    *,
    all_a_zones=None,
):
    """Resolve the final A/S/E lineage closure after StopAll reconciliation."""
    stopall_source_indices = {int(item.source_index) for item in stopalls}
    final_e_zones = [
        item for item in e_zones
        if int(getattr(item, "source_index")) not in stopall_source_indices
    ]
    e_source_indices = {
        int(getattr(item, "source_index")) for item in final_e_zones
    }
    final_s_zones = visible_s_zones_after_module_resets(
        s_zones,
        [*final_e_zones, *stopalls],
        direction,
        stop_event_finder,
        source_event_finder=source_event_finder,
        candles=candles,
    )

    # Presentation is a lineage closure over accepted calculations. If a final
    # E references an S parent, retain that historical S even if it no longer
    # owns downstream lifecycle calculation.
    referenced_s_sources = {
        getattr(item, "parent_source_time")
        for item in final_e_zones
        if str(getattr(item, "parent_type", "")).upper() == "S"
    }
    final_s_identities = {module_identity(item) for item in final_s_zones}
    final_s_zones.extend(
        item for item in s_zones
        if getattr(item, "source_time") in referenced_s_sources
        and module_identity(item) not in final_s_identities
    )
    final_s_zones.sort(
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        )
    )

    final_a_zones = visible_a_zones_after_module_boundaries(
        a_zones,
        final_s_zones,
        [*final_e_zones, *stopalls],
        direction,
        stop_event_finder,
    )
    referenced_a_sources = {getattr(item, "a_source_time") for item in final_s_zones}
    lineage_a_zones = a_zones if all_a_zones is None else all_a_zones
    final_a_identities = {
        (getattr(item, "source_time"), int(getattr(item, "source_index")))
        for item in final_a_zones
    }
    final_a_zones.extend(
        item for item in lineage_a_zones
        if getattr(item, "source_time") in referenced_a_sources
        and (
            getattr(item, "source_time"), int(getattr(item, "source_index"))
        ) not in final_a_identities
    )
    final_a_zones.sort(
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        )
    )

    occupied = e_source_indices | stopall_source_indices
    final_a_zones = [
        item for item in final_a_zones
        if int(getattr(item, "source_index")) not in occupied
    ]
    final_s_zones = [
        item for item in final_s_zones
        if int(getattr(item, "source_index")) not in occupied
        and (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ) not in invalid_s_identities
    ]
    return final_e_zones, final_s_zones, final_a_zones
```

### FUN-LIF-034 — `visible_a_zones`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `lifecycle_engine.py:visible_a_zones`  
Source-Lines: 1249-1255  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def visible_a_zones(a_zones: Sequence[object], s_zones: Sequence[object]) -> list[object]:
    """Return A objects whose source candle is not occupied by a final S."""
    occupied = {int(getattr(item, "source_index")) for item in s_zones}
    return [
        item for item in a_zones
        if int(getattr(item, "source_index")) not in occupied
    ]
```

### FUN-REA-001 — `classify_candle_color`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:classify_candle_color`  
Source-Lines: 89-91  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def classify_candle_color(open_price: Decimal, close_price: Decimal) -> str:
    """Match Lightweight Charts: Open <= Close is an up/green candle."""
    return "GREEN" if open_price <= close_price else "RED"
```

### FUN-REA-002 — `opposite_direction`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:opposite_direction`  
Source-Lines: 94-100  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def opposite_direction(direction: str) -> str:
    """Return the exact Bullish/Bearish mirror direction."""
    if direction == "bullish":
        return "bearish"
    if direction == "bearish":
        return "bullish"
    raise ValueError("Direction must be 'bullish' or 'bearish'.")
```

### FUN-REA-003 — `DetectorBase.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:DetectorBase.__init__`  
Source-Lines: 104-126  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(
        self,
        candles: Sequence[Candle],
        raw_candles: Sequence[Candle],
        start_index: int,
        end_index: int,
    ) -> None:
        self.candles = candles
        self.raw_candles = raw_candles
        self.start_index = start_index
        self.end_index = end_index
        self.main_times = self._shared_time_index(candles)
        self.raw_times = self._shared_time_index(raw_candles)
        self.lower_index = shared_lower_timeframe_index(raw_candles)
        self._reaction_break_index_cache: dict[str, tuple[int, list[int]]] = {}

        if len(candles) > 1:
            self.timeframe = candles[1].timestamp - candles[0].timestamp
        else:
            self.timeframe = timedelta(seconds=1)

        if self.timeframe.total_seconds() <= 0:
            raise ValueError("Main timeframe must be positive.")
```

### FUN-REA-004 — `DetectorBase._shared_time_index`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:DetectorBase._shared_time_index`  
Source-Lines: 129-137  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _shared_time_index(candles: Sequence[Candle]) -> list[datetime]:
        """Build one immutable-source timestamp index per calculation process."""
        key = id(candles)
        cached = _SEQUENCE_TIME_INDEXES.get(key)
        if cached is not None and cached[0] is candles:
            return cached[1]
        times = [candle.timestamp for candle in candles]
        _SEQUENCE_TIME_INDEXES[key] = (candles, times)
        return times
```

### FUN-REA-005 — `DetectorBase.raw_between`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:DetectorBase.raw_between`  
Source-Lines: 139-142  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def raw_between(self, start: datetime, end: datetime) -> Iterable[Candle]:
        left = bisect.bisect_left(self.raw_times, start)
        right = bisect.bisect_left(self.raw_times, end)
        return (self.raw_candles[index] for index in range(left, right))
```

### FUN-REA-006 — `DetectorBase.main_source_for_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:DetectorBase.main_source_for_time`  
Source-Lines: 144-155  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def main_source_for_time(self, timestamp: datetime) -> Candle | None:
        position = bisect.bisect_right(self.main_times, timestamp) - 1
        if position < self.start_index or position > self.end_index:
            return None
        end = (
            self.candles[position + 1].timestamp
            if position + 1 < len(self.candles)
            else self.candles[position].timestamp + self.timeframe
        )
        if timestamp < end:
            return self.candles[position]
        return None
```

### FUN-REA-007 — `DetectorBase.minimum_low`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:DetectorBase.minimum_low`  
Source-Lines: 157-164  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def minimum_low(self, start_index: int, end_index: int) -> tuple[Decimal, Candle]:
        source = self.candles[start_index]
        candles = self.candles
        for index in range(start_index + 1, end_index + 1):
            candle = candles[index]
            if candle.low < source.low:
                source = candle
        return source.low, source
```

### FUN-REA-008 — `DetectorBase.maximum_high`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:DetectorBase.maximum_high`  
Source-Lines: 166-173  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def maximum_high(self, start_index: int, end_index: int) -> tuple[Decimal, Candle]:
        source = self.candles[start_index]
        candles = self.candles
        for index in range(start_index + 1, end_index + 1):
            candle = candles[index]
            if candle.high > source.high:
                source = candle
        return source.high, source
```

### FUN-REA-009 — `BullishDetector._is_context_color`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BullishDetector._is_context_color`  
Source-Lines: 185-186  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _is_context_color(self, candle: Candle) -> bool:
        return candle.tag == self.context_color
```

### FUN-REA-010 — `BullishDetector._is_first_color`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BullishDetector._is_first_color`  
Source-Lines: 188-189  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _is_first_color(self, candle: Candle) -> bool:
        return candle.tag == self.first_color
```

### FUN-REA-011 — `BullishDetector.green_run_peak_before`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BullishDetector.green_run_peak_before`  
Source-Lines: 191-202  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def green_run_peak_before(self, first_red_index: int) -> tuple[Decimal, Candle]:
        run_end = first_red_index - 1
        if run_end < self.start_index or not self._is_context_color(self.candles[run_end]):
            raise ValueError(
                f"Mode-A first-color candle must immediately follow "
                f"a {self.context_color} context candle."
            )

        run_start = run_end
        while run_start > self.start_index and self._is_context_color(self.candles[run_start - 1]):
            run_start -= 1
        return self.maximum_high(run_start, run_end)
```

### FUN-REA-012 — `BullishDetector.breakout_analysis`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BullishDetector.breakout_analysis`  
Source-Lines: 204-228  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def breakout_analysis(
        self, candidate: Candidate, breakout_candle: Candle
    ) -> IntrabarAnalysis | None:
        start_index = (
            candidate.box_top_source_idx + 1
            if candidate.box_top_source_idx < candidate.first_idx
            else candidate.box_top_source_idx
        )
        start = candidate.intrabar_start or self.candles[start_index].timestamp
        end = breakout_candle.timestamp + self.timeframe
        left = bisect.bisect_left(self.raw_times, start)
        right = bisect.bisect_left(self.raw_times, end)
        crossing = self.lower_index.first_greater(left, right, candidate.box_top)
        if crossing is None:
            return None
        minimum_low, minimum_position = self.lower_index.range_minimum(
            left, crossing + 1
        )
        minimum_time = self.raw_times[minimum_position]
        source = self.main_source_for_time(minimum_time)
        if source is None:
            return None
        return IntrabarAnalysis(
            self.raw_candles[crossing], minimum_low, source
        )
```

### FUN-REA-013 — `BullishDetector.mode_a_invalidation_before_breakout`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BullishDetector.mode_a_invalidation_before_breakout`  
Source-Lines: 230-264  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def mode_a_invalidation_before_breakout(
        self, candidate: Candidate, candle: Candle
    ) -> bool:
        # A Mode-A candidate belongs to the complete leg that opened at the
        # analysis/Reset boundary. Later lower first-color candles are internal
        # BoxBottom updates; only a strict break of the frozen leg floor can
        # invalidate the candidate before its BoxTop breaks.
        invalidation_level = (
            candidate.anchor_value
            if candidate.anchor_value is not None
            else candidate.leg_boundary_value
        )
        if invalidation_level is None:
            return False
        if candle.low >= invalidation_level:
            return False
        if candle.high <= candidate.box_top:
            return True

        end = candle.timestamp + self.timeframe
        left = bisect.bisect_left(self.raw_times, candle.timestamp)
        right = bisect.bisect_left(self.raw_times, end)
        invalidation = self.lower_index.first_less(
            left, right, invalidation_level
        )
        breakout = self.lower_index.first_greater(
            left, right, candidate.box_top
        )
        if invalidation is None:
            return breakout is None
        if breakout is None:
            return True
        # The legacy loop checks Low first inside one lower-timeframe candle,
        # so invalidation wins a true same-second tie.
        return invalidation <= breakout
```

### FUN-REA-014 — `BullishDetector.confirmed_reset_before_breakout`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BullishDetector.confirmed_reset_before_breakout`  
Source-Lines: 266-284  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def confirmed_reset_before_breakout(
        self, candidate: Candidate | None, candle: Candle, confirmed_bottom: Decimal
    ) -> bool:
        if candidate is None or candle.high <= candidate.box_top:
            return True

        end = candle.timestamp + self.timeframe
        left = bisect.bisect_left(self.raw_times, candle.timestamp)
        right = bisect.bisect_left(self.raw_times, end)
        reset = self.lower_index.first_less(left, right, confirmed_bottom)
        breakout = self.lower_index.first_greater(
            left, right, candidate.box_top
        )
        if reset is None:
            return breakout is None
        if breakout is None:
            return True
        # Reset is checked before breakout within one lower-timeframe candle.
        return reset <= breakout
```

### FUN-REA-015 — `BullishDetector.post_breakout_reset`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BullishDetector.post_breakout_reset`  
Source-Lines: 286-299  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def post_breakout_reset(
        self,
        analysis: IntrabarAnalysis | None,
        box_bottom: Decimal,
        breakout_candle: Candle,
    ) -> Candle | None:
        if analysis is None:
            return None
        start = analysis.event_second.timestamp + timedelta(microseconds=1)
        end = breakout_candle.timestamp + self.timeframe
        left = bisect.bisect_left(self.raw_times, start)
        right = bisect.bisect_left(self.raw_times, end)
        position = self.lower_index.first_less(left, right, box_bottom)
        return None if position is None else self.raw_candles[position]
```

### FUN-REA-016 — `BullishDetector.detect`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BullishDetector.detect`  
Source-Lines: 301-576  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect(self, *, first_only: bool = False) -> DetectionResult:
        reactions: list[Candidate] = []
        resets: list[ResetEvent] = []
        mode = "A"
        state = "SCANNING"
        last_confirmed_bottom: Decimal | None = None
        last_confirmed_first_idx: int | None = None
        running_peak: Decimal | None = None
        running_peak_src: int | None = None
        leg_open_low: Decimal | None = None
        leg_just_started = True
        anchor_red: Candle | None = None
        anchor_red_origin: str | None = None
        reset_context: Candle | None = None
        candidate: Candidate | None = None

        for index in range(self.start_index, self.end_index + 1):
            candle = self.candles[index]
            reset_detected = (
                last_confirmed_bottom is not None and candle.low < last_confirmed_bottom
            )
            reset_occurs_first = reset_detected
            if reset_detected and state == "WAITING":
                reset_occurs_first = self.confirmed_reset_before_breakout(
                    candidate, candle, last_confirmed_bottom
                )

            if reset_occurs_first:
                resets.append(
                    ResetEvent(
                        index=candle.index,
                        display_time=candle.display_time,
                        second_time=None,
                        broken_level=last_confirmed_bottom,
                        from_first_idx=last_confirmed_first_idx,
                    )
                )
                candidate = None
                last_confirmed_bottom = None
                last_confirmed_first_idx = None
                running_peak = None
                running_peak_src = None
                mode = "A"
                state = "SCANNING"
                leg_open_low = None
                leg_just_started = True
                anchor_red = candle if self._is_first_color(candle) else None
                anchor_red_origin = "reset" if self._is_first_color(candle) else None
                reset_context = candle
                continue

            if state == "WAITING":
                assert candidate is not None

                if (
                    candidate.mode == "A"
                    and self.mode_a_invalidation_before_breakout(candidate, candle)
                ):
                    candidate = None
                    state = "SCANNING"
                    anchor_red = candle if self._is_first_color(candle) else None
                    anchor_red_origin = (
                        "candidate_invalidation" if self._is_first_color(candle) else None
                    )
                    continue

                if candle.low < candidate.box_bottom:
                    candidate.box_bottom = candle.low
                    candidate.box_bottom_source_idx = candle.index
                    candidate.box_bottom_source_time = candle.display_time

                if candle.high > candidate.box_top:
                    candidate.break_idx = candle.index
                    candidate.break_time = candle.display_time
                    analysis = self.breakout_analysis(candidate, candle)

                    if (
                        candidate.box_bottom_source_idx == candle.index
                        and analysis is not None
                    ):
                        candidate.box_bottom = analysis.extreme
                        candidate.box_bottom_source_idx = analysis.extreme_source.index
                        candidate.box_bottom_source_time = (
                            analysis.extreme_source.display_time
                        )

                    confirmed = replace(candidate)
                    reactions.append(confirmed)
                    if first_only:
                        return DetectionResult(
                            direction="bullish",
                            reactions=reactions,
                            resets=resets,
                            start_index=self.start_index,
                            end_index=self.end_index,
                        )
                    last_confirmed_bottom = confirmed.box_bottom
                    last_confirmed_first_idx = confirmed.first_idx
                    running_peak = candle.high
                    running_peak_src = candle.index
                    mode = "B"
                    state = "SCANNING"
                    candidate = None

                    reset_second = self.post_breakout_reset(
                        analysis, last_confirmed_bottom, candle
                    )
                    if reset_second is not None:
                        resets.append(
                            ResetEvent(
                                index=candle.index,
                                display_time=candle.display_time,
                                second_time=reset_second.display_time,
                                broken_level=last_confirmed_bottom,
                                from_first_idx=last_confirmed_first_idx,
                            )
                        )
                        last_confirmed_bottom = None
                        last_confirmed_first_idx = None
                        running_peak = None
                        running_peak_src = None
                        mode = "A"
                        state = "SCANNING"
                        leg_open_low = None
                        leg_just_started = True
                        anchor_red = candle if self._is_first_color(candle) else None
                        anchor_red_origin = "reset" if self._is_first_color(candle) else None
                        reset_context = candle
                        continue

                    if self._is_first_color(candle):
                        candidate = Candidate(
                            first_idx=candle.index,
                            first_time=candle.display_time,
                            box_top_source_idx=candle.index,
                            box_top_source_time=candle.display_time,
                            box_top=running_peak,
                            box_bottom_source_idx=candle.index,
                            box_bottom_source_time=candle.display_time,
                            box_bottom=candle.low,
                            mode="B",
                        )
                        state = "WAITING"
                continue

            if mode == "A":
                if leg_just_started:
                    leg_open_low = candle.low
                    leg_just_started = False
                    previous_reset = reset_context
                    reset_context = None
                    if self._is_first_color(candle):
                        if (
                            previous_reset is not None
                            and self._is_context_color(previous_reset)
                            and candle.low >= previous_reset.low
                        ):
                            green_high, green_source = self.green_run_peak_before(
                                candle.index
                            )
                            if green_high >= candle.high:
                                box_top = green_high
                                box_top_source = green_source
                            else:
                                box_top = candle.high
                                box_top_source = candle
                            candidate = Candidate(
                                first_idx=candle.index,
                                first_time=candle.display_time,
                                box_top_source_idx=box_top_source.index,
                                box_top_source_time=box_top_source.display_time,
                                box_top=box_top,
                                box_bottom_source_idx=candle.index,
                                box_bottom_source_time=candle.display_time,
                                box_bottom=candle.low,
                                mode="A",
                                leg_boundary_value=leg_open_low,
                            )
                            state = "WAITING"
                        else:
                            anchor_red = candle
                            anchor_red_origin = "leg_open"
                    continue

                previous = self.candles[index - 1]
                passes = False
                box_top: Decimal | None = None
                box_top_source: Candle | None = None

                if self._is_context_color(previous) and self._is_first_color(candle):
                    if (
                        anchor_red is not None
                        and anchor_red_origin == "candidate_invalidation"
                        and previous.low < anchor_red.low
                        and candle.low < anchor_red.low
                    ):
                        anchor_red = None
                        anchor_red_origin = None

                    if anchor_red is not None:
                        passes = candle.low >= anchor_red.low
                    elif candle.low >= previous.low or candle.low >= leg_open_low:
                        passes = True

                    if passes:
                        green_high, green_source = self.green_run_peak_before(candle.index)
                        if green_high >= candle.high:
                            box_top = green_high
                            box_top_source = green_source
                        else:
                            box_top = candle.high
                            box_top_source = candle

                if passes:
                    assert box_top is not None and box_top_source is not None
                    candidate = Candidate(
                        first_idx=candle.index,
                        first_time=candle.display_time,
                        box_top_source_idx=box_top_source.index,
                        box_top_source_time=box_top_source.display_time,
                        box_top=box_top,
                        box_bottom_source_idx=candle.index,
                        box_bottom_source_time=candle.display_time,
                        box_bottom=candle.low,
                        mode="A",
                        anchor_idx=anchor_red.index if anchor_red else None,
                        anchor_value=anchor_red.low if anchor_red else None,
                        leg_boundary_value=leg_open_low,
                    )
                    state = "WAITING"
                elif self._is_first_color(candle):
                    anchor_red = candle
                    anchor_red_origin = "scan"
                elif not self._is_context_color(candle) and not self._is_first_color(candle):
                    anchor_red = None
                    anchor_red_origin = None
            else:
                if self._is_first_color(candle):
                    box_top = candle.high
                    box_top_source_idx = candle.index
                    if running_peak is not None and running_peak >= box_top:
                        box_top = running_peak
                        box_top_source_idx = running_peak_src

                    bottom_start = (
                        box_top_source_idx + 1
                        if box_top_source_idx < candle.index
                        else candle.index
                    )
                    bottom, bottom_source = self.minimum_low(bottom_start, candle.index)
                    candidate = Candidate(
                        first_idx=candle.index,
                        first_time=candle.display_time,
                        box_top_source_idx=box_top_source_idx,
                        box_top_source_time=self.candles[
                            box_top_source_idx
                        ].display_time,
                        box_top=box_top,
                        box_bottom_source_idx=bottom_source.index,
                        box_bottom_source_time=bottom_source.display_time,
                        box_bottom=bottom,
                        mode="B",
                    )
                    state = "WAITING"

                if running_peak is None or candle.high > running_peak:
                    running_peak = candle.high
                    running_peak_src = candle.index

        return DetectionResult(
            direction="bullish",
            reactions=reactions,
            resets=resets,
            start_index=self.start_index,
            end_index=self.end_index,
        )
```

### FUN-REA-017 — `mirror_candle`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:mirror_candle`  
Source-Lines: 579-596  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def mirror_candle(candle: Candle) -> Candle:
    """Reflect OHLC geometry while preserving the true market candle color.

    Candle.tag is market truth and is never directionally recolored. In
    particular, Open == Close is GREEN everywhere. BearishDetector swaps the
    context/first *roles* used by the shared Reaction state machine instead of
    mutating GREEN/RED tags.
    """
    return Candle(
        index=candle.index,
        timestamp=candle.timestamp,
        display_time=candle.display_time,
        tag=candle.tag,
        open=candle.open.copy_negate(),
        high=candle.low.copy_negate(),
        low=candle.high.copy_negate(),
        close=candle.close.copy_negate(),
    )
```

### FUN-REA-018 — `mirror_candidate`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:mirror_candidate`  
Source-Lines: 599-616  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def mirror_candidate(candidate: Candidate | None) -> Candidate | None:
    """Mirror geometry while preserving invariant dynamic gate state."""
    if candidate is None:
        return None
    mirrored = replace(
        candidate,
        box_top=candidate.box_bottom.copy_negate(),
        box_bottom=candidate.box_top.copy_negate(),
        box_top_source_idx=candidate.box_bottom_source_idx,
        box_top_source_time=candidate.box_bottom_source_time,
        box_bottom_source_idx=candidate.box_top_source_idx,
        box_bottom_source_time=candidate.box_top_source_time,
        anchor_value=(candidate.anchor_value.copy_negate()
                      if candidate.anchor_value is not None else None),
        leg_boundary_value=(candidate.leg_boundary_value.copy_negate()
                            if candidate.leg_boundary_value is not None else None),
    )
    return mirrored
```

### FUN-REA-019 — `mirror_analysis`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:mirror_analysis`  
Source-Lines: 618-624  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def mirror_analysis(analysis: IntrabarAnalysis | None) -> IntrabarAnalysis | None:
    if analysis is None:
        return None
    return IntrabarAnalysis(
        mirror_candle(analysis.event_second), analysis.extreme.copy_negate(),
        mirror_candle(analysis.extreme_source),
    )
```

### FUN-REA-020 — `_ReflectedCandles.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:_ReflectedCandles.__init__`  
Source-Lines: 635-637  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(self, source: Sequence[Candle]) -> None:
        self.source = source
        self._cache: list[Candle | None] = [None] * len(source)
```

### FUN-REA-021 — `_ReflectedCandles.__len__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:_ReflectedCandles.__len__`  
Source-Lines: 639-640  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __len__(self) -> int:
        return len(self.source)
```

### FUN-REA-022 — `_ReflectedCandles.__getitem__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:_ReflectedCandles.__getitem__`  
Source-Lines: 642-649  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __getitem__(self, index):
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(len(self.source)))]
        cached = self._cache[index]
        if cached is None:
            cached = mirror_candle(self.source[index])
            self._cache[index] = cached
        return cached
```

### FUN-REA-023 — `_reflected_view`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:_reflected_view`  
Source-Lines: 655-662  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reflected_view(source: Sequence[Candle]) -> _ReflectedCandles:
    key = id(source)
    cached = _REFLECTED_VIEWS.get(key)
    if cached is not None and cached[0] is source:
        return cached[1]
    view = _ReflectedCandles(source)
    _REFLECTED_VIEWS[key] = (source, view)
    return view
```

### FUN-REA-024 — `BearishDetector.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BearishDetector.__init__`  
Source-Lines: 673-691  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(self, candles, raw_candles, start_index, end_index):
        super().__init__(candles, raw_candles, start_index, end_index)
        self.reference = BullishDetector(
            candles, raw_candles, start_index, end_index,
        )
        # Time indexes are invariant under price reflection. Construct them
        # from the original rows; lazily transform OHLC only when consumed.
        # _ReflectedCandles caches each mirrored candle so repeated scans do
        # not re-allocate, while construction stays cheap (important because
        # _append_reaction builds a fresh BearishDetector per reaction).
        self.reference.candles = _reflected_view(candles)
        self.reference.raw_candles = _reflected_view(raw_candles)
        self.reference.lower_index = ReflectedLowerTimeframeIndex(self.lower_index)
        # Keep market Candle.tag untouched. In Bearish logic the shared state
        # machine simply swaps which real market color owns each role:
        # RED context -> GREEN First. Dojis therefore remain GREEN and can
        # participate only wherever GREEN is valid.
        self.reference.context_color = "RED"
        self.reference.first_color = "GREEN"
```

### FUN-REA-025 — `BearishDetector.red_run_bottom_before`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BearishDetector.red_run_bottom_before`  
Source-Lines: 693-695  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def red_run_bottom_before(self, first_green_index):
        value, source = self.reference.green_run_peak_before(first_green_index)
        return value.copy_negate(), mirror_candle(source)
```

### FUN-REA-026 — `BearishDetector.breakdown_analysis`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BearishDetector.breakdown_analysis`  
Source-Lines: 697-700  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def breakdown_analysis(self, candidate, breakdown_candle):
        return mirror_analysis(self.reference.breakout_analysis(
            mirror_candidate(candidate), mirror_candle(breakdown_candle),
        ))
```

### FUN-REA-027 — `BearishDetector.invalidation_high_break_before_breakdown`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BearishDetector.invalidation_high_break_before_breakdown`  
Source-Lines: 702-705  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def invalidation_high_break_before_breakdown(self, candidate, candle):
        return self.reference.mode_a_invalidation_before_breakout(
            mirror_candidate(candidate), mirror_candle(candle),
        )
```

### FUN-REA-028 — `BearishDetector.confirmed_reset_before_breakdown`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BearishDetector.confirmed_reset_before_breakdown`  
Source-Lines: 707-711  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def confirmed_reset_before_breakdown(self, candidate, candle, confirmed_top):
        return self.reference.confirmed_reset_before_breakout(
            mirror_candidate(candidate), mirror_candle(candle),
            confirmed_top.copy_negate(),
        )
```

### FUN-REA-029 — `BearishDetector.post_breakdown_reset`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BearishDetector.post_breakdown_reset`  
Source-Lines: 713-718  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def post_breakdown_reset(self, analysis, box_top, breakdown_candle):
        result = self.reference.post_breakout_reset(
            mirror_analysis(analysis), box_top.copy_negate(),
            mirror_candle(breakdown_candle),
        )
        return mirror_candle(result) if result is not None else None
```

### FUN-REA-030 — `BearishDetector.detect`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:BearishDetector.detect`  
Source-Lines: 720-728  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect(self, *, first_only: bool = False) -> DetectionResult:
        result = self.reference.detect(first_only=first_only)
        return DetectionResult(
            direction="bearish",
            reactions=[mirror_candidate(candidate) for candidate in result.reactions],
            resets=[replace(reset, broken_level=reset.broken_level.copy_negate())
                    for reset in result.resets],
            start_index=result.start_index, end_index=result.end_index,
        )
```

### FUN-REA-031 — `published_reaction_candidate`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:published_reaction_candidate`  
Source-Lines: 731-826  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def published_reaction_candidate(
    direction: str,
    candidate: Candidate,
    chronology: object,
) -> Candidate:
    """Return a presentation clone with Break-candle geometry frozen at confirmation.

    Detection/lifecycle ownership is intentionally not mutated here.  The public
    Reaction box must not include an opposite-edge extreme that happened later
    inside the same main Break candle after the Reaction had already confirmed.

    Main candles strictly before Break are fully eligible.  Only when the
    full-main-candle opposite extreme is owned by Break do we use native RAW
    chronology to keep prices up to and including the first strict confirmation:

      Bullish -> published BoxBottom is the minimum eligible Low before the
                 first strict High > BoxTop breakout.
      Bearish -> published BoxTop is the maximum eligible High before the
                 first strict Low < BoxBottom breakdown.

    Equal extremes retain the earliest main-candle owner.  If lower-timeframe
    data cannot resolve the strict confirmation, preserve the detector geometry
    rather than guessing an intrabar order.
    """
    candles = chronology.candles
    raw_candles = chronology.raw_candles
    published = replace(candidate)
    if candidate.break_idx is None:
        return published

    first_index = int(candidate.first_idx)
    break_index = int(candidate.break_idx)
    if first_index < 0 or break_index < first_index or break_index >= len(candles):
        return published

    break_candle = candles[break_index]
    timeframe = chronology.timeframe

    if direction == "bullish":
        # No Break-candle ownership -> the published full-range minimum was
        # already made before confirmation and is therefore chronology-safe.
        if int(candidate.box_bottom_source_idx) != break_index:
            return published
        value = candles[first_index].low
        source = candles[first_index]
        for index in range(first_index + 1, break_index):
            candle = candles[index]
            if candle.low < value:
                value, source = candle.low, candle
        threshold = candidate.box_top
    elif direction == "bearish":
        if int(candidate.box_top_source_idx) != break_index:
            return published
        value = candles[first_index].high
        source = candles[first_index]
        for index in range(first_index + 1, break_index):
            candle = candles[index]
            if candle.high > value:
                value, source = candle.high, candle
        threshold = candidate.box_bottom
    else:
        raise ValueError(f"Unsupported reaction direction: {direction}")

    lo, hi = chronology.lower_bounds(
        break_candle.timestamp, break_candle.timestamp + timeframe
    )
    confirmed = False

    for second in raw_candles[lo:hi]:
        if direction == "bullish":
            if second.low < value:
                value = second.low
                source = break_candle
            if second.high > threshold:
                confirmed = True
                break
        else:
            if second.high > value:
                value = second.high
                source = break_candle
            if second.low < threshold:
                confirmed = True
                break

    if not confirmed:
        return published

    if direction == "bullish":
        published.box_bottom = value
        published.box_bottom_source_idx = source.index
        published.box_bottom_source_time = source.display_time
    else:
        published.box_top = value
        published.box_top_source_idx = source.index
        published.box_top_source_time = source.display_time
    return published
```

### FUN-REA-032 — `_decimal_value`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:_decimal_value`  
Source-Lines: 829-831  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _decimal_value(value: object) -> Decimal:
    """Normalize external numeric values without binary-float arithmetic."""
    return value if isinstance(value, Decimal) else Decimal(str(value))
```

### FUN-REA-033 — `LowerTimeframeIndex.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:LowerTimeframeIndex.__init__`  
Source-Lines: 841-880  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(self, candles: Sequence[Candle]) -> None:
        self.candles = candles
        self.times = [getattr(item, "timestamp") for item in candles]
        size = 1
        while size < len(candles):
            size <<= 1
        self.size = size
        self.length = len(candles)
        self.minimum: list[Decimal | None] = [None] * (2 * size)
        self.maximum: list[Decimal | None] = [None] * (2 * size)
        self.minimum_position = array("i", [-1]) * (2 * size)
        self.maximum_position = array("i", [-1]) * (2 * size)
        for position, candle in enumerate(candles):
            node = size + position
            self.minimum[node] = _decimal_value(getattr(candle, "low"))
            self.maximum[node] = _decimal_value(getattr(candle, "high"))
            self.minimum_position[node] = position
            self.maximum_position[node] = position
        for node in range(size - 1, 0, -1):
            left, right = node * 2, node * 2 + 1
            low_left, low_right = self.minimum[left], self.minimum[right]
            high_left, high_right = self.maximum[left], self.maximum[right]
            if low_left is None:
                self.minimum[node] = low_right
                self.minimum_position[node] = self.minimum_position[right]
            elif low_right is None or low_left <= low_right:
                self.minimum[node] = low_left
                self.minimum_position[node] = self.minimum_position[left]
            else:
                self.minimum[node] = low_right
                self.minimum_position[node] = self.minimum_position[right]
            if high_left is None:
                self.maximum[node] = high_right
                self.maximum_position[node] = self.maximum_position[right]
            elif high_right is None or high_left >= high_right:
                self.maximum[node] = high_left
                self.maximum_position[node] = self.maximum_position[left]
            else:
                self.maximum[node] = high_right
                self.maximum_position[node] = self.maximum_position[right]
```

### FUN-REA-034 — `LowerTimeframeIndex.first_less`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:LowerTimeframeIndex.first_less`  
Source-Lines: 882-883  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def first_less(self, left: int, right: int, level: Decimal) -> int | None:
        return self._first(1, 0, self.size, left, right, level, True)
```

### FUN-REA-035 — `LowerTimeframeIndex.first_greater`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:LowerTimeframeIndex.first_greater`  
Source-Lines: 885-886  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def first_greater(self, left: int, right: int, level: Decimal) -> int | None:
        return self._first(1, 0, self.size, left, right, level, False)
```

### FUN-REA-036 — `LowerTimeframeIndex.range_minimum`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:LowerTimeframeIndex.range_minimum`  
Source-Lines: 888-890  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def range_minimum(self, left: int, right: int) -> tuple[Decimal, int]:
        """Return the minimum Low and earliest owning position in [left, right)."""
        return self._range_query(left, right, minimum=True)
```

### FUN-REA-037 — `LowerTimeframeIndex.range_maximum`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:LowerTimeframeIndex.range_maximum`  
Source-Lines: 892-894  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def range_maximum(self, left: int, right: int) -> tuple[Decimal, int]:
        """Return the maximum High and earliest owning position in [left, right)."""
        return self._range_query(left, right, minimum=False)
```

### FUN-REA-038 — `LowerTimeframeIndex._range_query`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:LowerTimeframeIndex._range_query`  
Source-Lines: 896-932  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _range_query(
        self, left: int, right: int, *, minimum: bool
    ) -> tuple[Decimal, int]:
        if left < 0 or right > self.length or left >= right:
            raise ValueError("Range contains no lower-timeframe candles.")
        values = self.minimum if minimum else self.maximum
        positions = self.minimum_position if minimum else self.maximum_position
        left += self.size
        right += self.size
        best_value: Decimal | None = None
        best_position = -1
        while left < right:
            if left & 1:
                value = values[left]
                position = positions[left]
                if value is not None and (
                    best_value is None
                    or (value < best_value if minimum else value > best_value)
                    or (value == best_value and position < best_position)
                ):
                    best_value, best_position = value, position
                left += 1
            if right & 1:
                right -= 1
                value = values[right]
                position = positions[right]
                if value is not None and (
                    best_value is None
                    or (value < best_value if minimum else value > best_value)
                    or (value == best_value and position < best_position)
                ):
                    best_value, best_position = value, position
            left >>= 1
            right >>= 1
        if best_value is None or best_position < 0:
            raise ValueError("Range contains no lower-timeframe candles.")
        return best_value, best_position
```

### FUN-REA-039 — `LowerTimeframeIndex._first`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:LowerTimeframeIndex._first`  
Source-Lines: 934-951  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first(
        self, node: int, start: int, end: int, left: int, right: int,
        level: Decimal, less: bool,
    ) -> int | None:
        if end <= left or right <= start or start >= self.length:
            return None
        extreme = self.minimum[node] if less else self.maximum[node]
        if extreme is None or (extreme >= level if less else extreme <= level):
            return None
        if end - start == 1:
            return start
        middle = (start + end) // 2
        found = self._first(node * 2, start, middle, left, right, level, less)
        if found is not None:
            return found
        return self._first(
            node * 2 + 1, middle, end, left, right, level, less
        )
```

### FUN-REA-040 — `shared_lower_timeframe_index`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:shared_lower_timeframe_index`  
Source-Lines: 959-969  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def shared_lower_timeframe_index(
    candles: Sequence[Candle],
) -> LowerTimeframeIndex:
    """Reuse one immutable lower-timeframe index per source sequence."""
    key = id(candles)
    cached = _LOWER_TIMEFRAME_INDEXES.get(key)
    if cached is not None and cached[0] is candles:
        return cached[1]
    index = LowerTimeframeIndex(candles)
    _LOWER_TIMEFRAME_INDEXES[key] = (candles, index)
    return index
```

### FUN-REA-041 — `ReflectedLowerTimeframeIndex.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:ReflectedLowerTimeframeIndex.__init__`  
Source-Lines: 977-979  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(self, base: LowerTimeframeIndex) -> None:
        self.base = base
        self.times = base.times
```

### FUN-REA-042 — `ReflectedLowerTimeframeIndex.first_less`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:ReflectedLowerTimeframeIndex.first_less`  
Source-Lines: 981-982  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def first_less(self, left: int, right: int, level: Decimal) -> int | None:
        return self.base.first_greater(left, right, level.copy_negate())
```

### FUN-REA-043 — `ReflectedLowerTimeframeIndex.first_greater`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:ReflectedLowerTimeframeIndex.first_greater`  
Source-Lines: 984-985  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def first_greater(self, left: int, right: int, level: Decimal) -> int | None:
        return self.base.first_less(left, right, level.copy_negate())
```

### FUN-REA-044 — `ReflectedLowerTimeframeIndex.range_minimum`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:ReflectedLowerTimeframeIndex.range_minimum`  
Source-Lines: 987-989  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def range_minimum(self, left: int, right: int) -> tuple[Decimal, int]:
        value, position = self.base.range_maximum(left, right)
        return value.copy_negate(), position
```

### FUN-REA-045 — `ReflectedLowerTimeframeIndex.range_maximum`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:ReflectedLowerTimeframeIndex.range_maximum`  
Source-Lines: 991-993  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def range_maximum(self, left: int, right: int) -> tuple[Decimal, int]:
        value, position = self.base.range_minimum(left, right)
        return value.copy_negate(), position
```

### FUN-REA-046 — `MarketChronology.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:MarketChronology.__init__`  
Source-Lines: 1015-1035  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(
        self,
        candles: Sequence[Candle],
        raw_candles: Sequence[Candle],
        timeframe_seconds: int,
        lower_index: LowerTimeframeIndex | None = None,
    ) -> None:
        if timeframe_seconds < 1:
            raise ValueError("Timeframe must be at least one second.")
        self.candles = candles
        self.raw_candles = raw_candles
        self.times = [getattr(item, "timestamp") for item in candles]
        self.raw_times = (
            lower_index.times
            if lower_index is not None
            else [getattr(item, "timestamp") for item in raw_candles]
        )
        self.timeframe = timedelta(seconds=timeframe_seconds)
        self.lower_index = lower_index or shared_lower_timeframe_index(raw_candles)
        self._confirmation_cache: dict[tuple[object, ...], datetime] = {}
        self._reset_time_cache: dict[tuple[object, ...], datetime] = {}
```

### FUN-REA-047 — `MarketChronology.opposite_direction`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:MarketChronology.opposite_direction`  
Source-Lines: 1038-1040  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def opposite_direction(direction: str) -> str:
        """Expose the shared mirror-direction contract to downstream engines."""
        return opposite_direction(direction)
```

### FUN-REA-048 — `MarketChronology.main_index`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:MarketChronology.main_index`  
Source-Lines: 1042-1049  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def main_index(self, timestamp: datetime, *, clamp: bool = False) -> int:
        """Map an exact lower-timeframe timestamp to its owning main candle."""
        index = bisect.bisect_right(self.times, timestamp) - 1
        if index < 0:
            if clamp:
                return 0
            raise ValueError("Lower-timeframe event precedes the main candles.")
        return index
```

### FUN-REA-049 — `MarketChronology.lower_bounds`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:MarketChronology.lower_bounds`  
Source-Lines: 1051-1060  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def lower_bounds(
        self, start: datetime, end: datetime | None = None
    ) -> tuple[int, int]:
        left = bisect.bisect_left(self.raw_times, start)
        right = (
            len(self.raw_candles)
            if end is None
            else bisect.bisect_left(self.raw_times, end)
        )
        return left, right
```

### FUN-REA-050 — `MarketChronology.lower_window`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:MarketChronology.lower_window`  
Source-Lines: 1062-1066  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def lower_window(
        self, start: datetime, end: datetime | None = None
    ) -> Sequence[Candle]:
        left, right = self.lower_bounds(start, end)
        return self.raw_candles[left:right]
```

### FUN-REA-051 — `MarketChronology._reset_cache_key`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:MarketChronology._reset_cache_key`  
Source-Lines: 1069-1078  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reset_cache_key(reset: object) -> tuple[object, ...]:
        """Return a stable Reset identity suitable for chronology caches."""
        return (
            int(getattr(reset, "index", -1)),
            int(getattr(reset, "from_first_idx", -1)),
            getattr(reset, "second_time", None),
            getattr(reset, "display_time", None),
            getattr(reset, "timestamp", None),
            str(getattr(reset, "broken_level", "")),
        )
```

### FUN-REA-052 — `MarketChronology._reaction_cache_key`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:MarketChronology._reaction_cache_key`  
Source-Lines: 1081-1093  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reaction_cache_key(
        reaction: object, direction: str, use_intrabar_start: bool
    ) -> tuple[object, ...]:
        """Return a stable physical/geometry identity for confirmation caches."""
        return (
            direction,
            bool(use_intrabar_start),
            int(getattr(reaction, "first_idx")),
            int(getattr(reaction, "break_idx")),
            str(getattr(reaction, "box_top")),
            str(getattr(reaction, "box_bottom")),
            getattr(reaction, "intrabar_start", None) if use_intrabar_start else None,
        )
```

### FUN-REA-053 — `MarketChronology.reset_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:MarketChronology.reset_time`  
Source-Lines: 1095-1112  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def reset_time(self, reset: object) -> datetime:
        """Return the exact Reset event time, preserving legacy provenance."""
        cache_key = self._reset_cache_key(reset)
        cached = self._reset_time_cache.get(cache_key)
        if cached is not None:
            return cached
        second = getattr(reset, "second_time", None)
        if second:
            result = datetime.strptime(second, "%Y-%m-%d %H:%M:%S")
        else:
            display = getattr(reset, "display_time", None)
            result = (
                datetime.strptime(display, "%Y-%m-%d %H:%M:%S")
                if display
                else getattr(reset, "timestamp")
            )
        self._reset_time_cache[cache_key] = result
        return result
```

### FUN-REA-054 — `MarketChronology.reaction_confirmation`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:MarketChronology.reaction_confirmation`  
Source-Lines: 1114-1159  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def reaction_confirmation(
        self,
        direction: str,
        reaction: object,
        *,
        use_intrabar_start: bool = True,
    ) -> datetime:
        """Return the first strict lower-timeframe Reaction confirmation.

        ``use_intrabar_start=False`` preserves the established A-engine
        chronology contract, which starts its scan at the Break candle open.
        S/E and public Reaction chronology use the exact intrabar start when
        present.
        """
        cache_key = self._reaction_cache_key(
            reaction, direction, use_intrabar_start
        )
        cached = self._confirmation_cache.get(cache_key)
        if cached is not None:
            return cached
        break_index = int(getattr(reaction, "break_idx"))
        break_candle = self.candles[break_index]
        candle_start = getattr(break_candle, "timestamp")
        start = (
            getattr(reaction, "intrabar_start", None) or candle_start
            if use_intrabar_start
            else candle_start
        )
        candle_end = candle_start + self.timeframe
        if start < candle_start or start >= candle_end:
            start = candle_start
        level = _decimal_value(
            getattr(reaction, "box_top" if direction == "bullish" else "box_bottom")
        )
        left, right = self.lower_bounds(start, candle_end)
        field = "high" if direction == "bullish" else "low"
        for position in range(left, right):
            item = self.raw_candles[position]
            value = _decimal_value(getattr(item, field))
            confirms = value > level if direction == "bullish" else value < level
            if confirms:
                result = getattr(item, "timestamp")
                self._confirmation_cache[cache_key] = result
                return result
        self._confirmation_cache[cache_key] = candle_start
        return candle_start
```

### FUN-REA-055 — `MarketChronology.canonical_order_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:MarketChronology.canonical_order_stop`  
Source-Lines: 1162-1224  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def canonical_order_stop(
        self,
        order_direction: str,
        reaction_number: int,
        reaction: object,
        opposite_reactions: Sequence[object],
        *,
        start_index: int = 0,
    ) -> tuple[Decimal, int, datetime]:
        """Return canonical opposite-Order stop provenance for S and E.

        Mode A owns the true leg head/floor from its anchor/context through
        Break inclusive. Mode B inherits the previous healthy opposite
        Reaction's semantic outer box edge. This is the single authoritative
        implementation used by every downstream behavior family.
        """
        if str(getattr(reaction, "mode")) == "A":
            first_index = int(getattr(reaction, "first_idx"))
            break_index = int(getattr(reaction, "break_idx"))
            anchor_index = getattr(reaction, "anchor_idx", None)
            scan_start = (
                max(start_index, int(anchor_index))
                if anchor_index is not None
                else max(start_index, first_index - 1)
            )
            context_tag = "GREEN" if order_direction == "bearish" else "RED"
            while (
                scan_start > start_index
                and getattr(self.candles[scan_start - 1], "tag") == context_tag
            ):
                scan_start -= 1

            attribute = "high" if order_direction == "bearish" else "low"
            source_index = scan_start
            level = _decimal_value(getattr(self.candles[source_index], attribute))
            for candle in self.candles[scan_start + 1 : break_index + 1]:
                candidate = _decimal_value(getattr(candle, attribute))
                better = (
                    candidate > level
                    if order_direction == "bearish"
                    else candidate < level
                )
                if better:
                    source_index = int(getattr(candle, "index"))
                    level = candidate
            return level, source_index, getattr(self.candles[source_index], "timestamp")

        if reaction_number <= 1:
            raise ValueError("Mode-B order reaction has no previous healthy reaction.")
        previous = opposite_reactions[reaction_number - 2]
        if order_direction == "bearish":
            source_index = int(getattr(previous, "box_top_source_idx"))
            return (
                _decimal_value(getattr(previous, "box_top")),
                source_index,
                getattr(self.candles[source_index], "timestamp"),
            )
        source_index = int(getattr(previous, "box_bottom_source_idx"))
        return (
            _decimal_value(getattr(previous, "box_bottom")),
            source_index,
            getattr(self.candles[source_index], "timestamp"),
        )
```

### FUN-REA-056 — `build_behavior_reaction_views`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:build_behavior_reaction_views`  
Source-Lines: 1227-1332  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def build_behavior_reaction_views(
    full_results: dict[str, object],
    chronology: MarketChronology,
):
    """Mark true cross-direction Reaction interiors for downstream behavior."""
    candles = chronology.candles
    raw_candles = chronology.raw_candles
    raw_times = chronology.raw_times
    public: dict[str, list[Candidate]] = {}
    confirmation: dict[str, list[datetime]] = {}
    for direction in ("bullish", "bearish"):
        public[direction] = [
            published_reaction_candidate(direction, item, chronology)
            for item in full_results[direction].reactions
        ]
        confirmation[direction] = [
            chronology.reaction_confirmation(direction, item)
            for item in full_results[direction].reactions
        ]

    def path_is_contained(
        first_time: datetime,
        confirmed_at: datetime,
        bottom: Decimal,
        top: Decimal,
    ) -> bool:
        left = bisect.bisect_left(raw_times, first_time)
        right = bisect.bisect_right(raw_times, confirmed_at)
        relevant = raw_candles[left:right]
        if not relevant:
            return False
        return all(
            _decimal_value(item.low) >= bottom
            and _decimal_value(item.high) <= top
            for item in relevant
        )

    blocked: dict[str, set[tuple[int, int]]] = {
        "bullish": set(),
        "bearish": set(),
    }
    for direction in ("bullish", "bearish"):
        opposite = opposite_direction(direction)
        for number, reaction in enumerate(full_results[direction].reactions, start=1):
            reaction.behavior_public_number = number
            published = public[direction][number - 1]
            reaction.behavior_public_box_top = _decimal_value(published.box_top)
            reaction.behavior_public_box_bottom = _decimal_value(published.box_bottom)
            reaction.behavior_confirmation_time = confirmation[direction][number - 1]
            reaction.behavior_first_time = candles[int(getattr(reaction, "first_idx"))].timestamp

        for reaction, published, confirmed_at in zip(
            full_results[direction].reactions,
            public[direction],
            confirmation[direction],
        ):
            inner_first = candles[int(getattr(reaction, "first_idx"))].timestamp
            inner_top = _decimal_value(published.box_top)
            inner_bottom = _decimal_value(published.box_bottom)
            for outer, outer_published, outer_confirmed_at in zip(
                full_results[opposite].reactions,
                public[opposite],
                confirmation[opposite],
            ):
                outer_first = candles[int(getattr(outer, "first_idx"))].timestamp
                if inner_first <= outer_first or confirmed_at > outer_confirmed_at:
                    continue
                outer_top = _decimal_value(outer_published.box_top)
                outer_bottom = _decimal_value(outer_published.box_bottom)
                if (
                    inner_top <= outer_top
                    and inner_bottom >= outer_bottom
                    and path_is_contained(
                        inner_first,
                        confirmed_at,
                        outer_bottom,
                        outer_top,
                    )
                ):
                    blocked[direction].add(
                        (
                            int(getattr(reaction, "first_idx")),
                            int(getattr(reaction, "break_idx")),
                        )
                    )
                    break

    behavior_results = {}
    number_maps = {}
    blocked_first_times = {"bullish": set(), "bearish": set()}
    for direction in ("bullish", "bearish"):
        full = full_results[direction]
        for item in full.reactions:
            identity = (
                int(getattr(item, "first_idx")),
                int(getattr(item, "break_idx")),
            )
            item.behavior_internal = identity in blocked[direction]
        behavior_results[direction] = full
        number_maps[direction] = {
            number: number for number, _item in enumerate(full.reactions, start=1)
        }
        blocked_first_times[direction] = {
            candles[first_idx].timestamp for first_idx, _ in blocked[direction]
        }
    return behavior_results, number_maps, blocked, blocked_first_times
```

### FUN-REA-057 — `directional_a_stop_order_finder`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:directional_a_stop_order_finder`  
Source-Lines: 1335-1395  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def directional_a_stop_order_finder(
    candles: Sequence[Candle],
    raw_candles: Sequence[Candle],
    direction: str,
):
    """Build the cached bounded opposite-Reaction resolver used after A stop."""
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    order_direction = opposite_direction(direction)
    first_tag = "GREEN" if order_direction == "bearish" else "RED"
    context_tag = "RED" if order_direction == "bearish" else "GREEN"
    cache: dict[tuple[int, int], Candidate | None] = {}
    detection_cache: dict[tuple[int, int], tuple[Candidate, ...]] = {}

    def find(gate_index: int, gate_event: datetime, end_index: int):
        key = (gate_index, end_index)
        if key in cache:
            return cache[key]
        first = next(
            (
                index
                for index in range(max(1, gate_index), end_index + 1)
                if candles[index].tag == first_tag
                and candles[index - 1].tag == context_tag
            ),
            None,
        )
        if first is None:
            cache[key] = None
            return None
        context = first - 1
        while context > 0 and candles[context - 1].tag == context_tag:
            context -= 1
        detection_key = (context, end_index)
        reactions = detection_cache.get(detection_key, ())
        order = next(
            (
                reaction
                for reaction in reactions
                if int(getattr(reaction, "first_idx")) >= gate_index
            ),
            None,
        )
        if order is None:
            result = UnifiedReactionDetector(
                candles, raw_candles, context, end_index, order_direction
            ).detect(stop_after_first_at_or_after=gate_index)
            reactions = tuple(result.reactions)
            detection_cache[detection_key] = reactions
            order = next(
                (
                    reaction
                    for reaction in reactions
                    if int(getattr(reaction, "first_idx")) >= gate_index
                ),
                None,
            )
        cache[key] = order
        return order

    return find
```

### FUN-REA-058 — `UnifiedReactionDetector.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector.__init__`  
Source-Lines: 1408-1431  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(
        self,
        candles: Sequence[Candle],
        raw_candles: Sequence[Candle],
        start_index: int,
        end_index: int,
        output_direction: str,
    ) -> None:
        super().__init__(candles, raw_candles, start_index, end_index)
        self.output_direction = output_direction
        # Directional helpers are created lazily: a bullish-only run must not
        # pay the BearishDetector mirroring cost and vice versa.
        self._bull: BullishDetector | None = None
        self._bear: BearishDetector | None = None
        self.all_reactions: dict[str, list[Candidate]] = {
            "bullish": [],
            "bearish": [],
        }
        self.all_resets: dict[str, list[ResetEvent]] = {
            "bullish": [],
            "bearish": [],
        }
        self._geometry_after_reset_cache: dict[tuple, Candidate | None] = {}
        self._simple_geometry_gate_cache: dict[tuple, Candidate | None] = {}
```

### FUN-REA-059 — `UnifiedReactionDetector.bull`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector.bull`  
Source-Lines: 1434-1439  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def bull(self) -> BullishDetector:
        if self._bull is None:
            self._bull = BullishDetector(
                self.candles, self.raw_candles, self.start_index, self.end_index
            )
        return self._bull
```

### FUN-REA-060 — `UnifiedReactionDetector.bear`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector.bear`  
Source-Lines: 1442-1447  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def bear(self) -> BearishDetector:
        if self._bear is None:
            self._bear = BearishDetector(
                self.candles, self.raw_candles, self.start_index, self.end_index
            )
        return self._bear
```

### FUN-REA-061 — `UnifiedReactionDetector._append_reaction`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._append_reaction`  
Source-Lines: 1449-1513  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _append_reaction(self, direction: str, candidate: Candidate) -> bool:
        # A confirmed adjacent opposite-direction Anchor may extend the outer
        # boundary, but it must never shrink the candidate's own box.
        opposite_anchor_is_confirmed = False
        if (
            candidate.break_idx is not None
            and candidate.anchor_idx is not None
            and candidate.anchor_idx + 1 == candidate.first_idx
            and self.all_resets[direction]
        ):
            reset_index = self.all_resets[direction][-1].index
            opposite_detector = (
                BullishDetector if direction == "bearish" else BearishDetector
            )(
                self.candles,
                self.raw_candles,
                reset_index,
                candidate.first_idx,
            )
            opposite_anchor_is_confirmed = any(
                reaction.break_idx == candidate.anchor_idx
                for reaction in opposite_detector.detect().reactions
            )

        if opposite_anchor_is_confirmed:
            anchor = self.candles[candidate.anchor_idx]
            first = self.candles[candidate.first_idx]
            if direction == "bearish":
                # A RED Leg-Start with a higher ceiling than FirstGreen owns
                # the leg boundary; FirstGreen must keep its own BoxBottom.
                if anchor.high <= first.high:
                    candidate.box_bottom = anchor.low
                    candidate.box_bottom_source_idx = anchor.index
                    candidate.box_bottom_source_time = anchor.display_time
            else:
                # Exact mirror: a GREEN Leg-Start whose floor is below
                # FirstRed owns the leg boundary; FirstRed keeps its BoxTop.
                if anchor.low >= first.low:
                    candidate.box_top = anchor.high
                    candidate.box_top_source_idx = anchor.index
                    candidate.box_top_source_time = anchor.display_time

        # Canonical confirmed-Reaction box ownership.  The directional
        # confirmation edge keeps the structure that discovered the Reaction:
        #   Bullish  -> BoxTop is the breakout edge.
        #   Bearish  -> BoxBottom is the breakdown edge.
        # The opposite edge, however, belongs to the complete confirmed
        # First..Break geometry (inclusive), not to pre-First context.
        # This rule is symmetric and applies to every published Reaction.
        if candidate.break_idx is not None:
            first_index = int(candidate.first_idx)
            break_index = int(candidate.break_idx)
            if direction == "bullish":
                bottom, bottom_source = self.minimum_low(first_index, break_index)
                candidate.box_bottom = bottom
                candidate.box_bottom_source_idx = bottom_source.index
                candidate.box_bottom_source_time = bottom_source.display_time
            else:
                top, top_source = self.maximum_high(first_index, break_index)
                candidate.box_top = top
                candidate.box_top_source_idx = top_source.index
                candidate.box_top_source_time = top_source.display_time

        self.all_reactions[direction].append(replace(candidate))
        return True
```

### FUN-REA-062 — `UnifiedReactionDetector._append_reset`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._append_reset`  
Source-Lines: 1515-1531  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _append_reset(
        self,
        direction: str,
        candle: Candle,
        level: Decimal,
        first_idx: int,
        second_time: str | None = None,
    ) -> None:
        self.all_resets[direction].append(
            ResetEvent(
                index=candle.index,
                display_time=candle.display_time,
                second_time=second_time,
                broken_level=level,
                from_first_idx=first_idx,
            )
        )
```

### FUN-REA-063 — `UnifiedReactionDetector._refine`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._refine`  
Source-Lines: 1533-1552  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _refine(
        self, direction: str, candidate: Candidate, candle: Candle
    ) -> IntrabarAnalysis | None:
        helper = self.bull if direction == "bullish" else self.bear
        analysis = (
            helper.breakout_analysis(candidate, candle)
            if direction == "bullish"
            else helper.breakdown_analysis(candidate, candle)
        )
        if analysis is None:
            return None
        if direction == "bullish" and candidate.box_bottom_source_idx == candle.index:
            candidate.box_bottom = analysis.extreme
            candidate.box_bottom_source_idx = analysis.extreme_source.index
            candidate.box_bottom_source_time = analysis.extreme_source.display_time
        if direction == "bearish" and candidate.box_top_source_idx == candle.index:
            candidate.box_top = analysis.extreme
            candidate.box_top_source_idx = analysis.extreme_source.index
            candidate.box_top_source_time = analysis.extreme_source.display_time
        return analysis
```

### FUN-REA-064 — `UnifiedReactionDetector._candidate_from_confirmation_remainder`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._candidate_from_confirmation_remainder`  
Source-Lines: 1554-1621  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _candidate_from_confirmation_remainder(
        self,
        direction: str,
        confirmed: Candidate,
        candle: Candle,
        analysis: IntrabarAnalysis | None,
    ) -> Candidate | None:
        """Reuse a correctly colored confirmation candle for the next reaction."""
        required_tag = "RED" if direction == "bullish" else "GREEN"
        if candle.tag != required_tag or analysis is None:
            return None
        # A cross-direction Leg-Start confirmation candle may simultaneously
        # become the first candle of the next same-direction reaction. Its
        # decisive second belongs to the new box boundary, so no second,
        # still-more-extreme tick is required. Other confirmations retain the
        # ordinary fresh post-event boundary requirement.
        # Every confirmation opens Normal Search. If its main candle has the
        # required start color, that complete candle is the next First candle,
        # regardless of whether the confirmed reaction was Mode A or Mode B.
        whole_confirmation_candle = True
        remainder_start = (
            candle.timestamp
            if whole_confirmation_candle
            else analysis.event_second.timestamp + timedelta(microseconds=1)
        )
        remainder_end = candle.timestamp + self.timeframe
        seconds = list(self.raw_between(remainder_start, remainder_end))
        if not seconds:
            return None
        if direction == "bullish":
            top_second = max(seconds, key=lambda item: (item.high, -item.timestamp.timestamp()))
            bottom_second = min(seconds, key=lambda item: (item.low, item.timestamp))
            if (
                not whole_confirmation_candle
                and top_second.high <= analysis.event_second.high
            ):
                return None
            return Candidate(
                first_idx=candle.index,
                first_time=candle.display_time,
                box_top_source_idx=candle.index,
                box_top_source_time=candle.display_time,
                box_top=top_second.high,
                box_bottom_source_idx=candle.index,
                box_bottom_source_time=candle.display_time,
                box_bottom=bottom_second.low,
                mode="B",
                intrabar_start=remainder_start,
            )
        bottom_second = min(seconds, key=lambda item: (item.low, item.timestamp))
        top_second = max(seconds, key=lambda item: (item.high, -item.timestamp.timestamp()))
        if (
            not whole_confirmation_candle
            and bottom_second.low >= analysis.event_second.low
        ):
            return None
        return Candidate(
            first_idx=candle.index,
            first_time=candle.display_time,
            box_top_source_idx=candle.index,
            box_top_source_time=candle.display_time,
            box_top=top_second.high,
            box_bottom_source_idx=candle.index,
            box_bottom_source_time=candle.display_time,
            box_bottom=bottom_second.low,
            mode="B",
            intrabar_start=remainder_start,
        )
```

### FUN-REA-065 — `UnifiedReactionDetector._first_initial`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._first_initial`  
Source-Lines: 1623-1633  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_initial(self, direction: str) -> Candidate | None:
        initial_result = (
            self.bull.detect(first_only=True)
            if direction == "bullish"
            else self.bear.detect(first_only=True)
        )
        return (
            replace(initial_result.reactions[0])
            if initial_result.reactions
            else None
        )
```

### FUN-REA-066 — `UnifiedReactionDetector._first_direct_same_direction_after_reset`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._first_direct_same_direction_after_reset`  
Source-Lines: 1636-1672  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_direct_same_direction_after_reset(
        self, direction: str, reset_index: int
    ) -> Candidate | None:
        """Return the first structurally owned reaction after Reset.

        The earliest eligible candidate owns the evolving leg until it either
        confirms or its outer leg boundary is strictly crossed. A nested local
        pattern cannot confirm while that owner is unresolved. If the boundary
        breaks first, restart strictly after that event. Bearish is the exact
        price/color mirror of Bullish.
        """
        context_tag = "GREEN" if direction == "bullish" else "RED"
        first_tag = "RED" if direction == "bullish" else "GREEN"
        blocked_through = reset_index

        for first_index in range(reset_index + 1, self.end_index + 1):
            first = self.candles[first_index]
            if first_index <= blocked_through:
                continue
            if first.tag != first_tag or self.candles[first_index - 1].tag != context_tag:
                continue

            candidate = self._build_direct_candidate(
                direction, reset_index, first_index
            )
            if candidate is None:
                continue
            confirmed, invalidation_index = self._scan_direct_candidate(
                direction, candidate, self.end_index
            )
            if confirmed is not None:
                return confirmed
            if invalidation_index is None:
                continue
            blocked_through = invalidation_index

        return None
```

### FUN-REA-067 — `UnifiedReactionDetector._first_geometry_after_reset`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._first_geometry_after_reset`  
Source-Lines: 1674-1724  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_geometry_after_reset(
        self, direction: str, reset_index: int, end_index: int | None = None,
    ) -> Candidate | None:
        """Return the first complete same-direction geometry after Reset.

        This search intentionally does not apply the normal Reset/invalidation
        gate.  In an E space, the reset-leg rule only requires the geometric
        Top-Bottom-Top / Bottom-Top-Bottom structure.
        """
        _lim = self.end_index if end_index is None else min(end_index, self.end_index)
        _ck = (direction, reset_index, _lim)
        if _ck in self._geometry_after_reset_cache:
            _cached = self._geometry_after_reset_cache[_ck]
            return replace(_cached) if _cached is not None else None
        first_tag = "RED" if direction == "bullish" else "GREEN"
        context_tag = "GREEN" if direction == "bullish" else "RED"
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        for first_index in range(reset_index + 1, limit + 1):
            if (
                self.candles[first_index].tag != first_tag
                or self.candles[first_index - 1].tag != context_tag
            ):
                continue
            candidate = self._build_direct_candidate(
                direction, reset_index, first_index
            )
            if candidate is None:
                continue
            for scan in range(first_index + 1, limit + 1):
                candle = self.candles[scan]
                if direction == "bullish":
                    if candle.low < candidate.box_bottom:
                        candidate.box_bottom = candle.low
                        candidate.box_bottom_source_idx = candle.index
                        candidate.box_bottom_source_time = candle.display_time
                    if candle.high > candidate.box_top:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        return candidate
                else:
                    if candle.high > candidate.box_top:
                        candidate.box_top = candle.high
                        candidate.box_top_source_idx = candle.index
                        candidate.box_top_source_time = candle.display_time
                    if candle.low < candidate.box_bottom:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        return candidate
        return None
```

### FUN-REA-068 — `UnifiedReactionDetector.first_geometry_after_reset`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector.first_geometry_after_reset`  
Source-Lines: 1726-1730  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def first_geometry_after_reset(
        self, direction: str, reset_index: int, end_index: int
    ) -> Candidate | None:
        """Public lifecycle API for post-Reset geometry discovery."""
        return self._first_geometry_after_reset(direction, reset_index, end_index)
```

### FUN-REA-069 — `UnifiedReactionDetector.first_simple_geometry_after_gate`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector.first_simple_geometry_after_gate`  
Source-Lines: 1733-1779  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def first_simple_geometry_after_gate(
        self,
        direction: str,
        reset_index: int,
        gate_index: int,
        end_index: int | None = None,
    ) -> Candidate | None:
        """Find the first E Order_B geometry from its actual Reset context.

        The Order_B gate is opened later by a strict lower-timeframe boundary
        crossing, but its simple geometry still belongs to the Reset that
        created the leg.  Reconstructing it from ``gate_index - 1`` invents a
        new Reset context and can promote a pattern that is not an
        authoritative reaction.  This bounded helper preserves the real Reset
        while restricting First to the gate candle or later.
        """
        _lim = self.end_index if end_index is None else min(end_index, self.end_index)
        _ck = (direction, reset_index, gate_index, _lim)
        if _ck in self._simple_geometry_gate_cache:
            _cached = self._simple_geometry_gate_cache[_ck]
            return replace(_cached) if _cached is not None else None
        first_tag = "RED" if direction == "bullish" else "GREEN"
        context_tag = "GREEN" if direction == "bullish" else "RED"
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        start = max(reset_index + 1, gate_index)
        for first_index in range(start, limit + 1):
            if (
                self.candles[first_index].tag != first_tag
                or self.candles[first_index - 1].tag != context_tag
            ):
                continue
            candidate = self._build_direct_candidate(
                direction, reset_index, first_index
            )
            if candidate is None:
                continue
            # The earliest eligible post-gate candidate owns this Reset leg.
            # It must survive the outer boundary inherited from ``reset_index``;
            # a later local candidate cannot recover a leg whose owner was
            # strictly invalidated before confirmation.
            confirmed, _ = self._scan_direct_candidate(
                direction, candidate, limit
            )
            self._simple_geometry_gate_cache[_ck] = confirmed
            return confirmed
        self._simple_geometry_gate_cache[_ck] = None
        return None
```

### FUN-REA-070 — `UnifiedReactionDetector._reaction_break_indices`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._reaction_break_indices`  
Source-Lines: 1781-1794  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reaction_break_indices(self, direction: str) -> list[int]:
        """Cached ascending `break_idx` values mirroring `all_reactions[direction]`.

        `all_reactions[direction]` is append-only and strictly non-decreasing
        in `break_idx`, so this index list can be reused via bisect instead of
        rescanning the full reaction history on every gate lookup.
        """
        reactions = self.all_reactions[direction]
        cached = self._reaction_break_index_cache.get(direction)
        if cached is not None and cached[0] == len(reactions):
            return cached[1]
        indices = [int(reaction.break_idx) for reaction in reactions]
        self._reaction_break_index_cache[direction] = (len(reactions), indices)
        return indices
```

### FUN-REA-071 — `UnifiedReactionDetector.first_order_reaction_after_gate`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector.first_order_reaction_after_gate`  
Source-Lines: 1796-1914  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def first_order_reaction_after_gate(
        self,
        direction: str,
        gate_index: int,
        end_index: int | None = None,
        gate_event_time: datetime | None = None,
    ) -> Candidate | None:
        """Return direct Order_A geometry from continuous Reaction context."""
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        if gate_index < self.start_index or gate_index >= limit:
            return None

        def confirmed_no_later_than_gate(reaction: Candidate) -> bool:
            break_index = int(reaction.break_idx)
            if break_index < gate_index or gate_event_time is None:
                return break_index <= gate_index
            if break_index > gate_index:
                return False
            break_candle = self.candles[break_index]
            start = reaction.intrabar_start or break_candle.timestamp
            end = break_candle.timestamp + self.timeframe
            level = reaction.box_bottom if direction == "bearish" else reaction.box_top
            for lower in self.raw_between(start, end):
                crossed = (
                    lower.low < level
                    if direction == "bearish"
                    else lower.high > level
                )
                if crossed:
                    return lower.timestamp <= gate_event_time
            return break_candle.timestamp <= gate_event_time

        reactions = self.all_reactions[direction]
        break_indices = self._reaction_break_indices(direction)
        # `break_indices` is non-decreasing and duplicate-free for this
        # engine's reaction stream, so every reaction strictly before
        # `gate_index` is automatically confirmed; only a reaction whose
        # `break_idx` equals `gate_index` needs the fine-grained intrabar
        # check via `confirmed_no_later_than_gate`.
        cut = bisect.bisect_left(break_indices, gate_index)
        history = list(reactions[:cut])
        if cut < len(reactions) and break_indices[cut] == gate_index:
            if confirmed_no_later_than_gate(reactions[cut]):
                history.append(reactions[cut])
        search_start = gate_index + 1
        if not history:
            result = self._earliest_confirmed_geometry(
                direction, search_start, limit
            )
            if result is not None:
                result.order_gate_decision = "no-history"
            return result

        owner = max(history, key=lambda item: int(item.break_idx))
        boundary_end = max(int(owner.first_idx), gate_index - 1)
        gate = self.candles[gate_index]
        if direction == "bearish":
            outer_boundary, _ = self.maximum_high(
                int(owner.first_idx), boundary_end
            )
            gate_boundary = gate.low
        else:
            outer_boundary, _ = self.minimum_low(
                int(owner.first_idx), boundary_end
            )
            gate_boundary = gate.high

        event_start = gate_event_time or gate.timestamp
        event_end = self.candles[limit].timestamp + self.timeframe
        decision: tuple[str, Candle] | None = None
        for lower in self.raw_between(event_start, event_end):
            if direction == "bearish":
                outer_cross = lower.high > outer_boundary
                gate_cross = lower.low < gate_boundary
            else:
                outer_cross = lower.low < outer_boundary
                gate_cross = lower.high > gate_boundary
            if outer_cross:
                decision = ("restart", lower)
                break
            if gate_cross:
                decision = ("continue", lower)
                break

        if decision is None:
            return None
        if decision[0] == "restart":
            source = self.main_source_for_time(decision[1].timestamp)
            if source is None:
                return None
            search_start = int(source.index) + 1
        if search_start > limit:
            return None
        result = self._earliest_confirmed_geometry(
            direction, search_start, limit
        )
        if result is not None:
            result.order_gate_decision = decision[0]
            if decision[0] == "continue":
                # Order-context only: a stop inside an already-open post-Reset
                # leg keeps the real leg head/floor as Mode-A provenance.
                prior_resets = [
                    item for item in self.all_resets[direction]
                    if item.index < int(result.first_idx)
                ]
                if prior_resets:
                    reset_index = max(item.index for item in prior_resets)
                    if direction == "bullish":
                        boundary, source = self.minimum_low(
                            reset_index, int(result.first_idx) - 1
                        )
                    else:
                        boundary, source = self.maximum_high(
                            reset_index, int(result.first_idx) - 1
                        )
                    result.anchor_idx = source.index
                    result.anchor_value = boundary
                    result.leg_boundary_value = boundary
        return result
```

### FUN-REA-072 — `UnifiedReactionDetector._earliest_confirmed_geometry`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._earliest_confirmed_geometry`  
Source-Lines: 1916-1969  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _earliest_confirmed_geometry(
        self, direction: str, start_index: int, end_index: int | None = None,
    ) -> Candidate | None:
        """Return the geometry whose strict confirmation occurs first.

        Multiple First candidates may overlap. Order-gender chronology belongs
        to the structure that completes first, not necessarily to the oldest
        still-unconfirmed First candle.
        """
        first_tag = "RED" if direction == "bullish" else "GREEN"
        context_tag = "GREEN" if direction == "bullish" else "RED"
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        active: list[Candidate] = []
        reset_index = max(self.start_index, start_index - 1)
        for scan in range(start_index, limit + 1):
            candle = self.candles[scan]
            if (
                scan > reset_index
                and candle.tag == first_tag
                and self.candles[scan - 1].tag == context_tag
            ):
                candidate = self._build_direct_candidate(
                    direction, reset_index, scan
                )
                if candidate is not None:
                    active.append(candidate)

            confirmed: list[Candidate] = []
            for candidate in active:
                if scan <= candidate.first_idx:
                    continue
                if direction == "bullish":
                    if candle.low < candidate.box_bottom:
                        candidate.box_bottom = candle.low
                        candidate.box_bottom_source_idx = candle.index
                        candidate.box_bottom_source_time = candle.display_time
                    if candle.high > candidate.box_top:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        confirmed.append(candidate)
                else:
                    if candle.high > candidate.box_top:
                        candidate.box_top = candle.high
                        candidate.box_top_source_idx = candle.index
                        candidate.box_top_source_time = candle.display_time
                    if candle.low < candidate.box_bottom:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        confirmed.append(candidate)
            if confirmed:
                return min(confirmed, key=lambda item: item.first_idx)
        return None
```

### FUN-REA-073 — `UnifiedReactionDetector._build_direct_candidate`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._build_direct_candidate`  
Source-Lines: 1971-2026  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _build_direct_candidate(
        self, direction: str, reset_index: int, first_index: int
    ) -> Candidate | None:
        context_tag = "GREEN" if direction == "bullish" else "RED"
        first_tag = "RED" if direction == "bullish" else "GREEN"
        first = self.candles[first_index]
        if (
            first_index <= reset_index
            or first.tag != first_tag
            or self.candles[first_index - 1].tag != context_tag
        ):
            return None

        context_start = first_index - 1
        while (
            context_start - 1 >= reset_index
            and self.candles[context_start - 1].tag == context_tag
        ):
            context_start -= 1
        local_start = context_start
        while (
            local_start - 1 >= reset_index
            and self.candles[local_start - 1].tag == first_tag
        ):
            local_start -= 1

        if direction == "bullish":
            local_floor, _ = self.minimum_low(local_start, first_index - 1)
            if first.low < local_floor:
                return None
            box_top, top_source = self.maximum_high(context_start, first_index)
            leg_boundary, leg_source = self.minimum_low(
                reset_index, first_index - 1
            )
            return Candidate(
                first_index, first.display_time,
                top_source.index, top_source.display_time, box_top,
                first_index, first.display_time, first.low,
                mode="A", anchor_idx=leg_source.index,
                anchor_value=leg_boundary, leg_boundary_value=leg_boundary,
            )

        local_ceiling, _ = self.maximum_high(local_start, first_index - 1)
        if first.high > local_ceiling:
            return None
        box_bottom, bottom_source = self.minimum_low(context_start, first_index)
        leg_boundary, leg_source = self.maximum_high(
            reset_index, first_index - 1
        )
        return Candidate(
            first_index, first.display_time,
            first_index, first.display_time, first.high,
            bottom_source.index, bottom_source.display_time, box_bottom,
            mode="A", anchor_idx=leg_source.index,
            anchor_value=leg_boundary, leg_boundary_value=leg_boundary,
        )
```

### FUN-REA-074 — `UnifiedReactionDetector._scan_direct_candidate`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._scan_direct_candidate`  
Source-Lines: 2029-2057  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _scan_direct_candidate(
        self, direction: str, candidate: Candidate, stop_index: int
    ) -> tuple[Candidate | None, int | None]:
        for scan in range(candidate.first_idx + 1, stop_index + 1):
            candle = self.candles[scan]
            confirms = (
                candle.high > candidate.box_top
                if direction == "bullish"
                else candle.low < candidate.box_bottom
            )
            invalidates = self._owner_boundary_before_confirmation(
                direction, candidate, candle
            )
            if invalidates:
                return None, scan
            if direction == "bullish" and candle.low < candidate.box_bottom:
                candidate.box_bottom = candle.low
                candidate.box_bottom_source_idx = candle.index
                candidate.box_bottom_source_time = candle.display_time
            if direction == "bearish" and candle.high > candidate.box_top:
                candidate.box_top = candle.high
                candidate.box_top_source_idx = candle.index
                candidate.box_top_source_time = candle.display_time
            if confirms:
                candidate.break_idx = scan
                candidate.break_time = candle.display_time
                self._refine(direction, candidate, candle)
                return candidate, None
        return None, None
```

### FUN-REA-075 — `UnifiedReactionDetector._owner_boundary_before_confirmation`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._owner_boundary_before_confirmation`  
Source-Lines: 2059-2097  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _owner_boundary_before_confirmation(
        self, direction: str, candidate: Candidate, candle: Candle
    ) -> bool:
        """Return whether structural alignment is lost before confirmation.

        A Bearish Leg-Start Top must not rise above its outer ceiling.
        A Bullish Leg-Start Bottom must not fall below its outer floor.
        Equality preserves the unresolved candidate. If a strict invalidation
        competes with confirmation in the same main candle, ordered native RAW
        data decides which event occurred first.
        """
        boundary = candidate.leg_boundary_value
        if boundary is None:
            return False

        if direction == "bullish":
            reaches_boundary = candle.low < boundary
            confirms = candle.high > candidate.box_top
        else:
            reaches_boundary = candle.high > boundary
            confirms = candle.low < candidate.box_bottom
        if not reaches_boundary:
            return False
        if not confirms:
            return True

        end = candle.timestamp + self.timeframe
        for second in self.raw_between(candle.timestamp, end):
            if direction == "bullish":
                if second.low < boundary:
                    return True
                if second.high > candidate.box_top:
                    return False
            else:
                if second.high > boundary:
                    return True
                if second.low < candidate.box_bottom:
                    return False
        return True
```

### FUN-REA-076 — `UnifiedReactionDetector._result`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector._result`  
Source-Lines: 2100-2107  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _result(self) -> DetectionResult:
        return DetectionResult(
            direction=self.output_direction,
            reactions=self.all_reactions[self.output_direction],
            resets=self.all_resets[self.output_direction],
            start_index=self.start_index,
            end_index=self.end_index,
        )
```

### FUN-REA-077 — `UnifiedReactionDetector.detect`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `reaction_engine.py:UnifiedReactionDetector.detect`  
Source-Lines: 2109-2389  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect(
        self, *, stop_after_first_at_or_after: int | None = None
    ) -> DetectionResult:
        direction = self.output_direction
        initial = self._first_initial(direction)
        if initial is None:
            return DetectionResult(
                direction=direction,
                reactions=[],
                resets=[],
                start_index=self.start_index,
                end_index=self.end_index,
            )
        self._append_reaction(direction, initial)
        if (
            stop_after_first_at_or_after is not None
            and initial.first_idx >= stop_after_first_at_or_after
        ):
            return self._result()
        previous = initial
        index = initial.break_idx + 1
        running_value = (
            self.candles[initial.break_idx].high
            if direction == "bullish"
            else self.candles[initial.break_idx].low
        )
        running_source = initial.break_idx
        candidate: Candidate | None = None
        initial_break_candle = self.candles[initial.break_idx]
        initial_helper = self.bull if direction == "bullish" else self.bear
        initial_analysis = (
            initial_helper.breakout_analysis(initial, initial_break_candle)
            if direction == "bullish"
            else initial_helper.breakdown_analysis(initial, initial_break_candle)
        )
        initial_reset_second = (
            initial_helper.post_breakout_reset(
                initial_analysis, initial.box_bottom, initial_break_candle
            )
            if direction == "bullish"
            else initial_helper.post_breakdown_reset(
                initial_analysis, initial.box_top, initial_break_candle
            )
        )
        pending_reset_index = (
            initial.break_idx if initial_reset_second is not None else None
        )
        if initial_reset_second is not None:
            self._append_reset(
                direction,
                initial_break_candle,
                initial.box_bottom if direction == "bullish" else initial.box_top,
                initial.first_idx,
                initial_reset_second.display_time,
            )

        while index <= self.end_index:
            candle = self.candles[index]
            reset = pending_reset_index is not None or (
                candle.low < previous.box_bottom
                if direction == "bullish"
                else candle.high > previous.box_top
            )
            candidate_break = candidate is not None and (
                candle.high > candidate.box_top
                if direction == "bullish"
                else candle.low < candidate.box_bottom
            )
            if reset and candidate_break:
                if direction == "bullish":
                    reset = self.bull.confirmed_reset_before_breakout(
                        candidate, candle, previous.box_bottom
                    )
                else:
                    reset = self.bear.confirmed_reset_before_breakdown(
                        candidate, candle, previous.box_top
                    )
            if reset:
                reset_index = (
                    pending_reset_index
                    if pending_reset_index is not None
                    else index
                )
                reset_candle = self.candles[reset_index]
                pending_reset_index = None
                level = previous.box_bottom if direction == "bullish" else previous.box_top
                already_recorded = (
                    self.all_resets[direction]
                    and self.all_resets[direction][-1].from_first_idx
                    == previous.first_idx
                )
                if not already_recorded:
                    self._append_reset(
                        direction, reset_candle, level, previous.first_idx
                    )
                # A Reset reopens the ordinary same-direction ownership gate.
                # The geometric relaxation belongs only to the cross-direction
                # structural/E path and must not relabel every normal Reset.
                direct_candidate = self._first_direct_same_direction_after_reset(
                    direction, reset_index
                )
                # Both paths are valid interpretations of the same requested-
                # direction restart. The chronologically first confirmation
                # wins; a later Anchor-based candidate must never hide an
                # already complete direct post-Reset color sequence.
                structural = direct_candidate
                if structural is None or structural.break_idx is None:
                    break
                structural.mode = "A"
                structural.cross_direction_origin = False
                structural.cross_direction_chain_owner = False
                if not self._append_reaction(direction, structural):
                    candidate = None
                    index = structural.break_idx + 1
                    pending_reset_index = structural.break_idx
                    continue
                if (
                    stop_after_first_at_or_after is not None
                    and structural.first_idx >= stop_after_first_at_or_after
                ):
                    return self._result()
                previous = structural
                index = structural.break_idx + 1
                running_value = (
                    self.candles[structural.break_idx].high
                    if direction == "bullish"
                    else self.candles[structural.break_idx].low
                )
                running_source = structural.break_idx
                break_candle = self.candles[structural.break_idx]
                helper = self.bull if direction == "bullish" else self.bear
                analysis = (
                    helper.breakout_analysis(structural, break_candle)
                    if direction == "bullish"
                    else helper.breakdown_analysis(structural, break_candle)
                )
                post_reset_second = (
                    helper.post_breakout_reset(
                        analysis, structural.box_bottom, break_candle
                    )
                    if direction == "bullish"
                    else helper.post_breakdown_reset(
                        analysis, structural.box_top, break_candle
                    )
                )
                if post_reset_second is not None:
                    reset_level = (
                        structural.box_bottom
                        if direction == "bullish"
                        else structural.box_top
                    )
                    self._append_reset(
                        direction,
                        break_candle,
                        reset_level,
                        structural.first_idx,
                        post_reset_second.display_time,
                    )
                    # The confirmation candle has already reset the reaction
                    # after its exact intrabar confirmation. Its remainder
                    # cannot seed a Normal successor. Restart from the next
                    # main candle as a fresh Leg-Start search.
                    candidate = None
                    pending_reset_index = structural.break_idx
                else:
                    candidate = self._candidate_from_confirmation_remainder(
                        direction, structural, break_candle, analysis
                    )
                continue

            if candidate is not None:
                if direction == "bullish":
                    if candle.low < candidate.box_bottom:
                        candidate.box_bottom = candle.low
                        candidate.box_bottom_source_idx = candle.index
                        candidate.box_bottom_source_time = candle.display_time
                    if candle.high > candidate.box_top:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        analysis = self._refine(direction, candidate, candle)
                        post_reset_second = self.bull.post_breakout_reset(
                            analysis, candidate.box_bottom, candle
                        )
                        self._append_reaction(direction, candidate)
                        if (
                            stop_after_first_at_or_after is not None
                            and candidate.first_idx >= stop_after_first_at_or_after
                        ):
                            return self._result()
                        previous = replace(candidate)
                        running_value = candle.high
                        running_source = candle.index
                        if post_reset_second is not None:
                            self._append_reset(
                                direction,
                                candle,
                                previous.box_bottom,
                                previous.first_idx,
                                post_reset_second.display_time,
                            )
                            candidate = None
                            pending_reset_index = candle.index
                        else:
                            candidate = self._candidate_from_confirmation_remainder(
                                direction, previous, candle, analysis
                            )
                else:
                    if candle.high > candidate.box_top:
                        candidate.box_top = candle.high
                        candidate.box_top_source_idx = candle.index
                        candidate.box_top_source_time = candle.display_time
                    if candle.low < candidate.box_bottom:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        analysis = self._refine(direction, candidate, candle)
                        post_reset_second = self.bear.post_breakdown_reset(
                            analysis, candidate.box_top, candle
                        )
                        self._append_reaction(direction, candidate)
                        if (
                            stop_after_first_at_or_after is not None
                            and candidate.first_idx >= stop_after_first_at_or_after
                        ):
                            return self._result()
                        previous = replace(candidate)
                        running_value = candle.low
                        running_source = candle.index
                        if post_reset_second is not None:
                            self._append_reset(
                                direction,
                                candle,
                                previous.box_top,
                                previous.first_idx,
                                post_reset_second.display_time,
                            )
                            candidate = None
                            pending_reset_index = candle.index
                        else:
                            candidate = self._candidate_from_confirmation_remainder(
                                direction, previous, candle, analysis
                            )
            else:
                if direction == "bullish" and candle.tag == "RED":
                    top = max(running_value, candle.high)
                    top_source = running_source if running_value >= candle.high else candle.index
                    bottom_start = top_source + 1 if top_source < candle.index else candle.index
                    bottom, bottom_source = self.minimum_low(bottom_start, candle.index)
                    candidate = Candidate(
                        candle.index,
                        candle.display_time,
                        top_source,
                        self.candles[top_source].display_time,
                        top,
                        bottom_source.index,
                        bottom_source.display_time,
                        bottom,
                        mode="B",
                    )
                elif direction == "bearish" and candle.tag == "GREEN":
                    bottom = min(running_value, candle.low)
                    bottom_source = running_source if running_value <= candle.low else candle.index
                    top_start = bottom_source + 1 if bottom_source < candle.index else candle.index
                    top, top_source = self.maximum_high(top_start, candle.index)
                    candidate = Candidate(
                        candle.index,
                        candle.display_time,
                        top_source.index,
                        top_source.display_time,
                        top,
                        bottom_source,
                        self.candles[bottom_source].display_time,
                        bottom,
                        mode="B",
                    )
            if direction == "bullish" and (running_value is None or candle.high > running_value):
                running_value, running_source = candle.high, candle.index
            if direction == "bearish" and (running_value is None or candle.low < running_value):
                running_value, running_source = candle.low, candle.index
            index += 1

        return self._result()
```

### FUN-S-001 — `_decimal`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:_decimal`  
Source-Lines: 61-62  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _decimal(value: object) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))
```

### FUN-S-002 — `SZoneDetector.__init__`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector.__init__`  
Source-Lines: 66-130  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def __init__(
        self,
        direction: str,
        trend_reactions: Sequence[object],
        opposite_reactions: Sequence[object],
        trend_blue_lines: Sequence[object],
        a_zones: Sequence[object],
        chronology: object,
        start_index: int | None = None,
        end_index: int | None = None,
        opposite_resets: Sequence[object] = (),
        initial_order_geometry: Callable[[int, datetime, int], object | None] | None = None,
    ) -> None:
        self.policy = get_direction_policy(direction)
        self.direction = self.policy.name
        self._is_bullish = self.policy.is_bullish
        self._extreme_name = self.policy.extreme_attr
        self.order_direction = chronology.opposite_direction(direction)
        self.trend_reactions = list(trend_reactions)
        self.opposite_reactions = list(opposite_reactions)
        self.opposite_resets = list(opposite_resets)
        self.initial_order_geometry = initial_order_geometry
        self.trend_blue_lines = list(trend_blue_lines)
        self.a_zones = sorted(
            a_zones,
            key=lambda item: (
                getattr(item, "reaction_break_time"),
                int(getattr(item, "source_index")),
            ),
        )
        self.chronology = chronology
        self.candles = chronology.candles
        self.lower = chronology.raw_candles
        self.timeframe = chronology.timeframe
        self.candle_times = chronology.times
        self.lower_times = chronology.raw_times
        self.lower_index = chronology.lower_index
        self.start_index = 0 if start_index is None else int(start_index)
        self.end_index = (
            len(self.candles) - 1 if end_index is None else int(end_index)
        )
        if not 0 <= self.start_index <= self.end_index < len(self.candles):
            raise ValueError("Invalid S analysis range.")
        self.range_start = self.candle_times[self.start_index]
        self.range_end = self.candle_times[self.end_index] + self.timeframe
        self.order_audit: dict[tuple[int, int], dict[str, object]] = {}
        # A strict A stop reserves its continuation for S, including a race
        # that has no order or decision yet. A decided S reopens at its source.
        self.a_ownership_windows: list[tuple[datetime, datetime | None]] = []
        self._reset_blue_formation_by_reaction: dict[int, datetime] = {}
        self._opposite_by_first_index = {
            int(getattr(item, "first_idx")): (number, item)
            for number, item in enumerate(self.opposite_reactions, start=1)
        }

        for line in self.trend_blue_lines:
            if not bool(getattr(line, "calculation_valid", True)):
                continue
            if str(getattr(line, "kind")) != "reset":
                continue
            reaction_number = int(getattr(line, "reaction_number"))
            if reaction_number not in self._reset_blue_formation_by_reaction:
                self._reset_blue_formation_by_reaction[reaction_number] = (
                    self._blue_formation_time(line)
                )
```

### FUN-S-003 — `SZoneDetector._main_index`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._main_index`  
Source-Lines: 132-133  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _main_index(self, timestamp: datetime) -> int:
        return self.chronology.main_index(timestamp)
```

### FUN-S-004 — `SZoneDetector._lower_window`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._lower_window`  
Source-Lines: 135-138  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _lower_window(
        self, start: datetime, end: datetime | None
    ) -> Sequence[object]:
        return self.chronology.lower_window(start, end)
```

### FUN-S-005 — `SZoneDetector._reaction_confirmation_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._reaction_confirmation_time`  
Source-Lines: 140-143  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reaction_confirmation_time(
        self, reaction: object, direction: str
    ) -> datetime:
        return self.chronology.reaction_confirmation(direction, reaction)
```

### FUN-S-006 — `SZoneDetector.reaction_confirmation_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector.reaction_confirmation_time`  
Source-Lines: 145-149  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def reaction_confirmation_time(
        self, reaction: object, direction: str
    ) -> datetime:
        """Public chronology API used by cross-stage lifecycle ownership."""
        return self._reaction_confirmation_time(reaction, direction)
```

### FUN-S-007 — `SZoneDetector._reset_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._reset_time`  
Source-Lines: 152-153  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _reset_time(self, reset: object) -> datetime:
        return self.chronology.reset_time(reset)
```

### FUN-S-008 — `SZoneDetector._a_confirmation_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._a_confirmation_time`  
Source-Lines: 155-161  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _a_confirmation_time(self, zone: object) -> datetime:
        number = int(getattr(zone, "reaction_number"))
        if number < 1 or number > len(self.trend_reactions):
            raise ValueError("A refers to a missing trend reaction.")
        return self._reaction_confirmation_time(
            self.trend_reactions[number - 1], self.direction
        )
```

### FUN-S-009 — `SZoneDetector._trend_extreme`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._trend_extreme`  
Source-Lines: 163-166  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _trend_extreme(self, candle: object) -> Decimal:
        return _decimal(
            getattr(candle, self._extreme_name)
        )
```

### FUN-S-010 — `SZoneDetector._a_stopped`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._a_stopped`  
Source-Lines: 168-169  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _a_stopped(self, value: Decimal, level: Decimal) -> bool:
        return self.policy.strict_cross(value, level)
```

### FUN-S-011 — `SZoneDetector._first_a_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._first_a_stop`  
Source-Lines: 171-205  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_a_stop(
        self, level: Decimal, start: datetime
    ) -> tuple[int, datetime, datetime] | None:
        scan_start = max(start, self.range_start)
        left = bisect_left(self.lower_times, scan_start)
        right = bisect_left(self.lower_times, self.range_end)
        if right > left and self.lower_index is not None:
            position = (
                self.lower_index.first_less(left, right, level)
                if self._is_bullish
                else self.lower_index.first_greater(left, right, level)
            )
            if position is None:
                return None
            event_time = self.lower_times[position]
            index = self._main_index(event_time)
            return index, getattr(self.candles[index], "timestamp"), event_time

        lower_items = self.lower[left:right]
        for item in lower_items:
            if self._a_stopped(self._trend_extreme(item), level):
                event_time = getattr(item, "timestamp")
                index = self._main_index(event_time)
                return index, getattr(self.candles[index], "timestamp"), event_time
        if lower_items:
            return None
        start_index = max(self.start_index, bisect_left(self.candle_times, start))
        for item in self.candles[start_index : self.end_index + 1]:
            if self._a_stopped(self._trend_extreme(item), level):
                return (
                    int(getattr(item, "index")),
                    getattr(item, "timestamp"),
                    getattr(item, "timestamp"),
                )
        return None
```

### FUN-S-012 — `SZoneDetector.first_a_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector.first_a_stop`  
Source-Lines: 207-211  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def first_a_stop(
        self, level: Decimal, start: datetime
    ) -> tuple[int, datetime, datetime] | None:
        """Public lifecycle API for the first strict A stop."""
        return self._first_a_stop(level, start)
```

### FUN-S-013 — `SZoneDetector._first_order_after`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._first_order_after`  
Source-Lines: 214-292  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_order_after(
        self, a_stop_event_time: datetime
    ) -> tuple[int, object, datetime] | None:
        """Return the first healthy opposite Order Reaction after A-stop.

        A main candle can contain the exact A-stop after its opening timestamp.
        Therefore a canonical opposite Reaction whose First belongs to that
        same main candle is still eligible when its exact confirmation occurs
        strictly after the A-stop event.

        A local/bounded geometry is only a search aid.  If its physical
        identity ``(FirstIndex, BreakIndex)`` matches a published opposite
        Reaction, the published Reaction is canonical and must supply Mode,
        box ownership, and Mode-dependent Order-stop provenance.  This keeps
        local reconstruction from relabeling a healthy Mode-B Reaction as
        Mode-A.
        """
        gate_index = self._main_index(a_stop_event_time)

        # Same-main-candle chronology: the main candle's timestamp is not the
        # exact stop event.  Only a canonical, lifecycle-valid Reaction may be
        # admitted here, and its confirmation must remain strictly later.
        for number, reaction in enumerate(self.opposite_reactions, start=1):
            first_index = int(getattr(reaction, "first_idx"))
            if first_index < gate_index:
                continue
            if first_index > gate_index:
                break
            confirmation = self._reaction_confirmation_time(
                reaction, self.order_direction
            )
            if confirmation > a_stop_event_time:
                return number, reaction, confirmation

        # Otherwise use the existing exact-gate local search, then canonicalize
        # by physical identity before Mode-dependent stop calculation.
        if self.initial_order_geometry is not None:
            order = self.initial_order_geometry(
                gate_index, a_stop_event_time, self.end_index
            )
            if order is not None:
                identity = (
                    int(getattr(order, "first_idx")),
                    int(getattr(order, "break_idx")),
                )
                canonical = next((
                    (ordinal, item)
                    for ordinal, item in enumerate(self.opposite_reactions, 1)
                    if (
                        int(getattr(item, "first_idx")),
                        int(getattr(item, "break_idx")),
                    ) == identity
                ), None)
                if canonical is not None:
                    ordinal, order = canonical
                    confirmation = self._reaction_confirmation_time(
                        order, self.order_direction
                    )
                    if confirmation <= a_stop_event_time:
                        raise ValueError(
                            "Initial order must confirm after the exact A stop."
                        )
                    return ordinal, order, confirmation
                # A bounded/local geometry is only a search aid.  An Order
                # must be a real published opposite Reaction; unmatched local
                # geometry may not manufacture an Order identity.  Continue
                # into the canonical published-Reaction scan below.

        for number, reaction in enumerate(self.opposite_reactions, start=1):
            first_index = int(getattr(reaction, "first_idx"))
            first_time = getattr(self.candles[first_index], "timestamp")
            if first_time <= a_stop_event_time:
                continue
            confirmation = self._reaction_confirmation_time(
                reaction, self.order_direction
            )
            if confirmation > a_stop_event_time:
                return number, reaction, confirmation
        return None
```

### FUN-S-014 — `SZoneDetector._audit_stopped_a`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._audit_stopped_a`  
Source-Lines: 294-334  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _audit_stopped_a(self, zone: object) -> None:
        """Record the independent order gender created by one stopped A."""
        source_time = getattr(zone, "source_time")
        a_price = _decimal(getattr(zone, "price"))
        a_stop = self._first_a_stop(a_price, self._a_confirmation_time(zone))
        if a_stop is None:
            return
        _, _, a_stop_event_time = a_stop
        order_match = self._first_order_after(a_stop_event_time)
        if order_match is None:
            return
        order_number, order, order_confirmation_time = order_match
        (
            order_stop_level,
            order_stop_source_index,
            order_stop_source_time,
        ) = self._order_stop(order_number, order)
        identity = (
            int(getattr(order, "first_idx")),
            int(getattr(order, "break_idx")),
        )
        entry = self.order_audit.get(identity)
        if entry is None:
            entry = {
                "reaction_number": order_number,
                "reaction": order,
                "confirmation_time": order_confirmation_time,
                "stop_level": order_stop_level,
                "stop_source_index": order_stop_source_index,
                "stop_source_time": order_stop_source_time,
                # Keep the original scalar fields for E compatibility.  The
                # complete A-stop provenance is retained below.
                "a_source_time": source_time,
                "a_stop_event_time": a_stop_event_time,
                "a_causes": [],
            }
            self.order_audit[identity] = entry
        a_causes = entry.setdefault("a_causes", [])
        cause = (source_time, a_stop_event_time)
        if cause not in a_causes:
            a_causes.append(cause)
```

### FUN-S-015 — `SZoneDetector._candidate_source`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._candidate_source`  
Source-Lines: 336-351  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _candidate_source(
        self, start_index: int, end_index: int
    ) -> tuple[int, datetime, Decimal]:
        if end_index < start_index:
            raise ValueError("S candidate range ends before the A stop.")
        source = self.candles[start_index]
        value = self._trend_extreme(source)
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = self._trend_extreme(item)
            better = (
                self.policy.improves(candidate, value)
            )
            if better:
                source = item
                value = candidate
        return int(getattr(source, "index")), getattr(source, "timestamp"), value
```

### FUN-S-016 — `SZoneDetector._candidate_source_last`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._candidate_source_last`  
Source-Lines: 353-369  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _candidate_source_last(
        self, start_index: int, end_index: int
    ) -> tuple[int, datetime, Decimal]:
        """Return the directional extreme, assigning equality to the last candle."""
        if end_index < start_index:
            raise ValueError("S candidate range ends before it starts.")
        source = self.candles[start_index]
        value = self._trend_extreme(source)
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = self._trend_extreme(item)
            better_or_equal = (
                candidate <= value if self._is_bullish else candidate >= value
            )
            if better_or_equal:
                source = item
                value = candidate
        return int(getattr(source, "index")), getattr(source, "timestamp"), value
```

### FUN-S-017 — `SZoneDetector._first_trend_reaction_after_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._first_trend_reaction_after_order`  
Source-Lines: 371-380  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_trend_reaction_after_order(
        self, order_confirmation_time: datetime
    ) -> tuple[int, object, datetime] | None:
        for number, reaction in enumerate(self.trend_reactions, start=1):
            confirmation = self._reaction_confirmation_time(
                reaction, self.direction
            )
            if confirmation > order_confirmation_time:
                return number, reaction, confirmation
        return None
```

### FUN-S-018 — `SZoneDetector._nested_trend_reaction`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._nested_trend_reaction`  
Source-Lines: 383-411  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _nested_trend_reaction(
        self, order: object, order_confirmation_time: datetime
    ) -> tuple[int, object, datetime] | None:
        order_first_index = int(getattr(order, "first_idx"))
        order_break_index = int(getattr(order, "break_idx"))
        order_first = getattr(self.candles[order_first_index], "timestamp")
        order_top = _decimal(getattr(order, "box_top"))
        order_bottom = _decimal(getattr(order, "box_bottom"))
        for number, reaction in enumerate(self.trend_reactions, start=1):
            first_index = int(getattr(reaction, "first_idx"))
            break_index = int(getattr(reaction, "break_idx"))
            first = getattr(self.candles[first_index], "timestamp")
            if (
                first <= order_first
                or first_index <= order_first_index
                or break_index > order_break_index
                or first >= order_confirmation_time
            ):
                continue
            confirmation = self._reaction_confirmation_time(
                reaction, self.direction
            )
            wholly_inside = (
                _decimal(getattr(reaction, "box_top")) <= order_top
                and _decimal(getattr(reaction, "box_bottom")) >= order_bottom
            )
            if confirmation <= order_confirmation_time and wholly_inside:
                return number, reaction, confirmation
        return None
```

### FUN-S-019 — `SZoneDetector._simple_candidate`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._simple_candidate`  
Source-Lines: 413-420  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _simple_candidate(
        self, order: object, reaction: object
    ) -> tuple[int, datetime, Decimal]:
        """Use the inclusive order-Break to aligned-Break interval."""
        return self._candidate_source_last(
            int(getattr(order, "break_idx")),
            int(getattr(reaction, "break_idx")),
        )
```

### FUN-S-020 — `SZoneDetector._type3_reset_leg`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._type3_reset_leg`  
Source-Lines: 422-436  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _type3_reset_leg(
        self, reset: object
    ) -> tuple[int, datetime, Decimal] | None:
        """Return Order_B-equivalent inclusive Break-to-Reset geometry."""
        owner_match = self._opposite_by_first_index.get(
            int(getattr(reset, "from_first_idx"))
        )
        if owner_match is None:
            return None
        _, owner = owner_match
        start_index = int(getattr(owner, "break_idx"))
        end_index = self._main_index(self._reset_time(reset))
        if end_index < start_index:
            return None
        return self._candidate_source_last(start_index, end_index)
```

### FUN-S-021 — `SZoneDetector._type3_has_trend_reaction`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._type3_has_trend_reaction`  
Source-Lines: 438-446  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _type3_has_trend_reaction(
        self, a_stop_event: datetime, crossing: datetime
    ) -> bool:
        return any(
            a_stop_event
            < self._reaction_confirmation_time(reaction, self.direction)
            <= crossing
            for reaction in self.trend_reactions
        )
```

### FUN-S-022 — `SZoneDetector._first_type3`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._first_type3`  
Source-Lines: 448-516  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _first_type3(
        self,
        a_stop_event: datetime,
        deadline: datetime,
    ) -> tuple[int, datetime, Decimal, int, datetime, int, datetime, datetime] | None:
        """Find the first no-order Reset-leg S decision before a new order."""
        reset_times_by_owner: dict[int, list[datetime]] = {}
        for reset in self.opposite_resets:
            reset_times_by_owner.setdefault(
                int(getattr(reset, "from_first_idx")), []
            ).append(self._reset_time(reset))

        eligible: set[int] = set()
        for reaction in self.opposite_reactions:
            first_index = int(getattr(reaction, "first_idx"))
            confirmation = self._reaction_confirmation_time(
                reaction, self.order_direction
            )
            # A reaction whose Breakout and the A stop share the finest
            # available candle is already the pre-stop owner: its confirmation
            # threshold is crossed before the slightly deeper A-stop level in
            # the accepted Type-3 geometry.
            if confirmation > a_stop_event:
                continue
            if any(
                reset_time <= a_stop_event
                for reset_time in reset_times_by_owner.get(first_index, [])
            ):
                continue
            eligible.add(first_index)

        winner = None
        for reset in sorted(self.opposite_resets, key=self._reset_time):
            owner_first = int(getattr(reset, "from_first_idx"))
            reset_time = self._reset_time(reset)
            if (
                owner_first not in eligible
                or reset_time <= a_stop_event
                or reset_time >= deadline
            ):
                continue
            leg = self._type3_reset_leg(reset)
            if leg is None:
                continue
            source_index, source_time, boundary = leg
            crossing = None
            for item in self._lower_window(reset_time, deadline):
                if self._candidate_crossed(item, boundary):
                    crossing = getattr(item, "timestamp")
                    break
            if crossing is None:
                continue
            if not self._type3_has_trend_reaction(a_stop_event, crossing):
                continue
            decision_index = self._main_index(crossing)
            owner_number = self._opposite_by_first_index[owner_first][0]
            candidate = (
                source_index,
                source_time,
                boundary,
                decision_index,
                getattr(self.candles[decision_index], "timestamp"),
                owner_number,
                reset_time,
                crossing,
            )
            if winner is None or candidate[-1] < winner[-1]:
                winner = candidate
        return winner
```

### FUN-S-023 — `SZoneDetector._candidate_after_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._candidate_after_order`  
Source-Lines: 519-558  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _candidate_after_order(
        self,
        order_confirmation_time: datetime,
        reaction: object,
    ) -> tuple[int, datetime, Decimal]:
        """Find a candidate strictly after the order is confirmed.

        A reaction anchor is authoritative only when it is also after the
        order confirmation.  Otherwise the earliest extreme in the candles
        following the confirmation through the reaction First owns the
        candidate.
        """
        first_index = int(getattr(reaction, "first_idx"))
        start_index = bisect_left(self.candle_times, order_confirmation_time)
        start_index = max(self.start_index, min(start_index, first_index))
        anchor_index = getattr(reaction, "anchor_idx", None)
        anchor_value = getattr(reaction, "anchor_value", None)
        if anchor_index is not None and int(anchor_index) >= start_index:
            source = self.candles[int(anchor_index)]
            return (
                int(anchor_index),
                getattr(source, "timestamp"),
                _decimal(anchor_value),
            )
        candidate = self._candidate_source(start_index, first_index)
        containing_index = self._main_index(order_confirmation_time)
        if containing_index < start_index:
            # Do not discard the valid remainder of an intrabar confirmation
            # candle, or import an extreme that occurred before confirmation.
            remainder = self._lower_window(
                order_confirmation_time,
                self.candle_times[containing_index] + self.timeframe,
            )
            for item in remainder:
                value = self._trend_extreme(item)
                if self._a_stopped(value, candidate[2]) or value == candidate[2]:
                    candidate = (
                        containing_index, self.candle_times[containing_index], value
                    )
        return candidate
```

### FUN-S-024 — `SZoneDetector._a_source_event_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._a_source_event_time`  
Source-Lines: 560-567  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _a_source_event_time(self, zone: object) -> datetime:
        """Locate the source extreme, including an A-stop main candle."""
        source = getattr(zone, "source_time")
        price = _decimal(getattr(zone, "price"))
        for item in self._lower_window(source, source + self.timeframe):
            if self._trend_extreme(item) == price:
                return getattr(item, "timestamp")
        return source
```

### FUN-S-025 — `SZoneDetector._a_owned_by_s`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._a_owned_by_s`  
Source-Lines: 569-599  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _a_owned_by_s(self, zone: object) -> bool:
        event_time = self._a_source_event_time(zone)
        for start, end in self.a_ownership_windows:
            if not (start <= event_time and (end is None or event_time < end)):
                continue

            # A decided S normally owns this continuation. A fresh Reset-Blue
            # pair may open a new A only when the entire pair is born after
            # that S ownership began, Blue-1 has already stopped before Blue-2
            # forms, and Blue-2's stop candle is the A source. Open/undecided S
            # windows never grant this preemption.
            blue_1_source = getattr(zone, "blue_1_source_time", None)
            blue_2_source = getattr(zone, "blue_2_source_time", None)
            blue_1_stop = getattr(zone, "blue_1_stop_time", None)
            blue_2_stop = getattr(zone, "blue_2_stop_time", None)
            source_time = getattr(zone, "source_time", None)
            if (
                end is not None
                and blue_1_source is not None
                and blue_2_source is not None
                and blue_1_stop is not None
                and blue_2_stop is not None
                and source_time is not None
                and start < blue_1_source
                and blue_1_stop < blue_2_source
                and source_time == blue_2_stop
                and self._a_pair_is_reset_reset(zone)
            ):
                return False
            return True
        return False
```

### FUN-S-026 — `SZoneDetector._a_pair_is_reset_reset`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._a_pair_is_reset_reset`  
Source-Lines: 601-612  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _a_pair_is_reset_reset(self, zone: object) -> bool:
        """Whether both Blue Lines that define A are Reset Blues."""
        first = int(getattr(zone, "blue_1_ordinal", 0)) - 1
        second = int(getattr(zone, "blue_2_ordinal", 0)) - 1
        if not (0 <= first < len(self.trend_blue_lines)):
            return False
        if not (0 <= second < len(self.trend_blue_lines)):
            return False
        return (
            str(getattr(self.trend_blue_lines[first], "kind", "")) == "reset"
            and str(getattr(self.trend_blue_lines[second], "kind", "")) == "reset"
        )
```

### FUN-S-027 — `SZoneDetector.eligible_a_zones`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector.eligible_a_zones`  
Source-Lines: 615-617  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def eligible_a_zones(self) -> list[object]:
        """A candidates outside stopped-parent S ownership, before rendering."""
        return [zone for zone in self.a_zones if not self._a_owned_by_s(zone)]
```

### FUN-S-028 — `SZoneDetector._candidate_timing`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._candidate_timing`  
Source-Lines: 619-640  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _candidate_timing(
        self,
        a_stop_index: int,
        order: object,
        order_confirmation_time: datetime,
    ) -> str:
        """Return whether the candidate is formed before or after the order.

        Equality belongs to the after-order case. A strict penetration of the
        A-stop candle extreme is required before the candidate may belong to
        the pre-order leg.
        """
        stop_extreme = self._trend_extreme(self.candles[a_stop_index])
        boundary = _decimal(
            getattr(
                order,
                "box_bottom" if self._is_bullish else "box_top",
            )
        )
        if self._is_bullish:
            return "after" if boundary <= stop_extreme else "before"
        return "after" if boundary >= stop_extreme else "before"
```

### FUN-S-029 — `SZoneDetector._candidate_before_order`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._candidate_before_order`  
Source-Lines: 642-680  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _candidate_before_order(
        self,
        a_stop_index: int,
        order: object,
        a_stop_event_time: datetime | None = None,
    ) -> tuple[int, datetime, Decimal]:
        """Use the lowest/highest leg extreme from A-stop through order First."""
        if a_stop_event_time is None:
            a_stop_event_time = self.candle_times[a_stop_index]
        first_index = int(getattr(order, "first_idx"))
        candidate = self._candidate_source(a_stop_index, first_index)
        stop_candle_end = self.candle_times[a_stop_index] + self.timeframe
        eligible_stop_remainder = self._lower_window(
            a_stop_event_time, stop_candle_end
        )
        if not eligible_stop_remainder:
            return candidate
        source = eligible_stop_remainder[0]
        value = self._trend_extreme(source)
        for item in eligible_stop_remainder[1:]:
            item_value = self._trend_extreme(item)
            better = (
                self.policy.improves(item_value, value)
            )
            if better:
                source = item
                value = item_value
        later_candidate = (
            self._candidate_source(a_stop_index + 1, first_index)
            if first_index > a_stop_index
            else None
        )
        if later_candidate is not None:
            better = (
                self.policy.improves(later_candidate[2], value)
            )
            if better:
                return later_candidate
        return a_stop_index, self.candle_times[a_stop_index], value
```

### FUN-S-030 — `SZoneDetector._candidate_event_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._candidate_event_time`  
Source-Lines: 682-695  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _candidate_event_time(
        self,
        source_index: int,
        level: Decimal,
        not_before: datetime,
    ) -> datetime:
        """Return the first lower-timeframe event that forms the candidate."""
        source_time = self.candle_times[source_index]
        for item in self._lower_window(
            max(source_time, not_before), source_time + self.timeframe
        ):
            if self._trend_extreme(item) == level:
                return getattr(item, "timestamp")
        return max(source_time, not_before)
```

### FUN-S-031 — `SZoneDetector.candidate_event_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector.candidate_event_time`  
Source-Lines: 697-701  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def candidate_event_time(
        self, source_index: int, price: Decimal, fallback: datetime
    ) -> datetime:
        """Public lifecycle API for exact S candidate provenance."""
        return self._candidate_event_time(source_index, price, fallback)
```

### FUN-S-032 — `SZoneDetector._blue_formation_time`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._blue_formation_time`  
Source-Lines: 704-732  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _blue_formation_time(self, line: object) -> datetime:
        explicit = getattr(line, "formation_time", None)
        if explicit is not None:
            return explicit
        source_index = int(getattr(line, "source_index"))
        source_time = getattr(self.candles[source_index], "timestamp")
        if str(getattr(line, "kind")) != "reset":
            reaction_number = int(getattr(line, "reaction_number"))
            if 1 <= reaction_number <= len(self.trend_reactions):
                return self._reaction_confirmation_time(
                    self.trend_reactions[reaction_number - 1], self.direction
                )
            return source_time
        broken_level = getattr(line, "broken_level", None)
        if broken_level is None:
            return source_time
        end = source_time + self.timeframe
        for item in self._lower_window(source_time, end):
            value = _decimal(
                getattr(item, "low" if self.direction == "bullish" else "high")
            )
            crossed = (
                value < _decimal(broken_level)
                if self.direction == "bullish"
                else value > _decimal(broken_level)
            )
            if crossed:
                return getattr(item, "timestamp")
        return source_time
```

### FUN-S-033 — `SZoneDetector._candidate_cross_has_blue`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._candidate_cross_has_blue`  
Source-Lines: 734-749  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _candidate_cross_has_blue(
        self,
        reaction_number: int,
        event_time: datetime,
    ) -> bool:
        """Return whether the candidate cross has its aligned Reset Blue.

        The Reset Blue belongs to the same-direction reaction, but it does
        not have to be drawn on the candidate candle or on the candle that
        crosses the candidate.  Its exact formation event only needs to be
        no later than the candidate crossing event.
        """
        if reaction_number < 1 or reaction_number > len(self.trend_reactions):
            return False
        formation_time = self._reset_blue_formation_by_reaction.get(reaction_number)
        return formation_time is not None and formation_time <= event_time
```

### FUN-S-034 — `SZoneDetector._has_ordinary_trend_reaction`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._has_ordinary_trend_reaction`  
Source-Lines: 751-768  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _has_ordinary_trend_reaction(
        self, behavior_start: datetime, event_time: datetime
    ) -> bool:
        """Return whether ordinary aligned geometry completed in the leg.

        Order/S behavior deliberately consumes the maintained reaction output
        as geometry, without requiring its Reset Blue to own the event.  The
        reaction may complete before or after the opposite order confirms, but
        it must complete after the active A-stop behavior begins and no later
        than the candidate crossing.
        """
        for reaction in self.trend_reactions:
            confirmation = self._reaction_confirmation_time(
                reaction, self.direction
            )
            if behavior_start < confirmation <= event_time:
                return True
        return False
```

### FUN-S-035 — `SZoneDetector._order_stop`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._order_stop`  
Source-Lines: 771-780  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _order_stop(
        self, order_number: int, reaction: object
    ) -> tuple[Decimal, int, datetime]:
        return self.chronology.canonical_order_stop(
            self.order_direction,
            order_number,
            reaction,
            self.opposite_reactions,
            start_index=self.start_index,
        )
```

### FUN-S-036 — `SZoneDetector._candidate_crossed`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._candidate_crossed`  
Source-Lines: 782-784  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _candidate_crossed(self, candle: object, level: Decimal) -> bool:
        value = self._trend_extreme(candle)
        return self._a_stopped(value, level)
```

### FUN-S-037 — `SZoneDetector._order_stop_crossed`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._order_stop_crossed`  
Source-Lines: 786-789  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _order_stop_crossed(self, candle: object, level: Decimal) -> bool:
        if self.order_direction == "bearish":
            return _decimal(getattr(candle, "high")) > level
        return _decimal(getattr(candle, "low")) < level
```

### FUN-S-038 — `SZoneDetector._decision`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._decision`  
Source-Lines: 791-883  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _decision(
        self,
        candidate_level: Decimal,
        order_stop_level: Decimal,
        start: datetime,
        trend_reaction_number: int,
        behavior_start: datetime,
        candidate_start: datetime | None = None,
        fallback_on_unqualified_cross: bool = False,
    ) -> tuple[str, int, datetime, datetime] | None:
        lower_items = self._lower_window(max(start, self.range_start), self.range_end)
        for item in lower_items:
            event_time = getattr(item, "timestamp")
            candidate_cross = (
                self._candidate_crossed(item, candidate_level)
                and (candidate_start is None or event_time >= candidate_start)
            )
            order_cross = self._order_stop_crossed(item, order_stop_level)
            if candidate_cross and order_cross:
                return None
            if order_cross:
                index = self._main_index(event_time)
                return (
                    "red",
                    index,
                    getattr(self.candles[index], "timestamp"),
                    event_time,
                )
            if (
                candidate_cross
                and (
                self._candidate_cross_has_blue(trend_reaction_number, event_time)
                or self._has_ordinary_trend_reaction(behavior_start, event_time)
                )
            ):
                index = self._main_index(event_time)
                return (
                    "blue",
                    index,
                    getattr(self.candles[index], "timestamp"),
                    event_time,
                )
            if candidate_cross and fallback_on_unqualified_cross:
                index = self._main_index(event_time)
                return (
                    "fallback",
                    index,
                    getattr(self.candles[index], "timestamp"),
                    event_time,
                )
        if lower_items:
            return None

        start_index = max(
            self.start_index, bisect_right(self.candle_times, start) - 1
        )
        for item in self.candles[start_index : self.end_index + 1]:
            event_time = getattr(item, "timestamp")
            candidate_cross = (
                self._candidate_crossed(item, candidate_level)
                and (candidate_start is None or event_time >= candidate_start)
            )
            order_cross = self._order_stop_crossed(item, order_stop_level)
            if candidate_cross and order_cross:
                return None
            if order_cross:
                return (
                    "red",
                    int(getattr(item, "index")),
                    event_time,
                    event_time,
                )
            if (
                candidate_cross
                and (
                self._candidate_cross_has_blue(trend_reaction_number, event_time)
                or self._has_ordinary_trend_reaction(behavior_start, event_time)
                )
            ):
                return (
                    "blue",
                    int(getattr(item, "index")),
                    event_time,
                    event_time,
                )
            if candidate_cross and fallback_on_unqualified_cross:
                return (
                    "fallback",
                    int(getattr(item, "index")),
                    event_time,
                    event_time,
                )
        return None
```

### FUN-S-039 — `SZoneDetector._build_type3_zone`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._build_type3_zone`  
Source-Lines: 885-941  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _build_type3_zone(
        self,
        zone: object,
        a_ordinal: int,
        a_price: Decimal,
        a_stop: tuple[int, datetime, datetime],
        type3: tuple[int, datetime, Decimal, int, datetime, int, datetime, datetime],
    ) -> SZone:
        """Build the order-free Blue Type-3 continuation for one stopped A."""
        a_stop_index, a_stop_time, a_stop_event_time = a_stop
        (
            source_index,
            source_time,
            price,
            decision_index,
            decision_time,
            reset_reaction_number,
            reset_time,
            decision_event_time,
        ) = type3
        return SZone(
            direction=self.direction,
            color="blue",
            formation_type="type3",
            a_ordinal=a_ordinal,
            a_source_index=int(getattr(zone, "source_index")),
            a_source_time=getattr(zone, "source_time"),
            a_price=a_price,
            a_stop_index=a_stop_index,
            a_stop_time=a_stop_time,
            a_stop_event_time=a_stop_event_time,
            order_direction=None,
            order_reaction_number=None,
            order_mode=None,
            order_first_index=None,
            order_first_time=None,
            order_break_index=None,
            order_break_time=None,
            order_confirmation_time=None,
            order_box_top=None,
            order_box_top_source_index=None,
            order_box_top_source_time=None,
            order_box_bottom=None,
            order_box_bottom_source_index=None,
            order_box_bottom_source_time=None,
            order_stop_level=None,
            order_stop_source_index=None,
            order_stop_source_time=None,
            reset_reaction_number=reset_reaction_number,
            reset_time=reset_time,
            source_index=source_index,
            source_time=source_time,
            price=price,
            decision_index=decision_index,
            decision_time=decision_time,
            decision_event_time=decision_event_time,
        )
```

### FUN-S-040 — `SZoneDetector._build_order_backed_zone`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector._build_order_backed_zone`  
Source-Lines: 943-1112  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _build_order_backed_zone(
        self,
        zone: object,
        a_ordinal: int,
        a_price: Decimal,
        a_stop: tuple[int, datetime, datetime],
        order_match: tuple[int, object, datetime],
    ) -> SZone | None:
        """Resolve Simple/Advanced S ownership after a stopped A finds an Order."""
        a_stop_index, a_stop_time, a_stop_event_time = a_stop
        order_number, order, order_confirmation_time = order_match
        order_stop_level, order_stop_source_index, order_stop_source_time = (
            self._order_stop(order_number, order)
        )
        candidate_timing = self._candidate_timing(
            a_stop_index, order, order_confirmation_time
        )
        pre_order_candidate = (
            self._candidate_before_order(
                a_stop_index,
                order,
                a_stop_event_time=a_stop_event_time,
            )
            if candidate_timing == "before"
            else None
        )

        decision_behavior_start = a_stop_event_time
        decision = None
        use_pre_order_candidate = False
        if pre_order_candidate is not None:
            formation_type = "simple"
            source_index, source_time, price = pre_order_candidate
            red_source = pre_order_candidate
            trend_reaction_number = 0
            candidate_event_time = self._candidate_event_time(
                source_index, price, a_stop_event_time
            )
            decision_behavior_start = candidate_event_time
            decision = self._decision(
                price,
                order_stop_level,
                order_confirmation_time,
                trend_reaction_number,
                decision_behavior_start,
                candidate_event_time,
                fallback_on_unqualified_cross=True,
            )
            if decision is None:
                return None
            if decision[0] != "fallback":
                use_pre_order_candidate = True
            else:
                decision = None

        advanced_blue = False
        if not use_pre_order_candidate:
            decision_behavior_start = a_stop_event_time
            nested_match = self._nested_trend_reaction(
                order, order_confirmation_time
            )
            advanced_blue = nested_match is not None

        if not use_pre_order_candidate and advanced_blue:
            formation_type = "advanced"
            red_source = None
            trend_reaction_number, _, trend_confirmation_time = nested_match
            source_index = int(
                getattr(
                    order,
                    "box_bottom_source_idx"
                    if self.direction == "bullish"
                    else "box_top_source_idx",
                )
            )
            source_time = getattr(self.candles[source_index], "timestamp")
            price = self._trend_extreme(self.candles[source_index])
            decision_candidate_start = trend_confirmation_time
        elif not use_pre_order_candidate:
            formation_type = "simple"
            trend_match = self._first_trend_reaction_after_order(
                order_confirmation_time
            )
            if trend_match is None:
                return None
            trend_reaction_number, trend_reaction, trend_confirmation_time = (
                trend_match
            )
            source_index, source_time, price = self._simple_candidate(
                order, trend_reaction
            )
            red_source = (
                pre_order_candidate
                if pre_order_candidate is not None
                else self._candidate_after_order(
                    order_confirmation_time, trend_reaction
                )
            )
            decision_candidate_start = trend_confirmation_time

        if decision is None:
            decision = self._decision(
                price,
                order_stop_level,
                order_confirmation_time,
                trend_reaction_number,
                decision_behavior_start,
                decision_candidate_start,
            )
        if decision is None:
            return None

        color, decision_index, decision_time, decision_event_time = decision
        order_break_index = int(getattr(order, "break_idx"))
        if color == "red":
            if use_pre_order_candidate and red_source is not None:
                source_index, source_time, price = red_source
            else:
                source_index, source_time, price = self._candidate_source(
                    order_break_index, decision_index
                )

        order_first_index = int(getattr(order, "first_idx"))
        box_top_source_index = int(getattr(order, "box_top_source_idx"))
        box_bottom_source_index = int(getattr(order, "box_bottom_source_idx"))
        return SZone(
            direction=self.direction,
            color=color,
            formation_type=formation_type,
            a_ordinal=a_ordinal,
            a_source_index=int(getattr(zone, "source_index")),
            a_source_time=getattr(zone, "source_time"),
            a_price=a_price,
            a_stop_index=a_stop_index,
            a_stop_time=a_stop_time,
            a_stop_event_time=a_stop_event_time,
            order_direction=self.order_direction,
            order_reaction_number=order_number,
            order_mode=str(getattr(order, "mode")),
            order_first_index=order_first_index,
            order_first_time=getattr(
                self.candles[order_first_index], "timestamp"
            ),
            order_break_index=order_break_index,
            order_break_time=getattr(
                self.candles[order_break_index], "timestamp"
            ),
            order_confirmation_time=order_confirmation_time,
            order_box_top=_decimal(getattr(order, "box_top")),
            order_box_top_source_index=box_top_source_index,
            order_box_top_source_time=getattr(
                self.candles[box_top_source_index], "timestamp"
            ),
            order_box_bottom=_decimal(getattr(order, "box_bottom")),
            order_box_bottom_source_index=box_bottom_source_index,
            order_box_bottom_source_time=getattr(
                self.candles[box_bottom_source_index], "timestamp"
            ),
            order_stop_level=order_stop_level,
            order_stop_source_index=order_stop_source_index,
            order_stop_source_time=order_stop_source_time,
            reset_reaction_number=None,
            reset_time=None,
            source_index=source_index,
            source_time=source_time,
            price=price,
            decision_index=decision_index,
            decision_time=decision_time,
            decision_event_time=decision_event_time,
        )
```

### FUN-S-041 — `SZoneDetector.detect`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:SZoneDetector.detect`  
Source-Lines: 1114-1180  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect(self) -> list[SZone]:
        output: list[SZone] = []
        self.a_ownership_windows.clear()
        self.order_audit.clear()
        for zone in self.a_zones:
            self._audit_stopped_a(zone)

        cycle_start_time = self.range_start
        for zone_offset, zone in enumerate(self.a_zones):
            a_ordinal = zone_offset + 1
            if self._a_owned_by_s(zone):
                continue
            source_time = getattr(zone, "source_time")
            if source_time < cycle_start_time or (
                source_time == cycle_start_time and output
            ):
                continue

            next_a_confirmation = (
                self._a_confirmation_time(self.a_zones[zone_offset + 1])
                if zone_offset + 1 < len(self.a_zones)
                else None
            )
            a_price = _decimal(getattr(zone, "price"))
            a_stop = self._first_a_stop(a_price, self._a_confirmation_time(zone))
            if a_stop is None:
                continue
            _, _, a_stop_event_time = a_stop
            order_match = self._first_order_after(a_stop_event_time)
            if (
                next_a_confirmation is not None
                and a_stop_event_time >= next_a_confirmation
            ):
                continue

            self.a_ownership_windows.append((a_stop_event_time, None))
            type3_deadline = (
                order_match[2] if order_match is not None else self.range_end
            )
            type3 = self._first_type3(a_stop_event_time, type3_deadline)
            if type3 is not None:
                s_zone = self._build_type3_zone(
                    zone, a_ordinal, a_price, a_stop, type3
                )
            elif order_match is not None:
                s_zone = self._build_order_backed_zone(
                    zone, a_ordinal, a_price, a_stop, order_match
                )
                if s_zone is None:
                    continue
            else:
                continue

            output.append(s_zone)
            cycle_start_time = s_zone.source_time
            self.a_ownership_windows[-1] = (
                a_stop_event_time,
                max(
                    a_stop_event_time,
                    s_zone.decision_event_time + timedelta(microseconds=1),
                ),
            )

        return sorted(
            output,
            key=lambda item: (item.source_time, item.decision_event_time),
        )
```

### FUN-S-042 — `detect_s_zones`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `s_zone_detector.py:detect_s_zones`  
Source-Lines: 1183-1206  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def detect_s_zones(
    direction: str,
    trend_reactions: Sequence[object],
    opposite_reactions: Sequence[object],
    trend_blue_lines: Sequence[object],
    a_zones: Sequence[object],
    chronology: object,
    start_index: int | None = None,
    end_index: int | None = None,
    opposite_resets: Sequence[object] = (),
    initial_order_geometry: Callable[[int, datetime, int], object | None] | None = None,
) -> list[SZone]:
    return SZoneDetector(
        direction,
        trend_reactions,
        opposite_reactions,
        trend_blue_lines,
        a_zones,
        chronology,
        start_index,
        end_index,
        opposite_resets,
        initial_order_geometry,
    ).detect()
```

### FUN-PIPE-001 — `emit_progress`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:emit_progress`  
Source-Lines: 29-34  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def emit_progress(status: str, label: str, duration_ms: float | None = None):
    """Send machine-readable lifecycle events without contaminating JSON stdout."""
    event = {"status": status, "label": label}
    if duration_ms is not None:
        event["durationMs"] = round(duration_ms, 2)
    print(f"QG_PROGRESS:{json.dumps(event, separators=(',', ':'))}", file=sys.stderr, flush=True)
```

### FUN-PIPE-002 — `timed`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:timed`  
Source-Lines: 37-46  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def timed(timings: dict[str, float], label: str, work):
    """Measure an existing pipeline phase without changing its inputs or output."""
    started = perf_counter()
    emit_progress("started", label)
    try:
        return work()
    finally:
        duration_ms = (perf_counter() - started) * 1000
        timings[label] = timings.get(label, 0.0) + duration_ms
        emit_progress("completed", label, duration_ms)
```

### FUN-PIPE-003 — `load_module`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:load_module`  
Source-Lines: 49-56  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load reaction engine: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
```

### FUN-PIPE-004 — `load_engine`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:load_engine`  
Source-Lines: 59-60  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def load_engine(path: Path):
    return load_module("reaction_engine", path)
```

### FUN-PIPE-005 — `decimal`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:decimal`  
Source-Lines: 63-64  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def decimal(value: object) -> Decimal:
    return Decimal(str(value))
```

### FUN-PIPE-006 — `local_datetime`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:local_datetime`  
Source-Lines: 67-69  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def local_datetime(epoch_value: int) -> datetime:
    """Convert an epoch to the project's naive Asia/Tehran datetime."""
    return datetime.fromtimestamp(epoch_value, TEHRAN).replace(tzinfo=None)
```

### FUN-PIPE-007 — `epoch`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:epoch`  
Source-Lines: 72-74  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def epoch(local: datetime) -> int:
    """Convert a project-local naive datetime back to epoch seconds."""
    return int(local.replace(tzinfo=TEHRAN).timestamp())
```

### FUN-PIPE-008 — `isolate_raw_range`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:isolate_raw_range`  
Source-Lines: 77-84  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def isolate_raw_range(
    source_rows: list[dict], from_time: int, end_exclusive: int,
) -> list[dict]:
    """Slice validated chronological rows without scanning the full source."""
    row_time = lambda row: int(row["time"])
    first = bisect_left(source_rows, from_time, key=row_time)
    last = bisect_left(source_rows, end_exclusive, lo=first, key=row_time)
    return source_rows[first:last]
```

### FUN-PIPE-009 — `_price_normalizer`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:_price_normalizer`  
Source-Lines: 87-100  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def _price_normalizer():
    """Return a cached Decimal normalizer scoped to one RAW-loading pass."""
    cache: dict[tuple[type, object], Decimal] = {}

    def normalize(value: object) -> Decimal:
        key = (type(value), value)
        try:
            return cache[key]
        except KeyError:
            result = decimal(value)
            cache[key] = result
            return result

    return normalize
```

### FUN-PIPE-010 — `build_native_raw_candles`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:build_native_raw_candles`  
Source-Lines: 103-131  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def build_native_raw_candles(engine, rows: list[dict]) -> list[object]:
    """Create one engine Candle per original RAW row without aggregation."""
    normalize = _price_normalizer()
    candle_type = engine.Candle
    classify = engine.classify_candle_color
    candles: list[object] = []
    append = candles.append
    fmt = _DTFMT.format
    for index, row in enumerate(rows):
        timestamp = int(row["time"])
        open_price = normalize(row["open"])
        high = normalize(row["high"])
        low = normalize(row["low"])
        close = normalize(row["close"])
        stamp = local_datetime(timestamp)
        append(candle_type(
            index=index,
            timestamp=stamp,
            display_time=fmt(
                stamp.year, stamp.month, stamp.day,
                stamp.hour, stamp.minute, stamp.second,
            ),
            tag=classify(open_price, close),
            open=open_price,
            high=high,
            low=low,
            close=close,
        ))
    return candles
```

### FUN-PIPE-011 — `build_timeframe_buckets`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:build_timeframe_buckets`  
Source-Lines: 134-158  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def build_timeframe_buckets(
    rows: list[dict], raw_candles: list[object], timeframe: int
) -> list[dict]:
    """Aggregate native RAW candles into the requested main timeframe."""
    if len(rows) != len(raw_candles):
        raise ValueError("RAW rows and native candle views must stay index-aligned.")
    buckets: list[dict] = []
    current = None
    for row, candle in zip(rows, raw_candles):
        timestamp = int(row["time"])
        bucket_time = timestamp if timeframe == 1 else timestamp // timeframe * timeframe
        if current is None or current["time"] != bucket_time:
            current = {
                "time": bucket_time,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
            }
            buckets.append(current)
        else:
            current["high"] = max(current["high"], candle.high)
            current["low"] = min(current["low"], candle.low)
            current["close"] = candle.close
    return buckets
```

### FUN-PIPE-012 — `build_candle_objects`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:build_candle_objects`  
Source-Lines: 161-188  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def build_candle_objects(engine, buckets: list[dict]):
    """Create maintained engine candles from already-normalized buckets."""
    candles = []
    append = candles.append
    candle_type = engine.Candle
    classify = engine.classify_candle_color
    local = local_datetime
    fmt = _DTFMT.format
    for index, item in enumerate(buckets):
        stamp = local(item["time"])
        append(candle_type(
            index=index,
            timestamp=stamp,
            display_time=fmt(
                stamp.year,
                stamp.month,
                stamp.day,
                stamp.hour,
                stamp.minute,
                stamp.second,
            ),
            tag=classify(item["open"], item["close"]),
            open=item["open"],
            high=item["high"],
            low=item["low"],
            close=item["close"],
        ))
    return candles
```

### FUN-PIPE-013 — `serialize`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:serialize`  
Source-Lines: 191-236  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def serialize(result, start_index=None, end_index=None, reaction_transform=None):
    def selected(index):
        return (
            start_index is None
            or end_index is None
            or start_index <= int(index) <= end_index
        )

    resets = [{
        "index": item.index,
        "time": epoch(datetime.strptime(item.display_time, "%Y-%m-%d %H:%M:%S")),
        "secondTime": (
            epoch(datetime.strptime(item.second_time, "%Y-%m-%d %H:%M:%S"))
            if item.second_time is not None
            else None
        ),
        "brokenLevel": str(item.broken_level),
        "fromFirstIndex": item.from_first_idx,
    } for item in result.resets if selected(item.index)]
    reactions = []
    for item in result.reactions:
        if not selected(item.first_idx):
            continue
        public_item = reaction_transform(item) if reaction_transform is not None else item
        reactions.append({
            "firstIndex": public_item.first_idx,
            "firstTime": epoch(datetime.strptime(public_item.first_time, "%Y-%m-%d %H:%M:%S")),
            "boxTopSourceIndex": public_item.box_top_source_idx,
            "boxTopSourceTime": epoch(
                datetime.strptime(
                    public_item.box_top_source_time, "%Y-%m-%d %H:%M:%S"
                )
            ),
            "boxTop": str(public_item.box_top),
            "boxBottomSourceIndex": public_item.box_bottom_source_idx,
            "boxBottomSourceTime": epoch(
                datetime.strptime(
                    public_item.box_bottom_source_time, "%Y-%m-%d %H:%M:%S"
                )
            ),
            "boxBottom": str(public_item.box_bottom),
            "breakIndex": public_item.break_idx,
            "breakTime": epoch(datetime.strptime(public_item.break_time, "%Y-%m-%d %H:%M:%S")),
            "mode": public_item.mode,
        })
    return reactions, resets
```

### FUN-PIPE-014 — `serialize_blue_lines`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:serialize_blue_lines`  
Source-Lines: 239-261  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def serialize_blue_lines(items, start_index=None, end_index=None):
    def selected(index):
        return (
            start_index is None
            or end_index is None
            or start_index <= int(index) <= end_index
        )

    return [{
        "direction": item.direction,
        "kind": item.kind,
        "reactionNumber": item.reaction_number,
        "previousStrikeCount": item.previous_strike_count,
        "strikeCount": item.strike_count,
        "fibonacciLevel": str(item.fibonacci_level) if item.fibonacci_level is not None else None,
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "sourceExtreme": str(item.source_extreme),
        "brokenLevel": str(item.broken_level) if item.broken_level is not None else None,
        "linePrice": str(item.line_price),
        "startTime": epoch(item.start_time),
        "endTime": epoch(item.end_time),
    } for item in items if selected(getattr(item, "source_index"))]
```

### FUN-PIPE-015 — `serialize_a_zones`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:serialize_a_zones`  
Source-Lines: 264-288  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def serialize_a_zones(items):
    return [{
        "direction": item.direction,
        "blue1Ordinal": item.blue_1_ordinal,
        "blue2Ordinal": item.blue_2_ordinal,
        "blue1SourceTime": epoch(item.blue_1_source_time),
        "blue2SourceTime": epoch(item.blue_2_source_time),
        "blue1StopTime": epoch(item.blue_1_stop_time),
        "blue2StopTime": epoch(item.blue_2_stop_time),
        "blue1StopLevel": str(item.blue_1_stop_level),
        "blue2StopLevel": str(item.blue_2_stop_level),
        "continuationLevel": str(item.continuation_level),
        "continuationSourceIndex": item.continuation_source_index,
        "continuationSourceTime": epoch(item.continuation_source_time),
        "triggerIndex": item.trigger_index,
        "triggerTime": epoch(item.trigger_time),
        "triggerEventTime": epoch(item.trigger_event_time),
        "reactionNumber": item.reaction_number,
        "reactionFirstTime": epoch(item.reaction_first_time),
        "reactionBreakTime": epoch(item.reaction_break_time),
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "calculationValid": True,
    } for item in items]
```

### FUN-PIPE-016 — `serialize_s_zones`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:serialize_s_zones`  
Source-Lines: 291-353  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def serialize_s_zones(items):
    return [{
        "direction": item.direction,
        "color": item.color,
        "formationType": item.formation_type,
        "aOrdinal": item.a_ordinal,
        "aSourceIndex": item.a_source_index,
        "aSourceTime": epoch(item.a_source_time),
        "aPrice": str(item.a_price),
        "aStopIndex": item.a_stop_index,
        "aStopTime": epoch(item.a_stop_time),
        "aStopEventTime": epoch(item.a_stop_event_time),
        "orderDirection": item.order_direction,
        "orderReactionNumber": item.order_reaction_number,
        "orderMode": item.order_mode,
        "orderFirstIndex": item.order_first_index,
        "orderFirstTime": (
            epoch(item.order_first_time) if item.order_first_time is not None else None
        ),
        "orderBreakIndex": item.order_break_index,
        "orderBreakTime": (
            epoch(item.order_break_time) if item.order_break_time is not None else None
        ),
        "orderConfirmationTime": (
            epoch(item.order_confirmation_time)
            if item.order_confirmation_time is not None
            else None
        ),
        "orderBoxTop": str(item.order_box_top) if item.order_box_top is not None else None,
        "orderBoxTopSourceIndex": item.order_box_top_source_index,
        "orderBoxTopSourceTime": (
            epoch(item.order_box_top_source_time)
            if item.order_box_top_source_time is not None
            else None
        ),
        "orderBoxBottom": (
            str(item.order_box_bottom) if item.order_box_bottom is not None else None
        ),
        "orderBoxBottomSourceIndex": item.order_box_bottom_source_index,
        "orderBoxBottomSourceTime": (
            epoch(item.order_box_bottom_source_time)
            if item.order_box_bottom_source_time is not None
            else None
        ),
        "orderStopLevel": (
            str(item.order_stop_level) if item.order_stop_level is not None else None
        ),
        "orderStopSourceIndex": item.order_stop_source_index,
        "orderStopSourceTime": (
            epoch(item.order_stop_source_time)
            if item.order_stop_source_time is not None
            else None
        ),
        "resetReactionNumber": item.reset_reaction_number,
        "resetTime": epoch(item.reset_time) if item.reset_time is not None else None,
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "decisionIndex": item.decision_index,
        "decisionTime": epoch(item.decision_time),
        "decisionEventTime": epoch(item.decision_event_time),
        "calculationValid": True,
    } for item in items]
```

### FUN-PIPE-017 — `serialize_e_zones`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:serialize_e_zones`  
Source-Lines: 356-404  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def serialize_e_zones(items):
    return [{
        "direction": item.direction,
        "family": item.family,
        "number": item.number,
        "parentType": item.parent_type,
        "parentSourceIndex": item.parent_source_index,
        "parentSourceTime": epoch(item.parent_source_time),
        "parentPrice": str(item.parent_price),
        "parentStopIndex": item.parent_stop_index,
        "parentStopTime": epoch(item.parent_stop_time),
        "parentStopEventTime": epoch(item.parent_stop_event_time),
        "orderDirection": item.order_direction,
        "orderReactionNumber": item.order_reaction_number,
        "orderMode": item.order_mode,
        "orderCauses": list(item.order_causes),
        "orderParentStopCauseTime": (
            epoch(item.order_parent_stop_cause_time)
            if item.order_parent_stop_cause_time is not None else None
        ),
        "orderResetLegResetTime": (
            epoch(item.order_reset_leg_reset_time)
            if item.order_reset_leg_reset_time is not None else None
        ),
        "orderResetLegBreakTime": (
            epoch(item.order_reset_leg_break_time)
            if item.order_reset_leg_break_time is not None else None
        ),
        "orderFirstIndex": item.order_first_index,
        "orderFirstTime": epoch(item.order_first_time),
        "orderBreakIndex": item.order_break_index,
        "orderBreakTime": epoch(item.order_break_time),
        "orderConfirmationTime": epoch(item.order_confirmation_time),
        "orderBoxTop": str(item.order_box_top),
        "orderBoxTopSourceIndex": item.order_box_top_source_index,
        "orderBoxTopSourceTime": epoch(item.order_box_top_source_time),
        "orderBoxBottom": str(item.order_box_bottom),
        "orderBoxBottomSourceIndex": item.order_box_bottom_source_index,
        "orderBoxBottomSourceTime": epoch(item.order_box_bottom_source_time),
        "orderStopLevel": str(item.order_stop_level),
        "orderStopSourceIndex": item.order_stop_source_index,
        "orderStopSourceTime": epoch(item.order_stop_source_time),
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "decisionIndex": item.decision_index,
        "decisionTime": epoch(item.decision_time),
        "decisionEventTime": epoch(item.decision_event_time),
    } for item in items]
```

### FUN-PIPE-018 — `serialize_stopalls`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:serialize_stopalls`  
Source-Lines: 407-457  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def serialize_stopalls(items):
    return [{
        "direction": item.direction,
        "number": item.number,
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "decisionIndex": item.decision_index,
        "decisionTime": epoch(item.decision_time),
        "decisionEventTime": epoch(item.decision_event_time),
        "gateType": item.gate_type,
        "gateEventTime": epoch(item.gate_event_time),
        "stoppedBehaviorType": item.stopped_behavior_type,
        "stoppedBehaviorKey": item.stopped_behavior_key,
        "stoppedBehaviorCount": item.stopped_behavior_count,
        "underlyingEFamily": item.underlying_e_family,
        "underlyingENumber": item.underlying_e_number,
        "orderDirection": item.order_direction,
        "orderReactionNumber": item.order_reaction_number,
        "orderMode": item.order_mode,
        "orderCauses": list(item.order_causes),
        "orderParentStopCauseTime": (
            epoch(item.order_parent_stop_cause_time)
            if item.order_parent_stop_cause_time is not None else None
        ),
        "orderResetLegResetTime": (
            epoch(item.order_reset_leg_reset_time)
            if item.order_reset_leg_reset_time is not None else None
        ),
        "orderResetLegBreakTime": (
            epoch(item.order_reset_leg_break_time)
            if item.order_reset_leg_break_time is not None else None
        ),
        "orderFirstIndex": item.order_first_index,
        "orderFirstTime": epoch(item.order_first_time),
        "orderBreakIndex": item.order_break_index,
        "orderBreakTime": epoch(item.order_break_time),
        "orderConfirmationTime": epoch(item.order_confirmation_time),
        "orderBoxTop": str(item.order_box_top),
        "orderBoxTopSourceIndex": item.order_box_top_source_index,
        "orderBoxTopSourceTime": epoch(item.order_box_top_source_time),
        "orderBoxBottom": str(item.order_box_bottom),
        "orderBoxBottomSourceIndex": item.order_box_bottom_source_index,
        "orderBoxBottomSourceTime": epoch(item.order_box_bottom_source_time),
        "orderStopLevel": str(item.order_stop_level),
        "orderStopSourceIndex": item.order_stop_source_index,
        "orderStopSourceTime": epoch(item.order_stop_source_time),
        "stopIndex": item.stop_index,
        "stopTime": epoch(item.stop_time) if item.stop_time else None,
        "stopEventTime": epoch(item.stop_event_time) if item.stop_event_time else None,
    } for item in items]
```

### FUN-PIPE-019 — `serialize_order_audit`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:serialize_order_audit`  
Source-Lines: 460-515  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def serialize_order_audit(prepared_items, detector):
    """Serialize already-resolved Order Audit identities without business filtering."""
    output = []
    for prepared in prepared_items:
        entry = prepared["entry"]
        reaction = prepared["reaction"]
        crossed = prepared["crossed"]
        first_index = int(getattr(reaction, "first_idx"))
        causes = []
        for cause in prepared["causes"]:
            if cause["kind"] == "parent-stop":
                causes.append({
                    "kind": cause["kind"],
                    "parentType": cause["parentType"],
                    "parentFamily": cause["parentFamily"],
                    "eventTime": epoch(cause["eventTime"]),
                    "parentSourceTime": epoch(cause["parentSourceTime"]),
                })
            else:
                causes.append({
                    "kind": cause["kind"],
                    "resetTime": epoch(cause["resetTime"]),
                    "boundaryBreakTime": epoch(cause["boundaryBreakTime"]),
                })
        output.append({
            "direction": detector.order_direction,
            "reactionNumber": int(
                getattr(reaction, "behavior_public_number", None)
                or entry["reaction_number"]
            ),
            "reactionMode": str(getattr(reaction, "mode")),
            "firstIndex": first_index,
            "firstTime": epoch(detector.candles[first_index].timestamp),
            "boxTopSourceIndex": int(getattr(reaction, "box_top_source_idx")),
            "boxTopSourceTime": epoch(datetime.strptime(
                getattr(reaction, "box_top_source_time"), "%Y-%m-%d %H:%M:%S"
            )),
            "boxTop": str(getattr(reaction, "box_top")),
            "boxBottomSourceIndex": int(getattr(reaction, "box_bottom_source_idx")),
            "boxBottomSourceTime": epoch(datetime.strptime(
                getattr(reaction, "box_bottom_source_time"), "%Y-%m-%d %H:%M:%S"
            )),
            "boxBottom": str(getattr(reaction, "box_bottom")),
            "breakIndex": int(getattr(reaction, "break_idx")),
            "breakTime": epoch(
                detector.candles[int(getattr(reaction, "break_idx"))].timestamp
            ),
            "stopLevel": str(entry["stop_level"]),
            "stopSourceIndex": entry["stop_source_index"],
            "stopSourceTime": epoch(entry["stop_source_time"]),
            "stopHitIndex": crossed[0] if crossed is not None else None,
            "stopHitTime": epoch(crossed[1]) if crossed is not None else None,
            "stopHitEventTime": epoch(crossed[2]) if crossed is not None else None,
            "causes": causes,
        })
    return sorted(output, key=lambda item: (item["firstTime"], item["breakTime"]))
```

### FUN-PIPE-020 — `parse_arguments`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:parse_arguments`  
Source-Lines: 538-602  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def parse_arguments(argv=None):
    """Parse and validate the production pipeline command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reaction-engine",
        "--engine",
        dest="reaction_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--blue-line-engine",
        "--blue-engine",
        dest="blue_line_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--a-zone-engine",
        "--a-engine",
        dest="a_zone_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--s-zone-engine",
        "--s-engine",
        dest="s_zone_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--e-zone-engine",
        "--e-engine",
        dest="e_zone_engine",
        type=Path,
        required=False,
    )
    parser.add_argument(
        "--lifecycle-engine",
        "--stopall-engine",
        dest="lifecycle_engine",
        type=Path,
        required=False,
    )
    parser.add_argument(
        "--blue-lines", choices=("enabled", "disabled"), default="enabled"
    )
    parser.add_argument(
        "--a-zones", choices=("enabled", "disabled"), default="enabled"
    )
    parser.add_argument(
        "--s-zones", choices=("enabled", "disabled"), default="enabled"
    )
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--timeframe", type=int, required=True)
    parser.add_argument("--from-time", type=int, required=True)
    parser.add_argument("--to-time", type=int, required=True)
    parser.add_argument(
        "--direction", choices=("bullish", "bearish", "both"), required=True
    )
    args = parser.parse_args(argv)
    if args.timeframe < 1:
        raise ValueError("Timeframe must be at least one second.")
    return args
```

### FUN-PIPE-021 — `load_engines`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:load_engines`  
Source-Lines: 605-636  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def load_engines(args, timings: dict[str, float]) -> EngineBundle:
    """Load every configured calculation engine exactly once."""
    reaction = timed(
        timings, "Load Reaction engine", lambda: load_engine(args.reaction_engine)
    )
    blue_line = timed(
        timings,
        "Load Blue Line engine",
        lambda: load_module("blue_line_detector", args.blue_line_engine),
    )
    a_zone = timed(
        timings, "Load A engine", lambda: load_module("a_zone_detector", args.a_zone_engine)
    )
    s_zone = timed(
        timings, "Load S engine", lambda: load_module("s_zone_detector", args.s_zone_engine)
    )
    e_zone = (
        timed(
            timings,
            "Load E engine",
            lambda: load_module("e_zone_detector", args.e_zone_engine),
        )
        if args.e_zone_engine is not None
        else None
    )
    lifecycle_path = args.lifecycle_engine or Path(__file__).with_name("lifecycle_engine.py")
    lifecycle = timed(
        timings,
        "Load Lifecycle engine",
        lambda: load_module("lifecycle_engine", lifecycle_path),
    )
    return EngineBundle(reaction, blue_line, a_zone, s_zone, e_zone, lifecycle)
```

### FUN-PIPE-022 — `prepare_market_context`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:prepare_market_context`  
Source-Lines: 639-690  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def prepare_market_context(
    args, engines: EngineBundle, timings: dict[str, float]
) -> MarketContext:
    """Read, isolate, normalize and index the selected raw-data range."""
    source_bytes = timed(
        timings, "Read source file", lambda: args.data.read_bytes()
    )
    # Match the former ``utf-8-sig`` behavior without decoding the entire raw
    # payload to a Python string before orjson parses it.
    source_bytes = source_bytes.removeprefix(b"\xef\xbb\xbf")
    source_rows = timed(
        timings, "Parse source JSON", lambda: orjson.loads(source_bytes)
    )
    range_end_exclusive = args.to_time + args.timeframe
    rows = timed(
        timings,
        "Isolate raw range",
        lambda: isolate_raw_range(
            source_rows, args.from_time, range_end_exclusive
        ),
    )
    if not rows:
        raise ValueError("The selected range contains no raw candles.")

    raw_candles = timed(
        timings,
        "Build native RAW candle views",
        lambda: build_native_raw_candles(engines.reaction, rows),
    )
    lower_index = engines.reaction.shared_lower_timeframe_index(raw_candles)
    candles = (
        raw_candles
        if args.timeframe == 1
        else timed(
            timings,
            "Build timeframe candle views",
            lambda: build_candle_objects(
                engines.reaction, build_timeframe_buckets(rows, raw_candles, args.timeframe)
            ),
        )
    )
    chronology = engines.reaction.MarketChronology(
        candles, raw_candles, args.timeframe, lower_index
    )
    return MarketContext(
        raw_candles=raw_candles,
        candles=candles,
        lower_index=lower_index,
        chronology=chronology,
        start_index=0,
        end_index=len(candles) - 1,
    )
```

### FUN-PIPE-023 — `create_e_detector`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:create_e_detector`  
Source-Lines: 727-786  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def create_e_detector(
    direction: str,
    e_engine,
    full_results: dict[str, object],
    s_zones: list[object],
    chronology,
    geometry_detectors: dict[str, object],
    initial_order_audit,
    lifecycle_engine,
    *,
    blocked_order_first_times: set[datetime] | None = None,
):
    """Construct one E detector from the shared geometry/lifecycle contract."""
    opposite = chronology.opposite_direction(direction)
    end_index = len(chronology.candles) - 1

    def reset_geometry(geometry_direction, geometry_start, geometry_end):
        return geometry_detectors[geometry_direction].first_geometry_after_reset(
            geometry_direction,
            max(0, geometry_start - 1),
            geometry_end,
        )

    def direct_geometry(
        geometry_direction, geometry_start, geometry_end, gate_event
    ):
        return geometry_detectors[geometry_direction].first_order_reaction_after_gate(
            geometry_direction,
            geometry_start,
            geometry_end,
            gate_event,
        )

    def simple_reset_geometry(
        geometry_direction, reset_index, gate_index, geometry_end
    ):
        return geometry_detectors[geometry_direction].first_simple_geometry_after_gate(
            geometry_direction,
            reset_index,
            gate_index,
            geometry_end,
        )

    return e_engine.EZoneDetector(
        direction,
        full_results[direction].reactions,
        full_results[opposite].reactions,
        s_zones,
        full_results[direction].resets,
        full_results[opposite].resets,
        chronology,
        0,
        end_index,
        reset_geometry,
        direct_geometry,
        blocked_order_first_times=blocked_order_first_times,
        initial_order_audit=initial_order_audit,
        reset_geometry_finder=simple_reset_geometry,
        sequence_priority=lifecycle_engine.sequence_priority,
    )
```

### FUN-PIPE-024 — `calculate_full_direction_state`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:calculate_full_direction_state`  
Source-Lines: 789-966  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def calculate_full_direction_state(
    direction: str,
    engines: EngineBundle,
    market: MarketContext,
    full_results: dict[str, object],
    geometry_detectors: dict[str, object],
    initial_order_geometry: dict[str, object],
    timings: dict[str, float],
) -> FullDirectionState:
    """Run Blue→A→S→E calculation and lifecycle reconciliation for one direction."""
    blue_engine = engines.blue_line
    a_engine = engines.a_zone
    s_engine = engines.s_zone
    e_engine = engines.e_zone
    lifecycle_engine = engines.lifecycle
    assert e_engine is not None
    candles = market.candles
    chronology = market.chronology
    opposite = engines.reaction.opposite_direction(direction)

    blue_lines = timed(
        timings,
        f"Blue Line • {direction.title()}",
        lambda: blue_engine.detect_blue_lines(
            direction,
            full_results[direction].reactions,
            chronology,
            full_results[direction].resets,
        ),
    )
    a_zones = timed(
        timings,
        f"A • {direction.title()}",
        lambda: a_engine.detect_a_zones(
            direction,
            full_results[direction].reactions,
            blue_lines,
            chronology,
        ),
    )
    s_detector = s_engine.SZoneDetector(
        direction,
        full_results[direction].reactions,
        full_results[opposite].reactions,
        blue_lines,
        a_zones,
        chronology,
        0,
        len(candles) - 1,
        full_results[opposite].resets,
        initial_order_geometry=initial_order_geometry[direction],
    )
    s_zones = timed(timings, f"S • {direction.title()}", s_detector.detect)
    s_candidates = list(s_zones)

    e_detector = create_e_detector(
        direction,
        e_engine,
        full_results,
        s_zones,
        chronology,
        geometry_detectors,
        s_detector.order_audit,
        lifecycle_engine,
    )
    e_zones = timed(
        timings, f"E • {direction.title()} • initial", e_detector.detect
    )
    valid_s_zones = lifecycle_engine.s_zones_for_module_engines(
        s_zones, e_zones, direction
    )
    if len(valid_s_zones) != len(s_zones):
        e_detector = create_e_detector(
            direction,
            e_engine,
            full_results,
            valid_s_zones,
            chronology,
            geometry_detectors,
            s_detector.order_audit,
            lifecycle_engine,
            blocked_order_first_times={
                getattr(item, "source_time")
                for item in s_zones
                if item not in valid_s_zones
            },
        )
        e_zones = timed(
            timings,
            f"E • {direction.title()} • S reconciliation",
            e_detector.detect,
        )
        s_zones = valid_s_zones

    candidate_a = lifecycle_engine.visible_a_zones(
        s_detector.eligible_a_zones, s_zones
    )
    candidate_a = lifecycle_engine.visible_a_zones_after_s_stops(
        candidate_a, s_zones, candles
    )
    _calculation_a, invalid_a = lifecycle_engine.split_a_zones_by_dominant_stops(
        candidate_a,
        s_candidates,
        e_zones,
        [],
        candles,
        direction,
        lambda item: e_detector.parent_stop(
            "S" if hasattr(item, "a_source_time") else "E", item
        ),
        trend_reactions=s_detector.trend_reactions,
        confirmation_finder=s_detector.reaction_confirmation_time,
    )
    invalid_a_identities = {
        (getattr(item, "source_time"), int(getattr(item, "source_index")))
        for item in invalid_a
    }
    invalid_a_source_times = {source_time for source_time, _ in invalid_a_identities}
    invalid_s = [
        item for item in s_candidates
        if getattr(item, "a_source_time") in invalid_a_source_times
    ]
    invalid_s_identities = {
        (getattr(item, "source_time"), int(getattr(item, "source_index")))
        for item in invalid_s
    }

    accepted_a_sources = {
        getattr(item, "source_time")
        for item in s_detector.eligible_a_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in invalid_a_identities
    }
    pending_s_a_sources = {getattr(item, "a_source_time") for item in s_candidates}
    accepted_orders, blocked_order_first_times = lifecycle_engine.resolve_order_context(
        s_detector.order_audit,
        accepted_a_sources,
        set(getattr(e_detector, "blocked_order_first_times", set())),
        invalid_a,
        pending_s_a_sources,
        full_results[opposite].reactions,
        candles,
        direction,
        lambda item: s_detector.first_a_stop(
            Decimal(str(getattr(item, "price"))),
            getattr(item, "source_time"),
        ),
    )
    e_detector = create_e_detector(
        direction,
        e_engine,
        full_results,
        s_zones,
        chronology,
        geometry_detectors,
        accepted_orders,
        lifecycle_engine,
        blocked_order_first_times=blocked_order_first_times,
    )
    e_zones = timed(
        timings, f"E • {direction.title()} • final audit", e_detector.detect
    )
    s_zones = [
        item for item in s_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in invalid_s_identities
    ]
    return FullDirectionState(
        e_zones=e_zones,
        e_detector=e_detector,
        s_detector=s_detector,
        blue_lines=blue_lines,
        a_zones=a_zones,
        invalid_a_identities=invalid_a_identities,
        invalid_s_identities=invalid_s_identities,
        s_zones=s_zones,
        s_candidates=s_candidates,
    )
```

### FUN-PIPE-025 — `prepare_pipeline_state`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:prepare_pipeline_state`  
Source-Lines: 969-1082  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def prepare_pipeline_state(
    args,
    engines: EngineBundle,
    market: MarketContext,
    timings: dict[str, float],
) -> PipelineState:
    """Run shared calculation stages once and retain reusable detector state."""
    engine = engines.reaction
    e_engine = engines.e_zone
    raw_candles = market.raw_candles
    candles = market.candles
    chronology = market.chronology
    initial_order_geometry = {
        direction: engine.directional_a_stop_order_finder(
            candles, raw_candles, direction
        )
        for direction in ("bullish", "bearish")
    }
    directions = ("bullish", "bearish") if args.direction == "both" else (args.direction,)
    behavior_modules_enabled = (
        args.blue_lines == "enabled"
        or args.a_zones == "enabled"
        or args.s_zones == "enabled"
    )
    required_directions = (
        ("bullish", "bearish") if behavior_modules_enabled else directions
    )
    reusable_full_context = e_engine is not None and args.s_zones == "enabled"

    full_e_zones: dict[str, list[object]] = {}
    full_e_detectors: dict[str, object] = {}
    full_s_detectors: dict[str, object] = {}
    full_lines_by_direction: dict[str, list[object]] = {}
    full_a_by_direction: dict[str, list[object]] = {}
    invalid_a_identities_by_direction: dict[str, set[tuple[datetime, int]]] = {}
    invalid_s_identities_by_direction: dict[str, set[tuple[datetime, int]]] = {}
    full_s_by_direction: dict[str, list[object]] = {}
    full_s_candidates_by_direction: dict[str, list[object]] = {}

    if reusable_full_context:
        geometry_detectors = {
            direction: engine.UnifiedReactionDetector(
                candles, raw_candles, 0, len(candles) - 1, direction
            )
            for direction in ("bullish", "bearish")
        }
        results = {
            direction: timed(
                timings,
                f"Reaction geometry • {direction.title()}",
                detector.detect,
            )
            for direction, detector in geometry_detectors.items()
        }
        _, _, internal_reaction_identities, _ = timed(
            timings,
            "Internal Reaction ownership",
            lambda: engine.build_behavior_reaction_views(results, chronology),
        )
        for direction in directions:
            state = calculate_full_direction_state(
                direction,
                engines,
                market,
                results,
                geometry_detectors,
                initial_order_geometry,
                timings,
            )
            full_e_zones[direction] = state.e_zones
            full_e_detectors[direction] = state.e_detector
            full_s_detectors[direction] = state.s_detector
            full_lines_by_direction[direction] = state.blue_lines
            full_a_by_direction[direction] = state.a_zones
            invalid_a_identities_by_direction[direction] = state.invalid_a_identities
            invalid_s_identities_by_direction[direction] = state.invalid_s_identities
            full_s_by_direction[direction] = state.s_zones
            full_s_candidates_by_direction[direction] = state.s_candidates
    else:
        results = {
            direction: timed(
                timings,
                f"Reaction • {direction.title()}",
                lambda direction=direction: engine.UnifiedReactionDetector(
                    candles, raw_candles, 0, len(candles) - 1, direction
                ).detect(),
            )
            for direction in required_directions
        }
        if behavior_modules_enabled:
            _, _, internal_reaction_identities, _ = timed(
                timings,
                "Internal Reaction ownership",
                lambda: engine.build_behavior_reaction_views(results, chronology),
            )
        else:
            internal_reaction_identities = {"bullish": set(), "bearish": set()}

    return PipelineState(
        directions=tuple(directions),
        results=results,
        reusable_full_context=reusable_full_context,
        initial_order_geometry=initial_order_geometry,
        internal_reaction_identities=internal_reaction_identities,
        full_e_zones=full_e_zones,
        full_e_detectors=full_e_detectors,
        full_s_detectors=full_s_detectors,
        full_lines_by_direction=full_lines_by_direction,
        full_a_by_direction=full_a_by_direction,
        invalid_a_identities_by_direction=invalid_a_identities_by_direction,
        invalid_s_identities_by_direction=invalid_s_identities_by_direction,
        full_s_by_direction=full_s_by_direction,
        full_s_candidates_by_direction=full_s_candidates_by_direction,
    )
```

### FUN-PIPE-026 — `calculate_direction_range_state`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:calculate_direction_range_state`  
Source-Lines: 1110-1209  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def calculate_direction_range_state(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    timings: dict[str, float],
) -> DirectionRangeState:
    """Collect detector output for one requested direction before visibility rules."""
    result = state.results[direction]
    opposite = engines.reaction.opposite_direction(direction)
    start_index = market.start_index
    end_index = market.end_index

    requires_blue_lines = (
        args.blue_lines == "enabled"
        or args.a_zones == "enabled"
        or args.s_zones == "enabled"
    )
    if state.reusable_full_context and requires_blue_lines:
        blue_lines = [
            item
            for item in state.full_lines_by_direction[direction]
            if start_index <= int(getattr(item, "source_index")) <= end_index
        ]
    elif requires_blue_lines:
        blue_lines = timed(
            timings,
            f"Blue Line - {direction.title()}",
            lambda: engines.blue_line.detect_blue_lines(
                direction,
                result.reactions,
                market.chronology,
                result.resets,
            ),
        )
    else:
        blue_lines = []

    requires_a_zones = args.a_zones == "enabled" or args.s_zones == "enabled"
    if state.reusable_full_context and requires_a_zones:
        a_zones = [
            item
            for item in state.full_a_by_direction[direction]
            if start_index <= int(getattr(item, "source_index")) <= end_index
        ]
    elif requires_a_zones:
        a_zones = timed(
            timings,
            f"A - {direction.title()}",
            lambda: engines.a_zone.detect_a_zones(
                direction,
                result.reactions,
                blue_lines,
                market.chronology,
            ),
        )
    else:
        a_zones = []

    s_candidates: list[object] = []
    accepted_s_zones: list[object] = []
    if args.s_zones == "enabled":
        if state.reusable_full_context:
            s_candidates = state.full_s_candidates_by_direction[direction]
            accepted_s_zones = state.full_s_by_direction[direction]
            a_zones = state.full_s_detectors[direction].eligible_a_zones
        else:
            s_detector = engines.s_zone.SZoneDetector(
                direction,
                result.reactions,
                state.results[opposite].reactions,
                blue_lines,
                a_zones,
                market.chronology,
                0,
                len(market.candles) - 1,
                state.results[opposite].resets,
                initial_order_geometry=state.initial_order_geometry[direction],
            )
            s_candidates = timed(
                timings, f"S - {direction.title()}", s_detector.detect
            )
            state.full_s_detectors[direction] = s_detector
            accepted_s_zones = s_candidates
            a_zones = s_detector.eligible_a_zones

    return DirectionRangeState(
        blue_lines=blue_lines,
        a_zones=a_zones,
        s_candidates=s_candidates,
        accepted_s_zones=accepted_s_zones,
        e_zones=list(state.full_e_zones.get(direction, [])),
        invalid_a_identities=state.invalid_a_identities_by_direction.get(
            direction, set()
        ),
        invalid_s_identities=state.invalid_s_identities_by_direction.get(
            direction, set()
        ),
    )
```

### FUN-PIPE-027 — `finalize_direction_visibility`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:finalize_direction_visibility`  
Source-Lines: 1212-1358  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def finalize_direction_visibility(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    direction_state: DirectionRangeState,
    timings: dict[str, float],
) -> DirectionVisibilityState:
    """Apply lifecycle, range and Internal-Reaction rules to detector output."""
    lifecycle_engine = engines.lifecycle
    opposite = engines.reaction.opposite_direction(direction)
    start_index = market.start_index
    end_index = market.end_index

    visible_a_zones = lifecycle_engine.visible_a_zones(
        direction_state.a_zones, direction_state.accepted_s_zones
    )
    visible_a_zones = lifecycle_engine.visible_a_zones_after_s_stops(
        visible_a_zones,
        direction_state.accepted_s_zones,
        market.candles,
    )

    e_zones = list(direction_state.e_zones)
    stopalls: list[object] = []
    stopall_enabled = (
        args.lifecycle_engine is not None
        and engines.e_zone is not None
        and args.s_zones == "enabled"
    )
    if stopall_enabled and direction in state.full_e_detectors:
        e_zones, stopalls = lifecycle_engine.reconcile_stopall_lifecycle(
            state.full_e_detectors[direction],
            direction_state.accepted_s_zones,
            e_zones,
            market.chronology,
            direction,
            lambda label, work: timed(timings, label, work),
        )

    if direction in state.full_e_detectors:
        visibility_stop = lambda item: state.full_e_detectors[direction].parent_stop(
            "S" if hasattr(item, "a_source_time") else "E", item
        )
    else:
        visibility_stop = lambda item: state.full_s_detectors[direction].first_a_stop(
            Decimal(str(item.price)), item.decision_event_time
        )

    e_zones, visible_s_zones, visible_a_zones = timed(
        timings,
        f"Apply visibility filters - {direction.title()}",
        lambda: lifecycle_engine.finalize_behavior_visibility(
            visible_a_zones,
            direction_state.s_candidates,
            e_zones,
            stopalls,
            direction,
            direction_state.invalid_s_identities,
            visibility_stop,
            lambda item: state.full_s_detectors[direction].candidate_event_time(
                item.source_index, item.price, item.source_time
            ),
            market.candles,
            all_a_zones=direction_state.a_zones,
        ),
    )

    visible_s_zones = [
        item
        for item in visible_s_zones
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]
    visible_a_zones = [
        item
        for item in visible_a_zones
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]
    e_zones = [
        item
        for item in e_zones
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]
    stopalls = [
        item
        for item in stopalls
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]

    display_a_zones = [
        item
        for item in visible_a_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in direction_state.invalid_a_identities
    ]
    display_s_zones = [
        item
        for item in visible_s_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in direction_state.invalid_s_identities
    ]
    order_audit_a_sources = {
        getattr(item, "source_time") for item in display_a_zones
    }

    all_behavior_reactions = [
        reaction
        for result_item in state.results.values()
        for reaction in result_item.reactions
    ]
    engines.blue_line.mark_internal_blue_lines(
        direction_state.blue_lines,
        state.results[direction].reactions,
        all_behavior_reactions,
    )
    display_a_zones, display_s_zones, e_zones, stopalls = (
        lifecycle_engine.filter_internal_behavior_outputs(
            display_a_zones,
            display_s_zones,
            e_zones,
            stopalls,
            state.results[opposite].reactions,
            state.internal_reaction_identities.get(opposite, set()),
            all_behavior_reactions,
        )
    )

    prepared_order_audit = (
        lifecycle_engine.prepare_order_audit(
            state.full_e_detectors[direction],
            start_index,
            end_index,
            state.full_s_detectors.get(direction),
            order_audit_a_sources,
        )
        if direction in state.full_e_detectors
        else []
    )
    return DirectionVisibilityState(
        blue_lines=engines.blue_line.public_blue_lines(direction_state.blue_lines),
        a_zones=display_a_zones,
        s_zones=display_s_zones,
        e_zones=e_zones,
        stopalls=stopalls,
        prepared_order_audit=prepared_order_audit,
    )
```

### FUN-PIPE-028 — `serialize_direction_payload`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:serialize_direction_payload`  
Source-Lines: 1361-1412  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def serialize_direction_payload(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    visibility: DirectionVisibilityState,
    timings: dict[str, float],
):
    """Serialize one direction without applying any trading rule."""
    result = state.results[direction]
    reactions, resets = timed(
        timings,
        f"Serialize Reaction - {direction.title()}",
        lambda: serialize(
            result,
            market.start_index,
            market.end_index,
            reaction_transform=lambda item: engines.reaction.published_reaction_candidate(
                direction, item, market.chronology
            ),
        ),
    )

    def build_payload():
        return {
            "reactions": reactions,
            "resets": resets,
            "blueLines": serialize_blue_lines(
                visibility.blue_lines if args.blue_lines == "enabled" else [],
                market.start_index,
                market.end_index,
            ),
            "aZones": serialize_a_zones(
                visibility.a_zones if args.a_zones == "enabled" else []
            ),
            "sZones": serialize_s_zones(visibility.s_zones),
            "eZones": serialize_e_zones(visibility.e_zones),
            "stopAlls": serialize_stopalls(visibility.stopalls),
            "orderAudit": (
                serialize_order_audit(
                    visibility.prepared_order_audit,
                    state.full_e_detectors[direction],
                )
                if direction in state.full_e_detectors
                else []
            ),
        }

    return timed(
        timings, f"Serialize output - {direction.title()}", build_payload
    )
```

### FUN-PIPE-029 — `build_direction_output`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:build_direction_output`  
Source-Lines: 1415-1438  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def build_direction_output(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    timings: dict[str, float],
):
    """Calculate, finalize and serialize one requested trend direction."""
    direction_state = calculate_direction_range_state(
        direction, args, engines, market, state, timings
    )
    visibility = finalize_direction_visibility(
        direction,
        args,
        engines,
        market,
        state,
        direction_state,
        timings,
    )
    return serialize_direction_payload(
        direction, args, engines, market, state, visibility, timings
    )
```

### FUN-PIPE-030 — `build_response_payload`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:build_response_payload`  
Source-Lines: 1440-1489  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def build_response_payload(
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    timings: dict[str, float],
    pipeline_started: float,
) -> dict[str, object]:
    """Build the public response envelope around serialized direction outputs."""
    e_enabled = engines.e_zone is not None and args.s_zones == "enabled"
    stop_all_enabled = (
        args.lifecycle_engine is not None
        and engines.e_zone is not None
        and args.s_zones == "enabled"
    )
    payload: dict[str, object] = {
        "engine": "reaction_engine.py",
        "version": engines.reaction.REACTION_ENGINE_VERSION,
        "blueLineVersion": engines.blue_line.BLUE_LINE_VERSION,
        "aVersion": engines.a_zone.A_ZONE_VERSION,
        "sVersion": engines.s_zone.S_ZONE_VERSION,
        "eVersion": engines.e_zone.E_ZONE_VERSION if engines.e_zone else None,
        "stopAllVersion": (
            engines.lifecycle.STOP_ALL_VERSION
            if args.lifecycle_engine is not None
            else None
        ),
        "blueLinesEnabled": args.blue_lines == "enabled",
        "aEnabled": args.a_zones == "enabled",
        "sEnabled": args.s_zones == "enabled",
        "eEnabled": e_enabled,
        "stopAllEnabled": stop_all_enabled,
        "timeframe": args.timeframe,
        "actualFrom": epoch(market.candles[market.start_index].timestamp),
        "actualTo": epoch(market.candles[market.end_index].timestamp),
        "directions": {},
    }
    direction_payloads = payload["directions"]
    assert isinstance(direction_payloads, dict)
    for direction in state.directions:
        direction_payloads[direction] = build_direction_output(
            direction, args, engines, market, state, timings
        )
    payload["timings"] = {
        "phasesMs": {
            label: round(duration, 2) for label, duration in timings.items()
        },
        "bridgeTotalMs": round((perf_counter() - pipeline_started) * 1000, 2),
    }
    return payload
```

### FUN-PIPE-031 — `main`

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:main`  
Source-Lines: 1492-1522  
Contract-Type: Exact frozen function/method semantics  

**Normative contract:** The following implementation semantics MUST be preserved. Source comments/docstrings are informative; executable statements and control-flow order are normative.

```python
def main() -> int:
    pipeline_started = perf_counter()
    timings: dict[str, float] = {}
    validation_started = perf_counter()
    emit_progress("started", "Validate request")
    args = parse_arguments()
    validation_ms = (perf_counter() - validation_started) * 1000
    timings["Validate request"] = validation_ms
    emit_progress("completed", "Validate request", validation_ms)

    engines = load_engines(args, timings)
    market = prepare_market_context(args, engines, timings)
    state = prepare_pipeline_state(args, engines, market, timings)
    payload = build_response_payload(
        args, engines, market, state, timings, pipeline_started
    )

    emit_progress(
        "completed",
        "Calculation pipeline",
        (perf_counter() - pipeline_started) * 1000,
    )
    encoding_started = perf_counter()
    encoded_payload = json.dumps(payload, separators=(",", ":"))
    emit_progress(
        "completed",
        "Encode response JSON",
        (perf_counter() - encoding_started) * 1000,
    )
    print(encoded_payload)
    return 0
```

### FUN-PIPE-MODULE-001 — module-level entrypoint

Status: Active  
Direction: Bearish standalone reconstruction context  
Source-Origin: `trading_pipeline.py:<module>`  
Source-Lines: 1525-1530  
Contract-Type: Exact frozen module-level execution semantics  

```python
if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        raise SystemExit(1)
```

## 30. Change Log

### V4.0.1

Type: PATCH  

Changed:
- Added a complete normative reconstruction appendix containing every frozen production function/method body and the module-level pipeline entrypoint as source-faithful executable pseudocode.
- This closes all remaining function-level and branch-order ambiguity while retaining the readable Rule-based specification in Sections 1–28.
- No production source or calculation behavior changed.

Algorithm Behavior Impact: None.  
Source Baseline Impact: None; all eight frozen production SHA-256 values are unchanged.  


### V4.0.0

Type: MAJOR documentation-architecture release  
Algorithm Behavior Impact: None intended; this document describes the frozen production source baseline listed in Section 1.  
Baseline Impact: ZERO DIFFERENCE by definition of this documentation-only release.  

Changed:

- Rebuilt the entire Bearish Algorithm Reference from production source code.
- Converted the document into a standalone reimplementation specification.
- Added exact Original RAW chronology rules.
- Added complete active Reaction, Reset, Blue, A, S, Order, E, StopAll, Internal-Reaction, lifecycle, and visibility rules.
- Added public output schemas.
- Added source-faithful pseudocode identifiers.
- Added source hashes, source-function coverage inventory, test contracts, and reimplementation checklist.

Removed from active specification:

- Any rule not present in the frozen production source baseline.
- Any dependency on historical Algorithm Reference files.
- Any requirement to consult the opposite-direction Algorithm Reference.
