# Verification and acceptance

This directory is documentation only. The previous isolated test scripts and oracle helper are deliberately excluded from the current branch tree. Historical report evidence is retained unchanged. Verification must run in a separate environment using the pinned implementation baseline and an independent candidate.

## Procedures

- [Reconstruction protocol](Reconstruction_Protocol.md): isolate the candidate from original source.
- [Edge cases](Edge_Cases.md): minimum cases to cover.
- [Partial test specification](Partial_Test_Specification.md): scope of the previously executed checks.
- [Acceptance gates](Acceptance_Gates.md): outstanding full-engine requirements.
- [Historical verification report](../Audit/Verification_Report.json) and [migration retest](../Audit/Migration_Synthetic_Retest.json): observed results.
- [Benchmark evidence](../Audit/Benchmark_Report.json): isolated timings only.

The former runner and reference implementation can be recovered by an authorized verifier from the prior repository history if needed, outside this branch's checked-out tree; do not give the original source, oracle or audit mapping to a clean-room implementer. An independent implementation must not require those historical files. Re-run full RAW tests with all seven external datasets identified by digest, and preserve new reports separately. No test was executed as part of this tree cleanup.
