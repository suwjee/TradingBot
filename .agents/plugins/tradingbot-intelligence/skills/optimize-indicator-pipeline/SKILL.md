---
name: optimize-indicator-pipeline
description: Improve TradingBot indicator-pipeline performance while proving byte-equivalent outputs. Use for caching, hot-loop, serialization, profiling, or throughput work.
---

# Optimize indicator pipeline

Read `SPEED_CODING_RULES.md` before editing. Benchmark the unmodified path,
identify a measured bottleneck, make one bounded optimization, and compare the
before/after outputs byte-for-byte for identical inputs. Preserve Decimal,
ordering, strict comparisons, output schema, and cache invalidation behavior.
Performance without equivalence proof is not a completed change.
