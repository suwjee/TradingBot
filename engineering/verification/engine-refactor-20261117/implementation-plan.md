---
title: Engine feature removal and exact-equivalence performance plan
document_role: evidence
lifecycle: historical
owner: engine-refactor-20261117
created_at: 2026-11-17T19:59:54+03:30
last_modified_at: 2026-11-18T09:56:32+03:30
---

# Engine feature removal and performance plan

The user authorizes removing automatic T/F assessments and trading-position annotations, manual Long/Short positions, and Manual Review True/False selections. Native physical Order/OrderAudit, Reaction, Reset, Blue, A, S, E, StopAll and primary structures remain calculation contracts. Ordinary program booleans remain necessary.

The implementation is performed in the requested live checkout. Initial Git status was clean. No staging, commit, publication, RAW modification or Graphify execution is authorized.

## Approach

Keep two independently reviewable changes: feature removal and implementation-only optimization. Broad historical rollback would discard subsequent live continuation fixes; rewriting every module without measured benefit would add regression risk. Remove the owning feature stage and consumers, then optimize measured repeated work in the existing stage owners.

## Execution and verification

- [x] Discover live production closure and current engineering instructions; capture original Source and immutable RAW copies under ignored local scratch.
- [x] Run original Engine unit suite: 426 passed. Capture exploratory profile; profile duration is not benchmark evidence.
- [x] Remove feature owner, bridge/live hooks, Chart consumers/manual tools and review choices; replace retired feature tests with removal contracts.
- [x] Capture the post-removal, pre-optimization Source baseline separately.
- [x] Optimize measured range queries, repeated immutable indexes and accepted-state lookups in small steps. Preserve exact prices/Decimal strings, event chronology, tie ownership, ordering, identity, provenance, lifecycle and public output.
- [x] Compare original versus removed output allowing only the six removed annotation fields. Compare post-removal baseline versus optimized output with no stable exclusions except top-level timing telemetry. Use direct ordered JSON/text comparisons as well as hashes.
- [x] Run complete frozen RAW in both directions, representative timeframes, deterministic repeats, targeted boundaries and all relevant unit/integration checks. Capture upstream and downstream stage evidence for changed owners.
- [x] Measure paired fresh-process timings, representative median speed ratios and peak working set on identical inputs; distinguish total pipeline speed from individual stage speed and feature-removal savings.
- [x] Synchronize both reconstructable References, maintained architecture/testing/UI documentation and record Vault snapshot drift explicitly.
- [x] Review final diff and deliver exact results, scope and remaining limits. No universal correctness or unmeasured speed claim.

## Review focus

Equal Decimal values with different representations must retain the same winning source. Half-open lower windows and inclusive stop activation/end boundaries must not change. Duplicate source identities retain first-match behavior. Live append/revised provisional candles cannot reuse stale immutable indexes. Historical drawings and review data must remain readable without reactivating removed tools.

## Completion evidence

All plan steps completed for the stated preservation scope. See [the final report](FINAL_REPORT.md) for the measured full-file speedups, six-repeat bounded live results, the four unchanged disabled-behavior errors, exact output checks and unperformed independent market-correctness certification. No release or external Vault rebuild was performed.
