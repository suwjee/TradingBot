# CP412 — W3 B06-03: E live zone cache

Pinned main: `c99b4c957e932d9ee70c492ca03ce80711447fc1`; source: `240369edf3352006082efe094eb68ac027d6689f`, lines 196–219. Entry algorithm: `5c61b4e23bb4ee00e0a54c05a148c697a4def44e`, tree `ed8400981471256644668e48896fdbd0b7cfe744`. Scoped source-only local forensic review.

## E06 exact contract

- **E06-A** (lines 196–200): Inputs detector, family, number, parent type and object, exact parent stop event, nine-item OrderMatch and source triple; return annotation EZone. Postponed annotations do not validate or coerce.
- **E06-B** (lines 201–201): Invoke E03 first; chronology identity (not equality) and non-null dirty required. Dirty retained unchanged. Failure precedes unpack and map access; this gate alone proves neither valid dirty evidence nor native race selection.
- **E06-C** (lines 202–203): Unpack exactly nine items in order: order_number, order, confirmation, level, stop_index, stop_time, crossed, causes, cause_time. Non-iterable or wrong arity raises; no starred fallback. Assert crossed is not None, not truthiness or tuple length; AssertionError in normal assertion mode, omitted under optimization. No alternate selection. Malformed crossing can still fail later; a current hit may bypass crossed[2].
- **E06-D** (lines 204–211): Construct one ordered 26-element tuple left to right: detector.direction; family; number; parent_type; parent.source_index; parent.source_time; str(parent.price); stop_event; order_number; order.first_idx; order.break_idx; order.mode; order.box_top_source_idx; str(order.box_top); order.box_bottom_source_idx; str(order.box_bottom); confirmation; str(level); stop_index; stop_time; crossed; causes; cause_time; source[0]; source[1]; str(source[2]). Retain nested crossing and causes as supplied, not flattened, sorted or normalized. Five explicit strings are representation-sensitive. Decimal 1.0 versus 1.00 compares numerically equal and hashes equally in E04, but their strings differ in E06; signed zero and exponent representations can also differ. No rounding, quantization or normalization. Ordinary dictionary hashing and tuple equality apply elementwise with Python identity/equality behavior; collisions alone are not equality; elements must be hashable. No separate Order object identity, parent object identity, Order direction, First/Break or box-source timestamps, chronology identity/time array, range or feedback scope in key. Their relevant consistency is conditional on native caller/market ownership. Native Order direction derives from detector chronology; builder derives times from positions. Key retains uncoerced indices and mode; builder conversion is separate.
- **E06-E** (lines 212–212): Current dictionary get by complete tuple, None sentinel. Non-null result including a falsey object is a hit; no type check, builder or cutoff evaluation on this route. Attribute, string, subscript, hashing and equality failures propagate.
- **E06-F** (lines 213–214): Only current None evaluates max(stop_event,crossed[2],confirmation) strictly less than dirty. All three comparable event instants must be earlier; equality of maximum excludes previous lookup. No lower or range-end guard; no race recomputation. Max arguments evaluated in order; crossing indexed only on current miss. If strict guard true consult previous dictionary by same tuple. Non-null previous is reused as identical object, no copy, replace or field check. Previous map not mutated.
- **E06-G** (lines 215–216): Remaining None calls detector._build_zone once with seven positional arguments family, number, parent_type, parent, stop_event, original match, original source. No reconstruction from key. Native E32 unpacks again, asserts crossing, computes decision_event=max(stop_event,crossed[2]) (confirmation not in this max), maps decision and parent stop to main positions, uses detector order_direction and indexed times; normalizes parent and box prices via as_decimal, int-converts selected indices, str-converts mode, retains provided source price, Order stop level, cause tuple and exact event times. Constructs frozen slotted EZone with 35 declared fields. E06 does not validate return type or value, including None from custom builder. Dynamic calls and failures propagate.
- **E06-H** (lines 217–219): Unconditional current-map assignment after current hit, previous hit or successful build, then return exactly the selected reference. No mutation of previous map or zone fields, no copying. Ordinary dict insertion adds encounter order, overwrite does not move an existing equal key. Failed gate, unpack, key construction, lookup, cutoff or builder prevents final explicit write; assignment can itself fail. No try, rollback, cleanup or compensation for prior dynamic side effects or upstream ledger changes. No promise of behavior on malformed custom objects; annotations are not enforcement.

## Provider and consumer boundaries

- **engine/pipeline/e_zone_detector.py** (`240369edf3352006082efe094eb68ac027d6689f`, 103–151, 196–218, 335–390, 608–675, 677–733): Native _zone obtains inherited, gate-owned, carried and post-stop accepted routes, registers audit, requests direct candidates, sorts crossed direct/inherited/carried streams by exact crossing and negative First index, merges with post-stop groups sorted by same key, computes prospective source, skips disowned-S-only Orders and takes first surviving match. No match returns None; only non-null continuation delegates E06; otherwise direct E32. E06 alone never performs this race. Equal key consistency requires current selected ledger/geometry, exact identity and aligned chronology. E02 rotates maps only on same first-main/timeframe scope; E03 checks chronology identity.
- **engine/pipeline/order_audit_engine.py** (`6ddb93ba097ef137af2405ef15356b6f6bcf97de`, 523–527, 925–951): OrderMatch alias has exactly nine items; crossing is nullable (int,datetime,datetime), causes tuple[str,...], nullable parent stop cause time. Native parent-stop registration constructs the same positional record and compares physical geometry; E06 does not create Order or adjudicate ledger ownership.
- **engine/pipeline/core_utils.py** (`38a1053510c5fb114e1b4290de00a2d3b27fc373`, 51–53): as_decimal preserves existing Decimal object; otherwise Decimal(str(value)). E32 uses this for parent and box prices, not E06 cache key normalization.
- **engine/bridge/trading_pipeline.py** (`e1e65ba960c5f726f9a05e2ab89e4457b65e5735`, 2280–2306, 2648–2656, 3738–3767): live_e is optional from live.e_continuation; create_e_detector receives it. Native calculate_live_from_buckets calls _run_live_calculation, which calls prepare_pipeline_state without live, default None. This observed route is not proof of active E cache; other conditional caller routes remain separate.
- **engine/bridge/live_pipeline.py** (`e1f1e7d3414a75ed073b67ff2ded3a5a481f6182`, 22–65): Native live transport calls calculate_live_from_buckets with market views and bucket delta; no E continuation argument. No empirical equivalence or global dispatch claim.

## Inventory

| Category | CP412 | B06 total |
|---|---:|---:|
| branches | 4 | 334 |
| comparisons | 4 | 218 |
| arithmetic | 0 | 104 |
| calls | 10 | 453 |
| accesses | 108 | 3765 |
| effects | 4 | 270 |
| exits | 1 | 113 |
| Total | 131 | 5257 |

18 W1 and 113 additional; two supplements. Prior 563 rows and six supplements structurally revalidated; all 1109 CP317 links and 18 filter IDs resolved. Cumulative 694; remaining 4563. B05 exact 8318 union retained. CP411 publication: untruncated recursive trees 1370→1375, seven allowed changed leaf files, six evidence references and completion matching, no removed leaf. W3 INCOMPLETE, W4 NOT RUN, Phase08 BLOCKED.

## Limitations

- Separate source-first local forensic review by GPT, not independently staffed. Existing AST inventories directly compared, not regenerated.
- Local source-only scope; no RAW payload, runtime, ZIP, production or main change, new cross-owner acceptance or empirical cache equivalence.
- Prior 563 row identities, operations, spans, historical W1 dispositions/interpretations and six supplemental identities checked against pinned artifacts; semantic contracts re-read by groups, not re-executed. All 1109 CP317 links checked against canonical inventory, W1 crosswalk and partitions; historical 25-partition reconciliation retained from predecessor, not all historical partitions fetched anew.
- Ordinary native object, hashable tuple members, finite Decimal representation, comparable times, stable omitted-field consistency and valid dirty evidence remain conditional. No assertion malformed input is reachable.
- Publication readback is Git identity and exact content comparison, not independent SHA-256 or signature verification.
