# CP404 — Independent local accepted Order audit rebuild

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, OA62–OA63 lines 2046–2233. B05-21. Source-only; no algorithm execution.

## OA62-A — lines 2046–2052

Inputs numbered E list and optional supplemental S sequence default empty tuple. Replace accepted E source identity set with (raw source_time, int(source_index)) for every numbered item, deduplicating equal pairs. Evaluate complete set before assignment; conversion/hash failures prevent replacement. No sorting or acceptance validation here, and empty numbered publishes empty set.

## OA62-B — lines 2053–2059

Construct invalid S source times by projecting time from each pair of getattr invalid_s_root_identities (default newly constructed empty set), then union with time projection of the newly published accepted E set. Pair unpacking required; no int conversion or source-index comparison in this filter. A same-time different-index S may be excluded by OA63 although OA40 registration uses full identity pairs. No local catch; accepted E set may already have changed if projection fails.

## OA63-A — lines 2060–2073

Local predicate closes over invalid time set. Reject falsey cause first, then cause slot 0 unequal to literal parent-stop. For remaining causes, reject only if slot 1 equals S, length >4 and slot 4 belongs to invalid time set, in that exact short-circuit order. Non-S labels pass without length or source access. A matching-kind one-slot tuple raises at slot 1; matching-kind S tuple of length 2–4 passes. Empty cause is rejected, not indexed. No tuple/type validation, source-index/family/time normalization or acceptance proof. Unhashable source or malformed attributes can raise; no catch. Negation returns True for nonexcluded parent-stop causes; this filter is distinct from OA60's universal disowned-S predicate and from OA40's pair gate.

## OA62-C — lines 2074–2084

Before clearing, iterate every current ledger item in mapping order, build new mapping per identity using shallow entry expansion and fresh set of causes passing OA63; get causes defaults to empty set only if missing, explicit None is not replaced. Set deduplicates hash-equal causes; all non-cause fields and nested references (reaction, B-cause list/dicts) are shared. Preserve even rows whose filtered cause set is empty in this temporary snapshot. Failure during snapshot leaves ledger uncleared, but accepted E set already published. Then dynamically invoke clear: actual OA27 clears ledger and confirmation index in place and invalidates carried result/creation/append, post-stop list/sorted/pending states; not all detector geometry/crossing caches.

## OA62-D — lines 2085–2095

Register self.order_b_legs before parent processing; reset-leg provenance can prepopulate identity and geometry. Build entire parent list eagerly: all existing self.s_zones in their current order labelled S, then numbered items in supplied order labelled StopAll if source_time in sequence_resets else E. Supplemental S does not participate. For each, invoke dynamic _parent_stop(label,parent); only exact None skips; otherwise pass slot 1 of stop as exact event to OA40, not main index slot 0. No local sorting or chronology check. _parent_stop ignores label and resolves from decision_event_time with Decimal-normalized price; OA40 separately checks invalid/occupied full S pair and reset boundary and sets route flags by label. S still labelled S even at reset source until OA40 label override; StopAll-labelled E uses neither S nor E flags. Failure after clear can leave partial B/parent registrations; no rollback.

## OA62-E — lines 2096–2106

For each numbered zone in original order normalize First and Break via order_identity (int First then int Break); if normalized identity already in rebuilt ledger skip entire recovery, including initial/explicit/prior cause gathering and crossing. First successfully inserted row controls geometry; prior retention pass may later merge parent causes, not overwrite it. On absent key read prior snapshot row and look up opposite reaction by raw zone.order_first_index, not normalized key. Lookup uses existing last-wins by-int-First map, not full physical identity position map.

## OA62-F — lines 2107–2123

If reaction is None, or int(getattr(reaction, break_idx, -1)) differs from raw zone.order_break_index, construct SimpleNamespace with raw recorded mode, First, Break, box top/bottom and both source indices/times, behavior_internal=False. Short circuit avoids Break access when reaction missing. Existing matching reaction reused without extra geometry validation; no First recheck, mode/box/confirmation equivalence or recomputation here. Default -1 applies only when missing attribute; conversion failure propagates rather than falling back. Fallback does not synthesize missing box fields or normalize prices.

## OA62-G — lines 2124–2130

Start empty parent cause set. If prior entry not None, union its causes selected by truthiness then slot0 equality parent-stop, again from get default empty set. These are already OA63-filtered on snapshot, but explicit truth/kind gate is repeated here. No B causes imported at this recovery step. Nonempty malformed one-slot parent-stop might fail earlier snapshot; no independent catch.

## OA62-H — lines 2131–2143

Initial audit lookup uses normalized pair; only None skips. Read a_causes with no default; choose it if truthy, otherwise eagerly form one pair from a_source_time and a_stop_event_time via get. A truthy empty iterator does not use fallback; each selected item must unpack exactly two values. Skip when source None OR stop None, in that order. Add parent-stop A cause with family None, event equal A stop and source equal A source. No source/stop chronology or type check, no verification of initial reaction geometry, and no use of initial B fields. Set union deduplicates exact equal cause tuples.

## OA62-I — lines 2144–2164

Carried-S fallback runs only if accumulated causes falsey, then carried-live label membership, then zone parent_type equals S. No recheck after later OA63 filtering; a nonempty but later-rejected set suppresses fallback. Eagerly expand all self.s_zones then supplemental_s_zones into temporary list, then take first match via next(default None), evaluating int required source index vs raw zone parent index, required source time vs raw parent time, optional Order First then Break vs raw zone pair, in that order. No normalization of Order pair or raw target index. Original S precedes supplemental; no sorting, eligibility or invalid-root check here. If parent found, add parent-stop A cause using required a_stop_event_time then a_source_time; unlike initial branch no None guard. Empty source match or no parent leaves set unchanged; required attribute/iteration/hash errors propagate.

## OA62-J — lines 2165–2184

Only non-None order_parent_stop_cause_time enables explicit cause; its value is not the stored event and need not equal actual parent stop. Start with raw zone.parent_type label; if E, find first numbered item in supplied order matching raw parent source index then time, default None; if found format E plus number (no int coercion). Next override label to StopAll plus reset value for any parent type if source time in sequence_resets. Add parent-stop tuple: selected label, empty family if source time in resets (membership evaluated again) else raw zone.family, zone.parent_stop_event_time, zone.parent_source_time. No use-label membership requirement here, no new parent stop query or source/index validation. E lookup happens before reset override, so its errors not suppressed by reset membership.

## OA62-K — lines 2185–2188

Rebuild causes set by OA63 over all accumulated causes, including prior, initial, carried fallback and explicit. Set iteration order unspecified for native sets; malformed cause may raise if reached. Skip recovery if resulting set empty; no fallback retry, no B-only recovery through this path and no crossing calculation for skipped zone.

## OA62-L — lines 2189–2204

Invoke dynamic cross helper with zone.order_confirmation_time and as_decimal(zone.order_stop_level) evaluated left-to-right. Decimal instance retained else Decimal(str(value)); no forced precision or rounding. Cache/dynamic live crossing behavior delegated. None crossing permitted; no requirement that crossing follows confirmation or source. Construct row from zone number, selected reaction, raw confirmation, original (not normalized result) stop level, raw stop source index/time, returned crossing and filtered cause set. Publish row first then call confirmation-index insertion with same identity and a freshly read raw confirmation; no local rollback on insertion error. Existing B fields not recovered here; ordinary new row only listed fields. No direct cause-only cache invalidation.

## OA62-M — lines 2206–2216

Retention visits all prior snapshot identities in insertion order, including ones not consumed by numbered zones. Re-filter prior parent causes via OA63 (same captured time set). If empty skip regardless of prior B causes; this is parent-cause retention, not general historical B-only retention. If nonempty, lookup current row by prior identity without normalization. Earlier rebuilt rows retain precedence for geometry.

## OA62-N — lines 2217–2221

When current row not None, use setdefault causes with eagerly allocated empty set, assert isinstance set (subclasses accepted under enabled asserts), update in place with prior parent causes then continue. No B-cause union, geometry replacement, crossing recomputation, reindex or explicit carried-cache invalidation on this path. Existing nested set reference retained. A present non-set causes value may raise (assert or update depending on execution settings); no rollback.

## OA62-O — lines 2222–2227

When current row None, make shallow restored mapping from prior entry with fresh set(prior_causes); preserve all other fields including original reaction, stop geometry, crossing and any B collection references. Publish using original prior identity then index using restored required confirmation_time. No normalization, crossing recompute, fresh physical validation or B-field copy. If confirmation access/indexing fails, row may already be visible. Prior B-only row without valid parent cause was skipped above.

## OA62-P — lines 2228–2233

Return newly sorted list of numbered zones by raw (source_time,source_index), stable for equal keys, not a ledger list or list of restored Orders. No final cache invalidation or other postprocessing. Sort key/comparison errors can occur after all ledger mutations; no transaction. The function can change ledger and caches without changing numbered membership or original list order. Source-wide exception behavior remains conditional on dynamic delegates and native comparability.

## Decision boundaries (source-derived, not runtime tests)

| Condition under ordinary native input contracts | Effect |
|---|---|
| Prior cause falsey or non-parent-stop | OA63 rejects |
| Parent-stop S with length greater than four and invalid source time | OA63 rejects, regardless of source index |
| Parent-stop S length two through four | OA63 accepts; no source access |
| Parent-stop with one slot | OA63 label access raises |
| Current physical identity already present | Skip numbered recovery; later prior parent causes may merge |
| Initial A pair contains None | Skip pair |
| Carried S fallback matching parent A attributes contain None | Add without local null check |
| Explicit cause-time non-None | Actual event from zone parent stop, label from E parent or reset override |
| All recovered parent causes rejected | Skip crossing and insertion |
| Prior valid parent causes empty, prior B truthy | OA62 retention skips |
| Current row exists, prior valid parent causes nonempty | Merge parent set only; current geometry and B fields retained |
| Current row absent, prior valid parent causes nonempty | Restore shallow row with copied parent set, original crossing and B references; index |

## Consumer boundaries

- engine/pipeline/core_utils.py [[51,66]] (blob 38a1053510c5fb114e1b4290de00a2d3b27fc373): Decimal normalization retains Decimal instances else Decimal(str(value)); physical identity normalizes First then Break by int. OA62 uses normalized pair for current/prior/initial ledger access, but raw First for opposite lookup and raw pair comparisons in fallback; malformed data and conversion failure not handled locally.
- engine/pipeline/order_audit_engine.py [[640,651],[1089,1132],[1135,1198],[1339,1433],[1459,1477],[2020,2043]] (blob 6ddb93ba097ef137af2405ef15356b6f6bcf97de): Opposite First map is last-wins by int First while separate pair position map is first-wins. OA27 clears audit/index and carried/post-stop state, not crossing/initial geometry caches. OA28 B registration may insert row/index and append/sort B causes. OA40 skips invalid/occupied S full identity pair, reset in (parent source, stop], delegates routes by label; registers only parent-stop use matches, creates normalized identity, adds physical parent cause with StopAll override, invalidates carried on new/earlier creation and may stage append. OA43 caches start/level including None, strict lower crossing in [max(start,range_start),range_end), direction-sensitive. OA60/61 are exclusion predicates, not OA63 pruning. OA62 has no final cause-union cache invalidation; coherent cache lifecycle remains owner-dependent.
- engine/pipeline/e_zone_detector.py [[337,356],[385,389],[507,535],[537,557],[569,578],[1495,1506]] (blob 240369edf3352006082efe094eb68ac027d6689f): Detector snapshots invalid root set, sorts S by source_time,int index, retains truthy initial ledger, tuples B legs. Parent stop ignores passed label, uses decision_event_time and normalized price, searches strict crossing from max(start,range_start) to exclusive end, returns mapped index/exact event or None; live continuation path can delegate. Cross helper override delegates to base or live first_stop and populates same local cache, so no assertion of universal base dispatch. detect clears previous accepted sources/audit, registers B, discovers/reconciles/consumed-S/same-source conflicts, then returns OA62's sorted result. E ownership and acceptance remain outside local review.
- engine/bridge/trading_pipeline.py [[2535,2557],[2606,2627]] (blob e1e65ba960c5f726f9a05e2ab89e4457b65e5735): External continuation replacement invokes public rebuild with final E zones and consumed S as supplemental evidence before filtering invalid S public list. Later StopAll feedback reconciles, restores independent S roots and calls ensure before discovering accepted Order B reset legs. Adjacent OA64/OA65 wrappers (2234–2290) forward shallow list and have distinct restoration/invalidations; not included in CP404 closure. No final pipeline equivalence or cross-owner acceptance.

## Verification

533 category rows: 141 W1, 392 additional; 8 historical supplements. Branches 50, comparisons 29, arithmetic 8, calls 54, accesses 354, effects 29, exits 9. All 6446 prior rows (1485 W1, 4961 additional), 122 supplements and 1892 CP316 links reconciled; exact disjoint local union 6979/8318. Historical and canonical seven-category arrays and AST nodes match exactly. Six filter IDs mapped to AST nodes: 429:8582, 442:8770, 452:8855, 458:8932, 464:8998, 468:9069. See [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP404_W3_B05_Accepted_Order_Audit_Rebuild_Local_Forensic_Register.json) and [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP404_Completion.json).

- Source-first local review by GPT, not independently staffed. OA62 reconstructs ledger from supplied accepted state and prior provenance, not proof of final E/S acceptance or valid B legs. Pair-based OA40 eligibility and time-only OA63 pruning differ; no production defect asserted merely from potential malformed inputs or incoherent owner state.
- Recovery and retention are ordered mutations, not an atomic transaction; a late exception can leave partial state. Native source equality/hash, dynamic dispatch, index consistency, live cache reuse, cause-only cache coherence and prior alias immutability remain conditional. No cross-owner acceptance or runtime equivalence asserted.
- No RAW payload, runtime, ZIP, production changes, performance measurements, fresh AST generator, or independent SHA-256 claim. Pinned old/current canonical AST arrays, CP316, historical W1 crosswalk and prior registers were directly reconciled.
