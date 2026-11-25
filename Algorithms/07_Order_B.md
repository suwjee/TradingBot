# OA-B — Reset-leg Order creation

Status: DOCUMENTED / PARTIALLY_VERIFIED package; this module is not independently validated end to end.

Use the latest prior dominant stop and a distinct latest accepted behavior anchor before reset Reaction First. The anchor-to-First interval includes both endpoints. The LL/HH must strictly extend beyond the anchor and its source precede First. After Reset, require strict crossing. An accepted A at or before the crossing main candle expires setup. Opposite canonical Reaction First must be at or after that main candle, and exact confirmation strictly after crossing. Record reset-leg provenance on the same physical identity, not a duplicate.

## Supplemental directional specification

Supplementary material below is the English semantic prose of the existing synchronized references, pinned to 466eb875070f02cd0dbfb105033422bbe2fd8c70. It is not a fresh branch-level proof. Exact production-source appendices are excluded. Historical acceptance examples remain historical.

## 10. Order_B — ACTIVE Bullish reset-leg rule

### 10.1 Eligibility and post-stop owner

Order_B is eligible only after an accepted lifecycle stop (`A`, `S`, `E`, or `StopAll`) selected by the accepted lifecycle owner of the stopped main candle. The stop opens eligibility; it is **not** the geometric LL anchor.

### 10.2 Geometric behavior anchor

For each reset Bullish Reaction, choose the latest accepted behavior source that exists strictly before the Reaction FirstRed candle, independent of current dominance. Valid anchor families are A/S/E/StopAll. When several lifecycle projections share exactly one source candle, lifecycle priority and number resolve only that exact-source tie.

### 10.3 LL construction and extension

Use the closed main-candle range from anchor behavior source through reset Reaction FirstRed, inclusive:

`LL = minimum Low(anchor candle .. reset Reaction FirstRed)`

Only a strict better Low replaces the current source, so equal extremes retain the earliest source. The LL source must be strictly before the reset Reaction FirstRed. It must also extend beyond the anchor itself: the LL must be strictly below the anchor behavior `Low`; equality invalidates the setup.

### 10.4 Reset and calculation-timeframe strict-break candle

The reset Reaction must first produce its canonical Reset. A strict `Low < LL` must occur after that Reset. The **configured calculation candle containing the first valid post-Reset strict crossing** is the Order_B break candle. Equality is not a break.

Lower-timeframe RAW is consulted only when exact intrabar chronology is required: to prove that a crossing in the Reset candle happened after the exact Reset, to retain the exact crossing timestamp as `strict_break_time`, and to prove any same-candle confirmation occurs strictly after that crossing. The exact lower-timeframe timestamp does **not** postpone the Order_B First-candle gate beyond its owning calculation candle.

### 10.5 Accepted-A expiry

Let the next accepted A formation after the reset Reaction First be `A_next`. Compare `A_next` and the strict break by their owning calculation-timeframe candles. If the A candle is at or before the strict-break candle, the pending reset leg expires. A is upstream of Order_B feedback, so this hard expiry prevents a stale S/E/StopAll setup from firing inside a newer A lifecycle.

### 10.6 Physical canonical opposite Reaction

Let `BreakCandleIndex` be the main calculation-candle index containing `strict_break_time`. Choose the first canonical Bearish Reaction satisfying both:

`FirstIndex >= BreakCandleIndex`

`strict_break_time < ConfirmationTime`

Therefore a Bearish Reaction whose First is the **same main candle** as the strict LL break is eligible even if its candle opened before the exact lower-timeframe crossing. Exact lower-TF chronology remains relevant only to the strict confirmation-after-crossing condition. Canonical-Reaction membership is mandatory; geometry-only evidence cannot become Order_B.

### 10.7 Provenance and identity

Order_B records post-stop behavior, geometric anchor type/source/extreme, reset Reaction identity/confirmation, Reset index/broken level/time, frozen LL boundary/source, exact strict break, and final physical opposite Reaction identity/confirmation. Physical Order identity remains `(FirstIndex, BreakIndex)`. Multiple reset-leg causes may merge into one identity; they do not create duplicate physical Orders.

## 10. Order_B — ACTIVE Bearish reset-leg rule

### 10.1 Eligibility and post-stop owner

Order_B is eligible only after an accepted lifecycle stop (`A`, `S`, `E`, or `StopAll`) selected by the accepted lifecycle owner of the stopped main candle. The stop opens eligibility; it is **not** the geometric HH anchor.

### 10.2 Geometric behavior anchor

For each reset Bearish Reaction, choose the latest accepted behavior source that exists strictly before the Reaction FirstGreen candle, independent of current dominance. Valid anchor families are A/S/E/StopAll. When several lifecycle projections share exactly one source candle, lifecycle priority and number resolve only that exact-source tie.

### 10.3 HH construction and extension

Use the closed main-candle range from anchor behavior source through reset Reaction FirstGreen, inclusive:

`HH = maximum High(anchor candle .. reset Reaction FirstGreen)`

Only a strict better High replaces the current source, so equal extremes retain the earliest source. The HH source must be strictly before the reset Reaction FirstGreen. It must also extend beyond the anchor itself: the HH must be strictly above the anchor behavior `High`; equality invalidates the setup.

### 10.4 Reset and calculation-timeframe strict-break candle

The reset Reaction must first produce its canonical Reset. A strict `High > HH` must occur after that Reset. The **configured calculation candle containing the first valid post-Reset strict crossing** is the Order_B break candle. Equality is not a break.

Lower-timeframe RAW is consulted only when exact intrabar chronology is required: to prove that a crossing in the Reset candle happened after the exact Reset, to retain the exact crossing timestamp as `strict_break_time`, and to prove any same-candle confirmation occurs strictly after that crossing. The exact lower-timeframe timestamp does **not** postpone the Order_B First-candle gate beyond its owning calculation candle.

### 10.5 Accepted-A expiry

Let the next accepted A formation after the reset Reaction First be `A_next`. Compare `A_next` and the strict break by their owning calculation-timeframe candles. If the A candle is at or before the strict-break candle, the pending reset leg expires. A is upstream of Order_B feedback, so this hard expiry prevents a stale S/E/StopAll setup from firing inside a newer A lifecycle.

### 10.6 Physical canonical opposite Reaction

Let `BreakCandleIndex` be the main calculation-candle index containing `strict_break_time`. Choose the first canonical Bullish Reaction satisfying both:

`FirstIndex >= BreakCandleIndex`

`strict_break_time < ConfirmationTime`

Therefore a Bullish Reaction whose First is the **same main candle** as the strict HH break is eligible even if its candle opened before the exact lower-timeframe crossing. Exact lower-TF chronology remains relevant only to the strict confirmation-after-crossing condition. Canonical-Reaction membership is mandatory; geometry-only evidence cannot become Order_B.

### 10.7 Provenance and identity

Order_B records post-stop behavior, geometric anchor type/source/extreme, reset Reaction identity/confirmation, Reset index/broken level/time, frozen HH boundary/source, exact strict break, and final physical opposite Reaction identity/confirmation. Physical Order identity remains `(FirstIndex, BreakIndex)`. Multiple reset-leg causes may merge into one identity; they do not create duplicate physical Orders.
