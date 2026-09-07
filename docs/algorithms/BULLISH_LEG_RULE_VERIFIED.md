---
id: RULE-TRADINGBOT-BULLISH-LEG-20260906
type: trading-rule
status: verified
direction: bullish
authority: user-lesson-2026-09-06-and-corrections-2026-09-07
implementation_status: complete-for-reviewed-range
timezone: Asia/Tehran
---

# Verified bullish leg ownership

This rule governs context, ownership, validity, and lineage between the
existing Reaction, Blue Line, A, S, E, and StopAll calculations. It does not
replace their formation rules. The maintained source and tests in
`D:\My-Projects\TradingBot` are the final authority; older `Prj-1` snapshots
and generated artifacts are not authoritative.

## Scope

- Analytical timeframe: 30 seconds.
- Local timezone: `Asia/Tehran`.
- Reviewed source: `market-data/raw/RAW FOREXCOM_XAUUSD 1S FROM 2026-08-18 04-44-40 TO 2026-09-05 00-29-39.json`.
- Acceptance range: source-file start through the complete
  `2026-08-19 05:54:00` candle.
- Review inventory: `examples/2026-09-06-bullish-leg-user-review.csv`.
- The CSV is a minimum accepted inventory, not a runtime whitelist.
- Production code must not read review timestamps, prices, filenames, verdicts,
  output hashes, or fixture identity to alter a calculation.

## Ownership rules

1. A bullish leg contains at least one confirmed bullish Reaction. After the
   breakout, the minimum Low looking backward from and including First Red
   identifies the leg head. A head does not require an A/S/E label.
2. Exact lower-timeframe chronology owns stop and confirmation order. Price
   crossings are strict and equality does not cross a boundary.
3. When an internal behavior and a larger owner stop in the same transition,
   the larger owner continues the next sequence. Priority is
   `StopAll > E red > S red > E blue > S blue > A`.
4. If a new leg head stops before its pending internal S forms, abandon that S
   wait and resume the larger owner's E sequence.
5. An invalid bullish leg head with an actual pending S candidate owns its
   internal window until the head's exact strict stop. Opposite-Reaction Firsts
   opened while the head is live cannot own the resumed outer E space.
   Selection resumes after the stop. Invalid heads without a pending S
   candidate do not block unrelated orders.
6. A bullish A inside a newly confirmed lower Reaction head remains valid when
   the head precedes the A, `head.Low < A.price`, and the head Reaction confirms
   before the A source. Existing owner consumption remains in force.
7. Bullish inherited-order eligibility ends at that order's strict stop. A
   superseded Blue-E branch cannot seed a later ledger after a confirmed Red S
   owns the lifecycle.
8. Rejected A/S candidates may remain as internal lifecycle evidence. They are
   absent from the public payload and cannot create labels, counts, list
   entries, or order geometry. The browser also filters legacy objects marked
   `calculationValid=false`.

## Confirmed chronology

- Head `2026-08-18 05:41:30`, Low `4398.630`, has an invalid A. It remains
  live through strict stop `06:03:58`, blocks order First `06:01:30`, and then
  permits Order_B `06:05:30`. E1 blue `06:13:30` uses parent S `05:18:30` and
  that Order_B without any timestamp-specific exception.
- A `2026-08-19 01:52:30` opens ordinary bearish order search at its exact
  stop. The order First is `02:07:30`, Stop source is `02:05:30`, Stop is
  `4336.570`, and strict order stop is `02:35:44`. S blue `02:10:30` owns E1
  blue `02:30:00`, which carries the same live order.
- Order audit `2026-08-18 16:38:00` and S blue `23:45:30` are confirmed valid
  additional calculations.
- S blue `2026-08-18 22:55:00` is rejected and absent from public output.

## Verification contract

`indicator/tests/test_bullish_leg_review.py` checks 132 review rows and four
exact order/parent assertions. The verified run returns 136 passing tests.
Every `True` behavior is present, every `False` behavior is absent, and the
`not_computed` S blue at `02:10:30` is present through the general calculation
and verified parent lineage. Output may include other valid calculations when
the maintained general rules produce them.

The live-invalid-head behavior is approved for Bullish only. A Bearish mirror
requires separate explicit user approval.

The 2026-09-07 publication audit also ran every maintained Python test file.
It returned 340 passed, 22 failed, 6 skipped, and 1 strict xfail. The remaining
failures are outside this reviewed acceptance contract: 16 deferred Bearish
symmetry E-audit cases, three legacy StopAll ranges, and three legacy FXCM
E/order regressions. The Blue Line module has two separately recorded legacy
reset-window failures. These results are retained as limits, not hidden by
altering expected output.
