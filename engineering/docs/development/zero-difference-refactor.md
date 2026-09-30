---
title: TradingBot Zero-Difference Refactor
document_role: procedure
lifecycle: maintained
owner: zero-difference-refactor
scope:
  - engine-refactor
  - performance
  - equivalence
  - deterministic-verification
last_modified_at: 2026-09-30T11:40:11+03:30
---

# TradingBot Zero-Difference Refactor

## 1. Purpose

This document is the maintained procedure for **behavior-preserving refactoring and performance optimization** in TradingBot.

It answers:

> How do we optimize or restructure implementation while proving that required observable behavior did not change?

The governing rule is:

`CURRENT STABLE BEHAVIOR == REFACTORED STABLE BEHAVIOR`

Correctness and equivalence come before performance.

Use root [`AGENTS.md`](../../../AGENTS.md) for authority, ownership, safety, and first-difference debugging; [Testing](testing.md) for general test discovery/status/RAW policy; [Algorithm Reference Maintenance](algorithm-reference-maintenance.md) when Source synchronization affects accepted References; and [Technical Architecture](../architecture/technical-architecture.md) for subsystem boundaries.

## 2. What qualifies as zero-difference work

A pure refactor or implementation-only optimization may change structure, data access, decomposition, caching, indexing, allocation, or internal implementation while intentionally changing **no stable observable trading behavior**.

If a task intentionally changes any trading rule, public contract, lifecycle result, identity, chronology, or serialization meaning, it is not pure zero-difference work. Reclassify the task and follow the behavioral-change workflow.

Do not hide a semantic change behind the word “refactor.”

## 3. Dynamic scope discovery

Before refactoring:

1. recursively inspect the current live project area and relevant Engine dependency closure;
2. identify production-owned Source dynamically from runtime loading, imports, package initialization, configuration, and ownership;
3. inspect relevant accepted References;
4. discover current tests/regression/RAW tooling through [Testing](testing.md);
5. identify public/runtime outputs and side effects affected by the changed path;
6. identify current architecture owner and upstream/downstream consumers.

Do not use a permanent module count, filename list, Source version list, hash list, or old benchmark snapshot as authority.

## 4. Baseline before production edits

Establish a reproducible baseline **before** implementation-only Source changes.

Choose baseline evidence appropriate to the affected risk. It may include:

- targeted contract/unit tests;
- direct stage/output snapshots;
- regression comparison artifacts;
- authoritative RAW-derived output;
- repeated deterministic runs;
- end-to-end serialized output;
- runtime/stage performance measurements;
- peak-memory measurements when relevant.

Record enough context to reproduce the comparison:

- input dataset/evidence;
- calculation scope and presentation scope;
- direction;
- timeframe/configuration;
- supported entry point/runner;
- relevant stable outputs;
- runtime mode/environment factors;
- completion status.

Do not define one universal baseline command. Discover current tooling.

A failed or incomplete baseline cannot support a claim of complete zero-difference verification.

## 5. Stable behavior that must be preserved

Preserve every applicable observable invariant, including:

- output values;
- Decimal-sensitive behavior and representations;
- strict/inclusive boundaries;
- chronology and event time;
- first/last/tie selection;
- source identity;
- physical/domain identity;
- provenance and cause relationships;
- ownership and parentage;
- event/object ordering;
- lifecycle and reset state;
- visibility/public state;
- stable serialization shape/content/order;
- deterministic behavior;
- direction-specific behavior;
- public API/CLI/output contracts where relevant.

Returning the same price from a different authoritative source event is not automatically equivalent.

## 6. Calculation history and RAW safety

Never optimize by deleting or clipping historical state that later calculation may need.

- calculation scope and presentation scope remain distinct;
- authoritative RAW is immutable;
- earlier history must remain available when current semantics require it;
- exact event ordering uses the finest authoritative chronology available;
- coarser OHLC cannot replace finer chronology merely for speed.

Use [Testing](testing.md) for dataset selection and RAW evidence rules.

## 7. Numerical and boundary safety

Preserve the current project-required numerical contract.

Do not introduce binary-float shortcuts into Decimal-sensitive trading decisions.

Do not alter equality behavior while simplifying comparisons.

For strict boundaries, equality remains non-triggering when current authority defines it that way.

Optimization may reduce repeated normalization or lookup only when the resulting values, winners, and chronology remain identical.

## 8. Directional safety

If changed code can affect directional behavior:

- identify direction-sensitive primitives;
- preserve direction-invariant semantics;
- verify both Bullish and Bearish paths;
- verify approved directional exceptions independently;
- do not treat mirror parity alone as independent correctness.

A one-direction-only verification is insufficient for shared directional Source unless the unaffected direction is demonstrably not reachable through the changed path.

## 9. Ownership-preserving refactor

Refactor the owner of the implementation concern.

Do not move trading policy into presentation, serialization, generic utilities, caches, or orchestration merely to reduce local complexity.

Before moving logic across modules/subsystems, verify:

- destination ownership is correct;
- dependencies improve or remain valid;
- no duplicate business rule is created;
- no circular/runtime-loading hazard is introduced;
- state scope does not become broader or more mutable;
- public/internal boundaries remain stable.

Architecture redesign is outside a normal zero-difference refactor unless explicitly authorized.

## 10. Optimization priority

Prefer this order:

1. remove unnecessary repeated work;
2. improve algorithmic/data-access patterns;
3. avoid repeated scans/sorts/parsing/conversion;
4. reuse safe immutable derived data;
5. introduce bounded run-scoped indexes/caches when justified;
6. reduce unnecessary allocation/object churn;
7. only then consider micro-optimizations.

Do not encode today's hotspot as permanent project truth. Measure current bottlenecks.

Do not knowingly write an obviously inefficient design with the intention of fixing it later.

## 11. Cache and index safety

Caches and indexes are acceleration structures, never authoritative trading state.

Before adding/changing one, prove:

- the underlying operation is deterministic for the cache context;
- every behavior-affecting input is represented in scope/keying;
- direction is included when relevant;
- dataset/run identity is included when local indexes may repeat;
- lifecycle/reconciliation mutation cannot silently stale the answer;
- invalidation/reset rules are explicit and complete;
- memory is bounded appropriately;
- authoritative state remains available.

Prefer run-scoped caches unless cross-run safety is formally established.

A stale fast result is a regression.

## 12. Memory and lifetime safety

Reduce memory only when state lifetime is proven complete.

Do not release or compact internal evidence that downstream stages, reconciliation, audit, visibility, or serialization may still require.

When adding indexes/caches/collections:

- estimate retained size;
- avoid duplicate full-object collections where references/indexes suffice;
- release large temporary structures after their true last consumer;
- measure peak memory when the change can materially affect it.

Never trade Decimal correctness or provenance for memory savings.

## 13. CPU and I/O hot-path discipline

For high-volume paths:

- avoid repeated full-history scans without necessity;
- avoid repeated sorting of the same logical data;
- avoid repeated parsing/normalization when safe reusable state exists;
- avoid file I/O and serialization inside per-item hot loops;
- avoid unbounded diagnostic logging;
- avoid hidden expensive helpers whose complexity is disproportionate to call frequency.

Use profiling or clear complexity evidence before claiming a bottleneck is performance-critical.

## 14. Concurrency

Do not introduce threading, multiprocessing, async parallel stage execution, or similar complexity merely to mask inefficient sequential logic.

Parallelism is acceptable only when:

- stage dependencies permit it;
- chronology/determinism are preserved;
- shared mutable state is safe or absent;
- output ordering remains stable;
- measured benefit justifies complexity;
- zero-difference verification passes.

Never parallelize algorithm stages whose sequential chronology is part of the trading contract.

## 15. Determinism gate

Repeat equivalent inputs when determinism matters.

Compare the stable content directly, including identity, chronology, provenance, ordering, lifecycle/public state, and serialized output.

Do not define correctness as hash equality alone. Hashes can prove stored byte identity but cannot explain semantic completeness.

Nondeterministic performance telemetry may be excluded only when clearly outside the stable output contract.

## 16. Exact comparison strategy

Compare at the earliest useful semantic layers, not only final JSON.

Depending on the change, compare:

- upstream unaffected stages;
- directly changed stage state;
- downstream dependent stages;
- Order/OrderAudit state;
- lifecycle/visibility;
- public/bridge projection;
- final serialization.

For each stable difference:

1. identify the earliest divergence;
2. determine whether it is nondeterministic telemetry, environment variance, baseline defect, refactor regression, or an actually intended semantic change;
3. reject unexplained differences.

In pure refactor work, downstream differences are not automatically acceptable because they follow an earlier difference.

## 17. Order, identity, provenance, and lifecycle

Changes touching data structures, indexes, reconciliation, S/E, lifecycle, Order, OrderAudit, or serialization require special attention to:

- canonical physical identity;
- source/confirmation/stop chronology;
- cause/provenance preservation;
- deduplication;
- accepted/live state;
- parent/ownership transitions;
- lifecycle reset boundaries;
- stable ordering.

Use the current canonical semantics for exact expectations. This document does not restate them.

## 18. Serialization boundary

Serialization remains a projection of finalized state.

A refactor must not move business decisions into serialization to make before/after output match.

If serialization changes structurally as part of a pure internal refactor, prove the public stable contract remains exactly equivalent or reclassify the task as a public-contract change.

## 19. Algorithm Reference impact

After an approved Source refactor, inspect the current accepted Reference structure.

If References embed Source, implementation details, manifests, symbol indexes, or reconstruction material, synchronize them through [Algorithm Reference Maintenance](algorithm-reference-maintenance.md) even when trading semantics did not change.

Record semantic behavior change as `NONE` only when that statement is actually true.

## 20. Performance measurement

Measure performance only after correctness/equivalence requirements are satisfied for the compared candidate.

Use comparable conditions:

- same relevant input;
- same calculation scope;
- same direction/timeframe/configuration;
- same runtime mode;
- comparable environment/load;
- repeated measurements when noise matters.

Report representative measurements, not only the best run.

Benchmark results are evidence. Do not place one measured number into this maintained procedure as permanent Current truth.

## 21. Performance acceptance

A speed improvement is valid only if required zero-difference checks still pass.

A faster implementation that changes one stable identity, event order, Decimal result, lifecycle state, provenance relation, or public output fails zero-difference.

A slower implementation may still be behaviorally equivalent, but it does not satisfy a performance-improvement objective unless the task accepts the tradeoff.

## 22. Failure handling

If optimized output differs from the baseline:

1. stop performance acceptance;
2. find the earliest meaningful difference;
3. classify the difference as:
   - intended semantic change;
   - refactor regression;
   - baseline defect;
   - nondeterminism;
   - environment/input mismatch;
4. correct or reclassify the work;
5. rebuild the baseline if and only if the baseline itself is proven invalid;
6. rerun required verification.

Never weaken equality criteria merely to accept a faster implementation.

## 23. Change sequencing

Prefer small, auditable refactor steps.

For each step:

1. identify the bottleneck/code smell;
2. state the behavior contract;
3. make the smallest ownership-correct structural change;
4. run targeted equality checks;
5. expand regression according to risk;
6. measure performance if the step is performance-motivated;
7. review the diff;
8. continue only from a verified state.

Do not combine unrelated cleanup, semantic fixes, and performance changes into one opaque refactor.

## 24. Testing and evidence

Use [Testing](testing.md) for:

- dynamic test discovery;
- standard result statuses;
- RAW immutability/chronology selection;
- browser/runtime classification;
- directional verification;
- evidence reporting.

For zero-difference work, strengthen that general procedure with the baseline and exact-equivalence requirements in this document.

Historical benchmark/regression artifacts may help choose scenarios but do not establish a current PASS.

## 25. Final verification gate

A pure refactor is verified only when every mandatory applicable category is `PASS`.

Typical categories include:

- Current Source/Reference understanding;
- ownership/dependency review;
- baseline capture;
- structural/runtime integrity;
- targeted exact comparison;
- upstream/downstream exact comparison;
- Order/OrderAudit integrity where relevant;
- serialization/public output;
- determinism;
- Bullish verification;
- Bearish verification;
- mirror/invariant checks;
- relevant historical regressions;
- representative/full RAW regression when risk requires;
- performance comparison for performance work;
- peak-memory comparison when material;
- maintainability review;
- final diff review.

Use `NOT APPLICABLE` only when irrelevance is demonstrated.

If a mandatory applicable category is `FAIL`, `NOT RUN`, or `INCOMPLETE`, report:

`ZERO-DIFFERENCE REFACTOR NOT VERIFIED`

Only after all mandatory applicable checks pass may report:

`ZERO-DIFFERENCE REFACTOR VERIFIED`

## 26. Reporting

For substantial zero-difference work report:

### Objective
The bottleneck or structural problem.

### Behavior contract
What must remain identical.

### Scope inspected
Current Source/References/tests/RAW/configuration actually inspected.

### Changed files
Owner and purpose of each change; semantic change must be explicitly stated.

### Equivalence result
Baseline versus candidate stable-output comparison.

### Performance result
Comparable runtime/stage measurements, number of runs, and representative result.

### Memory result
Comparable peak-memory result when applicable.

### Verification result
Each required category using the standard status model.

### Remaining limitations
Any unexecuted or incomplete evidence.

## 27. Acceptance scenarios

This procedure remains valid when:

- a faster implementation changes one Order identity — zero-difference fails;
- runtime improves and stable outputs remain identical — potential PASS after required verification;
- benchmark inputs differ — performance claim is invalid;
- a cache returns stale trading state — zero-difference fails;
- internal file organization changes with identical behavior — procedure still applies;
- Engine modules are reorganized — dynamic discovery finds the live scope;
- a benchmark helper is replaced — current tooling is rediscovered.

## 28. Review triggers

Review this document when the behavior-equivalence contract, baseline methodology, performance-comparison rules, cache/index safety model, deterministic verification requirements, or refactor-specific release gate changes materially.

Do not rewrite it merely because Source files, tests, versions, hashes, module counts, benchmark values, or internal layout change.
