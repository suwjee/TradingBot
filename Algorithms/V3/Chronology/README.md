# Chronology & Event Ordering — Phase 07 checkpoint 01

**INCOMPLETE for full semantic closure.** Historical baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; selected clauses revised for `c99b4c957e932d9ee70c492ca03ce80711447fc1`. [Rebaseline register](../../../Audit/Phase_07/Rebaseline_v2_8_7.json); remaining source anchors and coverage require reconciliation.

- [Time domains and Reaction](01_Time_Reaction.md): CH01–CH08
- [Blue, A and S](02_Blue_A_S.md): CH09–CH18
- [Order and E](03_Order_E.md): CH19–CH28
- [Lifecycle and Primary](04_Lifecycle_Primary.md): CH29–CH36
- [Projection, Live and T/F](05_Projection_Live_TF.md): CH37–CH45

## Critical joint-event rules

| Owner | Equality / tie behavior |
|---|---|
| Reaction | Invalidation first within lower row; first main completion, then earliest First. |
| Blue | Penetration recorded before breakout check on same row. |
| A | Trigger confirmation equality allowed; crossing and extreme end bounds differ. |
| S | Same lower position rejects; same main row rejects only in no-lower fallback. |
| Order A/B | Strictly later exact confirmation; same main First permitted. |
| E | Earliest exact stop then latest First. |
| StopAll | E before S at same source time in iteration. |
| Primary | PH equality allowed; PL strictly later; equal seek or cancel/winner ambiguous. |
| T/F | Primary, StopAll, E, S projection precedence; not physical ordering. |

Distinguish lower position, timestamp, source/decision/confirmation/stop, main bucket and visibility horizon. Never invent intrarow market chronology. See [foundations](../../../Specification/03_Chronology_And_Time_Model.md), [state registry](../State_Machines/README.md) and [audit](../../../Audit/Phase_07/README.md).

## Checkpoint 03

[Additional owner boundaries](06_Additional_Owner_Boundaries.md): CH46–CH75; 75 total reviewed clauses. Full semantic closure remains incomplete.

## Checkpoint 05

[Cross-owner chronology and replay boundaries](07_Cross_Owner_Chronology.md): CH76–CH123, 123 reviewed clauses total. [Integration and comparison evidence](../../../Audit/Phase_07/Chronology_Integration.md). Structural checks passed; semantic closure remains incomplete.
