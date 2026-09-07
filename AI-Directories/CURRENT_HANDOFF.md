# Current handoff

## Architecture

`lightweight-charts/` is the browser workstation and dev-server boundary.
`indicator/indicator-settings/backend/reaction_bridge.py` validates inputs,
keeps causal raw context through `to + timeframe`, aggregates candles,
orchestrates the Python pipeline, and serializes only the selected presentation
range. History before `from` is calculation warm-up and must not be discarded.
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

The bridge must produce the same common-window result when only `from-time`
changes. `to-time + timeframe` is the exclusive raw-data boundary; `[from, to]`
is applied after the full Reaction -> Blue -> A -> S -> E -> StopAll fixed
point, during serialization and visibility filtering.

The public indicator payload contains accepted calculations only. Rejected A/S
candidates may remain in internal lifecycle state when later ownership depends
on them, but they must not be serialized, counted, listed, or drawn. The chart
also removes any legacy `calculationValid=false` objects defensively.

Read `AI-Directories/BULLISH_LEG_CONTINUATION_HANDOFF.md` and
`docs/algorithms/BULLISH_LEG_RULE_AMENDMENT_20260907.md` for the completed
live-invalid-head Order_B ownership rule and current verification evidence.

## Publication state

The current TradingBot repository is the final project authority. Published
commits must keep source, tests, AI routing, algorithm documents, launcher
behavior, and the paired Obsidian knowledge records synchronized.

## Graphify

`graphify-out/` has a project knowledge graph. It may guide discovery but is
not a calculation input or a substitute for maintained source and tests.

## Publication verification on 2026-09-07

The exact reviewed-range suite returns 136 passed and the causal viewport-start
invariance test also passes. The chart suite returns 99
passed and the Vite production build succeeds. The complete maintained Python
test inventory, excluding backup copies, returns 339 passed, 22 failed, 6
skipped, and 1 strict xfail. The 22 failures are the existing unresolved
non-acceptance groups: 16 deferred Bearish symmetry E-audit cases, three legacy
StopAll ranges, and three legacy FXCM E/order regressions. The Blue Line module
returns 12 passed and its two separately documented reset-window cases fail.
These failures do not change the verified Bullish review result and must not be
silenced by changing expectations without a confirmed rule.
