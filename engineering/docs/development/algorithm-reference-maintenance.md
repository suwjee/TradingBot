---
title: TradingBot Algorithm Reference Maintenance
document_role: procedure
lifecycle: maintained
owner: algorithm-reference-maintenance
scope:
  - bullish-reference
  - bearish-reference
  - production-source-discovery
  - source-reference-synchronization
supersedes: engineering/archive/documentation/standalone-reference-specification-legacy-2026-09-30.md
created_at: 2026-09-30T11:40:11+03:30
last_modified_at: 2026-09-30T11:40:11+03:30
---

# TradingBot Algorithm Reference Maintenance

## 1. Purpose

This document is the maintained procedure for keeping the accepted Bullish and Bearish Algorithm References complete, reconstructable, and synchronized as TradingBot production Source evolves.

It answers:

> How do we keep the formal directional Algorithm References complete and synchronized as production Source evolves?

It does **not** reproduce the trading algorithm. Current intended semantics belong to the canonical trading-knowledge system and accepted Algorithm References; current executable behavior belongs to production Source.

Use root [`AGENTS.md`](../../../AGENTS.md) for authority and ambiguity handling, [Documentation Governance](../documentation-governance.md) for document lifecycle, and [Testing](testing.md) for execution/evidence rules.

## 2. Maintenance boundary

This procedure owns:

- discovery of the current accepted directional References;
- dynamic discovery of production Source relevant to the Reference contract;
- Source-to-Reference completeness checks;
- embedded-Source reconstruction/synchronization when the current format uses it;
- Bullish/Bearish synchronization;
- semantic-text synchronization;
- implementation-only versus semantic-change handling;
- stale manifest/snapshot detection;
- final Reference validation.

It must not become:

- a third Algorithm Reference;
- a copy of current Reaction/Blue/A/S/E/Order/lifecycle rules;
- a permanent list of production modules;
- a permanent version/hash manifest;
- a release guide.

## 3. Discover the current Reference contract first

Before editing a Reference:

1. read root AGENTS and applicable project instructions;
2. discover the current accepted Bullish and Bearish Reference files from the live project;
3. read both current References completely enough to understand their entire maintained format;
4. identify their semantic sections, reconstruction sections, manifests, embedded Source, schemas, history, verification sections, and directional structure;
5. identify any tooling that validates or reconstructs their content;
6. determine whether both documents use shared Source snapshots, direction-specific prose, or both;
7. treat archived/older References only as Historical evidence.

Do not select a Reference because its filename has the largest version number or newest timestamp without confirming current acceptance.

## 4. Dynamic production-Source discovery

Never define Reference coverage as exactly N files or one fixed filename/hash/version list.

At maintenance time:

1. recursively inspect the live Engine tree;
2. follow current runtime entry points, loading, imports, package initialization, configuration, and dependency ownership;
3. identify the production-owned Source participating in the Reference contract;
4. include production package/init Source when it is required for reconstruction;
5. distinguish production Source from tests, fixtures, benchmarks, caches, generated output, bytecode, Historical/archive material, verification-only helpers, and temporary files;
6. determine whether support artifacts outside the obvious pipeline tree are actually part of the formal reconstruction contract;
7. automatically include future production modules when live runtime/ownership evidence makes them part of the contract.

Familiar current paths are discovery anchors only.

## 5. Establish Source coverage

Build a task-time production inventory from current Source.

For every discovered production-owned item relevant to the Reference contract, determine:

- runtime/reconstruction role;
- owning subsystem/stage;
- dependency/import relationship;
- whether it must be embedded, described, indexed, or otherwise represented by the current Reference format;
- whether both directional References must represent the same bytes or different directional specification text.

Then compare that live inventory with the current Reference representation.

The maintenance procedure must detect both:

- a Source item missing from the Reference;
- a stale Reference item that is no longer part of current production ownership.

Do not accept “the manifest has the expected count” as completeness proof.

## 6. Current standalone/reconstruction contract

When the accepted Reference format is standalone/reconstructable, preserve that contract.

If the current format embeds production Source:

- embedded Source must be complete for every file required by that format;
- preserve exact bytes where byte-exact reconstruction is the contract;
- preserve imports, constants, schemas, package markers, and required comments;
- do not use ellipses, “same as previous”, omitted helpers, or dependency on an older Reference;
- extract/reconstruct embedded Source during validation and compare it directly with current production Source;
- compile or otherwise parse reconstructed Source where applicable.

If the accepted format later changes, re-evaluate what “standalone” and “complete” mean from the current accepted contract instead of preserving an obsolete embedding mechanism by inertia.

## 7. Source manifest and symbol/index material

If the current Reference format contains manifests, hashes, versions, byte counts, line counts, or symbol indexes:

- regenerate them from the current Source at maintenance time;
- verify they correspond to the Source actually represented;
- do not copy values from a previous Reference;
- do not use those values as semantic authority;
- regenerate line-address material after structural changes;
- detect stale or omitted entries.

Hashes and counts are integrity evidence. They do not prove semantic completeness by themselves.

## 8. Source-to-Reference synchronization

Reference maintenance requires both implementation and semantic comparison.

Where applicable verify:

- every required current production Source item is represented;
- embedded Source matches current Source according to the accepted exactness contract;
- no stale Source snapshot remains;
- package/init material required for reconstruction is included;
- function/class/schema/index material is complete;
- semantic prose describes the approved intended behavior;
- serialization/public-contract prose matches the accepted contract;
- reconstruction instructions remain executable/unambiguous;
- Historical/superseded rules are clearly separated from active rules.

A Reference is not synchronized merely because it exists or parses.

## 9. Semantic change versus implementation-only change

### Semantic change

A semantic change alters intended trading behavior.

After the intended rule is approved, synchronize all authorities required by root AGENTS, including as applicable:

- canonical knowledge;
- both accepted directional References;
- production Source;
- tests/regression evidence.

Reference prose, schemas, examples, history, and embedded Source must be updated wherever the approved rule affects them.

### Implementation-only change

An implementation-only refactor/performance change intends to preserve observable behavior.

Do not add a new trading rule to Reference prose.

However, if the accepted Reference embeds Source, implementation details, manifests, symbol indexes, or reconstruction material, the Reference may still require synchronization even when semantics are unchanged.

Therefore:

> “No semantic change” does not automatically mean “no Reference change.”

Inspect the current Reference structure.

## 10. Bullish/Bearish first-class synchronization

Treat both directional References as first-class maintained artifacts.

For every relevant change:

1. review both References;
2. classify affected content as direction-invariant or direction-sensitive;
3. keep shared implementation representation synchronized where the current format requires identical shared Source;
4. mirror only the directional semantics defined by current canonical authority;
5. preserve legitimate direction-specific exceptions;
6. preserve invariant concepts unchanged;
7. verify both documents remain independently complete where the accepted format requires standalone use.

Do not mechanically mirror text or code that canonical semantics define as direction-invariant or intentionally asymmetric.

## 11. Shared Source changes

When a shared production implementation changes, review both directional References even if only one user-visible direction was involved in the originating task.

If both References embed the same shared Source, verify that both reconstructed copies represent the same current Source bytes according to the accepted format.

If Reference prose is direction-specific, review whether the implementation change affects either explanation even when trading semantics are unchanged.

## 12. Direction-specific semantic changes

When an approved semantic change applies only to one direction or contains a legitimate directional exception:

- update the affected directional semantic text;
- explicitly review mirror impact;
- do not overwrite the opposite Reference mechanically;
- preserve approved invariant text;
- record the directional nature of the revision.

Independent correctness remains required; mirror similarity is not a substitute.

## 13. Material disagreement

If canonical knowledge, accepted Reference, and current Source disagree materially:

1. stop semantic normalization;
2. identify the exact disagreement;
3. separate intended semantics from executable behavior;
4. follow root AGENTS to resolve the intended rule;
5. only then update semantic specification or production implementation as authorized.

Do not silently choose Source merely because it runs.
Do not silently choose Reference merely because it is documented.
Do not infer a new trading rule from RAW observations alone.

## 14. RAW and regression relationship

RAW, fixtures, regression outputs, and runtime traces verify how an established rule behaves; they do not author the rule.

When chronology or lifecycle behavior is under review, use [Testing](testing.md) and the finest authoritative RAW required by the rule.

Do not turn one historical candle into Reference semantics.

## 15. Current validation helpers

Discover verification tooling dynamically before use.

Current tooling may include helpers that:

- discover embedded Source blocks;
- compare them with the live Engine tree;
- validate declared integrity metadata;
- compile reconstructed Source;
- verify unique directional Reference selection;
- run semantic/regression checks.

Treat helper names/paths as current implementation details. Inspect the helper itself and confirm that its discovery logic still matches the current Reference contract before trusting its PASS.

## 16. Stale snapshot detection

A Reference maintenance task must look for:

- production Source absent from the embedded/declared inventory;
- embedded files no longer production-owned;
- duplicate embedded paths;
- stale exact Source bytes;
- stale manifest hashes/counts/versions;
- stale symbol/function indexes;
- missing package/init Source required by reconstruction;
- one directional Reference updated without the other;
- semantic prose inconsistent with the approved current rule;
- Historical wording presented as active;
- missing revision/verification evidence required by the accepted format.

Do not rely on filename/version comparison alone.

## 17. Validation gate

Before declaring Reference synchronization successful, verify every applicable item:

- current accepted Bullish Reference discovered;
- current accepted Bearish Reference discovered;
- current production Source discovered dynamically;
- Reference-owned Source coverage established;
- embedded/reconstructed Source directly compared;
- stale/omitted Source detection completed;
- package/init coverage checked;
- Bullish/Bearish shared Source synchronized;
- direction-specific semantic text reviewed;
- approved semantic text matches intended behavior;
- schemas/public contracts reviewed when affected;
- Reference parses/renders/reconstructs according to its current format;
- appropriate tests/regression completed under [Testing](testing.md);
- final diff contains only intended Reference/task changes.

Use the standard status model from Testing. Never infer PASS from file existence.

## 18. Version and hash policy

Reference versions, Source versions, hashes, line counts, byte counts, and timestamps may legitimately exist inside the Algorithm References as snapshot/integrity metadata.

This maintenance procedure never hard-codes today's values as future authority.

For each maintenance task:

- discover/generate current values from current artifacts;
- record them only where the Reference format requires;
- treat them as evidence;
- compare underlying Source/semantics directly.

Procedural rule and current evidence snapshot must remain conceptually separate.

## 19. Change-history expectations

When the accepted Reference format requires revision history, record the change truthfully.

Distinguish at least:

- semantic/behavioral revision;
- implementation-only/refactor revision;
- documentation-only correction;
- verification/evidence update.

Do not describe a behavior change as implementation-only.
Do not describe embedded-Source synchronization as a semantic change when behavior did not change.

## 20. Acceptance scenarios

This procedure remains valid when:

- a new production Engine module becomes part of the Reference contract;
- production modules are reorganized or multiplied;
- legitimate Source changes regenerate new hashes;
- shared Source changes require both References to be reviewed;
- only one direction has an approved semantic exception;
- Source and Reference materially disagree;
- the current exact-source validation helper is renamed or replaced;
- the accepted Reference format changes its reconstruction mechanism.

The response is live discovery and contract validation, not editing a permanent file inventory here.

## 21. Review triggers

Review this procedure when:

- the accepted Reference structure changes materially;
- production-Source discovery contract changes;
- Reference reconstruction/completeness requirements change;
- directional synchronization policy changes;
- Reference validation/evidence requirements change.

Do not revise it merely because modules, versions, hashes, line counts, commits, or ordinary Source layout change.

## 22. Historical provenance

The previous standalone-reference specification is preserved as Historical evidence at [legacy Standalone Reference Specification](../../archive/documentation/standalone-reference-specification-legacy-2026-09-30.md).

It records a detailed earlier reconstruction contract, including fixed Source inventory assumptions that are no longer maintained authority.
