# CP341 — W2 Bridge market/input queue reconciliation

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, source blob `e1e65ba960c5f726f9a05e2ab89e4457b65e5735`. W2 NOT_ACCEPTED. Scoped source review of 17 queue records. B09 W1 traceability normalized from 16 historical review files; 2317 unique rows, exact ID/ledger membership, zero recorded-prior mapping discrepancies.

## CP323-P25 — LV-M04 / TR-M02

Stage captures previous published map and fresh current map. Key exact direction, absolute offset and excluded end, boundary candle timestamp, visible start and min(end,boundary-1), both initial flags. Read previous only when absolute exclusive end<=first_dirty_main; None miss recalculates. No current-map lookup on repeated same-stage key. Yield then publish current only on successful exit.

Handoff: Only reuse independent closed prefixes, not open trading stages. Outer protected append discards retained views on failure. Cached local payload is copied before publication/index projection and T/F.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1756-L1785). B09 overlap occurrences: 10.

## CP330-S01 — TB01–03

ContextVar token restored in finally. Details merged after status/label; explicit nonnull duration overwrites durationMs after rounding. Sink non-null called directly, else compact flushed stderr. Timed stage starts clock and emits started before try; finally accumulates unrounded milliseconds then completed, even when work fails; finally exception can replace original failure/result.

Handoff: Telemetry has no intended price effect, but no blanket exception suppression. Callback errors remain observable.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L54-L84). B09 overlap occurrences: 24.

## CP330-S03 — TB06–08

Epoch cache miss converts via Tehran then strips tzinfo. Reverse conversion attaches/replaces tzinfo, not timezone conversion; int truncates toward zero. Native datetime including subclass bypasses display string cache, otherwise exact format parsed; nonnull hits reused (0 epoch valid). No fallback.

Handoff: Native chronology uses wall-clock values; serialized epoch is distinct coordinate. Cache lifecycle TB97 scope.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L101-L137). B09 overlap occurrences: 20.

## CP330-S04 — RAW-M01/02 / TB09

Optional tails are retained by reference even main tail if lower_only. Iterate supplied order, int time then Decimal callback O,H,L,C. Consecutive equal key preserves O, max/min previous-first (equal representation retained), latest C. Main floor division except TF1; lower_only bypasses main update entirely. No global merge of discontiguous equal keys, sorting, filling or validation.

Handoff: Batch aggregation differs from live checked iterator; same-time lower grouping not equal to RAW timeframe expansion.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L140-L184). B09 overlap occurrences: 31.

## CP330-S05 — TB10–11

Fresh typed value cache per invocation. Lookup only inside KeyError catch, on miss as_decimal and store. Same-type equal Decimal can return first representation despite different exponent; existing Decimal returned unchanged by provider on miss. No newly introduced float conversion.

Handoff: Exact native representation contract, not universal preservation of every distinct input lexeme. Unhashable/malformed values propagate.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L187-L202). B09 overlap occurrences: 5.

## CP330-S06 — TB12–13

Frozen slotted delta holds dirty and settled counts; exact int timeframe (not bool/subclass) positive. Main aliases same lower list at TF1, otherwise separate. Last timestamp null, typed persistent prices empty; append enters stage and returns yielded delta after context exit.

Handoff: Bucket owner is input normalization; not behavior ownership.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L205-L227). B09 overlap occurrences: 12.

## CP330-S07 — TB14

Initial dirty indices lengths; empty yields delta without modification. First timestamp int-converted before validation; rewind lower on previous last exact equality and existing bucket, copy tail; rewind main on aligned last key only nonshared, copy tail. TF1 dirty main=dirty lower. Private price additions and previous-time capture begin before checked iteration.

Handoff: Time check occurs during later lazy checked rows; preliminary int conversion can fail outside rollback. Caller input order not repaired.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L229-L254). B09 overlap occurrences: 25.

## CP330-S09 — TB14/17

Snapshot old suffixes, prior timestamp; publish new prices then lower/main suffix then last time BEFORE try. Catch BaseException in delta construction or consumer body: restore lower then nonshared main then last time, delete new keys, rethrow. Earlier commit assignments outside try; empty branch outside rollback. Delta counts exclusive max(0,len-1).

Handoff: Only bucket transaction rollback, not arbitrary callbacks or view index mutations. Last bucket provisional even with RAW gaps.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L278-L303). B09 overlap occurrences: 19.

## CP330-S10 — TB18

Enumerate supplied normalized buckets from start_index, convert epoch to Tehran naive and format six components; engine callback classifies original open/close; construct Candle with original OHLC references, order and positional indices. No independent normalization.

Handoff: Dynamic Candle/classifier owner conditional; native classifier semantics not inferred for arbitrary configured engine.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L306-L333). B09 overlap occurrences: 7.

## CP330-S11 — TB19–21

Fresh view lists/index null and closed cache. Rebuild dirty suffix or zero if no index, replace list before index update. New index with retain_crossings=True if absent or length>capacity; equal capacity refresh. Native refresh guard requires 0<=first<=old_length<=new_length<=size; clear prior history only first<old_length-1; no local rollback. Lower update assigned before separate main; TF1 aliases list/index.

Handoff: Retained view may be partially mutated on failure, outer Live owner discards it. Dirty frontier and stable prefix are caller premise, not runtime equivalence.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L336-L364). B09 overlap occurrences: 17.

## CP330-S12 — TB-M05 / records

Frozen slotted EngineBundle and MarketContext are reference containers: required engine entries incl nullable E/lifecycle, primary default null; context full lower/main lists and chronology/index, visible bounds, offset zero, trend flags false. Freeze does not recursively freeze lists/index.

Handoff: No source selection or behavior acceptance inside record declarations; dynamically supplied module interfaces conditional.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1732-L1753). B09 overlap occurrences: 5.

## CP330-S15 — TB66

Required engine path aliases Reaction/Blue/A/S, data, timeframe/from/to and direction enumerated. E/lifecycle optional; four enabled/disabled flags default enabled, bridge-output store_true, raw timeframe default1. Parse native int then analysis TF guard before RAW TF guard. No independent from/to order or timestamp positivity.

Handoff: CLI options do not prove all engines enabled; load and stage gates are distinct (TB67,TB71/73).

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1897-L1971). B09 overlap occurrences: 25.

## CP330-S17 — TB68

Timed full read then remove exactly one BOM prefix; JSON parse_float Decimal and default ints. No filter before normalization; parse/read failure propagate, telemetry finally observable.

Handoff: Source-only review; no file payload loaded. Decimal lexeme preservation at parse distinct from typed cache equality.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L2012-L2027). B09 overlap occurrences: 6.

## CP330-S18 — TB69

Timed pass-through of same source_rows object; reject falsy, normalize full history with lower_only exactly TF1, delegate context construction. No requested window filtering, sorting or future-row truncation.

Handoff: Range is presentation, full chronology may resolve provisional earlier behavior with later rows; independent reversal slicing is separate.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L2030-L2052). B09 overlap occurrences: 8.

## CP330-S20 — TB70

Use lower buckets at TF1 else main; align from/to floor except TF1. Start lower_bound(start key), inclusive end lower_bound(end key+TF)-1. Reject start>=main len or end<start before clamp to last main. Return context full arrays/index and local display bounds, defaults offset/trends.

Handoff: No calculation slicing, no raw_timeframe slots; selected range not necessarily exact requested timestamp endpoints.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L2081-L2111). B09 overlap occurrences: 24.

## CP330-S21 — TB-M05 / records

Mutable slotted PipelineState retains directional results, reusable flag, initial geometry, internal IDs, full E/StopAll/S/candidates and detector/Blue/A maps, invalid A/S IDs, optional primary/live. FullDirectionState holds initial S separately, default fresh StopAll list. No deep copies on construction.

Handoff: Accepted vs candidate distinction supplied by orchestration; presence in container not proof of calculation validity or display.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L2113-L2150). B09 overlap occurrences: 5.

## CP330-S22 — TB-M01 / scope

Clear three caches before fetching optional clear_market_indexes; nonnull callback invoked before try. Finally invoke same callback then clear time caches. Setup exception bypasses try; callback failure in finally can prevent later time clears. RAW live entry forwards rows and fresh preparer to common runner.

Handoff: Native runner calls prepare_pipeline_state without live trading-stage continuation, closed regime resolver separate. No runtime guarantee.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3713-L3735). B09 overlap occurrences: 14.

## Remaining gates

CP342 / W2 Trading Pipeline serialization and chronology queue: 28 remaining Bridge transition records, CP322-E02/E03/E04, then 2 Live records; split by projection, range/Primary and accepted ledger as warranted. Use CP341 normalized B09 traceability parts. F05 and CP333-R01/R02 remain OPEN.
