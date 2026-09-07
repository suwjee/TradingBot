# TradingBot Performance Optimization Summary

## Verified result

- Source: `RAW_FOREXCOM_XAUUSD_1S_FROM_2026_08_18_04_44_40_TO_2026_09_05_00.json`.
- Workload: Bullish, 30 seconds, `2026-08-18 04:44:40` through the complete
  `2026-09-05 00:29:30` candle.
- Profile baseline: `735,381.74 ms` and `671,408,443` calls.
- First optimized pass: `362,162.26 ms` (`2.03x`).
- Final optimized passes: `137,230.39 ms` under load, a best observed
  `79,007.34 ms`, and `105,156.91 ms` in the final post-`bisect` publication
  rerun (`5.36x` conservative, `9.31x` best observed, `6.99x` final rerun).
- The final calculation payload is exactly equal to both the first optimized
  output and the golden baseline after removing runtime timings. The only
  metadata difference from the old baseline is `actualFrom`: the isolated
  source builds the partial first bucket at `04:44:30` from raw rows beginning
  at `04:44:40`; no earlier raw data enters that bucket.

## Range contract

The bridge filters raw rows to `[from, to + timeframe)` before aggregation.
Main-candle indexes start at zero and every engine sees only that virtual file.
A selected range can legitimately differ from the same clock window in a
longer run because prior state is intentionally absent. A six-hour regression
proves that selecting a range from the full JSON is byte-equivalent to running
the bridge on a physical JSON file containing only those selected raw rows.

## Optimizations

### Bridge

- Eliminated duplicate Reaction detection and reused the geometry result for
  serialization and downstream modules.
- Kept one-pass raw normalization for one-second and main-timeframe buckets.
- Retained `orjson`, cached epoch conversions, and fast display-time formatting.

### Reaction

- Shares timestamp indexes for identical immutable candle sequences.
- Shares lazy reflected candle views used by Bearish geometry.

### A and S

- Caches repeated Reaction confirmation-time lookups within each detector.

### E

- Shares the sorted lower-candle list, timestamp index, and strict-cross index
  between E detector instances in one bridge process.
- Caches order-candidate searches by start, deadline, and audit mode. This
  reduced the four dominant E phases from about `257.7 s` to `62.7 s` while
  preserving every returned object.

## Verification artifacts

- `tmp/baseline-profile-output.json`
- `tmp/baseline-full.prof`
- `tmp/optimized-full-v1.json`
- `tmp/optimized-full-v2.json`

Generated benchmark files are diagnostic evidence only. Maintained code,
algorithm documents, and tests remain authoritative. Production calculation
code contains no timestamp, price, filename, CSV, or output hardcoding.
