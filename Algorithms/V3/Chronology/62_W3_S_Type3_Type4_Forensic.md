# CP377 — S Type3/Type4

Pinned source: `53460e68538ac790ab969084c1c7101e5ca833d7`; B04-03 403–586. 434 category rows, 80 W1, 354 additional, 8 supplements; 1286 prior rows revalidated without overlap.

### W3 CP377 — order-free Type3/Type4 search and builder (S20–S23)

- **S20 (403–408)**: Type3 helper receives stopped-A event and deadline; no independent new Order search in this helper.
- **S20 (409–412)**: Winner initially None; strict Reset event window (A-stop,deadline) via right then left bounds, traverse stable time-sorted Reset pairs.
- **S20 (413–419)**: Convert owner First, get separate confirmation map; missing or > stop skips. Get owner Reset times default empty tuple; nonempty earliest <= stop skips current even if later.
- **S20 (420–425)**: Resolve S18 nullable whole-main last-equal leg, skip absent; unpack source and boundary. Lower query starts inclusive Reset time and ends exclusive deadline.
- **S20 (426–435)**: Direct lower_index directional strict query without local null-index/empty guard. None skip; first hit timestamp from lower_times. If no trend confirmation in (A-stop,crossing], reject this Reset without recross search.
- **S20 (436–447)**: Map crossing to main position; owner ordinal from mixin First map. Construct source index/time, Decimal boundary, decision main position/time, owner ordinal, Reset event and exact crossing tuple.
- **S20 (448–452)**: Replace winner only when None or candidate crossing strictly earlier; equality retains earlier traversal candidate. Scan all admitted Resets, then return winner or None.
- **S21 (453–463)**: Blue gate begins at candidate source main open (not A-stop or candidate event), uses sorted public-valid formation times and inclusive upper crossing bound. Existence only, no Blue identity/kind association.
- **S22 (464–478)**: Receives A-stop triple and deadline; docstring describes mirrored Type4 and candidate transfer, no new Order lookup here.
- **S22 (479–488)**: Select sorted confirmations strictly after A-stop and before deadline; filter Break index >= A-stop main position. Preserve original sorted tuple tie keys and ordinal; next aligned means filtered sequence.
- **S22 (489–496)**: Traverse aligned rows; reread integer Break; S14 whole main inclusive last-equal candidate from A-stop. S31 candidate event starts max(source open,A-stop), returns first matching lower extreme or fallback; not unconditional exact hit.
- **S22 (497–506)**: Search start max(confirmation,candidate_event,A-stop); end min(deadline,next filtered confirmation or deadline). Skip start>=end, including equal-confirmation earlier empty windows; no merging.
- **S22 (507–516)**: Lower-only strict index query on half-open bounds, no explicit null-index or main fallback. None advances; otherwise first crossing from lower_times.
- **S22 (517–521)**: First hit lacking S21 public Blue skips current aligned row; no retry at later crossing of same candidate. Next aligned row rebuilds from common A-stop origin.
- **S22 (522–533)**: First qualifying aligned candidate returns source index/time/level, mapped decision position/main timestamp, original Reaction ordinal and crossing event; exhaustion None. No scan-all winner comparison as Type3.
- **S23 (534–547)**: Unpack caller A-stop and Type4 tuple; trend ordinal intentionally unused, no extra geometry calculation.
- **S23 (548–558)**: Construct frozen slotted SZone, direction, blue/type4, caller A ordinal and price, native int parent source index and direct source/stop provenance.
- **S23 (559–577)**: All Order fields and Reset ordinal/time explicitly None; no physical Order creation or accepted ledger mutation in builder.
- **S23 (578–586)**: Retain Type4 source/price and separate decision main/index/event unchanged; record construction not lifecycle acceptance.

Direct index calls in S20/S22 have no local null-index guard or main fallback. This is a caller/provider proof obligation, not a demonstrated runtime defect. S40 resolver arbitration and accepted lifecycle remain independent.
