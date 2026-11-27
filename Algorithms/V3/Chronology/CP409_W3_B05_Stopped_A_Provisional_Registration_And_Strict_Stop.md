# CP409 — W3 B05-26: Stopped-A provisional audit registration and strict stop

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 2622–2714, OA78–OA82. Entry algorithm `608eaf53e2e3825060b781b456a2bb367c39a2f3`, tree `6af7f2c1026521dba93fd663519f72766f449287`. Source-only local review.

## Independent procedure contracts

### OA78-A — lines 2622–2628

Signature and docstring describe attachment of a stopped-A cause; annotations do not validate. No transactional wrapper.

### OA78-B — lines 2629–2630

Required zone.source_time read precedes exact three-item match unpacking. Missing attribute or wrong iterable arity raises before ledger lookup. Retain supplied values and reaction reference.

### OA78-C — lines 2631–2635

Eagerly call _order_stop(number, object), unpack exactly three returned values before identity or ledger lookup, even for existing identity or duplicate cause. Provider failure prevents lookup/dedup.

### OA78-D — lines 2636–2638

Compute physical identity from int First and Break; construct exact A source/event tuple; get ledger row by pair. No direction, ordinal, price or time component in key; no rounding.

### OA78-E — lines 2639–2651

Only None from get creates and publishes nine fields: reaction_number, reaction, confirmation_time, stop_level, stop_source_index, stop_source_time, a_source_time, a_stop_event_time, a_causes. Retain original reaction reference, supplied confirmation and stop triple. Fresh list. No stop_cross or confirmation-index insertion. Existing non-None row preserves initial geometry and selected cause fields even if new geometry differs.

### OA78-F — lines 2652–2654

setdefault returns existing a_causes by alias or inserts fresh list if missing. Does not repair present None/wrong type. Full tuple equality membership; append unique pair in call order, no sort/copy. Failure after publication or setdefault leaves prior mutation; no catch/rollback. Implicit None.

### OA79-A — lines 2657–2660

Normalize required A price before owner A confirmation; call _first_a_stop with normalized price and confirmation. Owner validates one-based trend reaction number; lower strict crossing may occur at effective start; owner main fallback only on empty lower slice outside indexed branch.

### OA79-B — lines 2661–2663

Only None means no A stop; return immediately. Else unpack exactly three components, discard first two and retain exact third event timestamp.

### OA79-C — lines 2664–2667

Call _first_order_after with exact A stop event; None returns immediately, else forward zone, same event and match to OA78. No independent Order stop-crossing or S eligibility gate here. Implicit None; prior provider/cache effects not rolled back.

### OA80-A — lines 2670–2679

Return chronology.canonical_order_stop(order_direction, order_number, reaction, opposite_reactions, start_index=self.start_index) unchanged. Four positional and exact named start_index; no cache, conversion, fallback, validation or catch. Provider owns Mode A extreme or previous Mode B edge.

### OA81-A — lines 2682–2685

Exact bearish selects required high and strict > level; every other value selects required low and strict < level. Normalize selected candle extreme only; supplied level unchanged. Equality not crossing for ordinary comparable finite prices. No local direction validation, fallback or catch.

### OA82-A — lines 2688–2694

Effective scan_start=max(confirmation,range_start); evaluate bisect_left(lower_times,scan_start), then bisect_left(lower_times,range_end). Sorted comparable aligned timestamps precondition. Half-open positions [left,right) include exact start, exclude range end; confirmation equality not excluded here. No main fallback.

### OA82-B — lines 2695–2700

Evaluate right>left first; then lower_index is not None, including falsey non-null objects. Exact bearish first_greater(left,right,level), otherwise first_less, with level unchanged. Earliest position conditional on valid aligned index.

### OA82-C — lines 2701–2705

Indexed None immediately returns None; no scan retry. Otherwise use lower_times[position], map exact event via owner _main_index, read candles[index].timestamp. Return (index, main candle timestamp, exact lower event). No local bounds check, recheck, clamping or strictly-after confirmation guard.

### OA82-D — lines 2707–2712

Outside indexed branch iterate self.lower[left:right] in supplied slice order; call OA81 per item; read timestamp only for first true result, map owner main index, read candle timestamp and return triple. Exhaustion including empty/reversed slice returns None. Scan timestamp from item, not lower_times; no sort, main fallback, cache or rollback. Invalid attributes, comparisons, slice/index and provider exceptions propagate.

## Provider and consumer boundary

- **engine/pipeline/core_utils.py** (`38a1053510c5fb114e1b4290de00a2d3b27fc373`, lines 51–66): as_decimal preserves Decimal object or Decimal(str(value)); reaction_identity int-normalizes required first_idx then break_idx. Neither validates geometry chronology or prices.
- **engine/pipeline/s_zone_detector.py** (`53460e68538ac790ab969084c1c7101e5ca833d7`, lines 78–119, 178–251, 962–988, 1251–1299, 1340–1385): S validates direction; order_direction opposite; chronology-owned sequences, range and index, empty audit. A confirmation one-based valid reaction, default intrabar chronology. _first_a_stop indexed strict crossing with no retry on miss, lower scan in order, and main-candle fallback only when lower slice empty. _detect clears audit and audits all sorted A before S ownership and next-A gates. Main fallback consumer calls OA81 independently; reconciliation normalizes level, uses valid cached stop_cross or OA82, then rejects None or confirmation >= exact crossing event; sorts by exact event, confirmation, First, Break. OA82 itself includes equality in time.
- **engine/pipeline/reaction_engine.py** (`9adffb832ffa231ba0cb01de507a30fbe62be0b0`, lines 893–916, 959–963, 1028–1069, 1095–1108, 1153–1192, 1257–1302, 1305–1367): Lower index normalizes leaf prices, first_less excludes >= and first_greater excludes <=, left-first traversal and reverse deferred right nodes; reflected view negates level and reverses comparator. Chronology keeps sequence/time/index references; main_index bisect_right minus one, pre-first raises unless clamp. Confirmation exact lower strict break crossing, validated intrabar start or break start fallback. Canonical stop Mode A scans from bounded anchor/context through Break inclusive, strict better preserves first tie; non-A requires number >1, previous native edge source index/time, number zero can fail. Wrapper does not certify external implementations.
- **engine/pipeline/lifecycle_engine.py** (`2885dcbd3af108baadde7510ffd7968ad735c57e`, lines 606–658): resolve_order_context filters provisional identity-keyed entries through accepted_audit_entry with accepted sources before removing accepted First times from provisional block; not general public acceptance.
- **engine/bridge/trading_pipeline.py** (`e1e65ba960c5f726f9a05e2ab89e4457b65e5735`, lines 1792–1811, 2274–2306, 2408–2425, 3040–3098): MarketIndexWindow clamps local positions then translates base result; Bridge filters eligible A source set before E creation, later supplies accepted source/invalid identities to Lifecycle, and collects full calculation accepted A sources before presentation filtering and prepare_order_audit; public required identities separate. Dynamic live and callback contracts conditional.
- **engine/pipeline/order_audit_engine.py** (`6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 2300–2329, 2442–2461, 2462–2505, 2517–2714): OA76/77 select independent/native match; OA78/79 register provisional geometry and cause only. accepted_audit_entry filters by source and retains identity geometry, first accepted cause and complete accepted list; may return original or shallow copy. _collect_s_ledger_entries uses nonempty causes or legacy pair, filters when requested and emits parent-stop A causes. prepare_order_audit merges and resolves parent ownership. No new cross-owner acceptance.

## Exact inventory and prior evidence

| Category | CP409 | B05 total |
|---|---:|---:|
| branches | 11 | 551 |
| comparisons | 11 | 374 |
| arithmetic | 1 | 123 |
| calls | 28 | 844 |
| accesses | 196 | 5856 |
| effects | 11 | 371 |
| exits | 9 | 199 |
| Total | 267 | 8318 |

51 W1 and 216 additional, 7 historical supplements. All 8051 earlier category rows (1841 W1 and 6210 additional) and 152 supplements independently revalidated; exact disjoint union of 26 ranges, all 1892 CP316 links and 27 AST filter IDs reconciled. B05 scoped local closure only. W3 remains INCOMPLETE; W4 NOT RUN; Phase 08 BLOCKED.

## Limitations

- Separate source-first local review by GPT, not independently staffed; existing AST inventories compared, not regenerated.
- Local source-only coverage; no RAW, runtime, ZIP, new cross-owner acceptance or production change.
- Sorted/aligned timestamps, stable comparable values, valid indices and correct provider state are conditional; malformed/custom objects may fail or produce divergent behavior. No claim malformed inputs occur.
- Index miss does not retry and OA82 does not enforce strictly later event; S consumer enforces strict chronology separately. No empirical index/scan equivalence asserted.
- No independent SHA-256 assertion; Git object identities and readback are publication checks. Initial validator used wrong historical supplemental text field for CP384–386; corrected bounded retry matched all. A 26-partition link request exceeded per-call tool limit; two bounded retries matched all. Initial candidate generation stopped before writes because structuredClone was unavailable; replaced with JSON copy.
