# repository-graphify

**created_at:** `2026-09-30T15:43:03+03:30`
**last_modified_at:** `2026-09-30T15:43:03+03:30`

## Purpose

This directory holds **repository analysis evidence**, architecture analysis artifacts, audit support material, and AI context material produced by a full live-repository Graphify-style analysis.

It is **not**:

- production source
- runtime code
- algorithm authority
- maintained documentation

## Authority rules

1. Previous Graphify outputs (including `snapshots/`) are historical evidence only.
2. They are not current project authority.
3. Every rebuild analyzes the live repository.
4. Hashes/versions are not used as graph identity.
5. Historical outputs may be preserved for comparison.

## Contents

| File | Purpose |
| --- | --- |
| `GRAPH_REPORT.md` | Main engineering report |
| `GRAPH_HEALTH.md` | Integrity / drift / orphan / duplicate health report |
| `graph.json` | Durable knowledge graph (nodes/edges/analysis) |
| `graph.html` | Interactive searchable/zoomable/filterable graph |
| `full-file-inventory.json` | Per-file path/type/language/size/subsystem/ownership/lifecycle/degree |
| `manifest.json` | Generation manifest |
| `reports/` | architecture, dependency, ownership, test-impact, documentation |
| `cache/` | temporary analysis cache and generator |
| `snapshots/` | historical graph outputs preserved for comparison |

## Rebuild

Live analysis is performed against the current repository each time. Classification rules are path/subsystem based so new Engine modules, plugins, and tests are included automatically.
