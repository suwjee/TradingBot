# Mandatory RAW indicator verification protocol

User decision: 2026-11-26. Status: **MANDATORY for applicable runtime verification; NOT RUN by this policy update.**

## Authority and scope

For every future applicable TradingBot RAW indicator calculation, regression, reconstruction comparison, or benchmark, the canonical real-market fixture source is the `raw/` directory on the `algorithm` branch ([GitHub directory](https://github.com/suwjee/TradingBot/tree/algorithm/raw)). This is a persistent user requirement, not a one-off test suggestion. Read this protocol before selecting test inputs. If working on another branch or external runner, obtain the canonical fixtures from algorithm without merging that branch into main. The committed production source selected for the test remains the implementation authority.

The active source-only algorithm extraction and Phase 07 static audit do not require runtime testing; this protocol specifies HOW to run applicable tests when they are requested or otherwise authorized. Do not launch runtime tests solely because fixtures exist. Historical results keep their original datasets and scope; they cannot substitute for new required coverage.

## Mandatory test matrix and UI-equivalent settings

For each RAW JSON fixture currently in the canonical directory, run two independent complete indicator calculations: one with initial trend Bullish and one with initial trend Bearish. The current four fixtures therefore require at least eight complete executions per tested implementation/configuration. For baseline/candidate equivalence, execute the same matrix on both versions using identical fixture bytes and settings. Enumerate the directory at the start of each campaign so new fixtures are included. Each file is a separate scenario; do not concatenate different files or symbols as a substitute for per-file coverage.

| Setting | Required value |
|---|---|
| Indicator | QG Indicator, On |
| Chart timeframe | 30 seconds (30s) |
| Analysis timeframe | Follow chart timeframe, resolving to exactly 30s |
| RAW source granularity | Original native 5s for current fixtures; retain lower-timeframe evidence |
| Trend Required | Bullish, then independently Bearish (fresh state for each direction) |
| From | First actual aggregated 30s candle of that file |
| To | Last actual aggregated 30s candle of that file, included |
| Range | All available data; not Visible chart or a selected subset |
| Foundation settings visible in reference UI | Reaction, Blue Line, A, S and E On; E stop line Off in the reference presentation |
| Other options | Use the corresponding native indicator settings for the requested test; record all effective options, do not silently disable computational stages |

The two reference screenshots show the same configuration with opposite Trend Required selections. Use their settings, not their example symbol or date strings, as the rule for each input file. The full-file first/last 30s candle timestamps are derived from the actual native aggregation, not guessed from filename bounds, chart viewport, or screenshots.

Use the native RAW parser and aggregation contract ([RAW aggregation](../Algorithms/V3/21_RAW_Aggregation_Contract.md)). Keep original 5s lower-timeframe data; do not pre-reduce inputs to 30s OHLC and lose exact intrabar event evidence. Use native time alignment, timestamp conversion, Decimal price representation, gap treatment and last-candle/closed-horizon behavior. Do not round, fabricate candles, trim a warm-up prefix, exclude the final candle, or stop on the first signal. Select the full native main-candle range from index 0 through N-1 inclusive (N is the actual count for that file), ensuring the underlying API's inclusive/exclusive range conversion includes the entire final available bucket. No synthetic closure or future prices. Trend Required is an initial configuration, not permission to suppress native reversal or lifecycle behavior.

Run the same calculation path as applying QG Indicator on the chart with the above settings. A headless/CLI runner is acceptable only if it invokes equivalent native input preparation, full range and indicator configuration; record the mapping. Use independent fresh per-file/per-direction calculation state, not a continuation from the previous run.

## Fixtures observed in the user-designated directory

At algorithm commit `5ab988d209ec209763f2c3519ee35318862c13db`, GitHub reports four Git LFS pointers. The table records their declared object SHA-256 and payload size, not a claim that the payload bytes were downloaded or tested.

| File (relative to raw/) | LFS SHA-256 | Declared bytes |
|---|---|---:|
| `RAW FOREXCOM_XAUUSD 5S FROM 2026-06-24 14-50-00 TO 2026-08-01 00-00-00.json` | `d199dce40a744d237875f6b7aae5cdfe0849b0b5591f49512dd1a9b394c3c861` | 36727178 |
| `RAW FOREXCOM_XAUUSD 5S FROM 2026-08-01 00-00-00 TO 2026-11-26 07-25-55.json` | `cfce51004d63eeab02d9ce2acf90422d50d8262bba305f98a461d47534086e43` | 112048237 |
| `RAW FXCM_USOIL 5S FROM 2026-06-24 14-50-00 TO 2026-08-01 00-00-00.json` | `a7a81ad073fe6b21377a0261be8b612f39a656550bf84c19f3c438fc91567536` | 29518196 |
| `RAW FXCM_USOIL 5S FROM 2026-08-01 00-00-00 TO 2026-11-26 07-21-05.json` | `20a9ed99cf78a97e3d1155432d6b40b00e93bb02d57fd85c9624cd6d8adfcf72` | 94901522 |

Materialize the actual Git LFS objects before any runtime test (for example using an authorized Git LFS checkout). Verify the retrieved payload size and SHA-256 against its pointer and record exact branch commit, path and hash. A pointer is not market JSON and must never be passed to the indicator. If a file is unavailable, report BLOCKED/INCOMPLETE, not PASS; never silently substitute a smaller or older dataset. Additional synthetic/edge tests may supplement this mandatory matrix, not replace it.

## Completion and evidence

- Run each required case through the last available 30s candle; no sampling, time-range shortening, early termination, or skipping large files. If execution is interrupted, retain evidence and mark the case INCOMPLETE; resume/re-run until completed.
- Record fixture path, source commit and content SHA-256, raw row count, native lower/main counts, actual first and last main candle timestamps/indices, effective analysis timeframe, direction, effective indicator options, baseline/candidate commit, output artifact and completion status, elapsed time and any errors. Record actual processed range and confirm final main candle inclusion.
- For equivalence/refactor tests, compare complete stable indicator outputs, schemas, event ordering, exact price representations and Decimal precision without tolerance or rounding; report timing/benchmark metrics separately. Do not treat equivalent timing as equivalent output, or local static PASS as runtime PASS.
- A matrix is complete only after every required fixture-direction case finishes and applicable comparison/acceptance checks pass. Record failures and blockers explicitly. Do not claim successful tests on the basis of this policy or the mere existence of fixture files.

This protocol remains effective for future applicable tests unless the user explicitly changes it.
