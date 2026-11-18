---
title: Engine assessment removal and zero-difference performance report
document_role: evidence
lifecycle: historical
owner: engine-refactor-20261117
created_at: 2026-11-18T09:55:29+03:30
last_modified_at: 2026-11-18T09:55:29+03:30
---

# Engine removal and performance report

The requested T/F assessment and trading-position extension has been removed. The separate implementation refactor preserves every tested remaining stable output, including Decimal strings, event chronology, physical identities, provenance, lifecycle, array order and mapping order. This is exact equivalence to the post-removal baseline for the executed cases; it is not a formal proof for every possible input or independent certification of unchanged trading rules.

## Completed scope

- Removed the standalone automatic bullish setup Engine, Bridge projection/execution and live setup state. The six retired fields are `setupVersion`, `setupPhase`, `positionSetups`, `stopAllAssessments`, `behaviorAssessments` and `setupReferenceBreaks`, including independent regimes.
- Removed automatic Chart T/F/Buy annotations, manual Long/Short tools, position geometry controls, and Manual Review verdict selection, bulk actions, storage integration and verdict export column. Native report data, category/date filters, Bridge detail, copy/download, Measure and unrelated drawings remain. Legacy retired drawings are omitted by scoped normalization; unrelated state is retained.
- Reviewed the live production Python closure and relevant runtime imports, current engineering procedures, both directional References and affected tests/consumers. Physical Order/OrderAudit, Reaction, Reset, Blue, A, S, E, StopAll and PL/PH/MBL formation remain native calculation owners. Ordinary Boolean validity/state flags remain.
- No RAW modification, staging, commit, push, tag, publication or Graphify execution occurred. The initial working tree was clean; work is uncommitted on `main` from HEAD `26a61a08328e71c478d73eb866b346df1b8e7fdd`.

## Implementation changes

| Owner | Change and preservation contract |
| --- | --- |
| Reaction | Reuse main-candle range indexes for longer extrema queries; reflected queries reuse the original opposite extreme and `copy_negate`. Earliest equal source, Decimal representation and live index release remain unchanged. |
| A | Reuse the existing lower range index instead of allocating/scanning a window. Inclusive exact endpoint and main-only fallback remain unchanged. |
| E | Reuse immutable directional sparse geometry within one chronology; index first physical S parents and maximum child decisions during enqueue. Native parent/child ownership and dynamic replacement remain unchanged. |
| Lifecycle | Replace repeated full-history S predecessor scans with ordered queries and repeated lifetime dominance scans with a sweep. Strict predecessor time, first equal winner, E-before-S ties and inclusive lifetimes remain unchanged. |
| OrderAudit | Index carried creation time, avoid invalidating it for later/equal parent provenance, and lazily merge accepted post-stop candidates. All causes remain in the authoritative ledger. New identity/earlier creation, reparent/revocation/rebuild invalidation and exact tie order remain protected. Conservative legacy paths retain demonstrated malformed-row exception behavior and Decimal flags. |

## Exact-equivalence evidence

- The original full USOIL bullish output versus the isolated feature-removal baseline differs only by the six retired annotation fields. The baseline retains the original native calculation source; only the removal-owned Bridge paths differ.
- Four complete RAW/request modes were each executed three times before and three times after optimization. All six stable serialized outputs within each mode are directly byte-identical after excluding only the top-level `timings` telemetry. The first optimized matrix sample was superseded by final-source review fixes; that candidate and its paired baseline were both actually rerun in immediate succession. Earlier sample summaries were retained separately rather than relabeled as final evidence.
- The 46 bounded option/timeframe/direction/hash-seed cases comprise 42 successful exact stable byte comparisons and four reproduced unchanged baseline failures. Successful cases cover 1/5/30/60-second calculation timeframes, both individual directions and combined output, presentation clipping, legacy projection, disabled primary/lifecycle options and process seed repeats. The bounded fixtures retain the original JSON price lexemes by exact byte-prefix slicing. The four disabled-behavior cases compare exception type/arguments, owning Engine call chain, Decimal flags and empty stdout exactly; they are not described as successful calculations.
- Targeted range, source-ownership, lifecycle, malformed-row, eager-error, identity replacement, reset, mirror and live-continuation tests pass. The separate E route comparator exercises 3,456 bounded scenarios; it compares frozen original E route code with current eager/lazy query behavior, not an independently reconstructed market algorithm.
- Bounded real-data live continuation also passes: two symbols, both initial directions, six successive horizons through 8,000 original rows and 6 repeats per variant. Seed and append timings are recorded separately in [live continuation results](live-variant-results.json); they are distinct from the full-file manual-calculation speed table.

## Performance

The table reports end-to-end fresh-process pipeline time at a 30-second calculation timeframe with the complete supplied 5-second RAW, primary/lifecycle behavior and Bridge Output enabled. An individual initial direction can require both native directions and later independent reversal regimes. The baseline already excludes the retired setup extension, so the ratios measure refactoring rather than feature-removal savings. Values are medians of three executions; no profiler was active during these measurements. [Environment](environment.json), [raw measurements and phases](performance-results.json), [source/input identities](source-input-manifest.json).

| RAW | Initial request direction | Baseline median (s) | Final median (s) | Wall speedup | CPU speedup |
| --- | --- | ---: | ---: | ---: | ---: |
| USOIL | bullish | 365.404 | 158.021 | 2.312x | 1.943x |
| USOIL | bearish | 384.234 | 205.312 | 1.871x | 1.832x |
| XAUUSD | bullish | 191.281 | 100.761 | 1.898x | 1.916x |
| XAUUSD | bearish | 740.036 | 204.425 | 3.620x | 2.978x |

The shared workstation showed runtime variation. The complete per-run wall/CPU durations remain in the linked measurements; the ratios apply to these recorded inputs and configuration, not every future dataset or computer.

### Short live continuations

These bounded updates take fractions of a second and do not reproduce the full-file workload. After the first three runs showed mixed wall-clock results, three additional runs recorded CPU time as well. All original runs remain included: 6 wall-time repeats and three instrumented CPU repeats per variant. A CPU ratio below 1 means slower in this sample. Initial [three-run evidence](live-variant-results-first-three.json) is retained separately. There is no claim that every short live update is faster.

| RAW | Direction | Seed median before / after (ms) | Five appends median before / after (ms) | Seed CPU ratio | Appends CPU ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| USOIL | bullish | 106.1 / 111.2 | 358.0 / 321.1 | 0.857x | 1.000x |
| USOIL | bearish | 143.9 / 133.2 | 398.0 / 388.7 | 1.250x | 1.182x |
| XAUUSD | bullish | 127.6 / 88.7 | 371.8 / 317.8 | 1.143x | 1.185x |
| XAUUSD | bearish | 96.9 / 134.0 | 324.2 / 318.5 | 0.750x | 1.167x |

## Peak memory

Windows process peak working set is measured separately from elapsed time. The optimization does not clip historical input or remove required calculation state.

| RAW | Initial request direction | Baseline median peak (MiB) | Final median peak (MiB) |
| --- | --- | ---: | ---: |
| USOIL | bullish | 1015.81 | 1003.15 |
| USOIL | bearish | 1250.68 | 1273.06 |
| XAUUSD | bullish | 876.43 | 887.13 |
| XAUUSD | bearish | 762.13 | 767.13 |

## Inputs

- `apps\chart\state\tmp\engine-refactor-20261117\inputs\USOIL-full.json`: 319,188 original rows; epoch range `1790879400..1793628195`; finest supplied positive step `5s`.
- `apps\chart\state\tmp\engine-refactor-20261117\inputs\XAUUSD-full.json`: 276,672 original rows; epoch range `1792965660..1794932740`; finest supplied positive step `5s`.

These are frozen copies inside ignored project-local scratch. The original acquired RAW was not rewritten. No finer supplied dataset was discovered for these selected spans. Input hashes and interval metadata are evidence, not trading-rule authority.

## Verification status

| Check | Status | Evidence |
| --- | --- | --- |
| Final Engine unit and contract suite | PASS | 507 tests; [log](engine-final.log) |
| Final Chart unit suite | PASS | 329 tests; [log](chart-final.log) |
| Build | PASS | [log](build-final.log); existing Vite large-chunk warning remains |
| Live worker restart/recovery integration | PASS | [log](live-recovery-final.log) |
| Full RAW exact equality and deterministic repeats | PASS | [summary](summary.log), [measurements](performance-results.json) |
| Bounded option/timeframe/process-seed equivalence | PASS | [46 results](variant-results.json): 42 successful outputs, four identical pre-existing errors |
| Simultaneously disabled Blue/A/S with PL/PH disabled | FAIL | Pre-existing in both baseline and final; see the limitation below |
| Bounded real-data live continuation and repeats | PASS | [results](live-variant-results.json), six horizons and 6 repeats per mode |
| E route adjudication comparison | PASS | [log](e-routes-final.log) |
| Directional exact-source Reference reconstruction | PASS | [log](references-final.log), both References reconstruct the live source byte-for-byte |
| Source/input snapshot isolation | PASS | [log](manifest-final.log) |
| Desktop/mobile Chart and Manual Review browser interaction | PASS | [contract audit](contracts-audit.md), [Chart screenshot](browser/chart-removal-desktop.png), [review screenshot](browser/manual-report-desktop.png) |
| Source review | PASS | [review report](final-code-review.md); requested reviewer-authored compatibility fixes are disclosed |
| Documentation integrity and final whitespace diff | PASS | [anti-drift](anti-drift-final.log), [diff](diff-final.log) |
| Independent correctness of all unchanged trading rules on arbitrary markets | NOT RUN | Outside behavior-preserving comparison; no universal market-correctness claim |

`ZERO-DIFFERENCE REFACTOR VERIFIED` for the executed post-removal behavior contract and stated scope.

## Operational and evidence limits

- The existing user server on port5173 retained old transformed modules because its watcher was disabled. Browser verification used a fresh isolated server, which was stopped afterward. Restart the ordinary workstation server and refresh/reapply the indicator to load the new code; no user acquisition/session process was stopped by this task.
- The existing `engine/engine.zip` remains an unchanged earlier archive. It is not current runtime source and was not used as authority or silently regenerated.
- The connected Vault is a separately pinned older, scoped snapshot. Its captured source/reference copies were not rebuilt. Current local References, live Source and this explicit user instruction govern this change; local synchronization is not a claim of completed external Vault synchronization.
- Review found and corrected private accepted-ledger error/ordering differences before final acceptance. Arbitrary adversarial private-helper objects were not exhaustively tested. No history clipping, float shortcut, fixture-specific production branch or parallel chronology execution was introduced.
- An existing optional-configuration defect remains: `--blue-lines disabled --a-zones disabled --s-zones disabled --pl-ph disabled` reaches an unconditional `full_s_detectors[direction]` lookup in `finalize_direction_visibility`, although the disabled behavior branch never populates that map. Both snapshots fail with the same directional `KeyError`, call chain, Decimal flags and empty stdout on both symbols/directions. The normal complete-indicator path passes. This defect was not introduced or repaired by the refactor; changing that baseline behavior would be a separate behavioral fix. [Initial finding](variants-initial-failure.log), [exact error/output comparisons](variant-results.json).

## Reproduction and artifacts

Preserved local snapshots are under `apps/chart/state/tmp/engine-refactor-20261117/`: `original`, `removed`, `optimized`, frozen `inputs`, exact outputs and profiles. [Task plan](implementation-plan.md), [stage audit](stage-audit.md), [removal/Bridge audit](contracts-audit.md), [source/input manifest](source-input-manifest.json), [checks](checks-complete.json).

Run the task scripts from the repository root. `run_matrix.py --runs 3` performs serial paired measurements, `summarize_results.py` validates saved exact repeats and computes representative ratios, and `verify_variants.py` checks the bounded request modes. `engine/tests/verification/verify_order_references.py` reconstructs both exact-source references. The task source bundle is generated from final live files; no old package is represented as current.
