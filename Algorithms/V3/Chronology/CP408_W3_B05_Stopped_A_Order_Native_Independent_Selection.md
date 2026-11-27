# CP408 — W3 B05-25: Stopped-A native and independent Order selection

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`; source `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 2517–2621, OA75–OA77. Entry algorithm `702c42922d6bf3b5a0761f489a89e24defb4c0f4`, tree `64a84d84a5b03d56da21bf20376fade4242b298e`. Source-only local review.

## Independent procedure contracts

### OA75-A — lines 2517–2521

Class declaration and method definition establish S mixin ownership; docstring and annotations do not perform runtime validation or guarantee geometry immutability.

### OA75-B — lines 2522–2525

Evaluate dictionary comprehension before assigning attribute. Enumerate opposite_reactions from one, unpack each ordinal/item; normalize required first_idx through int before storing (ordinal, original item). Duplicate normalized First keys overwrite with last input entry, not earliest confirmed or full physical identity. No copy of item or Break check. Missing or nonconvertible First propagates before publication of this new dictionary.

### OA75-C — lines 2526–2538

Second independent enumeration from one builds native tuples. Evaluate chronology confirmation with original item and order_direction before required int First then int Break, then ordinal and original object. sorted consumes generated tuples and sorts lexicographically by confirmation, First, Break, ordinal, object. Distinct ordinal resolves equal prior keys under ordinary comparable values; no price or stop crossing check. Original order remains ordinal authority; no deduplication. Reiteration assumes stable iterable; S owner supplies a list. Failure after map assignment leaves earlier assignments; no local rollback.

### OA75-D — lines 2539–2541

Project position zero of each sorted tuple into a new list, in exact sorted order, then assign. Positional alignment with the sorted tuple list is required for subsequent upper-bound search; mutable list and object references are not frozen or copied.

### OA75-E — lines 2542–2545

Assign a new empty dict to exact-stop native-choice cache after previous attributes have been assigned. Annotation describes datetime to tuple-or-None, not validation. Reinitialization replaces the cache rather than retaining entries. No epoch, bound, invalidation listener or transactional update is implemented here.

### OA76-A — lines 2546–2560

Eagerly call OA77 with exact supplied A stop before inspecting callback; return native unchanged only if initial_order_geometry is exactly None. A falsey callable is still called; a falsey noncallable may raise. Native cache can be populated even if later independent evaluation fails. No combined-result cache.

### OA76-B — lines 2562–2565

Map stop through owner main-index accessor again (even after native lookup on a miss), then invoke current callback with positional gate_index, exact a_stop_event_time, end_index in that order. No local clamping or adjustment. Callback owns search and can have side effects; error propagates.

### OA76-C — lines 2566–2567

If physical is None, short circuit without Break access. Otherwise getattr with default None; missing or null Break returns native. Falsey non-None object and Break zero are not rejected by this guard. Attribute access errors other than default-handled absence propagate.

### OA76-D — lines 2568–2570

Read required physical First and convert to int. Reject only normalized First strictly less than gate; equality passes. No local upper-bound First validation, no additional Break ordering or sign validation. Return exactly previously selected native on rejection.

### OA76-E — lines 2571–2575

Compute independent confirmation through current chronology callback with physical and order_direction. Reject confirmation <= exact stop, including equal; only a strictly later comparable confirmation passes initial gate. No local crossing proof and no substitution for malformed callback result. Return native on rejection.

### OA76-F — lines 2577–2579

Compute physical pair via reaction_identity (int First,int Break), then dictionary get by earlier normalized First. Only a non-None mapped pair triggers evaluation of mapped[1] and its full normalized identity equality. Last duplicate First controls mapping; no search through all duplicates, no match by source time alone. Repeated reads can diverge under mutable/custom objects.

### OA76-G — lines 2580–2583

On exact mapped pair equality unpack its one-based native number and original mapped object, replacing independent geometry reference. Recompute confirmation through current chronology; no repeated initial First/confirmation guard after remap, no repeated identity check. Earlier first_index local still used later in ranking. Object alias is preserved; callback can return different chronology for same pair.

### OA76-H — lines 2584–2587

Otherwise assign number zero, preserve independent object and its prior confirmation. This marks Order-only geometry, not an invented public Reaction. Construct tuple (number,physical,confirmation) retaining object reference; no additional normalization.

### OA76-I — lines 2588–2589

If native is exactly None return independent tuple immediately. No tie comparison or post-remap confirmation guard on this path.

### OA76-J — lines 2590–2598

Evaluate left rank (original normalized First,current confirmation), then right rank (int required native object First,native confirmation). Native First is reread from object, not stored indexed First. Strict lexicographic less chooses independent; equal or greater returns original native tuple, independent number/Break not tie keys. Tuple ordering may short-circuit confirmation comparison when First differs. Malformed comparable values or access can raise; no rollback of prior native cache or callback effects.

### OA77-A — lines 2601–2607

Bind current cache; exact key membership precedes any mapping or bisect. Hit returns stored value unchanged, including None and original tuple/object alias; key equality/hash native datetime semantics, not rounded main index. No local expiration or refresh. Unhashable/malformed key may raise.

### OA77-B — lines 2609–2612

On miss map exact stop using owner accessor, then bisect_right on aligned confirmation array; strict after-stop boundary excludes equal confirmation when sorted comparable timestamps. No lower-timeframe scan by mixin. Invalid index mapping, unsorted or incomparable input is not locally repaired.

### OA77-C — lines 2613–2616

Initialize match None; iterate increasing positions from bisect result to len(sorted tuple list) exclusive. Read and unpack confirmation, normalized stored First, discarded Break, ordinal, original object; require First >= gate inclusive. No end bound check, no extra stop crossing gate and no earliest-First resort; primary order is precomputed confirmation tuple order.

### OA77-D — lines 2617–2618

Construct first qualifying tuple (number,reaction,confirmation), then break immediately. Later qualifying rows are not examined. Return uses stored native confirmation and original object, not a fresh confirmation call.

### OA77-E — lines 2619–2621

Store match under exact stop, including None on exhaustion, then return it. No explicit catch, invalidation, bounds, copying or rollback. Cache-hit and newly stored tuples alias underlying native objects; owner immutable-run premise is a precondition, not established by local code.

## Provider and consumer boundary

- **engine/pipeline/s_zone_detector.py** (`53460e68538ac790ab969084c1c7101e5ca833d7`, lines 78–119, 178–189, 1251–1299): S validates direction and range; derives opposite direction through chronology, copies opposite sequence into mutable list of original elements, stores optional callback, shares chronology and calls OA75 after range initialization. Main-index wrapper passes no clamp; confirmation wrapper passes direction/reaction using provider default intrabar start. _detect clears ownership and audit, audits each A, then calls OA76 before next-A confirmation exclusion; passes result to candidate resolver. No OA77 reset is shown in _detect; repeated invocations on the same instance retain native cache unless reinitialized. Local delegation and observed callsites only; do not infer global input immutability or candidate acceptance.
- **engine/pipeline/core_utils.py** (`38a1053510c5fb114e1b4290de00a2d3b27fc373`, lines 64–66): reaction_identity reads First then Break, int-normalizes both; no direction, time, price or ordinal component. Physical normalized pair equality is not full object or chronology equivalence.
- **engine/pipeline/reaction_engine.py** (`9adffb832ffa231ba0cb01de507a30fbe62be0b0`, lines 1132–1150, 1185–1192, 1257–1302, 1554–1614, 2068–2093): Main mapping bisect_right(times,timestamp)-1, pre-first raises unless clamp, default False. Confirmation cache uses provider key and exact intrabar start default; normalizes direction-dependent level and scans strict lower crossing in break candle, falls back to break candle start if absent. Standalone bounded callback accepts gate/stop/end but local cache keys gate/end, uses bounded directional search. Continuous provider limits end and guards gate, keys by direction/gate/limit/event; copies cached candidate on hit. OA76 does not verify provider geometry, remapped chronology or cache consistency; local source-level provider boundaries only. No equivalence between callback paths asserted.
- **engine/bridge/trading_pipeline.py** (`e1e65ba960c5f726f9a05e2ab89e4457b65e5735`, lines 2256–2271, 2712–2727, 2757–2763, 2900–2922): S receives opposite native reactions and direction-specific initial_order_geometry. Reusable context binds opposite direction in lambda; forwards gate_index,end_index,gate_event to geometry detector; when live non-None invokes live.order_geometry(detector,order_direction,gate_index,end_index,gate_event). Standalone path uses directional_a_stop_order_finder. S result consumption can reuse full state or construct S for non-reusable path. Dynamic live receiver implementation not inferred; forwarding order verified, no new W2/W3 cross-owner acceptance.
- **engine/pipeline/order_audit_engine.py** (`6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 2517–2621): OA75–OA77 own initial native index, native-only exact-stop cache and independent-vs-native selection; callback may return nested geometry without inventing public Reaction number. No stop calculation, ledger registration, acceptance or crossing performed in these methods. Later OA78+ and Lifecycle/Bridge consumers remain outside this checkpoint.

## Exact inventory and prior evidence

| Category | Rows |
|---|---:|
| branches | 15 |
| comparisons | 11 |
| arithmetic | 3 |
| calls | 27 |
| accesses | 183 |
| effects | 12 |
| exits | 10 |
| Total | 261 |

56 historical W1 and 205 additional rows; 7 historical supplements. All 24 earlier registers (7790 rows: 1785 W1, 6005 additional; 145 supplements) revalidated against canonical and historical evidence, no identity/span/operation or membership discrepancy, missing/extra, or overlap. 1892 CP316 canonical/crosswalk links checked; 27 AST filter IDs resolve across full inventory, zero in this range. Current canonical union 8051/8318; remaining 267. Full canonical and historical category and AST-node arrays identical. No new runtime or cross-owner acceptance.

## Limitations

- Separate source-first local review by GPT, not independently staffed. No runtime, RAW, ZIP, new cross-owner acceptance or production change.
- The native lookup depends on stable comparable timestamps, stable normalized indices, tuple/list alignment and stable owner state; mutability, aliasing and custom attribute/call semantics are not ruled out. No assertion that malformed input occurs.
- OA76 remapped confirmation is not re-gated; the native winner ranks by confirmation first, the combined selection ranks by First first. No runtime equivalence or defect assertion.
- Live Bridge invocation is a dynamic provider boundary; the presence or implementation of an arbitrary live object is not established by the callsite alone. No new cross-owner acceptance.
- Existing canonical AST inventories compared directly, not freshly generated; no independent SHA-256 assertion.
