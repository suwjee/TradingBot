# V9 — Deep Profiling and Golden Execution Trace

**INCOMPLETE / TRACE_COVERAGE_PARTIAL / NO-GO for V10.** See [current state](../../STATE.json), [original prompt](../../prompts/V9.txt), [prior gate report](reports/V9_CURRENT_GATES.json), [baselines](../../baselines/README.md), and [journal](../../journal/).

- `tooling/`: active test-only observer, strict comparison, lossless integrity audits, portable runner, security and streaming tests, pinned cases. Earlier superseded variants are recoverable by exact commit/path in the archive index.
- `reports/`: historical V9 gate reports and analysis, not all rerun during reorganization. Historical local paths may not be accessible on other hosts.
- `evidence/2026-11-24/`: recovered 100k and 250k paired reports, frozen inputs, trace manifests, profiles and hash inventories. Full binary traces/native outputs are not committed; long-term external retention is unverified.

Run `python -m pytest versions/V9/tooling/test_strict_trace_gate_v9.py versions/V9/tooling/test_safe_sidecar.py` and `python versions/V9/tooling/test_v9_large_stage_stream.py`. See `python versions/V9/tooling/run_verified_trace_pair_v9.py --help` for full pair arguments. Use exact source and RAW case hashes and fresh output paths. Do not use branch HEAD as an oracle.

Both recovered pairs have stable Golden output PASS, but selected semantic trace remains INCOMPLETE. 250k is the largest recovered complete strict pair, not a proven resource maximum. Full 1M selected internal pair and all semantic mutation/Live state coverage remain open. No V9 speedup claim.
