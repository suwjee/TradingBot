# CP395 — Independent local primary Order registration and label reconciliation

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 1250–1338. B05-12, OA32–OA39. Source-only, no execution.

## OA32 — lines 1250–1259

PH registration requires exact bearish direction and kind PH. Direction mismatch short-circuits kind getattr(default None); either mismatch raises ValueError before registration. Valid returns shared OA36 result. Historical reset boundaries retained by OA31; no extra validation here.

## OA33 — lines 1260–1265

PL registration mirrors PH only in exact bullish owner and PL kind; same ordered guard, failure and delegation. No separate temporal or ownership algorithm.

## OA34-A — lines 1266–1270

Lower chronology window: upper bound decision timestamp, lower bound range_end; both endpoints excluded, including duplicate endpoint times. No range_start clamp, no local sort. Normalize parent price using as_decimal (existing Decimal retained, otherwise Decimal(str(value))), no rounding. Select less iff direction exactly bullish; native service uses low < level for bullish, high > level for bearish, equality excluded. Bounds computed before price, then direction flag and crossing call; sorted aligned lower owner and index contract required.

## OA34-B — lines 1271–1276

Position is not None, including zero, selects exact lower timestamp without local index validation; absent position gives None. Only non-null stop calls OA19 with exact stop, deadline None, bounded false, confirmation_after=stop, E flag default false. Return pair stop/direct including nulls. No post-selection confirmation check; OA20 filters initial native prefix then blocked First skips without repeating threshold; do not certify global monotonicity or confirmation > stop for arbitrary streams.

## OA35-A — lines 1277–1282

Dependency query calls same primary search; no direct returns two fields (stop,None), even when stop exists. Otherwise unpack direct into number, reaction, confirmation; no kind/direction wrapper validation in this helper.

## OA35-B — lines 1283–1285

Resolve canonical stop triple, then return six fields in order stop, native repr of direct tuple, native str of exact level, stop source index, stop source time, crossing at confirmation with original level. repr/str evaluated before crossing, not JSON or canonical cross-run fingerprint. No direct ledger registration; delegated caches can mutate and errors propagate.

## OA36-A — lines 1286–1292

Search then always invoke OA31 before null return or ledger lookup. If direct present compute identity for reparent argument first; otherwise None. Even no stop/direct can permit independent anchor relabel or causeless-row revocation by OA31. Failure in identity or reparent aborts further registration. Null direct returns None after successful reparent, not a no-side-effect guarantee.

## OA36-B — lines 1293–1305

Unpack direct, derive identity again, lookup ledger after reparent; exact None enters creation. Resolve stop and crossing and complete row before publishing, with number, reference, confirmation, unchanged stop level and provenance, crossing, fresh empty parent set. Publish first then OA26 confirmation index. Existing non-null geometry retained with no new stop/cross/index operation. No transaction or consistency recheck.

## OA36-C — lines 1306–1311

Build exact five-field parent cause: parent-stop, formatted kind+number, empty family, supplied stop event, parent source time. Membership of exact cause in entry causes; absent adds in place then carried invalidation. Existing duplicate avoids this additional invalidation, not necessarily earlier OA31 effects. Return normalized physical identity. No explicit post-stop flush except OA31 or index state maintenance. Partial effects persist on failures.

## OA37 — lines 1312–1315

High reconciliation delegates with PH prefix; ignores helper return, implicit None. No owner/kind guard analogous to registration.

## OA38 — lines 1316–1319

Low reconciliation delegates with PL prefix; same lack of owner/kind guard, implicit None. Prefix is direction-specific only at this caller.

## OA39-A — lines 1320–1323

Build source-time keyed dictionary of formatted prefix+point number in supplied iteration order; duplicate equal keys last value wins. Does not normalize timestamps or check point kind. Complete dictionary before traversing ledger values in insertion order; initialize changed false.

## OA39-B — lines 1324–1330

Read previous cause set with fresh empty default; unpack each cause as exactly five fields. Rebuild set, retain kind/family/event/source; label replaced by labels.get(source, original) only if native str(label) starts exact supplied prefix, otherwise untouched. No kind gate; unknown source preserves label. Set may collapse equal tuples after relabel. Equality comparison controls replacement, equal retains original collection reference.

## OA39-C — lines 1331–1335

For each ledger row, after parent-set handling call OA01 with prior B collection (fresh empty list default) and same map. OA01 deep copies each cause, checks three role fields in order for either PH or PL prefix independent of wrapper prefix, replaces by matching source time and dedups by complete dictionary equality preserving first occurrence. Compare full list by equality; equal retains original reference, unequal installs new and marks changed. No sort or geometry change.

## OA39-D — lines 1336–1338

After full traversal invalidate carried only if changed, no post-stop or geometry/index mutation. No catch/rollback; later malformed cause or helper error may leave earlier replacements without final invalidation. No actual source behavior modification; conditional contract only.

## Consumer boundaries

- engine/pipeline/e_zone_detector.py:420–435; engine/pipeline/core_utils.py:51–66: Owner delegates first_less/first_greater on [left,right) when lower_index exists; otherwise ascending scan normalizes low/high and applies strict comparison. OA34 uses exact lower time, unchanged Decimal normalization and only direction-sensitive comparison flag. Indexed path equivalence is not a new runtime assertion. Physical identity is integer First/Break.
- engine/pipeline/order_audit_engine.py:809–918,1202–1248: OA19 caches exact tuple or None using threshold in key; OA20 canonical geometry threshold and initial native prefix filter are separate from blocked-First skipping. OA34 requests strict confirmation but does not independently enforce it on returned native candidate. OA31 can independently relabel B anchors even with null stop/direct; removes causeless rows and invalidates caches conditionally.
- engine/pipeline/order_audit_engine.py:25–37,1100–1132: OA01 checks parentType, postBehaviorType, anchorBehaviorType in order against either primary prefix, each source key independent; deep-copy and ordered equality dedup. OA26 indexes published row; OA28 invalidates carried result and creation state only. Registration and reconciliation are not transactions.
- engine/bridge/trading_pipeline.py:3428–3456: Pipeline commit callback picks PL registration for bullish else PH, then prepares OrderAudit. Final resolver and reconciliation wrapper likewise chosen by direction; reconcile receives resolved points through market end index before later audit preparation. These are source-traced call boundaries, not complete cross-owner validation.

## Verification

311 category rows, 70 prior W1, 241 additional; six supplements; 3572 prior rows revalidated without overlap. Local scoped acceptance only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP395_W3_B05_Primary_Order_Registration_Label_Reconciliation_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP395_Completion.json).
