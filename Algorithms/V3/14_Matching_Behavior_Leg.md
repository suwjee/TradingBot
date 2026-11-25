# MBL — Matching behavior qualification, activation and publication (V3)

**Conventions:** B = bullish, R = bearish. A strict trend stop means Low < level for B, High > level for R; improvement uses the same predicate. Main source identity and exact event chronology are separate. Preserve Decimal representation, operation order and stable ordering. Required record fields/defaults are in [record interfaces](../../Contracts/Declared_Record_Schemas.md); shared searches in [Index and cache contracts](20_Indexes_And_Caching.md). Procedure labels identify semantic operations, not required implementation symbols.


## MB-M01 — Qualification

Input accepted S/E and StopAll, not every provisional candidate. Build events in source-time order with StopAll priority 0, S 1, E 2, then source index; S/E at occupied StopAll index excluded and explicit calculation-invalid S/E excluded. Dedup (kind,index,time). Each StopAll resets reference and matching state; reference only if number>=3. For subsequent events before first qualification, advance dominant behavior with exact (kind,family,number), S number null. If unchanged owner skip. New count=1 clears accumulated confirmations, then append current exact decision. When exact key armed count>=2, qualify once for this reference: maximum reference decision and matching decisions, retain reference and decisive second behavior. Lower-priority interposition cannot replace current owner. No activation merely because qualified.

## MB-M02 — Activation and frozen geometry

In bearish coordinates level=reference StopAll main High, first lower High>level strictly after qualification activates; bullish reflection uses reference main Low and strict Low<level. Dedup reference/second source indexes. Sort activations by exact event,qualification,reference index,second index. Bearish MBL floor=min main Low from second source through activation main inclusive; bullish max main High, earliest tie. Freeze source/index/price; own stop strictly after activation below floor bearish/above ceiling bullish. Create independent cycle with id direction:cycle:reference index:second index. Simultaneous activations precede point commits; earlier/equal reversal wins. Skip new cycle if reference already promoted. MBL can be retained without stop (null fields), or refreshed by live continuation without changing geometry.

## MB-M03 — Public horizon and cap

Leg is public only when cycle activation and at least one primary confirmation decision are within visible horizon. Earliest such primary decision determines confirmation metadata. Source/index/price, reference/second, activation, confirmation and optional stop retained. Stop omitted when beyond horizon. Drawing cap source index+400 actual candle time if present, otherwise extrapolate from last main timestamp and timeframe; reversal clips cap at regime end. This is presentation, not a hard calculation stop. Procedures P09,P15–P21 in [Primary Structures](12_Primary_Structures.md) and TB84 in [Serialization](19_Serialization.md).
