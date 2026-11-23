# TradingBot — Golden 30-second BOTH-direction regression baseline

**Permanent correctness anchor:** `01d54ecf0149ebd15de92798be18810b6e2eb791` of [suwjee/TradingBot](https://github.com/suwjee/TradingBot/tree/01d54ecf0149ebd15de92798be18810b6e2eb791/engine). The existing Engine runtime code is **not modified** by this documentation commit.

## What is frozen

- **7 original 5-second RAW datasets (791,174 rows)**, bullish **and** bearish in a **single native `direction=both` call**, `timeframe=30`, `raw-timeframe=5`, all indicator stages enabled (Reaction, Blue Line, A/S/E, StopAll, PH/PL, OrderAudit, lifecycle, trends and bridge).
- [inputs.json](inputs.json): every filename, file SHA-256, first/last timestamp, row count, and expected byte-stable output SHA-256.
- [source_blobs.json](source_blobs.json): exact 15 original executable engine Git blob IDs.
- [golden_results.csv](golden_results.csv): historical baseline CPU / elapsed / RAM per file.
- [version_performance.csv](version_performance.csv): V7/V8.1/V8.2 time, CPU, RAM and zero-difference result, **all rows**.
- [version_history.json](version_history.json): step-by-step release changes, tests, rejected experiments and measured synthetic scaling.
- [ARTIFACTS.md](ARTIFACTS.md): exact ZIP names, checksums and account-Library archive locations.
- [ZERO_DIFFERENCE_CONTRACT.md](ZERO_DIFFERENCE_CONTRACT.md): mandatory acceptance rules.
- [verify_golden.py](verify_golden.py): executable fail-closed regression against the full immutable snapshot ZIP.
- [FUTURE_RELEASE_TEMPLATE.md](FUTURE_RELEASE_TEMPLATE.md): mandatory record for each additional optimization step.

## Status

| Release | Full RAW parity | Sum of seven wall times (seconds) | Promotion |
|---|---|---:|---|
| Frozen original | Reference | 139.116 | Frozen correctness only |
| V7 | 7/7 PASS | 118.648 | Experimental |
| V8.1 | 7/7 PASS | 109.770 | Experimental performance reference |
| V8.2 | 7/7 PASS | 110.518 | **NOT promoted**: unproven persistent speed benefit |

The output comparison is **byte-exact** after excluding *only numeric runtime measurements in final `timings`*; timing key names/value types are separately asserted. Every other field remains covered. Historical runs do **not** constitute mathematical proof of all hidden engine state, arbitrary callback behaviour or all possible Live cases.

## Verify an optimized version

The full original `*.stable.json` files and complete original output JSON files are preserved in the **GoldenBaseline ZIP in ChatGPT Library** (they are **not duplicated into this GitHub tree**). This repository stores their fingerprints and a verification program. Obtain the ZIP, place the seven unchanged RAWs locally, and run:

```sh
python engine/bridge/trading_pipeline.py --help  # optional CLI inspection
python engineering/verification/golden-baseline-30s-both/verify_golden.py \
  --baseline-zip /path/to/TradingBot_GitHubMain_Baseline_30s_Both_01d54ecf_20261123_v1.zip \
  --candidate-root /path/to/candidate/engine \
  --raw-dir /path/to/7-raw-files \
  --out-dir /path/to/new-verification
```

The runner verifies the ZIP digest, RAW SHA-256, complete both-direction output, stable byte order, timing schema and exact expected output SHA. It rejects missing, altered and unsupported inputs. **It never modifies the baseline**.

## Important boundaries

- The old 5-minute RAW was explicitly removed from the active verification suite by the owner. Do not interpolate it or reintroduce it.
- NEVER use a newer candidate as the correctness oracle: always compare directly against the **pinned GitHub commit and baseline snapshot**.
- Version-specific runtime code is delivered separately as ZIPs, not silently installed on `main`.
- Do not overwrite this frozen baseline. New datasets require an addendum and an explicit new baseline identity, never silently rewrite historical SHA values.
- Performance timings must be reported as observations, not guarantees; keep the order-alternated paired benchmark as a promotion gate.
