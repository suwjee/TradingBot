# CP385 — Independent W3 B05 Order_B reset-leg discovery

Pinned production: `c99b4c957e932d9ee70c492ca03ce80711447fc1`; source `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 198–377. Local contract only.

### OA06-DECL — lines 198–226
Signature and docstring describe expected HH/LL geometry. Actual executable gates below govern; default anchors empty, callbacks optional. Type annotations are not runtime validation.

### OA06-A — lines 227–230
Reject direction outside exact bullish/bearish before any empty-input shortcut; ValueError is native. Falsey post_stops skips evaluation of behavior_anchors and returns empty; falsey anchors likewise return empty.

### OA06-B — lines 232–238
Capture lower times, obtain opposite direction from chronology, choose low for bullish else high. Truthy boundary/crossing callbacks selected, otherwise native closures; default crossing uses bisect_right excluding all lower timestamps equal to Reset. Custom callback outputs not independently proved.

### OA06-C — lines 240–252
Resolve each trend confirmation with direction, int First/Break, zero-based original ordinal, original object reference. Tuple ascending sort prioritizes confirmation then First/Break then ordinal; unique ordinal avoids comparing reaction objects. Group by First preserving sorted order and duplicate identities.

### OA06-D — lines 254–263
Resolve opposite confirmation using provider opposite direction. Tuple order confirmation, int First, int Break, one-based original input number, object reference. Number is not sorted rank; repeated physical geometry not deduplicated.

### OA06-E — lines 264–272
Resolve each reset exact event through OA03 before constructing tuple. Only non-None events retained, sorted by event, int from_first_idx, zero-based ordinal. Duplicate events retained; null skip prevents further reset-field reads for that row.

### OA06-F — lines 273–280
Stable-sort stops by event, behavior source time/index/type; extract parallel event array. Exact equal-key records remain input-ordered. Later bisect selects last eligible sorted record, not first.

### OA06-G — lines 281–290
Independent anchors sorted by source time/index, priority, number, type; extract source-time array. A formation times separately sorted, no dedup or additional lifecycle filtering here.

### OA06-H — lines 291–300
For each sorted Reset, filter same-First group by exact confirmation < Reset (equality excluded); if empty skip. Select last sorted qualifying tuple, hence greatest confirmation, then Break/ordinal for same First. Read selected First main time directly; no alternative retry.

### OA06-I — lines 302–306
Stop eligibility uses bisect_left(First main time)-1; event strictly earlier, equality excluded. Negative position skips. Selected stop is latest, last among equal-time sorted ties.

### OA06-J — lines 307–313
Anchor eligibility independently uses strict earlier source time; negative position skips. Select latest sorted anchor then reject if its source index > current First. Equality of index is allowed at this gate. No fallback to earlier anchor if rejected.

### OA06-K — lines 314–324
Call selected boundary provider with anchor index and current First; unpack triple unchanged. Strict lower extension for bullish, strict higher for bearish; equality fails. Boundary source must be strictly before current First. No local lower bound or requirement source >= anchor, no Decimal coercion for callback triple.

### OA06-L — lines 326–339
Invoke crossing_after with exact Reset and boundary. None skips; any non-None time mapped through chronology.main_index(clamp=True). Native default is strictly after Reset; custom return not rechecked against Reset or lower prices. Main-candle gate and precise event provenance remain distinct.

### OA06-M — lines 340–346
bisect_right on A formation times selects first A strictly after current First main time, not Reset or break. If present and clamped owning main <= break main, skip before opposite selection. Same-main expiry is intentional. No A-expiry test against later opposite confirmation here.

### OA06-N — lines 348–354
From confirmation-first sorted opposite tuples choose first with First index >= break main and exact confirmation > strict break. Equality of First main eligible, equality of confirmation not. No new geometry constructed, no eligibility check on opposite intrabar First timestamp.

### OA06-O — lines 356–375
Append one frozen reset leg for every successful sorted Reset. Store selected stop/anchor, same-direction Reaction reference and confirmation, int Reset index, normalized broken_level, exact Reset, untouched boundary and source index, direct source main time, exact strict break, original opposite input number/object/confirmation. No signature or physical dedup. Return list in Reset traversal order.

## Census

- branches: 31
- comparisons: 17
- arithmetic: 7
- calls: 45
- accesses: 301
- effects: 11
- exits: 12

424 category rows = 100 W1 + 324 additional; 6 historical supplements. All 623 prior CP384 rows revalidated without overlap. B05 cumulative 1,047 category rows, 246 W1, 801 additional, 14 supplements.

## Consumer boundaries

- OA03->OA06: Exact Reset resolver output controls event admission; null skipped. Native provider index alignment and delegated precise-time return remain conditional.
- OA04/OA05->OA06: Default geometry and strict crossing use native helpers; supplied callback can return unvalidated times, indices or prices. Only explicit extension/source-before-First/non-null gates applied.
- OA11->OA06: Accepted lifetime filtering, stop ownership and independent anchors constructed by caller; OA06 consumes them without revalidating acceptance. A triggers supplied separately.
- OA06->OA07–OA10: Live closures delegate boundary/crossing; dirty frontier and cache validity not accepted in this checkpoint.
- OA06->OA12: Leg identity feedback is separate; OA06 preserves repeated legs and physical object references. Ledger creation, dedup and serialization pending.

## CP385-F01

Clarified native vs injected crossing, conditional callback geometry, duplicate preservation, exact Reset and same-main A/physical First eligibility; no runtime defect asserted.

- OA06 is a local discovery contract, not accepted ledger or creator proof. Caller acceptance of A/S/E/StopAll, mutable aliases, chronology provider, injected callbacks and live cache freshness remain independent.
- No RAW payload, runtime, ZIP or production changes. Native exceptions not tested.
- Overlap and prior W2 semantic rows are not independent W3 acceptance.
