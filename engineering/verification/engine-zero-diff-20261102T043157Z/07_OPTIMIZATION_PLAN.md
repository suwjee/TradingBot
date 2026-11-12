---
title: Risk-ranked Engine optimization plan
document_role: evidence
lifecycle: generated
owner: engine-zero-difference-audit
created_at: 2026-11-02T10:35:59+03:30
---

# Optimization plan

Spec: discovery/USER_REQUEST.md plus the user's delegated preparatory-repair choice with strict calculation equality. This plan has no authority to alter trading semantics, public payload values or baseline expectations.

## Prerequisite gates

- Original full Source/prose read and44-run baseline are preserved, including the2mapping-order failures.
- The separate preparatory Bridge key-order repair must show zero other calculation differences and a complete deterministic repaired-before matrix before any performance Source edit.
- Capture immutable post-repair production bytes/hashes and complete public payloads; collect selective native snapshots for each scenario where accessible and representative warm and separate fresh profile probes. No profiler runs concurrently with normal measurements.
- Original and repaired baseline paths remain separate. Final optimization comparison uses ordered bytes and typed field content against repaired-before, with only top-leveltimings excluded.

## Candidate O1: carried-Order temporary creation-history reduction

Owner: `engine/pipeline/order_audit_engine.py`, `_carried_orders_for_parent`, original1423-1432. Actual original profile identifies this query as a material cumulative hotspot; see06_PROFILE_HOTSPOTS.md and raw pstats. Both directions call the shared owner through E._zone before registering the current parent's new Order.

Exact contract: first collapse all eagerly extracted parent creation events to their earliest event (first equal object), then eagerly extract every B confirmation in source order. Preserve strict lifecycle_start < creation < parent_stop, inclusive confirmation <= parent_stop and crossed event >= parent_stop, current failure precedence, native Reaction is identity, ledger insertion order and stable residual sort ties. Keep all cache keys, invalidations, data types, Decimal conversion, initial-ledger path and output tuple fields unchanged.

Proposed implementation: use the parent-created list as the working creation list. Empty and singleton lists already equal their reduced representation; call min and replace with a one-element list only for multiple parents, releasing the large old scratch list before B extraction. Append each B creation directly instead of allocating a generator for list.extend. This retains the old eager extraction/predicate order. It introduces no cache/index or persistent state. Scan/sort asymptotics remain unchanged; the expected gain is fewer temporary allocations and generator resumptions, not a claimed asymptotic speedup.

Worst-case temporary references shrink from roughly p+1+b to max(p,1+b), where p parent causes and b B causes describe a row. Python allocator byte behavior must be measured. No retained run memory is added; existing cache worst-case capacity and object lifetime remain the same. A naive stop/confirmation prefilter is rejected because it can hide malformed-row errors and alter supported partial-row behavior.

## Test and measurement sequence

1. New `engine/tests/unit/test_carried_order_query.py` pins independent literal domain expectations for parent/B creation, earliest-only parent rule, both directions, strict/equal boundaries, residual insertion ties, canonical object identity, fresh cache lists and partial/malformed rows. Characterization expectations must already pass on baseline; do not alter an expected result for the optimization.
2. A focused runtime allocation contract uses an artificial typed dense-provenance query row to require one history-sized scratch footprint; it is not a claim that10k simultaneous creators are market-reachable. Watch its current redundant-history peak fail the generous140kB budget for two10k-pointer histories before the patch; observe GREEN only after actual lower allocation, with unchanged selected native Order. The test checks real traced resources, not source text or a mocked call counter.
3. Make the smallest owner patch. Update only this module's existing version/timestamp according to current live convention; its current version is1.8.1, not the older Vault snapshot. Keep all serialized envelope version fields unchanged. No new dependency or module.
4. Run focused and complete current Engine tests, supported parse/import/CLI, direct native snapshot and full22scenario ordered-output equality against original repaired-before artifacts. Any first difference rejects candidate acceptance; preserve evidence and undo only this candidate's bytes if necessary.
5. Run comparable uninstrumented cold/warm repeated measurements and a separate profile. Prefer5 measured repetitions on practical scenarios; retain actual counts/median/min/max and use fewer documented repetitions for multi-minute month runs. Check OS peakWorkingSet and Python allocation separately, with sampling limitations.
6. Retain only if actual CPU/wall/allocation improvement justifies the small patch and complete equality remains0. A faster helper with an unexplained whole-run regression is not accepted. If noise dominates, collect paired comparable measurements or reject; never quote only the fastest result.
7. Synchronize both exact-source directional References, source manifests/indexes and truthful implementation history; rerun integrity/tests/equality after synchronization. Preserve canonical Vault trading semantics and pre-existing ambiguity records.

## Deferred higher-risk alternatives

Creation/liveness indexes across mutable audit state, reordering eligibility before eager extraction, cached E detector/table reuse across regimes, S canonical first-only lookup and Blue containment indexes require separate evidence/proofs. Do not combine them withO1. They remain proposals rather than retained improvements.
