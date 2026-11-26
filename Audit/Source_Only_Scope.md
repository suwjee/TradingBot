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

This explicit instruction supersedes the runtime and RAW verification requirements in [the historical requested prompt](Requested_Prompt.md), Phase 01/02 historical reports, and earlier reconstruction protocol for the active task. Historical reports and their manifests are immutable. The prior structural inventory remains valid for its recorded pinned baseline; semantic specification coverage remains incomplete. No source or trading behavior is changed. The active branch remains English and specification-only, with the user-designated RAW fixture directory as a permitted data-only exception.

## Standing RAW test requirement (subsequent user instruction, 2026-11-26)

The user designates [algorithm/raw](../raw/) as the permanent canonical real-market test dataset directory. For any applicable authorized runtime test, follow [the mandatory RAW test protocol](../Verification/RAW_Test_Protocol.md): every file, native 30-second analysis, independent Bullish and Bearish runs, first through last actual 30-second candle inclusive. The source-only task remains static; no RAW payload is read or calculation executed solely to register this instruction. This distinguishes the method for future tests from the present static completion gates.
