---
title: Final Engine removal and refactor code review
document_role: evidence
lifecycle: historical
owner: engine-refactor-20261117
created_at: 2026-11-18T07:11:45+03:30
last_modified_at: 2026-11-18T07:12:01+03:30
---

# Final code review

Review target: the current uncommitted working-tree diff against HEAD `26a61a0`, following the task implementation plan and root `AGENTS.md`. This review covered the changed production Python and Chart paths, affected consumers, new unit contracts, baseline/comparison runners, and maintained-documentation changes. No Graphify execution, staging, commit, push, RAW edit, or heavy RAW workload was performed by this reviewer.

The review began independently and read-only. After two demonstrated findings, the parent explicitly authorized this reviewer to fix only the post-stop iterator and its tests. Those fixes are disclosed below; this report is not a second independent review of their authorship.

## Strengths

- The retired assessment/position stage is removed at its owner, bridge invocation, live continuation and presentation consumers. Native Order/OrderAudit and primary calculation remain in place. Runtime searches found only intentional legacy normalization references to the retired drawing/object types.
- Existing immutable range indexes retain earliest equal extrema and exact Decimal objects. The reflected main-candle route queries the original opposite extreme and uses `copy_negate`. Live continuation releases sequence-keyed indexes, and the new E sparse cache belongs to one chronology and direction.
- S predecessor lookup preserves strict source precedence, first equal-source ownership and E-before-S ties. The dominance sweep retains first equal-ranked ownership and inclusive lifetime endpoints. The new differential tests exercise those contracts rather than merely checking speed or call counts.
- E parent/child indexes preserve the first physical S parent, maximum child decision and dynamic enqueue updates. Carried creation indexing preserves ledger order and has a conservative legacy path with isolated Decimal validation.
- The final `_register_order_audit` invalidation refinement is consistent with the actual carried query: new physical identities, first parent creation and earlier minimum creation invalidate it; later/equal parent provenance remains authoritative in the ledger without changing any carried match. Other cause mutation/revocation owners retain broad invalidation. Disowned-S eligibility reads current causes directly.
- Legacy drawing/history normalization retains unrelated drawings and native objects. Loading normalizes the browser copy; a later ordinary save also omits retired position rows from filesystem storage. This is consistent with the explicit complete removal scope. Manual Review retains native event inspection, filtering, Bridge detail and export without restoring old verdict state.

## Findings resolved during review

### P2: Preserve skipped-row errors and eager query failure order

Owner: `engine/pipeline/order_audit_engine.py`, `_iter_post_stop_accepted_orders` (current line 1744).

The original complete query excludes accepted rows confirmed at or before the parent stop before normalizing their prices. The new iterator initially normalized every row, so an excluded row with `stop_level="invalid-decimal"` changed `[]` into `decimal.InvalidOperation`; an excluded mixed-timezone crossing likewise introduced a `TypeError`. As a generator, it also delayed a selected malformed-row error until iteration, after the direct Order route had already been evaluated.

Resolution: prepare the iterator eagerly; validate and cache native generations once inside `localcontext`; delegate malformed/partial generations to the unchanged complete query before returning an iterator. Native generations still enumerate lazily, and a test verifies no repeated ledger scan across parent queries. Native uncrossed rows use the fast path only when the existing immutable crossing cache confirms the absence of a crossing.

Tests: `engine/tests/unit/test_carried_order_query.py` lines 185, 198, 212, 222 and 233. Three expected RED failures were observed before this fix; the partial-row lookup characterization already passed and remains covered.

### P2: Preserve identity insertion order after an audit replacement

Owner: the same post-stop iterator, including its duplicate-geometry guard (current line 1831).

Small reproducer: initial identity X `(5,8)` confirms at 130 and stops at 230; audit X and Y `(5,6)` both confirm at 190 and stop at 215. At parent stop 125, the complete query retains X's earlier dictionary insertion position after replacing its geometry, producing `[X,Y]`. The original stream instead produced `[Y,X]`; a real E calculation consequently selected BreakIndex 6 instead of 8. This is an observable ordering/provenance difference, not only a hash discrepancy.

Resolution: cache a conservative legacy-query fallback when an initial/audit duplicate identity has differing stop/confirmation geometry. Equal native geometry retains the stream path. This avoids guessing the original query-specific insertion rank from a winning audit row.

Tests: `test_post_stop_replacement_keeps_initial_identity_insertion_tie`, current line 252, covers both complete query order and the final E-selected physical identity. Both expected RED failures were observed before the fix.

## Verification observed by this reviewer

| Check | Status | Evidence |
| --- | --- | --- |
| Current production diff, owners and mutation paths | PASS | Source inspection and targeted runtime/reference searches |
| Final carried/post-stop unit file | PASS | 43 tests, 0.57 seconds |
| Final full Engine unit suite | PASS | 507 tests, 2.74 seconds; `python -B -m pytest engine/tests/unit -q --tb=short` |
| Whitespace check for the reviewer-edited source/test | PASS | `git diff --check` completed without output |
| Final-source full RAW equivalence/repeats/performance/memory | INCOMPLETE | Parent owns the running matrix; this review does not promote an older candidate measurement to a final-source PASS |
| Chart suite/build/browser checks | NOT RUN | Inspected implementation and task evidence; did not independently rerun these checks |
| Regenerated exact-source References after the final fixes | NOT RUN | Parent must synchronize and verify the final source bytes |
| Independent market correctness | NOT RUN | Neither unit parity nor baseline equality establishes universal market correctness |

The comparison runners use paired fresh processes and direct stable output bytes with only top-level timing telemetry excluded. That is appropriate for the implementation-only part of the task. Performance claims must use the final frozen candidate and completed comparable measurements.

## Declined to judge

- Strategy profitability and correctness of unchanged trading rules: the task requires preserved native behavior, not a new strategy or an independent market-rule certification.
- Arbitrary adversarial objects or malformed private-helper arguments outside validated RAW/runtime inputs: these were not exhaustively assessed. The concrete accepted-ledger exception and ordering differences found here were addressed rather than dismissed.
- Historical `engine/engine.zip` and old verification artifacts: they are not current runtime inputs, and release/package regeneration was not requested. They must not be described as newly synchronized production packages.
- Vault snapshot rebuild: the plugin/Vault evidence is a separately pinned older snapshot. Explicit user removal scope governs this change; local source/reference synchronization must not be represented as a completed external Vault rebuild.

## Assessment

No unresolved Critical or Important production code finding remains from this review. The reviewed source is ready for the parent's final verification and integration decision. Whole-task completion still requires the final-source RAW/performance matrix and final reference synchronization owned by the parent. No release or publication is authorized by this verdict.
