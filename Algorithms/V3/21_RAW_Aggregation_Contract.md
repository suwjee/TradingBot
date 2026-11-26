# RAW aggregation — input normalization and market context (V3)

**Conventions:** B = bullish, R = bearish. Preserve Decimal representation, evaluation order, native failures, exact versus main-candle time, original array order and nulls. Record interfaces: [Declared schemas](../../Contracts/Declared_Record_Schemas.md). Operation IDs designate semantic procedures, not required implementation symbols. This contract does not claim runtime equivalence.


## RAW-M01 — Batch input and numeric preservation

Read complete bytes, remove UTF-8 BOM prefix, parse JSON using Decimal for floating numeric lexemes. Do not convert to binary float then string. Nonempty rows required; no sort or general OHLC validity check in batch aggregation. For each row in original order, integer-convert time and normalize Open,High,Low,Close with local cache keyed by exact value type and equality of value (first normalized representation retained, even if equal Decimal has different exponent). Already Decimal returned unchanged unless cache returns earlier equal representation. Other types use native string conversion. Do not invent missing slots or adjust OHLC. Raw timeframe argument controls closed-horizon semantics, not timestamp bucket expansion.

## RAW-M02 — Aggregation formula and order

Let t=int(raw time), TF positive calculation timeframe. Lower key=t; main key=t for TF=1 otherwise floor(t/TF)*TF using integer floor division. On first row of a key, store time,O,H,L,C. Consecutive same key: keep original Open, update High=max(previous,current), Low=min(previous,current), Close=current Close. Equal extrema retain first under native min/max. Lower and main aggregate in the same traversal. When lower_only true do not build separate main; TF1 view aliases lower. Discontiguous duplicate keys in unordered batch are not globally merged. No forced chronological sorting.

Build candle objects by enumerated positions, local timestamp from epoch with Asia/Tehran then strip timezone, display string year-month-day hour:minute:second; tag GREEN if Open<=Close else RED. Reuse prepared lower index if exact source identity. Full RAW is calculation context even when requested view ends earlier. Visible start bucket=floor(from/TF)*TF and end bucket=floor(to/TF)*TF (TF1 unchanged); first main at/after start, end=first at/after end+TF minus1, clamp last. Missing range -> ValueError. No calculation truncation.

## RAW-M03 — Append transaction

Live constructor requires exact int TF>=1; lower/main bucket arrays share identity TF1. Validate each row's time numeric integer, positive, nondecreasing; equal raw times allowed at aggregation level (transport lineage stricter). Empty append yields unchanged dirty lengths/delta. If first new raw time equals previous last, copy lower tail and rewind dirty lower to last. For nonshared main, copy last main if new first falls in same bucket; TF1 dirty main=dirty lower. Aggregate using local new-price keys with persistent cache first. Snapshot old suffixes/last time, commit new keys/suffixes/time before yielding delta. On BaseException from transaction body, restore both suffixes, previous time and delete newly added keys; propagate. Prior validation/aggregation does not mutate committed suffixes. Delta fields first_dirty_second/main and settled_seconds/main=max(0,len−1) exclusive; latest bucket provisional. No synthetic completion from raw gaps.

Live views retain immutable candle objects before dirty; rebuild suffix with same positional indexes. Reuse existing index only when length within capacity; update suffix; otherwise new index with crossing-history retention enabled (not copied old history). TF1 shares views and index. Fresh chronology wraps retained views; actual trading stage replay is [Live Bridge](18_Live_Bridge.md).

## RAW-M04 — Independent regime slice

Require 0<=start<stop<=main length. Select lower range by first main timestamp inclusive and stop main open exclusive, or last+TF. Copy/reindex selected main/lower from zero, fresh chronology same type and TF. Range start=max(0,old start−start), end=min(stop−start−1,old end−start); offset=old+start. Initial trend flags inherited only at start0 unless overridden. No price/time transform. Release indexes via owning caller. See [Reversal](15_Trend_Reversal.md).

## Detailed RAW procedures

### TB09 — _aggregate_candle_buckets
Start lower/main lists with optional existing tail dicts. Iterate rows in supplied order, convert time to int and OHLC with supplied decimal callback. Consecutive equal raw timestamp merges into lower bucket: original Open, max High, min Low, latest Close. Otherwise append new bucket. Unless lower_only, repeat aggregation at epoch-aligned floor time (timeframe 1 uses raw timestamp). Return lower and main buckets; modifies supplied tail dicts, does not sort or enforce chronology itself. The output lists contain supplied non-null tail dictionaries by reference, including the main tail even when lower_only is true. Lower-only bypasses main-key calculation after each lower update. Same-key extrema use previous value first in native min/max; no discontiguous-key merge, time validation or sort.

### TB10 — build_candle_buckets
Initialize per-call normalization cache, delegate TB09 with TB11 and lower_only flag.

### TB11 — cached_decimal
Key by (type,value); first normalized representation retained. On missing key normalize using as_decimal, store, return. Cache is local to TB10; invalid value propagates. The lookup alone is inside the try and only KeyError is caught. Miss conversion and insertion failures propagate; equality is by exact type/value key rather than Decimal lexeme. BucketAppend is a frozen slotted metadata record of two dirty indexes and two settled boundaries.

### TB12 — LiveMarketBuckets.__init__
Require timeframe of exact int type >=1. Lower buckets empty, main aliases lower at timeframe1, otherwise separate list. Last raw timestamp null and persistent price cache empty. Exact type excludes bool and int subclasses; invalid type short-circuits the positive test. TF1 main and lower are the same list object.

### TB13 — LiveMarketBuckets.append
Enter transactional stage_append context, return its yielded delta, exit context normally.

### TB14 — LiveMarketBuckets.stage_append
Initial dirty indices are current lengths. Empty rows yield delta without change. Otherwise int first timestamp, floor main bucket. If first timestamp equals last raw timestamp, dirty lower is last bucket and copy it as tail; similarly copy last main if same bucket, except timeframe1 shares lower. Aggregate checked rows using TB15 and TB16. Snapshot old suffixes and last time before replacing suffixes, inserting new price keys, updating last time. Yield TB17 delta. If BaseException during consumer body, restore old suffixes/time and delete newly inserted price keys, then rethrow. Pre-yield validation/aggregation uses copies and local price additions, no committed mutation. Do not silently accept decreasing RAW time. Initial dirty values are lengths; empty input yields without modifying state. First timestamp is int-converted before checked-row traversal. Tail copies are shallow and only selected on existing list plus equality of previous last raw time or aligned main key; nonshared main is checked separately. The rollback try begins after new cache keys, suffixes and last timestamp are published; it covers delta construction and the consumer's yield body, not earlier commit assignments. Restore lower suffix, nonshared main suffix, timestamp and delete newly inserted keys, then rethrow BaseException.

### TB15 — checked_rows
Generator converts time to int, requires equal original numeric value and >0, rejects decreasing time relative to previous including prior append. Updates captured previous timestamp and yields original row. Equal timestamps permitted. Original numeric equality after conversion is not an exact-type test: an integer-equivalent positive value can pass, subject to native conversion/equality; decreasing times fail, equal times pass. The original row is yielded only after updating the captured previous time.

### TB16 — cached_decimal
Consult persistent price cache by type/value then local additions. On miss normalize and add locally; return preserved first value. Persistent membership is checked first, including values equal under the typed key. Local cache additions remain private until aggregation succeeds; the checked iterator validates lazily during aggregation.

### TB17 — LiveMarketBuckets._delta
Construct BucketAppend with dirty lower/main indices and exclusive settled counts max(0,length-1), last bucket provisional. Settled lower and main counts are independent exclusive boundaries derived from actual list lengths; no estimate of missing RAW slots.

### TB18 — build_candle_objects
Enumerate bucket dicts from supplied start index; convert time to Tehran naive datetime and formatted display string; classify color with engine callback, construct engine.Candle with OHLC unchanged. Return list. Enumerate from caller-specified start index, retain bucket order; format six local wall-clock components and invoke the engine classifier with original Open/Close. OHLC objects are supplied without a further normalization step.

### TB19 — LiveMarketViews.__init__
Initialize lower/main candle arrays and indexes empty/null; create fresh LiveClosedRegimes cache.

### TB20 — LiveMarketViews._update_series
Rebuild mutable candle suffix from dirty if existing index else zero; replace suffix. If no index or new length exceeds capacity, construct a fresh LowerTimeframeIndex with crossing-history retention enabled; otherwise refresh_suffix in existing index. Return index. The retained candle list is changed before index construction or suffix refresh; there is no local rollback. Equal length to capacity reuses the index. An absent index forces rebuild from zero, even if caller supplies a later dirty boundary.

### TB21 — LiveMarketViews.update
Timed update of lower series; timeframe1 main and index alias lower, otherwise timed separate main update. Mutates object in place. Lower update is published first. TF1 aliases both candle and index objects; nonshared main is updated separately and may fail after the lower update.

## Legacy and projected serialization

### TB63 — market_segment
Require 0<=start<stop<=len(main). Slice main [start,stop), lower bounds bisect_left on first main time and exclusive stop main time (last+duration when full tail), so equality at stop excluded. If indexed_reaction is None or start is nonzero, copy/reindex main records; independently copy/reindex lower if indexed_reaction is None or lower left nonzero. With indexed_reaction non-null construct lower and main MarketIndexWindows over parent indexes, register via shared_lower_timeframe_index(seconds,prepared=lower) and same for main, in that order; pass both returned indexes to chronology constructor. Without indexed_reaction pass no indexes and reconstruct fresh chronology. Local visible start=max(0,old start-start), end=min(stop-start-1,old end-start); offset += start. Explicit non-null initial trend overrides independently, otherwise inherit only at start zero. No visible-overlap requirement. [Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1826-L1857).

### TB68 — prepare_market_context
Timed read input bytes; remove UTF-8 BOM prefix; parse JSON using Decimal parse_float; delegate rows to TB69. Read complete bytes, remove one leading UTF-8 BOM prefix only, and use native JSON parser with Decimal for floating lexemes; integer parsing remains native default. No pre-filter of requested timestamps or numeric conversion through binary float. Parse and file failures propagate.

### TB69 — _prepare_market_context_from_rows
Use full file rows for calculation; empty raises ValueError. Timed bucket normalization, lower_only at tf1. Delegate TB70, never slice raw to visible range. Full rows are returned unchanged by timed pass-through; only falsiness rejects empty input. Timeframe one selects lower_only, all other timeframes build both arrays. from/to do not truncate the calculation context, and this wrapper does not sort or repair rows.

### TB70 — _prepare_market_context_from_buckets
Batch: build lower candles, shared lower index, main candles or tf1 alias, chronology. Live: require delta, update views, register prepared lower/main indexes, chronology. Determine requested visible bucket epochs (floor for tf>1); bisect start and end+tf minus one. Empty range raises, end clamped to last. Return full context with visible bounds. Exact null live_views selects batch. Timeframe one aliases lower candles rather than rebuilding main. Live branch uses an assertion for non-null delta, updates views then registers lower and main prepared indexes in that order; chronology receives both. Exceptions are not transactionally caught here. Both visible boundaries use integer floor alignment except timeframe one unchanged. Bisect left on bucket time yields inclusive start and exclusive end+timeframe, then subtract one. Reject start beyond candle length or end before start before clamping end to last actual candle. Returned market keeps full calculation arrays and default zero offset/trend flags.


### TB103 — LiveClosedRegimes.stage

Context manager with first_dirty_main. Capture previous published map by reference, allocate empty current map, yield the resolver TB106. Assign the current map as published only on normal continuation after the yield, dropping unused entries. An exception thrown through the yield bypasses the assignment. Does not catch errors or publish the original cache on failure; outer append error handling replaces the view.

### TB104 — MarketIndexWindow.__init__

Keep supplied candle reference, slice parent timestamps at [start,stop), and store logical length stop-start. If the supplied index is another MarketIndexWindow, flatten its base and add start to its base offset; otherwise use supplied index and start. No independent bounds validation or candle equality check at construction.

### TB105 — LiveClosedRegimes.__init__

Allocate fresh empty published mapping for this owner instance. No other inputs or return value.

### TB106 — LiveClosedRegimes.stage.resolve

Compute absolute excluded end = market.index_offset + boundary. Key fields in order: direction, index offset, end, boundary candle timestamp, visible start, min(visible end,boundary-1), initial bullish flag, initial bearish flag. Consult previous map only if end<=first_dirty_main; missing/null selects calculate() with no arguments. Store selected result in current map and return same reference. Does not read current for a second same-stage hit. Caller validates the independently confirmed Primary3; projection copies before annotations. Native callback and lookup failures propagate.

### TB107 — MarketIndexWindow._first

Clamp left=max(left,0), right=min(right,length). Empty interval returns null without dispatch. Otherwise query selected base method at [base_offset+left,base_offset+right) with unchanged level. Return null for null hit, otherwise subtract base_offset from position. Position zero is valid.

### TB108 — MarketIndexWindow.first_less

Call TB107 with bound base.first_less and unchanged local bounds/level. Strict Low crossing and earliest qualifying position are delegated.

### TB109 — MarketIndexWindow.first_greater

Call TB107 with bound base.first_greater and unchanged local bounds/level. Strict High crossing and earliest qualifying position are delegated.

### TB110 — MarketIndexWindow._extreme

Require 0<=left<right<=length; otherwise ValueError. Call selected base method at translated half-open bounds. Return base extreme value unchanged and base position minus offset. No clamping, conversion or independent tie rule.

### TB111 — MarketIndexWindow.range_minimum

Delegate to TB110 with bound base.range_minimum and unchanged local bounds. Preserve base extreme/tie semantics.

### TB112 — MarketIndexWindow.range_maximum

Delegate to TB110 with bound base.range_maximum and unchanged local bounds. Preserve base extreme/tie semantics.
