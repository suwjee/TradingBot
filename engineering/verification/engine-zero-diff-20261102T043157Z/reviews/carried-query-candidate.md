# Carried-Order query: smallest candidate after the repaired baseline gate

Read-only design evidence. No production/test/Reference/Vault edit and no runtime, test, profile or benchmark execution occurred for this follow-up. Only this report was written. The parent owns the separately authorized ordering repair, version policy and running repaired-before matrix. Do not implement this candidate until those gates complete.

## Recommendation

**Worth trying first: reuse the parent-creation list and remove the per-row B generator, without reordering any eligibility predicate.** This is a small local allocation/control-flow optimization of `order_audit_engine.py:1423-1432`. It changes no cache, index, caller, ledger shape, creation rule, numeric operation, accepted-state rule or output ordering. It removes work from the measured expensive scan while preserving the existing malformed-row failure ordering more closely than a naive early rejection.

The original saved `before/profile/xau-oct26-30s-bullish/top-cumulative.txt` reports 27,911 `_carried_orders_for_parent` calls, 14.924s cumulative and 8.523s self, within a 60.958s cProfile total. Its B extraction generator at line1429 accounts for 4,638,677 cProfile calls/resumptions and 0.929s. These are measured original-profile facts, not a predicted improvement or a repaired-candidate benchmark. The proposal still scans the ledger and builds a parent-date comprehension, so a large speedup is not guaranteed. It is a safer first experiment than adding mutation-sensitive indexes or changing error semantics. Reject it if comparable after measurements do not improve the objective.

## Concrete proposed patch — not applied

```diff
         matches: list[OrderMatch] = []
         for entry in self.order_audit.values():
-            a_created_events = [
+            created_events = [
                 cause[3]
                 for cause in entry.get("causes", set())
                 if cause[0] == "parent-stop"
             ]
-            created_events = [min(a_created_events)] if a_created_events else []
-            created_events.extend(
-                cause["physicalOrderConfirmationTime"]
-                for cause in entry.get("order_b_causes", ())
-            )
+            if len(created_events) > 1:
+                earliest_created = min(created_events)
+                created_events[0] = earliest_created
+                del created_events[1:]
+            for cause in entry.get("order_b_causes", ()):
+                created_events.append(cause["physicalOrderConfirmationTime"])
             if not created_events:
                 continue
             confirmation = entry["confirmation_time"]
             crossed = entry.get("stop_cross")
             if (
                 not any(lifecycle_start < created < parent_stop for created in created_events)
                 or confirmation > parent_stop
                 or crossed is None
                 or crossed[2] < parent_stop
             ):
                 continue
```

The remainder of the function stays byte-for-byte unchanged apart from inevitable line shifts. Keep the existing parent-date comprehension instead of replacing it with a lazy `min(generator)`: the comprehension first extracts every applicable parent tuple element before the minimum comparisons begin. That existing exception/evaluation order is useful to preserve. A singleton minimum is exactly its sole element even if that element is malformed; the later original comparison still raises in the same place in the logical sequence. The empty case still has no parent creation event.

Do not also move `confirmation`, `stop_cross`, cause-window qualification, current-parent registration, or initial-ledger handling in this first patch. Do not combine it with the previous first-match-S proposal, an accepted-order index, a cache invalidation redesign or a version-policy decision.

## Why the obvious early rejection is not fully equivalent

For valid native records, rejecting on `confirmation > parent_stop`, `stop_cross is None` or `stop_cross[2] < parent_stop` before allocating creation lists would give the same result. Every native creator inspected writes complete confirmation/cross fields. That observation is not enough to claim identical failure behavior for this duck-typed API:

- A cause-less row can legitimately be skipped before accessing missing `confirmation_time`; eagerly indexing that field raises instead.
- Every B cause's `physicalOrderConfirmationTime` is currently extracted before confirmation/cross metadata is accessed or any date eligibility comparison occurs. A malformed B cause must not be silently hidden merely because the Order is open or its confirmation is in the future.
- Creation-date comparisons currently precede the cheap rejection predicates. A malformed creation timestamp or aware/naive incompatibility can raise even when a later confirmation or missing cross would reject a well-formed row.
- Lazy `any` across B extraction can stop after a valid first cause and hide an invalid later cause, which the current eager extension would visit.

Therefore the simple early-rejection patch cannot preserve both all supported result cases and the currently observable invalid-record failures without either a row-shape contract narrowing or a validated fast path with fallback. The public ledger is a mutable dictionary and existing tests deliberately build partial rows; no validated-record marker currently proves it safe to skip extraction. A validation guard that scans every cause and checks all timestamp compatibility can eat the intended gain and is larger than the recommended allocation patch. Do not silently turn malformed data into an empty result for performance.

## Exact-equivalence argument

Let P be the list of `cause[3]` values extracted in the original set iteration order for parent-stop causes; let B be the list of physical confirmation values extracted in original B-cause list order. The old creation sequence is `([min(P)] if P else []) + B`.

- If P is empty, the new parent list is empty.
- If P has one element, the new list already equals `[min(P)]` without a minimum call.
- If P has two or more elements, the same `min` processes the same already-extracted list in the same order. Replacing element0 with that exact winner and deleting the tail produces the same one-element sequence. Tied winners retain the same first object.
- The ordinary B loop appends all the same looked-up values in the same order before any metadata access or eligibility comparison. It does not short-circuit.

Consequently `created_events` has the same elements, object identities and order before the unchanged eligibility test. The parent-stop rule remains the **earliest parent creation only**, plus **all B physical confirmation events**. It must not become `any` parent creation: a later parent cause inside the lifecycle does not qualify an Order whose earliest A-type creation is outside it.

The unchanged function still requires strict `lifecycle_start < created < parent_stop`, inclusive `confirmation <= parent_stop`, non-null stop crossing, and inclusive `crossed_event >= parent_stop`. Missing `parent.decision_event_time` still returns an empty list before the cache. Same-event boundaries, canonical Reaction references/numbers, Decimal stop values, source indices/times and output tuple content are untouched.

The live mutable ledger is still traversed in insertion order; initial records are still appended afterward. The final stable sort remains `(exact Order stop, -FirstIndex)`. Do not introduce a new First/Break tie key or traverse confirmation order instead: exact remaining sort ties currently retain insertion/append order. Cache values remain tuples returned as fresh lists on hits. No native creation/use route is converted or deduplicated differently.

## Caller and data-shape audit

Live search found one production call site: `EZoneDetector._zone`, E lines378-490, specifically line391. It queries carried Orders **before** registering the current parent's Order at392, then builds the complete E race from direct, inherited, carried and post-stop accepted routes. It rejects disowned creator-only candidates after the global stop/First sort. Moving registration before this query would change creator chronology and is excluded.

Direct test calls are lifecycle-contract lines252,258,331 and Order_B lines270-275. The Order_B test uses a `SimpleNamespace` detector with a valid B-only row, cached/initial-record stubs and **no confirmation index**, which is an exercised supported shape. The proposed patch adds no new detector requirement and still supports it.

Mutable E native rows contain canonical `reaction`, integer `reaction_number`, datetime `confirmation_time`, Decimal-compatible stop level and source metadata, optional exact stop tuple/None, a `causes` set of parent-stop tuples, and optional B-cause list. A parent-stop tuple's consumed fields are kind at0 and event at3. B consumes `physicalOrderConfirmationTime`; the complete recorded provenance remains untouched. Physical fields are written when a row is created/restored, while cause sets and B labels can change later.

S's A-owned audit has a different shape (`a_source_time`, `a_stop_event_time`, `a_causes`) and may omit `stop_cross`. It is supplied as the separate initial ledger and materialized through `_initial_order_records`; it is not this mutable native scan. The proposed patch deliberately leaves that initial path untouched.

Tests also hold intentionally partial E rows containing only cause information (`test_order_audit_lifecycle_contracts.py:168-170,214-216`) for ownership checks. Those rows are not permission to assume every dictionary in the public ledger has prevalidated physical fields. The proposed local transformation leaves the existing success/failure evaluation path intact when a partial row reaches this query.

## Every native ledger mutation relevant to this query

These paths were included in the earlier complete Order module read and rechecked by the live mutation search; the assigned Order module remains SHA-256 `84201f1784fe9a1c924c8c6d3a8f67999d629032c6987c4384a4330954acf2af` with no Git diff at review time.

| Mutation path | State affected | Existing carried-cache handling |
| --- | --- | --- |
| E initialization, E133/177 | Separate initial audit reference; new empty live audit. | New run-scoped cache at E167-169. |
| `_clear_order_audit`, Order928-932 | Clears live ledger and chronological index. | Clears carried/post-stop caches. |
| `register_order_b_reset_legs`,945-1009 | Creates complete rows, appends/deduplicates/sorts all reset causes; preserves independent parent causes. | Invalidates carried cache when legs are registered and when a new cause is added. |
| `_reparent_primary_high_causes`,1012-1058 | Replaces/removes obsolete StopAll parent causes, relabels eligible B provenance, removes cause-less identities/index entries. | Invalidates carried on cause/identity change; post-stop on revocation. |
| `_register_primary_point`,1076-1107 | Creates complete PH/PL native rows, including open `stop_cross=None`, or adds a parent cause. | Invalidates when cause added. |
| `_reconcile_primary_labels`,1117-1134 | Replaces parent aliases and B cause dictionaries with deduplicated relabeled equivalents. | Invalidates on cause content change. |
| `_register_order_audit`,1136-1208 | Applies invalid S/sequence gates, creates complete rows and/or adds one valid native parent cause. | Invalidates when ledger/cause state changes. |
| `_rebuild_accepted_order_audit`,1579-1764 | Filters disowned S causes, clears/rebuilds accepted parents and B causes, recreates covered rows and restores valid historical rows/causes. | Clear establishes fresh cache state; creator registration invalidates as needed. Retained historical creator rights remain authoritative. |
| `ensure_accepted_order_audit`,1782-1821 | Preserves valid independent identities across subset rebuild, filters invalid S, restores index entries. | Final carried invalidation. |
| `sequence_resets` setter, E229-246 | Replaces hard-boundary map and sorted reset-time index. | Clears contextual carried/candidate/post-stop/direct caches; retains immutable physical caches. |
| Test-only direct mutations | Adds/replaces causes or synthetic rows at unchanged ledger size. | Existing focused tests clear/query explicitly and verify cause-sensitive behavior; candidate adds no stale derived state. |

S `_record_a_order_audit` (Order2131-2163) mutates the separate initial A-owned ledger, not the E live dictionary. `prepare_order_audit` and Bridge projection read/merge accepted data; they do not replace this native scan with a serializer-owned rule. No additional production direct assignment to the E native ledger was found outside its owning module.

The candidate introduces **no derived cache or index**, so it requires no new invalidation or ownership promise. All of the mutation cases above remain governed by the current rules and test anchors.

## Why existing indexes are not the first candidate

The confirmation index could identify a confirmation prefix, but this carried route also depends on earliest parent creation, all B creation events, parent lifecycle start and exact stop liveness. It does not index those causes. Iterating its sorted tuples instead of the ledger changes residual tie order; building a membership set and then scanning the ledger still costs O(A) and adds O(A) per-query temporary memory. The supported B-only stub has no index, and silently ignoring unindexed rows would change behavior. A proper creation/liveness index must account for every addition, cause-only update, revocation, restoration, relabel/dedup and hard reset while preserving insertion rank. That is a larger second-stage design, justified only if the local patch is insufficient and profiles still show this owner dominates.

## Memory and performance limits

Let p be parent-stop causes on one row and b its B causes. The old temporary state retains the full p-element parent list plus a separate 0/1+b-element creation list and the B generator. The candidate retains one creation list, whose logical contents are collapsed to0/1 before B append; its peak logical reference count is approximately `max(p, (1 if p else 0)+b)` instead of `p+(1 if p else 0)+b`. Python list capacity and allocator behavior can differ, so this is not a measured byte reduction. The minimum winner is the same existing datetime object; no domain object or provenance dictionary is copied or discarded.

No retained per-run memory is added. Existing carried cache worst-case storage remains O(K*M) OrderMatch references for K distinct lifecycle contexts with up to M matches, plus the unchanged initial-audit/index views. Scan and sorting complexity remain O(A + total causes + relevant initial range + M log M) per cache miss. This is a constant-factor allocation optimization, not an asymptotic claim. cProfile timings are instrumented evidence and must not be compared directly with unprofiled wall-time as a speedup.

## Verification to run only after parent gates pass

1. Preserve the repaired-before baseline and full output order. Run the narrow current lifecycle, E-source ownership, Order_B and native PH/PL parent tests first, then the complete current suite. In particular retain cause-only refresh at lifecycle249-258, B-only carry at Order_B245-275, valid historical parent removal at lifecycle285-295, independent B retention at299-322, reset-publication at326-372 and disowned-S independent E/B rebuild at E-source382-413.
2. Add focused independent contract cases for empty/one/multiple parent causes; earliest parent outside versus later parent inside; B-only and shared A/B; empty B sequence; all lifecycle/confirmation/cross equalities; open Orders; identical final-sort keys; canonical Reaction `is` identity; cache hit list isolation; same-count cause mutation; rebuild/restoration and both directions. Expectations should assert domain selections and ordered tuple content, not mirror the implementation's temporary lists.
3. Preserve error cases: cause-less row missing physical fields remains skipped; nonempty cause with missing confirmation still raises the same `KeyError`; malformed B lookup raises before confirmation/cross rejection; malformed parent tuple retains indexing failure; mixed/invalid creation timestamps retain minimum/window comparison failures; a short cross tuple is inspected only after preceding conditions pass. A later malformed B must not disappear behind an earlier eligible cause. Traceback line/frame locations can change with implementation; do not claim byte-identical traceback text unless that separately required contract is actually tested.
4. Compare complete stage/native audit and final serialized bytes against repaired-before for all22 current scenarios/repeats, including direction and repeated regimes. Preserve original pre-repair artifacts and report their separate key-order delta under the parent's already disclosed authorization. No sorting or baseline rewriting may conceal a candidate difference.
5. Only after equality passes, run comparable unprofiled repeated timing/peak-memory checks and the same bounded profile context. Confirm whole-run improvement and no material memory regression; exact-match correctness remains decisive. If the small patch is slower or noise dominates, retain the baseline implementation and evaluate the next measured candidate separately.

All candidate verification and performance claims are currently **NOT RUN**. No version bump is selected in this report; the parent owns the public/implementation metadata policy and Source/Reference synchronization. The concrete patch is a reviewable proposal, not an implementation or a PASS.
