# CP394 — Independent local primary StopAll reparenting review

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 1202–1249. B05-11, OA31. Source-only, no execution.

## OA31-A — lines 1202–1207

Construct primary label by formatting kind and number without separator; then normalize only parent source index via int and pair with supplied source time. Initialize change flag false and empty revoked set. This occurs even with no ledger rows or null stop/direct identity. No direction check locally; both PH and PL wrappers can call via OA36.

## OA31-B — lines 1208–1211

Traverse authoritative ledger items in native insertion order. Read existing parent cause set with fresh empty default, allocate separate current set, traverse previous set in its native iteration order; no sorting. Missing causes not automatically installed unless resulting set differs.

## OA31-C — lines 1212–1214

Ordered short-circuit parent predicate: kind equals parent-stop, native string label has case-sensitive StopAll prefix, cause source timestamp equals parent.source_time, supplied stop is not None, stored cause event equals supplied stop, stored event strictly later than decision. Source index not compared in this route. Equal decision fails. No global condition requiring direct candidate.

## OA31-D — lines 1215–1221

Retain nonmatching original tuple in new set. For matching tuple, retain replacement only if ledger identity equals direct_identity; replacement uses original kind, newly formatted label, empty family, original event and source; no extra fields retained. Null direct removes matching native identities. Set equality deduplicates naturally; replace entry cause set and set changed only if sets unequal, otherwise preserve existing set object. Does not move cause to another row.

## OA31-E — lines 1222–1227

Walk existing B cause sequence, default empty tuple. Post-stop predicate is ordered: string of label (default empty) begins StopAll, exact stored source-index/time tuple equals normalized parent pair, supplied stop not None, stored post event equals supplied stop, supplied stop strictly greater than decision. Both tuple operands evaluated before equality; stored index not normalized here. No direct identity gate, no comparison of reset or anchor fields.

## OA31-F — lines 1228–1230

On post predicate success assign only postBehaviorType in existing cause dictionary and mark changed; no check whether new label equals prior. Then unconditionally read resetReactionIdentity, regardless of post predicate result.

## OA31-G — lines 1231–1236

Independent anchor predicate: native string label with StopAll prefix, exact anchor source pair equals parent pair, truthy reset identity, main timestamp indexed by int(reset_identity[0]) >= decision. Equality included; no stop-event/direct gate; no Break comparison, no clamp, no reset confirmation comparison. Assign only anchorBehaviorType in same dictionary, mark changed. Both roles may relabel in same cause. No resort or dedup after mutations.

## OA31-H — lines 1237–1240

After both cause routes, add identity to revoked set if current parent set is falsey and entry B causes get is falsey. Includes rows already causeless; absent/empty B list qualifies, any truthy B causes protects regardless of relabel. Defer deletions until ledger traversal complete; delete each revoked key in native set order, not chronologically sorted.

## OA31-I — lines 1241–1246

If revoked nonempty, build filtered confirmation list retaining every item whose raw pair at slots 1,2 not in revoked; preserve surviving order, remove all duplicates for revoked identities. Assign by full slice preserving index list identity, then invoke post-stop invalidator. Cause-only changes do not invoke post-stop invalidation. Failure before assignment can leave deleted ledger rows with old index.

## OA31-J — lines 1247–1249

If changed truthy or revoked truthy, invalidate carried cache after post-stop step when applicable. Otherwise no invalidation. Implicit None return. No local catch, rollback, reset-map deletion, price arithmetic, geometry/cross rewrite or candidate/direct cache flush. Errors may leave earlier role mutations, deletions or cache effects; no empirical failure asserted.

## Consumer boundaries

- engine/pipeline/order_audit_engine.py:1250–1310: PH wrapper requires bearish and PH kind, PL requires bullish and PL kind; both call OA36, which obtains stop/direct then invokes OA31 even if direct None. OA34 requests first strict directional lower cross after decision and before range_end; OA31 trusts passed event and identity, performs no price search. OA36 may subsequently create row, index and add parent cause. OA31 does not itself relocate or create a missing direct row.
- engine/pipeline/order_audit_engine.py:1135–1199,1312–1337: OA30 creates B cause dict and stable sorts by post/Reset/strict break/physical identity, while OA31 edits two role labels in place and does not repeat dedup/sort. OA38/39 label reconciliation is a separate later route; not equivalent to StopAll role eligibility. Native cause shapes and timestamp/index validity owner-dependent.
- engine/pipeline/order_audit_engine.py:1100–1132,1798–1826,1920–2008: Confirmation index tracks geometry, not creation roles. Revocation modifies index in place and invalidates post-stop result cache/sorted audit/pending; carried invalidation clears creation state as well. Cause-only edits affect carried, not post-stop cache. No claim of arbitrary cache mutation safety or independent stream equivalence.
- Algorithms/V3/State_Machines/04_Order_Ledger.md OLC05/06: Parent-stop source-time comparison and B source pair are different, post role requires exact strict-later stop while anchor uses inclusive reset First main bound. StopAll historical reset boundaries remain. Ownership transfer conditional on native supplied evidence, not a new acceptance rule.

## Verification

236 category rows, 64 prior W1, 172 additional; five supplements; 3336 prior rows revalidated without overlap. Local scoped acceptance only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP394_W3_B05_Primary_StopAll_Reparenting_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP394_Completion.json).
