# GRAPH_HEALTH.md

**created_at:** `2026-09-30T15:43:03+03:30`
**last_modified_at:** `2026-09-30T15:43:03+03:30`

## Broken references

Documentation link targets that do not resolve inside the repository: 4

- `engineering/archive/documentation/technical-architecture-audit-2026-09-22.md` -> `engineering/archive/operations/local-state.md`
- `engineering/archive/documentation/ui-ux-audit-2026-09-22.md` -> `engineering/archive/operations/local-state.md`
- `engineering/archive/repository-graphify/README.md` -> `engineering/archive/repository-graphify/rebuild-2026-09-23`
- `engineering/archive/repository-graphify/snapshots/pre-rebuild-2026-09-30_154000/README.md` -> `engineering/archive/repository-graphify/snapshots/pre-rebuild-2026-09-30_154000/rebuild-2026-09-23`

## Orphan nodes

Maintained/test/docs files with no non-ownership relationship edges: 23

- `.editorconfig`
- `.gitattributes`
- `.gitignore`
- `apps/chart/index.html`
- `apps/chart/package-lock.json`
- `apps/chart/review.html`
- `apps/chart/scripts/dev-server.mjs`
- `apps/chart/src/features/manual-review/review.css`
- `apps/chart/tests/unit/chart-update-contract.test.mjs`
- `apps/chart/tests/unit/vite-state-policy.test.mjs`
- `engine/__init__.py`
- `engine/engine.zip`
- `scripts/git.zip`
- `scripts/git/git.bat`
- `scripts/git/Git.Menu.ps1`
- `scripts/git/IMPLEMENTATION_PLAN.md`
- `scripts/git/Invoke-TradingBotRelease.ps1`
- `scripts/git/production-policy.psd1`
- `scripts/git/Release.Workflow.psm1`
- `scripts/git/RELEASE_WORKFLOW_DESIGN.md`
- `scripts/git/Test-ReleaseWorkflow.ps1`
- `scripts/launch.bat`
- `scripts/start.ps1`

## Circular dependencies

Import-edge cycles detected: 0

- none

## Suspicious duplicates

Basename collisions across subsystems or archive/live paths: 39
Identical-content groups: 8

- `.graphify_labels.json`: `engineering/archive/repository-graphify/.graphify_labels.json`, `engineering/archive/repository-graphify/rebuild-2026-09-23/.graphify_labels.json`, `engineering/archive/repository-graphify/snapshots/pre-rebuild-2026-09-30_154000/.graphify_labels.json`
- `__init__.py`: `engine/__init__.py`, `engine/bridge/__init__.py`, `engine/pipeline/__init__.py`
- `case-01.baseline.json.gz`: `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output-large/case-01.baseline.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output/case-01.baseline.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/default/case-01.baseline.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/smoke-default/case-01.baseline.json.gz`
- `case-01.candidate.json.gz`: `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output-large/case-01.candidate.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output/case-01.candidate.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/default/case-01.candidate.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/smoke-default/case-01.candidate.json.gz`
- `case-01.json.gz`: `engineering/archive/docs/order-architecture-2026-09-27/phase2-cache-targeted/case-01.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/phase2-extract-smoke/case-01.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/phase2-extract-targeted/case-01.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/phase2-s-extract-smoke/case-01.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_DIAGNOSTIC_INTERRUPTED/case-01.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-01.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-01.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/recovery-smoke/case-01.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/smoke-precision/case-01.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/smoke-usoil-precision/case-01.json.gz`
- `case-01.stderr.log`: `engineering/archive/docs/order-architecture-2026-09-27/phase2-cache-targeted/case-01.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/phase2-extract-smoke/case-01.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/phase2-extract-targeted/case-01.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/phase2-s-extract-smoke/case-01.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_DIAGNOSTIC_INTERRUPTED/case-01.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-01.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-01.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/recovery-smoke/case-01.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/smoke-precision/case-01.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/smoke-usoil-precision/case-01.stderr.log`
- `case-02.baseline.json.gz`: `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output-large/case-02.baseline.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output/case-02.baseline.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/default/case-02.baseline.json.gz`
- `case-02.candidate.json.gz`: `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output-large/case-02.candidate.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output/case-02.candidate.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/default/case-02.candidate.json.gz`
- `case-02.json.gz`: `engineering/archive/docs/order-architecture-2026-09-27/phase2-cache-targeted/case-02.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/phase2-extract-targeted/case-02.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_DIAGNOSTIC_INTERRUPTED/case-02.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-02.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-02.json.gz`
- `case-02.stderr.log`: `engineering/archive/docs/order-architecture-2026-09-27/phase2-cache-targeted/case-02.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/phase2-extract-targeted/case-02.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_DIAGNOSTIC_INTERRUPTED/case-02.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-02.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-02.stderr.log`
- `case-03.baseline.json.gz`: `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output/case-03.baseline.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/default/case-03.baseline.json.gz`
- `case-03.candidate.json.gz`: `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output/case-03.candidate.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/default/case-03.candidate.json.gz`
- `case-03.json.gz`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-03.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-03.json.gz`
- `case-03.stderr.log`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_DIAGNOSTIC_INTERRUPTED/case-03.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-03.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-03.stderr.log`
- `case-04.baseline.json.gz`: `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output/case-04.baseline.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/default/case-04.baseline.json.gz`
- `case-04.candidate.json.gz`: `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output/case-04.candidate.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/default/case-04.candidate.json.gz`
- `case-04.json.gz`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-04.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-04.json.gz`
- `case-04.stderr.log`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-04.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-04.stderr.log`
- `case-05.baseline.json.gz`: `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output/case-05.baseline.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/default/case-05.baseline.json.gz`
- `case-05.candidate.json.gz`: `engineering/archive/docs/hpzr2-regression-2026-09-23/bridge-output/case-05.candidate.json.gz`, `engineering/archive/docs/hpzr2-regression-2026-09-23/default/case-05.candidate.json.gz`
- `case-05.json.gz`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-05.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-05.json.gz`
- `case-05.stderr.log`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-05.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-05.stderr.log`
- `case-06.json.gz`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-06.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-06.json.gz`
- `case-06.stderr.log`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-06.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-06.stderr.log`
- `case-07.json.gz`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-07.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-07.json.gz`
- `case-07.stderr.log`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-07.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-07.stderr.log`
- `case-08.json.gz`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-08.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-08.json.gz`
- `case-08.stderr.log`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-08.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-08.stderr.log`
- `case-09.json.gz`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-09.json.gz`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-09.json.gz`
- `case-09.stderr.log`: `engineering/archive/docs/order-architecture-2026-09-27/PHASE_1_FINAL_BASELINE/case-09.stderr.log`, `engineering/archive/docs/order-architecture-2026-09-27/PHASE_2_FINAL_REGRESSION/case-09.stderr.log`

## Missing ownership

Files classified as Project/Unknown ownership: 3

## Architecture boundary risks

- Chart must not become a second trading algorithm (AGENTS.md §5). Chart algorithm UI content lives under `apps/chart/src/algorithm/content/` and is presentation/reference UI, not engine authority.
- Vite must not redefine Engine semantics; `vite.config.js` should remain orchestration/transport.
- FARAZ must not define trading rules.
- `engineering/archive/**` is evidence only.

## Documentation drift risks

- Prior Graphify outputs under `repository-graphify/` and `snapshots/` are historical.
- `engineering/archive/documentation/*legacy*` documents are historical classifications.
- Algorithm references under `engine/algorithms/*Source_Synchronized.md` are accepted references; verify currency before treating as sole semantic authority.

## Graph health summary

| Check | Status |
| --- | --- |
| Extraction produced nodes | PASS (662 nodes) |
| Extraction produced edges | PASS (2038 edges) |
| Broken doc refs | WARN (4) |
| Circular imports | PASS (0) |
| Orphan maintained files | WARN (23) |
| Duplicates reported only | PASS |
