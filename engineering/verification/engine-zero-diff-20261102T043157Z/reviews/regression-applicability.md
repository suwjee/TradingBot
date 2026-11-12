# Current RAW regression helper applicability

Read-only assessment while candidate measurements run. No workload, test, helper invocation or production/Reference/Vault edit occurred. Only this report was written. All execution outcomes discussed below are applicability decisions or earlier documented evidence, not new PASS results.

The actual primary helper discovered live is `engine/tests/regression/verify_pl_ph_raw.py` (184 lines), not `engine/tests/verification/verify_pl_ph_raw.py`. The Order_B helper is `engine/tests/verification/verify_order_b_raw.py` (122 lines). Both were read completely for this assessment. The Source/Reference line citations below address the current live files after Reference regeneration; earlier reports have earlier prose line offsets.

## Smallest recommended invocation set

After benchmarks finish, run two existing primary-helper invocations against **unaltered final saved full-stream JSON**:

```text
python -B engine/tests/regression/verify_pl_ph_raw.py --after <final-phase>/xau-sep28-30s-bearish/run-01.stdout.json --xauusd-user-example --formed-mbls
python -B engine/tests/regression/verify_pl_ph_raw.py --after <final-phase>/usoil-month-30s-bearish/run-01.stdout.json --usoil-user-example --formed-mbls
```

`<final-phase>` is the parent's completed candidate evidence directory, not a new pipeline calculation. The selected original commands were confirmed from repaired-before metrics: both are primary-enabled, StopAll-enabled, complete original RAW input at30s, from the full dataset start through its end. These two invocations cover active bounded XAUUSD/USOIL anchors, source versus confirmation, conceptual/native Order direction, accepted parent-stop identity, the USOIL older-First joint confirmation, current400-candle MBL cap and bearish formed-MBL provenance. They do **not** establish every current reversal/regime invariant or independent bullish market correctness; exact all-scenario before/after comparison and the existing directional/regime tests remain distinct evidence.

For an unchanged Order_B helper invocation that avoids the known coarse-timeframe conflict, the existing two real5s legacy cases are the smallest useful directional subset **provided a read-only preflight confirms selected RAW events are aligned to5s calculation-candle opens**:

```text
python -B engine/tests/verification/verify_order_b_raw.py --raw "apps/chart/state/data/RAW/FXCM/USOIL/RAW FXCM_USOIL 5S FROM 2026-10-22 19-25-25 TO 2026-10-23 19-25-25.json" --payload <final-phase>/usoil-oct22-5s-bearish-legacy-no-primary/run-01.stdout.json --timeframe 5
python -B engine/tests/verification/verify_order_b_raw.py --raw "apps/chart/state/data/RAW/FXCM/USOIL/RAW FXCM_USOIL 5S FROM 2026-10-22 19-25-25 TO 2026-10-23 19-25-25.json" --payload <final-phase>/usoil-oct22-5s-bullish-legacy-no-primary/run-01.stdout.json --timeframe 5
```

Both case names/input paths/timeframe5/primary-disabled/full input bounds are verified from repaired-before metrics, with RAW SHA-256 `70da6116bb79d04f26bea45057de993c9f77504f7af8f326c8428e778d5e9cbf`. Actual row alignment and helper success were **not** checked during this no-execution review. Do not infer alignment solely from the filename. When every lower event is itself a calculation-candle open, accepted `FirstIndex >= break-main-index` implies `FirstTime >= strictBreakTime`; the stale extra exact-time restriction then excludes no same-candle case in that bounded chronology. Require complete public Reset witnesses and record returned per-direction cause counts. A zero count is vacuous coverage, not proof that Order_B geometry was exercised; select another existing suitable saved case or report the limitation if needed.

If that precondition cannot be established, do not use this whole helper as an unrestricted current Order_B gate. Its30s invocation may still be run diagnostically on original/repaired-before/final payloads, but retain and classify any same-main-candle failure rather than repairing the output, rounding the break, pruning causes or weakening its assertions. No new market calculation is needed merely to discover the known conflict.

## Primary flags and bundled assertions

| Flag / function | Current applicability | Exact evidence |
| --- | --- | --- |
| `--xauusd-user-example` /15-32 | Active bounded acceptance on the exact full XAUUSD September28..October6 stream at30s, bearish initial direction, primary enabled. No global cycle/high count assumption. | Current Bearish Reference655-659 retains the same PH1/MBL/selected physical Order source and exact confirmation/stop. This is fixture verification only. |
| `--usoil-user-example` /35-65 | Active initial-regime anchor on the complete October USOIL stream at30s. Its older First, joint confirmation, parent-stop direction/type, PH-over-StopAll and MBL checks remain applicable even when later regimes are aggregated. | Reference651,663-667 and native gate definition550-555; primary gate implementation211-219 and NativePrimaryOrders531-568. |
| USOIL cap assertion64 | Active: source15:50:30 through19:10:30 is40030s candles in the bounded continuous interval. | Bridge45 sets400 and3076-3079 calculates actual-candle cap; active Reference637/775 says400. Reference665's100-candle16:40:30 example residue is internally stale, as disclosed previously; it must not override active400 or cause a test expectation edit. |
| `--formed-mbls` /127-138 | Active for full-stream primary-enabled payloads containing a bearish group and complete visible source/cycle/StopAll witnesses. Works across flat same-direction aggregates with distinct absolute indexes/IDs. Not a bullish formed-leg verifier and not appropriate to narrow presentation windows or primary-disabled outputs. | Primary181-195 requires the owning cycle's confirmed main point within horizon; Reference512-537,619-624,719-723 and773; Bridge3103-3117 serializes counts/joins. |
| `--before` /141-145 | The value-comparison loop142-144 can be used for matching primary-disabled legacy outputs, but the bundled145 assertion is obsolete for primary-enabled current output: it forbids bullish `primaryHighs`. It also ignores mapping key order, top-level metadata and extra after directions/keys, so it cannot replace the task's exact stable comparison. | Current Reference767 explicitly gives both directions primary arrays. Current bridge main/primary projection produces those fields for enabled bullish calculation. Use the parent's strict matrix comparator instead. |
| `--usoil-independent-cycles` /68-78 | Initial outgoing-regime assertions remain meaningful, but global `len(primaryCycles)==1` at75 is not a general current aggregate invariant. Distinct later bearish regimes may add qualified cycles. Apply only to an explicitly bounded first-regime acceptance payload whose scope independently warrants that count, not by trimming the final result to make it pass. | Reference759 repeats physically fresh reversals and773 concatenates same-direction list collections. Bridge3234-3259 aggregates every segment;3289-3290 stops each outgoing prefix's cycles. |
| `--usoil-ph-number-priority` /81-102 | Initial PH source/number anchors88-91 and final alias consistency remain active. Whole aggregate `len(highs)==3` at92 is not a current global invariant when a direction returns. Three is the terminal primary number per owner regime; it is not a universal total number of physical highs across all independent cycles/regimes. | Reference651 preserves the first three anchors;757-759/773 authorize subsequent fresh regimes. Final number reconciliation also preserves independent coincident roles and physical identities. |
| `--usoil-trend-reversal` /105-124 | Contains active first handoff/bootstrap anchors113-123, but bundles the preceding count restrictions and global assumptions: latest `activeDirection==bullish` at111; exactly one bullish transition at112; every bearish Reaction predates the first boundary at124. These are not general current whole-stream invariants after repeated reversals. | Reference769 defines activeDirection as latest published regime;773 aggregates repeated directions/transition lists. Bridge3295-3329 repeats transitions;3234-3259 concatenates same-direction collections. Existing `test_bullish_primary_serialization.py:74-88,99-135` explicitly covers repeated direction segments/fresh restarts. |

The flagged aggregate assumptions can still happen to hold for a particular saved dataset (for example if a later returning regime never confirms a new primary). That does not promote them into the current algorithm's general rules. This assessment does not claim that each excluded flag actually fails the current final payload; none was executed here. The current accepted reference supports initial anchors, not a universal end direction, universal one-transition count or universal whole-stream three-high total. Do not infer a production defect from a bundled older scope assumption.

`--formed-mbls` requires special scope care: its `highCount` is a presentation-selected count, not a complete temporal proof at every earlier requested window. Bridge3110 uses selected source points and Primary181-195 uses decision horizon. A valid retained leg can outlive a hidden pre-range source, so this helper is recommended only on the full-stream cases above. It also covers bearish legs only (helper129), despite current bullish primary being supported.

## Order_B assertion-by-assertion applicability

The whole Order_B helper has only `--raw`, `--payload` and `--timeframe`; no option disables its obsolete First-time restriction. There is no honest flag combination that turns it into a general current coarse-timeframe oracle.

| Helper lines | Status and limit |
| --- | --- |
|15-33 | RAW/main reconstruction assumes supplied chronological rows/adjacent duplicates and matching full input coordinate scope. `orjson.loads` then `Decimal(str(value))` does not preserve every original JSON float lexeme; it is not independent production lexical-Decimal boundary proof. The current production contract parses Decimal lexically. |
|50-55 | Active physical identity join and confirmation not before physical Break main candle. Source `register_order_b_reset_legs` preserves the exact physical pair and confirmation provenance; Bridge1624-1634 translates identity pairs and index fields for fresh regimes. |
|58-64 | Mixed necessary chronology plus an obsolete extra predicate: `postBehaviorStopTime < resetTime < strictBreakTime` is active, but `strictBreakTime <= order.firstTime` at62 wrongly excludes a canonical opposite First in the strict break's owning main candle. It also does not by itself assert the required strict confirmation-after-crossing when those exact times coincide. |
|65-71 | Optional historical `previousReaction*` chronology is guarded on field presence. Current production registered cause does not require these optional legacy fields; they must not be invented to satisfy the helper. |
|72-89 | Current reset identity/breakout and exact-or-reconstructed Reset event comparisons are relevant if that Reset is present in the saved public witness collection. A required pre-range/internal cause can lack a public witness; diagnose missing lookup before calling it a trading defect. Full source input and full presentation are the intended helper scope. |
|90-103 | Active frozen accepted-anchor through Reset-First closed range, directional LL/HH, earliest equal extreme source and source-time checks. This is useful independent bounded geometric evidence with the loader precision limitation above. |
|104-110 | Active first strict selected-RAW crossing after exact Reset (`bisect_right`). Same lexical/input-scope limitations apply. This does not check every accepted-A expiry or dominance/creator eligibility rule. |
|111-113 | Counts only actually visited reset-leg causes. Zero is a valid result but supplies no non-vacuous Order_B case evidence. |

The stale predicate is demonstrated directly, not inferred from a passing fixture. Current Order Source303-325 maps the exact RAW break to its main index and selects with `strict_break_index <= physical.first_idx` and `strict_break_time < confirmation`. Current Reference370-376 explicitly allows First in that same main candle even when its opening timestamp is earlier than the exact crossing. Existing `test_order_b_reset_leg.py:110-118` exercises First12:02:30 with break12:02:35 and later confirmation. The helper's62 predicate rejects that permitted case. O1 edits are confined to carried-query allocation and cannot create or justify this mismatch.

## Final gate treatment

Keep three categories separate:

1. Exact repaired-before versus final comparison across all current saved scenarios/repeats, including every stable mapping/array/type/value and the separately disclosed original ordering repair.
2. Active bounded current RAW anchors/invariants actually executed using applicable helper flags and unaltered saved payloads, plus current directional/unit/regime tests.
3. Pre-existing stale helper/Reference residues and unperformed independent correctness coverage. Record these transparently; do not change expectations, normalize final output or relabel a stale-helper failure as a new trading implementation defect without its first difference.

This review does not create an algorithm-fix authorization and does not certify global market correctness. If any actually applicable active assertion fails, compare the same assertion on the untouched original/repaired-before saved payload, find the first divergence and report whether it is pre-existing or candidate-introduced. Preserve FAIL/NOT RUN/INCOMPLETE honestly. A stale general helper does not override the accepted same-main-candle or repeated-regime contracts, and a finite helper PASS cannot certify all RAW histories.
