---
title: Engine complexity and candidate hotspot map
document_role: evidence
lifecycle: generated
owner: engine-zero-difference-audit
created_at: 2026-11-02T08:11:25+03:30
---

# Complexity map

This is static source analysis, not a measured speedup. Profiles will determine actual hot paths before any candidate is selected. Let R=lower RAW rows, M=main candles, Q=range/event queries, G=geometries, A/S/E=stage objects, O=accepted Orders/causes, P=active primary cycles and K=regimes. Worst-case bounds can be loose because chronology gates and existing caches constrain real activity.

| Stage | Current dominant work | Time / retained space hypothesis | Candidate and main equivalence risk |
| --- | --- | --- | --- |
| Bridge parse/normalization | Parse full RAW, typed price cache, construct lower/main Candle objects | O(R+M), O(R+M+unique prices) | Avoid repeated immutable conversion only with exact exponent/typed-cache behavior; preserve all supplied history |
| Chronology/index setup | Timestamp arrays, segment extrema/cross indexes | Usually O(R+M) to O(R log R) setup, index space | Avoid duplicate index construction only if all mutable/global scope contracts remain exact |
| Reaction/Reset | Sequential state transitions plus bounded geometry/range probes | Normal traversal linear plus query/search work; worst repeated nested probes can approach O(Q*M) | Existing lower indexes already accelerate many routes; never truncate successor chronology or resolve REF-REACTION-SUCCESSOR |
| Internal ownership | Reaction comparisons and lower containment indexes | Index-build plus lookup/output work | Existing segment-index reuse means old brute-force profile claims may be stale |
| Blue | Reaction strike windows, lower confirmation prefix, reset scans | Can scan full lower windows per query, O(Q*R) upper bound | Use exact first strict/event/extreme indexes with inclusive confirmation and earliest ties |
| A | `_range_extreme` allocates/scans inclusive lower window and maps winner to main; reset first-cross scans | O(Q*R) worst with O(window) temporaries | Existing LowerTimeframeIndex range extrema may replace work; preserve end+1us inclusive semantics, first equal source and no-lower fallback |
| S | Per-A stop/Order match/context/extreme scans; existing candidate/confirmation caches | O(A*(M+G)) broad upper bound, per-detector caches | `_candidate_before_order` initial main scan may be discarded when lower remainder exists; initial Order helper materializes full canonical suffix where sole consumer takes first |
| E | Parent stop/race/reconciliation/independent-root passes; sparse source-extreme index | Source index O(M log M), parent/candidate loops depend on E/O | Per-pass first-win parent maps; preserve mutation points, exact same-source selection, run/reset invalidation and accepted audit |
| OrderAudit | Per-reset opposite scans, geometry and canonical suffix query, full ledger scans | O(reset*G) and O(query*O) broad bounds; contexts/cache copies | First-only S canonical lookup can avoid suffix materialization; public all-match method remains contractual; native commits/reset lifetimes invalidate dependent caches |
| Lifecycle/StopAll | Chronological dominance, repeated parent/child/visibility/audit scans | Broad O((A+S+E+O)^2) possibilities | Indexed joins/sweeps need exact tie priority, source order, ownership and hard-prefix boundaries |
| Primary | Per-cycle proposals, range extrema, native ledger materialization and callbacks | O(P*(M+O)) broad probe bound plus proposal invalidation | Cannot retain prospective decisions after native commit or merge independent cycles; preserve final-role/horizon arbitration |
| Fresh regimes | Physically copy and recalculate prefixes/suffixes | Roughly sum over K full subruns; retained history can duplicate input/index objects | High potential cost, high correctness risk; state independence is a semantic requirement |
| Legacy serialization | Visit selected finalized objects, timestamps/Decimal text | Linear in emitted fields with timestamp caches | Avoid temporary rows for count-only work only if exception/side-effect behavior identical |
| Optional Bridge projection | For each behavior scan accepted causes; repeat physical Order formatting | O(behavior*O*causes), output allocation | Exact cause/family/ambiguity joins; never invent missing Order ownership or replacement events |

## Cache and memory observations

Existing module-level reaction/reflection/lower-index and Bridge timestamp caches can retain source sequences in a warm long-lived process, while the supported production request normally exits its Python child. Any lifetime optimization must be verified under both cold CLI and repeated in-process calls. E/OrderAudit contextual caches depend on ledger/primary mutations; a run-scoped cache with incomplete mutation context is still unsafe. No global or persistent cache is proposed.

The apparent Reaction `_first_geometry_after_reset` cache is dormant in the discovered runtime call closure; it must not be ranked as a real hotspot merely because its setter is absent. Existing indexes and older optimization work require current measurements, not repeated implementation of a historical proposal.

Detailed line anchors, candidate validity constraints and worst-case memory notes live in the per-owner reports under `reviews/`. `06_PROFILE_HOTSPOTS.md` will distinguish these static hypotheses from measured call counts, cumulative time and allocation evidence.
