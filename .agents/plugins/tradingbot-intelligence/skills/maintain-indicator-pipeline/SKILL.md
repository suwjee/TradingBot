---
name: maintain-indicator-pipeline
description: Safely inspect, change, debug, or verify the TradingBot Reaction-to-StopAll Python pipeline, bridge, tests, and documentation. Use for missed/extra events, algorithm changes, or cross-module calculation defects.
---

# Maintain indicator pipeline

Read `AGENTS.md`, the applicable sections of
`docs/algorithms/BULLISH_INDICATOR_ALGORITHM.md`, maintained module source,
bridge code, and focused tests. The current repository—not Prj-1—is authority.

- Preserve strict Decimal comparisons and the runtime `Open <= Close` GREEN
  rule unless an explicitly approved algorithm change says otherwise.
- Classify a discrepancy as data, specification, implementation, or
  expectation before editing.
- Mirror directional semantics exactly when the algorithm requires it.
- Make the smallest change, validate focused behavior, compile affected Python,
  and verify bridge/UI contracts when affected.
- Update documentation with fresh evidence; never hand-edit generated results.
