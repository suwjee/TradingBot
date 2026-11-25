# DP — Direction policy

Source-derived specification; module version 1.0.0. Owns directional price primitives only, not chronology, lifecycle, candle classification, numbering, visibility or mutable trading state.

## Policy model

A policy is an immutable field record (direction, extreme attribute, opposite extreme attribute, first reaction tag, context tag). The source creates two reusable singleton records.

| Field | Bullish | Bearish |
|---|---|---|
| direction | bullish | bearish |
| extreme attribute | low | high |
| opposite extreme attribute | high | low |
| first reaction tag | RED | GREEN |
| context tag | GREEN | RED |
| opposite direction | bearish | bullish |

POLICY_FOR accepts exactly the strings bullish and bearish, returning the corresponding pre-existing record. Any other input raises ValueError with message: Direction must be 'bullish' or 'bearish'. No case normalization or default policy exists. The record constructor itself has no additional runtime validation; the factory is the validated selection path. The record is frozen and slotted.

## Operations

| Operation | Bullish | Bearish |
|---|---|---|
| STRICT_CROSS(value, level) | value < level | value > level |
| BETTER_EXTREME(value, current) | value < current | value > current |
| CHOOSE_EXTREME(left, right) | min(left, right) | max(left, right) |
| CONFIRMATION_CROSS(value, level) | value > level | value < level |

All comparison inputs are expected to have Decimal semantics. Methods do not perform conversion, quantization or rounding. For strict cross, better extreme, and confirmation cross, equality is false. For choose extreme, native two-argument min/max returns the first argument on a comparison tie (important for preserving an existing representation or identity). The confirmation value must already be selected on the confirmation side; the method does not choose a candle field.

OPPOSITE_DIRECTION is a computed property, not stored state. In the source all instance methods use a bullish equality check and otherwise the alternate branch; directly constructing an invalid record does not validate it and would select that alternate branch. This is an implementation observation, not an approved extra trading direction.

## Direction-invariant boundaries

The policy does not classify Doji, build candles, confirm a Reaction chronologically, select a time interval, resolve a tie between source candles, or own a lifecycle transition. Its tags describe roles, not a replacement candle-color rule. Every calculation using it must retain the owning algorithm's original timing and order.

Errors from native comparisons propagate; no local fallback is present. These rules are derived from source, not executed examples.

Source provenance: see [Phase 02 module inventory](../Audit/Phase_02/pipeline__direction_policy.json). Historical runtime evidence is separate.
