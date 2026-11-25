# Phase 02 — Deep Static Analysis checkpoint

**Status: STRUCTURAL INVENTORY VERIFIED / DYNAMIC AND SEMANTIC CLOSURE PARTIAL.** Main baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`. No production modification.

| Gate | Result |
|---|---|
| Latest main identity, parse and compile | 16/16 PASS |
| AST declarations | 576 functions/methods, 85 classes; 127 lambda scopes; 364 comprehension scopes |
| Location inventory | 65,842 AST nodes with location/derived comprehension location |
| Decision/control-event inventory | 3,133 sites, 6,608 outcome labels |
| Explicit exits/transfers | 1,184 sites |
| Statement CFG | 677 graphs, 8,231 statements + 17 handlers, 18,552 edges |
| Compiled control flow | 902 code objects, 9,629 blocks, 15,367 edges, 712 exception regions |
| Call inventory | 5,120/5,120, candidate resolution partial |
| Data flow and mutation | Access, scope/group, conservative reaching-write and effect inventories complete for declared syntactic model |
| Dependency graph | Static imports, dynamic loader and type-only cycle reviewed; runtime closure partial |
| Dead-code screening | No unreachable nodes in declared abstractions; semantic feasibility NOT PROVEN |
| Independent inventory checks | 16/16 PASS |
| Deterministic repeat | 20/20 generated JSON reports byte-identical |

The deliverable is suitable as Phase 03 input and for traceability. It is not an exact full interprocedural semantics or proof of zero errors. 1,164 dynamic/inherited call sites remain unresolved by static candidate analysis; external/imported candidates also require runtime-context checking. No exhaustive alias analysis or exact exception feasibility is claimed. All runtime, full RAW, clean-room and equivalence gates remain future phases. An initial validator execution timed out due to repeated AST enumeration; the validator was corrected to compute the statement kind set once and both complete executions passed. No production source was changed.

Source code and executable analyzer scripts are intentionally excluded from the documentation branch and distribution package. Results record metadata and structural evidence only. See Methodology.md and Validation_Report.json for exact scope.
