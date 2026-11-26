# CP336 — W2 S queue reconciliation

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`. Re-review of 20 existing transition IDs; no duplicate transitions. W2 remains open.

## CP324-S01 — S-M01; record SZone

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L27-L64) · [Owner specification](../05_S_Zone.md)

Frozen slotted SZone carries distinct parent A, physical Order, Reset, S source and decision fields. Nullable order fields do not establish original formation type after shared revision.

Handoff: Shared revision may attach Order provenance while preserving formation_type.

## CP324-S03 — S13–S14

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L279-L312) · [Owner specification](../05_S_Zone.md)

Inclusive main endpoints, reversed raises. Strict directional improvement first tie versus <=/>= last tie in separate helper. Return candle integer index and timestamp.

Handoff: Type3/4/simple last-tie; red nonpre first tie.

## CP324-S04 — S15–S17

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L314-L376) · [Owner specification](../05_S_Zone.md)

Native trend list first confirmation strictly >Order, bisect only sorted eligible original confirmations and exact naive input else original-order scan. Nested First index/time strictly after Order First, time strictly before Order confirmation, Break <=Order Break, confirmation<=Order confirmation and inclusive box containment. First eligible original ordinal wins. Simple last extreme Order Break..trend Break.

Handoff: Original ordinal and confirmation-sorted list distinct; Advanced nested preserves legacy timing.

## CP324-S05 — S18–S19

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L378-L401) · [Owner specification](../05_S_Zone.md)

Reset owner via First map; absent or mapped Reset main before owner Break null. Last tie inclusive owner Break..Reset main. Trend qualifier strictly after A stop and <=crossing.

Handoff: Native Reset fallback allowed; distinct from Order_B proof.

## CP324-S06 — S20

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L403-L450) · [Owner specification](../05_S_Zone.md)

Type3 sorted Reset in (A-stop,deadline); owner confirmation exists <=A stop, earliest owner reset must >A stop. First strict lower [reset,deadline), direct index call no null guard or coarse fallback. First crossing rejected without trend qualification, no recross. Earliest exact event, stable reset tie.

Handoff: Reset owner/time feed order-free S; distinct from B boundary break.

## CP324-S07 — S21–S22

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L453-L532) · [Owner specification](../05_S_Zone.md)

Type4 public valid Blue >=candidate source main and <=cross. Aligned trend confirmation in (A-stop,deadline), Break>=stop index, sorted rows. Last-tie source stop..Break, candidate equality-derived time may fallback; scan [max(confirmation,candidate event,A stop),min(next FILTERED aligned confirmation,deadline)). Equal window skips. Direct first strict hit without Blue discards until next aligned reaction; no recross or main fallback.

Handoff: Type4 public-only differs from ordinary Reset Blue map, which may include internal.

## CP324-S08 — S23

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L534-L584) · [Owner specification](../05_S_Zone.md)

Type4 blue, preserves A/selected geometry; Order/Reset fields null, aligned ordinal discarded.

Handoff: Later shared revision may attach Order, no creation inference.

## CP324-S09 — S24

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L587-L626) · [Owner specification](../05_S_Zone.md)

After-Order source start=clamp(bisect_left(main times,confirmation),stage start,First). Anchor accepted on index>=start alone, no upper anchor bound or exact-time recheck; normalized anchor_value required. Else earliest main extreme then if containing main earlier than start, scan lower remainder from confirmation and replace on strict improvement OR equality, returns containing main source.

Handoff: Docstring strictly after confirmation not universally established; computed source may be unused in final non-pre red.

## CP323-S36 — S25–S28

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L628-L694) · [Owner specification](../05_S_Zone.md)

A source event first lower equality with zone price in source main else open. First matching window [start,end) or open; trigger>start returns eligible immediately. Closed window Reset/Reset exception requires nonnull times, Blue1 source>start, Blue1 stop<Blue2 source, A source=Blue2 stop and both ordinals in range and exact reset kind. No additional Blue2 source>start guard. First matching decision. Fresh eligible list in original sorted A order.

Handoff: Calculation eligibility distinct from visibility and final hierarchy; full Blue ordinal mapping needed.

## CP324-S10 — S29

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L696-L739) · [Owner specification](../05_S_Zone.md)

Legacy after when Order opposite box edge<=stop main extreme B or >=R; before immediate. If after and nested exists keep after; else candidate event via exact-or-fallback helper, compare strictly <Order First main =>before; equality after.

Handoff: Do not steal Advanced by treating all earlier source geometry as pre-Order.

## CP324-S11 — S30

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L741-L783) · [Owner specification](../05_S_Zone.md)

Compute full main candidate inclusive A stop..First first; reversed may raise. Lower remainder [supplied stop,stop main end) without additional main-open clamp; empty returns full-main candidate. Nonempty earliest equal lower extreme; later main candidate selected only strictly better; equal keeps stop main.

Handoff: Selected price may come from lower evidence but output main source.

## CP324-S12 — S31–S32

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L785-L804) · [Owner specification](../05_S_Zone.md)

First lower equality in [max(source,not_before),source+TF); absent returns max(source,not_before), even beyond source candle end. Public delegate identical.

Handoff: Returned candidate event not universal proof; use exact-vs-fallback distinction.

## CP323-S37 — S33–S34

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L807-L852) · [Owner specification](../05_S_Zone.md)

Explicit formation_time if nonnull wins. Non-reset valid ordinal uses S default confirmation else source fallback. Reset missing broken level source fallback, otherwise first strict lower in source main, absent source open. Reset Blue qualifier requires valid reaction ordinal and first recorded valid Reset time<=candidate event; no same-main or internal requirement.

Handoff: A false-flag formation and Type4 public-only list are distinct contracts.

## CP324-S13 — S35–S36

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L854-L868) · [Owner specification](../05_S_Zone.md)

Ordinary trend qualification first sorted confirmation strictly >behavior_start and <=event. Candidate directional strict predicate delegates A-stop logic.

Handoff: No inferred lower proof from qualifier alone.

## CP324-S14 — S37 lower

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L870-L960) · [Owner specification](../05_S_Zone.md)

Order strict stop independently queried [max(start,range_start),range_end). Candidate gate=max(scan start,candidate_start or scan start). Normal qualifier earliest nonnull aligned Reset Blue or first trend strictly after behavior start, then max gate; fallback starts ungated by qualifier. Both null or same lower position rejects; distinct rows with equal timestamp do not satisfy tie guard. Order earlier red; candidate winner fallback upgrades only if Blue/ordinary qualifier by event.

Handoff: Same-position tie not timestamp equality.

## CP324-S15 — S37 main

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L962-L993) · [Owner specification](../05_S_Zone.md)

Only empty lower window enables main scan from containing main via bisect_right(original start)-1 clamped stage start. Candidate predicate strict with main-time gate; both candidate and Order crossing reject BEFORE candidate qualification, even unqualified. Order red otherwise, qualified candidate blue or enabled fallback; main time duplicated.

Handoff: Main-only branch asymmetry preserved, not normalized to lower race.

## CP324-S16 — S38

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L996-L1052) · [Owner specification](../05_S_Zone.md)

Type3 blue, Reset owner ordinal/exact reset time present, all Order fields null; separate A, S source and exact/main decision.

Handoff: Later shared revision may clear Reset fields.

## CP324-S17 — S39

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L1054-L1223) · [Owner specification](../05_S_Zone.md)

Canonical Order stop then timing. Pre-order simple attempt with ordinal zero and candidate event as behavior start, fallback enabled; null ends, fallback clears decision, other wins preserve pre source. Else Advanced nested uses Order opposite source MAIN extreme and nested confirmation gate; simple requires later aligned trend, last-tie Break..Break, evaluates after-Order source if no pre source even though final non-pre red ignores it. Normal race if needed. Red preserves pre source only when pre chosen, otherwise earliest extreme Order Break..decision main. Blue keeps chosen source. No new Order discovery.

Handoff: Creation versus consumption distinct; computing unused candidate may still raise.

## CP324-S18 — S40

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L1225-L1246) · [Owner specification](../05_S_Zone.md)

Deadline selected Order confirmation or range end. Both Type3 and Type4 computed before choosing; earliest exact event, Type3 wins equality. Only neither qualified uses order-backed route if Order present else null.

Handoff: Do not infer evaluation short-circuit from winner priority.

## CP324-S23 — S50

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L1528-L1551) · [Owner specification](../05_S_Zone.md)

Fresh SZoneDetector receives all positional inputs including optional initial_order_geometry, then detect. No persistent continuation wrapper here.

Handoff: Configured callback conditional; native default and optional LiveS service distinct.

## Findings and closure boundary

- CP336-F01: Strict post-Order wording of _candidate_after_order docstring is not a universal exact chronology predicate. Source uses clamped main index and anchor lower bound; detailed S24 already qualifies.
- CP336-F02: Type3 and Type4 direct lower index access has no local null-index fallback; ordinary decision fallback only empty lower rows. Type4 requires public Blue while ordinary Reset map may include internal.
- CP336-F03: Same lower position versus same main candle race distinct; main race rejects both raw predicates before qualifier, even unqualified candidate. Existing S37 documents this distinction.
- CP336-F04: Order-free Type3/4 both evaluated; later shared accepted stop can attach Order provenance without changing original formation type. Distinguish formation, creation and later consumption.

Cumulative queue review: 56/185. Seven remaining accessor sites; no overall W2 acceptance. Original historical records retained; no runtime, RAW payload or production change.

[Evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP336_W2_S_Queue_Reconciliation.json).
