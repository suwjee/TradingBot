# CP323 — W2 Reaction/Reset and Blue/A owner reconciliation

Pinned production baseline: `c99b4c957e932d9ee70c492ca03ce80711447fc1`. Source-only, no execution. This is a bounded cross-owner register, not a Phase 07 acceptance statement.

## Exact cross-owner qualifications

### Q1

BL09 emits at most one Blue per native Reaction: Scale sets hasBlue and counter=0, suppressing every same-group Reset; first eligible Reset likewise zeroes counter and suppresses all remaining group members. Native ordinal strictly increases between emissions. Thus A01's stable sort by (reaction_number,source_time,kind) preserves native Blue order, including invalid/internal; S01's copied list aligns with A ordinal in both Bridge paths. Conditional external reordered/synthetic inputs are not proven. The complete native chain uses full Blue for A/S before display filtering; caller of optional live protocol must preserve same sequence and ordinal contract.

### Q2

A18 progress: no-match breaks, no-source/trigger skips; after successful match under coherent native chronology, formation events belong to their stated main intervals and A13 trigger is at/after both prior and current formation (inheritance requires previous earlier; no-inheritance route either previous stop earlier or trigger at/after both stops). A15 returns confirmation>=trigger, and A14 scan is bounded to matched Break main or its open fallback. Under ordered native main grid and coherent formation/stop mapping, previous formation index<=matched Break, so skip-through-cycle advances at least current previous position; bridge-reuse also increments. No unconditional index increment is implemented; malformed/external chronology or noncoherent custom timestamps remain conditional, not asserted runtime termination.

### Q3

CH13 wording 'Break-open confirmation' means scan START at Break open (false flag), not necessarily confirmation at open; actual strict lower crossing may be later. CH86 later lower rows excluded only when lower evidence exists; A08 empty-lower fallback includes complete endpoint main OHLC. Public Reaction clone First==Break corner is documented; no invented intrabar proof. Native analysis start, published clone start, A false-flag and default confirmation are separate.

### Q4

Blue internal flag can be mutated in place after calculation and is monotonic for a retained line object; LiveBlue result shares objects and rewind depends on caller first_changed including removed old resets and changes to prior behavior metadata. LiveBehavior can revise previous inner flags if opposite geometry changes. Optional live protocol implementation is not established by public entry; no guarantee of composed cache equivalence beyond explicit guards.

## Traceability

- [Prior 29 transition records](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP323_W2_Reaction_Blue_A_Partial.json)
- [Supplemental transition and edge register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP323_W2_Reaction_Blue_A_Reconciliation.json)
- [Named symbol census](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP323_W2_Transition_Symbol_Census.json)
- [CP323 acceptance record](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP323_Completion.json)
- [Source: Reaction](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py), [Blue](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py), [A](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py), [S](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py), [Bridge](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py).

Historical CH clauses and original CP323 partial evidence remain unchanged. No RAW payload or production source modified or executed.
