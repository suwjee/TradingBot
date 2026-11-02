---
title: TradingBot Non-Engine Refactor — Phase 1 FARAZ Response Ownership
document_role: evidence
lifecycle: historical
owner: chart-faraz
created_at: 2026-11-02T06:47:53.913Z
last_modified_at: 2026-11-02T06:47:53.913Z
---

# Non-Engine Refactor — Phase 1: FARAZ Response Ownership

## Authority and immutable boundary

- User-approved target branch: `refactor`, created from `main@afb586b69ecd6e12bcef30e2dbc4163e764dfcdb`.
- Explicit rule: **no file, reference, test, archive, or generated data beneath `engine/` may change**.
- This change repairs a demonstrated browser-session bug, rather than claiming a pure zero-difference transformation of the affected broken behavior.
- Trading algorithms, input RAW evidence, Engine serialization, existing user state, and release branches are outside this change's scope.

## Confirmed root cause

In `apps/chart/server/faraz-candle-api.js`, the same lexical scope defined two `captureHistoryResponse` functions:

1. `captureHistoryResponse(response)` for Playwright browser history responses and session finalization.
2. `captureHistoryResponse(job, chunk, response, text)` for extraction response-audit persistence.

JavaScript duplicate function declaration binding selected the latter implementation when registering `page.on("response", captureHistoryResponse)`. The browser supplied only the Playwright response argument, so the audit callback's `if (!job.responseAuditPath) return` bypassed session finalization.

## Minimal production correction

Only the owner-local FARAZ handler naming and affected call sites changed:

- Browser callback: `captureHistoryAuthResponse(response)`.
- Browser event registration: `page.on("response", captureHistoryAuthResponse)`.
- Audit callback: `writeHistoryResponseAudit(job, chunk, response, text)`.
- Audit invocation: `writeHistoryResponseAudit(job, chunk, response, text)`.

Both handlers now have distinct, descriptive responsibilities; the extraction response-audit schema and browser-session persistence format remain unchanged. No Engine or trading-rule changes were made.

## Regression-first evidence

Added `apps/chart/tests/unit/faraz-history-response.test.mjs` with four deterministic synthetic cases:

1. Successful allowlisted history response captures and persists browser credentials without status polling.
2. Unknown host, unrelated path, and unsuccessful response do not capture a session.
3. Concurrent successful callbacks finalize only one session.
4. Authenticated extraction response audit continues to produce NDJSON entries independently of browser login capture.

**Before production correction:** [run 41401520607](https://github.com/suwjee/TradingBot/actions/runs/41401520607) reproduced the defect: Ubuntu Chart test run failed the positive session-capture and concurrent-finalization cases; the negative-response case passed.

**After production correction:** [run 41401971262](https://github.com/suwjee/TradingBot/actions/runs/41401971262) completed successfully on both environments:

| Verification | Ubuntu | Windows |
| --- | --- | --- |
| Chart tests | **PASS** 259 passed, 5 skipped, 0 failed (264 total) | **PASS** 264 passed, 0 skipped, 0 failed |
| Vite production build | **PASS** | **PASS** |
| Branch-relative `engine/` diff guard | **PASS** | **PASS** |
| Read-only Python integration dependency setup | **PASS** | **PASS** |

The separate [anti-drift workflow run 41401971144](https://github.com/suwjee/TradingBot/actions/runs/41401971144) also completed **PASS**.

The Windows runner initially exposed missing `tzdata`; the new non-Engine workflow now installs Python 3.12 plus `orjson` and `tzdata`, then runs the existing Chart tests/build. The extraction audit fixture expectation was corrected to match the existing request contract (`firstDataRequest=true`, `latest=true` for the initial packet); the application was not changed to satisfy an incorrect test assumption.

## Engine protection and exact scope

At the initial baseline `engine/` contained 43 tracked Git blobs. GitHub branch comparison of `main` against `refactor` showed no changed `engine/` paths; the CI branch-relative guard independently enforced this for both Linux and Windows. This proves unchanged tracked Engine content in the compared Git revisions; it does not claim inspection of any user's untracked local workstation state.

Non-Engine files added or changed for this phase:

- `apps/chart/server/faraz-candle-api.js` — fix callback collision.
- `apps/chart/tests/unit/faraz-history-response.test.mjs` — deterministic event and audit regression.
- `.github/workflows/chart-refactor.yml` — Linux/Windows test/build and no-Engine-change guard.
- This evidence report.

No direct `main` change, merge, PR, tag, release, or publication is part of this phase.

## Evidence boundaries and next work

**NOT RUN:** authenticated browser session against the real FARAZ service; interactive Windows Chart UI/browser E2E; historical RAW-based end-to-end comparison of Bullish/Bearish Engine projections; CPU/RAM performance benchmarks on a running workstation; full source-wide refactor.

These checks are separate from the passing unit, integration-mock and build evidence. This phase is complete as a narrowly scoped **FARAZ response callback ownership and regression** change, not as completion of all non-Engine bug fixes or performance objectives.

The next isolated phase should benchmark and inspect Vite request/cancellation, RAW read/merge, calculation cache/coordinator, and Chart event/rendering lifetimes before any broader refactor. Each patch requires pre/post tests and an unchanged Engine tree.
