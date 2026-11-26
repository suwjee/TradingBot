# StopAll — Dominant group and repeated hard-stop sequence (V3)

**Conventions:** B = bullish, R = bearish. A strict trend stop means Low < level for B, High > level for R; improvement uses the same predicate. Main source identity and exact event chronology are separate. Preserve Decimal representation, operation order and stable ordering. Required record fields/defaults are in [record interfaces](../../Contracts/Declared_Record_Schemas.md); shared searches in [Index and cache contracts](20_Indexes_And_Caching.md). Procedure labels identify semantic operations, not required implementation symbols.


## SA-M01 — Inputs, output and state

Consume accepted S/E collections, after lifecycle ownership filtering; chronology supplies strict parent-direction stops. Output immutable StopAll record contains number, donor geometry/decision, gate type/exact event, stopped group metadata, optional underlying E and physical Order provenance, own actual stop and separate donor metadata. Do not confuse stopped group source with donor source or gate with donor actual stop. Sequence owner defined by [Lifecycle](10_Lifecycle.md). Initialize owner null,pending completed stop null,active StopAll tuple empty,output empty. Sort S/E events by (source_time,kind,source_index); E precedes S on true source-time tie.

## SA-M02 — Armed stop evidence

Owner armed when exact key count>=2. Search first strict lower stop from latest owner's decision inclusive; no lower fallback. Accept as completed if stop strictly earlier than current candidate source. For E donor, also allow stop <= donor decision when same donor source main contains exact stop and donor price strictly crosses owner, or exact parent type/index/time/price/stop matches owner. No inferred intrabar order. Freeze pending completed stop, independent from later owner updates.

## SA-M03 — Promotion decision table (evaluated in row order)

| Current event | Gate | Action |
|---|---|---|
| S red | Current owner Blue, armed and owner latest decision < S decision | StopAll1, opposite-s-group-stop, gate S decision; active singleton, clear owner/pending |
| S red | Completed pending/current armed Blue stop and S Order mode uppercased B | StopAll1 from S, gate completed exact stop; active singleton, clear owner/pending |
| Other S | No promotion | Keep first pending completed stop, advance dominant owner |
| E | Any active StopAll strict stop <= E decision | StopAll max stopped number+1, gate earliest stopped event, count stopped; remove stopped active by identity, append new, clear owner/pending |
| E | No active StopAll stop; completed pending/current armed stop exists | StopAll1, sequence-group-stop, append active; clear owner/pending |
| Other E | No promotion | Advance dominant owner with exact E family/number |

Donor is current event; source and price copied, decision retained; StopAll1 from S has optional Order fields and an empty order_causes tuple even when underlying E metadata is present; its order_parent_stop_cause_time is the S A-stop event if supplied. StopAll from E preserves the donor's full native Order provenance. Resolve each emitted StopAll's own strict stop from its decision after traversal, independent of promotion gate. Lifecycle projection adds sequence reset map source->number (later duplicate wins); does not alter donor creation cause. Final public StopAll may be replaced by confirmed primary source ownership only through primary rule. In the active bridge, StopAll detection is performed inside each enabled Order_B feedback pass on its exact donor list; LC40 assigns sequence_resets without retroactively rebuilding E and returns the donor-list copy plus StopAll. The converged pass's StopAll list is stored in PipelineState by direction and used for visibility, Primary groups and final audit; visibility does not run StopAll a second time. The disabled pass supplies an empty StopAll list.

## SA-M04 — Continuation

Live caches event keys (kind,representation of immutable record) and checkpoints after each event. Rewind dirty to prior covered-until if earlier; retain matching prefix whose source and decision are before dirty; replay suffix. Earlier emitted own-stop records reused only if existing exact hit and dirty is null or the hit is strictly before dirty; otherwise rescan from max(decision,dirty) when dirty is non-null, or decision when null. Preserve output order. Shallow result copies, immutable records. No empirical equivalence assertion.

## Detailed StopAll procedures

### LC06 — StopAllDetector.__init__
Validate direction against bullish/bearish. Copy S/E collections; retain chronology, main/lower candles, corresponding times and lower index. Checkpoint record defaults owner/pending null, active tuple empty, output_count zero. StopAll record is frozen/slotted, with explicit donor metadata separate from underlying owner. Direction validation precedes S then E shallow copies; chronology and all main/lower arrays/index are retained by reference. All eight donor fields are keyword-only with None defaults; frozen record is not a recursive freeze.

### LC07 — StopAllDetector._strict_stop
Lower-bound start on lower times; first_less for B or first_greater for R to end of lower candles. Null if no crossing. Otherwise return clamped containing main index, main time, exact lower event. Equality is not a stop; no coarse fallback. The right-exclusive bound is len(lower); lower_times is used for bisect and selected event lookup. A position of zero is valid. Map event with clamp=True; no local catch or alternative query.

### LC08 — StopAllDetector._dominates_e
Same family: strictly greater number. Different families: red dominates blue, not reverse.

### LC09 — StopAllDetector._stopall_from_e
Construct immutable StopAll using donor E source/time/price and decision index/time/event. Number, gate type/event and stopped behavior metadata are caller-supplied. Preserve underlying E family/number and full Order provenance (normalize integer fields and Decimal prices); causes tuple defaults empty, parent cause time defaults null. Stop index/time/event initially null. Donor type E, source index/time, family, number and price populated separately; donor-stop fields default null. Do not substitute stopped owner's geometry for donor geometry. E Order direction/mode and numeric identity/geometry fields are required and converted as written; only order_causes and parent-stop cause time use getattr defaults. Explicit None causes are not normalized before tuple conversion. Own stop fields are None. Separate donor index/family/number/price are read and converted again; donor-stop fields are not supplied.

### LC10 — StopAllDetector._optional_int
Null stays null; otherwise int conversion. Identity None test, so zero and other falsy non-null values are converted; conversion errors propagate.

### LC11 — StopAllDetector._optional_decimal
Null stays null; otherwise shared as_decimal conversion. Identity None test, otherwise delegate directly to as_decimal; no additional rounding or exception fallback.

### LC12 — StopAllDetector._stopall_from_s
Construct number 1, gate type opposite-s-group-stop, from S donor's source/time/price and decision. Gate event and stopped owner metadata supplied; optional underlying E tuple supplies family/number, else null. Copy optional Order identity/provenance with LC10/11 conversions; order causes empty; parent stop cause time equals S A-stop event. All own stop fields null. Donor type S, source/time, color, number null, price; donor-stop metadata defaults null. Underlying E tuple elements are copied unchanged when non-null (no length guard). S optional order_direction/order_mode are not string-normalized, missing attributes default None. Parent-stop cause time is getattr(item,a_stop_event_time,None). Source/decision indices and donor index converted, price and donor price normalized separately; donor color str without lowercase. Own stop and donor-stop fields remain None. Constructor does not itself validate promotion eligibility.

### LC13 — StopAllDetector._events
Combine S and E tagged events; sort (source_time, kind, source_index). E sorts before S on exact source tie. Stable sorting for equal keys. Materialize S-tagged list then E-tagged list before concatenation and sort; raw source_index and source_time are keys, not decision time; stable same-key order.

### LC14 — StopAllDetector.detect
Allocate output, run LC15 with default checkpoint, resolve stop fields for each output with LC20 and return. Evaluate sorted events first, default checkpoint second, pass mutable output; resolve each emitted record only after traversal, in output order, producing a new list. No local catch.

### LC15 — StopAllDetector._detect_events
Resume checkpoint owner/pending/active, mutate provided output by chronological events. S tag goes LC18; any other tag goes LC19. Optional checkpoints appended after each event, containing current owner, pending, active and output length. Nested helpers share nonlocal state. No stop resolution until LC20. Restore checkpoint references directly; no output truncation by this helper. Dispatch supplied event order without sorting: exact S else E. Capture post-event checkpoint only on successful return when checkpoints is non-null (empty list valid). No local catch.

### LC16 — _detect_events.armed_stop_before
Require armed owner. Locate strict stop from owner's latest decision event and price. If absent => null. Stop strictly earlier than boundary => return. Otherwise require E donor and stop <= donor decision. Accept same-main case only if clamped stop index equals donor source index, donor source <= exact stop < source+timeframe, and donor price strictly crosses owner price. Alternatively accept exact parent match: donor parent type upper equals owner kind, non-null parent index equals owner source index, parent time equals owner source time, normalized price equals owner price, parent_stop_event equals stop. Else null. This preserves actual-event comparison despite source-time labels. Owner absence short-circuits armed check; normalize owner latest price before search. Stop strictly before boundary returns before donor tests; equality requires donor and stop<=donor decision. Convert donor source index before same-main gate, then clamp mapping, inclusive source and exclusive source+timeframe, then selected strict price relation. If same-main fails, read optional parent index and price before parent type check. Parent type is uppercased against raw owner kind; exact parent alternative does not repeat same-main conditions. Test non-null index/price before conversion, preserve left-to-right short circuit.

### LC17 — _detect_events.accept
Update nonlocal owner via LC05; no independent mutation of pending/active.

### LC18 — _detect_events.process_s_event
Normalize S color. If red and current owner blue armed with owner latest decision strictly before S decision, emit LC12 number 1 using S decision as gate, set active singleton, clear owner/pending, return. Else get gate LC16 at S source; completed = existing pending, or owner/gate when available. If red and completed owner blue and order_mode.upper()==B, emit LC12 using completed stop, reset active/owner/pending identically. Otherwise store completed as pending only if previously absent, then accept S. Completed stop is frozen historical evidence, not a replacement owner. Direct route emits then replaces active singleton, clears owner and pending; no price stop or mode B check. On fallback, armed_stop_before is called even if pending is already truthy, then pending wins by truthiness. A new pair requires both non-null owner and gate. Mode is str(getattr(...,empty)).upper(); E underlying key only for exact E owner. Without promotion assign completed only if pending is None, then ordinary acceptance.

### LC19 — _detect_events.process_e_event
Evaluate strict stop of each active StopAll from its own decision. Select all stop events <= E decision. If any, highest stopped number h; earliest stop gate; emit LC09 number h+1, gate stopall-stop, behavior StopAll, key StopAll{h}, count number stopped. Remove stopped active objects by identity, append new, clear owner/pending. Else completed = pending or current armed stop via LC16 with donor E. If completed, emit LC09 number 1, gate sequence-group-stop, stopped owner kind/key/count, append active and clear owner/pending. Otherwise accept E with lowercase family and integer number. Search every active entry using raw stored price. Maximum number and minimum stop are independent and may come from different entries; count list entries, not unique IDs. Remove by Python object id, not value/physical identity, then append output and extend active tuple. If no stopped active, call armed search even when pending exists; truthy pending wins. Sequence-group promotion extends active tuple, unlike S singleton. Ordinary E normalization is str(family).lower() then int(number).

### LC20 — StopAllDetector._resolve_stop
Start decision event, or max(decision, optional after). Find strict stop LC07. Replace stop index/time/event, null triple if no hit; other fields preserved. after uses non-null identity test; search level is item.price unchanged. Replace only three stop fields; each selects on stop tuple truthiness, not explicit None. No fallback.

### LC21 — LiveStopAllContinuation.__init__
Store direction, one default checkpoint, empty event keys/output/result and null covered_until. Call update first_dirty_main=0. Assign direction, default checkpoint list, event keys, output, result and absent covered_until in that order before immediate update(0).

### LC22 — LiveStopAllContinuation.result
Return shallow list copy, not internal result list. Shallow copy preserves record identity.

### LC23 — LiveStopAllContinuation.update
Validate dirty index 0..len(main times). Dirty = main time at index or null at end; rewind to covered_until if non-null and earlier than dirty (or dirty null). New detector/event list; keys (kind, repr(record)). Common prefix while equal keys and max(source, decision) < dirty if dirty present. Restore prefix checkpoint/output and rerun suffix with checkpoint capture. For prefix outputs, reuse prior resolved record if stop exists and before dirty (or dirty null); otherwise LC20 after dirty. Newly emitted outputs resolve normally. Replace checkpoints, keys, unresolved output and result. covered_until = last lower time +1 microsecond, else null. Return result copy. No claim of runtime append equivalence. Bounds are chained inclusive 0<=index<=count. Terminal index yields null before prior coverage rewind. Prefix zip stops at shortest of three lists; mismatch short-circuits dirty check; max(source,decision)>=dirty invalidates equality. Retain checkpoint and output slices; no in-place mutation of stored lists during replay. Old output stop must exist to reuse even when dirty null; equal dirty rescans. For retained outputs rescan after dirty, newly emitted outputs from decision. Assign checkpoints, keys, unresolved output, result, then covered_until (last lower timestamp +1 microsecond, not candle duration or main end), then return shallow result. No local rollback or independent prefix data proof.

### LC24 — detect_stopalls
Instantiate detector and return detect. Forward supplied direction,S/E,chronology unchanged to constructor; then return detect result, without local recovery.

## Order context and module identity
