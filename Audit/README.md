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
