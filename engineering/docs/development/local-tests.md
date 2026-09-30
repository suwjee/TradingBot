# Component-local verification

All test-only code is local and Git-ignored. A fresh clone needs the local test bundle before running these commands.

| Path | Responsibility |
| --- | --- |
| `apps/chart/tests/unit/` | Chart, server, storage and filesystem access contracts |
| `engine/tests/unit/` | Order/lifecycle contracts |
| `engine/tests/verification/` | Exact source-reference reconstruction and RAW provenance checks |
| `engine/tests/regression/` | Selected-RAW runners and saved-result comparison |
| `engine/tests/benchmarks/` | Synthetic benchmark generation and execution |

```powershell
# From apps/chart
npm.cmd ci
npm.cmd test
npm.cmd run build

# From the repository root
python -B -m pytest -q -p no:cacheprovider -p no:benchmark engine/tests/unit
python -B engine/tests/verification/verify_order_references.py
python -B engine/tests/regression/order_regression.py --help
```

Current selected-RAW defaults use `apps/chart/state/data/raw/`; optional state overrides must remain inside the dedicated state subtree. Give runners an explicit output directory under `engineering/verification/`. Production-source inventories include only the root Engine package marker, bridge and pipeline; component tests are not production source or embedded-reference inventory.

HPZR2 tools preserve historical snapshot expectations and archived evidence. Their dated assertions are not current complete Engine proof. The regression comparer intentionally checks absolute RAW paths; comparisons across a relocation require an explicit reviewed input mapping while retaining all RAW hashes/rows/ranges/configuration checks.

Algorithm correctness, source regression, directional parity and independent real-data validation require separate scoped evidence. Storage/AST/import checks establish structural integrity. Full market regression is not required solely for a storage-only migration with byte-identical Engine and RAW; any Engine or chronological behavior change uses the operating protocol's full applicable gate.
