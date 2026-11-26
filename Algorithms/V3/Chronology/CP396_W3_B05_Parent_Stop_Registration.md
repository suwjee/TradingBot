# CP396 — Independent local Parent-Stop Order registration

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA40 lines 1339–1435. B05-13. Source-only, no execution.

## OA40-A — lines 1339–1342

Interface takes owner, parent_type, parent and exact parent_stop event; implicit None on successful completion and early returns. Docstring is intent, not cardinality proof. No direction-sensitive geometry here.

## OA40-B — lines 1343–1347

Only exact S reads source_time then int(source_index); membership in invalid S roots first, accepted E source identities only if first false. Either true returns before reset/candidate calls. Other types bypass veto; no whitelist.

## OA40-C — lines 1348–1349

All surviving types call OA25 using source_time and parent_stop; bisect_right excludes equal source, includes reset equal stop, assuming sorted reset times. No local timestamp normalization or reset map synchronization; true returns.

## OA40-D — lines 1350–1360

OA23 precedes independent OA19 call. Both use exact parent_stop and None deadline. S: bounded true, trend false, E flag false; E: bounded false, trend true in OA23 only, E flag true in both; others all false. Both calls may populate delegated caches; no local sort or filter before direct.

## OA40-E — lines 1361–1369

Only non-None direct considered. Normalize integer First/Break pair. Test every match by identity in native order, short-circuit on equality regardless of cause; reset-only collision suppresses supplementation. Empty pool permits append. If absent resolve stop triple then assemble nine-field direct match, crossing may be None, parent-stop singleton and exact parent_stop. No renewed deadline, sort, chronology or single-owner reduction; appended direct can coexist with another parent-stop owner.

## OA40-F — lines 1371–1376

Capture ledger reference after candidate supplementation; previous_index starts None. Only exact dict (not subclass) and truthy carried cache permit getattr creation index with default None; short-circuit. Fresh list records new row references; earlier-existing flag false.

## OA40-G — lines 1377–1384

Traverse native matches order. Unpack first six before slots 6/7; slot 8 unused. Skip without parent-stop cause; canonical integer First/Break key then lookup. Exact None alone is new; no truthiness substitution. No dedup/sort beyond physical key.

## OA40-H — lines 1385–1400

New row stores unchanged match geometry, reaction reference, crossing, fresh empty cause set. Publish first, then OA26 indexes confirmation, then append same row reference. Existing non-null geometry/index retained. Read required causes key then assert isinstance(set), subclasses allowed; assertion subject to host assertion mode. No B cause deletion.

## OA40-I — lines 1401–1412

Nested family default getattr evaluated eagerly even with color; stringify chosen value. Read optional number; base label supplied type, E+number for exact E and non-None including zero. Membership in sequence_resets rereads source_time to lookup; override StopAll+mapped number and empty family for ANY type. Exact five-field tuple parent-stop,label,family,function parent_stop,required source_time. Match slot 8 not used, no Decimal conversion.

## OA40-J — lines 1413–1421

Only absent exact tuple updates. Try min item[3] for existing causes whose item[0] is parent-stop (no shape guard), default None. Earlier iff no min or parent_stop strictly less; equal not earlier. Exception in scan/min/comparison sets conservative true; membership, tuple formation and set.add outside catch. Add new tuple even if later/equal; malformed provenance can fail outside catch.

## OA40-K — lines 1422–1426

Only earlier creation on existing row sets flag. New rows independently trigger invalidation; later/equal distinct causes retained without changing earliest native parent event. Every B confirmation remains separate input to carried eligibility (OA50); untouched. Duplicate tuple skips minimum and addition.

## OA40-L — lines 1427–1433

After successful entire loop invalidate carried if new rows or earlier existing flag. OA28 clears results then creation index and pending append. After invalidation check ordered short-circuit: no earlier existing mutation, previous index non-None, saved ledger is same local ledger, saved payload non-None, saved entry count plus new rows equals ledger length. Only then save pending pair; no validation or Decimal operation here. OA52 later consumes and validates new rows/context, can fall back. No explicit post-stop flush; OA26 maintains confirmation/pending state.

## OA40-M — lines 1434–1435

Implicit None, no transaction. Errors before final invalidation may leave rows/indexes/causes/delegated caches mutated. Failure in invalidation or append condition may occur after mutation; only prior-min/comparison Exception caught. No proof for arbitrary custom object, chronology or cross-owner runtime.

## Consumer boundaries

- engine/pipeline/order_audit_engine.py [809,918]: OA19 direct query owns selection and cached result; OA40 calls independently after OA23.
- engine/pipeline/order_audit_engine.py [921,1070]: OA21/22/23 merge geometry, select at most one parent owner within map, maintain reset-leg independence, choose earliest crossing deadline and eligible confirmations, sort and cache; OA40 can append after reduction without rechecking.
- engine/pipeline/order_audit_engine.py [1089,1132]: OA25 reset (source,stop]; OA26 confirmation sorted insertion and post-stop pending; OA28 carried cache/index/append clear only.
- engine/pipeline/core_utils.py [64,66]: Physical identity exact integer FirstIndex/BreakIndex; label/number/confirmation/cause not key.
- engine/pipeline/order_audit_engine.py [1635,1740]: Earliest parent creation plus every B confirmation; deferred append consumed and validated under local Decimal context, identity/length/timezone guards; fallback on invalid native rows. OA40 does not validate at registration.
- engine/pipeline/e_zone_detector.py [[343,345],[401,401],[622,622],[866,866],[1002,1002],[1048,1048],[1160,1160],[1490,1490]]: Caller supplies invalid/accepted root sets, reset state and stop event; parent race computes carried before registration, then post-stop queries. Stopped S prescan also calls registration. Actual owner state conditional.
- engine/pipeline/order_audit_engine.py [2046,2094]: Rebuild sets accepted E identities, excludes invalid S time causes from historical ledger, clears and registers B legs first; re-register S and E or StopAll based on source mapping when parent stop exists. Final prepared owner reduction is separate, not OA40 local invariant.

## Verification

309 category rows: 84 prior W1 and 225 additional; seven historical supplements; all 3883 prior rows structurally revalidated without overlap. Local scoped only; cross-owner acceptance remains open. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP396_W3_B05_Parent_Stop_Registration_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP396_Completion.json).

Separate source-first pass by GPT, not independently staffed. Local review only; caller chronology, native tuple shapes, reset synchronization, cache/Decimal context and final cross-owner ownership remain conditional.

No runtime, RAW payload, ZIP or production changes. Counts derived from pinned canonical source-backed inventory, not newly generated AST. CP321–395 historical progress retained via active plan and CP395 completion; direct re-read of all 12 relevant B05 registers, not every unrelated historical artifact.
