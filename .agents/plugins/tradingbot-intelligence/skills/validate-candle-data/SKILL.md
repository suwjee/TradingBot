---
name: validate-candle-data
description: Validate TradingBot candle datasets for required fields, numeric OHLC integrity, Unix timestamps, ordering, duplicates, range bounds, market gaps, and Asia/Tehran rendering.
---

# Validate candle data

Do not load large raw candle files into model context. Use a bounded validator
or a streaming inspection. Treat malformed rows, invalid OHLC, timestamps,
ordering, duplicates, and conflicting duplicates as integrity failures. Report
gaps separately because market closures can make a gap legitimate. Candle count
is not elapsed-time coverage.
