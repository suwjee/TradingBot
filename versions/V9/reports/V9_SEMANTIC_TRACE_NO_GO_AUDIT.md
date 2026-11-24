# V9 semantic trace — fail-closed coverage audit

**Correctness oracle**: `01d54ecf0149ebd15de92798be18810b6e2eb791`; 15 unchanged original source Git blobs.

**Scope**: test-only V9 instrumentation of Original and V8.1, full native 30s/5s/BOTH engine calls. No production source rewrite, RAW alteration, numerical tolerance, sorted stable output, or change of trading behavior.

## Verified, scope-limited evidence

1. Seven complete real 5s RAWs: stable native output exactly matches frozen Original; the selected AST operation meters also preserve these outputs.
2. Four synthetic sizes (100k/250k/500k/1M), both Original/V8.1: 8/8 AST selected-site meter runs pass exact stable-output comparison, count fields fully manifested.
3. 545 official unit tests from pinned source and 545 official V8.1 test runs on AST-instrumented test-only source pass. Separate ABBA benchmarks do not imply a V9 speedup.
4. Selected in-process output/transition trace uses event ordinal, stage, direction, source/provenance, Decimal string and stage timing. It compares selected function *return* events across the single native BOTH invocation, not every state mutation.
5. Fresh Candidate collection snapshot instrumenter v4 passed test-only mutation injection and OIL15k full RAW native parity. The earlier v3 recorder used first-use-only snapshots of mutable Candidate collections and cannot by itself prove later state.

## Why the current event trace cannot be certified complete

- The 15-file AST inventory identifies **103 functions with possible state mutations** (98 unique basename/function keys) not directly observed by the selected method wrapper. Static tags include implementation caches and domain state; classification needs owner-specific review.
- Runtime `sys.setprofile` on full OIL 15,061 rows confirms **81 risk function keys actually invoked** in each version, with 141,332 Original calls and 140,901 V8.1 calls. Runtime call observation is read-only and full native output still matches Golden; call counts are **not** semantic mismatch evidence and do **not** verify pre/post state.
- In v4 OIL15k strict owner-collection snapshot comparison, **25 of 4,012** selected positions differ by noncanonical `set` iteration order. Diagnostic member-set comparison (without changing the original trace or stable output) finds no other payload differences among these 25 positions, but there are **1,100 unverified input drift positions**. This does NOT authorize replacing raw chronological trace with a sorted set or claiming universal semantic equivalence.
- Selected method-event comparison excludes implementation-only inner call families (OrderAudit index and Parent Stop internals), as documented in comparison scripts. Some semantic transitions could occur only inside excluded call families or 81 uncovered risk methods.
- Unobserved Live continuation and hidden state/caches, tie-breaking under unseen inputs, and order of all mutation events remain not fully established.

## Release decision

Unless these coverage holes are closed with independently tested, lossless owner-specific mutation transitions and strict ON/OFF native parity, **`TRACE_COVERAGE_PARTIAL` and `INCOMPLETE` are mandatory**. Full stable-output and selected trace parity cannot be relabeled `TOOLING VERIFIED`. It is not permissible to silently drop or normalize a differing field in order to pass.

The record does not certify or reject the mathematical correctness of any trading algorithm; it documents what was actually observed.