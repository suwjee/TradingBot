# Bridge projection and independent refutation

The complete optional projection region `package/bridge/trading_pipeline.py:508-1523` was READ_FULL by the lifecycle reviewer. Root read the complementary 1-507 and 1524-2957 regions. This reviewer additionally read bootstrap/shared-load 1-122, serialization caller 2700-2840, optional parser/loader 1597-1701, feedback 2181-2234, final visibility 2484-2700, and relevant called production stop/confirmation/Order cause routines. Scope is read-only.

Integrity boundary: all twelve existing package/live production Python files match byte-for-byte. Both Reference documents embed eleven nonempty files with CRLF rather than current Source LF, so those embedded bytes are not exact; their twelve existing embedded files are newline-normalized and AST-equal, with only the empty root marker byte-exact. The extra embedded `bridge/__init__.py` path is absent from current package/live Source. These facts are verified in root `reference-byte-analysis.json`; the `Source_Synchronized` label is not independent proof of byte synchronization. Projection probes load extracted package Source directly and remain valid.

## BR-01 — Confirmed HIGH: optional lifecycle-engine omission crashes a valid RAW configuration

The parser accepts an omitted `--lifecycle-engine` / `--stopall-engine` (1635-1640). `load_engines` then loads the normal lifecycle module by fallback (1694-1699), so a valid engine remains present. Order_B feedback unconditionally calls `reconcile_stopall_lifecycle` and supplies those StopAll objects to `discover_accepted_order_b_reset_legs` (2203-2219). Final visibility instead enables StopAll only when the **explicit argument** is non-None (2511-2519), so the same calculation produces an empty StopAll list there. It recomputes accepted Order_B identities with this different input (2540-2557), compares them against the converged feedback identities, and raises (2559-2562).

First static divergence: **StopAll participation in accepted Order_B input**, at feedback 2203 vs final 2511. It is an orchestration configuration mismatch, not an Order_B geometry tie or a serializer problem.

Root's real RAW reproduction is recorded in `configurations/manifest.json`, entry `without-stopall-engine` and `configurations/without-stopall-engine.stdout.json`. It uses the immutable five-second XAUUSD file `RAW FOREXCOM_XAUUSD 5S FROM 2026-09-16 22-35-00 TO 2026-09-17 19-15-35.json`, 30-second main candles, both directions, E enabled, Bridge Output enabled, all normal engine paths except the optional StopAll path omitted. Recorded exit code is 1 and response is:

```json
{"error":"Final Order_B lifecycle causes differ from converged E feedback."}
```

Independent refutation: optional-path omission could mean either default lifecycle-on (suggested by fallback load) or StopAll-off (suggested by final gate). The detailed desired default is not explicit in Reference 13.3, which only lists enablement fields. Either interpretation requires one consistent configuration across feedback and final visibility. The parser-accepted configuration fails on valid supplied RAW and the explicit-path control passes, so the defect is confirmed regardless of which default is ultimately selected. No semantics fix was applied.

## Projection compliance

| Requirement | Source closure | Result |
|---|---|---|
| Build from exact finalized legacy selections | `serialize_direction_payload:2756-2833` -> `build_bridge_output:1351-1453` | Implemented; legacy and projection use the same selected lists; full parent maps provide historical metadata only |
| Strict event guard must not select a replacement | `_bridge_proven_strict_event:547-584` | Implemented: validates exact lower timestamp, loops only duplicate rows at that same timestamp; no later crossing search |
| Preserve direction / strict equality | guard576-580, shared as_decimal | Implemented; Bullish Low<level / Bearish High>level; paired probe equality at120 returns null although strict cross exists at125 |
| Bound projected exact events by presentation horizon | horizon536-544, guard560-564, stopview595-604 | Implemented upper horizon; older historical parent events remain valid by design |
| Reaction confirmation uses opposite stop predicate | confirmation607-628 -> `MarketChronology.reaction_confirmation` | Implemented strict High>top / Low<bottom verification; guarded fallback returns null event when unproved |
| Formation Order is physical identity based | `_bridge_order_identity`, `BridgeProjection.audit_by_identity`, `parent_order` | Implemented `(FirstIndex,BreakIndex)` join; no list-position inference |
| Current creator Order needs one exact cause | `current_order:718-771` -> canonical prepared causes | Implemented type/source/time/family parent-stop match; reset-leg postBehavior match; missing/ambiguous returns null |
| E/StopAll numbered creator labels match audit | projector E1260-1265, StopAll1325-1330; Order register1019-1027 and restore1506-1523 | Implemented: OrderAudit writes E<n>/StopAll<n> labels used by projector; no alleged E-vs-E<n> mismatch |
| Parent metadata resolves exact historical source | `_bridge_source_index`, `_bridge_parent_behavior_for_e`, full maps1386-1406 | Implemented index+time joins; paired probe refuses same index with wrong time |
| Blue and A ordinal mapping includes non-public calculation ledger | `_bridge_full_lines_by_ordinal:1015-1024`, `state.full_lines_by_direction` | Implemented source sort matches calculation ordinal route; no synthetic public-only ordinal join |
| Blue stops cannot be newly fabricated | `_bridge_project_blue:1001-1008` | Implemented deliberate null when finalized BlueState stop evidence is absent |
| Preserve exact StopAll donor vs stopped owner distinction | `_bridge_project_stopall:1272-1338` -> frozen StopAll donor fields | Implemented projection reads donor metadata independently from group gate; absent donor stop remains null |
| No semantic input mutation | all projector paths / production paired probes | PASS for bounded S/E/OrderAudit build: accepted ledger, parent S, E object and sequence resets remain value-equivalent after projection |
| Public Order identities and exact parent causes consistent | `validate_order_audit_bridge:1456-1521` | Implemented rejects missing physical identity and duplicate physical owner per exact parent-stop key; does not choose or rank Orders |
| Invalid cause is not invented by projection | current_order/OrderAudit format only consume prepared causes | Implemented projection owner boundary; LC-02 rejected-A restoration arrives from upstream prepared ledger and must be resolved there |

Projection query clarification: `_bridge_parent_stop` says “never perform a new stop search,” but calls E's `parent_stop` -> `_first_parent_stop`, which performs the authoritative first-cross segment query; `_bridge_a_stop` also reuses S's pure first-stop query. The projector does not choose an alternate event or modify semantic detector state, but these docstrings overstate the absence of queries. `MarketChronology.reaction_confirmation` may memoize the same authoritative confirmation in a derived cache. No trading divergence was found from these queries; they should not be reported as substitute-event calculation without such evidence.

## Complete projection symbol accountability

| Lines / all symbols read | Checked behavior |
|---|---|
| 508-544 `bridge_datetime`, `bridge_direction`, `bridge_mode`, `bridge_color`, `_bridge_horizon`, `_bridge_in_horizon` | Native local formatting, enum formatting and upper display horizon |
| 547-636 `_bridge_proven_strict_event`, `_bridge_stop_view`, `_bridge_reaction_confirmation`, `_bridge_order_identity` | Exact recorded strict checks, fallback null, opposite confirmation predicate, physical identity |
| 639-830 `BridgeProjection`, `__init__`, `physical_order`, `parent_order`, `current_order`, `order_audit` | New identity index and projected dictionaries; canonical cause joins; unique-cause conflict handling; Order geometry formatting |
| 833-910 `_bridge_parent_stop`, `_bridge_a_stop`, `_bridge_behavior_stop`, `_bridge_blue_formation` | Existing authoritative owner queries, guarded event formatting; Scale vs Reset formation |
| 913-1024 `_bridge_project_reaction`, `_bridge_project_reset`, `_bridge_project_blue`, `_bridge_full_lines_by_ordinal` | All output fields, canonical public/raw geometry, reset evidence, intentionally unavailable Blue stops, calculation ordinal lookup |
| 1027-1178 `_bridge_project_a`, `_bridge_project_s`, `_bridge_source_index` | All A/S fields, Blue pair references, physical parent/current Orders, exact source identity |
| 1181-1348 `_bridge_parent_behavior_for_e`, `_bridge_project_e`, `_bridge_project_stopall`, `_bridge_audit_order_key` | Parent lineage lookup, numbered current causes, immutable StopAll donor metadata, physical chronological audit sorting |
| 1351-1521 `build_bridge_output`, `validate_order_audit_bridge` | Every final selected collection, full-history metadata maps, public physical identity and single-owner invariant |
| Shared bootstrap/load 1-122; serialize caller2700-2840 | Flat package-source imports, native Tehran epoch conversion, exact same legacy/projection list selection |

## Bounded dynamic evidence

`python -B lifecycle-audit/projection_probes.py` completed successfully and wrote `projection-probe-results.json`. It uses actual packaged MarketChronology/Candle/SZone/EZoneDetector/OrderAudit owners in both directions. Known lower event `2000-01-01 00:02:05` is validated, equality at `00:02:00` returns null without scanning to the later cross, a beyond-horizon event is null, wrong family/event creator causes are declined, and an exact-source parent resolves while same-index/wrong-time does not. Each direction builds one public S, one E and one canonical OrderAudit through `build_bridge_output` and verifies semantic input immutability.

The probe does not dynamically exercise every Reaction/Reset/Blue/A/StopAll projection field; those paths were fully inspected and the root full-RAW projections provide integration evidence. Do not elevate this bounded test to proof of all projection histories.

## Independent Reaction / Blue refutation

This reviewer read `reaction-audit/probes.py`, Reference Sections 4.4 and 5.2 in both directions, and the relevant production `UnifiedReactionDetector.detect:2129-2228`, initial first-only handling1642-1652, `DetectorBase:105-157`, and full `count_scale_strikes`/intrabar helper84-204. Each of the four other-agent repro functions was independently executed without writing its evidence or modifying Source. All four reproduced in both directions.

| Candidate | Refutation checked | Independent judgment |
|---|---|---|
| Initial confirmation candle cannot seed next normal Reaction | Break candle has the required directional First role; complete post-confirmation remainder has no first strict Reset; main low8.6 does not break prior8.5. Unified initializes `candidate=None` and starts at break+1, while standalone includes same-candle First | Confirmed contradiction of Reference4.4; no invalidity/Reset rationale defeats the fixture |
| GREEN Break main candle Scale strike uses post-confirmation extreme | First strict confirmation is12:01:00; eligible Low through it9.1 remains above Fibonacci8.764; Low5 occurs12:01:15. Full-main GREEN branch appends pending without exact cutoff | Confirmed contradiction of Reference5.2; green confirmation does not authorize later Break-candle prices |
| Intrabar pending Scale search passes the first confirmation with no eligible strike | At12:01:00 strict Reaction confirmation already occurs but eligible list is empty; helper checks `breaks and eligible` and continues until later Low5. The normative cutoff is first Reaction confirmation, independent of candidate eligibility | Confirmed contradiction of Reference5.2; helper must not keep a pending strike search open after first confirmation |
| Sparse first main gap infers wrong timeframe and misassigns Reset main candle | Starts0,60,90,120 represent valid sparse30s supplied buckets; first60s gap is not evidence timeframe60. Source derives timeframe from first pair; reset120 maps to index2 rather than containing3 | Confirmed sparse-input source defect; missing RAW bucket is a legitimate boundary condition, not fabricated chronology |

No proposed fix, source rewrite or changed fixture output was used in this independent pass.

Next bounded action: open root `configurations/without-stopall-engine.stdout.json` and compare the StopAll input gates at bridge2203 and2511 before choosing any configuration-semantics correction.
