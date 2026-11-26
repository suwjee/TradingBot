# Phase 07 — Checkpoint 161 / W1 B08-24

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `5b8fc97ab572038ab288cb9d51bb47b22efa3b16`. **Local partition PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** P44–P46, lines 800–840; 25 original rows, 3 supplemental items, 2 resolved local clarification groups. Primary cumulative 670/670.

[Site evidence](Semantic_Closure_B08_24.json), [immutable crosswalk](Decision_Site_Crosswalk_02.json), [context ledger](Semantic_Context_Primary.json), [Primary](../../Algorithms/V3/12_Primary_Structures.md#L228), [state model](../../Algorithms/V3/State_Machines/06_Primary_Reversal.md). Pinned blob `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`; exact IDs, spans, procedures and operations matched.

## Live continuation, dirty main-candle rewind and commit order

- B08-24-S01: Direction membership exactly bearish/bullish; invalid value raises before detector setup. Raise ValueError for invalid direction. Select bullish detector only exact bullish, else bearish after validation. Allocate fresh run with no previous state. Calculate initial result using original inputs and stored run. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L800-L815).
- B08-24-S02: Reject timeframe unequal to original before validating dirty timestamp. Raise ValueError for changed analysis timeframe. Require datetime instance, subclasses accepted; negate predicate. Raise TypeError for invalid dirty event. Visit old and new main timestamp sequences in that order. Containing candidate index is upper bound of original dirty event minus1, for each sequence independently. Only nonnegative index and dirty event strictly before main start+original timeframe rewind; equality at end excluded; addition is timestamp duration. Frontier min with containing main start; both histories may contribute. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L816-L833).
- B08-24-S03: Create candidate run with current retained run and computed frontier. Detect with new inputs; only successful return permits clearing previous and replacing wrapper state. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L834-L840).

## Findings

- B08-24-F01: The constructor validates the direction before allocating the run, and keeps original timeframe/timestamp references. The result property returns the stored object itself. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L220).
- B08-24-F02: Timeframe rejection precedes datetime validation. Old and new timestamp searches both use the original dirty event, not progressively rewound frontier. Rewind only inside the half-open main interval; at exact end that interval is not eligible. After successful detection, sever previous then publish run/result then new times; callback side effects are not transactionally rolled back if detection fails. [Active contract](../../Algorithms/V3/12_Primary_Structures.md#L228).

W2/W3/W4 open. No RAW payload read, runtime, benchmark or production change.
