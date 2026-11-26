# CP390 — Independent local direct parent-stop selection

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 809–920. B05-07, OA19–OA20. Source-only, no execution.

## OA19-A — lines 809–819

Native five-element tuple key in order: exact start, deadline, bounded flag, E flag, optional keyword-only confirmation_after. Defaults E=false and threshold=None. No normalization, coercion or rounding; key omits owner/dataset/direction state so it relies on per-owner stable lifetime.

## OA19-B — lines 820–821

Return cached object by reference if get is not None, otherwise check key membership; cached None is a valid negative result. Short circuit membership if non-null; no clone, recomputation or revalidation on hit.

## OA19-C — lines 822–827

On miss call OA20 with four positional values and keyword confirmation threshold; store exact returned tuple or None only after successful computation, then return it. Errors propagate; no wrapper-level rollback of any inner cache mutation.

## OA20-A — lines 829–840

Convert start to clamped main index using owner callback, read exact main timestamp at that index, then call OA16 with original exact start and bounded flag. No local catch or fallback for failed index or finder call.

## OA20-B — lines 841–848

Discard geometry only if present AND threshold present AND returned canonical confirmation <= threshold; preserve short-circuit order. Native lower bound uses gate main timestamp and opposite First array, so equal First eligible. If threshold supplied, advance initial native prefix while position is in range and stored confirmation <= threshold. This does not globally filter all later candidates.

## OA20-C — lines 849–865

Separate second loop: range check, First membership in blocked set, then equality of First with original gate time. Only inside that loop, truthy E flag, membership of exact (start,gate_time) pair, then stored confirmation strictly > start permits break retaining position. Otherwise increment position by one. No recheck of confirmation_after after blocked skips and no universal post-start confirmation gate. Do not equate exact event and main timestamp.

## OA20-D — lines 867–878

Initialize native candidate None. In-range position constructs 1-based position, actual opposite object, and stored confirmation from aligned arrays; no identity deduplication or recomputed confirmation. If geometry exists, read restart label from returned canonical object (default None), even if deadline absent; otherwise label None.

## OA20-E — lines 879–887

Preference is ordered conjunction: deadline non-null, geometry non-null, label exactly restart, and (deadline equals range_end OR deadline strictly before geometry confirmation). Equality to range_end short-circuits second comparison. Equality to geometry confirmation alone does not qualify. Not a general deadline clipping or geometry eligibility rule.

## OA20-F — lines 888–895

Native crossing initially None. Whenever native candidate exists, eagerly resolve its canonical stop by number and exact object, destructure triple retaining Decimal level, then call crossing at stored confirmation with unchanged level. Runs even if geometry preferred. No cast, price comparison, quantization or alternative directional arithmetic here; owner resolves strict crossing and horizon. Exceptions propagate and inner caches may remain changed.

## OA20-G — lines 897–911

Mutually exclusive priority: preferred geometry first; else geometry present AND native crossing exactly None AND (native absent OR geometry First strictly earlier than native First); else native if present. No evaluation of First comparison when native absent or earlier guards fail. Equal First selects native in non-preferred route; non-null native crossing blocks ordinary geometric preference. Pool has at most one element.

## OA20-H — lines 913–920

Empty pool returns None; otherwise min uses key (owner-resolved First main time, stored confirmation), even on singleton, so callback/index exceptions can still propagate. No local retry, further threshold/deadline validation, cloning, registration or stop/cross requirement on returned geometry.

## Consumer boundaries

- engine/pipeline/order_audit_engine.py:613–688; engine/pipeline/e_zone_detector.py:382–417,559–566: Opposite First and confirmation arrays retain owner order (not locally sorted), positional alignment and callback stability required. Canonical stop uses number cache only for exact indexed object; context start discarded. E owner sequence reset setter clears direct cache; this is not proof of freshness under arbitrary mutation.
- engine/pipeline/order_audit_engine.py:689–761: OA16 may reject provisional noncanonical geometry, or return canonical replacement without revalidating its confirmation; OA20 threshold applies to returned canonical timestamp. OA16 bounded flag is unused internally but remains in OA19 key.
- engine/pipeline/order_audit_engine.py:1459–1477; engine/pipeline/e_zone_detector.py:505–556: Native crossing delegated unchanged Decimal stop level. Base search uses half-open lower window from max(confirmation,range_start) to range_end, strict less unless order direction bearish, then strict greater; cache stores None and event tuple. E live override uses dirty-time and continuation search; no claim of general live equivalence or arbitrary callback behavior.
- engine/pipeline/order_audit_engine.py:1002–1070,1269–1284,1354–1369: Candidate collector calls OA19 without threshold, then merges identity and separately enforces deadline and ownership; primary path supplies exact stop as threshold, no deadline, bounded false; registration can append direct if identity absent. Neither caller policy is a universal local OA20 constraint. No ledger mutation performed by OA20 itself; delegated caches can mutate.

## Verification

288 category rows, 76 prior W1, 212 additional; six supplements; 2358 prior rows revalidated without overlap. Local scoped acceptance only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP390_W3_B05_Direct_Parent_Stop_Selection_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP390_Completion.json).
