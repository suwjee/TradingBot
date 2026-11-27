# CP411 — W3 B06-02: E live stop and extreme cache

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source `240369edf3352006082efe094eb68ac027d6689f`, lines 153–195, E04–E05. Entry algorithm `251c06c6d3e322c8e63efa46887c8e6dec713ffe`, tree `cad3aeb58f7e8e651c488358895e24769058c6c8`. Source-only local review.

## Independent procedure contracts

### E04-A — lines 153–157

Inputs detector, start datetime, Decimal level, keyword-only less and search callback returning nullable datetime; invoke E03 before key construction or map access. Annotations are not runtime conversion. Chronology object identity and non-null dirty required; returned dirty is unchanged.

### E04-B — lines 158–159

Construct key from less, original start, level in that order; no range end, detector direction, search identity, parent identity, feedback scope or Decimal string representation. Ordinary Decimal equality/hash is numeric, so equal finite values with different scales share a key; stored price object is not rounded. Ordinary dict lookup uses hash/equality and returns None on missing. Hash/comparison exceptions propagate.

### E04-C — lines 160–163

Only a None current result permits previous-map lookup. For non-null previous progress, invalidate when event is None or event >= dirty (including equality); short circuit avoids comparing None. Replacement is a new frozen record with scanned_until=min(old scanned_until,dirty) and event None; previous map unchanged. Previous non-null event strictly before dirty reuses the same record; current non-null entry bypasses dirty invalidation.

### E04-D — lines 164–167

If progress exists, store it into current map before evaluating its event or range boundary; insertion preserves encounter order for new keys, assignment to existing key does not move it under ordinary dict. Non-null retained event returns that same event only if strictly before detector.range_end; equality or later returns None immediately, retaining progress and never retrying. No lower-bound recheck or callback invocation on this branch.

### E04-E — lines 168–171

For retained null event, advance local search start to max(original start, scanned_until), not the key. Without progress use original start. If effective start >= detector.range_end return None, inclusive equality; no fresh progress record is created on empty interval, but prior promotion already remains. No coercion of start or range end.

### E04-F — lines 172–174

Invoke supplied search once with effective start, freshly read detector.range_end, original level, positional order; less is not passed because callback controls its own predicate. Save a newly constructed progress record: scanned_until is event if truthy, otherwise a further read of range_end; event stored exactly as returned, then return it unchanged. No range-end, start, chronology, strictness or type postcondition check on a fresh result. Falsey non-None custom result can diverge from later is-not-None read. Callback errors, truthiness errors or record/map-write errors propagate; earlier current-map promotion remains; no transaction/rollback. Callback may mutate dynamic receiver state.

### E05-A — lines 176–181

Inputs inclusive start/end main positions; validate E03 before any key/cache access. Key contains detector.direction, start_index, end_index (no candles identity, range, feedback scope or timestamp). Current lookup uses None sentinel. Current non-null value bypasses end-time guard, index construction and all query work; final assignment still occurs.

### E05-B — lines 182–184

On current None only, read detector.times[end_index] and compare strictly < dirty. If true, lookup previous map; equal/later cannot reuse. Previous hit returns same stored tuple reference, not copy, with no price/time/index revalidation; store in current map. Missing previous or false guard leaves result None. Negative indexing may be valid for guard while provider later rejects negative query bounds; no local type/bounds validation.

### E05-C — lines 185–188

On no reusable result, if shared continuation main index is None, import LowerTimeframeIndex locally, construct over detector.candles using provider default retain_crossings=False, then assign. One index shared for both directions and all calls within this advance generation; no per-call candles identity check, refresh, fallback or main_range_index reuse. Provider retains candles reference and materializes times/min/max/positions. E02 clears index on every advance. Import/build failure leaves index unassigned; later failure after build may leave it assigned.

### E05-D — lines 189–191

Select range_minimum only for direction equal to literal bullish; all other values choose range_maximum (valid detector construction normally limits direction to bullish/bearish). Call once on [start_index,end_index+1) so main endpoints inclusive. Provider rejects negative left, right beyond length, empty/reversed intervals; minimum Low or maximum High, earliest sequence position on numeric equality, preserves selected Decimal object. No local clamp, sorting, retry or sparse fallback. Query may fail or dynamically return wrong shape; unpack requires two values.

### E05-E — lines 192–195

Result constructed as integer conversion of detector.candles[position].index, detector.times[position], provider price in this evaluation order; physical candle code may differ from positional index. Timestamp taken from detector times, not provider copied times; correctness depends on aligned stable sequences. No local Decimal conversion or rounding. Store tuple in current map then return same object; current/previous hits return existing tuple. Attribute, index, int conversion, query or assignment errors propagate with no rollback, including retained main index.

## Provider and consumer boundary

- **engine/pipeline/e_zone_detector.py** (`240369edf3352006082efe094eb68ac027d6689f`, lines 128–151, 335–390, 416–435, 507–578, 581–606, 639–675): E02 rotates maps and always clears index; E03 validates identity. Parent stop clamps start to range_start, selects less iff detector bullish, supplies bound _search_parent_stop and maps non-null event to main index. Parent type is not a search-key component; parent decision_event_time and normalized price feed start/level. Order stop uses separate per-detector (start,level) membership cache including None; hit still validates E03; miss clamps start and supplies less iff order_direction != bearish. With normal opposite direction, both callback predicates are same trend direction; shared key is conditional on equivalent provider semantics. Both native callbacks bisect lower times at start/end, seek first strict crossing, return exact lower timestamp or None; indexed result (even None) is authoritative, no scan retry. Linear fallback normalizes selected low/high. _extreme_between maps both boundary instants to main positions, clamps to detector range and raises end to start if inverted; whole boundary candle OHLC included, no partial lower clipping. _zone consumes prospective source before ownership rejection. Optional continuation switches only when non-null; nonlive route separate.
- **engine/pipeline/reaction_engine.py** (`9adffb832ffa231ba0cb01de507a30fbe62be0b0`, lines 21–21, 893–939, 959–1017, 1019–1069, 1153–1178, 1185–1192): LowerTimeframeIndex constructor retains candles reference, copies timestamps, defaults crossing retention off, builds power-of-two segment tree for both extrema, normalizes lows/highs with imported as_decimal, stores sequence position separately. Parent aggregation chooses left on equality; range query compares numeric extremes then earliest position, including cross-segment ties. Range query rejects left<0, right>length, left>=right, absent valid result. No rounding of chosen value. First crossing clamps positions, excludes Low>=level or High<=level, descends earliest eligible segment, optional index-owned retained crossing history (not E cache). Chronology retains aligned main/lower sequences; main_index uses bisect_right-1 and lower clamp, not nearest time. E05 does not invoke refresh_suffix; provider index stability and exact alignment conditional.
- **engine/pipeline/core_utils.py** (`38a1053510c5fb114e1b4290de00a2d3b27fc373`, lines 51–53): Decimal helper returns existing Decimal unchanged, otherwise Decimal(str(value)). E04 level key uses numeric equality not string; E05 returns provider Decimal, not a local conversion.
- **engine/bridge/trading_pipeline.py** (`e1e65ba960c5f726f9a05e2ab89e4457b65e5735`, lines 2190–2208, 2280–2306, 3738–3767): Optional live continuation is forwarded only when present. Observed native live worker route calls prepare_pipeline_state without live argument, so do not equate live transport with active E04/E05 continuation. Dynamic callers must advance correct chronology and supply valid dirty evidence; no new cross-owner acceptance.
- **engine/bridge/live_pipeline.py** (`e1f1e7d3414a75ed073b67ff2ded3a5a481f6182`, lines 22–65): Live transport retains buckets and market views and invokes calculate_live_from_buckets. This does not establish direct E04/E05 dispatch.

## Inventory

| Category | CP411 | B06 total |
|---|---:|---:|
| branches | 14 | 334 |
| comparisons | 13 | 218 |
| arithmetic | 3 | 104 |
| calls | 14 | 453 |
| accesses | 153 | 3765 |
| effects | 10 | 270 |
| exits | 4 | 113 |
| Total | 211 | 5257 |

44 W1 and 167 additional; 3 supplements. CP410 352 rows and 3 supplements revalidated. All 1109 CP317 links and 18 filter IDs resolved. Cumulative 563 rows, 4694 remaining; 25 start-line partitions disjoint and complete. B05 exact 8318 union preserved. W3 INCOMPLETE, W4 NOT RUN, Phase08 BLOCKED.

## Limitations

- Separate source-first local review by GPT, not independently staffed. Existing AST inventories compared directly, not regenerated.
- Local source-only coverage; no RAW, runtime, ZIP, new cross-owner acceptance or production change.
- Correct dirty evidence, equivalent callback semantics for equal keys, stable candle/timestamp alignment, comparable finite Decimal prices and normal index bounds are conditional provider/caller requirements; malformed/custom inputs may diverge or raise, not asserted present.
- No independent SHA-256 assertion; Git object identities and readback are publication checks. Native live transport does not establish active E continuation; no empirical cache-versus-full-recompute equivalence claimed.
