# Phase 04 — Function-level reverse engineering (V3.0)

**Status: COMPLETE for named-function extraction and structural traceability. Semantic closure remains partial; not a certification of lossless reconstruction.**

Implementation authority: frozen main commit `466eb875070f02cd0dbfb105033422bbe2fd8c70`. This phase follows the [source-only scope](../Source_Only_Scope.md), [Phase 02 structural handoff](../Phase_02/Source_Only_Closure/README.md), and [Phase 03 foundational handoff](../Phase_03/Closure_02.md). No production code or RAW data was changed, no trading engine executed, no differential reconstruction or performance benchmark run.

## Deliverables

Each of the 576 named functions/methods (including nested named functions) has an individual source-derived English description. The table counts declarations, not runtime paths. The earlier checkpoint is retained unchanged.

| Owner | Named functions | Description |
|---|---:|---|
| Core utilities | 6 | [C01–C06](Checkpoint_01.md#f04-c--core-utilities) |
| Direction policy | 6 | [D01–D06](Checkpoint_01.md#f04-d--direction-primitives) |
| Final True/False | 7 | [TF01–TF07](Checkpoint_01.md#f04-tf--final-truefalse-annotations) |
| Live bridge | 13 | [L01–L13](Checkpoint_01.md#f04-l--live-bridge-transport) |
| Blue Line | 18 | [BL01–BL18](Blue_Line_Functions.md) |
| A Zone | 39 | [A01–A39](A_Zone_Functions.md) |
| Primary structures | 46 | [P01–P46](Primary_Structure_Functions.md) |
| S Zone | 50 | [S01–S50](S_Zone_Functions.md) |
| E Zone | 54 | [E01–E54](E_Zone_Functions.md) |
| Lifecycle and StopAll | 46 | [LC01–LC46](Lifecycle_Functions.md) |
| Order Audit | 82 | [OA01–OA82](Order_Audit_Functions.md) |
| Reaction Engine | 107 | [RE01–RE107](Reaction_Functions.md) |
| Trading Bridge | 102 | [TB01–TB102](Trading_Bridge_Functions.md) |
| Three package initialization files | 0 | [Module surfaces](Checkpoint_01.md#package-initialization-surfaces) |
| **Total** | **576** | **576 individual named descriptions** |

The descriptions record observed decisions, data ownership, input/output, state mutation, ordering and tie-breaking, boundary comparisons, fallbacks, and side effects where present. They distinguish native geometry, accepted behavior, Order provenance and public projection. Exact source ranges in the machine-readable traceability files supersede approximate prose end-line references in the historical checkpoint. Sixteen lifecycle end-line references were corrected after comparing to the AST inventory.

## Verification and traceability

[Validation.json](Validation.json) records 12 passing structural checks; the source blobs of all 16 modules matched Phase 02. Existing AST reports were fetched by immutable blob and joined to current source and named contract IDs. No new AST compilation or runtime coverage was claimed.

| Metric | Count |
|---|---:|
| Production source module identities | 16/16 |
| Named function declarations mapped | 576/576 |
| Class declarations linked to owners | 85/85 |
| All scope records linked | 1,168/1,168 |
| AST nodes in matched original inventories | 65,842 |
| Call sites | 5,120 |
| Decision/control sites | 3,133 |
| Effect sites | 2,045 |
| Explicit exits | 1,184 |
| Literal source-spelling records | 6,696 |
| Direct reference-binding sites | 449 |
| Arithmetic operator records | 1,074 |
| Comparison operator records | 2,177 |
| Previously reviewed call candidates linked to owning contracts | 1,528 |

- [Traceability 01](Traceability_01.json): package and bridges.
- [Traceability 02](Traceability_02.json): primary structures, pipeline package, A and Blue.
- [Traceability 03](Traceability_03.json): core, direction, E, lifecycle.
- [Traceability 04](Traceability_04.json): Order Audit, Reaction, S, T/F.
- [Call candidate crosswalk](Call_Candidate_Crosswalk.json): all 1,528 prior reviewed call records linked to a function or enclosing owner.

Each trace record gives the immutable AST scope ID, source range, parent, contract reference and original site totals. Exact individual node IDs remain in the Phase 02 module/Scope_Evidence files; the traceability groups also preserve literal source spellings, parameter/decorator metadata and arithmetic/comparison operators. Source spellings are not decoded runtime values (particularly formatted string fragments). The 85 classes and 16 modules have declaration/owner links; declared record fields are in the [Phase 03 catalog](../../Contracts/Declared_Record_Schemas.md). The 491 anonymous scopes are linked to their nearest enclosing named function, class or module, not individually certified as separate semantic contracts.

## Acceptance and handoff limitations

The completion decision applies to the named-function documentation and static traceability deliverables. It does **not** establish that each prose statement is independently correct or that every expression/branch, exception and dynamic receiver selection has been formally specified. The 596 name-only candidate rows (288 internal, 308 standard) remain conditional, not proven call edges; the 240 originally unclassified rows use the earlier source-only dynamic selection supplement. Their exact conditions and provenance must remain explicit during further semantic integration. External paths, callbacks, Python data model behavior and alias lifetimes must not be silently replaced by guessed behavior.

Full intra-expression evaluation and exact decoded literal semantics are not certified by structural counts. The remaining rule-level semantic completeness audit, cross-module dependency consistency, state machines, chronological and directional contracts, complete serialization, independent specification sufficiency and source-to-rule traceability are mandatory in the later phases. Keep the historical checkpoints intact; reconcile discrepancies in new documented revisions against pinned main. Phase 05 may consume these named-function descriptions as its input, but may not treat their existence or count as proof of algorithmic equivalence.

**Runtime / RAW / benchmarks: OUT OF SCOPE by explicit user instruction.** No claim of bit-for-bit output equivalence or executable reconstruction readiness is made. Main must remain untouched.
