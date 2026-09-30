---
title: TradingBot Testing
document_role: procedure
lifecycle: maintained
owner: testing
scope:
  - engine
  - chart
  - vite
  - faraz
  - integration
  - regression
supersedes: engineering/archive/documentation/local-tests-legacy-2026-09-30.md
created_at: 2026-09-30T11:40:11+03:30
last_modified_at: 2026-09-30T11:40:11+03:30
---

# TradingBot Testing

## 1. Purpose

This document is the maintained owner for **how the Current TradingBot project is verified**.

It defines test discovery, risk-based scope selection, execution-status rules, regression evidence, RAW-based verification, directional verification, determinism, browser/runtime relationships, and reporting obligations.

It does not define trading semantics, repository-integrity policy, system architecture, or the specialized methodology for behavior-preserving performance/refactor work.

Use the root [`AGENTS.md`](../../../AGENTS.md) for project authority and safety, [Documentation Governance](../documentation-governance.md) for document ownership/lifecycle, and [Zero-Difference Refactor](zero-difference-refactor.md) when the task is specifically a behavior-preserving refactor or optimization.

## 2. Testing authority boundary

Testing answers:

> How do we verify the Current project correctly?

Testing evidence can prove or disprove a stated expectation. It does not invent the expectation.

Trading expectations come from the authority model in root AGENTS. Current tests, fixtures, regression outputs, RAW, and runtime evidence remain verification evidence beneath canonical intended semantics and current executable Source.

A failing test can reveal a mismatch. A passing fixture cannot become a new production rule.

## 3. Dynamic test discovery

Never define the test surface by a permanent test-file count, test-case count, suite total, runner version, or one directory.

At task time:

1. recursively inspect the current repository for test roots;
2. inspect manifests and runner configuration;
3. inspect test-support modules, fixtures, regression helpers, browser/end-to-end tooling, and verification scripts relevant to the affected owner;
4. identify which tests are tracked, generated, local-only, historical, or runtime-created from current repository policy rather than assumption;
5. identify the normal supported invocation from current manifests/tooling;
6. follow dependencies far enough to understand what the tests actually exercise.

Current paths such as Chart tests under `apps/chart/tests/` and Engine verification under `engine/tests/` are useful discovery anchors, not a permanent exhaustive inventory.

Do not document that tests are permanently ignored, permanently local-only, or permanently concentrated in one tree.

## 4. Current runner discovery

Before executing tests, inspect the live project for:

- package-manager scripts and lockfiles;
- Python test configuration and installed test dependencies;
- repository scripts that wrap testing;
- browser/runtime harnesses;
- regression and comparison utilities;
- verification helpers;
- fixture and RAW locations;
- environment/runtime prerequisites.

Use the current supported command from those sources. Do not copy an old command merely because it worked in a previous report.

If no supported runner exists for a required check, report that limitation explicitly instead of inventing a false PASS.

## 5. Risk-based scope selection

Testing scope depends on the change.

Use this flow:

1. identify the owning subsystem and changed contract;
2. discover the relevant current tests and evidence;
3. run the narrowest checks that can fail directly on the changed behavior;
4. expand to dependent/subsystem checks;
5. expand to broader regression when state, chronology, lifecycle, serialization, persistence, transport, or public-output effects can propagate;
6. use RAW-based verification when real chronology or market-state reconstruction matters;
7. verify both directions when directional behavior can be affected;
8. run browser/runtime checks when the changed contract exists only or materially at runtime;
9. review reproducibility and the final task diff.

A documentation-only change normally requires documentation/link/static validation, not trading regression, unless the documentation change itself exposes a possible implementation/reference defect.

## 6. Verification status model

Use only:

- `PASS`
- `FAIL`
- `NOT RUN`
- `INCOMPLETE`
- `NOT APPLICABLE`

### PASS

Use `PASS` only when the check actually ran to completion and every required assertion/comparison succeeded.

### FAIL

Use `FAIL` when the check completed and a required assertion/comparison was violated.

### NOT RUN

Use `NOT RUN` when the check was not executed.

### INCOMPLETE

Use `INCOMPLETE` when execution started but did not produce a valid complete result, including timeout/interruption/partial evidence cases.

### NOT APPLICABLE

Use `NOT APPLICABLE` only when the check is demonstrably irrelevant to the change.

Never promote compile/import success, static inspection, an old report, or a visually plausible output into a trading-correctness `PASS`.

## 7. Verification layers

Keep evidence categories distinct.

### Structural checks

Examples include syntax parsing, importability, configuration parsing, link checking, schema checks, and repository-policy checks.

They can establish structural correctness only.

### Unit and contract checks

Use focused tests for local invariants, boundaries, ownership contracts, and deterministic helper behavior.

### Integration/subsystem checks

Use them when behavior crosses Chart/server/Engine/FARAZ or multiple Engine stages.

### Regression checks

Compare current behavior against an appropriate accepted baseline or expected contract. Preserve exact identity, ordering, provenance, chronology, and public output where those are part of the contract.

### Runtime/browser checks

Use actual runtime/browser execution for contracts that static/unit tests cannot establish, including rendering, focus, interaction, browser APIs, process coordination, and end-to-end transport.

### RAW-based checks

Use authoritative market data when chronology, lifecycle, crossings, prices, or historical state propagation matter.

No one layer silently substitutes for another.

## 8. RAW verification policy

RAW is immutable evidence.

Required rules:

- never modify RAW to make a test pass;
- calculation scope may require history earlier than the user-visible presentation range;
- choose overlapping datasets by required time coverage and finest authoritative chronology;
- for event ordering, prefer `1s RAW > 5s RAW > coarser data` when available;
- do not reconstruct exact intrabar chronology from a coarser candle when finer authoritative RAW exists;
- preserve the original evidence when malformed input is discovered;
- discover current RAW datasets at task time rather than maintaining a permanent filename inventory here.

When a test uses only a bounded RAW subset, state that scope. Do not generalize a bounded result into full-market correctness.

## 9. Fixtures and regression anchors are evidence, not rules

Fixtures and regression anchors may:

- reproduce known behavior;
- protect a corrected general rule;
- exercise boundaries and historical defects;
- compare before/after stable output.

They must not:

- define a new production rule;
- justify timestamp-specific, symbol-specific, price-specific, RAW-filename-specific, index-specific, or OHLC-fingerprint-specific production logic;
- substitute for canonical semantics;
- silently convert a historical expectation into Current authority.

State the general rule first; use the fixture only as evidence that the rule is implemented.

## 10. Determinism verification

When the system contract requires deterministic calculation, repeat equivalent executions with the same relevant Source/configuration/input and compare the stable outputs that matter.

Compare directly where practical:

- object identities;
- event/order chronology;
- source and owner fields;
- provenance/cause data;
- stable ordering;
- Decimal-sensitive values;
- lifecycle/public state;
- serialized stable content.

Hashes may support evidence storage or byte identity, but hash equality alone is not the semantic definition of correctness.

Nondeterministic telemetry such as timing may be excluded only when the current contract explicitly treats it as non-stable evidence.

## 11. Bullish and Bearish verification

When a change can affect directional behavior:

1. identify shared and direction-specific code paths;
2. test the directly affected direction;
3. test the opposite direction independently;
4. verify mirror/invariant obligations from current canonical authority;
5. verify legitimate direction-specific exceptions separately.

Mirror parity is useful evidence but does not by itself prove that either direction is independently correct.

Do not mechanically mirror a test expectation when canonical semantics define an approved directional difference.

## 12. Boundary and invariant testing

Where applicable include explicit cases for:

- strict crossing versus equality;
- inclusive/exclusive range boundaries;
- first/last selection and tie-breaking;
- Decimal-sensitive comparisons;
- canonical identity;
- provenance and parent/cause preservation;
- event ordering;
- lifecycle boundaries and reset behavior;
- serialization/public contract;
- invalid cases that must not trigger.

The exact expected rule comes from current authority, not from this document.

## 13. Regression and verification tooling

Discover current helpers dynamically.

The live repository may contain tools for purposes such as:

- exact before/after result comparison;
- Order/OrderAudit regression;
- Reference/source reconstruction checks;
- RAW provenance/chronology verification;
- benchmark/performance comparison;
- saved-evidence verification.

Treat current helper names and locations as implementation details. Inspect each helper before use to understand:

- accepted inputs;
- comparison semantics;
- excluded telemetry;
- output/evidence format;
- whether it reads or writes RAW;
- whether it is current or historical.

A helper is not authoritative merely because it exists.

## 14. First-difference regression triage

For a regression mismatch, use the root AGENTS first-difference workflow rather than duplicating it here.

Conceptually:

`Input / RAW → current Source state → actual → expected → earliest difference → owning component → correction → regression`

For a pure behavior-preserving refactor, the first unexplained stable-output difference is a refactor failure until resolved under [Zero-Difference Refactor](zero-difference-refactor.md).

## 15. Browser and UI testing relationship

Testing owns verification methodology; [UI/UX Reference](../architecture/ui-ux-reference.md) owns the user-facing interaction contract.

Discover current frontend tooling and classify checks as appropriate:

- unit/component;
- server/integration;
- browser/end-to-end;
- runtime/manual;
- build/static.

Do not freeze a browser-tool version, browser count, test count, or one permanent end-to-end command here.

A browser/runtime contract is `NOT RUN` if only static Source/tests were inspected.

## 16. Engine and integration testing relationship

For Engine-affecting work, dynamically discover:

- affected production Source;
- relevant Engine unit/contract tests;
- integration or bridge tests;
- regression/verification helpers;
- accepted References;
- RAW needed to establish chronology.

For transport-only or presentation-only work, verify the correct owner boundary and do not claim Engine semantic correctness without Engine evidence.

## 17. Reference-maintenance testing

When Algorithm References change, use [Algorithm Reference Maintenance](algorithm-reference-maintenance.md).

Testing may execute the required structural/reconstruction/regression checks, but Reference ownership, completeness, synchronization, and embedded-Source policy belong to that procedure.

## 18. Zero-difference testing

When a change is explicitly implementation-only, use [Zero-Difference Refactor](zero-difference-refactor.md) to define the baseline/equivalence/performance gate.

This Testing document supplies the general status model, dynamic discovery, RAW, direction, and evidence rules; the refactor document owns the stronger equivalence contract.

## 19. Evidence and reporting obligations

For every meaningful verification report record:

- what was tested;
- current input/evidence source;
- direction/timeframe/scope where relevant;
- command or runner actually used;
- environment constraints that materially affect interpretation;
- status using the standard model;
- exact failures or limitations;
- whether evidence is structural, synthetic, bounded regression, browser/runtime, or real RAW.

Do not report a suite as “all passed” without identifying the actual executed scope.

Do not convert historical evidence into a current run.

## 20. Acceptance scenarios

This procedure remains valid when:

- test count doubles;
- tests move into different directories;
- a new frontend runner appears;
- historical evidence records an old PASS total;
- overlapping RAW datasets provide different chronology precision;
- one regression fixture exposes a strange candle;
- a current test helper is renamed or replaced.

Expected behavior is dynamic discovery and evidence classification, not a rewrite of this document for ordinary inventory changes.

## 21. Review triggers

Review this document when the testing ownership model, supported execution model, status model, RAW verification policy, directional verification policy, or evidence/reporting methodology changes materially.

Do not rewrite it merely because test totals, runner versions, filenames, hashes, commits, or ordinary test layout change.

## 22. Historical provenance

The previous maintained testing document is preserved as Historical evidence at [legacy Local Tests](../../archive/documentation/local-tests-legacy-2026-09-30.md).

That file records an older local-only verification model and is not Current testing authority.
