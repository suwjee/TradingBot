# OA-A — Parent-stop Order creation

Status: DOCUMENTED / PARTIALLY_VERIFIED package; this module is not independently validated end to end.

Reaction Mode A/B is geometry, not Order_A/Order_B creation cause. A physical Order_A needs a valid accepted parent stop. Independent geometry may map to canonical opposite Reaction, or have number zero when not matched. One physical Order_A per exact parent stop by earliest confirmation, then First, then Break. Keep an independent reset-leg cause. The canonical strict stop follows the actual Order direction.

## Supplemental directional specification

Supplementary material below is the English semantic prose of the existing synchronized references, pinned to 466eb875070f02cd0dbfb105033422bbe2fd8c70. It is not a fresh branch-level proof. Exact production-source appendices are excluded. Historical acceptance examples remain historical.

## 9. Order_A — ACTIVE canonical physical parent-stop rule

### 9.1 Creation gate

Order_A is the physical `parent-stop` route opened by an accepted strict behavior stop. Ordinarily a bounded/direct Order candidate must match a canonical opposite-direction (Bearish) Reaction identity `(FirstIndex, BreakIndex)`. **Approved 5.4.30 exception:** after an accepted A stop, independently confirmed complete physical opposite Order geometry may enter S OrderAudit even when it is absent from the public opposite Reaction stream. It receives `reactionNumber=0`, not a synthetic canonical Reaction, and retains its real physical First/Break identity and exact confirmation. An incomplete, unconfirmed, or otherwise invalid geometry cannot enter the accepted audit.

After a stopped A, the first eligible physically confirmed opposite Order is immutable for that A. For S/E parent stops, direct bounded geometry may be evaluated subject to the existing canonical acceptance contract. One exact parent-stop cause may own at most one physical Order_A; when multiple candidates compete, earliest canonical confirmation, then FirstIndex, then BreakIndex owns the cause.

For an A parent, “accepted” means the A survives S ownership and current invalid-A lifecycle filtering into the finalized A behavior set. A provisional/detected A that is S-owned, consumed, filtered or invalid cannot open an A-owned Order_A and cannot be retained as an A `parent-stop` cause in the final OrderAudit. Other independently valid creation causes on the same physical Order identity remain valid.

A shared accepted physical Order stop that changes S Blue to S Red must preserve its opposite `order_direction`, identity, First/Break, confirmation, and exact stop provenance.

### 9.2 Canonical stop

Order stop provenance comes from `MarketChronology.canonical_order_stop`. For Mode A it uses the canonical leg-head/floor context required by that opposite Reaction; for Mode B it uses the previous healthy opposite Reaction's outer edge under the established chronology. The Order's exact strict stop uses the **opposite direction** predicate; for this Bullish calculation that is `High > OrderStop`. Equality does not stop an Order.

### 9.3 Parent validity and retention

An S explicitly identified in invalid_s_root_identities is calculation evidence, not an accepted S parent, and cannot create or retain a `parent-stop` Order_A cause. An E derived from that S may be accepted only when its chosen physical Order has a valid creating cause independent of the invalid S. This applies to ordinary chain reconciliation, consumed-S continuation, and independent-root restoration; provisional geometry alone cannot publish an E or StopAll. Ordinary E/lifecycle reconciliation can change who uses a valid accepted physical Order_A while retaining its valid causes and identity. Confirmed directional primary ownership has the explicit exception in Sections 13.4a–13.4b: revoke or transfer an obsolete same-stop StopAll parent cause and remove the identity only if no independently valid cause remains. A shared Order_B identity retains its independently accepted reset-leg provenance.

The same acceptance rule applies during every OrderAudit rebuild/reconciliation pass: nonaccepted A causes are removed before a physical identity is retained on A provenance. This prevents a provisional A cause from being reintroduced after downstream E reconciliation while preserving independent valid S/E or reset-leg provenance for the same physical Order.

## 9. Order_A — ACTIVE canonical physical parent-stop rule

### 9.1 Creation gate

Order_A is the physical `parent-stop` route opened by an accepted strict behavior stop. Ordinarily a bounded/direct Order candidate must match a canonical opposite-direction (Bullish) Reaction identity `(FirstIndex, BreakIndex)`. **Approved 5.4.30 exception:** after an accepted A stop, independently confirmed complete physical opposite Order geometry may enter S OrderAudit even when it is absent from the public opposite Reaction stream. It receives `reactionNumber=0`, not a synthetic canonical Reaction, and retains its real physical First/Break identity and exact confirmation. An incomplete, unconfirmed, or otherwise invalid geometry cannot enter the accepted audit.

After a stopped A, the first eligible physically confirmed opposite Order is immutable for that A. For S/E parent stops, direct bounded geometry may be evaluated subject to the existing canonical acceptance contract. One exact parent-stop cause may own at most one physical Order_A; when multiple candidates compete, earliest canonical confirmation, then FirstIndex, then BreakIndex owns the cause.

For an A parent, “accepted” means the A survives S ownership and current invalid-A lifecycle filtering into the finalized A behavior set. A provisional/detected A that is S-owned, consumed, filtered or invalid cannot open an A-owned Order_A and cannot be retained as an A `parent-stop` cause in the final OrderAudit. Other independently valid creation causes on the same physical Order identity remain valid.

A shared accepted physical Order stop that changes S Blue to S Red must preserve its opposite `order_direction`, identity, First/Break, confirmation, and exact stop provenance.

### 9.2 Canonical stop

Order stop provenance comes from `MarketChronology.canonical_order_stop`. For Mode A it uses the canonical leg-head/floor context required by that opposite Reaction; for Mode B it uses the previous healthy opposite Reaction's outer edge under the established chronology. The Order's exact strict stop uses the **opposite direction** predicate; for this Bearish calculation that is `Low < OrderStop`. Equality does not stop an Order.

### 9.3 Parent validity and retention

An S explicitly identified in invalid_s_root_identities is calculation evidence, not an accepted S parent, and cannot create or retain a `parent-stop` Order_A cause. An E derived from that S may be accepted only when its chosen physical Order has a valid creating cause independent of the invalid S. This applies to ordinary chain reconciliation, consumed-S continuation, and independent-root restoration; provisional geometry alone cannot publish an E or StopAll. Ordinary E/lifecycle reconciliation can change who uses a valid accepted physical Order_A while retaining its valid causes and identity. Confirmed directional primary ownership has the explicit exception in Sections 13.4a–13.4b: revoke or transfer an obsolete same-stop StopAll parent cause and remove the identity only if no independently valid cause remains. A shared Order_B identity retains its independently accepted reset-leg provenance.

The same acceptance rule applies during every OrderAudit rebuild/reconciliation pass: nonaccepted A causes are removed before a physical identity is retained on A provenance. This prevents a provisional A cause from being reintroduced after downstream E reconciliation while preserving independent valid S/E or reset-leg provenance for the same physical Order.
