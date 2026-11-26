# CP389 — Independent local healthy direct geometry and trend-leg order review

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 689–808. B05-06, OA16–OA18. Source-only, no execution.

## OA16-A — lines 689–706

Signature defaults bounded continuation to false but body never reads it; restarted is initialized and later written but never read. Missing finder means exact None, not falsey. Resolve clamped containing main index and retain exact original gate event; no added rounding.

## OA16-B — lines 707–713

Loop includes end_index. Finder called with order direction, current main index, end index and exact event; exact None ends search immediately; candidate First resolved through main-time array.

## OA16-C — lines 714–720

Membership in blocked First set evaluated before original-gate main-time equality. Only conjunction vetoes. Recompute containing index from original start, not current search event; on veto convert candidate first_idx to int, add one, set search event to candidate First and continue. No locally asserted monotonicity.

## OA16-D — lines 721–731

Compute candidate confirmation in order direction before selecting prior owner. Right bisect opposite confirmation sequence at current search event minus one includes equal confirmations; negative means no prior. Position alignment and sorted confirmations are conditional owner contracts.

## OA16-E — lines 732–743

Only non-null prior participates; use prior integer First index and stored reset list (empty default). First stored Reset with search_event strictly less than reset_time and reset_time at most candidate confirmation wins; break. If found, use clamped containing Reset main and exact Reset event, set otherwise unread restarted flag and continue. No main+1 or local progress assertion; exact lower event respected by finder contract.

## OA16-F — lines 744–761

Physical identity is integer First/Break pair; lookup first-win canonical position, None terminates rather than trying another geometry. Return canonical object, 1-based position and stored confirmation, not provisional candidate data; no repeat of prior Reset/confirmation checks after replacement. Loop exhaustion returns None.

## OA17-A — lines 764–782

Exact None finder returns None. Right bisect sorted trend confirmation times excludes equality at start. Iterate sorted positions in ascending order; unpack confirmation, First and trend; skip First <= start.

## OA17-B — lines 783–792

Cache by sorted trend position using membership, not truthiness; compute OA18 only on miss and store successful return including None. Non-null canonical position (including zero) returns first qualifying canonical 1-based number/object/stored confirmation. No local cache invalidation or repeat candidate validation; exhausted returns None.

## OA18-A — lines 794–797

Reject truthy behavior_internal (missing defaults false). No local finder presence check; relies on OA17 caller or compatible direct caller.

## OA18-B — lines 798–802

Call finder with order direction, integer trend Break, end index and exact trend confirmation. Short circuit None before gate-label access; gate decision must equal literal continue, missing defaults None.

## OA18-C — lines 803–808

Call candidate confirmation resolver even though its value is discarded (failure propagates). Resolve First and reject First <= trend confirmation. Return canonical physical lookup of reaction identity, including None. No local blocked-First check, canonical confirmation gate, price arithmetic or fallback.

## Consumer boundaries

- engine/pipeline/e_zone_detector.py:382–417,559–566: Owner installs finder and initializes audit, blocked set and exception tuple. Sequence reset setter clears candidate/carried/post-stop/direct caches but not the trend-leg-position cache. Main index delegates clamp=True; confirmation delegates chronology; First derives from times[int(first_idx)]. Cache reuse assumes run-consistent sorted position, geometry, arrays and callbacks.
- engine/pipeline/order_audit_engine.py:809–920: OA20 calls OA16 before native fallback; confirmation_after applies to returned canonical geometry; separate native selection and E exception rules are not local OA16 rules. Candidate rejection in OA16 does not eliminate OA20 fallback.
- engine/pipeline/order_audit_engine.py:983–1030: order_candidates calls direct path first; optional allow_trend_leg_continue gates OA17 separately, and successful matches enter identity merge. Local geometry result does not itself prove final parent-stop ownership, stop or crossing.

## Verification

309 category rows, 76 prior W1, 233 additional; six supplements; 2049 prior rows revalidated without overlap. Local scoped acceptance only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP389_W3_B05_Healthy_Direct_Geometry_Trend_Leg_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP389_Completion.json).
