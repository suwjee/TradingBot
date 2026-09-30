# TradingBot Project Operating Contract

This root `AGENTS.md` is the durable navigation and operating contract for AI-assisted work in TradingBot. It defines authority, discovery, ownership boundaries, safety rules, engineering workflow, and verification obligations. It is intentionally discovery-first: mutable repository facts must be re-discovered from the live project instead of being frozen here.

Historical snapshots, old audit reports, generated artifacts, previous AI output, and memory are evidence only. They must never silently override maintained instructions, canonical trading knowledge, accepted references, or the current executable project.

## 1. Purpose and Scope

Use this file to determine:

- which authority to consult;
- how to discover the current project safely;
- which subsystem owns a change;
- how to investigate trading behavior;
- how to protect user work;
- what verification is required;
- how to report evidence honestly.

This file is **not** a second TradingBot algorithm specification. Detailed and changeable Reaction, Reset, Blue, A, S, E, Order, OrderAudit, StopAll, lifecycle, dominance, ownership, directional-exception, and edge-case semantics belong to the current canonical trading-knowledge system and accepted Algorithm References.

## 2. Governing Authority

For TradingBot work, apply this authority order:

1. Current explicit user instruction.
2. This root `AGENTS.md` and any nearer applicable `AGENTS.md`.
3. TradingBot Intelligence Plugin retrieval.
4. Canonical / normative TradingBot Knowledge Vault content.
5. Current accepted Algorithm References.
6. Current production Source and configuration as evidence of executable behavior.
7. Current tests, approved regression evidence, authoritative RAW, and reproducible runtime evidence.
8. Historical documents, archives, old audit reports, previous AI output, memory, and inference.

Important distinction:

- Plugin / Vault / accepted References define **intended trading semantics**.
- Current Source / configuration / runtime define **currently executable behavior**.

If intended semantics and executable behavior disagree:

- do not silently reconcile them;
- do not guess which side is correct;
- report the exact mismatch;
- determine whether implementation, canonical knowledge, references, or the requirement must change.

Hashes, versions, counts, timestamps, and recorded environment details may support evidence, but they are not semantic authority.

## 3. Mandatory Project Discovery

Before substantial work, discover the live project rather than relying on remembered structure.

1. Locate the actual repository root from the current environment and repository metadata. Do not assume a fixed drive or absolute path.
2. Inspect current Git status when a working tree is available.
3. Preserve all existing user work, including staged, unstaged, untracked, deleted, renamed, and local-only files.
4. Recursively inventory the current repository tree at the level needed for the task.
5. Read this `AGENTS.md` completely and read any nearer applicable project instructions.
6. Inspect the maintained engineering-documentation index and the current documentation relevant to the task.
7. Inspect current `.gitignore`, `.gitattributes`, root `README.md`, manifests, configuration, startup files, and release/tooling documentation when they affect the task.
8. Discover the current test layout and test configuration dynamically.
9. For Engine work, recursively inventory the current live Engine tree and determine the production-owned Source dynamically.
10. For trading semantics, query the TradingBot Intelligence Plugin and canonical Vault if available, then inspect current accepted Algorithm References as required.
11. Follow imports, runtime entry points, manifests, configuration references, and dependency closure far enough to understand ownership and downstream impact.
12. Treat archived, generated, cached, historical, or verification-only material as supporting evidence unless current governance explicitly promotes it.

Do not use old chat memory, historical reports, archived files, remembered versions, remembered hashes, remembered module counts, or previous AI summaries as primary current truth.

If multiple copies of a document or source artifact exist, determine which copy is maintained/current before relying on it.

## 4. Trading Semantic Workflow

Before interpreting, debugging, validating, or changing a trading semantic rule:

1. Retrieve the relevant canonical trading knowledge.
2. Identify the current accepted reference material for that rule.
3. Read the current executable Source that implements the affected path.
4. Inspect relevant tests, regression evidence, and RAW/runtime chronology.
5. Separate **intended semantics** from **current executable behavior**.
6. Resolve any material ambiguity before making a behavioral decision.
7. Find the earliest divergent state or transition.
8. Fix the owning component with the smallest general rule that satisfies canonical semantics.
9. Verify both directly affected behavior and required downstream behavior.
10. Synchronize durable knowledge/references when the approved change requires it.

If the Plugin is unavailable, use the highest available authority and state the limitation. Do not invent missing canonical semantics.

### Durable trading-safety invariants

AGENTS may state only durable constraints needed to work safely:

- preserve project-required Decimal semantics for price-sensitive behavior;
- preserve strict versus inclusive boundaries exactly as defined by current canonical authority;
- preserve directional consistency and mirror obligations defined by current authority;
- use the finest authoritative chronology available when event order matters;
- preserve identity, provenance, ordering, and serialization contracts unless an approved change explicitly modifies them;
- do not infer a production rule from one fixture or historical example;
- do not hard-code known timestamps, candle identities, symbols, RAW filenames, timeframe identities, OHLC fingerprints, fixture IDs, or expected outputs unless they are explicitly part of the formal specification;
- resolve material semantic ambiguity before implementation.

Detailed current algorithm behavior must be retrieved dynamically rather than duplicated here.

## 5. Architecture Ownership

Use conceptual ownership, not an exhaustive filename inventory.

### Chart

The Chart/browser application owns:

- visualization;
- interaction;
- workspace and chart UI state;
- drawing presentation;
- review and presentation behavior;
- user-facing rendering of finalized results.

The Chart must not become a second trading algorithm.

### Vite / local server boundary

The Vite/server layer owns:

- local API and transport boundaries;
- orchestration between browser, local services, files, and Engine;
- process/subprocess coordination;
- request/response and progress transport;
- cache/response coordination where currently assigned;
- local service integration.

Vite must not become a second trading engine or silently redefine finalized Engine semantics.

### FARAZ

FARAZ integration owns:

- external market-data acquisition;
- authentication/session handling;
- history and update integration;
- RAW acquisition/integration.

FARAZ must not define TradingBot trading semantics.

### Engine

The Engine owns:

- authoritative trading calculation;
- trading state and stage execution;
- lifecycle and reconciliation owned by calculation logic;
- finalized trading results exposed to transport/serialization.

The Engine must not depend on browser presentation behavior.

### Boundary invariants

- presentation must not repair or redefine trading truth;
- transport/serialization must not silently become a second algorithm;
- external acquisition must not define trading rules;
- subsystem ownership must be verified from current Source before moving logic across boundaries.

Stable roots such as `apps/`, `engine/`, `engineering/`, and `scripts/` are discovery anchors in the current project, not permission to assume their internal inventory will never evolve.

## 6. Dynamic Source and Engine Discovery

Never define production Source by a permanent file count, exhaustive filename list, hash list, version list, or old snapshot.

For substantial Engine work:

1. Recursively inventory the current live `engine/` tree.
2. Identify production-owned Source from current structure, runtime loading, imports, manifests, references, and repository conventions.
3. Distinguish production Source from:
   - tests;
   - benchmarks;
   - fixtures;
   - generated output;
   - caches;
   - historical copies;
   - archived files;
   - verification-only helpers;
   - temporary files;
   - bytecode.
4. Inspect all relevant current production modules, not only the file named in the task.
5. Follow dependency and ownership relationships far enough to understand upstream/downstream effects.
6. Automatically include future production modules when live project evidence shows they participate in Engine behavior.
7. Treat familiar filenames as discovery anchors only, never as an exhaustive future inventory.

If Engine packages or directories are reorganized, rediscover the current production closure from live project evidence. No future production file may be missed merely because it was absent when this document was written.

### Hash and version policy

Hashes may support integrity checks, regression baselines, forensic analysis, migrations, and release evidence. They are not semantic authority and do not replace reading current Source.

Versions may be recorded as evidence or checked for compatibility when required. Do not hard-code mutable current versions as permanent truth. Discover tool, runtime, package, Source, and reference versions at task time when they matter.

## 7. Dynamic Test Discovery

Do not rely on fixed test-file counts, test-case counts, historical suite totals, or permanent assumptions about how test source is tracked or distributed.

For each task:

1. Discover the current test layout from the live repository.
2. Determine current ownership for affected areas such as Chart, Vite/server, FARAZ, Engine, integration/regression, documentation, and repository integrity.
3. Inspect current manifests, test configuration, runner scripts, fixtures, and verification helpers that affect the task.
4. Run the narrowest relevant current tests first.
5. Expand to broader regression or end-to-end checks according to risk and current project requirements.
6. Never reuse a historical PASS as a current PASS.
7. Separate structural checks, unit results, bounded regressions, mirror/metamorphic evidence, browser/runtime evidence, and independent real-data correctness.

Use these verification statuses:

- `PASS`
- `FAIL`
- `NOT RUN`
- `INCOMPLETE`
- `NOT APPLICABLE`

A status is `PASS` only when the check actually completed and its required assertions/comparisons succeeded.

Keep mutable commands and suite layout in dedicated testing documentation or current runner/manifests; do not duplicate them extensively here.

## 8. Git and Dirty-Work Safety

Preserve user work.

Do not, without explicit authorization:

- `git reset`;
- `git clean`;
- stash user work;
- discard user changes;
- overwrite unrelated files;
- restore files over user changes;
- broad-delete paths;
- stage unrelated files;
- rewrite history;
- force-push;
- push to a remote;
- publish a release.

Before editing:

- inspect working-tree state when available;
- distinguish pre-existing changes from task changes;
- avoid whole-file formatting or line-ending churn;
- keep changes limited to the requested scope.

Before claiming a commit, push, tag, release, deployment, or publication succeeded, verify the actual resulting state.

Previous authorization to publish does not carry forward to a later task.

## 9. Debugging and First-Difference Workflow

When actual output disagrees with expected behavior, debug from upstream to downstream.

Use the evidence chain:

`Input / RAW -> current Source -> state transition -> actual -> expected -> first difference -> owning component -> root cause -> correction -> regression`

Rules:

- find the earliest state where expected and actual behavior diverge;
- treat downstream differences as consequences until independently proven otherwise;
- inspect the owner of that first difference;
- do not patch serialization or UI to hide an upstream calculation defect;
- do not convert one known candle, timestamp, price, symbol, fixture, or expected JSON into a production special case;
- verify chronology with the finest authoritative data available;
- report competing explanations when evidence is not conclusive.

## 10. Verification Obligations

Verification depth must match change risk.

At minimum, consider:

- syntax/parse checks for changed code;
- import/runtime initialization through the supported current path;
- targeted unit/invariant tests;
- affected subsystem tests;
- strict/equality and boundary checks;
- upstream/downstream regression where behavior can propagate;
- serialization/public-contract checks;
- determinism checks;
- both directional paths when directional behavior is affected;
- historical regression anchors when still active;
- representative or full RAW regression when chronology/history/lifecycle risk requires it;
- performance and memory comparison for refactors, caches, indexes, or hot-path changes;
- final diff review.

Never claim stronger verification than was actually performed.

Compilation is not trading correctness. Static inspection is not runtime verification. Mirror parity is not independent opposite-direction correctness. A bounded fixture is not global market correctness.

## 11. Refactor and Performance Obligations

Correctness and semantic equivalence take priority over speed, code reduction, or elegance.

For implementation-only refactors:

- establish a reproducible baseline before changing production behavior;
- preserve stable observable behavior exactly;
- identify the owning component and current complexity;
- prefer eliminating repeated work and improving data access before micro-optimization;
- preserve chronology, tie-breaking, Decimal semantics, identity, provenance, lifecycle state, ordering, and public output;
- keep caches/indexes subordinate to authoritative state;
- avoid persistent or cross-run caches unless safety is formally established;
- verify deterministic output;
- compare performance only with comparable inputs and environments.

Use [Zero-difference refactor](engineering/docs/development/zero-difference-refactor.md) for specialized refactor/performance methodology. If that document conflicts with this root authority model, this `AGENTS.md` governs authority and current live project evidence governs mutable facts.

## 12. Documentation and Knowledge Synchronization

Documentation must follow current project truth rather than forcing the project to match an old document.

Classify documentation before relying on it:

- maintained normative guidance;
- maintained descriptive architecture;
- accepted Algorithm Reference;
- current verification procedure;
- historical evidence;
- generated evidence.

Historical snapshots may preserve old paths, counts, versions, hashes, or behavior records. Those facts remain historical and must not be promoted to current authority without fresh verification.

When an approved change affects durable behavior or architecture:

1. update the owning Source/configuration;
2. run required verification;
3. synchronize canonical Plugin/Vault knowledge when required;
4. synchronize accepted Algorithm References when required;
5. update maintained architecture/development/operations documentation affected by the change;
6. preserve useful historical evidence as historical rather than rewriting it as current.

Do not duplicate volatile algorithm semantics into general engineering documents.

Current documentation navigation begins at [Engineering documentation](engineering/docs/README.md). Verify the status/currentness of a linked document before treating its body as maintained authority.

For current local-state ownership, use [Project-local workstation state](engineering/docs/operations/local-state.md).

## 13. Release and Publication Rules

Release mechanics are owned by the current release subsystem, not by this file.

When release work is requested:

- inspect the current release implementation and [release operations](scripts/git/README.md);
- preserve dirty user work;
- use the maintained release tooling rather than inventing a parallel process;
- verify remote state and authentication safely;
- do not force-push or rewrite history unless the user explicitly authorizes a separately justified operation;
- do not push, tag, publish, or create a release without explicit authorization for the current task;
- report partial publication honestly.

Do not impose a permanent package format, package filename, release artifact, tag format, or packaging step on every engineering task unless current release tooling or the explicit task requires it.

## 14. Package / Archive Inputs

Prefer the current live repository when it is available.

If a task explicitly supplies an archive, package, extracted source bundle, or alternate checkout as authoritative input:

- inspect it recursively enough for the task;
- determine whether it or the live repository is the current authority;
- detect duplicate/stale/conflicting copies;
- do not assume a permanent package filename;
- do not treat a package as authoritative merely because a previous task used it.

## 15. Optional Tooling

Optional tools support navigation, analysis, or verification. They do not define TradingBot semantics.

This applies to tools such as Graphify, Semgrep, SonarQube, Trivy, Codex Security, Superpowers, MCP servers, and other plugins.

### Graphify

Graphify is navigation/evidence support, not semantic authority.

Every Graphify execution requires explicit user approval for that specific execution. Installation or previous approval does not authorize a new run.

If Graphify is used:

- validate important relationships directly against current Source;
- distinguish inferred graph edges from implementation facts;
- do not treat old graph snapshots as current dependency truth.

### Other tools

Scanner, security, testing, and analysis tools may surface evidence or risks. Validate meaningful conclusions against the current project before documenting them as facts.

## 16. Security and Local-State Safety

Keep credentials, sessions, tokens, private keys, and secret state private.

Do not copy secret values into:

- chat output;
- documentation;
- tests;
- logs;
- delivery packages;
- release metadata.

Discover current local-state ownership from the live project and maintained operations documentation rather than assuming an old storage layout. Do not modify RAW merely to make a test pass.

## 17. Authoring Standards

Developer-facing TradingBot technical content authored by an AI must be English unless the task explicitly requires a dedicated localization artifact.

This includes source identifiers, comments, docstrings, technical logs, test names, assertion messages, technical Markdown, algorithm references, commit messages, and changelog entries.

Persian may be used in user-facing conversation.

Existing language content required for compatibility, localization, data fidelity, or historical preservation must not be destructively rewritten without explicit authorization.

Prefer:

- clear ownership;
- descriptive domain terminology;
- small auditable changes;
- direct evidence;
- deterministic behavior;
- minimal duplication;
- links to the owning document instead of copying volatile content.

## 18. Truthfulness and Evidence Labels

Never claim to have read, run, tested, verified, benchmarked, modified, committed, pushed, deployed, synchronized, or validated something unless that action actually occurred.

When useful, label statements as:

- `VERIFIED FACT`
- `USER CLAIM`
- `DOCUMENTED CLAIM`
- `INFERENCE`
- `ASSUMPTION`
- `HYPOTHESIS`
- `UNVERIFIED RESULT`

For test/execution outcomes use the verification statuses defined in Section 7.

Do not convert old evidence into a new PASS.

## 19. Completion Checklist

Before declaring substantial TradingBot work complete, verify the applicable items:

- [ ] Current repository/project state was inspected.
- [ ] Current applicable instructions were read.
- [ ] User work was preserved.
- [ ] Trading semantics were resolved from the highest available current authority.
- [ ] Intended semantics and executable behavior were distinguished.
- [ ] Relevant current Source/configuration was discovered dynamically.
- [ ] Future production files were not excluded by a fixed inventory assumption.
- [ ] Relevant tests were discovered dynamically.
- [ ] No historical PASS was reused as a current PASS.
- [ ] Chart/Vite/FARAZ/Engine ownership boundaries were preserved.
- [ ] No fixture/timestamp/OHLC-specific production hardcoding was introduced.
- [ ] Hashes/versions/counts were used only as evidence, not permanent authority.
- [ ] Required direction/mirror impact was checked.
- [ ] Required regression/runtime/performance checks were run or honestly marked otherwise.
- [ ] Maintained documentation/knowledge was synchronized when required.
- [ ] Local links added or changed by the task were verified.
- [ ] Final diff was reviewed.
- [ ] No unrelated user work was overwritten.
- [ ] No unauthorized staging, commit, push, tag, release, or publication occurred.
- [ ] Final report distinguishes verified facts, limitations, and unperformed checks.

## 20. Future-Proof Acceptance

This operating contract is intentionally valid when mutable project details change.

A normal change in any of the following must not require editing `AGENTS.md` by itself:

- number of Engine production modules;
- test files or test cases;
- Source hashes;
- Git HEAD;
- package/runtime/tool versions;
- route or endpoint counts;
- repository file totals;
- benchmark numbers;
- internal package layout.

Update this file only when durable governance, authority, ownership boundaries, safety requirements, engineering workflow, or verification obligations change.