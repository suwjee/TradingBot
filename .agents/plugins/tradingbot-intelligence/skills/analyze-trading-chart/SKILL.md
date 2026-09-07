---
name: analyze-trading-chart
description: Analyze a TradingBot candle range using deterministic pipeline output and source-backed evidence. Use for reaction explanations, chart analysis, or market-structure interpretation; do not use mental calculation as authoritative output.
---

# Analyze TradingBot chart

1. Confirm dataset, symbol, range, source timeframe, direction, and timezone.
2. Validate the candle data if integrity is uncertain.
3. Run the maintained Python pipeline; separate its facts from interpretation.
4. Cite exact candle evidence and the authoritative source/test path.
5. State ambiguity, missing data, and rejected alternatives.

Never invent a box, manually adjust a price, or silently override executable
output. Do not give trade instructions unless the user separately requests a
strategy discussion.
