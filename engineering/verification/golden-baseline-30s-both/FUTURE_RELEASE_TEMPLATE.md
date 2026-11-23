# Required record for each new optimization stage

Copy this template to `releases/V{version}.md` and fill **from actual test outputs**, not guesses:

- Source ZIP name, size and SHA256:
- Parent/previous performance-reference version:
- GitHub frozen oracle commit (unchanged):
- Exact changed module(s), diff and function scope:
- Candidate experimental algorithm assumptions / proof of equivalence:
- Input SHA256 verification 7/7:
- 30s both-direction full outputs identical against pinned baseline (7/7):
- SHA256 of each candidate stable output and telemetry-schema equality:
- Internal E/OrderAudit/lifecycle traces, events and chronology (N/N):
- Edge adversarial cases; Live seed/update/error and rollback:
- Candidate output discrepancy found? If yes, exact first byte/path and **REJECT**:
- One-run wall/CPU/RSS each dataset; runtime environment:
- Alternated paired benchmark: per-pair numbers and median speed ratios:
- Synthetic 100k/250k/500k/1M actual wall, CPU, RSS and stable output parity:
- Rejected optimization attempts: reason with precise benchmark evidence:
- Final promotion decision (parity approval and **separate** speed approval):
- Full separate archive location, checksum, logs, SHA256SUMS, code, visual charts:
- Outstanding untested states and acknowledged limitations:
- PR/commit references for documentation only; note whether runtime modified:
