<!-- created_at: 2026-09-30T17:56:06+03:30 -->
<!-- last_modified_at: 2026-09-30T17:56:06+03:30 -->

# Documentation report

## Current owners

`engineering/docs/README.md` is the maintained engineering index; `documentation-governance.md` owns classification and one-maintained-owner policy. `engineering/docs/development/testing.md` owns test procedure. The two files under `engine/algorithms/` label themselves active Bullish/Bearish references, which is document status rather than independently verified semantic synchronization. Archived docs and generated Graphify outputs remain evidence.

## Broken local links

- `engineering/archive/documentation/technical-architecture-audit-2026-09-22.md:1` -> `engineering/archive/operations/local-state.md` (historical)
- `engineering/archive/documentation/ui-ux-audit-2026-09-22.md:1` -> `engineering/archive/operations/local-state.md` (historical)

## Drift and duplicate authority

`engineering/docs/verification/repository-integrity.md:L388-L436` names absent `scripts/verification/anti_drift.py` and `.github/workflows/anti-drift.yml`. Archived `engineering/archive/documentation/local-tests-legacy-2026-09-30.md` still declares maintained lifecycle even though the current testing guide supersedes it.
