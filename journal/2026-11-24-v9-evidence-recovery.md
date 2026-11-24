# 2026-11-24 — V9 evidence recovery and durable handoff

Parent reorganization commit: 7d27b461ea4dd016c1adee2a82ce0ce5f37d8c03. No main/production changes. This task restores exact reports from the previous completed local executions; it is not a new Engine run.

| RAW 5s candles | Original events | V8.1 events | Equal selected noninput positions | Unresolved input drifts | Stable Golden | Selected coverage |
|---:|---:|---:|---:|---:|---|---|
| 100000 | 165846 | 144240 | 38292 | 0 | PASS | INCOMPLETE |
| 250000 | 732321 | 625914 | 158893 | 0 | PASS | INCOMPLETE |

Observer-on wall times (Original/V8.1): 43.545786251 / 43.34532872 s and 181.768532097 / 168.628433695 s. Not native performance benchmarks or V9 speedup. Both pairs have 6 independently verified stage sidecars per variant; the full run manifests and profiles are in ../../refactor-v9/evidence/2026-11-24 (navigate from V9 README). The frozen case manifests pin RAW and 15 source module hashes per source. 250k is the largest recovered completed strict pair, not a proven host maximum. No 1M full selected trace or universal state proof. Exact original prompt preserved.

Strict comparator pytest re-run: 15 passed. Full Engine/Chart suites NOT RUN for this cleanup. Previous reported gates 13 PASS / 2 INCOMPLETE are historical, not all independently rerun. Keep NO-GO.

Store the new strict runner, gate, tests, updated coverage audit, frozen cases, and strict Golden helper. Older coverage audit is recoverable at 75bfd33e15a8eb56d5b832a4e0121f9a33cbd50f. The binary traces and full native outputs are not in Git; SHA256 inventories identify them for reproducibility. External long-term storage of these full artifacts is not verified. No RAW data or secrets added.

Next: repair full state representation and semantic mutator observation, attempt the full 1M pair or largest feasible full run, record all results, and verify all gates before V10.
