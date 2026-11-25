# Chronology and time model — foundational contract (V3.0)

Use these time primitives without replacing the event-order rules owned by each algorithm. See [Phase 03 evidence](../Audit/Phase_03/README.md).

## T01 — Time representations

RAW time is converted to an integer epoch-second value during aggregation. Lower observations retain their timestamp; the variable name seconds is not proof of one-second sampling. Do not create intervening synthetic candles or infer the order of high/low inside an OHLC record.

Bridge local conversion uses the Asia/Tehran timezone database, then removes the timezone from the resulting local datetime. The inverse attaches Asia/Tehran to the local datetime and converts to epoch, then to integer (native truncation toward zero). It does not reinterpret local values using the host timezone. It does not separately normalize an already-aware input before replacing its timezone. Cache by epoch integer for forward conversion and by native datetime equality for inverse conversion. Display timestamp strings use year-month-day, a space, hours:minutes:seconds. Parsing uses that format; datetime inputs bypass string parsing. String conversion has a separate cache. No constant UTC offset is specified: runtime timezone database and ambiguous-local-time behavior are external conditions.

## T02 — Market timeframes and ranges

Configured main timeframe is positive integer seconds at CLI. MarketChronology rejects timeframe_seconds < 1, stores a duration and uses supplied timestamp arrays from prepared indexes when present. DetectorBase independently derives its timeframe from the first two main timestamps, or one second for a singleton/empty sequence, and rejects nonpositive duration. These are different contracts; do not silently substitute the configured timeframe for the derived value.

Main bucket timestamp = floor(epoch / timeframe) times timeframe (epoch aligned). For one second, use the exact normalized epoch. Lower buckets group only consecutive equal integer timestamps. Main buckets group consecutive equal aligned timestamps. Missing slots are not inserted. See [candle contract](07_Candles_And_Market_Input.md).

Batch calculation consumes the complete input, not a subset cut at from/to. The requested start and end are aligned down to the main bucket boundary (identity for one second). With ascending bucket times:
- visible start = first bucket at or after aligned start;
- visible end = first bucket at or after aligned end + timeframe, minus 1;
- reject if start is past available candles or end precedes start; clamp end to last candle.
Both index endpoints are included for visibility selection. The full physical chronology is still available for formation and resolution. The response actualFrom and actualTo are epoch timestamps of the visible boundary candles, not necessarily the request integers.

## T03 — Lookup bounds and source ownership

Define LOWER_BOUND(sorted, x) as first position with value >= x, or length; UPPER_BOUND as first position with value > x, or length. They do not sort input. Equality, duplicates and empty ranges follow these definitions.

| Service | Contract |
|---|---|
| MarketChronology.lower_bounds(start,end) | left = lower_bound(lower times,start); right = lower_bound(lower times,end), or length if end absent. Slice [left,right). |
| MarketChronology.main_index(time, clamp=false) | upper_bound(main times,time)-1; if negative return 0 only when clamp true, otherwise raise. No separate upper bound on timestamp; after last start maps to last position for nonempty input. Empty array with clamp true can return 0, not proof of a candle. |
| DetectorBase.seconds_between | lower bounds at start and end; lazy iteration of selected positions. |
| DetectorBase.main_source_for_time | upper_bound-1; require position in detector start/end inclusive, then time strictly before next actual main timestamp or last timestamp + derived timeframe; otherwise null. |

A positional index is not inherently the same as the value stored in a candle's index field; standard construction aligns them, regime segmentation reindexes them. Preserve each call's distinction. In gaps the mapping can select the previous main start, not a synthetic bucket.

## T04 — Reset and confirmation time

Reset resolution precedence: nonempty second_time parsed as display datetime; otherwise nonempty display_time parsed; otherwise native timestamp attribute. Cache by integer index (default -1), integer from_first_idx (default -1), second_time, display_time, timestamp, and string broken_level (default empty). Return cached non-null value. No fabricated fallback for malformed strings.

Reaction confirmation cache key includes direction, Boolean use_intrabar_start, integer First and Break, string BoxTop and BoxBottom, and intrabar_start only when enabled. Resolve Break candle by its index. Start at intrabar_start if enabled and truthy, else at Break open. If start precedes Break open or is at/after Break open + timeframe, use Break open. Scan lower rows in [start,Break open + timeframe) in order. Return first timestamp satisfying high > BoxTop for bullish, low < BoxBottom otherwise. If none, return Break open and cache it; that is a source fallback, not proof a strict lower crossing occurred. Default use_intrabar_start=true; false deliberately starts at Break open (A path).

## T05 — Independent regimes and public times

Segment uses existing main positions [start,stop), requires 0 <= start < stop <= length. Lower window begins at first included main time and ends at next main time, or last main time + timeframe at physical end. Replace each candle record with a local sequential index and construct a new chronology using the original runtime chronology type. Index offset accumulates segment start; source timestamp and price remain unchanged. Adjust visibility indexes relative to segment. Initial-trend flags use explicit override when supplied; otherwise inherit only at start zero.

Do not merge source, decision, confirmation, stop-candle and stop-event times into one field. At output, T/F repair search horizon is visible last main time plus timeframe minus one second, inclusive for lower rows. StopAll confirmation closure compares decision epoch plus configured main timeframe to the smaller of visible horizon exclusive and final lower timestamp plus raw_timeframe. Module-specific event races and exact order/priority rules remain later extraction work.

## Limits

The binary searches rely on input ordering; batch aggregation does not sort or validate it. Live ingestion validates chronological order separately. Native timezone and date parsing behavior is delegated to the runtime. No actual market data was accessed.
