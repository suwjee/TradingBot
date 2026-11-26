# CP384 — Independent W3 B05 Order Audit foundations

Pinned production: `c99b4c957e932d9ee70c492ca03ce80711447fc1`; source `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 1–197. Source-only local contracts; no runtime or cross-owner acceptance.

## Independent source findings

### OA-DECL — lines 1–24
Type-only EZone import, postponed annotations, module version and import bindings; no trading state or price decision.

### OA01-A — lines 25–32
Visit causes in supplied order; deepcopy before any edits; fixed parent, post-behavior and anchor label/source pairs. Custom copy protocol remains conditional.

### OA01-B — lines 33–34
String-convert label with empty default; PH/PL prefix is evaluated before source membership. Missing source defaults to None and can match None key. Replace only label with supplied value unchanged; no source or price conversion. Lookup, hash and conversion failures propagate.

### OA01-C — lines 35–38
Full-record native equality dedup after all relabeling; first unequal copied record retained in input order. Distinct original labels may collapse; this equality is not physical Order identity.

### OA-STOP — lines 39–46
Frozen slotted stop fields carry type, source index/time, stop event. Annotations do not validate types or timing.

### OA-ANCHOR — lines 47–55
Frozen slotted separate anchor type, source index/time, priority and number; no constructor validation.

### OA-LEG — lines 56–76
Frozen slotted reset-leg captures separate stop, anchor, reset reaction/time/index/level, boundary/source, strict break, physical reaction and confirmation. Frozen is shallow; object references may remain mutable. Decimal annotations do not coerce.

### OA02-A — lines 77–90
Initial rank per lifetime is priority callback, int(number default 0), source_time, int(source_index). Ascending rank with negative original ordinal makes first equal rank highest; no local timestamp normalization.

### OA02-B — lines 91–98
Invert sorted ordinal rank; activation is truthy trigger event, else truthy decision event, else source time. Sort activation then ordinal. Timestamp comparability and stable inputs are required.

### OA02-C — lines 99–106
Start empty owners and heap; traverse sorted distinct non-null stop events. Admit starts <= event, push negative rank and ordinal; cursor advances once. Equality admits activation.

### OA02-D — lines 107–113
Heap top owner survives if end is None or event <= end; record actual behavior reference and break. Otherwise pop expired top. End equality survives; lower expired entries lazily retained. No owner entry if heap empties.

### OA02-E — lines 114–122
Original lifetime traversal skips null stops; owner must be identical behavior object at exact event, not equal record or lifetime tuple. Repeated aliases can match multiple entries. Read source time/index and clamped main index at stop.

### OA02-F — lines 123–132
Reinvoke priority; compare rank including exact stop event; select strictly greater rank per main index. Equal rank retains first traversal record. Callback stability is a separate condition.

### OA02-G — lines 133–138
Return selected stops sorted by exact event then source index. Stable equal-key sort preserves dictionary insertion order; no physical identity or creator proof here.

### OA03-A — lines 139–145
Truthy second_time delegates to chronology.reset_time; return unchanged including None. Falsy/missing precise time enters fallback; no second search on delegated miss.

### OA03-B — lines 146–150
int reset index; direct main-start read, no bounds guard. Two lower-bound bisects define [start,start+timeframe), duplicates at start admitted and at end excluded. Normalize broken level even if empty.

### OA03-C — lines 151–156
Non-null lower index: exact bullish selects first_less, otherwise first_greater. Pass half-open bounds and normalized level; trust returned index; no scan after indexed null.

### OA03-D — lines 157–166
Only absent index scans ascending positions; exact bullish low < level, otherwise high > level. Normalize each visited price; stop first strict hit, default None. Equality never crosses.

### OA03-E — lines 167–169
None returns None; any non-None position including zero reads exact lower timestamp. Invalid position can raise; no coarse substitute.

### OA04-A — lines 170–172
Unconditional anchor read and as_decimal normalization; source and boundary initialized to first. No bounds check or quantization.

### OA04-B — lines 173–177
Scan first+1..last inclusive. Exact low means strict smaller else strict larger. Update boundary and source together only on strict improvement; first equal representation retained. Empty remainder retains anchor; return triple.

### OA05-A — lines 180–184
Right = lower timestamp array length. Left >= right returns None before index access; no lower clamp or input validation.

### OA05-B — lines 185–187
Non-null lower index uses first_less for exact low else first_greater, passing left/right/boundary unchanged. No fallback after provider null/error.

### OA05-C — lines 188–194
Absent index scans ascending supplied positions; normalize selected field, strict lower for low else greater; first hit breaks. Boundary not normalized here; negative left follows native indexing, not approved chronology.

### OA05-D — lines 195–197
Non-None position including zero returns exact lower timestamp; otherwise None. No interpolation, clamping or coarse fallback.

## Exact review census

- branches: 42
- comparisons: 28
- arithmetic: 9
- calls: 67
- accesses: 447
- effects: 19
- exits: 11

623 category rows = 146 W1 + 477 additional; 8 historical supplements tracked separately. Both CP316 reconciliation parts and exact W1 crosswalk joined by category, current row, node, source span, operation and original W1 ID. All 1,892 B05 W1 links structurally reconciled; only this partition receives independent W3 local review.

## Consumer boundaries

- OA01->OA39: Copy/relabel does not itself mutate ledger; native consumer invokes on previous B causes. Equality dedup distinct from physical identity; wrapper replacement/cache invalidation pending.
- OA02->OA11: Caller filters invalid A by exact source pair; derives A/S/E/StopAll lifetimes, passes same priority callback to sweep and separate anchors. Sweep uses object identity; caller purity, repeated aliases, stop-source chronology and complete acceptance remain independent.
- OA03->OA06: Native reset event enters sorted events only if non-null; precise delegation, lower index freshness, sorted times and alignment remain independent.
- OA04/OA05->OA06/OA09/OA10: Default crossing uses bisect_right(reset_time); live closures use native helpers and cache paths. Scope excludes cache invalidation/dirty frontier and callback equivalence.
- Decimal normalization: as_decimal retains existing Decimal object or constructs Decimal from str(value); no quantization. Equal extrema retain first representation. order_identity/reaction_identity use int First/Break and are not called in OA01–OA05.

## Finding CP384-F01

Clarified shallow immutability, None-key alias case, equality vs physical identity, callback reevaluation, tied Decimal representation and strict lower crossing provider conditions; no runtime defect asserted.

- Local source review only. Frozen records retain mutable references; callback purity, repeated aliases, native chronology alignment, provider return validity and accepted creator/consumer ownership require independent cross-owner proof.
- No RAW payload, runtime, ZIP or production changes. Native exceptions not tested.
- W1/W2 scoped evidence preserved; overlap alone not proof.
