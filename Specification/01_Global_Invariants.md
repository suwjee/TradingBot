# Global invariants

Main[i] is the selected calculation candle; Raw[j] is the original lower-timeframe observation. The name seconds does not imply one-second resolution. Within one five-second OHLC row, the order of highs and lows cannot be inferred. Apply the specified race rule per path. Use Decimal, never introduce rounding, and preserve the order of arithmetic. Candle color GREEN iff close >= open; doji is GREEN in native market coordinates. Reflection can alter an internal role but not public color semantics.

| Concept | Bullish | Bearish |
|---|---|---|
| Stop-side extreme | Low | High |
| Opposite extreme | High | Low |
| First reaction | RED | GREEN |
| Context | GREEN | RED |
| Strict stop | Low < level | High > level |
| Confirmation | High > BoxTop | Low < BoxBottom |
| Better extreme | min | max |
| Primary | PL | PH |
| Secondary | PH | PL |
| MBL | max High | min Low |

Source is the geometric owner; confirmation is the evidence of formation; decision is the exact event that commits a behavior; stop event is the first eligible strict crossing. Main-candle time and precise RAW time are not interchangeable. Semantic price/source_extreme is not necessarily the drawn price. calculation_valid and behavior_internal are separate. An equality is not a strict crossing. Reaction simultaneous reset/break favors reset; S exact order-stop/candidate tie has no decision; E exact Order-stop tie favors later First. A/E often select earliest equal extrema; several S paths select latest. Do not apply a global tie-break. Blue/Red family and Mode A/B are not directions.

## 3. Global invariants

1. **Decimal:** JSON floating-number lexemes are parsed directly with `parse_float=Decimal`, then normalized with `Decimal(str(value))`; no binary-float decision is authoritative.
2. **Candle color:** `GREEN` iff `close >= open`; `RED` iff `close < open`; a Doji is always GREEN in both market directions.
3. **Strict crossing:** equality never satisfies a strict price crossing. For Bullish behavior-space stops the directional primitive is `Low < Level`; the Bearish mirror uses the opposite strict comparator.
4. **Chronology / calculation timeframe:** trading eligibility is evaluated on the configured calculation timeframe unless the active rule explicitly requires intrabar ordering. Lower-timeframe RAW is authoritative only for those explicit within-candle chronology questions and exact event provenance; it must not by itself move a main-timeframe eligibility gate to a later calculation candle. Time is never mirrored.
5. **Reaction identity:** physical Reaction/Order identity is `(FirstIndex, BreakIndex)`. Identity, provenance structure, stable ordering, lifecycle priority, behavior-family names and public schemas are direction-invariant.
6. **Determinism:** candidate ordering and tie-breaking are explicit. Equal main-candle extremes keep the earliest source unless the owning rule explicitly requests last-on-equality (S Type-3/Type-4 candidate construction).
7. **Canonical mirror:** the Bearish Reaction path mechanically reflects the shared Bullish coordinate state machine. Independently inspect explicit directional branches and policies. Reflect prices/roles; preserve time, state ownership, canonical identity, cause structure and lifecycle families.
8. **Calculation vs presentation:** internal/historical objects may remain necessary for later calculation even when they are not independently visible. Final filters cannot rewrite upstream truth.
