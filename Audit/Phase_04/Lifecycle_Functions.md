# Lifecycle and StopAll — function-level source contracts

Baseline: main `466eb875070f02cd0dbfb105033422bbe2fd8c70`, `engine/pipeline/lifecycle_engine.py` blob `2885dcbd3af108baadde7510ffd7968ad735c57e`. STOP_ALL_VERSION 1.18.6; implementation 1.22.2. This is source-only documentation, not executed validation. B/R denote bullish/bearish; strict directional crossing means price < boundary for B and > boundary for R. Source time labels and actual decision/stop events are distinct.

## Sequence and immutable state

### LC01 — sequence_priority (37–39)
Normalize kind and family with str().lower(); dictionary lookup S blue=1, E blue=2, S red=3, E red=4. Unknown pair raises KeyError.

### LC02 — _DominantBehavior.priority (106–107)
Property delegates to LC01 on kind/family. Frozen slotted record also carries number, count, latest object.

### LC03 — _DominantBehavior.armed (110–111)
True precisely when count >=2.

### LC04 — _DominantBehavior.key (114–118)
Format E number and family if kind exactly E; otherwise S and family.

### LC05 — advance_dominant_behavior (121–139)
Create incoming owner count=1. No prior owner => incoming. Exact kind/family/number match => replace previous count+1 and latest. Otherwise replace only on higher priority, or equal priority with both E and LC08 dominance. Otherwise return previous object unchanged. No mutation of owner record.

## StopAll detection

### LC06 — StopAllDetector.__init__ (151–168)
Validate direction against bullish/bearish. Copy S/E collections; retain chronology, main/lower candles, corresponding times and lower index. Checkpoint record defaults owner/pending null, active tuple empty, output_count zero. StopAll record is frozen/slotted, with explicit donor metadata separate from underlying owner.

### LC07 — StopAllDetector._strict_stop (170–184)
Lower-bound start on lower times; first_less for B or first_greater for R to end of lower candles. Null if no crossing. Otherwise return clamped containing main index, main time, exact lower event. Equality is not a stop; no coarse fallback.

### LC08 — StopAllDetector._dominates_e (187–194)
Same family: strictly greater number. Different families: red dominates blue, not reverse.

### LC09 — StopAllDetector._stopall_from_e (196–252)
Construct immutable StopAll using donor E source/time/price and decision index/time/event. Number, gate type/event and stopped behavior metadata are caller-supplied. Preserve underlying E family/number and full Order provenance (normalize integer fields and Decimal prices); causes tuple defaults empty, parent cause time defaults null. Stop index/time/event initially null. Donor type E, source index/time, family, number and price populated separately; donor-stop fields default null. Do not substitute stopped owner's geometry for donor geometry.

### LC10 — StopAllDetector._optional_int (255–256)
Null stays null; otherwise int conversion.

### LC11 — StopAllDetector._optional_decimal (259–260)
Null stays null; otherwise shared as_decimal conversion.

### LC12 — StopAllDetector._stopall_from_s (262–348)
Construct number 1, gate type opposite-s-group-stop, from S donor's source/time/price and decision. Gate event and stopped owner metadata supplied; optional underlying E tuple supplies family/number, else null. Copy optional Order identity/provenance with LC10/11 conversions; order causes empty; parent stop cause time equals S A-stop event. All own stop fields null. Donor type S, source/time, color, number null, price; donor-stop metadata defaults null.

### LC13 — StopAllDetector._events (350–354)
Combine S and E tagged events; sort (source_time, kind, source_index). E sorts before S on exact source tie. Stable sorting for equal keys.

### LC14 — StopAllDetector.detect (356–359)
Allocate output, run LC15 with default checkpoint, resolve stop fields for each output with LC20 and return.

### LC15 — StopAllDetector._detect_events (361–523)
Resume checkpoint owner/pending/active, mutate provided output by chronological events. S tag goes LC18; any other tag goes LC19. Optional checkpoints appended after each event, containing current owner, pending, active and output length. Nested helpers share nonlocal state. No stop resolution until LC20.

### LC16 — _detect_events.armed_stop_before (368–416)
Require armed owner. Locate strict stop from owner's latest decision event and price. If absent => null. Stop strictly earlier than boundary => return. Otherwise require E donor and stop <= donor decision. Accept same-main case only if clamped stop index equals donor source index, donor source <= exact stop < source+timeframe, and donor price strictly crosses owner price. Alternatively accept exact parent match: donor parent type upper equals owner kind, non-null parent index equals owner source index, parent time equals owner source time, normalized price equals owner price, parent_stop_event equals stop. Else null. This preserves actual-event comparison despite source-time labels.

### LC17 — _detect_events.accept (418–420)
Update nonlocal owner via LC05; no independent mutation of pending/active.

### LC18 — _detect_events.process_s_event (422–473)
Normalize S color. If red and current owner blue armed with owner latest decision strictly before S decision, emit LC12 number 1 using S decision as gate, set active singleton, clear owner/pending, return. Else get gate LC16 at S source; completed = existing pending, or owner/gate when available. If red and completed owner blue and order_mode.upper()==B, emit LC12 using completed stop, reset active/owner/pending identically. Otherwise store completed as pending only if previously absent, then accept S. Completed stop is frozen historical evidence, not a replacement owner.

### LC19 — _detect_events.process_e_event (475–515)
Evaluate strict stop of each active StopAll from its own decision. Select all stop events <= E decision. If any, highest stopped number h; earliest stop gate; emit LC09 number h+1, gate stopall-stop, behavior StopAll, key StopAll{h}, count number stopped. Remove stopped active objects by identity, append new, clear owner/pending. Else completed = pending or current armed stop via LC16 with donor E. If completed, emit LC09 number 1, gate sequence-group-stop, stopped owner kind/key/count, append active and clear owner/pending. Otherwise accept E with lowercase family and integer number.

### LC20 — StopAllDetector._resolve_stop (525–531)
Start decision event, or max(decision, optional after). Find strict stop LC07. Replace stop index/time/event, null triple if no hit; other fields preserved.

### LC21 — LiveStopAllContinuation.__init__ (537–544)
Store direction, one default checkpoint, empty event keys/output/result and null covered_until. Call update first_dirty_main=0.

### LC22 — LiveStopAllContinuation.result (547–548)
Return shallow list copy, not internal result list.

### LC23 — LiveStopAllContinuation.update (550–590)
Validate dirty index 0..len(main times). Dirty = main time at index or null at end; rewind to covered_until if non-null and earlier than dirty (or dirty null). New detector/event list; keys (kind, repr(record)). Common prefix while equal keys and max(source, decision) < dirty if dirty present. Restore prefix checkpoint/output and rerun suffix with checkpoint capture. For prefix outputs, reuse prior resolved record if stop exists and before dirty (or dirty null); otherwise LC20 after dirty. Newly emitted outputs resolve normally. Replace checkpoints, keys, unresolved output and result. covered_until = last lower time +1 microsecond, else null. Return result copy. No claim of runtime append equivalence.

### LC24 — detect_stopalls (593–599)
Instantiate detector and return detect.

## Order context and module identity

### LC25 — resolve_order_context (606–692)
Filter initial Order audit with accepted_audit_entry against accepted A sources; retain non-null entries under original keys. Copy inherited blocked First times and add LC32 for invalid A whose source belongs to pending S A sources. Normalize accepted initial reaction First strings with format %Y-%m-%d %H:%M:%S; subtract accepted First times from blocked. Optional E-specific exceptions: if accepted E stop events and opposite confirmation callback, group opposite reactions by integer First index. For each pending invalid A with stop exact event in accepted E stops, map to containing main via upper_bound-1; skip negative. For reactions in that main, require First in blocked, not in inherited blocked, invalid A source <= First < exact stop, and opposite confirmation > stop. Add pair (exact stop, First). Update supplied exception set if not null; return accepted audit and blocked times. Never globally unblock the E exception.

### LC26 — visible_a_zones_after_s_stops (695–710)
Map each S decision event to containing main index via upper_bound-1; discard -1. Retain A whose integer source index is not in that set. This uses S decision, not its own eventual stop.

### LC27 — module_priority (712–724)
Attribute presence order: stopped_behavior_type =>5; family =>4 if lowercase red else2; a_source_time =>3 if lowercase color red else1; otherwise0.

### LC28 — module_identity (726–733)
Tuple (runtime type name, family or default color, number default null, required source_time, source_index default null). No price identity.

### LC29 — module_stop_event (735–747)
Return explicit non-null stop_event_time first. If no finder or null finder result => null. Tuple finder result => last element; otherwise return result directly.

### LC30 — strictly_beyond_boundary (749–752)
Use validated direction policy strict_cross. No equality crossing.

### LC31 — dominant_module (754–763)
Max by (module priority, integer number default0, source time, integer source index default -1). First item wins equal key; empty input follows max error.

### LC32 — split_a_zones_by_dominant_stops (766–971)
Validate direction. Sort S/E/StopAll by (source time,index); gather non-null exact stops and containing main positions >=0. Optional A stop finder adds A owners (tuple last or direct event), recording identities. For each stopped entry retain ordinal and source; maps stop index/event overwritten for identical identity, first_stop_event set once. Sort enumerated stop rows by main position. Process A sorted source time/index; move all stops at index<=A source index into ready identity groups unless consumed. Eligible rows require owner source strictly earlier and row stop index<=A index; exclude A owner if new A trigger (default source) > last stop exact. No eligible => valid. Choose max (identity's last stop index, priority, number, owner source, index, negative ordinal). If candidate price not strictly beyond winner => valid without consumption.
Interior exception: winner not A, trend reactions and confirmation callback present, A index>0 and reaction_first_time present. Map winner's first stop event and A First to main indexes. If valid interval, select first min Low (B) or max High (R), Decimal(str), over inclusive interval. Head must occur before A index and strictly beyond A price. Then any trend reaction with First >= head index and <= A First main, Break < A index, and exact confirmation < A source time permits interior. Interior => valid and consume ready eligible identities of priority <= winner. Otherwise invalid; if winner has a_source_time (S), optionally record stage_invalid_a_identities (source,index) but consume none. For other winner consume ready eligible identities of priority <= winner. Return valid/invalid. Ready groups are removed only on consumption; comparison is price-directional while source/stop ordering is invariant.

### LC33 — blocked_orders_while_invalid_leg_heads_are_live (973–993)
For each invalid A, get stop; skip null. For every opposite reaction, main First time at integer first_idx in [A source, stop[2]) is added to set. Direction not used. Return set.

### LC34 — consumed_s_evidence_after_larger_stop (996–1136)
Validate direction. Accepted identity pairs (A source,S source). Sort E source/index, precompute non-null stops mapped inside main range. Iterate S candidates sorted source/index, skip accepted and out-of-range source. Normalize candidate source Close. Eligible owner must precede A source, exact stop strictly before A source, outrank S, and candidate Close strictly beyond stop-main Close. Find latest prior E by reverse sorted source strictly before A source. Retain latest if qualified, or older owner with strictly higher (priority,number), stop after latest E decision (default source), and stop main index >= latest qualified owner's when present. Choose max (stop main index,priority,number,source,index). Keep earliest S (source,index) per owner identity. Return sorted pairs (candidate,owner) by candidate source/index. No owner means no evidence.

### LC35 — s_zones_for_module_engines (1138–1178)
Sort E by source only and S by source only. For each S choose latest prior E or already accepted S (strictly earlier); S replaces prior E only on strictly later source. LC36 resolves duplicate timestamps. For lower/equal priority reject if A source < prior source or A price strictly beyond prior price or S price strictly beyond prior price. Higher priority bypasses these filters. Append otherwise. Return visible S.

### LC36 — s_zones_for_module_engines.latest_prior (1145–1151)
Lower bound source minus one; negative => null; find first index at selected prior timestamp (lower bound). First duplicate wins.

### LC37 — s_zones_for_stopall (1180–1197)
Apply LC35, then remove S whose exact (integer index,source time) appears in E.

### LC38 — visible_s_zones_after_module_resets (1199–1375)
Validate direction, sort external owners by source/index, optionally build candle times; per-call stop cache LC39. For each sorted S, ownership event = source-event callback if supplied else source main time (valid directions override initial A stop). Consider prior external and accepted S strictly earlier by source and not consumed. Latest prior external by source/index establishes cutoff: ignore earlier prior modules. When ownership event non-null, stopped prior are those exact stop<=ownership event. If candles available and stopped external, latest such external by source/index: when new S priority lower and both stop-main/source indexes in range, skip candidate if source Close strictly beyond stop-main Close, without consumption. Otherwise choose dominant max (exact stop,priority,number,source,index). If both S and new priority strictly greater, append. If new S price not strictly beyond dominant, append. Else consume all stopped prior of priority <= dominant and skip candidate. When no applicable stop, append. Return visible list; no mutation of input records.

### LC39 — visible_s_zones_after_module_resets.cached_stop_event (1228–1232)
Cache module_stop_event result (including null) by id(module), invoke finder at most once per object per call.

### LC40 — reconcile_stopall_lifecycle (1377–1409)
Use supplied timed_step or immediate callable wrapper, stopall_finder or LC24. Measure LC37 visible S, then detect StopAll. Assign detector.sequence_resets map source_time:number (later duplicate overwrites). Return copy of E list and StopAll list; do not rebuild E.

### LC41 — visible_a_zones_after_module_boundaries (1412–1457)
Direction unused. Sort modules S/E (caller may include StopAll) and A by source/index. Gather stopped prior with source<=A source and non-null stop<=A source. Choose LC31 priority-based dominant, get stop again. If minimum of Blue1/Blue2/continuation/Reaction First provenance times < boundary, exclude. Else include. Equality allowed. Return retained A.

### LC42 — reaction_number_is_internal (1459–1470)
Null false, convert number to int, require 1..len(reactions); check physical order_identity(first_idx,break_idx) in identities.

### LC43 — point_is_inside_healthy_reaction (1473–1493)
Null time or price false. Normalize price. For each reaction with First and confirmation non-null, require First < source <= confirmation and bottom < price < top. True first match, false otherwise. No explicit healthy flag in this function.

### LC44 — filter_internal_behavior_outputs (1496–1507)
Ignore last three inputs; return list copies of A/S/E/StopAll in that order.

### LC45 — finalize_behavior_visibility (1509–1601)
Build integer StopAll source indexes, remove E collisions. Compute visible S with final E+StopAll via LC38. Restore historical S referenced by final E parent type.upper()==S at parent_source_time if module_identity absent from original visible set; set is not updated during extension. Sort S source/index. Filter A via LC41 with S and E+StopAll. Restore historical A referenced by S a_source_time, using all_a_zones if non-null otherwise original A; compare (source time,int index) against initial visible identity set; sort. Occupied indexes E+StopAll: remove collisions from A/S; also remove S whose (source_time,index) in invalid identities. Return (final E, final S, final A).

### LC46 — visible_a_zones (1604–1610)
Build final S integer source index set; retain A outside it.

## Audit status
46 named functions/methods documented against pinned source. External calls into Order Audit, chronology and policy remain subject to cross-module review. No production source changed, no RAW loaded and no calculation executed.