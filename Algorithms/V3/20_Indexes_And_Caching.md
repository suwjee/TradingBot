# Shared primitives, chronology, indexes and caching (V3)

**Conventions:** B = bullish, R = bearish. Preserve Decimal representation, evaluation order, native failures, exact versus main-candle time, original array order and nulls. Record interfaces: [Declared schemas](../../Contracts/Declared_Record_Schemas.md). Operation IDs designate semantic procedures, not required implementation symbols. This contract does not claim runtime equivalence.


## IX-M01 — Core and directional semantics

Use exact Decimal normalization: already Decimal remains same object; other values convert from native string, not binary-float constructor unless a particular owning operation explicitly uses direct Decimal conversion. This does not recover precision already lost upstream. Physical identity is ordered integer-converted First/Break, with direction supplied by containing ledger, no inferred validity. Direction policy owns price comparisons only.

| Property | B | R |
|---|---|---|
| Directional extreme | Low | High |
| Opposite extreme | High | Low |
| First color | RED | GREEN |
| Context | GREEN | RED |
| Strict stop and improvement | X < level | X > level |
| Choose directional extreme | min | max |
| Reaction confirmation | High > BoxTop | Low < BoxBottom |

For standard finite prices equality never crosses; native exceptional Decimal comparisons/traps apply. Opposite direction is independent of color or family. Native candle tag GREEN iff Open<=Close. Reflection copies Decimal sign and swaps High/Low/RED/GREEN internally, not market Doji classification.

## IX-M02 — Chronological queries and containment

Market main and lower times preserve original input order; binary search assumes appropriate ordering. lower_bounds uses first position >=start and >=end (end null -> length), half-open interval; upper_bound gives first strictly after. Containing main = upper_bound(main times,event)-1; clamp only if requested on left, no right guard. Detector-specific main_source_for_time additionally requires selected range and next actual main timestamp (last uses nominal timeframe). Do not replace these two different mapping contracts by one. Reaction exact confirmation uses Break main interval, optional intrabar_start when within candle, otherwise main open; first strict confirmation else main open fallback. A disables intrabar start. Reset parse exact second first, then display, then timestamp. All cache keys preserve specified strings and exact times; no inference of true lower evidence from fallback.

Containment index partitions caller-order triples into runs when start or end decreases; each run monotone both. Query start strictly greater than stored start and query end <=stored end: bisect start cutoff, then first end>=query end before cutoff, yield original payloads. No sorting or fallback occurs inside the shared index. Native Reaction containment traverses the original opposite spans if any span bound is not an exact naive datetime. Blue builds its index lazily only when geometry is needed, skips Reaction entries with missing time bounds, disables the index for any remaining ineligible bound, and traverses the original Reaction list when the index is unavailable or the Blue source time is ineligible. Both callers retain their own time and geometry predicates. Equal start excluded, equal end included. Native timeline may contain gaps; do not fabricate missing candles.

## IX-M03 — Segment index

Capacity smallest power of two >= length (minimum1), arrays of min Low/max High and earliest positions, null empty leaves. Fill leaves; parent chooses better child, left wins equality. Range query [left,right) requires valid nonempty interval, decomposes segment nodes, selects strict better or equal earlier position. First strict crossing clamps bounds, rejects empty, skips segment if min>=level or max<=level, inspects left nodes then reversed right nodes to find earliest eligible; descend left first unless excluded. Missing hit null. Reflected queries swap min/max, negate price by sign-copy, preserve position. Main extreme scan uses segment service for distance>=16, otherwise strict sequential update; E sparse table uses earliest tie. No common tie policy for S last-equal source (owner module explicit).

Suffix refresh requires 0<=first<=old length<=new length<=capacity. Replace times and leaves, update ancestors; clear crossing cache only when changed position < old length−1. Crossing cache keyed (left,level,exclusion comparator), remembers settled results only before last position; on append resume examined frontier. Cache hit returned only within requested right. FIFO cap 16384; expansion beyond capacity creates new index. Source identity global caches require same sequence object; clear/release by calculation context. Not a proof against arbitrary external mutation of shared objects.

## IX-M04 — Module cache dependency map

| Owner | Key / invalidation authority |
|---|---|
| Reaction | shared sequence identity, gate direction/index/end/exact event, confirmation geometry and flag, reset identity/time/level, live prefix/checkpoint; bounded gate FIFO32768 |
| Blue | reaction checkpoints previous/count/spacing/output length; dirty Reaction/Reset owners rewind |
| A | dirty exact time, common reaction First/Break/confirmation prefix, stop/cross/extent/zone histories, null entries and Decimal representation keys |
| S | detector range/scope and changed trend/opposite geometry, Reset/Blue dependencies; settle lower decision plus required Break/confirmation |
| E | chronology identity/scope, dirty stop progress, main ranges, zone geometry keys and reconciled source steps/evidence; reopened race invalidates replay |
| Order | physical number/identity, start and level, parent/deadline/flags, ledger creation/confirmation indexes, reset map; native validation fallback and invalidations |
| StopAll | event representation keys, checkpoint state and covered lower horizon |
| Primary | activation schedule, exact dirty boundary, strict crossing cache and reflected object identity |
| Bridge | epoch/local/display conversion keys scoped to calculation, bucket/view suffix transaction; closed-prefix cache by complete independent regime key and dirty main frontier (TB103,TB105,TB106); MarketIndexWindow translates local bounds/positions (TB104,TB107–TB112) |

Exact per-owner keys and reuse gates are defined in owning module procedures, not generalized to a shared cache policy. [Live Bridge](18_Live_Bridge.md) distinguishes active replay from conditional continuation.

## Detailed core operations

### C01 — ChronologicalContainmentIndex constructor

Input: ordered iterable of triples (start datetime, end datetime, payload of arbitrary type). Create an empty ledger of runs, and three empty working arrays. In caller iteration order, when the working run is nonempty, split BEFORE the current triple if its start is strictly less than the last start OR its end is strictly less than the last end. Store the three previous arrays as a run and start fresh arrays. Append current start, end and original payload reference to corresponding arrays. At exhaustion store final run only if nonempty. Equal boundaries do not split. No sorting, deduplication, interval validity validation or payload copy. Empty input gives zero runs. State owned by the index. Iterable/unpacking/comparison failures propagate; construction does not return a separate result.

### C02 — ChronologicalContainmentIndex.enclosing

Input: query start S, end E. Lazy iterator: for each stored run in original order, calculate stop = first index whose start >= S (or run length), then first = first index in ends[0:stop] whose end >= E (or stop). Yield original payloads at positions first through stop exclusive, in ascending order. Equivalent predicate on valid sorted runs: stored start < S AND stored end >= E. Strict left, inclusive right; equal start excluded; equal end included. Does not reorder, mutate, copy or deduplicate payloads. No match yields nothing. Search/comparison failures occur during iteration, not necessarily at iterator creation.

### C03 — ordered_naive_datetimes

Input sequence. First require ALL values to have exact datetime type (subclasses excluded) and null tzinfo, with short-circuit evaluation. Only if true, require every consecutive pair in original order to satisfy earlier <= later. Empty and singleton eligible sequences pass when element check passes. Equal times allowed; no sorting. Return Boolean. Index/comparison/type-protocol errors propagate. Both generator scopes are included in this description.

### C04 — as_decimal

If value is an instance of Decimal (including subclass), return the same object. Otherwise obtain the native string representation and construct Decimal from that string, under applicable native Decimal conversion behavior. No rounding policy, quantization or binary-float conversion is added; already-float inputs retain the native string's representation, not the original lost precision. Conversion failures propagate. No explicit mutation.

### C05 — order_identity

Inputs first index and break index as arbitrary convertible objects. Convert first to integer, then break to integer; return ordered two-element tuple. Native integer conversion (including truncation of convertible non-integral numeric values) applies, not an explicit index validator. Errors propagate in evaluation order. No chronology/order validity check, direction, numbering or provenance field is included.

### C06 — reaction_identity

Input reaction-like object. Read first_idx and convert to integer, then read break_idx and convert to integer; return ordered pair. Missing attribute or conversion errors propagate. No call to C05 is required, no validation or mutation. Same physical identity convention as C05.

## Detailed directional operations

### D01 — Opposite direction
Exact stored bullish yields bearish; all other stored direction values yield bullish. Public selection D06 validates separately.

### D02 — Strict stop
Use value < level for bullish, value > level otherwise.

### D03 — Better extreme
Use value < current for bullish, value > current otherwise.

### D04 — Choose extreme
Native min for bullish, max otherwise; first equal ordinary value retained.

### D05 — Confirmation-side crossing
Already selected confirmation-side value > level for bullish, < level otherwise.

### D06 — Policy selection
Exact bullish/bearish selects shared immutable record; anything else raises ValueError. No general annotation runtime validation.

## Detailed chronology/index procedures

### RE31 — LowerTimeframeIndex.__init__
Store candles, optional OrderedDict crossing history, timestamp list; power-of-two size>=length starting1. Min/max arrays null, signed int positions -1 of size2*size. Fill leaves then parents.

### RE32 — _fill_leaves
From first through length, normalized low/high and position at leaf size+position.

### RE33 — _update_parents
Descending nodes last..before_first exclusive. Null left=>right, null right or left min<=right/max>=right=>left, otherwise right; copy corresponding position. Earliest tie.

### RE34 — refresh_suffix
Require 0<=first<=old length<=new length<=size; if first==new length no-op. Clear history if present and dirty first<old length-1. Replace timestamp suffix in place, publish length, update leaves, recompute affected ancestor ranges bottom-up; this helper has no internal rollback. A timestamp-build failure can occur after history clearing, and a leaf/parent failure can leave changed length and partially updated arrays. Caller-owned rollback/discard and accurate first-dirty admission are separate conditions.

### RE35 — first_less
RE40 minimum tree, exclude nodes with value>=level.

### RE36 — first_greater
RE40 maximum tree, exclude nodes with value<=level.

### RE37 — range_minimum
RE39 minimum=true.

### RE38 — range_maximum
RE39 minimum=false.

### RE39 — _range_query
Require left>=0,right<=length,left<right. Standard half-open segment decomposition; consider non-null selected min/max values, strictly better or equal earlier position wins. Raise ValueError if no valid result; return value,position.

### RE40 — _first
Clamp left>=0/right<=length; empty null. Dispatch history or direct RE43.

### RE41 — _first_with_history
Key (clamped left, supplied level, excludes function), with native tuple equality/hash rather than a Decimal string/exponent key. Right bound and source generation are not in the key; reuse depends on the index's owned-source and invalidation contract. Cached crossing returned only if <right; examined>=right =>null. Search from examined. Settled excludes last candle (length-1); remember hit only if <settled, otherwise record no-hit coverage min(right,settled) when advanced. Return actual found crossing even latest unsettled.

### RE42 — _remember_crossing
Assign history key; evict oldest insertion FIFO when size>16384. Updating an existing OrderedDict key does not move it to the end and reading a key does not promote it; this is not LRU.

### RE43 — _search_first
Root null or excluded =>null. Decompose interval; inspect left segments immediately, defer right segments and inspect reversed; first qualifying node descend RE44. This is sequence-position order, not a timestamp sort. Only the root has an explicit null guard; valid populated internal nodes and native exclusion predicates are required. No hit returns null.

### RE44 — _descend_first
Descend left child unless excluded then right; the right child is not separately tested. The valid-tree/qualifying-parent premise makes this positional descent meaningful. Return leaf position with no further clipping.

### RE45 — shared_lower_timeframe_index
If prepared supplied require its candles is source else ValueError; register and return. Otherwise reuse id+identity cached or construct/store.

### RE46 — ReflectedLowerTimeframeIndex.__init__
Retain base and same times.

### RE47 — reflected first_less
Base first_greater with negated level.

### RE48 — reflected first_greater
Base first_less with negated level.

### RE49 — reflected range_minimum
Base maximum, negate value, preserve position.

### RE50 — reflected range_maximum
Base minimum, negate value, preserve position.

### RE51 — clear_market_indexes
Clear all three global time/range/reflected caches.

### RE52 — release_market_indexes
For each supplied sequence remove id key from each global cache if present.

## MarketChronology and internal behavior

### RE53 — MarketChronology.__init__
Require timeframe_seconds>=1. Retain sequences; alias prepared main/lower times by nonnull test, else build. Timeframe timedelta; choose lower index by truthiness (false-valued supplied index falls back to shared index even though its times were selected by nonnull test); store main range index. No local supplied-index identity validation. Empty confirmation/reset/E main extremes caches. Fresh dictionaries belong to this chronology instance, but the retained sequences and prepared time arrays are references, not immutable copies. The initial comparison rejects values below one; native timedelta construction may additionally reject invalid input types or values. RE60/RE61 have no local cache eviction, generation key or invalidation on later input mutation; coherence is an owner/caller lifetime condition, not an unconditional guarantee. A non-None cached result wins before the subsequent source lookup; a cached None remains a miss.

### RE54 — MarketChronology.opposite_direction
Delegate to the module-level RE02 function, not recursively to the class method; RE02 selects the shared direction policy and raises for an unsupported direction under native bindings.

### RE55 — main_index
Upper_bound(main times,timestamp)-1; negative returns0 only if clamp else ValueError. No right-end guard.

### RE56 — lower_bounds
Lower bounds start/end, end null=>len(seconds). Half-open interval.

### RE57 — lower_window
Slice lower by RE56.

### RE58 — _reset_cache_key
Tuple int index/from First defaults -1, second/display/timestamp defaults null, str broken level default empty.

### RE59 — _reaction_cache_key
Direction,bool use_intrabar,int First/Break,str top/bottom, intrabar_start only if enabled else null.

### RE60 — reset_time
Cache RE58; nonnull cached result wins. Parse truthy second_time else truthy display_time using %Y-%m-%d %H:%M:%S, else required timestamp attr. Invalid truthy parse propagates, never falls through to a different time field. Cache result.

### RE61 — reaction_confirmation
Cache RE59; Break main time. Start truthy intrabar_start or candle_start if enabled, otherwise main start; start before open or at/after Break end resets to main start. Scan lower in source order to Break end exclusive, first strict High>top for exact bullish or Low<bottom otherwise, normalized; no local direction validation. Cache/return hit timestamp; absent => Break main start (fallback, not proof of crossing). A uses flag false; S/E/public usually true.

### RE62 — canonical_order_stop
String-converted mode A: scan_start=max(start_index,int(anchor_idx) if non-null else First-1), extend backward while prior candle tag GREEN for exact bearish Order or RED otherwise. Initialize at scan_start, then scan through Break inclusive; max High bearish/min Low otherwise, strict update first tie, improved source uses candle.index. Return normalized price,source index,time from main sequence at source index. No local range validation. Other modes: reaction_number<=1 raises ValueError; previous opposite at number-2, use previous top/source bearish or bottom/source otherwise. No local previous-health check or new contextual extreme.
