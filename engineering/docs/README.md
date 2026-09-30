---
title: TradingBot Engineering Documentation
document_role: reference
lifecycle: maintained
owner: documentation
last_modified_at: 2026-09-30T09:24:21+03:00
---

# Engineering documentation

This directory is the maintained documentation entry point. Root [`AGENTS.md`](../../AGENTS.md) governs project authority and workflow; [Documentation governance](documentation-governance.md) governs documentation classification, lifecycle, ownership, placement, duplication, archiving, generated-material policy, and maintenance triggers.

| Responsibility | Maintained owner / current navigation |
| --- | --- |
| Documentation governance | [Documentation governance](documentation-governance.md) |
| AI operating process | [Operating protocol](ai/operating-protocol.md) |
| Architecture | [Technical architecture](architecture/technical-architecture.md), [UI/UX reference](architecture/ui-ux-reference.md) |
| Source/reference engineering | [Standalone references](development/standalone-reference-specification.md), [Zero-difference refactor](development/zero-difference-refactor.md) |
| Testing / local verification | [Local tests](development/local-tests.md), [Repository integrity](verification/repository-integrity.md) |
| Operations | [Local storage](operations/local-state.md) |
| Existing engineering-audit material | [Audit workflow](verification/engineering-audit-workflow.md) |
| Existing migration evidence | [Single-root migration](verification/single-root-migration.md) |

Current placement alone does not determine lifecycle or authority. Some existing audit/migration documents intentionally remain in their current locations until later documentation-stabilization phases classify or restructure them.

Historical Graphify, regression, source-recovery, audit, and migration evidence belongs under the project’s current archive/history ownership. Current verification evidence belongs under `engineering/verification/` according to repository policy. Only narrowly classified disposable execution residue is Git-ignored; do not infer lifecycle or authority from ignore status alone.

Current accepted directional Algorithm References are discovered under `engine/algorithms/` according to root `AGENTS.md`; do not freeze their count, filenames, hashes, or versions in this index. Plugin/Vault and accepted References own intended trading semantics according to the current authority model; historical/generated evidence remains supporting context only.