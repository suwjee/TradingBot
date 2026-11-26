# PH / PL — Primary and secondary roles (V3)

**Conventions:** B = bullish, R = bearish. A strict trend stop means Low < level for B, High > level for R; improvement uses the same predicate. Main source identity and exact event chronology are separate. Preserve Decimal representation, operation order and stable ordering. Required record fields/defaults are in [record interfaces](../../Contracts/Declared_Record_Schemas.md); shared searches in [Index and cache contracts](20_Indexes_And_Caching.md). Procedure labels identify semantic operations, not required implementation symbols.


## PH-M01 — Native role map

| Conceptual role | Bearish regime | Bullish regime |
|---|---|---|
| Primary point | PH, max High from trigger main through native Order stop | PL, min Low from trigger main through native Order stop |
| Secondary point | PL, min Low | PH, max High |
| Primary gate | Order confirmation >= gate event; First not restricted here | Same in reflected coordinates |
| Secondary gate | First >= gate main AND confirmation > gate event | Same |
| Continuing primary >1 | parent-stop or reset-leg with Order boxTop > prior PH | parent-stop or reset-leg with Order boxBottom < prior PL |
| Reversal | Strict High > confirmed PH3 after decision | Strict Low < confirmed PL3 after decision |
| Post-secondary3 | Evaluate Orders but no PL4 | Evaluate Orders but no PH4 |

Main extreme windows include both endpoints. Physical Order must actually stop strictly after own confirmation and after gate in native resolver; earliest exact stop, later First, earlier Break wins. Secondary canonical ordinal positive; eligibility reset-leg or earliest direct parent-stop. Primary permits order-only zero if native resolver's other requirements hold. Primary direction and Order physical direction remain separate.

## PH-M02 — Ownership and numbering

Use the per-cycle seek/prospect algorithm in [Primary Structures](12_Primary_Structures.md). Only confirmed winner changes checkpoint. Secondary resets next primary local count to 1. Multiple cycles can confirm same source; resolve physical points by earliest group decision, choose highest number with role-order tie, earliest role identity retained. Strict successive progressive price may extend final number; equal price does not. A confirmed PH/PL at StopAll physical source replaces public StopAll ownership, not historical object. Primary callback reassigns obsolete matching exact StopAll parent-stop cause, preserving independent reset-leg causes; final label reconciliation uses source time. No retroactive unproved point or cross-direction recoloring. Procedures P04–P08, P10–P14, P22–P25 and P36–P43 define all local rules in the primary module.
