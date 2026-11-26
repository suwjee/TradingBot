# Phase 07 — Checkpoint 48 / W1 B05-02

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `4c89229367259b8fb3bb805c854bd1a373c329f7`. **Local review PASS; B05 INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** OA06, lines 198–377; 100 original rows, 6 supplemental items, 4 resolved local clarifications. Order Audit cumulative 246/1892.

[Individual evidence](Semantic_Closure_B05_02.json) matches exact category IDs and spans from [immutable AST crosswalk](Decision_Site_Crosswalk_04.json) and [context ledger](Semantic_Context_Order_Audit.json). Pinned source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de` verified directly. Active contracts [Order B](../../Algorithms/V3/07_Order_B.md) and [Order Ledger state model](../../Algorithms/V3/State_Machines/04_Order_Ledger.md); source-only, no direct full Phase 02 inventory re-read claimed.

## Verified local behavior

Independent post-stop and anchor selection; exact Reset owner, strict boundary extension, callback trust, main-timeframe expiry, physical selection and full provenance.

- Validate direction before empty input check; both callbacks selected by truthiness, not non-null identity. Default crossing excludes equal reset timestamps; injected crossing is not independently verified.
- Sort trend, opposite and Reset tuples with original ordinal tie-breaks; opposite number is one-based input ordinal; reset event resolved before constructing tuple; grouping and sorted arrays preserve duplicates.
- For equal latest earlier stop times, last sorted source time/index/type wins; for equal latest earlier anchor times, last sorted source index/priority/number/type wins. Only selected anchor tested for index compatibility; no retry.
- Boundary callback outputs used as-is; directional extension strict and source strictly before First; no local lower bound validation for source index. Crossing null skips, otherwise clamped main mapping; custom callback not checked for strict post-Reset crossing.
- A expiry uses first formation strictly after First main time, compares clamped main <= cross main before selecting opposite; opposite First >= cross main, exact confirmation strictly later. Selection order confirmation then First/Break/input ordinal.
- Each successful Reset appends one immutable full-provenance leg, even repeated physical identities; original reset traversal order preserved. Physical number from input, not sort rank. Boundary not re-normalized, Reset broken level normalized at construction.

## Findings

- B05-02-F01: Document truthy optional callback dispatch and trust boundary; only native crossing guarantees strict search after Reset. Active contract amended at line 38 to preserve source-established behavior.
- B05-02-F02: Make last-equal sorted stop/anchor selection and absence of alternate anchor retry explicit. Active contract amended at line 38 to preserve source-established behavior.
- B05-02-F03: Clarify that discovery retains duplicates and original opposite number; normalizes broken level, not callback geometry. Active contract amended at line 38 to preserve source-established behavior.
- B05-02-F04: Distinguish default strict crossing from supplied callback in state transition OB07. Active contract amended at line 50 to preserve source-established behavior.

## Open dependencies

- W2 verify chronology confirmation, reset mapping, callback geometry/time contracts and accepted A/physical inputs; no independent callback validation inferred.
- W3 separate source-first review pending; no runtime or RAW execution.

No RAW read, runtime execution, benchmark, production change or main modification.
