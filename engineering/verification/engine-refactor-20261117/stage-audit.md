---
title: Engine stage source audit for the 2026-11-17 refactor
document_role: evidence
lifecycle: historical
owner: engine-refactor-20261117
created_at: 2026-11-17T20:00:08+03:30
last_modified_at: 2026-11-17T20:11:08+03:30
---

# Stage source audit

This is read-only source evidence captured for the current refactor task. It is not trading-semantic authority, a benchmark, an implementation change, or an equivalence result. Source line references below describe the source as inspected before production edits by the parent task.

## Inspection scope and status

The repository root was confirmed with `git rev-parse --show-toplevel` as `X:/My-Projects/TradingBot`. Git status was clean at initial inspection. A later status showed only the parent task's new verification directory. The repository inventory found no nearer instructions under `engine/`; the root operating contract applies.

Read completely:

| Source | Observed lines | Audit coverage |
| --- | ---: | --- |
| `engine/pipeline/a_zone_detector.py` | 1032 | All data models, constructor, crossing/extreme selection, formation routes, filtering, live histories and continuation |
| `engine/pipeline/s_zone_detector.py` | 1554 | All data models, constructor indexes, source selection, Types 3/4, order-backed decision races, ownership, reconciliation and live continuation |
| `engine/pipeline/e_zone_detector.py` | 1566 | All data models, live state, constructor, geometry, chain discovery, source arbitration, reconciliation and restoration |
| `engine/pipeline/blue_line_detector.py` | 566 | All strike counting, exact-break prefix, Scale/Reset Blue construction, tail checkpointing and public/internal projection |
| `engine/pipeline/PL_PH_detector.py` | 820 | All primary models, seed qualification, concurrent logical cycles, native Order access, reflected bullish path and live continuation |
| `engine/pipeline/direction_policy.py` | 70 | Complete |
| `engine/pipeline/core_utils.py` | 26 | Complete |
| `engine/pipeline/__init__.py` | 28 | Complete |

Also read the empty `engine/__init__.py`, the root `AGENTS.md`, the maintained engineering index, the zero-difference procedure, the relevant testing-procedure opening sections, documentation-governance sections, and the current `LowerTimeframeIndex` / reflection implementation at `reaction_engine.py:867-1081`. Read `test_live_a_zones.py` completely; discovered relevant current test names in the S/E/Blue/primary test suites. The parent task owns canonical/reference retrieval, complete dependency closure, runtime baseline and profiling.

| Category | Status | Meaning |
| --- | --- | --- |
| Assigned source reading | PASS | Every line of the assigned files was inspected |
| Production modification | NOT APPLICABLE | This audit makes no production edits |
| Benchmark / profile | NOT RUN | Parent task owns measurement |
| Candidate equivalence | NOT RUN | Proposals below are static analysis |
| Trading correctness | NOT RUN | No independent trading-correctness claim |

## Concrete opportunities

Complexity statements describe the visible implementation, not measured runtime importance. Let `N` be lower-row count, `M` main-candle count, `R` reaction count, `B` Blue count, `A` A count, `S` S count, `C` E candidate count, and `L` active E count.

### A: use the existing lower-row range index

`AZoneDetector._range_extreme` at lines 167-199 slices a lower window and performs an additional slice and linear directional-extreme scan, costing O(K) time and references for each K-row interval. It is reached by inherited Blue continuation, pair triggers, and exact A source ownership, including `_inherited_stop:548` and `_a_source:573`.

The current chronology already exposes `LowerTimeframeIndex.range_minimum` and `range_maximum`. Those methods at `reaction_engine.py:926-970` preserve the exact winning Decimal and the earliest position on equality, matching this A loop's strict-only replacement. Its `_decimal_value:867-869` normalization is identical to `core_utils.as_decimal`.

Smallest proposed change: bisect the existing `lower_times` using exactly `[start, end + 1 microsecond)`, query the direction's existing range primitive if nonempty and supported, map the winning lower timestamp through `_main_index`, and return that main source timestamp. Keep the existing empty-lower main-candle fallback intact. This reduces lower-range selection to O(log N) without constructing another index or retaining more market state.

Required preservation: earliest equal extreme, the winning Decimal lexeme/exponent, exact inclusive end, complete main source identity mapping, and lower-data-presence suppression of main fallback. Live caches must keep their existing invalidation gates. A source is frozen at exact Reaction confirmation; no later Break-main extreme may enter it.

### A: reduce repeated special/ordinary ownership scans

`_filter_special_a:714-732` constructs every earlier ordinary candidate and takes `max(source_time)` for each special A, costing O(A * special). A sorted index by source time with stable first-item selection at duplicate times can answer the strict predecessor query with bisect. Preserve the first item returned by the current stable `max`, not the last same-time entry.

`_filter_special_a:735-758` checks every special pair against every ordinary pair. Build `earliest_special_trigger_by_blue_ordinal` and test the ordinary trigger against the earliest trigger for each of its two ordinals. The current predicate is strict `ordinary.trigger > special.trigger`; equality must continue to retain the ordinary zone. This replaces repeated set allocation and O(A * special) membership with O(A + special).

`_first_reaction_after:487-503` and `_inherited_stop:505-553` restart from the first reaction. A future index must preserve original reaction order, not assume confirmation order equals input order. `_first_reaction_after` already accepts a start position and the live implementation uses common-prefix information. Do not simply bisect an unsorted confirmation list.

### S: range geometry has distinct first/last tie contracts

`_candidate_source:295-308` is an O(K) main interval scan that assigns equality to the first candle. `_candidate_source_last:310-328` is a separate O(K) scan that deliberately assigns equality to the last candle. These helpers are reached repeatedly by Simple, Type-3 and Type-4 routes. `_first_type4:492-496` rescans the same A-stop origin through successive aligned Break indexes, so nested prefixes can cost the sum of all prefix lengths.

Safe options, subject to measurement: reuse a run-scoped main-price range index with an explicit tie policy, or incrementally extend the Type-4 running extreme only after proving aligned Break indexes are monotone. The currently available `LowerTimeframeIndex` range methods choose the first equal candle and cannot replace `_candidate_source_last` directly. A reverse tie policy must also return the actual winning Decimal representation when numerically equal values have different exponents or signed zeros.

`_first_trend_reaction_after_order:330-339` scans trend reactions and asks for confirmations again even though constructor lines 157-170 already precompute confirmation records. A cache per exact order-confirmation time can preserve the first match in original reaction enumeration without imposing a sort assumption.

`_nested_trend_reaction:342-370` is called from `_candidate_timing:730` and again from `_build_order_backed_zone:1115`. Cache the immutable result within one detector run for the same Order geometry and exact confirmation, or return the result alongside candidate timing internally. Preserve original first-match reaction numbering and boundary inclusion.

Constructor lines 168-170 sort confirmation times extracted from an already sorted `_trend_ordered` list. Reusing/copying `_trend_ordered_confirmation_times` would remove a redundant sort, though this is likely a minor cost and should follow measured larger opportunities.

Source-event searches at `_a_source_event_time:631-638` and `_candidate_event_time:788-801` repeatedly scan a single main candle's lower rows for equality. A run-scoped cache keyed by source index, exact price representation and lower start gate is possible. Do not substitute a strict-cross index for equality, or share results across live market revisions.

Existing optimizations are already substantial: the constructor materializes reaction/reset/Blue chronology indexes; `_decision` queries lower strict-cross positions; `reconcile_shared_order_stops:1328-1424` deduplicates physical Orders, computes crossings once, sorts and bisects. Reintroducing per-(S,Order) scans or moving policy into transport would regress this design.

### E: index child existence and first parent lookup in reconciliation

`_compute_reconciliation:1353-1372` nests a scan over all candidates inside an active-owner scan for every eligible candidate. Its child subpredicate only asks whether an E child with a matching physical parent has `decision_event_time >= candidate.decision_event_time`.

Small proposed index: a map from `(parent_source_index, parent_source_time)` to the maximum decision event of matching E children. Build it in original candidate iteration, update it on every `enqueue:1214-1224`, and test the threshold against the map. The existence predicate has no winner/provenance output, so max preserves its current meaning while replacing the innermost O(C) scan with O(1). Initial construction is O(C); dynamic insertions remain O(1). Preserve the `parent_type == "E"` restriction and exact `>=` boundary. Do not cache the outer `stopped_by` or accepted ownership result across mutations.

`parent_active:1235-1246` repeatedly scans all S zones for the first physical parent match. A local map built with `setdefault((source_index, source_time), s_zone)` preserves the current first-win result and changes lookup from O(S) to O(1). A normal last-win dict comprehension would be incorrect if duplicate parents exist. Similar identity lookups at restoration lines 1012-1013 and regenerated-parent lookup lines 1330-1333 can use indexes only with their own current first-win semantics and dynamic-numbered updates.

`parent_active:1256-1284` scans numbered history for an earlier E and an already-used S-parent source. An append-maintained source-time index/set is possible, but each history query is horizon- and reset-sensitive. This is a higher-risk follow-up than the two direct maps above.

### E: avoid rebuilding equivalent main extreme structures per detector

Non-live `EZoneDetector.__init__:364-370` builds directional main prices and `_build_extreme_sparse:518-545`, an O(M log M) table, for every detector instance. `_find_extreme` queries are already O(1), so optimize construction/lifetime only if repeated detector construction is measured significant.

The live implementation already lazily builds a main `LowerTimeframeIndex` in `LiveEContinuation.extreme:172-190`. A current-chronology-scoped main index shared among E instances could replace duplicate construction while preserving first-equal candle behavior. Measure the segment-tree query time tradeoff, and do not add an unbounded cross-run cache or let old indexes survive market revisions. The full OHLC of both boundary main candles belongs to E geometry (`_extreme_between:636-647`), so an A-style exact lower-prefix extreme is not equivalent.

### E: preserve the mutable Order ledger and source-race rules

`_zone:657-720` registers Order audit before combining all eligible route choices. Sorting at line 705 intentionally performs a global exact-stop then later-First competition; reducing a route to its own single winner first is not equivalent. `_order_created_only_by_disowned_s` is evaluated using each prospective source. A prospective source can change Order eligibility.

`restore_independent_s_roots:960-1050`, `replace_with_earlier_continuation:869-914`, consumed S evidence and `_compute_reconciliation` all update accepted source state or reselect native Orders. Broad memoization of `parent_active`, `valid_order`, `_zone`, or root decisions is unsafe unless all acceptance, ledger, sequence reset and dynamic enqueue state is represented in a generation key. The current live continuation explicitly catches `_ReopenedERace` and restarts before mutating native provenance; preserve that safety path.

`LiveEContinuation.reconcile:216-305` builds `repr(zone)` dependency records for every candidate and constructs grouped evidence every pass. Replacing repr with an explicit immutable field tuple could reduce formatting/allocation if profiled significant, but must include every current/future dataclass field and preserve Decimal representation. Using dataclass numeric equality alone would lose exponent distinctions currently present in repr. This is lower priority than clear scan reductions.

### Primary PL/PH: range selection and reflection allocation

`_extreme:239-245` scans complete main intervals and preserves first equal source. A main range index can replace this if shared across the immutable chronology, including reflected bullish prices. Complete gate/stop main candles remain inclusive, and long Decimal lexemes must retain their representation.

`_ReflectedChronology:707-713` allocates one wrapper per main and lower row for each bullish primary calculation. The price index itself is correctly reused via `_ReflectedPriceIndex`. A lazy sequence view that wraps only accessed rows could avoid O(M+N) wrapper allocation on every live tick. It must satisfy indexing, negative indexes and length used by the state machine, preserve Decimal `copy_negate` semantics, and remain scoped to the immutable original chronology. Test callbacks and object identity paths carefully; this is a structural follow-up, not the smallest local optimization.

`NativePrimaryOrders.__call__:636-674` rescans each current audit bucket for every proposal, recomputes its causes/confirmation, builds StructureOrders and deep-copies audit causes. A generation-scoped immutable projection is possible only with a real native-ledger mutation generation. Confirmed PH callbacks mutate the ledger (`detect_bearish:398-403`) and deliberately clear pending decisions across all cycles. Reusing proposals after a callback would break global decision chronology, including cycles that previously had no accepted Order. Keep `deepcopy` until audit cause mutation and snapshot ownership are proven safe.

`first_bullish_transition:101-112` reconciles all current highs after every accepted PH, and `_resolve_primary_points:147-172` groups/sorts them. Incremental tracking might reduce repeated work, but physical final numbering and identity-source ownership can change as coincident roles arrive. This is high risk relative to immutable range selection.

## Per-file preservation notes

| Source | Contracts found in current executable source |
| --- | --- |
| A | Sort Blue by reaction number/source/kind, retain invalid Blue ordinals for special route, distinct ordinary and double-stop routes, exact first stop vs recross, inherited stop vs source stop, cycle-after/bridge reuse, exact confirmation-frozen source, original reaction first-match order, live retained object identity |
| S | Original A ordinal, separate source-event and confirmation gates, earliest vs latest equal-main source rules, Type-3 precedence only on exact tie with Type-4, independent Order/candidate race with simultaneous events unresolved, physical shared-order dedupe preference, live input-dependency invalidation |
| E | Physical source ownership, first-equal main extreme, complete boundary main OHLC, global all-route Order choice, disowned-S independent-cause filtering, dynamic reselect/enqueue, family/number arbitration, independent S root restoration, native provenance rebuild |
| Blue | Exact lower prefix through Reaction Break, pending/confirmed strikes, first equal decisive row, healthy-reaction spacing, invalid double-stop Reset Blue, source extreme distinct from rendered price, continuation checkpoint prefix identity, internal/public visibility remains downstream projection |
| PL/PH | Multiple concurrent logical cycles, activation before tied decision, global native callback order, PH vs PL eligibility gates, first-equal main extreme, source identity distinct from decision time, complete main geometry, exact ambiguous lower-event handling, physical roles distinct from logical cycles, bearish-to-bullish `copy_negate` reflection |
| Direction | Frozen slotted singleton primitives; strict comparisons only; `choose_extreme` retains left operand on equality; this module intentionally owns no chronology/lifecycle |
| Core | Existing Decimal objects are returned unchanged; other values use `Decimal(str(value))`; physical identity converts both indexes to ints; no new numerical shortcuts warranted |
| Package init | Compatibility `sys.path` insertion and public Blue imports; no calculation hotspot; avoid replacing flat/module imports without testing both supported entry paths |

## Verification needed for selected changes

1. Capture baseline before edits; compare exact stage state and final stable serialization in both directions, including identity/provenance/ordering and Decimal tuples, not just numeric equality.
2. For range-index replacements, compare against the legacy scan over varied ranges with repeated extrema, equal numeric values with differing Decimal exponents, signed zero, long Decimal lexemes under a small context, missing lower data, irregular timestamps and inclusive exact-end events.
3. Keep main-first and main-last tie policies separate. Check A exact lower confirmation boundaries and E/primary complete boundary main geometry independently.
4. Run current live A/S/Blue/E/primary continuation suites and source-ownership regression paths. The current A suite explicitly covers old stops withdrawing, lower-data fallback suppression, new lower rows displacing an old main-only result, and retained zone object identity.
5. If E reconciliation indexes change, compare all candidate/native-numbered/accepted-source/lifecycle state before and after, and run `test_e_source_ownership.py` cases with dynamic replacement, moved sources, independent roots and hard resets.
6. Measure comparable repeated runtime and peak memory after correctness equivalence. Static complexity improvement is not a measured speed claim.

The initial audit phase performed no production edit or test execution. No Graphify execution, staging, commit, push, or release was performed by this subtask.

## Implementation and verification follow-up

The parent task subsequently authorized this subtask to implement the A lower-range reuse, E parent/child reconciliation maps, and E immutable-chronology sparse-table reuse. Production edits are limited to `a_zone_detector.py` and `e_zone_detector.py`; the parent owns the new `MarketChronology._e_main_extremes` slot in `reaction_engine.py`.

Implemented:

- A indexed lower-range queries use the existing chronology bounds and range-minimum/range-maximum primitives. Empty lower ranges and absent lower indexes retain the legacy scan/fallback path.
- E non-live construction reuses the exact existing `(stop_values, candle_codes, extreme_sparse)` tuple per direction on the current immutable chronology. A chronology without that optional cache builds local tables. Live continuation retains its separate existing main index.
- E reconciliation builds a first-win physical S-parent map and a maximum child-decision map. Dynamically enqueued E children update the latter map before any later eligibility query. All accepted-source and native Order decisions remain live calculations.

New tests are `engine/tests/unit/test_stage_range_refactor.py` and `engine/tests/unit/test_e_reconciliation_indexes.py`. The A scan oracle independently selects winners by chronological row filtering and stable min/max. Its finite domain exhaustively covers 256 four-row signed-zero/equal-lexeme combinations, 66 irregular closed time windows, both directions and both indexed/unindexed paths (67,584 comparisons). Additional checks cover microsecond-inclusive ends, long Decimal lexemes under precision 5, empty lower fallback, reversed ranges, and avoiding lower-window allocation when an index exists.

The E tests cover first physical S-parent precedence with duplicate parents, child-decision maximum rather than first/last child insertion, inclusive exact-event ties, direction-separated cache ownership, same-chronology reuse, new-chronology rebuild after source revision, absence of the optional cache, and live-continuation cache ownership.

Observed verification:

| Check | Status | Observed result |
| --- | --- | --- |
| A tests before production edit | PASS | 9 behavior cases passed; 2 deliberately failing allocation guards exposed the existing lower-window materialization |
| A/live A after edit | PASS | 18 cases passed |
| E tests before production edit | PASS | 16 parent/race behavior cases passed; 2 deliberately failing reuse guards exposed repeated sparse-table construction |
| Targeted A/E/source ownership/live parent/Order lifecycle after edit | PASS | 132 cases passed |
| Full Engine unit suite after initial A/E edit | PASS | 487 cases passed in 2.45 seconds; before the final 4 E optional-cache/live checks were added |
| Final A/E new tests | PASS | 33 cases passed in 0.40 seconds |
| Frozen-original E differential | PASS | 724 comparisons: 720 complete candidate permutations across both directions and three source-ownership layouts; 4 dynamic native Order reselection scenarios |
| Full RAW / runtime / memory | NOT RUN | Parent owns these checks; this subtask ran no heavy RAW workload |

The frozen-original comparison loaded `apps/chart/state/tmp/engine-refactor-20261117/original/engine/pipeline/e_zone_detector.py` under a distinct module name. Both versions consumed equivalent state and the same current dependency implementations. It compared complete returned dataclass field trees using Decimal tuples and also compared accepted E identities, lifecycle starts, candidate history and Order audit state. This isolates the E changes; it does not replace the parent's whole-pipeline baseline comparison.

## Independent review of the parent's performance changes

Reviewed the current diff and owning source for `DetectorBase.minimum_low` / `maximum_high`, `s_zones_for_module_engines`, and `dominant_post_behavior_stops`.

- Reaction's indexed main range selects the same earliest source on numeric equality. Reflected ranges query the original opposite extreme and use Decimal `copy_negate`, matching the existing reflection contract. Live `LiveReactionContinuation._release_indexes` removes both main/lower sequence IDs after each calculation, including the new main index. No new stale live-cache path was found in this review.
- S eligibility's strict predecessor bisect retains the first equal-time item within each collection. Combining the E and visible-S predecessors retains E on a same-time tie, preserving the old concatenated `[E..., S...]` max winner.
- The dominance sweep's precomputed rank incorporates negative original position so the first equal-rank owner still wins. Activation includes the event, and expiry removes an owner only when its end is strictly earlier than the event, preserving inclusive lifetime endpoints. The final by-main ranking remains unchanged.

No behavioral regression was found in these reviewed valid-input paths. This is source review supported by the parent's targeted differential tests, not independent market-correctness proof.

The parent then requested a creation-time index review for `_carried_orders_for_parent`. Mutation/invalidation closure inspected:

| Mutation owner | Existing invalidation |
| --- | --- |
| `register_order_b_reset_legs` | Before nonempty registration and after a new B cause |
| `_reparent_primary_high_causes` | After changed/revoked causes; post-stop index cache also cleared on revoked identities |
| `_register_primary_point` | After new parent cause |
| `_reconcile_primary_labels` | After changed A/B labels |
| `_register_order_audit` | Once after any new identity/cause |
| `ensure_accepted_order_audit` | After all external-restoration merges |
| `_clear_order_audit` | Directly cleared carried query cache; new creation-index state must also be invalidated |
| `_rebuild_accepted_order_audit` | Clears at entry, then inserts/restores identities and unions creation causes; recommended explicit final invalidation for a new index |

No production assignment replacing the E `order_audit` dictionary was found outside its owner. S's separate stopped-A audit is not an E creation-index owner.

The proposed creation index must extract rows in original ledger insertion order. For every nonempty creation list, the old code eagerly reads `confirmation_time` before checking interval membership, and all B confirmation keys are extracted before that read. Retaining that order preserves current malformed-row failures. Sorting malformed non-datetime or mixed-timezone creation events can introduce a new error where the old interval `any(...)` short-circuited, so this corner requires an explicit compatibility path or a demonstrated narrower input contract.
