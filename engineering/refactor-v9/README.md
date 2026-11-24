# V9 — deep profiling and Golden execution trace

**INCOMPLETE / TRACE_COVERAGE_PARTIAL / NO-GO for V10.**

Start with [permanent workspace](../refactor/README.md), [current state](../refactor/STATE.json), [original V9 prompt](V9_ORIGINAL_PROMPT.txt), [prior gate report](V9_CURRENT_GATES.json), and [latest journal](../refactor/journal/2026-11-24-v9-evidence-recovery.md).

- tooling/: active test-only observers, strict trace gate, verified runner, frozen cases, and mutation tests.
- legacy-v9-tooling/: historical utilities; verify before reuse.
- Root V9 audit files: prior checkpoints and selected evidence; 13 PASS and 2 INCOMPLETE in latest prior report (not all re-executed).
- [100k run](evidence/2026-11-24/synthetic-100000/pair_report.json) and [250k run](evidence/2026-11-24/synthetic-250000/pair_report.json): completed pairs, Golden stable output PASS, selected trace INCOMPLETE. [Prior strict continuation report](evidence/2026-11-24/strict-continuation-result.json).
- Full artifact hash inventories in each run directory. Binary trace/native output bodies not committed; external durable retention not verified.
- [Historical archive index](../refactor/archive-index.json) locates removed superseded tooling and bulk outputs by Git commit and blob SHA.

Golden oracle: 01d54ecf0149ebd15de92798be18810b6e2eb791. Never substitute current HEAD for pinned Original or frozen V8.1. V9 instrumentation is test-only, no RAW/production changes.

Run `python -m pytest engineering/refactor-v9/tooling/test_strict_trace_gate_v9.py`. Use `python engineering/refactor-v9/tooling/run_verified_trace_pair_v9.py --help` and frozen case JSONs with exact pinned RAW/source snapshots and a fresh output dir. Do not treat local paths from historical reports as accessible on every host.

Outstanding gates: full 1M selected internal pair and all semantic mutator/Live state coverage. Attempt the largest feasible complete pair if full million cannot be completed; this is not a full-scale PASS. No V9 speedup claim.
