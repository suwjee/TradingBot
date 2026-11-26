# Verification and acceptance

Active scope: source-only reverse engineering, per the latest user instruction. This branch is specification-only except for user-designated Git LFS RAW fixtures. No RAW tests or runtime calculation verification are required or performed for the active task. Read [source-only scope](../Audit/Source_Only_Scope.md) and [active acceptance gates](Acceptance_Gates.md).

The following historical material remains available for traceability; it does not define active task requirements:

- [Reconstruction protocol](Reconstruction_Protocol.md)
- [Edge cases](Edge_Cases.md)
- [Partial test specification](Partial_Test_Specification.md)
- [Historical verification report](../Audit/Verification_Report.json) and [migration retest](../Audit/Migration_Synthetic_Retest.json)
- [Benchmark evidence](../Audit/Benchmark_Report.json)

Do not treat a source review as a proof of runtime equivalence. No tests are requested under the current source-only scope.

## Permanent RAW test standard

For every applicable authorized runtime test, follow [Mandatory RAW indicator verification protocol](RAW_Test_Protocol.md). The canonical fixtures are in [algorithm/raw](../raw/); each file requires complete independent Bullish and Bearish calculations at 30s, from the first actual main candle through the final actual main candle inclusive. The current four files require eight full runs per implementation. This is a standing requirement for relevant runtime verification, not a new execution claim or a change to the static scope.
