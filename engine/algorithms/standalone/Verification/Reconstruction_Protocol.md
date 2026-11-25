# Reconstruction acceptance gate

1. Install exact pinned baseline externally; record runtime and SHA.
2. Independent implementer receives semantic specs and authorized fixtures only, not production source or audit source mapping.
3. Rebuild all models, APIs, state transitions, and both directions.
4. Run all RAW data, supported timeframes, directions, Batch/Live and flag combinations.
5. Compare exact Decimal representation, types, order, identity, ownership, time and schema. Exclude only documented nondeterministic diagnostics.
6. Diagnose each mismatch; repair specification gaps and repeat independently.
7. Run all project tests, new branch/edge tests and benchmark. Distinguish coverage of specification, executed branches, and observed equivalence. No complete PASS until evidence exists.
