# Algorithm branch maintenance policy

Scope: the current tree of the algorithm branch. All new documentation must be English.

- Keep this branch specification-only except the user-designated RAW test fixtures under raw/ (Git LFS payloads/pointers). Permit Markdown, JSON, CSV and text metadata or verification evidence; never add production code, executable implementations, test scripts, binary archives, dependencies, application assets, CI/build workflows, or embedded exact-source appendices.
- Use language-neutral pseudocode, explicit formulas, decision tables, state transitions, diagrams, input/output contracts and test vectors instead of copied implementation bodies. Interface identifiers, source locations, hashes and declaration metadata are allowed in Audit for traceability, not as implementation dependencies.
- Maintain distinct actual behavior, intended behavior and unresolved gaps. Never invent a trading rule, silently change a comparison, round a price, or claim a test passed without evidence.
- Preserve exact Decimal representation, strict versus inclusive comparisons, RAW and main-candle chronology, event priorities, source identities, ownership, numbering and serialization.
- Active scope is source-only reverse engineering and language-neutral algorithm specification. Do not run RAW tests, load market dataset payloads, create a clean-room implementation, execute a differential/regression suite or benchmark as part of this source-only task. For applicable runtime tests when authorized, the mandatory permanent RAW test protocol below applies. Historical verification evidence remains historical; runtime equivalence is not asserted.
- Keep historical evidence immutable; new results must identify the baseline, candidate, scope, runtime and status. Distinguish specification coverage, execution coverage and observed equivalence.
- Do not change main or merge this documentation-only tree into main. Do not use a checkout of this branch as a production application.
- Before committing, inspect the entire staged tree, preserve user-designated raw/ fixtures, reject unapproved file types and embedded implementation snapshots, verify relative links and validate JSON/CSV metadata. A branch restructure is not a computational validation.

## V2.0 baseline selection

For algorithm extraction, the user explicitly assigns latest committed production source on main as the sole implementation authority. Re-resolve main at the start of each phase and pin the exact commit; compare changed production source and behavior-affecting configuration blobs before continuing. Historical Golden baselines and archived packages are evidence only; never promote a different source based on version labels or timestamps. Preserve separate actual/intended semantics and disclose unavailable canonical authority. See Audit/Phase_01/Source_Authority.md. Keep source and runnable tests out of this branch.

## Active user scope — 2026-11-26

The latest explicit user instruction supersedes prior runtime and RAW verification requirements for this task. Derive the algorithm descriptions exclusively from the current committed production source in main. Document RAW-handling logic where source implements it, without reading or testing market data. Preserve unresolved dynamic inputs and conditional behavior explicitly; exact runtime dispatch or feasibility is not a completion condition for source extraction. Completion requires complete source-derived semantic and traceability coverage, not execution evidence. See [active scope](Audit/Source_Only_Scope.md).

## Permanent user requirement — RAW indicator tests (2026-11-26)

Before any applicable indicator runtime test, regression, reconstruction verification or benchmark, read and follow [Mandatory RAW indicator verification protocol](Verification/RAW_Test_Protocol.md). Use every current native RAW file in [raw/](raw/) on algorithm, independently at 30s for BOTH Bullish and Bearish, exactly as QG Indicator with chart timeframe 30s, analysis following chart, All available data, From the first actual 30s candle through To the last actual 30s candle inclusive. Preserve native lower-timeframe evidence and exact prices. Do not truncate, sample, concatenate as a substitute, skip large files or claim PASS before each full required run completes. Materialize and verify actual Git LFS bytes, not pointers. Record the complete matrix and evidence. The current four files require eight independent full runs per tested implementation. This standing rule applies when relevant tests are authorized, and does not itself launch runtime testing or change the current source-only Phase 07 extraction scope. No production changes or merging algorithm into main.

## Permanent user reporting preference (2026-11-26)

At the end of each completed work session, provide a very brief user-facing progress report (Persian for this user). Include: number and range of checkpoints actually completed and published; previous and current measured progress for the active work package and current owner, with compact horizontal progress bars and all owner/batch statuses when available; a short summary of what was reviewed and what was added or corrected in the algorithm documentation; next checkpoint, commit link, and any blockers or limitations. Distinguish local source review from runtime validation. Use actual evidence counts, not estimates or invented completion percentages; do not treat W1 coverage as overall Phase 07 completion. Keep the detailed technical evidence in GitHub, not in a long chat report.

## Checkpoint cadence and verification (2026-11-26)

Target ten consecutive evidence-complete checkpoints per work session when feasible; never split or label incomplete work PASS merely to meet the count. End-of-session report must name each checkpoint number/title and its actual verification status, explicitly confirming PASS for completed scoped checkpoints only after evidence validation and publication. Disclose any incomplete checkpoint and next exact resume location. Phase, owner and runtime acceptance remain separate.

## Permanent visual progress reporting (2026-11-26)

The user prefers visual-first, compact Persian reports after every session, with minimal explanatory prose. Show the status of ALL earlier, current and later phases (phase completion only within its actual documented scope); separate overall current-phase acceptance status from measured W1 site-category coverage, and show W1/W2/W3/W4 and all batch statuses. Show previous/current percentages and change, actual completed checkpoint numbers/titles and verified PASS/INCOMPLETE status, preferably using horizontal progress bars, charts and tables. Do not invent an overall phase percentage when no weighted metric exists or a total checkpoint count when not defined. Include the short summary of documented additions/corrections, next exact resume point, commit and any limitations. Ten checkpoints per session remains the target; no forced PASS or runtime claims.
