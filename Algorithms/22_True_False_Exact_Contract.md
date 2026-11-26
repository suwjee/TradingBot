# TF — Exact final annotation contract

Input: direction, final group containing sZones/eZones/stopAlls and primaryLows (bullish) or primaryHighs (bearish); optional first_crossing(direction,start,price) and stopall_confirmation_closed(row). Required sourceTime, S color, E family and number, optional parentSourceTime; StopAll and Primary number; price for repair. Only calculationValid exactly false excludes. Mutate in place only trueFalse (V), trueFalseRepairTime (R), trueFalseRepeated (P); return no independent value.

## TF-01 owner selection
Remove all three annotations from every row in the four relevant groups. Choose first valid row per sourceTime, in group priority Primary, StopAll, E, S and original within-group order. Sort owners by sourceTime. Set each V=null. Accumulate S/E in Basic; StopAll in current group. Primary finalizes and clears StopAll group and sets V=T for 1, F for 2 or 3, else null. Basic is not reset at Primary. At end finalize Basic and last StopAll group.

## TF-02 Basic
Rank=(priority,ordinal), lexicographic. Priority S Blue=1,E Blue=2,S Red=3,E Red=4; S ordinal 0, E number. Skip before first S. Maintain known[sourceTime] and repeats[rank]=(latest,repair_count,verdict_count).
```text
FOR each Basic event after (and including) first S:
  lower := existing ranks < current rank
  engulf := any lower.verdict_count >= 2
  IF S OR engulf: v := T
  ELSE IF known parent exists: v := opposite(parent verdict)
  ELSE: v := F IF number odd ELSE T
  row.V := v; known[source] := v
  FOR each lower rank: remove it; IF latest.V=F AND repair_count=1: REPAIR(latest,source)
  IF engulf: reset only verdict_count of remaining repeats to 0
  repair_count := 1; verdict_count := 1
  IF same rank exists AND latest.V=v:
    add previous counts respectively
    IF v=F:
      IF latest.R exists AND latest.R >= source: delete latest.R
      REPAIR(row,source)
  repeats[rank] := (row,repair_count,verdict_count)
REPAIR(row,start):
  IF callback absent OR R already present: RETURN
  t := first_crossing(direction,start,row.price)
  IF t != null: row.R := t
```
Actual callback scans bounded lower index from first time >= start through last time <= horizon inclusive, Decimal price, first Low < level bullish or High > level bearish; return epoch or null. Exact equality is not a crossing. Actual lower-index callback was not integration-tested.

## TF-03 StopAll series
State previous=0, prior_end=0,max_prior=0,series_start=null,verdict_start=null,prefix=[],restart=false.
```text
FOR row IN chronological group:
  n := row.number
  IF series_start=null OR n<=previous:
    prior_end := previous; max_prior := max(max_prior,prior_end)
    series_start := n; verdict_start := n; clear prefix; restart := false
  ELSE IF restart: verdict_start := n; restart := false
  previous := n
  row.V := T IF (n-verdict_start) even ELSE F
  IF n <= max_prior:
    append row to prefix
    IF n IN {prior_end,max_prior} AND (closed callback absent OR closed(row)):
      FOR item IN prefix:
        item.P := true; item.V := T IF (item.number-series_start) even ELSE F
      restart := true
```
Prefix persists after match, allowing later larger match to overwrite temporary verdicts. Primary starts a fresh StopAll group. Example 1,2,3 then 1,2,3,4, confirmations closed: first T,F,T; second 1..3 repeated T,F,T; 4 fresh T. Closed=false prevents repetition match, not ordinary verdict. Tested against pinned true_false with synthetic callbacks and extracted priority, not full lifecycle.
