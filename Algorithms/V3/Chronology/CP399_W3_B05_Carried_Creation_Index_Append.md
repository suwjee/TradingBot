# CP399 — Independent local carried creation validation and append extension

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA50–OA51 lines 1644–1721. B05-16. Source-only, no execution.

## OA50-A — lines 1644–1653

Initialize fresh local event list, timezone sentinel None, separate have_timezone false before try. Enter localcontext with inherited Decimal settings, isolate flags and traps from caller; no forced precision or rounding change. Enumerate entries in supplied order from zero, including rows later skipped. Exception handler encloses context enter, body, sort and exit; initial allocations outside try. No ledger/cache publication here.

## OA50-B — lines 1654–1659

Require exact built-in dict (not subclasses). Read causes then order_b_causes using missing-key default empty tuple, without replacing explicit None. First container must have exact set/frozenset/tuple/list type; second exact tuple/list; second type gate short-circuits if first invalid. Return None on failure, not empty successful index.

## OA50-C — lines 1660–1666

Test every ordinary cause until first failing exact tuple or empty tuple; no full arity/type validation of slots at this step. Then test every B cause until first non-exact dict. Only after both checks invoke class-qualified OA49 (not instance override). Its earliest ordinary parent-stop reduction and all B confirmations determine created list. If empty skip row before reading confirmation, geometry, price or crossing; original ordinal unchanged.

## OA50-D — lines 1667–1673

Read required confirmation then optional stop_cross then required stop_source_time before crossing shape validation. Date groups start with created then (confirmation,source time). None crossing permitted; otherwise exact tuple, length at least three, first slot exact int; short-circuit in that order. Append slice of slots 1 and 2 as additional date group; ignore extras. No crossing presence/chronological eligibility, positivity or bounds requirement.

## OA50-E — lines 1674–1681

Traverse groups and their events in order. Each event must be exact datetime, not subclass. If any earlier event processed, require current tzinfo is same object as remembered timezone, not equality or matching offset; first event seeds even None. Update timezone then flag for each accepted event. No conversion or timezone normalization; all dated rows share identity, even dates not subsequently indexed. Empty validation returns timezone None with no events, distinct from failure.

## OA50-F — lines 1682–1687

Read required reaction, then eagerly construct four-field tuple in order: reaction_number, stop_source_index, reaction.first_idx, reaction.break_idx; all reads occur before any exact int test. Generator any short-circuits on first non-int. Bool and subclasses rejected; no geometry bounds, sign, relation, object class or ledger-key identity check.

## OA50-G — lines 1688–1691

Require exact stop_level type Decimal, str, int or float (bool/subclasses rejected). Read level again for as_decimal, which retains Decimal instance else Decimal(str(value)); require is_finite, reject infinities and NaNs without rounding, positivity or scale gate. No replacement of original row value. Local context isolates validation effects; traps inherited, exceptions trigger fallback.

## OA50-H — lines 1692–1698

For each eligible row deduplicate created dates with native set semantics, extend local list with (event,original ordinal) for each unique event. No dedup across distinct rows; no index by reaction identity. Sort pairs ascending lexicographic by native datetime then ordinal inside context, including empty list. Catch Exception (not arbitrary BaseException) and return None; no partial index returned, caller's legacy path owns evaluation order. On success return exact local list plus last remembered timezone (None possible). No claim that all malformed/exotic inputs are equivalent at runtime.

## OA51-A — lines 1699–1705

Read pending attribute with default None; assign None immediately before checking value or unpacking. Only None means absent. Unpack expected nested pair (ledger,entries,(events,timezone)),new_entries; no local type checks or catch. Malformed pending can raise after consumption, never restored.

## OA51-B — lines 1706–1710

Require ledger is current self.order_audit by object identity before lengths evaluated; require len(old entries)+len(new entries)==len(ledger), counting all rows. Does not verify entry references, exact key order or old prefix contents; relies on owner invalidation and pending producer. Call class-qualified OA50 for new entries only under current context. None rejects; valid empty event list accepted.

## OA51-C — lines 1711–1716

Unpack new event list and timezone. Reject mismatching timezone object only when both event lists truthy; old empty adopts new timezone even when new empty; old nonempty/new empty retains old. No old-event revalidation. Set offset to old entries length, not event count; skipped rows still count.

## OA51-D — lines 1717–1721

Iterate sorted new event pairs, insert (event,offset+ordinal) into original events list using insort_right (right insertion bound on equal complete pairs). Only after all insertions extend original entries list with all new entries, including rows with no indexed event. Return new outer tuple containing same ledger, same mutated entries and same mutated events list with selected timezone. No catch/transaction rollback: insertion or extension failure may leave partial mutation, pending already consumed; no cache assignment in helper itself.

## Consumer boundaries

- engine/pipeline/order_audit_engine.py [[5,15],[1635,1642]]: Native bisect/insort_right, datetime, Decimal and localcontext imports; class-qualified OA49 reduces multiple parent-stop dates to minimum, appends every B confirmation before OA50 dedup. Invalid cause shape or comparison can raise inside validation and yield fallback.
- engine/pipeline/core_utils.py [[51,53]]: Decimal instance unchanged, otherwise Decimal(str(value)); OA50 exact input type check and finite check under localcontext, not mutation of ledger price.
- engine/pipeline/order_audit_engine.py [[1114,1127],[1135,1140],[1371,1433]]: Clear and B registration invalidate carried state; parent registration captures prior index only exact dict ledger with truthy carried cache. New rows and earlier existing parent creation invalidate; equal/later ordinary creation remains in causes but does not trigger earlier flag. Exception in earliest comparison conservatively marks earlier. Pending staged only if no earlier existing creation, prior index exists with identical ledger and non-null validated payload, prefix plus new size matches. Deferred validation under next query context. No unconditional prefix content check in OA51.
- engine/pipeline/e_zone_detector.py [[398,411]]: Sequence reset setter clears named carried query cache, not explicitly creation index/pending; OA52 refreshes when cache empty, extension or complete snapshot. Full synchronization conditional on owner.
- engine/pipeline/order_audit_engine.py [[1722,1755],[1757,1795]]: OA52 returns empty on missing lifecycle start; cache hit bypasses index. On miss refresh if index absent or carried cache falsey, consume OA51 then full values snapshot and OA50 on None. Store outer tuple even validation None. Native query requires exact datetime and tzinfo identity; bounds strictly lifecycle_start<creation<parent_stop by tuple sentinels, selected ordinals deduped and sorted. Legacy generator invokes OA49 lazily. Selection compares confirmation<=stop and crossing>=stop; selected price normalized only in legacy match construction shared by both branches. Initial route then stable crossing/negative First sort. OA52 closure deferred.

## Verification

302 category rows: 94 prior W1 and 208 additional; six historical supplements; all 4872 prior rows structurally revalidated without overlap; all 92 prior supplemental IDs and spans match historical partitions. Local scoped only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP399_W3_B05_Carried_Creation_Index_Append_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP399_Completion.json).

Separate source-first pass by GPT, not independently staffed. Local source review only; old prefix immutability, owner invalidation, native timezone/date comparability and Decimal-context behavior remain conditional. No exact indexed/legacy runtime equivalence asserted; partial mutation is source-visible possibility, not observed runtime defect.

No runtime, RAW payload, ZIP or production changes. Counts derived from pinned canonical source-backed inventory, not newly generated AST. Prior B05 row identity and all supplemental ID/span checks revalidated; unrelated historical artifacts not re-read. Remote Git blob identity used; independent SHA-256 not computed.
