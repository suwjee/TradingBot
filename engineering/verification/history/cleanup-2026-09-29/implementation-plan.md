# Repository Cleanup Implementation Plan

**Goal:** Stage maintainable project content while preserving Engine bytes and valuable local state.
**Architecture:** Use one shared application storage resolver, sibling local storage, local ignored tests, and purpose-based documentation. No Engine or reference edits.
**Spec:** User attachment Pasted text.txt, sections 1-60.
**Constraints:** No commit, push, Graphify execution, secret disclosure, algorithm change, or unrelated work loss. Existing work is included only under the user's explicit complete-staging instruction. Native execution in the authoritative dirty checkout is required for this cleanup; no new worktree.

- [x] Capture Git topology/index/diffs, recursive inventory, source/reference/RAW hashes and source archive outside the repository.
- [ ] Classify documentation, scripts, imports, duplicate hashes and runtime callers; preserve unknowns rather than delete.
- [ ] Add shared external storage resolver and meaningful local path tests; connect Vite, FARAZ and launcher.
- [ ] Move RAW/persistent runtime state with hash verification; archive historical/generated evidence externally; remove dependency/cache/build directories.
- [ ] Centralize Node/Python tests and test helpers; repair imports, fixture storage paths and commands; ignore all tests.
- [ ] Organize durable docs and archive obsolete duplicate references/prompts/migration tools; repair live navigation.
- [ ] Reinstall dependencies from lockfile, run local suites, build, validate Engine AST/normal bridge load and exact embedded references; clean regenerated artifacts.
- [ ] Scan intended/index content for secrets, inspect source/path/link dependencies, stage all intended content, and verify hashes/trees/untracked audit.
- [ ] Write external 26-section report, per-file manifest and release ZIP with readme.txt; preserve HEAD and remote.

**Review focus:** custom state root outside checkout; rejection of inside-checkout roots; FARAZ synthetic sessions/RAW use explicit test storage; relocated test imports; launcher/server share same default paths.
