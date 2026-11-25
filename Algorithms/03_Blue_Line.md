# BL — Blue Line

Status: DOCUMENTED / PARTIALLY_VERIFIED package; this module is not independently validated end to end.

Compute the Decimal 0.618 Fibonacci reference from the Mode A anchor/leg or Mode B prior Reaction edge. Track pending directional strike extrema and confirm with qualifying candle color. Restrict Break-candle strike search to exact Reaction confirmation inclusive. A scale line requires a prior count and growth with at least one healthy intervening Reaction; reset lines use Reset evidence and spacing. Preserve double-stop invalid Reset Blue for A calculation evidence. Draw price uses one-third for scale and one-fifth for reset from directional main edge, separate from semantic source_extreme. Internal if owner is internal or both prices are strictly within protected opposite Reaction geometry. Public output requires calculation_valid and not behavior_internal. A stop is the first strict crossing of semantic extreme.

## Supplemental directional specification

Supplementary material below is the English semantic prose of the existing synchronized references, pinned to 466eb875070f02cd0dbfb105033422bbe2fd8c70. It is not a fresh branch-level proof. Exact production-source appendices are excluded. Historical acceptance examples remain historical.

## 5. Blue — ACTIVE Bullish specification

### 5.1 Inputs and reference level

Blue consumes canonical Bullish Reactions and Bullish Resets. For each Reaction, the scale reference is the Mode-A boundary when present; otherwise it is the previous Reaction opposite edge. The 0.618 level is `BoxTop − 0.618 × (BoxTop − reference)`.

### 5.2 Scale strikes

Within Reaction First..Break inclusive, a new strike requires a strictly lower `Low` than the previous confirmed strike (or than the Fibonacci level for the first strike). Pending strikes confirm on a `GREEN` main candle. A Break main candle is eligible only with its lower-TF extreme through the strict Reaction confirmation row, inclusive; later main-candle extremes are excluded. A pending strike reaching the Break candle may confirm intrabar only from lower-TF chronology through that exact confirmation row, inclusive; the decisive extreme is the most directional eligible lower-TF extreme.

A Scale Blue is emitted when strike count increases and spacing ownership permits it (first Blue, or at least one healthy Reaction since the previous Blue). Its source is the decisive strike; line price is `Low + (High − Low) / 3` and its drawing interval is one timeframe before/after the source time.

### 5.3 Reset Blue and double-stop calculation validity

A Reset Blue is sourced by the Reset main candle, with source extreme `Low`, broken level from Reset, and line price `Low + (High − Low) / 5`. If the prior Blue first strict-stops on that same Reset candle and the Reset source extends strictly farther in the Bullish direction than the prior Blue source extreme, the new Reset Blue is marked `calculation_valid=False`. That invalid line remains calculation evidence for the A double-stop route but is excluded from public Blue output.

### 5.4 Internal/public Blue

A Blue becomes behavior-internal when its owning Reaction is internal, or when both the source extreme and rendered line price lie strictly inside the same protected healthy Reaction. Drawing offset alone does not create internal ownership. Public Blue is exactly `calculation_valid and not behavior_internal`.

## 5. Blue — ACTIVE Bearish specification

### 5.1 Inputs and reference level

Blue consumes canonical Bearish Reactions and Bearish Resets. For each Reaction, the scale reference is the Mode-A boundary when present; otherwise it is the previous Reaction opposite edge. The 0.618 level is `BoxBottom + 0.618 × (reference − BoxBottom)`.

### 5.2 Scale strikes

Within Reaction First..Break inclusive, a new strike requires a strictly higher `High` than the previous confirmed strike (or than the Fibonacci level for the first strike). Pending strikes confirm on a `RED` main candle. A Break main candle is eligible only with its lower-TF extreme through the strict Reaction confirmation row, inclusive; later main-candle extremes are excluded. A pending strike reaching the Break candle may confirm intrabar only from lower-TF chronology through that exact confirmation row, inclusive; the decisive extreme is the most directional eligible lower-TF extreme.

A Scale Blue is emitted when strike count increases and spacing ownership permits it (first Blue, or at least one healthy Reaction since the previous Blue). Its source is the decisive strike; line price is `High − (High − Low) / 3` and its drawing interval is one timeframe before/after the source time.

### 5.3 Reset Blue and double-stop calculation validity

A Reset Blue is sourced by the Reset main candle, with source extreme `High`, broken level from Reset, and line price `High − (High − Low) / 5`. If the prior Blue first strict-stops on that same Reset candle and the Reset source extends strictly farther in the Bearish direction than the prior Blue source extreme, the new Reset Blue is marked `calculation_valid=False`. That invalid line remains calculation evidence for the A double-stop route but is excluded from public Blue output.

### 5.4 Internal/public Blue

A Blue becomes behavior-internal when its owning Reaction is internal, or when both the source extreme and rendered line price lie strictly inside the same protected healthy Reaction. Drawing offset alone does not create internal ownership. Public Blue is exactly `calculation_valid and not behavior_internal`.
