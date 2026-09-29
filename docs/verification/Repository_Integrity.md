# Repository integrity verification

Repository cleanup protects maintained Engine source, Engine styles, and both current references with SHA-256 comparison. RAW and sidecars move without changing bytes. The original Git index, staged/unstaged binary diffs, recursive inventory, and source archive remain external.

Structural checks include clean dependency installation, chart/Python tests, build, Python AST checks, normal dynamic bridge loading, and exact source reconstruction in both references. Scan prospective and staged Git content for credentials without printing values; verify no local state/test files remain indexed and no legitimate file remains unexplained/untracked.

Dependency/build/cache output, RAW, runtime state, temporary output, Graphify artifacts, and tests are excluded from the staged tree. During source-only preparation, local-state and generated directories must also be absent physically, except the intentionally retained ignored test tree.

These checks establish cleanup and reproducibility. They do not prove independent trading correctness or repair existing Reference narrative discrepancies. No Engine or algorithm changes are authorized. A new RAW market regression is not required solely for storage/layout migration with unchanged calculation and input bytes.

Reports and command logs remain external. Re-run relevant checks after later changes; an old report is not a current PASS claim.
