# TradingBot — Standalone Algorithm Specification

**Documentation-only branch | English | PARTIALLY_VERIFIED**

This branch is an independent reading and distribution surface for algorithmic knowledge. Its current checked-out tree contains only Markdown specifications, language-neutral pseudocode, diagrams, structured metadata and verification evidence. It contains no production application or engine files, runnable test scripts, copied source appendices, build workflows, archives or RAW market datasets.

The implementation baseline is commit `466eb875070f02cd0dbfb105033422bbe2fd8c70`. The specification describes actual implemented behavior; intended trading-rule changes must be separately approved. The present specification is not certified sufficient for a full reconstruction.

## Reading order

| Section | Purpose |
|---|---|
| [Specification](Specification/README.md) | Architecture, invariants, time and numerical contracts, direction primitives |
| [Algorithms](Algorithms/README.md) | Reaction, Blue, A, S, Orders, E, Lifecycle, primary structures, bridge, serialization and T/F |
| [Directional](Directional/README.md) | Bullish and Bearish semantic maps and mirror rules |
| [Contracts](Contracts/README.md) | Input, output and inter-module interfaces |
| [Verification](Verification/README.md) | Test specifications, independent reconstruction and acceptance gates |
| [Audit](Audit/README.md) | Baseline traceability, open gaps, coverage, historical measurements and publication evidence |

Read [the final audit](Audit/Final_Audit_Report.md) before using any algorithm for production reconstruction. The earlier measured checks and their limitations are preserved; reorganizing documents is not a new execution or proof of equivalence.

## Separation policy

Source code and runnable verification tools must live outside this branch's current tree. An independent implementer should receive only Specification, Algorithms, Directional, Contracts and the approved semantic test cases from Verification; exclude Audit and any historical Git references. The repository's earlier shared history is retained and is not a clean-room access boundary. For strict isolation, export the allowlisted documents without Git metadata and supply them to a separate implementation environment.

See [AGENTS.md](AGENTS.md) for maintenance rules.
