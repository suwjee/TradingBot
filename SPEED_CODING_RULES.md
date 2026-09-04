# Performance Coding Rules for TradingBot Indicator Pipeline
# This file MUST be read by any AI/code agent before writing performance-critical code.

## 1. General Rules

### 1.1 Never change calculation output
- Optimization MUST NOT alter any computed values or JSON output
- Before/after comparison: byte-for-byte identical output is required
- Use `tmp/verify_optimized.py` to validate

### 1.2 Use fast libraries
- **orjson** instead of `json` for parse/serialize (3-5x faster)
- **numpy** for vectorized operations on large datasets (100K+ rows)
- Prefer C-level builtins over pure-Python loops

### 1.3 Use appropriate data structures
- `dict` for O(1) lookup instead of list scan O(n)
- `set` for membership testing instead of list
- `bisect` for binary search on sorted lists
- `__slots__` on frequently-created dataclasses (10-20% faster construction)

---

## 2. Caching Rules

### 2.1 Cache any function that is called repeatedly with the same arguments
```python
# BAD - recomputes every call
def epoch(local: datetime) -> int:
    return int(local.replace(tzinfo=TEHRAN).timestamp())

# GOOD - caches results
_epoch_cache: dict[datetime, int] = {}
def epoch(local: datetime) -> int:
    cached = _epoch_cache.get(local)
    if cached is not None:
        return cached
    result = int(local.replace(tzinfo=TEHRAN).timestamp())
    _epoch_cache[local] = result
    return result
```

### 2.2 Cache keys must be hashable and lightweight
- Use `int`, `str`, `tuple` as cache keys
- Datetime objects are hashable and work as keys
- Avoid `id()` as keys (objects may be recreated)

### 2.3 Cache at the correct scope
- Instance-level cache is better than global cache
- Cache lifetime must match object lifetime
- If object is recreated, cache is naturally reset

### 2.4 For frozen dataclasses, return copies not originals
```python
# GOOD - caller may mutate the result
if _ck in self._cache:
    _cached = self._cache[_ck]
    return replace(_cached) if _cached is not None else None
```

---

## 3. Loop Optimization Rules

### 3.1 Use local variables instead of attribute access in hot loops
```python
# BAD
for row in rows:
    o = Decimal(str(row["open"]))

# GOOD - local binding eliminates attribute lookup
_D = Decimal
_S = str
for row in rows:
    o = _D(_S(row["open"]))
```

### 3.2 Prefer list comprehensions over loop + append
```python
# BAD
result = []
for item in items:
    if condition(item):
        result.append(transform(item))

# GOOD
result = [transform(item) for item in items if condition(item)]
```

### 3.3 Use built-in min/max (C-level) instead of manual comparison
```python
# GOOD - min/max use C implementation
current["high"] = max(current["high"], new_high)
current["low"] = min(current["low"], new_low)
```

### 3.4 Use bisect for binary search on sorted data
```python
from bisect import bisect_left, bisect_right
# O(log n) instead of O(n)
position = bisect_left(sorted_list, target)
```

---

## 4. Object Creation Rules

### 4.1 Add __slots__ to frequently-created frozen dataclasses
```python
@dataclass(frozen=True, slots=True)  # slots=True for performance
class Candle:
    index: int
    timestamp: datetime
    # ...
```
- 10-20% faster construction
- ~30% less memory per instance

### 4.2 Use fast string formatting instead of strftime
```python
# BAD (slow)
display_time = stamp.strftime("%Y-%m-%d %H:%M:%S")

# GOOD (fast)
_DTFMT = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}"
display_time = _DTFMT.format(stamp.year, stamp.month, stamp.day,
                              stamp.hour, stamp.minute, stamp.second)
```

### 4.3 Cache datetime.fromtimestamp calls
```python
_local_dt_cache: dict[int, datetime] = {}
def local_datetime(epoch: int) -> datetime:
    cached = _local_dt_cache.get(epoch)
    if cached is not None:
        return cached
    result = datetime.fromtimestamp(epoch, TEHRAN).replace(tzinfo=None)
    _local_dt_cache[epoch] = result
    return result
```

---

## 5. Duplicate Computation Elimination

### 5.1 Share results between pipeline stages
- If two stages compute the same thing, share the result
- Example: Reaction detection was running twice (E pipeline + payload) -> eliminated

### 5.2 Detect range overlap
- If computing on a subset gives same result as full range, use full range + filter
- Example: reusable_full_context - when start_index is near 0, use full-range results

### 5.3 Quick guard before expensive computation
```python
# GOOD - fast check first
if cached_result is not None:
    return cached_result
# Then expensive computation
result = expensive_computation(...)
```

---

## 6. JSON and Serialization Rules

### 6.1 Use orjson
```python
import orjson
data = orjson.loads(text)  # 3-5x faster than json.loads
```

### 6.2 Minimize string conversions
- `str()` and `repr()` are expensive in tight loops
- Use direct values when possible

### 6.3 Batch Decimal conversion
```python
# GOOD - local binding for speed
_D = Decimal
_S = str
for row in rows:
    value = _D(_S(row["open"]))
```

---

## 7. Python-Specific Rules

### 7.1 Use `from __future__ import annotations` for lazy annotation evaluation

### 7.2 Use `functools.replace` for frozen dataclass copies
```python
from dataclasses import replace
new_obj = replace(old_obj, field=new_value)
```

### 7.3 Use `@dataclass(frozen=True, slots=True)` for immutable objects
- Hashable (can be dict keys)
- Thread-safe
- slots=True saves memory and speeds up creation

### 7.4 Use lazy properties for expensive computed values
```python
@property
def expensive_result(self):
    if self._cached is None:
        self._cached = expensive_computation()
    return self._cached
```

---

## 8. Benchmarking Rules

### 8.1 Always benchmark before and after optimization
- Measure wall clock time with `perf_counter()`
- Compare JSON output byte-for-byte

### 8.2 Output must not change
- Optimization only affects speed, not results
- Use `tmp/verify_optimized.py` for validation

### 8.3 Use cProfile for bottleneck identification
```python
import cProfile
cProfile.run('my_function()', sort='cumtime')
```

---

## 9. Structural Rules

### 9.1 Keep code modular
- One function = one responsibility
- Cache definitions near their associated functions

### 9.2 Use proper naming conventions
- `_prefix` for internal variables
- `__prefix` for private variables
- `_CACHE_SUFFIX` for cache dictionaries

### 9.3 Write docstrings explaining WHY
- Explain why this optimization was applied
- Document cache invalidation conditions

---

## Priority Order (Highest Impact First)

1. **Eliminate duplicate computation** (largest impact)
2. **Cache expensive function calls** (high impact)
3. **Local variable binding in loops** (medium impact)
4. **__slots__ and fast string formatting** (low-medium impact)
5. **orjson and appropriate data structures** (medium impact)
