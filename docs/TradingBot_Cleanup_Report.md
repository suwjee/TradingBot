# TradingBot Cleanup Report

Date: 2026-09-18  
Scope: read-only project analysis plus task-owned documentation and Graphify artifacts

## Decision

No pre-existing project file was deleted, moved, renamed, or rewritten by this task.

The repository contains generated, cached, duplicated-looking, historical, and accidental-path candidates, but the current dirty working tree makes automatic cleanup unsafe. Several runtime and source paths are untracked while their tracked predecessors are deleted. A file that appears obsolete in isolation can therefore still be part of active user work or evidence needed for reconciliation.

## Reviewed Candidate Classes

| Candidate class | Examples | Decision | Reason |
|---|---|---|---|
| Build output | `apps/chart/dist/**` | Keep | Generated and non-authoritative, but pre-existing and potentially used for comparison/deployment |
| Vite/package caches | `apps/chart/node_modules/.vite/**`, `node_modules/**` | Keep | Reproducible in principle, but installed dependency state belongs to the user and was included in the requested full audit |
| Python bytecode | `engine/**/__pycache__/**` | Keep | Generated, but pre-existing and useful as version/timestamp evidence during this read-only audit |
| Calculation/runtime caches | `runtime/calculations/**`, drawings/templates/session artifacts | Keep | May encode user state and historical regression evidence |
| Historical algorithm docs | `engine/algorithms/*V4.0.1.md` | Keep, label historical | Obsolete as current authority but valuable as an explicit historical snapshot |
| Root algorithm references | `engine/TradingBot_*_Algorithm_Reference.md` | Keep | Contain useful amendments despite internal contradictions; replaced as current authority only by the new `docs/` references |
| Suspicious mirrored path | `apps/chart/ Folders/**` | Keep | Looks accidental, but ownership and intent cannot be proven from static evidence |
| RAW market data and sidecars | `data/raw/**` | Keep | Authoritative input and integrity metadata; all validated successfully |
| Untracked replacement engine | `engine/bridge/trading_pipeline.py`, `engine/pipeline/*_detector.py`, lifecycle/shared modules | Keep | Active runtime implementation referenced by current launcher/backend |
| Deleted tracked legacy engine | Git deletions under `engine/bridge` and `engine/pipeline` | Preserve status | User-owned migration state; restoring or finalizing it is outside the documentation task |

## Task-Generated Temporary Files

After the final graph, health diagnostics, inventory, report, labels, and visualization were verified, this task removed its own raw extraction sidecars, temporary helper scripts, and two Graphify cache trees. Removed task-owned classes were `.graphify_ast.json`, `.graphify_extract.json`, `.graphify_detect.json`, `.graphify_files.json`, four semantic/image chunk JSON files, analysis JSON, temporary build/label/finalization scripts, marker files, and 79 cache files. None existed before this task and none was project source.

The retained Graphify set is `graph.json`, `graph.html`, `GRAPH_REPORT.md`, `GRAPH_HEALTH.md`, `graph-health.json`, `.graphify_labels.json`, `README.md`, `manifest.json`, `cost.json`, `full-file-inventory.json`, and `engine-audit-evidence.md`.

Deletion ledger:

| Exact task-owned path | Removed entries | Recovery |
|---|---:|---|
| `docs/graphify/.build_graph.py` | 1 | Recreate from the documented Graphify build sequence; final graph is retained |
| `docs/graphify/.label_communities.py` | 1 | Labels are retained in `.graphify_labels.json`; regenerate deterministically from dominant paths/symbols |
| `docs/graphify/.finalize_inventory.py` | 1 | Recreate the final hashing walk; inventory/manifest/cost outputs are retained |
| `docs/graphify/.graphify_analysis.json` | 1 | Re-run Graphify analysis; conclusions remain in `GRAPH_REPORT.md` |
| `docs/graphify/.graphify_ast.json` | 1 | Re-run structural extraction |
| `docs/graphify/.graphify_detect.json` | 1 | Re-run corpus detection |
| `docs/graphify/.graphify_extract.json` | 1 | Re-merge AST, file hierarchy and semantic chunks |
| `docs/graphify/.graphify_files.json` | 1 | Re-run file-hierarchy extraction |
| `docs/graphify/.graphify_chunk_01.json` through `.graphify_chunk_04.json` | 4 | Re-run the three semantic and one image extraction partitions |
| `docs/graphify/.graphify_python`, `.graphify_root` | 2 | Re-detect the local Graphify interpreter/root |
| `docs/graphify/cache/` | 15 cache files | Re-run Graphify AST extraction; cache is non-authoritative |
| `docs/graphify/graphify-out/` | 64 cache files | Re-run Graphify with the same corpus; cache is non-authoritative |

The baseline proves task ownership because none of these paths appears in the pre-existing 89-path boundary. Recovery does not depend on deleted content: every authoritative source remains present and the final graph, labels, report, health diagnostics, inventory and manifest are retained.

## Safe Future Cleanup Procedure

1. First commit or otherwise reconcile the active engine migration.
2. Capture hashes and ownership for runtime caches and user-state files.
3. Prove that generated paths can be recreated from committed inputs.
4. Delete one bounded class at a time.
5. Re-run tests, production build, bridge smoke validation, and Git-status comparison.
6. Record every removed path and recovery method.

Until those prerequisites are met, the correct cleanup action is preservation.

## Current-turn update (2026-09-19)

The current turn created only task-owned Graphify intermediates and a dated verified snapshot under `docs/graphify/rebuild-2026-09-19/`. The intermediates were used for extraction, clustering, diagnosis, and query checks; they are not application inputs. Because recursive deletion was blocked by the safety policy, the intermediates were moved intact to `docs/graphify/rebuild-2026-09-19/raw-run/`, preserving recoverability while keeping all Graphify artifacts under `docs/graphify`. The dated snapshot, its report, visualization, manifest, diagnostics, and raw-run evidence are retained.

No pre-existing file was deleted, renamed, or cleaned. In particular, the suspicious mirrored `apps/chart/ Folders/**` tree, installed dependencies, runtime caches, RAW data, historical references, and the tracked-deletion/untracked-replacement engine migration remain preserved because ownership or runtime irrelevance cannot be proven from this checkout.
