# CP400 — Independent local carried Order lifecycle query

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA52 lines 1722–1797. B05-17. Source-only, no execution.

## OA52-A — lines 1722–1728

Read parent decision_event_time via getattr with None default; only None means absent. Return a new empty list before forming key, accessing caches, pending append, ledger, or initial records. No parent class/type or direction gate. Attribute retrieval exceptions are not caught.

## OA52-B — lines 1729–1732

Key is the native pair (lifecycle_start,parent_stop), not parent identity, parent type, direction, ledger version or Decimal context. Dictionary lookup precedes native datetime validation and may fail (e.g. unhashable value). Non-None cached value, including empty tuple, is a hit: return a new shallow list, no refresh or eligibility recomputation. Native equality/hash, not tzinfo identity, governs this cache lookup.

## OA52-C — lines 1733–1741

Read optional creation index. Refresh if index is None or carried result cache falsey; missing index short-circuits truth test. Invoke class-qualified OA51 first; only None triggers full fallback, capturing current ledger then list of values in native insertion order and class-qualified OA50. Publish outer triple even if OA50 returns None. Reuse an existing triple when result cache nonempty; no fresh ledger identity, size, row or prefix check on reuse. Unpack stored triple, discard ledger binding locally. OA51 exceptions propagate; pending consumption/partial mutation may already have occurred. Full snapshot list aliases original row objects, not a deep copy.

## OA52-D — lines 1742–1745

Native route requires non-None validated payload and both endpoints exact datetime (not subclass), each with tzinfo identical by is to stored timezone. all evaluates start then stop, type test before tzinfo access; short-circuits. Empty valid event list is not failure. No normalization, offset equivalence or query-order validation; mismatch selects legacy, not rebuilding solely for mismatch.

## OA52-E — lines 1746–1753

With native payload use sorted (creation,ordinal) events; right-bisect upper sentinel (start,len(entries)) excludes every start-equal valid ordinal; left-bisect lower sentinel (stop,-1) excludes every stop-equal valid ordinal. Slice selects strict open interval start<creation<stop conditional on valid sorted events and 0<=ordinal<len(entries). Build set of ordinals across slice then sort ascending, restoring ledger order; duplicates per row collapse, not distinct rows with same physical identity. Generator lazily yields entries[ordinal] and None marker, indicating creation predicate already established. No direct comparison start<=stop or exception catch.

## OA52-F — lines 1754–1759

Otherwise build lazy generator over snapshot entries in order, class-qualified OA49 evaluated as each row is requested. OA49 selects earliest ordinary parent-stop and all B physical confirmations. No prefiltering of legacy rows by timestamp index; if creation result is non-None and falsey skip before confirmation/cross reads. Native None marker bypasses this skip. Validation previously attempted may have inspected other rows but OA50's Exception fallback is not a catch around the legacy scan.

## OA52-G — lines 1760–1770

For each remaining row read required confirmation then optional stored stop_cross before rejection expression. Reject in exact short-circuit order: legacy non-None creation list lacking any strictly start<created<stop (any evaluates in its list order), confirmation strictly greater than stop, crossing None, crossing slot 2 strictly less than stop. Both confirmation=stop and crossing=stop allowed; no separate crossing>confirmation, sequence-reset, parent identity, geometry, deadline or direction predicate here. Native route bypasses creation any but shares remaining tests. Missing key, comparison and indexing failures propagate; an earlier true reject suppresses later checks, not preceding reads.

## OA52-H — lines 1771–1776

Read reaction only after eligibility; construct nine-field OrderMatch in order: int reaction_number, same reaction reference, stored confirmation, as_decimal(stop_level), int stop_source_index, stored source time, same stored crossing object, singleton carried-live provenance, None parent-stop-cause time. Conversion occurs after filtering, in caller context, no recomputation of accepted crossing, no rewriting row values, no source selection change. No physical-identity key or map used by this query; malformed eligible conversion propagates.

## OA52-I — lines 1778–1789

Only after accepted traversal call dynamic OA45, assert First-time index non-None (not nonempty); no local repair. OA45 may materialize all initial rows and compute crossing before slice or reuse cached records. Bisect left at lifecycle start and right at parent stop selects inclusive First-time range, unlike accepted strict creation range. Iterate primary stable records; read confirmation, reject >stop before reading crossing; reject None or crossing[2]<stop. Use dynamic OA46 to append carried-live match; no creation-event test, no direct registration and no dedup against accepted matches or within initial route. Same physical identity can occur more than once. Initial exceptions occur after accepted traversal; no final result cached on failure.

## OA52-J — lines 1790–1795

Stable sort combined list ascending by exact stored crossing slot 2, then negative int First index (larger First index wins equal crossing). No confirmation, Break, source or identity tie key. Equal complete sort key retains accepted-before-initial and native traversal order. Key reads crossing then dynamic First conversion; comparison/conversion errors propagate, no sort catch. Publish tuple(result) under original key only after successful full sort; return original fresh list on miss, shallow list copy on hit. Tuple/list containers differ but nested reaction/crossing objects remain shared. Earlier index and initial-record cache side effects are not rolled back if later failure occurs.

## Consumer boundaries

- engine/pipeline/order_audit_engine.py [[574,599],[1114,1140],[1199,1199],[1248,1248],[1309,1309],[1337,1337],[1371,1433],[2283,2287]]: Run-local carried cache and initial geometry structures; clear, B registration, primary reparent/relabel and rebuild invalidate carried index/results. Parent registration may stage append only under prior exact dict and identity/size gates, with no earlier existing creation. Reuse requires owner invalidation, not enforced by OA52.
- engine/pipeline/order_audit_engine.py [[1524,1596],[1635,1721]]: OA45 materializes all initial records, crossing and normalized level, primary sort First/confirmation/FirstIndex/BreakIndex, First array and separate confirmation view; OA46 returns original geometry and supplied causes. OA49 earliest ordinary creation plus every B confirmation; OA50 exact native validation and isolated Decimal context returns None on Exception; OA51 consumes pending and mutates prefix event/entry arrays in place, may propagate exceptions.
- engine/pipeline/core_utils.py [[51,53],[64,66]]: as_decimal retains Decimal instance else Decimal(str(value)); actual selected conversion in caller context. Physical identity is (int FirstIndex,int BreakIndex); OA52 never calls identity helper or performs physical-identity dedup.
- engine/pipeline/e_zone_detector.py [[398,411],[608,668],[670,697]]: Sequence reset setter clears result caches, not explicitly carried index/pending; empty carried cache causes refresh. _zone obtains inherited S, gate-owned initial and carried before registering current parent, then post-stop accepted, direct; S deadline depends on not carried. gate_owned evaluated but unused in this body. Global merge stable crossing/negative First across direct,inherited,carried and regrouped post-stop; skip disowned-S-only via physical identity and prospective source; first surviving route chosen. _build_zone uses max(parent stop,crossing) for decision. No OA52 cross-route dedup or final E ownership adjudication; these are caller concerns.

## Verification

296 category rows: 77 W1, 219 additional; 6 historical supplements. All 5174 prior rows (1130 W1, 4044 additional), 98 supplements, and 1892 CP316 links structurally reconciled; exact disjoint local union 5470/8318. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP400_W3_B05_Carried_Order_Lifecycle_Query_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP400_Completion.json).

Separate source-first GPT pass, not independently staffed. Local source contracts only. Conditional on immutable initial records, stable row/ordinal ownership, cache invalidation, native datetime comparability and caller Decimal context; no runtime equivalence asserted.

No RAW payload, runtime, ZIP or production changes. Counts from pinned canonical source-backed inventory, not newly executed AST generator. Initial inventory count omitted string comprehension-filter IDs in three prior ranges; corrected using canonical node suffix map, full checks returned zero missing/extra. CP396 read via pinned path, not blob endpoint. Git blob identities used; no independent SHA-256 claimed.
