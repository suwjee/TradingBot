# V3 — State machines and lifecycle

This is the active Phase 06 companion to the [module algorithm registry](../README.md), [shared foundations](../../../Specification/README.md), and [declared records](../../../Contracts/Declared_Record_Schemas.md). All state models describe existing behavior; none introduces a new Engine state or trading rule.

## Registry

| Contract | Models | Transition rows |
|---|---|---:|
| [Reaction and Reset](01_Reaction_Reset.md) | RXI, RXU, RXS, RXG, RXV | 50 |
| [Blue and A](02_Blue_A.md) | BLS, BLQ, AP, AD | 40 |
| [S Zone](03_S_Zone.md) | SOW, SRT, SOR, SR | 32 |
| [Order ledger and creation](04_Order_Ledger.md) | OAS, OAP, OB, OLR, OLC | 52 |
| [E, Lifecycle and StopAll](05_E_Lifecycle_StopAll.md) | ER, EC, EQ, EF, LC, SA | 76 |
| [Primary and reversal](06_Primary_Reversal.md) | MB, PP, PG, PO, TR | 49 |
| [Continuation and transport](07_Continuation.md) | LX, LT, IX, RC, CV, EV, LV | 75 |
| [Pipeline, projection and T/F](08_Pipeline_Projection_TF.md) | BF, OF, PJ, TFC, TFB, TFS | 61 |
| [Shared services and adapters](09_Shared_Services.md) | CI, MC, RD, PR, ES, LS, IO | 57 |
| Total | 49 models | 492 |

## Interpretation and acceptance

Each machine is an extended-state description: control labels plus the registers, ordered guards, state updates, emitted records and resulting control label. A table row can encode a conditional substep, or a family of guards with alternative destinations. Labels such as INIT/RETURN/READY are explanatory unless explicitly identified as a native label. Native mode A/B and SCANNING/WAITING in the standalone Reaction detector and seek/PH/PL in the primary prospect are distinguished from analytical stages. Registers include candidate geometry and provenance, active/accepted identity sets, ownership windows, cause maps, pending proposals and retained checkpoints; these are not collapsed to a single Boolean or enum.

Interpret rows within the specific operation/decision stage. Some rows perform subsequent actions on the same input before the next traversal step (e.g., improve a pending strike, then check color; filter eligible E, then rank). Do not treat every row as a separate market event, or use all table rows as a globally ordered event queue. Read the owning module's exact procedure when a guard refers to it. A RETURN state returns the method's applicable result, not necessarily the end of the whole calculation. A null record is not a synthetic stop or confirmation. Exceptional paths propagate unless an explicit guard catches them. Runtime dispatch and arbitrary external callbacks remain conditional.

## Ownership and lifecycle invariants

| Dimension | Authoritative boundary |
|---|---|
| Geometry | Native Reaction and its exact prefix refinement; public geometry is a separate clone |
| Pending vs confirmed | No confirmed output until strict gate accepted; live cursor may retain pending work |
| Formation vs invalidation | A mode-A candidate invalidation is not a confirmed Reaction Reset; S windows may remain open without S |
| Physical Order vs cause | Same physical First/Break within direction; independent parent-stop and reset-leg causes; consumption never creates cause by itself |
| Eligibility vs visibility | Provisional calculation evidence, accepted identity and final display are separate; historical referenced records may survive display reconciliation |
| E ownership | Active parents and source-group arbitration; reopened native race when sole creation cause disowned |
| Sequence owner vs active StopAll | Exact S/E key, count and latest versus separate active StopAll tuple and frozen pending stop |
| Logical vs physical primary | Independent cycle checkpoint/proposal versus globally committed point, physical projection and numbering |
| Regime | Exact confirmed Primary3 break, independent prefix validation and fresh advancing suffix |
| Live | Active input transaction and full replay; optional per-stage checkpoints are separate interfaces |
| T/F | Final row annotation only, no geometric or lifecycle mutation |

## Critical precedence cross-check

This is a compact index of the source-checked race rules, not a complete Phase 07 chronology contract.

| Race | Rule | Transition reference |
|---|---|---|
| Standalone mode-A invalidation or confirmed Reset vs confirmation | Outward wins equal lower position; with both main predicates and neither lower proof, invalidation/Reset wins; only confirmed crossing can defeat missing outward proof | RXI02–05, RXU06 |
| Unified bounded structural reset search | Earlier incomplete First may be skipped, earlier invalidation blocks through its main; preserve earliest unresolved replay boundary | RXS04–07, RC07 |
| Independent Order geometry gate | Outward restart wins exact lower-position tie | RXG06–07 |
| Ordinary A two stops | Equal exact stops may directly trigger; ordinary search expiry exclusive, stop guard allows equality | AP08–10 |
| Type3 vs Type4 | Earlier exact decision; Type3 on equality | SRT04–05 |
| S Order vs eligible candidate | Same lower position returns null; main-only fallback both main predicates returns null even before qualification | SOR10–13 |
| E candidates | Earliest exact Order stop, later physical First; source family ownership priority then earlier decision/parent stop | ER04, EQ09 |
| StopAll | E donor stops active StopAll before considering armed owner; direct S Red armed Blue promotion before completed-stop route | SA06–13 |
| Primary | Reversal <= activation/decision wins; activation <= decision wins; point tie uses cycle index; ordinary same-event cancellation and winner ambiguous | PG04–07, PP03, PP11 |
| Order_B | Eight-pass convergence only for feedback; equal semantic signatures accepted, repeat unequal fails | OF04–08 |
| Live | Byte lineage commits only after successful normalized-input transaction; mismatch recoverable only in specified worker branches | LT05–15, LX09 |
| T/F | First source owner priority primary/StopAll/E/S; StopAll repeated-prefix parity can revise earlier labels | TFC01, TFS05 |

## Scope boundary

All 576 prior named procedures have a role: 550 directly referenced by guarded transition rows, 26 explicitly classified as supporting operations. This is structural traceability of the state-model deliverables, not source-branch equivalence, a formal proof of reachability, mutual exclusion, totality or path feasibility. The full original site inventories, 491 anonymous scopes, exact temporal windows, and conditional bindings still require the later chronology, decision-table, direction, integration and forensic audits. The state models do not authorize RAW reads, engine execution, runtime testing, executable reconstruction or benchmark.

The counts above describe the current tables, not a re-certified v2.8.7 transition inventory. See [active rebaseline](../../../Audit/Phase_07/Rebaseline_v2_8_7.json).
