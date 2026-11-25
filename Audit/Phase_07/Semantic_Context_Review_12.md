# Phase 07 — Semantic context review 12: Order Audit

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Entry algorithm: `93cbeb9318adf4c70a0138b97a1af5797cc8d438`. Source: `engine/pipeline/order_audit_engine.py`, blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`. Review: [ledger](Semantic_Context_Order_Audit.json), [cumulative progress](Semantic_Context_Progress_12.json). Source-only, no execution.

## Findings

- Dominant lifetime activation/stop boundaries are inclusive; exact object ownership at the stop precedes per-main ranking. Order_B selects a distinct latest pre-First anchor, which need not be dominant. Boundary improvement is strict, First must follow the extreme, lower crossing is strictly after Reset, opposite confirmation strictly after crossing; First may equal crossing main. A expiry compares main indices.
- Native stopped-A Order selection uses strict confirmation after stop and First at/after gate main. Independent geometry may map to a canonical identity or number zero; its (First, confirmation) must be strictly earlier to replace native. Canonical remap recomputes confirmation without another explicit gate check.
- Ordinary Order stop searches include exact confirmation time but exclude range end; price crossing remains strict. Primary parent stop starts strictly after decision. Carried creation interval is open, carried confirmation/crossing boundaries inclusive. Initial ledger carried First bounds are inclusive. Post-stop accepted crossing and confirmation both strictly follow parent stop; reset interval (stop,cross] blocks. These are distinct predicates, not interchangeable.
- Direct creation, reset-leg creation, carried-live and accepted-live use routes have separate ownership. Direct registration may retain an identity outside the candidate decision deadline. Exact parent cause winner uses earliest confirmation, First, Break. Geometry and valid historical causes survive rebuild; invalid S causes are removed, B causes independent. Primary replacement only matches the specified source and exact stop after decision.
- Native carried/post-stop indexes validate exact types, timezone identity and finite Decimal inside local context; fallback retains authoritative scan. Append/invalidation follows geometry versus earliest creation changes; reset gate evaluated at query time. Post-stop order key uses crossing, confirmation, later First; exact initial merge tie precedes audit. Live B reuse requires settled boundary or crossing before dirty and within available lower history.

## Validation

All 2714 source lines partitioned into 92 reviewed contexts. Original crosswalk IDs retained exactly: 551 branch sites, 374 comparisons, 123 arithmetic sites, 844 call sites. 81 distinct procedures with sites linked to existing contracts in Order A/B/Audit (declarations or procedures without inventoried sites are covered by the line partition). No correction to prior clauses required in this module. This is contextual review, not independent certification of each nested expression or runtime dispatch.

Cumulative: 15/16 modules, 631 contexts, 2581 branches, 1844 comparisons, 912 arithmetic, 3891 calls. Remaining: Trading Pipeline, 552 branches, 333 comparisons, 162 arithmetic, 1229 calls. Phase 07 remains incomplete; Phase 08 blocked.
