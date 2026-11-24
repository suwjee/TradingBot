# 2026-11-24 — Standalone refactor workspace and CI repair

Owner clarified that no other project source is to appear in the live refactor tree. Prior refactor snapshot `eef50eb2cedb06ba4c77bb82c6ac3b312ef1e7ba` remains reachable for reproduction; all product branch refs are read-only. Protected starting heads: main `466eb875070f02cd0dbfb105033422bbe2fd8c70`, production `9838fa9809865aa6507adb7be871810d878bdb5f`.

## Prior checks diagnosed

- Engine job 138495106024, run 45408362564: **296 unit tests passed**, then compile failed in `semantic_trace_v9.py` line 500 because two statements were joined without a newline. Recovered the valid observer that was actually exercised in previous runs; the code's trading source remains unchanged.
- SonarCloud check 138496287337: 21.8% new-code duplication (limit 3%) and E new-code security rating (requires A) on open PR #5 (`refactor` -> `main`). Exact security annotations could not be retrieved from the available API. The new memory branch is not mergeable into product branches. Do not suppress active implementation security analysis or claim Sonar PASS without a new observed analysis. Superseded tool implementations remain in history instead of active duplicated sources.
- Previous pinned oracle, Chart Linux/Windows and anti-drift checks passed. Preserve their actual commands using read-only pinned checkouts in the new CI; this is historical source verification, not live product deployment.

## Local verification (observed)

- `python -m compileall -q versions/V9/tooling`: PASS.
- `python -m pytest -q versions/V9/tooling/test_strict_trace_gate_v9.py versions/V9/tooling/test_safe_sidecar.py`: 18 passed, 11 subtests passed.
- `python versions/V9/tooling/test_v9_large_stage_stream.py`: 8/8 PASS.
- Re-audit previous full 15,061-candle Original/V8.1 trace and stage sidecars: both integrity PASS, not full semantic coverage.
- Earlier global/family-local/sidecar corruption suites in recovered original tooling: 10/6/9 PASS.
- `git apply --check` and `git apply` V8.1 delta to isolated frozen Original, SHA256 of all 15 modules matches archived V8.1 exactly. Original unchanged. `verify_baseline.py` 15 checks PASS.
- Workflow YAML parsed. Full remote CI and Sonar outcome are NOT RUN at local preparation time; record remote results separately, never infer success.

## Security hardening

Reject absolute paths, traversal, alternate separators, NUL, symlinks and nonregular sidecar files referenced by a manifest. Valid sidecar hashes/ordinal audits still pass. This addresses an independently identified path-handling weakness; it is not evidence that Sonar's unavailable exact vulnerability finding is resolved.

## Scope

Move current V9 reports, exact prior run reports, manifests and original prompt to dedicated directories. Preserve historical tools and all removed product files via Git commit/path/blob recovery indices. Store only a verified V8.1 refactor delta, not complete Engine code. No force-push/history rewrite, no RAW modifications and no production runtime change. Full 1M and full state coverage remain INCOMPLETE.
