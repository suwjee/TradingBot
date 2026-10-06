# S/E forensic audit — immutable Current package

Date: 2026-10-05. Real-market timestamps below are Asia/Tehran (`+03:30`). Artificial probes use a fixed, naive `2000-01-01` wall clock and are explicitly not market RAW.

**Result:** one E selection defect is confirmed in four unique final-visible E rows on real XAUUSD RAW, two in each direction; a second conditional S provenance defect and one specification conflict are reproduced in both directions. Retained S ownership was found, but its alleged output impact was refuted on the two complete traced RAW inputs. No production, archive, or RAW correction was made. These findings concern Current `engine.zip` Source and the current V5.4.24 prose, not the correctness of a historical implementation.

## Authority and complete reading coverage

The root audit established twelve packaged production Python files equal to their live counterparts. This subtask uses `package/` directly. S SHA-256 is `ef71a2e4176caaabc25d1ef0c1f0f24efb54ed3110982cdb7cf52d2449cca2ee`; E SHA-256 is `9047cfbe0beba2b91d36a136c9b6033563bc5ac1ebd7a54af6b698c962f80aef`. The complete source spans are S `1–1444` and E `1–1140`. All classes, dataclass fields, properties, methods, wrappers, and nested closures were read. Exact coverage of all **81** definitions is in `FUNCTION-COVERAGE.md` and `coverage.json`.

Both standalone algorithm prose documents were covered completely: Bullish lines `1–726` were read; Bearish lines `1–329` were read, and `330–726` were compared line by line as an identical text duplicate of the fully read Bullish span. This comparison is asserted in `build_coverage.py`; it is a text comparison after decoding and newline handling, not an embedded-Source byte comparison. These line numbers also identify the same prose in `package/algorithms/TradingBot_{Bullish,Bearish}_Algorithm_Reference_V5.4.24_Source_Synchronized.md`, before the embedded Source section. Copied Source is not counted as a second independent semantic authority.

**Final byte review, 2026-10-06:** `check_reference_bytes.py` and `reference-byte-analysis.json` distinguish Reference fidelity from package/live equality. Each Reference embeds thirteen paths. All twelve existing packaged/live files remain byte-equal to one another. Their twelve corresponding Reference embeds are equal after CRLF-to-LF normalization and have equal parsed Python ASTs. Eleven nonempty embeds use CRLF while current Source uses LF, so those embeds are not byte-exact; only the empty root `__init__.py` embed is byte-exact. The thirteenth embedded path, `bridge/__init__.py`, has no corresponding packaged/live file. This integrity caveat is retained by the root audit. The S/E Source comparisons and unchanged-output RAW proof remain valid.

| Direct dependency / caller | Coverage | Scope limit |
|---|---|---|
| `order_audit_engine.py` | `1–1613`, `1818–1947` READ_FULL | Includes every S/E mixin callee, Order_B dataclasses/discovery and identity/cache operations. Preparation/serialization helpers `1614–1817` belong to the root's Order audit. |
| `reaction_engine.py` | `974–1202` READ_FULL | Every `MarketChronology` callee used by S/E; complete Reaction owner audited separately. |
| `direction_policy.py`, `core_utils.py` | READ_FULL | Decimal, strict crossing, directional geometry and physical identity. |
| `bridge/trading_pipeline.py` | `123–210`, `1865–2349` READ_FULL | Normalization plus full S/E rebuild, Order_B feedback, shared state reuse and retained eligibility. Full bridge audit belongs to root. |
| `lifecycle_engine.py` | `613–815` READ_FULL | Accepted-owner A validation used for independent refutation. Broader lifecycle audited by its owner. |
| `test_order_audit_lifecycle_contracts.py` | READ_FULL and executed | Current result: **37 passed, 2 xfailed**. Covers artificial accepted Order/invalid S/reset contracts, not full S formation or market correctness. |

Study coverage and verification are separate. READ_FULL means complete inspection, not universal correctness proof.

## Findings and certainty

| ID | Classification | Consequence | Evidence |
|---|---|---|---|
| SE-01 | **Confirmed RAW**, spec-to-code divergence | Equal-stop Order tie chooses earlier First instead of the specified later First; final-visible E Order identity, mode, box, stop and provenance differ. | Both-direction executable probe plus original `_zone` boundary trace: 4 unique final-visible E rows on idx8, 2 Bullish and 2 Bearish. |
| SE-02 | **Confirmed**, conditional provenance/schema defect | An order-free S converted to Red keeps `order_direction=None`, despite acquiring a physical opposite Order. | Both-direction executable probe with decision strictly after A stop; no public occurrence found in 21 completed saved calculations. |
| SE-03 | **Specification conflict** | Shared-Order S reconciliation can set decision before the A stop that opens S space. | Both-direction executable probe; current prose §7.6 expressly permits the source-start test but conflicts with §7.1's gate. |
| SE-04 | **Suspected structural risk; output impact NOT confirmed** | Provisional/invalid S ownership and initial S state remain reused after later validity/reconciliation. | Two complete RAW traces, both directions, three passes each: all revived A remain independently invalid, individually and in batch. |
| SE-05 | **Confirmed pre-existing cache defect; root owns deduplication** | Restored reset-leg Order rows can exist in the ledger but be absent from the confirmation index used by later E queries. | Current strict xfail in both directions; detailed ownership belongs to root Order audit. |

### SE-01 — a route's early minimum discards the specified equal-stop winner

**Specification:** both references §8.2, lines `185–187`, and reconstruction table §13.8, E row `620`, specify earliest exact Order stop, then **larger FirstIndex** for a true stop-event tie. Physical creation's separate earliest-confirmation rule in §9.1 and table row `621` does not replace the E consumption rule.

**Source chain:** `EZoneDetector._zone`, E `391–418`, retains only `inherited[0]`, `carried[0]`, `post_stop_accepted[0]`, and the one result of `_first_order`. Its final key correctly uses `(stopEvent, -FirstIndex)`, but a candidate can already have been dropped. `OrderAuditEngineMixin.order_candidates`, Order `830–840`, sorts equal stopped candidates by ascending FirstTime; `_first_order`, `843–856`, returns the first one. `_post_stop_accepted_orders_for_parent`, `1366–1374`, ranks confirmation before `-FirstIndex`. The other eligible Order never reaches `_zone`'s final comparison.

**Minimal reproduction:** `python -B engineering/verification/forensic-audit-2026-10-05/s-e-audit/probes.py`. In `order_equal_stop_tie`, a canonical direct parent-stop Order has identity `(5,6)` and confirmation `2000-01-01 00:03:10`; an accepted canonical reset-leg Order has identity `(7,8)` and confirmation `00:04:10`. Both strictly stop at `00:04:35`. Source chooses First `5`; the stated consumption tie rule chooses `7`. Exact Decimal reflection yields the identical identity error in Bearish. The Order_B accepted-stage boundary is explicitly supplied as an `OrderBResetLeg`; this probe does not independently prove its market discovery.

**First divergence:** physical eligible choices contain both Orders; route-specific reduction chooses `(5,6)` before E construction. Source and decision geometry can remain equal because the stop events are equal, while Order identity/number/mode/box/provenance are already wrong under §8.2. No output correction was applied.

**Confirmed RAW execution:** the root's `trace_pipeline.py --raw-index 8 --timeframe 30 --order-ties` calls each original `_first_order` and `_zone` unchanged, records the actual native `order_candidates` query with the same positional and keyword arguments, and returns the original results. Thus both choices are eligible in the same parent branch and with the same hard-reset bounds; the trace does not infer eligibility from final ledger membership. `raw_tie_analysis.py` independently confirms the complete traced stable payload equals uninstrumented stdout after removing timings, joins exact physical parent/Order/source/decision identity to final public E, and verifies the two Orders' exact ledger stop events match that E decision.

There are **334** subroute observations and **324** observations where the wrong Order survives `_zone`. Deduplication gives **20** unique parent-stop/actual/expected/stop conflicts, **20** physical constructed-E identities, and **52** intermediate family/number variants. Of those, **4** unique final-visible E rows retain the wrong Order, **2 per direction**. Intermediate counts must not be presented as final-output defect counts. Family/number may be recanonicalized after branch construction; the join retains the complete physical parent, selected Order, source and decision identity and reports actual final family/number.

| Final visible E / source (Asia/Tehran) | Exact parent stop | Selected Order `(First,Break)` | Required later Order | Shared exact Order stop |
|---|---|---|---|---|
| Bullish Red E5, `2026-09-29 21:28:00` | `2026-09-29 21:10:05` | `(2825,2839)` | `(2841,2847)` | `2026-09-29 21:30:00` |
| Bullish Blue E1, `2026-09-30 12:37:30` | `2026-09-30 12:30:00` | `(4541,4542)` | `(4544,4545)` | `2026-09-30 12:38:30` |
| Bearish Blue E1, `2026-09-29 21:03:30` | `2026-09-29 20:49:10` | `(2777,2793)` | `(2801,2805)` | `2026-09-29 21:08:25` |
| Bearish Red E4, `2026-10-02 08:02:00` | `2026-10-02 07:43:40` | `(9476,9498)` | `(9499,9508)` | `2026-10-02 08:08:30` |

For the first Bullish row, parent E source is `2026-09-29 20:38:30`. The selected Order confirms at `21:24:15`, mode A/number 250, box `4146.525 / 4143.415`, stop `4147.6`; eligible reset-leg identity `(2841,2847)` confirms at `21:28:25`, mode B/number 251, box `4143.7 / 4142.71`, stop `4146.525`. Both exact stops are `21:30:00`; the specified later First is discarded before `_zone`'s correct final tie comparison. The Bearish Blue E1 counterpart chooses confirmation `21:01:05` over eligible reset-leg confirmation `21:07:05`, both exact stops `21:08:25`. Complete native observation/final-output joins are in `RAW-tie-confirmation.json`.

**Same-class broader search:** `scan_saved_outputs.py` separately examined 21 completed 30/60-second stable outputs and found 52 E rows with a later final-ledger identity sharing the selected Order's exact stop, and later FirstTime strictly after the E parent stop. These remain candidates unless independently joined to actual boundary observations. The number 52 in this wider scan is unrelated to the 52 intermediate zone variants above. Complete broader candidates are in `RAW-order-direction-findings.json`; only the four native-traced final rows above are upgraded to Confirmed RAW here.

**Repair recommendation only:** resolve consumption ties across the complete eligible physical-Order set or prove that each subroute uses the same `(stopEvent,-FirstIndex)` minimum before taking one member. Preserve the separate one-parent-stop creation rule. Review any intended confirmation-before-First consumption rule as a Reference change rather than silently replacing §8.2.

### SE-02 — newly Order-backed S retains null opposite direction

**Source chain:** order-free Type4 and Type3 builders set `order_direction=None` at S `562` and `1030`. `reconcile_shared_order_stops`, S `1393–1417`, replaces color and every physical Order geometry/chronology field but omits `order_direction`. Ordinary Order-backed construction explicitly sets it at S `1193`. Legacy serializer projects the retained value directly at Bridge `345`; no serializer recalculation repairs it.

The mirrored `shared_s_direction_after_a_gate` probe has S source `00:01:00`, A stop `00:00:35`, verified physical Order confirmation `00:01:10`, and exact stop/Red decision `00:01:30`. Decision is safely after the A gate. Result is Red with a populated Order identity but null direction in both paths; expected physical direction is `bearish` for Bullish behavior and `bullish` for Bearish behavior. This defect is independent of SE-03's earlier-decision conflict.

Reference §7.6 (`175–177`) requires the accepted physical Order to remain authoritative, and the mirror table's opposite-Order row near `558` assigns its direction. Schema §13.2 (`316`) includes `orderDirection`. Existing native Order-backed S establishes the intended populated-field behavior. No such public row occurred in the 21 completed saved calculations scanned here; conversion can remain latent or later invisible. The confirmed claim is conditional Source behavior, not current RAW prevalence.

**Repair recommendation only:** when reconciliation accepts a physical Order, populate the same opposite direction as native Order-backed S. Do not change the physical Order's creating cause or formation history.

### SE-03 — source-start reconciliation conflicts with post-A-stop opening

S `1376–1381` accepts the first Order stop at/after `zone.source_time`, strictly before the existing S decision. It never checks `a_stop_event_time`. For Type3 the source may predate A stop because its complete Break-to-Reset geometry starts earlier. `shared_s_before_a_gate` uses source `00:00:00`, A stop `00:00:35`, original decision `00:01:50`, and a recorded physical Order stop verified against actual synthetic lower candles at `00:00:15`. Source replaces S's decision with `00:00:15`, before its own opening gate, in both directions.

Both references §7.1, line `144`, say S begins at A's first strict stop. Both §7.6, line `177`, expressly use the frozen source main-candle start and do not add an A-stop lower bound. The implementation accurately follows the latter predicate. Therefore this is a **specification conflict**, not permission to add a speculative comparator. RAW reachability of the earlier-decision case was not established in this subtask.

**Required semantic decision before repair:** is a historical accepted Order stop before A stop allowed to decide S retrospectively, or must S decision occur at/after its A stop? Then synchronize the shared-reconciliation rule and code consistently in both directions.

### SE-04 — stale eligibility state exists, but the supplied anchor does not establish a Current bug

**Structural chain:** S `1228–1299` builds `a_ownership_windows` during the initial S pass. `eligible_a_zones`, `695–697`, reads those retained windows. Bridge `1922–1929` reuses the same detector and `initial_s_zones` on Order_B feedback; later S filtering, invalid S identification, and shared-Order decision replacement do not refresh that ownership state. Both §2 (`43–45`) and stage-order rules require final accepted context, but reference independence/continuation rules must also preserve valid historical non-public state. Releasing every non-public S would be too broad.

**Known anchor:** immutable XAUUSD idx8 has 68,492 five-second rows and is calculated at 30 seconds. All-A contains Bullish A source `2026-09-29 20:15:30`, price `4144.795`, trigger `20:09:00`, confirming Reaction Break `20:18:00`; the RAW source extreme occurs at `20:15:50`. It is absent from retained eligible-A because the initial Advanced S owns `20:14:00 .. 20:26:40.000001`. That S's source is `20:15:30`, parent A source `19:51:30`, and its identity is explicitly in final invalid-S. Removing only explicitly invalid-S windows makes this A eligible for the next audit stage.

**Independent refutation:** production `split_a_zones_by_dominant_stops` on actual RAW chronology plus accepted S/E/StopAll rejects that restored A in all three feedback passes. Accepted E2 Red source `2026-09-29 18:59:00`, price `4148.43`, decision `19:17:15`, first strictly stops at `20:14:35`. Its stopped main candle is newer than E1 Blue source `19:51:30`, whose stop is `20:14:00`. The A price is strictly below the Red E price and is the new closed-leg head; the accepted-owner interior exception does not rescue it. This is consistent with both references §12.6, line `303`.

The final Order_B candidate uses accepted E anchor `19:51:30`, reset Reaction First `20:20:30`, Reset `20:22:45`, frozen boundary `4144.795` sourced at `20:15:30`, strict break `20:26:40`, physical opposite Reaction First `20:32:00`, and confirmation `20:33:00`. Invalid A geometry may still be the market extreme inside an accepted anchor's LL range; the LL source is not itself an assertion of accepted A behavior. The alleged stale-S-to-invalid-Order_B causal diagnosis is therefore **not confirmed under Current authority**.

**Generalized refutation:** the saved observation traces are root-verified equal to uninstrumented outputs. `general_ownership_analysis.py` reconstructs original eligibility exactly before every experiment, then removes only windows attached to explicitly invalid S. Each revived A is tested independently and all revived A are also tested together through the native accepted-owner split.

| Complete RAW / direction | Feedback passes | Explicit-invalid S windows removed per pass | Revived A per pass | Newly accepted A individually / batch |
|---|---:|---:|---:|---:|
| idx8 XAUUSD Bullish | 3 | 35 | 13 | 0 / 0 |
| idx8 XAUUSD Bearish | 3 | 29 | 6 | 0 / 0 |
| idx14 USOIL Bullish | 3 | 46 | 17 | 0 / 0 |
| idx14 USOIL Bearish | 3 | 49 | 16 | 0 / 0 |

RAW hashes were checked before and after these read-only experiments: XAUUSD `2d871c57ad7b0a2ea2ad0e0f2954d70a6d4585fc273e4cadbf048803929c8428`; USOIL `4c7f874d141a51e3188a176a26eca108e40967baa543922ea34c0e027cda7b4e`. USOIL contains 93,533 rows. Every before/after hash equals the registry.

**Related suspected class:** `_a_owned_by_s`, S `640–679`, returns False immediately on the first matching window when the A trigger is after that window start. A supplied overlapping-window probe gives different results when window order is reversed in both directions. Production windows are appended in deterministic chronology; this observation alone does not establish an output bug or require order-insensitive behavior. It stays a scoped risk until native reachability and authoritative ownership meaning are proven.

**Repair recommendation only:** if a future accepted-output counterexample establishes impact, replace anonymous mutable windows with explicitly identity-owned state and refresh only state whose parent was invalidated. Preserve valid historical/non-public S evidence, run accepted-owner validation before declaring A restored, and re-evaluate Order_B feedback from that validated context. Do not expose the known `20:15:30` A solely because its provisional S was removed.

### SE-05 — restored Order cache/index remains a root-owned defect

`OrderAuditEngineMixin.ensure_accepted_order_audit`, Order `1590–1611`, merges preserved entries with `setdefault` after the canonical rebuild but does not restore `_order_audit_confirmation_index` for those entries. `_post_stop_accepted_orders_for_parent`, `1340–1374`, enumerates that index. The accepted ledger and the query index can disagree. `test_ensure_restored_order_is_visible_through_confirmation_query` (`266–286`) is a strict expected failure in both directions. Current execution confirms `37 passed, 2 xfailed`; this audit does not relabel expected failures as correct behavior. No change was made.

## Rule and implementation coverage

| Reference rule / Source responsibility | Reviewed implementation | Verdict and proof limit |
|---|---|---|
| §3 Decimal/strict crossing/identity/mirror | Core, DirectionPolicy, S `225–273`, E `251–372` | Implemented in reviewed branches; fixed Decimal reflection exercised in all new probes. |
| §7.1 A-stop handoff, stale-next-A guard, ownership/independence | S `631–742`, `1228–1302`; Bridge reuse | Retained state inspected; SE-04 risk and two-RAW refutation recorded, no universal output defect claimed. |
| §7.2 Type3 Reset owner, deadline, inclusive complete source, last equality, trend qualification | S `381–453`, `999–1055` | Branches correspond to prose; full market branch exhaustiveness not proven by existing unit suite. |
| §7.3 Type4 fresh candidate, Blue/public gate, next-confirmation exclusive deadline, Type3 tie | S `456–587`, `1272–1284` | Corresponds to prose and explicitly direction-mirrored. No additional counterexample established. |
| §7.4 immutable first physical Order, Simple timing, nested Advanced and candidate source | S `276–379`, `590–629`, `699–807`, `1057–1226`; Order `1821–1915` | Physical identity and source-window rules inspected; no later native refresh of the A Order. |
| §7.5 strict Order/candidate race, tie and qualification/fallback | S `810–996` | Exact equal lower position returns no decision; lower predicate and fallback were read completely. Universal market correctness not claimed. |
| §7.6 shared physical accepted stop, dedup/winner/provenance | S `1305–1418`; Order `1922–1947` | Partial: SE-02; source accurately implements conflicting §7.6 predicate in SE-03. |
| §8.1 first parent stop after decision | E `320–356` | Implemented; existing native chronology tests run for both directions. |
| §8.2 eligible physical routes and exact consumption tie | E `374–476`; Order `440–1387` | Contradicted for equal stops by SE-01; complete route/calculation cache closure reviewed. |
| §8.3 complete main boundary candles, earliest equal source | E `271–318`, `358–372`, `433–436` | Implemented; existing `test_extreme_range_query_keeps_first_equal_source` passes both directions. |
| §8.4 recursive parent chains, family/number, active transitions | E `729–1096` including all five nested helpers | Read completely; same-source and parent identity/family paths inspected. Complete boundary-candle source geometry prevents an earlier hidden lower extreme from being used to claim a later strict stop of a natively constructed E. No new independent counterexample established. |
| §8.5 consumed S / valid independent roots / invalid creation cause | E `477–599`, `644–819` | Existing invalid-S, independent Order_B cause, consumed-S and root restoration tests pass in both directions. |
| §8.6 same source and canonical ledger refresh | E `600–642`, `1098–1108`; Order `1389–1611` | Same-source winner contract inspected; ledger index restoration defect separately retained as SE-05. |
| §9/§11 canonical membership and cause/use separation | Order mixins and accepted-ledger rebuild | Canonical identity checks plus invalid S cause filtering reviewed and exercised by 37 passing tests. This is bounded validation, not independent Order_B market discovery proof. |
| §10 accepted Order_B anchoring/expiry into feedback | Order `55–435`; Bridge `2181–2232` | Entire dependency read; detailed semantic findings belong to root. A expiry receives `trigger_event_time` at Order `403`, which should be reconciled explicitly with any prose use of “formation”. |
| §12.5 atomic hard boundary cache refresh | E `225–242`; Order cache/index methods | Existing real StopAll-publication synthetic test passes, caches depending on boundaries clear and immutable physical stop/cross caches remain. SE-05 remains separate. |
| Public S/E fields | Dataclasses read completely; S reconciliation and direct serializer field inspected | SE-02 identifies the conditional missing direction; full projection audit delegated to root. |

## Reproduction and verification artifacts

| Artifact / command | Result |
|---|---|
| `python -B .../s-e-audit/probes.py` | PASS execution; expected SE-01 divergence and SE-02 omission observed both directions; SE-03 conflict and overlap observation preserved in `probe-results.json`. |
| `python -B .../s-e-audit/trace_analysis.py` | PASS reconstruction and native refutation for known XAUUSD anchor; exact original eligibility, RAW hash checks, three feedback passes. |
| `python -B .../s-e-audit/general_ownership_analysis.py` | PASS two complete saved RAW traces, both directions, 12 passes; all individually and batch restored A remain invalid. |
| `python -B .../s-e-audit/scan_saved_outputs.py` | PASS 21 completed stable outputs, no incomplete files used; 0 public missing-direction rows; 52 broader real-output equal-stop candidates. |
| `python -B .../s-e-audit/raw_tie_analysis.py` | PASS unchanged-source trace equality and exact native/final identity/ledger checks; 4 unique final-visible wrong E Order rows, 2 in each direction. |
| `python -B -m pytest -q -p no:cacheprovider engine/tests/unit/test_order_audit_lifecycle_contracts.py` | `37 passed, 2 xfailed in 0.30s`; source is byte-equal to the packaged S/E/Order implementation. |

`trace-analysis.json`, `general-ownership-results.json`, `RAW-order-direction-findings.json`, `RAW-tie-confirmation.json`, `coverage.json`, and execution logs retain machine-readable evidence. All probes are isolated under this audit folder. No Graphify, additional agents, production tests requiring modifications, full Engine RAW reruns, or Source/RAW fixes were performed by this subtask. The root performed the observation-only full RAW trace; this subtask independently inspected and analyzed its saved evidence.

## Limits and recommended follow-up

Source reading is complete for S/E, and all discovered candidate classes were searched/refuted within the available scope. This does not prove all possible market histories. The immediate reviewable follow-up is a consumption-only equal-stop correction for SE-01 and a direction-field correction for SE-02, subject to the user's separate authorization to fix Source. Decide SE-03's conflicting time gate before changing its chronology. Preserve the known anchor's independent accepted-owner rejection; the retained-window observation does not justify inventing an accepted A or removing its legitimate Order_B geometry.
