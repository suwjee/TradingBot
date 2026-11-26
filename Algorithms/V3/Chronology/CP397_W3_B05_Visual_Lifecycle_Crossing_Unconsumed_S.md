# CP397 — Independent local visual Order lifecycle, crossing and unconsumed S reuse

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA41–OA44 lines 1436–1523. B05-14. Source-only, no execution.

## OA41-A — lines 1436–1443

Static method takes explicit owner argument; no automatic instance binding. Compute lower_bound of native opposite First array, then iterate increasing positions through len(opposite_reactions)-1. No local sorting or alignment check; equal First starts at first equal slot under sorted premise.

## OA41-B — lines 1444–1449

Read reaction, First, confirmation in that order before either test. Skip if First < start, otherwise test confirmation < start. Both equalities permitted. Number is native position + 1, including skipped slots; not an identity or renumbered eligible ordinal. No blocked-First, reset, acceptance, parent ownership or deadline predicate.

## OA41-C — lines 1450–1458

Resolve stop triple via owner _order_stop(number,reaction), then crossing via dynamically dispatched _cross_order(confirmation,level). Return first eligible singleton of eight fields in exact order: number, original reaction reference, confirmation, unchanged level, source index, source time, crossing (may be None), boolean False. No further scan for a crossing; exhausted loop returns fresh empty list. No direct ledger registration; delegated caches can mutate. Errors propagate.

## OA42-A — lines 1459–1464

Use native (start,level) tuple as cache key. Membership distinguishes cached None from absent; hit returns stored value unchanged before range/direction evaluation or validation. No local price normalization, direction, range, owner, or chronology in key; per-detector lifetime premise. Native equality/hash, not Decimal string fingerprint; malformed/unhashable inputs can fail at membership.

## OA42-B — lines 1465–1469

Compute left as lower_bound(max(start,range_start)), then right as lower_bound(range_end); lower interval inclusive start/exclusive end, including duplicate start rows and excluding all equal end rows, under sorted array premise. No local empty/reversed-range guard; delegate exact level unchanged, less flag true unless order_direction exactly bearish. Bearish Order strict high > level; all other direction values strict low < level in native scan. Equality never crossing. Indexed search exclusively when lower_index non-None; no scan retry on indexed miss. Indexed implementation and aligned chronology remain conditional.

## OA42-C — lines 1470–1472

Only position is None denotes absence, including empty window if owner returns None. Publish None before returning; zero valid. No special fallback or reset/acceptance predicate.

## OA42-D — lines 1473–1479

Read exact lower timestamp at returned position, map main index via owner clamp, then required candle timestamp, then construct (index, main candle.timestamp, exact lower event). No local position/bounds validation, no timestamp from self.times on base path. Store triple before return; no rollback of owner effects on errors. Main mapping and lower positions rely on delegated contract.

## OA43 — lines 1480–1486

Public instance wrapper forwards supplied confirmation_time and stop_level unmodified through self._cross_order; returns same result without validation/conversion. Dynamic E override can change evaluation path, cache-hit dirty guard and main timestamp source. No independent search or direct mutation.

## OA44-A — lines 1487–1496

No parent_type or owner/kind check inside helper. Required getattr color then str, exact blue only; OR short-circuits, optional confirmation None guard before optional level None guard. Empty/zero values other than None pass corresponding null guards. Reject returns fresh empty list. Missing color raises rather than defaulting.

## OA44-B — lines 1497–1501

Reread required confirmation then required level; normalize using as_decimal (preserve Decimal instance, otherwise Decimal(str(value))). Call dynamically dispatched crossing. Reject if crossed is None, otherwise compare exact slot 2 < parent_stop. Equal crossing accepted; no separate confirmation-vs-parent_stop or upper-bound test. No local stop provenance recomputation.

## OA44-C — lines 1502–1510

Construct fresh SimpleNamespace by reading mode, First, Break, box top, top source index, box bottom, bottom source index in order. All required; copied unchanged, no int/Decimal conversion here, no lookup or geometry revalidation; no canonical Reaction object identity. Physical identity later computed from integer First/Break pair, not namespace object reference.

## OA44-D — lines 1511–1523

Return fresh singleton nine-field OrderMatch: int(reaction number), namespace, confirmation, normalized stop level, int(stop source index), required stop source time, exact crossing, singleton carried-live label tuple, None creation time. Number conversion happens before stop-source conversion/read. No new parent-stop cause, direct ledger registration, or final ownership decision. Exceptions propagate; crossing cache may already have been populated before a later required field/conversion fails.

## Consumer boundaries

- engine/pipeline/order_audit_engine.py [[557,569],[619,624],[653,686]]: Per-detector crossing cache initializes empty. Opposite First and confirmation arrays constructed in input order. OA11 canonical stop cache only exact canonical reaction object at in-range ordinal, otherwise delegate uncached; context_start discarded; visual does not bypass this path.
- engine/pipeline/reaction_engine.py [[1185,1192],[1305,1367]]: Main index bisect_right minus one; clamp to zero only when preceding first, otherwise index including last equal start. Canonical A scans anchor or First-1 clamped to start_index, extends across preceding context color, strict high/low improvement retains first equal extreme, Break inclusive; non-A follows Mode B prior opposite reaction edge, number<=1 raises. Visual delegates, inherited S uses recorded stop instead.
- engine/pipeline/core_utils.py [[51,53],[60,66]]: Existing Decimal returned unchanged, other values Decimal(str(value)); canonical identity integer First/Break, not reaction number or reference. OA44 only converts selected fields.
- engine/pipeline/e_zone_detector.py [[343,367],[416,435]]: Owner order_direction opposite of trend, copies opposite reactions preserving supplied order, uses chronology lower/candle arrays, range_end main end plus timeframe. Main index delegates clamp=True. Strict search indexed when non-None else ascending scan normalized low/high; no fallback on indexed miss.
- engine/pipeline/e_zone_detector.py [[148,174],[524,557]]: Override delegates base OA42 if no live state. Live cache hit first validates dirty chronology (may raise). Miss calls first_stop with clamped start, direction comparator, native strict-search callback; live key (less,start,level), previous progress reused only under dirty-boundary conditions, event < range_end, scan resumes at max(start,scanned_until), no search if start>=range_end. Live result uses self.times[index], not candle.timestamp; cache None or triple. Dynamic OA41/OA43/OA44 dispatch is conditional, no equivalence claim.
- engine/pipeline/e_zone_detector.py [[608,642],[651,696]]: Inherited query only for exact S at _zone, before gate-owned/carried/registration. If S and no carried, inherited crossing sets continuous deadline or range_end. E merges non-null crossing candidates from direct/inherited/carried/post-stop, sorts by exact event then descending First int and rejects disowned S creation; winner only then builds zone. No ownership conclusion from inherited helper alone.
- engine/pipeline/order_audit_engine.py [1945,1964]: Accepted stream validates cached None as resolved crossing; cache absence vs stored None is significant. No local accepted stream equivalence established.

## Verification

273 category rows: 56 prior W1 and 217 additional; six historical supplements; all 4192 prior rows structurally revalidated without overlap; 79 prior supplemental IDs unique. Local scoped only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP397_W3_B05_Visual_Lifecycle_Crossing_Unconsumed_S_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP397_Completion.json).

Separate source-first pass by GPT, not independently staffed. Local source review only; native array alignment, index contract, live continuation, Decimal context and cross-owner ownership remain conditional.

No runtime, RAW payload, ZIP or production changes. Counts derived from pinned canonical source-backed inventory, not newly generated AST. Prior B05 register row identity and supplemental ID uniqueness revalidated; unrelated historical artifacts not re-read.
