---
type: "spec-to-code"
date: "2026-09-09T10:20:14.238549+00:00"
question: "Bullish order stop rule: Mode A leg start from breakout backward; Mode B previous bearish Reaction BoxTop"
contributor: "graphify"
outcome: "corrected"
source_nodes: ["SDetector._order_stop", "EDetector._order_stop", "UnifiedReactionDetector.first_order_reaction_after_gate"]
---

# Q: Bullish order stop rule: Mode A leg start from breakout backward; Mode B previous bearish Reaction BoxTop

## Answer

SDetector and EDetector both consumed anchor_value for Mode A, which selected 03:05:30. The corrected order-specific rule scans from the Break candle backward through the immediate pre-First context and chooses the maximum High for bearish orders; 03:06:30 now stops at High 4430.545 from 03:06:00. Bullish Mode B in E now unconditionally uses the previous bearish Reaction BoxTop, matching S.

## Outcome

- Signal: corrected

## Source Nodes

- SDetector._order_stop
- EDetector._order_stop
- UnifiedReactionDetector.first_order_reaction_after_gate