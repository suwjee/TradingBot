# Phase 07 — Checkpoint 65 / W1 B05-19

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `0277ecb9c244c1a18dee733da788031e61a99be6`. **Local review PASS; B05 INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** OA55, OA56, OA57, OA58, OA59, lines 1879–2019; 175 original rows, 8 supplemental items, 6 resolved local clarifications. Order Audit cumulative 1460/1892.

[Individual evidence](Semantic_Closure_B05_19.json) matches exact category IDs and AST spans in [immutable AST crosswalk](Decision_Site_Crosswalk_04.json) and [context ledger](Semantic_Context_Order_Audit.json). Pinned source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de` confirmed directly; no direct full Phase 02 inventory re-read claimed. Active contracts [Order Audit](../../Algorithms/V3/08_Order_Audit.md), [Order Ledger state model](../../Algorithms/V3/State_Machines/04_Order_Ledger.md).

## Verified local behavior

- Outer function executes eagerly before returning inner generator. Capture range_start.tzinfo; native_time exact datetime and timezone identity, native_match ordered checks after eager four-int tuple construction; exact Decimal finite and optional crossing exact tuple len>=3, int index and two native timestamps. Extra slots ignored. Non-native query immediately calls eager OA53 then iter.
- Initial None builds once; materialize OA45 outside try and before audit. Under local context eagerly convert all records and validate all, then stable sort only cross non-null and >confirmation. Map normalized identity to first (cross,confirmation) pair; differing pair rejects, equal allowed without geometry/price equality. Publish triple or False; False remains eager fallback. No local reset of initial view on audit invalidation.
- Audit refresh iff None or pending truthy, selects full index iff None otherwise pending. Exact indexed dates/ints and exact dict/price types, normalize price, require native match plus indexed confirmation equality; indexed First/Break are not checked against reaction identity. Catch Exception within build, not query-time merge.
- Null crossing requires known-null cache at (confirmation,level), no recompute; omit null or non-null cross<=confirmation. For qualifying cross compare initial identity event pair only, differing pair rejects. No audit-to-audit conflict check here. Full row key includes indexed First/Break after main key, not necessarily normalized reaction identity.
- New empty mapping or shallow copy prior mapping after validation; stable sort new rows by full key, tier=length.bit_length(), merge colliding tiers (not necessarily equal sizes) older first, fresh list, recompute tier; publish run and aligned crossing projection. Pending cleared in place after success/caught failure before publication; False with pending retries validation but False.copy fails if reached, falls back. Existing run lists not mutated by build.
- Capture first reset strictly after parent stop before returning generator, or None. Eligible generator upper-bounds crossing>stop, unwraps audit row if requested, breaks on cross>=captured reset, yields original entry only confirmation>stop. No separate crossing>confirmation check at consumption (build established it).
- Upon consumption create audit eligible generators in mapping order, merge full keys and project matches; merge initial first and audit second by main key; initial wins exact main-key ties, audit equal full keys use stream order. Fresh seen set, add identity before yield, first wins. No second eager rank arbitration or registration.
- Initial materialization errors outside catch propagate. Validation failures fall back eagerly; lazy generator errors after returned iterator not caught. Runs are treated immutable by build, not frozen objects; caller mutation and parity with eager path remain W2/W3, no runtime equivalence claim.

## Findings

- B05-19-F01: Specify outer eager/inner lazy boundary, nonnative fallback and ordered native validators. Active contract amended at line 117 and related clauses; rechecked against pinned source.
- B05-19-F02: Clarify initial materialization outside try, False sentinel and pair-only conflict. Active contract amended at line 117 and related clauses; rechecked against pinned source.
- B05-19-F03: Specify native audit guards, known-null proof and lack of index/reaction identity or audit-audit conflict check. Active contract amended at line 117 and related clauses; rechecked against pinned source.
- B05-19-F04: Clarify bit-length tiers, copy-on-build run publication and False/pending behavior. Active contract amended at line 117 and related clauses; rechecked against pinned source.
- B05-19-F05: Specify captured reset, original row yield and lazy merge tie precedence. Active contract amended at line 126 and related clauses; rechecked against pinned source.
- B05-19-F06: Clarify OLR08/09/10 distinction between lazy native strict confirmation gate and eager fallback, and scope of validation. Active contract amended at line 74 and related clauses; rechecked against pinned source.

## Open dependencies

- W2: indexed identity/actual reaction coherence, immutable initial records and published runs, pending append/rebuild/reset cache lifetimes, exact datetime/Decimal context, eager-vs-lazy tie and exception precedence, consumer iteration behavior. No assumption of runtime parity or proof that malformed inputs arise.
- W3 separate source-first forensic review pending. No RAW, runtime, differential or benchmark.

No RAW read, trading execution, benchmark, production change or main modification.
