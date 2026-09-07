# Project map

| Work | Start here | Authority |
|---|---|---|
| Browser chart, drawings, export, UI | `lightweight-charts/` | `lightweight-charts/src/`, focused Node tests |
| Visual language, accessibility, responsive behavior | `UI_UX_DESIGN_RULES.md` | `lightweight-charts/src/styles/tokens.css` and maintained UI |
| API, candle inventory, cache, bridge | `indicator/indicator-settings/backend/reaction_bridge.py` | bridge source and bridge tests |
| Reaction and Reset | `indicator/Modules/1_reaction-detector/` | maintained engine, algorithm doc, regression tests |
| Blue Line | `indicator/Modules/2_blue-line/` | engine and focused tests |
| A | `indicator/Modules/3_A-zone/` | engine and focused tests |
| S | `indicator/Modules/4_S-zones/` | engine and focused tests |
| E / order lifecycle | `indicator/Modules/5_E-zones/` | engine and focused tests |
| StopAll | `indicator/Modules/6_StopAll/` | engine and focused tests |
| Candle datasets | `market-data/raw/` and `DATA_POLICY.md` | source file plus validation result |
| Performance | `SPEED_CODING_RULES.md` | byte-equivalent output verification |

For cross-module behavior, begin with
`docs/algorithms/BULLISH_INDICATOR_ALGORITHM.md`, then verify every claim in
the current executable path and focused tests.
