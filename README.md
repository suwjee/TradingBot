# TradingBot — Standalone Algorithm Specification

**Documentation-only branch | English | SOURCE-ONLY REVERSE ENGINEERING IN PROGRESS**

This branch is an independent reading and distribution surface for algorithmic knowledge. Its current checked-out tree contains only Markdown specifications, language-neutral pseudocode, diagrams, structured metadata and verification evidence. It contains no production application or engine files, runnable test scripts, copied source appendices, build workflows, archives or RAW market datasets.

The implementation baseline is commit `466eb875070f02cd0dbfb105033422bbe2fd8c70`. The specification describes actual implemented behavior; intended trading-rule changes must be separately approved. The present specification is not certified sufficient for a full reconstruction.

## Reading order

| Section | Purpose |
|---|---|
| [Specification](Specification/README.md) | Architecture, invariants, time and numerical contracts, direction primitives |
| [Algorithms](Algorithms/README.md) | Reaction, Blue, A, S, Orders, E, Lifecycle, primary structures, bridge, serialization and T/F |
| [Directional](Directional/README.md) | Bullish and Bearish semantic maps and mirror rules |
| [Contracts](Contracts/README.md) | Input, output and inter-module interfaces |
| [Verification](Verification/README.md) | Static specification acceptance and historical test evidence |
| [Audit](Audit/README.md) | Baseline traceability, open gaps, coverage, historical measurements and publication evidence |

Read [the final audit](Audit/Final_Audit_Report.md) before using any algorithm for production reconstruction. The earlier measured checks and their limitations are preserved; reorganizing documents is not a new execution or proof of equivalence.

## Separation policy

Source code and runnable verification tools must live outside this branch's current tree. An independent implementer should receive only Specification, Algorithms, Directional, Contracts and the approved semantic test cases from Verification; exclude Audit and any historical Git references. The repository's earlier shared history is retained and is not a clean-room access boundary. For strict isolation, export the allowlisted documents without Git metadata and supply them to a separate implementation environment.

See [AGENTS.md](AGENTS.md) for maintenance rules.

## Formal specification V2.0 — Phase 01

[Phase 01: Source Discovery and Baseline Freeze](Audit/Phase_01/README.md) is COMPLETE for its defined discovery scope. The current implementation baseline is the latest main commit observed on 2026-11-26, `466eb875070f02cd0dbfb105033422bbe2fd8c70`. All 64 engine blobs are inventoried and hashed, with exact reference synchronization and verified RAW and historical Golden evidence. Re-resolve main before each subsequent phase. The specification itself remains PARTIALLY_VERIFIED; Phase 01 does not establish full semantic equivalence.

## V2.0 Phase 02 — Deep Static Analysis (historical checkpoint)

[Phase 02 analysis](Audit/Phase_02/README.md) is structurally verified against latest main at commit `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Complete AST inventories and conservative control/data-flow graphs are recorded; dynamic and semantic closure remains partial. Phase 03 must re-resolve main before using this evidence. See [static closure supplement](Audit/Phase_02/Closure_01/README.md).

## Active task scope

Per the user's 2026-11-26 instruction, continue source-only reverse engineering. No RAW tests, execution of production calculations, independent executable reconstruction, or benchmark are required for this task. The sole semantic authority is the current committed production source on main. Historical validation reports remain evidence of their original scope, not active completion gates. See [Source-only scope](Audit/Source_Only_Scope.md).

## V3.0 Phase 02 — Source-only static analysis handoff

[Current Phase 02 handoff](Audit/Phase_02/Source_Only_Closure/README.md) is COMPLETE for structural inventory and conservative static handoff under the source-only scope. Exact dispatch, alias lifetime, and path feasibility are not proven; function-level semantic extraction and full source-to-specification coverage remain open. All 16 source identities match main, 5,120 calls and 3,133 decision/control sites are indexed, and 240 previously unclassified calls have source-derived selection categories. No runtime or RAW tests were performed. Proceed to Phase 03 after re-resolving main.

## V3.0 Phase 03 — Fundamental computational contracts

[Phase 03 checkpoint 01](Audit/Phase_03/README.md) is IN PROGRESS. Numerical representation, chronology, candles and input aggregation, and shared search/cache primitives have been expanded directly from the pinned main source. Identity, full shared data and module-specific cache/visibility contracts remain open. No RAW tests or engine execution.

### V3.0 Phase 03 — checkpoint 02

[Current foundational handoff](Audit/Phase_03/Closure_02.md) is COMPLETE for shared primitive contracts and declared record interfaces (46 records, 438 fields). The checkpoint 01 report above remains historical. Module-specific function semantics, dynamic fields and full serialization remain open for later phases. User confirms main is frozen until further notice; do not modify it. Proceed to Phase 04 with the pinned main source and Phase 02/03 evidence. No RAW or engine execution.

## V3.0 Phase 04 — Function-level reverse engineering

[Checkpoint 01](Audit/Phase_04/Checkpoint_01.md) remains the historical initial extraction (32 of 576 named declarations). The [Phase 04 handoff](Audit/Phase_04/README.md) is COMPLETE for named-function extraction and structural traceability: all 576 named functions have individual source-derived descriptions, all 16 pinned source identities match, and all 85 classes, 1,168 scopes, 5,120 call sites and 3,133 decision/control sites are linked to the original inventories. [Validation](Audit/Phase_04/Validation.json) records 12 passing structural checks. Semantic closure remains partial; exact dynamic binding, intra-expression and rule-level completeness are not certified. No RAW tests, trading engine execution, benchmarks or production modifications. Phase 05 may consume this handoff without assuming reconstruction equivalence.


## V3.0 Phase 05 — Module-level algorithm extraction

[Phase 05 handoff](Audit/Phase_05/README.md) is COMPLETE for module composition and structural traceability. The active [V3 module specifications](Algorithms/V3/README.md) contain 23 English module documents, 89 composed rule sections and all 576 named procedures exactly once. All 16 source modules, 85 classes, 1,168 scopes and 91 distinct per-document relative links are mapped; [validation](Audit/Phase_05/Validation.json) records 12 passing structural checks. [Dependency review](Audit/Phase_05/Dependency_Graph.json) separates the guarded E/Order type-import cycle from native feedback/replay. The earlier Algorithms documents are retained as historical references. Semantic path equivalence and final reconstruction sufficiency are not certified. No RAW or Engine execution; main remains frozen. Proceed to Phase 06 formal state and lifecycle extraction.


## V3.0 Phase 06 — State Machine & Lifecycle

[Phase 06 handoff](Audit/Phase_06/README.md) is COMPLETE for guarded state-model and lifecycle documentation. The [active state-machine registry](Algorithms/V3/State_Machines/README.md) contains nine English specifications, 49 extended-state models and 491 guarded transitions. All 576 named procedure roles are accounted for (550 direct references, 26 supporting-only); all 16 source blob identities match the frozen main. [Validation](Audit/Phase_06/Validation.json) records 13 passing structural checks. These analytical tables are not an executable FSM or proof of every source decision path. Phase 07 shall extract chronology and exact event-ordering semantics. No RAW data reads, engine execution or production changes.


## V3.0 Phase 07 — checkpoint 01

[Phase 07 chronology](Audit/Phase_07/README.md) is INCOMPLETE for semantic closure. 45 owner-specific reviewed source clauses recorded; Phase 08 remains blocked. No RAW or production execution.

### Phase 07 checkpoint 02

[Source inventory](Audit/Phase_07/Source_Index_README.md) now accounts for all 16 source blobs and 576 named procedures; lexical candidates and prior AST operator evidence are not complete semantic closure. Phase 08 is still blocked.

### Phase 07 checkpoint 03

[Additional owner-specific chronology](Algorithms/V3/Chronology/06_Additional_Owner_Boundaries.md) expands the reviewed source clauses to 75. Phase 07 semantic closure remains INCOMPLETE; Phase 08 blocked.

### Phase 07 checkpoint 04

[Exact AST-site crosswalk](Audit/Phase_07/Decision_Site_Crosswalk.md) maps all inventoried branch/control, comparison, arithmetic and call sites. Structural coverage does not establish semantic closure; Phase 08 remains blocked.

### Phase 07 checkpoint 05

[Chronology integration](Audit/Phase_07/Chronology_Integration.md) expands reviewed clauses to 123 and joins all 576 named procedures to prior semantic contracts, with all 2,177 comparison operand partitions structurally validated. Phase 07 semantic closure remains incomplete; Phase 08 blocked.

### Phase 07 checkpoint 06

[Direct semantic context review](Audit/Phase_07/Semantic_Context_Review.md): 8/16 source files reviewed by explicit context, with remaining modules tracked separately. Phase 07 INCOMPLETE; Phase 08 blocked.

### Phase 07 checkpoint 07

[Direct A and Primary semantic context review](Audit/Phase_07/Semantic_Context_Review_07.md): 10/16 files reviewed with exact pinned source context. Six remain pending. Phase 07 INCOMPLETE; Phase 08 blocked.

### Phase 07 checkpoint 08

[S direct semantic context review](Audit/Phase_07/Semantic_Context_Review_08.md): 11/16 files, five pending direct review. Phase 07 INCOMPLETE; Phase 08 blocked.

### Phase 07 checkpoint 09

[E direct semantic context review](Audit/Phase_07/Semantic_Context_Review_09.md): 12/16 files, four pending direct review. Phase 07 INCOMPLETE; Phase 08 blocked.

### Phase 07 checkpoint 10

[Lifecycle and StopAll direct semantic context review](Audit/Phase_07/Semantic_Context_Review_10.md): 13/16 files, three pending. Phase 07 INCOMPLETE; Phase 08 blocked.

### Phase 07 checkpoint 11

[Reaction direct semantic context review](Audit/Phase_07/Semantic_Context_Review_11.md): 14/16 files, two pending. Phase 07 INCOMPLETE; Phase 08 blocked.

- Phase 07 checkpoint 12: [Order Audit direct review](Audit/Phase_07/Semantic_Context_Review_12.md); 15/16 modules reviewed, Trading Pipeline pending. No runtime claim.

### Phase 07 checkpoint 13

[All-module direct chronology/context review](Audit/Phase_07/Semantic_Context_Review_13.md) is COMPLETE for the 16 inventoried source modules and all original site mappings (744 contexts). [Coverage validation](Audit/Phase_07/Semantic_Context_Coverage_Validation.json) rechecks main blob identities and the full site inventory. The broader independent per-expression semantic gate is not certified by coverage; Phase 08 not started. No runtime/RAW execution or main changes.


### Phase 07 — semantic closure execution plan

[Execution plan](Audit/Phase_07/Semantic_Closure_Execution_Plan.md) and [execution register](Audit/Phase_07/Semantic_Closure_Plan.json) define the remaining evidence-driven work. Planning COMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED. No new independent semantic verification or runtime claim.


### Phase 07 — checkpoint 14

[W1 B01 shared primitives and initialization](Audit/Phase_07/Semantic_Closure_B01.md): local source-first review PASS (five modules, 74 original rows); remaining owner reviews, W2 and W3 open. Phase 07 INCOMPLETE; Phase 08 BLOCKED.


### Phase 07 — checkpoint 15

[W1 B02-01 Reaction local review](Audit/Phase_07/Semantic_Closure_B02_01.md): RE01–RE12, 171 original rows; sub-batch PASS, Reaction owner remains INCOMPLETE. Phase 07 INCOMPLETE; Phase 08 BLOCKED.


### Phase 07 — checkpoint 16

[W1 B02-02 local review](Audit/Phase_07/Semantic_Closure_B02_02.md): RE13–RE18, 179 original rows, one local specification correction; B02 remains INCOMPLETE. Phase 07 INCOMPLETE; Phase 08 BLOCKED.


### Phase 07 — checkpoint 17

[Reflected sequences, Bearish adapters and published geometry](Audit/Phase_07/Semantic_Closure_B02_03.md): 103 original rows, local PASS; B02 remains INCOMPLETE. Phase 07 INCOMPLETE; Phase 08 BLOCKED.


### Phase 07 — checkpoint 18

[Segment index, suffix refresh, strict crossing and cache lifecycle](Audit/Phase_07/Semantic_Closure_B02_04.md): 229 original rows, local PASS; B02 remains INCOMPLETE. Phase 07 INCOMPLETE; Phase 08 BLOCKED.


### Phase 07 — checkpoint 19

[MarketChronology, Reset and confirmation cache, canonical Order stop](Audit/Phase_07/Semantic_Closure_B02_05.md): 153 original rows, local PASS; B02 INCOMPLETE. Phase 07 INCOMPLETE; Phase 08 BLOCKED.


### Phase 07 — checkpoint 20

[Reaction span ownership and internal containment](Audit/Phase_07/Semantic_Closure_B02_06.md): 71 original rows, local PASS; B02 INCOMPLETE. Phase 07 INCOMPLETE; Phase 08 BLOCKED.
