# V10 — Historical Range-Query & Indexing Engine Optimization

**Experimental preflight; NO_SAFE_INDEX_PROMOTED.** Owner authorized this phase entry after best-effort V9; V9 remains uncertified. Original oracle and frozen V8.1 unchanged. Never write to main/production.

[Original prompt](../../prompts/V10.md) (historical main-write instructions superseded), [inventory](reports/V10_HISTORICAL_QUERY_INVENTORY.csv), [invariants](reports/V10_QUERY_INVARIANTS.md), [randomized comparison](reports/V10_RANDOMIZED_EQUIVALENCE.json). 12500 isolated exact queries; no native integration or speed promotion. Run `PYTHONPATH=versions/V9/tooling python -B versions/V10/tooling/inventory_queries_v10.py --help`; `python -B versions/V10/tooling/v10_confirmation_query_probe.py --help`. Use pinned ignored local source copies. Actual branch frequency and cost are next; full RAW/synthetic/Live/trace and performance gates still required.

## Native query measurement — 2026-11-24

See [checkpoint](reports/V10_CHECKPOINT.md) and [native query meter](reports/V10_NATIVE_QUERY_METER.json). All seven complete frozen V8.1 RAW runs (791174 records), exact Golden stable bytes and telemetry schema PASS; Confirmation Index rejected (139794 direct calls, 41 branch entries, zero skipped rows). Carried row revalidation prototype has scoped 24000 operation parity with explicit notification; stale negative control forbids native integration until ownership proof. No V10 runtime patch or native speed promotion. V9 million cancelled without archive.
