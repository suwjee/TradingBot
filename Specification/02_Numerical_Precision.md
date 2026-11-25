# Numerical precision — foundational contract (V3.0)

This specification describes source behavior, not a new precision policy. See the [Phase 03 evidence map](../Audit/Phase_03/README.md). Apply these primitives together with each owning algorithm's ordered expressions.

## N01 — Parse and normalize

Batch input removes a leading UTF-8 BOM and parses JSON fractional/exponent-number tokens directly into Decimal; JSON integer tokens use the native integer parser. Live input also parses fractional tokens as Decimal, then requires a nonempty list. Do not introduce a binary floating-point intermediate. A price encoded as a string remains a string until its applicable conversion. Input prices are not globally validated for finiteness, positivity or OHLC consistency by the normalization helper.

NORMALIZE(value): if the value is a Decimal instance, including a subclass, return the original object. Otherwise construct a Decimal from the native string representation of value. Conversion failures propagate unless the calling path explicitly catches them. This is not a guarantee that an already-rounded external float can be recovered. Some owning paths instead use direct Decimal construction; preserve that difference for non-Decimal inputs. See [core utilities](05_Core_Utilities.md).

## N02 — Representation-sensitive normalization cache

Batch aggregation allocates a fresh map keyed by (runtime type, native equality/hash value). For each RAW record, perform cached normalization in open, high, low, close order. On a cache miss normalize, store and return; on hit return the existing object. The key is not the textual token. Decimal 1.00 and Decimal 1.0 compare equal and can share the first stored representation; integer 1 and string "1" use different type keys. Native key equality also applies to signed zeros and equal values with different exponents. No forced quantization or formatting is added.

Live bucket aggregation retains the existing price map across successful appends and stages new keys separately. Existing entries win over new entries. On rollback remove keys added by that transaction; do not reset historical representation on each append. A newly introduced key must be hashable, and constructor or map errors are not silently converted into a default price.

Analytical illustration (not a run): if Decimal 2.00 is the first such value encountered in an aggregation cache, a later equal Decimal 2.0 resolves to that original Decimal 2.00. The specification must preserve this behavior rather than require every original RAW lexeme to survive unchanged in every derived field.

## N03 — Comparison and selection

| Operation | Bullish behavior space | Bearish behavior space |
|---|---|---|
| Directional extreme | Low | High |
| Strict stop / improved directional extreme | x < level | x > level |
| Strict confirmation | high > BoxTop | low < BoxBottom |
| Directional choose-extreme | min(left,right) | max(left,right) |

Equality does not cross. Native min/max retain the first operand on equal comparison. Aggregate extrema compare previous value first, so equal extrema retain the previously selected Decimal. Range-index queries break equal price ties by earliest position, not traversal order. Other algorithm-specific paths can choose last-equal or use compound tie keys; never generalize the index rule to all algorithms.

## N04 — Decimal arithmetic and reflection

Blue Fibonacci ratio is the exact decimal literal 0.618. Compute in source operation order:
- Bullish: difference = BoxTop minus reference; scaled = ratio multiplied by difference; result = BoxTop minus scaled.
- Bearish: difference = reference minus BoxBottom; scaled = ratio multiplied by difference; result = BoxBottom plus scaled.

Do not reorder these operations, replace the ratio with a float, or round the output. Source uses ordinary Decimal operators; arithmetic uses active Decimal context. Do not assume unlimited precision, force a particular precision/rounding mode, or assume all possible Decimal operations are exact. No explicit global context configuration was found in the inspected Engine modules; caller/runtime context is an external condition, not a fixed numeric setting extracted here.

Reflection uses the Decimal copy-negate operation, not subtraction from zero or a rounded unary operation. Swap high and low roles when reflecting candles; swap top and bottom and their source identities for Reaction geometry. Keep time/index unchanged. Signed zero and exponent representation must follow the native copy-negate contract. Internal color role reflection is not reclassification of native candles.

## N05 — Scoped validation context

Order Audit uses a local copy of the current Decimal context in three optimized validation paths: carried-creation index validation; initial accepted-order stream geometry validation; pending/accepted audit index validation. This isolates flags/traps from validation rather than defining a different price precision. A malformed or non-native candidate can make the optimized path fall back to its authoritative legacy/eager path. Do not replace exceptions with arbitrary rounded values. Native accepted-order validation allows exact types Decimal, string, integer and float in its guarded conversion path; this is compatibility behavior, not permission to introduce floats for normal RAW parsing.

## N06 — Output and diagnostics

Native serializers project price fields as native Decimal strings (e.g. Reaction box bounds, Reset broken level, A price and Order stop level), retaining selected representation and any scientific notation produced by the native string operation. Null handling and specific field presence are defined per serializer. Do not impose a fixed number of decimals or coerce strings to JSON numeric values. The bridge rounds duration diagnostics to two decimals; that is telemetry, not a price-rounding rule. Full field-by-field serialization mapping belongs to later function/module phases.

## Constraints

No RAW dataset was read and no numeric engine operation was executed to produce this contract. The examples are source-derived illustrations. Full enumeration of module-specific arithmetic, special values, failure propagation and contextual price selection is not yet closed. See [direction policy](06_Direction_Policy.md) and [range index contract](08_Range_Indexes_And_Caches.md).
