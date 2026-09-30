---
title: TradingBot AI Engineering Workflow
document_role: procedure
lifecycle: maintained
owner: ai-engineering-workflow
scope:
  - engineering-task-execution
  - documentation-synchronization
created_at: 2026-09-30T10:14:08+03:30
last_modified_at: 2026-09-30T11:40:11+03:30
---

# TradingBot AI Engineering Workflow

This document defines the maintained execution workflow for AI-assisted engineering work. It complements the root [`AGENTS.md`](../../../AGENTS.md); it does not replace or restate that operating contract.

For documentation classification, lifecycle, placement, and ownership, use [Documentation Governance](../documentation-governance.md). For current documentation navigation, use the [Engineering Documentation index](../README.md).

## 1. Workflow boundary

Use this document for the repeatable path from a task request to a verified, synchronized result. Do not use it as:

- an Algorithm Reference;
- a trading-semantic specification;
- a test-suite inventory;
- a release implementation guide;
- a repository snapshot.

Mutable project facts are discovered from the live project when needed.

## 2. Standard execution flow

Follow this sequence:

`Task → authority discovery → project inspection → ownership identification → investigation/implementation → verification → documentation synchronization → timestamp update → diff review → authorized commit/push → remote verification → final delivery`

A step may be `NOT APPLICABLE`, but it must not be silently skipped when the root operating contract or the task requires it.

## 3. Authority discovery

1. Read the current explicit user instruction.
2. Read root [`AGENTS.md`](../../../AGENTS.md) and any nearer applicable instructions.
3. For trading semantics, retrieve the current canonical knowledge required by root AGENTS, then inspect the current accepted Algorithm References and current executable Source as applicable.
4. For documentation work, read [Documentation Governance](../documentation-governance.md) and identify the maintained owner of the fact being changed.
5. If authorities conflict, report the conflict instead of inventing a reconciliation.

Do not infer authority from filename age, timestamp, version, hash, file count, or a historical report.

## 4. Project inspection

Before substantial work:

- locate the actual repository root from the current environment;
- inspect current branch, remote, and working-tree state when a working tree is available;
- preserve staged, unstaged, untracked, deleted, renamed, and local-only user work;
- recursively inspect the project structure to the depth required by the task;
- discover current Source, tests, manifests, configuration, documentation, and evidence dynamically;
- follow imports, runtime entry points, references, and ownership boundaries far enough to understand impact.

Do not assume a fixed Engine inventory, fixed test count, fixed version, fixed hash, fixed Git HEAD, or universal package/archive input.

## 5. Ownership routing

Keep work in its owning layer:

- **Chart** owns visualization, interaction, workspace/chart UI state, and presentation.
- **Vite/server** owns local transport, orchestration, process coordination, and assigned persistence/response boundaries.
- **FARAZ** owns market-data acquisition, authentication/session handling, and RAW/history integration.
- **Engine** owns authoritative trading calculation and trading state.
- **Documentation owners** describe their bounded maintained responsibilities according to Documentation Governance.

Use [Technical Architecture](../architecture/technical-architecture.md) for architecture ownership, [UI/UX Reference](../architecture/ui-ux-reference.md) for UI responsibility, and current Source when executable behavior must be established.

## 6. Investigation and implementation

For bugs, find the earliest divergent state and fix the owning component rather than patching downstream symptoms.

For behavioral work:

- resolve material ambiguity before implementation;
- use the smallest general rule supported by current authority;
- preserve directional/mirror obligations;
- preserve numerical, chronology, identity, provenance, lifecycle, ordering, and serialization contracts unless an approved change intentionally modifies them;
- never create fixture-, timestamp-, symbol-, filename-, or expected-output-specific production logic.

For refactoring/performance work, follow [Zero-Difference Refactor](../development/zero-difference-refactor.md).

For Algorithm Reference construction/maintenance responsibilities, use [Algorithm Reference Maintenance](../development/algorithm-reference-maintenance.md) and discover the accepted References dynamically under `engine/algorithms/`.

## 7. Verification routing

Discover the current applicable verification rather than copying old suite totals or historical PASS results.

Use specialized owners where relevant:

- [Testing](../development/testing.md) for current test discovery, execution, RAW/regression policy, and result interpretation;
- [Repository Integrity](../verification/repository-integrity.md) for repository/integrity verification;
- [Zero-Difference Refactor](../development/zero-difference-refactor.md) for behavior-equivalence and performance verification;
- [Local State](../operations/local-state.md) for storage/state ownership.

Verification depth must match risk. Report outcomes using the statuses defined by root AGENTS. Never convert a historical result into a current PASS.

## 8. Documentation synchronization

After an approved change, update only the maintained owner documents whose governed facts changed.

Apply these rules:

- one durable fact has one maintained owner;
- link to owners instead of copying mutable facts;
- preserve Historical/Generated evidence as evidence;
- update `last_modified_at` for every maintained Markdown file whose content changes;
- add `created_at` to newly created maintained Markdown files;
- use real ISO 8601 timestamps with seconds and timezone offset;
- do not treat timestamps as authority.

Do not duplicate detailed trading semantics into generic engineering documentation.

## 9. Diff and publication

Before publication:

1. inspect the exact task diff;
2. verify only task-owned changes are included;
3. confirm no unintended Source, tests, RAW, References, Plugin/Vault content, or unrelated user work changed;
4. validate changed links and timestamp metadata;
5. verify required tests/checks completed or are honestly reported.

Commit or push only when the current user instruction explicitly authorizes it and root AGENTS permits it.

Release mechanics are owned by [TradingBot release operations](../../../scripts/git/README.md). Do not recreate release mechanics here.

After any authorized remote write, verify the resulting remote branch/commit and key paths. A write request alone is not proof of successful synchronization.

## 10. Final delivery

Report:

- what changed and what intentionally did not change;
- affected owners;
- verification status and limitations;
- exact changed paths;
- timestamp metadata for created/edited maintained files;
- commit/branch/remote state when publication occurred;
- final artifact locations when delivery is required.

Deliver every newly created or substantially rewritten file required by the task as a byte-equivalent artifact.

## 11. Review triggers

Review this workflow when the stable AI/engineering execution process, authority relationship, task-to-owner routing, documentation synchronization sequence, publication handoff, or final-delivery contract changes.

Do not revise it merely because modules, tests, hashes, versions, commits, routes, endpoints, or benchmark values change.
