# Matching Behavior Leg

## 4. MBL formation, break and display horizon

1. At cycle activation, measure the interval of whole main candles from the second matching behavior's source through the reference-break candle, including both endpoints. Take maximum High in bullish and minimum Low in bearish. If the winning extreme occurs on more than one candle, use the earliest candle. Freeze the time, level, reference, second source, and exact activation event.
2. This is initially a candidate leg. A leg becomes part of public output once its own first directional primary confirms within the requested end horizon. An opposite point, another cycle's primary, or a future confirmation does not publish the leg.
3. Starting strictly after activation, track the first strict MBL break using RAW. Keep the first exact event and its main index. An MBL can already be broken by the time it becomes public. A local primary reset or further matching leaves the frozen MBL in that cycle unchanged.
4. Public `stopIndex`, `stopTime` and `stopEventTime` are null until the requested main-candle horizon contains the break. Bridge supplies `capTime` from the actual main candle at source index + 400 when available. When that index does not yet exist, it extrapolates from the last main timestamp by the remaining number of analysis periods. A stopped regime clamps the cap at the reversal boundary. Chart ends the line at the earliest applicable end and does not search for a replacement price crossing.
5. Several formed legs may coexist. IDs use direction plus the reference and second source indexes. First-cycle compatibility access through the internal aggregate `.mbl` is not a substitute for the formed-leg collection.
