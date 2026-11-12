---
title: Performance methods and limits
document_role: evidence
lifecycle: generated
owner: engine-zero-difference-audit
created_at: 2026-11-02T12:27:57+03:30
last_modified_at: 2026-11-02T12:31:27+03:30
---

# Performance methods and limits

The optimization baseline is immutable repaired-before, not the original nondeterministic serialization. All normal process measurements include startup/import/input loading/full calculation/encoding/stdout I/O; controller hashing and equality checks are outside the timed region. Process CPU comes from Windows100ns native counters. OS PeakWorkingSet is sampled every50ms; the final sampling gap may miss a last-moment peak. Every input file is consumed completely. No profiler or other deliberate audit workload runs concurrently with measurements.

| Scenario | BEFORE wall s | AFTER wall s | Wall delta | BEFORE/AFTER CPU s (delta) | BEFORE/AFTER peak MiB (delta) | Repetitions each |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| xau-oct26-30s-bullish | 9.876267 | 9.824490 | -0.52% | 9.484375 / 9.296875 (-1.98%) | 174.238 / 174.156 (-0.05%) | 5 |
| xau-oct26-30s-bearish | 6.482395 | 6.003732 | -7.38% | 6.265625 / 5.765625 (-7.98%) | 152.152 / 151.961 (-0.13%) | 5 |
| usoil-oct22-5s-bearish-legacy-no-primary | 3.483498 | 3.576881 | +2.68% | 3.328125 / 3.250000 (-2.35%) | 70.266 / 70.484 (+0.31%) | 5 |

The CSV contains all22 default-randomized cold scenarios,3 initial matched-seed paired scenarios,3 additional seed-and-bytecode-cache-controlled scenarios and3 warm cases, plus separate allocation observations. The displayed table uses the final cache-controlled pairs. Negative delta is a reduction. Median/min/max and actual repetition counts are retained. Cold means a fresh Python process, not a flushed OS file cache: controller pre-run hashing reads the complete input and Source before the clock, warming file pages equally. Native CPU counters are queried in100ns units but observed scheduling granularity matters on short cases. The default cold phases were collected at different times and show substantial device/power/background variability; large apparent month speedups are **not causal estimates**. The paired auxiliary sequences use seeds0..4 shared by each before/after pair and execution orderAB/BA/AB/BA/AB. The additional control applies the same empty PYTHONPYCACHEPREFIX only to each child, with -B preventing writes; the directory remains empty. This prevents asymmetric reading of existing bytecode in live versus frozen Source paths. No global setting or existing cache was changed. These controls are explicitly recorded and never replace or secretly pin the default-randomized determinism matrix. Source-root path normalization applies only to module paths for frozen-source comparison, not market parameters.

Warm mode loads engines/market once, discards one warmup, measures five fresh full pipeline/result constructions, and stops clocks before writing/comparing outputs. It does not measure OS peak memory and does not establish persistent cache safety. Profiles and tracemalloc are separate instrumented runs, never normal wall/CPU benchmarks. Their raw records are preserved under repaired-before/profile, after/profile, repaired-before/alloc and after/alloc.

The artificial dense-provenance native query probe demonstrates lower temporary Python allocation at the supported interpreter; it does not prove that10k simultaneous parent/B causes occur in markets or that full process RSS halves. See discovery/carried-allocation-before-after.json. The scratch asymptotic bound remains O(p+b); the reduction concerns simultaneous reference collections and generator work. No retained cache/index/state is added. No whole-market correctness or universal speedup claim follows from these finite datasets.
