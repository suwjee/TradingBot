# Local-only verification

All test-only code lives under ignored `/tests/`. These files are preserved locally and deliberately excluded from GitHub. A fresh clone needs the local test bundle before running test commands.

| Path | Purpose |
| --- | --- |
| `tests/chart/unit/` | Node chart/server contracts and external storage tests |
| `tests/engine/unit/` | Python Order/lifecycle contracts |
| `tests/engine/helpers/` | Exact reference and serialized RAW provenance checks |
| `tests/engine/regression/` | Selected-RAW runners and saved-result comparison |
| `tests/engine/benchmarks/` | Synthetic input generation and benchmark scripts |

```powershell
# From apps/chart
npm.cmd ci
npm.cmd test
npm.cmd run build

# From the repository root
python -B -m pytest -q -p no:cacheprovider tests/engine/unit
python -B tests/engine/helpers/verify_order_references.py
python -B tests/engine/regression/order_regression.py --help
```

The selected-RAW runner reads external `TRADINGBOT_LOCAL_STATE_ROOT/data/raw/` and requires an explicit output directory. Keep outputs external. Historical HPZR2 saved-evidence tools retain their original source-snapshot expectations and point at external archives; their results are not current Engine regression proof.

Algorithm correctness, source-direction regression, mirror parity, and independent real-data validation need separate scoped evidence. AST/import checks and storage tests establish structural integrity only.
