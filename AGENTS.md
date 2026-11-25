# Algorithm branch maintenance policy

Scope: the current tree of the algorithm branch. All new documentation must be English.

- Keep this branch documentation-only. Permit Markdown, JSON, CSV and text metadata or verification evidence; never add production code, executable implementations, test scripts, binary archives, dependencies, application assets, CI/build workflows, or embedded exact-source appendices.
- Use language-neutral pseudocode, explicit formulas, decision tables, state transitions, diagrams, input/output contracts and test vectors instead of copied implementation bodies. Interface identifiers, source locations, hashes and declaration metadata are allowed in Audit for traceability, not as implementation dependencies.
- Maintain distinct actual behavior, intended behavior and unresolved gaps. Never invent a trading rule, silently change a comparison, round a price, or claim a test passed without evidence.
- Preserve exact Decimal representation, strict versus inclusive comparisons, RAW and main-candle chronology, event priorities, source identities, ownership, numbering and serialization.
- Active scope is source-only reverse engineering and language-neutral algorithm specification. Do not run RAW tests, load market datasets, create a clean-room implementation, execute a differential/regression suite or benchmark as part of this task. Historical verification evidence remains historical; runtime equivalence is not asserted.
- Keep historical evidence immutable; new results must identify the baseline, candidate, scope, runtime and status. Distinguish specification coverage, execution coverage and observed equivalence.
- Do not change main or merge this documentation-only tree into main. Do not use a checkout of this branch as a production application.
- Before committing, inspect the entire staged tree, reject unapproved file types and embedded implementation snapshots, verify relative links and validate JSON/CSV metadata. A branch restructure is not a computational validation.

## V2.0 baseline selection

For algorithm extraction, the user explicitly assigns latest committed production source on main as the sole implementation authority. Re-resolve main at the start of each phase and pin the exact commit; compare changed production source and behavior-affecting configuration blobs before continuing. Historical Golden baselines and archived packages are evidence only; never promote a different source based on version labels or timestamps. Preserve separate actual/intended semantics and disclose unavailable canonical authority. See Audit/Phase_01/Source_Authority.md. Keep source and runnable tests out of this branch.

## Active user scope — 2026-11-26

The latest explicit user instruction supersedes prior runtime and RAW verification requirements for this task. Derive the algorithm descriptions exclusively from the current committed production source in main. Document RAW-handling logic where source implements it, without reading or testing market data. Preserve unresolved dynamic inputs and conditional behavior explicitly; exact runtime dispatch or feasibility is not a completion condition for source extraction. Completion requires complete source-derived semantic and traceability coverage, not execution evidence. See [active scope](Audit/Source_Only_Scope.md).
