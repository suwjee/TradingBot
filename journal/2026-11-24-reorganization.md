# 2026-11-24 — Refactor reorganization

Owner authorizes writes only to refactor and requires persistent records for every task.

- Before: 75bfd33e15a8eb56d5b832a4e0121f9a33cbd50f, tree e00fc3c8d5130c6e4805fe84beaafbed7cbefa86, 1231 tracked files.
- Archive 118 files (873371242 logical bytes) from the active tree. Every path and blob SHA is in ../archive-index.json; original commit remains accessible. This does not shrink full Git history.
- Preserve runtime, source/tests, maintained docs and workflow paths. The superseded expanded V9 tooling snapshot has 16 byte-identical duplicates and one historical distinct runner, all recoverable.
- 100k and 250k strict trace pairs previously completed; stable outputs passed Golden comparison, selected trace remains INCOMPLETE. Persist full reports in subsequent evidence commit.
- Strict comparator mutation tests re-run: 15 passed. Full Engine/Chart suite NOT RUN in this housekeeping task. No new 1M test or algorithm change.
- main at 466eb875070f02cd0dbfb105033422bbe2fd8c70; production at 9838fa9809865aa6507adb7be871810d878bdb5f. Verify after write.
- V9 remains NO-GO for V10.
