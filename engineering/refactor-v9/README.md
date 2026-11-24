# V9 — deep profiling and Golden execution trace

**INCOMPLETE / TRACE_COVERAGE_PARTIAL / NO-GO for V10.**

Start with [workspace](../refactor/README.md), [current gates](V9_CURRENT_GATES.json), and [archive index](../refactor/archive-index.json). Earlier README and expanded tooling are recoverable at 75bfd33e15a8eb56d5b832a4e0121f9a33cbd50f.

- tooling/: current V9 observers, comparators, audits, runners and tests.
- legacy-v9-tooling/: historical utilities; verify before reuse.
- Root V9 reports: earlier audits; V9_CURRENT_GATES.json reports 13 PASS and 2 INCOMPLETE (not all re-executed).
- evidence/: recovered strict continuation reports and manifests, added in subsequent evidence commit.

Golden oracle: 01d54ecf0149ebd15de92798be18810b6e2eb791. Never replace it or frozen V8.1 with branch HEAD. No RAW or runtime edits for V9 instrumentation.

Remaining: full 1M selected trace pair and complete semantic mutation/Live state coverage. The completed 100k and 250k strict pairs have exact Golden stable outputs, but selected trace remains incomplete. No V9 speedup claim.
