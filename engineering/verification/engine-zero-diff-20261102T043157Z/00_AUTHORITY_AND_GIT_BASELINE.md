---
title: Engine audit authority and Git baseline
document_role: evidence
lifecycle: generated
owner: engine-zero-difference-audit
created_at: 2026-11-02T08:01:57+03:30
---

# Authority and Git baseline

Task-selected authority is the live local checkout `X:/My-Projects/TradingBot`, independently resolved with `git rev-parse --show-toplevel`. The initial branch is `main`, HEAD `afb586b69ecd6e12bcef30e2dbc4163e764dfcdb`; `git status --porcelain=v1 -uall` was empty before task evidence creation. Initial staged and unstaged diffs are empty and preserved under `discovery/`. Remote `origin` is `https://github.com/suwjee/TradingBot.git`; no fetch, pull, checkout, stage, commit or remote write occurred. Existing other worktrees were inventoried and are untouched.

## Governing scope

The exact user request is retained in `discovery/USER_REQUEST.md`. It authorizes implementation-only optimizations only after the valid BEFORE baseline and profiling gates, requires exact stable outputs, forbids semantic fixes, and requires all numbered artifacts. It explicitly authorizes ordinary safe changes without another approval. No Graphify execution or publication is authorized. The explicit live-checkout requirement takes precedence over optional worktree-isolation skill advice; the production checkout remains the selected baseline.

Root `AGENTS.md` was read completely. Recursive instruction discovery found no nearer instructions in `engine/`. `GPT_bot/AGENTS.md` and `GPT_bot/TradingBot_AI_Operating_Protocol.md` are portable companions, subordinate to root governance; the protocol is reviewed because the user expressly requires discovery. Full protocol coverage is recorded by the parent (1-1130) and the delegated reader (`reviews/protocol-review.md`, 1131-end). Do not infer protocol completion before that ledger exists.

## Maintained owner documents read

- `engineering/docs/README.md`: documentation navigation, maintained reference.
- `engineering/docs/ai/engineering-workflow.md`: task procedure.
- `engineering/docs/development/zero-difference-refactor.md`: mandatory equivalence/performance gate.
- `engineering/docs/development/testing.md`: dynamic tests, status and immutable RAW policy.
- `engineering/docs/development/algorithm-reference-maintenance.md`: both directional References and exact reconstruction.
- `engineering/docs/architecture/technical-architecture.md`: current runtime ownership, supplied-input scope, process/cache boundary.
- `engineering/docs/verification/repository-integrity.md`: byte preservation, generated evidence placement, Anti-Drift invocation.
- `engineering/docs/documentation-governance.md`: owner/lifecycle/timestamp/placement policy.
- `engineering/docs/operations/local-state.md`: RAW/cache/secret/scratch classification.
- `.gitignore`, `.gitattributes`, root `README.md`: actual tracking, exact-source byte protection and supported startup/dependencies.

Current accepted References were discovered from the live `engine/algorithms/` owner, its unique directional target declarations and maintained navigation, not selected by version ordering. Both names end `V5.4.33_Source_Synchronized.md`. Team prose/format reviews are under `reviews/`. Their shared embedded Source is read through the corresponding live production owner; the supported independent verifier directly compared all fourteen embedded files in each Reference, verified declared SHA/bytes/LF and compiled recovered content. Actual log: `discovery/reference-verification-before.log`. This establishes current local byte synchronization, not semantic consistency or market correctness.

## Real connected knowledge retrieval

The TradingBot Knowledge MCP actually responded. Read `system.authority`, `system.retrieval`, `version.current`, `source.source_manifest`, `source.reference_registry`, `source.reference_consistency`, `core.invariants`, `core.pipeline`, `workflow.operating`. Bootstrap results and all authority/status/warning fields are preserved in `discovery/mcp-bootstrap.json` (the initial authority/retrieval responses are also present in this chat's tool evidence). Source snapshots in the Vault explicitly exclude the standalone primary detector; its Code tree is not a complete runnable Engine. RAW/Fixture stores are documented `EMPTY_BY_DESIGN`, and local `08_DATA/` has registry/model/navigation notes rather than RAW arrays. No Vault data integrity or market regression PASS is inferred from retrieval.

The user-provided public GitHub engineering URL was read through the GitHub connector in GET-only mode. It exposes `archive`, `docs`, `verification`; it is supplementary navigation only. No remote content replaced local files. Local maintained documentation governs this task.

## Explicit discrepancies and bounded decisions

1. **Vault snapshot drift:** its Source/Reference pins describe the October 27 capture (`c2e790...` provenance), while the actual local checkout and current References contain later November 1 changes. Example: Vault bridge SHA `d70481975d2b8e41c6271a02243862d967d5c906bbe1f2f23a432df6fc0f85a1`; live pre-edit bridge SHA `6d93dbaf67e4dce02060575b92dda5de6eaf6de0148f6db54056015c072181dc`. Treat Vault executable claims as captured evidence. Current explicit user scope includes the primary detector despite the Vault capture's bounded exclusion. No new primary knowledge is added to the Vault.
2. **REF-REACTION-SUCCESSOR:** Vault `source.reference_consistency` and current Reference 4.4 retain ambiguity between a whole confirmation First candle and wording about eligible post-event boundary prices. The executable helper retains whole-candle geometry after its separate post-event Reset check. This task does not choose or repair a semantic interpretation; both claims remain documented. Changes requiring that decision are excluded.
3. **Stale workflow task boundary:** `workflow.operating` ends with the prior knowledge-audit read-only Source scope. The present explicit user instruction separately permits implementation after the gates, so that older task-specific limitation does not revoke this authorization.
4. **Reference example residue:** the Bearish reader found a current example with a 100-candle cap while the active general rule says 400 actual candles. Keep this semantic/documentation conflict separate from refactoring; do not silently change the example or implementation.
5. **Historical benchmark restrictions:** the October 2 runner hardcodes a former 10 MiB cap and obsolete paths; the current regression helper defaults to another size cap. Those are historical execution choices, not this user's constraint. The audit matrix has no RAW size exclusion and includes the 24 MB/309,266-row month file.
6. **RAW helper qualification:** `verify_order_b_raw.py` has a whole-time assertion narrower than the accepted same-main-candle Order rule and uses `orjson` floating parsing. It cannot serve as a complete lexical-precision or chronology oracle. Do not change production to satisfy it.

## Safe evidence and environment

This unique folder is a generated verification evidence owner under `engineering/verification/`, consistent with documentation governance and integrity policy. Original Source bytes are copied once under `discovery/source-before/engine/` with hashes; original RAW files are only read and hashed. This folder is outside production loading and Vite static access. No secrets/session/cache files are read or copied. Original ignored RAW and other workstation state remain in place.

The actual interpreter is Python 3.15.0 on Windows 11; paths and package observations are in `discovery/environment.json`. CPU/RAM are in `discovery/cpu.json` and `ram.json`. Existing runtime packages: orjson 3.13.0, tzdata 2026.5. Pytest was absent, so a task-local virtual environment with existing system runtime packages was created under the permitted ignored `apps/chart/state/tmp/engine-audit-20261102T043157Z-venv`. Only trusted test runner packages were installed there (pytest 9.2.0); no global settings or project dependency manifests changed. Freeze is preserved under `discovery/test-environment-packages.txt`.

## Remaining gate at this checkpoint

### Later explicit user steering and preparatory exception

The original matrix completed44 cold CLI runs across22 scenarios and exposed two repeatability failures limited to aggregate Bridge projection mapping-key order. The separate repair proposal was shown with exact one-line diff. The user delegated the choice while requiring completely identical before/after calculation outputs. The parent explicitly selected a separately disclosed preparatory serialization-order repair, preserving every original artifact and requiring zero differences in calculation values/types/Decimal strings/identities/provenance/array order. The approved mapping-order delta is reported separately; it is not normalized away to claim original zero-difference. A new immutable `repaired-before` baseline must pass before performance implementation. Public API versions remain unchanged, while existing Bridge implementation metadata and both exact-source References are synchronized. This later steering does not authorize trading-rule changes or any other output exclusion.

Before production changes: finish and validate full source/read ledgers, full Reference/protocol reviews, immutable repeated BEFORE matrix, native stage snapshots, initial test/contract execution, and separate profiles. Source/Reference identity alone does not satisfy those gates. All benchmark results remain NOT RUN until their logs exist.
