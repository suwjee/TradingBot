---
title: TradingBot Engineering Documentation
document_role: reference
lifecycle: maintained
owner: documentation
last_modified_at: 2026-10-04T05:09:22+03:30
---

# Engineering documentation

This directory is the maintained documentation entry point. Root [`AGENTS.md`](../../AGENTS.md) governs project authority and safety; [Documentation Governance](documentation-governance.md) governs document classification, lifecycle, ownership, placement, duplication, archiving, generated-material policy, and maintenance triggers.

| Responsibility | Current maintained owner / navigation |
| --- | --- |
| Documentation governance | [Documentation Governance](documentation-governance.md) |
| AI / engineering execution | [AI Engineering Workflow](ai/engineering-workflow.md) |
| Architecture | [Technical Architecture](architecture/technical-architecture.md), [UI/UX Reference](architecture/ui-ux-reference.md) |
| Source/reference engineering | [Algorithm Reference Maintenance](development/algorithm-reference-maintenance.md), [Zero-Difference Refactor](development/zero-difference-refactor.md) |
| Testing / verification | [Testing](development/testing.md), [Repository Integrity](verification/repository-integrity.md) |
| Operations | [Local State](operations/local-state.md) |

Historical documentation is preserved outside the maintained documentation surface under `engineering/archive/`. Historical verification/migration evidence is preserved under `engineering/verification/history/` or its associated dated evidence area. Historical and generated material is supporting evidence, not Current authority.

The [Graphify archive](../archive/repository-graphify/README.md) provides generated navigation evidence for the repository. [Repository Integrity](verification/repository-integrity.md) explains how to classify and validate that evidence against Current Source.

Maintained owner documents describe Current durable contracts. Historical phase records and superseded snapshots remain evidence under the project archive/verification owners and must not be interpreted as pending Current instructions.

Current accepted Algorithm References are discovered under `engine/algorithms/` according to root AGENTS. Do not freeze their count, filenames, hashes, or versions in this index.
