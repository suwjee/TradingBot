# Search, range-index and cache contracts (V3.0)

This is the shared primitive contract; caller-specific time gates, cache dependencies and event ownership remain with their respective algorithms.

## I01 — LowerTimeframeIndex model and construction

Store original candle sequence by reference; store timestamp list, logical length, capacity (smallest power of two >= length, starting at 1), parallel minimum/maximum arrays of size 2*capacity with empty values null, and matching positions initially -1. Index positions are sequence positions. Normalize each leaf Low and High by shared Decimal helper. For every internal parent, select nonempty lower minimum and higher maximum, taking left child on equality. Unoccupied subtrees have null extreme and position -1. Tree construction does not reorder candles or validate monotonic time. Optional retain_crossings=false; if true allocate ordered crossing history.

## I02 — Query contracts

| Query | Bounds | Result / tie |
|---|---|---|
| range_minimum(left,right) | require left>=0, right<=length, left<right | minimum Low plus earliest equal position |
| range_maximum(left,right) | same | maximum High plus earliest equal position |
| first_less(left,right,level) | clamp left to at least 0, right to at most length; empty returns null | earliest position with Low strictly below level |
| first_greater(left,right,level) | same clamping | earliest position with High strictly above level |

Extreme queries reject invalid/empty ranges or no found extreme with ValueError, rather than returning null. Both use half-open [left,right). Range traversal folds candidate tree nodes, replaces best on improvement or equal value with smaller position. Crossing search prunes by root extreme, scans left intervals in forward order, defers right intervals and scans them in reverse discovery order; descends qualifying node taking left child unless its extreme excludes the predicate, otherwise right. Less search excludes values >= level; greater search excludes <= level. No equality crossing. Do not substitute final candle high/low for exact earliest lower observation.

## I03 — Refresh and settled crossing history

Refresh suffix requires 0 <= first <= old length <= new length <= capacity. If first equals new length return unchanged. If crossing cache exists and first < old length-1, clear crossing history. Replace timestamp suffix, update logical length, refill leaf suffix and recompute affected parent ranges. No shrink via this method; caller may construct new index instead.

Crossing cache key = (clamped left, level, excludes predicate identity). Value = (examined position, found position or null). Default (left,null). If a cached found position exists, return it only if < current right, otherwise null. If already examined >= right return null. Search from examined to right. Settled boundary = length-1; remember found position only when strictly before settled boundary. Otherwise, if min(right,settled) advances beyond examined, store that new examined point with null found. Latest row remains mutable and must be reconsidered. On insertion/update beyond 16,384 entries evict the first entry in insertion order; cache hits do not move entries. The source uses ordered dictionary insertion order, not LRU.

## I04 — Identity caches

Process-local caches for sequence timestamps, lower indexes and reflected views are keyed by object identity; stored original sequence reference is checked by identity before reuse. Distinct equal sequences do not share these entries. A prepared lower index must belong to exactly the supplied candle sequence, otherwise ValueError. A provided valid prepared index replaces the entry. Timestamp and reflected-view caching assumes appropriate immutable-source lifetime; do not extend the cache to different sequences by value equality.

Reflected candle view is lazy; cache each mirrored record by source position. Slice normalizes bounds and returns a newly built list of selected reflected records. Reflected lower index shares base timestamps and delegates:
- first_less(level) -> base.first_greater(copy-negate(level));
- first_greater(level) -> base.first_less(copy-negate(level));
- range_minimum -> base.range_maximum and copy-negate returned price;
- range_maximum -> base.range_minimum and copy-negate returned price.
Positions are unchanged.

Clear all three market caches at calculation scope boundaries; release selected regime sequences by identity. The bridge clears its three timestamp-conversion caches before and in finally after calculation and calls optional reaction clear_market_indexes at both boundaries. MarketChronology owns independent confirmation/reset caches and shared E main-extreme cache for its chronology. See [time contract](03_Chronology_And_Time_Model.md) for exact keys. Do not treat these process-local cache rules as a guarantee of thread safety or global immutability.

## I05 — Additional primitives

Chronological containment index partitions source intervals into monotonically ordered runs when start or end decreases; queries strict interval-start and inclusive interval-end, preserving source order. Ordered-naive-datetime helper requires exact native datetime type, null timezone and nondecreasing sequence. See [core utilities](05_Core_Utilities.md) for the complete primitives.

DetectorBase minimum_low and maximum_high scan inclusive start/end when end-start<16, updating only on a strict better value. At end-start>=16 use range index on [start,end+1); reflected sources delegate to reversed extreme and copy-negate. This is the source threshold, not a benchmark result.

## Module-specific continuation

See [module cache contracts](11_Module_Cache_Contracts.md) for the Order gate key/capacity, Reaction, Blue, A, S, E, Order Audit, StopAll and Primary continuation dependencies. Detailed function-level extraction remains separate. No execution, benchmark or dataset access.
