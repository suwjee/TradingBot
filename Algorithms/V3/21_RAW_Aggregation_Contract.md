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
Initialize lower/main candle arrays and corresponding indexes to empty/null.

### TB20 — LiveMarketViews._update_series
Rebuild mutable candle suffix from dirty if existing index else zero; replace suffix. If no index or new length exceeds capacity, construct a fresh LowerTimeframeIndex with crossing-history retention enabled; otherwise refresh_suffix in existing index. Return index. The retained candle list is changed before index construction or suffix refresh; there is no local rollback. Equal length to capacity reuses the index. An absent index forces rebuild from zero, even if caller supplies a later dirty boundary.

### TB21 — LiveMarketViews.update
Timed update of lower series; timeframe1 main and index alias lower, otherwise timed separate main update. Mutates object in place. Lower update is published first. TF1 aliases both candle and index objects; nonshared main is updated separately and may fail after the lower update.

## Legacy and projected serialization

### TB63 — market_segment
Require nonempty valid [start,stop). Slice main and lower by main boundary times (end exclusive, last+timeframe if full tail). Replace candles with local enumerated indexes; construct fresh chronology same type and lower index. Offset increased by start; visible range clamped/adjusted; initial trend flags inherited only if start=0 unless explicitly supplied.

### TB68 — prepare_market_context
Timed read input bytes; remove UTF-8 BOM prefix; parse JSON using Decimal parse_float; delegate rows to TB69.

### TB69 — _prepare_market_context_from_rows
Use full file rows for calculation; empty raises ValueError. Timed bucket normalization, lower_only at tf1. Delegate TB70, never slice raw to visible range.

### TB70 — _prepare_market_context_from_buckets
Batch: build lower candles, shared lower index, main candles or tf1 alias, chronology. Live: require delta, update views, register prepared lower/main indexes, chronology. Determine requested visible bucket epochs (floor for tf>1); bisect start and end+tf minus one. Empty range raises, end clamped to last. Return full context with visible bounds.
