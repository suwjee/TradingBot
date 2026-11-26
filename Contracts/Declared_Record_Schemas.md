# Declared record schemas — foundational contract (V3.0)

All 46 declared dataclass records and 438 annotated class fields in the current Engine are listed below. These are language-neutral record interfaces, not executable definitions. Field order follows the declaration. Type terms: Decimal is the source decimal representation; int is integer; str is text; datetime is a native timestamp (market timestamps are normally naive local); bool is Boolean; None means null; list is an ordered mutable sequence; tuple is an ordered fixed sequence; dict is a map; set and frozenset are unordered sets (mutable and immutable respectively). Object and unparameterized tuple deliberately retain the source's broad type. References to other record names are resolved within this catalog or their owning specification. Union types indicate declaration intent, not runtime enforcement.

Required means no constructor default, even when nullable. Explicit defaults are values; list/dict factory means a fresh independent empty container per construction. Keyword-only fields are marked. Frozen records reject normal field rebinding but do not recursively freeze nested data. Native dataclass equality is fieldwise unless the class overrides it; this is separate from physical identity and cache keys. Record fields with a timestamp suffix do not automatically represent exact lower events: source, trigger, decision and stop roles are separate (see [time](../Specification/03_Chronology_And_Time_Model.md)). Index fields are local positions/identities in the owning sequence; Ordinal/number is a logical label, not an index. Prices are Decimal except when a field explicitly has another type. A class with no dataclass declaration can still own mutable state or custom properties; its initialization and field-use semantics are later function-level work. The source-located evidence is separated in [Phase 03 audit](../Audit/Phase_03/README.md).

## Trading Bridge

### BucketAppend

Frozen record, slotted in the source. Owner: Trading Bridge.

| Field | Declared type | Constructor default |
|---|---|---|
| first_dirty_second | int | Required |
| first_dirty_main | int | Required |
| settled_seconds | int | Required |
| settled_main | int | Required |

### EngineBundle

Frozen record, slotted in the source. Owner: Trading Bridge.

| Field | Declared type | Constructor default |
|---|---|---|
| reaction | object | Required |
| blue_line | object | Required |
| a_zone | object | Required |
| s_zone | object | Required |
| e_zone | object \| None | Required |
| lifecycle | object \| None | Required |
| primary | object \| None | None |

### MarketContext

Frozen record, slotted in the source. Owner: Trading Bridge.

| Field | Declared type | Constructor default |
|---|---|---|
| seconds | list[object] | Required |
| candles | list[object] | Required |
| lower_index | object | Required |
| chronology | object | Required |
| start_index | int | Required |
| end_index | int | Required |
| index_offset | int | 0 |
| initial_bullish_trend | bool | False |
| initial_bearish_trend | bool | False |

### PipelineState

Mutable record, slotted in the source. Owner: Trading Bridge.

| Field | Declared type | Constructor default |
|---|---|---|
| directions | tuple[str, ...] | Required |
| results | dict[str, object] | Required |
| reusable_full_context | bool | Required |
| initial_order_geometry | dict[str, object] | Required |
| internal_reaction_identities | dict[str, set[tuple[int, int]]] | Required |
| full_e_zones | dict[str, list[object]] | Required |
| full_e_detectors | dict[str, object] | Required |
| full_s_detectors | dict[str, object] | Required |
| full_lines_by_direction | dict[str, list[object]] | Required |
| full_a_by_direction | dict[str, list[object]] | Required |
| invalid_a_identities_by_direction | dict[str, set[tuple[datetime, int]]] | Required |
| invalid_s_identities_by_direction | dict[str, set[tuple[datetime, int]]] | Required |
| full_s_by_direction | dict[str, list[object]] | Required |
| full_s_candidates_by_direction | dict[str, list[object]] | Required |
| primary_result | object \| None | None |
| live_stages | object \| None | None |

### FullDirectionState

Mutable record, slotted in the source. Owner: Trading Bridge.

| Field | Declared type | Constructor default |
|---|---|---|
| e_zones | list[object] | Required |
| e_detector | object | Required |
| s_detector | object | Required |
| blue_lines | list[object] | Required |
| a_zones | list[object] | Required |
| invalid_a_identities | set[tuple[datetime, int]] | Required |
| invalid_s_identities | set[tuple[datetime, int]] | Required |
| s_zones | list[object] | Required |
| s_candidates | list[object] | Required |
| initial_s_zones | list[object] | Required |

### DirectionRangeState

Mutable record, slotted in the source. Owner: Trading Bridge.

| Field | Declared type | Constructor default |
|---|---|---|
| blue_lines | list[object] | Required |
| a_zones | list[object] | Required |
| s_candidates | list[object] | Required |
| accepted_s_zones | list[object] | Required |
| e_zones | list[object] | Required |
| invalid_a_identities | set[tuple[datetime, int]] | Required |
| invalid_s_identities | set[tuple[datetime, int]] | Required |

### DirectionVisibilityState

Mutable record, slotted in the source. Owner: Trading Bridge.

| Field | Declared type | Constructor default |
|---|---|---|
| blue_lines | list[object] | Required |
| a_zones | list[object] | Required |
| s_zones | list[object] | Required |
| e_zones | list[object] | Required |
| stopalls | list[object] | Required |
| prepared_order_audit | list[object] | Required |
| projection_s_zones | list[object] | Required |
| projection_e_zones | list[object] | Required |
| projection_stopalls | list[object] | Required |
| primary_groups | dict[str, list[object]] | Fresh empty dict (keyword-only) |

## Primary structures

### StructureOrder

Frozen record, slotted in the source. Owner: Primary structures.

| Field | Declared type | Constructor default |
|---|---|---|
| direction | str | Required |
| reaction_number | int | Required |
| first_index | int | Required |
| break_index | int | Required |
| confirmation_event_time | datetime | Required |
| stop_level | Decimal | Required |
| stop_source_index | int | Required |
| stop_index | int | Required |
| stop_event_time | datetime | Required |
| causes | tuple[str, ...] | Required |
| box_top | Decimal \| None | None |
| box_bottom | Decimal \| None | None |
| reaction_mode | str \| None | None |
| audit_causes | tuple[dict[str, object], ...] | () |

### PrimaryPoint

Frozen record, slotted in the source. Owner: Primary structures.

| Field | Declared type | Constructor default |
|---|---|---|
| kind | str | Required |
| number | int | Required |
| source_index | int | Required |
| source_time | datetime | Required |
| price | Decimal | Required |
| trigger_index | int | Required |
| trigger_event_time | datetime | Required |
| decision_index | int | Required |
| decision_event_time | datetime | Required |
| order | StructureOrder | Required |
| cycle_id | str \| None | None (keyword-only) |
| identity_source | PrimaryPoint \| None | None (keyword-only) |

### MatchingBehaviorLeg

Frozen record, slotted in the source. Owner: Primary structures.

| Field | Declared type | Constructor default |
|---|---|---|
| source_index | int | Required |
| source_time | datetime | Required |
| price | Decimal | Required |
| reference_stopall_index | int | Required |
| second_behavior_index | int | Required |
| trigger_index | int | Required |
| trigger_event_time | datetime | Required |
| stop_index | int \| None | Required |
| stop_event_time | datetime \| None | Required |

### TrendTransition

Frozen record, slotted in the source. Owner: Primary structures.

| Field | Declared type | Constructor default |
|---|---|---|
| index | int | Required |
| event_time | datetime | Required |
| level | Decimal | Required |
| high | PrimaryPoint | Required |
| target_direction | str | "bullish" |

### PrimaryResult

Mutable record, slotted in the source. Owner: Primary structures.

| Field | Declared type | Constructor default |
|---|---|---|
| highs | list[PrimaryPoint] | Fresh empty list |
| lows | list[PrimaryPoint] | Fresh empty list |
| mbl | MatchingBehaviorLeg \| None | None |
| status | str | "waiting-for-matching-behaviors" |
| post_pl3_orders | list[StructureOrder] | Fresh empty list |
| cycle_id | str \| None | None |
| cycles | list[PrimaryResult] | Fresh empty list |
| qualification_event_time | datetime \| None | None |
| transition | TrendTransition \| None | None |
| direction | str | "bearish" |

### _CycleCheckpoint

Mutable record, slotted in the source. Owner: Primary structures.

| Field | Declared type | Constructor default |
|---|---|---|
| result | PrimaryResult | Required |
| reference_price | Decimal | Required |
| gate_index | int | Required |
| cursor | datetime | Required |
| phase | str | "PH" |
| reset_high | bool | False |

### _PrimaryStep

Frozen record, slotted in the source. Owner: Primary structures.

| Field | Declared type | Constructor default |
|---|---|---|
| event_time | datetime | Required |
| activations | int | Required |
| cycle_index | int \| None | None |
| checkpoint | _CycleCheckpoint \| None | None |
| point | PrimaryPoint \| None | None |

### _PrimaryRun

Mutable record, slotted in the source. Owner: Primary structures.

| Field | Declared type | Constructor default |
|---|---|---|
| previous | _PrimaryRun \| None | None |
| dirty_event | datetime \| None | None |
| schedule | tuple | () |
| steps | list[_PrimaryStep] | Fresh empty list |
| crossings | dict[tuple, tuple[int, datetime] \| None] | Fresh empty dict |
| projected_points | dict[int, tuple[PrimaryPoint, PrimaryPoint]] | Fresh empty dict |

### _ReflectedRow

Frozen record, slotted in the source. Owner: Primary structures.

| Field | Declared type | Constructor default |
|---|---|---|
| original | object | Required |

## A Zone

### BlueState

Frozen record, slotted in the source. Owner: A Zone.

| Field | Declared type | Constructor default |
|---|---|---|
| ordinal | int | Required |
| line | object | Required |
| formation_index | int | Required |
| formation_time | datetime | Required |
| stop_index | int \| None | Required |
| stop_time | datetime \| None | Required |
| stop_event_time | datetime \| None | Required |
| stop_level | Decimal | Required |
| stop_event_extreme | Decimal \| None | Required |

### AZone

Frozen record, slotted in the source. Owner: A Zone.

| Field | Declared type | Constructor default |
|---|---|---|
| direction | str | Required |
| blue_1_ordinal | int | Required |
| blue_2_ordinal | int | Required |
| blue_1_source_time | datetime | Required |
| blue_2_source_time | datetime | Required |
| blue_1_stop_time | datetime | Required |
| blue_2_stop_time | datetime | Required |
| blue_1_stop_level | Decimal | Required |
| blue_2_stop_level | Decimal | Required |
| continuation_level | Decimal | Required |
| continuation_source_index | int | Required |
| continuation_source_time | datetime | Required |
| trigger_index | int | Required |
| trigger_time | datetime | Required |
| trigger_event_time | datetime | Required |
| reaction_number | int | Required |
| reaction_first_time | datetime | Required |
| reaction_break_time | datetime | Required |
| source_index | int | Required |
| source_time | datetime | Required |
| price | Decimal | Required |
| formation_route | str \| None | None (keyword-only) |
| blue_1_stop_event_time | datetime \| None | None (keyword-only) |
| blue_2_stop_event_time | datetime \| None | None (keyword-only) |

### _AHistory

Mutable record, slotted in the source. Owner: A Zone.

| Field | Declared type | Constructor default |
|---|---|---|
| confirmations | dict[_EventKey, datetime] | Fresh empty dict |
| reset_formations | dict[_EventKey, datetime] | Fresh empty dict |
| crossings | dict[_EventKey, tuple[_MarketEvent \| None, bool]] | Fresh empty dict |
| extremes | dict[_EventKey, tuple[Decimal, int, datetime]] | Fresh empty dict |
| matches | dict[_EventKey, int \| None] | Fresh empty dict |
| inherited_stops | dict[_EventKey, tuple \| None] | Fresh empty dict |
| triggers | dict[_EventKey, tuple \| None] | Fresh empty dict |
| sources | dict[_EventKey, _MarketEvent \| None] | Fresh empty dict |
| zones | dict[_EventKey, AZone] | Fresh empty dict |

## Blue Line

### ScaleStrike

Frozen record, slotted in the source. Owner: Blue Line.

| Field | Declared type | Constructor default |
|---|---|---|
| source_index | int | Required |
| source_time | datetime | Required |
| extreme | Decimal | Required |

### BlueLine

Frozen record, slotted in the source. Owner: Blue Line.

| Field | Declared type | Constructor default |
|---|---|---|
| direction | str | Required |
| kind | str | Required |
| reaction_number | int | Required |
| previous_strike_count | int \| None | Required |
| strike_count | int \| None | Required |
| fibonacci_level | Decimal \| None | Required |
| source_index | int | Required |
| source_time | datetime | Required |
| source_extreme | Decimal | Required |
| broken_level | Decimal \| None | Required |
| line_price | Decimal | Required |
| start_time | datetime | Required |
| end_time | datetime | Required |
| calculation_valid | bool | True |
| behavior_internal | bool | False |

### _BlueCheckpoint

Frozen record, slotted in the source. Owner: Blue Line.

| Field | Declared type | Constructor default |
|---|---|---|
| previous_reaction | object \| None | None |
| previous_count | int \| None | None |
| healthy_since_blue | int | 0 |
| line_count | int | 0 |

## Direction policy

### DirectionPolicy

Frozen record, slotted in the source. Owner: Direction policy.

| Field | Declared type | Constructor default |
|---|---|---|
| direction | Direction | Required |
| extreme_attr | Literal["low", "high"] | Required |
| opposite_extreme_attr | Literal["high", "low"] | Required |
| first_reaction_tag | Literal["RED", "GREEN"] | Required |
| context_tag | Literal["GREEN", "RED"] | Required |

## E Zone

### EZone

Frozen record, slotted in the source. Owner: E Zone.

| Field | Declared type | Constructor default |
|---|---|---|
| direction | str | Required |
| family | str | Required |
| number | int | Required |
| parent_type | str | Required |
| parent_source_index | int | Required |
| parent_source_time | datetime | Required |
| parent_price | Decimal | Required |
| parent_stop_index | int | Required |
| parent_stop_time | datetime | Required |
| parent_stop_event_time | datetime | Required |
| order_direction | str | Required |
| order_reaction_number | int | Required |
| order_mode | str | Required |
| order_causes | tuple[str, ...] | Required |
| order_parent_stop_cause_time | datetime \| None | Required |
| order_first_index | int | Required |
| order_first_time | datetime | Required |
| order_break_index | int | Required |
| order_break_time | datetime | Required |
| order_confirmation_time | datetime | Required |
| order_box_top | Decimal | Required |
| order_box_top_source_index | int | Required |
| order_box_top_source_time | datetime | Required |
| order_box_bottom | Decimal | Required |
| order_box_bottom_source_index | int | Required |
| order_box_bottom_source_time | datetime | Required |
| order_stop_level | Decimal | Required |
| order_stop_source_index | int | Required |
| order_stop_source_time | datetime | Required |
| source_index | int | Required |
| source_time | datetime | Required |
| price | Decimal | Required |
| decision_index | int | Required |
| decision_time | datetime | Required |
| decision_event_time | datetime | Required |

### _ParentStopProgress

Frozen record, slotted in the source. Owner: E Zone.

| Field | Declared type | Constructor default |
|---|---|---|
| scanned_until | datetime | Required |
| event | datetime \| None | Required |

### _EReconciliationStep

Frozen record, slotted in the source. Owner: E Zone.

| Field | Declared type | Constructor default |
|---|---|---|
| source | int | Required |
| count | int | Required |
| active | tuple[EZone, ...] | Required |
| sequence_start | datetime \| None | Required |

### _ReconciledE

Frozen record, slotted in the source. Owner: E Zone.

| Field | Declared type | Constructor default |
|---|---|---|
| candidates | tuple[EZone, ...] | Required |
| numbered | tuple[EZone, ...] | Required |
| accepted | frozenset[tuple[datetime, int]] | Required |
| lifecycle_starts | frozenset[datetime] | Required |
| evidence | tuple | Required |
| steps | tuple[_EReconciliationStep, ...] | Required |
| native_numbered | tuple[EZone, ...] | Required |

## Lifecycle

### StopAll

Frozen record, slotted in the source. Owner: Lifecycle.

| Field | Declared type | Constructor default |
|---|---|---|
| direction | str | Required |
| number | int | Required |
| source_index | int | Required |
| source_time | datetime | Required |
| price | Decimal | Required |
| decision_index | int | Required |
| decision_time | datetime | Required |
| decision_event_time | datetime | Required |
| gate_type | str | Required |
| gate_event_time | datetime | Required |
| stopped_behavior_type | str | Required |
| stopped_behavior_key | str | Required |
| stopped_behavior_count | int | Required |
| underlying_e_family | str \| None | Required |
| underlying_e_number | int \| None | Required |
| order_direction | str \| None | Required |
| order_reaction_number | int \| None | Required |
| order_mode | str \| None | Required |
| order_causes | tuple[str, ...] | Required |
| order_parent_stop_cause_time | datetime \| None | Required |
| order_first_index | int \| None | Required |
| order_first_time | datetime \| None | Required |
| order_break_index | int \| None | Required |
| order_break_time | datetime \| None | Required |
| order_confirmation_time | datetime \| None | Required |
| order_box_top | Decimal \| None | Required |
| order_box_top_source_index | int \| None | Required |
| order_box_top_source_time | datetime \| None | Required |
| order_box_bottom | Decimal \| None | Required |
| order_box_bottom_source_index | int \| None | Required |
| order_box_bottom_source_time | datetime \| None | Required |
| order_stop_level | Decimal \| None | Required |
| order_stop_source_index | int \| None | Required |
| order_stop_source_time | datetime \| None | Required |
| stop_index | int \| None | Required |
| stop_time | datetime \| None | Required |
| stop_event_time | datetime \| None | Required |
| donor_type | str \| None | None (keyword-only) |
| donor_source_index | int \| None | None (keyword-only) |
| donor_source_time | datetime \| None | None (keyword-only) |
| donor_color | str \| None | None (keyword-only) |
| donor_number | int \| None | None (keyword-only) |
| donor_price | Decimal \| None | None (keyword-only) |
| donor_stop_time | datetime \| None | None (keyword-only) |
| donor_stop_event_time | datetime \| None | None (keyword-only) |

### _DominantBehavior

Frozen record, slotted in the source. Owner: Lifecycle.

| Field | Declared type | Constructor default |
|---|---|---|
| kind | str | Required |
| family | str | Required |
| number | int \| None | Required |
| count | int | Required |
| latest | object | Required |

### _StopAllCheckpoint

Frozen record, slotted in the source. Owner: Lifecycle.

| Field | Declared type | Constructor default |
|---|---|---|
| owner | _DominantBehavior \| None | None |
| pending_stop | tuple[_DominantBehavior, datetime] \| None | None |
| active | tuple[StopAll, ...] | () |
| output_count | int | 0 |

## Order Audit

### PostBehaviorStop

Frozen record, slotted in the source. Owner: Order Audit.

| Field | Declared type | Constructor default |
|---|---|---|
| behavior_type | str | Required |
| behavior_source_index | int | Required |
| behavior_source_time | datetime | Required |
| event_time | datetime | Required |

### OrderBBehaviorAnchor

Frozen record, slotted in the source. Owner: Order Audit.

| Field | Declared type | Constructor default |
|---|---|---|
| behavior_type | str | Required |
| behavior_source_index | int | Required |
| behavior_source_time | datetime | Required |
| priority | int | Required |
| number | int | Required |

### OrderBResetLeg

Frozen record, slotted in the source. Owner: Order Audit.

| Field | Declared type | Constructor default |
|---|---|---|
| post_stop | PostBehaviorStop | Required |
| anchor_behavior_type | str | Required |
| anchor_behavior_source_index | int | Required |
| anchor_behavior_source_time | datetime | Required |
| anchor_behavior_extreme | Decimal | Required |
| reset_reaction | object | Required |
| reset_confirmation_time | datetime | Required |
| reset_source_index | int | Required |
| reset_broken_level | Decimal | Required |
| reset_time | datetime | Required |
| leg_boundary | Decimal | Required |
| leg_source_index | int | Required |
| leg_source_time | datetime | Required |
| strict_break_time | datetime | Required |
| reaction_number | int | Required |
| physical_reaction | object | Required |
| physical_confirmation_time | datetime | Required |

## Reaction

### Candle

Frozen record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| index | int | Required |
| timestamp | datetime | Required |
| display_time | str | Required |
| tag | str | Required |
| open | Decimal | Required |
| high | Decimal | Required |
| low | Decimal | Required |
| close | Decimal | Required |

### Candidate

Mutable record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| first_idx | int | Required |
| first_time | str | Required |
| box_top_source_idx | int | Required |
| box_top_source_time | str | Required |
| box_top | Decimal | Required |
| box_bottom_source_idx | int | Required |
| box_bottom_source_time | str | Required |
| box_bottom | Decimal | Required |
| mode | str | Required |
| anchor_idx | int \| None | None |
| anchor_value | Decimal \| None | None |
| leg_boundary_value | Decimal \| None | None |
| break_idx | int \| None | None |
| break_time | str \| None | None |
| intrabar_start | datetime \| None | None |
| cross_direction_origin | bool | False |
| cross_direction_chain_owner | bool | False |
| order_gate_decision | str \| None | None |
| behavior_public_number | int \| None | None |
| behavior_public_box_top | Decimal \| None | None |
| behavior_public_box_bottom | Decimal \| None | None |
| behavior_confirmation_time | datetime \| None | None |
| behavior_first_time | datetime \| None | None |
| behavior_internal | bool | False |

### ResetEvent

Frozen record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| index | int | Required |
| display_time | str | Required |
| second_time | str \| None | Required |
| broken_level | Decimal | Required |
| from_first_idx | int | Required |

### IntrabarAnalysis

Frozen record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| event_second | Candle | Required |
| extreme | Decimal | Required |
| extreme_source | Candle | Required |

### DetectionResult

Frozen record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| direction | str | Required |
| reactions | list[Candidate] | Required |
| resets | list[ResetEvent] | Required |
| start_index | int | Required |
| end_index | int | Required |

### _NormalReactionCursor

Mutable record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| next_index | int | Required |
| previous | Candidate | Required |
| candidate | Candidate \| None | Required |
| running_value | Decimal | Required |
| running_source | int | Required |
| pending_reset_index | int \| None | Required |

### _ReactionCheckpoint

Mutable record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| cursor | _NormalReactionCursor | Required |
| reaction_count | int | Required |
| reset_count | int | Required |

### _InitialLegCursor

Mutable record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| next_index | int | Required |
| state | str | Required |
| leg_open_low | Decimal \| None | Required |
| leg_just_started | bool | Required |
| anchor | Candle \| None | Required |
| anchor_origin | str \| None | Required |
| candidate | Candidate \| None | Required |

### _TrendLegCursor

Mutable record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| next_index | int | Required |
| fixed_source | Candle | Required |
| candidate | Candidate \| None | Required |

### _BehaviorReactionSpan

Frozen record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| identity | tuple[int, int] | Required |
| first_time | datetime | Required |
| confirmed_at | datetime | Required |
| top | Decimal | Required |
| bottom | Decimal | Required |

### _LiveBehaviorReactionEntry

Frozen record, slotted in the source. Owner: Reaction.

| Field | Declared type | Constructor default |
|---|---|---|
| geometry | tuple | Required |
| span | _BehaviorReactionSpan | Required |
| extremes | tuple[Decimal, Decimal] \| None | Required |

## S Zone

### SZone

Frozen record, slotted in the source. Owner: S Zone.

| Field | Declared type | Constructor default |
|---|---|---|
| direction | str | Required |
| color | str | Required |
| formation_type | str | Required |
| a_ordinal | int | Required |
| a_source_index | int | Required |
| a_source_time | datetime | Required |
| a_price | Decimal | Required |
| a_stop_index | int | Required |
| a_stop_time | datetime | Required |
| a_stop_event_time | datetime | Required |
| order_direction | str \| None | Required |
| order_reaction_number | int \| None | Required |
| order_mode | str \| None | Required |
| order_first_index | int \| None | Required |
| order_first_time | datetime \| None | Required |
| order_break_index | int \| None | Required |
| order_break_time | datetime \| None | Required |
| order_confirmation_time | datetime \| None | Required |
| order_box_top | Decimal \| None | Required |
| order_box_top_source_index | int \| None | Required |
| order_box_top_source_time | datetime \| None | Required |
| order_box_bottom | Decimal \| None | Required |
| order_box_bottom_source_index | int \| None | Required |
| order_box_bottom_source_time | datetime \| None | Required |
| order_stop_level | Decimal \| None | Required |
| order_stop_source_index | int \| None | Required |
| order_stop_source_time | datetime \| None | Required |
| reset_reaction_number | int \| None | Required |
| reset_time | datetime \| None | Required |
| source_index | int | Required |
| source_time | datetime | Required |
| price | Decimal | Required |
| decision_index | int | Required |
| decision_time | datetime | Required |
| decision_event_time | datetime | Required |

## True/False

### BasicRepeat

Mutable record, slotted in the source. Owner: True/False.

| Field | Declared type | Constructor default |
|---|---|---|
| latest | dict | Required |
| repair_count | int | Required |
| verdict_count | int | Required |

## Scope

This is the complete declared record interface catalog, not a claim that every dynamically assigned instance attribute, property, dictionary payload, constructor validation, serialization field, or field-use condition has been semantically extracted. Those are covered by the owning function/module, lifecycle and serialization phases. No production implementation or executable tests are included.
