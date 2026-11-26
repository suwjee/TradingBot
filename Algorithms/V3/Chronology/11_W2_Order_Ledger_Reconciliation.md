# CP325 — W2 Order_A / Order_B ledger chronology

Baseline: `c99b4c957e932d9ee70c492ca03ce80711447fc1`. Static source review only. Prior 102 transition records remain immutable.

## CP325-S01 — OA01

Deep-copy cause dictionaries; relabel parent/post/anchor types starting PH or PL if corresponding source in labels. Equality dedup in encounter order, no geometry change.

[Source engine/pipeline/order_audit_engine.py:25–37](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L25-L37)

## CP325-S02 — Order_B schemas

Frozen slotted stop, anchor and leg records distinguish dominant post-stop from independent anchor, exact Reset/strict break/physical confirmation and main source. Nested reaction object not recursively frozen.

[Source engine/pipeline/order_audit_engine.py:39–75](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L39-L75)

## CP325-S03 — OA02

Rank active lifetimes by priority,number,source time,index, earliest input ordinal on equal. Activation trigger or decision or source by truthiness. Sweep distinct stop events with inclusive activation and expiry, discard expired heap heads. Only identical behavior object owning exact event qualifies. Clamped main groups choose max(priority,number,source time,index,event); strict replacement, first full tie retained. Sort event,source index.

[Source engine/pipeline/order_audit_engine.py:77–136](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L77-L136)

## CP325-S04 — OA04–05

Anchor through First inclusive; strict Low min bullish/High max bearish, earliest equal. Anchor read even if last<first. Crossing from supplied lower position through end, indexed if present else linear strict scan; no main fallback or retry on index miss.

[Source engine/pipeline/order_audit_engine.py:170–195](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L170-L195)

## CP325-S05 — OA06 entry

Validate direction before empty shortcut. Parent extreme Low bullish/High bearish. Truthy optional boundary/cross callback; default crossing uses bisect_right Reset time, excluding rows equal to Reset. Callback trusted subject to later checks.

[Source engine/pipeline/order_audit_engine.py:198–239](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L198-L239)

## CP325-S06 — OA06 ordering

Trend tuples sorted confirmation,First,Break,zero ordinal; group First. Opposite same keys with one-based number. CP322 Reset provider non-null events only, sort event,owner First,ordinal. Stops sort event,source time,index,type; anchors source time,index,priority,number,type; A trigger times sorted. Native chronology fallback is not new exact proof.

[Source engine/pipeline/order_audit_engine.py:240–289](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L240-L289)

## CP325-S07 — OA06 ownership

For each Reset choose last same-First trend tuple with confirmation strictly before Reset. Latest dominant stop event and anchor source time strictly before owner First main, last sorted tie; anchor index>First rejects without retry. Boundary must strictly extend anchor extreme and source index strictly before First. Stop and anchor independent.

[Source engine/pipeline/order_audit_engine.py:291–324](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L291-L324)

## CP325-S08 — OA06 expiry/physical

First strict post-Reset boundary break (default lower only), clamp to main. Next accepted A trigger strictly after owner First expires if mapped main<=break main. First opposite confirmation-sorted native reaction with First>=break main and confirmation>exact break; same-main First permitted, equality confirmation rejected. Store independent provenance, preserve Reset iteration and duplicate legs.

[Source engine/pipeline/order_audit_engine.py:326–375](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L326-L375)

## CP325-S09 — OA07–09

Live direction fixed, dirty main 0..length. Dirty null at end; old lower coverage upper-bound previous last time in current array. Boundary key first,last, current first then prior only last<dirty main, else recompute. New queried-only dictionaries.

[Source engine/pipeline/order_audit_engine.py:378–415](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L378-L415)

## CP325-S10 — OA10

Crossing key Reset time,Decimal level using numeric equality, including null cached. Prior non-null reused only strictly before dirty or dirty null, latest lower exists and old<=latest. Otherwise search after Reset; prior key enables max(original left,min(old coverage,dirty lower)). Commit queried caches/last time only after successful discovery; caller guarantees prefix/dirty validity.

[Source engine/pipeline/order_audit_engine.py:416–439](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L416-L439)

## CP325-S11 — OA11

Accepted A excludes invalid source pair; ordinal−1 access without local validity guard, default confirmation then S first stop tuple[2]. S/E parent stop tuple[1]; StopAll explicit event. Open lifetimes retained. Dominant stops separate from anchors of all accepted behaviors incl unstopped. Per source pair rank priority,number,type, strict replacement. Truthy finder override, pass accepted A trigger times not source.

[Source engine/pipeline/order_audit_engine.py:442–520](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L442-L520)

## CP325-S12 — OA12 / OrderMatch

Match number,reaction,confirmation,stop level/source,nullable crossing,route labels,nullable parent creation event. Feedback signature sorted tuples includes stop type/index/event, anchor identity/extreme, Reset identity/index/level/time, boundary/source, strict break, physical identity. Omits post-stop source time, Reset confirmation, leg source time, physical number/confirmation; preserves duplicates; Decimal tuple numeric not byte equality.

[Source engine/pipeline/order_audit_engine.py:523–550](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L523-L550)

## CP325-S13 — OA13

Fresh ledger/caches/indexes. Four input-order First/confirmation passes; trend triples stable sort confirmation only; opposite arrays supplied order. Opposite resets grouped supplied order. Last duplicate First map; first duplicate physical identity canonical position. No local sortedness verification.

[Source engine/pipeline/order_audit_engine.py:557–651](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L557-L651)

## CP325-S14 — OA14–15

Ignore context_start; exact canonical object at valid ordinal caches stop by ordinal; noncanonical uncached canonical provider CP324-S29. No context-only stop manufacture.

[Source engine/pipeline/order_audit_engine.py:653–686](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L653-L686)

## CP325-S15 — OA16

No finder null. Gate containing main/exact start. Blocked First at original gate advances First+1, search event First. Prior owner latest opposite confirmation<=search event via bisect; first stored Reset with search_event<Reset<=candidate confirmation restarts at Reset main/exact event. Require canonical identity, return canonical object/confirmation without repeating candidate checks. allow_bounded_continue unused locally, restarted assigned not read; no local progress guard.

[Source engine/pipeline/order_audit_engine.py:689–761](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L689-L761)

## CP325-S16 — OA19–20

Cache nullable result by start/deadline/bounded/E flag/confirmation_after. Geometry optional confirmation filter; native lower bound First at gate main then initial confirmation threshold loop, followed by blocked same-gate skip (no threshold recheck). E exception exact (start,gate) and confirmation>start. Prefer restart geometry with supplied deadline==range_end or deadline<geometry confirmation; independent stop/cross evaluated even then. Otherwise geometry only if independent crossing absent AND independent absent or geometry First strictly earlier; else independent; empty pool null.

[Source engine/pipeline/order_audit_engine.py:809–918](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L809-L918)

## CP325-S17 — OA21–22

Merge direct by physical identity, compute canonical stop/cross; replace only earlier confirmation/First/Break. At most one parent-stop among current map, min confirmation,First,Break; remove parent-stop from losers, retain independent reset-leg with null parent creation time; otherwise remove row.

[Source engine/pipeline/order_audit_engine.py:921–979](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L921-L979)

## CP325-S18 — OA23–24

Cache start/deadline/bounded/trend/E flags, copy on hit. Direct and optional trend continuation, then each B leg with First strictly after start; existing geometry retained with reset-leg label appended uniquely. Enforce parent owner, earliest actual crossing (range_end only if none) clipped by deadline; retain confirmation<=deadline, stable sort crossing or range_end then First. First-order convenience filters nonnull crossings.

[Source engine/pipeline/order_audit_engine.py:982–1086](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L982-L1086)

## CP325-S19 — OA25–29

Hard Reset in (start,end] via upper bound. New physical confirmation tuple inserted after equals; pending append if sorted audit dict else reset sorted view. Clear ledger/index in place then carried/post-stop caches, not all geometry caches. Carried invalidation drops creation index/pending append; post-stop invalidation clears results/sorted view/pending. Cause-only changes not automatically post-stop flush.

[Source engine/pipeline/order_audit_engine.py:1089–1132](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1089-L1132)

## CP325-S20 — OA30

Truthy B list invalidates carried upfront. New physical row canonical stop/cross, empty parent set then index; existing geometry untouched. Full cause dictionary includes stop/anchor/Reset/boundary/break/physical provenance, strings for three prices. Equality dedup, stable sort stop,Reset,strict break,physical pair; invalidate carried on unique cause. No local acceptance revalidation/rollback.

[Source engine/pipeline/order_audit_engine.py:1135–1199](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1135-L1199)

## CP325-S21 — OA31

Primary reparent parent-stop StopAll-prefix same source TIME, non-null equal stop strictly after decision; matching cause relabelled only on selected direct identity otherwise revoked. B post-stop relabel exact source pair/equal stop/strict decision bound, independent of direct identity. B anchor relabel exact pair, truthy Reset identity and Reset First main>=decision; independent of stop. Delete all causeless rows, filter index in place, flush post-stop on revocation and carried on change/revocation. Sequence reset history untouched.

[Source engine/pipeline/order_audit_engine.py:1202–1248](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1202-L1248)

## CP325-S22 — OA32–36

PH bearish / PL bullish owner only; strict primary stop lower (decision,range_end), direct confirmation_after=stop (OA20 caveat). Dependency stop,null or stop,repr(direct),str(level),source index/time,cross. Reparent before null-direct return, add selected row/index if absent and exact primary parent-stop cause, invalidate carried on addition.

[Source engine/pipeline/order_audit_engine.py:1250–1310](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1250-L1310)

## CP325-S23 — OA37–39

Last source wins label map. Parent tuples relabel prefix-specific only, set dedup; B helper accepts either PH/PL prefix using supplied map, deep-copy/dedup. Mutate only changed collections and invalidate carried; no rediscovery/index change.

[Source engine/pipeline/order_audit_engine.py:1312–1337](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1312-L1337)

## CP325-S24 — OA40

S creator veto by invalid or accepted E-owned source pair; sequence reset between parent source and stop veto. Query pool S bounded/E trend flags; append direct if identity absent even after earlier deadline/single-owner filtering, no second enforcement. Only parent-stop-labelled matches register. Preserve geometry; new row/index then cause E number or sequence StopAll override (empty family). Exact cause set; carried invalidated for new entry or earlier existing creation (conservative on malformed causes). Later/equal cause does not alter earliest creation availability. Deferred append only matching prior ledger, valid payload, expected count. Distinguish candidate-local one-owner rule from final export dedup.

[Source engine/pipeline/order_audit_engine.py:1339–1433](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1339-L1433)

## CP325-S25 — OA41

Static method explicit self argument; first opposite First>=start and confirmation>=start; singleton stop/cross and false flag or empty; no creation.

[Source engine/pipeline/order_audit_engine.py:1436–1456](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1436-L1456)

## CP325-S26 — OA42–43

Cache strict opposite crossing start,level including null. Lower [max(start,range_start),range_end), less iff Order not bearish, via owner first-cross service. Map main/exact event, no coarse fallback. Public delegate.

[Source engine/pipeline/order_audit_engine.py:1459–1484](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1459-L1484)

## CP325-S27 — OA44

Unconsumed S only exact blue, confirmation/level non-null. Compute strict crossing require >=parent stop (equality allowed). Copy recorded geometry namespace, carried-live null creation; no remapping/ledger mutation.

[Source engine/pipeline/order_audit_engine.py:1487–1521](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1487-L1521)

## CP325-S28 — OA45–47

Lazy initial A audit records: compute crossing, normalize level, number/source; stable First time,confirmation,First,Break sort. Reuse records in First buckets and confirmation-sorted index, preserve references. Match conversion drops First time, supplied route/null creation. Entry conversion computes cross. No local invalidation for mutating initial audit.

[Source engine/pipeline/order_audit_engine.py:1524–1609](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1524-L1609)

## CP325-S29 — OA48–49

Gate-owned initial First exact containing main; confirmation>=parent stop and crossing>=parent stop, min crossing then First. Carried creation times earliest parent-stop cause if multiple, plus every B physical confirmation, without dedup here.

[Source engine/pipeline/order_audit_engine.py:1612–1642](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1612-L1642)

## CP325-S30 — OA50

Native carried index validation under local Decimal context: exact dict, accepted cause containers/element shapes, skip no-creation rows after shape checks, exact datetime and identical tzinfo object for all dates, cross tuple shape/int position, exact ints number/source/First/Break, allowed price types finite after normalization. Per-row dedup created events, original ordinal; sort. Invalid/exception null, legacy owns exception ordering; no index bounds validation.

[Source engine/pipeline/order_audit_engine.py:1644–1697](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1644-L1697)

## CP325-S31 — OA51

Consume deferred append before checks. Same ledger object/expected count, validate new rows; compatible timezone when both event lists nonempty, adopt new if old empty. Insert old ordinal offset and extend old entries; no rollback.

[Source engine/pipeline/order_audit_engine.py:1699–1720](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1699-L1720)

## CP325-S32 — OA52

Null lifecycle decision empty; cache decision,parent stop. Native index unique ordinals in strict creation interval (decision,stop), ledger order. Fallback lazy creation scan, same interval. Require confirmation<=stop, stored crossing nonnull>=stop. Initial A separate inclusive First [decision,stop] same confirmation/cross guards, no cross-route dedup. Sort crossing then negative First; stable accepted-before-initial tie. Caller invalidation critical.

[Source engine/pipeline/order_audit_engine.py:1722–1795](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1722-L1795)

## CP325-S33 — OA53–54

Eager accepted-live cache stop,index length. Initial confirmation strictly >stop; audit tuple-index bound exact 2^63−1 sentinel, current row confirmation used without separate >stop recheck. Skip incomplete geometry, malformed/absent cross recomputed locally. Require crossing>parent stop and own confirmation, no sequence Reset (stop,cross]. Dedup identity strictly earlier (cross,confirmation,First), keep insertion rank; final sort cross,confirmation,-First. Return list copy.

[Source engine/pipeline/order_audit_engine.py:1798–1877](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1798-L1877)

## CP325-S34 — OA55–57 initial validation

Lazy key cross,confirmation,-First; exact native datetime/timezone identity, exact ints, finite exact Decimal and crossing shape. Non-native query eager fallback. Initial records materialized before validation try; validate all under localcontext then only cross>confirmation. Conflicting same identity event pair disables optimized initial view; False fallback, not proof price/source equality.

[Source engine/pipeline/order_audit_engine.py:1879–1934](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1879-L1934)

## CP325-S35 — OA55 audit runs

Build full audit if None else pending. Validate exact index types, row dict, allowed price type/finite normalized, confirmation matches index; null crossing requires cached known-null. Include cross>confirmation; conflict with initial event pair fallback, no audit-audit pair conflict check. Key plus indexed First/Break. Copy tier mapping, merge older equal bit_length tiers into new runs; clear pending, assign dict or False; exceptions fallback. False+pending can attempt copy and fail again.

[Source engine/pipeline/order_audit_engine.py:1935–1993](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1935-L1993)

## CP325-S36 — OA58–59

Capture first hard Reset strictly after parent stop. Per run begin cross>stop, terminate at cross>=Reset, require confirmation>stop. Merge audit runs full key then initial first on equal main key; first physical identity emitted. Lazy iteration errors outside validation catches; no empirical parity claim.

[Source engine/pipeline/order_audit_engine.py:1994–2017](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1994-L2017)

## CP325-S37 — OA60–61

Disowned-S-only false if missing/no parent causes, B cause or initial identity. Otherwise every cause parent-stop S and source in disowned set or equals prospective source. Gate-owned veto only for E parent-stop use if initial confirmation strictly earlier than zone Order First. Neither creates cause.

[Source engine/pipeline/order_audit_engine.py:2020–2043](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2020-L2043)

## CP325-S38 — OA62–63 rebuild start

Set accepted E source pairs, project invalid S roots and occupied E to source times; filter prior parent-stop causes (S invalid times rejected), shallow snapshot, clear, register B, then original S and numbered E/StopAll parents. Supplemental S not registration list. Skip recovery if numbered E identity already present.

[Source engine/pipeline/order_audit_engine.py:2046–2104](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2046-L2104)

## CP325-S39 — OA62 recovery

Missing identity geometry uses prior CP323-S44. Recover valid prior parent causes and initial accepted A pairs skipping null; if no causes and carried-live S parent, first matching source pair/Order identity in original then supplemental S recovers A creation. Explicit nonnull Order parent cause time enables parent label from E/StopAll; actual event zone parent stop, family override. Refilter; no cause no insert. Recompute strict crossing, store original stop level/geometry, index.

[Source engine/pipeline/order_audit_engine.py:2124–2204](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2124-L2204)

## CP325-S40 — OA62/64–65 retention

Retain prior valid parent causes even if not consumed; current geometry wins and union parent set else restore prior shallow entry/index. Prior B-only not restored by OA62 solely on B. Return sorted numbered source time,index. Ensure snapshot then rebuild; absent prior identity restore if remaining non-invalid S cause or B, index; existing skipped not merged by ensure. Unconditional carried invalidation on success.

[Source engine/pipeline/order_audit_engine.py:2206–2288](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2206-L2288)

## CP325-S41 — OA66–69

Parent-stop key type,family,event,source time. Collect S first accepted A source filter; E parent tuples sorted by str and accepted A filter then B causes. Merge physical identity with First inclusive range or required identity. First geometry/cross wins, explicit null retained, only missing key invokes crossing. Later distinct full-dict causes appended; first-list duplicates preserved.

[Source engine/pipeline/order_audit_engine.py:2291–2401](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2291-L2401)

## CP325-S42 — OA70–71

Final prepared view one owner per exact parent-stop cause key by min confirmation,First,Break; first tie, owner object identity. Keep nonparent causes/duplicate winning causes; drop causeless row, preserve order. Required identity bypasses range not cause filter.

[Source engine/pipeline/order_audit_engine.py:2404–2459](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2404-L2459)

## CP325-S43 — OA74

Missing either index false, otherwise int physical pair membership in internal identities; zero allowed.

[Source engine/pipeline/order_audit_engine.py:2508–2514](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2508-L2514)

## CP325-S44 — LC25 cross-owner invalidation

Filter accepted A audit by accepted source; union inherited First veto and invalid-A pending-S leg blocks; remove accepted initial First times (parse strings). E-only exception exact stop equal accepted E stop, First same stop main and blocked not inherited, invalid A source<=First<exact stop, opposite confirmation>stop. Return accepted ledger and blocks, optional set update; no global unblock.

[Source engine/pipeline/lifecycle_engine.py:606–693](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/lifecycle_engine.py#L606-L693)

## CP325-S45 — Decimal / identity primitive

Existing Decimal instance unchanged; other numeric input Decimal(str(value)). Physical identity int First/Break, scoped by direction/segment externally; no price or parent fields in pair.

[Source engine/pipeline/core_utils.py:51–66](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/core_utils.py#L51-L66)

## Cross-owner qualifications

- CH100 candidate-local single parent owner is not a blanket invariant of intermediate registration: OA40 may append a direct identity removed by candidate filtering without reapplying owner gate. Final OA70 independently enforces exact cause-key ownership on prepared rows.
- CH101 eager accepted-live index uses integer sentinel and current entry confirmation, not universal strict confirmation recheck for arbitrary input; optimized lazy branch does recheck. Do not claim runtime equivalence.
- Order_B feedback identity omits specific fields; equality does not prove complete record equality or Decimal lexical equality. Live callback is conditional; active public path does not establish per-detector continuation.
- Creation and use routes distinct. A/S/E/StopAll ownership and primary reparent do not change physical identity; final view filtering not a new trading decision.

[Detailed transition register and prior links](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP325_W2_Order_Ledger_Reconciliation.json). [CP324](10_W2_S_Decision_Reconciliation.md). Full W2 and empirical acceptance remain open.
