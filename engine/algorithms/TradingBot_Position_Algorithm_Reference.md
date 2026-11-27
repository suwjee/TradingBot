---
title: TradingBot Position Algorithm Reference
document_role: reference
lifecycle: maintained
owner: engine/algorithms
scope:
  - buy-and-sell-position-setups
  - position-public-output
  - foundation-liquidity
created_at: 2026-11-26T23:47:55+03:30
last_modified_at: 2026-11-27T05:51:35+03:30
---

# TradingBot position algorithm

The Engine derives chart position setups from finalized indicator behavior, direction, and closed market candles. Bullish regimes are eligible for Buy setups. Bearish regimes are eligible for Sell setups. Use the actual regime at the event being evaluated, including in a calculation requested for one direction. Each reversal starts a fresh scope for the new direction. Type 1, Type 2, and Type 3 are independent. One event can qualify for more than one family, and a position or stop in one family leaves the other families' progress intact.

The approved Notion teaching page `position` (`42496a3f-e412-8081-b25e-cb8b0ffcfe8c`) and the user's subsequent clarifications define these rules. The [Primary Structures and True/False reference](TradingBot_Primary_Structures_and_True_False_Algorithm_Reference.md) defines the underlying regime boundaries, accepted PL and PH points, and published T/F labels. The [project authority model](../../AGENTS.md) governs any discrepancy between these rules and executable behavior. The position calculation consumes finalized indicator results to publish chart schematics.

## Direction, entry, and price boundaries

The **anchor** supplies the stop price. The **trigger** supplies the confirmation candle. For an S-triggered setup, the trigger can be either S Blue or S Red, regardless of the S's own T/F label. A Foundation anchor is any accepted group-one S or E. Wherever the rules require a T or F, read the current published indicator label for the anchor at that calculation horizon, including when replaying history.

| Rule | Bullish Buy | Bearish Sell |
| --- | --- | --- |
| Directional primary points | PL-1, PL-2, PL-3 | PH-1, PH-2, PH-3 |
| Stop price from the anchor source candle | Low | High |
| Inclusive S geometry for Type 1 and Type 2 | S source Low ≥ anchor Low | S source High ≤ anchor High |
| Strict S geometry for Type 3.1 | S source Low > PL-1 Low | S source High < PH-1 High |
| Strict stop in RAW | Low < stop price | High > stop price |

Use the following event times for separate purposes.

1. **Source formation.** Use the accepted source candle and the finest authoritative RAW chronology to determine when its source extreme formed. Source order governs window assignment and StopAll ownership. Use exact formation events to determine whether an anchor preceded S, whether an S formed before a strict crossing, and whether a replacement F formed at or after its prerequisite stop. A bucket timestamp identifies the source candle and can precede the exact event inside it.
2. **Confirmation.** The anchor must have confirmed by the trigger's confirmation. Both confirmation candles must be closed at entry. The entry price is the Close of the trigger's closed analysis-timeframe confirmation candle. The entry time identifies that bucket. S confirmation supplies the entry for Types 1.1, 1.2, 2.1, 2.2, and 3.1. Primary confirmation supplies the entry for Types 3.2 and 3.3. Select the first eligible S by exact confirmation time, with source order as the tie-break.
3. **Strict stop.** Use the first strict adverse crossing in the applicable chronology. Touching the stop price leaves the setup unstopped. An anchor whose level strictly crosses at or before the prospective S formation is ineligible for that S. If S forms first and the level strictly crosses before the confirmation candle closes, publish the setup at that close and record the actual earlier stop. That crossing can unlock the corresponding `.2` under the same window or stage rules. An F formation at the exact prerequisite stop event meets the start boundary for the `.2` search. A strict stop after entry also retains the drawing.

The 4R extension has no effect on selection, state transitions, or subsequent stop eligibility. A target touch leaves the setup eligible to register a later strict stop.

## Setup identifiers

| Family | Buy type | Buy algorithm | Sell type | Sell algorithm |
| --- | --- | --- | --- | --- |
| Foundation T | `1.1B` | `Buy_Foundation_T` | `1.1S` | `Sell_Foundation_T` |
| Foundation F | `1.2B` | `Buy_Foundation_F` | `1.2S` | `Sell_Foundation_F` |
| StopAll T | `2.1B` | `Buy_StopAll_T` | `2.1S` | `Sell_StopAll_T` |
| StopAll F | `2.2B` | `Buy_StopAll_F` | `2.2S` | `Sell_StopAll_F` |
| First directional primary | `3.1B` | `Buy_PL1` | `3.1S` | `Sell_PH1` |
| Second directional primary | `3.2B` | `Buy_PL2` | `3.2S` | `Sell_PH2` |
| Third directional primary | `3.3B` | `Buy_PL3` | `3.3S` | `Sell_PH3` |

## Type 1 — Foundation T followed by Foundation F

A Type 1 window starts at the beginning of the calculation, at a reversal into the applicable regime, after each confirmed StopAll, and after each confirmed directional primary (PL in bullish, PH in bearish). Each new window starts with empty Type 1 progress and Foundation rank history.

1. Find the first eligible S in the window that follows a Foundation **T** and meets the inclusive geometry and chronology requirements. Use the T source as the stop anchor and the S confirmation as the entry trigger. If the same S qualifies for several T anchors, take the earliest eligible anchor by source order. Publish at most one `1.1` in that window.
2. A strict stop of that `1.1` in the same window opens the `1.2` search. Evaluate Foundation **F** candidates formed at or after that exact stop event. An eligible F must strictly exceed **every earlier Foundation rank in that window**, including earlier behavior before the `1.1` stop. Earlier Foundation behavior counts toward the maximum regardless of verdict or whether it qualified as an entry anchor. The candidate must have a later S that meets the inclusive geometry and chronology requirements. Use the F source as the stop anchor and the S confirmation as the entry trigger.
3. Apply the same S confirmation ordering and anchor source tie-break to `1.2`. Publish at most one `1.2` in the window. Further Foundation behavior and stops cannot restart the sequence. The next Type 1 boundary opens a fresh opportunity.

Foundation rank is `S Blue < E Blue < S Red < E Red`. Within each E color, the larger E number ranks higher. Equal rank is insufficient for `1.2`. For example, if the current window already contains E4 Red, E3 Red F and E4 Red F are ineligible. E5 Red F is higher and can qualify if it forms at or after the prior stop, survives until S formation, and has a later eligible S. A higher-ranked candidate whose own S never qualifies still counts as earlier Foundation behavior when evaluating a subsequent F.

## Type 2 — StopAll T followed by StopAll F

A Type 2 stage starts at calculation start, at a reversal into the applicable regime, or after a confirmed directional primary. Successive StopAll events delimit S source ownership within the stage. The stage's attempt counts carry across those StopAll events.

1. Associate an S with the StopAll whose source precedes the S's source before the next StopAll source. Ownership follows source chronology even if S confirms later than a newer StopAll. Each owner's own verdict, validity, confirmation, and S geometry determine its eligibility. A StopAll without an eligible S cannot supply a setup or lend an S from a later owner's interval.
2. The first qualifying StopAll **T** and its owned eligible S produce `2.1`. Use the StopAll source as the stop anchor and the S confirmation as the entry trigger. The stage allows one `2.1`.
3. After a strict stop of that `2.1` in the same stage, find the first qualifying StopAll **F** formed at or after the stop. Its owned S must pass the same inclusive geometry and chronology requirements. The F StopAll supplies the stop and its S supplies the entry for `2.2`. The stage allows one `2.2`. Further T or F StopAll events cannot restart the sequence before the next stage.

For example, a T StopAll without an eligible S leaves `2.1` available. If the next StopAll is F, the search remains open for a later qualified T. Once a qualifying T and its S yield `2.1` and that setup strictly stops, an F StopAll without an eligible S leaves `2.2` available. A later T cannot yield another `2.1` in that stage. A subsequent eligible F and its owned S can yield `2.2`.

## Type 3 — Directional primary sequence

Track the accepted sequence of directional primaries in each actual regime. A reversal starts fresh Type 3 progress. Buy follows PL-1, PL-2, and PL-3. Sell follows PH-1, PH-2, and PH-3. Type 3 uses the primary sequence independently of the Type 1 and Type 2 resets caused by those same primary events.

| Type | Required state in the same regime | Trigger and stop |
| --- | --- | --- |
| `3.1B` / `3.1S` | The first directional primary has confirmed. A qualifying S has strict favorable source geometry and a source strictly after PL-1 or PH-1 and before the next directional primary source, if present. | Enter on the S confirmation Close before the next primary confirmation closes. Use PL-1 Low or PH-1 High as the stop. |
| `3.2B` / `3.2S` | The first and second directional primaries have formed in order. By the second confirmation close, `3.1` was absent or has strictly stopped. | Enter on the PL-2 or PH-2 confirmation Close. Use that primary's source extreme as the stop. |
| `3.3B` / `3.3S` | The first, second, and third directional primaries have formed in order. `3.1` was never taken. By the third confirmation close, `3.2` was absent or has strictly stopped. | Enter on the PL-3 or PH-3 confirmation Close. Use that primary's source extreme as the stop. |

Types 3.2 and 3.3 need no S. If no S qualified for `3.1`, the next decision is at the second primary confirmation close. Taking `3.1` makes `3.3` ineligible for the rest of that regime. A subsequent strict stop can make `3.2` eligible. A still-unstopped `3.2` blocks `3.3`.

## Engine output and chart behavior

The Engine publishes finalized setup rows in `positions` for Chart rendering. A row has these fields.

| Field | Meaning |
| --- | --- |
| `id` | Stable setup identity for the same type, anchor, and trigger across equivalent calculations. |
| `type`, `algorithm`, `side` | Compact type and algorithm identifier from the table above. Side is `buy` or `sell`. |
| `anchorSourceTime`, `triggerSourceTime` | Accepted anchor and trigger source-candle timestamps. A primary-only trigger can identify the same source as its anchor. |
| `entryTime` | Timestamp of the closed analysis-timeframe confirmation bucket. |
| `entryPrice`, `stopPrice`, `targetPrice` | Decimal strings for the entry Close, stop level, and initial visual 4R level. |
| `stopEventTime` | Optional exact timestamp of the recognized strict crossing. |
| `preEntryStop` | Present as `true` for a recognized strict stop before the trigger's confirmation close. |

The initial visual risk distance is `R = abs(entryPrice - stopPrice)`. Plot the target at `entryPrice + 4R` for Buy and `entryPrice - 4R` for Sell. Plot the compact type below the Buy stop region and above the Sell stop region. The position settings offer independent per-type visibility controls. Chart users can edit, move, or delete individual objects as presentation changes. Engine setup selection, prices, and stop chronology continue to come from the calculation. Setup rows and chart objects have no broker-order side effects.

## Foundation liquidity

Evaluate liquidity from finalized group-one S/E and the same source ownership used for T/F. Start fresh candidate and repetition history at the calculation start, every regime reversal, every published StopAll, and every directional primary source (PL in bullish, PH in bearish). Continue checking already formed levels against later RAW, including after a reset or reversal.

| Rule | Bullish | Bearish |
| --- | --- | --- |
| Level of a confirmed F | Source Low | Source High |
| Favorable RAW movement after F forms | High > level | Low < level |
| Strict direct collection | Low < level | High > level |
| Favorable later S/E source | Source Low > F Low | Source High < F High |

The first favorable RAW movement establishes ordinary liquidity if it precedes the first strict direct collection. Movement can stay inside the F candle's full range. Use Decimal prices and the finest available RAW chronology. Equality at the level leaves it active. When both directions first cross in the same RAW candle, require an earlier favorable event to establish ordinary liquidity.

Publish an ordinary line after the anchor and an eligible later S/E have confirmed on closed candles. The later behavior may have either verdict. Its source must form inside the same window, in favorable geometry and strictly before any direct collection of the F level. Draw from the F source candle. A level can form and be collected without ever qualifying for a line.

Two or more F behaviors with the same group-one family, color and E number form a repetition group within the same window. Smaller intervening S/E and same-rank T leave the group open. A strictly larger S/E ends the smaller-rank group. When a matching F confirms, it qualifies for a line without a subsequent S/E. The first member also qualifies when the repetition is confirmed. A strict crossing of the newest member at the time collects all older, still-active members of the group. A member can also be collected directly at its own level. Preserve the earliest collection event.

The directional `liquidity` rows publish `sourceTime`, Decimal-string `price`, `movementTime`, `visibleFrom`, `repeatGroupSourceTime`, `directSweepTime`, `collectedTime`, and `lineEndTime`. Nullable fields indicate unavailable movement, eligibility, group, collection or drawing geometry. The line ends at its own first strict crossing candle or at 1,500 analysis candles after its source, whichever comes first. Project the remainder of the cap when the calculation has fewer future candles. The cap and collection through a similar F affect display geometry and validity independently.

The Chart paints eligible lines at 0.5 CSS pixels in `#b8b8b8` with a centered `$$$` when the line has room. The center text follows the source S/E label size, which defaults to 10 CSS pixels. The Liquidity configuration provides Active, Collected, and Repeated F switches. The status switch applies to repeated lines as well. Each eligible line has a stable Chart object identity. Chart edits, movement, resizing, and deletion affect its presentation while the published Engine liquidity record remains available. Position entry families continue to use the rules above.

## Illustrative market chronology

The examples below use XAUUSD five-second RAW with 30-second analysis candles. Times are Tehran local. The same rules apply to other inputs.

1. In the bearish regime on 2026-11-06, E2 Red T sourced at 09:54:30 supplies the `1.1S` stop of `4052.12`. S Blue sourced at 10:49:30 confirms in the 10:53:00 bucket, whose Close is `4051.315`. The visual 4R level of `4048.095` is touched at 10:55:05. The first strict stop is at 11:22:30 and opens the `1.2S` search in the active window.
2. The subsequent E3 Red candidate sourced at 12:20:30 has High `4074.935`. RAW crosses that High at 12:27:10 before the candidate's prospective S forms, making this anchor ineligible.
3. E7 Red F on 2026-11-09 at 23:58:30 supplies a later qualifying `1.2S` anchor at `4148.655`. Its S Red is sourced on 2026-11-10 at 00:27:00 and confirms in the 00:56:00 bucket with entry Close `4137.47`.

4. On 2026-11-17 a T StopAll at 19:13:00 with S Red at 19:45:00 yields `2.1S` on the 19:50:30 confirmation bucket. The same S Red is a Foundation T anchor. A later S Red sourced at 22:47:00 yields `1.1S` on the 22:55:30 confirmation bucket. The earlier `2.1S` remains unstopped at the second entry.
