# CU — Core utilities

Source-derived specification; module version 1.1.0. Behavior-neutral helpers do not own market state. No market data or runtime tests were used for this revision.

## Decimal normalization and physical identity

| Operation | Inputs | Output and exact behavior |
|---|---|---|
| AS_DECIMAL | value | If already a Decimal (including subclasses), return the original object. Otherwise construct a Decimal from its string representation, without rounding or quantization. |
| ORDER_IDENTITY | first index, break index | Convert each independently to an integer in first-then-break order; return the ordered pair. |
| REACTION_IDENTITY | reaction-like object | Read its first_idx then break_idx and convert each to an integer; return the ordered pair. |

OrderIdentity is a pair of integers. Direction, timestamps, price, numbering and provenance are not part of that pair. Conversion and missing-field exceptions propagate; there is no fallback. Decimal conversion does not independently reject non-finite values; constructor semantics apply. Do not assume arbitrary external inputs are lossless before their string conversion.

## Ordered naive datetime predicate

Given a sequence, first require every element's exact type to be datetime (not a subclass) and its timezone field to be null. If that check succeeds, require each adjacent pair to be nondecreasing. Equality is accepted; empty and valid singleton sequences return true. Any failed condition returns false. No sorting, normalization or timezone conversion is performed. The first universal check short-circuits before the ordering check.

## Chronological containment index

The constructor consumes an iterable of triples (interval start, interval end, payload). Maintain a sequence of runs, each with aligned start, end and payload arrays.

1. Start with empty runs and an empty current run.
2. For each input triple in caller order, if the current run is nonempty and either the new start is strictly less than the last start or the new end is strictly less than the last end, seal the current run and begin an empty run.
3. Append all three values to the current run, preserving original payload identity.
4. Seal the final run only if nonempty.

Both time arrays in each run are nondecreasing. Equality does not split runs. No global sort, deduplication, interval validation or price operation occurs.

Query (query start, query end) is lazy and produces an iterator of original payloads:

~~~text
FOR EACH run in original run order:
    stop := first position whose start is >= query start (or run length)
    first := first position within [0, stop) whose end is >= query end
             (or stop if none)
    YIELD payloads at positions first through stop - 1 in ascending order
~~~

Equivalent predicate on comparable timestamps: interval start strictly precedes query start AND interval end is at or after query end. Exact start equality excludes; end equality includes. Identical/duplicate qualifying triples are not coalesced. An empty index yields nothing. The query neither mutates the run arrays nor recomputes intervals. Comparability errors propagate; the ordered-naive helper is separate and is not called by the constructor.

Build time and storage are O(n). Query cost across r runs of lengths n_i is O(r + sum(log(n_i + 1)) + k), where k is the number of results, assuming constant-time comparisons. This complexity is inferred from the two bounded binary searches per run, not benchmarked.

## Ownership and errors

Only the constructor builds the index; querying is read-only apart from iterator progress. None of the helpers change trading lifecycle or directional semantics. All external conversion and comparison behavior is delegated to the relevant native types; no local error swallowing exists.

Source provenance: see [Phase 02 module inventory](../Audit/Phase_02/pipeline__core_utils.json). Historical synthetic evidence is separate and not a requirement of this source-only revision.
