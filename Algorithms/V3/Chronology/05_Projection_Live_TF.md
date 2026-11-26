# Projection, Live and T/F

Source-only Phase 07 checkpoint. These clauses describe pinned main, not proposed algorithm changes.

## CH37

Projection horizon exclusive visible last start + timeframe. Recorded strict event verified only at same timestamp including duplicate lower times. Missing/unproven/late event null; no replacement search.

[Source engine/bridge/trading_pipeline.py:690–738](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L690-L738)

## CH38

Independent segment main [start,stop), lower [first main,next main or final + duration); local indices reset, offset accumulated, visible bounds adjusted. Projection offsets nonnegative integer index fields and identity components, not timestamps.

[Source engine/bridge/trading_pipeline.py:1755–1789](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L1755-L1789)

## CH39

Live accepts equal positive integer epochs, rejects descending; dirty lower rolls back one on equal timestamp, dirty main on same bucket. One-second timeframe shares frontier. Transaction on exception restores suffixes/time and removes new cached prices.

[Source engine/bridge/trading_pipeline.py:225–295](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L225-L295)

## CH40

Append validation before transaction; request end moves to latest RAW time. Active path full replay from buckets; failure resets retained market views and rethrows. No generalized rollback of external callback effects.

[Source engine/bridge/live_pipeline.py:35–70](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/live_pipeline.py#L35-L70)

## CH41

Repair through endpoint included by upper bound; start inclusive; reference direction strict crossing; missing hit null.

[Source engine/pipeline/true_false.py:17–29](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/true_false.py#L17-L29)

## CH42

Basic T/F starts first S and consumes supplied event order. Higher rank repairs prior singleton F starting current source time; repeated same-rank F removes old repair if >= current time then searches new repair. Engulf resets verdict count only.

[Source engine/pipeline/true_false.py:45–94](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/true_false.py#L45-L94)

## CH43

StopAll verdict groups restart when number <= previous; parity from current verdict start. Repeat prefix requires prior-series or largest-prior-end match and confirmation closure if supplied.

[Source engine/pipeline/true_false.py:97–125](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/true_false.py#L97-L125)

## CH44

T/F clears old annotations, excludes calculationValid=false, first row per source time wins in order directional Primary, StopAll, E, S. Sort selected by source time; Primary flushes StopAll verdict group. No native geometry changes.

[Source engine/pipeline/true_false.py:128–157](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/true_false.py#L128-L157)

## CH45

Reversed outputs applied only if transition index <= visible end. Active direction chosen by maximal (segment start index,direction). Repair through = visible last start + duration - one second; closed-through min(through epoch + 1,last lower epoch + raw timeframe). StopAll closure decision epoch + timeframe <= closed-through.

[Source engine/bridge/trading_pipeline.py:3639–3655](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L3639-L3655)
