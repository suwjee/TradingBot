# Active scope decision — 2026-11-26

User instruction (English translation): RAW tests are not needed at all. Rewrite and reverse-engineer the algorithms only from the source code present in main.

Baseline at this decision: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Prior algorithm commit: `3da5425c0b38dbba8f46e810a437bcb1fac15651`.

## In scope

- Pin latest committed main at each phase. Read all production logic and behavior-affecting configuration relevant to the algorithm.
- Extract self-contained English specifications, language-neutral pseudocode, explicit formulas, input/output schemas, state transitions, ownership, dependencies, chronological boundaries, tie-breaking, exception/fallback paths, ordering, Decimal semantics, and Bullish/Bearish behavior.
- Document RAW ingestion, aggregation, and search semantics as implemented by source, not as a dataset experiment.
- Maintain source-to-spec traceability, record source-level conditional and dynamic behavior, distinguish what source establishes from what remains input-dependent.
- Verify documentation integrity and consistency against source without executing the trading algorithm.

## Out of scope

RAW dataset testing, full RAW backtests, execution-based branch coverage, independent executable candidate, differential regression, full-engine benchmark, and empirical claims of runtime equivalence. Do not infer runtime results from a static analysis.

## Precedence

This explicit instruction supersedes the runtime and RAW verification requirements in [the historical requested prompt](Requested_Prompt.md), Phase 01/02 historical reports, and earlier reconstruction protocol for the active task. Historical reports and their manifests are immutable. The prior structural inventory remains valid for its recorded pinned baseline; semantic specification coverage remains incomplete. No source or trading behavior is changed. The active branch remains documentation-only and English.
