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

## Formal specification V2.0 — Phase 01

[Phase 01: Source Discovery and Baseline Freeze](Audit/Phase_01/README.md) is COMPLETE for its defined discovery scope. The current implementation baseline is the latest main commit observed on 2026-11-26, `466eb875070f02cd0dbfb105033422bbe2fd8c70`. All 64 engine blobs are inventoried and hashed, with exact reference synchronization and verified RAW and historical Golden evidence. Re-resolve main before each subsequent phase. The specification itself remains PARTIALLY_VERIFIED; Phase 01 does not establish full semantic equivalence.

## V2.0 Phase 02 — Deep Static Analysis

[Phase 02 analysis](Audit/Phase_02/README.md) is structurally verified against latest main at commit `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Complete AST inventories and conservative control/data-flow graphs are recorded; dynamic and semantic closure remains partial. Phase 03 must re-resolve main before using this evidence.
