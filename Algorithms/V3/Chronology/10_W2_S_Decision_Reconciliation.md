# CP324 — W2 S decision chronology

Baseline: `c99b4c957e932d9ee70c492ca03ce80711447fc1`. Static source review; no runtime claim.

## CP324-S01 — S record

Frozen slotted SZone preserves separate A, Order, Reset, source and exact/main decision fields; null Order fields distinguish order-free construction, not all later shared-reconciled states.

[Source engine/pipeline/s_zone_detector.py:27–64](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L27-L64)

## CP324-S02 — S11–12

Public first-A-stop delegates native stop; resolved Order-backed route delegates first selected physical match, no later canonical replacement.

[Source engine/pipeline/s_zone_detector.py:253–276](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L253-L276)

## CP324-S03 — S13–14

Inclusive main range rejects reverse. Strict improvement retains earliest tie; <= bullish or >= bearish replaces on equality for last-source variant.

[Source engine/pipeline/s_zone_detector.py:279–312](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L279-L312)

## CP324-S04 — S15–17

Original reaction order first confirmation strictly after Order; bisect only sorted naive exact datetime. Nested candidate First strictly after Order First in index and time and strictly before confirmation, Break <= Order Break, confirmation <= Order, inclusive contained box, first eligible original ordinal. Simple uses last-tie Order Break through aligned Break.

[Source engine/pipeline/s_zone_detector.py:314–376](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L314-L376)

## CP324-S05 — S18–19

Reset owner via First index map, absent/reversed returns null; last-tie inclusive owner Break through Reset containing main. Trend qualifier strictly after A stop and <= crossing.

[Source engine/pipeline/s_zone_detector.py:378–401](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L378-L401)

## CP324-S06 — S20

Type3 Reset window (A-stop,deadline); owner confirmation <= A stop; skip owner already reset at/before A stop. Search first strict lower cross [Reset,deadline); failure of qualifier on first hit discards Reset route, no recross. Earliest exact cross wins, equal retains first stable Reset iteration.

[Source engine/pipeline/s_zone_detector.py:403–450](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L403-L450)

## CP324-S07 — S21–22

Type4 public valid noninternal Blue formation within [candidate source main,cross]. Aligned trend confirmations (A-stop,deadline), Break >= stop main; last tie from stop through Break. Search [max(aligned confirm,candidate event,A stop),min(next filtered aligned confirm,deadline)); equal windows skip. First hit without Blue discards candidate until next aligned reaction; no coarse fallback, no later recross.

[Source engine/pipeline/s_zone_detector.py:453–532](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L453-L532)

## CP324-S08 — S23

Type4 emits blue, preserves A fields and selected geometry; all Order and Reset fields null; aligned reaction number not stored.

[Source engine/pipeline/s_zone_detector.py:534–584](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L534-L584)

## CP324-S09 — S24

After-Order source start clamped by First and range start. Anchor accepted by index lower bound only; otherwise earliest main extreme then earlier containing lower remainder can replace on strict improvement or equality. Clamp/anchor path does not universally establish strictly post-confirmation evidence.

[Source engine/pipeline/s_zone_detector.py:587–626](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L587-L626)

## CP324-S10 — S29

Legacy before/after from Order boundary vs A stop main extreme. Preserve after when nested Advanced exists; otherwise exact-or-fallback candidate time strictly < Order First main means before; equality after.

[Source engine/pipeline/s_zone_detector.py:696–739](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L696-L739)

## CP324-S11 — S30

Compute full main stop..First; then if lower stop remainder exists use strict extreme there and later main candidate only if strictly better; equal retains stop main. Empty lower remainder uses full main candidate.

[Source engine/pipeline/s_zone_detector.py:741–783](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L741-L783)

## CP324-S12 — S31–32

Candidate exact first lower extreme equals level in [max(source,not_before),source+TF); absent returns max(source,not_before), even beyond candle end; public delegate, not proof.

[Source engine/pipeline/s_zone_detector.py:785–804](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L785-L804)

## CP324-S13 — S35–36

Ordinary qualifier first confirmation > behavior start and <= event; candidate crossing uses strict parent directional predicate.

[Source engine/pipeline/s_zone_detector.py:854–868](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L854-L868)

## CP324-S14 — S37 lower

Order stop queried independently from clamped start. Candidate gate max(scan start,candidate start); normal route earliest nonnull Reset Blue or ordinary trend qualifier sets start; fallback scans ungated by qualifier then upgrades candidate winner if qualified. Both null or same lower position rejects; earlier position wins, equal timestamp on different rows is not same-position tie.

[Source engine/pipeline/s_zone_detector.py:870–960](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L870-L960)

## CP324-S15 — S37 main

Only empty lower window enables main scan from containing main, clamped range start. Main candidate gate uses main timestamp; both raw gated candidate and Order crossing rejects before qualification, even unqualified candidate; Order red otherwise, qualified candidate blue, fallback only enabled; main time duplicated.

[Source engine/pipeline/s_zone_detector.py:962–993](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L962-L993)

## CP324-S16 — S38

Type3 blue with Reset owner number/exact time, all Order fields null; A/source/decision from inputs.

[Source engine/pipeline/s_zone_detector.py:996–1052](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L996-L1052)

## CP324-S17 — S39

Canonical Order stop then timing; pre-order race fallback-enabled with ordinal zero and candidate event as behavior start. Null ends, fallback discards decision, otherwise retains pre-route. Advanced nested geometry uses Order opposite source main extreme and nested confirmation gate. Simple aligned later required, last-tie Break..Break; after-order source computed even if unused by non-pre red. Normal race if needed. Red preserves pre source only if pre chosen; otherwise earliest extreme Order Break..decision main. Blue retains chosen source. Full provenance, no new Order search.

[Source engine/pipeline/s_zone_detector.py:1054–1223](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L1054-L1223)

## CP324-S18 — S40

Both independent Type3 and Type4 evaluated before selection; deadline selected Order confirmation or range end. Earliest exact event, Type3 wins equality; only if neither qualifies use Order-backed resolver, absent Order returns null.

[Source engine/pipeline/s_zone_detector.py:1225–1246](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L1225-L1246)

## CP324-S19 — S43

Dedup physical First/Break, first entry unless retained crossing null and new nonnull; malformed nonnull can block richer preference. Require datetime confirmation and crossing shape or compute strict lower crossing, confirmation<cross. Supplied valid-shaped crossing trusted locally. Sort stop,confirm,First,Break; select earliest stop >= S source main and < existing decision; inclusive source, not strictly after as docstring says. Replace color/Order/decision, clear Reset fields; retain A, price, source, formation type, order of zones. No creation cause rewrite; no universal Order-confirmation-before-S-start condition.

[Source engine/pipeline/s_zone_detector.py:1307–1421](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L1307-L1421)

## CP324-S20 — S44–46

Live dependency tuple includes Break main time, side, original zero ordinal, geometry/source/string prices/mode/intrabar/anchor; sets Reset event/owner First, Reset Blue time/number, public Blue time. Set collapses duplicates, does not include every field. Scope initially null.

[Source engine/pipeline/s_zone_detector.py:1424–1466](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L1424-L1466)

## CP324-S21 — S47

Type3/4 frontier decision event; Order-backed requires row presence from max(confirm,range_start) through decision (not proof of crossing or row inside range_end). Frontier max decision, Order Break main, aligned later trend Break main and confirmation if any.

[Source engine/pipeline/s_zone_detector.py:1468–1490](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L1468-L1490)

## CP324-S22 — S48–49

Dirty index 0..len inclusive; scope direction/TF/start index/range start. Same scope dirty=min supplied dirty and earliest dependency symmetric difference, else no prior. Key A ordinal/index/time/string price/stop tuple and Order number/signature/confirmation. Reuse iff through strictly < dirty, no null caching; detector._detect rebuilds ownership/audit even reused resolver result. Commit wrapper state only after success, detector mutation may survive failure. Correctness conditional on caller dirty evidence/signature sufficiency.

[Source engine/pipeline/s_zone_detector.py:1492–1525](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L1492-L1525)

## CP324-S23 — S50

Stateless public wrapper forwards all arguments then detect; no persistent continuation.

[Source engine/pipeline/s_zone_detector.py:1528–1551](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/s_zone_detector.py#L1528-L1551)

## CP324-S24 — OA stopped-A index

Map First->last ordinal/reaction; canonical sort (confirmation,First,Break,number,object); cache by exact A stop event.

[Source engine/pipeline/order_audit_engine.py:2520–2544](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2520-L2544)

## CP324-S25 — OA physical selection

Native candidate first; independent callback gate main/exact stop/end; reject null/unconfirmed Break, First before gate, confirmation <= stop. Map only exact identity to canonical object and recompute confirmation (no second local >stop check), otherwise number zero. If both candidates choose independent only if (First,confirmation) strictly earlier, ties native. No public reaction insertion.

[Source engine/pipeline/order_audit_engine.py:2546–2598](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2546-L2598)

## CP324-S26 — OA canonical choice

Bisect strictly later confirmation, first sorted entry with First>=gate main; cache hit including null; selection primarily confirmation not earliest First across all native candidates.

[Source engine/pipeline/order_audit_engine.py:2601–2620](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2601-L2620)

## CP324-S27 — OA audit

First physical identity creates immutable core metadata entry; append unique (A source time,stop exact) causes in encounter order. Audit starts from A confirmation, independent of later eligibility. Missing stop or Order returns.

[Source engine/pipeline/order_audit_engine.py:2622–2667](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2622-L2667)

## CP324-S28 — OA shared stop

Delegate stop level/source to chronology canonical provider; strict opposite predicate. Shared stop [max(confirm,range_start),range_end) with index if present else linear lower; no main fallback. Scan may return own confirmation row; S43 later excludes equality without rescan.

[Source engine/pipeline/order_audit_engine.py:2670–2712](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2670-L2712)

## CP324-S29 — Canonical stop provider

Mode A anchor if present else First-1, clamped start; expand preceding context tag, inclusive scan through Break, strict outer extreme retains first tie. Non-A requires number>1 else raises, uses preceding opposite reaction semantic box edge/source (not re-extremized). Independent zero only supported by A branch; no fallback for non-A zero.

[Source engine/pipeline/reaction_engine.py:1305–1367](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L1305-L1367)

## Boundary

Retain CP323 A ownership and freeze clauses, distinguish optional per-detector continuation from active entry, and do not infer accepted E/Order_B ownership from S geometry. [Evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP324_W2_S_Decision_Reconciliation.json).
