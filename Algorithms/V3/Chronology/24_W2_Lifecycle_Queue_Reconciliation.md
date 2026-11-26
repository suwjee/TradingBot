# CP339 — W2 Lifecycle Queue Semantic Reconciliation

**Status:** PASS_SCOPED after publication; W2 NOT_ACCEPTED.

Pinned source: `c99b4c957e932d9ee70c492ca03ce80711447fc1`, `2885dcbd3af108baadde7510ffd7968ad735c57e`. Entry `0a6c82e630396497b6b8da194f1fd88fd27815fd`.

## CP327-S01 — LC01

Source: `engine/pipeline/lifecycle_engine.py:29–39`.

Normalize str(kind).lower() and str(family).lower() in shared exact sequence table; ranks S blue 1,E blue 2,S red 3,E red 4, missing pair raises. Module priority separate and attribute-shape based includes StopAll 5.

**Handoff:** E and StopAll consume shared direction-independent family rank; unknown sequence pair is not module_priority fallback.

B07 overlapping link occurrences: 4.

## CP327-S02 — StopAll record / LC06

Source: `engine/pipeline/lifecycle_engine.py:42–92`.

Frozen slotted record has donor geometry/decision, gate exact event/type, stopped group key/count, underlying E, nullable physical Order and actual own stop. Eight keyword-only donor fields default null. Donor provenance does not define gate.

**Handoff:** Do not conflate E/S constructor donor with stopped behavior, or gate with donor/own actual strict stop.

B07 overlapping link occurrences: 40.

## CP327-S05 — LC07–08

Source: `engine/pipeline/lifecycle_engine.py:170–194`.

Lower-bound decision start inclusive, required index first_less bullish or first_greater bearish, right len(lower). Miss returns None, no linear/coarse retry. Map exact event clamped main index/time. E dominance same family strictly higher number; different only red over blue.

**Handoff:** Index owner guarantees coherent lower arrays; priority not direction-mirrored; equality price not a strict stop.

B07 overlapping link occurrences: 16.

## CP327-S06 — LC09

Source: `engine/pipeline/lifecycle_engine.py:196–252`.

E donor passes source/decision geometry and normalized price/index, supplied gate/type/stopped key/count/number, native Order identity/box/stop/cause tuple and optional cause time. Own stop triple null; separate donor metadata converted again, donor-stop defaults null.

**Handoff:** Constructor does not establish promotion eligibility; physical Order provenance remains source-owned.

B07 overlapping link occurrences: 24.

## CP327-S07 — LC10–12

Source: `engine/pipeline/lifecycle_engine.py:254–348`.

Optional conversions bypass only None. S donor fixed number1/opposite-s-group-stop, gate/stopped group from caller, underlying E tuple optional, optional Order fields. order_causes always empty even with underlying E metadata; order_parent_stop_cause_time S a_stop_event_time. Own stop and donor-stop null; no local promotion check.

**Handoff:** Correct SA-M03 ambiguous summary; S donor never copies E cause tuple merely because stopped owner was E.

B07 overlapping link occurrences: 49.

## CP327-S11 — LC18 fallback

Source: `engine/pipeline/lifecycle_engine.py:448–473`.

After direct armed-blue decision gate fails, call armed_stop_before S source even if pending already exists. Truthy pending wins, else owner/gate pair. Red S + completed Blue owner + uppercased Mode B promotes with completed exact stop; singleton active and clear owner/pending. Otherwise freeze first pending only when absent then accept.

**Handoff:** Direct earlier-decision Red S promotion has no mode-B or price-stop requirement; fallback is distinct, pending historical evidence not active owner.

B07 overlapping link occurrences: 25.

## CP327-S12 — LC19 active StopAll

Source: `engine/pipeline/lifecycle_engine.py:475–496`.

E event queries every active StopAll own strict stop from decision, includes hits <= E decision. Number max stopped+1, gate min exact event independently, count list entries. Remove active by Python id, append new to output and active, clear owner/pending.

**Handoff:** StopAll repetition gate and new E donor geometry independent; no merging by physical source.

B07 overlapping link occurrences: 24.

## CP327-S13 — LC19 armed group

Source: `engine/pipeline/lifecycle_engine.py:498–515`.

If no active stop eligible, run armed query with E donor even if pending exists. Pending wins; any completed owner emits StopAll1 sequence-group-stop, extends active (not singleton), clears owner/pending. Else accept normalized lowercase E family/integer number.

**Handoff:** E donation need not itself have prior active StopAll stop; same-main/parent exact gate LC16 is owner-defined.

B07 overlapping link occurrences: 15.

## CP327-S14 — LC15/20

Source: `engine/pipeline/lifecycle_engine.py:517–531`.

Dispatch exact S tag else E without local sorting; append optional post-event checkpoint after successful processing. Resolve own strict stop from decision or max(decision,after) inclusive; replace only stop triple, null on miss.

**Handoff:** No rewriting gate, donor or Order cause during own-stop resolution; live replay conditional.

B07 overlapping link occurrences: 19.

## CP327-S18 — LC24

Source: `engine/pipeline/lifecycle_engine.py:593–599`.

Wrapper constructs detector with supplied direction,S/E,chronology and calls detect, no local retry or recovery.

**Handoff:** Bridge may choose live finder instead; wrapper static review not runtime proof.

B07 overlapping link occurrences: 2.

## CP327-S19 — LC33

Source: `engine/pipeline/lifecycle_engine.py:973–993`.

For each invalid A with non-null stop, use stop[2] and add opposite First main timestamp if A source<=First<exact stop. Direct int index lookup, no bounds or direction predicate; stop miss skips.

**Handoff:** LC resolve_order_context removes accepted A First from blocked set and adds exact E-only exceptions separately; no global invalidation of physical Order.

B07 overlapping link occurrences: 14.

## CP327-S24 — LC35–36

Source: `engine/pipeline/lifecycle_engine.py:1138–1178`.

Stable source-only E and S ordering. Latest strictly prior uses lower bound then first duplicate of chosen timestamp. Prior accepted S overrides only strictly later than prior E; E wins tie. Lower/equal S rejects if A source earlier or A/S price strict beyond prior normalized price. Higher rank bypasses.

**Handoff:** Engine input eligibility is not final public visibility; exact source tie not a prior owner.

B07 overlapping link occurrences: 48.

## CP327-S25 — LC37

Source: `engine/pipeline/lifecycle_engine.py:1180–1197`.

Call S engine eligibility, then remove exact (int source index,time) occupied by supplied E for StopAll grouping, retain order/references.

**Handoff:** Distinct from final public index-only collision and donor-list Bridge filter.

B07 overlapping link occurrences: 11.

## CP327-S26 — LC38–39 init

Source: `engine/pipeline/lifecycle_engine.py:1199–1232`.

Direction guard, sort external by source/int index; candle times materialized only when supplied. Per-invocation cache uses id(module), stores None too; module_stop_event explicit non-null wins else callback (tuple last) or None.

**Handoff:** Stop callback optional, not executed-call evidence; cache scoped to invocation.

B07 overlapping link occurrences: 18.

## CP327-S27 — LC38 frontier

Source: `engine/pipeline/lifecycle_engine.py:1234–1285`.

Sorted S source/index; reads initial A stop then valid direction overwrites ownership by supplied source-event callback or main source; callback None not replaced. Earlier external/visible S excluding consumed; latest earlier external even consumed sets source cutoff; stop<=ownership qualifies.

**Handoff:** Actual ownership event not A-stop nor always exact decision; cutoff not stop chronological ranking.

B07 overlapping link occurrences: 48.

## CP327-S28 — LC38 Close suppression

Source: `engine/pipeline/lifecycle_engine.py:1286–1322`.

From stopped prior classify external by missing a_source_time, choose latest source/index. With candles and strictly lower S rank and valid mapped indexes, compare Decimal(str(source Close)) strictly beyond stop-main Close. Continue without consuming on strict crossing.

**Handoff:** No main OHLC inference of stop chronology; exact stop selected first, Close used for suppression only.

B07 overlapping link occurrences: 42.

## CP327-S29 — LC38 arbitration

Source: `engine/pipeline/lifecycle_engine.py:1328–1375`.

Choose max exact stop then module priority,number,source,index, first full tie. Both S markers and strictly higher new S retained; if price not strictly beyond dominant, retain incl equality; else consume stopped prior identities <= dominant rank and omit candidate. No applicable owner => retain.

**Handoff:** Identity consumption local visibility pass; not deleting source records or ledger. Exact event ranking differs from stopped-main A ownership.

B07 overlapping link occurrences: 39.

## Findings and scope

- CP339-F01 / DOCUMENTATION_CORRECTED: SA-M03 S donor order_causes is always empty, even when underlying E family/number populated; S A-stop cause time is separate. Detailed LC12 already correct.
- CP339-F02 / QUALIFIED: Sequence rank, module priority, source-time donor sorting, exact-stop visibility arbitration and main-stop A stage arbitration are distinct; no direction mirroring of family rank.
- CP339-F03 / OPEN_CROSS_OWNER: Primary/Bridge/Live handoffs remain queued; F05 and CP333-R01/R02 remain open.

Queue: 133/185; remaining 52. Supplemental accessors: 6/9; remaining 3. W1 B07: 1179/1179 retained, 438 overlapping link occurrences. Runtime and RAW NOT_RUN. CP340 / W2 Primary queue semantic reconciliation: directly rereview 5 queued Primary records against W1/B08, active Primary/MBL/lifecycle specs and pinned source; follow with 45 Trading Pipeline, 2 Live records and CP322-E02/E03/E04. CP331-F05 and CP333-R01/R02 remain OPEN; W2 not accepted.
