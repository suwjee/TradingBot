# Source-only algorithm specification acceptance gates

Active user scope: 2026-11-26. See [scope decision](../Audit/Source_Only_Scope.md).

| Gate | Status at scope change |
|---|---|
| Pin latest main and identify relevant production modules | PASS at pinned baseline |
| Complete structural source inventory | PASS in recorded scope |
| Complete source-derived function and branch semantics | INCOMPLETE |
| Complete model, state, ownership and serialization contracts | INCOMPLETE |
| Self-contained language-neutral pseudocode and decision rules | INCOMPLETE |
| Both directions, equality, time windows, event ordering and numerical precision documented from source | INCOMPLETE |
| Source-to-spec traceability and documented dynamic conditions | INCOMPLETE |
| Internal documentation consistency and publication integrity | Required for each publication |
| RAW tests, runtime branch coverage, executable candidate, differential regression and benchmarking | OUT OF SCOPE |

Static extraction must not silently assert a dynamic receiver, alias, feasible path or external behavior that source does not establish. Record conditions and unknowns explicitly. A complete source specification is not a proof of runtime equivalence. Historical acceptance reports retain their original status.
