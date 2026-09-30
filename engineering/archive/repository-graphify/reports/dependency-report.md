# dependency-report.md

**created_at:** `2026-09-30T15:43:03+03:30`
**last_modified_at:** `2026-09-30T15:43:03+03:30`

## Import edges (internal)

Count of internal import edges: 141

## External package edges

Count of external/npm edges: 279

## Hotspots

- `apps/chart/server/raw-resource-store.js` (35)
- `apps/chart/src/main.js` (33)
- `engineering/docs/architecture/technical-architecture.md` (24)
- `engineering/docs/architecture/ui-ux-reference.md` (23)
- `engineering/docs/documentation-governance.md` (23)
- `apps/chart/tests/unit/raw-resource-store.test.mjs` (22)
- `engineering/docs/ai/engineering-workflow.md` (19)
- `engineering/docs/development/testing.md` (19)
- `AGENTS.md` (18)
- `engine/tests/unit/test_order_audit_lifecycle_contracts.py` (17)
- `engineering/docs/development/zero-difference-refactor.md` (17)
- `engineering/docs/README.md` (17)
- `engine/bridge/trading_pipeline.py` (16)
- `engine/pipeline/order_audit_engine.py` (16)
- `engine/tests/regression/order_regression.py` (15)

## Cycles

- none detected

## Notes

Engine tests use flat imports against `engine/pipeline` modules (runner `sys.path`).
Chart tests use relative imports under `apps/chart`.
