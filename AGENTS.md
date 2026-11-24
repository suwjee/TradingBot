# TradingBot — standalone refactor operating contract

Owner directive (2026-11-24): only `refactor` may be written by AI. Never write, merge, reset, delete, rebase, push, or change `main`, `production`, or other branches absent a fresh explicit instruction for that exact operation. Never open a merge PR from this standalone memory branch to a product branch. GitHub access is not authorization. Read-only checkout and comparison of exact source commits is permitted.

## Start every task

Read `STATE.json`, `README.md`, `protocols/README.md`, the latest journal, the current phase prompt and gate reports. Resolve remote refactor HEAD and read main/production heads before any write. Inspect actual current state; historical reports are not new tests. Only fast-forward commits with expected-head checks; verify remote refs and protected branch identity after every push. Do not force-push.

## Scope and layout

This branch contains ONLY refactor-specific tooling, patches, manifests, phase prompts, reports, test evidence, journals and governance. No live product source trees (`apps/`, `engine/`, product launch scripts), RAW candles, credentials, dependencies, build output or copied product repositories. Fetch exact pinned source into an isolated ignored `.scratch/` or CI checkout; never commit it. Store proposed refactor source changes as reviewed patches against exact source commits with source/hash manifests. Historical source remains reachable via Git history and product branches; this is a tree-scope rule, not an access-control/security boundary.

## Correctness

Do not modify RAW, the Golden oracle, price precision/Decimal representations, trading logic, event order, identities, provenance, lifecycle, cross-direction semantics, or exact stable outputs in implementation-only refactors. For V9, no runtime refactor: use test-only observers and frozen Original/V8.1. Full one-million-candle test preferred; if real limits block it, execute the greatest feasible complete identical-input pair and record attempted sizes, limiting resources, timings and actual completed count. Do not promote a partial test or selected trace to full semantic PASS. Statuses PASS, FAIL, INCOMPLETE, NOT RUN must reflect evidence. No performance claim from instrumented timings or incomparable hosts.

## Durable handoff

Commit and push every completed or interrupted task on refactor. Update STATE, journal and owning phase evidence: exact inputs/hashes, commands, tool versions, timings/memory, changed files, results and blockers, artifact locations and SHA256, next steps. Record storage/availability limits explicitly. Preserve previous work in Git; use `archive/` indices for historical paths. CI must actually run relevant tests; do not weaken gates, hide failures or claim success without observed results. Never use branch isolation as permission to modify a protected branch.
