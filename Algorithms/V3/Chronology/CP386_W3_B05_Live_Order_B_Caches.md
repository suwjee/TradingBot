# CP386 — Independent W3 B05 Live Order_B caches

Pinned production: `c99b4c957e932d9ee70c492ca03ce80711447fc1`; source `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 378–441. Local contract only.

### OA07-A — lines 378–385
Fixed direction at construction: exact bullish/bearish required; invalid direction raises before any assignments. Store direction and low for bullish else high. No per-update direction change or dataset identity.

### OA07-B — lines 386–389
Initialize independent empty boundary/crossing dictionaries and previous lower timestamp None. No external ledger ownership.

### OA08-A — lines 390–396
Validate first_dirty_main in inclusive 0..len(main times), chained comparison short-circuits. Sentinel equal length yields None; otherwise direct main timestamp lookup. No proof input dirty index is first actual modification.

### OA08-B — lines 397–404
Read current lower timestamp array, last element if truthy else None. dirty_lower lower bound of dirty timestamp or current length when sentinel. old_limit upper bound of previous last timestamp on CURRENT lower array or zero. These count positional coverage only if caller preserved prefix and current arrays/index alignment. Allocate two new local dictionaries; persistent fields unchanged.

### OA09-A — lines 406–410
Boundary key native (first,last) tuple. Current get first; only None permits old lookup and only when last < dirty main; equality invalidates prior boundary. Does not compare prices, source identity or actual prefix.

### OA09-B — lines 411–415
If still None compute native boundary; assign to current key and return cached triple unchanged. Only queried keys retained after publication. No Decimal normalization on reused values beyond original provider.

### OA10-A — lines 416–419
Crossing key is (reset_time,level), native hash/equality; equal Decimal numeric values with differing exponents coalesce, not representation-exact key. Current membership distinguishes cached None from absent and returns unchanged immediately.

### OA10-B — lines 420–422
Read previous value with get; reuse non-None only if dirty None or old strictly before dirty, latest lower exists and old <= last_lower. Dirty equality rejects; last equality accepts. Does not locally check old still present or unchanged at exact position.

### OA10-C — lines 423–427
Otherwise start strictly after Reset via bisect_right; if old key exists including old None, advance to max(base left,min(old_limit,dirty_lower)); absent old key searches from base. Old coverage computed against current chronology, not independent historical array. Native OA05 scan may return None. Correct reuse requires aligned immutable prefix and complete dirty invalidation.

### OA10-D — lines 428–430
Assign found timestamp or None in current crossing dict and return. Distinguish current cache null retention from previous-key suffix eligibility; no direct persistent assignment here.

### OA08-C — lines 431–435
Call OA06 with fixed direction, all supplied streams, anchors, local boundary/crossing closures. No catch; if discovery or its callbacks raise before normal return, persistent cache assignments below not reached. Arbitrary external callback mutation is not rolled back.

### OA08-D — lines 436–441
After normal return (including empty result), replace persistent boundaries, crossings, then last lower timestamp, return found unchanged. Unqueried old keys evicted. This is post-success publication, not transactional rollback for arbitrary setter or external side effect.

## Census

- branches: 16
- comparisons: 16
- arithmetic: 2
- calls: 16
- accesses: 154
- effects: 13
- exits: 6

223 category rows = 50 W1 + 173 additional; 5 historical supplements. All 1,047 prior CP384–385 rows revalidated without overlap. B05 cumulative 1,270 category rows, 296 W1, 974 additional, 19 supplements.

## Consumer boundaries

- OA08->OA06: Discovery normal return precedes publication; local exceptions before return do not assign persistent caches. External effects not rolled back.
- OA09->OA04: Boundary reuse strictly before first_dirty_main; native calculation only on None. Caller must prove unchanged source candles and exact Decimal representation on reused prefix.
- OA10->OA05: Native numeric Decimal key equality, current null retention, previous key membership permits suffix. Caller must establish aligned current lower arrays/index, prefix through old coverage, safe dirty timestamp, no stale hit or excluded candidate.
- Caller dirty-frontier and live finder: No dataset identity key or prefix check in OA07–OA10; independent live caller scope, creation and reset/replacement conditions remain pending. No runtime bug asserted.

## CP386-F01

Explicit current/previous null distinction, native Decimal cache-key equality, strict dirty admission, prefix-dependent suffix coverage and post-normal-return publication; no runtime defect asserted.

- Local cache mechanics only. Full prefix equivalence, lower-index freshness, dirty-frontier correctness, caller direction/run scope and rollback of external mutation remain independent.
- No RAW payload, runtime, ZIP or production changes. Native exceptions not tested.
- No new runtime defect inferred from missing local caller validation.
