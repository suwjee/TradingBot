# TradingBot permanent refactor workspace

This branch is exclusively for refactoring. Root [AGENTS](../../AGENTS.md) governs write authorization and correctness. Main and production are read-only unless the owner explicitly authorizes a specific change.

## Start here
1. [Current state](STATE.json) and [latest journal](journal/2026-11-24-reorganization.md).
2. [V9 workspace](../refactor-v9/README.md) and [V9 gates](../refactor-v9/V9_CURRENT_GATES.json).
3. [Handoff template](handoff-template.md) and [historical artifact index](archive-index.json).
4. Discover live application, engine, test and documentation ownership before each task.

## Layout
- apps/chart/, engine/, scripts/: executable source and tests retained unchanged in this reorganization.
- engineering/docs/: maintained engineering guidance.
- engineering/refactor/: cross-phase state, journal, handoff and archive index.
- engineering/refactor-v9/: V9 tools, gate reports, frozen inputs and run evidence.
- engineering/archive/ and engineering/verification/: historical reports; large generated files are recoverable from the immutable commit in the archive index.
- Future phases use engineering/refactor-v10/ etc. only after preceding gates pass.

Every task must commit and push to refactor, record even incomplete work, verify the remote branch and protected heads, and update STATE plus journal. Preserve existing history; do not force-push. Store reproducible evidence, exact hashes, commands, results and constraints; disclose anything not stored in Git. A small passing test is not full-scale verification.
