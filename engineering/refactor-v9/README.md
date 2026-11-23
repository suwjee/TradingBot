# V9 completion — refactor branch only

This path exists **only on branch `refactor`**. No algorithmic or production engine source modifications are authorized by this task. The correctness oracle is Git commit `01d54ecf0149ebd15de92798be18810b6e2eb791`; V8.1 is the previous performance reference, independent of the `refactor` branch HEAD.

## Ground rules
1. Never merge a later `main` engine or an unverified `refactor` engine into the Golden oracle.
2. Freeze and independently validate all 7 RAW SHA-256s, Golden ZIP, 15 Git blob SHA values, stable byte output and timing schema.
3. All profiling, semantic tracing, mutation tests, complexity reports and release metadata are **test-only**, in this directory or attached to the dedicated V9 Library folder. Never modify `engine/`, archived Golden, or RAW data for this phase.
4. A profiler run must be separate from unprofiled runtime benchmarks.
5. Internal call counts may differ between Original and V8.1 because of implementation optimization; compare semantically significant outcomes and event order, not call-count equality. Coverage holes must remain visible.
6. `TRACE_COVERAGE_PARTIAL` / `INCOMPLETE` is the correct status until every hard gate in the V9 request has been executed and passed. Never silently upgrade release status.

## Baseline reports already verified (previous V9 iteration)
- 7/7 full RAW native BOTH stable outputs matched.
- 4/4 synthetic 100k, 250k, 500k and 1M stable outputs matched.
- 7/7 final-output stage-boundary trace projections matched; these are **not** internal semantic event traces.
- Source snapshot, immutable Golden ZIP and input checksums verified.
- Full V9 TOOLING and VERIFICATION evidence ZIPs preserved at `/TradingBot/Versions/V9-2026-11-24/` in account Library.

## Continuation
Tools in `tooling/` instrument separate copies of Golden and V8.1; function-event tracing and AST loop counting have been smoke-tested against a complete 15,061-row USOIL RAW without output drift. Full in-process semantics and a statistical paired 1M benchmark remain separate mandatory release gates. Current status is **INCOMPLETE** pending full audit. See the separate V9 release report and JSON manifests, with unverified operations explicitly labeled.

Previous V9 audit was committed to `main` before the user requested isolation. That historical documentation is not modified; **all new refactor-related work and publication take place on `refactor`**.
