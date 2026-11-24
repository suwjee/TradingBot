# V9 prompt-clause audit — best-effort continuation (2026-11-24)

Authority: original V9 prompt and owner's later refactor-only directive. The owner now authorizes beginning V10 after best-effort V9; this is not a waiver of correctness or certification gates. Original oracle `01d54ecf0149ebd15de92798be18810b6e2eb791`; frozen V8.1 candidate unchanged.

| Requirement | Evidence | Status |
|---|---|---|
| V9.0 Freeze: pinned blob IDs, ZIP SHA/CRC/member checks, seven RAW and stable hashes | `freeze-recheck.json` (15 source blobs, 51 member digests, 7 RAW cases); GitHub pinned tree independently queried | PASS |
| Strict verifier mutation controls | `golden-mutations.json` 10 controls incl allowed telemetry-only change; no Golden edit | PASS scoped |
| Environment and separate native/profile allocation modes | `freeze-recheck.json`, `profile-15061.json`; actual Python/psutil/cgroup/CPU/GC, six whole invocations | PASS scoped; high-volume allocation matrix and rigorous instrumentation-overhead paired repeats not complete |
| V9.1 flow/state contract registry | Historical `V9_COMPLEXITY_MAP.md`, new AST inventory in V10 report; 14 query definitions, 26 name-matched callsites, 986 potential mutations; no dynamic alias/dispatch completeness assertion | INCOMPLETE |
| V9.2 all seven RAW selected native both-direction trace | Historical selected trace gate; fresh lifecycle matrix on all seven RAW, exact complete stable bytes and complete scoped event equality; first-divergence and integrity controls | PASS scoped |
| V9.2 native observer ON/OFF | Historical Golden; new lifecycle observed native outputs match authentic Golden and both native unprofiled on 15,061; no production code changed | PASS for tested scope |
| V9.2 lossless full semantic mutator coverage | OrderAudit boundary coverage prior five RAW; 97,930 archive re-audit now complete; new lifecycle entry/return, cache controlled method bodies, existing scoped Live; intra-function, cross-snapshot identity and remaining source/Live alias transitions not proven | INCOMPLETE |
| V9.2 full synthetic trace | Prior 500k pair and authenticated replay PASS execution; selected representation incomplete; prior 1M native stable output PASS, current 1M selected observer job not yet completed at last observation | INCOMPLETE |
| V9.3 profiling/complexity | Prior 7 real meter and synthetic 4x2 meter/ABBA reports; fresh 15k native/cProfile/alloc GC measurements; V10 query inventory with exact source line and current 15k profile counts | INCOMPLETE for complete allocation/cache/sort/scan counters per scale and robust profiling overhead repeats; no V9 product speedup claim |
| V9.4 cumulative regression and tooling | Prior routine 7/7 CI successful; 69 locally executed Delta/lifecycle tests, 10 actual Golden mutation controls, complete real Lifecycle matrices | PASS scoped; full semantic gate still INCOMPLETE |
| Deliverables | This continuation's tool-only and verification packages, member SHA/CRC and exact source input cases; historical V9 packages remain immutable; no runtime product source committed | Partial aggregate release evidence; no `TOOLING VERIFIED` final claim |

Do not infer full coverage from equal selected events or controlled method bodies. All native times in this continuation are observed with the stated instrument modes and possible concurrent local work; no paired speedup claim. `V10` is allowed to begin as experimental investigation only, with frozen V8.1 reference and unchanged V9 blockers. The V10 query probe does not replace the actual runtime path. No product/RAW/Golden modifications; only refactor writes.
