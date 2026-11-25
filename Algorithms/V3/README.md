# V3 — Module-level algorithm specification

This is the active module-level reading surface for the source-only specification. Read it with the shared [foundations](../../Specification/README.md) and [declared record interfaces](../../Contracts/Declared_Record_Schemas.md). All rules describe the observed implementation, not proposed trading improvements. The earlier files in the parent Algorithms directory are retained historical specifications; where they differ, this V3 composition is the active reading surface for Phase 05. Subsequent formal state, chronology, directional, integration and forensic reviews must reconcile any remaining discrepancies. No empirical equivalence or reconstruction certification is asserted.

## Reading order and procedure registry

| # | Algorithm | Unique procedure definitions | Prerequisite contracts |
|---:|---|---|---|
| 01 | [Reaction Engine](01_Reaction_Engine.md) | RE01–RE30, RE63–RE98 | 20, 21; Reset below |
| 02 | [Reset](02_Reset_Algorithm.md) | uses RE11–13, RE27–28, RE77, RE83–86, RE93–98, RE58–60 | 01, 20 |
| 03 | [Blue Line](03_Blue_Line.md) | BL01–BL18 | 01, 02, 20 |
| 04 | [A Zone](04_A_Zone.md) | A01–A39 | 01, 03, 20 |
| 05 | [S Zone](05_S_Zone.md) | S01–S50 | 01–04, 06, 20 |
| 06 | [Order A](06_Order_A.md) | OA14–24, OA40–43, OA75–82 | 01, 02, 08, 20 |
| 07 | [Order B](07_Order_B.md) | OA02–12, OA30 | 01, 02, 08, 10, 11, 17, 20 |
| 08 | [Order Audit](08_Order_Audit.md) | OA01, OA13, OA25–29, OA31–39, OA44–74 | 06, 07, 20 |
| 09 | [E Zone](09_E_Zone.md) | E01–E54 | 05–08, 10, 20 |
| 10 | [Lifecycle](10_Lifecycle.md) | LC01–05, LC25–46 | 04–09, 11, 20 |
| 11 | [StopAll](11_StopAll.md) | LC06–LC24 | 05, 09, 10, 20 |
| 12 | [Primary Structures](12_Primary_Structures.md) | P01–P46 | 08–11, 20 |
| 13 | [Primary High/Low roles](13_Primary_High.md) | uses P04–P14, P22–25, P36–43 | 12, 08 |
| 14 | [Matching Behavior Leg](14_Matching_Behavior_Leg.md) | uses P09, P15–21, TB84 | 10–12, 19 |
| 15 | [Trend Reversal](15_Trend_Reversal.md) | uses P02–06, TB63–65, TB90–96 | 12, 17, 19, 21 |
| 16 | [True/False](16_True_False.md) | uses TF01–TF07 | 10, 19, 20, 22 |
| 17 | [Trading Bridge](17_Trading_Bridge.md) | TB01–08, TB66–67, TB71–78, TB87–102 | all calculation and projection modules |
| 18 | [Live Bridge](18_Live_Bridge.md) | L01–L03, RE99–RE107 | 17, 20, 21, 23 |
| 19 | [Serialization](19_Serialization.md) | TB22–62, TB64–65, TB79–86 | 01–15, 17, 20 |
| 20 | [Indexes, chronology and caches](20_Indexes_And_Caching.md) | C01–06, D01–06, RE31–62 | normalized candle and Decimal contracts |
| 21 | [RAW aggregation](21_RAW_Aggregation_Contract.md) | TB09–21, TB63, TB68–70 | 20, 17 timestamp conventions |
| 22 | [True/False exact recurrence](22_True_False_Exact_Contract.md) | TF01–TF07 | 10, 16, 20 |
| 23 | [Live transport](23_Live_Transport_Contract.md) | L04–L13 | 18, 21 |

Procedure IDs are stable semantic labels, not required implementation symbols. Each of the 576 named operation descriptions appears once in this registry; cross-cutting documents (Reset, PH/PL, MBL, Reversal and T/F overview) compose or refer to the owning procedures rather than duplicate them. For common data types use the record catalog; for input-dependent results follow explicit guards and fallback rules. The module compositions and detailed procedure clauses together define the active Phase 05 deliverables.

## Calculation ownership and dependency flow

| Stage | Consumes | Owns / returns |
|---|---|---|
| Input normalization | RAW rows, timeframe, requested view | Full lower/main chronology, indexes, visible bounds |
| Native geometry | Market chronology, direction, initial trend flags | Canonical Reaction/Reset streams; published box clones and internal metadata separately |
| Blue | Native Reaction/Reset, chronology | All scale/reset lines; invalid/internal metadata |
| A | Native trend Reactions and all Blue | Frozen A source, Blue pair and trigger/confirmation provenance |
| S + initial Order_A | A, Blue, trend/opposite geometry and stops | Provisional S decisions, A ownership windows, initial physical audit |
| E + Order ledger | Accepted A causes, S, opposite geometry, Order_B evidence | Candidate chains, accepted E, canonical physical Order causes |
| Lifecycle/StopAll | Accepted and provisional A/S/E, stop finders | Accepted/invalid identities, restoration, dominant stop groups and sequence resets |
| Primary | Accepted full groups and native Order service | MBL, confirmed primary/secondary points, transition and native Order reparenting |
| Final projection | Accepted calculation objects, visible bounds, audit | Legacy arrays and optional nested Bridge Output, regime segments |
| T/F | Final selected public rows and bounded original lower search | Annotation keys only |
| Live transport | Exact append lineage and normalized prefix | Transactional input replay and response; not a new geometry algorithm |

Use a direction-specific physical Order identity (First, Break) distinct from logical ordinal, behavior source, cause key and public row identity. Source-level exact lower event and main-candle timestamp are separate. Do not feed public display suppression back into calculations except the explicit accepted-ownership gates in Lifecycle and bridge orchestration. Full-history calculation precedes visible source clipping.

## Directed feedback, not uncontrolled recursion

1. **Order_B ↔ E/Lifecycle.** Initial Reaction/Blue/A/S stages are shared. Calculate E from current reset legs, reconcile optional StopAll, restore independent roots and ledger; rediscover Order_B from accepted evidence. Stable signature returns the direction state; repeated non-equal signature or exceeding eight passes fails. Final visibility checks the converged signature again. This is the explicit eight-pass feedback, not a generic engine limit.
2. **E ↔ accepted Order provenance.** A candidate's only creation cause can become disowned S during source reconciliation. Reopen the complete native Order race for an eligible parent and enqueue valid regenerated candidates. Checkpoint reuse that reopens a race restarts reconciliation. Parent-active checks, source grouping, accepted identity and chain-specific duplicate detection are semantic gates, not a blanket retry cap.
3. **Primary ↔ ledger.** Primary commitment reassigns eligible exact StopAll parent causes to the native primary role, preserves independent causes, and refreshes native OrderAudit. Pending proposals are invalidated under the specified callback rule; exact reversal/activation/decision ordering is re-evaluated. No speculative point commitment.
4. **Reversal ↔ full pipeline.** A confirmed physical Primary3 strict crossing ends one independent regime. Recalculate its historical prefix and validate that same Primary3; new regime begins at the boundary candle with fresh geometry and its own bootstrap flag. Each reversal must advance; no carried historical trading state.
5. **Live transport ↔ replay.** Accepted input bytes advance lineage only after successful normalized input transaction and full replay. Retained views/indexes optimize input; standalone incremental stage services remain conditional, not automatically enabled in active worker.

Source imports and semantic data/feedback dependencies are different. The type-reference dependency from Order audit to E is guarded for static type checking; runtime E uses Order services. E may locally load the shared main range index for its optional live extent calculation. The primary serializer imports primary resolution locally; the configured bridge loader and callbacks remain conditional. Package initialization: top engine has no behavior; bridge package has only descriptive metadata; pipeline compatibility surface prepends its resolved directory only if absent and exposes BlueLine, ScaleStrike, count_scale_strikes, detect_blue_lines and fibonacci_level in that order. Normal bridge also prepends the pipeline directory only if absent. These package/loader rules must not change price semantics.

## Failure and precision invariants

- Preserve native Decimal operations, including direct-versus-string construction, exact sign-copy reflection, equality and earliest/latest ties; never introduce quantization or an unapproved finite-value filter.
- Keep lower-row strict tests, inclusive/exclusive time bounds, explicit fallback behavior and same-row ambiguity. Do not invent ordering within one RAW row.
- Preserve exact physical identity and independent creation provenance when consumer/visibility changes. Preserve nulls and conditional failures.
- All cache optimizations are defined per owner and depend on validated chronology, dirty frontier and key identity. Do not assume arbitrary mutation safety or universal incremental equivalence.
- This collection is an implementation-oriented module composition, not a formal proof of every branch or all-input runtime behavior. Formal state machines, full event-order crosswalk, executable-neutral decision tables, directional integration and forensic completeness are later phase deliverables. The active task excludes RAW, execution, differential reconstruction and benchmark.



## Phase 06 companion

Read the [state-machine and lifecycle registry](State_Machines/README.md) alongside the module contracts. It adds source-derived guarded transitions, register lifetimes, ownership and replay states without changing the existing source or historical Phase 05 module text.
