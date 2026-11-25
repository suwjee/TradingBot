# Data model contract map

Status: DECLARED RECORD SCHEMAS COMPLETE / FIELD-USE AND SERIALIZATION SEMANTICS INCOMPLETE. The semantic field contracts are distributed through the following modules; the declaration inventory has been moved to Audit because it is evidence about the implementation, not a standalone formal data schema.

The foundational Candle, normalized bucket, MarketContext and BucketAppend contracts are now expanded in [Candle and market input](../Specification/07_Candles_And_Market_Input.md). See [declared record schemas](Declared_Record_Schemas.md) for all 46 dataclasses and 438 fields, types and defaults. Dynamic instance fields, detailed field-use semantics and serialized payloads remain later phase work.

| Model family | Semantic contract |
|---|---|
| RAW and main OHLC candles, bucket results | [RAW aggregation](../Algorithms/21_RAW_Aggregation_Contract.md) |
| Candle, Candidate, Reaction, Reset, chronology | [Reaction Engine](../Algorithms/01_Reaction_Engine.md) |
| Blue Line, Scale Strike | [Blue Line](../Algorithms/03_Blue_Line.md) |
| A Zone | [A Zone](../Algorithms/04_A_Zone.md) |
| S Zone | [S Zone](../Algorithms/05_S_Zone.md) |
| Physical Order, creation causes, audit ledger | [Order Audit](../Algorithms/08_Order_Audit.md) |
| E Zone | [E Zone](../Algorithms/09_E_Zone.md) |
| StopAll and dominance state | [Lifecycle](../Algorithms/10_Lifecycle.md) |
| Primary structures, MBL, independent cycles | [Primary Structures](../Algorithms/12_Primary_Structures.md) |
| Market and Pipeline state, visibility, response | [Trading Bridge](../Algorithms/17_Trading_Bridge.md) and [Serialization](../Algorithms/19_Serialization.md) |
| Live transport, prefix and transactional state | [Live transport](../Algorithms/23_Live_Transport_Contract.md) |
| Final verdict, repair, repeat | [True/False](../Algorithms/22_True_False_Exact_Contract.md) |

For each model, future formalization must enumerate every field, type, default, optionality, unit, owner, identity, mutability, equality, lifecycle and serialization rule. No missing field may be invented to close a reconstruction gap. The current tree does not contain an executable model implementation.
