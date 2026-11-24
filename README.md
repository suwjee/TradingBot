# TradingBot — Refactor workspace

**Independent engineering memory. Not a deployable copy of TradingBot. Do not merge this branch into main/production.** Only refactor-specific files are tracked here. Product code is fetched read-only at exact commits in an isolated checkout when needed; refactor patches are stored separately.

| Start here | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Owner rules and branch boundary |
| [STATE.json](STATE.json) | Current phase, exact oracle and open gates |
| [protocols](protocols/README.md) | Engineering procedure and historical authority |
| [baselines](baselines/README.md) | Pinned sources, verified V8.1 delta and manifest |
| [prompts](prompts/) | Original refactor instructions |
| [versions/V9](versions/V9/README.md) | Active V9 tools, reports, test evidence |
| [journal](journal/) | Durable task records and handoff |
| [archive](archive/README.md) | Historical commits and exact recovery index |

**V9: INCOMPLETE / TRACE_COVERAGE_PARTIAL. V10 NO-GO.** Largest recovered completed strict pair is 250,000 5s candles (not a proven capacity limit). Full million and full state coverage remain open. This reorganization does not rerun the million-candle test.

CI checks this standalone workspace, active tooling, frozen Original and reconstructed V8.1 Engine tests, historical refactor Engine tests, historical Chart tests on Linux/Windows, and historical anti-drift tests. Sources are checked out separately at immutable SHAs, not copied into this branch. Prior PR #5 to main is incompatible with the new memory-only role; do not merge it. See the isolation journal for observed check results and limitations.

The Git repository is public and older commits remain reachable. Removing files from the current tree is not deletion of history or access control. No full product source is tracked at this branch HEAD.
