# Engineering documentation

This directory owns maintained project guidance. Current production paths remain under `apps/chart/` and `engine/`; all project-owned local content remains inside the checkout.

| Responsibility | Maintained document |
| --- | --- |
| AI operating process | [Operating protocol](ai/operating-protocol.md) |
| Architecture | [Technical architecture](architecture/technical-architecture.md), [UI/UX reference](architecture/ui-ux-reference.md) |
| Source/reference engineering | [Standalone references](development/standalone-reference-specification.md), [Zero-difference refactor](development/zero-difference-refactor.md) |
| Local verification | [Local tests](development/local-tests.md), [Repository integrity](verification/repository-integrity.md) |
| Operations | [Local storage](operations/local-state.md) |
| Engineering review | [Audit workflow](verification/engineering-audit-workflow.md) |
| Migration evidence | [Single-root migration](verification/single-root-migration.md) |

Architecture audit bodies retain their original dated evidence; their location notes identify the current layout. Historical Graphify, regression and source-recovery artifacts live in ignored `engineering/archive/`. Local command logs, manifests and recovery snapshots live in ignored `engineering/verification/`.

The only current directional references are the two source-synchronized documents in `engine/algorithms/`. Semantic authority follows root AGENTS and Plugin/Vault retrieval; historical archived documents are supporting evidence only.
