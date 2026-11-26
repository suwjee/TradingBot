# Time domains and Reaction

Source-only Phase 07 checkpoint. These clauses describe pinned main, not proposed algorithm changes.

## CH01

MarketChronology main owner is upper bound minus one; before first raises unless clamp. Lower window [start,end) uses lower bounds at both endpoints; absent end uses physical length.

[Source engine/pipeline/reaction_engine.py:1185–1209](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L1185-L1209)

## CH02

Reset time precedence is nonempty second_time, display_time, native timestamp; no invented precision.

[Source engine/pipeline/reaction_engine.py:1238–1255](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L1238-L1255)

## CH03

Reaction confirmation scans [valid intrabar start,Break open + timeframe), strict high above BoxTop bullish / low below BoxBottom bearish. Invalid start resets scan start to Break open; absent strict crossing returns Break open as the confirmation fallback. A disables intrabar start.

[Source engine/pipeline/reaction_engine.py:1257–1302](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L1257-L1302)

## CH04

Lower extreme uses half-open position range; invalid/empty raises; equal price selects earliest position.

[Source engine/pipeline/reaction_engine.py:973–1009](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L973-L1009)

## CH05

First crossing clamps bounds and visits intervals chronologically. Cached evidence excludes final mutable lower row from settled history. Cached crossing must be strictly before requested right.

[Source engine/pipeline/reaction_engine.py:1011–1062](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L1011-L1062)

## CH06

Gate owner on same main candle qualifies if confirmation <= exact gate; without exact gate use Break index <= gate. Missing lower confirmation uses Break open. New scan starts gate index + 1.

[Source engine/pipeline/reaction_engine.py:2095–2129](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L2095-L2129)

## CH07

Overlapping direct candidates: first completing main candle wins; within that candle choose smallest First index, not an independently ranked intrabar confirmation time.

[Source engine/pipeline/reaction_engine.py:2217–2289](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L2217-L2289)

## CH08

Leg invalidation requires strict penetration. Same main candle race scans lower rows in order, invalidation before confirmation within each row. Absent decisive lower evidence defaults to invalidation.

[Source engine/pipeline/reaction_engine.py:2379–2417](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L2379-L2417)
