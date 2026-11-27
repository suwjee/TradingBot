---
title: TradingBot Bullish Buy Position Algorithm Reference
document_role: reference
lifecycle: historical
owner: engine/algorithms
created_at: 2026-11-26T16:04:16+03:30
last_modified_at: 2026-11-26T23:50:15+03:30
---

# Bullish Buy position algorithm

> Historical record of the earlier position algorithm. The [current combined position reference](TradingBot_Position_Algorithm_Reference.md) governs Buy and Sell.

The Engine derives these positions from the finalized bullish indicator stream and the supplied market candles. Read the [primary structures and T/F companion](TradingBot_Primary_Structures_and_True_False_Algorithm_Reference.md) for published StopAll verdicts, source and decision fields, and regime boundaries. Buy and Sell share the same position calculation. The directional source extreme mirrors Low to High. Source ownership, T/F, and event order are invariant.

| Chart type | Algorithm identifier | Entry trigger | Stop |
| --- | --- | --- | --- |
| Type-1B | `Bullish_Buy_PL1` | First eligible S Blue or S Red after confirmed PL-1 | Low of PL-1 |
| Type-2B | `Bullish_Buy_PL2` | Confirmation of PL-2 | Low of PL-2 |
| Type-3B | `Bullish_Buy_StopAll-T` | First eligible confirmed S belonging to a StopAll whose published verdict is T | Low of that StopAll |
| Type-4B | `Bullish_Buy_StopAll-F` | First eligible confirmed S belonging to a StopAll whose published verdict is F, after a qualifying Type-3 stop | Low of that StopAll |

Entries use the Close of the closed confirmation candle in the analysis timeframe. Use exact decisions and finest available RAW chronology for event ordering. A strict stop is a Low < the stop level. Equality is insufficient. StopAll source order associates an S with its owner even when the S confirms after a newer StopAll. Within the associated candidates, the first eligible S is selected in exact confirmation order. For stop eligibility, use the first available RAW event at the accepted source extreme rather than the analysis bucket start. If one S independently satisfies two types, both entries may be displayed.

Each confirmed PL starts a fresh position calculation window. A change of trend also ends the old window. The stop of Type-3 opens one Type-4 opportunity in the same window after the eligible S has confirmed. The F StopAll supplying Type-4 forms after the qualifying strict stop. After a Type-4 entry, another Type-4 requires a fresh Type-3 stop. The Type-3 prerequisite can also occur when an eligible S forms while its T StopAll is active, its StopAll level strictly crosses, and the S confirms subsequently. In that case Type-3 qualifies internally for Type-4 and no Type-3 row is published for drawing. A stop after entry leaves an existing drawing visible.

For segments with a drawable entry, the Engine publishes `positions` on the directional segment and aggregates those rows when a direction has multiple segments. Each row contains `id`, `type`, `algorithm`, `side`, `anchorSourceTime`, `triggerSourceTime`, `entryTime`, `entryPrice` and `stopPrice`. Engine prices remain Decimal strings at the boundary. Chart derives the visual four-risk-unit extension from entry and stop. The Type label is below the stop region. The extension is presentation only. Drawings do not close when the level is crossed.

See the [Sell position reference](TradingBot_Sell_Position_Algorithm_Reference.md) for the reflected aliases and presentation.
