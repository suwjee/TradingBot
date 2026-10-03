# Zero-difference Engine performance refactor — final summary

Scope: RAW inputs with filesystem size **< 10 MiB** only (user instruction).

## Eligible datasets used

| Dataset | Size | Role |
| --- | --- | --- |
| XAUUSD 30S 2026-09-28..29 | 0.13 MiB | smoke |
| XAUUSD 5S 2026-09-16..17 | 1.10 MiB | medium |
| USOIL 5S 2026-09-21..24 | 2.26 MiB | medium / Order-heavy |

## Excluded (>= 10 MiB)

- FARAZ XAUUSD 1S (48.4 MiB)
- USOIL 5S BaseLine / long (29.9 / 33.4 MiB)
- XAUUSD 5S long histories (27.6 / 14.3 MiB)
- XAUUSD 1S (12.6 MiB)

## Baseline → optimized (median wall, warmed)

| Dataset | Direction | Before | After | Δ | Stable digest |
| --- | --- | ---: | ---: | ---: | --- |
| xauusd-30s-smoke | bullish | 0.457s | 0.424s | -7.2% | 8326a59ae776… MATCH |
| xauusd-30s-smoke | bearish | 0.459s | 0.470s | ~0 | f0fcdae12033… MATCH |
| xauusd-5s-medium | bullish | 3.875s | 3.896s | ~0 | 925c4270fab8… MATCH |
| xauusd-5s-medium | bearish | 8.322s | 6.777s | **-18.6%** | 28f62b6030e1… MATCH |
| usoil-5s-medium | bullish | 21.081s | 19.314s | **-8.4%** | 39b447577354… MATCH |
| usoil-5s-medium | bearish | 52.231s | 36.856s | **-29.4%** | 56ed0ce828ac… MATCH |

Peak RSS (after): smoke ~32 MB, XAUUSD medium ~71 MB, USOIL medium ~167 MB.
Baseline peak RSS was not captured (NOT APPLICABLE).

## Hotspots addressed

1. E `_zone` → OrderAudit carried/post-stop O(n) scans per parent
2. Repeated direct-order geometry recomputation
3. `_extreme_between` linear candle scans (E)
4. A reaction time/confirmation getattr scans
5. `reaction_identity` / timestamp getattr flood

## Source changed

- `engine/pipeline/order_audit_engine.py` — created-time carried rows, post-stop cache, direct-order cache, selective invalidation
- `engine/pipeline/e_zone_detector.py` — extreme sparse table, times[] lookups, cache fields
- `engine/pipeline/a_zone_detector.py` — precomputed reaction first/break/confirm times
- `engine/pipeline/core_utils.py` — faster identity/as_decimal helpers

Semantics/serialization unchanged (stable digests equal).

## Verification

| Check | Status |
| --- | --- |
| Unit tests (23) | PASS |
| Stable JSON digests (all executed cases) | PASS |
| Order regression (smoke RAW) | PASS |
| Reference exact-source reconstruction (both) | PASS |
| RAW immutability | PASS |
| Large-RAW Engine execution | NOT APPLICABLE — excluded by <10 MiB rule |
| Full hpzr2 / all-RAW order suite | NOT RUN — would require >=10 MiB RAW |

## Scope limitation

RAW-based performance/regression execution was intentionally restricted to source files smaller than 10 MiB by current user instruction. Files >=10 MiB were not processed.

FINAL STATUS: ZERO-DIFFERENCE PERFORMANCE REFACTOR VERIFIED WITH <10 MIB DATASET SCOPE
