# CP352 — W3 MarketChronology local forensic review

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`; Reaction source blob `9adffb832ffa231ba0cb01de507a30fbe62be0b0`, lines 1132–1369. Separate same-assistant source-first pass, not an independently staffed or blind audit.

## Local disposition

PASS_SCOPED for RE53–RE62 only: 153 W1 rows, 460 additional category rows, 8 historical supplemental items, 61 source contract groups. The exact category/row/node/span joins are structural evidence; source-group semantics and each row's operation/role supply the scoped semantic review. These are overlapping categories, not distinct rules or execution paths.

- Constructor: rejects timeframe below one before assignments; retains sequence references. Non-null checks select prepared time arrays, whereas truthiness selects the lower index itself. Prepared index identity validation belongs to the separate shared-index registration path, not this constructor. Caches are separate, instance-owned dictionaries, without local invalidation or generation keys.
- Mapping: right bisect minus one, last equal position; underflow clamp only; no upper horizon validation. Lower search boundaries are left bisects or physical length for absent end. No local sort or timestamp-row alignment validation.
- Reset: ordered key fields, non-null cached result wins; truthy second then truthy display parse then required timestamp. Invalid truthy parse raises. None fallback remains a miss on next lookup.
- Confirmation: key includes raw direction, boolean flag, integer First/Break, string geometry and conditional start. Miss uses Break timestamp plus nominal timeframe; false flag scans from open, invalid start resets to open. Strict directional scan returns first matching lower timestamp; no hit caches Break open. No lower-index first-cross call; no proof flag, local direction validation, or freshness check.
- Canonical stop: exact string A route uses main anchor/context through Break, strict improvement; first ties persist. Improved source uses candle.index and subsequent timestamp lookup requires index alignment. Non-A uses previous supplied ordinal after <=1 guard; no independent healthy test, no local upper ordinal guard and no creator ownership.

## Findings

CP352-F01: static lexical call candidate for RE54 at 1183 names the class wrapper; native unqualified lookup targets module-level RE02 at 143–145. Preserve historical inventory, append correction and clarify RE54.

CP352-F02: clarify lifetime/aliasing and absence of local invalidation in RE53, RE60/RE61. Actual cache safety depends on caller coherence; no runtime safety claim.

CP352-F03: open full consumer trace. Bridge batch/live construction, A flag, Order stop adapters, E and Bridge proof are bounded reviewed source paths, not full cross-owner acceptance.

## Evidence

- [Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP352_W3_MarketChronology_Local_Forensic_Register.json)
- [Consumer boundary register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP352_W3_Chronology_Consumer_Boundaries.json)
- [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP352_Completion.json)

W3 remains INCOMPLETE; W4 NOT RUN. B02 complement 1–1131 and 1370–2908. Continue with LowerTimeframeIndex and shared/reflected indexes, 886–1131. No RAW payload, runtime, ZIP, production or main change.
