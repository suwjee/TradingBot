# V9 — Deep Profiling and Golden Execution Trace

**INCOMPLETE / TRACE_COVERAGE_PARTIAL / NO-GO for V10.** See [current state](../../STATE.json), [original prompt](../../prompts/V9.txt), [prior gate report](reports/V9_CURRENT_GATES.json), [baselines](../../baselines/README.md), and [journal](../../journal/).

- `tooling/`: active test-only observer, strict comparison, lossless integrity audits, portable runner, security and streaming tests, pinned cases. Earlier superseded variants are recoverable by exact commit/path in the archive index.
- `reports/`: historical V9 gate reports and analysis, not all rerun during reorganization. Historical local paths may not be accessible on other hosts.
- `evidence/2026-11-24/`: recovered 100k and 250k paired reports, frozen inputs, trace manifests, profiles and hash inventories. Full binary traces/native outputs are not committed; exact storage references and finite CI retention are recorded in STATE. The new OIL/XAU evidence is also archived in private Library.

Run `python -m pytest versions/V9/tooling/test_strict_trace_gate_v9.py versions/V9/tooling/test_safe_sidecar.py` and `python versions/V9/tooling/test_v9_large_stage_stream.py`. See `python versions/V9/tooling/run_verified_trace_pair_v9.py --help` for full pair arguments. Use exact source and RAW case hashes and fresh output paths. Do not use branch HEAD as an oracle.

Both recovered pairs have stable Golden output PASS, but selected semantic trace remains INCOMPLETE. 500k is the largest verified complete pair in the prior CI report; full selected state remains incomplete. Full 1M selected internal pair and all semantic mutation/Live state coverage remain open. No V9 speedup claim.

## Efficient validation

The [fused exact validation plan](reports/EFFICIENT_EXACT_VALIDATION_PLAN.md) is partially implemented. Use `run_verified_trace_pair_v9.py --audit-mode fused` (default); `--audit-mode legacy` remains available. The fused pipeline preserves legacy selected-event checks and all sidecars, and compares exact stable native bytes. Full report equivalence and one-block ABBA are verified on complete OIL and XAU short RAW pairs. 100k/250k checkpoint CI validates larger cases against the pinned old reader. Long native runs now require an explicit request-manifest push (or workflow dispatch where available): create/update `reports/SYNTHETIC_RUN_REQUEST.json` with a unique `request_id` and `level` of `checkpoint` or `full`. Full 500k/1M remains required for certification. Archived trace replays use `reports/TRACE_REPLAY_REQUEST.json` and verify the pinned ZIP SHA, every member and exact old report; no Engine rerun. No full semantic coverage claim. See [latest journal](../../journal/2026-11-24-v9-guarded-replay.md).
