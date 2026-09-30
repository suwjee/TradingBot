---
title: TradingBot Engineering Documentation
document_role: reference
lifecycle: maintained
owner: documentation
last_modified_at: 2026-09-30T10:14:08+03:30
---

# Engineering documentation

This directory is the maintained documentation entry point. Root [`AGENTS.md`](../../AGENTS.md) governs project authority and safety; [Documentation Governance](documentation-governance.md) governs document classification, lifecycle, ownership, placement, duplication, archiving, generated-material policy, and maintenance triggers.

| Responsibility | Current maintained owner / navigation |
| --- | --- |
| Documentation governance | [Documentation Governance](documentation-governance.md) |
| AI / engineering execution | [AI Engineering Workflow](ai/engineering-workflow.md) |
| Architecture | [Technical Architecture](architecture/technical-architecture.md), [UI/UX Reference](architecture/ui-ux-reference.md) |
| Source/reference engineering | [Standalone References](development/standalone-reference-specification.md), [Zero-Difference Refactor](development/zero-difference-refactor.md) |
| Testing / local verification | [Local Tests](development/local-tests.md), [Repository Integrity](verification/repository-integrity.md) |
| Operations | [Local State](operations/local-state.md) |

Historical documentation is preserved outside the maintained documentation surface under `engineering/archive/`. Historical verification/migration evidence is preserved under `engineering/verification/history/` or its associated dated evidence area. Historical and generated material is supporting evidence, not Current authority.

Some maintained owner paths still contain explicitly marked dated bodies that are scheduled for later owner-specific rewrites. Until those phases run, follow their lifecycle notes, root AGENTS, current Source, and Documentation Governance rather than promoting snapshot facts to durable Current truth.

Current accepted Algorithm References are discovered under `engine/algorithms/` according to root AGENTS. Do not freeze their count, filenames, hashes, or versions in this index.
