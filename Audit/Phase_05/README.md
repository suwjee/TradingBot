# Phase 05 — Module-Level Algorithm Extraction (V3.0)

**Status: COMPLETE for the module composition and structural traceability deliverables.** Final branch-level semantic verification is not certified.

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm head: `6926ba33f111cdbeb32136c70462953c77602992`. The source-only scope and frozen main decision remain binding. This phase consumes [Phase 04](../Phase_04/README.md) and its immutable source inventories. It converts the function-level descriptions to implementation-oriented module workflows, retains the detailed procedure contracts in the normative reading surface, and explicitly separates runtime import dependencies from calculation feedback.

## Published deliverables

The active [V3 module catalog](../../Algorithms/V3/README.md) contains 23 English module documents. The older Algorithms files remain historical. Each document has composed rules for its module boundary, data flow, arithmetic, selection, lifecycle interaction and failure behavior, where applicable. The detailed descriptions of all 576 named procedures are attached exactly once, with cross-cutting algorithms composing their owner procedures rather than duplicating them. Shared types reference the declared-record catalog. Source locations and Git identities belong to Audit, not the module algorithm bodies.

| Measure | Verified |
|---|---:|
| Module specifications | 23/23 |
| Composed algorithm sections | 89 |
| Named procedure definitions | 576/576 (unique) |
| Source modules | 16/16 |
| Class ownership mappings | 85/85 |
| Scope ownership mappings | 1,168/1,168 |
| Declared record classes linked | 46/46 |
| Distinct per-document internal link pairs | 91/91 |
| Structural checks in Validation.json | 12/12 passing |

The 23 documents contain 327,258 characters and 2,700 lines counted by newline splitting at the recorded blobs. These are documentation measures, not path coverage. The machine-readable [Module traceability](Module_Traceability.json) connects the exact original AST identity and location to the committed V3 procedure heading and document blob. All 491 anonymous scopes remain enclosing-owner links rather than independent semantic certification. Historical 5,120 call, 3,133 branch and other site inventories remain in Phase 02/04; do not mistake this mapping for a new site-by-site semantic proof.

## Dependency review

[Dependency graph](Dependency_Graph.json), [import evidence 01](Import_Evidence_01.json) and [import evidence 02](Import_Evidence_02.json) contain 29 unique internal static import-candidate edges across 16 source files. One static candidate SCC comprises E and Order Audit: Order Audit imports EZone only under TYPE_CHECKING (source lines 17–18), while E imports OrderAudit services at runtime. Excluding the type-only and local imports leaves no SCC in the resolved eager-import candidate graph. This is not proof for arbitrary dynamically configured engines.

The active module catalog documents five calculation feedback contracts: Order_B/E/Lifecycle (equality convergence, repeat error, cap eight passes); E/disowned-S native race reopening; Primary/OrderAudit commitment; independent trend-reversal regimes; and transactional Live input replay. These are not import cycles and do not share a single iteration limit. The active live worker replays the trading stages; it does not pass the optional retained trading-stage object into prepare_pipeline_state.

## Review findings and decisions

- Prior module-level documents were retained rather than overwritten; Algorithms/V3 is the new active reading surface. The detailed procedure clauses are composed from the Phase 04 extraction and rechecked against pinned source at module boundaries and critical decisions. They are not a fresh independent proof of each statement.
- In lifecycle procedure LC25 the internal cross-reference for invalid-A Order blocking was corrected from LC32 to LC33 in the V3 edition. In TB20, new index allocation was clarified as enabling crossing-history retention, not copying the previous index history. The Phase 04 historical files remain unchanged.
- Source-based distinctions explicitly reviewed include Blue spacing and invalid Reset Blue evidence, A trigger route precedence/expiry, S exact race and Type3/4 arbitration, S-side order-only number zero, E global physical Order race and source arbitration, StopAll promotion, primary cancellation/activation/reversal precedence, strict lower-event projection, RAW cache representation and active Live replay.
- The documentation scope does not replace the original source's native type/Decimal/protocol semantics. Conditional modules, callbacks, externally supplied input and aliasing remain conditional. No new trading rule was invented.
- The 23 module bodies have no hits in the recorded audit-reference lexical screen and no code fences. That screen is not a formal proof of absence of every possible copied expression; descriptions, formulas and interface identifiers are allowed. No executable source, runnable tests or RAW files were added.

## Evidence

[Catalog 01](Module_Catalog_01.json), [Catalog 02](Module_Catalog_02.json), [Catalog 03](Module_Catalog_03.json), [validation](Validation.json), [source-to-module mapping](Module_Traceability.json), and dependency evidence above. The 12 checks concern catalog identity, procedure uniqueness, original source declaration/scope matching, relative link targets, and lexical screens. Import SCC calculation is a separate static check.

## Handoff to Phase 06

The module composition deliverables are complete. Phase 06 shall produce formal state machines and lifecycle transition specifications, explicitly resolving state initialization, transitions, guards, cancellation/restart, ownership, invalidation, simultaneous events and continuation checkpoints from the pinned source. The detailed chronology, formal pseudocode and decision tables, directional semantics, integration and final rule-by-rule completeness audit remain later deliverables. Do not assert complete semantic equivalence merely from the 576/576 mapping.

No RAW market dataset was opened, no Engine calculation, runtime test, benchmark, backtest or independent executable reconstruction was performed. No production source was modified. All work remains in the documentation-only algorithm branch.
