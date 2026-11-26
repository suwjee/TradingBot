# CP327 — W2 lifecycle and StopAll

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`. 183 prior rows retained, 30 new scoped transitions. No runtime or RAW execution.

## CP327-S01 — LC01

Source: `engine/pipeline/lifecycle_engine.py:29–39`.

Normalize kind and family with str().lower(); exact sequence rank S Blue 1,E Blue 2,S Red 3,E Red 4; unknown key raises. Module rank separately uses attribute shape and includes StopAll 5, prior CP323-S39.

## CP327-S02 — StopAll record

Source: `engine/pipeline/lifecycle_engine.py:42–92`.

Frozen slotted output separates donor source/price/decision, gate exact event, stopped behavior key/count, underlying E, Order provenance and own eventual stop. Eight keyword-only donor fields default null, constructor donor provenance is presentation-only; no inference that gate equals donor stop.

## CP327-S03 — LC02–05

Source: `engine/pipeline/lifecycle_engine.py:95–139`.

Owner exact raw (kind,family,number), count/latest. Armed iff count>=2; E key formatted with number. No owner creates count1; exact key increments and replaces latest without priority check. Higher sequence priority or equal priority both E with dominance replaces count1; otherwise retain old object.

## CP327-S04 — LC06

Source: `engine/pipeline/lifecycle_engine.py:142–168`.

Checkpoint owner/pending null, active tuple empty, output_count0. Validate direction; shallow copy S/E, retain chronology/main/lower arrays and lower index references.

## CP327-S05 — LC07–08

Source: `engine/pipeline/lifecycle_engine.py:170–194`.

Strict stop from bisect_left(start) through all lower candles; bullish first_less, bearish first_greater; no main fallback. Clamped containing main index/time/exact event. E same-family higher number wins; across families Red beats Blue.

## CP327-S06 — LC09

Source: `engine/pipeline/lifecycle_engine.py:196–252`.

E donor constructs immutable StopAll with source/price/decision copied, supplied gate/type/key/count/number, underlying E family/number, physical Order geometry/causes. Normalize specified indexes and Decimal; order causes tuple, parent cause optional. Own stop triple null; donor type/source/color/number/price stored separately, donor-stop fields default null.

## CP327-S07 — LC10–12

Source: `engine/pipeline/lifecycle_engine.py:254–348`.

Optional int/Decimal conversion only bypasses None. S donor constructs number1, opposite-s-group-stop, gate provided, underlying E from tuple when present. Optional Order geometry retained; causes empty, parent stop cause time is S a_stop_event_time; own stop triple null, donor number null. No promotion validation inside constructors.

## CP327-S08 — LC13–15 entry

Source: `engine/pipeline/lifecycle_engine.py:350–366`.

Stable events sort by source_time,kind,raw source_index (E before S at equal time), not decision time. Native detect uses empty checkpoint/output, resolves each own stop after traversal. Replay restores owner/pending/active directly; supplied output not truncated here.

## CP327-S09 — LC16

Source: `engine/pipeline/lifecycle_engine.py:368–416`.

Armed owner only; first strict stop from latest decision/price. Return when stop<boundary. Otherwise E donor required and stop<=donor decision. Same-main exception needs mapped stop index=donor source index, source<=stop<source+timeframe and donor price strict beyond owner. Alternatively exact donor parent type/index/time/normalized price/stop event matches owner; no same-main requirement on parent match. Null otherwise.

## CP327-S10 — LC17–18 direct

Source: `engine/pipeline/lifecycle_engine.py:418–446`.

Accept updates only owner via shared rule. Direct Red S route requires current Blue owner armed and owner.latest exact decision strictly earlier than S decision. Emit StopAll1 gate S decision, active singleton, clear owner/pending. Neither price stop nor Order Mode B required.

## CP327-S11 — LC18 fallback

Source: `engine/pipeline/lifecycle_engine.py:448–473`.

Query armed stop at S source even if pending exists. Completed = truthy pending else owner/gate pair. Red S plus completed Blue owner and uppercased Order mode B emits StopAll1 with completed exact stop; singleton active, clear owner/pending. Otherwise freeze first completed pending only if absent then accept S.

## CP327-S12 — LC19 active StopAll

Source: `engine/pipeline/lifecycle_engine.py:475–496`.

For E donor scan strict stops of all active StopAll from own decision/price. All hits <= E decision qualify. Highest number and earliest stop independently determine new number highest+1 and gate. Count stopped entries; remove active by Python object id, append new to output and active, clear owner/pending.

## CP327-S13 — LC19 armed group

Source: `engine/pipeline/lifecycle_engine.py:498–515`.

If no active stop, armed query with donor E even if pending exists; pending wins. Any completed owner emits StopAll1 sequence-group-stop from E, appends to active (not singleton), clears owner/pending. Otherwise accept E with lowercase family/int number.

## CP327-S14 — LC15/20 output

Source: `engine/pipeline/lifecycle_engine.py:517–531`.

Dispatch exact S tag else E; optional checkpoint after each successful event, recording count. Own stop resolution uses max(decision,after) if supplied, else decision inclusive, replaces only stop index/time/event nullable triple. Gate and donor unchanged.

## CP327-S15 — LC21–22

Source: `engine/pipeline/lifecycle_engine.py:534–548`.

Live continuation initializes empty event keys/output/result, default checkpoint and null covered_until, invokes update(0). Result returns shallow list copy.

## CP327-S16 — LC23 prefix

Source: `engine/pipeline/lifecycle_engine.py:550–571`.

Validate dirty index inclusive 0..len. Dirty main timestamp or null at end; lower it to previous covered_until if earlier or dirty null. New detector/events; keys kind and repr(record), retaining Decimal representation. Zip common prefix until key mismatch or max(source,decision)>=dirty. Restore checkpoint and unresolved output prefix, replay suffix.

## CP327-S17 — LC23 own-stop replay

Source: `engine/pipeline/lifecycle_engine.py:572–590`.

Retained output reuses prior resolved hit only if exists and strictly before dirty or dirty null. Otherwise rescan from max(decision,dirty); new output scans from decision. Assign new checkpoints, keys, unresolved output/result and coverage last lower timestamp+1 microsecond else null. No independent proof of unchanged input prefix.

## CP327-S18 — LC24

Source: `engine/pipeline/lifecycle_engine.py:593–599`.

Wrapper instantiates detector and detects; no local catch or fallback.

## CP327-S19 — LC33

Source: `engine/pipeline/lifecycle_engine.py:973–993`.

For each invalid A with non-null stop, add opposite Reaction First main timestamps in [A source,exact stop[2]). Direct int First index lookup; no local bounds guard or direction use. No stop skips that A.

## CP327-S20 — LC34 consumed S setup

Source: `engine/pipeline/lifecycle_engine.py:996–1034`.

Validate direction. Accepted S identity (A source,S source), not price/index. Sort E source/index; compute exact stop once per E entry; retain containing main inside range.

## CP327-S21 — LC34 eligibility

Source: `engine/pipeline/lifecycle_engine.py:1036–1066`.

Sort S candidates source/index; skip accepted pair and invalid source index. Eligible E source and exact stop strictly before candidate A source, E priority higher, source-main Close strictly beyond stop-main Close. Decimal(str) comparison, no substitute zone price.

## CP327-S22 — LC34 latest prior boundary

Source: `engine/pipeline/lifecycle_engine.py:1073–1108`.

Latest prior E from all E (including unstopped/ineligible) by reverse sorted order, source strictly before A. Latest qualified recognized by object identity; older eligible only rank(priority,number)>latest, stop>latest decision(default source), stop-main>=latest qualified main if any. Retain latest itself if eligible.

## CP327-S23 — LC34 owner choice

Source: `engine/pipeline/lifecycle_engine.py:1112–1136`.

Rank latest stopped MAIN index then module priority,number,source,index; first complete tie. Earliest S source/index per module_identity replaces only strictly earlier. Output sorted candidate source/index, original records.

## CP327-S24 — LC35–36

Source: `engine/pipeline/lifecycle_engine.py:1138–1178`.

Stable source-only E and S sorts; prior is latest strictly earlier timestamp, FIRST duplicate chosen by second lower bound. Accepted prior S wins only if strictly later than prior E (E wins tie). Lower/equal S rejected if A source earlier than prior source, A price strict beyond prior, or S price strict beyond prior. Higher rank bypasses these filters.

## CP327-S25 — LC37

Source: `engine/pipeline/lifecycle_engine.py:1180–1197`.

Apply engine S eligibility first, then exclude any exact (integer source index,time) occupied by supplied E for StopAll grouping. Preserve order and references.

## CP327-S26 — LC38–39 init

Source: `engine/pipeline/lifecycle_engine.py:1199–1232`.

Validate direction, sort external by source/index. Optional candle times materialized once. Exact stop cache keyed object id per invocation, includes null; module_stop_event contract from CP323-S39.

## CP327-S27 — LC38 ownership frontier

Source: `engine/pipeline/lifecycle_engine.py:1234–1285`.

Sort S source/index. Ownership event source callback else source time, NOT initial A stop for valid directions. Eligible prior external/visible S strictly earlier and not consumed. Latest prior external (including consumed external) bounds current lifecycle source; discard older prior modules. Stop<=ownership event qualifies, equality included.

## CP327-S28 — LC38 Close suppression

Source: `engine/pipeline/lifecycle_engine.py:1286–1322`.

From stopped external (no a_source_time attr) choose latest source/index. With candles, lower-priority S and valid indexes, strict candidate source Close beyond stop-main Close suppresses without consuming. Decimal(str) normalization.

## CP327-S29 — LC38 stop arbitration

Source: `engine/pipeline/lifecycle_engine.py:1328–1375`.

Choose max exact stop,priority,number,source,index, not stop-main index. Higher S priority versus S retained; if candidate price not strict beyond dominant (including equality) retain. Otherwise consume identities of all stopped prior <= dominant priority and omit S. Without applicable owner append. No input geometry mutation.

## CP327-S30 — LC40 hard reset

Source: `engine/pipeline/lifecycle_engine.py:1377–1409`.

Truthiness callback defaults; measure S-for-StopAll then detect StopAll once per invocation from provided E. Publish source_time:number reset mapping (last duplicate wins) via E setter. Return shallow E copy and original StopAll result. No retroactive E reconstruction within function.

## Retained prior LC records

- CP323-S39, lines 695–763: A visible suppression by main containing S decision; module identity type/family-or-color/number/source time/index; exact stop attribute else callback tuple last; priority StopAll>E red>S red>E blue>S blue>A/default; dominance stable rank key.
- CP323-S40, lines 766–971: Register exact stopped S/E/StopAll and optional A with containing main; last duplicate identity stop map vs first stop for interior. Candidate A ordered source/index; eligible owner source strictly earlier and stop main <= A, prior A trigger>stop escapes. Rank latest stop main,priority,number,source,index,earliest ordinal; strict beyond price required to reject. Interior exception requires main head directional extreme from owner stop to A First and head before A plus aligned trend First/Break/exact confirmation strictly bounded. Interior valid consumes eligible <= priority; invalid S-owned A does not consume S, records stage invalid; other invalid consumes <= priority. No source mutation.
- CP323-S41, lines 1412–1610: Provenance boundary uses earliest A Blue1/Blue2/continuation/First vs dominant prior exact stop, not price. Internal point and reaction helpers exist but current filter copies lists only. Final lineage restores historical S for E and A for S, sorted by source/index; original identity snapshots not updated during extension; E/StopAll occupancy then invalid S removes records, no second lineage pass; public A index occupancy separately.
- CP325-S44, lines 606–693: Filter accepted A audit by accepted source; union inherited First veto and invalid-A pending-S leg blocks; remove accepted initial First times (parse strings). E-only exception exact stop equal accepted E stop, First same stop main and blocked not inherited, invalid A source<=First<exact stop, opposite confirmation>stop. Return accepted ledger and blocks, optional set update; no global unblock.

## Cross-owner boundaries

- `engine/bridge/trading_pipeline.py:2508–2567`: Consumed S evidence integration and accepted audit refresh; previously reviewed, not counted.
- `engine/bridge/trading_pipeline.py:2569–2645`: Eight-pass Order_B feedback; shared geometry; StopAll enabled donors accepted E plus missing independent source roots; LC40 per pass; restore independent roots and ensure audit before reset-leg discovery; stable identity returns; repeated changed identity or exhausted passes raises. Disabled StopAll empty.
- `engine/bridge/trading_pipeline.py:2939–3006`: Visibility consumes converged E/StopAll, does not run StopAll again; callbacks differ by E presence, capture accepted projection before filtering, Primary groups formed before range clip.
- `engine/pipeline/e_zone_detector.py:394–411`: Reset setter copies/sorts map and clears only specified four caches; no native reconstruction within LC40.

## Remaining

CP328 / W2 Primary PL/PH and reversal regime: qualification, activation/decision race, exact confirmation/ownership, native and conditional live scheduler, StopAll promotion and regime boundary; then projection/live and W3/W4.
