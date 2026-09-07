# AI routing index

Read only what affects the requested work:

1. `CURRENT_HANDOFF.md` for the live architecture and known validation limits.
2. `PROJECT_MAP.md` to locate the single owning subsystem.
3. `CONCURRENCY.md` before shared changes or delegation.
4. `AGENT_ORCHESTRATION.md` before parallel work.
5. `GIT_WORKFLOW.md` before staging, committing, or publishing.
6. `DATA_POLICY.md` before touching candle data, caches, or generated output.
7. `USER_WORKING_RULES.md` for communication, rule clarification, scope, and tests.
8. `UI_UX_DESIGN_RULES.md` before a chart workstation visual or interaction change.
9. `docs/algorithms/BULLISH_INDICATOR_ALGORITHM.md`, maintained source, and
   focused tests for any algorithm change.

Do not treat `graphify-out/`, `tmp/`, `primary-cache/`, dependency directories,
or backup files as runtime authority. `graphify-out/` is useful navigation only.
