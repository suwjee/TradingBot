# Independent baseline determinism review

Generated read-only evidence, reviewed on 2026-11-02. Scope: the two saved repeat pairs reported as FAIL, their original CLI stdout, the diagnosis and matrix scripts, and the current merge owner. This review does not rerun market calculation or profiles and changes only this report.

## Conclusion

**FAIL: the original before baseline is not deterministic under the required exact stable serialization contract.** Both failed pairs have exactly one structural difference: key insertion order in the aggregated same-direction `bridgeOutput` object. The original saved bytes differ. A complete independent traversal found no other object-key membership, type, value, numeric lexical, array-length, or array-order differences in either stored stable pair.

The earliest demonstrated divergent owner is `engine/bridge/trading_pipeline.py:3252-3255`: `merge_regime_outputs` builds `bridge_keys` as a set of strings, then uses its iteration order to construct a new dictionary. Hash-seed-dependent set order becomes JSON object-key order. This is a pre-existing aggregation/serialization determinism defect on the untouched Source, rather than evidence of a candidate-refactor regression or a different trading-price/event selection.

The distinction does not excuse the failure: stable mapping order is explicitly included in this task's equality contract. Neither unordered-map equality, fixed diagnostic hash seeds, sorted JSON, nor regenerated baseline output may promote these original runs to PASS. User scope excludes behavioral/public-contract fixes, so no ordering repair is made or recommended for silent inclusion in this refactor. The failed full before/determinism gate blocks production refactor edits under the current instructions. Profiles can supply diagnostic evidence but cannot establish acceptance against this failed exact baseline.

## Evidence read and independent checks

Read the complete `discovery/determinism-first-differences.json` and `scripts/diagnose_determinism.py`, the relevant matrix capture/comparison code at `scripts/matrix.py:34-52,98-136,151-173`, and current `merge_regime_outputs` at bridge lines 3234-3260. Read all four case metrics files and decompressed each failed pair's `run-01.stable.json.gz` / `run-02.stable.json.gz` directly. Source was not imported for this comparison.

The independent comparator was separate inline Python, using object-pair lists to preserve mapping order and detect duplicate keys, explicit recursive type/membership/value checks, sequential list comparison, and string wrappers for JSON floating-number lexemes. It traversed the complete stored stable trees rather than stopping at the first reported difference. No baseline file was rewritten. For each of the four runs, the saved stable bytes were independently reproduced exactly from original `run-XX.stdout.json` by removing only the top-level `timings` envelope and encoding with the existing stable format. Thus the reported failures are present in the actual saved CLI evidence and are not artifacts of a missing/corrupted stable file or a comparison that sorted keys.

| Case | Stable size per run | First differing byte, zero based | Compared nodes | Object/order differences | Other differences |
| --- | ---: | ---: | ---: | ---: | ---: |
| `usoil-month-30s-bearish` | 10,520,023 | 1,125,125 | 507,339 | 1 | 0 |
| `xau-sep28-30s-bullish` | 3,913,622 | 719,677 | 189,066 | 1 | 0 |

USOIL difference path: `$.directions.bearish.bridgeOutput`.

- Run 01 key order: `aZones, orderAudit, blueLines, stopAlls, reactions, resets, eZones, sZones`.
- Run 02 key order: `reactions, orderAudit, eZones, resets, sZones, blueLines, aZones, stopAlls`.
- Run 01 decompressed stable SHA-256: `b7e50fc7572a163f1fd39a367ba93a8a8dbb88a92cbe221d189c23c99b955051`.
- Run 02 decompressed stable SHA-256: `7fc640563b1b19d046f8518663556aeaafdcb1fb2e4f3bfebe19a3d54293e061`.

XAU difference path: `$.directions.bullish.bridgeOutput`.

- Run 01 key order: `resets, eZones, blueLines, stopAlls, orderAudit, sZones, aZones, reactions`.
- Run 02 key order: `blueLines, orderAudit, eZones, sZones, stopAlls, aZones, resets, reactions`.
- Run 01 decompressed stable SHA-256: `e19ec3311f9bbdc0217f0760871aac7d0233eb31d7c09094ea00fdcdf685b417`.
- Run 02 decompressed stable SHA-256: `c6c238045d90fc6510ab411f923013abbda3ef14a1acc69781a3a79b79063f6a`.

Both directions contain two `calculationSegments` in these failed cases. In both runs, each individual segment's `bridgeOutput` key order is the same canonical sequence: `reactions, resets, blueLines, aZones, sZones, eZones, stopAlls, orderAudit`. The aggregate dictionary alone has the differing order. All values nested under those aggregate keys, including full ordered lists, compare identically. This locates the first saved-state divergence at aggregate object construction rather than the per-segment calculations.

## Root-cause reproduction without production import

Independently parsed the live bridge AST, extracted only the exact `merge_regime_outputs` function at lines 3234-3260, and executed that function with two tiny, freshly constructed segment dictionaries. No production module or trading engine was imported. Four subprocesses used explicit diagnostic `PYTHONHASHSEED` values 0, 1, 2 and 3; no files were written by this probe.

The single-segment control retained the canonical eight-key `bridgeOutput` order for every seed. The two-segment aggregate produced four different key orders, matching the parent's recorded seed-probe evidence:

| Seed | First aggregate bridge key | Remaining keys, in order |
| --- | --- | --- |
| 0 | `orderAudit` | `blueLines, stopAlls, reactions, aZones, eZones, resets, sZones` |
| 1 | `resets` | `aZones, sZones, eZones, blueLines, reactions, orderAudit, stopAlls` |
| 2 | `aZones` | `reactions, eZones, orderAudit, blueLines, stopAlls, resets, sZones` |
| 3 | `reactions` | `resets, blueLines, orderAudit, sZones, stopAlls, eZones, aZones` |

The earlier set at bridge lines 3246-3249 enumerates aggregate array fields. In these observed cases those keys already exist in `dict(segments[-1])`, so overwriting their values does not change their insertion positions. By contrast lines 3253-3255 create a new `bridgeOutput` mapping directly from the randomized set. The single-segment early return at 3241-3243 bypasses this reconstruction entirely. Other shapes with absent last-segment fields were not exhaustively tested, so this review does not certify that the observed aggregate bridge mapping is the only possible nondeterministic output in all inputs.

## Source integrity and scope limits

Independently rehashed all 14 production paths in `discovery/source-manifest-before.json`; every live hash still matches the initial pre-edit capture. `git diff --numstat -- engine` is empty, and current Git status shows only the task evidence directory as untracked. No production, test, accepted Reference, Vault, RAW or baseline artifact was changed by this review. This report is the only new file written for the follow-up.

Both repeat-02 metrics records correctly retain FAIL with exit code 0 and unequal stable bytes. Successful CLI completion and run-01 self-comparison/capture do not establish repeat determinism. The diagnosis script's unordered-key traversal is useful for classifying every difference; it explicitly does not grant PASS. The independent check confirms that classification without changing the gate.

This establishes bounded serialized-content equivalence apart from mapping order for these two saved pairs. It does not independently certify internal trading-state equality, global market correctness, every other scenario, profile validity, or future hash-seed behavior. No expensive calculation, benchmark, full suite, baseline recapture or candidate implementation ran here.

| Check | Result |
| --- | --- |
| Saved evidence readable and stable files match original stdout minus only explicit timings | PASS |
| Complete independent non-order comparison of both failed stable pairs | PASS: zero non-order differences |
| Independent tiny extracted-function reproduction of seed-dependent merge order | PASS |
| All initial production Source hashes unchanged | PASS |
| Original exact stable repeat determinism | FAIL |
| Candidate zero-difference equivalence / performance acceptance | NOT RUN; before gate failed |

**ZERO-DIFFERENCE REFACTOR NOT VERIFIED.** Preserve the failing evidence and current scope; do not repair ordering, weaken equality, pin a new acceptance environment, or sort/replace the baseline to report PASS.
