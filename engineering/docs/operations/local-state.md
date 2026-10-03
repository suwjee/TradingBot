---
title: TradingBot Local State
document_role: reference
lifecycle: maintained
owner: local-state
scope:
  - runtime-state
  - persistence
  - sessions
  - cache
  - raw
last_modified_at: 2026-09-30T16:03:01+03:30
---

# TradingBot Local State

## 1. Purpose and boundary

This document owns the operational classification of TradingBot local state:

> What local/runtime/persistent state exists, who owns it, how persistent is it, and how can it be handled safely?

Use root [`AGENTS.md`](../../../AGENTS.md) for project authority and safety, [Documentation Governance](../documentation-governance.md) for document lifecycle/ownership, [Technical Architecture](../architecture/technical-architecture.md) for subsystem boundaries, [UI/UX Reference](../architecture/ui-ux-reference.md) for interaction behavior, [Testing](../development/testing.md) for RAW/regression procedure, and [Repository Integrity](../verification/repository-integrity.md) for Git/tracking policy.

This document does not redefine trading semantics, UI behavior, test methodology, release mechanics, or repository tracking rules.

## 2. Current local-state model

TradingBot has more than one kind of local state. Classify an artifact by its owner, purpose, lifecycle, persistence, rebuildability, evidence value, sensitivity, and current runtime use before deciding how to handle it.

| State class | Current owner | Persistence | Rebuildability / recovery | Cleanup rule |
| --- | --- | --- | --- | --- |
| Dedicated filesystem state | Chart/Vite/FARAZ integration | Machine-local, under the Chart-owned state root | Depends on the child category | Never delete the whole state root by category name alone |
| Browser workspace/preferences | Chart | Browser-local persistent state | Some preferences can be recreated; user work may not be reconstructable exactly | Clear only through a scoped user/maintenance action |
| Saved drawings/templates | Chart | Persistent filesystem/browser state | User-created; not assumed rebuildable | Preserve unless deletion is explicitly requested and scoped |
| Calculation cache | Vite/Chart integration | Persistent filesystem cache | Rebuildable only when required Source, RAW, configuration, and request context remain available | Invalidate through the owning cache contract; do not infer safety from “cache” |
| FARAZ authentication/session | FARAZ integration | Persistent secret-sensitive state | Normally reacquired by authentication, not reconstructed from public project data | Treat as credentials; never commit, report, or copy casually |
| FARAZ acquisition temporary output | FARAZ integration | Ephemeral filesystem state | Recreated by the acquisition workflow | Remove only when no active job or unpublished result depends on it |
| Vite/process coordination state | Vite/local server | Process-local ephemeral state | Recreated on process start | Ends with the owning process unless explicitly persisted elsewhere |
| Engine calculation state | Engine | Process/in-memory calculation state | Recomputed from authoritative inputs | Do not describe it as persistent unless Current Source introduces persistence |
| RAW market data and sidecars | Chart/FARAZ data owner; used as verification evidence | Persistent | Not assumed reproducible from local Source | Preserve as immutable evidence; never edit to make a test pass |
| Verification/archive evidence | Engineering verification/archive owners | Persistent evidence | Often not reproducible exactly | Preserve according to evidence lifecycle; not ordinary runtime cache |
| Logs/diagnostics | Producing subsystem | Runtime or generated evidence | Varies | Classify sensitivity/evidence value before removal; no retention period is implied |

The categories above are conceptual. Discover Current concrete paths and producers from live Source/configuration instead of maintaining an exhaustive filename inventory here.

## 3. Dedicated filesystem state root

The Current resolver owns one Chart state subtree inside the project checkout. Its default is:

`apps/chart/state`

A configured `TRADINGBOT_LOCAL_STATE_ROOT` is accepted only when it resolves to that dedicated subtree or a descendant; the resolver also checks the physical path so a junction/symlink cannot redirect state outside the allowed owner boundary.

The Current resolver exposes conceptual children for:

- RAW data;
- persistent cache/state;
- secret-sensitive state;
- temporary state.

The launcher and Vite/server use the same resolver. This is an operational ownership contract, not permission to treat every child as equivalent or disposable.

Do not relocate or create a second state root by documentation convention. If the resolver/storage contract changes, update this document from Current Source.

## 4. Chart and browser state

Chart owns user-facing workspace persistence. Current Source uses browser persistence for state such as workspace selection, preferences, review/UI state, and feature-specific state. Current Source also supports browser cache/IndexedDB layers for indicator-related data and scoped clearing.

Filesystem persistence under the Chart cache owner currently includes durable concepts such as:

- drawings;
- indicator calculation results;
- indicator templates.

These categories have different recovery properties. Saved drawings and templates can contain user-created state and are not presumed reproducible. Calculation results are caches, but they remain valid only under the owning input/Source identity contract.

Do not duplicate detailed interaction semantics here. Use [UI/UX Reference](../architecture/ui-ux-reference.md).

## 5. Vite/local-server state

Vite/local-server owns orchestration state required while the workstation runs, including in-memory request/progress coordination and short-lived runtime metadata.

Process-local maps, channels, subprocess coordination, and similar transient structures are not persisted operational state merely because they influence a request.

The server also owns the persistent calculation/drawing/template storage boundary assigned to the Chart state root. Persistent filesystem state and process memory must not be conflated.

Generated build output and installed dependencies are rebuildable development artifacts, not workstation user state. Their Git/release classification belongs to [Repository Integrity](../verification/repository-integrity.md) and the release subsystem.

## 6. FARAZ authentication and session state

FARAZ integration owns authentication/session lifecycle.

Current Source stores the reusable session in the dedicated secret owner. The Current writer uses an editable clear-text session format; legacy Windows DPAPI material can be migrated into that format. The session can contain cookies, access credentials, browser storage state, and captured endpoint metadata.

Therefore the entire FARAZ session artifact is **secret-sensitive**, regardless of filename or legacy naming.

Never copy actual credentials, cookies, tokens, session identifiers, browser storage values, or private profile data into:

- Git;
- maintained documentation;
- tests or fixtures;
- logs/reports without safe redaction;
- delivered artifacts;
- commit messages;
- release metadata.

A logout/session-clear action may remove the saved session. Expiry or invalidation is an authentication lifecycle event, not evidence that unrelated local state is disposable.

## 7. FARAZ acquisition state and RAW publication

FARAZ acquisition uses process-local job/browser state while work is active and a dedicated temporary area for unpublished export material. Temporary payloads exist to support safe validation/publication and may be required until the owning operation completes.

Validated market data is published into the RAW owner and accompanied by metadata where the current store requires it. Once published as RAW evidence, it is no longer temporary acquisition state.

Do not use a temporary-file suffix as proof that deletion is safe while an owning process may still depend on it.

## 8. Engine transient calculation state

Current Engine production Source is calculation-oriented and does not establish an Engine-owned persistent filesystem store. Calculation ledgers, indexes, caches, stage state, and reconciliation state are process/in-memory implementation state unless Current Source explicitly persists them.

An in-memory optimization cache is not an operational datastore and is not authority. Engine truth remains the authoritative calculation/state structures defined by Current Source.

If future Engine Source introduces persistence, update this document only when the ownership/lifecycle contract materially changes.

## 9. RAW data policy

RAW is authoritative market evidence, not disposable cache.

Rules:

- never modify RAW to make an output or test pass;
- never silently normalize or rewrite evidence during cleanup;
- never delete RAW merely because it is untracked, ignored, old, generated-looking, or duplicated-looking;
- overlapping datasets may legitimately coexist;
- discover current datasets dynamically;
- when event order matters, use the finest authoritative RAW chronology according to [Testing](../development/testing.md);
- preserve original evidence when a malformed input is discovered; corrections belong in separate explicit fixtures/evidence where appropriate.

Current repository policy may intentionally track curated baseline RAW while ordinary machine-local RAW remains excluded. That tracking distinction does not change RAW's evidence semantics.

## 10. Cache policy

“Cache” is a lifecycle claim that must be proven, not inferred from a filename.

For every cache class determine:

1. owner;
2. authoritative source of truth;
3. complete invalidation context;
4. whether it contains user-created state;
5. whether it can be rebuilt exactly;
6. whether it is currently in use;
7. whether it has verification/evidence value;
8. Git/release classification from the owning policy.

The Current Chart cache subtree is intentionally mixed: calculation results are rebuildable under the correct context, while drawings/templates can contain durable user-created state. A blanket cache-directory deletion is therefore unsafe.

Browser storage, browser Cache Storage, and IndexedDB also require scoped ownership-aware clearing. Use the application's supported clear behavior where applicable instead of deleting unrelated browser data.

## 11. Temporary files, runtime artifacts, and logs

Temporary state can include unpublished acquisition payloads, process/intermediate files, lock/process artifacts, and validation residue. It is safe to remove only after the owning process has stopped or released it and after confirming no unique user/evidence value remains.

Current project evidence does not establish one universal log-retention policy. Do not invent a retention period.

Diagnostics can contain request/response or operational context. Treat diagnostic output as potentially sensitive until reviewed; redact secret values before retaining, reporting, or delivering it.

## 12. Secret handling

Secret-sensitive state includes FARAZ authentication/session material and any future credential-bearing local state.

Minimum handling contract:

- keep it under the Current secret owner;
- do not stage or commit it;
- do not expose values in terminal/chat/report output;
- do not copy it into fixtures or verification bundles;
- do not include it in normal source/release packages;
- remove temporary secret copies after the owning operation when safe;
- if backup is explicitly required, protect it as credential material rather than ordinary project data.

A file being inside the repository directory does not make it repository content.

## 13. Backup and recovery

No formal project-wide backup mechanism for all local state is established by Current Source/documentation. Recovery therefore depends on state class:

- **Tracked repository content:** recover through Git according to repository/release policy.
- **User-created Chart state:** drawings/templates/browser state can be unique; preserve or back up deliberately before destructive maintenance.
- **RAW evidence:** preserve independently when it is unique or needed for regression; do not rely on reacquisition as guaranteed recovery.
- **Calculation caches:** rebuild only when their authoritative inputs and Current calculation contract remain available.
- **FARAZ session:** normally recover by authenticating again; do not treat copying a clear-text session as a normal backup strategy.
- **Verification/archive evidence:** preserve when it records a non-reproducible execution or provenance fact.
- **Temporary/process state:** normally recreated by the owning workflow after a clean restart, once no unpublished result depends on it.

Do not claim a recovery guarantee that the owning subsystem does not implement.

## 14. Git expectations

Git classification is owned by [Repository Integrity](../verification/repository-integrity.md), not by this document.

Operationally:

- machine-local cache, secret, temporary state, and ordinary acquired RAW are excluded by Current repository policy;
- curated baseline RAW may be intentionally tracked as reproducibility evidence;
- browser-origin state is outside the Git index entirely;
- ignored, untracked, generated, old, or cache-like does **not** mean disposable.

Always determine actual index/ignore state from live Git before staging or cleanup.

## 15. Conservative cleanup gate

Before deleting any local artifact answer all of the following:

- Who owns it?
- Is it persistent or ephemeral?
- Is a process currently using it?
- Is it user-created?
- Is it secret-sensitive?
- Is it authoritative RAW or verification evidence?
- Is it tracked, ignored, or merely untracked?
- Can it be rebuilt exactly, and from what?
- Would deletion invalidate a saved workspace, session, calculation, or audit trail?
- Has any required backup/recovery step been completed?

Never infer:

`untracked = disposable`  
`ignored = disposable`  
`generated = disposable`  
`old = disposable`  
`cache = disposable`

Phase/documentation work must describe cleanup safety; it must not perform broad cleanup.

## 16. Operational discovery procedure

When local-state handling is part of a task:

1. resolve the live project root;
2. inspect the Current state resolver/startup configuration;
3. identify browser-local versus filesystem versus process-local state;
4. inspect the owning Source before classifying persistence;
5. inspect actual Git state separately;
6. protect secrets from output;
7. classify RAW/evidence before any deletion or migration;
8. use the smallest owner-supported mutation;
9. verify the resulting state without exposing sensitive values.

## 17. Acceptance scenarios

This document remains valid when:

- a new cache is added — ownership/rebuildability must be established before deletion;
- an unknown untracked file appears — untracked status alone never authorizes deletion;
- a new authentication artifact appears — it remains secret-sensitive and non-committable until classified;
- RAW is required for regression — it remains immutable evidence;
- a file named “cache” contains unique state — unique/user evidence wins over the name;
- Engine creates temporary calculation state — it remains distinct from persistent local state;
- workspace persistence implementation changes — this document changes only if ownership/lifecycle materially changes.

## 18. Review triggers

Review this document when any of these durable contracts changes:

- local-state root or containment policy;
- subsystem ownership of persistent state;
- session/secret persistence model;
- Chart workspace persistence ownership;
- RAW ownership/lifecycle;
- cache rebuildability/invalidation contract;
- backup/recovery contract;
- cleanup-safety policy.

Do not rewrite it merely because filenames, dataset counts, cache entries, Source hashes, versions, or Git HEAD change.
