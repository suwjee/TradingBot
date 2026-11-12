---
title: Change ledger
document_role: evidence
lifecycle: generated
owner: engine-zero-difference-audit
created_at: 2026-11-02T10:35:59+03:30
last_modified_at: 2026-11-02T12:31:27+03:30
---

# Change ledger

## R1: Separately delegated deterministic Bridge key order

Owner: engine/bridge/trading_pipeline.py, merge_regime_outputs. Replace set key collection with dict.fromkeys in first-appearance order; existing public pipeline version1.13.0 unchanged, implementation1.16.0 ->1.16.1. This is a disclosed preparatory serialization-order correction, not a performance claim. Original44runs/2repeatFAIL remain intact. Original versus repaired22case comparison:0unexpected typed/value/Decimal/string/array differences. Repaired-before104cold runs and all22native collections completed before O1. RED4determinism failures/3preservation passes; GREEN full303tests. Both exact-source References synchronized and verified. Temporary key collection stays O(K); no persistent cache/state. Final status: RETAINED under the user's delegated proposal choice.

## O1: Carried-Order scratch allocation

Owner: engine/pipeline/order_audit_engine.py, _carried_orders_for_parent. Internal version1.8.1 ->1.8.2, actual Source timestamp2026-11-02T11:23:50+03:30. Reuse eagerly extracted parent list, call min only for multiple parents, release that scratch history before eagerly appending all B confirmations. Native minimum/tie identity, strict lifecycle bounds, inclusive confirmation/stop, error precedence, ledger iteration/stable sort order, cache keys/invalidation and returned tuple/Decimal fields remain unchanged. No trading rule, public envelope metadata or input filter changes. No new retained cache/index; broad scan/sort asymptotics unchanged, temporary reference lifetime changes from roughly p+1+b to max(p,1+b) on the measured CPython path.

Characterization tests pin both directions, earliest-parent/all-B semantics, strict/equal boundaries, literal Decimal text, shared Order identity, insertion ties, cache freshness and partial/malformed native rows. The artificial dense-provenance allocation test RED1fail/26pass (baseline peak171032B), GREEN full330PASS. Isolated child probing also works with a pre-existing parent tracemalloc session. Measured focused scratch peak 171032 -> 85720B (-49.88%). This artificial row is not asserted market-reachable; full process RSS does not halve.

Full final22scenario104cold matrix, ordered/typed comparison, raw lexical comparison and all native hook snapshots:0differences versus repaired-before. Current tests/anchors/reference/Anti-Drift PASS; real timings and actual memory variability are in11_PERFORMANCE_AND_MEMORY_RESULTS.csv, with matched controls/methods in11_PERFORMANCE_METHODS.md. Final status: RETAINED; exact rationale in discovery/retention-decision.json. Independent review found no supported production regression; all identified harness/test gaps were fixed and reread.

| Scenario | BEFORE wall s | AFTER wall s | Wall delta | BEFORE/AFTER CPU s (delta) | BEFORE/AFTER peak MiB (delta) | Repetitions each |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| xau-oct26-30s-bullish | 9.876267 | 9.824490 | -0.52% | 9.484375 / 9.296875 (-1.98%) | 174.238 / 174.156 (-0.05%) | 5 |
| xau-oct26-30s-bearish | 6.482395 | 6.003732 | -7.38% | 6.265625 / 5.765625 (-7.98%) | 152.152 / 151.961 (-0.13%) | 5 |
| usoil-oct22-5s-bearish-legacy-no-primary | 3.483498 | 3.576881 | +2.68% | 3.328125 / 3.250000 (-2.35%) | 70.266 / 70.484 (+0.31%) | 5 |

## Scope and discarded proposals

Exact patches from original Source are under source-diffs/. Only the two owning production modules, both required exact-source References and two new tests changed. No pre-existing user change, original RAW, expected result, historical artifact, global environment, dependency manifest, Git index/HEAD or remote was altered. Live checkout is explicitly user-selected. No worktree/commit/publication/Graphify action was inferred from skill defaults.

Naive metadata-first eligibility was rejected because it hides malformed eager extraction errors. New mutable creation/liveness indexes, shared E tables across regimes and Blue containment indexing were deferred pending stronger lifetime/chronology/identity/invalidation proofs. No unmeasured candidate is retained merely for fewer lines. Public versions and canonical Vault trading semantics remain unchanged; pre-existing Source/Reference/Vault semantic conflicts remain separate.
