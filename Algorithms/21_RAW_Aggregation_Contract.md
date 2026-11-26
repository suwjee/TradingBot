# TB-RAW — Exact aggregation contract

Input: ordered or unordered RAW records with integer-convertible time and Decimal-convertible OHLC, positive integer timeframe in CLI, lower_only defaults false. Function does not validate chronology. Return (LowerRows, MainRows) with time, open, high, low, close; no synthetic gap candles.

```text
cache := empty map keyed by (runtime type, equality value)
NORMALIZE(x):
  IF key exists: RETURN cache[key]
  cache[key] := x if Decimal else Decimal(string(x))
  RETURN cache[key]
LOWER := []; MAIN := []
FOR row IN original input order:
  t := integer(row.time)
  p := [NORMALIZE(row.open), NORMALIZE(row.high), NORMALIZE(row.low), NORMALIZE(row.close)]
  PUSH_OR_MERGE(LOWER,t,p)
  IF lower_only: CONTINUE
  bucket := t IF timeframe=1 ELSE floor(t/timeframe)*timeframe
  PUSH_OR_MERGE(MAIN,bucket,p)
RETURN (LOWER,MAIN)
PUSH_OR_MERGE(series,time,[o,h,l,c]):
  IF series empty OR last.time != time: append(time,o,h,l,c)
  ELSE:
    last.high := h IF h > last.high ELSE last.high
    last.low := l IF l < last.low ELSE last.low
    last.close := c
```
Nonconsecutive equal buckets need not merge. First open, last close, equal extrema keep earlier representation. Lower-only returns empty Main. Batch timeframe 1 uses lower_only=true. Cache per build. Internal optional tails are mutable initial output records; live transaction is a separate contract.

Example: two time=5 rows with OHLC [1.00,2.0,0.50,1.5], [1.5,2.00,0.4,1.25] -> lower time=5 OHLC [1.00,2.0,0.4,1.25]; main tf=60 time=0 same OHLC. Time=65 opens bucket=60. Equal Decimal keys share first representation. Validated against extracted Bridge aggregation for all seven RAW files at 1/60/300 seconds, plus synthetic tests; not full Engine or live transaction.
