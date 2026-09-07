# Current handoff

## Architecture

`lightweight-charts/` is the browser workstation and dev-server boundary.
`indicator/indicator-settings/backend/reaction_bridge.py` validates inputs,
isolates raw rows to `[from, to + timeframe)`, aggregates and indexes that
selection as an independent virtual source file, orchestrates the Python
pipeline, and serializes its accepted calculations. No candle before `from` or
after the selected final candle participates in module state.
The maintained calculation modules live under `indicator/Modules/` in order:
Reaction, Blue Line, A, S, E, and StopAll. `market-data/raw/` holds selectable
raw candles; `primary-cache/` holds disposable cache data.

## Current authority

`docs/algorithms/BULLISH_INDICATOR_ALGORITHM.md` documents the current
code-derived bullish behavior as of 2026-09-07. It explicitly says that source
in this repository outranks the prior Prj-1 snapshot. The document records
current known test limitations; do not infer unrecorded production correctness.

## Current bullish leg lesson

Read `docs/algorithms/BULLISH_LEG_RULE_VERIFIED.md` and its linked English
example CSV before changing leg ownership. The user's 2026-09-06 lesson and
subsequent corrections outrank conflicting older examples. Existing behavior
discovery must remain unchanged. The reviewed bullish range is implemented and
passes all 132 review rows plus four exact order/parent assertions.
The CSV is not an exhaustive whitelist; additional outputs produced by general
calculation rules are allowed. Do not force historical outputs or infer rules
from timestamps. Bearish changes await separate user approval. All persisted
records must be in English.

Every selected range is a fresh calculation universe. The bridge filters raw
rows before aggregation, gives every module indexes `0..n-1`, and runs the full
Reaction -> Blue -> A -> S -> E -> StopAll fixed point only on those rows.
Changing `from-time` may therefore change valid labels and numbering in a
shared clock window; state outside the selected range is intentionally absent.

The public indicator payload contains accepted calculations only. Rejected A/S
candidates may remain in internal lifecycle state when later ownership depends
on them, but they must not be serialized, counted, listed, or drawn. The chart
also removes any legacy `calculationValid=false` objects defensively.

Read `AI-Directories/BULLISH_LEG_CONTINUATION_HANDOFF.md` and
`docs/algorithms/BULLISH_LEG_RULE_AMENDMENT_20260907.md` for the completed
live-invalid-head Order_B ownership rule and current verification evidence.
Bullish dominant-stop selection is chronological before it is hierarchical:
the latest stop-containing main candle wins, then same-candle module priority
and sequence number resolve ties. In the full-file run this removes the
user-rejected A candidates at `2026-08-20 08:44:00`, `09:08:00`, and
`10:25:30` without timestamp rules. A separately selected range beginning at
`08:08:00` has no earlier owner state, so `08:44:00 A` is valid in that
independent calculation universe.

## Publication state

The current TradingBot repository is the final project authority. Published
commits must keep source, tests, AI routing, algorithm documents, launcher
behavior, and the paired Obsidian knowledge records synchronized.

## Graphify

`graphify-out/` has a project knowledge graph. It may guide discovery but is
not a calculation input or a substitute for maintained source and tests.

## Publication verification on 2026-09-07

The authoritative XAUUSD suite returns 144 passed: 132 CSV rows, four exact
parent/order assertions, two range-isolation regressions, and six focused
range/full-file regressions. A selected six-hour range is byte-equivalent to a
physical source file containing only those raw rows. Per the user's latest
instruction, only
`RAW_FOREXCOM_XAUUSD_1S_FROM_2026_08_18_04_44_40_TO_2026_09_05_00.json`
determines acceptance. FXCM, Bearish, and other datasets are outside this
success criterion and must not be used to alter the canonical XAUUSD result.
