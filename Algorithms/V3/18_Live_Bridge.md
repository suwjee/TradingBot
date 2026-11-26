# Live Bridge — active replay and optional continuation contracts (V3)

**Conventions:** B = bullish, R = bearish. Preserve Decimal representation and arithmetic order, native exception behavior, main time versus exact lower event, order and nulls. Record definitions are in [declared interfaces](../../Contracts/Declared_Record_Schemas.md). Procedure IDs designate semantic operations, not required implementation symbols. No runtime equivalence asserted.


## LV-M01 — Active path versus available incremental engines

The private continuation accepts complete E/S behavior pipeline and exact positive integer timeframe. Stores shallow args copy, engines, transactional buckets and retained views including closed-regime cache. Validates nondecreasing positive integer-valued RAW times, copies args to latest end, stages input, updates market views/indexes and computes from buckets. Active state preparation passes no live trading-stage continuation; closed-prefix result reuse is separately possible in the reversal path. Do not claim full-history replay of every previously closed regime on every append.

On any BaseException inside append transaction, rollback bucket suffix/price additions/last time, discard retained views and rethrow; rebuild views on retry. Progress start before protected body; completedStages increments before callback, totalStages=direction_count+4 (2 if primary present or both requested, else1). Return successful payload only after transaction exit. Worker byte lineage and errors defined in [Live Transport](23_Live_Transport_Contract.md), input bucketing in [RAW](21_RAW_Aggregation_Contract.md).

## LV-M02 — Standalone committed Reaction continuation

This service is separate from the active worker replay. Initial committed main >=2, nonempty aligned lower data, positive timeframe. New main positions contiguous, time strictly increasing in integral timeframe multiples; lower positions contiguous, strictly increasing time; lower window within new main extension. Both empty no-op, one empty invalid. Keep committed copies, result and initial cursor/normal checkpoint. A checkpoint captures earliest pending reset-search owner when unresolved, else next index and reaction/reset prefix counts. On extension build new lists, instantiate full-bound detector; if initial unresolved, resume initial cursor, otherwise retain prefixes and replay from checkpoint with cloned mutable candidates. Release per-market caches in finally. Advance commits, preview does not. Return snapshot clones, not mutable internal record list. Count processed main from replay boundary.

## LV-M03 — Other conditional retained stages

Blue replays reaction suffix and spacing checkpoints; A reuses settled exact query/zone histories; S caches decisions with geometry dependency frontier; E maintains strict stop/extreme/zone/reconciliation histories, may reopen race; Order_B retains settled boundary and crossing coverage; StopAll replays event checkpoint prefix; Primary replays scheduled steps and projected native identities. Each has its own dirty scope; see [Blue](03_Blue_Line.md), [A](04_A_Zone.md), [S](05_S_Zone.md), [E](09_E_Zone.md), [Order B](07_Order_B.md), [StopAll](11_StopAll.md), [Primary](12_Primary_Structures.md). Do not infer a common arbitrary rollback or universal append equivalence. Active regime callbacks are conditional on supplied live object. No engine execution is claimed.

## Detailed live replay procedures

### L01 — LivePipelineContinuation constructor

Inputs args and engines. If engines.e_zone is null OR args.s_zones not enabled, raise ValueError (complete behavior pipeline required). Next require exact integer timeframe >=1 (Boolean and subclass excluded), otherwise ValueError. Shallow-copy args, retain engines reference, construct fresh LiveMarketBuckets using original args.timeframe, then fresh LiveMarketViews. No explicit result. Initialization failures propagate.

### L02 — LivePipelineContinuation.append

Input rows list of mappings. Start previous_time at bucket last_raw_time. In caller order, convert row.time to integer; reject if converted value differs numerically from original or is <=0; reject if earlier than previous_time when previous exists. Equality with previous is permitted here (different from L10). Update local previous_time. If still null, raise ValueError for no timeframe candles. Shallow-copy retained args; set copy.to_time=previous_time. Direction count=2 if primary engine non-null OR direction is both, else 1. Local stage count=0. Establish L03 callback. Emit started event for Build live market chronology, liveProgress=true, before protected block. In protected block open bucket stage_append transaction with rows; obtain delta; call calculation with copied args, retained engines, buckets, live_views=current view object, bucket_delta=delta and report_stage callback. Report Calculated result ready for validation within transaction. On any BaseException from protected block (including context exit), replace current views with fresh LiveMarketViews then re-raise; transaction rollback semantics delegated to bucket owner. Return payload after successful context exit. Pre-validation and initial progress exceptions are outside that catch. State of external callbacks is not rolled back by this wrapper. The wrapper admits numeric integer-valued time inputs after int conversion (distinct from the exact-type timeframe constructor check).

### L03 — LivePipelineContinuation.append.report_stage

Input label. Increment captured completed_stages before emitting completed progress: liveProgress=true, completedStages=current count, totalStages=direction_count+4. Captures direction_count and mutable local counter. No explicit result; emit failure propagates after counter increment.

## Committed Reaction continuation procedures

### RE99 — LiveReactionContinuation.__init__
Validate direction via policy, require >=2 committed main else LiveReactionUnavailable. Copy candles/lower, options and timeframe. RE104 initial validation; construct RE102 before try, run RE97 retain cursor inside try and release indexes finally. Construction failure lies outside this cleanup scope. Save result/checkpoint/initial cursor, processed_main_candles=0.

### RE100 — result
RE101 snapshot.

### RE101 — _snapshot
Replace result, clone each mutable candidate and copy reset list.

### RE102 — _detector
New Unified on lists, full window 0..len-1, direction/options.

### RE103 — _release_indexes
RE52.

### RE104 — _validate_extension
Positive timeframe, both batches nonempty. Main index0 when no previous, else index previous+1, positive timestamp gap divisible by timeframe. Lower index0 or +1 with strictly increasing time. Lower first>=new main first, lower last<new main last+timeframe. Violations LiveReactionUnavailable with distinct messages.

### RE105 — advance
RE107 commit true.

### RE106 — preview
RE107 commit false.

### RE107 — _extend
Both empty return snapshot. Validate against last committed main/lower; concatenate into new lists, new detector. No checkpoint: processed=len(new batch main), RE97 with initial cursor. Else copy prior reaction/reset prefixes at checkpoint counts, clone cursor previous/candidate, processed=len(full main)-cursor.next_index, RE98. Release new sequence indexes finally for replay after detector construction; constructor failure is outside try. Only commit true updates owned lists/result/checkpoints/initial cursor and processed count. Return snapshot either way after optional commit (snapshot failure is not a rollback trigger).


## LV-M04 — Closed-regime cache and index windows (v2.8.7)

Active worker retains normalized input, views and independent closed-prefix cache. calculate_live_from_buckets constructs inputs tuple; if live_views is None delegate common runner without closed resolver, otherwise assert non-null bucket_delta and stage closed_regimes using first_dirty_main; pass resolver to common runner and response. Runner still calls prepare_pipeline_state without live continuation, so active trading state is freshly calculated; settled independent historical prefixes may be reused via resolver. The cache is not a universal incremental engine state. [Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3738-L3767).

LiveClosedRegimes owns _published mapping initially empty. stage(first_dirty_main) captures previous mapping by reference and creates empty current map. Returned resolve(direction,market,boundary,calculate) uses absolute excluded end = market.index_offset+boundary; key = ordered tuple(direction,index_offset,end,boundary candle timestamp,market.start_index,min(market.end_index,boundary-1),initial_bullish_trend,initial_bearish_trend). Read prior entry only when end<=first_dirty_main, otherwise None; if None call calculate, then assign current[key]=saved and return saved. Does not consult current for a second same-stage hit. Yield resolver; only successful context exit assigns _published=current, dropping unused prefixes. Failure before normal completion leaves prior map, and outer live wrapper discards views on BaseException. Cached history is unannotated local output; publish recursively copies even zero offset before metadata and horizon-dependent T/F. [Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1756-L1785).

MarketIndexWindow retains supplied candles and slices index.times[start:stop]; length=stop-start. If index is already a window, flatten base and add its start to new start, otherwise retain original index and start. First-crossing adapter clamps left=max(left,0), right=min(right,length), returns None if left>=right; otherwise call selected strict base query with offset bounds and level, subtract offset from non-null hit (zero valid). Range extreme adapter does not clamp: require 0<=left<right<=length else ValueError; query base range and return value unchanged plus position minus offset. Delegates first_less/first_greater and range_minimum/range_maximum, preserving base tie/price semantics. [Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1788-L1823).

On error in the protected outer append body (including exit), the entire LiveMarketViews object is replaced, so its cache is not retained on retry. Callback side effects outside view ownership are not universally rolled back.
