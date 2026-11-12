# Separate deterministic-serialization repair proposal (NOT APPLIED)

Scope: a preparatory public byte-order correction, outside the present no-output-change authorization. This proposal is not a performance optimization and cannot be silently merged into the zero-difference task.

## Observed evidence

The original unchanged Source produced two ordered-output failures in 44 completed cold CLI runs. Exact paths and complete before/repeat payloads are retained in `../discovery/determinism-first-differences.json` and the two corresponding `before/<case>/run-*.stdout.json` files. Each failed pair differs in one mapping-order path and in zero non-order values, types or array positions. Current `merge_regime_outputs` collects `bridge_keys` into a set and uses that set as dictionary insertion order. A four-seed probe of the actual current function reproduces four different orders. No sorted comparison is accepted as PASS.

## Concrete proposed change

In `engine/bridge/trading_pipeline.py`, function `merge_regime_outputs`, replace only the unordered key collector:

```diff
-            bridge_keys = {key for item in bridge_outputs for key in item}
+            bridge_keys = dict.fromkeys(key for item in bridge_outputs for key in item)
```

This makes the merged projection's key order follow the first appearance of each field in finalized segment Bridge outputs. Ordinary `build_bridge_output` already declares its eight keys in a fixed order. Values, array concatenation, segment membership, trading state and all other fields keep their current source paths. This still intentionally changes previously variable serialized byte order, so it needs explicit separate approval.

## Required work if approved

1. Add focused multi-segment and multiple-hash-seed tests, including disjoint/empty segment keys and preservation of all arrays/identities.
2. Apply the narrowly scoped ordering correction. Preserve public API version fields; update only the existing Bridge implementation version/timestamp under current convention.
3. Synchronize exact embedded Bridge Source, implementation metadata, affected indexes/manifests and truthful revision notes in both accepted References; no new trading semantics or Vault primary content.
4. Verify only the explicitly approved key-order correction against original saved results, with zero other differences. Rerun both failed real scenarios across independent process seeds and all existing Engine tests/reference checks.
5. Establish a new immutable, explicitly named post-repair BEFORE baseline. Preserve the original failed baseline forever; it must not be overwritten or relabeled PASS.
6. Resume any measured implementation-only optimization only against that newly authorized stable baseline, with the original strict equality gates and final regression.

Alternative within the current authorization: leave all production Source/References untouched, deliver the completed read/profile evidence and report ZERO-DIFFERENCE REFACTOR NOT VERIFIED. No speedup or after-candidate comparison can be claimed.
