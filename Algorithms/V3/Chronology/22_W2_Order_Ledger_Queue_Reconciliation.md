# CP337 — W2 Order ledger queue semantic reconciliation

Baseline: `c99b4c957e932d9ee70c492ca03ce80711447fc1`. Direct source-only review: 39/39 Order Audit queued records and three additional accessor sites. Cumulative 95/185 queue, 5/9 supplemental accessor reviews. W2 remains **NOT ACCEPTED** (CP331-F05, CP333-R01/R02 open).

Physical identity (First, Break) within owner direction; parent-stop/reset-leg create, carried-live/accepted-live consume, final prepared audit projects. Preserve Decimal and independent exact event/main time.

## CP323-S43 — OA17–18

Optional E trend route excludes internal trend and non-continue geometry, invokes confirmation but discards its value, requires First strictly after trend confirmation then canonical physical lookup. Cached null/position; no final canonical confirmation recheck.

Handoff: E trend-leg candidate is not an independent noncanonical creator.

[Source 776–806](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L776-L806). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP323-S44 — OA62

Absent ledger identity uses opposite First lookup only if Break agrees, otherwise reconstructs recorded box/source fields with internal false. No new native Reaction is published; later valid cause still required.

Handoff: E supplies geometry, OrderAudit owns accepted insertion.

[Source 2105–2122](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2105-L2122). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP324-S26 — OA77

Native stopped-A selection sorted primarily by confirmation; upper bound excludes equal stop, scan for First>=gate main. Cache exact stop including null. Not earliest First globally.

Handoff: S gate and chronology provider; independent callback evaluated separately.

[Source 2601–2620](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2601-L2620). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP324-S27 — OA78–79

Normalize A price, resolve A confirmation/first strict stop, first physical match; null at either gate means no record. Compute canonical stop even for existing identity. First geometry and A pair retained; distinct source/stop pairs append. No crossing or E index created.

Handoff: A→S creation precedes eligibility/visibility filters; accepted A causes later filtered.

[Source 2622–2667](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2622-L2667). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP324-S28 — OA80–82

Canonical stop provider unchanged. Opposite bearish High>level else Low<level; exact lower [max(confirm,range_start),range_end). Index used for nonempty interval, miss returns null without scan. Else sequential first strict crossing, map main and exact event. Can hit confirmation row.

Handoff: S/E share stop geometry, consumption gates own strict event threshold.

[Source 2670–2712](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2670-L2712). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S01 — OA01

Deep-copy cause dictionaries, relabel PH/PL role fields by corresponding source time. First equal duplicate retained; original untouched.

Handoff: Primary labels change provenance, not geometry.

[Source 25–37](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L25-L37). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S02 — Order_B schemas

Frozen/slotted wrappers distinguish dominant stop, geometric anchor, reset Reaction/event, boundary source and physical opposite Reaction. Nested objects not recursively immutable.

Handoff: Finder outputs provenance; registration establishes accepted entry.

[Source 39–75](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L39-L75). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S04 — OA04–05

Read anchor before loop; inclusive main boundary, strict improvement retains earliest equal. Lower crossing from supplied left through end, strict Low< or High>, index or linear only if absent, no main fallback.

Handoff: Boundary main geometry and lower crossing proof separate.

[Source 170–195](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L170-L195). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S05 — OA06 entry

Validate direction before empty shortcut; missing stops/anchors empty. Truthy boundary/cross callback selected; default upper bound excludes Reset-equal rows. Returned callback values trusted except downstream explicit gates.

Handoff: Native/live dispatch conditional; no universal guarantee for arbitrary callbacks.

[Source 198–239](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L198-L239). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S06 — OA06 ordering

Both Reaction lists use default confirmation. Same direction tuple zero-based ordinal/group First; opposite one-based original number. Non-null Reset sort event,owner First,ordinal; stops, anchors and A triggers sorted separately. Break-open fallback not observed crossing.

Handoff: CP322-E14/E15/E16; coordinate/ordinal distinctions.

[Source 240–289](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L240-L289). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S07 — OA06 ownership

For each Reset last same-First candidate with confirm<Reset. Latest stop and independent anchor strictly before current First main; distinct tie ranks. Reject anchor index after First without retry. Require strict boundary extension and source before First.

Handoff: Dominant stopped lifecycle eligibility does not determine geometric anchor.

[Source 291–324](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L291-L324). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S08 — OA06 expiry/physical

Map nonnull break to main. Next accepted A trigger strictly after current First expires when mapped main<=break main. First sorted opposite First>=break main and confirmation>exact break; same-main First eligible. Preserve ordinal and all provenance, no leg dedup.

Handoff: Accepted A expiry main-owned, confirmation lower chronology-owned.

[Source 326–375](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L326-L375). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S09 — OA07–09

Live finder direction fixed, dirty index 0..length. Compute dirty lower and old coverage using current array. Boundary prior reuse only last<dirty main, else recompute. New queried-only cache.

Handoff: Caller guarantees dirty frontier/unchanged prefix.

[Source 378–415](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L378-L415). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S10 — OA10

Reset-time/level key native Decimal equality incl null. Reuse prior crossing only before dirty or no dirty and within latest lower coverage. Else resume max(after Reset,min(old coverage,dirty lower)) only if key existed. Publish queried caches and last time on successful discovery.

Handoff: Live geometry reuse does not own acceptance.

[Source 416–439](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L416-L439). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S13 — OA13

Four input-order First/confirmation passes; only trend triples stable-sorted by confirmation. Group opposite resets supplied order; last duplicate First mapping, first duplicate identity position. Fresh ledger/index/caches; immutability and aligned sorted arrays owner premises.

Handoff: E constructor sorts resets and S roots, supplies initial audit and callbacks.

[Source 557–651](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L557-L651). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S14 — OA14–15

Ignore context start. Cache stop by valid one-based ordinal only when exact canonical object matches; noncanonical geometry delegates uncached. No synthetic contextual stop.

Handoff: Chronology canonical_order_stop owns price/source.

[Source 653–686](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L653-L686). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S15 — OA16

No finder null. Blocked First at original gate advances First+1. Prior owner latest confirmation<=event; first stored Reset with event<Reset<=confirmation restarts at Reset main/exact event. Canonical physical identity required; stored confirmation returned without repeat checks. Bounded flag unused locally, no progress guard.

Handoff: E direct geometry callback supplies candidate only.

[Source 689–761](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L689-L761). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S17 — OA21–22

Compute stop/cross before duplicate rank. Per identity strict earlier confirmation/First/Break replaces entire match. Candidate-map parent owner min rank, strip losing label, retain independent reset-leg with null parent cause time or delete. Zero owner allowed.

Handoff: Candidate reduction distinct from OA40 supplement and OA70 final arbitration.

[Source 921–979](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L921-L979). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S19 — OA25–29

Hard reset in (start,end]. Insert confirmation tuple right of equals; pending append only if sorted view dict else reset view. Clear ledger/index in place then carried/post-stop caches. Carried drops creation index/pending append; post-stop clears sorted view/pending. Not all geometry caches cleared.

Handoff: E sequence reset setter separately clears four query caches.

[Source 1089–1132](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1089-L1132). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S21 — OA31

Reparent StopAll parent causes by source TIME, nonnull equal stop strictly after decision; selected direct identity new label, other matching roles revoked. B stop relabel exact pair/equal stop/strict bound; anchor independently Reset First>=decision. Revoke causeless rows, filter index, flush post-stop; carried if changed. No reset-history removal.

Handoff: Primary owns decision/label, Order owns cause revocation and relabel.

[Source 1202–1248](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1202-L1248). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S22 — OA32–36

PH bearish / PL bullish only. Strict lower stop (decision,range_end), direct confirmation threshold requested but no universal final recheck after blocked skips. Reparent before null-direct return. Dependency stop/null or repr/direct, string level/source/cross. Registration retains existing geometry and indexes new physical row.

Handoff: Primary callback owns activation; Order owns actual direct registration.

[Source 1250–1310](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1250-L1310). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S23 — OA37–39

Last primary source in map wins. Parent tuple labels prefix-specific; B relabel matches either PH/PL with map, deep copy/equality dedup. Carried invalidation only on change; no geometry or index change.

Handoff: Final labels do not rediscover Orders.

[Source 1312–1337](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1312-L1337). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S24 — OA40

S creator veto by exact invalid/occupied E pair then hard reset (source,stop]. Query S/E flags, supplement absent direct identity even after deadline/one-owner reduction, no repeat enforcement. Register parent-stop labels only; preserve geometry, exact cause, E number or sequence StopAll override. Carried invalidation new identity or earlier parent event; later/equal cannot change earliest creation. Optional append same ledger and expected count.

Handoff: E registers before post-stop query; final prepared audit separately filters per cause.

[Source 1339–1433](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1339-L1433). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S25 — OA41

Static helper explicit self; first opposite First>=start and confirmation>=start; singleton stop/cross (possibly null), false flag. No reset/blocked/acceptance filtering or ledger mutation.

Handoff: Visual selection is not creation.

[Source 1436–1456](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1436-L1456). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S26 — OA42–43

Cache strict opposite crossing (start,level) incl null. Lower half-open [max(start,range_start),range_end), less unless bearish. Map hit to main timestamp/exact event, no coarse fallback. Public delegate unchanged.

Handoff: E first-cross service owns indexed-vs-linear dispatch; time equality to start possible.

[Source 1459–1484](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1459-L1484). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S27 — OA44

Exact blue S and nonnull confirmation/level. Crossing must exist and >=parent stop. Copy recorded geometry namespace, no canonical remap, carried-live null creation.

Handoff: Inherited consumption does not create Order.

[Source 1487–1521](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1487-L1521). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S28 — OA45–47

Lazy initial ledger materialization normalizes level and computes crossing; sort First time,confirm,First,Break; First buckets and confirmation view reuse records. Match conversion preserves geometry and supplies route/null creation. Assumes immutable initial mapping.

Handoff: Initial A source-filtered ledger owned by S/Bridge.

[Source 1524–1609](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1524-L1609). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S29 — OA48–49

Gate-owned initial First exact main, confirmation/cross>=parent stop, min cross then First. Carried creation list earliest parent-stop cause plus each B physical confirmation, no dedup here.

Handoff: Gate-owned route later used as veto, not extra creator.

[Source 1612–1642](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1612-L1642). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S30 — OA50

Validate exact row/containers, nonempty tuple causes, B dicts; skip no-creation after shape checks. Exact datetime/tzinfo identity, crossing shape, int fields, finite normalized price under local Decimal context. Unique events per row sorted with original ordinal. Exception returns null to legacy; no bounds or complete semantic validation.

Handoff: Optimization index only; legacy owns exception ordering.

[Source 1644–1697](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1644-L1697). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S31 — OA51

Consume pending append before validating same ledger and size. Validate appended rows only; timezone compatible when both event lists nonempty. Original ordinal offset incl skipped rows. Insert then extend in place, no rollback.

Handoff: Earlier existing creation invalidation prevents stale prefix reuse.

[Source 1699–1720](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1699-L1720). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S32 — OA52

Null lifecycle decision empty; key decision,stop. Indexed events strictly inside interval and unique ordinal order or legacy scan; confirmation<=stop and crossing>=stop. Initial A separate inclusive First window, same confirmation/cross guards, no cross-route dedup. Sort crossing then later First; carried-live null creation.

Handoff: E receives carried candidates before current parent registration.

[Source 1722–1795](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1722-L1795). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S33 — OA53–54

Eager accepted route initial confirmations strictly later; ledger tuple bound sentinel, no universal current-row confirmation recheck. Skip incomplete geometry, recompute malformed/null crossing locally; crossing>both stop and own confirmation, reject reset (stop,cross]. Dedup earlier rank, final sort cross,confirm,later First. Key stop/index length, list copies.

Handoff: Physical membership and reset invalidation critical; E reorders equal-cross groups.

[Source 1798–1877](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1798-L1877). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S34 — OA55–57

Native optimized iterator only exact query datetime/tzinfo identity, exact int geometry, finite exact Decimal and valid cross tuple. Initial records materialized before validation catch; only cross>confirm. Conflicting event pair disables fast route; equal pair not proof of price/source equality.

Handoff: Non-native fallback eager; no runtime parity assertion.

[Source 1879–1934](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1879-L1934). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S35 — OA55 audit runs

Validate full index if view None else pending rows; exact indexed confirmation, native geometry; known-null cross required in cache. Initial/audit event-pair conflict disables fast route. Sort new keyed rows and merge equal bit-length tiers, copy mapping; pending cleared and view dict or False. No audit-audit conflict check; generator errors outside catch.

Handoff: Append preserves older runs; rebuild/removal invalidates, cause-only update not geometry.

[Source 1935–1993](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1935-L1993). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S36 — OA58–59

Capture first reset strictly after stop. Per run begin cross>stop, terminate cross>=reset, require confirmation>stop. Merge audit runs full key then initial/audit main key, initial equal-key wins; first identity once. Lazy capture/consumption distinct.

Handoff: E groups exact crossing ties and applies later First.

[Source 1994–2017](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L1994-L2017). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S37 — OA60–61

Disowned-S-only false for absent/no parent causes, any B or initial identity; else every cause parent-stop S at disowned/prospective time. Gate-owned veto only for parent-stop-labelled E when initial confirm strictly before zone First. Equality does not block; neither creates cause.

Handoff: E race/reconciliation uses veto; invisible behavior not automatically disowned.

[Source 2020–2043](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2020-L2043). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S38 — OA62–63

Set accepted E pairs, project invalid/occupied S to times. Snapshot filtered parent-stop causes (B shallow), clear/index rebuild, register B then original S and numbered E/StopAll parents. Supplemental S not registration list; skip absent-identity recovery when present.

Handoff: Invalid S cause filter time-only differs from registration pair veto.

[Source 2046–2104](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2046-L2104). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S39 — OA62 recovery

Recover prior valid parent causes and initial accepted A nonnull pairs. Only absent causes plus carried-live S enables exact original/supplemental S match to recover A. Explicit nonnull cause marker enables parent creation with zone stop event, E number or StopAll label. Refilter; no valid causes no insertion. Compute crossing, preserve stored level, insert/index.

Handoff: Consumption alone never manufactures parent cause; retention preserves independently valid identity.

[Source 2124–2204](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2124-L2204). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## CP325-S43 — OA74

Missing either index false, otherwise normalized int First/Break membership in supplied internal set; zero valid, no bounds test.

Handoff: Visibility classifier does not alter calculation ledger.

[Source 2508–2514](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2508-L2514). B05 intersections: [CP337 evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP337_W2_Order_Ledger_Queue_Reconciliation.json).

## Accessors

- **CP322-E14**: Default flag true; same-direction confirmation sort with zero ordinal, group by First; returned time fallback Break open not observed strict crossing. Selected confirm strictly before Reset.
- **CP322-E15**: Default flag true, opposite-direction confirmation, original one-based number; First>=crossing main and confirm>exact crossing. Break-open fallback remains returned coordinate only.
- **CP322-E16**: Truthy precise second_time delegates reset_time; otherwise strict Low/High crossing inside Reset main half-open window; index or linear only absent index, null on miss; nonnull event sorted event/from First/ordinal; default crossing strictly after Reset.

## Qualifications

- CP337-F01: OA-M02 combined stopped-A choice not locally cached, only native cached. Optional independent callback runs per invocation.
- CP337-F02: OA-M03 at most one candidate-local parent-stop owner; OA40 may supplement direct; OA70 final exact-cause arbitration separate.
- CP337-F03: OL-M02 direct creation can retain null crossing. Legacy eager post-stop confirmation bound is not a current-row strict confirmation recheck; native stream explicit strict gate.
- CP337-F04: W1 intersections traceability only, no arbitrary callback/sortedness/runtime proof; F05 and CP333-R01/R02 open.

## Next bounded checkpoint

CP338 / W2 E queue semantic reconciliation: directly rereview all 21 queued E records and CP322-E11; reconcile E creation/use races, parent stop, independent S roots, accepted audit, numbering and live replay against W1/B06, active E/Order/Lifecycle specs and pinned source. Then 17 Lifecycle, 5 Primary, 45 Trading Pipeline, 2 Live records and remaining CP322-E02/E03/E04; F05 and CP333-R01/R02 remain OPEN.
