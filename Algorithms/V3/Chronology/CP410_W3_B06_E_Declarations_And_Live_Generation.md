# CP410 — W3 B06-01: E declarations and live generation state

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source `240369edf3352006082efe094eb68ac027d6689f`, lines 1–152, E declarations and E01–E03. Entry algorithm `7803f79db4c017e36051bdcf55407838afb3035c`, tree `3c4429d76758766b6e3c23e1640a687e7cea3a62`. Source-only local review.

## Independent procedure contracts

### E-D01 — lines 1–7

Module declaration separates physical Order ownership from E source/decision geometry, chains, family and numbering; lifecycle owns cross-stage visibility and StopAll grouping. Docstring is a boundary statement, not an execution or dispatch guarantee.

### E-D02 — lines 8–19

Postponed annotations; module imports heap merge, groupby, bisection and sorted insertion, dataclass and replacement, datetime, Decimal, heap operations, Callable and Sequence. Imports execute/bind at module load, while annotations do not perform runtime argument or field validation. Import failure propagates.

### E-D03 — lines 20–29

Bind Decimal normalizer and re-export physical reaction identity by same-name alias; bind direction policy, OrderAuditEngineMixin, OrderBResetLeg, OrderMatch, PostBehaviorStop and four named Order provider helpers. Importing does not itself execute a trading decision. Distinct Order owner contracts remain authoritative.

### E-D04 — lines 30–34

Assign metadata constants E_ZONE_VERSION 6.16.2, E_ZONE_IMPLEMENTATION_VERSION 6.20.4, E_ZONE_LAST_MODIFIED 2026-11-20T22:00:58+03:30. Metadata is not a schema or runtime equivalence proof; preserve unchanged.

### E-D05 — lines 35–40

EZone is a frozen slotted dataclass; declarations have no defaults. Required direction, family, number and parent type describe a result, not a local direction/number validation. Generated record equality is field based, not physical identity selection; freezing is shallow and default ordering is not enabled.

### E-D06 — lines 41–46

Parent source index/time and price, parent stop index/main time/exact event time are independent fields; Decimal annotation preserves intended representation but does not normalize or validate at construction. Do not equate exact event and main candle time.

### E-D07 — lines 47–56

Order direction, native reaction number, mode, ordered tuple of causes, nullable parent-stop cause time, physical First/Break indices and times, and confirmation time are required declared values. No fallback or geometry inference. The nullable annotation is not a default. Physical identity is the normalized First/Break pair at the owning provider, not EZone equality.

### E-D08 — lines 57–65

Store Order top and bottom Decimal levels, their source indices/times, stop level and stop source index/time separately. No price computation, rounding, direction mirroring or source-index check at declaration.

### E-D09 — lines 66–73

Store E source index/time/Decimal price and decision index/main time/exact event time as separate required fields. No comparison, ordering or chronology check at record construction.

### E-D10 — lines 74–79

_ParentStopProgress is frozen/slotted; required scanned_until and nullable event. A null event can represent unfinished or exhausted search evidence, not proof of no future stop. Meaning is supplied by E04; no default or validation.

### E-D11 — lines 80–87

_EReconciliationStep is frozen/slotted; source frontier, count, tuple of active EZone values and nullable sequence start, all required. Tuple is not a deep copy or proof of chronological order. Consumers define checkpoint replay.

### E-D12 — lines 88–91

_ReopenedERace is a dedicated Exception subclass with no additional behavior. Declaration does not raise it. Only named catch in continuation reconciliation is a bounded restart mechanism; no broad suppression established.

### E-D13 — lines 92–102

_ReconciledE is frozen/slotted; seven required fields for candidates, numbered, accepted exact (datetime,int) set, lifecycle start set, evidence, steps and native numbered tuple. Preserve distinction between native and projected numbering; tuple/frozenset annotations alone neither convert inputs nor recursively freeze nested evidence.

### E01-A — lines 103–111

LiveEContinuation retains geometry across market updates under the stated current-ledger and ownership-evidence conditions. Docstring states reuse preconditions but actual downstream key/filter/callback enforcement must be assessed separately; no global correctness assertion.

### E01-B — lines 112–115

Initialize chronology, scope and dirty marker to None, in assignment order, without an external chronology read. Annotations are descriptive.

### E01-C — lines 116–119

Allocate distinct fresh current and previous dictionaries for parent-stop progress and main extremes. No sharing, merge, or import-time/global cache; extreme payload records index, time and Decimal.

### E01-D — lines 120–126

Allocate distinct fresh current/previous maps for E zones, exact reconciliations and scoped reconciliations; initialize main index None. Ten dictionary objects total, four null attributes including chronology/scope/dirty/index. No computation or validation; no transactional rollback on exceptional attribute assignment.

### E02-A — lines 127–131

Read chronology.times before other accesses. Short-circuit empty/falsey times rejection; otherwise chained inclusive 0 <= first_dirty_main <= len(times), no integer conversion/type guard. Out-of-bounds or empty raises exact ValueError. Noncomparable values or unusual truthiness/len can raise earlier; a noninteger that passes comparison can still fail indexing.

### E02-B — lines 132–136

Construct scope from first main timestamp and chronology.timeframe. If first_dirty_main < len(times), use times at that position, else use last timestamp plus timeframe. Inclusive len sentinel denotes next main boundary under normal chronology. No lower timestamp search, rounding or monotonicity check; repeated timeframe access on sentinel path. Assign dirty only after selected expression succeeds.

### E02-C — lines 137–137

Compare new scope to retained scope by equality, after dirty assignment. Scope is only first main timestamp and timeframe, not chronology identity, direction, full market content, end time or feedback scope. Equality is not prefix proof; caller must supply correct dirty evidence.

### E02-D — lines 138–144

Rotate five pairs in exact order: stops, extremes, zones, reconciled, scoped. For each, equal scope aliases old current map as previous, otherwise allocates new empty previous; always allocate new empty current. Discard old previous reference from this owner; do not merge, copy, clear in place, or preserve older generations. External aliases may survive.

### E02-E — lines 145–147

After rotations clear main index even for equal scope; then store supplied chronology object and new scope, in that order. No transaction, catch or rollback: dirty and earlier pair updates can remain if later operations fail. Normal implicit None. No cache hit or market prefix proof in advance.

### E03-A — lines 148–150

Require detector.chronology is retained chronology by identity, not equality; mismatch short-circuits dirty check. If same object but dirty is None, raise same exact ValueError. Missing attribute/custom access propagates; no separate direction, scope, range or timestamp validity check.

### E03-B — lines 151–152

Return retained dirty value unchanged, with no copy, recalculation, timestamp conversion or clamp. The check is not a proof of valid input or correctness of prior cache reuse.

## Declared record schemas

All four records are frozen and slotted; every field is required and has no default. Annotations are descriptive, not a conversion or validation.

### EZone

- `direction`: `str`
- `family`: `str`
- `number`: `int`
- `parent_type`: `str`
- `parent_source_index`: `int`
- `parent_source_time`: `datetime`
- `parent_price`: `Decimal`
- `parent_stop_index`: `int`
- `parent_stop_time`: `datetime`
- `parent_stop_event_time`: `datetime`
- `order_direction`: `str`
- `order_reaction_number`: `int`
- `order_mode`: `str`
- `order_causes`: `tuple[str,...]`
- `order_parent_stop_cause_time`: `datetime|None`
- `order_first_index`: `int`
- `order_first_time`: `datetime`
- `order_break_index`: `int`
- `order_break_time`: `datetime`
- `order_confirmation_time`: `datetime`
- `order_box_top`: `Decimal`
- `order_box_top_source_index`: `int`
- `order_box_top_source_time`: `datetime`
- `order_box_bottom`: `Decimal`
- `order_box_bottom_source_index`: `int`
- `order_box_bottom_source_time`: `datetime`
- `order_stop_level`: `Decimal`
- `order_stop_source_index`: `int`
- `order_stop_source_time`: `datetime`
- `source_index`: `int`
- `source_time`: `datetime`
- `price`: `Decimal`
- `decision_index`: `int`
- `decision_time`: `datetime`
- `decision_event_time`: `datetime`

### _ParentStopProgress

- `scanned_until`: `datetime`
- `event`: `datetime|None`

### _EReconciliationStep

- `source`: `int`
- `count`: `int`
- `active`: `tuple[EZone,...]`
- `sequence_start`: `datetime|None`

### _ReconciledE

- `candidates`: `tuple[EZone,...]`
- `numbered`: `tuple[EZone,...]`
- `accepted`: `frozenset[tuple[datetime,int]]`
- `lifecycle_starts`: `frozenset[datetime]`
- `evidence`: `tuple`
- `steps`: `tuple[_EReconciliationStep,...]`
- `native_numbered`: `tuple[EZone,...]`

## Provider and consumer boundary

- **engine/pipeline/core_utils.py** (`38a1053510c5fb114e1b4290de00a2d3b27fc373`, lines 51–66): as_decimal preserves Decimal or constructs Decimal from string; reaction_identity uses int First then Break, no price/time/ordinal components. Imported alias is same binding. Record declaration does not invoke either helper.
- **engine/pipeline/direction_policy.py** (`f7d047abde0eb884905f86c1d2beeaaec3f6e07a`, lines 20–54): Direction policy owns strict trend cross and extreme mirror, exact bullish/bearish and ValueError otherwise; no chronology, lifecycle or numbering. E01–E03 direction-neutral, no local price or geometry transformation.
- **engine/pipeline/order_audit_engine.py** (`6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 39–74, 77–77, 139–139, 198–198, 442–442, 523–527, 554–555, 2035–2048, 2101–2113): Order imports bind owner declarations and helpers; OrderMatch has nine items including optional crossing triple, cause tuple and nullable cause time. E inherits mixin later; physical identity, accepted ledger and Order provenance remain Order-owned. B05 scoped closure retained, no new cross-owner acceptance.
- **engine/pipeline/reaction_engine.py** (`9adffb832ffa231ba0cb01de507a30fbe62be0b0`, lines 1153–1178): MarketChronology retains candles/seconds references, derives main and lower times from supplied index or row timestamps, converts timeframe to timedelta and owns lower index/caches. E02 reads chronology.times/timeframe directly; no independent prefix or input identity guarantee.
- **engine/pipeline/e_zone_detector.py** (`240369edf3352006082efe094eb68ac027d6689f`, lines 153–195, 201–214, 221–221, 258–309, 335–390, 510–517, 538–554, 586–594, 666–733, 1125–1133, 1294–1316, 1480–1488): Later E consumers use current/previous stop/extreme/zone/reconciliation maps and _dirty_time; optional live continuation only when non-null. Cached cross-order hit still checks chronology identity; nonlive branch uses owner search. EZone construction separately populates main vs exact event timestamps and normalizes selected prices. Steps snapshot active tuple before source group and at terminal frontier; reopened race raises control exception with checkpoint, one catch restarts native computation. Saved record only when not reopened; restoration copies candidate/numbered lists and accepted set, updates lifecycle starts. These are bounded consumer observations, not E04+ closure.
- **engine/pipeline/lifecycle_engine.py** (`2885dcbd3af108baadde7510ffd7968ad735c57e`, lines 37–39): Shared sequence_priority normalizes kind/family and performs dictionary lookup. Passed into E construction by Bridge; E declarations do not own priority or StopAll lifecycle.
- **engine/bridge/trading_pipeline.py** (`e1e65ba960c5f726f9a05e2ab89e4457b65e5735`, lines 336–364, 2160–2208, 2280–2306, 2440–2456, 2488–2502, 2648–2663, 2733–2744, 3531–3550, 3678–3685, 3738–3767): Bridge creates E using shared chronology and lifecycle priority, optionally forwards supplied live continuation and feedback scope for initial/final/shared-order calls. In observed native live worker route _run_live_calculation invokes prepare_pipeline_state without live argument; market views update candle indices and closed regimes but no E advance call in these observed sites. Optional external/dynamic live object and its advance/dirty evidence remain conditional; do not claim native live E cache is activated merely by declaration.
- **engine/bridge/live_pipeline.py** (`e1f1e7d3414a75ed073b67ff2ded3a5a481f6182`, lines 22–65): LivePipelineContinuation retains buckets and market views; append calls calculate_live_from_buckets and replaces views on BaseException following bucket transaction rollback. This outer route does not establish a direct E02 caller or local E02 transactional rollback.

## Exact inventory and prior evidence

| Category | CP410 | B06 total |
|---|---:|---:|
| branches | 11 | 334 |
| comparisons | 5 | 218 |
| arithmetic | 10 | 104 |
| calls | 8 | 453 |
| accesses | 287 | 3765 |
| effects | 28 | 270 |
| exits | 3 | 113 |
| Total | 352 | 5257 |

34 W1 and 318 additional; 3 historical supplements. All 1109 CP317 links and 18 AST filter IDs reconciled; exact category/index union of 25 disjoint start-line partitions. 4905 rows remain and are not semantically accepted. B05 exact 8318 union preserved. W3 remains INCOMPLETE; W4 NOT RUN; Phase 08 BLOCKED.

## Limitations

- Separate source-first local review by GPT, not independently staffed. Existing AST inventories compared directly, not regenerated.
- Local source-only coverage; no RAW, runtime, ZIP, new cross-owner acceptance or production change.
- Dataclass annotations and frozen slots are not input validation or deep immutability; market chronology alignment, stable comparable inputs and correct dirty evidence remain conditional.
- Scope equality is not full prefix proof. The observed native live replay route does not pass a live continuation into prepare_pipeline_state; optional dynamic live receivers remain conditional, not asserted active or defective.
- No independent SHA-256 assertion; Git object identities and readback are the publication checks. An initial live provider path lookup returned 404; the pinned main tree identified engine/bridge/live_pipeline.py and its source was subsequently read.
