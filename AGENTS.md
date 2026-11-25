# Algorithm branch maintenance policy

Scope: the current tree of the algorithm branch. All new documentation must be English.

- Keep this branch documentation-only. Permit Markdown, JSON, CSV and text metadata or verification evidence; never add production code, executable implementations, test scripts, binary archives, dependencies, application assets, CI/build workflows, or embedded exact-source appendices.
- Use language-neutral pseudocode, explicit formulas, decision tables, state transitions, diagrams, input/output contracts and test vectors instead of copied implementation bodies. Interface identifiers, source locations, hashes and declaration metadata are allowed in Audit for traceability, not as implementation dependencies.
- Maintain distinct actual behavior, intended behavior and unresolved gaps. Never invent a trading rule, silently change a comparison, round a price, or claim a test passed without evidence.
- Preserve exact Decimal representation, strict versus inclusive comparisons, RAW and main-candle chronology, event priorities, source identities, ownership, numbering and serialization.
- Keep verification procedures and reports here. Execute tests against a separately obtained pinned baseline and independent candidate outside this branch. Store outcomes and reproducibility metadata here without storing source or RAW data.
- Keep historical evidence immutable; new results must identify the baseline, candidate, scope, runtime and status. Distinguish specification coverage, execution coverage and observed equivalence.
- Do not change main or merge this documentation-only tree into main. Do not use a checkout of this branch as a production application.
- Before committing, inspect the entire staged tree, reject unapproved file types and embedded implementation snapshots, verify relative links and validate JSON/CSV metadata. A branch restructure is not a computational validation.
