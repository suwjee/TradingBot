# Lifecycle / StopAll forensic audit

Status: source-level audit complete; integration evidence is bounded. Production Source and RAW were not edited. Authority is the extracted `package/` snapshot from `engine/engine.zip`, checked by the parent inventory as byte-identical to live Source. Existing unit tests are evidence, not normative authority.

Final Reference integrity distinction: package/live comparison is byte-exact for all twelve existing production Python files. The two Reference documents are **not byte-synchronized** with those files despite their declared status: eleven nonempty embedded files use CRLF while current Source uses LF, so their raw embedded bytes differ. All twelve existing embedded files (including the empty root marker) are newline-normalized and AST-equal; only the empty root marker is byte-exact. The thirteenth embedded path, `bridge/__init__.py`, is absent from current package/live Source. `reference-byte-analysis.json` records these results. Reference prose was assessed as a specification; neither its label nor its byte-exact claims were accepted as integrity proof. Source-level probes use the authoritative extracted package and are unaffected.

## Evidence and coverage

| Item | Coverage / current verification |
|---|---|
| `package/pipeline/lifecycle_engine.py` | READ_FULL, all 1,439 lines, all 40 AST class/function/method/closure definitions accounted for below |
| `bullish-rules.md`, `bearish-rules.md` | READ_FULL prose, 726 lines each; current normative Sections 0-13 independently read in both directions; Section 14 historical claims are not rerun claims |
| `ARCHITECTURE.md`, `source-map.json` | READ_FULL architecture; map parsed and inventoried for all twelve packaged Python entries; all lifecycle definition bounds reviewed |
| `engine/tests/unit/test_stopall_dominance.py` | READ_FULL, 251 lines; executed with package-authoritative preloaded modules |
| `engine/tests/unit/test_order_audit_lifecycle_contracts.py` | READ_FULL, 389 lines; executed with package-authoritative preloaded modules |
| `direction_policy.py`, `core_utils.py` | READ_FULL |
| Called code / caller closure | Bridge 1930-2064, 2108-2180, 2484-2700; E initialization 70-245; OrderAudit 1124-1158, 1435-1499, 1721-1806; Reaction LowerTimeframeIndex 812-866, 912-929 and MarketChronology 993-1038; S initialization signature and `first_a_stop` 233-273 |
| Focused existing contracts | PASS: **79 passed, 2 xfailed** in 0.32 s, current invocation `python -B lifecycle-audit/run_contracts.py`; the xfails are the pre-existing restored-Order_B confirmation-index defect in both directions, not a PASS claim |
| Additional probes | PASS execution: `python -B lifecycle-audit/probes.py`; 16 source-level cases, direction-paired; detailed outcomes in `probe-results.json` |
| Saved actual RAW trace | READ: `traces/raw-08-30s.events.json` and payload; four unique intrabar-rounding pairs located across both directions, all already calculation-invalid; no new full RAW run by this subagent |

All additional scripts write only under `lifecycle-audit/`. `-B` prevents bytecode writes. `run_contracts.py` preloads all relevant production modules from package paths before tests execute their live-path imports and asserts those loaded paths. No detector was patched and no proposed semantic fix was used to create any outcome.

## Findings / candidates

### LC-01 — Confirmed helper indexing mismatch; actual final-output impact unproven

Location: `lifecycle_engine.py:549-556`, caller `bridge/trading_pipeline.py:2502-2506`.

`visible_a_zones_after_s_stops` says it suppresses the A candle **containing** a confirmed transition event. It computes `bisect_left(main_times, S.decision_event_time)`, which returns the **next** main candle when the decision occurs inside a candle. The production `MarketChronology.main_index` uses `bisect_right(...)-1` for the containing candle. With 30-second candles and S decision `2000-01-01 00:00:35`, the containing candle is `00:00:30`, index 1, while the helper suppresses A `00:01:00`, index 2. Both directions produce exactly the same mismatch.

The actual RAW idx8 trace contains these unique pairs (native local datetimes, Asia/Tehran +03:30):

| Direction | S source | S decision event | Containing main candle | A removed by left insertion |
|---|---|---|---|---|
| Bullish | 2026-09-30 03:48:00 | 2026-09-30 03:52:25 | 2026-09-30 03:52:00 | 2026-09-30 03:52:30, price 4181.45 |
| Bullish | 2026-09-30 16:53:30 | 2026-09-30 17:02:05 | 2026-09-30 17:02:00 | 2026-09-30 17:02:30, price 4188.28 |
| Bearish | 2026-10-01 19:09:00 | 2026-10-01 19:36:40 | 2026-10-01 19:36:30 | 2026-10-01 19:37:00, price 4176.66 |
| Bearish | 2026-10-02 10:45:00 | 2026-10-02 11:27:45 | 2026-10-02 11:27:30 | 2026-10-02 11:28:00, price 4192.27 |

Refutation performed: every A above also appears in `invalidA`; final calculation-invalid filtering removes it independently. These observations prove the helper is reached with real intrabar events, but they do **not** prove a visible output difference on idx8. The full-direction call at 1977 calculates `candidate_a`, which is not subsequently used for final validation; the final visibility call is the relevant potential impact route. The helper also calls S's decision its stop: these are S formation events, not S's later own strict stop. Reference Section 12.6 supplies the general exact-stop/source ownership rule but does not explicitly settle that helper's formation-vs-own-stop terminology. Report as confirmed documented-helper mismatch, not as a confirmed global trading-output defect.

### LC-02 — Confirmed rejected-A cause restoration; interpretation conflict requires authority resolution

Call chain: `resolve_order_context:509-514` -> `accepted_audit_entry` in OrderAudit 1779-1806 -> E `initial_order_audit` -> `_rebuild_accepted_order_audit` in OrderAudit 1472-1483 -> `prepare_order_audit` 1759-1776.

The A ledger for one canonical physical identity contains an accepted A source at `2000-01-01 00:00:00` and a rejected source at `00:00:30`. Only `00:00:00` is passed in `accepted_a_sources`. Selection correctly changes the entry's primary source to `00:00:00`, but leaves both `a_causes` in the returned entry. The production E rebuild iterates every retained A cause and inserts both as `parent-stop` creation causes. Final `prepare_order_audit(..., accepted_a_sources={00:00:00})` still contains the rejected source's parent-stop cause at event `00:01:05`, in both directions.

The repro uses the pre-existing contract's actual `EZoneDetector`, canonical `Candidate`, `SZone`, actual `MarketChronology`, an explicitly invalid S root (so valid independent A provenance is required), and the unmodified public `rebuild_accepted_order_audit` call. The source ledger remains unchanged, so this is an indirect restoration issue, not accidental in-place mutation of the S ledger.

Refutation / authority conflict: Reference Section 11.5 says to retain the complete cause set for presentation; Section 11.6 says invalid/suppressed parents lose creation rights, while valid historical provenance survives consumer reconciliation. Simply hidden accepted A provenance is legitimate history. An A removed from calculation acceptance is materially different. The repro confirms code restores that rejected provenance; whether the complete-set statement authorizes it is ambiguous because the Reference does not explicitly distinguish accepted historical vs rejected A causes in Section 11.5. Preserve **Specification conflict** for semantics; this is not resolved by assuming every historical cause is valid. Root's OrderAudit review owns market reachability and final categorization.

### LC-03 — High-confidence live invalid-head blocker defect / prefix sensitivity

Location: `lifecycle_engine.py:825-835`, reachable from `resolve_order_context` and bridge 2044-2056.

The helper's documented rule is that opposite Orders are blocked while an invalid head remains live, until that head stops. The implementation skips an invalid A entirely if `stop_finder(A)` returns `None`. A head which has not stopped by the supplied end therefore blocks no Orders. Appending a future stop causes the helper to retroactively block earlier Order First timestamps.

Both directions were reproduced with actual `SZoneDetector.first_a_stop`, actual five-second lower candles and `MarketChronology`: invalid head source `00:00:30`, opposite First `00:01:00`. Prefix through `00:01:30` has no strict head stop and returns no blocked First. Appending one lower row at `00:01:35` creates the first strict stop and suddenly blocks the already-existing `00:01:00` First. This is an observable first divergence in the returned lifecycle block set.

Refutation: no hardcoded market timestamps affect production; the probe's dates only identify artificial inputs. A post-stop prerequisite could justify skipping an unresolved head, but that contradicts the helper's live-interval description and the call's intended provisional veto. Reference Sections 12.6 and 11 give generic ownership/invalid-provenance requirements, not this interval's detailed boundary rule. Classify High-confidence against documented live-head behavior, with full-market output impact and exact normative interval still pending.

### LC-04 — High-confidence visibility priority bypasses newest-stop boundary

Location: `visible_a_zones_after_module_boundaries:1266-1284`, `dominant_module:601-610`.

Reference Section 12.6 resolves new-leg A ownership from the **newest stopped owner**. Earlier calculation validation (`split_a_zones_by_dominant_stops:714-725`) ranks stop-main-candle first. Final A provenance visibility instead ranks all stopped prior modules by priority/number/source and can reuse an older Red stop over a newer Blue stop.

Direction-paired production helper repro: old E Red source `00:00:00`, strict stop `00:00:45`; newer E Blue source `00:01:00`, strict stop `00:01:35`; A source `00:02:00` has minimum provenance `00:01:00`. It rebuilds after the old stop but straddles the newest stop. Final visibility selects old Red and publishes A. Under the newest stopped boundary it would be excluded. The provenance is aligned to a 30-second main candle; the earlier probe used an unnecessarily nonaligned `00:01:10` timestamp, which was corrected without changing the observed result.

Refutation: old high priority can legitimately remain dominant across a newer smaller E. This case has the old owner stopped **before** the newer E source, so its stop is historical, unlike an older owner surviving beyond the newer decision. Direct independent E1 roots can coexist in final E after restoration (E 644-703, confirmed by S/E reviewer); the helper input shape is structurally reachable. No actual RAW trace with this exact final visibility difference was established here. Keep High-confidence, not confirmed market behavior.

### LC-05 — Suspected S visibility discards an older surviving dominant E

Location: `visible_s_zones_after_module_resets:1089-1108`.

The function discards all prior modules sourced before the latest E/StopAll source, regardless of priority or whether the older larger owner remained alive beyond that newer decision. The direction-paired probe supplies old Red E source `00:00:00`, decision `00:00:05`, stop `00:01:20`; newer lower Blue E source `00:00:30`, decision `00:00:35`, no stop; S source `00:01:30` strictly beyond old Red price. S is suppressed with the old Red alone but becomes visible when the smaller newer Blue is included.

The consumed-S continuation helper specifically permits older strictly higher-ranked E owners that survive beyond the latest smaller E's decision (LC 910-948), so the two routes use inconsistent older-owner treatment. S/E reviewer confirms independent Blue roots may coexist with Red output. A concrete accepted-production/RAW reproduction and independent authority interpretation are still needed. Classify **Suspected**, with the actual helper behavior confirmed.

## Rule-by-rule compliance record

Reference line locations below are identical in both prose copies unless the direction text differs. Verdicts are scoped to read Source and bounded evidence, not proof over all market histories.

| Rule | Reference | Enforcement / checked closure | Verdict and evidence |
|---|---|---|---|
| S Blue < E Blue < S Red < E Red; A excluded | 12.1, L275-277 | SEQUENCE_PRIORITY 29-39, owner model 95-118, detector accept 367-379 | Implemented; A is not accepted by detector API |
| First exact occurrence highest but unarmed | 12.2, L281 | incoming count1; armed count>=2 | Implemented; count1 controls PASS both directions |
| Only exact family/number repeats count | 12.2 | accept tuple equality 372-373 | Implemented; existing different E-number controls PASS |
| Larger same-family E replaces, smaller does not | 12.2 | `_dominates_e` 160-167, accept 374-379 | Implemented; Red dominates Blue regardless of number |
| Lower owners cannot stay armed in parallel | 12.2-12.4 | one owner closure, no Blue ledger | Implemented; lower Blue S/E tests PASS |
| Latest occurrence supplies strict stop level/start | 12.2-12.3 | replace latest 373, strict start341 | Implemented; count2/3 existing controls PASS |
| First lower-timeframe strict crossing | 3.3-3.4, 12.3 | `_strict_stop` 143-157 -> real immutable LowerTimeframeIndex | Implemented; equality controls PASS both directions |
| Unrelated replacement source must follow prior stop | 12.3 | stop<boundary345, before-stop replacement controls | Implemented in bounded tests |
| Exact direct parent may donate with retrospective source | 12.3 | parent type/index/time/price/stop match 347-364 | Implemented; S and E direct-parent controls PASS |
| Parent stop <= E donor decision | 12.3 | guard347, `_strict_stop` first crossing | Implemented; after-decision negative control PASS |
| Wrong parent or wrong stop cannot use exception | 12.3 | exact comparisons354-362 | Implemented; mismatched S parent and E stop controls PASS |
| Completed historical stop survives replacement | 12.3 | pending_stop 407-408, E completed439-454 | Implemented; Mode-A intervening S test PASS |
| E family-independent geometry donor | 12.3 | `_stopall_from_e`, stopped owner recorded separately | Implemented; constructor copies actual Order fields |
| Existing StopAll stop gate precedes S/E gate | 12.3 | active stopall418-437 before owner439 | Implemented; numbering chain test PASS |
| S Red donor requires ModeB and armed stopped Blue | 12.4 | process_s389-400 | Implemented; no-stop and ModeA-negative controls PASS |
| Hard boundary clears count/owner/pending | 12.5 | reset blocks404-405,435-436,452-453 | Implemented; exact-owner reset test PASS |
| Atomic reset publication refreshes dependent caches | 12.5 | reconcile1235-1237 -> E setter230-242 | Implemented; existing cache/physical-stop retention controls PASS |
| History immutable during StopAll construction | 12.5, 3.8 | frozen dataclasses and replace output466-473 | Implemented; additional input snapshot remains equal |
| A comparison uses newest stopped main candle | 12.6 | split stopped source/stop indexes641-725 | Implemented in calculation; partial/inconsistent in final A visibility, LC-04 |
| A strict beyond invalid; equality remains eligible | 12.6 | policy strict_cross727-734, S stage801-810 | Implemented; mirror operators exact |
| A->A fresh trigger strictly after prior stop independently valid | 12.6 (general) | split699-709 | Stronger-than-spec detailed chronology rule; documented only by Source comments |
| Interior confirmed Reaction exception | 12.6 (general) | split736-796 | Undecidable detailed exception; Source-only provenance behavior, no exhaustive normative textual rule |
| Invalid live leg-head Order veto | 12.6 (general), Source docstring821-823 | helper825-835 -> resolve518 | Partial, LC-03; no-stop interval omitted |
| Accepted A cause beats provisional blocked First | 11.5, lifecycle owner doc502-507 | resolve509-540 -> accepted_audit_entry | Implemented for physical accepted First veto; cause set conflict LC-02 |
| Consumed S requires A strictly after larger E stop | 8.5 | helper898-905 | Implemented in Source; strict `<`/`>` geometry mirrored |
| Continuation retains latest-stop higher owner | 8.5, 12.6 | consumed eligibility910-964 | Implemented; inconsistent with S visibility LC-05 |
| Same-source E prevents S counting | 8.5, 12.2 | `s_zones_for_stopall` 1019-1028 | Implemented exact index/time key |
| Higher Red S can supersede stopped Blue S | 12.6 | visible_s1175-1181 | Implemented direction invariant priority |
| Lower/equal S under stopped larger ownership suppressed | 12.6 | visible_s1109-1202 | Partial / possible older-owner bypass LC-05 |
| E/StopAll source occupancy removes duplicate A/S | 12.6 | finalize1352-1359,1417-1429 | Implemented; physical index used consistently |
| Historical referenced S/A retained for lineage | 12.6 | finalize1372-1388,1397-1415 | Implemented source-time closure, then invalid/occupied filtering |
| Internal Reaction predicates keep boundary equality eligible | 4.8, Source doc1303-1306 | reaction_number1288-1299, point_inside1302-1322 | Implemented helper strict bounds; both helpers have no packaged caller |
| Internal-output filter does not perform obsolete Order veto | 3.8, current Source | filter1325-1336 | Implemented pass-through; currently returns fresh lists |
| Final A same-source S occupancy | 12.6 | visible_a1433-1439 | Implemented physical source index |
| Intrabar S transition belongs to containing main candle | Source doc544-547; 12.6 general | visible_a_after_s549-556 -> Bridge2502 | Contradicted helper doc, LC-01; market final impact masked in observed cases |

## Complete lifecycle symbol accountability

| Source region / symbols | Assessment |
|---|---|
| 24-39 versions, SEQUENCE_PRIORITY, sequence_priority | Reviewed constants and authoritative table |
| 43-92 StopAll | All public geometry, Order and optional donor fields reviewed; immutable output schema |
| 95-118 _DominantBehavior, priority, armed, key | Reviewed exact family/number identity, invariant key formatting and count boundary |
| 121-167 StopAllDetector.__init__, _strict_stop, _dominates_e | Reviewed sort, lower chronology, first strict crossing, index mapping and red-number dominance |
| 169-321 _stopall_from_e, _optional_int, _optional_decimal, _stopall_from_s | Reviewed all constructor fields, None handling, donor/counter separation and S parent-stop provenance |
| 323-475 detect, armed_stop_before, accept, process_s_event | Reviewed every branch, E/S chronological merge, pending gates, active StopAll continuation, hard reset and final stop completion |
| 478-540 detect_stopalls, resolve_order_context | Reviewed wrapper and accepted-vs-blocked identity/First precedence plus cause restoration closure |
| 543-610 visible_a_zones_after_s_stops, module_priority, module_identity, module_stop_event, strictly_beyond_boundary, dominant_module | Reviewed all helper branches; LC-01/LC-04 cover substantive gaps |
| 613-814 split_a_zones_by_dominant_stops | Reviewed all stopped-owner, A->A, latest stop-main-candle, interior-Reaction, consumption and S-stage-invalid paths |
| 816-979 blocked_orders_while_invalid_leg_heads_are_live, consumed_s_evidence_after_larger_stop | Reviewed all eligibility, exact stop/Close, older larger survival, owner tie and earliest-candidate paths |
| 981-1028 s_zones_for_module_engines, s_zones_for_stopall | Reviewed chronological previous-source eligibility and same-source E precedence; lower-priority larger-owner bypass remains pending through LC-05 |
| 1030-1206 visible_s_zones_after_module_resets, cached_stop_event | Reviewed immutable stop cache, latest external lifecycle restriction, source event, latest strict stop ties, higher S exception and consumption |
| 1208-1286 reconcile_stopall_lifecycle, visible_a_zones_after_module_boundaries | Reviewed single accepted-chronology pass, atomic reset publication and final provenance filtering |
| 1288-1336 reaction_number_is_internal, point_is_inside_healthy_reaction, filter_internal_behavior_outputs | Reviewed and checked packaged callers; first two are currently unused, filter intentionally pass-through |
| 1338-1439 finalize_behavior_visibility, visible_a_zones | Reviewed source occupancy, referenced S/A lineage restoration, invalid identity removal and stable source ordering |

## Limitations / remaining work

This subtask does not independently certify Reaction, Blue/A geometry, E/Order discovery, transport or projection. Parent/other subsystem agents own them. No complete RAW calculation was run here; actual data evidence comes from the parent's saved unmodified trace. The four visibility/blocker probes establish returned helper differences; they do not prove all supplied market files exhibit downstream output differences. LC-02 cannot be semantically resolved without distinguishing invalid A provenance from historical accepted provenance in the conflicting Reference wording. The existing 2 xfailed contracts are genuine unresolved cases and remain failures of the desired behavior, not successful verification.

Next bounded action: inspect `probe-results.json` cases `rejected_A_cause_restoration` and resolve the exact accepted-cause contract before any implementation change.
