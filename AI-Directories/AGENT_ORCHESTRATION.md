# Native agent orchestration

Use bounded Codex-native roles for non-trivial work:

| Work | Role | Write boundary |
|---|---|---|
| Cross-module plan | coordinator | Read-only |
| Rule meaning / directional semantics | rule analyst | Read-only |
| One indicator module | module implementer | One selected module |
| Bridge/API | bridge implementer | `indicator/indicator-settings/` |
| Browser workstation | chart implementer | `lightweight-charts/` |
| Candle integrity | data auditor | Read-only |
| Performance proof | optimization auditor | Read-only except owned benchmark artifacts |
| Integration / final tests | verification auditor | Read-only |

One writer owns each write surface. A coordinator must define the intended
contract, evidence, owner, and validation before multi-agent edits. The primary
agent reconciles the filesystem and test evidence before reporting completion.

Stop for unclear trading semantics, credentials, destructive operations,
publishing, or external side effects that were not explicitly authorized.
