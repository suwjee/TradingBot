# Concurrent Codex protocol

1. Read `AGENTS.md`, `CURRENT_HANDOFF.md`, and the owning map entry.
2. Assign one writer to one directory or one shared file at a time.
3. Re-read targets immediately before applying a patch.
4. Discovery and verification may run in parallel when they do not write.
5. Serialize contract changes along the pipeline: Reaction -> Blue -> A -> S -> E -> StopAll -> bridge -> UI.
6. Run focused validation before any integrated regression.
7. Do not overwrite, stage, or commit user/concurrent changes outside ownership.
