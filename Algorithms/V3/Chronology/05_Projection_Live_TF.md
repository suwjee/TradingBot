# Projection, Live and T/F

Source-only Phase 07 checkpoint. These clauses describe pinned main, not proposed algorithm changes.

## CH37

Projection horizon exclusive visible last start + timeframe. Recorded strict event verified only at same timestamp including duplicate lower times. Missing/unproven/late event null; no replacement search. For native Reaction confirmation the returned timestamp may be the Break-open fallback; proof can still succeed if an exact equal-time lower row crosses the strict level, even when that row precedes the effective native intrabar scan start. This is not proof of native scan firstness (CP342/TB38).

[Source engine/bridge/trading_pipeline.py:690–738](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L690-L738)

## CH38

Independent segment main [start,stop), lower [first main,next main or final + duration); local indices reset when needed, offset accumulated, visible bounds adjusted; explicit indexed mode can reuse zero-start records and register local windows over retained indexes. Projection offsets nonnegative integer index fields and identity components, not timestamps.

[Source independent segment and projection](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1826-L1871)

## CH39

Live accepts positive integral numeric epochs, checking equality to int-converted value rather than exact int type; equal epochs are permitted, descending epochs rejected; dirty lower rolls back one on equal timestamp, dirty main on same bucket. One-second timeframe shares frontier. The nonempty bucket rollback try starts after committing cache additions, suffixes and last time; BaseException during delta construction or consumer body restores suffixes/time and removes new cached prices. Earlier commit assignments are outside the inner try; empty input has no bucket changes.

[Source engine/bridge/trading_pipeline.py:225–295](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L225-L295)

## CH40

Append validation before transaction; request end moves to latest RAW time. Active path prepares trading state from buckets; optional exact-key reuse of settled historical closed prefixes. BaseException in the protected append block (including context exit) resets retained market views (including cache) and rethrows; input prevalidation and initial progress are outside that catch. No generalized rollback of external callback effects.

[Source engine/bridge/live_pipeline.py:35–70](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/live_pipeline.py#L35-L70)

## CH41

Repair through endpoint included by upper bound; start inclusive; reference direction strict crossing; missing hit null.

[Source TF repair](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/true_false.py#L18-L30)

## CH42

Basic starts at first S after each selected Primary/StopAll. Boundary clears price reference frontier and zeros retained base_count/verdict_count, preserves repair_count/latest. Greater rank gets T for any lower base_count>=2 independent of verdict and price; otherwise strict greatest-smaller-rank/latest eligible reference with direction normalization; display_restart independent. Higher rank evicts lower repeats, repairs singleton F at current source time. Same-rank F repair rule unchanged.

[Source Basic and strict reference](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/true_false.py#L47-L128)

## CH43

StopAll verdict groups restart when number <= previous; parity from current verdict start. Repeat prefix requires prior-series or largest-prior-end match and confirmation closure if supplied.

[Source StopAll](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/true_false.py#L131-L159)

## CH44

T/F clears old annotations, excludes only exact Boolean false, first row per source time wins directional Primary, StopAll,E,S. Sort selected once, primary flushes StopAll group; complete events including Primary/StopAll are passed to Basic as reset boundaries. No native geometry changes.

[Source collection](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/true_false.py#L162-L188)

## CH45

Reversed outputs applied only if transition index <= visible end. Active direction chosen by maximal (segment start index,direction). Repair through = visible last start + duration - one second; closed-through min(through epoch + 1,last lower epoch + raw timeframe). StopAll closure decision epoch + timeframe <= closed-through.

[Source response horizon](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3680-L3705)
