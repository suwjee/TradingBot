# TradingBot V9 — updated auditable gate status (2026-11-24)

**Release decision: `INCOMPLETE`, `TRACE_COVERAGE_PARTIAL`; NOT `TOOLING VERIFIED`.**

All new instrumentation, experiments, checks and reports for this task are restricted to `refactor`. Immutable correctness oracle: pinned `01d54ecf0149ebd15de92798be18810b6e2eb791`. Performance reference: untouched V8.1. This document does not promote a new runtime version or claim a V9 speedup.

## Verified, 11/16 gates

- Original Golden SHA256, ZIP CRC, 15 Git blob IDs and all seven 5s RAW SHA256/record counts: PASS.
- Full native 30s/BOTH stable output equality on 7/7 RAW and 4/4 synthetic scales up to 1,000,000: PASS.
- All seven real RAW, selected-site AST loop/cache/heap/sort instrumentation on isolated V8.1 copy, native output equality: PASS. 15,349,430 counted selected operations, **not full interpreter operations**.
- Unprofiled 1M native BOTH ABBA benchmark: three complete ABBA blocks / 12 executions, stable outputs PASS. Observed median frozen Original 451.201961908 seconds, V8.1 370.6800929905 seconds. This is a paired observation for historical versions, **not a V9 optimization**.
- Pinned V8.1 official unit tests: 545 PASS; isolated AST-metered V8.1 official unit tests: 545 PASS.
- Ten semantic comparator mutation checks: PASS. Nine gzip/event/sidecar/integrity mutations: PASS. All 15 V8.1 production Python bytes match source ZIP.
- One 97,930-row XAU instrumented internal observer run: Original 456,955 events, V8.1 414,097; 102,901 comparable globally sequenced *selected* semantic event outputs PASS. Trace includes explicit unsupported gaps and non-equivalent implementation call families.
- Observed selected internal trace results also checked on 15,061-row USOIL and six synthetic edge cases.

## Uncompleted mandatory gates (5/16)

1. Original and V8.1 AST metering across synthetic 100k / 250k / 500k / 1M in complete both-direction executions: NOT COMPLETED.
2. Paired unprofiled ABBA 3 blocks for **two smallest and two largest** real RAW: 2/4 datasets complete in the checkpoint, remaining large full runs not complete.
3. Full seven real RAW Original+V8.1 internal trace, with in-process semantic chronological comparison: NOT COMPLETED.
4. Synthetic 1M internal observer trace Original+V8.1: NOT COMPLETED.
5. A genuinely complete lossless authoritative pre/post state and all candidate/OrderAudit/ParentStop/Reset/StopAll/lifecycle/Live transition trace: **NOT VERIFIED**. The current observer explicitly excludes some internal branches and mutable-state revalidation. Some internal input differences are reported without triggering FAIL. Equality of final native outputs, 102,901 selected events or selected stage snapshots does not prove this contract.

## Independent rechecks in this continuation

- Freeze audit: PASS, 15 production Git blobs and seven inputs.
- Immutable V8.1 source audit: PASS 15/15.
- Global comparator mutation suite: PASS 10/10.
- Sidecar/checksum mutation suite: PASS 9/9.
- Gate consolidation script: `INCOMPLETE`, 11 PASS of 16, zero FAIL, five remaining.

## Artifacts

Checkpoint package: `TradingBot_V9_REFACTOR_AUDITED_CHECKPOINT_20261124.zip`, SHA256 `385f96a559e819c0b681d17a5afc34e05f1c4839b7991fb02984b03bc4d40d61`, with exhaustive gate JSON, freeze audit, mutation logs, unit-test logs, ABBA results, selected trace reports, input parity, SHA256SUMS.

Do not overwrite or reinterpret the prior immutable Golden ZIP. No production `engine/` modifications are part of V9. A release promotion requires independent PASS evidence for the five gaps above. This is a status snapshot, not permission to infer a PASS from an incomplete task.
