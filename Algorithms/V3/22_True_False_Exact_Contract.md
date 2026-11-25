# True/False — exact recurrence and repair contract (V3)

**Conventions:** B = bullish, R = bearish. Preserve Decimal representation, evaluation order, native failures, exact versus main-candle time, original array order and nulls. Record interfaces: [Declared schemas](../../Contracts/Declared_Record_Schemas.md). Operation IDs designate semantic procedures, not required implementation symbols. This contract does not claim runtime equivalence.


## TF-X01 — Rank, repair and buffers

Priority rank: S blue=(1,0), E blue=(2,number), S red=(3,0), E red=(4,number); unknown family raises. The repair search uses original lower index through inclusive supplied horizon, left lower_bound(start), first strict Low<level B or High>level R, returns epoch or null. Do not assign a repair if key already exists, including present null. Per [public annotation](16_True_False.md), selected rows only get verdicts. Basic and StopAll recurrences are independent.

## TF-X02 — Basic recurrence (language-neutral)

Initialize empty map of repeats keyed rank, empty map of known verdict by sourceTime, started=false. Iterate S/E buffer in caller order. First S sets started; skip preceding E. For row rank r at time t compute lower ranks L={q in repeats:q<r}, parent=known[parentSourceTime], engulf=any lower verdict_count>=2. Verdict T if S or engulf; else invert known parent (T->F, otherwise T), else F if number odd, T if even. Assign row and known[t].
For each lower repeat remove it; if latest F and repair_count=1, try repair latest at t. If engulf, zero remaining verdict_count only. For same rank if previous latest verdict matches, accumulate both counters from previous+1; when F remove prior repair if its time>=t, then try repair current at t. If no same-verdict match start both counters at1. Replace rank state with latest row reference and counters. No final sweep. Mutate earlier rows in-place when repair removed/assigned; no implicit rollback.

## TF-X03 — StopAll recurrence

Initialize previous_number, previous_series_end, largest_prior_end=0; group_start and verdict_start null; prefix empty; restart flag false. New series when first or n<=previous: previous_series_end=previous_number; largest=max(old,previous_series_end); group_start=verdict_start=n; clear prefix and restart. Else restart flag sets verdict_start=n and clears flag. Update previous_number=n. Assign T iff (n−verdict_start) even. If n<=largest_prior_end append row to prefix; if n equals immediate previous end or largest prior end, and closure callback absent or true, mark every prefix row repeated and recompute parity relative group_start; set restart. Prefix stays until series reset, allowing larger match to overwrite earlier temporary verdicts. Do not add repair to StopAll. Detailed exact procedures below.

## Detailed T/F procedures

### TF01 — repair_crossing_lookup

Inputs lower index, epoch-to-time and time-to-epoch converters, keyword-only through. Compute right = upper bound of through in lower_index.times, i.e. first position strictly after through; return closure TF02 capturing that right and supplied objects. No scan at construction. Captured index and converters are references, not copies.

### TF02 — repair_crossing_lookup.find

Inputs direction, integer start, string level. Compute left = lower bound of converted start in index times, search limited to [0,right). Resolve policy (invalid direction raises). Select first_less if policy extreme field is low, first_greater otherwise. Convert level directly to Decimal. Call chosen search on [left,right) with threshold. If no position return null; otherwise convert index time at result position to epoch and return. Includes start and through, strict crossing according to lower index contract; equality not enough. Do not manufacture intrabar order. Exact index search implementation and converter binding are downstream open items.

### TF03 — _basic_rank

Inputs key and row. If key is sZones, return pair (sequence priority for s and row.color, 0); otherwise (sequence priority for e and row.family, row.number). Priority dependency verified from the lifecycle priority contract: lowercase native string conversions of kind/family; map s/blue=1, e/blue=2, s/red=3, e/red=4; unknown key raises KeyError. Rank comparisons are lexicographic, not price-based. No row mutation. This dependency description is not counted as lifecycle module coverage.

### TF04 — _basic_verdicts

Inputs direction, ordered sequence of (key,row), optional-in-effect first_crossing callback (null permitted). Local maps: repeats keyed by rank and known keyed by source time; initially empty; started=false. Nested TF05 owns repair assignment.

For each event in caller order:
1. Determine is-S. An S permanently starts this pass; skip all preceding non-S events.
2. Compute rank and source time t. Collect keys of existing repeats strictly lower than rank, in map iteration order. Lookup parent verdict using optional parentSourceTime. Engulf is true if any lower rank's verdict_count >= 2.
3. Verdict = T if is-S or engulf; else if known parent is not null then F for parent T, T otherwise; else F for odd number, T for even. Store verdict in row then known[t] (same value; chained assignment evaluates right side once, target order is row then known). Duplicate source times overwrite known entries.
4. Remove each lower repeat. If removed latest verdict is F AND repair_count equals 1, invoke TF05 for that earlier row with current t.
5. If engulf, set verdict_count to zero on all still-retained repeats, leaving repair_count unchanged.
6. Lookup same-rank prior repeat. Start new counters at 1. If prior exists and prior latest verdict equals new verdict, add prior repair_count and verdict_count respectively. If verdict is F, remove prior row repair when its repair time (default -1) is >= t, then invoke TF05 on current row using t.
7. Replace rank's repeat with a new BasicRepeat pointing to current row and updated counters.

No final sweep of repeats; returns no value. This function assumes meaningful ordering from its caller, not internal sorting. Repair callback can mutate shared state or fail; earlier row annotations remain. Lower-rank list and engulf generator are evaluated before removal.

### TF05 — _basic_verdicts.repair

Captured direction and first_crossing; inputs row and start. If callback exists AND repair field absent (present null still counts as present), call callback(direction,start,row.price). If non-null crossing returned, write repair field. Otherwise leave untouched. No separate output; callback exceptions propagate.

### TF06 — _stopall_verdicts

Inputs ordered StopAll rows, optional confirmation_closed callback. Initialize previous_number=0, previous_series_end=0, largest_prior_end=0, group_start/verdict_start=null, empty repeated-prefix list, restart=false.
For each row with number n:
- New series if group_start null or n <= previous_number. Set previous_series_end to previous_number, update largest_prior_end by max, set both start values to n, clear prefix, restart=false. Otherwise if restart flag, set verdict_start=n and clear flag.
- Set previous_number=n. Assign T if (n-verdict_start) even, F otherwise.
- If n <= largest_prior_end, append original row to prefix. When n equals previous_series_end OR largest_prior_end, and callback absent OR callback(row) truthy, revisit every retained prefix row: repeated=true, verdict T for even (its number-group_start), F otherwise. Set restart=true. Prefix is retained until series reset; a larger matching boundary may overwrite earlier temporary verdicts.

No return value, sorting or repair computation. Confirmation callback not called unless the number boundary matches. Earlier repeated flags are not explicitly removed here (TF07 clears them before collection). Equal and decreasing numbers start new series.

### TF07 — apply_true_false

Inputs direction, group mapping, first_crossing default null, keyword-only stopall_confirmation_closed default null. Choose primaryLows for exact bullish, primaryHighs otherwise. Visit collections in priority order: selected primary, stopAlls, eZones, sZones; missing collection acts as empty tuple. For each row, remove the three annotation keys if present, even for invalid/donor rows. If calculationValid is NOT the exact Boolean false, retain the first row per sourceTime (set-if-absent); subsequent same-source rows do not replace it. Sort retained pairs by sourceTime ascending; stable sorting applies, though keys are unique.
Set retained row verdict to null. On a primary row, evaluate accumulated stop rows via TF06 and clear stop buffer; if number is 1,2,3 assign T only to 1 and F to 2/3. Other primary numbers stay null. On stopAlls append to stop buffer; on other collections append to basic buffer. After traversal evaluate TF04 on the entire basic buffer (not reset by primary rows) and then TF06 on remaining stop buffer. No return value, no creation of trading objects. Dictionary identity and row aliases remain observable; a row present in multiple collections can have annotation removed repeatedly during the collection pass. Sorting or callback errors propagate without rollback.
