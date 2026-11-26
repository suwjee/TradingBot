# CP392 — Independent local sequence reset, confirmation index and cache invalidation

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 1089–1134. B05-09, OA25–OA29. Source-only, no execution.

## OA25-A — lines 1089–1093

Read owner-published sorted reset timestamps. Upper bound on exact start skips every equal timestamp and selects the earliest strictly later entry in a sorted comparable sequence. No timestamp conversion, sorting or mutation in query.

## OA25-B — lines 1094–1098

Return ordered conjunction: position in range before reading element, then timestamp <= end. Empty/exhausted array returns false without access; equal end included, equal start excluded; inverted/equal interval yields false under sorted comparable native timestamps. No local interval normalization or exception recovery.

## OA26-A — lines 1100–1107

Unpack supplied physical identity as two values, no integer coercion or validation. Form tuple (exact confirmation, First, Break), compute right insertion by lexicographic full tuple, then insert into existing index list in place. Earlier/equal timestamps ordered by integer First then Break under native contract; exact duplicate placed after equals, not deduplicated. No ledger existence check, ledger mutation or independent resort.

## OA26-B — lines 1108–1112

After index insertion, inspect sorted-audit state by isinstance(dict), including subclasses and empty dictionary. If true append same tuple to pending list; otherwise set sorted-audit reference None, including prior False fallback sentinel, without clearing pending. Does not clear post-stop result or carried cache here. Index mutation remains if subsequent append or attribute operation fails.

## OA27-A — lines 1114–1119

Clear existing authoritative ledger in place, then existing confirmation index in place, invoke carried invalidator, then post-stop invalidator. Native aliases observe clears; no replacement, transaction, catch, finally or rollback. Exception stops subsequent operations. Does not reset candidate/direct/cross/canonical stop/initial-order/other geometry caches by itself.

## OA28-A — lines 1120–1128

Clear carried result mapping in place; then assign creation index None; then creation append None. Do not clear post-stop state or authoritative ledger/index. Source comment describes creation dependency; actual caller decides whether mutation changes eligibility. If clear fails, later assignments not reached.

## OA29-A — lines 1129–1134

Clear post-stop result mapping in place, set sorted accepted-audit reference None, clear pending list in place, in that exact sequence. No change to carried state, initial sorted stream or authoritative ledger/index. Existing issued references are not explicitly revoked. No catch or rollback.

## Consumer boundaries

- engine/pipeline/e_zone_detector.py:393–417: Getter returns underlying reset mapping, setter creates dictionary copy, sorts its keys into reset array, clears existing candidate/carried/post-stop/direct result caches in that order. Setter is not OA28/OA29 and does not explicitly null creation/index/pending/sorted-audit state. Direct mutation through getter is not proven synchronized. No empirical stale-cache claim.
- engine/pipeline/order_audit_engine.py:557–612,1371–1434,1685–1732: Ledger/index/pending initially fresh; accepted new row published before OA26, then causes; carried invalidation on new entries or earlier existing creation (including conservative exception). Validated append may be deferred, consumed on next query. OA26 does not itself flush carried. Cache/comment alone does not establish safety for arbitrary mutation.
- engine/pipeline/order_audit_engine.py:1798–1826,1920–2008: Post-stop result cache key includes parent stop and confirmation-index length; strict crossing after stop and confirmation and no reset in (stop,cross]. Sorted view rebuilds from whole index if None, otherwise pending, under local Decimal context; validation exception sets False and clears pending, then falls back. OA26 appends only with dict state, otherwise invalidates sentinel by None. Sorted initial side independent of OA29. Native consistency and caller-managed replacement/revocation required.
- engine/pipeline/order_audit_engine.py:1220–1250,2068–2088: Revocation removes ledger entries, filters index in place, explicitly invalidates post-stop on revocation and carried on changed/revoked. Rebuild snapshots prior entries then OA27 and re-registers B legs. OA27 does not certify full rebuilding or rollback. No direction-specific price arithmetic in reviewed functions.

## Verification

103 category rows, 17 prior W1, 86 additional; five supplements; 3067 prior rows revalidated without overlap. Local scoped acceptance only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP392_W3_B05_Reset_Confirmation_Index_Cache_Invalidation_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP392_Completion.json).
