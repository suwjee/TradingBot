---
type: "spec-to-code"
date: "2026-09-09T09:55:58.313423+00:00"
question: "Bullish 30s XAUUSD: why stopped A 01:56 lacks Order_A 03:06:30, why S-stop selects 03:14:30 instead of 03:17, and why special A 15:15 is suppressed"
contributor: "graphify"
outcome: "corrected"
source_nodes: ["SDetector._first_order_after", "SDetector.detect", "EDetector._carried_order_for_parent", "EDetector._register_order_audit", "ADetector._double_stop_a_candidates", "ADetector._a_was_stopped_before"]
---

# Q: Bullish 30s XAUUSD: why stopped A 01:56 lacks Order_A 03:06:30, why S-stop selects 03:14:30 instead of 03:17, and why special A 15:15 is suppressed

## Answer

Order_A audit was coupled to S eligibility and skipped superseded/type3 A zones; A-owned orders were absent from E carried ownership, allowing nested geometry during the live 03:06:30 order; special A was suppressed by a later recross instead of checking the earlier A's first strict stop.

## Outcome

- Signal: corrected

## Source Nodes

- SDetector._first_order_after
- SDetector.detect
- EDetector._carried_order_for_parent
- EDetector._register_order_audit
- ADetector._double_stop_a_candidates
- ADetector._a_was_stopped_before