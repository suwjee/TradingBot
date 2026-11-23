# V9 completion tooling — branch `refactor`

**Release: `INCOMPLETE / TRACE_COVERAGE_PARTIAL` (NO-GO).** This is a test-only continuation. The branch `refactor` must not be confused with the immutable Golden correctness oracle; never replace either Golden or V8.1 with its HEAD for a parity comparison.

The implementation and auditor sources are under `engineering/refactor-v9/tooling/` and the historical V9 utilities are under `engineering/refactor-v9/legacy-v9-tooling/`. The complete current audit and status manifest live in this directory. Archive ZIPs are stored independently in account Library `/TradingBot/Versions/V9-2026-11-24/`; no RAW or production source is committed to GitHub by V9.

## Commands in the same verified local working layout

```
python engineering/refactor-v9/tooling/test_internal_trace.py /mnt/data/V9_continue/results/V9_INTERNAL_MUTATION_TESTS.json
python engineering/refactor-v9/tooling/build_instrumented.py --source /mnt/data/V9_work/v81/engine --out /mnt/data/V9_continue/metered_v81/engine
python engineering/refactor-v9/tooling/semantic_trace.py --engine-root /mnt/data/V9_work/v81/engine --raw '/mnt/data/RAW FXCM_USOIL 5S FROM 2026-10-22 19-25-25 TO 2026-10-23 19-25-25.json' --from-time 1792684525 --to-time 1792770925 --trace-out /mnt/data/V9_continue/results/example.jsonl.gz
python engineering/refactor-v9/tooling/paired_benchmark.py --bars 100000 --blocks 1 --out /mnt/data/V9_continue/results/abba100k
```

The AST meter creates a modified **copy** solely for test instrumentation. It records selected loop/sort/heap/cache sites; no instrumented copy is eligible for production, and profiled meter wall-time is not comparable with unprofiled wall-time. Scripts use the verified working layout from this particular V9 execution and must not be run against another root without updating those paths or isolating them in a fresh runtime.

## Verified vs unverified

- Frozen 7/7 native stable parity, 4/4 synthetic parity and 7/7 output-boundary snapshots were completed in the prior V9 work.
- The new in-process observer was run on two complete short RAWs (both source snapshots) and the native stable bytes remained unchanged. Scoped family-local outcome comparison passed, with known excluded method invocation differences and input drift shown in reports.
- 151 E rejection events per source were measured for the short USOIL RAW with a concrete native branch guard reason; this is **not** exhaustive E rejection reason coverage.
- 5/7 complete real RAW AST operation-meter runs passed. Two large RAW remain incomplete/not run.
- One 100k ABBA block (4 complete native runs) passed. A repeated 1M ABBA benchmark remains **NOT RUN**.
- `TOOLING VERIFIED` cannot be claimed until all full semantic trace, global chronology, full operation coverage, official regression and 1M paired performance gates pass.

No V9 runtime refactoring, source version bump or permanent baseline replacement has been performed.
