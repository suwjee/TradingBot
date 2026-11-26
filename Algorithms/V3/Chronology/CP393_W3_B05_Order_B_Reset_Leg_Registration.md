# CP393 — Independent local accepted Order_B reset-leg registration review

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 1135–1201. B05-10, OA30. Source-only, no execution.

## OA30-A — lines 1135–1141

Input is a sequence of discovered accepted reset-leg records, not an acceptance calculation. Truthiness triggers carried invalidation before iteration, including all-duplicate sequences. Iteration follows supplied order; native empty sequence does no work. No new sort of leg input, parent-stop eligibility or reset/cross search validation here.

## OA30-B — lines 1142–1145

Read physical reaction, derive canonical integer First/Break identity via owner helper, then authoritative ledger get. Exact None (absent or explicit None) enters creation. Existing non-null entry reused without geometry, number, confirmation, stop/cross or parent causes replacement; no comparison of supplied evidence with previously recorded geometry.

## OA30-C — lines 1146–1160

On creation resolve canonical stop with supplied reaction number and physical reaction; retain returned exact Decimal level, source index and source time. Construct new row using leg number, reaction reference, leg physical confirmation, returned stop triple, crossing from leg physical confirmation with unchanged level, and fresh empty parent cause set. All field expressions and crossing evaluated before publishing ledger row; exception leaves no newly published row here, but pre-loop invalidation or delegated caches may remain.

## OA30-D — lines 1161–1164

Publish newly constructed row at physical identity, then index that identity using supplied physical confirmation. OA26 right insertion and pending-state effects apply. If insertion fails, row may already exist; no transaction. Existing non-null row skips stop/cross and index insertion, including repeated physical identity.

## OA30-E — lines 1165–1175

After creation or reuse, read reset reaction and construct full B cause. Kind reset-leg; record post-stop behavior type, exact stop time, source index, source time independently from anchor behavior type/index/time/extreme. Anchor extreme uses native str of supplied value only, no rounding or Decimal normalization.

## OA30-F — lines 1176–1184

Reset reaction identity is fresh list of int First and int Break. Breakout timestamp read from main times at integer Break, distinct from supplied exact reset confirmation. Store supplied reset source index, string of broken level and reset event time. No clamping, sorting, recomputing reset or fallback on missing/index/type errors.

## OA30-G — lines 1185–1191

Record native string of leg boundary, supplied boundary source index/time, strict-break time, fresh physical identity list from normalized key and supplied physical confirmation. Exactly three price-like fields stringified in cause (anchor extreme, reset broken level, leg boundary); authoritative row stop level remains returned Decimal. Cause may record new supplied physical confirmation even when existing row retains older one; no local consistency reconciliation.

## OA30-H — lines 1192–1194

Evaluate fresh empty list default and setdefault order_b_causes; existing list reference reused, not replaced. Full native dictionary equality membership determines duplicate, not partial key, physical pair or separate OA12 signature. New distinct dictionary appended to same list before sorting. Duplicate does not sort or invoke per-add invalidation; initial truthy-sequence invalidation still happened.

## OA30-I — lines 1195–1199

Stable in-place ascending sort of entire cause list by exact postBehaviorStopTime, resetTime, strictBreakTime and physicalOrderIdentity list lexicographically. No anchor, confirmation, source or ordinal tie key; equal ranks retain prior order, new equal-ranked cause follows earlier existing ones. After successful sort, invalidate carried results and creation state. Append/sort failure propagates, no guaranteed rollback or subsequent invalidation. No explicit post-stop flush other than earlier OA26 index maintenance.

## OA30-J — lines 1200–1201

Implicit null return on normal exhaustion; no return of accepted rows or proof of acceptance. Source-only record mutation; no runtime claim.

## Consumer boundaries

- engine/pipeline/order_audit_engine.py:40–76,530–553; engine/pipeline/core_utils.py:59–66: Frozen reset-leg record fields carry owner-provided stop/anchor/reset/physical evidence; references inside need not be immutable. Physical identity is integer First/Break. OA12 multi-field leg signature is distinct from full dictionary equality dedup here, including fields omitted by signature; do not substitute.
- engine/pipeline/order_audit_engine.py:653–688,1100–1132,1459–1477: Canonical stop/strict lower crossing delegates unchanged Decimal level. Exact object number cache conditional. Index insertion after publication, full-tuple right bisect; dict sorted audit appends pending, otherwise reset None. Carried invalidator clears result map and nulls creation index/append; post-stop invalidator not called here. No local direction-specific arithmetic.
- engine/pipeline/order_audit_engine.py:1202–1249,2074–2099: Later reparent may mutate post/anchor role labels separately and revoke empty entries, with explicit invalidation. Rebuild snapshots prior parent causes, clears ledger/index and appropriate caches, registers stored B legs before S/E parents. OA30 does not guarantee downstream accepted identity or reparent consistency.
- Algorithms/V3/State_Machines/04_Order_Ledger.md OB12: Registration is distinct from discovery/acceptance; source has eager sequence-level and successful unique-add invalidation. Parent set and B list remain separate. No runtime, arbitrary mutation, or cross-owner certification.

## Verification

166 category rows, 26 prior W1, 140 additional; five supplements; 3170 prior rows revalidated without overlap. Local scoped acceptance only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP393_W3_B05_Order_B_Reset_Leg_Registration_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP393_Completion.json).
