# Phase 01 — Frozen implementation baseline

| Item | Value |
|---|---|
| Repository | suwjee/TradingBot |
| Authoritative branch | main |
| Commit | 466eb875070f02cd0dbfb105033422bbe2fd8c70 |
| Committer timestamp (UTC) | 2026-11-23T22:17:08Z |
| Root tree | 7264d58a7ec20ed66dc4520c19d935d29a6f55c1 |
| Engine tree | 3908c2bb697bd7f5ebb8ce2cf8298b7f46bfdfd5 |
| Discovery date | 2026-11-26 |
| Scope | All tracked engine files; full repository tree for ownership, test and evidence discovery |
| Algorithm branch | Documentation only; do not merge into main |

## Inventory

All 64 tracked Engine blobs were fetched directly from the pinned main commit or exact pinned reference blob, with byte lengths and Git blob IDs checked and SHA-256 calculated. Of these: 13 operational Python modules, 3 package markers, 3 current references, 1 presentation stylesheet, 35 unit test files, 5 regression tools, 2 benchmark tools, 2 verification tools. The 16 production/package Python files contain 17,119 lines, 576 lexical function declarations and 85 lexical class declarations. These lexical counts are Phase 02 inputs, not measured semantic coverage. The full root tree contains 1,414 tracked blobs and was not truncated.

## Dependency boundary

The current Engine owns trading computation. Bridge and Pipeline are the algorithm extraction scope. Chart owns presentation; Vite/local server owns orchestration and transport; FARAZ owns acquisition. The engine CSS is a presentation file, not an algorithm. Relevant downstream and transport paths, test roots and configurations are inventoried separately, not treated as new trading calculation authority. Exact dependency closure and full call/data-flow analysis belong to Phase 02.

The main README specifies Python 3.12+ and orjson/tzdata for the workstation, and Node 20.19+ (20.x) or 22.12+ for Chart. A complete runnable current checkout has not been assembled in this phase. Do not infer environment compatibility from source inventory. The source-identical 15 archived members were compiled locally as a narrow structural check.

## Immutable rules

Preserve native Decimal representation and arithmetic order, strict and inclusive predicates, RAW/main chronology, order/behavior identity, ownership, numbering and serialized output. Do not make trading-rule changes. Exact reference embedded-source digests match all 16 production files in each of three references (48/48). This establishes synchronization, not correctness of prose or full semantic reconstruction.

Use Source_Manifest.json, Production_and_Reference_Integrity.json, Repository_Discovery.json, Test_Inventory.json, RAW_Manifest.json and Golden_Evidence.json as Phase 01 evidence.
