# Engine implementation and verification plan

> Execute inline with the existing CHECKPOINT ledger, test-first patches and a fresh final reviewer. User's explicit live-local-checkout and no-publication instructions override skill defaults for worktrees, commits and scratch deletion.

Spec: discovery/USER_REQUEST.md; current steering: user delegates the concrete deterministic-key repair choice while requiring completely identical before/after calculation outputs. Parent chose the separately disclosed one-line repair from reviews/DETERMINISM_REPAIR_PROPOSAL.md, retaining every original baseline artifact and reporting the byte-order difference explicitly.

## Task R: Preparatory deterministic serialization repair (separate from optimization)

- [x] Collect original44 CLI outputs/22scenarios and four CPU profiles; find first divergence; obtain independent review.
- [x] Present exact one-line repair and conditional rebaseline; user delegated decision with strict calculation equality requirement.
- [x] Add test_regime_output_determinism.py and observe canonical first-appearance key-order tests FAIL on actual Source across process hash seeds.
- [x] Guard original Source/Reference hashes and back up original Reference bytes. Replace set collector with ordered dict.fromkeys; keep public version constants unchanged, bump only existing Bridge implementation metadata.
- [x] Run focused/full Engine tests; compare all original saved calculation values/types/Decimal strings/identities/provenance/array order. Only the specifically disclosed aggregate bridgeOutput key ordering may differ in this preparatory repair.
- [x] Synchronize exact current Bridge bytes/manifests/indexes/revision evidence into both References without changing trading semantics. Verify recovered bytes/compile.
- [x] Establish immutable repaired-before matrix with repeatability in22scenarios, representative native stage snapshots, warm probes and fresh separate profiling. Original before remains failed original evidence.

## Task O: Measured optimization, only after Task R gates

- [x] Rank measured candidates from profiles. Most expensive current function includes OrderAudit._carried_orders_for_parent; study mutation/error/tie boundaries before selecting any patch.
- [x] Write candidate-specific contract, equivalence tests and baseline/hotpath metrics in07_OPTIMIZATION_PLAN.md.
- [x] Apply smallest owner patch; no stable byte difference versus repaired-before allowed. Retain only after focused/native/full matrix equality and measured real benefit with bounded memory cost.
- [x] Revert only task-owned unsuccessful candidate bytes, retain evidence. Do not rewrite expected outputs to accept it.

## Task F: Final gates and all numbered deliverables

- [x] Complete AFTER22matrix and native equality, current units/anchors/reference/Anti-Drift, RAW hashes and Source/dependency/diff review.
- [x] Reconcile both Reference snapshots and metadata; preserve canonical Vault semantics/exclusions and separate pre-existing conflicts.
- [x] Produce04-14 plus complete raw evidence and method limitations; final independent reviewer; Persian summary with exact original/preparatory/optimization boundaries.
- [x] No staging, commit, push, release, Graphify or RAW mutation.

Final closure 2026-11-02T12:31:28+03:30: all actual gates and independent review completed; no candidate rollback was needed (retainedO1). Conditional rollback-policy checkbox is satisfied as NOT APPLICABLE to an unsuccessful Source patch, not a claim that bytes were reverted.
