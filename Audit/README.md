# Audit and evidence

Audit contains metadata about the separate implementation baseline and recorded verification outcomes, not production source. For an independent implementer, exclude this directory from the clean-room export.

| File | Scope |
|---|---|
| [Final audit report](Final_Audit_Report.md) | Prior partial verification and gaps |
| [Source manifest](Source_Manifest.json) | Pinned baseline inventory and hashes |
| [Source-symbol inventory](Source_Symbol_Inventory.md) | Declaration metadata without assignment initializers or implementation bodies |
| [Source-to-algorithm matrix](Source_To_Algorithm_Matrix.csv) | Module-level traceability only |
| [Function coverage](Function_Coverage.json) | Incomplete |
| [Branch coverage](Branch_Coverage.json) | Not measured |
| [Verification report](Verification_Report.json) | Original isolated test evidence |
| [Migration synthetic retest](Migration_Synthetic_Retest.json) | Second isolated run |
| [Regression report](Regression_Report.json) | Outstanding full suite |
| [Benchmark report](Benchmark_Report.json) | Isolated RAW aggregation timings |
| [Ambiguities and conflicts](Ambiguities_And_Conflicts.md) | Outstanding gaps |
| [Reconstruction risks](Reconstruction_Risks.md) | Risks requiring validation |
| [Existing test inventory](Existing_Test_Inventory.md) | External baseline test names |
| [Requested requirements](Requested_Prompt.md) | English requirements |
| [Historical publication evidence](History/README.md) | Preserved prior-layout records |
| [Branch cleanup manifest](Branch_Cleanup_Manifest.json) | Current layout migration and scope |

The historical reports remain statements about the runs at their original commits. They must not be interpreted as fresh tests during cleanup. Source paths in the audit refer to the pinned baseline, not files present here.

## Current V2.0 audit checkpoint

Use [Phase 01](Phase_01/README.md) for current baseline evidence. [Source manifest](Phase_01/Source_Manifest.json), [completion report](Phase_01/Phase_01_Completion_Report.md), [test inventory](Phase_01/Test_Inventory.json), [RAW manifest](Phase_01/RAW_Manifest.json), [Golden evidence](Phase_01/Golden_Evidence.json) and [conflicts](Phase_01/Conflicts_Register.md) were created from fresh discovery. The earlier audit records are retained as historical evidence; they are not current baseline discovery authority.

## V2.0 Phase 02 — Deep Static Analysis

[Phase 02 analysis](Phase_02/README.md) is structurally verified against latest main at commit `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Complete AST inventories and conservative control/data-flow graphs are recorded; dynamic and semantic closure remains partial. Phase 03 must re-resolve main before using this evidence.


## Current V3.0 Phase 05 checkpoint

[Module-level algorithm extraction](Phase_05/README.md) is complete for composition and structural traceability, with [validation](Phase_05/Validation.json), [module mapping](Phase_05/Module_Traceability.json) and [dependency analysis](Phase_05/Dependency_Graph.json). This is not final semantic certification. See the [active module catalog](../Algorithms/V3/README.md).
