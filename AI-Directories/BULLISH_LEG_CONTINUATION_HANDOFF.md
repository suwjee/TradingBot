# Bullish leg continuation handoff

This handoff is for the next AI working in `D:\My-Projects\TradingBot`. It records the
user's latest bullish lesson and the exact state of the current implementation.
All persisted records must remain English. Conversation may remain Persian.
The verified rule `docs/algorithms/BULLISH_LEG_RULE_VERIFIED.md` and amendment
`docs/algorithms/BULLISH_LEG_RULE_AMENDMENT_20260907.md` supersede stale
working notes.

## Scope and authority

- Analytical timeframe: 30 seconds.
- Timezone: `Asia/Tehran`.
- Source:
  `market-data/raw/RAW FOREXCOM_XAUUSD 1S FROM 2026-08-18 04-44-40 TO 2026-09-05 00-29-39.json`.
- Acceptance range: file start through the complete candle
  `2026-08-19 05:54:00`.
- Range semantics: every request calculates from the source start through the
  complete candle ending at `to + timeframe`; rows before `from` are causal
  warm-up context, and `[from, to]` is applied only to the serialized payload.
  A shared output window must be invariant to its viewport start.
- User corrections in the latest message outrank earlier examples.
- Implement bullish behavior only. Do not write or implement the bearish
  mirror until the user explicitly approves it.
- Never use timestamps, OHLC fingerprints, source-name branches, review CSV
  values, or output overrides as production rules.
- Reaction, Blue Line, A, S, E, and StopAll remain the calculation owners.
  The leg layer supplies context, ownership, validity, and lineage.

## Confirmed user rules

- A bullish leg contains at least one confirmed bullish Reaction. After its
  breakout, the lowest Low from the inclusive First Red backward identifies
  the leg head. A head does not need an A/S/E label.
- In the first schematic, when an internal S and its larger E head stop
  together, the larger E remains dominant. If a new leg head stops before an
  internal S forms, abandon that S wait and resume the larger E sequence.
- `2026-08-18 05:41:30`, Low `4398.630`, is a leg head. Its A is invalid;
  the previous S-owned E space remains active.
- `2026-08-18 06:01:30` is invalid: it is neither Order_A nor Order_B.
  The user confirms `06:05:30` as Order_B and `06:13:30` as E1 blue. This
  result must be derived generically, not by
  a timestamp exception.
- A=`2026-08-19 01:52:30` is a valid A, not an order. Its exact stop opens
  the ordinary bearish Reaction order search. The order is First Green
  `02:07:30`, Stop source `02:05:30`, Stop `4336.570`, strict stop
  `02:35:44`. S blue is `02:10:30`; E1 blue is `02:30:00` and carries this
  live order. Do not replace this with a consecutive-red maximum-High rule.
- `2026-08-18 22:55:00` S blue is invalid. The user corrected the earlier
  missing-output verdict; keep the CSV row `False`.

## Current implementation already present

- `indicator/Modules/4_S-zones/app/s_detector.py` is version `4.1.2`. It accepts an optional
  bullish-only resolver for the exact same-candle continuation after an A
  stop. It invokes ordinary Reaction discovery in the continuation's own
  pre-First context and does not borrow the predecessor's mode-B Stop.
- `reaction_bridge.py` supplies that resolver only for bullish S detection.
- `5_E-zones/app/e_detector.py` is version `6.1.2`. For bullish inherited
  live orders, order eligibility is bounded by the inherited order's strict
  stop. A superseded Blue-E branch cannot seed a later audit or carried order
  after a later confirmed Red S owns the lifecycle.
- The bridge's final bullish S visibility compares a candidate's own exact
  source event, so a larger head that stops after A but before S decision can
  invalidate the S candidate. This makes S `07:30:00` invalid while preserving
  the user-corrected `22:55:00` invalid result.
- New focused tests exist in:
  `indicator/tests/test_s_gate_order.py` and
  `indicator/Modules/5_E-zones/tests/test_e_order_deadline.py`.

## Completed continuation work

The Reaction-derived interior-leg guard is implemented and changes only A
`09:36:00` from invalid to valid. It computes the Decimal minimum from the
owner stop through First Red, requires a confirmed Reaction witness, and keeps
the existing owner-consumption step. The exact witness is head `09:01:00`,
Low `4386.165`, First Red `09:03:00`, confirmation `09:03:34`, A price
`4387.670`.

The remaining Order_B ownership was derived from the confirmed head-lifecycle
rule. An invalid bullish leg head with an actual pending S candidate keeps its
internal lifecycle until the head's exact strict stop. Opposite-Reaction Firsts
that open while this head is live cannot own the resumed outer E space. Once
the head stops, the outer owner resumes and the first complete Order_B geometry
after that event is eligible. Heads without a pending S candidate do not close
an otherwise valid order window.

In the reviewed chain, head `05:41:30` remains live through `06:03:58`.
Order First `06:01:30` is therefore invalid; `06:05:30` is the first eligible
Order_B after resumption and E1 blue `06:13:30` carries it. The bridge derives
the blocked First set from invalid head ownership and exact A-stop chronology;
the E engine skips those Firsts only for bullish Order_B selection. No timestamp,
price, fixture, source filename, or output override is used.

## Current acceptance state

Run from `D:\My-Projects\TradingBot`:

```powershell
python -m pytest indicator/tests/test_bullish_leg_review.py -q --tb=no
```

The user confirmed that Order audit `16:38:00` and S blue `23:45:30` are valid
additional calculations. Both are recorded as positive review rows. The CSV is
a minimum required set; general calculations may produce additional outputs.

The latest run after these additions has **136 passed and 0 failed**. All 132
review rows and four exact parent/order assertions pass.

Focused verification already passes:

```powershell
python -m pytest indicator/tests/test_s_gate_order.py `
  indicator/Modules/5_E-zones/tests/test_e_order_deadline.py `
  indicator/Modules/4_S-zones/tests/test_s_ownership.py `
  indicator/Modules/5_E-zones/tests/test_e_dominance.py -q --tb=short
```

The command returned 58 passed after including the two new ownership tests.
Compile the changed Python files before any
report:

```powershell
python -m py_compile `
  indicator/Modules/4_S-zones/app/s_detector.py `
  indicator/Modules/5_E-zones/app/e_detector.py `
  indicator/indicator-settings/backend/reaction_bridge.py
```

The 2026-09-07 publication regression over all maintained Python test files,
excluding backup copies, returned 339 passed, 22 failed, 6 skipped, and 1
strict xfail. The remaining failures are 16 deferred Bearish symmetry E-audit
cases, three legacy StopAll ranges, and three legacy FXCM E/order regressions.
The Blue Line module separately returned 12 passed and two known reset-window
failures. Do not change expectations or implement the unapproved Bearish mirror
to make these unrelated suites green.

Run the bridge only with the exact source/range when inspecting payloads:

```powershell
python indicator/indicator-settings/backend/reaction_bridge.py `
  --engine indicator/Modules/1_reaction-detector/app/Reaction-detection-new.py `
  --blue-engine indicator/Modules/2_blue-line/app/blue_line.py `
  --a-engine indicator/Modules/3_A-zone/app/a_detector.py `
  --s-engine indicator/Modules/4_S-zones/app/s_detector.py `
  --e-engine indicator/Modules/5_E-zones/app/e_detector.py `
  --stopall-engine indicator/Modules/6_StopAll/app/stopall_detector.py `
  --data "market-data/raw/RAW FOREXCOM_XAUUSD 1S FROM 2026-08-18 04-44-40 TO 2026-09-05 00-29-39.json" `
  --timeframe 30 --direction bullish `
  --from-time 1787015680 --to-time 1787106240
```

Use the acceptance fixture's `epoch()` helper if epoch values need to be
recomputed; do not hand-edit the command's output. The bridge emits progress
lines, so parse the final JSON exactly as the existing test does.

## Maintenance checks

- Verify all previous passing rows remain passing after every patch.
- Verify bearish payloads are unchanged by the bullish changes.
- Run `git diff --check` and inspect `git status --short` before publication.
- Do not claim completion while any confirmed review row or parent/order
  assertion fails.
- If a rule remains ambiguous, stop at the exact example question instead of
  inventing a timestamp-specific implementation.
