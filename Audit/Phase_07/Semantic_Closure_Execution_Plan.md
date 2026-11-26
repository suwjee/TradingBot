# Phase 07 — Semantic Closure Execution Plan

Date: 2026-11-26. Frozen main: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Entry algorithm: `e1b352ae9641ae5b51322f56030159464cb78777`.

**Planning COMPLETE; Phase 07 INCOMPLETE; independent semantic audit NOT RUN; Phase 08 BLOCKED.** This plan does not certify an additional source expression. It supersedes proposed checkpoint numbering as a management schedule, not any recorded semantic evidence or acceptance requirement.

## Scope and authority

Follow [active source-only scope](../Source_Only_Scope.md) and [branch maintenance policy](../../AGENTS.md). Main is read-only; only algorithm documentation and structured evidence may change. No RAW data reads, trading execution, benchmark, candidate implementation, runtime feasibility or equivalence claim. Preserve actual behavior, exact Decimal semantics, strict/inclusive relations, Doji direction, event ordering, and source identities. Do not normalize source asymmetries into a presumed mirror. Use English and language-neutral algorithm descriptions.

## Entry evidence

Use [checkpoint 13](Semantic_Context_Review_13.md), [coverage validation](Semantic_Context_Coverage_Validation.json), [site crosswalk](Decision_Site_Crosswalk.md), [operand and integration evidence](Chronology_Integration.md), [Phase 05 contracts](../../Algorithms/V3/README.md), [Phase 06 state models](../../Algorithms/V3/State_Machines/README.md) and [chronology registry](../../Algorithms/V3/Chronology/README.md). Preserve all historical artifacts. 16 modules, 17,135 lines, 744 contexts, 576 procedures, 123 chronology clauses, and 491 guarded transitions are prior evidence, not independent semantic closure. The 11,504 category rows comprise 3,133 control, 2,177 comparison, 1,074 arithmetic and 5,120 call rows. Categories can overlap; they are not unique rules. Additional Boolean operands, conditional expressions, mutation sites, ordering keys, data-flow and implicit dependencies may lie outside these inventories. Track newly found items separately and never cap discovery at the existing denominator.

## Work package W1 — integrated owner review

Start with foundational primitives, then follow owner dependencies; defer live/visibility until pipeline orchestration is established. A batch can be split by complete procedure or source region, keeping stable IDs and cumulative progress. Numbers are inventory rows, not estimates of effort.

| Batch | Owner | Modules | Original category rows | Status |
|---|---|---:|---:|---|
| B01 | Shared primitives and initialization | 5 | 74 | NOT RUN |
| B02 | Reaction | 1 | 1,877 | NOT RUN |
| B03 | Blue and A | 2 | 1,145 | NOT RUN |
| B04 | S | 1 | 962 | NOT RUN |
| B05 | Order Audit | 1 | 1,892 | NOT RUN |
| B06 | E | 1 | 1,109 | NOT RUN |
| B07 | Lifecycle and StopAll | 1 | 1,179 | NOT RUN |
| B08 | Primary | 1 | 670 | NOT RUN |
| B09 | Trading Pipeline | 1 | 2,276 | NOT RUN |
| B10 | Live and True/False | 2 | 320 | NOT RUN |

For each batch: fetch exact pinned source and confirm its blob SHA; derive semantics from source before comparing prior prose; use original site coordinates/IDs, including lexical-negative rows; examine nested Boolean operands, chained comparisons (47 in prior inventory), short-circuit evaluation, return/exception/break/continue, sort and scan order, arithmetic, call side effects, aliasing, and conditional dispatch. Walk definitions and consumers for temporal values and implicit dependencies. Reconcile every relevant path and change of state against actual source and linked contracts. Preserve equality and missing-data distinctions, units, direction and fallback behavior. A grouping of sites is permitted only if each individual disposition has an explicit evidence link and the shared semantics actually apply.

Use sharded additive JSON ledgers rather than duplicating the large historical inventories. Record module path, pinned source blob, site category and original ID/coordinates (or supplemental ID and discovery reason), owner/procedure, semantic interpretation, temporal relevance and reason, ordered operand semantics, bounds and equality, dependency and state effect, conditional/fallback contract, source anchors, specification/transition links, disposition and verification evidence. Use explicit PENDING, PARTIAL, MISMATCH, VERIFIED, NOT_APPLICABLE, or SOURCE_CONDITIONAL dispositions. NOT_APPLICABLE requires reason; SOURCE_CONDITIONAL requires precise source-established contract and unknown input boundary, not a waiver. A context join, a lexical hit, a matching count or a bare status label is never verification. A source-conditional item may be accepted only after its documented contract is reviewed. Keep relevance and verification separate. Record findings with stable IDs, impact, source evidence, affected docs, resolution, and recheck. Correct active specifications and append correction history, never silently modify historical evidence.

## W2 — cross-owner reconciliation

Build the event/ownership and dependency register using source-derived edges, with distinct physical, lower and main indices, timestamps, decision/confirmation/stop horizons and visibility boundaries. Review Reaction/Reset, Blue/A freeze, A/S races, Order/S accepted revisions, E donor and family rules, Lifecycle/StopAll, Primary ties and activation, order feedback convergence and exception, native calls and callbacks, replay and segment projection, independent reversal, cache dirty frontier, open-candle handling and T/F repair. Cover conditional dispatch, implicit temporal dependencies, owner-local versus global sort keys, absence and same-position ties, cross-module mutation and invalidation. Document actual event priority, not a generic total order. Reconcile with all affected owner ledgers and active specifications.

## W3 — separate source-first forensic review

Perform a separate review pass over every owner and cross-owner dependency, starting from pinned source instead of reading the first pass's conclusions as authority. Compare resulting findings and reconcile discrepancies with source. Record reviewer/pass provenance and independence limits: a second pass by the same assistant is not an independently staffed audit. If a genuinely separate reviewer is available record that fact, otherwise do not claim it. No agreement alone establishes correctness. Unresolved source interpretations or unreviewed temporal sites block closure; runtime-input-dependent behavior is not itself a defect if its source contract is exact and reviewed.

## W4 — acceptance and publication

The machine-readable [execution register](Semantic_Closure_Plan.json) contains the initial batch partition and gate statuses. Progress is measured by reviewed/disposed original rows per category, independently reviewed supplemental items and resolved findings, not by file count or subjective percentages. Gates remain NOT RUN until evidence is produced. Require full accounted coverage, zero unreviewed temporal guards or unclassified dependencies, zero unresolved semantic defects, valid traceability and documented conditional boundaries, and structural readback of the actual published tree. Record scope, baseline, candidate, evidence, counts and status. Verify unchanged main, allowed branch content, no production changes, immutable history and links/metadata. Final closure is source-only specification closure; never runtime equivalence. Phase 08 remains blocked until the gates pass. No fixed maximum checkpoint count: split by evidence, not schedule.

## Resume protocol

At each work session: resolve main and algorithm heads; stop and reconcile baseline changes; read the latest progress and open findings; process the first unfinished batch; validate all new records and links and inspect the complete candidate tree; publish only to algorithm using the expected prior head, read back changes and confirm main unchanged. Update progress atomically with evidence where possible. Never turn an interrupted review into PASS. Begin with B01. If interrupted, retain the exact procedure/range, outstanding IDs, and next operation. No claim of background processing.

The current document is a management decision and entry plan, not a new semantic audit.
