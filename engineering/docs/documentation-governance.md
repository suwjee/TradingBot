---
title: TradingBot Documentation Governance
document_role: normative
lifecycle: maintained
owner: documentation
scope:
  - engineering-documentation
  - documentation-classification
  - documentation-lifecycle
  - documentation-ownership
  - documentation-placement
  - documentation-maintenance
created_at: 2026-09-30T09:24:20+03:00
last_modified_at: 2026-09-30T20:12:59+03:30
---

# TradingBot Documentation Governance

## 1. Purpose and boundary

This document is the maintained governance reference for the TradingBot documentation system. It defines how project documents are classified, owned, placed, maintained, archived, generated, and consumed. It also defines the anti-duplication and update rules that keep documentation future-proof as the repository evolves.

This document does **not** replace or compete with the root [`AGENTS.md`](../../AGENTS.md). Root `AGENTS.md` remains the owner of project-wide authority, discovery, safety, engineering workflow, and durable operating obligations.

This document is also **not**:

- an Algorithm Reference;
- a second trading-semantic authority;
- a Technical Architecture manual;
- a UI/UX specification;
- a testing manual;
- a release guide;
- an audit or migration report.

Its responsibility is documentation governance only.

## 2. Core governance principle

Stable maintained documentation describes durable concepts such as authority, ownership, architecture, contracts, responsibilities, discovery rules, invariants, procedures, and verification obligations.

Mutable repository facts are discovered from the current live project when needed.

Snapshots belong to evidence. Historical evidence remains historical. Generated output remains generated unless governance explicitly promotes a human-maintained result into a maintained document.

A maintained document should require revision only when the concept it owns changes. A new file, test, route, commit, hash, package version, benchmark result, or dependency count does not by itself require a conceptual document rewrite.

## 3. Authority is separate from document classification

Document role and lifecycle describe what a document is; they do not redefine project authority.

For authority and conflict resolution, defer to current root [`AGENTS.md`](../../AGENTS.md). In documentation terms, this means:

- no Engineering Doc may override root `AGENTS.md`;
- no general Engineering Doc may become a second Algorithm Reference;
- no general Engineering Doc may override canonical Plugin/Vault trading semantics or accepted Algorithm References;
- no historical report may override maintained Current guidance;
- no generated artifact may silently become normative;
- no hash, version, commit, count, timestamp, or inventory snapshot becomes semantic authority merely because it is recorded in a document.

If intended trading semantics and executable Source disagree, report the mismatch through the root authority model. Documentation governance must not silently reconcile the disagreement.

## 4. Two-dimensional classification model

Every project document should be understood through two independent dimensions: **document role** and **lifecycle status**.

### 4.1 Document role

| Role | Meaning |
| --- | --- |
| `NORMATIVE` | Defines rules, obligations, governance, invariants, or contracts that must be followed. |
| `REFERENCE` | Describes the current system, architecture, interfaces, responsibilities, or implementation model. |
| `PROCEDURE` | Defines how to perform a repeatable engineering or operational process. |
| `EVIDENCE` | Records what was observed, tested, measured, migrated, audited, benchmarked, or verified at a particular point in time. |

Additional roles should be introduced only when current project evidence demonstrates a real ownership need. Do not expand the taxonomy for convenience.

### 4.2 Lifecycle status

| Lifecycle | Meaning |
| --- | --- |
| `MAINTAINED` | Actively maintained and intended to describe Current rules, Current procedures, or Current system state. |
| `HISTORICAL` | Preserved from an earlier point in time for evidence, provenance, or context. It is not Current authority. |
| `GENERATED` | Produced mechanically or automatically by tooling. It is not automatically maintained documentation. |
| `DEPRECATED` | Temporarily retained for compatibility or navigation but no longer the intended maintained owner. |

Role and lifecycle must not be collapsed into one list. For example:

- Technical Architecture: `REFERENCE` + `MAINTAINED`;
- Documentation Governance: `NORMATIVE` + `MAINTAINED`;
- a dated migration report: `EVIDENCE` + `HISTORICAL`;
- a generated dependency graph: normally `EVIDENCE` + `GENERATED`.

A newer timestamp does not outrank lifecycle or authority.

## 5. Documentation ownership model

One knowledge class should have one clear maintained owner. The current project owners are conceptual responsibilities; live repository discovery determines current filenames and implementation details.

| Owner | Owns | Must not become |
| --- | --- | --- |
| Root [`AGENTS.md`](../../AGENTS.md) | Project authority, root workflow, discovery, safety, durable engineering obligations | A detailed algorithm specification |
| This governance document | Documentation classification, lifecycle, ownership, placement, duplication, archiving, generated-material policy, maintenance triggers, creation/split/merge rules | A second `AGENTS.md`, architecture manual, test guide, release guide, or audit |
| TradingBot Intelligence Plugin / canonical Vault | Intended trading-semantic knowledge according to current root authority | Generic engineering documentation |
| Current accepted Algorithm References | Maintained formal/reconstructable algorithm specification according to current project policy | Generic governance or release policy |
| Current production Source/configuration | Current executable implementation behavior | Intended semantic authority when it conflicts with higher intended-semantic authority |
| [Technical architecture](architecture/technical-architecture.md) | Current architecture, subsystem boundaries, responsibilities, runtime/data flow, architecture-level contracts | Historical audit container or algorithm specification |
| [UI/UX reference](architecture/ui-ux-reference.md) | Current Chart/UI implementation reference and interaction/state contracts | Trading calculation authority |
| [Testing](development/testing.md) and current test runner/configuration | Test strategy, execution procedure, test ownership, RAW/regression evidence rules, result interpretation | A permanent inventory of test counts |
| [Algorithm Reference Maintenance](development/algorithm-reference-maintenance.md) | Algorithm Reference construction/synchronization procedure | A current Algorithm Reference itself or a permanent production-Source inventory |
| [Zero-difference refactor](development/zero-difference-refactor.md) | Behavior-equivalence refactor and performance methodology | General project authority |
| [Local state](operations/local-state.md) | Local-state/storage operational ownership and contracts | Release or algorithm authority |
| [Repository integrity](verification/repository-integrity.md) | Repository-structure and integrity verification rules while maintained | A historical migration record |
| [Release operations](../../scripts/git/README.md) and current release subsystem | Release mechanics | Documentation governance |
| Historical audits and migrations | Their dated observations and provenance only | Current guidance merely because they are detailed or newer-looking |

If a maintained file mixes Current guidance with historical audit material, separate the responsibilities during the owning documentation-maintenance change while preserving unique evidence as Historical material.

## 6. One fact → one maintained owner

Mandatory anti-drift rule:

`One durable fact → one maintained owner → references elsewhere`

Other documents may link to the owner, provide a minimal contextual summary, or identify where the rule is owned. They must not maintain a competing independent copy of the same mutable rule.

If duplication is unavoidable for usability:

1. identify the owning source explicitly;
2. keep the duplicate summary minimal;
3. avoid volatile implementation details;
4. resolve conflicts in favor of the actual owning authority;
5. remove or correct stale non-owning copies in the appropriate maintenance phase.

## 7. Dynamic-discovery policy

Maintained documentation must not use mutable repository inventory as permanent Current authority when live discovery can answer the question.

Do not freeze as durable Current truth:

- exact Engine production-file counts;
- exhaustive Engine filename inventories;
- exact test-file or test-case counts;
- exact route or endpoint counts;
- repository file totals;
- current Git HEAD or commit SHA;
- mutable file hashes;
- mutable package/tool/runtime versions;
- mutable benchmark results;
- mutable dependency totals.

Operational need: discover the current value from the live project.

Historical need: preserve the observed value as `EVIDENCE` with its execution context.

Examples:

- Maintained: “Discover the current production Engine Source recursively.”
- Evidence: “At verification time X, the discovered production set contained N files.”
- Maintained: “Run the current applicable test suites.”
- Evidence: “At verification time X, N tests passed.”

Numbers are not prohibited. Mutable snapshot numbers are prohibited from becoming durable authority.

## 8. Hash, version, count, and timestamp policy

### 8.1 Hashes

Hashes may support integrity evidence, forensic comparison, migration proof, regression baseline identity, release evidence, and artifact manifests.

Hashes are not semantic authority, Source-discovery authority, architecture definition, or a substitute for reading and comparing current Source.

Maintained conceptual documentation must not require manual rewriting merely because legitimate Source hashes change.

### 8.2 Versions

Distinguish **observed version** from **required compatibility version**.

Observed mutable versions normally belong to manifests, Source metadata, release metadata, or verification evidence. Maintained conceptual documentation should usually instruct readers to discover the Current version at task time.

An exact version may remain in maintained documentation only when it defines a real compatibility or protocol contract.

### 8.3 Counts

Counts are permitted as dated evidence. They must not define ownership, discovery scope, or future completeness.

### 8.4 Timestamps

Document timestamps provide edit provenance only. They do not determine semantic authority, lifecycle, ownership, or correctness.

A newer `last_modified_at` does not make a Historical or Generated document authoritative.

## 9. Current, Historical, Generated, and Deprecated material

### 9.1 Maintained Current documentation

Maintained documents:

- describe Current rules, procedures, or system state;
- remain source-backed;
- should not contain large stale historical bodies;
- should not rely on a short “current note” to excuse a mostly historical body.

When a formerly Current document contains valuable historical material, later restructuring should preserve/archive that historical body and rebuild the maintained Current document separately.

### 9.2 Historical material

Historical material may legitimately preserve old paths, commands, counts, versions, hashes, architecture, Git state, and results. It must be clearly treated as historical and must not appear as Current guidance.

Do not silently rewrite historical evidence to make it resemble Current state.

### 9.3 Generated material

Generated material includes outputs such as Graphify artifacts, dependency graphs, generated manifests, scan/static-analysis reports, benchmark output, inventories, caches, and temporary reports.

Generated output does not automatically belong in maintained documentation and does not become normative merely because it is useful.

### 9.4 Deprecated material

Deprecated documentation remains only for a bounded compatibility/navigation purpose. Its intended replacement should be identifiable when one exists.

## 10. Placement policy

Placement follows responsibility and lifecycle, not filename age or convenience.

| Material | Conceptual location |
| --- | --- |
| Human-maintained Current guidance | `engineering/docs/` |
| Historical preserved material | the project’s current archive/history owner |
| Current verification evidence | `engineering/verification/` according to current repository policy |
| Generated/rebuildable output | the generated/verification/archive owner established by current repository policy |
| Trading Algorithm References | their current accepted owner under the Engine/reference system, discovered live |
| Release mechanics | current release subsystem under `scripts/git/` |

Do not hard-code a future generated directory that current repository governance does not guarantee.

Repository tracking policy and lifecycle are separate concepts. A tracked file can be Historical; an ignored file is not automatically disposable; a directory name such as `archive`, `verification`, `state`, or `raw` does not by itself determine Git policy or authority.

## 11. Archiving policy

Archive when:

- a maintained Current document is superseded but retains historical value;
- an audit is complete and becomes dated evidence;
- a migration report describes a completed historical event;
- a one-off prompt or plan is no longer an active workflow;
- a previous architecture or UI snapshot is retained for provenance.

Do not archive merely because a document is old. A durable maintained rule may remain maintained indefinitely while valid.

Prefer preserving unique engineering evidence over deleting it.

These rules define archiving policy but do not themselves authorize moving historical material; movement requires an explicitly scoped maintenance change that preserves unique evidence.

## 12. Conservative deletion policy

Delete documentation only when evidence establishes that it is:

- fully redundant;
- an accidental duplicate;
- rebuildable/generated and not required as evidence;
- invalid/corrupted without historical value; or
- explicitly approved for deletion.

Prefer archive over delete when unique historical engineering value exists.

Cleanup must never be used to erase unique provenance.

## 13. Maintained-document metadata standard

Use lightweight metadata. YAML frontmatter is preferred for maintained Markdown when compatible with current tooling.

For maintained Markdown created or edited during documentation-stabilization phases, use the following fields where applicable:

- `title` — human-readable maintained document title;
- `document_role` — `normative`, `reference`, `procedure`, or `evidence`;
- `lifecycle` — `maintained`, `historical`, `generated`, or `deprecated`;
- `owner` — conceptual responsibility owner;
- `scope` — optional bounded scope;
- `created_at` — required for newly created files;
- `last_modified_at` — required for every created or edited file.

Optional fields where useful:

- `supersedes`;
- `superseded_by`;
- `review_triggers`.

Timestamp format is ISO 8601 with second-level precision and timezone offset:

`YYYY-MM-DDTHH:MM:SS±HH:MM`

Rules:

- do not fabricate an unknown historical `created_at`;
- preserve a reliable existing `created_at` when present;
- update `last_modified_at` whenever the file content changes in a later phase;
- timestamps are provenance, not authority;
- do not require commit SHA, Source hashes, package versions, or exhaustive module inventory in maintained-document metadata.

For special-purpose Markdown whose parsing/discovery could be affected by frontmatter, use a safe explicit metadata block near the top instead.

## 14. Review and update triggers

Review a maintained document when the concept it owns changes, not merely when repository inventory changes.

| Owner document | Review/update triggers |
| --- | --- |
| Technical Architecture | Architecture ownership, subsystem boundary, runtime/data flow, or public architecture-contract change |
| UI/UX Reference | Workspace/state model, persistence contract, major interaction/navigation, or accessibility-contract change |
| Testing documentation | Test ownership, execution model, runner/tooling contract, or verification-methodology change |
| Algorithm Reference maintenance procedure | Reference synchronization process, Source-discovery contract, or accepted Reference structure change |
| Local State | Storage ownership, persistence model, migration policy, retention, or recovery change |
| Repository Integrity | Git policy, repository structural policy, or evidence/generated tracking rule change |
| Documentation Governance | Classification, lifecycle model, authority relationship, document ownership, placement, archive, or generated-material policy change |

Do not require a conceptual doc update merely because a file count, test count, version, hash, commit, benchmark, or dependency total changed.

## 15. Creating, splitting, and merging documents

### 15.1 New document creation

Before creating a maintained document, answer:

1. What unique responsibility will it own?
2. Is that responsibility already owned elsewhere?
3. Would extending an existing maintained document be clearer?
4. What is its document role?
5. What is its lifecycle?
6. Who owns it?
7. What event requires it to change?
8. Could it create duplicated authority?

Do not create another maintained document merely because an audit is long, a subsystem has many files, generated output is verbose, or an AI prefers another folder.

### 15.2 Split rule

Split a maintained document only when responsibilities are genuinely independent, maintenance triggers differ materially, audiences differ materially, coherent maintenance has become unsafe/difficult, or splitting reduces duplication/authority ambiguity.

Do not split based only on line count.

### 15.3 Merge rule

Merge/consolidate maintained knowledge when two documents independently own the same rule, duplicated facts repeatedly drift, or ownership boundaries cannot be explained cleanly.

Establish one owner; do not mechanically concatenate files. Preserve unique historical evidence separately when required.

## 16. Naming rules

Maintained filenames should describe stable responsibility.

Avoid naming maintained documents after:

- a temporary tool;
- current module/file/test count;
- current version;
- one audit date;
- one transient task;
- one implementation snapshot.

Names such as `technical-architecture.md`, `testing.md`, `repository-integrity.md`, and `documentation-governance.md` communicate durable responsibility. Historical/evidence filenames may intentionally include dates or snapshot identifiers.

## 17. README and navigation

[`engineering/docs/README.md`](README.md) is the maintained documentation navigation entry point.

README should:

- link to this governance document;
- link to maintained owner documents;
- describe each responsibility briefly;
- help distinguish Current maintained guidance from Historical/Generated/Evidence material.

README must remain navigation, not duplicate governance policy.

## 18. AI document-consumption rules

Before an AI agent relies on a document, it must determine:

1. its document role;
2. its lifecycle;
3. its owner;
4. whether it is maintained;
5. its relationship to root `AGENTS.md`;
6. whether it contains historical or generated material.

AI agents must not:

- silently reconcile contradictory documents;
- treat Historical/Generated evidence as Current authority;
- copy old snapshot values into maintained documentation;
- create accidental competing sources of truth;
- duplicate algorithm semantics into generic docs;
- infer authority from file age, timestamp, length, or filename;
- assume a filename containing “current” is authoritative without governance evidence.

Resolve Current-versus-Historical ambiguity before relying on a document.

## 19. Standard documentation change workflow

For a documentation change:

1. identify the fact/change;
2. determine its actual owner;
3. identify the owning document;
4. determine document role and lifecycle;
5. inspect Current Source/authority required for that fact;
6. modify only the owning maintained documentation;
7. update navigation/references where necessary;
8. update `last_modified_at` to the actual final edit-completion timestamp;
9. add `created_at` for newly created files;
10. preserve historical evidence separately where appropriate;
11. check for duplicated facts;
12. validate changed links and casing;
13. search changed text for stale paths/snapshot claims;
14. review the exact diff;
15. deliver every new or substantially rewritten file when task instructions require it;
16. report exact project-relative placement;
17. follow current Git/publication policy rather than inventing a separate publication process.

## 20. Conflict resolution

If two maintained documents conflict:

1. identify the owner of the disputed fact;
2. consult root `AGENTS.md`;
3. consult the actual authoritative Source/knowledge for that fact;
4. identify the non-owning or stale copy;
5. correct it in the appropriate maintenance phase.

Do not choose a winner merely because a file is newest, longest, has the highest version, or has the newest timestamp.

If maintained Current guidance conflicts with Historical evidence, maintained Current guidance governs Current use unless the historical evidence reveals a genuine unresolved discrepancy that must be investigated.

If a generic Engineering Doc conflicts with canonical trading semantics, follow the authority model in root `AGENTS.md`; do not infer a new trading rule from engineering documentation.

## 21. Architecture ownership guardrail

Documentation governance does not redesign TradingBot architecture.

The first-class ownership boundaries remain:

- **Chart** — visualization, interaction, workspace/chart UI state, drawings, and presentation of finalized results;
- **Vite/server** — local API/transport boundaries, orchestration, process coordination, persistence/response transport where currently assigned;
- **FARAZ** — market-data acquisition, authentication/session handling, and RAW/history integration;
- **Engine** — authoritative trading calculation, trading state/stages, lifecycle/reconciliation owned by calculation logic, and finalized trading results.

The detailed Current architecture belongs to the Technical Architecture owner and live Source, not to this governance document.

## 22. Release and publication boundary

Release mechanics belong to the [current release subsystem](../../scripts/git/README.md). Documentation governance must not define a competing release flow.

Documentation changes must follow the explicit publication authorization and phase boundary in the current task and root `AGENTS.md`.

## 23. Governance acceptance scenarios

| Scenario | Required governance result |
| --- | --- |
| A — New Engine module | No documentation rewrite merely because the file count changed; dynamic discovery finds it. |
| B — Architectural ownership change | Technical Architecture is reviewed. |
| C — Version-only change | Conceptual architecture is not automatically rewritten unless compatibility/architecture changed. |
| D — Historical contradiction | Historical evidence cannot override Current guidance. |
| E — Generated Graphify output | Generated output does not automatically become maintained architecture. |
| F — Generic doc conflicts with trading semantics | Generic docs cannot override canonical trading authority. |
| G — Duplicated mutable rule | Not acceptable; establish one maintained owner. |
| H — Audit snapshot contains hashes/versions/counts/commit | Allowed as Evidence. |
| I — Same snapshot treated as permanent maintained truth | Not acceptable. |
| J — Proposed doc has no unique responsibility | Do not create it. |
| K — Maintained file edited | Update real `last_modified_at` with seconds and timezone offset. |
| L — New maintained file created | Record both `created_at` and `last_modified_at`. |
| M — Historical file has newer timestamp | Timestamp recency does not override lifecycle or authority. |

## 24. Governance scope boundary

This governance owner defines documentation policy only. It does not by itself authorize or perform:

- moving or rewriting historical architecture/UI audit bodies;
- rehoming engineering workflow or migration evidence;
- rewriting Technical Architecture or UI/UX Reference;
- rewriting Testing or Algorithm Reference maintenance procedures;
- rewriting Zero-Difference, Local State, or Repository Integrity owners;
- changing Anti-Drift implementation;
- executing a comprehensive final documentation audit.

Those actions belong to their owning documents/subsystems and require explicitly scoped work under root `AGENTS.md`.

## 25. Final principle

Every future TradingBot document should make these questions answerable without guesswork:

- What kind of document is this?
- What is its lifecycle?
- What does it own?
- What does it not own?
- What authority does it have?
- What source wins on conflict?
- What event requires it to change?
- Where should a new fact be documented?
- Is a mutable fact discovered live or preserved as evidence?

Documentation drift is prevented by explicit ownership, classification, lifecycle, dynamic discovery, and references to the actual owner—not by copying mutable snapshots into more files.