# CP405 — Independent local public rebuild and ensure accepted Order audit

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA64–OA65 lines 2234–2290. B05-22. Source-only; no algorithm execution.

## OA64-A — lines 2234–2243

Public wrapper accepts a zones sequence and optional supplemental S sequence defaulting to empty tuple. Its documented caller motivation is external continuation replacement after detect, not independent validation of the accepted E branch.

## OA64-B — lines 2244–2248

Resolve the rebuild method, materialize zones through list before call, forward supplemental_s_zones as the original object by keyword, and return the callee result directly. List is shallow and preserves iteration order and element identity; neither wrapper sorts, deduplicates, validates, normalizes nor copies supplemental items. Iteration or dynamic lookup can fail before call; callee failures propagate with no rollback. OA62 itself sorts the result.

## OA65-A — lines 2249–2259

Ensure accepts same interface/default. Its purpose is to augment accepted audit after external independent S-owned E restoration without unconditionally discarding historical physical identities needed by already-created StopAll/history. The stated purpose is not proof every old row survives.

## OA65-B — lines 2260–2263

Before OA62, traverse order_audit.items in native mapping iteration order. Make a new outer mapping and shallow new entry per identity, replacing causes with a fresh set constructed from entry.get(causes, empty set). Default only applies to missing key; present None/noniterable or unhashable members may raise before the rebuild, with no snapshot publication to ledger. Duplicate equal causes collapse. All other fields, including reaction object and nested B-cause collections/dicts, remain aliases; no deep snapshot, and subsequent mutation of shared values may be observed. Native identity equality/hash and mapping expansion apply.

## OA65-C — lines 2264–2266

After full snapshot, materialize zones into shallow list and call OA62 with unchanged supplemental sequence by keyword. Store returned sorted list. OA62 first publishes accepted source pairs, derives exclusions, snapshots prior parent causes, clears ledger/index and carried/post-stop state, registers B legs and parents, recovers historical parent causes then sorts; failures can leave partial changes. OA65 has no try/finally or rollback; failed list conversion prevents OA62 invocation, failed OA62 prevents all later ensure steps.

## OA65-D — lines 2267–2271

After successful rebuild, read actual invalid_s_root_identities and newly accepted E source identities directly (no getattr fallback). Evaluate native pair-set union, unpack each member into exactly two components, and project source_time into a set, discarding index without normalization. Equal times collapse, and an S cause from a different index at that time can be excluded. Missing attributes, unsupported union, malformed pairs or unhashable projected times can fail after rebuild; no rollback.

## OA65-E — lines 2272–2274

Iterate preserved identities in snapshot insertion order. If identity is present in rebuilt ledger under native membership, skip completely: no preserved cause or B merge, no geometry replacement, no re-index, and no absent-row filter. Even a falsey stored value is membership-present. Absence, not current row truthiness or lookup success, enables restoration.

## OA65-F — lines 2275–2279

For absent identity, replace snapshot causes with fresh set retaining every cause except one for which slot 1 equals literal S, length is greater than four, and slot 4 belongs to invalid time set, in that exact left-to-right short circuit order. No cause-kind test, no falsey guard, no tuple/type check, no source index or normalization. Empty/one-slot cause can raise at slot 1 before length; short S shape of length 2–4 survives; non-S bypasses length and membership. Non-parent kind with S label and matching invalid time is removed; other hashable non-parent shapes may survive. Unhashable membership operand or user-defined native protocols may raise. Prior set conversion and comprehension are distinct; a filter exception occurs before assignment of that new set.

## OA65-G — lines 2280–2281

Skip if filtered causes falsey and order_b_causes retrieved with get is falsey; B field lookup is short-circuited when filtered causes are truthy. No kind or acceptance validation of retained cause or truthy B payload. Thus B-only absent rows can restore even when all parent causes were removed; unlike OA62 historical restoration which requires valid parent-stop cause, ensure preserves any remaining cause or truthy B collection. No requirement for both.

## OA65-H — lines 2282–2286

Publish the preserved shallow row to the authoritative ledger before indexing original stored confirmation_time. Do not recalculate crossing, Decimal prices, reaction, or confirmation from geometry. Missing confirmation, malformed physical identity or failing index insertion can leave ledger published without corresponding index; previously restored rows persist and later rows are not processed. Actual OA26 unpacks identity and inserts (confirmation,First,Break) at bisect-right; existing post-stop sorted dictionary gets pending append, otherwise sorted cache becomes None. OA27 rebuild clears index and post-stop cache; no additional post-stop flush in ensure. Index coherence and downstream owner acceptance remain conditional.

## OA65-I — lines 2287–2290

After normal completion of all iterations, call carried invalidator unconditionally, even with no preserved rows or all skipped. Actual OA29 clears carried result cache and sets carried creation index/append to None; it does not clear post-stop cache. Earlier exception bypasses this call; invalidator exception prevents return. Return OA62's already sorted E-zone list, not restored ledger rows, and do not re-sort/rebuild after restoration.

## Consumer boundaries

- `engine/pipeline/order_audit_engine.py` (1100–1132, 2046–2086, 2209–2231, 2234–2290): OA26 indexes (confirmation,First,Break) using bisect-right, appends pending if post-stop sorted audit is dict, otherwise sets sorted state None. OA27 clear invalidates carried and post-stop caches. OA29 carried invalidation clears carried cache/index/append only. OA62 publishes new accepted source set, clears/rebuilds and restores only historical valid parent-stop causes; returns sorted numbered E zones. OA65 restores absent physical rows on any remaining cause or truthy B collection without crossing recomputation and invalidates carried on normal completion.
- `engine/pipeline/e_zone_detector.py` (1495–1506): Normal detect clears old accepted identities/audit, registers B, discovers, reconciles, applies consumed S and same-source conflict resolution, then invokes OA62 directly. The wrappers are later external paths and do not repeat those acceptance decisions.
- `engine/bridge/trading_pipeline.py` (2535–2557, 2606–2635): Continuation replacement precedes OA64; it forwards the final E list and a newly assembled list of consumed S items, then filters invalid public S identities. StopAll feedback reconciles or takes copied E/no stopalls on alternate branch, restores independent S roots, assigns OA65 result with default supplemental sequence before accepted Order B reset-leg discovery (which consumes E, stopalls and detectors). No independent convergence, final acceptance or arbitrary runtime dispatch claim.

## Exact structural reconciliation

Seven-category counts: branches 9, comparisons 4, arithmetic 4, calls 13, accesses 86, effects 8, exits 4. 128 total (30 W1, 98 Additional), 4 separate historical supplements. All 6979 prior rows (1626 W1, 5353 Additional) and 130 prior supplements revalidated; exact disjoint local union 7107/8318; 1211 later rows. All 1892 CP316 links reconciled. One filter ID at 2277:19:UnaryOp resolves to AST 9251, branch row 477. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP405_W3_B05_Public_Rebuild_And_Ensure_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP405_Completion.json).

- Source-first local review by GPT, not independently staffed. OA64/OA65 operate on supplied accepted zones; neither independently establishes final E/S acceptance or valid B legs. Aliased reaction/B state, dynamic dispatch, native equality/hash and malformed input paths remain source-conditional.
- OA65 is ordered mutation, not transactional. Existing rebuilt identities take precedence without preserved merge; B-only absent restoration is not universal preservation. Index/cache coherence and feedback convergence are separate owner contracts; runtime equivalence and new cross-owner acceptance are not asserted.
- No RAW payload, runtime, ZIP, production changes, performance measurements, fresh AST generator, or independent SHA-256 claim. Git blob identities and full recursive tree/readback are the publication evidence.
