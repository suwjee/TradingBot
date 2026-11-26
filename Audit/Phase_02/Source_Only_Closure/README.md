# Phase 02 — Source-only static analysis handoff (V3.0)

**Status: COMPLETE for the structural static inventory and documented conservative handoff; semantic function extraction remains open.** Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70` (latest main re-resolved at phase start). Previous algorithm checkpoint: `4ce52e8b2492b6ba1ba6e9f5c870e6711fa8a809`. Active scope: [source-only user instruction](../../Source_Only_Scope.md). This closes the source inventory and static-screening phase, not an assertion of complete interprocedural semantics or universally correct reconstruction.

## Scope and evidence

All 16 production Python/package source files were retrieved from the pinned main commit, and their Git blob identities matched the original module inventories. No market dataset, engine execution, test, benchmark, runtime coverage or independent executable implementation was used. The historical Phase 02 AST/CFG evidence is retained byte-for-byte; the present pass reuses that pinned inventory and adds source-located review rather than claiming to have independently rerun the original CPython analyzer.

| Deliverable | Status / quantity |
|---|---|
| Source identities and module coverage | 16/16 matched |
| Function/method and class inventory | 576 / 85 |
| All scope records, including modules, lambdas and comprehensions | 1,168 |
| Located AST nodes (original evidence) | 65,842 |
| Decision/control site inventory and labels (original evidence) | 3,133 / 6,608 |
| Call inventory and scope attachment | 5,120 / 5,120 |
| Prior detailed dynamic/imported candidate review | 1,528 |
| Previously unclassified call sites given selection/dispatch descriptions | 240 / 240 |
| Source-located literal inventory (lexical metadata) | 6,696 |
| Direct reference binding sites identified by restricted exact assignment check | 449 |
| Effect records linked to same-statement read/write sites | 2,045 |
| Explicit object mutation / deletion sites (original evidence) | 688 / 4 |
| Reaching-write read sites / candidate relations (original evidence) | 12,743 / 22,617 |
| Explicit transfer/exit sites / exception handlers | 1,184 / 17 |
| Conservative statement-graph possible exception/raise edges | 8,193 |
| Statement and compiled CFGs | Original verified graphs retained |
| Structural unreachable nodes | Zero in the original graph abstractions; not semantic feasibility |

## Dynamic call selection

The [previous supplement](../Closure_01/README.md) identified 240 UNCLASSIFIED_DYNAMIC sites. Each of those sites now has a source-derived selection or binding description, named nominal targets when known, candidate inventory IDs when matched, and prior effect flags. Classifications are:

| Selection type | Sites |
|---|---:|
| Native/library protocol | 91 |
| Supplied callable or stored callback | 71 |
| Lexical binding | 10 |
| Configured module member | 44 |
| Runtime type construction | 1 |
| Conditional callable selection | 22 |
| Classmethod constructor | 1 |
| Total | 240 |

Zero of the original 240 sites is left without a selection category. This does **not** mean zero unresolved runtime calls. Nominal target labels describe candidate roles; a label can identify the enclosing declaration for a lambda or wrapper, and is not an exact edge. Candidate IDs are name/owner matches, not proof of alias dispatch or a complete possible-target set. The other 1,288 prior review rows retain their original evidence and limitations (including 596 internal/standard name-only rows and 364 imported candidates). They are mandatory traceability inputs for per-function extraction, not silently upgraded to exact bindings. External engine paths, optional callbacks, subclass behavior, closure bindings and mutable state can remain conditional.

## New files

- [Dynamic selection review](Dynamic_Selection_Review.json)
- [Scope evidence 01 — package and bridges](Scope_Evidence_01.json)
- [Scope evidence 02 — primary, package, A and Blue](Scope_Evidence_02.json)
- [Scope evidence 03 — utilities, direction, E and lifecycle](Scope_Evidence_03.json)
- [Scope evidence 04 — order audit, reaction, S and T/F](Scope_Evidence_04.json)
- [Ownership, evaluation order and exceptions](Static_Ownership_and_Evaluation.md)
- [Validation and limitations](Validation.json)

Each scope evidence file links its module to the immutable earlier module inventory blob. Node indices are local to that inventory. All 5,120 calls, 2,045 effects, 3,133 branch sites and 1,184 explicit exits are partitioned by enclosing scope. Literal values are lexical metadata, not evaluated values: numeric spellings and Boolean/null/ellipsis tokens are retained; other constants carry lexical span length only. In particular joined-string AST locations can encompass wider spans; the catalog is not an exact decoded string-value inventory. Unary sign is an operator outside the constant node. Simple alias rows require a single-line assignment and matching AST store/load entries, excluding Boolean/null tokens. They are local binding evidence, not transitive points-to results. Same-statement links are candidate data dependence, not an exact use-def proof.

## Phase boundary and handoff

Phase 03 shall re-resolve main. Extract complete numerical, time, identity and data contracts from current source. Phase 04 shall independently read every function and class against the inventory, including name-only and configured candidates, dynamic callback conditions, exact intra-expression evaluation, all literal values relevant to behavior, and state ownership. Phases 05–11 complete algorithm, state machine, chronology, directional and integration semantics and bidirectional source-to-specification traceability. No claim of full algorithm coverage or zero errors may be made at this phase.

Exact path feasibility, transitive heap aliasing, exact all-input dispatch, and semantic dead-code proof are not established. These are recorded limits of conservative static analysis; preserve every source-visible rule and conditional dependency in subsequent semantic extraction. Do not delete any code on the basis of this screening. Runtime verification is out of scope. Source and historical evidence remain unchanged.
